# Agent Prompt — 18.9 The endpoint-band whereabouts exemption + the vent-placement flag variant (default-OFF) + counterfactuals

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.9 — The endpoint-band whereabouts exemption + the vent-placement flag variant (default-OFF) + counterfactuals, anchored to audits/audit-phase-18-planning.md §3.3 (why roll-call lies can never mint STRONG flags); meetings/transcript.py:529 (`WEAK_REASON_ENDPOINT_TICK`), :2262-2270 (the band application), :1927-1945 (the single-tick self-alibi indexing); audits/audit-phase-17-close.md §6 item 4 (BOTH halves of the routed detector package: the endpoint relaxation AND the grounded-vent flag-minting variant); tasks/phase-17.md §Designer rulings (the 17.5 grounding chokepoint the variant reuses). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-endpoint-band-exemption`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.3 (why roll-call lies can never mint STRONG flags); meetings/transcript.py:529 (`WEAK_REASON_ENDPOINT_TICK`), :2262-2270 (the band application), :1927-1945 (the single-tick self-alibi indexing); audits/audit-phase-17-close.md §6 item 4 (BOTH halves of the routed detector package: the endpoint relaxation AND the grounded-vent flag-minting variant); tasks/phase-17.md §Designer rulings (the 17.5 grounding chokepoint the variant reuses)
**Complexity:** Medium

The detector half of the routed Phase-18 package — both flag-minting levers, each
independently flag-gated and default-OFF. **(1) The endpoint-band exemption**, the lever
that converts roll-call answers into conviction-economy currency: a single-tick whereabouts
self-alibi contradicted by a first-hand sighting mints a STRONG (interior-class) flag
instead of being endpoint-banded to weak. **(2) The vent-placement flag variant** (the 17.5
scope firewall's flag-minting variant, routed by the close): a GROUNDED spoken vent
sighting — matched against the speaker's own `VentWitnessRecord`, the 15.4 chokepoint —
placing subject X in contradiction with X's own stated path mints a physical-contradiction
flag (today the widening feeds only the absent-set derivation; this arm feeds the
detector). OFF-path bytes identical for both. With the mechanisms, the committed-bytes
counterfactuals the gate reads: over the corpus and samples, how many recorded whereabouts
lies would have minted STRONG flags under the exemption, by liar role (today: 25 corpus
lies, 20 crew-authored / 5 impostor-authored, all weak), and how many grounded vent
placements would have minted physical flags, by subject role — the honest price of each
change in both directions.

**Files in scope:**
- meetings/transcript.py; (both mechanisms + resolvers)
- tests/meetings/test_contradictions.py (OFF-path byte-identity; ON-path STRONG-mint and vent-flag fixtures; the committed-bytes counterfactual pins by role)

**Files NOT in scope:**
- meetings/manager.py; (18.8's region)
- eval/ (instruments read recorded flags; the counterfactuals live in the detector's own test pins)

**Definition of done:**
- [ ] With both flags OFF, `detect_contradictions` output over committed bytes is byte-identical (pinned); exemption ON, a contradicted single-tick whereabouts claim mints a STRONG `alibi_vs_sighting` flag while multi-tick alibi endpoint semantics are untouched; variant ON, a grounded vent placement contradicting the subject's stated path mints a physical-contradiction flag and an UNGROUNDED vent claim can never mint one — all fixture-pinned.
- [ ] Both committed-bytes counterfactuals are pinned: the would-be STRONG-mint census (by liar role) and the would-be vent-flag census (by subject role) over corpus + samples, quoted in the PR for the 18.11 gate memo.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Scope the exemption to the degenerate `from_tick == to_tick` self-alibi class only — the
narrow-window weak reason and the two-source discipline for genuine multi-tick alibis do
not move. The vent variant reuses the 17.5 grounding chokepoint verbatim (grounded-only is
the firewall — an ungrounded vent claim minting a flag would be a fabrication channel). The
counterfactuals are re-runs of the current detector with each flag ON over reconstructed
transcripts, the 17.5 pin pattern.

## Public types this task introduces
- `meetings.transcript.whereabouts_interior_flags_enabled`
- `meetings.transcript.vent_placement_contradictions_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-18-endpoint-band-exemption` with a title like `task 18.9: the endpoint-band whereabouts exemption + the vent-placement flag variant (default-off) + counterfactuals`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.3 (why roll-call lies can never mint STRONG flags); meetings/transcript.py:529 (`WEAK_REASON_ENDPOINT_TICK`), :2262-2270 (the band application), :1927-1945 (the single-tick self-alibi indexing); audits/audit-phase-17-close.md §6 item 4 (BOTH halves of the routed detector package: the endpoint relaxation AND the grounded-vent flag-minting variant); tasks/phase-17.md §Designer rulings (the 17.5 grounding chokepoint the variant reuses)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
