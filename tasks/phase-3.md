# Phase 3 — Strategic Agents And Meetings

## Goal
LLM-driven meetings work end-to-end. Reports, accusations, votes, contradiction
flags, replay artifacts, prompt versions, and cost metadata are structured and
testable. No real network LLM calls run in CI.

## Parallelism
Sequential foreground through 3.12, with prompt templates 3.4 through 3.7 able
to run in parallel after 3.3 because they depend on shared schemas and
rendered-memory inputs.

## Tasks

### Task 3.1 — LLM client
**Branch:** `phase-3-llm-client`
**Depends on:** Phase 2 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Medium

llm/client.py, provider adapter, fake provider, cache, and budget.

**Files in scope:**
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
- tests/llm/test_client.py
- tests/llm/test_budget.py

**Files NOT in scope:**
- agents/tactical/
- engine/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] **`LLMClient` Protocol exists and is provider-neutral.** The Protocol's public surface does not expose Anthropic-specific concepts (extended thinking, `cache_control`, prompt-caching beta headers, message-shape internals). Anthropic-specific behaviors live as private implementation details inside `AnthropicClient`. The Protocol is tight enough that adding a second provider (OpenAI, DeepSeek, local) is a new-file change — no edits required to call sites in `agents/`, `meetings/`, or `orchestrator/`.
- [ ] **Real provider adapter (`AnthropicClient`) is behind the Protocol.** Defaults to `claude-sonnet-4-6` for meeting-strength calls and `claude-haiku-4-5-20251001` for triggered-check calls. The model id is a constructor parameter (not a hardcoded literal); the default selection is by call type and overridable per-call.
- [ ] **Runtime provider/model selection.** The active provider and model are selected at construction time from configuration (environment variables like `AILIBI_LLM_PROVIDER=anthropic`, `AILIBI_LLM_MEETING_MODEL`, `AILIBI_LLM_TRIGGER_MODEL`, or an equivalent config object passed by the orchestrator). Document the chosen mechanism in the PR's `## Decisions` block.
- [ ] **Cross-provider portability is documented.** A `llm/README.md` (or top-of-file docstring in `llm/client.py`) describes the minimum surface a hypothetical second-provider adapter must implement, with one worked sketch (10–20 lines, no real SDK calls) showing what an OpenAI or DeepSeek adapter would look like. You do not ship the second adapter — you show that it would slot in cleanly.
- [ ] **Fake deterministic provider** exists for tests and CI; it produces schema-valid responses without recording or hashing. Tests pass the same prompt and always get the same response shape. The fake is the default for CI; the real provider is only invoked in explicit local/eval runs.
- [ ] **Prompt cache and per-game budget support exist.** Cache key is provider-neutral (does not bake in Anthropic message structure). Budget enforcement is fail-loud on overrun (raises a typed exception), not silent truncation.
- [ ] CI tests use the fake provider and make no network calls. The real provider adapter is exercised only by tests marked with an explicit `pytest.mark.real_provider` (or equivalent) that CI skips by default.
- [ ] No LLM calls are added to `agents/tactical/`.
- [ ] `uv run mypy --strict llm agents` passes.
- [ ] `uv run ruff check .` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §7 + §10.4 for the LLM-client surface. The fake deterministic provider is the most important piece — it is what every test in CI calls. `LLMClient` is a Protocol; the real and fake providers both implement it. Cache and budget are layered on top.

**Cross-provider portability is a hard requirement.** Anthropic Sonnet 4.6 and Haiku 4.5 are the Phase 3 defaults, but the architecture must support swapping the provider (to OpenAI, DeepSeek, or a local model) later without touching call sites. Keep the Protocol's surface minimal:

```python
# llm/client.py — illustrative shape; the implementing agent picks the exact signature
class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int

class LLMResponse(BaseModel):
    text: str
    usage: TokenUsage          # provider-agnostic counts
    cost_usd: float            # provider computes; Protocol consumers don't care how
    model: str                 # identifier; opaque to the Protocol

class LLMClient(Protocol):
    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse: ...
```

If you find yourself wanting to expose Anthropic-specific knobs (extended thinking, `cache_control`, beta headers) on the Protocol, stop — that's a smell. Add the knob as a private parameter on `AnthropicClient.__init__` instead. Phase 3 prompts that need Anthropic-only behavior get raised in the PR's `## Decisions` block for review rather than baked into the Protocol.

The provider/model selection mechanism: env var is simplest (`AILIBI_LLM_PROVIDER`, `AILIBI_LLM_MEETING_MODEL`, `AILIBI_LLM_TRIGGER_MODEL`). A config dict passed by the orchestrator is also fine. Pick one and document; the next Phase 3 task will inherit whichever you choose.

**Ready-to-paste prompt:** `agent_prompts/task-3-1-llm-client.md`

### Task 3.2 — Shared meeting/output schemas and `BodyView.victim_id` boundary
**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md §1.3, DESIGN.md Appendix A
**Complexity:** Medium

Two bundled deliverables that share schema-discipline work:

1. **Meeting / output schemas.** Centralize meeting artifacts in
   `meetings/schemas.py`. Agent strategic schemas may re-export or wrap
   the shared schemas, but must not duplicate independent schema
   definitions.
2. **R-4 retirement: `BodyView.victim_id` typed field.** Replace the
   `_BODY_ID_VICTIM_PATTERN` regex coupling in
   `agents/tactical/impostor_policy.py` (introduced by Task 2.10 as a
   Phase-2 inference bridge) with a typed `victim_id: PlayerId` field
   on `observation/packet.py::BodyView`. The packet builder populates
   `victim_id` directly from `BodyState.player_id`; perception surfaces
   `victim_id` in `saw_body` event payloads; the impostor policy reads
   the field instead of regex-parsing the body id. The body's victim
   id was already inferrable from the existing `body_id` format
   (`body-{victim_id}-{tick}` per `engine/rules.py:69`), so exposing it
   directly does not weaken the firewall — it formalizes what was
   already public and removes the agent→engine string coupling flagged
   as R-4 in `audits/audit-2026-05-16-0036-reconciled.md`.

The two deliverables are bundled because both are pure
schema-discipline work and both touch the boundary layer. The
meeting-schemas work alone would be Small; folding in R-4 retirement
makes the task Medium.

**Files in scope:**
- meetings/schemas.py
- agents/strategic/output_schemas.py
- observation/packet.py
- observation/service.py
- agents/perception.py
- agents/tactical/impostor_policy.py
- eval/leak_test.py
- tests/meetings/test_schemas.py
- tests/observation/test_service.py
- tests/observation/test_boundary_contracts.py
- tests/agents/test_perception.py
- tests/agents/test_impostor_policy.py

**Files NOT in scope:**
- engine/
- orchestrator/
- agents/tactical/crewmate_policy.py
- agents/tactical/pathing.py
- agents/runtime.py
- agents/base.py
- agents/memory/
- llm/
- api/
- frontend/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/test_crewmate_policy.py
- tests/agents/test_memory.py
- tests/agents/test_pathing.py
- tests/agents/test_runtime.py
- tests/engine/
- tests/eval/
- tests/orchestrator/
- tests/test_firewall.py

**Definition of done:**
- [ ] **Meeting / output schemas:** `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and contradiction/result DTOs in `meetings/schemas.py` match DESIGN.md §5.3 and §5.5. `agents/strategic/output_schemas.py` re-exports or wraps shared meeting schemas without duplicating them. Schemas are suitable for structured LLM output. Relevant schema tests in `tests/meetings/test_schemas.py` pass.
- [ ] **R-4 — `BodyView.victim_id` field added.** `observation/packet.py::BodyView` gains a `victim_id: PlayerId` field. The Pydantic model validates the field as a non-empty string matching the canonical `p-N` id form (or whatever shape `PlayerId` is typed as).
- [ ] **R-4 — packet builder populates `victim_id`.** `observation/service.py` populates `BodyView.victim_id` from `BodyState.player_id` (the engine-side hidden field) when constructing every `BodyView` for every packet. This is a read of engine state inside the privileged ObservationService — no firewall violation, since ObservationService is the single privileged consumer per DESIGN.md §1.3.
- [ ] **R-4 — perception surfaces `victim_id`.** `agents/perception.py` constructs `saw_body` `EpisodicEvent` payloads with a `victim_id` key whose value is taken from `BodyView.victim_id`. The existing `body_id` payload field remains (it stays the canonical body identifier for deduplication / replay reference); `victim_id` is the authoritative source for downstream agent code that needs the body's player id.
- [ ] **R-4 — impostor policy reads `victim_id`, regex retired.** `agents/tactical/impostor_policy.py::_confirmed_dead_from_bodies` reads `victim_id` directly from each `saw_body` event payload. The `_BODY_ID_VICTIM_PATTERN` regex constant (`agents/tactical/impostor_policy.py:88-94`) is deleted entirely along with the regex import line if it becomes unused. The `ValueError` guard becomes: raise if `victim_id` is missing or not a string (mirroring the previous body-id missing-payload guard).
- [ ] **R-3 test (Task 2.13) updated for `victim_id`.** `tests/agents/test_impostor_policy.py::test_confirmed_dead_from_bodies_raises_on_missing_body_id` is renamed to `test_confirmed_dead_from_bodies_raises_on_missing_victim_id` (or equivalent) and updated to construct a `saw_body` payload missing `victim_id` (rather than `body_id`). The test continues to assert `ValueError`. Existing stale-target tests in `TestImpostorStaleAndDeadTargetPruning` continue to pass against the new `victim_id`-based implementation; verify with `uv run pytest tests/agents/test_impostor_policy.py -v -k "Stale or Dead or victim_id"`.
- [ ] **R-4 — boundary contract tests cover `victim_id`.** `tests/observation/test_service.py` and `tests/observation/test_boundary_contracts.py` gain assertions that `BodyView.victim_id` is populated on every `BodyView` and matches the originating `BodyState.player_id`. Add at least one negative pin: a `BodyView` constructed without `victim_id` should fail Pydantic validation.
- [ ] **R-4 — perception tests cover `victim_id` surfacing.** `tests/agents/test_perception.py` gains an assertion that `saw_body` events carry `victim_id` in their payload and that the value matches the originating `BodyView.victim_id`.
- [ ] **R-4 — leak scanner remains green.** Re-run `uv run pytest eval/leak_test.py` and confirm no new packet field trips a leak guard. The player id `p-N` does not contain `impostor` / `crewmate` / `crew` substrings; the field name `victim_id` is not in the hidden-keys list. If the recursive field-name scanner has an explicit allow/deny list that requires updating to account for the new field, make the edit in `eval/leak_test.py` and document the change in `## Decisions`. Run a full 10-game tournament leak scan as well: `uv run python scripts/run_tournament.py --num-games 10 --start-seed 0 --output-dir /tmp/task-3-2-leak --max-ticks 1000` and confirm the per-game audit logs pass the scanner.
- [ ] No imports from `engine/` under `agents/` (firewall preserved).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §5.3 + §5.5 for the meeting-schemas surface. `meetings/schemas.py` owns the canonical Pydantic shapes for `ReportDocument`, `Statement`, `VoteBallot`, and `MeetingResult`. `agents/strategic/output_schemas.py` re-exports or wraps these — never duplicate.

**R-4 retirement is the bulk of the work.** The migration walks one chain: engine `BodyState.player_id` → observation `BodyView.victim_id` → perception `saw_body` event payload → impostor policy `_confirmed_dead_from_bodies`. Each hop is small; the diffs are concentrated and reviewable. Suggested order:

1. **Add the field to the schema.** `observation/packet.py::BodyView` gains `victim_id: PlayerId`. Pydantic does the validation for free.
2. **Populate it in the builder.** `observation/service.py` reads `BodyState.player_id` (engine-side, already accessible inside ObservationService) and passes it through to `BodyView`. The body's victim id was always inferrable from the existing `body_id` format, so exposing it directly is a refactor, not a firewall change.
3. **Surface it in perception.** `agents/perception.py` already ingests `BodyView`s and emits `saw_body` events. Find the event-construction site and add `"victim_id": body.victim_id` to the payload dict alongside the existing `"body_id"` entry.
4. **Consume it in the policy.** `agents/tactical/impostor_policy.py::_confirmed_dead_from_bodies` currently looks like:

   ```python
   match = _BODY_ID_VICTIM_PATTERN.match(body_id)
   if match is None:
       continue
   dead.add(match.group(1))
   ```

   Becomes:

   ```python
   victim_id = event.payload.get("victim_id")
   if not isinstance(victim_id, str):
       raise ValueError(
           f"saw_body event missing string 'victim_id': {event.payload!r}"
       )
   dead.add(victim_id)
   ```

   Delete the `_BODY_ID_VICTIM_PATTERN` constant (and the `re` import if it becomes unused elsewhere in the file).
5. **Update the R-3 test.** The Task 2.13 regression test was named for the `body_id` semantics; rename and retarget for `victim_id`. The other `TestImpostorStaleAndDeadTargetPruning` tests should pass as-is once the helper / event factories are updated to pass `victim_id` through.

The leak scanner should pass cleanly without changes — `victim_id` is not a reserved hidden-field name, and `p-N` values don't contain forbidden substrings. But re-run it to confirm; this is the kind of boundary change where surprising scanner behavior is worth catching before merge.

**Integration risk:**

The R-4 retirement crosses the engine→observation→agents chain (one hop per layer). The meeting-schemas work is independent and small.

- **Firewall preserved.** ObservationService is allowed to read engine state per DESIGN.md §1.3; surfacing `BodyState.player_id` as `BodyView.victim_id` is the same read pattern as every other field on `BodyView`. `agents/` continues to import only `observation/`, never `engine/`. Verify with `uv run lint-imports`.
- **No firewall regression.** The body's victim id was always inferrable from `body_id = f"body-{victim_id}-{tick}"` (engine/rules.py:69). The R-4 retirement formalizes this access pattern; it does not expose new information.
- **R-3 test rename is mandatory, not optional.** Task 2.13 just landed `test_confirmed_dead_from_bodies_raises_on_missing_body_id`; with `_BODY_ID_VICTIM_PATTERN` deleted, the test's body-id-based assertion no longer reaches the retired branch and the test would either become tautological or break. Rename and retarget in the same PR — do not leave the test pinning a removed code path.
- **Determinism preserved.** Adding `victim_id` to `BodyView` changes the byte content of every replay (the audit log includes packet contents). The byte-identity test compares two live runs of the same fixture against each other (not against a frozen reference), so it still passes — but verify explicitly with `uv run pytest tests/orchestrator/test_game.py eval/determinism_test.py -v`.
- **Leak scan re-run is required.** Packet-content changes are the highest-risk surface for the leak scanner. Run the full eval suite (`uv run pytest eval/leak_test.py`) plus a 10-game tournament audit scan.
- **`agents/memory/beliefs.py` is intentionally out of scope.** Earlier audits flagged a Phase-3-cleanup option to put a `is_confirmed_dead` flag on `PlayerBelief`. That's a separate decision that belongs to Task 3.3 (memory rendering) or later — not this task. The current impostor-policy implementation reading `victim_id` directly from episodic events is the contracted approach.
- **`audits/*` are read-only artifacts.** Do not edit any audit report.

**Ready-to-paste prompt:** `agent_prompts/task-3-2-output-schemas.md`

### Task 3.3 — Memory rendering
**Branch:** `phase-3-memory-rendering`
**Depends on:** 3.2 merged
**Section refs:** DESIGN.md §6.6
**Complexity:** Medium

agents/memory/store.py::render_for_prompt per §6.6.

**Files in scope:**
- agents/memory/store.py
- tests/agents/test_memory_rendering.py
- tests/fixtures/memory_rendering/

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `render_for_prompt` produces a token-budgeted structured view per DESIGN.md §6.6.
- [ ] Rendered memory comes from structured memory, not raw chat as source of truth.
- [ ] Salience ordering is deterministic and covered by golden tests.
- [ ] Rendered output includes open contradiction inputs when present.
- [ ] No imports from engine/ under agents/.
- [ ] **R-6 acceptance gate (per `audits/audit-2026-05-15-0225-reconciled.md` §R-6):** `agents/memory/store.py` exposes a composite memory surface that aggregates the episodic, working, and belief state introduced in Task 2.3 (`agents/memory/episodic.py`, `agents/memory/working.py`, `agents/memory/beliefs.py`). `render_for_prompt` produces its structured view by reading from all three components, not from any one of them in isolation. The composite surface is the integration point Phase 3 strategic agents import through.
- [ ] **R-10 acceptance gate for rendered memory (per `audits/audit-2026-05-15-0225-reconciled.md` §R-10):** The packet field/value leak scanners from `eval/leak_test.py` (`_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values`, or their canonical Phase 3 successors) are reused against `render_for_prompt` golden outputs in `tests/agents/test_memory_rendering.py`. At least one planted negative test pins that the scanner trips on a forbidden role-bearing string injected into the rendered surface (mirroring `test_role_bearing_value_scanner_trips_on_planted_visible_player_id` in `eval/leak_test.py:221-236`).
- [ ] `uv run mypy --strict agents meetings` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §6.6 for the canonical rendered-prompt example. The render function takes a `MemoryStore` and a token budget, then returns a single Markdown string with sections: role, tasks completed, recent observations (salience-sorted), beliefs, and open contradictions. Drop events past the token budget by lowest salience first.

**Ready-to-paste prompt:** `agent_prompts/task-3-3-memory-rendering.md`

### Task 3.4 — Crewmate report prompt
**Branch:** `phase-3-crewmate-report-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §6.6
**Complexity:** Medium

agents/strategic/prompts/crewmate_report.j2.

**Files in scope:**
- agents/strategic/prompts/crewmate_report.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Crewmate report prompt exists and targets the shared `ReportDocument` schema.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.


**Implementation hint:**

Jinja2 template only; pair with §5.3 ReportDocument schema.

**Ready-to-paste prompt:** `agent_prompts/task-3-4-crewmate-report-prompt.md`

### Task 3.5 — Impostor report prompt
**Branch:** `phase-3-impostor-report-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §4.5, DESIGN.md §5.3, DESIGN.md §6.6
**Complexity:** Medium

agents/strategic/prompts/impostor_report.j2.

**Files in scope:**
- agents/strategic/prompts/impostor_report.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Impostor report prompt exists and targets the shared `ReportDocument` schema.
- [ ] Prompt frames deception as a game rule without exposing hidden engine state.
- [ ] Prompt uses rendered memory view and public transcript inputs only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.


**Implementation hint:**

Jinja2 template only; pair with §5.3 + §4.5 (deception framing).

**Ready-to-paste prompt:** `agent_prompts/task-3-5-impostor-report-prompt.md`

### Task 3.6 — Accusation round prompt
**Branch:** `phase-3-accusation-round-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.2, DESIGN.md §5.3
**Complexity:** Medium

agents/strategic/prompts/accusation_round.j2.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation round prompt exists and targets the shared `Statement` schema.
- [ ] Prompt uses rendered memory view, transcript-so-far, and contradiction flags only.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.


**Implementation hint:**

Jinja2 template only; pair with §5.2 + §5.3 Statement schema.

**Ready-to-paste prompt:** `agent_prompts/task-3-6-accusation-round-prompt.md`

### Task 3.7 — Vote ballot prompt
**Branch:** `phase-3-vote-ballot-prompt`
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.5
**Complexity:** Small

agents/strategic/prompts/vote_ballot.j2.

**Files in scope:**
- agents/strategic/prompts/vote_ballot.j2

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ client code
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote ballot prompt exists and targets the shared `VoteBallot` schema.
- [ ] Prompt receives rendered memory, transcript, contradiction flags, and suspicion graph.
- [ ] Prompt includes uncertainty-aware skip behavior.
- [ ] Prompt includes a version marker.
- [ ] No code outside the prompt file is modified.


**Implementation hint:**

Jinja2 template only; pair with §5.5 VoteBallot schema.

**Ready-to-paste prompt:** `agent_prompts/task-3-7-vote-ballot-prompt.md`

### Task 3.8 — Meeting state machine
**Branch:** `phase-3-meeting-state-machine`
**Depends on:** 3.3 merged, 3.4 merged, 3.5 merged, 3.6 merged, 3.7 merged
**Section refs:** DESIGN.md §5.1, DESIGN.md §5.2
**Complexity:** Medium

`meetings/manager.py` and `meetings/transcript.py` per §5.1 + §5.2. The
state machine moves through report intake → accusation rounds → voting →
resolution, consuming the four prompt templates landed in Tasks 3.4–3.7
and returning a structured `MeetingResult` for the orchestrator (3.12)
to apply.

**C-3 directive from
`audits/audit-2026-05-16-0611-claude.md`:** the post-3.3 audit
identified that `MeetingTranscript` (`meetings/schemas.py:217-225`) is
`tuple[ReportDocument, ...]` + `tuple[Statement, ...]` with no
guaranteed statement ordering, no `round_max` invariant, and no test
exercising a multi-round transcript end-to-end. Without resolution
here, every downstream consumer (3.9 strategic reasoner, 3.10 voting,
3.11 contradiction detection) would have to invent its own sort
convention, risking drift. Task 3.8 must close this. Pick one of two
options (see DoD + Implementation hint) and document the choice in the
PR's `## Decisions` block.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py
- tests/meetings/test_manager.py
- tests/meetings/test_transcript.py
- meetings/schemas.py
- tests/meetings/test_schemas.py

**Files NOT in scope:**
- engine/ core rule changes
- orchestrator/
- agents/tactical/
- agents/strategic/
- agents/memory/
- agents/perception.py
- agents/runtime.py
- agents/base.py
- observation/
- llm/
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/llm/
- tests/agents/
- tests/observation/
- tests/orchestrator/
- tests/engine/
- tests/eval/
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`MeetingManager` follows trigger lifecycle in DESIGN.md §5.1.** Construction takes the LLM client, the four prompt callables (Tasks 3.4–3.7's deliverables), and a deadline configuration. It does not start until a meeting trigger fires; once triggered it runs to resolution.
- [ ] **Protocol implements report intake, accusation rounds, voting, and resolution per DESIGN.md §5.2.** Each phase consumes the appropriate prompt template; the state machine wires them together.
- [ ] **Missed deadlines yield default no-statement / no-vote behavior** as specified in §5.2. The default action is recorded in the transcript so the audit trail is complete.
- [ ] **Manager returns `MeetingResult`; it does not mutate engine state.** The orchestrator (3.12) applies the result. `MeetingManager` does not import from `engine/`; `lint-imports` must pass.
- [ ] **C-3 — statement ordering contract resolved.** Pick exactly one option and implement it:
  - **Option (a) — recommended: producer-guaranteed canonical order.** `MeetingManager` emits `Statement` instances into the transcript in canonical order: ascending `round_index`, then ascending insertion order within a round (stable). The contract is documented as a docstring on `MeetingManager.run` (or wherever the state machine produces the transcript) stating: *"Consumers may read `transcript.statements` in tuple order and trust that statements are sorted by `(round_index, insertion_order)` without re-sorting."* No schema change required.
  - **Option (b) — alternative: schemas add `round_max` + consumer sort discipline.** `meetings/schemas.py::MeetingTranscript` gains a `round_max: int = Field(ge=1)` field constraining the configured number of rounds, with a validator that no `Statement.round_index >= round_max`. Every consumer of the transcript is responsible for sorting. The contract is documented on the schema.
- [ ] **C-3 — statement-ordering pin test.** `tests/meetings/test_manager.py` (or `test_transcript.py`, depending on where the contract lives) gains a regression that drives `MeetingManager` through at least two accusation rounds with multiple participants, captures the resulting `MeetingTranscript`, and asserts either (a) `statements` is already sorted by `(round_index, insertion_order)` if option (a) was picked, OR (b) the `round_max` invariant rejects an out-of-range `round_index` if option (b) was picked. The test must fail against an implementation that allows ambiguous ordering.
- [ ] **Relevant meeting tests pass using fake strategic participants.** Use the existing `llm/fake_provider.py` plus shim participants — no real Anthropic calls.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy --strict meetings agents llm` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §5.1 + §5.2. `MeetingManager` is a state machine that moves through report intake → accusation rounds → voting → resolution. It must NOT mutate engine state; it returns a `MeetingResult` that the orchestrator (3.12) applies.

The four prompt templates from Tasks 3.4–3.7 are already wired through `meetings/schemas.py` types. The state machine's job is sequencing — it does not re-implement the prompt logic.

**C-3 resolution — option (a) is the default.** Producer-guaranteed canonical order is cleaner because it scales: consumers (3.9 reasoner, 3.10 voting, 3.11 contradictions) read the tuple in order and trust the contract. Option (b) scatters sort discipline across every consumer and risks drift between consumers if they implement it differently.

Suggested shape for option (a):

```python
# meetings/manager.py
@dataclass(frozen=True)
class _RoundOutput:
    round_index: int
    statements: tuple[Statement, ...]

class MeetingManager:
    """State machine for meetings (DESIGN.md §5.1, §5.2).

    Statement-ordering contract: the `MeetingTranscript.statements` tuple
    is guaranteed sorted by ascending `(round_index, insertion_order)`.
    Insertion order within a round is the order in which participants
    submitted statements (or their default-no-statement entry on
    deadline). Consumers may trust this order and need not re-sort.
    """

    async def run(...) -> MeetingResult:
        rounds: list[_RoundOutput] = []
        for round_index in range(self._round_count):
            round_statements = await self._collect_statements(round_index, ...)
            rounds.append(_RoundOutput(round_index=round_index, statements=round_statements))

        # Concatenation preserves (round_index, insertion_order) ordering
        ordered = tuple(stmt for r in rounds for stmt in r.statements)
        transcript = MeetingTranscript(reports=..., statements=ordered)
        ...
```

If you pick option (b) instead, the schema change is:

```python
# meetings/schemas.py
class MeetingTranscript(BaseModel):
    model_config = ConfigDict(frozen=True)

    reports: tuple[ReportDocument, ...]
    statements: tuple[Statement, ...]
    round_max: int = Field(ge=1)

    @model_validator(mode="after")
    def _validate_round_indices(self) -> "MeetingTranscript":
        for stmt in self.statements:
            if stmt.round_index >= self.round_max:
                raise ValueError(
                    f"Statement.round_index {stmt.round_index} >= round_max {self.round_max}"
                )
        return self
```

Either path is acceptable; pick one and commit. Document the choice with a one-paragraph rationale in `## Decisions`.

For the deadline / default-no-statement behavior, model on the existing prompt-template tests in `tests/meetings/` (Tasks 3.4–3.7 set the precedent for how missing-input scenarios are tested). The deadline timeout is a parameter, not hardcoded — `asyncio.wait_for` with the deadline value is the simplest implementation.

**Public types introduced:**

- `meetings.manager.MeetingManager`

(`MeetingTranscript` already lives in `meetings/schemas.py` per `meetings/schemas.py:217-225`; this task does not relocate or re-export it. If option (b) is chosen, the schema gains a `round_max` field but the type's import path is unchanged.)

**Integration risk:**

This task is the join point for sub-phase B's four prompt templates. It introduces the state machine that orchestrator (3.12) will eventually drive.

- **Statement ordering is the most important deliverable.** The C-3 directive above is non-negotiable. A 3.8 PR that ships without a documented ordering contract (either option a or b) is incomplete; the next audit will flag it as High.
- **Determinism preserved.** `MeetingManager` consumes the LLM client. In CI the client is the fake deterministic provider — same prompt → same response shape → same transcript. Verify the state machine itself is deterministic given fake-provider responses (no `dict.items()` iteration over participant ids without explicit sort, no `set` ordering assumptions).
- **Firewall preserved.** `meetings/` does not import from `engine/` or `orchestrator/`. `lint-imports` enforces; verify with `uv run lint-imports` post-implementation.
- **No leak scanner extension needed at this task.** The leak scanner already covers packet emission and rendered memory. Transcript-level scanning is Task 3.9's R-10 acceptance gate (strategic prompt inputs), not 3.8's.
- **Schema edits (option b only) must keep round-trip tests green.** `tests/meetings/test_schemas.py` already exercises round-trip serialization of `MeetingTranscript`; adding `round_max` requires every existing test to pass a value. Update the fixtures.
- **`audits/*` are read-only artifacts.** Do not edit any audit report; this task addresses C-3, it does not amend the record.

**Ready-to-paste prompt:** `agent_prompts/task-3-8-meeting-state-machine.md`

### Task 3.9 — Strategic reasoner
**Branch:** `phase-3-strategic-reasoner`
**Depends on:** 3.8 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §6.6
**Complexity:** Medium

agents/strategic/reasoner.py - wires render_for_prompt -> LLM -> parsed
structured outputs.

**Files in scope:**
- agents/strategic/reasoner.py
- tests/agents/test_strategic_reasoner.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Strategic reasoner calls `render_for_prompt`, invokes `LLMClient`, and parses structured outputs.
- [ ] Strategic calls occur only at meetings or specified trigger points.
- [ ] Tests use `llm.fake_provider` and make no network calls.
- [ ] No imports from engine/ under agents/.
- [ ] No LLM calls in agents/tactical/.
- [ ] **R-10 acceptance gate for strategic prompt inputs (per `audits/audit-2026-05-15-0225-reconciled.md` §R-10):** The packet field/value leak scanners from `eval/leak_test.py` (`_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values`, or their canonical Phase 3 successors) are reused against the strategic prompt inputs the reasoner assembles before they reach `LLMClient`. `tests/agents/test_strategic_reasoner.py` includes at least one planted negative test pinning that the scanner trips on a forbidden role-bearing string injected into a prompt input.
- [ ] `uv run mypy --strict agents llm meetings` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §4.4 + §6.6. Strategic reasoner pattern: render_for_prompt(memory) → llm_client.complete(prompt) → parse_structured_output(...) → return ReportDocument | Statement | VoteBallot. Tests use the fake provider; no network.

**Ready-to-paste prompt:** `agent_prompts/task-3-9-strategic-reasoner.md`

### Task 3.10 — Voting
**Branch:** `phase-3-voting`
**Depends on:** 3.9 merged
**Section refs:** DESIGN.md §5.5
**Complexity:** Small

meetings/voting.py per §5.5.

**Files in scope:**
- meetings/voting.py
- tests/meetings/test_voting.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Voting tally and uncertainty-aware skip behavior match DESIGN.md §5.5.
- [ ] `VoteBallot` structured output is parsed and tallied.
- [ ] Ballots are publicly logged in `MeetingResult` after meeting resolution.
- [ ] Relevant voting tests pass.
- [ ] `uv run mypy --strict meetings agents` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §5.5. Tally votes (target | SKIP); apply confidence threshold from §4.6; return ejection or skip. No LLM here — voting logic is mechanical; the *ballot* is LLM-produced (3.7).

**Ready-to-paste prompt:** `agent_prompts/task-3-10-voting.md`

### Task 3.11 — Contradiction detection
**Branch:** `phase-3-contradiction-detection`
**Depends on:** 3.10 merged
**Section refs:** DESIGN.md §5.4, DESIGN.md §6.4
**Complexity:** Medium

meetings/transcript.py::detect_contradictions per §5.4 + §6.4.

**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `detect_contradictions` flags incompatible alibi and saw-player claims.
- [ ] Contradiction flags are information, not verdicts.
- [ ] Detected contradictions are represented in shared schemas and can be surfaced to rendered memory.
- [ ] Relevant transcript tests pass.
- [ ] `uv run mypy --strict meetings agents` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §5.4 + §6.4. Index alibi claims by (agent, tick_range, location); cross-reference with `saw_player` observations; emit `ContradictionRef` objects. Detector is data, not verdict — flags feed back into the rendered memory view (3.3).

**Ready-to-paste prompt:** `agent_prompts/task-3-11-contradiction-detection.md`

### Task 3.12 — Meeting/orchestrator integration
**Branch:** `phase-3-meeting-orchestrator-integration`
**Depends on:** 3.11 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4
**Complexity:** Integration

Apply `MeetingResult` through the orchestrator, resume gameplay, and record
meeting artifacts in replay/eval records.

**Files in scope:**
- orchestrator/game.py
- orchestrator/replay.py
- tests/orchestrator/test_meeting_integration.py
- tests/orchestrator/test_replay_meetings.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Orchestrator applies `MeetingResult` ejection/skip outcomes to engine-owned world state.
- [ ] Gameplay resumes after meetings with tick/cooldown behavior matching DESIGN.md §3.1 and §5.1.
- [ ] Replay records meeting transcripts, ballots, contradiction flags, prompt versions, and LLM cost metadata.
- [ ] Engine remains pure; MeetingManager does not mutate engine state directly.
- [ ] **R-9 acceptance gate (per `audits/audit-2026-05-15-0225-reconciled.md` §R-9):** `ReplayEntry` — or its Phase 3 successor introduced by this task — records meeting transcripts, prompt versions, LLM outputs, and cost metadata per DESIGN.md §11.4. The replay-determinism test exercises at least one long-horizon replay (≥ 200 ticks or one full meeting cycle, whichever is longer) and asserts byte-for-byte identity. The existing short-horizon byte-identical test from Task 2.8 (`tests/orchestrator/test_game.py:139-155`) is preserved as a fast smoke check; it is not replaced.
- [ ] Relevant integration tests pass with fake LLM outputs.
- [ ] `uv run mypy --strict engine observation agents meetings orchestrator llm` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §3.1 + §11.4. The orchestrator owns the engine ↔ MeetingManager handoff: when the engine returns `phase == "MEETING"`, dispatch to MeetingManager, receive a `MeetingResult`, apply it to engine-owned state via a new engine function `apply_meeting_result(state, result)`, and resume. Replay log gains LLM-output records for replay determinism.

**Integration risk:**

This is the Phase 3 convergence point. It depends on tasks 3.1–3.11 plus 2.8.

- Determinism: replay must record LLM outputs alongside actions   and replay must re-use them, not re-call the model. Verify   with a determinism test that runs the same seed twice and   asserts byte-identical replay logs.
- Memory consistency: meeting outcomes must update each agent's   belief state. Without this, post-meeting reasoning is stale.
- Phase boundary: do not let MeetingManager touch engine state   directly — every state change goes through the orchestrator.

**Ready-to-paste prompt:** `agent_prompts/task-3-12-meeting-orchestrator-integration.md`

## Merge Criteria
- 50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI and real provider only in explicit local/eval runs.
- Impostor win rate in [25%, 65%] band.
- Cost per game <= $0.30 or provider equivalent.
- Meeting transcripts are human-readable.
- Replay/eval records include meeting artifacts, prompt versions, and LLM cost metadata.
