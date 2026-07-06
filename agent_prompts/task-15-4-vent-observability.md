# Agent Prompt — 15.4 Vent observability: make the game's hardest evidence speakable end-to-end

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.4 — Vent observability: make the game's hardest evidence speakable end-to-end, anchored to tasks/post-phase-14-clean-up.md H4; meetings/schemas.py:57-90 (the three-type observation union this task extends); meetings/transcript.py (contradiction detection + chain relevance); agents/memory/store.py:1239 (vent_witnessed is already remembered and rendered); audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 (the C3/C8 private-evidence citation catches). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-vent-observability`
**Depends on:** none
**Section refs:** tasks/post-phase-14-clean-up.md H4; meetings/schemas.py:57-90 (the three-type observation union this task extends); meetings/transcript.py (contradiction detection + chain relevance); agents/memory/store.py:1239 (vent_witnessed is already remembered and rendered); audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 (the C3/C8 private-evidence citation catches)
**Complexity:** Integration

Close the biggest measured transmission hole: witnessed impostor vents — role-PROVING evidence present
in 74/129 baseline-2 report meetings — have no structured representation in the meeting layer, so they
reach the transcript only 36/74 times as unciteable free text, invisible to the contradiction detector
and the ballot reason-id linkage. The substrate below the meeting layer already carries everything
needed (the engine witnesses vent events; the packet surfaces them witness-gated; `agents/memory/store`
records and renders them at high salience) — this task adds the missing top half: (a) a
`SawVentObservation` type in the turn observation union (subject, room, tick — deliberately NO
enter/exit phase field: the perception layer collapses both vent events into a single witnessed "vent"
action (`observation/service.py::_vent_observation_for_agent`) and memory persists only
player/room/action, so a phase field would be unobservable fabrication, and widening
`observation/`/`agents/memory/` stays out of scope), additive and backward-compatible so committed v4
transcripts still parse; (b) turn validation +
normalization in `meetings/manager.py` mirroring the existing observation paths; (c) a HARD
contradiction rule with a GROUNDING chokepoint: a structured vent observation naming a subject is
role-proving (only impostors can vent) — but speech alone must never mint hard evidence (a model that
hallucinates a vent sighting against an innocent would otherwise fabricate a STRONG flag, re-opening
the railroad class Phase 14 eliminated). The grounding input is TYPED, because the meeting boundary
today hands the manager only rendered-memory prose + a suspicion graph — nothing a validator could
check a vent claim against without parsing prompt text: the `MeetingAwareAgent` protocol gains ONE
self-channel accessor, `vent_witness_records_for_meeting() -> tuple[VentWitnessRecord, ...]` (the
agent's OWN witnessed-vent episodic records — subject, room, tick — typed in `meetings/schemas.py`
and implemented by `TacticalAgent` straight off episodic memory; firewall-clean, since an agent
reporting its own witnessed events leaks nothing). The STRONG flag fires only when the speaker's
spoken observation matches one of the speaker's own typed records (subject + room, tick within a
small tolerance) — the chokepoint NEVER parses rendered prose; a grounded observation feeds the same
strong-flag path a witnessed kill uses and is citable, since `primary_reason_id` already validates
against transcript turn ids and the observation now lives in a turn. An UNGROUNDED vent claim is
accepted as ordinary testimony (speech the voters may weigh) but raises NO flag; (d) the `qwen3_32b` set's turn/opening
templates edited IN PLACE to explicitly elicit the vent observations the rendered memory already
contains, with the version recorded by the single `PROMPT_VERSION_SETS` registry bump (`
_bespoke_versions("qwen3_32b", version="v4")` → `"v5"`) owned HERE (the Phase-14 C7 lesson: one shared
edit, owned by exactly one task; 15.5 layers onto v5 behind its dependency edge).

**Files in scope:**
- meetings/schemas.py (SawVentObservation + VentWitnessRecord + union registration; additive)
- meetings/transcript.py (vent hard-flag contradiction rule + chain/opt-in relevance treating a vent observation as relevant)
- meetings/manager.py (turn validation + observation normalization + grounding chokepoint seams region)
- agents/strategic/prompts/qwen3_32b/ (v5 set: turn/opening templates elicit structured vent observations)
- orchestrator/game.py (PROMPT_VERSION_SETS registry line — the v4 → v5 SET bump)
- orchestrator/game.py (MeetingAwareAgent protocol + TacticalAgent vent-witness accessor region — the typed grounding input; disjoint from the registry line above and from 15.8.1/15.9's regions)
- tests/meetings/test_schemas_vent.py (new)
- tests/meetings/test_transcript_vent_flag.py (new)
- tests/meetings/test_manager.py (validation-path extensions)

**Files NOT in scope:**
- observation/ + engine/ (the packet already carries witnessed vents; no firewall-surface change)
- agents/memory/ (already records + renders vent witnesses; consumed as-is)
- meetings/voting.py (the tally is untouched)
- replays/samples/ (the re-record is 15.7)
- eval/ (measurement is 15.3's instrument)

**Definition of done:**
- [ ] `SawVentObservation` round-trips through the turn schema; every committed v4 replay still parses (backward-compat pinned by a test loading a committed meeting entry).
- [ ] A fixture meeting where a voter's witnessed-vent episodic record exists produces an accepted structured vent observation through the validation path, the grounding chokepoint confirms it against the speaker's TYPED `vent_witness_records_for_meeting()` (never rendered prose), and the transcript layer raises the role-proving STRONG flag against the subject.
- [ ] Grounding is load-bearing: a fixture where a speaker FABRICATES a structured vent observation (no matching record in their own typed vent-witness channel) is accepted as testimony but raises NO flag and leaves the subject's hard-evidence state unchanged — speech alone cannot mint hard evidence.
- [ ] The `MeetingAwareAgent` protocol extension is implemented by `TacticalAgent` from episodic memory, is covered by the isinstance meeting-participant check, and is exercised by the leak suite (an agent reports only its OWN witnessed events).
- [ ] The grounded flag feeds the belief fold exactly like the witnessed-kill strong flag (same cap semantics — no new stacking channel), and a ballot's `primary_reason_id` citing the vent turn validates.
- [ ] The v5 templates elicit vent observations (prompt-fixture test: memory-with-vent renders → template output contains the elicitation instruction); this task owns the v4 → v5 SET bump in `PROMPT_VERSION_SETS` — the only later registry edit is 15.5's single vote_ballot v6 entry.
- [ ] The opt-in eligibility path treats a spoken vent observation as a relevance source (a non-speaker who was placed at the vent scene becomes eligible), consistent with the existing co-presence gate.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Model the schema/validation/flag path on the witnessed-kill lever (Task 13.5.3) — it walked the same
route from engine event to STRONG flag, and its grounding posture is the template: the hard evidence
derives from what a witness's own deterministic memory holds, with the spoken observation as the public,
citable surface. The memory side is already done: `_SALIENCE_VENT_WITNESSED` renders witnessed vents
above routine sightings, so elicitation is a prompt-template ask, not a memory change. Template work:
the prompt-set layout is FLAT — the four `.j2` templates live directly in
`agents/strategic/prompts/qwen3_32b/` and the version is a REGISTRY property, not a directory; edit the
turn/opening templates in place and bump `_bespoke_versions("qwen3_32b", version=…)` to `"v5"` in
`PROMPT_VERSION_SETS` (exactly how 14.11 shipped v4). Keep `vote_ballot.j2` byte-identical here (15.5
owns its v5 edits). The live behavioral effect (transmission 36/74 → ?) is measured at 15.7 by the 15.3
instrument — this task's DoD is the mechanism, fixture-proven, not the model's uptake.

## Public types this task introduces
- `meetings.schemas.SawVentObservation`
- `meetings.schemas.VentWitnessRecord`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Three coupling points. (a) Prompt-version provenance: the v4 → v5 SET bump is a single registry edit
owned here (the 14.11 lesson: never double-write the same entry); 15.5's later vote_ballot v6 entry is
a DIFFERENT, deliberate per-template bump behind its dependency edge — the two edits never touch the
same registry value twice. (b) Schema compat: the observation union is
additive; a strict validator change that rejects unknown types would break committed-replay loading —
the backward-compat pin is the guard. (c) Flag semantics: the vent flag must ride the EXISTING strong-
contradiction cap (`MEETING_CONTRADICTION_LIFT_CAP` + the joint cap), not add a new uncapped lift
channel — otherwise Wave 0 reintroduces the railroad class Phase 14 just eliminated. (d) The grounding
chokepoint is the whole defense against evidence-minting: if it is skipped or made advisory, a single
hallucinated observation converts speech into role-proving hard evidence against an innocent — treat
the fabricated-observation fixture as the task's most important test, and make the grounding
comparison deterministic (reconstructed memory, not LLM judgment).

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-15-vent-observability` with a title like `task 15.4: vent observability: make the game's hardest evidence speakable end-to-end`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H4; meetings/schemas.py:57-90 (the three-type observation union this task extends); meetings/transcript.py (contradiction detection + chain relevance); agents/memory/store.py:1239 (vent_witnessed is already remembered and rendered); audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 (the C3/C8 private-evidence citation catches)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
