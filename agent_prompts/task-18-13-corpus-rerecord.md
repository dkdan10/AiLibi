# Agent Prompt — 18.13 The corpus re-record at baseline 6 (operator ~18–20h, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.13 — The corpus re-record at baseline 6 (operator ~18–20h, $0), anchored to scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-corpus-rerecord`
**Depends on:** 18.12
**Section refs:** scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges)
**Complexity:** Integration

The long pole, re-run at the adopted layer: 150-game 9p2i + 50-game 4p1i, seeds 1000+, the
same `seed % 5` split rule, freeze-path staging, MANIFEST provenance exact. Duration
honesty: baseline-5 ran ~14–15 h and the roll-call round adds ~36% meeting calls — plan
**~18–20 h** with checkpoint-push (commit-and-push completed seed ranges so a container
reclaim never loses a leg). The README refreshes end-to-end; the Q3 canary-denominator
restoration re-states (the corpus is again canonical from this record; the 18.12 samples are
the continuity anchor).

**Files in scope:**
- replays/ml_corpus/9p2i/ + replays/ml_corpus/4p1i/ (the re-recorded bytes + MANIFESTs + splits.json)
- replays/ml_corpus/README.md (full substrate refresh)
- scripts/record_ml_corpus.sh (the substrate pin flip + duration note)
- tests/training/test_bakeoff_harness.py (corpus-derived re-pins ONLY — the constant flips are 18.14's)
- tests/training/test_surrogate_runner.py (corpus-derived re-pins ONLY — the re-fit is 18.14's)
- tests/training/test_crew_options.py (corpus-derived re-pins ONLY)
- tests/training/test_goodhart_probe.py (corpus-derived re-pins ONLY)
- tests/scripts/test_record_ml_corpus.py

**Files NOT in scope:**
- replays/samples/ (18.12's record — pinned)
- training/ (18.14/18.15 consume)

**Definition of done:**
- [ ] Both corpus sets recorded at baseline 6, validity gate PASS with exact provenance (model, versions, the ruled substrate flags, $0), byte-identical reconstruction, splits regenerated non-degenerate under the same rule.
- [ ] The README and the recorder script agree on every operative line (substrate, env, duration), the Q3 restoration is stated, and the conversion/deception-instrument reads over the new corpus are quoted in the PR.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.9 runbook verbatim plus the checkpoint-push discipline (an ~20 h session WILL span
reclaim risk). 4p1i first, then the 9p2i long leg sharded across 2 staggered workers with
jittered backoff and `AILIBI_SEED_MAX_ATTEMPTS=8`.

## Integration risk

The mixed-date MANIFEST precedent applies across a multi-day session. Corpus-pinned
training tests move; re-pin only what this record moves and leave the bar/surrogate
constants to 18.14 (the 17.9/17.11 split, kept).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`

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
Open a PR from branch `phase-18-corpus-rerecord` with a title like `task 18.13: the corpus re-record at baseline 6 (operator ~18–20h, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing scripts/record_ml_corpus.sh (the pin block moves to the baseline-6 substrate); replays/ml_corpus/README.md; tasks/phase-17.md 17.9 (the runbook this reprises); audits/audit-phase-17-close.md §5 (the staleness rule this discharges)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
