<!-- OWNER: confirm wording — first person, the author's own account; every figure is quoted from a committed source. -->
# What I learned

I built AiLibi between May and August 2026 without writing production code by hand. I wrote
the task contracts and the standing rules; coding agents wrote the code; a second model
reviewed it and, in August, audited the whole thing in three blind tracks. Here is what that
taught me, including the parts that do not flatter the method.
<!-- OWNER: end. -->

## Directing coding agents at scale

The unit of work is a written contract, not a conversation. Each one names a branch, its
dependencies, the files in scope, the files explicitly *out* of scope, and a definition of
done that ends in a command anyone can run. A generator turns that contract into the agent's
prompt by copying it in verbatim, and a check in the gate fails the moment the two disagree —
so the prompt an agent works from cannot quietly become a different task than the one I
reviewed. Each agent runs in a fresh checkout of its own, which is what makes a dozen of them
safe to run at the same time.

Two habits did more for throughput than any amount of prompt wording. The first is
re-anchoring. A contract written weeks earlier cites files and line numbers that have since
moved, and a competent agent follows a stale pointer confidently to the wrong place — so
before dispatching I re-read every anchor against the current code and commit the corrections
as their own change. The second is refusing outside patches: this repository
[takes issues, not pull requests](../CONTRIBUTING.md), because the claim it makes is that
every line arrived through a contract I wrote and a gate I can re-run, and a merged drive-by
would make that claim false.

## The code was right and the game was wrong

The most useful sentence to come out of the review is that its two technical tracks disagreed
about severity and both were correct. The code track found no top-severity defect in a
hundred and thirty findings; the gameplay track found eight. They were using different
definitions: for one, a severe defect is a correctness, security or data-loss hazard; for the
other, it is anything that stops the core loop being believable. Nearly every gameplay defect
was a faithful implementation of a rule nobody would have written after watching it run. That
is why a green build and a broken game are not a contradiction: the test suite defends
correctness against a specification, and nobody has tested the specification.

## What the gates could catch, and what they structurally could not

On the day [the reviewer](../audits/review-2026-08-19/B/repo-health-architecture.md) measured
it — 2026-08-18 — the default gate ran 4,621 tests and four import contracts, and it was green.
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
  [89 of 383 Python files](../audits/review-2026-08-19/B/collated-findings.md) when the review
  measured them. A file placed inside the agent package that imported
  the orchestrator, which imports the engine, passed all four. Fixed since: the contracts now
  run over every top-level package, and the test that plants a forbidden import plants it in a
  temporary tree instead of the live one.

The counterweight belongs in the same breath, because the lesson is not that tests are useless.
One test re-runs the real meeting machinery over two hundred committed meetings, compares what
comes out byte for byte, and ships a deliberately corrupted copy alongside it whose only job is
to prove that the comparison can fail; and [the reviewer](../audits/review-2026-08-19/B/repo-health-architecture.md)
followed every audit and contract path cited from the code and found 43 of 44 still resolve on
disk. A gate only sees the axis it was pointed at. The fix is another axis.

## Documentation drift is a defect, not untidiness

I found sentences on the front page describing behaviour the repository had stopped having,
and they had been true when they were written. Prose rots silently because nothing runs it. So
the front door now has a check in the same gate as the tests: outcomes are recomputed from the
recording manifests, the results table is re-derived from the instruments rather than compared
against a second copy of itself, every relative link is resolved, every count that ages
without an edit carries the date it was taken, and any private vocabulary either does not
appear or links a glossary entry that exists. Treating a stale claim as a failing test — not
as a chore — is the only version of this I have seen survive a moving codebase.

## Writing the bar down before the measurement

Before the recording that this phase's repairs were judged on, I wrote down what it would have
to show, and what a miss would mean, and merged that document before generating a byte. It
then missed two of its bars: convictions reached without engine-certified proof came up short
by less than a single wrongful ejection, and wrongful ejections came in over the ceiling I had
set. Under the rule as written that is a finding, not an adoption. I recorded the miss, put it
on the front page, and adopted the recording anyway — by an explicit override carrying my name
and its date, stated as an override rather than dressed up as a pass. Two earlier phases of
learned-policy search ended the same way: several policies won more games than the scripted
comparator they were measured against, every one of them failed an evidence bar written down
*before* the measurement that judged it, and both phases closed having adopted nothing. The
discipline is worth nothing unless the bar can say no, and the only proof that it can is a
published miss.

## The critique I am keeping

The sharpest thing anyone said about this project is not a defect report. The review's
[research-lead read](../audits/review-2026-08-19/C/p2-ml-research-lead.md) closed with:
*"strong on measurement, weak on knowing when to stop building measurement."* Nobody rebutted
it, and [the code track](../audits/review-2026-08-19/B/repo-health-architecture.md) then handed
over the measurement that makes it concrete: **95,824 lines of process narration** — contracts,
generated prompts, audits — against **57,776 lines of core product Python**, a ratio of 1.66
to 1, against **3,358 lines of durable engineering documentation**.

Half of that ratio I would defend. The contracts are not commentary on the work; they *are*
the work, in the sense that they are what the agents executed, and a project built this way
has to write down more than one built by hand. The third number is the indictment. The
durable half — the pages someone else could read to understand the system — is the smallest of
the three, and it stayed smallest for nineteen phases for one reason: it was the only one no
gate required. When the critique arrived my instinct was to answer it with another instrument,
which is precisely the behaviour it names. The honest answer is that some of the apparatus
should have stopped being built two phases before it did, that I could not have seen that from
the inside, and that an outside read was the cheapest way to find out. This page is the
answer, not a tool.

---

**The review that found most of this is published**, curated and indexed, each finding linked
to the change that closed it — and titled by the four of its own headline claims it disproved:
[the 2026-08-19 three-track review](../audits/review-2026-08-19/README.md).
