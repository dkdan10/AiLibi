# Agent Prompt — 13.5.5 Unfreeze rendered memory mid-meeting (refresh per turn)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.5 — Unfreeze rendered memory mid-meeting (refresh per turn), anchored to the 2026-06-25 diagnosis + PR #198 review (rendered_memory frozen at meeting-open while only `suspicion_graph` is recomputed pre-vote, so the belief lines and the `suspicion_graph` kwarg diverge); orchestrator/game.py (`render_memory_for_meeting`, the one-time frozen render ~:733-743); meetings/manager.py (`MeetingParticipant` frozen dataclass ~:486-507, the turn loop + the ballot render); [[project_substrate_cadence_doctrine]] (replay determinism). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-unfreeze-memory`
**Depends on:** 13.5.2
**Section refs:** the 2026-06-25 diagnosis + PR #198 review (rendered_memory frozen at meeting-open while only `suspicion_graph` is recomputed pre-vote, so the belief lines and the `suspicion_graph` kwarg diverge); orchestrator/game.py (`render_memory_for_meeting`, the one-time frozen render ~:733-743); meetings/manager.py (`MeetingParticipant` frozen dataclass ~:486-507, the turn loop + the ballot render); [[project_substrate_cadence_doctrine]] (replay determinism)
**Complexity:** Integration
**Files in scope:**
- orchestrator/game.py
- meetings/manager.py
- tests/orchestrator/test_meeting_integration.py
- tests/meetings/test_manager.py
**Files NOT in scope:**
- agents/memory/store.py (`render_for_prompt`) — UNCHANGED; this task CALLS the renderer per turn, it does not edit it, which keeps it file-disjoint from 13.5.4
- agents/memory/beliefs.py, meetings/transcript.py — disjoint from 13.5.3
- observation/, agents/perception.py — disjoint from 13.5.4
- the scalar fold and the §4.6 gate value — untouched
- engine/ and the recorded replays — NO re-record; `verify_samples.sh` must stay byte-identical

Today `render_memory_for_meeting` runs ONCE per participant at meeting open
(`orchestrator/game.py` ~:733-743) into the frozen `MeetingParticipant.rendered_memory`; every turn
AND the ballot reuse that open-tick snapshot, while the pre-vote fold updates the `suspicion_graph`
separately — so a speaker's later turn/ballot reads STALE belief lines that diverge from the
recomputed `suspicion_graph` (the PR #198 review inconsistency). This task re-renders a participant's
memory before their later turns and their ballot, from the CURRENT (pre-vote-folded) `BeliefState` +
episodic, so the belief lines are internally consistent with the suspicion graph the ballot reads.
HIGHEST RISK in Wave C: the per-turn re-render MUST be replay-deterministic (a pure function of the
deterministic `BeliefState` + episodic at that point, with the renderer's existing stable salience
tie-breaks), so `verify_samples.sh` reconstructs the committed replays byte-identically. Behind
`AILIBI_UNFREEZE_MEMORY` (default OFF → the one-time frozen render, byte-identical to HEAD). LAND
LAST (after 13.5.2–13.5.4) so the re-render is exercised against the real richer content.

**Definition of done:** with the flag ON, a participant's `rendered_memory` is recomputed before each
of their turns and their ballot from the current `BeliefState` / episodic (not the open-tick freeze),
so the rendered belief lines match the pre-vote `suspicion_graph` the ballot consumes; the
`MeetingParticipant` carries a refresh mechanism (a re-render hook / per-turn recompute) rather than a
single frozen string, without breaking the existing frozen-default call path. Replay-deterministic:
run twice → byte-identical; `scripts/verify_samples.sh` reconstructs all committed samples cleanly.
Flag OFF → the one-time frozen render, byte-identical to pre-task HEAD (the existing meeting suite
passes unchanged). NO `agents/memory/store.py` edit (the renderer is called, not changed — the
parallel-safety boundary with 13.5.4). New tests cover the refresh (a later turn sees updated belief
lines consistent with the suspicion graph), determinism (twice → identical; `verify_samples`), and
flag-off byte-identity. Full `scripts/check.sh` green; a 9B smoke (flag ON) holds the meeting-rate
floor and byte-identical reconstruction.

## Implementation hint
The frozen-default path is the byte-identity boundary: keep `MeetingParticipant.rendered_memory` as
the open-tick render when the flag is OFF, and ONLY when ON recompute it per the speaker's turn via a
re-render hook (a callable the participant holds, or a manager-side recompute that reads the live
`BeliefState`). The recompute calls the UNCHANGED `agents.memory.store.render_for_prompt` — do not
edit the renderer. Determinism is the hard part: the re-render must read only the deterministic
stored state at that point (no wall-clock, no RNG, no set iteration order), so a replay rebuilds the
identical string; pin it with a `verify_samples` run in the task. Because the per-meeting fold that
moves suspicion pre-vote already exists, the new content the re-render surfaces is just the
up-to-date belief lines — no new belief math here.

## Integration risk
The replay-determinism hazard is the reason this lands LAST. Re-rendering mid-meeting changes WHEN a
speaker sees its belief lines; if the re-render is not a pure function of the deterministic stored
state, a replay diverges and `verify_samples` breaks — so that check is the hard gate, not just
`check.sh`. Behind `AILIBI_UNFREEZE_MEMORY` (default OFF) so the merge is the frozen path,
byte-identical, with the existing meeting suite untouched; gameplay value is measured on the new
model in Phase 14. File-disjoint from 13.5.3 (`beliefs`/`transcript`) and 13.5.4 (`observation`/
`store`) — it touches only `game.py` + `manager.py` — so it can run in parallel, though landing it
after 13.5.3/13.5.4 exercises the re-render against the real richer memory. No re-record (smoke only).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import agents.perception"`

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
Open a PR from branch `phase-13-5-unfreeze-memory` with a title like `task 13.5.5: unfreeze rendered memory mid-meeting (refresh per turn)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 diagnosis + PR #198 review (rendered_memory frozen at meeting-open while only `suspicion_graph` is recomputed pre-vote, so the belief lines and the `suspicion_graph` kwarg diverge); orchestrator/game.py (`render_memory_for_meeting`, the one-time frozen render ~:733-743); meetings/manager.py (`MeetingParticipant` frozen dataclass ~:486-507, the turn loop + the ballot render); [[project_substrate_cadence_doctrine]] (replay determinism)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
