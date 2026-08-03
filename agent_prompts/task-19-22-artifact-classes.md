# Agent Prompt — 19.22 Artifact classes + the coevo prune + the fast-clone path

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.22 — Artifact classes + the coevo prune + the fast-clone path, anchored to audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-artifact-classes`
**Depends on:** 19.13, 19.19
**Section refs:** audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics)
**Complexity:** Medium

Implement locked decision 5. `docs/artifacts.md` defines the four artifact classes:
(a) small canonical fixtures in git; (b) manifests/hashes/summaries in git; (c) large
immutable evidence in the evidence branch; (d) disposable regenerated views. Then the
prune: FIRST enumerate every byte the two consumer test files pin (they are the
authority — the enumeration is the contract's first step and its output is committed
into the manifest); everything else under `training/artifacts/coevo/` moves to the
orphan evidence branch `evidence/phase-18-coevo` with a per-file sha-256 manifest
committed in-tree. Pinned bytes, `measurement-stability.json`, and the provenance
records stay in-tree. `replays/` does not move (locked decision 5). README and the
reading guide document `git clone --filter=blob:none` as the fast path, with the honest
caveat that full-history clones stay heavy absent a future deliberate rewrite.

**Files in scope:**
- training/artifacts/coevo/; (the prune — unpinned bytes removed from the working tree)
- docs/artifacts.md (new)
- README.md; (the fast-clone note)
- docs/reading-guide.md; (the same note where the guide describes cloning)
- scripts/fetch_evidence.sh (new — a small helper that checks out the evidence branch's bytes back into place)

**Files NOT in scope:**
- replays/ (stays whole — locked decision 5)
- tests/scripts/test_generate_campaign_tables.py + tests/training/test_finalist_eval_pins.py (their pinned bytes must remain in-tree so the tests are untouched)
- .git history (no rewrite)

**Definition of done:**
- [ ] The consumer enumeration is committed (the manifest marks each retained path with its pinning test); the full suite passes with NO test edits — the prune provably removed only unpinned bytes.
- [ ] The evidence branch exists, its bytes match the manifest sha-for-sha, and `scripts/fetch_evidence.sh` restores them; the working-tree size reduction is quoted in the PR.
- [ ] The fast-clone path is documented with the honest history caveat.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Build the retained-path allowlist by parsing the two test files' path literals plus
`training/artifacts/coevo/PATHS.md`/provenance conventions, then verify by running the
suite against a scratch tree with everything else removed BEFORE committing the prune.
The evidence branch is orphan (`git checkout --orphan evidence/phase-18-coevo`) carrying
only the moved bytes + a README naming the manifest commit.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-artifact-classes` with a title like `task 19.22: artifact classes + the coevo prune + the fast-clone path`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 23 [C; VERIFIED §8 row 11] + locked decision 5; the verified consumer set (planning session): exactly two test files read coevo bytes — tests/scripts/test_generate_campaign_tables.py (pins `measurement-stability.json` key-for-key) and tests/training/test_finalist_eval_pins.py (pins weights under `intermediates/`, `runnerups/`, run-01/run-c1/run-c2 generation dirs, and `realpath-crew/controls/…`); the tree: training/artifacts/coevo = ~109MB / 1,473 files, the realpath* subtrees ~104MB / 403 files; audits/audit-phase-18-close.md §6.3 C4 (the coevo namespace rules — the prune must not disturb `DEFAULT_RANKING_ROOTS` semantics)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
