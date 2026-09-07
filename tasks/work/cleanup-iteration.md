# Make cleanup delivery and experiment decisions easy to review

**Status:** done

## Outcome

Keep a small active queue, concise universal instructions, and a navigable
review ledger that distinguishes code delivery from experimental adoption.

## Evidence

The card pilot and first three parallel repairs now have concrete evidence:
the pilot's reviewer found parser defects, and the recording batch required
coordinated manifest and historical-loader follow-through. The original
235-line AGENTS.md still repeats detailed procedures on every task.

## Acceptance

- [x] Evaluate the pilot from recorded interventions, scope follow-through,
  verification, and independent review findings without inventing time savings.
- [x] Move detailed procedures to linked documentation while preserving the
  architectural, craft, verification, provider-budget, and final-review rules.
- [x] Keep task ownership and delivered commits visible; distinguish
  implementation, verification, independent review, merge, and adoption.
- [x] Preserve separate gameplay-first and code-first experiment findings and
  explicit budgets, held-out decision rules, and retirement conditions.
- [x] Existing workflow guards, historical prompt checks, and the full gate pass.

## Constraints

Follow `docs/architecture.md` and the owner's final-review/cleanup-branch policy.
No generated scheduling platform, historical contract edits, gameplay changes,
or live provider calls. New experiment adoption still needs measured evidence.

## Expected scope

`AGENTS.md`, `docs/workflow.md`, new `docs/agent-procedures.md`,
`tasks/README.md`, `tasks/cleanup-roadmap.md`, `tasks/review-ledger.md`, and this
card. Existing validators remain the enforcement mechanism; no new parser needed.

## Record impact

None. Process and review documentation do not modify simulation evidence.

## Validation

Run `uv run pytest tests/scripts/test_work_cards.py
tests/scripts/test_task_doc_guards.py`, the task and prompt validators,
`git diff --check`, and `bash scripts/check.sh`. Inspect the document move for
preserved rules and the ledger against actual branch commits and card results.

## Results

The pilot assessment in docs/workflow.md uses the recorded owner correction to
delivery, the explicit manifest/historical-reader scope follow-through, and
independent parser defects found during review. Verification counts and elapsed
test time are evidence of checking, not a claim about developer time saved.

AGENTS.md is 90 lines instead of 235. The detailed retirement, environment,
history, and GitHub/PR procedures live in docs/agent-procedures.md; current
provider details remain in llm/README.md and .env.example. Independent review
checked preservation of the engine, firewall, state, craft, retirement, setup,
dependency, complete-history, full-gate, and owner-review rules. The review ledger
references verified commit identities and keeps implementation and experimental
adoption separate. Its eleven existing task/planning/index commit references
resolve in the full-history checkout and none is an ancestor of main.

Thirty-seven focused work-card and historical-contract tests passed, and all
390 generated historical prompts remain in sync. The code-review agent's wider
audit/workflow selection passed 361 tests. No scheduling system, new prompt
copies, historical contract edits, or adoption decision was introduced. The combined project gate passed, as recorded below.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Code-review agent; rule preservation and full-history ledger references checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.
