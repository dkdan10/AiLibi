# Agent Prompt — 15.4.1 Spectator mirror for vent observations (API DTO + generated types + renderer)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.4.1 — Spectator mirror for vent observations (API DTO + generated types + renderer), anchored to tasks/post-phase-14-clean-up.md H4; api/replay_loader.py:1890-1915 (`_observation_claim_view` raises TypeError on an unsupported claim); api/schemas.py (ObservationClaimView); scripts/gen_frontend_types.py (DTO → frontend type generation). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-vent-spectator-mirror`
**Depends on:** 15.4
**Section refs:** tasks/post-phase-14-clean-up.md H4; api/replay_loader.py:1890-1915 (`_observation_claim_view` raises TypeError on an unsupported claim); api/schemas.py (ObservationClaimView); scripts/gen_frontend_types.py (DTO → frontend type generation)
**Complexity:** Medium

Mirror 15.4's schema extension through the privileged spectator path — without this, the first
baseline-3 replay containing a structured vent turn CRASHES the replay API: `_observation_claim_view`
is deliberately exhaustive and raises `TypeError` on any observation type it does not know
(`api/replay_loader.py:1915` — the no-silent-fallbacks doctrine working as designed, which is exactly
why the mirror must land before the re-record). Add the vent variant to `api/schemas.py`'s
`ObservationClaimView` union, extend the loader's observation-claim view mapping, regenerate
`frontend/src/types/api.ts` via `scripts/gen_frontend_types.py`, and extend the meeting-transcript
observation renderer (the exhaustive ObservationLine switch) so a vent sighting displays in the
spectator UI. Committed v4 replays contain no vent observations and must serve byte-identically.

**Files in scope:**
- api/schemas.py (ObservationClaimView vent variant — additive)
- api/replay_loader.py (observation-claim view mapping region — disjoint from 15.9's policy-stamp guard region)
- frontend/src/types/api.ts (regenerated via scripts/gen_frontend_types.py — mechanical output)
- frontend/src/ (the meeting-transcript observation renderer — the exhaustive ObservationLine switch gains the vent variant)
- tests/api/test_replay_loader_vent_view.py (new: fixture replay with a structured vent turn serves end-to-end)

**Files NOT in scope:**
- meetings/ (the source schema landed in 15.4)
- scripts/gen_frontend_types.py (run, not edited)
- replays/samples/ (v4 sets untouched; the first real vent turns arrive with 15.7)

**Definition of done:**
- [ ] A fixture replay containing a structured `SawVentObservation` turn loads and serves through the replay API without error (the pre-fix TypeError is pinned by a regression test against the old behavior's input).
- [ ] `frontend/src/types/api.ts` is regenerated (not hand-edited) and committed; `npm run tsc:check` and the build pass with the renderer extension.
- [ ] The observation renderer displays the vent sighting (subject, room, tick) in the meeting transcript view; the three existing observation variants render byte-identically.
- [ ] Committed v4 sets still load, byte-verify, and serve unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the existing three variants end-to-end as the template: `meetings.schemas` type →
`api.schemas.*View` → `_observation_claim_view` branch → generated TS type → renderer case. The
generator (`scripts/gen_frontend_types.py`) owns the TS file; run it and commit the output. Keep the
loader mapping exhaustive-with-raise (do not add a silent default branch — the TypeError doctrine
stays; this task just teaches it the fourth variant).

## Public types this task introduces
- `api.schemas.SawVentObservationView`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-15-vent-spectator-mirror` with a title like `task 15.4.1: spectator mirror for vent observations (api dto + generated types + renderer)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H4; api/replay_loader.py:1890-1915 (`_observation_claim_view` raises TypeError on an unsupported claim); api/schemas.py (ObservationClaimView); scripts/gen_frontend_types.py (DTO → frontend type generation)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
