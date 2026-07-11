# Agent Prompt — 16.5 Observation identity: stable ids + the citation plumbing (enforcement-free)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.5 — Observation identity: stable ids + the citation plumbing (enforcement-free), anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8 (the private-evidence citation chain); agents/memory/episodic.py:19-30 (EpisodicEvent — no id today); agents/memory/store.py (the memory render the ids must appear in); meetings/schemas.py:317-330 (VoteBallot + primary_reason_id); meetings/manager.py:2264-2303 (_normalize_ballot_reason_id — the validation pattern to mirror). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-observation-identity`
**Depends on:** 16.3, 16.4
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8 (the private-evidence citation chain); agents/memory/episodic.py:19-30 (EpisodicEvent — no id today); agents/memory/store.py (the memory render the ids must appear in); meetings/schemas.py:317-330 (VoteBallot + primary_reason_id); meetings/manager.py:2264-2303 (_normalize_ballot_reason_id — the validation pattern to mirror)
**Complexity:** Integration

The C8 chain, built enforcement-LAST so every piece is provable before anything blocks a ballot:
(a) **stable observation ids** on episodic events — deterministic (derived from agent/tick/
sequence, never RNG), assigned at write time in the perception path, surviving the store's
compaction; (b) **id rendering** in the memory prompt behind a default-OFF render lever
(`observation_id_rendering_enabled`) — rendering ids changes `rendered_memory` bytes, so OFF is
proven by the 16.3 golden and ON becomes real only at the 16.15 elicitation surface; (c) the
ballot gains `primary_reason_observation_id` (additive, optional — committed replays parse
unchanged); (d) the manager receives each voter's valid-id set (the same participant-threading
pattern as `vent_witness_records`) and VALIDATES the new field exactly as
`_normalize_ballot_reason_id` validates turn ids — mark-and-null on a dangling id, never a crash —
but NO gate consults it yet: 16.6 enforces. This is the task that makes private hard evidence
(a witnessed kill or vent the voter holds but nobody spoke) CITABLE, which is the C3 catch: a
citation gate without this path would block the honest convictions it exists to protect.
Dependency note: the 16.4 edge exists ONLY to serialize the `orchestrator/replay.py` lever-
registry region (the 15.6 → 15.8 precedent) — nothing semantic.

**Files in scope:**
- agents/memory/episodic.py (stable id field + deterministic assignment)
- agents/perception.py (id assignment at the observed-event write sites)
- agents/memory/store.py (id-rendering region behind the lever — the render changes only lever-ON)
- meetings/schemas.py (ballot citation-field region: `primary_reason_observation_id`, additive — disjoint from 16.7's observation-union region)
- meetings/manager.py (observation-id validation region beside `_normalize_ballot_reason_id` + participant threading — disjoint from 16.6's guard region and 16.7's turn-validation region)
- orchestrator/game.py (participant observation-id-set accessor region — the vent-accessor pattern; disjoint from 16.9's persona region and the registry line)
- orchestrator/replay.py (lever registration region — behind 16.4's entry)
- .env.example (the lever env line)
- tests/agents/test_episodic_ids.py (new)
- tests/meetings/test_ballot_observation_citation.py (new)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- meetings/transcript.py (no detection change — vouch grounding is 16.7's)
- agents/strategic/prompts/ (no template edit; the ids render lever-ON only and the elicitation ask is 16.15's)

**Definition of done:**
- [ ] Observation ids are deterministic and stable: two reconstructions of any committed replay assign identical ids (pinned over a committed set); ids survive store compaction; no RNG anywhere in the scheme.
- [ ] Id-rendering OFF = byte-identical (the golden green with the lever merged OFF); lever-ON renders each remembered observation with its id in a fixture (mechanism-proven; model uptake is 16.15/16.17's business).
- [ ] `primary_reason_observation_id` round-trips the ballot schema additively — every committed replay still parses (backward-compat pinned) — and the manager nulls a dangling id with a marker exactly like the turn-id path, never rejecting the ballot.
- [ ] The voter's valid-id set reaches the manager through typed participant threading (never prose parsing), and a fixture proves a private witnessed-kill observation's id validates while a fabricated id nulls.
- [ ] No gate, guard, or tally consults the new field (asserted) — enforcement is 16.6's, and this task's surface is provably inert with both levers OFF.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Derive ids as `{agent_id}:{tick}:{seq}` (or equivalent) so replay reconstruction regenerates them
byte-for-byte — the determinism suite is your proof, and any hash-of-content scheme that includes
floats is a trap. The threading is a near-copy of `vent_witness_records_for_meeting` → 
`MeetingParticipant` → validation; mirror the naming so the two channels read as siblings. Keep
(a)–(d) in separately revertable commits: enforcement-free means each layer is independently
provable.

## Public types this task introduces
- `agents.memory.episodic.ObservationId`
- `agents.memory.store.observation_id_rendering_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The id scheme is forever — once a recorded baseline renders ids into prompts (16.17), changing the
scheme re-records. Get the determinism suite ruthless now. The ballot-field addition touches the
same schemas file as 16.7's union work: keep to the ballot region, and rebase deliberately if 16.7
lands adjacent edits first (the preamble declares the regions disjoint — honor the declaration).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-16-observation-identity` with a title like `task 16.5: observation identity: stable ids + the citation plumbing (enforcement-free)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8 (the private-evidence citation chain); agents/memory/episodic.py:19-30 (EpisodicEvent — no id today); agents/memory/store.py (the memory render the ids must appear in); meetings/schemas.py:317-330 (VoteBallot + primary_reason_id); meetings/manager.py:2264-2303 (_normalize_ballot_reason_id — the validation pattern to mirror)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
