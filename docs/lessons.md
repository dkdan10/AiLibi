# How this was built

Part 1 is what I learned directing the build. Part 2 traces one decision from
its evidence to what later evidence limits.

## What I learned

I directed AiLibi's initial build from May through August 2026 without writing
production code by hand. Coding agents implemented the system and a second model
reviewed it; the August review used independent gameplay, code, and portfolio
tracks. September's cleanup adds Codex implementation and agent-drafted task
cards under my direction. The distinction matters: directing and reviewing work
is an ownership claim, not a claim to have personally written every artifact.

### Directing coding agents at scale

The original phase workflow used written contracts with separate branches,
explicit scope, and executable acceptance criteria. Generated prompts and
fresh checkouts supported that build. The [cleanup workflow](workflow.md) now
uses one canonical card per change, explicit shared-file ownership, independent
review, and focused commits on a short-lived branch merged by pull request.
Historical contracts stay as records; new work does not need a second
generated copy of its instructions.

Three habits did more for throughput than any amount of prompt wording. The first is
re-anchoring. A contract written weeks earlier cites files and line numbers that have since
moved, and a competent agent follows a stale pointer to the wrong place — so before
dispatching I re-read every anchor and commit the corrections as their own change. The second
is refusing outside patches: this repository
[takes issues, not pull requests](../CONTRIBUTING.md), to keep project direction, agent contributions,
and acceptance evidence attributable. A contract may be agent-drafted; the
important ownership decision is what work to authorize and accept. The third is contracting for both answers before a measurement
runs, so a rule that says no is prose, not a redesign.

### The code was right and the game was wrong

The most useful sentence to come out of the review is that its two technical tracks disagreed
about severity and both were correct. The code track found no top-severity defect in a
hundred and thirty findings; the gameplay track found eight. They used different definitions:
for one, a severe defect is a correctness, security or data-loss hazard; for the other,
anything that stops the core loop being believable. Nearly every gameplay defect was a
faithful implementation of a rule nobody would have written after watching it run. That
is why a green build and a broken game are not a contradiction: the test suite defends
correctness against a specification, and nobody has tested the specification.

### What the gates could catch, and what they structurally could not

On the day [the reviewer](../process/audits/review-2026-08-19/B/repo-health-architecture.md) measured
it — 2026-08-18 — the default gate ran 4,621 tests and four import contracts, all green.
On the same corpus, a fifth of what crewmates said about their own movements did not match
where they had been. Three findings explain how both are true, and not one of them is a
missing test.

- **An invariant that stopped being true.** A comment in the memory layer justified an
  inference on the rule that an agent's own job list only ever shrinks. A map setting flipped
  two phases later so that a dead player's unfinished jobs are handed to the living, and from
  then on the list could grow. Nothing failed, because the code still did exactly what its
  comment said — the comment had stopped describing the world. Agents began remembering work
  they had never touched, and citing it as evidence. Fixed since: a completion memory is now
  minted from the engine's own completion event, not inferred from a changed pending
  identifier.
- **A gate that checked shape instead of entitlement.** The leak scanner — the one the design
  calls the most important test in the repository — validated the structure and the strings of
  an agent's observation packet, never whether the agent was *entitled* to what the packet
  contained. A deliberately planted mutation that made every undiscovered body visible to
  everyone survived all four suites. Fixed since: the scanner recomputes visibility
  independently and compares it against what was handed out.
- **Contracts that covered a quarter of the tree.** The import contracts that enforce the rule
  at the centre of this project — agents may not import the engine — covered
  [89 of 383 Python files](../process/audits/review-2026-08-19/B/collated-findings.md) when the review
  measured them. A file placed inside the agent package that imported
  the orchestrator, which imports the engine, passed all four. Fixed since: the contracts now
  run over every top-level package, and the test that plants a forbidden import plants it in a
  temporary tree instead of the live one.

The counterweight belongs in the same breath, because the lesson is not that tests are useless.
One test re-runs the real meeting machinery over two hundred committed meetings, compares the
bytes, and ships a deliberately corrupted copy whose only job is to prove the comparison can
fail; and [the reviewer](../process/audits/review-2026-08-19/B/repo-health-architecture.md)
followed every audit and contract path cited from the code and found 43 of 44 still resolve on
disk. A gate only sees the axis it was pointed at. The fix is another axis.

### Documentation drift is a defect, not untidiness

I found sentences on the front page describing behaviour the repository had stopped having;
they had been true when written. Prose rots silently because nothing runs it. So the
results page the front door links has a check in the same gate as the tests: outcomes are recomputed from the
recording manifests, results are re-derived from the instruments rather than from a
second copy of themselves, and every relative link is resolved. The narrower checks that
once policed ageing dates and private vocabulary were retired on 2026-10-13: they held
pages in place for their own sake, not for a figure's. Treating a stale claim as a failing
test — not as a chore — is the only version of this I have seen survive a moving codebase.

### Writing the bar down before the measurement

Before the recording my repairs would be judged on, I wrote down what it would have to show
and what a miss would mean, and merged that document before generating a byte. It then missed
two bars: convictions reached without engine-certified proof came up short by less than a
single wrongful ejection, and wrongful ejections came in over the ceiling I had set. Under the
rule as written that is a finding, not an adoption. I recorded the miss, put it on the front
page, and adopted the recording anyway — by an explicit override carrying my name and date,
stated as an override rather than a pass ([traced below](#one-decision-traced)). Two earlier phases of learned-policy search made a different adoption decision: policies that won more games all failed an evidence bar written down *before*
the measurement, and both closed having adopted nothing. The discipline is worth nothing
unless the bar can say no, and the only proof that it can is a published miss.

The [next reasoning experiment](../process/audits/audit-phase-21-adopting-record.md)
also returned FINDING, and this time there was no override. Three of four
pre-registered checks passed; the reporter's share of innocent ejections missed.
The default recording stayed unchanged and the candidate changes stayed off.
A decrease in total errors did not excuse the remaining concentration of harm.
The published miss and the decision to retain the default are both part of the
result; implementing a candidate was not enough to adopt it.

### The critique I am keeping

The sharpest thing anyone said about this project is not a defect report. The review's
[research-lead read](../process/audits/review-2026-08-19/C/p2-ml-research-lead.md) closed with:
*"strong on measurement, weak on knowing when to stop building measurement."* Nobody rebutted
it, and [the code track](../process/audits/review-2026-08-19/B/repo-health-architecture.md) then handed
over the measurement that makes it concrete: **95,824 lines of process narration** — contracts,
generated prompts, audits — against **57,776 lines of core product Python**, a ratio of 1.66
to 1, against **3,358 lines of durable engineering documentation**.

Some extra process is necessary when agents execute the implementation: a reader
needs to know what they were asked to do and how it was checked. The smaller
investment in durable documentation is harder to defend. Adding another
instrument does not answer a criticism about too many instruments. The cleanup
therefore keeps the historical evidence but shortens the active instructions,
uses one task card, and puts the visitor's questions before the build history.
Whether that helps should be judged by the resulting experience and the defects
independent review still finds, not by another count of documents produced.

**The review that found most of this is published**, curated and indexed, each finding linked to
the change that closed it or the record of why it did not, and titled by the four of its own
headline claims it disproved:
[the 2026-08-19 three-track review](../process/audits/review-2026-08-19/README.md).

## One decision, traced

Daniel Keinan directed AiLibi; Claude Code and Codex agents implemented and
reviewed it. This case study was drafted by Codex from the preserved decision
records. It describes an owner ruling, not hand-written implementation or an
independent human audit.

### The problem and the options

The crew could treat contradictory speech as proof and convict innocent players.
The evidence repairs changed what meetings were allowed to claim: source-bound
observations, distinct categories for direct role evidence and weaker conflicts,
and clearer limits on fabricated statements. The proposed replacement recording
needed to show that these repairs improved decisions, not merely that tests passed.

The owner had two consequential options after the measurement: retain the prior
reference under the written decision rule, or explicitly adopt the repaired
system despite a failed rule. The [record's decision section](../process/audits/audit-phase-20-baseline-7.md#6-the-verdict)
ruled out selectively adopting convenient pieces. The experiment therefore did
not authorize an informal partial pass.

### What the evidence said

The [pre-registered measurement](../process/audits/audit-phase-20-baseline-7.md#3-the-pre-registered-read-bar-by-bar)
missed two central criteria. Conviction accuracy without direct role proof was
61/103 = 0.5922 against at least 0.60. Innocent ejections fell from 79 to 42,
but the criterion required fewer than 35. A one-ejection gap to the first bar
was still a miss; rounding it into a pass would change the decision rule after
seeing the result.

Other evidence favored the repairs. Fabricated completion lines disappeared,
false self-placement fell from 20.1% to 0.77%, and four inspected injustice
fixtures changed outcome. Some problematic event classes disappeared, leaving
metrics vacuous rather than proving each detector worked correctly. These were
observations about the recorded sample, not a controlled attribution of every
improvement to an individual repair.

### The owner judgment

On 2026-08-26, Daniel explicitly adopted the replacement as the reference while
leaving the experiment's verdict **FINDING**. The [owner ruling](../process/audits/audit-phase-20-baseline-7.md#61-the-owners-adoption-ruling-2026-08-26),
recorded on [PR #389](https://github.com/dkdan10/AiLibi/pull/389), cited the narrow
accuracy miss, the reduction in innocent convictions, reduced fabrication, and
the qualitative changes in the inspected meetings.

That traded adherence to the original adoption rule for the owner's judgment
that this was the more useful reference for subsequent work. It did not make
an experiment pass, establish general deduction, or demonstrate that the new
reference would generalize. A reviewer can disagree with the override while
still checking what was measured and who accepted the tradeoff. That separation
is the central ownership claim here.

### Implementation and review evidence

The [execution record](../process/audits/audit-phase-20-baseline-7.md#62-what-the-ruling-executed-in-this-pr)
lists what adoption actually changed: the reference, graduated behavior, and
associated provenance. Agents implemented those changes and wrote substantial
parts of the supporting material. The [close audit](../process/audits/audit-phase-20-close.md)
and later [maintenance recording](../process/audits/audit-phase-21-rerecord.md) remain
available to assess the implementation and its subsequent defects. The review
process used separate AI reviewers; it is not evidence of external human assurance.

The historical example below makes the original phases' contract-to-implementation
path inspectable; it does not claim that Daniel personally authored every source
contract or generated file.

<!-- EXHIBIT: the excerpt below is copied verbatim from its source; no test checks it since 2026-10-13. -->

**1 — the historical contract**, from [`tasks/phase-19.md`](../process/tasks/phase-19.md). Two runs of it, verbatim:

```markdown
### Task 19.2 — The in-code truth sweep: docstrings match the bytes
**Branch:** `phase-19-in-code-truth`
**Depends on:** none (root)
…  the section-reference line — a paragraph of anchors into the code — elided here
**Files in scope:**
- agents/memory/beliefs.py; (docstring/comment lines only)
- meetings/transcript.py; (same)
- meetings/manager.py; (same)
- orchestrator/game.py; (the :12-13 module-docstring claim only)

**Files NOT in scope:**
- agents/memory/store.py (the live path is evidence, not an edit target)
- meetings/constants.py; (the resolver homes already state "now always True")
- any resolver body or lever mechanism (behavior untouched)

**Definition of done:**
…  and the checklist, ending in: bash scripts/check.sh passes locally
```

**2 — the prompt generated from it**, which copied the contract verbatim; the generated prompts were deleted on 2026-10-13, and [this one can still be read at its last commit](https://github.com/dkdan10/AiLibi/blob/4a7bd9c04e81df696098d6229737e86761d45e43/agent_prompts/task-19-2-in-code-truth.md).

**3 — the pull request it produced**: [#328](https://github.com/dkdan10/AiLibi/pull/328), reviewed and merged; on `main` it is the squash commit whose subject ends `(#328)`.
<!-- EXHIBIT-END -->

### What later evidence limits

The maintenance recording measured proof-free accuracy at 50/96 = 0.5208 and
46 innocent ejections across four recorded sets. It registered no fresh adoption
bars and does not retroactively validate the override. In that recording's
9-player set, 68 of 82 correct ejections involved direct vent evidence; without
it, only 14 of 27 ejections targeted impostors. [The reading guide](reading-guide.md)
separates those denominators and explains why general social deduction remains
unproven.

[The next reasoning experiment](#writing-the-bar-down-before-the-measurement)
adopted nothing after missing a bar, and the [learned-policy program](ml-program.md)
adopted no default replacement after its candidates missed pre-registered
evidence-quality gates. Those decisions must not be conflated with the earlier
override.

The portfolio evidence is the ability to frame a question, preserve an unfavorable
measurement, make a named judgment, and leave enough implementation and review
material to challenge it. It is not an assertion that the judgment was inevitable
or that AI-written tests establish the right game design. Open the
[published results](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament)
to inspect the figures behind these judgments, set by set.

### A later ruling: keep the comparison records

**The problem and the options.** Each candidate round's committed copy is the
comparison record that isolates one change to the 9-player game: round 1's the
kill cooldown, round 2's the route field. The question was whether to delete
each superseded round's candidate recordings once a newer one lands, or keep
them. The [decision memo](../process/tasks/decision-2026-09-24-stage-b-wave.md) had
proposed deleting them: the card that lands round r+1 would remove round r's
directory, its audit citing the commit that held the bytes.

**What the evidence said.** Asked on 2026-10-09 whether a retirement list that
included round 1's directory should go ahead, the orchestrator advised keeping
that directory: each candidate copy is the comparison record for one change,
and reproducing a claim from committed evidence is worth more than a tidier
tree.

**The owner judgment.** The owner ruled, verbatim: "Keep the comparison
records". The earlier proposal was declined: round 1's recordings stay, and a
promotion of round 3 keeps round 2's bytes as their own candidate round.

**Implementation and review evidence.** Round 3's
[promotion](../process/tasks/work/promote-round-3.md) moved round 2's 54 files to
`replays/candidates/stage-b-r2` with none differing, by the per-file sha256
table in [the round-3 record](../process/audits/audit-2026-10-09-stage-b-r3.md). Its
tests read rounds 1 and 2 and fail on one changed byte of the moved config, a
declaration naming the wrong seeds, or a stray file in round 2's directory.

**What these records do not claim.** Keeping a round adopts nothing: the route
field round 3 carries stays a recorded setting, not an adopted one, and a kept
round is not the shown set. The ruling decides what stays in the tree, not what
any round shows about play.
