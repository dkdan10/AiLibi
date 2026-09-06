# Current work

Work directly on `codex/cleanup`. The owner will have Claude review the completed
cleanup by commit or PR, then arrange the final merge into `main`. Keep `main`
unchanged until then. Deliver each task as a focused, verified commit or small
commit sequence, with its evidence in the card's Results. See
[cleanup delivery](../docs/workflow.md#cleanup-delivery).

The next release should make simulation records accurate and the evidence
behind decisions inspectable. Start with accounting and replay integrity, then
use reliable records to evaluate reasoning and gameplay changes. Public results
and highlights should describe the same recording they display.

New work follows [the rolling workflow](../docs/workflow.md). Each card under
`work/` owns its status, acceptance criteria, and results; dispatch it by path.
The [cleanup roadmap](cleanup-roadmap.md) preserves all 49 priorities, grouped
by outcome and including the experiments that need a measured disposition.
The existing repairs are already included in `codex/cleanup`; their PRs are
review records and remain unmerged into `main`. The cards are:

| Card | Purpose | Review record |
| --- | --- | --- |
| [Workflow pilot](work/workflow-pilot.md) | Introduce the prospective card format while preserving historical checks. | `ccf42166`, [PR 431](https://github.com/dkdan10/AiLibi/pull/431) |
| [Budget accounting](work/budget-accounting.md) | Account for provider usage when a consumed response fails validation. | `b64e29b5`, [PR 431](https://github.com/dkdan10/AiLibi/pull/431) |
| [Aborted meeting calls](work/aborted-meeting-calls.md) | Retain completed responses and reported failed-attempt usage when a meeting aborts. | `26386914`, [PR 432](https://github.com/dkdan10/AiLibi/pull/432) |
| [Replay integrity](work/replay-integrity.md) | Bind spectator timelines and terminal claims to reconstructed engine state. | `55ed6d9a`, [PR 433](https://github.com/dkdan10/AiLibi/pull/433) |
| [Recording replacement](work/recording-replacement.md) | Replace a replay and its observation audit as one recording lifecycle. | `62ba0162`, [PR 434](https://github.com/dkdan10/AiLibi/pull/434) |
| [Cleanup delivery](work/cleanup-delivery.md) | Keep implementation on the working branch until the owner's final review and merge. | Commit history for the card |

The [review ledger](review-ledger.md) separates implementation commits, verified
checks, independent review, and the owner's pending final review and merge.

The first parallel implementation batch completed three recording-integrity
repairs. Each passed independent implementation review and the combined project
gate; their cards hold the evidence and remaining limitations. Milestone 1
continues with the next candidates below.

| Card | File ownership | Commit | Independent reviewer |
| --- | --- | --- | --- |
| [Report destinations](work/report-destinations.md) | Tournament CLI and destination helper/tests | `27885b10` | Portfolio-review agent |
| [Completed meeting attempts](work/completed-meeting-attempts.md) | Orchestrator call recording and manifest provenance/tests | `9bfe86d0` | Workflow-redesign agent |
| [Evaluation replay integrity](work/evaluation-replay-integrity.md) | Evaluation walker, report loaders, and their consumers/tests | `bf2689f9` | Code-review agent |

One agent writes each file at a time. The coordinating agent owns this index,
integrates review fixes, runs the shared full gate, and commits each task
separately. Investigation and test design may proceed in parallel; shared-file
changes are scheduled explicitly. Each card's Results records verification and
remaining limitations for the owner's final review.

The second batch completed completion/accounting status, tournament continuation
and cumulative limits, public provenance, dependency fixes, map validation, and
stronger audit checks. Their commits, independent reviews, and combined
6,409-Python / 455-frontend / 100-recording verification are in the ledger.

The third batch completed temporal observation implementation, exact citation
navigation, compact public results, lean replay delivery and measured performance.
Its 6,599-Python / 467-frontend / 100-recording verification and review are in the
ledger. The temporal behavior remains OFF; adoption is a separate decision.

The next parallel batch has one writer per shared surface:

| Card | Writer | Coordination |
| --- | --- | --- |
| [Reasoning evidence experiments](work/reasoning-evidence-experiments.md) | Workflow-redesign agent | Meetings, memory, strategic rendering and scorecard; shared registry wiring by provenance owner |
| [Tactical gameplay experiments](work/tactical-gameplay-experiments.md) | Code-review agent | Tactical policy experiments, engine reset comparison and measurements; shared orchestration edits by handover |
| [Model evidence provenance](work/model-evidence-provenance.md) | Portfolio-review agent | Training identity and recorded-substrate bindings; first writer of shared game/replay/readers |
| [Carried audit dispositions](work/carried-audit-dispositions.md) | Coordinator | Semantic gates, current findings ledger, lessons and source prose after handover |

The owner authorized continued implementation through the cleanup roadmap.
The active queue is
[reasoning evidence experiments](work/reasoning-evidence-experiments.md),
[tactical gameplay experiments](work/tactical-gameplay-experiments.md), and
[model evidence provenance](work/model-evidence-provenance.md). Dispatch after
shared surfaces are assigned; the preceding combined gate is recorded. Each
experiment retains its own measured disposition.
Write the next compact card when its evidence, dependencies, and scope are
understood. Experimental adoption and live-provider budgets remain explicit
separate decisions. Schedule shared-file ownership manually; the existing
`compute_next_task.py` tool continues to serve phase contracts only.

Historical `phase-*.md` files and their generated `agent_prompts/` exports remain
unchanged by this workflow. Their validators continue to run. Read them for the
contract and provenance of earlier work, or when explicitly resuming that work.
