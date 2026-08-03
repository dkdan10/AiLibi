# Agent Prompt — 13.5.3 Witnessed kill becomes real evidence (witness belief + kill-scene STRONG flag)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.3 — Witnessed kill becomes real evidence (witness belief + kill-scene STRONG flag), anchored to the 2026-06-25 design-thread eyewitness-strength decision (a first-hand kill view makes the WITNESS near-certain); agents/memory/beliefs.py (`apply_observation_rules` Rule 4 vent precedent + `VENTING_SUSPICION_DELTA`, `apply_contradiction_rule`); observation/service.py (the witness-gated kill stamp `PlayerView.action == "kill"`, ~:351); meetings/transcript.py (`_detect_alibi_vs_physical` / `reconstruct_stated_paths` ~:833 / `detect_contradictions` ~:922 / `PHYSICAL_CONTRADICTION_MIN_VOICES` ~:517 / `WEAK_REASON_LONE_PHYSICAL` ~:502 / `triggering_body_rooms` / `is_weak_contradiction` ~:610); audits/workflows/extract_gameplay_facts.py (the $0 R7 re-extraction); [[project_ejection_suspicion_principle]]. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-witnessed-kill`
**Depends on:** 13.5.1
**Section refs:** the 2026-06-25 design-thread eyewitness-strength decision (a first-hand kill view makes the WITNESS near-certain); agents/memory/beliefs.py (`apply_observation_rules` Rule 4 vent precedent + `VENTING_SUSPICION_DELTA`, `apply_contradiction_rule`); observation/service.py (the witness-gated kill stamp `PlayerView.action == "kill"`, ~:351); meetings/transcript.py (`_detect_alibi_vs_physical` / `reconstruct_stated_paths` ~:833 / `detect_contradictions` ~:922 / `PHYSICAL_CONTRADICTION_MIN_VOICES` ~:517 / `WEAK_REASON_LONE_PHYSICAL` ~:502 / `triggering_body_rooms` / `is_weak_contradiction` ~:610); audits/workflows/extract_gameplay_facts.py (the $0 R7 re-extraction); [[project_ejection_suspicion_principle]]
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- meetings/transcript.py
- tests/agents/test_beliefs.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- meetings/schemas.py, the LLM output schema, and agents/strategic/prompts/*.j2 — (b) REUSES the existing `alibi_vs_physical` kind + `reconstruct_stated_paths` with a kill-scene marker, NOT a new observation type or contradiction kind, so there is NO LLM-output-schema change and NO prompt-version-bump cascade. Literally surfacing "I witnessed the kill act" as a new public structured claim is the heavier alternative below; deferred.
- the scalar vote tally and the §4.6 gate value — unchanged; (a) moves suspicion through the existing perception rule, (b) through the unchanged `apply_contradiction_rule`
- engine/ and the recorded replays — re-extraction + a smoke only; NO re-record (the Phase-13 $0 R7 gate)
- 13.5.4 (movement), 13.5.5 (unfreeze)

A witnessed kill is the single most conclusive act in the game (only impostors kill), yet it moves
NO structured belief today: `apply_observation_rules` has rules for a witnessed VENT (+0.5,
"almost certain") and body-proximity (+0.2) but NONE for a witnessed KILL, so a crewmate who
directly sees the kill weights it BELOW a vent — backwards — and relies on the LLM reading a memory
line. This task makes a witnessed kill real evidence in two separable halves (land + validate (a)
first; (b) is the heavier detector change):

(a) WITNESS BELIEF — a perception-time rule keyed on the existing witness-gated stamp: when the
agent's packet carries a `PlayerView` with `action == "kill"`, lift the killer's suspicion over the
§4.6 gate to near-certain (`WITNESSED_KILL_SUSPICION_DELTA`, >= `VENTING_SUSPICION_DELTA`, pinning
to the ~1.0 clamp). Team-internal firewall (§4.7): an impostor that witnessed a TEAMMATE's kill
accrues NO suspicion against the teammate (exclude `self_state.fellow_impostor_ids`), mirroring
Rule 1's co-presence guard. The witness reasons from its OWN memory — unforgeable, no corroboration
needed (the owner decision: a first-hand kill view IS conclusive for the witness). The bump
persists into the meeting suspicion graph, so the witness votes the killer over-gate.

(b) MEETING PROPAGATION — a kill-scene intensification of the 13.4 `alibi_vs_physical` detector:
when independent public sightings place the accused at the BODY's room within the kill window (the
kill scene, from `triggering_body_rooms` / the `found_body` trigger) and the accused's stated alibi
places them elsewhere, mint a STRONG contradiction that crosses listeners' gate via the unchanged
`apply_contradiction_rule`. REUSE `reconstruct_stated_paths` + the existing kind; add a kill-scene
marker only. **(b)-strictness = STRICT (owner-LOCKED 2026-06-26):** a SINGLE kill-scene placement
INFORMS (sub-gate `WEAK_REASON_*`) and needs a second independent source (another placement, or the
body+placement two-source conjunction) to cross — so a FABRICATED kill-accusation cannot railroad a
crewmate ("no single signal ejects" on the forgeable spoken channel). The permissive
single-witness-convicts-listeners alternative was REJECTED. (a) is unconditional regardless — the
witness believes on its own first-hand kill; (b)-strictness only governs whether that testimony
moves OTHER crewmates.

Both halves behind `AILIBI_WITNESSED_KILL_EVIDENCE` (default OFF → byte-identical to HEAD).

**Definition of done:** (a) a witnessed kill (`PlayerView.action == "kill"`) lifts the witness's
suspicion of the killer over the §4.6 gate (near-certain), teammate-firewalled (an impostor
witnessing a teammate kill accrues nothing), and the bump persists into the meeting suspicion
graph; with both a vent and a kill witnessed, the kill weighs >= the vent. (b) a $0 re-extraction of
the committed replays shows the kill-scene `alibi_vs_physical` flag firing STRONG for an accused
placed at the kill scene with a contradicting alibi, every STRONG flag role-gated to a true impostor
(ZERO STRONG-on-crewmate), and the R4 wrong-ejection floor holds; (b)-strictness is STRICT
(owner-locked): a lone kill-scene placement is sub-gate and requires a second independent source to
cross. NO new LLM
observation type / contradiction kind / `.j2` edit / prompt-version bump. Flag OFF → every belief
render, suspicion graph, and re-extraction is byte-identical to pre-task HEAD and committed replays
reconstruct identically (`scripts/verify_samples.sh`). New tests cover (a) (kill → over-gate;
teammate firewall; kill >= vent) and (b) (kill-scene STRONG vs the strictness gate; lone/weak
sub-gate; no STRONG-on-crewmate). Full `scripts/check.sh` green; a 9B smoke (flag ON) lights R7 on
kill-scene flags with zero STRONG-on-crewmate and the wrong-ejection floor held.

## Implementation hint
(a) mirror the vent branch in `apply_observation_rules` exactly — a new `action == "kill"` clause
applying `WITNESSED_KILL_SUSPICION_DELTA` (>= 0.5, lands at the 1.0 clamp) — but ALSO read
`observation.self_state.fellow_impostor_ids` and SKIP a teammate killer (the vent branch needs no
such guard; the kill guard is load-bearing because an impostor frequently co-locates with a
teammate's kill). The rule runs at perception via `ingest_packet`, so the bump persists into the
stored `BeliefState` the meeting graph reads. (b) extend `_detect_alibi_vs_physical`: when a
contradicting placement falls in a `triggering_body_rooms` room within the kill window, classify it
kill-scene and apply the LOCKED strict rule: a single kill-scene placement stays sub-gate; STRONG
requires `PHYSICAL_CONTRADICTION_MIN_VOICES` or a body+placement two-source conjunction. Add a
`KILL_SCENE` reason read by `is_weak_contradiction` so the delta routes through the unchanged
`apply_contradiction_rule` — no new kind, no schema/api/frontend change. Validate by re-extracting
the committed replays (R7 up; zero STRONG-on-crewmate; R4 floor) — NO re-record. Keep `agents/`
engine-free.

## Public types this task introduces
- `agents.memory.beliefs.WITNESSED_KILL_SUSPICION_DELTA`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
Two suspicion paths gain a new source. (a) is low-risk (a pure perception rule on existing
witness-gated data; the only subtlety is the teammate firewall, which a test must pin). (b) touches
the live contradiction detector, so the hard guards are: ZERO STRONG-on-crewmate on re-extraction
(a kill-scene flag must never fire on an innocent — verify role-gated), the R4 wrong-ejection floor
holds, and the (b)-strictness keeps a lone forgeable kill-accusation sub-gate. Behind
`AILIBI_WITNESSED_KILL_EVIDENCE` (default OFF) so the merge is byte-identical and the existing suite
+ committed replays are untouched; gameplay value is measured on the new model in Phase 14's
re-record. No re-record here (the $0 R7 re-extraction is the gate, per the Phase-13 cadence).

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
Open a PR from branch `phase-13-5-witnessed-kill` with a title like `task 13.5.3: witnessed kill becomes real evidence (witness belief + kill-scene strong flag)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 design-thread eyewitness-strength decision (a first-hand kill view makes the WITNESS near-certain); agents/memory/beliefs.py (`apply_observation_rules` Rule 4 vent precedent + `VENTING_SUSPICION_DELTA`, `apply_contradiction_rule`); observation/service.py (the witness-gated kill stamp `PlayerView.action == "kill"`, ~:351); meetings/transcript.py (`_detect_alibi_vs_physical` / `reconstruct_stated_paths` ~:833 / `detect_contradictions` ~:922 / `PHYSICAL_CONTRADICTION_MIN_VOICES` ~:517 / `WEAK_REASON_LONE_PHYSICAL` ~:502 / `triggering_body_rooms` / `is_weak_contradiction` ~:610); audits/workflows/extract_gameplay_facts.py (the $0 R7 re-extraction); [[project_ejection_suspicion_principle]]), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
