# A decision that did not pass its own rule

Daniel Keinan directed AiLibi; Claude Code and Codex agents implemented and
reviewed it. This case study was drafted by Codex from the preserved decision
records. It describes an owner ruling, not hand-written implementation or an
independent human audit.

## The problem and the options

The crew could treat contradictory speech as proof and convict innocent players.
The evidence repairs changed what meetings were allowed to claim: source-bound
observations, distinct categories for direct role evidence and weaker conflicts,
and clearer limits on fabricated statements. The proposed replacement recording
needed to show that these repairs improved decisions, not merely that tests passed.

The owner had two consequential options after the measurement: retain the prior
reference under the written decision rule, or explicitly adopt the repaired
system despite a failed rule. The [record's decision section](../audits/audit-phase-20-baseline-7.md#6-the-verdict)
ruled out selectively adopting convenient pieces. The experiment therefore did
not authorize an informal partial pass.

## What the evidence said

The [pre-registered measurement](../audits/audit-phase-20-baseline-7.md#3-the-pre-registered-read-bar-by-bar)
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

## The owner judgment

On 2026-08-26, Daniel explicitly adopted the replacement as the reference while
leaving the experiment's verdict **FINDING**. The [owner ruling](../audits/audit-phase-20-baseline-7.md#61-the-owners-adoption-ruling-2026-08-26),
recorded on [PR #389](https://github.com/dkdan10/AiLibi/pull/389), cited the narrow
accuracy miss, the reduction in innocent convictions, reduced fabrication, and
the qualitative changes in the inspected meetings.

That traded adherence to the original adoption rule for the owner's judgment
that this was the more useful reference for subsequent work. It did not make
an experiment pass, establish general deduction, or demonstrate that the new
reference would generalize. A reviewer can disagree with the override while
still checking what was measured and who accepted the tradeoff. That separation
is the central ownership claim here.

## Implementation and review evidence

The [execution record](../audits/audit-phase-20-baseline-7.md#62-what-the-ruling-executed-in-this-pr)
lists what adoption actually changed: the reference, graduated behavior, and
associated provenance. Agents implemented those changes and wrote substantial
parts of the supporting material. The [close audit](../audits/audit-phase-20-close.md)
and later [maintenance recording](../audits/audit-phase-21-rerecord.md) remain
available to assess the implementation and its subsequent defects. The review
process used separate AI reviewers; it is not evidence of external human assurance.

Current work uses [canonical cards and explicit ownership](workflow.md), with
acceptance checks, adverse tests, and independent agent review before the owner's
final review. The original phases used generated prompts. The historical example
below makes that earlier contract-to-implementation path inspectable; it does
not claim that Daniel personally authored every source contract or generated file.

<!-- EXHIBIT: both excerpts below are byte-checked against their sources by tests/scripts/test_check_doc_facts.py. -->

**1 — the historical contract**, from [`tasks/phase-19.md`](../tasks/phase-19.md). Two runs of it, verbatim:

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

**2 — the prompt the generator produced from it**, [`agent_prompts/task-19-2-in-code-truth.md`](../agent_prompts/task-19-2-in-code-truth.md). It carries the contract in verbatim, and `uv run python scripts/generate_prompts.py --check` fails the gate the moment the two disagree:

```markdown
# Agent Prompt — 19.2 The in-code truth sweep: docstrings match the bytes

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.
```

**3 — the pull request it produced**: [#328](https://github.com/dkdan10/AiLibi/pull/328), reviewed and merged; on `main` it is the squash commit whose subject ends `(#328)`.
<!-- EXHIBIT-END -->

## What later evidence limits

The maintenance recording measured proof-free accuracy at 50/96 = 0.5208 and
46 innocent ejections across four recorded sets. It registered no fresh adoption
bars and does not retroactively validate the override. In the canonical 9-player
set, 68 of 82 correct ejections involve direct vent evidence; without it, only
14 of 27 ejections target impostors. [The reading guide](reading-guide.md)
separates those denominators and explains why general social deduction remains
unproven.

A later experiment reduced innocent ejections to 20 but missed its reporter-share
criterion: 11/20 = 0.5500 against 0.40. Its **FINDING** verdict was not overridden
and it was not adopted ([record](../audits/audit-phase-21-adopting-record.md)).
The [learned-policy program](ml-program.md) likewise adopted no default replacement
after its candidates missed pre-registered evidence-quality gates. Those decisions
must not be conflated with the earlier override.

The portfolio evidence is the ability to frame a question, preserve an unfavorable
measurement, make a named judgment, and leave enough implementation and review
material to challenge it. It is not an assertion that the judgment was inevitable
or that AI-written tests establish the right game design. Open the
[three replay cases](https://dkdan10.github.io/AiLibi/?set=9p2i&view=tournament)
to inspect where the system uses evidence well, where persuasive reasoning fails,
and where the agents leave a question unresolved.
