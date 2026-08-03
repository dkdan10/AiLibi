# Agent Prompt — 1.9 Post-audit pre-Phase-2 cleanup

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-1.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 1.9 — Post-audit pre-Phase-2 cleanup, anchored to DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §A. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-1.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-1-post-audit-cleanup`
**Depends on:** 1.B1 merged, 1.B2 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §A
**Complexity:** Medium

Address the documented findings from
`audits/audit-2026-05-09-1901.md` so the boundary contracts and engine state
encoding are clean before Task 2.2 begins. This is a single bundled PR that
fixes one fixture, one engine encoding, and several documentation
inconsistencies, and that retroactively scopes the empty FastAPI scaffolding
(Task 0.6). No agent-visible behaviour changes for downstream tasks beyond
the documented fixes.

**Files in scope:**
- engine/rng.py
- tests/engine/test_rng.py
- tests/fixtures/scripted_game_vent_and_emergency.json
- DESIGN.md
- tasks/phase-0.md
- tasks/phase-2.md

**Files NOT in scope:**
- engine/tick.py
- engine/world.py
- engine/visibility.py
- engine/rules.py
- engine/win_conditions.py
- engine/actions.py
- engine/entities.py
- engine/events.py
- observation/
- orchestrator/
- agents/
- api/
- llm/
- AGENT_IMPLEMENTATION.md
- audits/

**Definition of done:**
- [ ] engine/rng.py replaces `pickle` snapshot/restore with an explicit JSON encoding of `random.Random.getstate()`. Snapshot bytes are UTF-8 JSON; restore round-trips by re-tupling the inner state list.
- [ ] tests/engine/test_rng.py is updated so round-trip, same-seed, and bytes-shape tests cover the new encoding.
- [ ] tests/fixtures/scripted_game_vent_and_emergency.json no longer contains two actions for `impostor-1` on tick 2; the scripted game still ends in `MEETING` via the existing `emergency` action.
- [ ] DESIGN.md §A `ObservationPacket` snippet includes `cooldown: int | None  # impostor only` so it agrees with §4.2. No other DESIGN.md changes.
- [ ] tasks/phase-2.md Task 2.1 Definition of done line for `PublicMapView` lists `vent_rooms` alongside the other public-topology fields.
- [ ] tasks/phase-2.md Task 2.8 Integration risk block adds a bullet requiring a regression test that pins today's body-visibility-after-discovery behaviour from engine/visibility.py (bodies whose `discovered_by` is set are filtered out of every observer's `visible_bodies`).
- [ ] tasks/phase-0.md Task 0.6 (Empty FastAPI scaffolding) is recorded with a `Status` block documenting that it is already merged on `main` and listing api/main.py, tests/api/test_main.py, and docker-compose.yml as the in-scope files.
- [ ] uv run python scripts/generate_prompts.py produces matching prompts for any added or edited tasks; uv run python scripts/generate_prompts.py --check passes.
- [ ] uv run python scripts/validate_task_docs.py passes.
- [ ] uv run pytest passes.
- [ ] uv run mypy . passes.
- [ ] uv run ruff check . and uv run ruff format --check . pass.
- [ ] uv run lint-imports passes.
- [ ] bash scripts/check.sh passes locally.

## Implementation hint

For RNG, the smallest faithful change is to JSON-encode the `random.Random.getstate()` tuple. `getstate()` returns `(version: int, internal_state: tuple[int, ...], gauss_next: float | None)`; convert tuples to lists for `json.dumps` and re-tuple on `json.loads` before calling `setstate()`:

```python
def snapshot(self) -> bytes:
    version, internal, gauss = self._random.getstate()
    payload = {"v": version, "s": list(internal), "g": gauss}
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")

@classmethod
def from_state(cls, state: bytes) -> EngineRng:
    payload = json.loads(state.decode("utf-8"))
    inner = random.Random()
    inner.setstate((payload["v"], tuple(payload["s"]), payload["g"]))
    return cls(_random=inner)
```

The determinism test compares two runs of the same fixture, so it stays
byte-for-byte stable across the encoding change as long as both runs use
the new encoding. Re-run `pytest eval/determinism_test.py` after the
change to confirm.

For Task 0.6 retroactive scope, model the new section on Task 2.1's
existing `Status` block in tasks/phase-2.md: a short paragraph stating
the task is already merged on `main`, followed by the standard task
fields (Branch, Depends on, Section refs, Complexity, Files in scope,
Files NOT in scope, Definition of done with `- [x]` checkboxes, and a
Ready-to-paste prompt path).

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
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
Open a PR from branch `phase-1-post-audit-cleanup` with a title like `task 1.9: post-audit pre-phase-2 cleanup`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §A), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
