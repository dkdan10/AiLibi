# Agent Prompt — 13.5.2 Testimony as reported episodic content (+ wire alibi_map)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.5.2 — Testimony as reported episodic content (+ wire alibi_map), anchored to the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`; the "social info is a scalar, not content" root) + this file's Wave C; meetings/schemas.py (`MeetingTurn.claims`/`observations`, the `Claim`/`ObservationClaim` unions); meetings/manager.py (`derive_belief_evidence` / `extract_belief_evidence`, the scalar twin this mirrors, ~:2630-2740); agents/perception.py (`PROVENANCE_OBSERVED`/`INFERRED`); agents/memory/store.py (`absorb_meeting_evidence` ~:204, `render_for_prompt` ~:127, the `_SALIENCE_*` band, `_known_roster_ids`, `_latest_self_guard_fields`); agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis` — wired here, not modified); orchestrator/game.py (`extract_belief_evidence`→`absorb_meeting_evidence` per living agent, ~:1539); api/replay_loader.py (~:839-843); llm/provider.py (the `AILIBI_*` env-flag convention, ~:31). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-5-testimony-content`
**Depends on:** 13.5.1
**Section refs:** the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`; the "social info is a scalar, not content" root) + this file's Wave C; meetings/schemas.py (`MeetingTurn.claims`/`observations`, the `Claim`/`ObservationClaim` unions); meetings/manager.py (`derive_belief_evidence` / `extract_belief_evidence`, the scalar twin this mirrors, ~:2630-2740); agents/perception.py (`PROVENANCE_OBSERVED`/`INFERRED`); agents/memory/store.py (`absorb_meeting_evidence` ~:204, `render_for_prompt` ~:127, the `_SALIENCE_*` band, `_known_roster_ids`, `_latest_self_guard_fields`); agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis` — wired here, not modified); orchestrator/game.py (`extract_belief_evidence`→`absorb_meeting_evidence` per living agent, ~:1539); api/replay_loader.py (~:839-843); llm/provider.py (the `AILIBI_*` env-flag convention, ~:31)
**Complexity:** Integration
**Files in scope:**
- meetings/schemas.py
- meetings/manager.py
- agents/perception.py
- agents/memory/store.py
- orchestrator/game.py
- api/replay_loader.py
- tests/meetings/test_reported_testimony_derive.py
- tests/agents/test_reported_testimony.py
**Files NOT in scope:**
- the scalar belief path (`derive_belief_evidence` accused/corroborated/contradicted → `apply_meeting_evidence_rules`) — UNCHANGED. Reported content is additive narrative, never a suspicion Δ, so the §4.6 eject gate, decay, and the "no single signal ejects" principle are untouched
- agents/memory/beliefs.py — `record_alibi` / `PlayerBelief.alibis` already exist (earmarked by 13.5.1); this task CALLS `record_alibi` from the store ingest and READS `.alibis` to render, but does not modify the module
- agents/strategic/prompts/*.j2 — reported rows are self-framed as unverified claims in the rendered memory (`store.py`), so NO template edit and NO prompt-version bump; an explicit template directive is deferred to Phase-14 prompt authoring
- the witnessed-kill flag (13.5.3), movement (13.5.4), unfreeze-mid-meeting (13.5.5) — separate Wave-C tasks
- engine/ and the recorded replays — no engine change; reported-ingest derives purely from the recorded `MeetingResult`, so committed replays reconstruct byte-identically; NO re-record

Today a meeting moves only a scalar suspicion Δ (`absorb_meeting_evidence`); WHAT players said — who they placed where, who they accused, whose alibi they backed — evaporates when the meeting closes (`render_for_prompt` shows only first-hand `observed`/`inferred` rows + the suspicion table). This task gives each living agent a memory of public testimony: after a meeting the speakers' STRUCTURED claims/observations become `provenance="reported"` episodic rows, attributed to the speaker and self-framed as unverified claims, so the next round's prompt carries `[meeting] CLAIM by p-3 (unverified): saw p-5 in ELECTRICAL @ tick 12` — testimony the model weighs, not ground truth. It also finally populates the dead `alibi_map`. Owner decisions (locked 2026-06-25): (1) scope = structured claims + sightings only (`SawPlayerObservation`, `AlibiClaim`, `AccusationClaim`, `CorroborationClaim`); free-text is excluded. (2) firewall = FAITHFUL RECORD — reported content is PUBLIC speech, so it is NOT teammate-firewalled (an impostor records what was publicly said about its team); only the SCALAR suspicion firewall stays, unchanged (the impostor still accrues no suspicion Δ vs a teammate).

Pipeline, mirroring the scalar twin: (1) `meetings/schemas.py` — a frozen, engine-free `ReportedStatement` DTO (speaker, kind, subject, tick(s)/room). (2) `meetings/manager.py` — `derive_reported_testimony(result) -> tuple[ReportedStatement, ...]`, a pure replay-deterministic reduction of `result.transcript.turns`, sorted, roster-only, free-text dropped — sitting beside `derive_belief_evidence`. (3) `agents/perception.py` — `PROVENANCE_REPORTED` + an `EVENT_REPORTED_TESTIMONY` type. (4) `agents/memory/store.py` — `absorb_reported_testimony(memory, *, statements, ...)`: appends one `provenance="reported"` row per statement at the meeting-boundary tick (`_latest_self_state_tick + 1`, the tick `absorb_meeting_evidence` already uses), SKIPPING the recipient's own statements; for each `AlibiClaim` statement also calls `memory.beliefs.record_alibi(...)`; roster-only; NOT teammate-firewalled. (5) `store.py` render — `_build_observations` gains a reported branch (the self-framed `CLAIM by X (unverified): …` line) at a salience strictly BELOW first-hand (band ~20–40, under `_SALIENCE_SAW_PLAYER`=50, above `_SALIENCE_COOLDOWN_STATUS`=10), and the belief render surfaces the now-populated `alibi_map`. (6) `orchestrator/game.py` + `api/replay_loader.py` — call `absorb_reported_testimony` per LIVING agent in the SAME loop as `absorb_meeting_evidence`, gated on the flag. (7) flag `AILIBI_TESTIMONY_AS_CONTENT`, resolved once like `AILIBI_LLM_PROVIDER`, default OFF (= byte-identical to today); the 9B smoke + Phase-14 re-record run it ON.

**Definition of done:** `derive_reported_testimony` is a pure function of a `MeetingResult` (no engine/perception import; run twice → byte-identical; free-text excluded; only roster ids appear). With the flag ON, after a meeting each LIVING agent's memory carries `provenance="reported"` rows for OTHER speakers' structured claims/observations (never its own), self-framed as unverified claims, and `PlayerBelief.alibis` is populated for every `AlibiClaim` about a roster subject; the render shows reported lines BELOW first-hand observations (a budget-tight render sheds reported rows before first-hand sightings) and the alibi view renders. The scalar path is byte-identical (accused/corroborated/contradicted deltas, the §4.6 gate, decay) — reported content moves NO suspicion; the impostor scalar firewall is unchanged while reported CONTENT is NOT teammate-firewalled (a teammate-incriminating public statement DOES appear in an impostor's reported memory). Replay-deterministic: both `orchestrator/game.py` and `api/replay_loader.py` ingest per living agent; `scripts/verify_samples.sh` reconstructs the committed replays byte-identically. With the flag OFF every memory render and game outcome is byte-identical to pre-task HEAD (the regression boundary); the existing golden suite passes unchanged. New tests cover derivation (pure/deterministic/free-text-excluded/roster-only), ingest (own-statements skipped, alibi_map wired, NOT teammate-firewalled), render (reported below first-hand; flag-off byte-identical), and replay determinism. The PR description NOTES that DESIGN.md §6.1/§6.5 need a design-thread follow-up to mark reported-provenance + alibi_map as now-wired (this task must not edit DESIGN.md). Full `scripts/check.sh` green; a 9B smoke (3–5 seeds, flag ON) shows parse-success ≈ 100%, leak suite passing, meeting-rate ≥ 0.60, render within the 1500-tok budget, and byte-identical reconstruction.

## Implementation hint
Mirror the scalar twin exactly so determinism and the per-agent wiring come for free: put `derive_reported_testimony` beside `derive_belief_evidence` (reduced from the SAME `result.transcript`), and `absorb_reported_testimony` beside `absorb_meeting_evidence`, called from the SAME per-living-agent loops (`orchestrator/game.py` ~:1539, `api/replay_loader.py` ~:843) using the roster (`_known_roster_ids`) and own-id self channel (`_latest_self_guard_fields`) the scalar fold already reads — add NO new orchestrator channel. Append reported rows at the meeting-boundary tick so episodic non-decreasing-tick order holds and they render under a meeting tag. Read the flag once like `llm/provider.py` reads `AILIBI_LLM_PROVIDER`; default OFF. Salience is strictly below first-hand by construction — add a golden test that a budget-tight render drops reported rows before first-hand sightings. `meetings.schemas` is engine-free and already imported by `agents/memory/beliefs.py`, so importing it from `agents/` keeps the import-linter green. The leak suite must still pass — reported content is PUBLIC transcript speech and carries no role, but assert it. Do NOT edit any `.j2`: the `CLAIM by X (unverified)` framing lives in the rendered line, so flag-off output is byte-identical and no prompt version bumps.

## Public types this task introduces
- `meetings.schemas.ReportedStatement`
- `meetings.manager.derive_reported_testimony`
- `agents.memory.store.absorb_reported_testimony`
- `agents.perception.PROVENANCE_REPORTED`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk
Cross-module, multi-consumer: a new episodic event type + provenance flows into the salience-budgeted render (token competition — the band must keep first-hand facts), the alibi_map render, and the live + replay per-agent folds (determinism). Behind `AILIBI_TESTIMONY_AS_CONTENT` (default OFF) so the merge is byte-identical and the existing golden/regression suite is untouched; the lever's gameplay value is measured for the first time on the new model in Phase 14's combined re-record, not here. The one hard invariant: reported content is ADDITIVE narrative — it must never touch the scalar suspicion graph, the §4.6 eject gate, or the teammate scalar firewall, so "no single signal ejects" and replay byte-identity both hold. The self-framing (`CLAIM … (unverified)`) is load-bearing: without it a weaker model may treat reported sightings as things it witnessed.

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
Open a PR from branch `phase-13-5-testimony-content` with a title like `task 13.5.2: testimony as reported episodic content (+ wire alibi_map)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`; the "social info is a scalar, not content" root) + this file's Wave C; meetings/schemas.py (`MeetingTurn.claims`/`observations`, the `Claim`/`ObservationClaim` unions); meetings/manager.py (`derive_belief_evidence` / `extract_belief_evidence`, the scalar twin this mirrors, ~:2630-2740); agents/perception.py (`PROVENANCE_OBSERVED`/`INFERRED`); agents/memory/store.py (`absorb_meeting_evidence` ~:204, `render_for_prompt` ~:127, the `_SALIENCE_*` band, `_known_roster_ids`, `_latest_self_guard_fields`); agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis` — wired here, not modified); orchestrator/game.py (`extract_belief_evidence`→`absorb_meeting_evidence` per living agent, ~:1539); api/replay_loader.py (~:839-843); llm/provider.py (the `AILIBI_*` env-flag convention, ~:31)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
