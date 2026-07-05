# Agent Prompt — 15.8 The ML-calibration corpus: record, validate, freeze (operator-run, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.8 — The ML-calibration corpus: record, validate, freeze (operator-run, $0), anchored to audits/post-phase-14-ML-training-signal.md §5.6, §7.2 (the frozen-corpus doctrine + the data gap: 118 committed 9p2i ejections is thin); audits/audit-phase-14-close.md (the baseline-2 recording recipe: 2 seed workers, ~3.85h/100 games); scripts/refresh_samples.sh (the recording pattern to compose); api/replay_loader.py + api/main.py (set-discovery semantics the layout must not collide with). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-ml-corpus`
**Depends on:** 15.1, 15.4
**Section refs:** audits/post-phase-14-ML-training-signal.md §5.6, §7.2 (the frozen-corpus doctrine + the data gap: 118 committed 9p2i ejections is thin); audits/audit-phase-14-close.md (the baseline-2 recording recipe: 2 seed workers, ~3.85h/100 games); scripts/refresh_samples.sh (the recording pattern to compose); api/replay_loader.py + api/main.py (set-discovery semantics the layout must not collide with)
**Complexity:** Medium

Record the frozen training/calibration corpus the surrogate and the bake-off consume, at EXACT baseline-2
config (`Qwen/Qwen3-32B` Featherless non-thinking `fail_loud` `json_object`, prompt set `qwen3_32b.v4`, all
five levers ON, $0 flat-rate): **9p2i × 150 seeds (1000–1149)** primary and **4p1i × 50 seeds (1000–1049)**
secondary — fresh seed ranges so a corpus game can never be confused with the canonical 0–49 sets
(~3× the committed 9p2i meeting/ejection data, ~7h wall with 2 Featherless seed workers). Layout:
`replays/ml_corpus/9p2i/` + `replays/ml_corpus/4p1i/`, each carrying `replay-seed-*.jsonl`, `MANIFEST.md`
(with the 15.4 policy column stamping the FSM default), `roster.json` where applicable,
`tournament-eval-report.json` (the roles ground truth), and a committed by-game `splits.json`
(train/val/test — data only; the loader is 15.6's). The two-level nesting is LOAD-BEARING: a set directory
placed directly under `replays/` would make the API's directory resolution treat `./replays` as the active
parent and SHADOW the canonical samples — a discovery non-collision test pins that `replays/ml_corpus/` is
invisible to default spectator resolution while an operator can still opt-in serve it explicitly. Freeze =
MANIFEST records git_sha + an explicit FROZEN line; acceptance = the 15.1 validity gate + byte-verification,
run per set before the PR merges.

**Files in scope:**
- scripts/record_ml_corpus.sh (new: thin wrapper composing scripts/run_tournament.py — contiguous seed ranges, per-seed crash-retry, MANIFEST + report + splits emission)
- replays/ml_corpus/9p2i/ (new artifact set)
- replays/ml_corpus/4p1i/ (new artifact set)
- tests/scripts/test_record_ml_corpus.py (new: dry-run/arg/splits-emission tests, no network)
- tests/api/test_set_discovery_ml_corpus.py (new: spectator discovery non-collision pinned)

**Files NOT in scope:**
- replays/samples/ (the canonical baseline is untouched — the corpus is a SEPARATE release artifact)
- scripts/refresh_samples.sh (frozen; the new wrapper composes the same underlying tooling, never edits it)
- api/replay_loader.py + api/main.py (discovery semantics are pinned by test, not changed)
- training/ (no Python here — the corpus must be recordable before 15.3/15.6 land)

**Definition of done:**
- [ ] Both corpus sets recorded at exact baseline-2 config; `scripts/validity_gate.py` PASSES on each corpus dir, and the state-hash chains byte-verify via the `_verify_samples.py` machinery pointed at the corpus.
- [ ] Every corpus replay carries the substrate flags AND the 15.4 FSM-default policy stamp; MANIFEST rows carry seed/model/prompt_versions/flags/git_sha/cost ($0)/winner plus the policy column, and the FROZEN line names the git_sha.
- [ ] `splits.json` per set: a documented deterministic by-game split (train/val/test) committed as data; no game appears in two splits (asserted by a test reading the file).
- [ ] Corpus stats reported in the PR description from the gate/measure CLIs: game count, meeting/ejection/skip counts (expect roughly 3× the committed 9p2i 142/118/24), win split — measured, not estimated.
- [ ] The discovery test proves default spectator/API resolution ignores `replays/ml_corpus/` and that explicit opt-in serving of a corpus set still works.
- [ ] The recording script supports `--dry-run` (prints the plan, no network) and per-seed crash-retry; both covered by tests with no network access.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Compose, don't fork: `scripts/run_tournament.py --num-games … --output-dir …` with the roster env/args per
set is the underlying recorder (the same one `refresh_samples.sh` drives); clone refresh_samples' worker
queue + crash-retry shape for the 2-worker Featherless saturation and its MANIFEST/report emission
patterns via `scripts/_manifest_writer.py` + `scripts/build_sample_report.py`. Hosted models do not
byte-reproduce FRESH generation — recordings replay byte-identically (the loosened contract baseline 2
already carries); the validity gate + byte-verify is the acceptance, not generation-replay equality.
Operator gate: requires `FEATHERLESS_API_KEY`; ~7h wall; commit is one atomic PR after the gate passes. A
deterministic split rule (e.g. seed mod 5 → {0,1,2}=train, {3}=val, {4}=test) documented in the MANIFEST
keeps the split auditable from the file alone.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import eval.validity"`

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
Open a PR from branch `phase-15-ml-corpus` with a title like `task 15.8: the ml-calibration corpus: record, validate, freeze (operator-run, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §5.6, §7.2 (the frozen-corpus doctrine + the data gap: 118 committed 9p2i ejections is thin); audits/audit-phase-14-close.md (the baseline-2 recording recipe: 2 seed workers, ~3.85h/100 games); scripts/refresh_samples.sh (the recording pattern to compose); api/replay_loader.py + api/main.py (set-discovery semantics the layout must not collide with)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
