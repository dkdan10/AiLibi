# Agent Prompt — 17.17 Baseline 6: the mover record + the phase close (operator + owner, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.17 — Baseline 6: the mover record + the phase close (operator + owner, $0), anchored to tasks/phase-16.md 16.17 (the close runbook: atomic record, validity gates, floors, canaries, Q5, banner); audits/audit-phase-16-close.md §0.4 (the canary-band discipline + the R1 band-edge warning) + §8 (the staleness rule this close re-states for Phase 18); eval/vote_correctness.py (17.6's successor instrument — canary-eligible for the first time); replays/ml_corpus/ (the Q3-restored canonical denominator). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-baseline-6-close`
**Depends on:** 17.1, 17.3, 17.6, 17.13, 17.15, 17.16
**Section refs:** tasks/phase-16.md 16.17 (the close runbook: atomic record, validity gates, floors, canaries, Q5, banner); audits/audit-phase-16-close.md §0.4 (the canary-band discipline + the R1 band-edge warning) + §8 (the staleness rule this close re-states for Phase 18); eval/vote_correctness.py (17.6's successor instrument — canary-eligible for the first time); replays/ml_corpus/ (the Q3-restored canonical denominator)
**Complexity:** Integration

The phase's terminal record and second owner gate. FLIP path (17.16 flipped the
default): atomic re-record of both sample sets with the champion as the default mover —
**baseline 6**, the first mover-layer baseline — MANIFEST provenance exact (the policy
column names the champion stamp), validity gates, byte-identical bare reconstruction,
floors re-pinned, pre-registered canary bands on the Q3-restored corpus denominator
(the close's canaries finally leave the 50-seed UNDERPOWERED regime) with 17.6's
successor instrument as a named canary cell, full before/after on 16.10's instruments,
Q5 tag (the owner completes the push), close audit, banner flip to CLOSED, README +
roadmap provenance. NO-FLIP path: no record — the ladder tip stands, and the close
audit documents the finding (which floor failed, by how much, what Phase 18 would need)
with the same instrument reads over the existing bytes. Either way the audit re-states
the staleness rule for Phase 18 (heterogeneous lobbies change the meeting layer AGAIN —
nothing in this phase's artifacts survives that unexamined) and routes the deferred
items (crew deployment surface, detector-band relaxation, absence-prior Phase-18
re-run if stay-OFF, pooling-prompt uptake work).

**Files in scope:**
- replays/samples/9p2i/ + replays/samples/4p1i/ (the baseline-6 record — FLIP path only)
- eval/watchability.py (baseline-6 floors — FLIP path only)
- audits/baseline5-final-measure.json (new: the BEFORE column, captured pre-replacement — FLIP path)
- audits/audit-phase-17-close.md (new)
- tasks/phase-17.md (the banner flip)
- README.md + tasks/post-phase-14-plan.md (status + provenance)
- tests/ (re-pins + the byte-coupled sweep)

**Files NOT in scope:**
- replays/ml_corpus/ (recorded once at 17.9 — the mover flip does not invalidate meeting-layer calibration data; the close audit SAYS so explicitly, with the caveat that impostor-behavior-conditioned cells are champion-era from baseline 6 on)
- agents/ + training/ (frozen at 17.16)

**Definition of done:**
- [ ] FLIP path: both sets recorded with the champion default and PASS the validity gate; byte-identical bare reconstruction; the MANIFEST policy column names the champion stamp on every row; floors pinned; canaries judged on the corpus denominator with the pre-registered bands quoted (17.6's successor cell among them); the before/after instrument read committed. NO-FLIP path: the close audit's finding section carries the full floor arithmetic and instrument reads with no record.
- [ ] The close audit re-states the Phase-18 staleness rule and the routed items, names the Q5 tag arm (or its fallback), and the banner/README/roadmap lines record the close.
- [ ] `scripts/compute_next_task.py --phase 17` shows the phase complete; validator green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Pre-register the canary bands and capture the BEFORE column before the first recorded
seed (the 15.18/16.17 discipline). On the no-flip path resist recording anything — the
close's value is the honest finding; on the flip path the record session is the 16.17
runbook with the mover as the only changed layer.

## Integration risk

First mover-layer record on the ladder: the R-gate and funnel cells will move for
CHAMPION reasons, not meeting-layer reasons — the audit must attribute every canary
band to the right layer (the before column is same-meeting-layer, so deltas ARE the
mover; say so). The 16.4-era counterfactual tests that walk committed bytes with
recorded roles must be re-pinned for the new bytes — the same byte-coupled sweep every
record performs, budgeted in the session.

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
Open a PR from branch `phase-17-baseline-6-close` with a title like `task 17.17: baseline 6: the mover record + the phase close (operator + owner, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-16.md 16.17 (the close runbook: atomic record, validity gates, floors, canaries, Q5, banner); audits/audit-phase-16-close.md §0.4 (the canary-band discipline + the R1 band-edge warning) + §8 (the staleness rule this close re-states for Phase 18); eval/vote_correctness.py (17.6's successor instrument — canary-eligible for the first time); replays/ml_corpus/ (the Q3-restored canonical denominator)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
