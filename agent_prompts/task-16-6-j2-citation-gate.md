# Agent Prompt — 16.6 J2: citation-gated ballots (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.6 — J2: citation-gated ballots (default-OFF lever), anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2 (the gate design + the null-citation allowance it must respect); meetings/manager.py:1602-1648 (_collect_ballots guard chain — the slot after guard_ballot_target_graph); agents/strategic/prompts/qwen3_32b/vote_ballot.j2:134-153 (the sanctioned null-citation prose the gate must accommodate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-j2-citation-gate`
**Depends on:** 16.5
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2 (the gate design + the null-citation allowance it must respect); meetings/manager.py:1602-1648 (_collect_ballots guard chain — the slot after guard_ballot_target_graph); agents/strategic/prompts/qwen3_32b/vote_ballot.j2:134-153 (the sanctioned null-citation prose the gate must accommodate)
**Complexity:** Integration

The enforcement tooth, last in its chain: a zero-flag EJECT ballot (target carries no
contradiction flag this meeting) whose `primary_reason_id` AND `primary_reason_observation_id`
are both null/invalid is coerced to SKIP with a marker (never a crash, never a re-prompt), as a
new guard slotted AFTER `guard_ballot_target_graph` in `_collect_ballots` — the mark-and-coerce
pattern the guard chain already speaks. Scope honesty, straight from the planning doc's own
analysis: the gate cannot distinguish an honest memory-only conviction from a bare pile-on when
the voter cites nothing — that is WHY 16.5's observation-citation path must land first (an honest
witness can cite their private observation id), and why the DoD's soundness counterfactual is the
task's most important number. Default-OFF lever (`citation_gate_enabled`), registered behind
16.5's entry in the registry chain, stamped, byte-identical OFF.

**Files in scope:**
- meetings/manager.py (the citation-guard region after guard_ballot_target_graph — disjoint from 16.5's validation region and 16.7's turn-validation region)
- meetings/constants.py (the `citation_gate_enabled` resolver — the constants leaf keeps the manager import-clean)
- orchestrator/replay.py (lever registration region — behind 16.5's entry)
- .env.example (the lever env line)
- tests/meetings/test_citation_gate.py (new: coercion fixtures — zero-flag+no-citation coerced; flagged-target unaffected; turn citation satisfies; observation citation satisfies; fabricated citation nulls then coerces)

**Files NOT in scope:**
- meetings/voting.py (the tally consumes coerced ballots; it never learns about citations)
- agents/memory/ (no belief change — this is a ballot-surface guard)
- agents/strategic/prompts/ (the elicitation that ASKS for citations is 16.15's; the gate must behave correctly on today's prompts, where null citations are sanctioned prose)

**Definition of done:**
- [ ] Lever OFF = byte-identical (golden + `verify_samples.sh` green); lever ON changes ONLY the guard chain's output for the gated case (fixtures pin all five cases above).
- [ ] The soundness counterfactual on committed baseline-3 bytes: with the gate hypothetically ON and 16.5's citation path available, the report counts how many CORRECT impostor ejections would have been coerced (the contract's target: near zero, and every such case examined by hand in the PR) and how many soft-only mis-ejects would have been prevented — the J2 half of the judgment trade, measured before any graduation decision.
- [ ] Guard ordering is pinned: the citation guard runs after target-graph redirect (a redirected target's flag status is the redirected target's, not the original's — fixture-proven).
- [ ] The gate coerces, never rejects: a gated ballot becomes SKIP with a marker the transcript/artifacts record (the spectator surface reads it via the existing marker plumbing).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror `INVALID_REASON_ID_MARKER`'s shape for the coercion marker and slot the guard exactly where
the chain comment says post-redirect guards live. The zero-flag predicate reads this meeting's
`contradictions` tuple (already in `_collect_ballots` scope) keyed by target — no new plumbing.
The counterfactual rides the same offline machinery as 16.4's; run them on the same bytes so the
16.17 graduation slate reads one coherent judgment table.

## Public types this task introduces
- `meetings.constants.citation_gate_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This gate is a railroading-INVERSE — its failure mode is silencing honest convictions, which is
invisible in aggregate win rates. The soundness counterfactual (near-zero honest catches blocked)
is the merge bar, and any nonzero count is enumerated case-by-case in the PR for the graduation
slate. Ordering with 16.8's absence delta matters at the margins (absence can push a target over
the gate's zero-flag boundary only via flags, which absence never mints — assert that
non-interaction by test).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import agents.memory.beliefs"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-16-j2-citation-gate` with a title like `task 16.6: j2: citation-gated ballots (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J2 (the gate design + the null-citation allowance it must respect); meetings/manager.py:1602-1648 (_collect_ballots guard chain — the slot after guard_ballot_target_graph); agents/strategic/prompts/qwen3_32b/vote_ballot.j2:134-153 (the sanctioned null-citation prose the gate must accommodate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
