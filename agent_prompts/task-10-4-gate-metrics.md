# Agent Prompt — 10.4 Gate metrics

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.4 — Gate metrics, anchored to DESIGN.md §11.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-7 (B-B-1, C-C-6, D-D-2, H-H-5, H-H-7). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-gate-metrics`
**Depends on:** 10.1 (the genuine-class definition IMPORTS the repaired detector's classifier — one home, two importers, per the 9.6 shared-parse rule; dispatches in parallel with the roster-validation chain, whose files are disjoint)
**Section refs:** DESIGN.md §11.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-7 (B-B-1, C-C-6, D-D-2, H-H-5, H-H-7)
**Complexity:** Medium

The Phase-10 A/B ruler, offline (reads committed replays; no re-record). The audit specified the
gate surface: win split excluded (constant ~90/10, zero ejection-driven wins); deception metrics
conversion-controlled; progress gated on genuine-class conversion, never on raw
ejection_accuracy parity with the artifact-era 0.63. Ship the missing counters so 10.5 and every
later wave reads them off the report instead of deriving them operator-inline.

**Files in scope:**
- eval/vote_correctness.py + eval/meeting_quality.py + scripts/build_sample_report.py (ship: genuine-class conversion — ejections where a CANON-class strong contradiction named the ejected impostor, with its supplied/converted denominator pair; lost-opening-accusation count — openings carrying zero accusation claims, counted separately from cap-defaults; impostor-survival conditioned on rendered-max < 0.60 — the deception-vs-under-conversion split; the existing leads stay)
- eval/report_schema.py (wrapper-level additions only; CURRENT_FORMAT_VERSION stays 2 per the §11.4 policy unless the inner shape changes)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated offline; bytes + MANIFESTs untouched)
- tests/eval/* + tests/fixtures/prompt_regression/baseline.json (pins on the current committed set: genuine-class 0 converted / 4 supplied; lost-opening 5; defaults 2; conditioned survival n=1 of 45; baseline regenerated)

**Files NOT in scope:**
- engine/, meetings/, agents/ source (offline metric layer only)
- replays/samples/**/replay-seed-*.jsonl + MANIFESTs (no re-record)

**Definition of done:**
- [ ] genuine_class_conversion ships with both numerator and denominator (this set: 0/4) and is documented as the phase's PRIMARY progress gate; the report carries an explicit note that raw ejection_accuracy comparisons against pre-repair eras are invalid (the 0.63 was artifact-built).
- [ ] lost_opening_accusations (5 on this set, seeds 23/39/44/13m0/38m1) ships separately from cap-defaults (2); impostor survival conditioned on rendered < 0.60 ships (n=1/45 here) so Wave-2 deception claims are conversion-controlled from day one.
- [ ] The 9p/2i report regenerates to the audited values as regression pins; these pin the e750b40 set and 10.5 updates them — stated in the test docstrings.
- [ ] prompt-regression baseline regenerated; CI exact-match holds.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The audit extractor (audits/workflows/extract_gameplay_facts.py) already derives every one of
these — port its derivations to the eval layer rather than re-inventing them, reusing
eval/_suspicion_parse.py for anything reading rendered suspicion. CANON-class detection IMPORTS
the 10.1 classification helpers from meetings/transcript.py — never a parallel implementation,
even a temporary one; a drifted copy here poisons every later gate, which is precisely why this
task waits for 10.1.

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
Open a PR from branch `phase-10-gate-metrics` with a title like `task 10.4: gate metrics`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3; audits/audit-2026-06-10-1820-gameplay-data.md gp-7 (B-B-1, C-C-6, D-D-2, H-H-5, H-H-7)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
