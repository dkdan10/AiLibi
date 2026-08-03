# Agent Prompt — 11.3 Kill-memory privileged self-channel (legibility)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-11.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 11.3 — Kill-memory privileged self-channel (legibility), anchored to DESIGN.md §1.3 (firewall), §6.2 (memory rendering); experiments/lab/report-memory-fix-probe.md. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-11.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-11-kill-memory`
**Depends on:** 11.1 (shares the SelfView/packet/service/perception self-channel seam; sequence after it)
**Section refs:** DESIGN.md §1.3 (firewall), §6.2 (memory rendering); experiments/lab/report-memory-fix-probe.md
**Complexity:** Integration

An impostor's own kill is never recorded as a kill: `engine/rules.py:96` excludes the actor from its own
kill's witnesses, so `observation/service.py:306-307` (a kill is observed only `if agent_id in
event.witnesses`) never logs it, and the body it created surfaces through the ordinary `saw_body` channel as
"You discovered {victim}'s body in {room}" (`agents/memory/store.py:493`) — the killer narrates finding the
body it made. Surface the kill as an explicit PRIVILEGED self-channel line. SCOPE HONESTY: the memory-fix
probe FALSIFIED this as a survival/deflection lever (self-flags 17→17 — they come from OTHERS' sightings the
impostor never saw, not its own memory); ship it for LEGIBILITY only and claim NO interestingness-score
movement from it. The channel MUST be on `SelfView`, not `PlayerView` (VERIFIED: `eval/leak_test.py:115-128`
requires every visible kill/vent action to be witness-permitted, and the killer is excluded from its own
witnesses — a PlayerView kill action would fail the leak test; `SelfView` is the established privileged
channel where role/fellow_impostor_ids live).

**Files in scope:**
- observation/packet.py (new `OwnKillView{victim_id: PlayerId, room: RoomId}`; `SelfView.own_kill: OwnKillView | None`. `victim_id` is leak-allowed per the BodyView precedent; no role-bearing field names)
- observation/service.py (populate `own_kill` in the KilledEvent path ONLY when `event.actor == agent_id`, WITHOUT the witness gate — by construction it is never in any other agent's packet)
- agents/perception.py (ingest a new `EVENT_OWN_KILL` episodic event from `packet.self_state.own_kill`)
- agents/memory/store.py (render "[tick N] You (IMPOSTOR) killed {victim} in {room}." at a new salience above witnessed-kill; SUPPRESS the self-victim `saw_body` line — collect own-kill victim ids up front like the existing body-sightings set and skip the "discovered ... body" render for the killer's own victim)
- tests/observation/test_leak_property.py + tests/test_firewall.py (every crewmate packet has `own_kill is None`; the kill string is produced only in store rendering, never in packet JSON)
- tests/agents/test_memory_store.py (the killer's memory shows the kill line and NOT the self-victim "discovered body" line)

**Files NOT in scope:**
- engine/** (the witness-exclusion is correct as-is; this task reads the KilledEvent, it does not change kill resolution)
- agents/tactical/** , agents/strategic/prompts/** , meetings/**
- replays/samples/**, tests/fixtures/** (re-record is 11.4)

**Definition of done:**
- The killer's rendered memory reads "You (IMPOSTOR) killed {victim} in {room}" for its own victim and no
  longer renders that victim as a discovered body; other bodies render normally.
- `SelfView.own_kill` is populated only for the actor; the leak sweep + firewall test confirm crewmate (and
  fellow-impostor) packets never carry another agent's `own_kill`, and no packet JSON contains the substring
  "impostor" outside `self_state.role`.
- `bash scripts/check.sh` green.

## Implementation hint
Model `OwnKillView` exactly on the existing privileged self-state pattern (`SelfView.role` /
`fellow_impostor_ids`) — populated for the entitled recipient only, never mirrored into `PlayerView`. In the
store, suppress the self-victim body line by reusing the up-front body-sightings collection rather than a
second pass, so the salience ordering and dedup stay intact.

## Public types this task introduces
- `observation.packet.OwnKillView`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
This shares packet.py/service.py/perception.py with 11.1 — the depends-on edge above serializes them; keep
`own_kill` orthogonal to `in_vent`. It changes recorded bytes for policy-driven runs (11.4) but the
event-driven memory golden (`impostor_minimal.*`) is unaffected (no own-kill event in its hand-authored
events) — grep for any observation/packet golden pinning the SelfView shape and regenerate if found.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-11-kill-memory` with a title like `task 11.3: kill-memory privileged self-channel (legibility)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3 (firewall), §6.2 (memory rendering); experiments/lab/report-memory-fix-probe.md), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
