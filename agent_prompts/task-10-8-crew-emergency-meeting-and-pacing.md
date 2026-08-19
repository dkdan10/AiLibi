# Agent Prompt — 10.8 Crew emergency meeting and pacing

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.8 — Crew emergency meeting and pacing, anchored to DESIGN.md §3.2, §5.2; audits/audit-2026-06-11-2218-gameplay-data.md gp-3 (B-B-1 through B-B-9). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-emergency-pacing`
**Depends on:** none (file-disjoint from the wave root; functionally independent)
**Section refs:** DESIGN.md §3.2, §5.2; audits/audit-2026-06-11-2218-gameplay-data.md gp-3 (B-B-1 through B-B-9)
**Complexity:** Integration

Meeting supply is starved and impostor-controlled: 78/78 meetings are body reports, 0
emergency meetings ever fired (the intent exists but is gated behind witnessing a kill in
your own room — 53% of kills are unwitnessed — plus a button-room walk), median 1.56
meetings/game, and only 44% of games reach the accumulator's 2-meeting floor. This task makes
the emergency channel reachable for crew, breaking the kill-cadence monopoly and creating the
runway 10.7's conversions and the 9.8 accumulator need. Pacing is currently INVERTED (every
3-or-fewer-meeting game is a crew win, 3 of 4 four-meeting games are impostor wins), so the
anti-railroad gate in 10.9 is the hard condition, not the meeting count.

**Files in scope:**
- agents/tactical/crewmate_policy.py (add a suspicion-accumulation trigger beside the witnessed-kill trigger: a living crewmate whose private max suspicion over living players reaches the §4.6 threshold 0.60, with no meeting held since that belief crossed, sets EmergencyMeetingIntent and walks to the button as today — the walk stays, it is the counterplay cost; eligibility: at most ONE emergency call per player per game, plus a global cooldown of EMERGENCY_COOLDOWN_TICKS since the last meeting ended, a named constant anchored to the mean kill interval (~6 ticks on the W0 set) and reported in the PR — the anchor reasoning, recorded for future re-tunes: emergency supply should roughly match and never exceed organic body-report supply, so meetings cannot spawn faster than evidence accrues; the anchor shifts when kill cadence changes, and Wave 2's kill-intent gating will change it — re-derive there; the missing-player trigger is explicitly OUT — revisit only if supply is still starved after this wave; impostor policy untouched — impostors gain no button behavior until Wave 2 decides it)
- orchestrator/game.py (verify the EmergencyMeetingIntent path end-to-end into a meeting with trigger EMERGENCY; bump crewmate_report to v6 in DEFAULT_PROMPT_VERSIONS)
- agents/strategic/prompts/crewmate_report.j2 (an emergency-opening branch ONLY: when the meeting trigger is EMERGENCY the opener is the caller and the prompt frames the meeting as called-on-suspicion — state who you suspect and the first-hand basis, or unsure; the body-report branch is byte-unchanged; version v5 to v6)
- tests/agents/test_strategic_prompts.py + tests/agents/test_crewmate_policy.py + tests/orchestrator/* (pins below) + tests/fixtures/prompt_regression/ (regenerate the baseline for v6 per the established pattern)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (Wave 2)
- meetings/transcript.py, agents/memory/beliefs.py, meetings/manager.py vote/fold logic (10.6 and 10.7 own those seams; the meeting layer already accepts a trigger field)
- engine/** (the emergency action exists; no rule changes)
- vote_ballot.j2 and the §4.6 render (frozen); the 9.8 decay constants (the decay-vs-cadence question is ACCOUNTED in 10.9's report, not re-tuned here)
- replays/samples/**

**Definition of done:**
- [ ] Trigger unit pins: the intent fires when private max suspicion crosses 0.60 with no meeting since the cross; it does not fire below threshold, during cooldown, after the player's one call is spent, or for impostors (asserted against impostor policy output).
- [ ] End-to-end scenario: an unwitnessed kill followed by accumulated suspicion produces an EMERGENCY-triggered meeting with the caller as opener, opt-ins and ballots running normally, and the §5.2 chain rules unchanged.
- [ ] The emergency opening renders the called-on-suspicion frame; the body-report branch renders byte-identically to v5 for body meetings (golden-pin both branches); DEFAULT_PROMPT_VERSIONS and the version test pins read v6 — lineage confirmed at branch time: this builds on the v5 merged in Wave 0 and recorded by 10.5, no Wave-1 task touches the template in parallel (10.7 is prompts-frozen), so the lineage is v5 to v6 and this task is the sole owner of the prompt-regression baseline regeneration.
- [ ] A body-less meeting carries no found_body observation and nothing downstream assumes one (transcript, ballots, eval readers run clean on an EMERGENCY meeting fixture).
- [ ] Determinism: trigger evaluation is a pure function of the agent's observation/belief state; cooldown bookkeeping replays identically.
- [ ] `uv run mypy .`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run lint-imports`, `uv run python scripts/generate_prompts.py --check`, `uv run python scripts/validate_task_docs.py`, `uv run pytest`, and `bash scripts/check.sh` all pass.

## Implementation hint

The witnessed-kill path at crewmate_policy.py:105 and the button-walk at :203-218 are the
existing machinery — the new trigger is a second producer of the same intent, not a new
pipeline. Threshold one-home: read the §4.6 gate constant, do not restate 0.60. The
crewmate_report branch should follow the template's existing conditional style; keep the
emergency branch additive so the v5 body path stays byte-stable (the golden pin enforces it).

## Public types this task introduces
- `EMERGENCY_COOLDOWN_TICKS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Meeting spam is capped by once-per-player plus the global cooldown; the real risk is the
pacing inversion — more meetings currently correlate with MORE wrong ejections, which is why
this ships in the same re-record as 10.7's conversion fix and why 10.9 hard-gates on
wrong-ejection games not rising. The stopwatch coupling (13 margin-1 wins, 8 photo-finishes)
is reported in 10.9, never tuned here.

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
Open a PR from branch `phase-10-emergency-pacing` with a title like `task 10.8: crew emergency meeting and pacing`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2, §5.2; audits/audit-2026-06-11-2218-gameplay-data.md gp-3 (B-B-1 through B-B-9)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
