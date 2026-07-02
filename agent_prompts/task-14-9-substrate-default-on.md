# Agent Prompt — 14.9 Make the adopted 13.5 levers default-ON + retire the flag-OFF path

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.9 — Make the adopted 13.5 levers default-ON + retire the flag-OFF path, anchored to tasks/phase-13-5.md (the 4 levers); tasks/phase-14.md (the 14.7 flags-ON baseline + 14.8 ablation); agents/memory/store.py + meetings/transcript.py + observation/service.py + orchestrator/game.py (the `*_enabled()` resolvers). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-substrate-default-on`
**Depends on:** 14.8
**Section refs:** tasks/phase-13-5.md (the 4 levers); tasks/phase-14.md (the 14.7 flags-ON baseline + 14.8 ablation); agents/memory/store.py + meetings/transcript.py + observation/service.py + orchestrator/game.py (the `*_enabled()` resolvers)
**Complexity:** Integration

With the new baseline recorded flags-ON (14.7) and the per-lever ablation in hand (14.8), finish the
integration: make the adopted 13.5 levers the DEFAULT behavior and retire the now-vestigial flag-OFF path. Per
owner decision 2026-06-26 all 4 flags are adopted (the ablation is characterization, not a veto): flip the 4
`*_enabled()` resolvers to default-ON (or remove the env gate entirely), delete the now-dead OFF branches, and
retarget the flag-OFF byte-identity tests onto the flags-ON baseline. The committed replays are already
flags-ON (14.7), so reconstruction no longer needs the env vars set and the determinism story simplifies.

**Files in scope:**
- agents/memory/store.py (testimony + movement-sighting derivation becomes unconditional; the OFF branch + `ENV_TESTIMONY_AS_CONTENT` / `testimony_as_content_enabled` gate retired)
- meetings/transcript.py (`witnessed_kill_evidence_enabled` gate retired; kill-scene + witness-belief derivation unconditional)
- observation/service.py (`movement_perception_enabled` gate retired; the empty-tuple OFF branch removed)
- orchestrator/game.py (`unfreeze_memory_enabled` gate retired; the `rerender_memory is None` OFF branch removed)
- agents/memory/beliefs.py (the witnessed-kill suspicion read becomes unconditional)
- api/replay_loader.py (reconstruction no longer reads the flags — the corrected derivation is unconditional; the substrate-mismatch guard stays coherent for legacy stamped replays)
- orchestrator/replay.py (`substrate_flag_snapshot()` lazy-imports the four `*_enabled()` resolvers this task deletes — rework it to report the retired levers as unconditionally ON, keeping the stamp machinery generic for future levers like 14.10's)
- tests/ (the flag-OFF byte-identity / flag-toggle tests across tests/agents/ + tests/meetings/ + tests/observation/ + tests/orchestrator/ retargeted onto the flags-ON baseline)
- .env.example (remove the now-defunct flag knobs)

**Files NOT in scope:**
- replays/samples/ (the 14.7 flags-ON bytes ARE the baseline; this changes no replay)
- agents/strategic/prompts/ (the prompt sets are 14.2/14.5)
- llm/ (the provider is 14.1)
- scripts/_manifest_writer.py (the `flags` column from 14.7 stays as provenance even though the flags are no longer toggleable)

**Definition of done:**
- [ ] The 4 adopted levers are DEFAULT behavior (the `*_enabled()` env gates default-ON or removed); the now-dead flag-OFF branches and env constants are deleted, not left vestigial.
- [ ] The committed flags-ON baseline (14.7) reconstructs byte-identically WITHOUT any env vars set (`scripts/verify_samples.sh` under a bare environment); the MANIFEST/replay `flags` stamp reads "all 4 ON" and is consistent with the now-unconditional behavior.
- [ ] `orchestrator/replay.py`'s `substrate_flag_snapshot()` no longer imports the retired resolvers (the four levers report unconditionally ON); the loader's substrate-mismatch guard still validates legacy stamped replays; the stamp machinery stays generic so 14.10 can register its new lever.
- [ ] The former flag-OFF byte-identity tests are retargeted onto the flags-ON baseline (or deleted with rationale); no test asserts the retired OFF behavior; the leak suite stays green at 4p1i and 9p2i.
- [ ] `.env.example` no longer advertises the retired flag knobs.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

A pure simplification gated on the 14.7 baseline existing flags-ON: the corrected derivation becomes
unconditional, so the `*_enabled()` resolvers + their OFF branches + the env constants
(`ENV_TESTIMONY_AS_CONTENT` / `ENV_WITNESSED_KILL_EVIDENCE` / `ENV_MOVEMENT_PERCEPTION` /
`ENV_UNFREEZE_MEMORY`) can be deleted. Do it lever-by-lever, re-running `scripts/verify_samples.sh` under a
BARE environment after each so any residual flag-read is caught immediately. The `flags` MANIFEST column
(14.7) stays as provenance even though the flags are no longer toggleable — it records that this baseline was
generated on the corrected substrate. Note the tail of the phase: 14.12 re-records baseline 2 after the
14.10/14.11 fixes and re-pins the byte tests once more — keep this task's retargeting mechanical so that
second re-pin is cheap.

## Integration risk

Touches the exact files 13.5 just landed (`store.py`, `transcript.py`, `observation/service.py`, `game.py`,
`beliefs.py`, `replay_loader.py`) and the committed-baseline tests — a missed OFF-branch deletion or a test
still asserting flag-OFF behavior breaks the suite. Sequence AFTER 14.7 (the baseline must be flags-ON first)
and 14.8 (the ablation must confirm no lever is harmful; if one is, STOP and escalate rather than silently
dropping it — the owner adopted all 4). The reconstruction must be byte-identical under a BARE environment
once the gates are removed — that is the acceptance bar; verify it explicitly.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-substrate-default-on` with a title like `task 14.9: make the adopted 13.5 levers default-on + retire the flag-off path`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-13-5.md (the 4 levers); tasks/phase-14.md (the 14.7 flags-ON baseline + 14.8 ablation); agents/memory/store.py + meetings/transcript.py + observation/service.py + orchestrator/game.py (the `*_enabled()` resolvers)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
