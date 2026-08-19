# Agent Prompt — 10.14 Impostor toolkit (blending + anticipatory cover + kill discipline)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-10.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 10.14 — Impostor toolkit (blending + anticipatory cover + kill discipline), anchored to DESIGN.md §3.4, §4.5, §5.3; audits/audit-2026-06-13-1816-gameplay-data.md D-D-1/D-D-2/D-D-7 + MECH-B-1; experiments/lab/report-deception-battery-2.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-10.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-10-impostor-toolkit`
**Depends on:** none (Stage-1 detector repairs merged; impostor-side, file-disjoint from the crew lever)
**Section refs:** DESIGN.md §3.4, §4.5, §5.3; audits/audit-2026-06-13-1816-gameplay-data.md D-D-1/D-D-2/D-D-7 + MECH-B-1; experiments/lab/report-deception-battery-2.md
**Complexity:** Integration

The PRIMARY Wave-2 lever — make impostors a credible threat so the meeting layer becomes
load-bearing. Today impostors are passive: do_task 0 / report 0 / emergency 0, wait-share ~51% (crew
~12% — the "never-tasks" fingerprint), and ~15% of kill intents are wasted cross-room. The lab found
the toolkit is TRACTABLE: the do_task path is dormant-REACHABLE (not missing), and a lightweight
anticipatory-cover DIRECTIVE makes the 9B generate its own sheltered alibi 8/12 (no full script
generator needed). Activate blending + anticipatory cover + kill discipline; the 7.12/9.3 firewalls
and betrayal==0 stay inviolate.

**Files in scope:**
- agents/tactical/impostor_policy.py (BLENDING: make the dormant `_idle` do_task branch fire — an idle impostor emits a fake do_task that consumes the tick and RENDERS as do_task but makes NO task progress, drawn from a small per-impostor pretend-task set; tune the idle budget so impostor wait-share trends toward the crew ~10-12%, not 51%. KILL DISCIPLINE: gate the chosen kill target on same-room co-presence in the proposed action BEFORE emitting — a cross-room target degrades to move-toward/wait, eliminating the MECH-B-1 ~15% cross-room no-ops; also suppress a kill emission during cooldown)
- observation/service.py (surface a pretend `pending_task_id` for impostors so `_idle`'s do_task branch is reachable — today `_pending_task_id_for_agent` filters `task.owner==agent_id` and impostors own none; the pretend id must NOT create a real task instance or advance the task-win denominator)
- agents/strategic/prompts/impostor_report.j2 (ANTICIPATORY COVER: when the impostor recently killed, the opening frames "prepare an account that does NOT place you at the kill room/tick" — the lab's perform-from-a-goal directive, not a verbatim script; the cover room/window is PINNED by the policy once and reused so the justification does not drift per turn — battery-2 P1; impostor_report v4→v5)
- orchestrator/game.py (DEFAULT_PROMPT_VERSIONS impostor_report v5)
- tests/agents/test_impostor_policy.py + tests/agents/test_strategic_prompts.py + tests/observation/* + tests/fixtures/prompt_regression/ (regenerate for v5; pins below)

**Files NOT in scope:**
- the crew belief-spread lever (crew-side; the impostor toolkit must not touch the fold/tally)
- the 7.12 teammate firewall + betrayal coercion (inviolate — never weakened)
- engine/** kill resolution / win conditions (the fake task must not reach the real task counter — verify, do not change)
- the §4.6 render, the 9.8 constants, token caps (frozen)
- replays/samples/** (no re-record; the toolkit is measured at 10.17)

**Definition of done:**
- [ ] Blending: an idle impostor emits a fake do_task that renders as do_task and consumes the tick; offline/unit-verified it advances NO real task instance and does NOT move the CREWMATE_TASKS win denominator (the crew-side integrity invariant — a fake task can never help the crew win).
- [ ] Idle budget: impostor wait-share in a fresh smoke trends toward crew levels (target the ~10-12% band, reported not hard-pinned); do_task emissions > 0.
- [ ] Kill discipline: a cross-room kill intent degrades to move-toward/wait before emit (no ActionRejected cross-room no-op); a cooldown kill is suppressed; unit-pinned, and the MECH-B-1 class drops to ~0 on a fresh smoke.
- [ ] Anticipatory cover: the impostor_report v5 opening, given a recent kill, renders the prepare-an-alibi-away-from-the-scene frame; the policy supplies a PINNED cover room/window (reused, not regenerated); golden-pin the v5 opening.
- [ ] Firewall: betrayal accusations/ballots stay 0 by construction; the 7.12 guard is untouched; impostor never fake-tasks in a way that names a teammate.
- [ ] Determinism + full `bash scripts/check.sh` (mypy/ruff/format/lint-imports/generate_prompts --check/validate_task_docs/pytest/frontend) pass.

## Implementation hint

The do_task path is dormant-reachable: `ImpostorPolicy._idle` already has a do_task branch gated on
`pending_task_id`; surface a pretend id from observation/service.py keyed so the win-counter never
sees it. The anticipatory cover is a DIRECTIVE not a generator (battery-2 P3 — the 9B fabricates from
a stated goal); pin the cover evidence once (battery-2 P1 — persistence is good, justification drifts).
The kill-discipline gate is agent-side producer logic (the engine refusal is correct; this stops the
wasted intent before it reaches the engine).

## Public types this task introduces
- `PRETEND_TASK_MARKER (or equivalent — name in the PR; the fake-task sentinel that keeps it off the real task counter)`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The one inviolable invariant is the fake task NEVER advancing the real task-win denominator (else
impostors help the crew win) — pin it explicitly. The firewall stays the deterministic backstop
(battery-2 P5 found 1/11 prompt-level teammate leaks). Recording-side only; measured at 10.17, where
the EMERGENCY_COOLDOWN_TICKS anchor is re-derived against the toolkit-shifted kill cadence.

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
Open a PR from branch `phase-10-impostor-toolkit` with a title like `task 10.14: impostor toolkit (blending + anticipatory cover + kill discipline)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.4, §4.5, §5.3; audits/audit-2026-06-13-1816-gameplay-data.md D-D-1/D-D-2/D-D-7 + MECH-B-1; experiments/lab/report-deception-battery-2.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
