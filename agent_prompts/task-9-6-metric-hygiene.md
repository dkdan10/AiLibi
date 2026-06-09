# Agent Prompt — 9.6 Metric hygiene

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.6 — Metric hygiene, anchored to DESIGN.md §11.3, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-metric-hygiene`
**Depends on:** none (offline analysis root)
**Section refs:** DESIGN.md §11.3, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-2
**Complexity:** Medium

The audit found the lead conversion metric is a tautology: vote_correctness_rate =
evidence_backed_impostor_ejections / impostor_ejections, and `_has_real_evidence` is satisfied by the
same predicate that classifies an ejection as impostor-backed, so the rate is structurally pinned to
1.0 and measures nothing — a Wave-1 A/B run on it is blind. Fix the ruler BEFORE any conversion
source change records: demote the tautology to a sentinel, publish ejection_accuracy (the PRECISION
lead) and the impostor-accused -> ejected conversion rate (the RECALL lead — Wave 1 changes both, so
name a lead for each), ship the missed-skip SENTINEL, and reframe the inversion count. Offline only — reads the committed
replays, regenerates the offline reports + fixtures, touches no engine/recording path and no
committed bytes. This task BLOCKS the 9.11 A/B and so lands first.

**Files in scope:**
- eval/vote_correctness.py (demote vote_correctness_rate to a documented bug-sentinel: keep it computed but mark it NOT a KPI; surface ejection_accuracy, already computed on VoteCorrectnessReport, as the published lead)
- eval/meeting_quality.py + scripts/build_sample_report.py (ship ejection_accuracy + a new missed_skip_ballots count into tournament-eval-report.json; reframe threshold_inversions as a firewall sentinel on the report surface)
- a new eval/_suspicion_parse.py — the CANONICAL home for the rendered-suspicion parse (the "maximum suspicion among the living ejection targets is" regex), imported by BOTH eval/meeting_quality.py and audits/workflows/extract_gameplay_facts.py (audits -> eval is the allowed consumer direction); do NOT duplicate the regex on either side
- audits/workflows/extract_gameplay_facts.py (swap its inline rendered-suspicion regex for an import of eval/_suspicion_parse.py — the de-dup; the extractor's facts output stays byte-unchanged, a pure refactor; this is the ONLY audits/ edit and is what makes "both sides import" true)
- the missed-skip computation using that shared parse (a SKIP ballot is MISSED when the voter's rendered max-suspicion over a LIVING target was >= 0.60, else CORRECT), AND the recall lead: the impostor-accused -> impostor-ejected conversion rate (impostor ejections / meetings that verbally accused a true impostor, roles re-derived from the seeder — the audit's 21/47 = 0.45; gp-1b's measurable target)
- eval/report_schema.py (CURRENT_FORMAT_VERSION STAYS 2 — the added fields are wrapper-level aggregates older readers ignore, and 9.6 regenerates every report so there is no old-report read; per the §11.4 policy the version bumps only when older readers cannot interpret the shape)
- replays/samples/tournament-eval-report.json + replays/samples/9p2i/tournament-eval-report.json (regenerated offline from the committed replays; bytes + MANIFESTs untouched)
- tests/eval/test_vote_correctness.py + tests/fixtures/prompt_regression/baseline.json + tests/eval/test_prompt_regression.py (pin the new lead + missed_skip; assert vote_correctness_rate is labelled a sentinel; regenerate the baseline)

**Files NOT in scope:**
- engine/, meetings/, agents/, llm/ source (offline metric layer only; no behavior change)
- replays/samples/**/replay-seed-*.jsonl + MANIFESTs (no re-record; reports regenerate from existing bytes)

**Definition of done:**
- [ ] vote_correctness_rate is documented + surfaced as a bug-sentinel (structurally 1.0), not a KPI; a test asserts the semantics so a future reader cannot mistake it for the lead.
- [ ] TWO leads are published: ejection_accuracy (precision: impostor_ejections / total_ejections, denom all ejections) and the impostor-accused -> ejected conversion rate (recall). missed_skip_ballots is shipped as a SENTINEL (count + CORRECT/MISSED partition) — most MISSED are correct firewall coercions, so it is NOT a down-is-good metric; threshold_inversions likewise reads as a firewall sentinel.
- [ ] The 9p/2i report regenerates to the audited values from the committed bytes as a regression pin: ejection_accuracy 22/35 = 0.6286, conversion rate 21/47 = 0.45, missed_skip 38 (34 firewall + 4 invalid-target + 0 genuine). These pin the 9.5 baseline (9p2i @ fb3cfa5) and are NOT immutable — 9.11 updates them in the regenerated baseline.json, the standard re-record pattern.
- [ ] prompt-regression baseline regenerated; the metric-diff demonstration still attributes to one template version; the CI exact-match test holds.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

ejection_accuracy already exists on VoteCorrectnessReport — the work is plumbing it (and missed_skip +
the conversion rate) into the SHIPPED report surface, not recomputing it. The audit extractor already
parses the rendered max-suspicion per SKIP ballot; lift that parse into eval/_suspicion_parse.py and
import it from BOTH sides so they can never drift. Keep the tautology computed (removing it churns the
schema); just relabel it and add the real leads beside it.

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
Open a PR from branch `phase-9-metric-hygiene` with a title like `task 9.6: metric hygiene`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3, §5.5; audits/audit-2026-06-09-0347-gameplay-data.md gp-2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
