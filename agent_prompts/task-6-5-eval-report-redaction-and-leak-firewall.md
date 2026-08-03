# Agent Prompt — 6.5 Harmonize the eval-report failed-call surface and extend the leak firewall

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.5 — Harmonize the eval-report failed-call surface and extend the leak firewall, anchored to Audit B-B-1, D-D-1, B-B-2, D-D-2; DESIGN.md §11.2, §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-eval-report-redaction-and-leak-firewall`
**Depends on:** none
**Section refs:** Audit B-B-1, D-D-1, B-B-2, D-D-2; DESIGN.md §11.2, §11.3
**Complexity:** Medium

The Phase 4 spectator DTO `FailedCallView` deliberately drops `raw_response` and
`prompt_length` and truncates `error_message` to 200 chars, but the Phase 5 eval
route `GET /eval/tournament-report` (`api/routes/eval.py:38`) serves
`TournamentEvalReport` directly, transitively embedding `FailedCallReplayEntry`
with all three raw fields — re-exposing over HTTP exactly what the parallel
surface suppresses (audit B-B-1 = D-D-1, a convergent cross-phase finding). Both
surfaces are privileged GM views with no auth per the established model, so this
is a contract asymmetry, not a role/engine-state leak — but the two surfaces must
agree. Separately, the structural leak-test firewall pins only `api.schemas`
(`tests/api/test_leak.py`), so the eval route's `TournamentEvalReport` and its
leaf DTOs ride outside the guard: a future engine-state field added to a replay
leaf type would silently expand the served payload with no tripwire (B-B-2 =
D-D-2).

This task does two things. First, resolve the redaction asymmetry in ONE explicit
direction: either (a) route the eval route's failed-call data through a sanitized
DTO that mirrors `FailedCallView`'s exclusions (drop `raw_response`/
`prompt_length`, truncate `error_message`), or (b) consciously document on the
route that the privileged surface intentionally exposes the raw failed-call
payload and align both surfaces' stated contracts. Pick (a) unless there is a
demonstrated consumer that needs the raw blob; record the choice. Second, extend
the leak firewall to cover the eval route: snapshot the recursive field set of
`TournamentEvalReport` (its leaf DTOs + the four metric reports) and assert no
engine-state field (`state_hash`, `rng_state`, etc.) is reachable, so any future
field addition forces an explicit review touch.

**Files in scope:**
- api/routes/eval.py
- api/schemas.py
- tests/api/test_leak.py
- tests/api/test_eval_routes.py

**Files NOT in scope:**
- api/replay_loader.py (Task 6.6)
- api/main.py (Task 6.1)
- api/routes/replays.py (Task 6.6)
- eval/report_schema.py (Task 6.9)
- frontend/
- orchestrator/replay.py (reuse leaf types; do not reshape)

**Definition of done:**
- [ ] The redaction asymmetry is resolved in one explicit, documented direction. If (a): a sanitized failed-call DTO mirroring `FailedCallView` (no `raw_response`, no `prompt_length`, `error_message` truncated to 200 chars) is served by the eval route, and a test asserts the served payload excludes the raw fields. If (b): the eval route carries a docstring/comment stating the raw failed-call exposure is intentional, and a test pins that the raw fields ARE present so the contract is explicit. The PR `## Decisions` block states which and why (B-B-1/D-D-1).
- [ ] `tests/api/test_leak.py` is extended with a recursive field-set snapshot/assertion over `TournamentEvalReport` and its leaf DTOs + the four metric reports, asserting no `state_hash`/`rng_state`/other engine-internal field is reachable on the served eval surface (B-B-2/D-D-2). The assertion is structured so adding a field to any leaf type forces an explicit update to the snapshot.
- [ ] `tests/api/test_eval_routes.py` covers the chosen redaction direction end-to-end through the route.
- [ ] No change to engine-side replay records; leaf types are reused by import, not redefined.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `api/routes/eval.py:38` (the route returning `TournamentEvalReport`), the
Phase 4 `FailedCallView` in `api/schemas.py` (the exclusion/truncation pattern to
mirror), `orchestrator/replay.py`'s `FailedCallReplayEntry`, and
`tests/api/test_leak.py:34` (how the firewall currently walks `api.schemas`). For
direction (a), define the sanitized DTO next to `FailedCallView` and map at the
route/loader boundary — do not mutate the underlying replay entry. For the
firewall extension, dump the recursive JSON schema of `TournamentEvalReport` and
assert the forbidden engine-internal field names are absent anywhere in the tree;
model it on the existing `api.schemas` forbidden-type assertions so the style is
consistent. The snapshot must fail loudly when a new field appears — that
tripwire is the durable value (D-D-2).

## Public types this task introduces
- `api.schemas.FailedCallEvalView`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-6-eval-report-redaction-and-leak-firewall` with a title like `task 6.5: harmonize the eval-report failed-call surface and extend the leak firewall`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit B-B-1, D-D-1, B-B-2, D-D-2; DESIGN.md §11.2, §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
