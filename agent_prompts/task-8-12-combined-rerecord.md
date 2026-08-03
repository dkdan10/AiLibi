# Agent Prompt — 8.12 Combined re-record of BOTH sets + regenerate reports/manifests/baseline

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.12 — Combined re-record of BOTH sets + regenerate reports/manifests/baseline, anchored to DESIGN.md §11.4; audits/restructure-impact-map-2026-06-04-0223.md §3.1, §4 coupling 3 (the phase gate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-combined-rerecord`
**Depends on:** 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11
**Section refs:** DESIGN.md §11.4; audits/restructure-impact-map-2026-06-04-0223.md §3.1, §4 coupling 3 (the phase gate)
**Complexity:** Integration

The single coordinated re-record — the phase gate. Both byte-breakers (task re-key 8.1, meeting reshape 8.7) and the versioning (8.11) have landed; now re-record BOTH committed sets in ONE PR (never split): the flat **4p/1i** reference (re-recorded, still 4p/1i @ 1 task) and the canonical **9p/2i** set (re-recorded from the old 7p/2i, dir renamed `7p2i/`→`9p2i/`, `roster.json` → `{9,2,2}`). Regenerate both `tournament-eval-report.json` (now v2), both `MANIFEST.md`, and the prompt-regression `baseline.json` — the latter needs its `eval/prompt_regression.py` source edit (roster + meeting) to land with it. Re-enable + green the committed-set reconstruction tests (now 9p/2i) that 8.1/8.7 skipped, and re-run the $0 Ollama eval gate at 9p/2i. The re-record itself is an operator step (`refresh_samples.sh`); this contract is the source edits + the validity gate + the test re-enables.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded + report regenerated to v2)
- replays/samples/9p2i/ (the renamed-from-7p2i set: 50 replay JSONL + roster.json `{9,2,2}` + tournament-eval-report.json + MANIFEST.md) and the `7p2i`→`9p2i` path literals in the loader/tests
- eval/prompt_regression.py (`_seeded_roles` roster thread + `run_prompt_regression` over the new meeting seeds — the source edit that gates the baseline reset)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (RE-ENABLE the committed-set recon cases at 9p/2i; un-skip + green)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed bytes + provenance rows + the 9p/2i routing)

**Files NOT in scope:**
- engine/, meetings/, agents/, observation/ (all behavior landed in 8.1–8.11; this task records + regenerates, it does not change logic)

**Definition of done:**
- [ ] Both committed sets are re-recorded in ONE PR (4p/1i re-recorded; 7p2i→9p2i renamed + re-recorded at `{9,2,2}`); both `tournament-eval-report.json` regenerated to format v2; both `MANIFEST.md` carry the new git_sha + the bumped prompt versions; `baseline.json` + its `v_a`/`v_b` replays regenerated.
- [ ] The committed-set reconstruction tests skipped by 8.1/8.7 are re-enabled and green at 9p/2i (byte-identical reconstruction via the per-set loader); `_verify_samples` + `build_sample_report --check` are consistent.
- [ ] **Validity gate (HARD):** friendly-fire kills == 0; every game reaches `game_over`; the leak suite passes at 4p/1i and 2-of-9; the Stage-A floor holds at 9p/2i (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings); impostor betrayal ballots/accusations == 0. An impostor-favored split is reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Run the re-record via `refresh_samples.sh` at the 9p/2i env (Ollama, $0). Net meeting cost vs the old 7p/2i R=1 baseline is genuinely uncertain — the chain terminates early on convergence (fewer calls) but 9 players means deeper chains + more opt-in candidates — so iterate on a seed-subset smoke first and expect the full 50-seed run to possibly take noticeably longer than the 7p/2i one. The `eval/prompt_regression.py` source edit must land WITH the regenerated `baseline.json` (the source gates the fixture). The `7p2i`→`9p2i` rename cascades to the loader dir constants + ~3 path literals + both MANIFESTs — grep `7p2i`. The 8.3 memory-render goldens hold across the re-record (no behavior change between 8.3 and here), so they need no second regeneration. Re-enable the two committed-recon tests last, after the bytes are on disk. This is the SINGLE combined re-record — do not split the two byte-breakers across PRs (an intermediate commit would have un-reconstructable data).

## Integration risk

The whole phase converges here; it must be one atomic PR. The validity gate is a HARD stop — if friendly-fire ≠ 0, a game lacks `game_over`, reconstruction is not byte-identical, or the meeting floor fails at 9p/2i, STOP and fix upstream rather than papering the gate. The flat-4p/1i identity (descriptor-less default stays 4p/1i @ 1 task) must hold or the determinism reference silently reseeds wrong.

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
Open a PR from branch `phase-8-combined-rerecord` with a title like `task 8.12: combined re-record of both sets + regenerate reports/manifests/baseline`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4; audits/restructure-impact-map-2026-06-04-0223.md §3.1, §4 coupling 3 (the phase gate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
