# Agent Prompt — 4.16 ReplayLog fail-loud on existing file

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.16 — ReplayLog fail-loud on existing file, anchored to DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-replaylog-fail-loud`
**Depends on:** Phase 4 closure (4.15 merged, dev self-audit declared closed 2026-05-27)
**Section refs:** DESIGN.md §11.4
**Complexity:** Small

Phase 5 metric correctness depends on replay-data integrity. Today,
`orchestrator/replay.py::ReplayLog.__init__` accepts any path and
silently appends if the file already exists. This bit the project once:
during Phase 4 UX prep, two tournament runs against the same
`--output-dir` silently concatenated per-seed JSONL files, producing
26-line files that broke the loader's `meeting_by_tick` dedup and made
`AgentMemoryView` requests fail. The data corruption was invisible until
the loader crashed — the worst kind of failure mode for a substrate
that downstream metric work will trust.

This task hardens `ReplayLog` to fail-loud on existing-file and adds
a read-side sanity check that detects the doubled-file pattern. Critical-
path prelude for Phase 5: the eval metrics (5.2–5.5) and prompt
regression suite (5.8) read every replay JSONL in the configured
directory; silently-doubled files would produce silently-wrong metrics.

**Two fail-loud surfaces:**

1. **Write-side: `ReplayLog.__init__` raises on existing target.** If
   `path` already exists, raise `ReplayLog.AlreadyExistsError` (or
   reuse `FileExistsError` — implementing agent picks based on whether
   custom typed exceptions exist elsewhere in `orchestrator/`).
   Override gate: a `force: bool = False` keyword that intentionally
   re-opens the file in truncate mode. The orchestrator's
   `HeadlessGame.run` (which constructs the log) keeps its existing
   signature; callers that want overwrite semantics pass `force=True`
   through `--force` style CLI flags on downstream scripts.

2. **Read-side: `read_all_entries(path)` detects multiple "game start"
   patterns.** A doubled file has TWO sets of `kind="tick"` entries with
   overlapping `tick` values, plus TWO `kind="game_over"` entries (if
   both runs completed). The reader walks the JSONL once and raises
   `ReplayLog.CorruptedFileError` (or sibling type) if it sees either
   pattern. The error message names the file path and the conflicting
   tick value.

**Out of scope** (explicit decisions deferred):

- **Comprehensive read-side hardening** (corrupted JSON, missing
  required field, partial-write mid-line detection). The doubled-file
  case is the lived incident; broader corruption hardening can be
  incremental (caught when Pydantic validation fires today). If a
  future incident proves otherwise, file a follow-up.
- **State-hash mismatch detection.** Already handled in
  `api/replay_loader.py:_assert_hash` via the engine-playback
  reconstruction (Task 4.2). Not a `ReplayLog` concern.
- **Replay format versioning.** Carried in the Phase 5 carryover
  list; folded into Task 5.1 (Eval report schema). Don't add a
  format version field in this task.

**Files in scope:**
- orchestrator/replay.py
- orchestrator/game.py (only if `HeadlessGame.run` passes a `force` flag to `ReplayLog`; otherwise untouched)
- scripts/run_tournament.py (add `--force` flag if it currently overwrites silently)
- tests/orchestrator/test_replay.py (or test_replay_fail_loud.py if a new file is cleaner)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- replays/samples/ (samples are read-only test fixtures; do not regenerate or modify)
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/api/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`ReplayLog.__init__` raises on existing file.** New behavior: if `path.exists()` and `force=False`, raise an exception (`ReplayLog.AlreadyExistsError` or `FileExistsError`) with a message naming the path. Default `force=False`. Caller may opt in via `force=True`.
- [ ] **`scripts/run_tournament.py` exposes `--force`** that propagates to `ReplayLog` construction. Without `--force`, attempting to re-use an existing `--output-dir` with overlapping seeds raises and exits non-zero. With `--force`, the script truncates each conflicting file before writing.
- [ ] **Read-side doubled-file detection.** `read_all_entries(path)` (or a sibling helper) walks the JSONL and raises `ReplayLog.CorruptedFileError` if (a) two or more `kind="tick"` entries share the same `tick` value, OR (b) two or more `kind="game_over"` entries exist. The error message names the file path and the duplicate tick number (or game_over count).
- [ ] **Unit tests cover both surfaces.** Write-side: construct a `ReplayLog`, write one tick, construct a second `ReplayLog` to the same path with `force=False`, assert raises. Construct a third with `force=True`, assert succeeds and previous content is gone. Read-side: hand-craft a JSONL with two overlapping `tick=0` entries; assert `read_all_entries` raises with the duplicate tick mentioned in the message. Also: a hand-crafted file with two `game_over` entries; assert raises.
- [ ] **No regression on existing replay reads.** All 50 samples at `replays/samples/` still load cleanly via `api.replay_loader.ReplayLoader.load_replay`. Smoke: `for s in $(seq 0 49); do uv run python -c "from api.replay_loader import ReplayLoader; from pathlib import Path; ReplayLoader(Path('replays/samples')).load_replay(f'headless-seed-{$s}')" || echo "FAIL $s"; done` produces zero FAIL lines. Capture in `## Decisions`.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (new tests included).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `orchestrator.replay.ReplayLog.AlreadyExistsError`
- `orchestrator.replay.ReplayLog.CorruptedFileError`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-4-replaylog-fail-loud` with a title like `task 4.16: replaylog fail-loud on existing file`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
