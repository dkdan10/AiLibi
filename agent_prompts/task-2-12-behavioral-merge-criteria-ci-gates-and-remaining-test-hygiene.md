# Agent Prompt — 2.12 Behavioral merge-criteria CI gates and remaining test hygiene

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.12 — Behavioral merge-criteria CI gates and remaining test hygiene, anchored to DESIGN.md §11.2, DESIGN.md §11.3, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-behavioral-ci-gates`
**Depends on:** 2.10 merged, 2.10.5 merged, 2.11 merged
**Section refs:** DESIGN.md §11.2, DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Medium

Close the three test-coverage findings in
`audits/audit-2026-05-15-0225-reconciled.md` that prevent the Phase 2
acceptance gates from regressing silently: R-11 (no automated guard for
the decisive-outcome sweep or 100-game balance criterion — the repository
was green while those gates were failing live), R-13 (audit-log
append-mode regression absent — a future `"a"` → `"w"` change would slip
past current single-instance tests), and R-12 (property-test action
vocabulary intentionally limited to `move`/`wait`, leaving
kill/vent/report interleavings unexplored). All three are test-only
additions. None touches production code, and Task 2.10's behavioral
fixes must be merged first so the new gate encodes the passing outcome
rather than the pre-2.10 failing one.

**Files in scope:**
- tests/eval/test_balance_eval.py
- tests/observation/test_service.py
- tests/engine/test_tick_properties.py

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/
- llm/
- api/
- frontend/
- eval/
- scripts/
- DESIGN.md
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- audits/
- tasks/
- agent_prompts/
- README.md
- open_issues.md
- tests/agents/
- tests/meetings/
- tests/orchestrator/
- tests/observation/test_boundary_contracts.py
- tests/engine/test_actions.py
- tests/engine/test_events.py
- tests/engine/test_map_loader.py
- tests/engine/test_rng.py
- tests/engine/test_tick.py
- tests/engine/test_visibility.py
- tests/engine/test_world_state.py
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-11 — decisive-outcome CI guard:** `tests/eval/test_balance_eval.py` gains a test that runs a small, documented set of default-agent seeds (e.g. three to five seeds chosen so at least one is known-decisive post-2.10) through `HeadlessGame`, counts decisive outcomes (`CREWMATES` or `IMPOSTORS`), and fails if zero seeds are decisive. The seed list, the post-2.10 expected outcome for each seed, and a comment naming this guard as the R-11 CI floor must be encoded in the test file. The test must run within the existing pytest budget (target ≤ ~5s; bound it with a low `max_ticks` if necessary, e.g. 200). This test must encode the passing outcome from Task 2.10's R-2 sweep; it must not encode the pre-2.10 failing outcome.
- [ ] **R-13 — audit-log append-mode regression:** `tests/observation/test_service.py` gains a test (e.g. named `test_audit_log_appends_across_two_instances`) that constructs one `ObservationService` (or its `ObservationAuditLog`) pointed at a tmp path, records at least one packet, discards the instance, opens a second instance pointed at the same path, records another packet, and asserts the file contains both packets in order (e.g. two JSON lines). The test must fail if `observation/audit.py:20-23` is ever changed from `"a"` to `"w"` and must not import from `engine/` directly (use existing test helpers).
- [ ] **R-12 — broadened property-test vocabulary:** `tests/engine/test_tick_properties.py` gains a second `hypothesis` strategy (or a parametrized expansion of the existing strategy) that draws batches mixing role-valid `kill`, `vent`, `report`, and `wait` actions, plus a property covering the new vocabulary (at minimum: `advance_tick` does not raise on any drawn batch where roles and aliveness allow the action). The existing `move`/`wait` strategy stays untouched; the comment at `tests/engine/test_tick_properties.py:6-10` is updated to record that the broader vocabulary now ships alongside.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

For R-11, lean on the seed list Task 2.10's R-2 bullet records. Pick a subset that is small enough to be CI-friendly (≤ 5 seeds, ≤ 200 ticks each) and that includes at least one seed Task 2.10 ended at `CREWMATES` or `IMPOSTORS`:

```python
# tests/eval/test_balance_eval.py
_R11_CI_GUARD_SEEDS: Final[tuple[int, ...]] = (0, 1, 2, 7, 42)
_R11_CI_GUARD_MAX_TICKS: Final[int] = 200

def test_default_agent_sweep_reaches_at_least_one_decisive_outcome(
    tmp_path: Path,
) -> None:
    """R-11 CI floor: after Task 2.10 the small seed sweep must yield at
    least one decisive outcome. If this test fails, the Phase 2 tactical
    fixes (R-1/R-2/R-3) have regressed; investigate before reverting."""
    decisive = 0
    for seed in _R11_CI_GUARD_SEEDS:
        result = HeadlessGame(
            seed=seed,
            game_map=load_canonical_map(),
            replay_path=tmp_path / f"r-{seed}.jsonl",
            max_ticks=_R11_CI_GUARD_MAX_TICKS,
        ).run()
        if result.outcome in {"CREWMATES", "IMPOSTORS"}:
            decisive += 1
    assert decisive >= 1, (
        "R-11 regression: zero decisive outcomes across the CI guard "
        "seeds; see audits/audit-2026-05-15-0225-reconciled.md §R-11."
    )
```

If the existing test file does not import `HeadlessGame` / `load_canonical_map` / `Path` yet, add only the imports needed for the new test — do not reorganize the file. The 100-game tournament gate remains a local-only check; do not put a 100-game run in CI.

For R-13, model the new test on the existing `test_audit_log_records_sanitized_packet` at `tests/observation/test_service.py:289`. The simplest form:

```python
def test_audit_log_appends_across_two_instances(tmp_path: Path) -> None:
    state = _base_world_state()
    service_one = _observation_service(tmp_path)
    service_one.build_packet(world_state=state, agent_id="p-1", engine_events=[])
    del service_one
    service_two = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )
    service_two.build_packet(world_state=state, agent_id="p-2", engine_events=[])
    lines = (tmp_path / "observation_audit.jsonl").read_text().splitlines()
    assert len(lines) == 2
```

Use whichever player ids Task 2.11's R-14 rewrite settled on; do not re-introduce role-bearing helper ids. The path string must match `_observation_service`'s default.

For R-12, the existing strategy at `tests/engine/test_tick_properties.py:6-10` is the template. Add a sibling strategy (`hypothesis.strategies.composite`) that draws role-valid action tuples:

```python
@composite
def _role_aware_action_batches(draw, *, world_state):
    """Draw a batch mixing kill, vent, report, and wait actions, gated by
    the actor's role and aliveness. Used by the role-vocabulary property
    in addition to the existing move/wait property."""
    ...

@given(world_state=_world_states(), batch=_role_aware_action_batches(...))
def test_role_aware_action_batches_do_not_raise(world_state, batch):
    advance_tick(world_state, batch, game_map=load_canonical_map())
```

Keep the new property's invariant narrow: "does not raise" is enough; deeper invariants (e.g. role-correct event emission) can land later.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.seeder"`
- `uv run python -c "import orchestrator.scheduler"`
- `uv run python -c "import agents.tactical.impostor_policy"`
- `uv run python -c "import agents.tactical.pathing"`
- `uv run python -c "import agents.perception"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.working"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import agents.base"`
- `uv run python -c "import agents.runtime"`
- `uv run python -c "import observation.action_intent"`
- `uv run python -c "import observation.public_map"`
- `uv run python -c "import orchestrator.boundary"`
- `uv run python -c "import agents.tactical.crewmate_policy"`

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
Open a PR from branch `phase-2-behavioral-ci-gates` with a title like `task 2.12: behavioral merge-criteria ci gates and remaining test hygiene`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.2, DESIGN.md §11.3, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
