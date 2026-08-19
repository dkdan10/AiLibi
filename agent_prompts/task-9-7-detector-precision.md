# Agent Prompt — 9.7 Detector precision

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.7 — Detector precision, anchored to DESIGN.md §5.4, §6.3, §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (precision). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-detector-precision`
**Depends on:** none (belief-dynamics root)
**Section refs:** DESIGN.md §5.4, §6.3, §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (precision)
**Complexity:** Medium

The detector is the sole conversion fulcrum and a single contradiction lifts suspicion 0.5 → 0.8,
crossing the 0.60 eject-gate ALONE — so one noisy `alibi_vs_sighting` mismatch railroads an ejection.
13/13 wrong ejections were this; 8/13 were the body reporter's own self-stated alibi contradicted by
a third party's sighting of them. Per the owner principle, a LONE WEAK contradiction must not force
an eject; corroboration must. Reporters and innocents stay fully ejectable WITH a second signal — the
fix removes the mechanical railroad, not the ejectability.

**Files in scope:**
- meetings/transcript.py (thread `turn.speaker` onto `_IndexedAlibi`/`_IndexedSighting` in `_iter_alibis`/`_iter_sightings`; in `_detect_alibi_vs_sightings` identify a self-stated alibi `speaker == claim.subject` and a narrow window `to_tick - from_tick` below a small constant — these are the false-positive patterns)
- agents/memory/beliefs.py (PREFER a NARROW, GRADUATED down-weight that targets ONLY the flagged-weak contradictions (self-stated / narrow-window) and preserves a strong contradiction's full weight — a weak signal alone lands suspicious-but-below-gate in [0.5, 0.60), NOT zeroed and NOT crossing. Lower `CONTRADICTION_SUSPICION_DELTA` GLOBALLY only if the narrow version is impractical, stating the recall cost — global weakens strong contradictions too — and any schema/byte implication. Classifying a contradiction as weak for the graduated delta likely needs a derivable property or a new ContradictionRef kind; pick one and state its byte/format implication)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (self-stated and narrow-window contradictions do not alone cross 0.60; a self-stated alibi PLUS a second independent signal does; the seed-3/16/47 false-positive shapes no longer auto-eject)

**Files NOT in scope:**
- agents/strategic/prompts/** (no prompt edits here; gp-3 owns the turn prompts in 9.9)
- the §4.6 gate render in vote_ballot.j2 (FROZEN during measurement — the gate is gate-correct; this is a detector/suspicion change)
- replays/samples/** (re-record is 9.11)

**Definition of done:**
- [ ] A self-stated `alibi_vs_sighting` (the reporter's own alibi vs a sighting of them) and a narrow-window mismatch do NOT alone lift the subject across 0.60 — but the down-weight is GRADUATED, not a hard zero: a lone weak contradiction lands in the suspicious-but-not-eject band [0.5, 0.60), so it still raises suspicion (a self-stated conflict IS mildly suspicious). Pinned numerically with the seed-3/16/47 shapes.
- [ ] The same subject WITH a second independent contradiction (or a body-proximity / vent signal) DOES cross — corroboration still ejects. A test asserts the corroboration path so the fix is not "innocents become un-ejectable".
- [ ] If a per-contradiction weight on ContradictionRef is introduced, it is documented as a public-schema change and the format/byte implications are stated; otherwise the down-weight is derived from re-derivable properties with no schema change (preferred).
- [ ] Replay determinism holds: the detector + belief math are pure functions, re-running yields byte-identical flags.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The seam is small: `_iter_alibis`/`_iter_sightings` already have the turn in scope, so the speaker is
one field away. Prefer filtering/down-weighting from re-derivable properties (self-stated, window
width) over a ContradictionRef schema field — it avoids a byte/format change and keeps the recorded
flag set honest. Whatever mechanism is chosen, the corroboration test is the contract's hard line:
proving an innocent is still ejectable on a second signal is what distinguishes "stop the railroad"
from "shield the reporter".

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

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
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-9-detector-precision` with a title like `task 9.7: detector precision`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4, §6.3, §4.6; audits/audit-2026-06-09-0347-gameplay-data.md gp-1 (precision)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
