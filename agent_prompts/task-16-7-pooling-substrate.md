# Agent Prompt — 16.7 Pooling substrate: typed grounded vouching + the whereabouts claim

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.7 — Pooling substrate: typed grounded vouching + the whereabouts claim, anchored to meetings/schemas.py:56-149 (the observation union + VentWitnessRecord — the pattern to generalize); orchestrator/game.py:2369-2403 (the vent accessor to near-copy); meetings/transcript.py:1053-1156 (reconstruct_stated_paths — where whereabouts integrate) + :2251-2309 (the vent grounding chokepoint); agents/memory/beliefs.py:387-423 (CORROBORATION_SUSPICION_DELTA — the channel vouching feeds). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-pooling-substrate`
**Depends on:** 16.3
**Section refs:** meetings/schemas.py:56-149 (the observation union + VentWitnessRecord — the pattern to generalize); orchestrator/game.py:2369-2403 (the vent accessor to near-copy); meetings/transcript.py:1053-1156 (reconstruct_stated_paths — where whereabouts integrate) + :2251-2309 (the vent grounding chokepoint); agents/memory/beliefs.py:387-423 (CORROBORATION_SUSPICION_DELTA — the channel vouching feeds)
**Complexity:** Integration

Make sightings speakable-and-checkable the way 15.4 made vents speakable-and-checkable — with the
polarity inverted. Two halves. (a) **Typed grounded vouching**: a `SightingRecord`
(subject, room, tick, co_present) beside `VentWitnessRecord`; a `sighting_records_for_meeting()`
accessor on the `MeetingAwareAgent` protocol implemented by `TacticalAgent` off the same episodic
rows the vent accessor reads (drop the vent-action filter); `MeetingParticipant.sighting_records`
threading; and a grounding chokepoint in the transcript layer: a spoken `SawPlayerObservation`
that matches the SPEAKER's own typed record (subject + room, tick within tolerance) becomes a
GROUNDED VOUCH — which feeds the existing `corroborated` set (the −0.05 exculpation channel),
NEVER a strong flag and NEVER the dead trust field. The asymmetry with vents is the design:
grounding a sighting proves the speaker honestly reported what they saw — it does not prove the
subject innocent, so it earns the weak exculpation the corroboration channel already prices. An
ungrounded vouch stays ordinary testimony. (b) **The whereabouts claim**: `WhereaboutsClaim`
(room, tick — SELF-placement only; vouching for OTHERS needs no new kind, `SawPlayerObservation`
already expresses it) as the additive fifth observation-union member, validated in the manager's
turn path and integrated into `reconstruct_stated_paths` — answering roll-call places you on the
public record (removing you from 16.8's absence set), and LYING in it creates exactly the
contradiction-detectable material the alibi rules already prosecute.

**Files in scope:**
- meetings/schemas.py (observation-union + SightingRecord + WhereaboutsClaim region — disjoint from 16.5's ballot region)
- orchestrator/game.py (protocol accessor + TacticalAgent implementation region — the vent-accessor sibling; disjoint from 16.9's persona region and the registry line)
- meetings/manager.py (turn-validation + participant-threading region — disjoint from 16.5's ballot-validation and 16.6's guard regions)
- meetings/transcript.py (vouch grounding chokepoint + whereabouts stated-paths integration)
- agents/memory/beliefs.py — NOT edited; the grounded vouch reaches the existing corroborated-set argument through the manager's evidence derivation (listed here to declare the negative explicitly)
- tests/meetings/test_schemas_pooling.py (new)
- tests/meetings/test_vouch_grounding.py (new: grounded feeds corroboration; ungrounded is testimony; fabricated vouch never exculpates)
- tests/orchestrator/test_sighting_accessor.py (new: accessor determinism + protocol coverage, incl. the meeting-double sweep the 15.4 precedent taught)

**Files NOT in scope:**
- meetings/voting.py (tally untouched)
- agents/memory/beliefs.py (no new constant, no new channel — the corroboration delta is consumed as-is; the absence delta is 16.8's)
- agents/strategic/prompts/ (roll-call elicitation is 16.15's; this task is mechanism, fixture-proven)
- api/ + frontend/ (the spectator mirror is 16.7.1's)

**Definition of done:**
- [ ] `SightingRecord` and `WhereaboutsClaim` round-trip their schemas; every committed replay still parses (additive union, backward-compat pinned by loading a committed meeting entry).
- [ ] The accessor is deterministic and self-only (leak-suite covered: an agent reports only its OWN sightings), and every meeting-enabled test double crossing `_build_participants` gains it (the 15.4 protocol-extension sweep, applied on day one).
- [ ] Grounding: a spoken sighting matching the speaker's own record feeds the corroborated set (fixture: subject's suspicion moves by exactly the corroboration delta through the existing caps); an ungrounded or fabricated vouch changes NOTHING in the belief fold (the anti-collusion floor: two impostors vouching for each other with fabricated sightings earn zero exculpation — pinned).
- [ ] A `WhereaboutsClaim` places its speaker in `reconstruct_stated_paths` output (pinned), and a claim contradicting a grounded sighting of the same speaker raises the EXISTING alibi-vs-sighting flag path (no new flag kind — pinned).
- [ ] With no template asking for the new kinds, committed-set behavior is byte-identical (golden + `verify_samples.sh` green) — the mechanism is inert until 16.15 elicits it.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The accessor is genuinely a near-copy: `game.py:2369-2403` minus the vent-action filter, plus
`co_present` projection — mirror the naming (`sighting_records_for_meeting`) so the channels read
as siblings. The grounding comparator belongs beside `_vent_observation_matches_record` with its
own tolerance constant (start at the vent value; it is a named constant precisely so 16.17's
measurement can retune it). The corroboration feed goes through the manager's existing
evidence-derivation call into `apply_meeting_evidence_rules(corroborated=...)` — thread the
grounded subjects into that argument rather than inventing a parallel path.

## Public types this task introduces
- `meetings.schemas.SightingRecord`
- `meetings.schemas.WhereaboutsClaim`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Impostor collusion is the adversarial case: two impostors vouching for each other. The fabricated-
vouch fixture (zero exculpation without a matching record) is the floor, but note what grounding
CANNOT catch — an impostor who truthfully vouches for its partner ("I really did see them in
Medbay") earns the −0.05 legitimately. That is correct behavior (the sighting is true), it is
small by design, and the collusion PATTERN (mutual vouching) becomes visible material for Phase
17's detectors — record it as a known property in the module docstring, not a bug. Second risk:
the whereabouts/alibi interaction — a self-placement is almost an alibi claim; reuse the alibi
validators' chronology discipline rather than duplicating it.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.beliefs"`

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
Open a PR from branch `phase-16-pooling-substrate` with a title like `task 16.7: pooling substrate: typed grounded vouching + the whereabouts claim`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing meetings/schemas.py:56-149 (the observation union + VentWitnessRecord — the pattern to generalize); orchestrator/game.py:2369-2403 (the vent accessor to near-copy); meetings/transcript.py:1053-1156 (reconstruct_stated_paths — where whereabouts integrate) + :2251-2309 (the vent grounding chokepoint); agents/memory/beliefs.py:387-423 (CORROBORATION_SUSPICION_DELTA — the channel vouching feeds)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
