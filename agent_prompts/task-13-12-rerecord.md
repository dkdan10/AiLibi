# Agent Prompt — 13.12 ONE combined re-record under redistribute + the Wave-E substrate + close-audit gate + era-pin re-anchor

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.12 — ONE combined re-record under redistribute + the Wave-E substrate + close-audit gate + era-pin re-anchor, anchored to the cadence doctrine ([[project_substrate_cadence_doctrine]] — ONE combined re-record; era-pin re-anchor precedent `dbe1827`); engine/maps/canonical_1.yaml:40 (`dead_task_rule: drop` → flip to `redistribute`); the merged Wave-E substrate (13.13 de-imperatived gate / 13.14 detector — R7 now LIT 25/114 @ 74% on the pre-re-record set / 13.15 geomean rubric); experiments/lab/results-rubric-score.json (regenerate with the geomean); experiments/lab/forward_redesign_conversion_probe.py (the R4 prediction = +2 worst-case). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-rerecord`
**Depends on:** 13.10, 13.13, 13.14, 13.15
**Section refs:** the cadence doctrine ([[project_substrate_cadence_doctrine]] — ONE combined re-record; era-pin re-anchor precedent `dbe1827`); engine/maps/canonical_1.yaml:40 (`dead_task_rule: drop` → flip to `redistribute`); the merged Wave-E substrate (13.13 de-imperatived gate / 13.14 detector — R7 now LIT 25/114 @ 74% on the pre-re-record set / 13.15 geomean rubric); experiments/lab/results-rubric-score.json (regenerate with the geomean); experiments/lab/forward_redesign_conversion_probe.py (the R4 prediction = +2 worst-case)
**Complexity:** Integration
**Files in scope:**
- engine/maps/canonical_1.yaml
- replays/samples/9p2i/ (re-recorded)
- replays/samples/4p1i/ (re-recorded)
- experiments/lab/results-rubric-score.json (regenerated with the geomean)
- the ~15 era-pin recording-SHA / prompt-version assertions across tests/ (re-anchored to the new recording; precedent `dbe1827`)
**Files NOT in scope:**
- the engine / detector / gate / rubric CODE — all merged (13.10/13.13/13.14/13.15); this task only RECORDS under them + re-anchors pins, it changes no behavior
- the firewall (leak_test / leak-property) — RUN (must stay green), not edited

The single combined re-record (cadence doctrine — one record for all unrecorded substrate). (1) Flip `canonical_1.yaml:40` `dead_task_rule: drop → redistribute` (the validated config: tpc=2, ×1.0 durations). (2) **Fake-provider sweep FIRST** (`AILIBI_LLM_PROVIDER=fake`) — balance sanity, impostor win in the ≥14% band under the new config (abandon-branch if the fake-sweep craters balance, BEFORE the real run). (3) **Real-Ollama (`qwen3.5:9b`, think=false) re-record of BOTH committed sets** (4p1i + 9p2i) under the full Wave-E substrate (redistribute + 13.13 + 13.14 + 13.15). (4) **Regenerate** `results-rubric-score.json` with the 13.15 geomean. (5) **Re-anchor the era-pins** (the recording-SHA / prompt-version / committed-bytes assertions; precedent `dbe1827`). (6) **Close-audit** (the gameplay-data audit form) + the leak smoke + a mind-inspector-render assertion (the 13.13/13.14 changes surface no role-leak in the Phase-12 mind-inspector).

**Gate — the new baseline must show the meeting DECIDES:** **R1** eject-decided UP from the 6/50 baseline (the headline goal) **AND R4** wrong-ejection floor flat (crew wrong-ejections do NOT rise beyond the conversion probe's **+2** prediction; 0 railroad floors) **AND** impostor win ≥ 14% (the Phase-11 floor, not cratered) **AND R7 > 0** (the detector is now lit — 13.14; ~25/114 on the pre-re-record set) **AND** the geomean ranks eject-decided games above `CREWMATE_TASKS` stopwatch games (the achieved ranking reported). **Abandon the branch** if R4 rises beyond +2 or impostor < 14%. ~13h overnight, LOCAL real-Ollama.

**Firewall:** the leak_test + leak-property sweeps are RUN and byte-verified on the new recordings (roles / teammates / kill-attribution never leak; the re-key / detector / gate add no agent-visible field). **Determinism:** the new recordings are byte-deterministic (state-hash verified); the era-pins re-anchor to the new SHAs (the recording is the new reference).
**Definition of done:** `canonical_1.yaml` flipped to `redistribute`; the fake-sweep confirmed impostor ≥14% BEFORE the real run; both sets re-recorded on real `qwen3.5:9b` under the Wave-E substrate; `results-rubric-score.json` regenerated with the geomean; the era-pins re-anchored; the close-audit run + committed; the gate (R1-up AND R4-flat-≤+2 AND impostor≥14% AND R7>0 AND geomean-ranking) MET — else the branch is ABANDONED; leak smoke + mind-inspector assertion green; `scripts/check.sh` green.

## Implementation hint
run LOCALLY (real Ollama, overnight) — a recording, not a Web-session task. `run_tournament_eval` with the canonical config (redistribute, tpc=2, ×1.0) for both sets; the fake-sweep via `AILIBI_LLM_PROVIDER=fake` first; regenerate the rubric via `rubric_score.py` (now geomean); re-anchor the era-pins via the established refresh-samples + pin-update step (precedent `dbe1827`).

## Integration risk
this is the BASELINE the whole forward-redesign is judged on — the abandon-branch is LOAD-BEARING (never merge a re-record that fails the gate). The conversion probe predicts +2 worst-case wrong crew (deterministic-gate upper bound; 13.13 de-imperative should reduce it) — if the real R4 exceeds +2, the lone-STRONG trade did not hold on the live LLM and must be revisited, NOT merged. Freeze the substrate during the measurement (no code changes mid-re-record). The era-pin re-anchor is the standard substrate-change consequence (cadence doctrine), not scope creep.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-13-rerecord` with a title like `task 13.12: one combined re-record under redistribute + the wave-e substrate + close-audit gate + era-pin re-anchor`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the cadence doctrine ([[project_substrate_cadence_doctrine]] — ONE combined re-record; era-pin re-anchor precedent `dbe1827`); engine/maps/canonical_1.yaml:40 (`dead_task_rule: drop` → flip to `redistribute`); the merged Wave-E substrate (13.13 de-imperatived gate / 13.14 detector — R7 now LIT 25/114 @ 74% on the pre-re-record set / 13.15 geomean rubric); experiments/lab/results-rubric-score.json (regenerate with the geomean); experiments/lab/forward_redesign_conversion_probe.py (the R4 prediction = +2 worst-case)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
