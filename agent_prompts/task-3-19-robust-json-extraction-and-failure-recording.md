# Agent Prompt — 3.19 Robust JSON extraction + failure recording + game-end recording

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.19 — Robust JSON extraction + failure recording + game-end recording, anchored to DESIGN.md §7, DESIGN.md §10.4, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-robust-json-extraction-and-failure-recording`
**Depends on:** 3.18 merged
**Section refs:** DESIGN.md §7, DESIGN.md §10.4, DESIGN.md §11.4
**Complexity:** Medium

Close the three findings surfaced by the sixth Pre-Phase-4 real-provider
eval at `audits/audit-2026-05-25-2018-pre-phase-4-real-provider-eval.md`,
which made **significant progress** (27 of 50 games completed; 2
meetings fired and completed all three phases cleanly; cost $0.21 per
meeting, well under the $0.30/game cap; replay artifacts populated)
before crashing at game 28 (seed 27). The five Task 3.14–3.18 fixes
are working; the substrate is solid. This task closes the last
JSON-shape variant the live model emits, plus two hygiene improvements
that would have materially improved the diagnostic value of this and
prior eval crashes.

**Finding 1 (Critical, production crash path): prose preamble before
fenced JSON.** Anthropic Sonnet 4.6 nondeterministically emits
"thinking" prose before its fenced JSON output. Example payload from
the crashed call:

```
I need to analyze my memory ...
```json
{
  "agent_id": "p-3",
  ...
}
```
```

Task 3.15's `_strip_json_code_fences` is **open-anchored** (regex
`^\s*```(?:json)?\s*`): it requires the fence to be the FIRST thing
in the response. When prose comes before the fence, the regex doesn't
match, the fence + prose stay, and `model_validate_json` dies on the
leading `I`. This is the sixth distinct defect class in the chain
(after missing transport, unstripped closed fence, schema field-name
drift, report truncation, statement/vote truncation) — and the audit
notes this is the third 50-game eval to fail on JSON-shape variance.
Plausibly the LAST shape variant (clean / fenced / unclosed-open /
prose+fenced — extractor below covers all four).

**Finding 2 (Hygiene, diagnostic value): crashing meetings drop their
cost.** The `ValidationError` fires inside `provider.complete` BEFORE
`LLMResponse` is constructed, so the budget layer never sees the
tokens the model already burned to generate the rejected response,
and `ReplayLog.record_meeting` is never called for the meeting.
Result: §4 of the eval undercounts spend; we can't audit how much we
paid for the responses that broke us. Recording the failed call
upstream of the re-raise unblocks post-mortem cost analysis for THIS
crash and every future crash.

**Finding 3 (Hygiene, partial-run analysis): replay does not persist
game outcome.** `ReplayEntry`'s `kind="tick"` records actions +
`state_hash` but not the `GameOverEvent`. The eval's 27/50 partial
run could not produce a win-rate figure because §5 had no way to
recover decisive outcomes from the JSONL. A one-line `record_game_end`
emission per game makes win-rate evaluable from any replay log,
including partial tournaments that crashed mid-run.

This task closes all three findings in one bundled PR. Same diagnostic
family; small total surface (~80–120 LOC + tests).

**Out of scope** (explicit decisions deferred):

- **Migration to Anthropic's `messages.create(tools=[...])` forced-JSON
  mechanism.** Would structurally eliminate the entire "parse free-text
  output as JSON" class. Larger refactor (~100–200 LOC of
  `_default_send` changes), introduces Anthropic-specific patterns,
  doesn't translate cleanly to OpenAI/DeepSeek. Still deferred — keep
  ratcheting defensive extraction until proven insufficient. If
  another eval crashes on a NEW JSON-shape variant after this task,
  that's the signal to do the tool-use migration.
- **The remaining Concern-level findings** from the seed-23 debug
  report's §9 (7 items: impostor placeholder `agent_id`/`tick`,
  accusation template's collapsed-Markdown transcript rendering,
  fence-mode split, hallucinated `speaker: "p-0"`, FakeProvider's
  verbose-output gap, `check.sh`-with-anthropic-exported failure
  mode, no-per-game-outcome-in-replay → CLOSED by finding 3 of THIS
  task). The other 6 still deferred.

**Files in scope:**
- llm/provider.py
- orchestrator/replay.py
- orchestrator/game.py
- tests/llm/test_real_provider.py
- tests/orchestrator/test_replay.py

**Files NOT in scope:**
- llm/client.py
- llm/budget.py
- llm/budgeted_client.py
- llm/cache.py
- llm/fake_provider.py
- llm/README.md
- llm/__init__.py
- meetings/manager.py
- meetings/transcript.py
- meetings/schemas.py
- meetings/voting.py
- meetings/__init__.py
- agents/strategic/
- agents/
- engine/
- observation/
- orchestrator/scheduler.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- orchestrator/seeder.py
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/observation/
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_game.py
- tests/orchestrator/test_meeting_integration.py
- tests/orchestrator/test_replay_meetings.py
- tests/orchestrator/test_seeder.py
- tests/eval/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/llm/test_budgeted_client.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **Robust JSON block extractor.** Replace `_strip_json_code_fences` in `llm/provider.py:211+` with a new helper (e.g. `_extract_json_block(text: str) -> str`) that handles every observed shape:
  - **Clean JSON** (`{...}` start to finish) → return unchanged.
  - **Fenced JSON** (`` ```json\n{...}\n``` ``) → strip fences, return body.
  - **Unclosed fenced JSON** (`` ```json\n{...incomplete `` — Task 3.17's case) → strip opener, return remainder trimmed.
  - **Prose preamble + fenced JSON** (`I need to analyze...\n```json\n{...}\n```` — THIS TASK's case) → ignore prose, extract JSON.
  - **Prose preamble + bare JSON** (`I need to analyze...\n{...}` — possible variant) → ignore prose, extract JSON.
  - **JSON + trailing prose** (`{...}\n\nDone!` — possible variant) → extract JSON, ignore trailing prose.
  - **No JSON content** → pass through unchanged (let Pydantic fail loud).
  
  The implementation strategy: find the first `{` in the text, walk forward tracking brace depth with string-literal awareness (inside `"..."`, braces don't count; respect `\"` escape sequences), return the substring from the first `{` to its matching `}` (inclusive), stripped of surrounding whitespace. If no balanced block is found, fall back to existing fence-strip behavior (preserves Task 3.17's truncation handling).
- [ ] **Backward compatibility for the existing strip behavior.** All Task 3.15/3.17 unit tests in `TestStripJsonCodeFences` must still pass without modification. If the helper is renamed (e.g. `_strip_json_code_fences` → `_extract_json_block`), update internal call sites at [llm/provider.py:126](llm/provider.py#L126) and the test imports; the public-facing behavior (input shape → output shape) is preserved. Document any test-name renames in `## Decisions`.
- [ ] **Unit tests for the new shapes** in `tests/llm/test_real_provider.py::TestStripJsonCodeFences` (or rename the class to `TestJsonBlockExtraction` if more accurate). Six new tests, all NOT `@real_provider`-marked (pure string logic; runs in CI):
  - Prose preamble + fenced JSON → extracts JSON.
  - Prose preamble + bare JSON → extracts JSON.
  - JSON with trailing prose → extracts JSON.
  - JSON containing string-embedded `{` and `}` (e.g. `"text": "foo { bar }"`) → braces inside strings don't affect depth tracking.
  - JSON with escaped quotes (`"text": "she said \"hi\""`) → escape sequences inside strings respected.
  - Multiple balanced blocks in one response → returns ONLY the first.
- [ ] **`@real_provider` regression test for prose-preamble case.** Add to `tests/llm/test_real_provider.py::TestAnthropicTruncationFailureMode` (or a sibling class). Construct a prompt explicitly inviting prose preamble (e.g. "Think step by step about your role in this meeting, then emit a ReportDocument JSON object."). Call `client.complete(prompt=..., schema=ReportDocument, max_tokens=2048, temperature=0.0)`. Assert the call returns without raising. Skipped in CI by default. Cost: ~$0.01 per invocation.
- [ ] **Failed-LLM-call recording in replay log.** In `orchestrator/replay.py`, extend `LLMCallRecord` with an optional failure-detail field (e.g. `parse_status: Literal["success", "failed"] | None = None`, plus `parse_error: str | None = None`) — OR add a new `FailedLLMCallRecord` sibling type — to capture failed calls. In `llm/provider.py::complete`, on `ValidationError` (or `json.JSONDecodeError`), construct enough metadata (model id, prompt length, raw response text first 1KB, input/output tokens, cost_usd, exception type + first 200 chars of message) and surface it to the recording layer before re-raising. Implementing agent picks the surfacing mechanism (typed exception carrying the partial info, side-channel callback into the recording client, or a contextvar — whichever is cleanest given the existing `_RecordingLLMClient` shape at [orchestrator/game.py:200+](orchestrator/game.py#L200)). The record must persist through `ReplayLog.record_meeting` (or a new `record_failed_call` method) so post-mortem analysis can reconstruct per-meeting cost even when the meeting crashed.
- [ ] **Game-end recording in replay log.** Add `ReplayLog.record_game_end(winner, reason)` (or extend `ReplayEntry` with a new `kind="game_over"` variant) to `orchestrator/replay.py`. In `orchestrator/game.py::HeadlessGame.run`, after the engine emits `GameOverEvent` (typically as the final tick's event payload), call `record_game_end(winner=event.winner, reason=event.reason)`. The record is the LAST JSONL row in a successful game's replay. For tournament-driven crashes, a `record_game_end` row is present for every completed game preceding the crash — enabling post-hoc win-rate computation from any replay log, including partial runs. Add a helper in `orchestrator/replay.py` to read game-end records: `read_game_outcome(path: Path) -> WinnerSide | None`.
- [ ] **Unit tests for failed-call recording.** In `tests/llm/test_real_provider.py`, add a non-`@real_provider` test that constructs a synthetic `ValidationError` scenario via the fake provider (or by directly mocking the parse step), invokes `client.complete`, asserts `ValidationError` propagates AND that the recording layer captured the failed-call metadata. Verifies the contract works even without a real provider call.
- [ ] **Unit tests for game-end recording** in `tests/orchestrator/test_replay.py`. Round-trip test: write a `record_game_end(winner="CREWMATES", reason="all_tasks_complete")` row to a temp replay; read it back via `read_game_outcome`; assert the parsed value matches. Add at least one test for the missing-game-end case (partial replay with no game-end row) → returns `None`.
- [ ] **Post-merge local verification.** With `AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` set:
  - Run `AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v` — all existing `@real_provider` tests pass, plus the new prose-preamble test passes. Cost: ~$0.07 total.
  - Re-run the eval prompt's direct sanity call — must still pass.
  - Run a small smoke (5 games via `scripts/run_game.py` across seeds 0–4) with `AILIBI_LLM_PROVIDER=fake`; confirm `record_game_end` rows are present in each replay JSONL.
  - Paste verbatim outputs (test results, smoke replay grep showing game_end rows, sanity call output) into `## Decisions`. API key prefix only (8 chars).
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (the new `@real_provider` test skipped by default; all CI-running tests pass).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The balanced-block extractor is the load-bearing fix. The naive approach (regex) is insufficient because regular expressions cannot match nested structures with arbitrary depth. Walk the string with explicit state tracking. Suggested shape (illustrative; pick exact names consistent with the file):

```python
# llm/provider.py — illustrative
def _extract_json_block(text: str) -> str:
    """Extract the first balanced JSON object from a string.

    Handles every shape the live Anthropic provider has been observed
    to emit in the Pre-Phase-4 evals:

    - Clean JSON, fenced JSON (Task 3.15 cases),
    - Unclosed fenced JSON / truncated responses (Task 3.17 case),
    - Prose preamble + fenced/bare JSON (THIS task's case),
    - JSON followed by trailing prose.

    Strategy: find the first ``{`` in the input, then walk forward
    tracking brace depth, respecting string literals and their escape
    sequences. Return the substring from the first ``{`` to its
    matching ``}``, stripped of surrounding whitespace. If no balanced
    block is found, fall back to the existing fence-strip behavior
    (preserves Task 3.17's truncation handling).
    """
    open_index = text.find("{")
    if open_index == -1:
        return _legacy_strip_json_code_fences(text)  # the old behavior

    depth = 0
    in_string = False
    escape_next = False
    for index in range(open_index, len(text)):
        ch = text[index]
        if escape_next:
            escape_next = False
            continue
        if in_string:
            if ch == "\\":
                escape_next = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_index : index + 1].strip()
    # No balanced block found (truncated mid-object) — fall back.
    return _legacy_strip_json_code_fences(text)
```

The `_legacy_strip_json_code_fences` is the existing Task 3.17 helper, preserved as the fallback for shapes the new extractor can't handle (truncated mid-object, no JSON content at all). Tests from `TestStripJsonCodeFences` still pass because those inputs all pass through the fallback path (they're either fenced-with-matching-close, fenced-without-close, or no-JSON-content).

For the failed-call recording, the cleanest design is a typed exception carrying the partial metadata:

```python
# llm/provider.py — illustrative
class LLMSchemaParseError(ValidationError):  # or a sibling Exception
    """Raised when the live provider returned a non-empty response
    that fails schema validation. Carries the cost and partial data
    so the recording layer can persist a failed-call audit trail.
    """
    def __init__(
        self,
        original_error: ValidationError,
        *,
        model: str,
        prompt_length: int,
        raw_response: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
    ) -> None:
        ...
```

Then `_RecordingLLMClient.complete` at [orchestrator/game.py:200+](orchestrator/game.py#L200) catches `LLMSchemaParseError`, records the failed call into the in-progress meeting, and re-raises. The meeting still aborts (the caller can't proceed without a valid response), but the cost is captured.

Alternative simpler design: have AnthropicClient compute cost BEFORE attempting `model_validate_json`, attach it to the exception's `__cause__` chain via `raise ValidationError(...) from EnrichedException`. Implementing agent picks. The contract is "post-mortem analysis can reconstruct cost paid for the failed call."

For the game-end recording, the shape:

```python
# orchestrator/replay.py — illustrative
class GameEndReplayEntry(BaseModel):
    kind: Literal["game_over"] = "game_over"
    game_id: str
    tick: int
    winner: Literal["CREWMATES", "IMPOSTORS"] | None  # None = draw / unfinished
    reason: str

def record_game_end(
    self, *, game_id: str, tick: int, winner: ..., reason: str
) -> None:
    ...

def read_game_outcome(path: Path) -> Literal["CREWMATES", "IMPOSTORS"] | None:
    """Return the winner from the last game-end record in a replay log.

    Returns None if no game-end record is present (partial / crashed
    game).
    """
    ...
```

The orchestrator emits this at `HeadlessGame.run` exit after the engine fires `GameOverEvent`. Already-deterministic; no new state needed.

## Public types this task introduces
- `orchestrator.replay.GameEndReplayEntry` (or equivalent variant on existing `ReplayEntry`)`
- `orchestrator.replay.read_game_outcome`
- `Possibly `llm.provider.LLMSchemaParseError` (depending on implementing agent's design choice)`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import agents.strategic.reasoner"`
- `uv run python -c "import llm.budgeted_client"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-3-robust-json-extraction-and-failure-recording` with a title like `task 3.19: robust json extraction + failure recording + game-end recording`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §10.4, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
