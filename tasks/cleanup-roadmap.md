# Cleanup roadmap

Implement on `codex/cleanup`. The owner will arrange Claude's review of the
completed work by commit or PR, then the final merge into `main`. Preserve
published task commits and keep main unchanged until that review and decision.

This is the prioritized backlog from the 2026-09-05 review and owner discussion,
not a set of detailed implementation contracts. Each item receives one canonical
card when ready; that card owns acceptance, status, decisions, and results.
The item numbers preserve the conversation's priority list. Milestones group
outcomes, and independent work may proceed in parallel where prerequisites and
file ownership permit. No live-provider budget or experimental adoption is
implied by this roadmap.

## Existing foundation

The task index links the inherited workflow, budget, aborted-call, replay, and
recording-replacement cards to their original commits and PRs. The cleanup
delivery card records direct branch commits, final owner review, and CI on
cleanup pushes. These are implemented on this branch, not merged into main.

## Milestone 1: accurate recording and reporting

Exit: provider attempts reconcile, reports cannot destroy their evidence,
outcomes are verified, and incomplete runs have honest status and provenance.

| Item | Outcome / acceptance direction | Card |
| --- | --- | --- |
| 1 | Report destinations cannot alias any selected replay or audit; reject before provider work and publish reports atomically. | [Report destinations](work/report-destinations.md) |
| 2 | Distinct paid failures in completed meetings are retained exactly once; all accounting consumers reconcile. | [Completed meeting attempts](work/completed-meeting-attempts.md) |
| 3 | Current evaluation reports reject the same chronology and outcome corruption as strict playback. | [Evaluation replay integrity](work/evaluation-replay-integrity.md) |
| 4 | Spending remains visible while verified outcomes, unverified claims, and partial artifacts are distinguished. | [Completion status](work/report-completion-status.md) |
| 5 | Aborted, unfinished, and tick-limited games have distinct completion states and correct denominators. | [Completion status](work/report-completion-status.md) |
| 6 | Interrupted tournaments retain inspectable progress, bind reports to their recording inputs, and support safe continuation. | [Tournament lifecycle](work/tournament-lifecycle.md) |
| 7 | Whole-run token, cost, and wall limits are explicit and enforced through retries and cancellation. | [Tournament lifecycle](work/tournament-lifecycle.md) |

## Milestone 2: accurate public facts and reproduction

Exit: published facts and media identify their recordings; documented setup is
executable with stated prerequisites. Presentation work can run alongside the
recording repairs when it does not depend on a changed report contract.

Cards: [public provenance and reproduction](work/public-recording-provenance.md)
(8–10), [dependency advisories](work/dependency-advisories.md) (11).

| Item | Outcome / acceptance direction |
| --- | --- |
| 8 | Recompute or suppress stale highlights; corrupting a source fingerprint prevents obsolete enrichment from publishing. |
| 9 | Refresh media or label it historical, with verified recording provenance and captions. |
| 10 | Execute and correct the clean-clone journey; distinguish installation, offline verification, and current recording replacement behavior. |
| 11 | Recheck dependency advisories, assess actual use, and deliberately update affected packages with build/browser verification. |

## Milestone 3: evidence and meeting decisions

Exit: agents receive entitled, temporally coherent evidence; basic false claims
can be contested; adoption decisions use independent measurements. Inspect the
three existing unadopted reasoning candidates before adding overlapping work.

Card: [temporal observations](work/temporal-observation-contract.md) (12–13).
The following seven items use [reasoning evidence experiments](work/reasoning-evidence-experiments.md).

| Item | Outcome / acceptance direction |
| --- | --- |
| 12 | Define death/discovery/public-knowledge semantics and remove secret death-time encoding from agent-visible IDs if exact time is hidden. |
| 13 | Audit movement witness snapshots, same-tick delivery, and entitlement/traceability across every observation channel, including audible events. |
| 14 | Establish a scorecard, development cases, held-out inputs, and decision rules; separate direct role proof from other reasoning. |
| 15 | Give reporter reasoning, corroboration discipline, and testimony shapes an explicit next evaluation, revision, or retirement decision; retain the original FINDING verdict. |
| 16 | Render known death bounds distinctly from discovery; movement after public knowledge of death cannot establish murder opportunity. |
| 17 | Provide usable map-grounded counterevidence to false impossible-travel claims, with legal and impossible controls. |
| 18 | Experiment with bounded replies to consequential new allegations; measure correction, wrongful ejections, repetition, calls, and latency. |
| 19 | Preserve independent observation versus hearsay/repetition; agreement does not manufacture another witness. |
| 20 | Audit memory transformations, movement claims, coalesced citations, lost evidence, and later summaries of system-rewritten votes. |

## Milestone 4: purposeful tactical play

Exit: selected changes improve measured play on held-out cases without erasing
meaningful uncertainty or producing a new stagnant equilibrium. Compare each
candidate separately before testing interacting combinations.

Card: [tactical gameplay experiments](work/tactical-gameplay-experiments.md)
(21–25, with the separately measured 43–46 comparisons).

| Item | Outcome / acceptance direction |
| --- | --- |
| 21 | Compare deterministic workload-aware task redistribution with current seat preference. |
| 22 | Compare bounded patrol, accompaniment, or investigation with finished-crew waiting. |
| 23 | Evaluate vent-exit witness risk using only information available to the impostor. |
| 24 | Reduce purposeless short oscillations while preserving legitimate reversals and escape. |
| 25 | Test small tactical consequences of meetings that produce useful new information. |

## Milestone 5: an inspectable portfolio experience

Exit: a visitor understands the project and can follow a claim through its
evidence, decision, outcome, and limitations using the published recordings.

Card: [portfolio evidence experience](work/portfolio-evidence-experience.md) (26–31).

| Item | Outcome / acceptance direction |
| --- | --- |
| 26 | Make citations navigate to the observation/statement, relevant scene, and agent knowledge; disclose missing references. |
| 27 | Provide compact static tournament results with defined metrics, denominators, provenance, and evidence links. |
| 28 | Explain author, purpose, recorded games, source, and basic rules within the standalone demo. |
| 29 | Curate a justified deduction, unsupported persuasive accusation, and appropriately unresolved case. |
| 30 | Shorten the README and add a substantive ownership decision case study while preserving authorship disclosure. |
| 31 | Verify complete browser and clean-clone journeys; distinguish watching, mechanics verification, and live generation. |

## Milestone 6: maintainability and measured performance

Exit: expensive data boundaries are measured, narrow extractions preserve
behavior, and provenance/architectural gates reject the defects they claim to
prevent. Current performance is not a mandate for a wholesale rewrite.

| Item | Outcome / acceptance direction |
| --- | --- |
| 32 | Fetch model-call bodies on demand in API and static modes; reduce actual transferred replay bytes. |
| 33 | Measure cold/warm latency, payload, belief work, peak memory, and concurrent cache misses before selecting optimizations. |
| 34 | Reject unsupported map traversal durations or implement them consistently before expanding maps. |
| 35 | Extract coherent meeting/replay/evidence responsibilities after characterization and intended import-boundary checks. |
| 36 | Close current evaluation/ML corpus, roster, derivation, and substrate provenance gaps before another campaign. |
| 37 | Retire dead protocol paths and experimental mechanisms across all coupled consumers with explicit version handling. |
| 38 | Reproduce and disposition all carried audit findings, including semantic gates, claim checking, stale prose, and incomplete routing maps. |

Historical inputs: [phase close](../audits/audit-phase-21-close.md) and
[hardening audit](../audits/audit-phase-21-hardening.md). An old finding is not
automatically a current defect. Preserve fixed, refuted, and intentional cases
as such rather than generating new tasks from their titles alone.

Cards: [replay loading performance](work/replay-loading-performance.md) (32–33),
[map traversal contract](work/map-traversal-contract.md) (34),
[audit fact gates](work/audit-fact-gates.md) (part of 38; remaining carried
findings still require a disposition), and
[carried audit dispositions](work/carried-audit-dispositions.md) (remaining 38).
Current model/evaluation identity repairs and the next ML decision use
[model evidence provenance](work/model-evidence-provenance.md) (36, 48).

## Milestone 7: lightweight iteration

Run these improvements alongside the implementation rather than waiting for
every product task. Exit: task evidence and final review are easy to navigate,
without another generated-plan or scheduling system.

Card: [cleanup iteration](work/cleanup-iteration.md) (39–42).

| Item | Outcome / acceptance direction |
| --- | --- |
| 39 | Evaluate the card pilot using owner interventions, scope changes, verification effort, and independently found defects. |
| 40 | Keep universal rules concise and move detailed procedures to linked documents; preserve historical contracts. |
| 41 | Maintain a small ready queue, clear file ownership, and separate implemented, verified, reviewed, merged, and adopted states. |
| 42 | Keep gameplay-first and code-first findings independent before synthesis; each experiment has a budget and explicit decision/retirement rule. |

## Milestone 8: separately decided experiments and expansion

These items require measured or owner-decided dispositions; completion does not
mean enabling every proposed variant. Correct evidence use precedes balance
changes, and a live evaluation needs its own explicit budget.

| Item | Outcome / acceptance direction |
| --- | --- |
| 43 | Measure seat/action-order effects with identity permutations before evaluating alternative priorities. |
| 44 | Compare a coherent meeting-reset policy covering positions, vents, cooldowns, grace, and remaining corpses. |
| 45 | Investigate self-reporting and structural role tells, reusing existing roll-call studies. |
| 46 | Establish why sabotage and task victories contribute little in some configurations, then test one mechanism at a time. |
| 47 | Revisit vote-rule changes only after reasoning improvements; preserve the earlier tally study's tradeoffs and parked verdict. |
| 48 | Decide whether one current ML comparison serves the portfolio or close the remaining claims as historical; do not repeat completed refits without a trigger. |
| 49 | Add maps, providers, or live deployment only when an explicit need justifies their operational and verification cost. |

Reported-body cleanup and duplicate successful reports are not current repair
items. Other corpses persisting and positions remaining unchanged are existing
rules whose consequences require explicit evaluation.
