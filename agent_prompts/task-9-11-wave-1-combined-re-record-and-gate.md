# Agent Prompt — 9.11 Wave-1 combined re-record and gate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.11 — Wave-1 combined re-record and gate, anchored to DESIGN.md §11.4, §3.5; audits/audit-2026-06-09-0347-gameplay-data.md (the Wave-1 set). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-wave1-rerecord`
**Depends on:** 9.5, 9.6, 9.7, 9.8, 9.9, 9.10
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-09-0347-gameplay-data.md (the Wave-1 set)
**Complexity:** Integration

The Wave-1 gate, mirroring 9.5's operator shape. With the metric hygiene (9.6) and the four
byte-changers (9.7–9.10) merged, smoke first, then re-record BOTH committed sets on `qwen3.5:9b`
(think:false) in ONE PR, regenerate both reports + MANIFESTs + the prompt-regression fixtures and
baseline, and run the validity gate PLUS the conversion-quality deltas. The phase pauses at this
merge: the design thread re-runs the close audit on the new baseline and authors Phase 10 (impostor
gameplay) from its findings.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; model rows unchanged at qwen3.5:9b, git_sha updates)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — prompts + detector changed)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py + the committed-bytes pins in tests/scripts/* (git_sha, prompt-version rows crewmate_report.v4 / accusation_round.v6, model qwen3.5:9b, cost 0; re-scope any zero-denominator skips as 8.18/9.5 did)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 9.6–9.10; this task records + regenerates only). The §4.6 gate render and balance knobs stay FROZEN.
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel; the close audit re-run is a separate design-thread step)

**Definition of done:**
- [ ] Smoke first (3–5 seeds @ 9p/2i): the think:false guard holds; every smoke seed reaches game_over with zero ballot truncation AND zero TURN truncation now that 9.9's discipline is in (a residual runaway turn → STOP, escalate, do NOT raise the cap); per-seed wall time + full-run projection reported; STOP for operator go.
- [ ] Both sets re-recorded in ONE PR on qwen3.5:9b; both reports regenerated; both MANIFESTs carry the new git_sha + the crewmate_report.v4 / accusation_round.v6 rows; prompt-regression fixtures + baseline regenerated.
- [ ] Validity gate (HARD, the v3 set): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0; leak suite green; meeting_rate >= 0.60 with >= 30 resolved meetings @ 9p/2i; byte-identical reconstruction; zero tick-1 kills; zero dangling primary_reason_id; zero thinking trips; zero cross-room kill rejections; model rows correct.
- [ ] Conversion-quality deltas reported (the 9.6 metrics), each attributed honestly: PRECISION (primarily 9.7) — ejection_accuracy UP from 0.629, wrong_ejections DOWN from 13/35. RECALL (primarily 9.8) — the impostor-accused -> ejected conversion rate UP from 21/47 = 0.45, expecting a SMALL lift in these short games (the accumulator's runway is limited — known, not a failure). missed_skip_ballots is a SENTINEL, not a down-is-good metric: 34 of the 38 are correct firewall coercions that SHOULD persist; only the 4 invalid-target ones drop (via 9.9's living-roster). Plus defaulted-turn count DOWN from 4 (9.9), invalid-accusation-target drops DOWN from 17 (9.9), total_failed_calls the true distinct count (9.10). Reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Operator-run local session, identical mechanics to 9.5: `ollama pull qwen3.5:9b`,
AILIBI_LLM_PROVIDER=ollama on every refresh, model from the 9.4 constant. The conversion deltas are
the headline — read them against the 9.5 baseline (9p2i @ fb3cfa5) and name dir + commit + model in
the comparison. Expect the recall accumulator's effect to be SMALL in these short games; that is
known. One atomic PR; an intermediate commit is un-reconstructable.

## Integration risk

The wave converges here and the phase PAUSES at this merge — do not author or implement Phase 10
work in this task. If the floor fails, STOP and fix upstream rather than papering the gate; the
2048 turn cap stays frozen (9.9 is the turn-verbosity fix).

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
Open a PR from branch `phase-9-wave1-rerecord` with a title like `task 9.11: wave-1 combined re-record and gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4, §3.5; audits/audit-2026-06-09-0347-gameplay-data.md (the Wave-1 set)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
