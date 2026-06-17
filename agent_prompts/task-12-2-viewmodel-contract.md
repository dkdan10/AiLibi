# Agent Prompt — 12.2 View-model contract v1 + cheap projections

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.2 — View-model contract v1 + cheap projections, anchored to design/phase-12/stage-1-design.md §7, §9.5; design/phase-12/stage-0-understand.md §0.5, §3, §4; the firewall + identity rules in design/phase-12/claude-design-brief.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-viewmodel-contract`
**Depends on:** none
**Section refs:** design/phase-12/stage-1-design.md §7, §9.5; design/phase-12/stage-0-understand.md §0.5, §3, §4; the firewall + identity rules in design/phase-12/claude-design-brief.md
**Complexity:** Integration
**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- frontend/src/types/api.ts
- scripts/gen_frontend_types.py
- experiments/lab/rubric_score.py
- tests/api/test_view_model.py
**Files NOT in scope:**
- frontend components and the Pixi render layer — Waves B and C
- the per-tick per-agent visibility projection + UI leak test — Task 12.3
- engine/ and the recorded replays — every change here is a load-time projection; NO re-record

Introduce a `viewModelVersion` on the served payload and generate `frontend/src/types/api.ts` from the Pydantic schemas
(kill the hand-mirror and its documented drift). Add these additive projections, all from state the loader already
re-walks: a per-meeting belief snapshot plus an `Error` projection vs `PlayerView.role`; a `VentEventView` (enter/exit)
carried as a `TickEventView` member (from the engine's `VentEntered`/`VentExited`); `killed_by` from `state.bodies`;
`ContradictionView.weak: bool` (+ severity) via `is_weak_contradiction()`; a per-meeting §4.6
`gate{leader, leader_max_confidence, threshold, passed}` recomputed from persisted `ballots[].confidence` (drop the
un-persisted `rendered_max` — the real rule is plurality + at least one leader ballot ≥ 0.6, tie → SKIP, NOT a
vote-count majority); parsed `BallotView.rewrite_reasons[]` + `rationale_text_clean` (import the marker constants from
`meetings/voting.py` + `meetings/manager.py`, never hardcode; special-case `VOTE_PARSE_DEFAULT` = the whole string);
reactor `repair_progress` per room + `remaining_ticks`; a per-tick crew/impostor advantage series; and a per-set rubric
surface (`/eval/rubric`) with a staleness guard (compare the rubric `git_head` to the served set's MANIFEST sha) PLUS
its producer — a regen step that re-runs `experiments/lab/rubric_score.py`, stamps `git_head`, and co-locates
`results-rubric-score.json` per served set, wired into the refresh/re-record path so the happy path stays fresh (not only
banner-guarded when stale).
Surface the already-in-DTO render-ready fields (`current_action`, `winner_reason`, task-clock totals, `failed_calls`,
typed `conversion`/`gate_metrics`). Document why `SuspicionGraphView` stays dead (beliefs are timeless). Identity-palette
alignment, the one backend touch: replace `api/replay_loader.py::_COLOR_PALETTE` — today a 12-colour rainbow (`#e6194b`
red / `#ffe119` yellow / `#4363d8` blue / `#f58231` orange …) that collides with the reserved channels (red=kill,
amber=suspicion, blue=trust) — with the Playful identity palette from the committed
`design/phase-12/tokens-seed.md` (the SAME `identity[]` list 12.1 transcribes into `tokens.ts`, so the two parallel tasks
cannot drift on it) so `PlayerView.color` matches it and DTO ↔ design never drift. Colours are derived at load, so this is a loader-only change with NO
replay re-record; keep it firewall-clean (identity never encodes guilt).
**Definition of done:** the served payload carries `viewModelVersion`; `frontend/src/types/api.ts` is generated from the
Pydantic schemas (no hand-mirror); every new surface is served, cached, and covered by a test; the §4.6 gate is
per-meeting and `rendered_max` is gone; the rubric surface is per-set and staleness-guarded; `PlayerView.color` serves
the Playful identity palette (no rainbow) with the leak/determinism tests still green and NO re-record; the §4.6 gate has a CONSISTENCY test (the recomputed leader +
`passed` matches each meeting's actual outcome / `ejected_player_id` across the committed 9p2i set — not just a formula
unit test); the rubric has a regen step (re-run + `git_head` stamp, per-set), not only the staleness banner; a codegen
FIDELITY gate round-trips a real served payload through the generated TS types (compiles + narrows the discriminated
unions); `scripts/check.sh` is green.

## Implementation hint
do every projection inside the existing `_walk`/re-walk so nothing new is persisted; reuse
`is_weak_contradiction()` and the meeting marker constants by import; for the TS codegen prefer a small script over a
heavy dependency, wired into `check.sh` so drift fails CI.

## Public types this task introduces
- `api.schemas.BeliefFrameView`
- `api.schemas.VentEventView`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
the Pydantic→TS codegen pipeline is new — its riskiest spot is discriminated-union narrowing (`TickEventView` ⊃
`VentEventView`/`KillEventView`/…), so a fidelity gate round-trips a real payload through the generated types, and if the
bespoke script can't narrow reliably, fall back to `openapi-typescript` off FastAPI's OpenAPI schema; it must be
deterministic and run in CI; the
`_COLOR_PALETTE` change flows into `PlayerView.color`, so re-run the leak/determinism tests (it is colour-only and
firewall-neutral); the §4.6 recompute must match the engine gate exactly (plurality + ≥ 0.6, tie → SKIP), not the
mock's "majority".

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
Open a PR from branch `phase-12-viewmodel-contract` with a title like `task 12.2: view-model contract v1 + cheap projections`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §7, §9.5; design/phase-12/stage-0-understand.md §0.5, §3, §4; the firewall + identity rules in design/phase-12/claude-design-brief.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
