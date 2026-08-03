# Agent Prompt — 13.5.5 Align the ballot belief lines with the pre-vote-folded suspicion

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.5 — Align the ballot belief lines with the pre-vote-folded suspicion, anchored to the 2026-06-25 diagnosis + PR #198 review (the vote-ballot prompt carries BOTH the open-tick `rendered_memory` belief lines AND the recomputed pre-vote `suspicion_graph` kwarg, so the two suspicion numbers diverge); the PR #201 review finding (re-rendering the agent's STANDING memory is a no-op — the pre-vote fold is a throwaway manager-side `BeliefState`, never written to the agent's store: `meetings/manager.py` ~:1988 `BeliefState()` seeded + `apply_meeting_evidence_rules(phase="pre_vote")`, "discarded with the meeting"); agents/memory/store.py (`render_for_prompt` / `_build_belief_lines` / `_format_belief_score`); orchestrator/game.py (`render_memory_for_meeting`, `_memory_rerender_hook`, `unfreeze_memory_enabled`); meetings/manager.py (`MeetingParticipant`, `_collect_one_ballot`, the `suspicion_graph` it derives); [[project_substrate_cadence_doctrine]]. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-unfreeze-memory`
**Depends on:** 13.5.2, 13.5.4
**Section refs:** the 2026-06-25 diagnosis + PR #198 review (the vote-ballot prompt carries BOTH the open-tick `rendered_memory` belief lines AND the recomputed pre-vote `suspicion_graph` kwarg, so the two suspicion numbers diverge); the PR #201 review finding (re-rendering the agent's STANDING memory is a no-op — the pre-vote fold is a throwaway manager-side `BeliefState`, never written to the agent's store: `meetings/manager.py` ~:1988 `BeliefState()` seeded + `apply_meeting_evidence_rules(phase="pre_vote")`, "discarded with the meeting"); agents/memory/store.py (`render_for_prompt` / `_build_belief_lines` / `_format_belief_score`); orchestrator/game.py (`render_memory_for_meeting`, `_memory_rerender_hook`, `unfreeze_memory_enabled`); meetings/manager.py (`MeetingParticipant`, `_collect_one_ballot`, the `suspicion_graph` it derives); [[project_substrate_cadence_doctrine]]
**Complexity:** Integration
**Files in scope:**
- agents/memory/store.py
- orchestrator/game.py
- meetings/manager.py
- tests/agents/test_memory_rendering.py
- tests/orchestrator/test_meeting_integration.py
- tests/meetings/test_manager.py
**Files NOT in scope:**
- agents/memory/beliefs.py, meetings/transcript.py — the scalar belief math is unchanged; this task only renders the EXISTING per-voter `suspicion_graph` values into the belief lines, no new fold
- observation/, agents/perception.py — perception is paused mid-meeting; untouched
- agents/strategic/prompts/*.j2 — NO template / prompt-version change (the `suspicion_graph` already feeds the vote prompt; this only aligns the belief-line numbers with it)
- engine/ and the recorded replays — NO re-record; `verify_samples.sh` must stay byte-identical

The divergence the PR #198 review flagged lives ONLY in the VOTE-BALLOT prompt, which passes BOTH
the `rendered_memory` belief lines (the agent's STANDING open-tick suspicion) AND the `suspicion_graph`
kwarg (the PRE-VOTE-FOLDED suspicion). The first attempt re-rendered the agent's live memory to
"refresh" it, but that is a NO-OP: the pre-vote fold runs on a throwaway manager-side `BeliefState`
and is never written to the agent's store, and nothing else mutates the agent's persistent memory
mid-meeting, so re-rendering reproduces the open-tick string byte-for-byte. The fix renders the
ballot's belief-line SUSPICION from the SAME folded `suspicion_graph` the ballot consumes, so the two
are consistent by construction. Turn prompts have NO `suspicion_graph` kwarg (no inconsistency) and
the running evidence already reaches speakers via the transcript, so turns keep the frozen open-tick
render. Behind `AILIBI_UNFREEZE_MEMORY` (default OFF → the frozen render, byte-identical to HEAD).

Mechanism: (1) `agents/memory/store.py` — `render_for_prompt` / `_build_belief_lines` gain an optional
`suspicion_override: Mapping[PlayerId, float] | None`; when supplied, a belief line's SUSPICION value
becomes `suspicion_override.get(player_id, belief.suspicion)` (trust, alibis, last_seen, and the
open-contradictions section stay from `memory.beliefs`); default `None` → byte-identical. (2)
`orchestrator/game.py` — `render_memory_for_meeting` forwards a `suspicion_override`; the
`_memory_rerender_hook` closure becomes `Callable[[Mapping[PlayerId, float]], str]`. (3)
`meetings/manager.py` — turn sites revert to the frozen `participant.rendered_memory`; the ballot site
(`_collect_one_ballot`), after deriving the per-voter `suspicion_graph`, builds the override from it
(`{entry.player_id: entry.suspicion …}`) and calls the hook so the ballot's belief lines render the
folded values. The manager stays env-free (driven by hook presence).

**Definition of done:** flag OFF (`rerender_memory is None`) → the ballot uses the frozen open-tick
`rendered_memory`, byte-identical to pre-task HEAD; `scripts/verify_samples.sh` reconstructs both
committed sets cleanly and the existing meeting suite passes unchanged. Flag ON → for a subject the
meeting lifted pre-vote (standing suspicion below the folded value), the ballot prompt's
`rendered_memory` belief-line suspicion EQUALS that subject's `suspicion_graph` entry (the PR #198
inconsistency resolved). Turn prompts still render the frozen standing memory under the flag (no fold
at turn time). Replay-deterministic: the override is the deterministic per-voter `suspicion_graph`, so
a re-render twice is byte-identical and replays reconstruct identically. NO `.j2` / schema /
prompt-version change; `beliefs.py` / `transcript.py` / the scalar fold untouched. New tests REPLACE
the contrived live-memory-mutation test with a real ballot whose folded `suspicion_graph` differs from
the agent's standing suspicion, asserting the belief line tracks the graph under ON and the standing
value under OFF, plus determinism + flag-off byte-identity + turns-stay-frozen. Full
`scripts/check.sh` green; a 9B smoke (flag ON) holds the meeting-rate floor + byte-identical
reconstruction (operator-run).

## Implementation hint
Reuse the existing `AILIBI_UNFREEZE_MEMORY` flag, `unfreeze_memory_enabled`, and the
`_build_participants` hook-attachment; the changes are the hook SIGNATURE (now takes the override),
the `store.py` suspicion override, and the manager BALLOT wiring (drop the turn re-renders). The
override values ARE the `suspicion_graph` entries (a pure deterministic function of the recorded
transcript + the agent snapshot), so feeding them into the belief lines guarantees consistency AND
replay determinism with no new belief math — pin it with a `verify_samples` run. Default `None` on
every new parameter is the byte-identity boundary; confirm a memory-render fixture is byte-identical
with no override. `agents/memory/store.py` is now IN scope (the 13.5.4 parallel-safety boundary is
moot once 13.5.4 has merged); do NOT edit `beliefs.py` or the scalar fold.

## Integration risk
Flag ON now genuinely changes the vote-ballot prompt (the belief lines show folded suspicion), so it
is a real substrate behaviour change whose gameplay value is measured on the new model in the 9B
smoke / Phase-14 re-record — NOT gated here. Behind `AILIBI_UNFREEZE_MEMORY` (default OFF) so the
merge is the frozen path, byte-identical, existing meeting suite untouched. The hard invariant: the
override is the SAME `suspicion_graph` already passed to the vote prompt, so the belief lines and the
graph cannot disagree and the change adds no nondeterminism (no wall-clock / RNG / set-order); the
`verify_samples` reconstruction is the gate alongside `check.sh`. Supersedes the original no-op
design (the pre-vote fold is transient, so re-rendering the agent's standing memory could never
reflect it).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import agents.perception"`

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
Open a PR from branch `phase-13-5-unfreeze-memory` with a title like `task 13.5.5: align the ballot belief lines with the pre-vote-folded suspicion`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 diagnosis + PR #198 review (the vote-ballot prompt carries BOTH the open-tick `rendered_memory` belief lines AND the recomputed pre-vote `suspicion_graph` kwarg, so the two suspicion numbers diverge); the PR #201 review finding (re-rendering the agent's STANDING memory is a no-op — the pre-vote fold is a throwaway manager-side `BeliefState`, never written to the agent's store: `meetings/manager.py` ~:1988 `BeliefState()` seeded + `apply_meeting_evidence_rules(phase="pre_vote")`, "discarded with the meeting"); agents/memory/store.py (`render_for_prompt` / `_build_belief_lines` / `_format_belief_score`); orchestrator/game.py (`render_memory_for_meeting`, `_memory_rerender_hook`, `unfreeze_memory_enabled`); meetings/manager.py (`MeetingParticipant`, `_collect_one_ballot`, the `suspicion_graph` it derives); [[project_substrate_cadence_doctrine]]), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
