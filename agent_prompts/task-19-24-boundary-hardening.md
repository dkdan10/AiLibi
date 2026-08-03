# Agent Prompt — 19.24 Boundary hardening: the leak-scan library, `moved_players`, `intent.actor`, the API factory, DTO versions

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.24 — Boundary hardening: the leak-scan library, `moved_players`, `intent.actor`, the API factory, DTO versions, anchored to audits/audit-phase-19-triage.md §7 item 26 [S-Claude/S-Codex; §8 row 16; the DTO cast and the CWD import re-verified at HEAD: frontend/src/api/client.ts:51 (`data as T`), api/main.py:24-27 (CWD-relative fallbacks) + :188 (module-scope `create_app()`)]; eval/leak_test.py:9 (module-level pytest import) + :719 (`scan_factory_packets`) + training/bakeoff/harness.py:107 (the champion-gate path importing a pytest module); observation/service.py:458-506 (`_moved_players_for_agent` — the one packet channel with ZERO leak-suite coverage, whose docstring narrates a prior gating bug); orchestrator/game.py:2024-2033 (no `intent.actor` validation); frontend/src/types/api.ts:25 (`viewModelVersion: string`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-boundary-hardening`
**Depends on:** 19.2, 19.11, 19.12, 19.13, 19.14, 19.19 (the 19.12 edge: the client-side rejection test needs the vitest baseline to exist)
**Section refs:** audits/audit-phase-19-triage.md §7 item 26 [S-Claude/S-Codex; §8 row 16; the DTO cast and the CWD import re-verified at HEAD: frontend/src/api/client.ts:51 (`data as T`), api/main.py:24-27 (CWD-relative fallbacks) + :188 (module-scope `create_app()`)]; eval/leak_test.py:9 (module-level pytest import) + :719 (`scan_factory_packets`) + training/bakeoff/harness.py:107 (the champion-gate path importing a pytest module); observation/service.py:458-506 (`_moved_players_for_agent` — the one packet channel with ZERO leak-suite coverage, whose docstring narrates a prior gating bug); orchestrator/game.py:2024-2033 (no `intent.actor` validation); frontend/src/types/api.ts:25 (`viewModelVersion: string`)
**Complexity:** Integration

Five hardening moves on the project's trust boundaries. (a) Promote the packet scanners
to `eval/leak_scan.py` (a library with no pytest import); `eval/leak_test.py` becomes the
thin pytest wrapper; the harness imports the library — pytest leaves the champion-gate
import path. Every existing planted-leak self-test must still bite (the gates prove they
can fail — that property is the crown jewel; this move is import-path only). (b) Add
`moved_players` witness-gating coverage to the leak suite: the Hypothesis property sweep
and a planted-leak self-test proving the new scanner detects a violation. (c) One line at
the orchestrator boundary: `intent.actor == player_id` validation, fail-loud, with a
test — the seam the architecture explicitly anticipates learned movers on. (d) A
CWD-independent API factory: the data root resolves from an injected/config value or the
repo anchor, never the working directory; import-from-elsewhere is tested. (e) Runtime
DTO version rejection: the generator emits a literal version constant; the client rejects
a mismatched `viewModelVersion` loudly (and the static demo bundle bakes the matching
constant, so 19.13's artifact keeps working).

**Files in scope:**
- eval/leak_scan.py (new)
- eval/leak_test.py
- training/bakeoff/harness.py; (the import swap at :107 only)
- training/crew/scorer.py; (the same import swap at :113 — a second verified production consumer, transitively imported by the coevo stack and run_tournament)
- tests/observation/test_leak_property.py
- tests/observation/
- orchestrator/game.py; (the one-line validation + test hook)
- tests/orchestrator/
- api/main.py
- tests/api/
- scripts/gen_frontend_types.py; (the version-constant emission)
- frontend/src/types/api.ts; (regenerated)
- frontend/src/types/api.fidelity.ts; (regenerated — both generator artifacts)
- frontend/src/api/client.ts
- frontend/src/api/client.test.ts (new — the executable mismatch-rejection test on 19.12's vitest baseline)

**Files NOT in scope:**
- observation/service.py (covered, not changed)
- eval/leak_test.py's scanner SEMANTICS (the move is mechanical; scanner behavior changes are out)
- api/replay_loader.py (19.11 was the last writer; the loader does not move here)

**Definition of done:**
- [ ] Verify-then-fix for the DTO-cast claim: re-confirm the unvalidated cast at HEAD before adding rejection (re-verified by the planning session; re-run in-session).
- [ ] `import eval.leak_scan` succeeds without pytest installed in the environment probe (test-pinned); NEITHER production consumer (the harness at :107, the crew scorer at :113) transitively imports pytest after the swap — proven with the `--no-dev --exact` probe from 19.7's idiom; every pre-existing planted-leak self-test still fails when its leak is planted.
- [ ] The `moved_players` property sweep runs in the leak suite with its planted-leak proof; the leak-suite gap named by the audits is closed.
- [ ] A forged `intent.actor` fails loud at the boundary (test); the API imports and serves from a foreign CWD (test); a version-mismatched payload is rejected loudly client-side — proven by an executable vitest case (`client.test.ts`), not a cast replacement — and the demo bundle still passes its 19.13 test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The scanner move: `leak_scan.py` takes the scanner functions and constants verbatim
(`_walk_json`, the forbidden-field/value scanners, `scan_factory_packets` AND its
reconstruction dependencies — `collect_factory_packet_records` /
`_reconstruct_factory_records`, i.e. the replay walk the scan path needs);
`leak_test.py` re-exports for its tests and keeps every test body. The property sweep
already imports production scanners (tests/observation/test_leak_property.py:59-66) —
point those imports at the library. For `moved_players`: the docstring at
`observation/service.py:464-489` narrates the exact bug class to scan for (post-advance
visibility gating); the planted leak plants that bug.

## Public types this task introduces
- `eval.leak_scan.scan_factory_packets`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Touching the leak suite and the champion-gate import path in one PR. The invariant that
cannot regress: every scanner that could bite before still bites (run the planted-leak
matrix before and after the move and diff the outcomes — identical or the PR stops).
The DTO version rejection risks breaking the demo bundle and dev flows on skew — the
generated constant keeps client and server in lockstep through the same codegen.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`
- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`

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
Open a PR from branch `phase-19-boundary-hardening` with a title like `task 19.24: boundary hardening: the leak-scan library, `moved_players`, `intent.actor`, the api factory, dto versions`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 26 [S-Claude/S-Codex; §8 row 16; the DTO cast and the CWD import re-verified at HEAD: frontend/src/api/client.ts:51 (`data as T`), api/main.py:24-27 (CWD-relative fallbacks) + :188 (module-scope `create_app()`)]; eval/leak_test.py:9 (module-level pytest import) + :719 (`scan_factory_packets`) + training/bakeoff/harness.py:107 (the champion-gate path importing a pytest module); observation/service.py:458-506 (`_moved_players_for_agent` — the one packet channel with ZERO leak-suite coverage, whose docstring narrates a prior gating bug); orchestrator/game.py:2024-2033 (no `intent.actor` validation); frontend/src/types/api.ts:25 (`viewModelVersion: string`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
