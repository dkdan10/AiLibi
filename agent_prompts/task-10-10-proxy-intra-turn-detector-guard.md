# Agent Prompt — 10.10 Proxy-intra-turn detector guard

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.10 — Proxy-intra-turn detector guard, anchored to DESIGN.md §5.4, §6.3; audits/audit-2026-06-13-1816-gameplay-data.md C-C-2, C-C-3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-proxy-intra-turn`
**Depends on:** none (Stage-1 root)
**Section refs:** DESIGN.md §5.4, §6.3; audits/audit-2026-06-13-1816-gameplay-data.md C-C-2, C-C-3
**Complexity:** Medium

The close audit's one wrong ejection on an otherwise-clean baseline: the 10.9.2 guard redirected an
ungrounded ballot to an innocent (seed-40 p-4 @0.66) whose suspicion was a pure flag-stacking
ARTIFACT — TWO weak contradictions both minted from ONE speaker (p-5, crew) emitting two
mutually-contradictory proxy-alibis ABOUT p-4 in a single turn: an `alibi_conflict` between p-5's two
p-4-alibis and an `alibi_vs_sighting` between p-5's alibi-for-p-4 and p-5's own sighting of p-4.
Different lift-keys, so the 10.1 per-(subject,claim) dedup did NOT merge them (0.5+0.08+0.08=0.66).
This is the laundering case — a single unreliable speaker's claims ABOUT a third party stacking over
the gate. Generalizes set-wide: 3 of 9 single-turn self-contradictions are proxy (seed-40, seed-2).
The 10.6 proxy-alibi rule covers a third-party alibi the subject's own account contradicts; it does
NOT cover two same-speaker proxy-claims conflicting with EACH OTHER.

**CAREFUL LINE (the hard constraint):** this fixes ONLY the same-speaker intra-turn case. It must NOT
touch the cross-speaker third-party alibi where an impostor frames an innocent (seed-12 — impostor
p-1's alibi for p-6 minting the set's lone strong flag). That is a LEGITIMATE deception surface and a
10.13 probe input, not a bug; hardening it would blunt honest crew alibis. The guard keys on a single
speaker authoring BOTH events, which seed-12 (cross-speaker) does not satisfy.

**Files in scope:**
- meetings/transcript.py (a detector guard at contradiction construction: when BOTH events of a contradiction (event_a_id, event_b_id) resolve to turns by the SAME speaker AND that speaker is NOT in the flag's subjects, retarget the flag WEAK at the speaker via a new `WEAK_REASON_PROXY_INTRA_TURN` reason, OR suppress it against the subject — prefer re-target so the speaker's unreliability is still recorded, capped weak so it cannot eject alone; the event→turn→speaker resolution reuses the existing event-id parsing the lift-key machinery already does at `_contradiction_lift_key`; the guard runs AFTER the existing weak classification so a flag already weak stays weak)
- agents/memory/beliefs.py (only if the new weak reason needs registering in the weak-delta path; no constant changes)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py (pins below, offline against committed bytes)

**Files NOT in scope:**
- the cross-speaker proxy-alibi rule (10.6 `WEAK_REASON_RETARGETED_PROXY` — untouched; the seed-12 strong flag must SURVIVE)
- meetings/manager.py ballot-target guard (10.9.2 — the redirect logic is correct; this fixes the detector feeding it)
- the §4.6 render/threshold, 9.8 constants, token caps (frozen)
- replays/samples/** (no re-record)

**Definition of done:**
- [ ] Seed-40 pin: m0's two contradictions on p-4 (both from p-5's turn-1) are re-targeted WEAK at p-5 (or suppressed against p-4); p-4's re-derived max drops below 0.60; under the original recorded ballots p-4 is no longer the redirect argmax (walked offline against committed bytes).
- [ ] Seed-2 pin: the proxy intra-turn contradiction (p-7 about p-8) is re-targeted/suppressed identically.
- [ ] The seed-12 STRONG flag SURVIVES (cross-speaker: impostor p-1's alibi vs the reporter's sighting — different speakers, so the guard does not fire). Pinned individually — this is the tripwire.
- [ ] A genuine same-subject contradiction from TWO different speakers (a real two-witness disagreement) is unaffected; seed-14 m0's real two-witness fold on p-3 still classifies as today.
- [ ] Determinism: the guard is a pure function of the transcript; re-runs are byte-identical.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

The event-id → speaker map already exists in spirit: `_contradiction_lift_key` parses the
`event_a_id`/`event_b_id` to group flags. Reuse the same parse to find each event's turn, then the
turn's speaker. One-home: the guard lives beside the existing weak classification in transcript.py,
not in a new module. The seed-40 and seed-12 walks both run offline via the replay-loader pattern the
audit extractor demonstrates — every pin is checkable for $0.

## Public types this task introduces
- `WEAK_REASON_PROXY_INTRA_TURN`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-10-proxy-intra-turn` with a title like `task 10.10: proxy-intra-turn detector guard`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4, §6.3; audits/audit-2026-06-13-1816-gameplay-data.md C-C-2, C-C-3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
