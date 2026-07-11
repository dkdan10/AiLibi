# Agent Prompt — 16.4 J1: the hard-evidence render gate (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.4 — J1: the hard-evidence render gate (default-OFF lever), anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J1 (the measured 24/31 vs 6/16 trade — baseline-2-era, re-measure); agents/memory/beliefs.py (the 0.60 gate discipline + REPORTER_EXCULPATION precedent); orchestrator/replay.py:395-431 (_TOGGLEABLE_LEVER_RESOLVERS, currently empty, + _RETIRED_ALWAYS_ON_LEVERS). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-j1-hard-evidence-gate`
**Depends on:** 16.3
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J1 (the measured 24/31 vs 6/16 trade — baseline-2-era, re-measure); agents/memory/beliefs.py (the 0.60 gate discipline + REPORTER_EXCULPATION precedent); orchestrator/replay.py:395-431 (_TOGGLEABLE_LEVER_RESOLVERS, currently empty, + _RETIRED_ALWAYS_ON_LEVERS)
**Complexity:** Integration

Close the zero-flag channel at its root: a conviction-grade rendered suspicion (≥ 0.60) whose
provenance is ENTIRELY soft (testimony-spread + accusation-carry + carried prior — no flag, no
body-proximity, no kill/vent pin) is clamped to render just below the gate in the pre-vote
surface. Hard-backed suspicion renders untouched; the clamp classifies on 16.3's typed provenance,
never on the scalar or on prose. Ships as the first lever back into the now-empty
`_TOGGLEABLE_LEVER_RESOLVERS` (default-OFF, `substrate_flag_snapshot` stamped, the 13.5/14.10
pattern end-to-end). The planning doc's static counterfactual measured 24/31 crew mis-ejects
neutralized vs 6/16 impostor catches risked — but those are BASELINE-2-era figures and the
champion close reshaped exactly the relevant distribution (witnessed kills 5 → 32, structured
vents 0 → 55, innocent-reporter ejections 22 → 4); this task's DoD RE-MEASURES the counterfactual
on the committed baseline-3 bytes, and the 16.17 graduation decision re-checks it on the adopting
baseline's bytes. The trade is a hypothesis to re-measure, not a carried fact.

**Files in scope:**
- agents/memory/beliefs.py (the clamp rule + `hard_evidence_gate_enabled` resolver — behind 16.3's provenance region)
- orchestrator/replay.py (lever registration region — the first entry back into `_TOGGLEABLE_LEVER_RESOLVERS` + `substrate_flag_snapshot`)
- .env.example (the lever env line)
- tests/agents/test_beliefs_hard_evidence_gate.py (new: clamp classification + OFF-path byte pins)
- tests/orchestrator/test_replay.py (lever stamp region)

**Files NOT in scope:**
- meetings/manager.py + meetings/voting.py (the clamp lives in the belief render path; no guard or tally change — J2's guard is 16.6)
- meetings/render_contract.py (16.3 landed the contract; consumed as-is)
- replays/samples/ (OFF must be byte-identical; the re-record is 16.17)

**Definition of done:**
- [ ] Lever OFF = byte-identical: the 16.3 prompt-byte golden and `bash scripts/verify_samples.sh` both green with the lever merged OFF.
- [ ] The clamp classifies on typed provenance only: a soft-only 0.70 renders sub-gate; the SAME scalar with any hard component renders unchanged — both pinned by fixture, including the pre-vote re-render path.
- [ ] The offline counterfactual is RE-MEASURED on committed baseline-3 bytes via the 14.8 `allow_substrate_mismatch` machinery and reported in the PR: how many soft-only convictions the clamp would keep sub-gate, how many hard-backed catches change outcome (the over-damping canary — the contract's hard line is ZERO hard-backed outcome changes), with the baseline-2-era 24/31 vs 6/16 quoted only as the prior hypothesis.
- [ ] The lever is registered, stamped, and its OFF/ON behavior covered by the lever-pattern test suite (registration, stamp, resolver constant-ness at graduation readiness).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone the reporter-exculpation lever end-to-end (resolver + registration + stamp + counterfactual
+ byte-coupled OFF tests — the pattern has now shipped six times); the novelty is only the
classification predicate, which 16.3's decomposition makes a pure function of recorded provenance.
Clamp at render time (the pre-vote surface), never mutate the stored scalar — the fold and its
caps stay untouched, and OFF-path storage is bit-identical by construction.

## Public types this task introduces
- `agents.memory.beliefs.hard_evidence_gate_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Over-damping is the real risk, exactly as it was for the reporter lever: the counterfactual's
zero-hard-backed-changes canary is the contract's hard line, and a marginal result routes to the
16.17 graduation slate as an owner decision, not a silent graduation. Second: the clamp interacts
with `_joint_capped_suspicion` and `CONTRADICTION_RENDER_CEIL` — compose, never bypass; a clamp
applied before the joint cap produces different bytes than after, so pin the ordering by test.

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
Open a PR from branch `phase-16-j1-hard-evidence-gate` with a title like `task 16.4: j1: the hard-evidence render gate (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 J1 (the measured 24/31 vs 6/16 trade — baseline-2-era, re-measure); agents/memory/beliefs.py (the 0.60 gate discipline + REPORTER_EXCULPATION precedent); orchestrator/replay.py:395-431 (_TOGGLEABLE_LEVER_RESOLVERS, currently empty, + _RETIRED_ALWAYS_ON_LEVERS)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
