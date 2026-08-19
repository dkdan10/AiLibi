# Agent Prompt — 6.4 Wire the contradiction-detection subsystem into live meetings

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.4 — Wire the contradiction-detection subsystem into live meetings, anchored to Audit J-J-1, J-J-9, J-J-4, A-A-4; DESIGN.md §5.4, §6.3, §6.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-contradiction-detection-wiring`
**Depends on:** 6.3 merged
**Section refs:** Audit J-J-1, J-J-9, J-J-4, A-A-4; DESIGN.md §5.4, §6.3, §6.4
**Complexity:** Integration

The contradiction detector, belief Rule 2, and the perception belief-update path
all exist but are dead in live play — this is the hard prerequisite for any
Phase 7 "smarter agents" work, and this task makes the designed intelligence
actually function. Specifically: `detect_contradictions` (the whole §5.4/§6.4
subsystem) is invoked only by tests; `MeetingManager.run` hardcodes
`contradictions=()` and threads that empty tuple into every statement prompt,
vote prompt, and persisted result, so no agent ever sees a contradiction flag
(audit J-J-1, confirmed: all four meeting-bearing samples show contradictions=0).
Belief Rule 2's write-paths (`record_contradiction`, `adjust_suspicion`) are
defined and unit-tested but never called in production (J-J-4). And
`AgentRuntime._perceive` (`agents/runtime.py:56`) calls `ingest_packet` without a
`BeliefState`, so even the two implemented belief rules (1 and 4) are dormant in
headless games (A-A-4). `PlayerId` subject matching uses a hardcoded placeholder
allowlist, so non-roster subjects silently fail to match (J-J-9) — load-bearing
once the detector is live.

This task wires the existing pieces; it does NOT add new detector kinds (temporal
impossibility, body-discovery timing, mutual-witness — those are Phase 7,
J-J-2). Scope:

1. Wire `detect_contradictions` into `MeetingManager.run`: recompute from the
   transcript-so-far before each accusation round and before voting, thread the
   live tuple into the statement and ballot prompts and the persisted result.
2. Replace the hardcoded subject allowlist with roster-aware normalization: map
   self-placeholders to the speaker id and reject/flag any subject not in the
   living-player roster, so contradiction matching never silently drops a claim.
3. Implement belief Rule 2: on a detected contradiction, call
   `record_contradiction` + `adjust_suspicion` so the vote suspicion graph
   reflects detected lies.
4. Pass a `BeliefState` into `AgentRuntime._perceive` → `ingest_packet` so the
   already-implemented Rules 1 and 4 run in headless games.

This changes meeting behavior and therefore replay determinism, so fixtures are
regenerated — the SECOND and last fixture-regenerating task, sequenced after 6.3.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py
- agents/memory/beliefs.py
- agents/runtime.py
- agents/perception.py
- tests/meetings/test_manager.py
- tests/agents/test_beliefs_wiring.py
- replays/samples/MANIFEST.md
- replays/samples/

**Files NOT in scope:**
- meetings/schemas.py (reuse; do not reshape)
- engine/ (win_conditions.py was Task 6.3)
- api/
- frontend/
- eval/
- agents/strategic/prompts/ (no new detector-kind prompts; that is Phase 7)
- DESIGN.md (reconciled in the design thread)

**Definition of done:**
- [ ] `MeetingManager.run` calls `detect_contradictions` over the transcript-so-far before each accusation round and before voting, threads the resulting tuple into the statement prompts, the ballot prompts, and the persisted meeting result; `contradictions=()` is no longer hardcoded (J-J-1).
- [ ] Subject matching is roster-aware: self-placeholders map to the speaker id and any subject not in the living-player roster is rejected or explicitly flagged, replacing the hardcoded allowlist (J-J-9). A test covers a non-roster subject (e.g. `p-0`/`p-99`) being handled deterministically rather than silently dropped.
- [ ] Belief Rule 2 is wired: on a detected contradiction the meeting/runtime path calls `record_contradiction` + `adjust_suspicion`, and a test asserts the vote suspicion graph reflects a detected contradiction (J-J-4).
- [ ] `AgentRuntime._perceive` passes a `BeliefState` into `ingest_packet` so belief Rules 1 and 4 run in headless games; a test asserts a body-proximity (Rule 1) or witnessed-vent (Rule 4) update occurs in a headless run (A-A-4).
- [ ] No new detector kinds are added (temporal/body-timing/mutual-witness are Phase 7); `_iter_sightings` is extended to index statement-borne claims ONLY insofar as the existing `alibi_conflict`/`alibi_vs_sighting` detectors need it to see statement claims — no new detector enum values.
- [ ] The committed `replays/samples/` fixtures are regenerated with the refresh-samples workflow and `MANIFEST.md` updated; determinism / byte-identical replay tests pass; at least one regenerated meeting-bearing sample now shows a non-zero contradiction count where the transcript warrants it.
- [ ] The leak tests still pass — contradiction flags and belief updates introduce no cross-player role or engine-state exposure in any observation packet or rendered prompt.
- [ ] The PR `## Decisions` block records: that this is wiring-only (no new detector kinds); the `BeliefState` threading approach through `_perceive`; and that fixtures were regenerated once, after Task 6.3.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (the agents↔engine firewall is preserved; `BeliefState` is an agents-side type).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `meetings/transcript.py` (`detect_contradictions` at line 97, `_iter_
sightings`, and the exported detector kinds), `meetings/manager.py` (the `run`
loop, the `contradictions=()` hardcode, and the subject-allowlist around
line 124), `agents/memory/beliefs.py` (Rule 2 write-paths `record_contradiction`
/`adjust_suspicion`, around line 36), and `agents/runtime.py:56` →
`agents/perception.py:58` (the `ingest_packet` call missing the `beliefs=`
argument). Wire in the order the audit's prerequisite chain implies: detector
into `run` → roster-aware subject normalization → Rule 2 on detected
contradictions → `BeliefState` into `_perceive`. Keep the agents↔engine firewall
intact: `BeliefState` and belief updates are agents-side; do not import engine
types into `agents/`. Regenerate fixtures via the refresh-samples workflow, never
by hand, and confirm at least one meeting-bearing sample now records
contradictions so the wiring is demonstrably live (not just present). This is the
second and final fixture-regenerating task — it depends on 6.3 so the two
regenerations never interleave.

## Integration risk

This is the highest-blast-radius task in the phase: it changes agent-visible
meeting inputs, belief state, and replay determinism at once.

- **Behavior is now live where it was dead.** Agents that previously saw
  `contradictions=()` now see real flags and update suspicion. Expect meeting
  transcripts, ballots, and outcomes to shift; the regenerated fixtures capture
  the new behavior. Verify the determinism tests pass on the new set.
- **Firewall preservation is non-negotiable.** `BeliefState` threading runs
  entirely on the agents side; an accidental `engine/` import in `agents/` fails
  `lint-imports` and breaks the project's load-bearing invariant. Keep engine
  translation in orchestrator-owned code.
- **Leak surface re-check.** Contradiction flags are derived from transcript
  statements (already public to the meeting) and belief updates are per-agent;
  confirm no rendered prompt or observation packet now embeds another player's
  role or engine state. The leak tests must stay green.
- **Serial with Task 6.3.** Both regenerate `replays/samples/`; 6.4 depends on
  6.3 so the regenerations stay one-at-a-time and the close-gate can attribute
  each metric delta to its own change.
- **No scope creep into Phase 7.** Adding new detector kinds or impostor
  vent/sabotage here would entangle capability work with the wiring repair and
  blur the metric attribution. Keep strictly to wiring the existing pieces.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import engine.win_conditions"`

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
Open a PR from branch `phase-6-contradiction-detection-wiring` with a title like `task 6.4: wire the contradiction-detection subsystem into live meetings`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit J-J-1, J-J-9, J-J-4, A-A-4; DESIGN.md §5.4, §6.3, §6.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
