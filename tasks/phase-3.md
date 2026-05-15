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
- [ ] `LLMClient` protocol exists.
- [ ] Real provider adapter is behind `LLMClient` protocol.
- [ ] Fake deterministic provider exists for tests and CI.
- [ ] Prompt cache and per-game budget support exist.
- [ ] CI tests use the fake provider and make no network calls.
- [ ] No LLM calls are added to agents/tactical/.
- [ ] `uv run mypy --strict llm agents` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §7 + §10.4 for the LLM-client surface. The fake deterministic provider is the most important piece — it is what every test in CI calls. `LLMClient` is a Protocol; the real and fake providers both implement it. Cache and budget are layered on.

**Ready-to-paste prompt:** `agent_prompts/task-3-1-llm-client.md`

### Task 3.2 — Shared meeting/output schemas
**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A
**Complexity:** Small

Centralize meeting artifacts in meetings/schemas.py. Agent strategic schemas may
re-export or wrap the shared schemas, but must not duplicate independent schema
definitions.

**Files in scope:**
- meetings/schemas.py
- agents/strategic/output_schemas.py
- tests/meetings/test_schemas.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and contradiction/result DTOs match DESIGN.md §5.3 and §5.5.
- [ ] `agents/strategic/output_schemas.py` re-exports or wraps shared meeting schemas without duplicating them.
- [ ] Schemas are suitable for structured LLM output.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant schema tests pass.
- [ ] `uv run mypy --strict agents meetings` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §5.3 + §5.5. `meetings/schemas.py` owns the canonical Pydantic shapes for `ReportDocument`, `Statement`, `VoteBallot`, and `MeetingResult`. `agents/strategic/output_schemas.py` re-exports or wraps these — never duplicate.

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
**Depends on:** 3.3 merged
**Section refs:** DESIGN.md §5.1, DESIGN.md §5.2
**Complexity:** Medium

meetings/manager.py and meetings/transcript.py per §5.1 + §5.2.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py
- tests/meetings/test_manager.py
- tests/meetings/test_transcript.py

**Files NOT in scope:**
- engine/ core rule changes
- orchestrator/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `MeetingManager` follows trigger lifecycle in DESIGN.md §5.1.
- [ ] Protocol implements report intake, accusation rounds, voting, and resolution per DESIGN.md §5.2.
- [ ] Missed deadlines yield default no-statement/no-vote behavior as specified.
- [ ] Manager returns `MeetingResult`; it does not mutate engine state.
- [ ] Relevant meeting tests pass using fake strategic participants.
- [ ] `uv run mypy --strict meetings agents llm` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §5.1 + §5.2. `MeetingManager` is a state machine that moves through report intake → accusation rounds → voting → resolution. It must NOT mutate engine state; it returns a `MeetingResult` that the orchestrator (3.12) applies.

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
