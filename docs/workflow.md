# Iterating on AiLibi

Choose the next change from evidence, verify it, and use the result to choose
what follows. [AGENTS.md](../AGENTS.md) carries the standing rules and
[architecture.md](architecture.md) defines the system boundaries. The
[task index](../tasks/README.md) describes the current outcome and candidate
work; only work ready to start receives a detailed card.

## Cleanup delivery

`codex/cleanup` is the working branch for the cleanup backlog. Implement tasks
there and push verified, focused commits. Keep the original commits from the
existing repair PRs; their links remain useful review records.
The existing CI workflow also runs on pushes to this branch.

The owner will have Claude review the completed cleanup by commit or PR before
the final merge into `main`. There are no intermediate releases into `main`
during this work. Completion of a card means implemented and verified on the
cleanup branch, still awaiting that final review and merge.

A per-task PR is optional for this cleanup. When delivering by commit, the
card's Results carries the validation evidence, referenced contract/architecture
sections, material decisions, and limitations that would otherwise go in the PR.
Include the card path in the commit body so a reviewer can locate the contract
from the commit and locate its implementation with `git log -- <card-path>`.
Preserve task boundaries and published history; do not squash unrelated tasks
or amend published task commits while the cleanup is accumulating.

## One card per change

New tasks live at `tasks/work/<slug>.md`. That file is the canonical contract;
dispatch it by path instead of copying it into a generated prompt or issue.
Link longer evidence or design discussions rather than repeating them.

Use one `#` title, a `**Status:**` of `ready`, `active`, or `done`, and these
sections:

| Section | Content |
| --- | --- |
| Outcome | The observable problem to resolve and resulting behavior. |
| Evidence | A reproducible case and relevant source or decision links. |
| Acceptance | Checkboxes describing success and a meaningful adverse case. |
| Constraints | Non-goals, protected decisions, prerequisites, and any authorized run budget. |
| Expected scope | Likely files and the boundaries of permitted follow-through. |
| Record impact | Effects on future behavior, recorded bytes, compatibility, and evaluation. |
| Validation | Commands that establish acceptance, including the full project check. |

A completed card also has `## Results`, with verification evidence and any
material limitations. Keep cards concise; implementation detail belongs in the
code and durable decisions belong in the appropriate architecture or decision
document.

## Discover, implement, verify

1. **Ready:** the outcome is understood, prerequisites are available, and the
   owner has authorized the scope. Reproduce the failure, inspect current
   consumers, and choose an implementation before editing. Update the card if
   discovery changes the expected files; ask for an unresolved protected
   decision before dependent work.
2. **Active:** implement one coherent change with relevant tests. Directly
   necessary call-site, test, generated-output, and documentation updates are
   permitted within the card's boundaries. Record material follow-through in
   the PR or cleanup card's Results. Unrelated cleanup, new behavior,
   compatibility changes, dependencies, and spending require authorization if
   the card or owner has not provided it.
3. **Done:** acceptance is demonstrated, the required checks pass, and Results
   records the evidence. This means locally verified and ready for review; it
   does not mean merged, deployed, or adopted as an experimental baseline.

Run targeted checks while developing, then `bash scripts/check.sh` for final
verification. A new invariant gate needs a planted or perturbed failure proving
that it detects the claimed defect. Do not check an acceptance item merely
because its implementation exists. Reopen a done card as active if verification
or review reveals unfinished work.

## Coordinate and review

Keep the next few candidates in the task index and schedule them manually.
Declare semantic prerequisites in Constraints. Shared-file ownership is a
scheduling concern: assign one writer per file at a time, with isolated
worktrees where useful for independent investigation and review; cleanup
implementation stays on `codex/cleanup`. Independent investigation, test design,
and review can run alongside implementation. `scripts/compute_next_task.py` remains the
historical phase scheduler; it does not dispatch these cards.

A reviewer should attempt the adverse case and inspect relevant failure paths,
not just repeat the implementer's summary. For gameplay experiments and release
reviews, form gameplay-first and code-first findings independently, then
synthesize them. Preserve the distinction between engine truth, agent-visible
information, and model inference. Human decisions about game rules and
experimental adoption remain explicit.

## Records and experiments

Every card declares record impact, including a repair that changes future
failure handling without changing committed recordings. Preserve existing
reproducibility and historical-validation requirements. Use the existing replay
stamps, manifests, and experiment switches; a new task format changes none of
their guarantees.

For a behavior experiment, specify the hypothesis, inputs, comparison,
measurement, and decision rule before the evaluation that decides adoption.
Development cases can inform that rule; they are not independent confirmation.
Inspect existing candidate implementations and prior findings before creating
another variant. A later experiment never changes an earlier verdict.

A live-provider run needs an authorized provider and explicit token, wall-time,
and cost limits, including a cost statement for flat-rate service. Ordinary
implementation and CI use the fake provider. Each experiment needs a decision
point and a retirement condition. Adoption deletes the switch as required by
AGENTS; rejection deletes the candidate unless an explicitly authorized
comparison still needs it. Keep the recorded evidence and its provenance.

## Historical work and the pilot

Phase contracts, their generated prompts, and past audits remain historical
records. Existing phase validators and prompt synchronization checks continue
to run; the card check adds validation for new work. Do not rewrite old plans
to make them look like this workflow. An explicitly resumed phase task retains
its original contract and exact file scope.

Start with the workflow pilot and budget-accounting repair linked from the task
index. Evaluate the pilot after a few completed repairs using owner
interventions, scope amendments, verification effort, and defects found in
review. Adjust the process from those results before adding more tooling.
