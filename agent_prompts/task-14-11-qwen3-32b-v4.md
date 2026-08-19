# Agent Prompt — 14.11 qwen3_32b v4: alibi discipline, ballot craft, and voice (the measured-defect batch)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.11 — qwen3_32b v4: alibi discipline, ballot craft, and voice (the measured-defect batch), anchored to audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the per-defect counts + targets); agents/strategic/prompts/qwen3_32b/ (the v3 set); meetings/schemas.py (the frozen output contract); replays/samples/9p2i/replay-seed-44.jsonl (the worked railroad-fuel example). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-qwen3-32b-v4`
**Depends on:** 14.8
**Section refs:** audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the per-defect counts + targets); agents/strategic/prompts/qwen3_32b/ (the v3 set); meetings/schemas.py (the frozen output contract); replays/samples/9p2i/replay-seed-44.jsonl (the worked railroad-fuel example)
**Complexity:** Medium

Harden the locked `qwen3_32b` set v3 → v4 against the six defects MEASURED on baseline 1, so baseline 2's
dialogue is both more correct and more watchable. The fixes, each tied to its measured count: (1) ALIBI
DISCIPLINE — the alibi must match the speaker's own memory rows exactly, never spanning rooms they moved
between (10% of self-alibis were contradicted by the speaker's OWN same-turn task observation — the greedy
spans that fuel the railroad; seed-44 m1 p-1 is the worked example); (2) DEAD-ROSTER SALIENCE — move the
do-not-accuse/vote list adjacent to target selection with an explicit "naming an ejected/dead player wastes
your vote" (27 invalid-target ballots); (3) a REAL `turn_id` worked example for `primary_reason_id` — copy a
turn id verbatim from the transcript lines (20 invalid-id nulls); (4) CONFIDENCE CALIBRATION — a rubric (1.0
only for a first-hand witnessed kill; ~0.7 corroborated; ~0.5 hunch; 64 accusations sat at 1.0); (5)
OBSERVATION CURATION — put the 3–5 most probative observations on the record, not the whole movement log
(30+-row dumps bloat turns and feed the 23 missed-deadline rambles); (6) VOICED RATIONALE — the ballot
rationale states the argument in the agent's own words, referencing the specific turn that convinced them (33%
of ballots shared one literal template sentence). The output JSON schema is FROZEN (the same-schema
invariant); only instruction prose and examples change. In-place template edits are SAFE for baseline-1
byte-identity — reconstruction replays RECORDED prompt bytes and never re-renders templates (the 14.2
determinism contract); recorded `prompt_versions` rows stay `…​.v3` while the registry moves to v4 for future
recordings.

**Files in scope:**
- agents/strategic/prompts/qwen3_32b/crewmate_report.j2 (fixes 1, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/impostor_report.j2 (fixes 1, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/accusation_round.j2 (fixes 1, 2, 4, 5; header → v4)
- agents/strategic/prompts/qwen3_32b/vote_ballot.j2 (fixes 2, 3, 6; header → v4)
- orchestrator/game.py (registry bump ONLY: `qwen3_32b` → `_bespoke_versions("qwen3_32b", version="v4")` — one line at the PROMPT_VERSION_SETS registry, disjoint from the gate-retirement region 14.9 edits at `:714-735`; this task may run in PARALLEL with 14.9, whichever merges second rebases this trivially)
- tests/agents/test_bespoke_prompt_sets.py (render + cross-set parse stay green; add pins for the new directives — alibi-discipline present, dead-roster adjacency, confidence rubric — mirroring the cover-directive gating pins)

**Files NOT in scope:**
- the other bespoke sets + `qwen3_5_9b/` (frozen; this iterates ONLY the locked set)
- replays/samples/ (recorded v3 bytes verify unchanged; baseline 2 is 14.12)
- meetings/schemas.py + the graders (the output contract is the invariant)
- llm/ + agents/memory/ (the belief-side fix is 14.10)

**Definition of done:**
- [ ] All six measured defects are addressed in the templates, each traceable to its 14.8 count (the audit's targets are quoted in the template header comments where the directive lands).
- [ ] The registry maps `qwen3_32b` → v4; template headers read v4; recorded baseline-1 rows (…​.v3) are untouched and `scripts/verify_samples.sh` stays green on the committed sets (reconstruction replays recorded bytes — prove it, don't assume it).
- [ ] Every template renders under `StrictUndefined` with the existing loader kwargs; the cross-set parse check holds; the cover directive stays gated on `is_impostor`; the anti-meta-leak directive is preserved.
- [ ] A cheap offline validation pass runs the v4 set over reconstructed contexts (the 14.5 `--prompt-set` harness) and reports parse-success + the mechanical grades vs the v3 rows — a regression in either is a stop-and-iterate, not a ship.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Iterate on the v3 bodies (this is a hardening pass, not a ground-up rewrite — v3's response-shape checklist
and worked examples fixed the smoke failures; keep them). Fix 1 is the highest-leverage line in the phase
tail: the alibi bullet should read like "your `alibi` must quote your own memory exactly — one room, the tick
range you were ACTUALLY there; if you moved during the window, alibi only the room you were in at the relevant
tick; a range that spans rooms you moved between contradicts your own record and gets you ejected." For fix 6,
give two contrasting example rationales (one evidence-citing, one gut-read) so the model stops converging on a
single template sentence. Watch fix 5 vs the graders: curation must not drop the found_body/saw observations
`eval/vote_correctness.py` reads off the opening turn — say "always include the body report and the sightings
naming your suspect." Validate with `AILIBI_PROMPT_SET=qwen3_32b` + the featherless_sweep `--prompt-set`
axis on the same pinned contexts (operator, $0, fast); the LIVE proof is 14.12's smoke.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-14-qwen3-32b-v4` with a title like `task 14.11: qwen3_32b v4: alibi discipline, ballot craft, and voice (the measured-defect batch)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the per-defect counts + targets); agents/strategic/prompts/qwen3_32b/ (the v3 set); meetings/schemas.py (the frozen output contract); replays/samples/9p2i/replay-seed-44.jsonl (the worked railroad-fuel example)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
