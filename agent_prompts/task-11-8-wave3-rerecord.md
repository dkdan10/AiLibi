# Agent Prompt — 11.8 Wave-3 combined re-record, era-pin re-anchor, and rubric gate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.8 — Wave-3 combined re-record, era-pin re-anchor, and rubric gate, anchored to tasks/phase-11.md Task 11.4 (the Wave-1 re-record + 39-test re-anchor protocol, commits 853a601/9753a4b); experiments/lab/report-rubric-interestingness.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-wave3-rerecord`
**Depends on:** 11.4, 11.5, 11.6, 11.7
**Section refs:** tasks/phase-11.md Task 11.4 (the Wave-1 re-record + 39-test re-anchor protocol, commits 853a601/9753a4b); experiments/lab/report-rubric-interestingness.md
**Complexity:** Integration

After 11.5/11.6/11.7 merge, ONE combined re-record of both sample sets (flat 4p/1i + 9p2i) on qwen3.5:9b,
smoke-first, then re-anchor the committed-bytes era-pin tests to the new baseline (the 11.4 cadence) and
gate on the interestingness score (R1 + R5), not the win split.

**Files in scope:**
- replays/samples/** (both sets re-recorded; each MANIFEST + tournament-eval-report.json rebuilt)
- tests/eval/test_balance_eval.py, tests/eval/test_win_condition_selfcheck.py, tests/eval/test_gate_metrics.py, tests/eval/test_gate_spec_metrics.py, tests/eval/test_wave2_metrics.py (era-pin re-anchor to the new baseline)
- tests/meetings/test_transcript.py, tests/meetings/test_manager.py, tests/agents/test_beliefs.py (committed-bytes detector/fold pins re-anchored)
- tests/scripts/test_manifest_writer.py, tests/scripts/test_refresh_samples.py, tests/api/test_eval.py (manifest/version + meetings-seed-list pins re-anchored)
- any committed observation/memory golden whose GlobalView shape changed (regenerate if 11.5's two new fields appear in a pinned packet fixture)

**Files NOT in scope:**
- all production source (frozen at the merge of 11.5/11.6/11.7 — a re-record changes data, not code)
- the §4.6 gate / tally / caps / §6.3 constants / the task clock (FROZEN)

**Definition of done:**
- Smoke-first: 3 meeting-bearing 9p2i seeds dry-run→live; confirm a sabotage actually fires (`grep SabotageStarted` > 0), the crew diverts to repair (`grep SabotageRepair` present), and at least one game ends `IMPOSTOR_SABOTAGE` or a gated task race flips an eject-decided/parity outcome — before the full run (STOP-and-escalate if a sabotage loops or none ever fires).
- Full re-record of both sets; `scripts/verify_samples.sh` byte-reconstructs both; the firewall/leak sweeps + win-condition selfcheck stay green.
- HARD substrate gate (the 11.4 standard): game_over 100%, friendly-fire 0, betrayal 0, byte-identical ×2, inversions 0.
- `uv run python experiments/lab/rubric_score.py` on the fresh facts shows **R1 holds/rises (eject-decided share) AND R5 ≥ 3 win shapes** with a new gating-attributable win shape; the win split is a sentinel, not a gate.
- Re-run the close audit on the new 9p2i set; verdict stays substrate-VALID with no sabotage-spam degeneracy.

## Implementation hint
Mirror the 11.4 protocol exactly: smoke STOP-for-go, then `scripts/refresh_samples.sh --full` for flat and
the `AILIBI_SAMPLE_DIR=replays/samples/9p2i ...` env for the 2i set, `AILIBI_LLM_PROVIDER=ollama` ($0).
Re-anchor the era-pin tests in a single deliberate commit after a byte-clean baseline (as 9753a4b followed
853a601) — update the expected hashes/versions to the new baseline; do NOT weaken the assertions.

## Integration risk
The only task that rewrites committed bytes; a determinism break means upstream non-determinism slipped in
(a sabotage tie-break RNG, unsorted repair-room iteration, or a `_tasks_gated` read depending on dict
order) — bisect against 11.5's helper and 11.6/11.7's sort keys. Spend is $0 (ollama); smoke 3 seeds before
the multi-hour full run. If R5 does not reach 3 shapes, the lever fires too rarely/degenerately — escalate
to re-anchor the reactor timer or the impostor trigger threshold (still NOT the frozen task clock), then
re-smoke.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import observation.packet.GlobalView"`
- `uv run python -c "import observation.packet"`
- `uv run python -c "import observation.packet.SelfView"`

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
Open a PR from branch `phase-11-wave3-rerecord` with a title like `task 11.8: wave-3 combined re-record, era-pin re-anchor, and rubric gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-11.md Task 11.4 (the Wave-1 re-record + 39-test re-anchor protocol, commits 853a601/9753a4b); experiments/lab/report-rubric-interestingness.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
