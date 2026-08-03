# Agent Prompt — 10.16 Wave-2 metrics and gate spec

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.16 — Wave-2 metrics and gate spec, anchored to DESIGN.md §9, §11; audits/audit-2026-06-13-1816-gameplay-data.md (B-B-2 pacing inversion, D-D-1/D-D-2 toolkit + active-deflection, C-C-1 conversion); experiments/lab/report-deception-battery*.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-wave2-metrics`
**Depends on:** none (eval-only; file-disjoint from the source bundle, dispatchable in parallel)
**Section refs:** DESIGN.md §9, §11; audits/audit-2026-06-13-1816-gameplay-data.md (B-B-2 pacing inversion, D-D-1/D-D-2 toolkit + active-deflection, C-C-1 conversion); experiments/lab/report-deception-battery*.md
**Complexity:** Integration

The gate spec the 10.17 re-record is judged on. The Wave-2 re-record measures TWO adversarial changes
at once (impostor toolkit + crew belief-spread) in one record, so the win split is confounded and is a
GUARDRAIL, not a signal — the gate must read attribution-decomposed conversion + indistinguishability,
not the outcome split. Ships standalone (off the frozen TournamentEvalReport wrapper, exactly like the
gp-7 metrics) until the 10.17 re-record turns the era over; the metric CODE is independent of the
source tasks (it reads whatever the bytes carry — do_task is 0 on W1 bytes, >0 after the toolkit).

**Files in scope:**
- eval/meeting_quality.py (NEW standalone analyzers beside compute_multi_signal_conversion / compute_supply_gauges: (1) conversion_per_meeting = impostor ejections / resolved meetings — the pacing-inversion-proof KPI, since meeting COUNT correlates with impostor wins (B-B-2); (2) effective_deflection — of accused-impostor ACTIVE survivals (the impostor counter-accused), the subcount where plurality actually moved OFF the impostor to a third party or the named target, separating deception SKILL from SKIP-saved survival (audit D-D-2: ~5-9 of 59, NOT raw 27 — the A/B must gate on this subcount); (3) INDISTINGUISHABILITY: impostor vs crew wait-share, do_task emission counts by role, top-idler concentration — the "never-tasks" fingerprint metrics (D-D-1))
- eval/meeting_quality.py decompose_ejection_channels (EXTEND the channel decomposition to credit the 10.15 single-witness INFORM as a DISTINCT channel alongside flag / body-proximity / vent / prior-meeting-carry — this is the confounding-aware attribution that separates the crew lever's conversions from the toolkit's effects in the single combined re-record; an ejection's lift must decompose to a named channel so crew-lever vs toolkit credit is legible)
- eval/ ingest for per-tick action-by-role (the wait-share / do_task-by-role metrics need the tick action stream, which the meeting-only eval model does not currently carry — either extend build_tournament_eval_report's replay walk to tally actions by re-derived role, OR consume the audit extractor's role-tally; the implementer picks and documents the seam — roles re-derived from the seeder, never from behavior)
- scripts/build_sample_report.py (surface the new metrics in the run summary, like the gp-7 companions; the win split stays printed with its NON-GATE label)
- tests/eval/* (pins below)

**Files NOT in scope:**
- the TournamentEvalReport frozen wrapper (new metrics ship standalone until 10.17; no committed-report regen)
- the §4.6 render, the tally, the 9.8 constants (frozen)
- the source bundle (impostor toolkit / crew lever / detector) — this task only MEASURES
- replays/samples/** (no re-record; metrics populate meaningfully at 10.17)

**Definition of done:**
- [ ] conversion_per_meeting computes on the committed W1 bytes (baseline value recorded) and is independent of meeting count.
- [ ] effective_deflection separates the active-deflection-that-moved-plurality subcount from SKIP-saved survivals; on the committed W1 bytes it reproduces the audit's ~5-9 figure (pinned), NOT the raw 27.
- [ ] Indistinguishability: wait-share by role + do_task-by-role + idler concentration compute on the W1 bytes (do_task impostor = 0 today, the baseline the toolkit must move); the action-by-role ingest seam is documented and roles come from the seeder.
- [ ] decompose_ejection_channels gains the INFORM channel; on the W1 bytes (no inform yet) it credits 0 inform conversions and the existing channels are byte-unchanged (the extension is additive); a synthetic inform-driven ejection decomposes to the inform channel.
- [ ] The balance guardrail is DOCUMENTED as a reported band (impostor win rate), explicitly NOT a hard gate; the gate spec text (in the report or a module docstring) states the HARD lines, the Wave-2 directional gates, and the guardrail separately.
- [ ] New metrics surface in the report-builder summary; the committed reports are NOT regenerated; determinism + full `bash scripts/check.sh` pass.

## Implementation hint

Mirror the gp-7 standalone pattern exactly (10.6 shipped MultiSignalConversionReport /
SupplyGaugesReport off the frozen wrapper, surfaced only in the summary + --baseline-out). The
attribution extension reuses decompose_ejection_channels' existing channel logic — add the inform as
a sibling channel keyed on the 10.15 marker. The action-by-role ingest is the one new data path; the
replay loader already walks ticks, so tallying actions by re-derived role is the lighter option.

## Public types this task introduces
- `ConversionPerMeetingReport`
- `EffectiveDeflectionReport`
- `IndistinguishabilityReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The metric code must not depend on the source tasks being merged (it reads the schema; absent fields
read as zero on W1 bytes). The one real seam is the per-tick action ingest — keep it additive and
role-from-seeder. Standalone-off-the-wrapper keeps the committed single-era reports byte-stable.

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
Open a PR from branch `phase-10-wave2-metrics` with a title like `task 10.16: wave-2 metrics and gate spec`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §9, §11; audits/audit-2026-06-13-1816-gameplay-data.md (B-B-2 pacing inversion, D-D-1/D-D-2 toolkit + active-deflection, C-C-1 conversion); experiments/lab/report-deception-battery*.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
