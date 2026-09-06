# Cleanup corrections and gameplay work

Implementation continues on **`codex/cleanup`** after the owner's independent
Claude review. The earlier 26-card handoff covered 49 priorities through repairs,
experiments and retained decisions; the review reproduced incomplete acceptance
items, so affected cards are reopened. Main remains unchanged. The owner decides
the final merge and any experimental adoption separately.

The [post-review plan](post-review-plan.md) orders corrections, trustworthy
evaluation, one playable deduction case, meeting replies, investigation and a
separately budgeted fresh-model decision. The supplied
[review and findings](../audits/review-2026-09-06/README.md) are preserved verbatim.

## Active ownership

| Worker | Current scope |
| --- | --- |
| Recording worker | Replacement, publication, output protection, unresolved accounting |
| Viewer worker | Private confidence, stale-result copy, media and public claims |
| Report worker | Historical projection, isolated collection, terminal type fixture |
| Coordinator | Source-bound summary cache, review archive, integration and scenario plan |

Cards own precise acceptance and file boundaries. The coordinator serializes
shared-file handovers and commits; implementation workers do not commit.

Start with the [review ledger](review-ledger.md) for commits, independent reviews
and verification. The [roadmap](cleanup-roadmap.md) preserves priority numbers;
the [current finding dispositions](../docs/cleanup-dispositions.md) account for
all 104 original findings and the carried close/hardening routes. Historical
findings and current repairs remain distinct.

## Original implementation inventory

Each card owns its acceptance criteria, decisions, measurements and limitations.
The ledger retains original PR links for inherited work; those PRs remain review
records and have not been merged or otherwise managed during cleanup.

| Outcome | Cards |
| --- | --- |
| Working method and branch delivery | [Workflow pilot](work/workflow-pilot.md), [cleanup delivery](work/cleanup-delivery.md), [iteration](work/cleanup-iteration.md) |
| Provider accounting | [Budget accounting](work/budget-accounting.md), [aborted calls](work/aborted-meeting-calls.md), [completed attempts](work/completed-meeting-attempts.md) |
| Recording and reporting | [Replay integrity](work/replay-integrity.md), [recording replacement](work/recording-replacement.md), [report destinations](work/report-destinations.md), [evaluation integrity](work/evaluation-replay-integrity.md), [completion status](work/report-completion-status.md), [tournament lifecycle](work/tournament-lifecycle.md) |
| Public facts and reproduction | [Public provenance](work/public-recording-provenance.md), [dependencies](work/dependency-advisories.md), [portfolio experience](work/portfolio-evidence-experience.md) |
| Gameplay and evidence | [Temporal observations](work/temporal-observation-contract.md), [reasoning experiments](work/reasoning-evidence-experiments.md), [tactical experiments](work/tactical-gameplay-experiments.md) |
| Engineering boundaries | [Map traversal](work/map-traversal-contract.md), [replay loading](work/replay-loading-performance.md), [model provenance](work/model-evidence-provenance.md), [protocol retirement](work/protocol-retirement.md), [semantic validation](work/semantic-validation.md) |
| Claim checking and synthesis | [Audit facts](work/audit-fact-gates.md), [carried findings](work/carried-audit-dispositions.md), [synthesis](work/cleanup-synthesis.md) |

The original handoff's local verification passed 6,775 Python tests, 489 frontend tests and all
335 campaign-tier tests, plus typing, lint, formatting, import/document contracts
and the production build. All 100 canonical recordings verified. The isolated
API/static browser suite passed 13 tests with three intentional media skips.
The ledger states the ordinary Python skips, expected failures and archived
ML-evidence availability limits.

## Review follow-through

The current queue follows the [authorized plan](post-review-plan.md), including
the completed [public-results cache](work/public-results-cache.md). The verified checkpoint
binds [evaluation identity](work/experimental-evaluation-integrity.md),
repairs [evidence timing](work/temporal-evidence-v2.md), adds
[attributed public accounts](work/attributed-public-accounts.md), and compares
their mechanisms through the [finite scenario matrix](work/deduction-evaluation-matrix.md).
The next runtime card is [bounded investigation](work/bounded-investigation.md).
The [fresh-evaluation plan](work/fresh-deduction-evaluation.md) is complete as
planning only. New work uses [one canonical work card](../docs/workflow.md), with evidence, acceptance,
record impact, measurement and one writer per shared file. Preserve the separate
gameplay-first and code-first investigations before combining their decisions.

Temporal and reasoning changes remain OFF until an adopting record. Tactical
comparisons preserve their measured losses and require a separate promotion
decision; fake outcomes do not establish model quality. Live provider use needs
an explicit budget. Q1 search, Phase C co-evolution resumption and a corpus refit
remain distinct decisions, with no new research campaign chartered here.

Historical `phase-*.md` contracts and their generated `agent_prompts/` exports
remain unchanged and validated. Use them when resuming that historical work;
new cards do not generate duplicate prompts. `compute_next_task.py` continues
to serve phase contracts only.
