# Cleanup corrections and gameplay work

The cleanup merged into **`main`** on 2026-09-07 (`8161689a`, PR #435). The
earlier 26-card handoff covered 49 priorities through repairs, experiments and
retained decisions; the owner's independent Claude review reproduced incomplete
acceptance items, and the cards it reopened were corrected before that merge.
New implementation goes on a `work/<card-slug>` branch and reaches `main` by
pull request. Experimental adoption remains a separate owner decision.

The [post-review plan](post-review-plan.md) orders corrections, trustworthy
evaluation, one playable deduction case, meeting replies, investigation and a
separately budgeted fresh-model decision. The supplied
[review and findings](../audits/review-2026-09-06/README.md) are preserved verbatim.
The owner's later follow-up report and appendix are archived beside them by the
[follow-up review archive](work/followup-review-archive.md).

## Active ownership

No card is active. The [post-merge plan](post-merge-plan.md#ownership) holds the
writer-to-file table for the seven queued cards; it takes effect when the owner
dispatches one.

Cards own precise acceptance and file boundaries. Each card's worker commits on
that card's branch; the coordinator serializes shared-file handovers and owns
the planning commits on `main`.

Start with the [review ledger](review-ledger.md) for commits, independent reviews
and verification. The [roadmap](cleanup-roadmap.md) preserves priority numbers;
the [current finding dispositions](../docs/cleanup-dispositions.md) account for
all 104 original findings and the carried close/hardening routes. Historical
findings and current repairs remain distinct.

## Card inventory

As of 2026-09-09, `tasks/work/` holds 43 cards: 3 ready, 40 done. That sentence
is derived, not typed: `scripts/validate_task_docs.py` recomputes the total and
the per-status breakdown from the cards themselves and fails when either drifts,
so flipping one card's Status is enough to make this paragraph wrong out loud.
A card's `Status` is its work state; the delivery states each card reached are
in [the review ledger](review-ledger.md) and defined in
[the workflow](../docs/workflow.md).

## Original implementation inventory

Each card owns its acceptance criteria, decisions, measurements and limitations.
The ledger retains original PR links for inherited work; those PRs remain review
records and were not managed during the cleanup. #431 became merged by
reachability when the cleanup landed; #432-#434 were closed on 2026-09-07 once
their commits were on `main`.

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
The [bounded investigation](work/bounded-investigation.md) implementation and
[source-bound comparisons](../audits/investigation-candidate/README.md) are verified.
The [fresh-evaluation plan](work/fresh-deduction-evaluation.md) is complete as
planning only. New work uses [one canonical work card](../docs/workflow.md), with evidence, acceptance,
record impact, measurement and one writer per shared file. Preserve the separate
gameplay-first and code-first investigations before combining their decisions.

Temporal and reasoning changes remain OFF until an adopting record. Tactical
comparisons preserve their measured losses and require a separate promotion
decision; fake outcomes do not establish model quality. Live provider use needs
an explicit budget. Q1 search, Phase C co-evolution resumption and a corpus refit
remain distinct decisions, with no new research campaign chartered here.

The [post-merge plan](post-merge-plan.md) queues eight cards against the
archived follow-up review, with candidates still OFF: id-level
[review dispositions](work/followup-review-dispositions.md), the
[renderer salience repair](work/evidence-renderer-salience.md), the
[recorded-provenance gaps](work/recorded-provenance-gaps.md),
[accounts-channel hardening](work/accounts-channel-hardening.md), the
[fresh-model deduction instrument](work/fresh-deduction-instrument.md), the
[held-out prefix freeze](work/held-out-prefix-freeze.md) that prepared its
inputs (done, #438), the [nonblocking improvements](work/nonblocking-followup-improvements.md), and
[retiring temporal v1 and evidence v1](work/retire-temporal-evidence-v1.md).
These are planning documents; none is implemented, and none authorizes a live
provider call or an experimental adoption. The instrument's provider, token,
wall-clock and cost limits were authorized by the owner's merge of #437 on
2026-09-07 through [the authorization card](work/fresh-deduction-authorization.md);
no run is authorized until the renderer and provenance cards, the execution
manifest and the held-out freeze land. The retirement card is blocked until an
adopting record for evidence v2 exists.

Historical `phase-*.md` contracts and their generated `agent_prompts/` exports
remain unchanged and validated. Use them when resuming that historical work;
new cards do not generate duplicate prompts. `compute_next_task.py` continues
to serve phase contracts only.
