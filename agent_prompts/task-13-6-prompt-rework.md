# Agent Prompt — 13.6 Prompt rework: elicit richer testimony + breadcrumb render + trim

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.6 — Prompt rework: elicit richer testimony + breadcrumb render + trim, anchored to experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); experiments/lab/deception_battery_2.py (the local real-Qwen harness pattern) + experiments/lab/inference_testimony_probe.py (the richness metric); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2 — **RUN LOCALLY (needs local Ollama/Qwen); file-disjoint from 13.5/13.8 so it runs in parallel.**. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-prompt-rework`
**Depends on:** none
**Section refs:** experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); experiments/lab/deception_battery_2.py (the local real-Qwen harness pattern) + experiments/lab/inference_testimony_probe.py (the richness metric); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2 — **RUN LOCALLY (needs local Ollama/Qwen); file-disjoint from 13.5/13.8 so it runs in parallel.**
**Complexity:** Integration
**Files in scope:**
- agents/memory/store.py
- agents/strategic/prompts/crewmate_report.j2
- agents/strategic/prompts/accusation_round.j2
- agents/strategic/prompts/vote_ballot.j2
- agents/strategic/prompts/impostor_report.j2
- tests/agents/test_strategic_prompts.py
- experiments/lab/meeting_prompt_battery.py
**Files NOT in scope:**
- the in-band reasoning field / two-phase reason→emit — that is the gated 13.9 (keep `think=False`)
- engine/ visibility (13.8); api/ — none; NO re-record here (the testimony-richness payoff is measured at the smoke re-record)

**RUN LOCALLY (needs local Ollama/Qwen).** Unlike 13.5/13.8, 13.6's goal — does the new prompt make Qwen *state richer
sightings* — is INVISIBLE to offline checks; only running the prompts through real Qwen verifies it, and a cloud session
cannot reach local Ollama. The 13.4 gate proved the detector is STARVED (crew state only thin firsthand sightings →
reconstruction finds no contradictions, R7 0/50); 13.6 fattens the testimony the detector mines. Three changes:
(1) **elicit richer crew sightings** — rework `crewmate_report.j2` + `accusation_round.j2` so crew state WHO they saw,
WHERE, and WHEN as concrete `saw_player` observations (not vague free-text), and frame OTHERS' accounts as belief-movers —
more + more-specific `saw_player` claims are the two-source-conjunction material 13.4 needs. (2) **breadcrumb render** —
`agents/memory/store.py` emits a directional "saw X leave A→R" line for the agent's most-recent sighting per subject (pure
function of existing episodic deltas — NO packet field, firewall untouched). (3) **trim** accreted verbosity ONLY where it
removes no still-needed guard; bump the four prompt versions together. EXCLUDE the in-band reasoning field (→ 13.9; keep
`think=False`).

**Build approach — rebuild the two sighting prompts, don't patch the crowded ones.** `crewmate_report.j2` (241 lines)
and `accusation_round.j2` (315 lines) are accreted walls a 7B drowns in; layering MORE sighting-elicitation onto them
makes it worse. REBUILD those two from a clean, concise base tuned for the canonical model — **qwen2.5:7b-instruct with
`think=False` structured output** (that 7B is the deployed provider, NOT a 9B; a model change is a separate substrate
decision the model-ceiling probe already cautioned against). Ground the rebuild in qwen2.5 structured-output prompting
best-practices (web-search them if the local agent has access; else apply the principles — short, schema-clear, a few
worked examples, no redundant imperative stacking). CRITICAL: before rebuilding, **catalog the load-bearing guards** the
existing prompts encode (each defensive patch exists because the 7B failed a specific way — anti-over-skip,
anti-narration, cover-consistency, the firewall lines) and carry EACH forward; the fixture loop must regression-test the
rebuild against BOTH the new goal (richer sightings) AND those failure modes (husk / over-skip / leak / cover-drift), so
the rebuild trades crowding for clarity, NOT for regressions. `vote_ballot.j2` / `impostor_report.j2` get the lighter trim
+ the belief-mover framing, not a full rebuild.

**Iterate fixture-first, not by full games (efficiency).** Build a local meeting-prompt fixture harness
(`experiments/lab/meeting_prompt_battery.py`, extending the `deception_battery_2.py` pattern): **ISOLATE the fixed
pre-meeting context** each agent has entering a meeting — reconstructed from the committed 9p2i replays (the observation
re-walk, or the context already embedded in the recorded `llm_calls` prompts) — then render the NEW template against those
fixtures and run real Qwen **one call at a time**, inspecting whether the output carries richer/more-specific `saw_player`
observations. Iterate the template on the fixtures (fast, prompt-isolated) until it does; **only then** run a few full
real-Ollama seeds to confirm it holds in-game. This isolates the prompt as the only variable and avoids waiting on whole
games per edit.
**Definition of done:** `store.py` emits the directional breadcrumb (byte-deterministic, no new packet field — leak test
unaffected); the report/accusation prompts elicit concrete WHO/WHERE/WHEN `saw_player` observations + frame others'
accounts as belief-movers; verbosity trimmed without dropping a guard; the existing prompts' load-bearing guards (anti-over-skip / anti-narration /
cover-consistency / firewall lines) cataloged and carried into any rebuilt prompt, regression-tested by the fixture loop
against the known failure modes (husk / over-skip / leak / cover-drift); the four prompt versions bumped together;
`tests/agents/test_strategic_prompts.py` re-goldened; `think=False` preserved. **LOCAL real-Qwen validation (the real
bar):** the fixture harness shows the new template yields MORE + MORE-SPECIFIC `saw_player` observations than the old on
the SAME pre-meeting contexts, and a few full real-Ollama seeds + `inference_testimony_probe.py` show testimony richness
rises (placements/meeting up from the committed ~4.0). NO re-record (the full R7 lift is the Wave-B smoke re-record);
`scripts/check.sh` is green.

## Implementation hint
iterate on FIXTURES first (the `deception_battery_2.py` pattern) — reconstruct one realistic pre-meeting context per test,
render the new template, run Qwen once, inspect; only after the template is dialed run full seeds. The breadcrumb render
is a pure read of the existing episodic deltas (no packet field). Keep `think=False` (the in-band reasoning field
relocates JSON into the thinking channel — deferred to 13.9).

## Integration risk
RUN LOCALLY — a cloud session cannot reach Qwen, so it would ship prompts BLIND to their actual effect (the exact
look-done-but-inert failure the 13.4 gate caught). The R7 lift itself is observable only at the smoke re-record; 13.6's
own bar is the fixture-harness richness gain + the placements/meeting rise on a few seeds. `think=False` is load-bearing.
Firewall: the breadcrumb render adds no packet field; bump prompt versions together so the regression pins stay coherent.

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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing experiments/lab/report-phase-b-plan.md (prompts); the 13.4 GATE FINDING above (committed testimony is too thin to mine — this is the lever that fattens it); experiments/lab/deception_battery_2.py (the local real-Qwen harness pattern) + experiments/lab/inference_testimony_probe.py (the richness metric); agents/memory/store.py; agents/strategic/prompts/{crewmate_report,accusation_round,vote_ballot,impostor_report}.j2 — **RUN LOCALLY (needs local Ollama/Qwen); file-disjoint from 13.5/13.8 so it runs in parallel.**), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
