# Agent Prompt — 4.2 Replay loader + endpoint implementation

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.2 — Replay loader + endpoint implementation, anchored to DESIGN.md §7, DESIGN.md §11.4, DESIGN.md §1.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-replay-endpoint`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4, DESIGN.md §1.3
**Complexity:** Medium

Implement the replay loader and swap in real route handlers for the
DTOs defined in 4.1. The endpoint signatures from 4.1 are final; this
task only changes handler bodies and adds `api/replay_loader.py`. This
is the substrate the entire frontend (4.3–4.8) consumes.

**Engine-playback architecture.** Replays store `state_hash` per tick
but not positions ([orchestrator/replay.py:74-84](orchestrator/replay.py#L74)).
To produce per-tick `AgentTickStateView` DTOs the loader re-runs the
engine against the recorded action stream:

1. Read the first `ReplayEntry` from the JSONL; extract
   `game_id = "headless-seed-{N}"`; parse N.
2. `state = seed_initial_state(seed=N, map=load_canonical_map(), ...)`
   — same call shape as
   [orchestrator/game.py:674](orchestrator/game.py#L674).
3. For each `ReplayEntry` in order: deserialize the action list,
   call `state, events = advance_tick(state, actions, ...)`, snapshot
   `state` + `events` into a `TickView`.
4. After every meeting `ReplayEntry` (signalled by an interleaved
   `MeetingReplayEntry`), apply the meeting outcome to `state` —
   mirror the orchestrator pattern at
   [orchestrator/game.py](orchestrator/game.py#L770-L820)'s
   `_apply_meeting_result` (read-only re-use; do NOT modify that
   helper).
5. Verify the `state_hash` after each tick matches the recorded
   `ReplayEntry.state_hash`. Mismatch is a hard error (the determinism
   invariant is broken; surface as a 500 with the mismatching tick in
   the error body).

This is a read-only engine touch — the loader IMPORTS from `engine/`
and `orchestrator/` but does not MODIFY any of their code. Consistent
with the "no engine touches in Phase 4" scope guarantee, which is
about behavior change, not import boundaries.

**Loader caching.** Loading + replaying a 1000-tick game is non-
trivial CPU (~50-200 ms per game in headless tests). The loader
keeps an in-memory LRU cache keyed by `game_id`; default `maxsize=16`.
Invalidation happens on process restart (replays are immutable once
written). No cross-process cache (Redis) — that's Phase 5.

**Replay directory discovery.** A configured `replay_dir` path
(default: `$AILIBI_REPLAY_DIR` if set, else `./replays/` relative to
process cwd) is scanned for `replay-seed-*.jsonl` files. The pattern
is hard-coded — any file not matching is ignored. The endpoint never
recursively descends; subdirectories are out of scope for MVP.

**Out of scope** (explicit decisions deferred):

- **Pagination on `/replays`.** MVP returns all metadata in one shot.
  Add pagination when the replay count makes it matter (Phase 5+).
- **Replay deletion / management endpoints.** Read-only API. Replays
  are managed via filesystem; the API does not mutate.
- **Per-tick memory reconstruction between meetings.** Per the 4.1
  decision, `AgentMemoryView` is only available at meeting boundaries
  (where the `LLMCallRecord.prompt` text captures rendered memory).
  Between-meeting memory is NOT exposed — the endpoint returns 404
  for memory requests at non-meeting ticks. Document this in API docs.
- **Live game streaming via WebSocket.** Deferred phase-wide.
- **Persistent on-disk cache.** In-memory LRU only. Restart re-loads
  on first request.

**Files in scope:**
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- api/main.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/test_eval.py
- tests/api/fixtures/__init__.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/ (imported read-only; not modified)
- agents/
- llm/
- meetings/
- observation/
- orchestrator/ (imported read-only; not modified)
- frontend/
- api/schemas.py (DTOs are frozen at 4.1)
- api/ws.py
- api/routes/games.py
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
- tests/api/test_schemas.py (frozen at 4.1)
- tests/api/test_routes.py (frozen at 4.1; superseded by test_replays for body coverage)
- tests/api/test_leak.py (frozen at 4.1)
- tests/test_firewall.py

**Definition of done:**
- [ ] **`api/replay_loader.py` exposes `ReplayLoader`** with `list_replays() -> list[ReplayMetadataView]` and `load_replay(game_id: str) -> ReplayView`. Constructor takes `replay_dir: Path` and `map: Map`. The loader is the single source of truth for engine-playback; routes import it, never compose engine APIs directly.
- [ ] **Engine playback reproduces state byte-identically.** Every tick's reconstructed `state_hash` matches the recorded `ReplayEntry.state_hash`. Mismatch raises `ReplayStateMismatchError` (new exception in `api/replay_loader.py`) which routes catch and surface as `500 {"detail": "...", "tick": N, "game_id": "..."}`.
- [ ] **`GET /replays`** scans the configured replay directory and returns `list[ReplayMetadataView]`. Empty directory returns `[]`. Files not matching `replay-seed-*.jsonl` are silently skipped. Sorted by `seed` ascending.
- [ ] **`GET /replays/{game_id}`** returns the full `ReplayView`. Unknown `game_id` returns `404 {"detail": "replay not found: {game_id}"}`. Caches the result via the LRU cache.
- [ ] **`GET /replays/{game_id}/ticks/{tick}`** returns the `TickView` for one tick. Reuses the cached `ReplayView` if present; otherwise loads first. Tick out of range returns `404`.
- [ ] **`GET /replays/{game_id}/meetings/{meeting_id}`** returns one `MeetingView` derived from the corresponding `MeetingReplayEntry`. Unknown meeting returns `404`.
- [ ] **`GET /replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}`** returns the `AgentMemoryView` for one agent at one meeting boundary. The view is constructed from (a) the agent's role from the seeded roster, (b) the agent's `rendered_memory` extracted from that meeting's `LLMCallRecord.prompt` text, and (c) per-agent belief/contradiction state at that tick. Document the extraction strategy in `## Decisions` — depending on how cleanly the rendered memory parses, the implementing agent may need to either string-extract or re-render via `agents.memory.store.render_for_prompt` against the reconstructed engine state. Unknown agent returns `404`.
- [ ] **`GET /eval/cost-summary`** returns `EvalCostSummaryView` aggregated across every replay in the directory. Empty directory returns zero/null values, no crash.
- [ ] **Partial-replay handling.** Replays with no `GameEndReplayEntry` (per Task 3.19 the eval ran 27/50 before crashing; those 23 partial files are real artifacts) surface `winner=None` in `ReplayMetadataView` cleanly. The tick timeline is still readable up to the last recorded tick.
- [ ] **LRU cache.** `api/replay_loader.py` uses `functools.lru_cache` (or equivalent) with `maxsize=16` on `load_replay`. Cache is per-process. Cache hit shortcuts engine playback. Add a `clear_cache()` method called by a test fixture to keep tests hermetic.
- [ ] **Configuration via env.** `api/main.py` reads `AILIBI_REPLAY_DIR` env at startup; falls back to `./replays/`. Document the env var in `.env.example` (the only `.env.example` edit allowed by this task). The `ReplayLoader` is constructed once at app startup and injected via a FastAPI dependency.
- [ ] **No engine modification.** `engine/` and `orchestrator/` imports are read-only. `uv run lint-imports` still passes. The new module `api/replay_loader.py` IS allowed to import from `engine/` and `orchestrator/`; document this exception in `## Decisions` (the firewall forbids `agents/`, `llm/`, `meetings/` from importing `engine/`; `api/` is a privileged spectator surface, not part of the firewall).
- [ ] **Unit tests for `ReplayLoader`.** Construct a fixture JSONL (small 3-tick game with one meeting, written via `ReplayLog` in a test helper); load it; assert the resulting `ReplayView`'s `ticks`, `meetings`, and `metadata.winner` match expectations.
- [ ] **State-hash mismatch test.** Construct a JSONL where the recorded `state_hash` is wrong; assert `ReplayStateMismatchError` is raised with the bad tick number.
- [ ] **Partial-replay test.** Construct a JSONL with no `GameEndReplayEntry`; assert the loader returns `winner=None` and the tick timeline is intact up to the last recorded tick.
- [ ] **Endpoint tests via `TestClient`.** Cover all six endpoints + the 404/500 error paths.
- [ ] **Leak tests still pass.** The 4.1 leak tests run against the populated routes; no new DTO types leak through. The existing `tests/api/test_leak.py` must pass without modification.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/`. `uv run lint-imports` passes (it should already allow `api/` → `engine/` since `api/` isn't in the deny-list; verify in `pyproject.toml` import-linter config).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The loader's high-level shape (illustrative; pick exact names consistent with the module style):

```python
# api/replay_loader.py — illustrative
from functools import lru_cache
from pathlib import Path

from engine.world import Map, load_canonical_map
from orchestrator.game import _apply_meeting_result  # may need to be made public
from orchestrator.replay import (
    read_replay_entries, read_meeting_entries, read_game_outcome,
    read_failed_call_entries, compute_cost_usd,
)
from orchestrator.seeder import seed_initial_state
from engine.advance import advance_tick  # adjust import to actual location

from api.schemas import (
    ReplayMetadataView, ReplayView, TickView, MeetingView, AgentMemoryView,
    ...
)


class ReplayStateMismatchError(RuntimeError):
    """Raised when reconstructed state_hash diverges from the recorded one.
    Indicates a replay-determinism break; surfaced as HTTP 500."""
    def __init__(self, *, game_id: str, tick: int, expected: str, actual: str):
        ...


class ReplayLoader:
    def __init__(self, replay_dir: Path, *, map: Map | None = None) -> None:
        self._replay_dir = replay_dir
        self._map = map if map is not None else load_canonical_map()

    def list_replays(self) -> list[ReplayMetadataView]:
        out: list[ReplayMetadataView] = []
        for jsonl in sorted(self._replay_dir.glob("replay-seed-*.jsonl")):
            seed = self._parse_seed_from_filename(jsonl.name)
            out.append(self._metadata_view(jsonl, seed))
        return out

    @lru_cache(maxsize=16)
    def load_replay(self, game_id: str) -> ReplayView:
        path = self._resolve_path(game_id)
        if path is None:
            raise FileNotFoundError(game_id)
        seed = self._parse_seed_from_game_id(game_id)
        state = seed_initial_state(seed=seed, map=self._map)
        replay_entries = read_replay_entries(path)
        meeting_entries = read_meeting_entries(path)
        meeting_by_tick = {m.tick: m for m in meeting_entries}

        ticks: list[TickView] = []
        for entry in replay_entries:
            actions = self._deserialize_actions(entry.actions)
            state, events = advance_tick(state, actions)
            if entry.tick in meeting_by_tick:
                state = _apply_meeting_result(state, meeting_by_tick[entry.tick])
            self._assert_hash(entry, state)
            ticks.append(self._tick_view(entry.tick, state, events))

        return ReplayView(
            metadata=self._metadata_view(path, seed),
            map=self._map_view(),
            players=self._players_view(state),
            ticks=tuple(ticks),
            meetings=tuple(self._meeting_view(m) for m in meeting_entries),
            failed_calls=tuple(
                self._failed_call_view(f) for f in read_failed_call_entries(path)
            ),
        )

    # ... private helpers _metadata_view, _tick_view, _meeting_view, etc. ...
```

The `_apply_meeting_result` reuse point is the most fragile dependency. If it's currently private (leading underscore), the implementing agent can either (a) propose a one-line orchestrator change exposing a `apply_meeting_result_view` helper (small scope; defensible), or (b) inline the meeting-application logic locally. Document the choice in `## Decisions`. Bias toward (a) — single source of truth — if the orchestrator change is genuinely one line.

For the memory endpoint, the cleanest path is to re-render via `agents.memory.store.render_for_prompt` against the reconstructed engine state at that tick. This is determinism-preserving and avoids string-parsing the captured LLM prompt. Trade-off: requires the loader to maintain per-agent memory stores across the tick walk, which is more bookkeeping than the simpler "extract from LLMCallRecord.prompt" approach. The implementing agent picks; document the choice.

For the fixture JSONL, the cleanest pattern is a test helper that writes a small synthetic replay using the real `ReplayLog` API:

```python
# tests/api/fixtures/sample_replay.py — illustrative
def write_sample_replay(path: Path, *, seed: int = 0, ticks: int = 3) -> None:
    """Write a minimal real replay log. Used by api tests as ground truth."""
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(seed=seed, map=load_canonical_map())
    for t in range(ticks):
        actions = []  # no-op tick
        state, events = advance_tick(state, actions)
        log.record_tick(tick=t, actions=actions, state=state)
    log.record_game_end(tick=ticks - 1, winner="CREWMATES", reason="all_tasks_complete")
```

This guarantees the fixture is a real replay (matches what `ReplayLog` actually writes), not a hand-authored mock that could drift from the real schema.

## Public types this task introduces
- `api.replay_loader.ReplayLoader`
- `api.replay_loader.ReplayStateMismatchError`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-replay-endpoint` with a title like `task 4.2: replay loader + endpoint implementation`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §11.4, DESIGN.md §1.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
