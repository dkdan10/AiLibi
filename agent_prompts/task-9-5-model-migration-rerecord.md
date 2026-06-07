# Agent Prompt — 9.5 Migration re-record of BOTH sets on qwen3.5:9b + gate (PHASE PAUSES AFTER)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.5 — Migration re-record of BOTH sets on qwen3.5:9b + gate (PHASE PAUSES AFTER), anchored to DESIGN.md §11.4, §3.5; audits/audit-2026-06-07-0717-gameplay-data.md (the migration + hygiene set). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-model-migration-rerecord`
**Depends on:** 9.1, 9.2, 9.3, 9.4
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-07-0717-gameplay-data.md (the migration + hygiene set)
**Complexity:** Integration

The Wave-0 gate, mirroring 8.18's operator shape: with the three hygiene fixes and the client
migration merged, smoke first, then re-record BOTH committed sets on `qwen3.5:9b` (think:false) in
ONE PR, regenerate both reports + MANIFESTs + the prompt-regression fixtures and baseline, and run
the validity gate. This establishes the NEW control baseline. The phase pauses at this merge: the
close audit and the conversion-wave worksheet re-answer happen in the design thread before any 9.6+
contract exists.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded on qwen3.5:9b; model rows update)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster {9,2,2} unchanged)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated — the model changed, so the recorded fixtures must)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (committed-set pins re-verified on the new bytes; re-scope any zero-denominator runtime skips exactly as 8.18 did)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed-bytes pins: git_sha, model rows `qwen3.5:9b`, cost 0)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/, eval/ source (all behavior landed in 9.1–9.4; this task records + regenerates)
- audits/workflows/extract_gameplay_facts.py (run read-only for the funnel numbers; do not modify)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p/2i): the think:false guard holds on live calls (zero thinking content), per-seed wall time measured and the full-run projection reported BEFORE the full runs; STOP for operator go. If the smoke surfaces ANY thinking-guard trip (Ollama version predates the `think` parameter, or the flag is not honored), ABANDON this task without recording further: re-open 9.4 (or escalate the Ollama-version/model question to the design thread) — do not proceed to a full record, and do not weaken the guard.
- [ ] Both sets re-recorded in ONE PR on `qwen3.5:9b`; both reports regenerated (format v2; kill_gifted under the 9.1 definition); both MANIFESTs carry the new git_sha + `qwen3.5:9b` model rows; prompt-regression fixtures + baseline regenerated.
- [ ] Validity gate (HARD, the v3 set): friendly-fire 0; every game reaches game_over; betrayal ballots/accusations 0 — now structurally absent at the source per 9.3; leak suite green at 4p/1i and 2-of-9; meeting_rate ≥ 0.60 with ≥ 30 resolved meetings at 9p/2i; byte-identical reconstruction; zero tick-1 kills; zero missed-deadline markers; zero dangling primary_reason_id; PLUS migration assertions: zero thinking-guard trips, zero cross-room kill rejections (the 9.2 fix holding), model rows correct.
- [ ] Funnel report ($0): run audits/workflows/extract_gameplay_facts.py over the new 9p/2i set; PR body reports win split + kill-gifted split (9.1 definition), ejection count, accusation precision, accuser follow-through, persuasion rate, and the threshold-quoting-skip count (the 19/19 inversion class — the migration's headline question). The extractor does NOT compute the threshold-quoting count: derive it operator-inline (a regex over ballot `rationale_text` in the raw replay meeting records — the facts JSON does not carry rationales), and paste the derivation snippet into the PR body so the next migration reuses it instead of rediscovering the gap. Reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Operator-run local session: `ollama pull qwen3.5:9b` first; AILIBI_LLM_PROVIDER=ollama on every
refresh invocation (still defaults to anthropic); the model name now comes from 9.4's constant —
no model env needed. Expect roughly 2× per-token cost vs the 7B — the smoke's projection decides
whether the full run is an evening or a day. Win split is reported only and may move in ANY
direction (9.2 raises real kill cadence; the model change moves everything else) — the
threshold-inversion count is the number that decides what Wave 1 still needs to fix. One atomic
PR; an intermediate commit is un-reconstructable.

## Integration risk

The wave converges here and the phase PAUSES at this merge — do not author, dispatch, or implement
any conversion-wave work in this task. If the thinking guard trips or the floor fails, STOP and fix
upstream (9.4 or the model choice) rather than papering the gate.

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
Open a PR from branch `phase-9-model-migration-rerecord` with a title like `task 9.5: migration re-record of both sets on qwen3.5:9b + gate (phase pauses after)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4, §3.5; audits/audit-2026-06-07-0717-gameplay-data.md (the migration + hygiene set)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
