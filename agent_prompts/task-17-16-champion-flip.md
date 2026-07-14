# Agent Prompt — 17.16 Champion productization + the evidence-gated default flip

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.16 — Champion productization + the evidence-gated default flip, anchored to locked decision 2 (the flip criterion: referee PASS + retained win edge at 17.14); agents/tactical/learned/factory.py + forward.py (the opt-in surface, swapped in place); training/reports/report-finalist-eval.md (the evidence); tasks/phase-15.md 15.20/15.21 (the productization + factory precedents); orchestrator/replay.py `TacticalPolicyStamp` + `FSM_DEFAULT_POLICY_ID` (the default-mover identity the flip moves). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-champion-flip`
**Depends on:** 17.14
**Section refs:** locked decision 2 (the flip criterion: referee PASS + retained win edge at 17.14); agents/tactical/learned/factory.py + forward.py (the opt-in surface, swapped in place); training/reports/report-finalist-eval.md (the evidence); tasks/phase-15.md 15.20/15.21 (the productization + factory precedents); orchestrator/replay.py `TacticalPolicyStamp` + `FSM_DEFAULT_POLICY_ID` (the default-mover identity the flip moves)
**Complexity:** Integration

Read 17.14's evidence against locked decision 2 and act on the ruled branch. PASS
(referee floors + conversion + retained win edge): swap the committed champion artifact
to the winning finalist (weights + sha + config + stamp constants), then flip the
DEFAULT mover — the scripted-default factory yields to the learned factory as the
default policy (the run_tournament default, the orchestrator's default policy id, and
every surface that names `fsm-default` as the mover default), with the scripted FSM
retained as the named fallback/opt-out. FAIL: swap nothing OR swap the opt-in artifact
only if the new finalist referee-dominates the old one — either way the default stays
scripted and the finding is recorded. Both branches are contracted; the evidence
reading is quoted in the PR and ratified by the owner merging it. NO baseline records
here — 17.17 records the flipped substrate.

**Files in scope:**
- agents/tactical/learned/weights.json + .sha256 + config (the artifact swap)
- agents/tactical/learned/factory.py + forward.py (stamp constants; the default wiring on the PASS branch)
- scripts/run_tournament.py + orchestrator/ (the default-mover flip surfaces, PASS branch only)
- tests/ (stamp + default-identity re-pins on the ruled branch)

**Files NOT in scope:**
- replays/ (17.17 records)
- training/ (evidence is committed; this task consumes)

**Definition of done:**
- [ ] The evidence reading is stated against locked decision 2's criterion verbatim (each floor, the conversion figure, the win edge) and the ruled branch is fully implemented; on PASS the default-mover identity changes in every surface that names it (grepped and listed), the opt-out to the scripted FSM works and is fixture-pinned; on FAIL the default provably does not move.
- [ ] The committed artifact (if swapped) is sha-coherent (weights, sidecar, stamp constants, factory verification) and the provenance stamp names the new policy exactly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Grep for `fsm-default` and the factory-selection surfaces BEFORE writing: the flip is a
default-identity change in a small named set of places, and the DoD requires listing
them. Keep the scripted path fully alive behind the opt-out — the FSM is the fallback
and the anchor baseline for every future comparison.

## Integration risk

The default flip is the phase's riskiest single change: every replay consumer assumes
the mover identity stamped in recorded bytes, and committed sets were recorded
`fsm-default` — the flip must change FUTURE defaults without re-interpreting committed
history (stamps are per-record truth; nothing rewrites them). The 17.17 record is where
the flipped default first meets a canonical set — keep this task record-free.

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
Open a PR from branch `phase-17-champion-flip` with a title like `task 17.16: champion productization + the evidence-gated default flip`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing locked decision 2 (the flip criterion: referee PASS + retained win edge at 17.14); agents/tactical/learned/factory.py + forward.py (the opt-in surface, swapped in place); training/reports/report-finalist-eval.md (the evidence); tasks/phase-15.md 15.20/15.21 (the productization + factory precedents); orchestrator/replay.py `TacticalPolicyStamp` + `FSM_DEFAULT_POLICY_ID` (the default-mover identity the flip moves)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
