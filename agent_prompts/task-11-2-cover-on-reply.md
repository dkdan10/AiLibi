# Agent Prompt — 11.2 Cover-consistency directive on the reply turn

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.2 — Cover-consistency directive on the reply turn, anchored to DESIGN.md §5.2 (accusation round); experiments/lab/report-vent-escape-lab.md (the 3 residual self-pair-drift flags). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-cover-on-reply`
**Depends on:** none (prompt layer; file-disjoint from the policy and self-channel work)
**Section refs:** DESIGN.md §5.2 (accusation round); experiments/lab/report-vent-escape-lab.md (the 3 residual self-pair-drift flags)
**Complexity:** Integration

The impostor "cover" directive ("DECIDE on ONE room and tick-window AWAY from the body's room and the tick
it happened; state the SAME room and window every time you are asked; never place yourself in the body's
room") is stranded at `agents/strategic/prompts/impostor_report.j2:115-124`, gated on the body-report
OPENING that impostors never take — so on the REPLY turn (the only turn an impostor speaks) it gets no cover
guidance, and its account drifts across turns (the residual `alibi_conflict` self-pair flags the vent fix
cannot remove). Port the directive into the `accusation_round.j2` reply branch, gated on the impostor role.
VERIFIED current state: `accusation_round` is at v7 (`DEFAULT_PROMPT_VERSIONS` `orchestrator/game.py:226`;
template header `version: 7`); the reply branch is `{% if turn_kind == "reply" %}` at `accusation_round.j2:79`;
`participant.role` is available at `meetings/manager.py:1379`.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2 (add an `{% if is_impostor %}` cover block inside the reply branch porting the impostor_report directive — generic, never naming a teammate; bump the version marker to v8)
- agents/strategic/prompts/loader.py (add `is_impostor: bool = False` to `accusation_round_prompt`, threaded to the render)
- meetings/manager.py (the StatementPromptRenderer Protocol + `_render_turn_prompt` reply path: pass `is_impostor=(participant.role == "IMPOSTOR")`; default False keeps the crewmate_report conformance)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`: accusation_round v7 → v8, with a dated comment paragraph)
- tests/agents/test_strategic_prompts.py (version pins v7→v8; the impostor reply renders the cover block, the crewmate reply and the opt_in branch do not, and a raw render without `is_impostor` validates under StrictUndefined)

**Files NOT in scope:**
- the §4.6 vote-gate render (FROZEN), vote_ballot.j2, crewmate_report.j2 content
- agents/tactical/**, observation/**, agents/memory/** (11.1/11.3 own those)
- tests/fixtures/prompt_regression/baseline.json (moves only at the 11.4 re-record — it reads versions from the recorded replays, still v7 until then)

**Definition of done:**
- An impostor reply renders the cover directive; crewmate replies and opt-in turns do not.
- accusation_round is v8 across the template marker, `DEFAULT_PROMPT_VERSIONS`, and the version test pins.
- `uv run python scripts/generate_prompts.py --check` clean (the paste-ready prompt regenerated).
- `bash scripts/check.sh` green; do NOT touch `baseline.json` (it moves at 11.4).

## Implementation hint
Add an explicit `is_impostor` kwarg rather than reusing `fellow_impostor_ids` — a SOLE impostor has empty
fellows but must still get the directive (mirroring how impostor_report fires for sole impostors). Scope the
block to the reply branch only (the lab residual is opening↔reply drift; opt-in is terminal). Reuse the
exact directive text from impostor_report.j2 so the two paths stay one wording.

## Integration risk
The version fan-out (template marker + DEFAULT_PROMPT_VERSIONS + the live-version smoke test) must move
together or generate_prompts --check / the version test fails. The recorded replays still carry v7 until
11.4, so the prompt-regression baseline must NOT be regenerated in this task.

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
Open a PR from branch `phase-11-cover-on-reply` with a title like `task 11.2: cover-consistency directive on the reply turn`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2 (accusation round); experiments/lab/report-vent-escape-lab.md (the 3 residual self-pair-drift flags)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
