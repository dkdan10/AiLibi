# Agent Prompt — 13.6 Prompt rework: elicit richer testimony + breadcrumb render + trim

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.6 — Prompt rework: elicit richer testimony + breadcrumb render + trim, anchored to experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-prompt-rework`
**Depends on:** 13.5
**Section refs:** experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2
**Complexity:** Integration
**Files in scope:**
- agents/memory/store.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/prompts/impostor_report.j2
- tests/agents/test_strategic_prompts.py
**Files NOT in scope:**
- the in-band reasoning field / two-phase reason→emit — that is the gated 13.9 (keep `think=False`)
- engine/ visibility (13.8); api/ — none; NO re-record here (the testimony-richness payoff is measured at the smoke re-record)

**This is a primary game-changer.** The 13.4 gate proved the detector is STARVED: crew state only thin firsthand
sightings, so reconstruction finds no contradictions (R7 0/50). 13.6 fattens the testimony the detector mines. Three
parts: (1) **elicit richer crew sightings** — rework `crewmate_report.j2` + `accusation_round.j2` so crew state WHO they
saw, WHERE, and WHEN as concrete `saw_player` observations (not vague free-text), and frame OTHERS' accounts as
belief-movers (a second observation-backed account corroborates) — more + more-specific `saw_player` claims are the
two-source-conjunction material 13.4 needs. (2) **breadcrumb render** — `agents/memory/store.py` emits a directional
"saw X leave A→R" line for the agent's most-recent sighting per subject (pure function of existing episodic deltas — NO
packet field, firewall untouched). (3) **trim** accreted verbosity ONLY where it removes no still-needed guard; bump the
four prompt versions together. EXCLUDE the in-band reasoning field (→ 13.9).
**Definition of done:** `store.py` emits the directional breadcrumb (byte-deterministic over a fixed episodic log, no new
packet field — leak test unaffected); the report/accusation prompts elicit concrete WHO/WHERE/WHEN `saw_player`
observations and frame others' accounts as belief-movers; verbosity trimmed without dropping a guard; the four prompt
versions bumped together; `tests/agents/test_strategic_prompts.py` re-goldened at the new versions; `think=False`
preserved; NO re-record; `scripts/check.sh` is green.

## Implementation hint
the goal is MORE + MORE-SPECIFIC `saw_player` observations from crew (the reconstruction material), so make the report /
accusation templates ask for concrete who/where/when sightings, not prose; the breadcrumb render is a pure read of the
existing episodic deltas (no new packet field); keep `think=False` (the in-band reasoning field breaks structured output —
deferred to the gated 13.9).

## Integration risk
the payoff (richer testimony → detector flags → R7) is observable ONLY on a real-Ollama run, so 13.6 cannot be
$0-validated for its R7 effect — its offline DoD is render determinism + the prompt re-golden + no-leak; the R7 lift is
gated at the Wave-B smoke re-record. `think=False` is load-bearing (the in-band reasoning field relocates JSON into the
thinking channel). Firewall: the breadcrumb render adds no packet field; determinism intact; bump versions together so
the regression pins stay coherent.

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
Open a PR from branch `phase-13-prompt-rework` with a title like `task 13.6: prompt rework: elicit richer testimony + breadcrumb render + trim`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
