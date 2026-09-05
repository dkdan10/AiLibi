# Keep cleanup work on the owner's working branch

**Status:** done

## Outcome

Implement the cleanup backlog on `codex/cleanup`, with focused commits and
per-task review evidence. The owner arranges Claude's review after the cleanup
is complete, followed by the final merge into `main`.

## Evidence

The owner's 2026-09-05 instruction replaces the earlier recommendation to merge
intermediate cleanup milestones into main. The branch already contains the five
commits from PRs 431–434. Standing instructions still assume per-task PR delivery
and need an explicit commit-based path for this working branch.

## Acceptance

- [x] Standing instructions identify `codex/cleanup` as the working branch and
  reserve the final main merge for the owner after Claude's review.
- [x] Commit-based delivery retains task boundaries, validation evidence,
  decisions, contract references, and the existing repair review records.
- [x] Existing CI jobs are configured for cleanup pushes without requiring a per-task PR.
- [x] No new implementation branch, PR mutation, or main merge is performed.
- [x] Task documentation checks and the full project gate pass.

## Constraints

Preserve `docs/architecture.md` Layering and Determinism and the substrate ladder.
This changes delivery instructions and the existing CI branch trigger only.
Keep independent implementation review, required checks, historical contracts,
baseline decisions, and live-run budget requirements. Do not implement another
backlog item as part of this card.

## Expected scope

`AGENTS.md`, `docs/workflow.md`, `tasks/README.md`, `.github/workflows/ci.yml`,
and this card. The CI trigger is directly necessary follow-through for delivering
commits without per-task PRs; the jobs, permissions, and deployment workflow stay
unchanged.

## Record impact

None. No simulation, prompt, detector, replay, or public API behavior changes.

## Validation

Run `uv run python scripts/validate_task_docs.py`, `git diff --check`, and
`bash scripts/check.sh`. Parse the CI YAML and verify the added push branch,
unchanged job definitions, and unchanged deployment workflow. Inspect the diff
paths and branch before committing. No new tests are needed for this instruction
and branch-trigger change.

## Results

Verified 2026-09-05. `bash scripts/check.sh` passed: 6,214 Python tests
(20 skips, 3 expected failures), 440 frontend tests, lint, formatting, imports,
strict types, and build. Task validation passed for all 390 historical tasks
and prompts plus six work cards; `git diff --check` passed.

Independent review identified two remaining PR-only/review-routing phrases;
both now distinguish per-task implementation review and card evidence from the
owner's final Claude review. The task index maps the five inherited commits to
their four existing PRs. Implementation and the final commit stay on
`codex/cleanup`; no existing PR or main branch is changed.

Directly necessary follow-through: enable the existing CI workflow for cleanup
pushes because per-task PR creation is optional. Parsed the YAML with PyYAML's
BaseLoader, asserted the push branches are `main` and `codex/cleanup`, then
restored that field in memory and compared the entire configuration with HEAD:
equal. The job definitions and permissions are unchanged, and the deployment
workflow has no diff. This establishes configuration, not a claim that a future
GitHub run has already passed.

References: `docs/architecture.md` Layering and Determinism and the substrate
ladder remain unchanged; `docs/workflow.md` Cleanup delivery implements the
owner's branch and final-review instruction. No simulation record or baseline
impact. Claude's final review and the owner's merge remain pending.
