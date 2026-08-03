# Agent Prompt — 8.7 Meeting accusation-chain protocol + record schema

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.7 — Meeting accusation-chain protocol + record schema, anchored to DESIGN.md §5.2 (chain protocol), §5.3 (turn record), §5.4 (contradictions), Appendix A (`MeetingTurn`); audits/restructure-impact-map-2026-06-04-0223.md §2b, §3.1, §5 decisions 6–9. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-meeting-chain-protocol`
**Depends on:** none (the R-0 DESIGN.md meeting-protocol rewrite is merged; this is the meeting-track root)
**Section refs:** DESIGN.md §5.2 (chain protocol), §5.3 (turn record), §5.4 (contradictions), Appendix A (`MeetingTurn`); audits/restructure-impact-map-2026-06-04-0223.md §2b, §3.1, §5 decisions 6–9
**Complexity:** Integration

Replace the parallel-reports + fixed-`round_count` statement loop + vote with the reactive accusation chain (DESIGN.md §5.2): one ordered `turns` list — opening (accuse-or-unsure) → reactive chain (the accused responds; next speaker is the accused; deterministic 3-condition termination) → opt-in info-share (relevant non-speakers, terminal, no chain-extension) → vote. Reshape `meetings/schemas.py` (`Statement.round_index` → `turn_index` + `reply_to` + `turn_kind`; `MeetingTranscript` → an ordered `turns` tuple; `ReportDocument`'s observations/claims fold into the `opening` turn), rewrite `meetings/manager.py` (the sequencer, `_speaker_order` reactive turn-passing, `_collect_*` into chain + opt-in turns, `_statement_id` → a turn ordinal `{meeting_id}:turn-{N}`, the renderer Protocols, per-turn deadlines + a total cap), and rewrite `meetings/transcript.py::is_canonically_ordered` (the production C-3 impl keyed on `round_index`) to chain-turn order. The 7.12 teammate firewall guards (`exclude_teammate_accusation_claims` / `drop_teammate_statement_target` / `coerce_teammate_ballot_to_skip`) wrap EVERY turn-kind. Contradictions (§5.4) recompute once over the full transcript before voting. This changes `MeetingReplayEntry.transcript` (`extra='forbid'`), so committed meeting rows stop validating — the second byte-breaker.

**Files in scope:**
- meetings/manager.py (run sequencer; `_speaker_order` reactive turn-passing; `_collect_*` into chain + opt-in turns; `_statement_id` → `{meeting_id}:turn-{N}`; renderer Protocols + a per-turn/opt-in input; per-turn deadlines + total cap; the 7.12 guards on every turn)
- meetings/schemas.py (`Statement` → `MeetingTurn` with `turn_index`/`reply_to`/`turn_kind`; `MeetingTranscript` → ordered `turns`; `ReportDocument` observations/claims fold into the opening turn — keep `found_body`/`saw_player` queryable for vote_correctness)
- meetings/transcript.py (`is_canonically_ordered` rewritten from `round_index` to chain-turn order)
- meetings/voting.py (tally/plurality survive; confirm the candidate set over the final transcript)
- tests/meetings/test_manager.py + test_schemas.py + test_transcript.py + test_contradictions.py + test_voting.py (the chain sequencer, termination, turn ids, 7.12 guards on every turn, contradiction recompute, vote — rewritten green; a deterministic replay-walk-of-the-chain test)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (the committed-set meeting-recon cases stay SKIPPED pending 8.12 — idempotent with 8.1's skip; coordinate the trivial overlap at merge)

**Files NOT in scope:**
- agents/strategic/ (the prompts + reasoner producers are 8.8)
- eval/, api/, frontend/ (the metric re-pointing + meeting DTOs are 8.10)
- orchestrator/replay.py format_version (8.11); replays/samples/ (8.12)

**Definition of done:**
- [ ] `MeetingTranscript` is one ordered `turns` tuple of `MeetingTurn{turn_index, speaker, turn_kind ∈ {opening,reply,opt_in}, reply_to, observations, claims, free_text}`; turn ids are `{meeting_id}:turn-{N}` (unique across repeat speakers); `found_body`/`saw_player` observations live on the opening turn.
- [ ] The sequencer runs opening → reactive chain → opt-in → vote; the chain terminates deterministically (no new accusation / re-accusation cycle / turn-count == living-player-count) and a replay walks the recorded turn list without re-calling the LLM.
- [ ] Opt-in is limited to living non-speakers with a relevant observation, one terminal turn each, and an opt-in turn never extends the chain; contradictions recompute once over the full transcript before voting.
- [ ] The 7.12 teammate firewall guards wrap every turn-kind (an impostor never accuses/incriminates/votes a fellow impostor); `meetings/voting.py` tally + tie→SKIP are preserved.
- [ ] The meeting test suite is rewritten green incl. a deterministic chain-replay-walk test; the committed-set meeting-recon cases stay skipped pending 8.12; `eval/determinism_test.py` (fresh recordings) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The chain's next speaker is a pure function of the prior turn's accusation target, and termination is a pure function of the recorded turns — keep both deterministic so replay reconstructs from the recorded turn list (no LLM re-call). Route the 7.12 guards through one per-turn chokepoint so every turn-kind inherits them. Keep the strict `AlibiClaim` chronology + the 7.10 fail-soft on a malformed turn. The committed-recon skip is shared with 8.1 (idempotent); 8.8 carries the prompts/reasoner that drive the turns, 8.10 the eval/api readers — do not touch those here.

## Integration risk

This is the second byte-breaker and the single biggest meeting-side change; its `MeetingTranscript` shape is consumed by the four §11.3 eval metrics (8.10), the api meeting views (8.10), and the LLM `format=` schema (8.8/8.9), so lock the schema first. The deterministic termination + replay-walk is load-bearing (a non-deterministic chain breaks replay). Do not relax `extra='forbid'` to absorb old rows — they are intentionally re-recorded in 8.12.

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
Open a PR from branch `phase-8-meeting-chain-protocol` with a title like `task 8.7: meeting accusation-chain protocol + record schema`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.2 (chain protocol), §5.3 (turn record), §5.4 (contradictions), Appendix A (`MeetingTurn`); audits/restructure-impact-map-2026-06-04-0223.md §2b, §3.1, §5 decisions 6–9), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
