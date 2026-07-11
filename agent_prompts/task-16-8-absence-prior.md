# Agent Prompt — 16.8 The absence prior: a capped sub-gate delta for the publicly unplaced (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.8 — The absence prior: a capped sub-gate delta for the publicly unplaced (default-OFF lever), anchored to meetings/transcript.py:989-1092 (reconstruct_stated_paths — the absence complement is roster minus its keys, computed nowhere today); meetings/manager.py:1830-1861 (_joint_capped_suspicion — the cap everything composes through); agents/memory/beliefs.py:80-99 (the lone-weak-signal discipline); tasks/phase-15.md 15.5 (the boundary-sum pin precedent). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-absence-prior`
**Depends on:** 16.6, 16.7
**Section refs:** meetings/transcript.py:989-1092 (reconstruct_stated_paths — the absence complement is roster minus its keys, computed nowhere today); meetings/manager.py:1830-1861 (_joint_capped_suspicion — the cap everything composes through); agents/memory/beliefs.py:80-99 (the lone-weak-signal discipline); tasks/phase-15.md 15.5 (the boundary-sum pin precedent)
**Complexity:** Medium

The channel that makes visibility a resource: at the pre-vote fold, the ABSENT set — living
players whom nobody's public testimony placed anywhere this meeting (roster minus
`reconstruct_stated_paths(...)` keys, a fold that exists but whose complement is computed
nowhere) — receives a WEAK suspicion delta, `ABSENCE_SUSPICION_DELTA ≤ +0.08`, composed through
`_joint_capped_suspicion` like every meeting-time lift. The sizing is the contract: alone, the
delta must stay sub-gate (0.50 + 0.08 = 0.58 < 0.60 — a quiet crewmate is NEVER ejectable on
absence alone), but absence + testimony-spread deliberately CAN cross the gate (two independent
weak signals is the two-signal eject discipline). That intent must be a TEST, not an accident:
this task pins the lone-signal case AND the stacked combinations (the 15.5 boundary-sum
precedent — every documented crossing combination crosses, every documented non-crossing stays
under, IEEE-luck excluded). Default-OFF lever, registered behind 16.6 in the registry chain.
Note the loop this closes: answering 16.7's roll-call removes you from the absent set — so
impostors gain a reason to account for their time, lying creates prosecutable material, and
staying unseen finally has a price. That is the incentive Phase 17's retraining climbs.

**Files in scope:**
- meetings/transcript.py (the absent-set helper beside reconstruct_stated_paths — behind 16.7's edits)
- agents/memory/beliefs.py (ABSENCE_SUSPICION_DELTA + `absence_prior_enabled` resolver + the fold application region — behind 16.4's clamp region)
- meetings/manager.py (pre-vote absence-fold invocation region — disjoint from 16.3/16.5/16.6/16.7's regions per the preamble map)
- orchestrator/replay.py (lever registration region — behind 16.6's entry)
- .env.example (the lever env line)
- tests/agents/test_absence_prior.py (new: lone-signal + stacked boundary pins + cap composition)
- tests/meetings/test_absent_set.py (new: the set derivation — whereabouts answers remove; unplaced remain; dead players excluded)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- agents/perception.py + observation/ (absence is derived from PUBLIC transcript testimony only — the firewall exposes no liveness channel, and this task must not create one)
- replays/samples/ (OFF byte-identical; the re-record is 16.17)

**Definition of done:**
- [ ] The absent set derives ONLY from public testimony (stated paths + whereabouts claims): fixture-pinned, including the firewall negative (no private memory of others feeds it).
- [ ] Lone-signal discipline pinned: absence alone renders 0.58 on a neutral prior — below the gate — and the stacked combinations are pinned BOTH ways (absence + graduated spread crosses; absence + decay-drifted prior does not; the documented table in the test is the design intent).
- [ ] Composition: the delta routes through `_joint_capped_suspicion` and respects `CONTRADICTION_RENDER_CEIL` (asserted); it interacts with 16.6's citation gate only through flag-independence (absence mints no flag — asserted).
- [ ] Lever OFF = byte-identical (golden + `verify_samples.sh` green); the offline counterfactual on committed baseline-3 bytes reports how often the absent set is non-empty, its size distribution, and how many outcomes the delta would flip (the calibration evidence for the 16.17 graduation slate).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The helper is three lines on top of `reconstruct_stated_paths` — the work is the pins. Build the
boundary table first (every delta combination the docstrings document, with the expected
gate-side), then implement to the table; quantize-then-compare where the 15.6 band lesson applies.
On committed bytes the absent set will often be LARGE (roll-call does not exist yet — 16.15
elicits it), so the counterfactual's honest reading is "what would this delta do TODAY," which is
exactly why the lever stays OFF until the elicitation lands and 16.17 measures the pair together.

## Public types this task introduces
- `agents.memory.beliefs.ABSENCE_SUSPICION_DELTA`
- `agents.memory.beliefs.absence_prior_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`

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
Open a PR from branch `phase-16-absence-prior` with a title like `task 16.8: the absence prior: a capped sub-gate delta for the publicly unplaced (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing meetings/transcript.py:989-1092 (reconstruct_stated_paths — the absence complement is roster minus its keys, computed nowhere today); meetings/manager.py:1830-1861 (_joint_capped_suspicion — the cap everything composes through); agents/memory/beliefs.py:80-99 (the lone-weak-signal discipline); tasks/phase-15.md 15.5 (the boundary-sum pin precedent)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
