# Agent Prompt — 4.1 FastAPI app skeleton and spectator DTO inventory

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.1 — FastAPI app skeleton and spectator DTO inventory, anchored to DESIGN.md §7, DESIGN.md §1.3, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7, DESIGN.md §1.3, DESIGN.md §11.4
**Complexity:** Medium

Establish the API substrate that every Phase 4 frontend task consumes:
a FastAPI app skeleton, the concrete sanitized DTO inventory in
`api/schemas.py`, route registration with placeholder handlers, and
leak tests that pin down which fields are intentionally exposed. The
DTO design IS the deliverable; routes return `501 Not Implemented` and
get their bodies in 4.2. This split keeps the design lift isolated
from the implementation lift.

**Spectator privilege model.** The replay viewer is a *post-game*
privileged spectator (the analog of a "GM view" in tabletop). Role,
kill attribution, vent network, and impostor-only state are
intentionally exposed because that's what makes a replay watchable.
The firewall (DESIGN.md §1.3) still applies to *agents*; spectator
DTOs are a separate surface. The leak test's purpose is NOT to redact
role — it's to assert that every DTO field is *intentional* and to
prevent accidentally embedding `WorldState`, raw `ReplayEntry`s, or
observation-firewall internals (which would couple frontend to engine
shape and re-introduce leakage paths via copy-paste).

**Replay seed recovery.** Replays are stored as JSONL files whose
filename encodes the seed (`replay-seed-{N}.jsonl`) and whose
`game_id` field is `headless-seed-{N}` (per
[orchestrator/game.py:874](orchestrator/game.py#L874)). Per-tick agent
positions are NOT persisted in the JSONL — only `state_hash` is, plus
the action stream. To produce per-tick position DTOs, the eventual
replay loader (4.2) will re-seed via `seed_initial_state(seed=N)` and
re-apply actions through `advance_tick`. This is a read-only engine
usage, not an engine modification, and is consistent with the "no
engine touches in Phase 4" scope guarantee — we re-use the determinism
contract, we don't change it.

**Out of scope** (explicit decisions deferred):

- **Endpoint bodies.** Task 4.1 registers routes and returns `501`.
  Task 4.2 wires the replay loader and returns real payloads. Splitting
  these keeps DTO review independent from loader implementation review.
- **Per-tick memory + suspicion snapshots.** The replay does not
  capture per-tick memory state; memory is reconstructed on-the-fly
  when `render_for_prompt` runs. The captured `LLMCallRecord.prompt`
  text holds rendered memory only at meeting boundaries. MVP DTOs
  expose `AgentMemoryView` ONLY at meeting boundaries (parsed from or
  paired with the meeting's LLM call records). Between-meeting memory
  is not exposed. Document this constraint in `## Decisions` so the
  ThoughtStream task (4.6) doesn't assume otherwise.
- **WebSocket / live game.** Deferred to Phase 5+ per phase scope.
- **Pagination / cursor APIs.** MVP returns all replay metadata in one
  shot. Pagination lands when there are enough replays for it to matter.
- **OpenAPI schema export tooling.** FastAPI emits OpenAPI by default;
  whether the frontend (4.3) consumes it via `openapi-typescript` or
  hand-authored types is the 4.3 implementing agent's call.

**Files in scope:**
- api/__init__.py
- api/main.py
- api/schemas.py
- api/routes/__init__.py
- api/routes/replays.py
- api/routes/eval.py
- tests/api/__init__.py
- tests/api/test_schemas.py
- tests/api/test_routes.py
- tests/api/test_leak.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- frontend/
- api/ws.py (deferred — no WebSocket in MVP)
- api/routes/games.py (live game streaming deferred)
- api/replay_loader.py (deferred to 4.2)
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
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **FastAPI app skeleton.** `api/main.py` exposes a `create_app() -> FastAPI` factory plus a module-level `app = create_app()`. App registers `api/routes/replays.py` under `/replays` and `api/routes/eval.py` under `/eval`. App boots cleanly: `uv run uvicorn api.main:app --port 8000` returns 200 on `GET /` (return a minimal `{"service": "ailibi-api"}` response) and 404 on unknown paths. No CORS middleware needed for MVP (frontend served via Vite dev proxy in 4.3).
- [ ] **DTO inventory.** `api/schemas.py` defines every DTO listed in the Implementation hint below as a frozen Pydantic v2 model (`model_config = ConfigDict(frozen=True, extra="forbid")`). Each DTO carries a docstring naming its source (which engine/meetings/orchestrator type it shadows) and explicitly listing fields that exist in the source but are deliberately excluded. Discriminated unions use `Field(discriminator="type")` mirroring `meetings.schemas` patterns.
- [ ] **Route registration with placeholders.** `api/routes/replays.py` and `api/routes/eval.py` declare each endpoint with its response_model set to the appropriate DTO. Handler bodies raise `HTTPException(status_code=501, detail="Not implemented in 4.1; lands in 4.2")`. The endpoint signatures are final — 4.2 fills bodies without changing signatures.
- [ ] **Endpoint inventory (registered with 501 bodies):**
  - `GET /replays` → `list[ReplayMetadataView]`
  - `GET /replays/{game_id}` → `ReplayView`
  - `GET /replays/{game_id}/ticks/{tick}` → `TickView`
  - `GET /replays/{game_id}/meetings/{meeting_id}` → `MeetingView`
  - `GET /replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}` → `AgentMemoryView`
  - `GET /eval/cost-summary` → `EvalCostSummaryView`
- [ ] **Leak tests in `tests/api/test_leak.py`.** Static-import-based tests assert:
  - No DTO in `api/schemas.py` imports from `engine.*`, `observation.*`, or `orchestrator.*` (use `import_linter`-style assertions or a simple `inspect.getsource(api.schemas) | grep`).
  - No DTO has a field typed as `WorldState`, `PlayerState`, `BodyState`, `TaskState`, `SabotageState`, `ReplayEntry`, `MeetingReplayEntry`, `LLMCallRecord`, `MeetingResult`, `MeetingTrigger`, `Action`, or any other internal type that wasn't explicitly opted-in to the DTO surface.
  - The expected DTO inventory matches the actual `__all__` in `api/schemas.py` — i.e. someone adding a DTO has to update `__all__` AND a paired exposure-list fixture in the test, making accidental leakage visible in code review.
- [ ] **Round-trip serialization tests in `tests/api/test_schemas.py`.** For each top-level DTO (`ReplayView`, `TickView`, `MeetingView`, `AgentMemoryView`, `EvalCostSummaryView`, `ReplayMetadataView`), construct a fixture instance via direct constructor, `model_dump_json` it, `model_validate_json` it back, and assert equality. Discriminated unions need at least one fixture per variant.
- [ ] **Route registration tests in `tests/api/test_routes.py`.** Using FastAPI's `TestClient`, assert each endpoint above is registered (returns 501, not 404). Assert the OpenAPI schema (`GET /openapi.json`) reflects the documented DTOs (smoke-level: `ReplayMetadataView` appears in the components list, etc.).
- [ ] **API remains a thin adapter.** `api/routes/*.py` files contain ONLY route declarations + 501 placeholders. No business logic, no imports from `engine/`, `observation/`, or `orchestrator/`. (4.2 will need orchestrator import for the loader; that's fine because the loader lives in `api/replay_loader.py`, not in `api/routes/`.)
- [ ] **`Public types introduced` are documented** in the PR description AND in `## Decisions`.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes. (`api/` is not in the strict list yet; add it post-Phase-4 if discipline warrants.)
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The DTO inventory below is the load-bearing artifact. Implement these exactly; do not invent additional fields. Every field maps to a real engine / meetings / replay source and exists because a downstream Phase 4 component (4.4–4.8) needs it. Fields deliberately excluded are listed under "Excludes" — the leak test enforces these.

## Public types this task introduces
- `api.schemas.PositionView`
- `api.schemas.SizeView`
- `api.schemas.RoomView`
- `api.schemas.VentView`
- `api.schemas.EdgeView`
- `api.schemas.MapLayoutView`
- `api.schemas.PlayerView`
- `api.schemas.AgentTickStateView`
- `api.schemas.KillEventView`
- `api.schemas.ReportBodyEventView`
- `api.schemas.SabotageEventView`
- `api.schemas.TaskCompletedEventView`
- `api.schemas.MeetingTriggeredEventView`
- `api.schemas.TickEventView`
- `api.schemas.TickView`
- `api.schemas.SawPlayerView`
- `api.schemas.CompletedTaskObsView`
- `api.schemas.FoundBodyObsView`
- `api.schemas.ObservationClaimView`
- `api.schemas.AlibiClaimView`
- `api.schemas.AccusationClaimView`
- `api.schemas.CorroborationClaimView`
- `api.schemas.StatementClaimView`
- `api.schemas.ReportView`
- `api.schemas.StatementView`
- `api.schemas.ContradictionView`
- `api.schemas.BallotView`
- `api.schemas.LLMCallView`
- `api.schemas.MeetingView`
- `api.schemas.BeliefEntryView`
- `api.schemas.AgentMemoryView`
- `api.schemas.SuspicionEntryView`
- `api.schemas.SuspicionGraphView`
- `api.schemas.ReplayMetadataView`
- `api.schemas.FailedCallView`
- `api.schemas.ReplayView`
- `api.schemas.EvalCostSummaryView`
- `api.main.create_app`
- `api.main.app`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-4-fastapi-app-skeleton` with a title like `task 4.1: fastapi app skeleton and spectator dto inventory`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §1.3, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
