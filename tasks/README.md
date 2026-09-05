# Current work

The next release should make simulation records accurate and the evidence
behind decisions inspectable. Start with accounting and replay integrity, then
use reliable records to evaluate reasoning and gameplay changes. Public results
and highlights should describe the same recording they display.

New work follows [the rolling workflow](../docs/workflow.md). Each card under
`work/` owns its status, acceptance criteria, and results; dispatch it by path.
The initial cards are:

| Card | Purpose |
| --- | --- |
| [Workflow pilot](work/workflow-pilot.md) | Introduce the prospective card format while preserving historical checks. |
| [Budget accounting](work/budget-accounting.md) | Account for provider usage when a consumed response fails validation. |
| [Aborted meeting calls](work/aborted-meeting-calls.md) | Retain completed responses and reported failed-attempt usage when a meeting aborts. |

Select the next card after the active repair's verification and review,
using these candidates:

- Validate replay chronology and terminal metadata against reconstructed state.
- Keep replay replacement and its observation audit consistent.
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
