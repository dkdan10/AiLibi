# Agent Prompt — 10.6 Wave-1 instrument integrity and gate spec

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.6 — Wave-1 instrument integrity and gate spec, anchored to DESIGN.md §5.4, §6.3; audits/audit-2026-06-11-2218-gameplay-data.md gp-1 (C-C-5, C-C-4), C-C-3, gp-5 (H-H-1, H-H-2), gp-6 (H-H-4), gp-7 (C-C-6). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-instrument-integrity`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §5.4, §6.3; audits/audit-2026-06-11-2218-gameplay-data.md gp-1 (C-C-5, C-C-4), C-C-3, gp-5 (H-H-1, H-H-2), gp-6 (H-H-4), gp-7 (C-C-6)
**Complexity:** Integration

The Wave-0 close audit found the honest instrument has two remaining detector cracks, one
rule-credulity hole, and a fail-soft gap — all offline-repairable against committed bytes, no
re-record. This task closes them and ships the Wave-1 A/B gate metrics, then re-derives the
corrected W0 baseline that 10.9 measures against. True-positive load was measured before
removal per doctrine: all 22 placeholder-leak flags were false positives on one innocent
(zero TP loss), and the proxy-alibi repair is the TP-preserving option (b) by owner decision.

**Files in scope:**
- meetings/transcript.py (placeholder fix as a frozen canonical-room ALLOWLIST — a data constant of the map's canonical rooms; any claim room whose canonical form is not in the set is non-spatial and mints NO flag and NO corroboration, replacing the placeholder-label denylist, with a test asserting the allowlist equals the engine map's room set so a future map change re-triggers review; proxy-alibi subject-account-consistency — when alibi.speaker differs from subject AND the subject's own claims this meeting are consistent with the conflicting sighting, suppress the flag against the subject and mint a re-targeted WEAK flag against the proxy speaker, new weak-reason constant, no ContradictionRef schema change; the subject-account lookup MUST run on canonical claims BEFORE echo-dedup discards the subject's copy, else the subject's own account is invisible exactly when the proxy spoke first; Rule-3 relevance predicate — a supporting sighting corroborates ONLY if outside the spawn window, tick 2 or later, AND not a kill-scene sighting placing the subject in the meeting's triggering-body room within the corroborated alibi window; the predicate is a named pure function because 10.7 reuses it for accusation-side observation backing)
- agents/memory/beliefs.py (apply the relevance gate at the Rule-3 ingestion seam so claim-stated and detector-derived corroborations both pass through it; no constant changes)
- meetings/manager.py (retry feedback — the single opening retry prompt states the failure reason, naming the dropped dead target and demanding a LIVING target or unsure; unsure-degrade — a twice-failed opening records as an unsure opening with no accusation instead of a full default, so opt-ins and votes still run; telemetry distinguishes cap-default vs validation-degrade; bound the quoted-original in INVALID_ALIBI_SUBJECT_MARKER and sibling markers to 60 chars plus ellipsis)
- eval/vote_correctness.py + eval/meeting_quality.py + scripts/build_sample_report.py (gp-7: multi_signal_conversion — an impostor ejection counts when its rendered pre-vote lift decomposes into 2+ distinct design channels over the quantized rule lattice: contradiction-flag, body-proximity, vent-witness, prior-meeting carry; supply gauges: zero-contradiction meeting share, genuine-subject share, over-gate listeners per accused-impostor meeting, flag-subject role split; the published report labels win split non-gate)
- tests/meetings/test_transcript.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py + tests/eval/* (the pins below; offline against committed bytes)

**Files NOT in scope:**
- agents/strategic/prompts/** (§4.6 render frozen; 10.8 owns the emergency opening branch)
- the 9.8 accumulator constants (frozen)
- replays/samples/** (no re-record; committed tournament-eval-report.json is NOT regenerated — the corrected baseline lives in the PR body + a tests/fixtures JSON, keeping the committed sample dir single-era)
- meetings/manager.py fold/vote phases beyond the items named (10.7 owns the fold restructure)

**Definition of done:**
- [ ] Allowlist pins: seed 13 m1 mints 0 flags from VARYING_ROOMS (currently 22); seed 6 m1 HALLS mints 0; the canonical-set-equals-map test exists; no genuine CANON flag is lost (re-derive and compare the genuine supply before/after — expected unchanged).
- [ ] Proxy pins: seed 28 m1 has NO strong flag on p-9 and a weak re-target on p-7, with p-9's re-derived max below 0.60; seed 24 m0's strong flag on p-4 SURVIVES (the subject echoed the false alibi — no suppression). Both walked offline against committed bytes.
- [ ] Relevance-gate pins: seed 6 m1 — the accuser's ADMIN tick-16 sighting produces NO corroboration for p-6, and p-6's re-derived cross-meeting trajectory rises instead of rendering flat; spawn-window-sourced corroborations count 0 set-wide; total re-derived Rule-3 events remain above 0 (the channel is gated, not killed).
- [ ] Fail-soft pins: a guard-emptied opening's retry prompt contains the failure reason; a twice-failed opening records as unsure (no accusation) and the meeting still reaches opt-ins and ballots; a 3499-char invalid subject yields a bounded marker (unit test); telemetry splits cap-default vs validation-degrade.
- [ ] gp-7 pins: the 5 W0 impostor ejections decompose exactly as the audit found — seeds 8, 11, 26, 39 multi-signal and seed 24 flag-only; the gauges publish in the report builder.
- [ ] CORRECTED W0 BASELINE: re-run the 10.4 re-deriver + the new metrics over the committed W0 bytes; record the corrected table (total flags, weak/strong split, genuine supply + conversion, multi-signal conversion, gauge values) in the PR body and pin it at `tests/fixtures/phase10/corrected_w0_baseline.json` — the exact file 10.9 reads as its A/B baseline (one home: the fixture is the artifact, the PR-body copy is narrative).
- [ ] Determinism: detector, predicate, and metrics are pure; re-runs are byte-identical.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

One-home discipline throughout: the allowlist, the relevance predicate, and the proxy
consistency check live in meetings/transcript.py beside the existing classifier; beliefs.py
and eval consume them by import, never re-derive. The audit extractor
(audits/workflows/extract_gameplay_facts.py) shows the offline replay-walk pattern for every
pin. The echo-dedup ordering item is the subtle one: the seed-24 conviction currently exists
only because the impostor's proxy copy happened to be kept — under option (b) the subject's
own account must be consulted from the pre-dedup claim set so the outcome stops depending on
turn order.

## Public types this task introduces
- `CANONICAL_ROOMS`
- `WEAK_REASON_RETARGETED_PROXY`
- `MultiSignalConversionReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Over-suppression is the failure mode that matters: the W0 lesson is that 100% silence is as
bad as 93% artifacts. The seed-24 survival pin and the Rule-3-events-above-zero pin are the
tripwires. The re-target changes who gets lifted — it can only point at a speaker whose claim
conflicts with both the sighting and the subject's own account, and it lands weak, so it
cannot eject alone. Recording-side only; committed reconstruction unaffected.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-10-instrument-integrity` with a title like `task 10.6: wave-1 instrument integrity and gate spec`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.4, §6.3; audits/audit-2026-06-11-2218-gameplay-data.md gp-1 (C-C-5, C-C-4), C-C-3, gp-5 (H-H-1, H-H-2), gp-6 (H-H-4), gp-7 (C-C-6)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
