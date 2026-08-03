# Agent Prompt — 8.18 Wave re-record of BOTH sets + validity gate v3

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.18 — Wave re-record of BOTH sets + validity gate v3, anchored to DESIGN.md §11.4, §3.5; audits/audit-2026-06-06-0632-gameplay-data.md (the repair set + §12). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-wave875-rerecord`
**Depends on:** 8.14, 8.15, 8.16, 8.17
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-06-0632-gameplay-data.md (the repair set + §12)
**Complexity:** Integration

The wave gate, mirroring Task 8.12's shape: with the four repairs merged, re-record BOTH committed
sets in ONE PR (the cooldown re-seed is a byte-breaker for every game; the vote_ballot/v4 bump
re-points prompt provenance), regenerate both `tournament-eval-report.json` (format v2 with the 8.17
fields now populated), both `MANIFEST.md`, and the prompt-regression fixtures + `baseline.json`.
Re-enable the 8.14-skipped recon tests last. The re-record itself is an operator step
(`refresh_samples.sh` on local Ollama, $0); this contract is the source-side pins + the gate.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; report v2 with the new accounting fields)
- replays/samples/9p2i/ (50 replays + roster.json {9,2,2} + report + MANIFEST re-recorded)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated at vote_ballot/v4)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (re-enable the 8.14 skips; byte-identical green)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed-bytes pins: git_sha, vote_ballot/v4, cost 0)

**Files NOT in scope:**
- engine/, meetings/, agents/, observation/, eval/ source (all behavior landed in 8.14–8.17; this task records + regenerates, it does not change logic)
- audits/workflows/extract_gameplay_facts.py (run it read-only for the funnel numbers; do not modify it)

**Definition of done:**
- [ ] Both committed sets are re-recorded in ONE PR; both reports regenerate at format v2 with kill_gifted/instances fields populated; both MANIFESTs carry the new git_sha + vote_ballot/v4; prompt-regression fixtures + baseline.json regenerated.
- [ ] The 8.14 recon skips are re-enabled and green (byte-identical via the per-set loader); `_verify_samples` + `build_sample_report --check` are consistent on both sets.
- [ ] **Validity gate v3 (HARD):** friendly-fire kills == 0; every game reaches `game_over`; impostor betrayal ballots/accusations == 0; the leak suite passes at 4p/1i and 2-of-9; the Stage-A floor holds at 9p/2i (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings); AND the repair assertions: zero tick-1 kills, zero "(missed deadline" markers in any transcript, zero dangling `primary_reason_id`s across both sets.
- [ ] Funnel report ($0): run `audits/workflows/extract_gameplay_facts.py` over the new 9p/2i set and report in the PR body: win split + kill-gifted split, ejection count, accusation precision, accuser follow-through, persuasion rate. The extractor emits the RAW counts (win split, ejections, accusations by target role, ballot_follows_chain); the derived rates — precision, follow-through, persuasion — are operator-computed from the facts JSON aggregates (a few lines of python over the facts file, not a single command). Reported, not gated — these are the Wave-1 control-arm anchors.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Operator-run local session like 8.12: Ollama up, the model pulled, and AILIBI_LLM_PROVIDER=ollama on
EVERY refresh invocation (it defaults to anthropic). Smoke a few seeds before each full 50 —
per-seed wall time changes (deadline-free meetings may run longer per call but lose nothing to
defaults). The 9p/2i env block is documented at the top of scripts/refresh_samples.sh. Expect the
win split to MOVE (no spawn kill means fewer early parities; the kill-gifted split contextualizes
the crew rate). Re-enable the recon tests only after the bytes are on disk. One atomic PR — an
intermediate commit is un-reconstructable.

## Integration risk

The wave converges here; the validity gate is a HARD stop — if any repair assertion fails (a tick-1
kill, a missed-deadline marker, a dangling reason id), STOP and fix the upstream task rather than
papering the gate. The flat-4p/1i descriptor-less identity must hold or the determinism reference
silently reseeds wrong.

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
Open a PR from branch `phase-8-wave875-rerecord` with a title like `task 8.18: wave re-record of both sets + validity gate v3`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4, §3.5; audits/audit-2026-06-06-0632-gameplay-data.md (the repair set + §12)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
