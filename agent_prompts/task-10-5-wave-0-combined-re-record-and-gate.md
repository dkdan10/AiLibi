# Agent Prompt — 10.5 Wave-0 combined re-record and gate

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.5 — Wave-0 combined re-record and gate, anchored to DESIGN.md §11.4, §3.5; audits/audit-2026-06-10-1820-gameplay-data.md (the Wave-0 set). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-wave0-rerecord`
**Depends on:** 9.11, 10.1, 10.2, 10.3, 10.4
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-10-1820-gameplay-data.md (the Wave-0 set)
**Complexity:** Integration

The Wave-0 gate, the 9.5/9.11 operator shape: with the repairs merged, smoke first, then
re-record BOTH committed sets on qwen3.5:9b (think:false) in ONE PR, regenerate both reports +
MANIFESTs + the prompt-regression fixtures and baseline, and run the validity gate plus the
repair-specific assertions. This re-record establishes the HONEST conversion baseline — the
first one whose numbers are not artifact-dominated. The wave pauses at this merge: the design
thread re-runs the close audit and authors the Wave-1 (testimony + pacing) contracts from it.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; git_sha updates per the affirmed convention)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — detector + prompts changed)
- the committed-bytes test pins (prompt-version rows crewmate_report.v5 / impostor_report_v4 / accusation_round.v7, git_sha, model, cost 0; re-scope zero-denominator skips per the 8.18/9.5/9.11 precedent)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 10.1-10.4; this task records + regenerates only). The §4.6 render, tally, accumulator constants, and token caps stay FROZEN.
- audits/workflows/** (the close-audit re-run is the design thread's step after merge)

**Definition of done:**
- [ ] Smoke first (3-5 seeds @ 9p/2i): think:false guard holds; every smoke seed reaches game_over with zero ballot/turn truncation; opening-retry telemetry sane (no retry loops, retries counted); the per-seed wall-time projection ACCOUNTS for the 10.3 opening-retry adding roughly one extra meeting call per validation-failing opening — narration-only OR guard-emptied (the 10.3 validation runs on post-guard claims), ~5-10 per 50 games at baseline — so the full-run estimate does not under-shoot; STOP for operator go (or the documented autonomous-go protocol from 9.11 if unattended).
- [ ] Both sets re-recorded in ONE PR on qwen3.5:9b; reports + MANIFESTs + fixtures regenerated; version rows carry v5/v4/v7.
- [ ] Validity gate (HARD, the standing v3 set): friendly-fire 0; every game reaches game_over; betrayal 0; leak suite green; meeting_rate >= 0.60 with >= 30 resolved meetings; byte-identical reconstruction; zero tick-1 kills; zero dangling primary_reason_id; zero thinking trips; model rows correct.
- [ ] Repair assertions (the Wave-0 additions, reported with numbers): total contradiction volume collapses vs the 83/93%-artifact era (derive the artifact share with the audit extractor offline — compound-label and placeholder classes ~0; the endpoint class survives ONLY as weak-banded flags per the 10.1 weak-band decision, never full-weight); no innocent reaches suspicion 1.0 by flag stacking (the 10.1 per-subject cap is 0.3 — one strong flag's worth); Rule-3 fired count > 0 (the corroboration channel is alive — both the claim-stated and the detector-derived containment paths); CANON_INTERIOR impostor flags present and their conversion reported via 10.4's genuine_class_conversion (NOTE: these flags are weak self-stated by construction — a fabricated alibi is self-stated — so assert presence under 10.4's re-derived definition, not marker-strength); invalid-subject drop markers present where the model hallucinated; lost-opening-accusation count vs the 5-baseline.
- [ ] Conversion re-baseline reported with the explicit framing: these are the first honest numbers; comparisons to 0.629 (artifact era) and 0.476 (mixed era) are provenance-noted, not gates.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Operator-run local session, identical mechanics to 9.11: AILIBI_LLM_PROVIDER=ollama, model from
the client constant, one atomic commit of bytes + reports + fixtures + pins. Expect contradiction
counts to DROP hard — that is the repair working, not a regression; the report framing in the PR
body should lead with the artifact-share collapse and the genuine-class numbers, not the raw
ejection count.

## Integration risk

The wave converges here and PAUSES at this merge for the close-audit re-run — do not author or
implement Wave-1 work (testimony ingestion, emergency meeting) in this task. If the floor fails,
STOP and fix upstream; nothing frozen gets touched to chase a number.

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
Open a PR from branch `phase-10-wave0-rerecord` with a title like `task 10.5: wave-0 combined re-record and gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4, §3.5; audits/audit-2026-06-10-1820-gameplay-data.md (the Wave-0 set)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
