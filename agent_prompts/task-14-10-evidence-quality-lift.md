# Agent Prompt — 14.10 Evidence-quality lift fix: close the 10.1 railroad-cap bypass (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.10 — Evidence-quality lift fix: close the 10.1 railroad-cap bypass (default-OFF lever), anchored to tests/meetings/test_manager.py (the downgraded railroad tripwire + the pinned 5-row known set); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the 14.8 fix spec: the exact cap-bypass mechanism); agents/memory/beliefs.py (the Phase-10.1 same-meeting lift cap); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-evidence-quality-lift`
**Depends on:** 14.8, 14.9
**Section refs:** tests/meetings/test_manager.py (the downgraded railroad tripwire + the pinned 5-row known set); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the 14.8 fix spec: the exact cap-bypass mechanism); agents/memory/beliefs.py (the Phase-10.1 same-meeting lift cap); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses)
**Complexity:** Integration

Fix the crew-railroad defect baseline 1 exposed: the new model's ~4× contradiction-flag density (702 vs the
9B's 173 set-wide) DEFEATS the Phase-10.1 same-meeting lift cap — 5 crew rows rendered at certain-guilt 1.0
from 2–9 stacked same-meeting flags and 3 innocents were ejected. Using 14.8's diagnosis of the exact bypass
mechanism, change the belief fold so that NO count of same-meeting contradiction flags can drive a crew
render to 1.0 by stacking alone — bound the aggregate same-meeting contradiction lift (and, where 14.8's spec
supports it, weight flags by evidence class: a self-inconsistency or third-party-refuted alibi is worth more
than a proximity grumble — so evidence QUALITY, not flag COUNT, moves suspicion). The change alters belief
re-derivation, so committed baseline-1 replays would no longer reconstruct byte-identically under it — gate it
behind a NEW default-OFF env lever (the proven 13.5 pattern): OFF preserves baseline-1 byte-identity and every
committed-bytes test; 14.12 records baseline 2 with it ON and stamps it. Register the lever in the
`substrate_flag_snapshot()` stamp machinery (kept generic by 14.9) so the recording self-describes.

**Files in scope:**
- agents/memory/beliefs.py (the aggregate same-meeting lift bound + optional evidence-class weighting, behind the new `*_enabled()` resolver; the 10.1 cap logic is corrected, not bypassed)
- orchestrator/replay.py (register the new lever key in `SUBSTRATE_FLAG_KEYS` / `substrate_flag_snapshot()` so 14.12's recording stamps it — additive)
- .env.example (document the new default-OFF lever)
- tests/agents/test_beliefs.py (unit tests: a synthetic 9-flag same-meeting stack renders BELOW certain-guilt with the lever ON; byte-identity of the fold with it OFF; evidence-class weighting cases if implemented)
- tests/orchestrator/test_replay.py (the stamp round-trips the new lever)

**Files NOT in scope:**
- replays/samples/ (baseline 1 is untouched; the lever defaults OFF so it still byte-verifies — the re-record is 14.12)
- tests/meetings/test_manager.py (the railroad regression pin walks baseline-1 bytes and stays green as-is; RESTORING it to a tripwire happens at 14.12 when the bytes change)
- agents/strategic/prompts/ (the prompt-side fuel fix is 14.11)
- meetings/transcript.py detector logic (flags are still DETECTED the same; this task changes how the belief fold WEIGHS them)

**Definition of done:**
- [ ] With the lever ON, no crew render can reach 1.0 from same-meeting contradiction flags alone: the aggregate same-meeting contradiction lift is bounded per 14.8's spec, demonstrated by a unit test stacking ≥9 synthetic same-meeting flags (the seed-44 worst case) that renders below certain-guilt.
- [ ] With the lever OFF (the default), the belief fold is byte-identical to pre-task behavior: committed baseline-1 reconstructs byte-identically and every committed-bytes test stays green unmodified.
- [ ] If 14.8's spec includes evidence-class weighting, flags are weighted by class (self-inconsistency / third-party-refuted / proximity) with tests per class; if deferred, the audit records why.
- [ ] The new lever is registered in `substrate_flag_snapshot()` / `SUBSTRATE_FLAG_KEYS` and round-trips through the replay stamp + MANIFEST `flags` cell (so the 14.12 recording self-describes).
- [ ] `.env.example` documents the lever as default-OFF pending the 14.12 baseline-2 re-record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Start from 14.8's diagnosis, not from scratch — the audit names the exact mechanism by which ≥2 same-meeting
flags defeat the 10.1 cap (the pinned rows in `tests/meetings/test_manager.py` are the reproduction corpus:
seed-44 m1 p-1 with 9 flags is the worst case). The 13.5 lever pattern is the template for the gate: a module
constant `ENV_EVIDENCE_QUALITY_LIFT` + an `evidence_quality_lift_enabled()` resolver read ad-hoc from
`os.environ`, OFF branch byte-identical. The likely fix shape: the 10.1 cap bounds the lift PER FLAG (or per
detector kind) and stacking distinct flags each contributes — replace with an aggregate per-(meeting, subject)
contradiction-lift budget of one strong flag's worth (0.3), optionally allocated by evidence class. Re-run the
railroad walk from `test_manager.py` locally with the lever ON over baseline-1 bytes to confirm all 5 pinned
rows fall below 1.0 — that offline re-derivation is the cheapest proof the fix lands before 14.12 spends.

## Public types this task introduces
- `agents.memory.beliefs.evidence_quality_lift_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is a belief-fold change on the exact code path 13.5/14.9 just reshaped — the OFF-branch byte-identity
bullet is the guard against regressing the committed baseline; run `scripts/verify_samples.sh` (bare env)
before and after. Do NOT weaken the §4.6 vote gate or the detectors to make the numbers move — the fix is in
the FOLD's weighting, so genuine multi-witness evidence must still convict (the seed-44 m0 TRUE-impostor
catch, driven by real cross-referencing, must still convert with the lever ON; add it as a fixture if cheap).
Over-damping is the failure mode to watch: if the lever ON drops genuine-class conversion materially in the
14.12 smoke, the bound is too tight — iterate the weighting, do not ship a crew that can't convict.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Open a PR from branch `phase-14-evidence-quality-lift` with a title like `task 14.10: evidence-quality lift fix: close the 10.1 railroad-cap bypass (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tests/meetings/test_manager.py (the downgraded railroad tripwire + the pinned 5-row known set); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the 14.8 fix spec: the exact cap-bypass mechanism); agents/memory/beliefs.py (the Phase-10.1 same-meeting lift cap); tasks/phase-13-5.md (the default-OFF-lever + stamp pattern this task reuses)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
