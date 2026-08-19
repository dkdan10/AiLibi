# Agent Prompt — 16.14 Baseline 4: the model-only atomic re-record + the champion re-audit (operator-run, $0)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.14 — Baseline 4: the model-only atomic re-record + the champion re-audit (operator-run, $0), anchored to tasks/phase-15.md 15.7 (the atomic re-record runbook this clones); audits/audit-phase-16-model-lock.md (the substrate this records); eval/watchability.py (16.11's re-anchored referee + the per-baseline floors block); training/reports/results-champion-close.jsonl (the stamp-proof row convention the re-audit follows). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-baseline-4`
**Depends on:** 16.3, 16.11, 16.12, 16.13
**Section refs:** tasks/phase-15.md 15.7 (the atomic re-record runbook this clones); audits/audit-phase-16-model-lock.md (the substrate this records); eval/watchability.py (16.11's re-anchored referee + the per-baseline floors block); training/reports/results-champion-close.jsonl (the stamp-proof row convention the re-audit follows)
**Complexity:** Integration

GO-path only. Record **baseline 4** — both canonical sets on the locked model + the `qwen3_6_27b`
v1 set — with the model as the ONLY layer change: every Phase-16 lever merged OFF/inert (the
preflight: the prompt-byte golden green and `verify_samples.sh` bare on the pre-record tree),
mechanics byte-equivalent to baseline 3's. The 15.7 runbook end-to-end: 2 Featherless workers,
per-seed crash-retry, atomic staging, MANIFEST + report + rubric regeneration,
`audits/baseline3-final-measure.json` captured at the pre-replacement tip (the BEFORE column —
baseline 3 survives only in git history after this), the Q5 annotated tag at the recording
commit, README sample-provenance refresh, and the byte-coupled test re-pin sweep. Measurement:
the validity gate (with `--expected-model` flipped to the locked id), the re-anchored referee
(16.11's definition; baseline-4 floors pinned from the new bytes), the funnel, and the canaries
under the DEGRADED-Q3 rule (50-seed sets, two-proportion discipline, UNDERPOWERED recorded
honestly; the corpus quoted as stale context only). Same operator session, second artifact: the
opt-in champion's 50-seed re-audit against the new meeting substrate —
`scripts/run_tournament.py --agent-factory learned-champion` on the audit seeds, measurement
committed as `training/reports/results-champion-qwen36-audit.jsonl` with the stamp-proof rows
(read back from bytes, never echoed), raw recordings uncommitted. The champion was selected under
Qwen3-32B meetings; this is the honest re-reading, NOT a retrain (Phase 17's business), and a
degraded champion result is a FINDING for the close + Phase 17, never a blocker.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-4 set)
- replays/samples/4p1i/ (the baseline-4 set)
- audits/baseline3-final-measure.json (new: the BEFORE column, captured pre-replacement)
- audits/audit-phase-16-baseline-4.md (new: the model-swap measurement — funnel/R-gate/referee/canaries before/after + the champion re-audit reading)
- training/reports/results-champion-qwen36-audit.jsonl (new: the champion re-audit rows, stamp-proven)
- eval/watchability.py (baseline-4 floors in the per-baseline block region — behind 16.11's definition)
- scripts/validity_gate.py + scripts/measure_baseline.py — NOT edited; invoked (listed to declare the negative)
- README.md (sample-provenance paragraph region)
- tests/ (the byte-coupled re-pin sweep: manifest rows, committed-report aggregates, transcript pins — the 15.7 list plus whatever the sweep finds)

**Files NOT in scope:**
- replays/ml_corpus/ (stale by design after this record — Phase 17 re-grounds; the close audit re-states it)
- agents/ + meetings/ + engine/ (zero mechanics — the preflight proves it)
- agents/tactical/learned/ (the champion is measured, never modified)

**Definition of done:**
- [ ] Preflight proven and quoted in the audit: golden green + bare `verify_samples.sh` on the pre-record tree, every `_TOGGLEABLE_LEVER_RESOLVERS` entry OFF, `refresh_samples.sh`'s `REQUIRED_PROMPT_SET` literal matching the locked set, and HEAD's `PROMPT_VERSION_SETS` resolving that set to exactly `*.qwen3_6_27b.v1` (the registry is the version authority — `refresh_samples.sh` carries no version literal, and `record_ml_corpus.sh`'s coupled block stays baseline-3 until 16.17; the recorded MANIFEST provenance check below is the on-disk proof).
- [ ] Both sets recorded at the locked substrate, committed atomically with MANIFEST provenance exact (locked model id, v1 versions, six retired flags, git_sha, $0, winner) and the Q5 annotated tag; `scripts/validity_gate.py --expected-model <locked-id> --require-zero-cost` PASSES both sets; byte-identical reconstruction clean BARE.
- [ ] The BEFORE column is committed (`audits/baseline3-final-measure.json`, named with its tip sha) and the audit's before/after table regenerates from it + the new bytes via the committed CLIs — funnel, R-gate, referee (16.11 definition), canaries (degraded-Q3 discipline, UNDERPOWERED honestly recorded when the CI spans both hypotheses).
- [ ] Baseline-4 floors pinned in the per-baseline block with measured values; `measure_baseline.py --watchability` clean on the new sets.
- [ ] The champion re-audit rows are committed with the stamp-equality proof (all 50 games, read back from recording bytes) and the audit reads the result explicitly as finding-not-blocker, routed to the close + Phase 17.
- [ ] The byte-coupled re-pin sweep lands in this PR; `bash scripts/check.sh` green on the final tree is the proof.
- [ ] A canary regression (genuine-class conversion or R1 outside the pre-registered band on the 50-seed test) PAUSES the phase for an owner call — recorded as the one NO-GO, not absorbed.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 15.7 runbook transfers nearly verbatim — the deltas are the `--expected-model` flip, the
16.11-definition referee, and the champion re-audit leg (clone the 15.18 finalist-eval recipe:
tournament CLI with the factory flag, measurement via the committed CLIs, stamp rows from
`read_tactical_policy_stamp`). Budget ~4–5h wall for the two sets + ~2.5h for the champion leg;
the pre-registered canary bands go in the audit BEFORE the record starts (the 15.18 discipline).

## Integration risk

This is a substrate re-record with a model nobody has recorded at scale: the A/B sweep de-risks
parse behavior, but live full-game recording is where latency/truncation/format edge cases
surface — the per-seed crash-retry budget and the "record-only discipline" (a disappointing
uptake number is a finding for 16.15, never a mid-record prompt iteration) are the guardrails.
The re-pin sweep is the usual long tail; 15.7's list is the map, but the model swap may move
cells 15.7's didn't (different dialogue → different transcript pins).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.watchability"`
- `uv run python -c "import agents.memory.beliefs"`

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
Open a PR from branch `phase-16-baseline-4` with a title like `task 16.14: baseline 4: the model-only atomic re-record + the champion re-audit (operator-run, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.7 (the atomic re-record runbook this clones); audits/audit-phase-16-model-lock.md (the substrate this records); eval/watchability.py (16.11's re-anchored referee + the per-baseline floors block); training/reports/results-champion-close.jsonl (the stamp-proof row convention the re-audit follows)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
