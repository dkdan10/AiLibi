# Agent Prompt — 11.4 Wave-1 combined re-record and gate

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.4 — Wave-1 combined re-record and gate, anchored to tasks/phase-10.md (the 10.5/10.9 re-record protocol); experiments/lab/report-rubric-interestingness.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-wave1-rerecord`
**Depends on:** 11.1, 11.3, 11.2
**Section refs:** tasks/phase-10.md (the 10.5/10.9 re-record protocol); experiments/lab/report-rubric-interestingness.md
**Complexity:** Integration

After 11.1/11.2/11.3 merge, ONE combined re-record of BOTH sample sets (flat 4p/1i + 9p2i) on qwen3.5:9b,
smoke-first — never per-task. Then regenerate the determinism/prompt-regression fixtures and gate on the
interestingness score (R2), not the win split.

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST + tournament-eval-report.json rebuilt)
- tests/fixtures/prompt_regression/** (baseline.json + v_a/v_b rebuilt from the fresh recorded bytes; the recorded accusation_round version shifts v7→v8 here)
- any committed observation/memory golden whose SelfView shape changed (regenerate if 11.1/11.3 added fields to a pinned fixture)

**Files NOT in scope:**
- all production source (frozen at the merge of 11.1/11.2/11.3 — a re-record changes data, not code)
- the §4.6 gate / tally / caps / §6.3 constants / task clock (FROZEN through Wave 1)

**Definition of done:**
- Smoke-first: 3 meeting-bearing 9p2i seeds dry-run→live; confirm meeting_rate, `grep VentEntered` > 0, and no impostor stuck in a vent, before the full run (STOP-and-escalate if a turn truncates or a vent loops).
- Full re-record of both sets; `scripts/verify_samples.sh` byte-reconstructs both (the state-hash determinism gate); `determinism` + firewall/leak sweeps green.
- HARD substrate gate: game_over 100%, friendly-fire 0, betrayal 0, byte-identical ×2, inversions 0.
- `uv run python experiments/lab/rubric_score.py` on the fresh facts shows R2 UP (accused-impostor survival ↑, impostor flag-clean ↑) vs the W2 baseline (mean 38.2); R1/clock untouched (Wave 1 is deception, not balance).
- Re-run the close audit on the new 9p2i set; verdict stays substrate-VALID with no new degeneracy.

## Implementation hint
Mirror the 10.9 protocol exactly (smoke STOP-for-go, then `scripts/refresh_samples.sh --full`,
`AILIBI_LLM_PROVIDER=ollama`). The prompt-regression v_b reconstruction shifts when the recorded versions
move to v8 — update the attribution asserts deliberately, not silently.

## Integration risk
This is the only task that rewrites committed bytes; a determinism break here means an upstream
non-determinism slipped in (vent tie-break RNG, unsorted set iteration) — bisect against 11.1's sort keys.
Spend is $0 (ollama); smoke 3 seeds before the multi-hour full run.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import observation.packet"`
- `uv run python -c "import observation.packet.SelfView"`

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
Open a PR from branch `phase-11-wave1-rerecord` with a title like `task 11.4: wave-1 combined re-record and gate`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-10.md (the 10.5/10.9 re-record protocol); experiments/lab/report-rubric-interestingness.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
