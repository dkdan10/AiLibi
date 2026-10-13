# Decision: retire the generated prompts, 2026-10-13

**Status: relayed, pending the owner's merge.** On 2026-10-13, in a Claude Code session, the owner approved the
recommended decisions of the document clean-up plan, which include deleting the generated prompts. This record was
written from that direction; the owner's merge of the change that carries it is its confirming signature.

**What was retired.** `agent_prompts/` (390 files, 6,106,279 bytes), each generated from a contract in
`tasks/phase-*.md`; its generator (`scripts/generate_prompts.py`, `scripts/prompt_template.md.j2`) and the gate leg that
ran it; the phase-contract checks in `scripts/validate_task_docs.py` (prompt sync, dependency graph, complexity, record
impact, public types, file scope); and `scripts/compute_next_task.py`, the old phase scheduler. The repository history
keeps all of it.

**What stays.** The 24 `tasks/phase-*.md` contracts, unedited, as records. `scripts/validate_task_docs.py` keeps the
work-card checks and the task index's card count, and now fails when it finds no cards. The prompt the
[ownership case study](../../docs/ownership-case-study.md) quoted is linked at its last commit instead.

**What it reverses.** Recommendation 5 of the 2026-09-06 review ("Decline the deletion"), in the "Section 11 workflow
recommendations" table of [docs/cleanup-dispositions.md](../docs/cleanup-dispositions.md). That row is kept as written;
a dated note at the end of the ledger points here.
