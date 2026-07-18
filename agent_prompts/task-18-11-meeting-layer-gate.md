# Agent Prompt — 18.11 THE MEETING-LAYER GATE: probe + ruling (operator ~8–9h + owner) + phase-doc surgery

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.11 — THE MEETING-LAYER GATE: probe + ruling (operator ~8–9h + owner) + phase-doc surgery, anchored to audits/audit-phase-18-planning.md §3.4 + §7 (the package and its arms); audits/audit-phase-17-absence-gate.md (the ratified 0.20/0.60 bar + Ruling 3; the gate-with-surgery precedent); tasks/phase-17.md 17.7 (the memo-then-ruling shape); the 18.8/18.9/18.10 counterfactual pins (the offline evidence). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-meeting-layer-gate`
**Depends on:** 18.7, 18.8, 18.9, 18.10
**Section refs:** audits/audit-phase-18-planning.md §3.4 + §7 (the package and its arms); audits/audit-phase-17-absence-gate.md (the ratified 0.20/0.60 bar + Ruling 3; the gate-with-surgery precedent); tasks/phase-17.md 17.7 (the memo-then-ruling shape); the 18.8/18.9/18.10 counterfactual pins (the offline evidence)
**Complexity:** Integration

The phase's substrate decision, made on evidence. Operator leg: record two probe sets on
the real path at 25 seeds 9p2i each — FULL (roll-call round + endpoint exemption +
impostor-answer variant ON) and CREW-ONLY (round + exemption ON, impostor templates
default) — ~8–9 h total at 2 workers, working artifacts outside the tree, measurements
committed. Memo leg: assemble `audits/audit-phase-18-meeting-gate.md` quoting the probe
cells and the Wave-1 offline counterfactuals against the PRE-REGISTERED bars: (a) crew
roll-call coverage on the probe ≥ **0.60** (the ratified crew clause, measured live); (b)
the absence counterfactual re-run on probe bytes reads new-over-gate ≤ **0.20** (the
ratified ceiling); (c) the impostor-answer arm ships only if probe impostor win ≥ **0.20**
(not annihilated; FSM comparator 0.36) AND the STRONG self-flag rate ≤ **0.25** of answered
impostor roll-calls; (d) the vent widening AND its flag-minting variant (18.9's second
arm) re-ruled with the package (the 17.7 Ruling 2 HOLD travels here; the FULL probe runs
with the variant ON so its live flag yield is measured, not extrapolated). The owner rules
**FULL / CREW-ONLY / NONE**; absence-prior graduation rides the ruling per the ratified
bar. Then the surgery in the ruled direction, exactly as
the Baseline-numbering block enumerates; prompts regenerate; validator green.

**Files in scope:**
- audits/audit-phase-18-meeting-gate.md (new: the memo + the recorded ruling)
- orchestrator/replay.py; (the substrate-flag snapshot registry ONLY: the four new lever flags — roll-call round, endpoint exemption, vent-flag variant, impostor-answer — wired in BEFORE any probe seed records, so probe/adoption recordings self-describe the arms under test; today the snapshot knows only `absence_prior`)
- tests/orchestrator/ (the snapshot-registry fixtures)
- tests/experiments/test_probe_backends.py (the hard-coded `_FLAGS_ON`/default-snapshot pins — `active_substrate_flags` delegates to the snapshot and grows with it)
- tasks/phase-18.md; (the surgery + the banner note)
- agent_prompts/ (regenerated)

**Files NOT in scope:**
- meetings/ + agents/strategic/prompts/ (the mechanisms are built; the gate rules, never edits)
- replays/samples/ + replays/ml_corpus/ (no committed record at the gate — probe sets are working artifacts)

**Definition of done:**
- [ ] The four new lever flags are registered in the replay substrate-flag snapshot BEFORE the first probe seed records (fixture-pinned; committed sets re-verify byte-identical — the registry addition must not move existing bytes).
- [ ] Both probe sets recorded 25/25 on the real Featherless path ($0, the arms under test stamp-proven via the substrate-flag snapshot in the recorded bytes), validity-gated, with every bar cell quoted beside its pre-registered threshold and the ruling recorded verbatim (FULL / CREW-ONLY / NONE, plus the vent-widening and absence-graduation components).
- [ ] The surgery is complete in the ruled direction (the Baseline-numbering block's enumeration): validator green, prompts regenerated, `scripts/compute_next_task.py --phase 18` consistent with the surviving DAG, no orphan references.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Memo before ruling (the 15.18 shape). The 25-seed probe is deliberately underpowered for
fine effects — the bars are chosen so a fail is a >1σ read at n=25 (quote the two-proportion
z beside each verdict; the crew-coverage and self-flag cells have per-meeting denominators
well above 25). Price both directions honestly: what CREW-ONLY forfeits (no new impostor
lie material) and what FULL risks (the self-flag class).

## Integration risk

An operator + owner + surgery task in one PR, like 17.7 but with a recording leg. Keep the
probe recordings out of the tree (the finalist-eval separation discipline); if the ruling
stalls, the PR stays open with the memo complete and the DoD honest (the 17.14 PENDING
pattern) — never merge a ruling that has not happened.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`

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
Open a PR from branch `phase-18-meeting-layer-gate` with a title like `task 18.11: the meeting-layer gate: probe + ruling (operator ~8–9h + owner) + phase-doc surgery`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.4 + §7 (the package and its arms); audits/audit-phase-17-absence-gate.md (the ratified 0.20/0.60 bar + Ruling 3; the gate-with-surgery precedent); tasks/phase-17.md 17.7 (the memo-then-ruling shape); the 18.8/18.9/18.10 counterfactual pins (the offline evidence)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
