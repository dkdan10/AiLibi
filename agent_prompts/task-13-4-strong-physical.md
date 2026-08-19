# Agent Prompt — 13.4 alibi_vs_physical STRONG from reconstructed testimony (B3/B4)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.4 — alibi_vs_physical STRONG from reconstructed testimony (B3/B4), anchored to experiments/lab/report-phase-b-plan.md (B3/B4); experiments/lab/inference_testimony_probe.py (the 13.4-ceiling probe) + inference_feasibility_probe.py; meetings/transcript.py (the 13.2 `reconstruct_stated_paths` helper, `is_relevant_sighting`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-strong-physical`
**Depends on:** 13.2, 13.3
**Section refs:** experiments/lab/report-phase-b-plan.md (B3/B4); experiments/lab/inference_testimony_probe.py (the 13.4-ceiling probe) + inference_feasibility_probe.py; meetings/transcript.py (the 13.2 `reconstruct_stated_paths` helper, `is_relevant_sighting`)
**Complexity:** Integration
**Files in scope:**
- meetings/transcript.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- perception-time deltas — the firewall exposes no per-player liveness channel, so ALL absence/last-seen inference lives
  in the meeting layer over public testimony only
- agents/memory/beliefs.py (13.5); engine/ and recordings — NO re-record

**This task is THE R7 lever.** The 13.3 $0 gate confirmed R7 stays 0/50 from promotion alone — the committed transcripts
hold 111 `alibi_vs_sighting` + only 1 (guarded, crewmate-naming) `alibi_conflict`, so 13.3 had nothing to promote. 13.4
GENERATES the STRONG flags. Add a new `alibi_vs_physical` contradiction kind in `meetings/transcript.py`, emitted from
the 13.2 `reconstruct_stated_paths` over PUBLIC testimony: a subject whose stated alibi is **physically contradicted** by
independent placements over its tick range, or who is the last speaker-placed party with the victim before the body. Do
NOT rely on same-tick clashes — the ceiling probe found those are rare (~2); the lever is the reconstructed-path
impossibility + last-seen-with-victim. **THE CRUX (role-gating): flag only a genuinely CONTRADICTED alibi, NEVER mere
two-source co-placement.** The ceiling probe found the material exists (4.0 placements/meeting; 26 impostor-subjects
placed by ≥2 independent speakers) — but ALSO **28 CREWMATE-subjects with the same two-source coverage**, so a detector
that fires on co-placement (rather than on a genuine physical contradiction of the subject's OWN alibi) will
false-positive on crew. Emit STRONG ONLY under the TWO-SOURCE conjunction (the subject's uncorroborated alibi AND an
independent contradicting placement); a lone atom emits at the weak/mid band. DROP all perception-time forms (no liveness
channel exists). Reuse `is_relevant_sighting` + endpoint-tick exclusion.
**Definition of done:** new `alibi_vs_physical` STRONG flags are emitted from `reconstruct_stated_paths` (public testimony
only — no engine/perception); RE-EXTRACT + `rubric_score.py` shows **R7 > 0 on ≥2–3 seeds with EVERY STRONG flag
role-gated to a true impostor and ZERO STRONG-on-crewmate** (role-gating is the make-or-break given the 28 crew two-source
cases; gp-3 watch-the-games is a BLOCKING manual check); an assertion test confirms no flag references a placement not
traceable to a transcript `saw_player`; a lone atom cannot reach the §4.6 gate alone (only the two-source conjunction
does); $0, NO re-record; `scripts/check.sh` is green.

## Implementation hint
consume `reconstruct_stated_paths` (returns `{subject -> (StatedPlacement{tick, rooms, speaker, event_id}, ...)}`); a
STRONG flag = the subject's OWN alibi is physically impossible given ≥1 INDEPENDENT (different-speaker, non-accuser)
placement over the alibi's tick range, OR last-speaker-placed with the victim pre-body — never co-placement agreement;
single atoms weak/mid; reuse `is_relevant_sighting` + endpoint-tick exclusion; no perception-time delta.

## Integration risk
the 28 crew two-source cases are the Goodhart/R4 trap — a STRONG flag on a crewmate is a false positive (it games R7 AND
risks a wrong ejection), so the contradiction MUST be against the subject's own alibi, role-gated + counted (the gate's
zero-STRONG-on-crewmate is the guard). 13.4 carries the WHOLE R7 outcome (13.3 was a no-op), so if the gate yields thin
R7 or ANY crew false positive, STOP — that is the refine/re-sequence signal, not a reason to weaken the role-gate.
Firewall: every placement MUST trace to a public `saw_player` (a leak test does not scan the belief layer, so the
traceable-to-transcript assertion test is the guard). NO re-record; byte-determinism intact.

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-13-strong-physical` with a title like `task 13.4: alibi_vs_physical strong from reconstructed testimony (b3/b4)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (B3/B4); experiments/lab/inference_testimony_probe.py (the 13.4-ceiling probe) + inference_feasibility_probe.py; meetings/transcript.py (the 13.2 `reconstruct_stated_paths` helper, `is_relevant_sighting`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
