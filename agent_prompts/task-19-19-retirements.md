# Agent Prompt — 19.19 The retirements + the dead-code sweep (consumer-verified)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.19 — The retirements + the dead-code sweep (consumer-verified), anchored to audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the realpath docstring references in surviving files (training/coevo/hall_of_fame.py:279 `RealPathCandidate`, training/conviction/serving.py:301 `_TimeoutMeetingRunner` — rewritten with the deletion). NOTE 1: the five bespoke prompt-set dirs are NOT retired — all five are live (orchestrator/game.py:343-350; tests/agents/test_bespoke_prompt_sets.py loads every one); the source audits' deletion candidacy is REFUTED. NOTE 2: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-retirements`
**Depends on:** 19.1, 19.4, 19.6, 19.18 (19.1 is the llm/README.md serialization edge; 19.4 the tests/training/test_rewards.py edge; 19.6 the tests/llm/test_client.py edge)
**Section refs:** audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the realpath docstring references in surviving files (training/coevo/hall_of_fame.py:279 `RealPathCandidate`, training/conviction/serving.py:301 `_TimeoutMeetingRunner` — rewritten with the deletion). NOTE 1: the five bespoke prompt-set dirs are NOT retired — all five are live (orchestrator/game.py:343-350; tests/agents/test_bespoke_prompt_sets.py loads every one); the source audits' deletion candidacy is REFUTED. NOTE 2: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.
**Complexity:** Integration

Implement the tier map's RETIRE column plus the verified dead-code list, one deletion at
a time, each with a grep-proven consumer check recorded in the PR. Retire:
`training/realpath.py` + its test file (the ranking-row schema doc and committed rankings
survive — the map records where); the surrogate-ONLY meeting-runner exposure — with the
verified boundary respected: `load_surrogate_runner_factory` and
`SurrogateMeetingRunner` STAY (the composed runner's verification fence at
`composed_runner.py:266` and the harness at `:159/:1763/:2072` consume them, AST-pinned)
— the retire candidate is any config/CLI arm that runs the surrogate ALONE as a meeting
runner, and if the consumer grep proves no such consumer-free exposure exists, the
outcome is a recorded no-op for this item, not a forced deletion. The realpath deletion
carries a verified consumer migration: `scripts/generate_campaign_tables.py:76` imports
`RealPathRerankRow` from the module (its test imports the script), so the ranking-row
schema RELOCATES to a small surviving module (`training/realpath_schema.py`, new) with
its COMPLETE dependency closure — `RealPathSeedTelemetry` and the proof-block validators
the row model carries (`realpath.py:694/:760`) — and the script + test migrate onto it;
the schema's own defensive tests (the round-trip and invalid-proof cases currently
inside the deleted `test_realpath.py:4434` region) MOVE into a surviving
`tests/training/test_realpath_schema.py` rather than dying with the campaign tests — the
committed rankings' row contract survives the campaign machinery, validators and all. The `first_meeting` removal updates ALL its test constructors
(test_env.py:227-239, test_env_fast_path.py:141-154, test_rewards.py:115 — verified
list), and the cache deletion removes `llm/README.md`'s advertisement of the module
(:20-21) so 19.1's rewritten README does not point at a deleted API; the `first_meeting` episode
boundary (env + rollout plumbing; tests-only consumer); the stale crew-dir CLI
advertisement in run_tournament (the honest fail-loud behavior stays; the advertisement
of a stampless directory goes); `llm/cache.py` (+ its import in test_client);
`scripts/record_meeting_gate_probe.py`; `frontend/src/ui/SectionLabel.tsx`; and the
realpath docstring references left in surviving modules (hall_of_fame, conviction
serving — rewritten as historical notes, not left pointing at deleted APIs). The
bespoke prompt sets are NOT touched (live — see Section refs). Every deletion is
recoverable from git history; the PR lists each with its consumer-check output.

**Files in scope:**
- training/realpath.py; (deleted)
- tests/training/test_realpath.py; (deleted)
- training/realpath_schema.py (new — the relocated row contract with its full dependency closure: RealPathRerankRow + RealPathSeedTelemetry + the proof-block validators)
- tests/training/test_realpath_schema.py (new — the schema's round-trip + invalid-proof tests, MOVED from the deleted file)
- scripts/generate_campaign_tables.py; (the import migration onto the relocated schema)
- tests/scripts/test_generate_campaign_tables.py; (same)
- tests/training/test_env.py; (the first_meeting constructors)
- tests/training/test_env_fast_path.py; (same)
- tests/training/test_rewards.py; (the :115 boundary constructor)
- training/rewards.py; (docstring only — :278-281 still narrates a live "first-meeting opt-in episode" after the boundary retires; ordered behind 19.4's edit of the same file)
- llm/README.md; (EVERY PromptCache reference leaves with the module — the :20-21 inventory line AND the whole "Cache and budget composition" worked example at :126-147)
- training/coevo/driver.py; (the realpath reference rewrites only — :207, :281-283, :949)
- training/surrogate/runner.py; (the surrogate-only exposure, if the grep frees one)
- training/surrogate/; (ripple from the arm removal)
- training/bakeoff/harness.py; (only if a retired exposure ripples — record if touched)
- tests/training/test_bakeoff_harness.py; (the AST pins, only on ripple)
- tests/training/test_goodhart_probe.py; (only on ripple)
- tests/training/test_composed_runner.py; (only on ripple)
- tests/eval/test_balance_eval_meeting_runner.py; (only on ripple)
- training/env.py
- training/rollout.py
- tests/training/test_rollout.py
- tests/training/test_surrogate_runner.py
- tests/training/test_coevo_driver.py; (the :1764 realpath docstring reference + any removal ripple)
- tests/training/test_finalist_eval_pins.py; (ONLY the module-reference docstrings at :35-36/:40/:921/:1086-1087 — the `realpath-crew/` ARTIFACT paths at :484/:554 are data paths to committed bytes and stay untouched)
- scripts/run_tournament.py
- tests/scripts/test_run_tournament.py
- scripts/record_meeting_gate_probe.py; (deleted)
- llm/cache.py; (deleted)
- tests/llm/test_client.py; (the cache import removed)
- frontend/src/ui/SectionLabel.tsx; (deleted)
- training/coevo/hall_of_fame.py; (the :279 realpath docstring reference only)
- training/conviction/serving.py; (the :301 realpath docstring reference only)

**Files NOT in scope:**
- eval/determinism_test.py (NOT dead — see Section refs; it stays)
- agents/strategic/prompts/ (all sets live; nothing here moves)
- training/composed_runner.py + the conviction/compact-inference surfaces (KEEP column)
- frontend/src/api/ (dead client methods are backlog — they collide with 19.13/19.24)

**Definition of done:**
- [ ] Every deletion carries its consumer-check grep output in the PR; every skipped candidate (failed grep) is named with the blocking consumer.
- [ ] The surrogate boundary is proven: `load_surrogate_runner_factory`/`SurrogateMeetingRunner` and every verified consumer (composed runner fence, harness, the AST pins) are untouched and green; the surrogate-only exposure is either retired with its consumer grep quoted or recorded as no-consumer-free-exposure (a documented no-op), never force-deleted.
- [ ] `first_meeting` is gone from env/rollout with the three production call sites unchanged (`full_game` explicit) and every former boundary-constructing test (the verified list in the prose) updated and green.
- [ ] `RealPathRerankRow` lives in the surviving schema module WITH its complete closure (`RealPathSeedTelemetry`, the proof-block validators) and its defensive tests (round-trip, invalid-proof) alive in `test_realpath_schema.py`; `generate_campaign_tables` and its test consume it there; the committed rankings and `measurement-stability.json` pins are untouched.
- [ ] The full gate is green after all deletions; the gate-runtime delta is quoted in the PR.
- [ ] A repo-wide grep for `training.realpath` / `realpath.py` returns zero live references outside historical records (audits/, training/reports/, committed provenance) and outside `realpath-crew/` ARTIFACT paths (data, not module references) — the verified reference sites (hall_of_fame:279, serving:301, driver:207/:281-283/:949, test_coevo_driver:1764, test_finalist_eval_pins:35-36/:40/:921/:1086-1087) plus any the closing grep surfaces.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Order the deletions leaf-first (cache → gate probe → SectionLabel → first_meeting →
standalone arm → realpath) so each gate run isolates one removal. The realpath docstring
rewrites in hall_of_fame/serving land in the same commit as the module deletion so no
intermediate state points at a missing API; keep the historical facts, change the tense
and drop the dotted-path references.

## Public types this task introduces
- `training.realpath_schema.RealPathRerankRow`
- `training.realpath_schema.RealPathSeedTelemetry`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Deletions across five packages in one branch. The guards: leaf-first commit ordering with
the suite green at each step, the consumer-check discipline (nothing deleted on an
audit's say-so alone — the audits themselves got `eval/determinism_test.py` wrong, and
the first Codex review caught two more unlisted consumers, which is why the check is
mandatory), and the composed-runner dependency boundary pinned by its existing tests
before the standalone arm is removed. This contract MAY land as a reviewed sequence of
stacked PRs on the task branch (leaf-first boundaries are natural cut points); the
coordination session sanctions the split at dispatch, and the DoD applies to the
sequence's tip.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-19-retirements` with a title like `task 19.19: the retirements + the dead-code sweep (consumer-verified)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 19 (retire set) + singleton 31 + claude §4 item 16 [S-Claude/S-Codex; consumer checks mandatory] + locked decision 2; training/realpath.py (4,470 LOC; the one-shot campaign ops surface) + tests/training/test_realpath.py (4,601 LOC; wall-clock asserts :288/:320-322/:3307-3309); training/surrogate/runner.py:383 (`load_surrogate_runner_factory`) — VERIFIED LIVE CONSUMERS: training/composed_runner.py:266 (the sha/staleness verification fence) and training/bakeoff/harness.py:159/:1763/:2072, with AST call-site pins at tests/training/test_bakeoff_harness.py:1742-1772 — so the factory and class STAY and only a surrogate-ONLY runner exposure proven consumer-free may retire; training/env.py:1037-1056 (`first_meeting` — production callers all pass `full_game`: crew/scorer.py:946, bakeoff/harness.py:722, coevo/rollout.py:214); scripts/run_tournament.py:102-105 (the stale crew-dir CLI advertisement); llm/cache.py (192 LOC; sole importer tests/llm/test_client.py:12); scripts/record_meeting_gate_probe.py (zero references); frontend/src/ui/SectionLabel.tsx (dead); the realpath docstring references in surviving files (training/coevo/hall_of_fame.py:279 `RealPathCandidate`, training/conviction/serving.py:301 `_TimeoutMeetingRunner` — rewritten with the deletion). NOTE 1: the five bespoke prompt-set dirs are NOT retired — all five are live (orchestrator/game.py:343-350; tests/agents/test_bespoke_prompt_sets.py loads every one); the source audits' deletion candidacy is REFUTED. NOTE 2: eval/determinism_test.py is NOT retired — the planning session verified pytest collects it (`*_test.py`) and README cites it as the engine-purity proof; the source audit's "exercised by nothing" is REFUTED.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
