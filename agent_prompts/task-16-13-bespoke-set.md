# Agent Prompt — 16.13 The bespoke set `qwen3_6_27b` v1: semantics ported exactly, restyled to the new model

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.13 — The bespoke set `qwen3_6_27b` v1: semantics ported exactly, restyled to the new model, anchored to audits/audit-phase-16-model-lock.md; experiments/lab/qwen36_prompt_scratch/ (the v0→v5 ladder + README — the style base and its open caveats, incl. the detector-aligned phrasing note); agents/strategic/prompts/qwen3_32b/ (the v5/v6 source MECHANICS the merge must preserve); agent_prompts/task-14-5-new-model-prompts.md (the bespoke-set precedent); orchestrator/game.py PROMPT_VERSION_SETS (:317 — the registry the new entry joins); experiments/lab/featherless_sweep.py (the A/B instrument, --prompt-set axis). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-bespoke-set`
**Depends on:** 16.2
**Section refs:** audits/audit-phase-16-model-lock.md; experiments/lab/qwen36_prompt_scratch/ (the v0→v5 ladder + README — the style base and its open caveats, incl. the detector-aligned phrasing note); agents/strategic/prompts/qwen3_32b/ (the v5/v6 source MECHANICS the merge must preserve); agent_prompts/task-14-5-new-model-prompts.md (the bespoke-set precedent); orchestrator/game.py PROMPT_VERSION_SETS (:317 — the registry the new entry joins); experiments/lab/featherless_sweep.py (the A/B instrument, --prompt-set axis)
**Complexity:** Medium

GO-path only, ∥ 16.12. Author `agents/strategic/prompts/qwen3_6_27b/` v1 — starting from the
owner-directed from-scratch ladder's `experiments/lab/qwen36_prompt_scratch/v5/` (the proven
style base: tag-sectioned, compact ~7.9k, structural-beats-prohibitive, positive phrasing — its
validated profile is 0/32 self-co-location, 0/32 self-flag, 8/8 conversion) and MERGING IN the
baseline-3 mechanics the scratch set deliberately omitted: the vent-elicitation instructions
(scratch crewmate_report currently says "keep observations as an empty list" — that would undo
Wave 0's 0 → 55 structured-vent win), the reporter-exculpation section, the full observation/
claim vocabulary, and every other `qwen3_32b` v5/v6 mechanical directive. Baseline 4 must be
MECHANICS-PURE relative to baseline 3: same asks, same sections, same defaults — a reader
diffing the sets should find style, never semantics (the 16.15 elicitation batch adds the NEW
asks afterward, on this set, as its own attributable layer). Register `_bespoke_versions("qwen3_6_27b", version="v1")` in `PROMPT_VERSION_SETS`
(one new line — the registry line then serializes 16.13 → 16.15 → 16.16), add the set to
`BESPOKE_SETS` in the bespoke-set test suite, flip `refresh_samples.sh`'s `REQUIRED_PROMPT_SET`
literal (a disjoint line from 16.12's model literal; `record_ml_corpus.sh` is NOT touched — its
preflight couples set+versions and flipping one alone fails it; 16.17 re-pins that block whole),
register the set in the sweep harness's `_SET_OWNER` map (the sweep REJECTS an unregistered
`--prompt-set` before it starts — without this the A/B is unrunnable in scope), and operator-run
the A/B as a TWO-PASS protocol on the one new set (`_SET_OWNER` binds each set to its model, so
a cross-set control is structurally rejected): pass 1 sweeps the SCRATCH-V5-VERBATIM commit of
`qwen3_6_27b/` (the control arm — the known-clean profile, mechanics-incomplete; commit it
first, sweep it, record the template-source sha in the rows), pass 2 sweeps the
MECHANICS-COMPLETE commit (the candidate arm — the set baseline 4 actually records with); the
committed rows carry the sha per arm, so the A/B measures exactly the open question: HOW MUCH of
the scratch profile survives the mechanics merge (a measured regression on the tell/self-flag/
conversion cells is a finding for the lock record, not a silent cost) — the evidence that the restyle helps, or at least does not
hurt, before baseline 4 spends a record on it.

**Files in scope:**
- agents/strategic/prompts/qwen3_6_27b/ (new: crewmate_report.j2, impostor_report.j2, accusation_round.j2, vote_ballot.j2)
- orchestrator/game.py (the new PROMPT_VERSION_SETS line — disjoint from 16.7/16.9's regions; serializes ahead of 16.15/16.16)
- tests/agents/test_bespoke_prompt_sets.py (BESPOKE_SETS registration — the parametrized suites pick the set up automatically)
- scripts/refresh_samples.sh (REQUIRED_PROMPT_SET literal — disjoint from 16.12's model lines)
- tests/scripts/test_refresh_samples.py (set-gate pin region — disjoint from 16.12's model-literal pin region)
- experiments/lab/featherless_sweep.py (_SET_OWNER map entry + any slate wiring the A/B needs)
- experiments/lab/results-featherless-sweep-qwen3-6-27b-ab.jsonl (new: the A/B rows)
- experiments/lab/report-featherless-sweep-qwen3-6-27b.md (A/B section appended)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_32b/ (the source set is frozen — provenance-versioned bytes)
- scripts/record_ml_corpus.sh (its preflight compares `PROMPT_VERSION_SETS[$REQUIRED_PROMPT_SET]` to `REQUIRED_PROMPT_VERSIONS` — a set flip without a versions flip fails it, and its pins coherently describe the FROZEN corpus; 16.17 re-pins the whole block)
- meetings/ + agents/memory/ (templates only)
- replays/ (the record is 16.14's)

**Definition of done:**
- [ ] The four templates render under StrictUndefined with the full kwarg surface (the bespoke-set suite green), and a semantics diff table in the PR maps every `qwen3_32b` v5/v6 mechanical directive to its location in the merged set — nothing dropped (the mechanics-pure claim, reviewable) — plus every scratch-v5 style rule retained or consciously traded (the ladder's rules are load-bearing for the clean profile; a dropped rule is a recorded decision).
- [ ] The registry entry, BESPOKE_SETS registration, the refresh_samples set literal (with its script-test pins updated here), and the `_SET_OWNER` sweep registration all land; `AILIBI_PROMPT_SET=qwen3_6_27b` is env-selectable end-to-end (suite-proven), and `tests/scripts/test_record_ml_corpus.py` stays green UNTOUCHED (the corpus script is out of scope — asserted).
- [ ] The operator A/B rows are committed under the two-pass protocol (pass 1 = verbatim-port commit, pass 2 = restyled commit, each row carrying its template-source sha) — parse rates, grade booleans, latency per arm on the same model and contexts — and the report states the verdict (restyle adopted or the verbatim port kept; either is a finding).
- [ ] The prompt-byte golden still passes on committed sets (nothing here touches the old set or its renders).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Start from a verbatim copy of `qwen36_prompt_scratch/v5/`, then merge the mechanics in the
ladder's own discipline — one directive at a time, re-sweeping when a clean cell moves (the
ladder proved each rule earns its place by a measured failure; extend it, don't abandon it).
The likely tension: re-enabling structured observations for crew re-opens the surface the
scratch set closed structurally for impostor cover — the merge may need role-differentiated
schema contracts (crew: full observation vocabulary; impostor cover: the v0 accusation-only
structure), which is a STYLE choice both mechanics permit. Non-thinking pinned throughout
(the probe's default-reasoning finding). Keep every section anchor the loader/tests reference.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-16-bespoke-set` with a title like `task 16.13: the bespoke set `qwen3_6_27b` v1: semantics ported exactly, restyled to the new model`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-model-lock.md; experiments/lab/qwen36_prompt_scratch/ (the v0→v5 ladder + README — the style base and its open caveats, incl. the detector-aligned phrasing note); agents/strategic/prompts/qwen3_32b/ (the v5/v6 source MECHANICS the merge must preserve); agent_prompts/task-14-5-new-model-prompts.md (the bespoke-set precedent); orchestrator/game.py PROMPT_VERSION_SETS (:317 — the registry the new entry joins); experiments/lab/featherless_sweep.py (the A/B instrument, --prompt-set axis)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
