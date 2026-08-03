# Agent Prompt — 7.12 Teammate-aware impostor meeting behavior (J-5)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.12 — Teammate-aware impostor meeting behavior (J-5), anchored to audits/audit-2026-06-02-2112-gameplay-data.md (gp-imp-1, D-D-1, D-D-2, D-D-3, D-D-4, C-C-6); DESIGN.md §5.2–§5.3 (meeting protocol / reports), §6.6 (prompt rendering + leak firewall); the J-5 deferral marker at `agents/perception.py:196`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-7-impostor-meeting-coordination`
**Depends on:** 7.1, 7.2, 7.9, 7.10 (all merged — Wave 0 substrate + Wave 0.5 repair; the 2026-06-02 re-record + re-audit cleared the Wave-1 gate)
**Section refs:** audits/audit-2026-06-02-2112-gameplay-data.md (gp-imp-1, D-D-1, D-D-2, D-D-3, D-D-4, C-C-6); DESIGN.md §5.2–§5.3 (meeting protocol / reports), §6.6 (prompt rendering + leak firewall); the J-5 deferral marker at `agents/perception.py:196`
**Complexity:** Medium

The 2026-06-02 gameplay-data audit on the Wave-0.5 baseline found impostors actively help the crew in meetings. `fellow_impostor_ids` is delivered on the self channel (landed by 7.2) and consumed by the kill policy (7.9, why friendly-fire is now 0) but NOT by the meeting/vote path — `agents/perception.py:196` explicitly defers this to "Wave 2 (J-5)". From the recorded data: impostors voted to eject a fellow impostor in 40/91 ballots (44%), both impostors mutually betrayed each other in 11 meetings, and impostors fabricated eyewitness accusations against a teammate in 48/54 report accusations (0/19 corroborations supported a teammate). All 5 "correct" impostor ejections were aided by a teammate's betrayal vote, and in seed 6 that vote was outcome-pivotal — so the current 68% impostor win rate UNDER-states true impostor strength. This task closes the meeting-side teammate gap so the crew-intelligence A/B that follows is measured against a non-self-sabotaging opponent.

Meeting output is LLM-driven (unlike the FSM kill policy), so the fix is two layers: a prompt layer that tells an impostor who its teammates are and to protect them, and a deterministic guard that hard-excludes a teammate from the produced accusation/ballot regardless of what the model emits — the same belt-and-suspenders the kill policy plus engine guard use. The teammate list is firewall-safe self-channel data: it must enter an impostor's own prompt but NEVER a crewmate's, preserving the 7.2 leak invariant (`self_state.fellow_impostor_ids == ()` for crew). The 4p/1i frozen set is single-impostor, so every change is a no-op there.

This is a recorded-behavior change, so the committed 7p/2i set is re-recorded + re-audited after this merges (a separate operational step in the Wave-1 sequencing section); do not regenerate data here. It does not affect replay reconstruction of existing sets (meetings replay by applying the recorded outcome), so both committed sets stay byte-identical.

**Files in scope:**
- meetings/manager.py (`MeetingParticipant` gains `fellow_impostor_ids: tuple[PlayerId, ...] = ()`, threaded into the report/statement/vote prompt context the reasoner receives)
- orchestrator/game.py (populate `MeetingParticipant.fellow_impostor_ids` at construction — `orchestrator/game.py:434` — from world-state roles when the participant is an impostor; `()` for crewmates and a sole impostor; never the participant's own id)
- agents/strategic/reasoner.py (pass the teammate list into the impostor prompt context; after the LLM returns, hard-exclude teammates — a `VoteBallot` targeting a teammate coerces to `SKIP`, an `AccusationClaim` / `Statement.target` naming a teammate is dropped; allow an impostor's own `fellow_impostor_ids` through the prompt leak scanner the way the `## Your role:` line is already allowlisted)
- agents/strategic/prompts/impostor_report.j2 + accusation_round.j2 + vote_ballot.j2 (surface the teammate list with an instruction never to accuse, incriminate, or vote a teammate, and optionally to corroborate one; render the teammate block only when the list is non-empty, so crewmate prompts stay byte-unchanged)
- tests/agents/ (deterministic-guard unit tests over the reasoner: teammate-ballot coerces to SKIP, teammate-accusation dropped, crew + solo-impostor no-op; an impostor's own teammate ids do not trip the prompt leak scanner while a crewmate prompt carries no teammate block)
- tests/meetings/ + tests/orchestrator/ (`MeetingParticipant` carries the field; the orchestrator populates the other impostors' ids for an impostor and `()` for every crewmate / sole impostor)

**Files NOT in scope:**
- observation/service.py + observation/packet.py + agents/perception.py (`fellow_impostor_ids` is plumbed by 7.2 — consume it, do not edit the substrate)
- agents/tactical/impostor_policy.py + engine/ (the FSM kill layer is already teammate-aware via 7.9; no engine change)
- meetings/schemas.py (the `VoteBallot` / `Statement` / `AccusationClaim` schemas are unchanged — the guard coerces produced values, it never relaxes validation)
- eval/, replays/samples/ (no metric change here; the re-record is a separate step and never deletes the 4p/1i set)

**Definition of done:**
- [ ] `MeetingParticipant` carries `fellow_impostor_ids` (default `()`), populated by the orchestrator from world-state roles: the other impostors' ids for an impostor participant, `()` for every crewmate and for a sole impostor, never the participant's own id.
- [ ] An impostor's meeting prompts surface the teammate list with an instruction never to accuse, incriminate, or vote a teammate (and optionally to corroborate one); the shared accusation/vote prompts render NO teammate block for a crewmate (empty list), so crewmate prompts are byte-unchanged.
- [ ] A deterministic guard in the reasoner hard-excludes teammates from the produced output regardless of the model: a `VoteBallot` whose target is a `fellow_impostor_id` becomes `SKIP`; an `AccusationClaim` or `Statement.target` naming a teammate is dropped. The guard is a no-op for crewmates and a sole impostor, and is deterministic (no RNG, no new LLM call) so replay is unaffected.
- [ ] The prompt leak scanner allows an impostor's own `fellow_impostor_ids` (legitimate self-channel data, like the `## Your role:` line) while every crewmate meeting prompt still carries no teammate-id block; the 7.2 leak invariant (`self_state.fellow_impostor_ids == ()` for crew) and the existing leak suites stay green.
- [ ] Behavioral regression anchors (firewall-known, no role inference): an impostor never produces a ballot or accusation targeting a teammate across a seeded multi-impostor set. Repro fixture: seed 6 meeting-0 (the pivotal teammate-betrayal vote that, removed, turns a 2-vote eject into a 1-1-1-1 SKIP).
- [ ] The frozen 4p/1i set still reconstructs byte-identically (single impostor → every change is a no-op); both committed sets' leak suites stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The teammate list already exists on the observation packet (`SelfView.fellow_impostor_ids`, 7.2) and the orchestrator holds the world-state roles where it builds `MeetingParticipant` (`orchestrator/game.py:434`); add the field there rather than re-deriving roles in the meeting layer. The reasoner (`agents/strategic/reasoner.py`) already branches the report prompt on role (crewmate vs impostor) — thread `fellow_impostor_ids` into that same context and into the shared accusation/vote renderers, gating the teammate block on a non-empty list so crewmate prompts are byte-unchanged. For the guard, post-process the parsed `VoteBallot` / `Statement` / `ReportDocument` before returning: coerce a teammate-targeted ballot to `SKIP` and drop teammate accusations — pure functions of `fellow_impostor_ids`, deterministic, replay-safe, mirroring the kill policy's teammate filter. For the leak scanner, the reasoner already allowlists the legitimate `## Your role: X` line before running `eval.leak_test._assert_no_role_bearing_values`; extend that allowlist so an impostor's own teammate ids in their own prompt are not flagged, WITHOUT loosening the scan for crewmate prompts (whose list is empty). Keep everything deterministic so replay reconstruction of the committed sets is unaffected.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "from observation.packet import SelfView; assert 'fellow_impostor_ids' in SelfView.model_fields"`
- `uv run python -c "from meetings.manager import MeetingParticipant"`

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
Open a PR from branch `phase-7-impostor-meeting-coordination` with a title like `task 7.12: teammate-aware impostor meeting behavior (j-5)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-2026-06-02-2112-gameplay-data.md (gp-imp-1, D-D-1, D-D-2, D-D-3, D-D-4, C-C-6); DESIGN.md §5.2–§5.3 (meeting protocol / reports), §6.6 (prompt rendering + leak firewall); the J-5 deferral marker at `agents/perception.py:196`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
