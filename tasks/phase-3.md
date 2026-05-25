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

### Task 3.9 — Strategic reasoner + sub-phase C integration substrate
**Branch:** `phase-3-strategic-reasoner`
**Depends on:** 3.8 merged
**Section refs:** DESIGN.md §4.4, DESIGN.md §6.6
**Complexity:** Integration

Wire the strategic reasoner (`render_for_prompt` → `LLMClient` → parsed
structured output) AND land four integration-substrate deliverables that
the post-3.8 audit identified as required infrastructure for sub-phase C:

1. **Strategic reasoner** at `agents/strategic/reasoner.py` — the
   primary deliverable. Wraps the rendered memory, the four prompt
   templates from Tasks 3.4–3.7, and the LLM client into a single
   reasoner that produces `ReportDocument`, `Statement`, or `VoteBallot`.
2. **Jinja loader for the four `.j2` templates (C-4 from
   `audits/audit-2026-05-16-2239-claude.md`).** The four prompt
   templates at `agents/strategic/prompts/*.j2` currently have zero CI
   coverage. This task introduces a strict-undefined Jinja loader plus
   per-template smoke tests so a `{% endfor %}` typo or wrong-kwarg-name
   regression is caught in CI rather than at the first live-provider
   meeting.
3. **`BudgetedLLMClient` adapter (C-5 from
   `audits/audit-2026-05-16-2239-claude.md`).** `MeetingManager`
   currently takes a raw `LLMClient` with no budget tracking. This task
   introduces an adapter at `llm/budgeted_client.py` that wraps any
   `LLMClient` and enforces `GameBudget.preflight()` +
   `GameBudget.charge_response()` around every `complete()` call. The
   strategic reasoner uses the adapter by default; `MeetingManager` is
   constructed with it where Task 3.9 wires the meeting flow.
4. **Two carried-over coverage pins (L-1 and L-2 from the post-3.3
   audit, still open after sub-phase B).** L-1: budget cap-slack
   boundary test. L-2: `last_seen` suffix on confirmed-dead player.
   Both land in this task because the work touches budget and
   rendered-memory surfaces.
5. **Token-budget contract awareness (C-2 from the post-3.3 audit,
   resolved via DESIGN.md edit before dispatch).** DESIGN.md §6.6 now
   documents the non-elastic carve-out (role + tasks-completed +
   beliefs + contradictions always retained; only observations are
   elastic). The reasoner must respect this documented contract; no
   DESIGN.md edits required from the implementing agent.

The C-1 R-10 scanner-reuse hedge from the post-3.3 audit is closed by
this task's existing R-10 acceptance gate (which already requires
direct import of `_assert_no_recursive_hidden_fields` and
`_assert_no_role_bearing_values` from `eval/leak_test.py`). The
implementing agent must NOT re-implement the scanners; direct import
only.

**Files in scope:**
- agents/strategic/reasoner.py
- agents/strategic/prompts/__init__.py
- agents/strategic/prompts/loader.py
- llm/budgeted_client.py
- tests/agents/test_strategic_reasoner.py
- tests/agents/test_strategic_prompts.py
- tests/llm/test_budgeted_client.py
- tests/llm/test_budget.py
- tests/agents/test_memory_rendering.py

**Files NOT in scope:**
- engine/
- engine/maps/
- observation/
- orchestrator/
- agents/tactical/
- agents/perception.py
- agents/runtime.py
- agents/base.py
- agents/memory/store.py
- agents/memory/episodic.py
- agents/memory/working.py
- agents/memory/beliefs.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/impostor_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/output_schemas.py
- meetings/
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
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
- tests/agents/test_crewmate_policy.py
- tests/agents/test_impostor_policy.py
- tests/agents/test_pathing.py
- tests/agents/test_perception.py
- tests/agents/test_memory.py
- tests/agents/test_runtime.py
- tests/llm/test_client.py
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/engine/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **Strategic reasoner — primary deliverable.** `agents/strategic/reasoner.py` exposes a `StrategicReasoner` class (or equivalent) that takes an `AgentMemory`, an `LLMClient` (typically wrapped by `BudgetedLLMClient`), and the four prompt callables. It produces `ReportDocument`, `Statement`, or `VoteBallot` instances via the pipeline `render_for_prompt(memory) → load_template(...).render(...) → llm_client.complete(prompt, schema=...) → parsed_output`. Strategic calls occur only at meetings or specified trigger points (kill-witnessed, body-found); never inside `agents/tactical/`.
- [ ] **C-4 — Jinja loader with strict-undefined behavior.** `agents/strategic/prompts/loader.py` (or `__init__.py`) exposes a Jinja `Environment` configured with `autoescape=False, undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True`. It loads templates from the `agents/strategic/prompts/` directory and exposes one named callable per template (e.g. `crewmate_report_prompt`, `impostor_report_prompt`, `accusation_round_prompt`, `vote_ballot_prompt`). Strict-undefined ensures a typo'd variable name raises at render time rather than silently producing an empty string.
- [ ] **C-4 — Per-template smoke tests with Pydantic validation.** `tests/agents/test_strategic_prompts.py` exercises each of the four templates with realistic inputs (a stub rendered-memory string, stub transcript, stub schema). Each test asserts the rendered output (a) is non-empty, (b) contains the expected version-marker substring, and (c) parses cleanly through the corresponding Pydantic schema using `FakeProvider` for the LLM call. A `{% endfor %}` typo, missing kwarg, or schema-incompatible output must cause the test to fail.
- [ ] **C-5 — `BudgetedLLMClient` adapter.** `llm/budgeted_client.py` defines a `BudgetedLLMClient` class wrapping any `LLMClient` plus a `GameBudget`. Each `complete()` call invokes `budget.preflight(estimated_cost_usd)` before the underlying call and `budget.charge_response(actual_cost_usd)` after. If `preflight` raises `BudgetExceededError`, the error propagates without invoking the underlying client. The adapter conforms to the same `LLMClient` Protocol so consumers (including `MeetingManager`) accept it without signature changes.
- [ ] **C-5 — Meeting-ceiling budget test.** `tests/llm/test_budgeted_client.py` exercises a sequence of `complete()` calls whose cumulative cost approaches and then exceeds a configured budget cap. The test asserts `BudgetExceededError` propagates from the `preflight` check, NOT from silent truncation, and NOT after the underlying client has been called. At least one of these tests drives the adapter through a `MeetingManager`-shaped flow (multiple calls in sequence, fake provider, cumulative spend tracked) to confirm the integration path works end-to-end.
- [ ] **C-2 — Reasoner respects DESIGN.md §6.6 non-elastic carve-out.** DESIGN.md §6.6 was updated before dispatch to document that role + tasks-completed + beliefs + contradictions are always retained (non-elastic); only observations are elastic and drop salience-sorted. The reasoner must read this documented contract — it does NOT need to re-implement elasticity for beliefs/contradictions. If a meeting prompt would push past the model's context window, that is a sub-phase C operational concern (handled by the orchestrator passing a sane budget), not a reasoner-side defect. The implementing agent does NOT edit DESIGN.md.
- [ ] **L-1 — Budget cap-slack boundary pin.** `tests/llm/test_budget.py` gains ~10 LOC of regression: assert `cap=0.30, charge=0.30 + 1e-3` raises and `cap=0.30, charge=0.30 + 1e-9` does not. The test names the slack constant by inspection and pins the documented behavior so a future silent slack-widening (e.g. `1e-6` → `1e-3`) cannot pass CI.
- [ ] **L-2 — `last_seen` confirmed-dead suffix pin.** `tests/agents/test_memory_rendering.py` gains ~15 LOC of regression: record a `saw_player` event plus a `saw_body` event for the same player id, render via `render_for_prompt`, assert the `(last seen in ROOM at tick N)` suffix appears on the dead player's belief line. The test must fail if a future refactor silently suppresses `last_seen` for confirmed-dead players.
- [ ] **R-10 acceptance gate for strategic prompt inputs (per `audits/audit-2026-05-15-0225-reconciled.md` §R-10 and closing C-1 from `audits/audit-2026-05-16-2239-claude.md`):** The packet field/value leak scanners from `eval/leak_test.py` (`_assert_no_recursive_hidden_fields` and `_assert_no_role_bearing_values`) are imported **directly** and reused against the strategic prompt inputs the reasoner assembles before they reach `LLMClient`. Do NOT re-implement the scanners — direct import only. `tests/agents/test_strategic_reasoner.py` includes at least one planted negative test pinning that the scanner trips on a forbidden role-bearing string injected into a prompt input.
- [ ] Strategic calls occur only at meetings or specified trigger points.
- [ ] Tests use `llm.fake_provider` and make no network calls.
- [ ] No imports from `engine/` under `agents/`.
- [ ] No LLM calls in `agents/tactical/`.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

See DESIGN.md §4.4 + §6.6 for the strategic-reasoner shape. The pipeline is `render_for_prompt(memory) → load_template(...).render(...) → llm_client.complete(prompt) → parse_structured_output(...) → ReportDocument | Statement | VoteBallot`. All five new deliverables compose:

```
                   ┌────────────────────────────────────┐
                   │  StrategicReasoner                 │
                   │  ┌──────────────────────────────┐  │
                   │  │ render_for_prompt(memory)    │  │  ← reads composite memory
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ load_template(name)          │  │  ← Jinja loader (C-4)
                   │  │   .render(memory, ctx, ...)  │  │
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ BudgetedLLMClient.complete   │  │  ← C-5 adapter
                   │  │   (preflight + charge)       │  │
                   │  └──────────────┬───────────────┘  │
                   │                 ▼                  │
                   │  ┌──────────────────────────────┐  │
                   │  │ Pydantic parse → schema      │  │  ← schemas from 3.2
                   │  └──────────────────────────────┘  │
                   └────────────────────────────────────┘
```

**C-4 — Jinja loader.** Use Jinja2's `Environment` with these settings:

```python
# agents/strategic/prompts/loader.py
from jinja2 import Environment, FileSystemLoader, StrictUndefined

_ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent),
    autoescape=False,           # prompts are plain text, not HTML
    undefined=StrictUndefined,  # missing kwargs raise instead of rendering empty
    trim_blocks=True,
    lstrip_blocks=True,
)

def crewmate_report_prompt(**kwargs: object) -> str:
    return _ENV.get_template("crewmate_report.j2").render(**kwargs)

# ... three more per-template callables, one per .j2 file.
```

The per-template callable signature matches the `MeetingManager` Protocol expectations from Task 3.8. Do NOT modify the `.j2` files themselves — they are out of scope. If a template needs a kwarg the current schema does not provide, surface in `## Decisions` rather than editing the template.

**C-5 — BudgetedLLMClient adapter.** The cleanest pattern:

```python
# llm/budgeted_client.py
class BudgetedLLMClient:
    def __init__(self, *, inner: LLMClient, budget: GameBudget) -> None:
        self._inner = inner
        self._budget = budget

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        **kwargs: object,
    ) -> LLMResponse:
        # Preflight raises BudgetExceededError if the estimated cost would
        # push us past the cap. Never invoke the underlying client if
        # preflight fails — that would be a silent overrun.
        estimated_cost = self._estimate_cost(prompt, max_tokens)
        self._budget.preflight(estimated_cost)
        response = await self._inner.complete(
            prompt=prompt, schema=schema, max_tokens=max_tokens,
            temperature=temperature, **kwargs,
        )
        self._budget.charge_response(response.cost_usd)
        return response
```

The adapter implements the same `LLMClient` Protocol as `AnthropicClient` and `FakeProvider`, so consumers (including `MeetingManager`) accept it without signature changes.

**L-1 — Budget slack pin.** Read `llm/budget.py:42` (or wherever `_COST_USD_CAP_SLACK` lives) and inspect the constant's value. The test pins the documented behavior at the boundary:

```python
# tests/llm/test_budget.py — sketch
class TestSlackBoundary:
    def test_charge_exceeding_slack_raises(self) -> None:
        budget = GameBudget(cost_usd_cap=0.30)
        with pytest.raises(BudgetExceededError):
            budget.charge_response(0.30 + 1e-3)

    def test_charge_within_slack_does_not_raise(self) -> None:
        budget = GameBudget(cost_usd_cap=0.30)
        budget.charge_response(0.30 + 1e-9)  # no raise
```

**L-2 — `last_seen` on confirmed-dead pin.** Construct a memory state with a `saw_player` event and a `saw_body` event for the same player id, render via `render_for_prompt`, and assert the `(last seen in ROOM at tick N)` suffix appears:

```python
# tests/agents/test_memory_rendering.py — sketch
def test_last_seen_suffix_renders_for_confirmed_dead_player() -> None:
    memory = AgentMemory(...)
    memory.episodic.record_saw_player(player_id="p-2", room="MEDBAY", tick=10)
    memory.episodic.record_saw_body(victim_id="p-2", body_id="body-p-2-15", tick=15)
    memory.beliefs.set_suspicion("p-2", 0.5)
    rendered = render_for_prompt(memory, token_budget=8000)
    assert "(last seen in MEDBAY at tick 10)" in rendered
```

**R-10 + C-1 — Direct scanner import.** The R-10 gate from the May-15 audit and C-1 from the post-3.3 audit both require the leak scanners to be imported directly from `eval/leak_test.py`, not re-implemented. Do NOT write a Phase-3 successor; the existing helpers are the canonical scanners. The Task 3.3 implementation set the precedent — follow it.

**Public types introduced:**

- `agents.strategic.reasoner.StrategicReasoner`
- `llm.budgeted_client.BudgetedLLMClient`

**Integration risk:**

This task is the convergence point for sub-phase C. It wires composite memory + four prompt templates + LLM client + budget into one reasoner.

- **Determinism.** The reasoner runs against the fake provider in CI. Same memory state + same prompt template + same fake provider → same parsed output. Verify with at least one test that runs the same reasoning twice and asserts byte-identical outputs.
- **Engine isolation.** `agents/strategic/reasoner.py` does NOT import from `engine/`. The reasoner consumes shapes already inside `agents/memory/`, `meetings/schemas.py`, and `llm/`. Confirm with `uv run lint-imports`.
- **Cross-provider portability preserved.** `BudgetedLLMClient` implements the same `LLMClient` Protocol as `AnthropicClient` and `FakeProvider`. It does not leak Anthropic-specific concepts. Verify with `git grep -nE "anthropic|cache_control|extended_thinking" llm/budgeted_client.py tests/llm/test_budgeted_client.py` returning empty.
- **`MeetingManager` integration.** Task 3.8 constructed `MeetingManager` with a raw `LLMClient`. After Task 3.9, the reasoner constructs `MeetingManager` with a `BudgetedLLMClient` instance. The `MeetingManager.__init__` signature does not change — the budget is transparent to it. If the implementing agent finds they need to change `meetings/manager.py`, that is out-of-scope drift; stop and surface in `## Questions`.
- **`.j2` templates remain frozen.** The four `.j2` files at `agents/strategic/prompts/` are out of scope. The Jinja loader reads them as-is; do not edit the templates to make kwarg names align. If a kwarg drift exists, surface in `## Decisions` so the next hygiene task can address it.
- **Token-budget contract documented in DESIGN.md §6.6 before dispatch.** The implementing agent reads the carve-out and respects it; no DESIGN.md edits. If the documented contract appears wrong during implementation, stop and surface in `## Questions`.
- **`audits/*` are read-only artifacts.** Do not edit any audit report.

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

### Task 3.13 — Production meeting wire-up (close R-1 + R-2 from the Pre-Phase-4 reconciled audit)
**Branch:** `phase-3-public-meeting-wireup`
**Depends on:** 3.12 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §5.1, DESIGN.md §11.4
**Complexity:** Medium

Close the two High findings and two related Concerns identified by
`audits/audit-2026-05-25-0414-reconciled.md` §10, all of which describe
the same underlying gap: Tasks 3.9–3.12 built the meeting machinery and
the budgeted-LLM-client adapter as correct, isolated, well-tested
components — but no production entry-point actually wires them
together. The public CLI (`scripts/run_game.py`,
`scripts/run_tournament.py`, `eval/balance_eval.py`) constructs
`HeadlessGame` without a `meeting_runner=` kwarg, so the engine's
`MEETING` phase falls through to the legacy `MEETING_PHASE_REACHED`
outcome. A reconstructed 100-game tournament at the post-3.12 HEAD
produced `meeting_entries=0` across 100 replay files: meetings do not
fire from any public path. Separately, `BudgetedLLMClient` exists with
20 unit tests but `grep -rn "BudgetedLLMClient" orchestrator/ meetings/
agents/strategic/ scripts/ eval/balance_eval.py` returns only two
docstring references — production never constructs one, so the
`≤ $0.30/game` merge criterion can only be measured post-hoc from
replay logs, not enforced at call time.

This task closes:

- **R-1 [High]** — public CLI / tournament harness still pauses at
  `MEETING_PHASE_REACHED`.
- **R-2 [High]** — `BudgetedLLMClient` + `GameBudget` not wired into
  the orchestrator / meeting / strategic-reasoner production paths.
- **R-5 [Concern]** — no end-to-end test routes through the canonical
  `llm.fake_provider.FakeProvider`. Folds into R-1 for free by using
  `FakeProvider` as the default provider during the wire-up.
- **R-6 [Concern]** — no helper for per-game cost aggregation from a
  replay log. ~5-LOC helper the real-provider 50-game eval will need
  immediately after this task lands.

**Explicitly out of scope:**

- **R-3 [Concern]** (per-call `prompt_version` on `LLMCallRecord`).
  Defer to the real-provider eval owner — meeting-level mapping is
  currently functionally sufficient.
- **R-4 [Concern]** (`StrategicReasoner` defined but unused;
  defense-in-depth scanner bypassed in production meeting flow).
  Primary leak protection (observation packet scanning) is intact and
  passed the 100-log live tournament scan with zero violations.
  Reasoner consolidation is a significant refactor and warrants its
  own task if pursued; this task does not unify the meeting flow
  through `StrategicReasoner`.

**Wire-up shape: option (b) from the reconciled audit's recommended
action.** Make the meeting runner the production default; quarantine
the legacy `MEETING_PHASE_REACHED` outcome behind an explicit opt-out
that only Phase 2 byte-identity tests (`tests/orchestrator/test_game.py`
and similar) use. The public CLI never reaches `MEETING_PHASE_REACHED`.
This is cleaner than option (a) (a `--enable-meetings` flag defaulting
on) because it removes a backward-compat surface that exists only to
keep the pre-Task-3.12 legacy path runnable, and the byte-identity
tests already have a reason to opt out — they want engine-only replay,
not LLM-driven replay.

**Files in scope:**
- scripts/run_game.py
- scripts/run_tournament.py
- eval/balance_eval.py
- orchestrator/game.py
- orchestrator/replay.py
- tests/orchestrator/test_meeting_integration.py
- tests/eval/test_balance_eval.py
- tests/llm/test_budgeted_client.py

**Files NOT in scope:**
- engine/
- observation/
- agents/tactical/
- agents/perception.py
- agents/memory/
- agents/runtime.py
- agents/base.py
- agents/strategic/reasoner.py
- agents/strategic/prompts/
- agents/strategic/output_schemas.py
- meetings/manager.py
- meetings/schemas.py
- meetings/transcript.py
- meetings/voting.py
- llm/client.py
- llm/provider.py
- llm/fake_provider.py
- llm/cache.py
- llm/budget.py
- llm/budgeted_client.py
- api/
- frontend/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/observation/
- tests/meetings/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/engine/
- tests/eval/test_leak.py
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_game.py
- tests/orchestrator/test_replay.py
- tests/orchestrator/test_replay_meetings.py
- tests/orchestrator/test_seeder.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-1 — `HeadlessGame` meeting runner is the production default.** `scripts/run_game.py`, `scripts/run_tournament.py`, and `eval/balance_eval.py::run_balance_eval` all construct `HeadlessGame` with a `meeting_runner=` kwarg by default. The constructed runner is `DefaultMeetingRunner` wrapping the canonical `llm.fake_provider.FakeProvider` (R-5 closure: this is the canonical fake provider used through the orchestrator path). Construct one runner + one `GameBudget` per game; do not share runners or budgets across games in a tournament.
- [ ] **R-2 — `BudgetedLLMClient` wraps every production LLM call.** `orchestrator/game.py::DefaultMeetingRunner.__init__` (or an equivalent factory in the wire-up surface) accepts an optional `budget: GameBudget | None = None` kwarg. When `budget` is provided, the runner wraps `llm_client` in `BudgetedLLMClient(inner=llm_client, budget=budget)` before passing it through `_RecordingLLMClient` to `MeetingManager`. The three public entry-points always construct a `GameBudget` and pass it to the runner; the cost cap is enforced at call time, not post-hoc.
- [ ] **`MEETING_PHASE_REACHED` quarantined behind opt-out.** `HeadlessGame.run` continues to return `MEETING_PHASE_REACHED` when `meeting_runner=None`, but the three public entry-points never construct that path. The branch is reachable only by tests that explicitly pass `meeting_runner=None` (e.g. Phase 2 byte-identity tests that want engine-only behavior). Add a comment at the no-runner branch in `orchestrator/game.py` naming this contract: "engine-only opt-out for Phase 2 byte-identity tests; production paths always pass a runner."
- [ ] **R-6 — `compute_cost_usd(path)` helper.** `orchestrator/replay.py` exposes a helper `compute_cost_usd(path: Path) -> float` that walks the replay log and sums `LLMCallRecord.cost_usd` across all `MeetingReplayEntry` rows. ~5–15 LOC. Document the function as the canonical reduction for per-game cost; future eval code (including the real-provider 50-game eval) consumes it.
- [ ] **`eval/balance_eval.py` reframes `MEETING_PHASE_REACHED` bucket.** Since meetings now fire end-to-end from the public tournament path, `MEETING_PHASE_REACHED` should no longer appear as a normal non-decisive outcome bucket. Either: (a) remove the bucket and treat any `MEETING_PHASE_REACHED` in this path as a defect (raise), OR (b) keep the bucket but document that it should be zero after this task lands. Pick one and document in `## Decisions`.
- [ ] **End-to-end CI regression: meetings fire from the public CLI.** `tests/orchestrator/test_meeting_integration.py` adds a regression test that constructs `HeadlessGame` via the same factory path used by `scripts/run_game.py`, runs to completion, and asserts: (a) the replay log contains at least one `MeetingReplayEntry`, (b) the game outcome is NOT `MEETING_PHASE_REACHED`. Use the canonical `FakeProvider`; do not introduce a new inline stub. The test must fail against an implementation that reverts the runner wire-up.
- [ ] **End-to-end CI regression: budget cap propagates from production wire-up.** `tests/llm/test_budgeted_client.py` (or a new file in `tests/orchestrator/`) adds a regression that constructs the production wire-up with a tight `GameBudget` cap (e.g. `$0.01` per game) and runs a single game expected to fire at least one meeting. Assert `BudgetExceededError` propagates from the run-meeting flow, NOT silent truncation, NOT after the underlying client was called more than budget-cap times. The test must fail against an implementation that constructs `MeetingManager` without `BudgetedLLMClient` wrapping.
- [ ] **Tournament smoke after wire-up.** Run `uv run python scripts/run_tournament.py --num-games 10 --start-seed 0 --output-dir /tmp/task-3-13-smoke --max-ticks 1000`. Walk the resulting replay JSONLs (excluding `*.audit.jsonl`) and confirm at least one `MeetingReplayEntry` per game that reached the MEETING phase (most games will). Record the bucket counts, decisive split, and `meeting_entries` total in `## Decisions`.
- [ ] **Per-game cost aggregation works.** Use the new `compute_cost_usd(path)` helper on at least three of the 10 smoke games. Confirm the returned values are non-negative finite floats. Fake-provider costs are zero or near-zero; the helper must still return a sensible number (not crash on empty `LLMCallRecord` lists).
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] No Anthropic-specific concepts leak through the production wire-up. `git grep -nE "anthropic\|cache_control\|extended_thinking" orchestrator/ scripts/ eval/balance_eval.py` returns empty.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The four script edits are sibling shapes: each constructs a runner + budget + budgeted client + `HeadlessGame`. A factory helper in `orchestrator/game.py` (or `scripts/_meeting_factory.py` if you prefer to keep `orchestrator/` minimal) is the cleanest way to avoid duplication. Suggested shape:

```python
# orchestrator/game.py — illustrative; pick exact naming consistent with existing API
def build_default_meeting_runner(
    *,
    llm_client: LLMClient | None = None,
    budget: GameBudget | None = None,
) -> DefaultMeetingRunner:
    """Construct the production default meeting runner.

    If ``llm_client`` is None, the canonical ``FakeProvider`` is used.
    If ``budget`` is provided, wraps the LLM client in
    ``BudgetedLLMClient`` so the cap is enforced at call time.

    Production callers (``scripts/run_game.py``,
    ``scripts/run_tournament.py``, ``eval/balance_eval.py``) always pass
    a fresh ``GameBudget`` per game.
    """
    inner: LLMClient = llm_client or FakeProvider()
    client: LLMClient = (
        BudgetedLLMClient(inner=inner, budget=budget) if budget else inner
    )
    return DefaultMeetingRunner(
        llm_client=client,
        # ... existing kwargs unchanged
    )
```

Then each script becomes:

```python
# scripts/run_game.py — illustrative
runner = build_default_meeting_runner(budget=GameBudget(cost_usd_cap=0.30))
game = HeadlessGame(
    seed=args.seed,
    game_map=load_canonical_map(),
    replay_path=Path(args.replay_path),
    meeting_runner=runner,
    max_ticks=args.max_ticks,
)
```

`scripts/run_tournament.py` and `eval/balance_eval.py::run_balance_eval` follow the same pattern, but construct a NEW runner + budget per game (do not share across games in a tournament — the budget must reset, and the recording LLM client may carry per-game state).

**The `compute_cost_usd(path)` helper** is mechanical:

```python
# orchestrator/replay.py — illustrative
def compute_cost_usd(path: Path) -> float:
    """Sum LLM cost across all meeting entries in a replay log.

    Returns 0.0 for replay logs with no meeting entries (e.g. games
    that ended before any meeting fired).
    """
    return sum(
        call.cost_usd
        for entry in read_meeting_entries(path)
        for call in entry.llm_calls
    )
```

**Quarantining `MEETING_PHASE_REACHED`** is just a documentation comment plus the absence of any production caller relying on it. The branch at [orchestrator/game.py:645-651](orchestrator/game.py#L645) stays in place — Phase 2 byte-identity tests still pass `meeting_runner=None`. Add a comment naming the contract:

```python
# orchestrator/game.py
if state.phase == "MEETING" and self._meeting_runner is None:
    # Engine-only opt-out for Phase 2 byte-identity tests. Production
    # paths (scripts/run_*.py, eval/balance_eval.py) always pass a
    # meeting_runner; reaching this branch from a production caller
    # indicates the wire-up regressed.
    return HeadlessGameResult(
        final_state=state,
        outcome="MEETING_PHASE_REACHED",
        # ...
    )
```

**For the tight-cap regression test**, choose a cap small enough that the first meeting trips it (e.g. `$0.01`). The fake provider reports near-zero cost per call, so to reliably trip the cap you may need to either (a) configure `FakeProvider` with a non-zero cost-per-call, (b) construct a tight cap relative to whatever cost the fake reports, or (c) use a synthetic recorded-cost client. Read `llm/fake_provider.py` to see what cost it reports; pick the simplest path that makes the test fail-loud on a missing `BudgetedLLMClient` wrap. Document the choice in `## Decisions`.

**Public types introduced:**

- `orchestrator.game.build_default_meeting_runner` (or wherever the factory lands)
- `orchestrator.replay.compute_cost_usd`

**Integration risk:**

This task is the production wire-up that closes the gap between the substrate Phase 3 built (Tasks 3.1–3.12) and the merge criteria. Low risk per file; high signal value.

- **Phase 2 byte-identity tests must continue to pass.** Those tests intentionally construct `HeadlessGame` with `meeting_runner=None` to exercise the engine-only path. The quarantine comment documents this opt-out; the no-runner branch in `orchestrator/game.py` stays in place. Verify with `uv run pytest tests/orchestrator/test_game.py -v`.
- **Determinism preserved.** Adding `BudgetedLLMClient` to the production wire-up does not introduce randomness — the adapter is a transparent wrapper around `LLMClient`. The 200/500-tick byte-identity tests must still pass.
- **Tournament balance may shift.** Once meetings fire end-to-end from the public path, the tournament's decisive split will likely change (meetings introduce additional win paths: vote-ejection of the impostor, or impostor surviving a vote and continuing to kill). The post-3.8 baseline was `crew_wins=58 impostor_wins=35 tick_budget_reached=0 meeting_phase_reached=7`. After this task, expect `meeting_phase_reached:0` and the decisive split to redistribute. If the shift puts either decisive side below the Phase 2 Merge Criterion (> 20% of decisive), surface in `## Decisions` — do NOT silently accept a regression of the Phase 2 gate. The Phase 2 gate may need rephrasing once meetings are real (Phase 3 introduces new win paths), but that is a separate Phase-4-or-later concern, not a workaround inside this PR.
- **Cost helper precision.** `compute_cost_usd` returns a float; the real-provider eval will compare against `0.30`. Use Python's standard float arithmetic; do not introduce `Decimal` for this. The `≤ $0.30` cap has finite precision built into `_COST_USD_CAP_SLACK`.
- **`MEETING_PHASE_REACHED` literal must not be deleted.** It is still a valid `HeadlessGameResult.outcome` value for the engine-only test path. Removing it would break Phase 2 tests.
- **`eval/balance_eval.py` reframing.** The `MEETING_PHASE_REACHED` bucket was a Phase 2 placeholder. After this task, it should always be 0 from the public tournament path. Pick option (a) or (b) above; either way, document the change.
- **`audits/*` are read-only artifacts.** Do not edit any audit report.

**Ready-to-paste prompt:** `agent_prompts/task-3-13-production-meeting-wireup.md`

### Task 3.14 — Real-provider transport wire-up
**Branch:** `phase-3-real-provider-transport`
**Depends on:** 3.13 merged
**Section refs:** DESIGN.md §7, DESIGN.md §10.4
**Complexity:** Medium

Close the two compounding gaps surfaced by the Pre-Phase-4 real-provider
eval report (`audits/audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md`),
which exited at pre-flight with verdict **Pre-flight failed — live
provider unreachable**. Total eval spend so far: $0.00. The eval's new
direct-sanity-call gate caught the failure before any tournament-wrapped
API spend.

**Gap A — `AILIBI_LLM_PROVIDER` is ignored by the production path.**
`orchestrator/game.py::build_default_meeting_runner` at line 342 defaults
a missing `llm_client` to `FakeProvider()` rather than to
`build_default_client()`. The public scripts (`scripts/run_game.py`,
`scripts/run_tournament.py`) and `eval/balance_eval.py::run_balance_eval`
all call the factory without `llm_client=`, so the env-var selector
exists but never flows through the public CLI.

**Gap B — `AnthropicClient` has no real transport.**
`llm/provider.py::_default_send` is a one-line
`raise RuntimeError("...real Anthropic SDK is not wired in this build...")`.
`grep -rn "import anthropic" --include='*.py'` returns zero hits outside
`.venv`; the `anthropic` SDK is not declared in `pyproject.toml`
dependencies. The adapter scaffold exists from Task 3.1, but the SDK
transport was never wired in — CI never noticed because every test uses
`FakeProvider`, and prior audits explicitly forbade real-provider calls.

This task closes both gaps so the real-provider eval can be re-attempted.
No new merge criteria are introduced; the existing Phase 3 Merge
Criteria become *measurable* after this task lands.

**Files in scope:**
- pyproject.toml
- uv.lock
- llm/provider.py
- orchestrator/game.py
- tests/llm/test_real_provider.py

**Files NOT in scope:**
- engine/
- observation/
- agents/
- meetings/
- llm/client.py
- llm/budget.py
- llm/budgeted_client.py
- llm/cache.py
- llm/fake_provider.py
- llm/README.md
- llm/__init__.py
- orchestrator/replay.py
- orchestrator/scheduler.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- orchestrator/seeder.py
- scripts/run_game.py
- scripts/run_tournament.py
- eval/
- api/
- frontend/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- DESIGN.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/llm/test_client.py
- tests/llm/test_budget.py
- tests/llm/test_budgeted_client.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **Gap B step 1 — `anthropic` declared as a dependency.** Add the `anthropic` Python SDK to `pyproject.toml` `dependencies` using an **exact version pin** to match the project's existing convention (every other dep in the block is exact-pinned, e.g. `fastapi==0.136.1`). Choose a current stable version that supports the `claude-sonnet-4-6` and `claude-haiku-4-5-20251001` model ids. Regenerate `uv.lock` with `uv lock` and commit both files. Document the chosen version + reasoning in `## Decisions`.
- [ ] **Gap B step 2 — `_default_send` implements the real SDK call.** `llm/provider.py::_default_send` becomes a real implementation, NOT a `RuntimeError` stub. The implementation:
  - **Lazy-imports** the `anthropic` package inside the function body (not at module top-level). The existing module docstring at `llm/provider.py:9-11` describes this lazy-import design; honor it. Lazy import keeps the `anthropic` dependency optional at module load time so `FakeProvider`-only test runs and `bash scripts/check.sh` don't require the SDK to be installed (though it will be installed via `uv sync` after `pyproject.toml` changes).
  - Constructs an `anthropic.AsyncAnthropic(api_key=api_key)` client. Reuses the function-scoped client; do not introduce module-level state.
  - Calls `messages.create(model=..., max_tokens=..., temperature=..., messages=[{"role": "user", "content": prompt}])`. Use a single `user` message; the `LLMClient.complete` Protocol surface does not currently carry a system prompt parameter (DESIGN.md §7 / `llm/client.py`).
  - Translates the response into `AnthropicRawResponse(model=..., text=..., input_tokens=..., output_tokens=...)`. The text is the first content block's text. Token counts come from `response.usage.input_tokens` / `response.usage.output_tokens`.
  - The `extended_thinking` and `prompt_caching_beta` parameters are already plumbed through the call signature but stay **no-ops** in this task — wiring them through to the SDK is a separate concern. Document the no-op decision in `## Decisions`.
- [ ] **Gap A — `build_default_meeting_runner` honors `AILIBI_LLM_PROVIDER`.** In `orchestrator/game.py::build_default_meeting_runner`, change the `llm_client=None` fallback from `FakeProvider()` to `build_default_client()` (imported from `llm.provider`). Single-line behavior change: the env-var selector now flows through whenever the factory is called without an explicit `llm_client`. The default case (`AILIBI_LLM_PROVIDER` unset) still produces a `FakeProvider` via `build_default_client`'s own default, so existing tests that rely on the FakeProvider fallback continue to pass without modification. Remove the unused `FakeProvider` import from `orchestrator/game.py` if it becomes unused after the change.
- [ ] **Real-provider round-trip test.** `tests/llm/test_real_provider.py` is a new test file containing at least one test decorated with `@real_provider` (the existing marker defined in `tests/llm/test_client.py`, which wraps `pytest.mark.skipif` keyed on `os.environ.get("AILIBI_RUN_REAL_PROVIDER_TESTS") != "1"`). The test:
  - Imports `real_provider` from `tests.llm.test_client` (or re-defines the same marker locally; either is acceptable).
  - Constructs `AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])` directly (not via `build_default_client`) so the test is self-contained.
  - Calls `await client.complete(prompt="Respond with the single token: OK", schema=None, max_tokens=8, temperature=0.0)`.
  - Asserts `response.text` is a non-empty string, `response.usage.input_tokens > 0`, `response.usage.output_tokens > 0`, `response.cost_usd > 0.0`, `response.model` is a non-empty string. The exact response text is not asserted (LLM output varies).
  - CI continues to skip the test by default (the env-var gate is unset in CI per `llm/README.md`).
- [ ] **Static gates pass without the env var set.** `bash scripts/check.sh` passes on a fresh checkout with `AILIBI_LLM_PROVIDER` unset (and `AILIBI_RUN_REAL_PROVIDER_TESTS` unset). All 667+ existing tests continue to pass; the new `tests/llm/test_real_provider.py` test reports as skipped.
- [ ] **Post-merge sanity check (developer-only; not a CI gate).** After merge, run the direct sanity call from `audits/prompts/pre-phase-4-real-provider-eval-prompt.md` §2 with `AILIBI_LLM_PROVIDER=anthropic` and a real `ANTHROPIC_API_KEY` set. Expected outcome: non-zero `cost_usd`, sensible response text, model id matches `AILIBI_LLM_MEETING_MODEL`. The PR description's `## Decisions` block records the post-merge sanity-call output verbatim (model + cost + response text), with the API key NOT printed.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (with the new test skipped).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The Anthropic Python SDK exposes an async client (`anthropic.AsyncAnthropic`) and a `messages.create` method that returns a typed response. The minimal call shape:

```python
# llm/provider.py — illustrative; pick exact names matching the SDK version chosen
async def _default_send(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    extended_thinking: bool,
    prompt_caching_beta: bool,
) -> AnthropicRawResponse:
    # Lazy import per the design intent at llm/provider.py:9-11. Keeps
    # the SDK optional at module-load time; tests that never touch the
    # real provider don't import it.
    import anthropic

    # extended_thinking and prompt_caching_beta are plumbed through the
    # signature but unused in this task. Wiring them through is a
    # separate concern; document in ## Decisions.
    _ = extended_thinking
    _ = prompt_caching_beta

    client = anthropic.AsyncAnthropic(api_key=api_key)
    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    text_blocks = [
        block.text for block in response.content
        if getattr(block, "type", None) == "text"
    ]
    if not text_blocks:
        raise RuntimeError(
            f"Anthropic returned no text content blocks (model={model!r})"
        )

    return AnthropicRawResponse(
        model=response.model,
        text="".join(text_blocks),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )
```

**Gap A fix is a one-line behavioral change** plus an import swap:

```python
# orchestrator/game.py — current at line 342
inner: LLMClient = llm_client if llm_client is not None else FakeProvider()

# After Gap A fix
inner: LLMClient = llm_client if llm_client is not None else build_default_client()
```

Add `from llm.provider import build_default_client` to the imports; remove `from llm.fake_provider import FakeProvider` if no other reference in the file uses it (the new fallback delegates the env-var routing — including the fake-provider default — to `build_default_client`).

**Real-provider test shape:**

```python
# tests/llm/test_real_provider.py — illustrative
import os
import pytest
from llm.provider import AnthropicClient
from tests.llm.test_client import real_provider  # the existing marker


class TestAnthropicRoundTrip:
    @real_provider
    @pytest.mark.asyncio
    async def test_real_provider_round_trip(self) -> None:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        client = AnthropicClient(api_key=api_key)
        response = await client.complete(
            prompt="Respond with the single token: OK",
            schema=None,
            max_tokens=8,
            temperature=0.0,
        )
        assert response.text, "Expected a non-empty response from the live provider"
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0
        assert response.cost_usd > 0.0
        assert response.model
```

To run this test locally:
```bash
set -a; source .env; set +a
AILIBI_RUN_REAL_PROVIDER_TESTS=1 uv run pytest tests/llm/test_real_provider.py -v
```

CI runs `uv run pytest` without `AILIBI_RUN_REAL_PROVIDER_TESTS=1` and the test is reported as skipped.

**Public types introduced:**
None.

**Integration risk:**

This task closes a substrate gap rather than introducing new behavior. Low risk per file; high signal value (re-enables the real-provider eval).

- **CI must remain free of network calls.** The `@real_provider` marker is the only thing that protects against accidental live calls in CI. Verify by reading the marker definition at `tests/llm/test_client.py` and confirming it gates on the env var. Do NOT introduce a new test that calls the real provider without the marker.
- **`anthropic` SDK version compatibility.** Pin a version that supports the Claude 4-series models (`claude-sonnet-4-6`, `claude-haiku-4-5-20251001`). If the chosen version's `messages.create` signature differs from the illustrative snippet, adjust accordingly; the `AnthropicRawResponse` shape is what consumers depend on, not the SDK call shape.
- **`build_default_client()` behavior preserved.** The function already reads `AILIBI_LLM_PROVIDER` and defaults to `FakeProvider` when unset. Changing the `build_default_meeting_runner` fallback to call `build_default_client()` does NOT change behavior in tests that leave `AILIBI_LLM_PROVIDER` unset — both `FakeProvider()` (the old default) and `build_default_client()` (the new default) produce a `FakeProvider` in that environment. Confirm by running the full test suite before opening the PR.
- **Lazy import is non-negotiable.** If `import anthropic` is moved to module top-level, every module that imports from `llm.provider` (including `orchestrator/game.py` via the new `build_default_client` import) pulls in the SDK at module-load time. This breaks the design principle that fake-provider runs don't depend on the real SDK being installed. Pin via `## Decisions` and confirm with `python -c "import orchestrator.game"` succeeding without `anthropic` installed (i.e., with the dependency present but never actually imported at load time — verify by inspecting the lazy import is inside the function).
- **Post-merge sanity-call verification is part of the PR description, not a CI gate.** The implementing agent runs the sanity call locally after the PR's tests pass and pastes the output verbatim (model, cost, response text) into `## Decisions`. CI cannot run this because CI does not have an API key.
- **Cost from a single sanity call: ~$0.001.** Negligible. The `pytest.mark.real_provider` round-trip test will charge the same when opted into.
- **`audits/*` are read-only artifacts.** Do not edit the Pre-Phase-4 real-provider eval report; this task closes the gaps it surfaces, it does not amend the record.

**Ready-to-paste prompt:** `agent_prompts/task-3-14-real-provider-transport.md`

## Merge Criteria
- 50-game eval: full-LLM games complete end-to-end using fake-provider tests in CI and real provider only in explicit local/eval runs.
- Impostor win rate in [25%, 65%] band.
- Cost per game <= $0.30 or provider equivalent.
- Meeting transcripts are human-readable.
- Replay/eval records include meeting artifacts, prompt versions, and LLM cost metadata.
