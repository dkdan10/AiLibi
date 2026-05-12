# Agent Prompt — 2.7.5 Post-2.7 audit repair

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.7.5 — Post-2.7 audit repair, anchored to DESIGN.md §1.3, DESIGN.md §3.6, DESIGN.md §4.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-post-audit-repair`
**Depends on:** 2.6 merged, 2.7 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.6, DESIGN.md §4.4
**Complexity:** Medium

Address the documented findings from
`audits/audit-2026-05-10-0721.md`, plus the PR-workflow gap surfaced in the
post-2.7 conversation (audit PR #25 shipped with an empty body because no
non-task-prompted PR has structured-body instructions), so the agent layer
and the contributor workflow are defensively sound before Task 2.8 wires
agents into a live game. This is a single bundled PR that:

- fixes one contract-scope drift (M-1),
- hardens one tactical policy against disconnected maps (L-2),
- documents one deliberate behavioural narrowing (L-3),
- pins one engine→perception enum coupling (L-4),
- ships the body-after-discovery regression test that the prior audit
  deferred from 2.8 (L-5),
- and closes the PR-template enforcement gap (PR-W1) by promoting the
  `.github/pull_request_template.md` shape into both `AGENTS.md` (so the
  template applies to every PR, task and ad-hoc alike) and
  `scripts/prompt_template.md.j2` (so generated task prompts agree with
  the template).

No agent-visible behaviour change beyond those documented fixes. The
prompt-template alignment will regenerate every existing `agent_prompts/*`
file via `scripts/generate_prompts.py`; the diff to those files is purely
mechanical (no task contract changes).

**Files in scope:**
- tasks/phase-2.md
- agents/tactical/crewmate_policy.py
- tests/agents/test_crewmate_policy.py
- tests/agents/test_perception.py
- tests/observation/test_service.py
- AGENTS.md
- scripts/prompt_template.md.j2

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/runtime.py
- agents/perception.py
- agents/memory/
- agents/tactical/impostor_policy.py
- agents/tactical/pathing.py
- agents/base.py
- llm/
- api/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- audits/
- .github/pull_request_template.md
- scripts/generate_prompts.py
- scripts/_task_parser.py
- scripts/validate_task_docs.py

**Definition of done:**
- [ ] `tasks/phase-2.md` Task 2.4 `Files in scope` list includes `agents/runtime.py`, recording the historical scope of PR `908c6a3`.
- [ ] `tasks/phase-2.md` Task 2.6 records, in a short prose note after the implementation hint, that the `KILL_WITNESSED` interrupt deliberately fires only when the kill action is reported in the agent's own room (narrower than the engine's `same_room_and_adjacent` visibility window) and that this is an intentional tactical choice, not a bug.
- [ ] `agents/tactical/crewmate_policy.py` `_move_toward` and `_flee_and_report` wrap their `find_path` calls in `try / except ValueError`, falling back to `WaitIntent` when no path exists. Mirror the pattern already used in `agents/tactical/impostor_policy.py:145-149` and `:335-339`.
- [ ] `tests/agents/test_crewmate_policy.py` adds a regression test that builds a `PublicMapView` with a disconnected goal room and asserts the crewmate emits `WaitIntent` instead of raising.
- [ ] `tests/agents/test_perception.py` adds a regression test asserting that `agents.perception._AUDIBLE_EVENT_TYPES.keys()` equals the set of literals in the `AudibleEvent.kind` type from `observation/packet.py` (use `typing.get_args` on the Literal alias). The test must fail if a new `kind` is added to `AudibleEvent` without an accompanying entry in `_AUDIBLE_EVENT_TYPES`.
- [ ] `tests/observation/test_service.py` adds an integration test that pins today's body-after-discovery filter behaviour: build a `WorldState` with a body in the observer's room, build a packet and assert the body appears in `visible_bodies`, then mutate `state.bodies[body_id]` so `discovered_by` is non-`None` and assert the same observer's next packet omits the body (including for the reporter themselves on the discovery tick). Name the test `test_discovered_body_is_hidden_from_subsequent_packets` or equivalent.
- [ ] `AGENTS.md` gains a new top-level `## PR description` section that names `.github/pull_request_template.md` as the canonical body shape, requires every PR — task-driven and ad-hoc (audits, hygiene, hotfixes) alike — to populate `## Summary`, `## Definition of done`, `## Decisions`, and (only when blocking) `## Questions`, and explicitly forbids `gh pr create --body ""` or `--fill` without a structured body. The section must mention that passing `--body` overrides the template.
- [ ] `scripts/prompt_template.md.j2` `Output expectation` block is aligned with `.github/pull_request_template.md`: it references the template file by path and enumerates `## Summary` alongside the existing `## Definition of done`, `## Decisions`, and `## Questions` requirements. After the template edit, run `uv run python scripts/generate_prompts.py` so every `agent_prompts/task-*.md` is regenerated against the new template; the diff to those files must be purely mechanical (no task-contract content changes).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

For the crewmate `find_path` hardening, mirror the impostor's existing pattern exactly so the codebase reads consistently:

```python
# agents/tactical/crewmate_policy.py
def _move_toward(self, *, own_room: RoomId, goal: RoomId, public_map: PublicMapView) -> ActionIntent:
    try:
        path = find_path(public_map=public_map, start=own_room, goal=goal)
    except ValueError:
        return self._wait()
    ...
```

Apply the same guard to `_flee_and_report`. The fallback should be `WaitIntent`, not `MoveIntent` to a neighbour — `wait` is the only intent that is always safe regardless of map state.

For the `AudibleEvent` enum coupling test, extract the Literal members deterministically rather than hard-coding them:

```python
from typing import get_args
from observation.packet import AudibleEvent

# AudibleEvent.model_fields["kind"].annotation is the Literal alias.
expected_kinds = set(get_args(AudibleEvent.model_fields["kind"].annotation))
assert set(agents.perception._AUDIBLE_EVENT_TYPES) == expected_kinds
```

For the body-after-discovery test, build the state by reusing `tests/observation/test_service.py::_base_world_state` and `_observation_service`, then either run a `report` action through `advance_tick` or directly mutate the body via `dataclasses.replace` to set `discovered_by`. Both approaches are valid; the direct-mutation form is shorter and pins the engine-visibility behaviour without coupling to the report rule.

For the Task 2.4 scope fix and the Task 2.6 narrowing note, edit `tasks/phase-2.md` only; do not touch `agents/runtime.py` or `agents/tactical/crewmate_policy.py`'s kill-witnessed branch — the changes are documentation-only.

For the `AGENTS.md` PR-description section, model it on the existing `## Definition of done (always)` section: short, imperative, no examples. Suggested shape:

```markdown
## PR description (always)

Every PR — task-driven or ad-hoc (audits, hygiene, hotfixes) — must
populate the sections in `.github/pull_request_template.md`:

- `## Summary` — 1–3 bullets stating what changed and why.
- `## Definition of done` — copy the task's checklist and tick each item;
  for ad-hoc PRs, list the scope you actually executed.
- `## Decisions` — every judgment call resolved without human input.
  Write "None." if there were none.
- `## Questions` — blocking questions only; omit the section if none.

When creating the PR with `gh pr create`, pass `--body` with a here-doc
containing the populated template. `gh pr create --fill` and
`gh pr create --body ""` both ship empty bodies and are not permitted.
```

For `scripts/prompt_template.md.j2`, the existing `## Output expectation` block reads:

```
The PR description must reference {{ task.section_refs }}, list the
definition-of-done checklist, and include `Decisions` and (if blocking)
`Questions` sections.
```

Replace it with a version that names the template and adds `## Summary`:

```
The PR description must follow `.github/pull_request_template.md` and
include `## Summary` (1–3 bullets referencing {{ task.section_refs }}),
`## Definition of done` (the checklist from this contract, ticked),
`## Decisions` (every judgment call), and (only when blocking) `## Questions`.
```

After editing the template, run `uv run python scripts/generate_prompts.py`. Every `agent_prompts/task-*.md` will see the new wording; that is the expected mechanical diff. `scripts/generate_prompts.py --check` must then pass.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-2-post-audit-repair` with a title like `task 2.7.5: post-2.7 audit repair`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.6, DESIGN.md §4.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
