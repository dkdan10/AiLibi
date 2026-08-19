# Agent Prompt — 2.9 Headless tournament harness

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.9 — Headless tournament harness, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-headless-tournament-harness`
**Depends on:** 2.8 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

scripts/run_tournament.py and eval/balance_eval.py per §11.3. This task
aggregates many headless games; it must not invent the single-game
orchestrator.

**Files in scope:**
- scripts/run_tournament.py
- eval/balance_eval.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- engine/ core rule changes
- orchestrator/game.py
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Headless tournament harness runs multiple orchestrated games.
- [ ] Balance eval reports win rates across seeds.
- [ ] 100-game headless tournament completes without crashes.
- [ ] Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); `TICK_BUDGET_REACHED` games are reported separately and do not count toward decisive totals.
- [ ] `TICK_BUDGET_REACHED` is a first-class outcome bucket in the tournament report, reported alongside `CREWMATES` and `IMPOSTORS` (and `MEETING_PHASE_REACHED` when the meeting manager has not landed). Non-decisive outcomes must not be silently dropped or coerced into the decisive buckets.
- [ ] Leak test still passes across all tournament games.
- [ ] `uv run pytest tests/eval/test_balance_eval.py` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

```python
# eval/balance_eval.py
@dataclass(frozen=True)
class BalanceReport:
    games: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    seeds_used: tuple[int, ...]

def run_balance_eval(*, seeds: Sequence[int]) -> BalanceReport: ...
```

Reuse `HeadlessGame` from 2.8 — do NOT reinvent the single-game loop.

## Public types this task introduces
- `eval.balance_eval.BalanceReport`
- `eval.balance_eval.run_balance_eval`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-2-headless-tournament-harness` with a title like `task 2.9: headless tournament harness`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
