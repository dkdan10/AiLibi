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

Select the next card after the active repair's local verification and independent
implementation review. Claude's owner-arranged review follows the completed
cleanup, not each card. The next candidates are:

- Separate reported spending from verified outcome claims.
- Distinguish aborted, unfinished, and tick-limited runs.
- Bind tournament progress and reports to their actual recording inputs.
- Enforce whole-run token, cost, and wall-time limits.
- Reconcile displayed highlights and results with their recording provenance.
- Evaluate death-time reasoning and response opportunities against existing
  experiments before adding new gameplay variants.

The list expresses direction, not an approved implementation plan or a live-run
budget. Write the next compact card when its evidence, dependencies, and scope
are understood. Schedule shared-file ownership manually; the existing
`compute_next_task.py` tool continues to serve phase contracts only.

Historical `phase-*.md` files and their generated `agent_prompts/` exports remain
unchanged by this workflow. Their validators continue to run. Read them for the
contract and provenance of earlier work, or when explicitly resuming that work.
