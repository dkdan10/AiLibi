# Agent Prompt — 13.13 De-imperative the §4.6 vote gate (non-directive prompt; deterministic tally floor stays)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-13.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 13.13 — De-imperative the §4.6 vote gate (non-directive prompt; deterministic tally floor stays), anchored to DESIGN.md §4.6 + §5.5 (reconciled — the gate is a deterministic tally backstop, the prompt non-directive); experiments/lab/report-forward-redesign-probes.md Probe 1 (the imperative is an OUTCOME lever: 9/39 ejections accused-by-nobody, 13–38/39 flip to SKIP without it); agents/strategic/prompts/vote_ballot.j2:131-149 (the pre-computed MUST-vote/MUST-skip block); meetings/voting.py:120-213 (`tally_ballots` — the floor that STAYS); orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-13.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-13-deimperative-gate`
**Depends on:** 13.6, 13.10
**Section refs:** DESIGN.md §4.6 + §5.5 (reconciled — the gate is a deterministic tally backstop, the prompt non-directive); experiments/lab/report-forward-redesign-probes.md Probe 1 (the imperative is an OUTCOME lever: 9/39 ejections accused-by-nobody, 13–38/39 flip to SKIP without it); agents/strategic/prompts/vote_ballot.j2:131-149 (the pre-computed MUST-vote/MUST-skip block); meetings/voting.py:120-213 (`tally_ballots` — the floor that STAYS); orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`)
**Complexity:** Integration
**Files in scope:**
- agents/strategic/prompts/vote_ballot.j2
- orchestrator/game.py
- tests/agents/test_strategic_prompts.py
**Files NOT in scope:**
- meetings/voting.py — the deterministic tally floor (plurality, SKIP-first-class, tie→skip, leader-confidence floor) is UNCHANGED; it remains the silent anti-cascade backstop
- meetings/manager.py::guard_ballot_target_graph (:2315) — the SECOND deterministic copy of the §4.6 verdict; deliberately UNCHANGED (it never forces SKIP→eject, so A-1 is NOT a no-op; do not soften this frozen safeguard)
- the committed replays — NO re-record here; the recorded ballots stay byte-identical under the OLD prompt version; A-1's effect appears only in NEW recordings (the held 13.12 re-record)
- the detector / beliefs / suspicion graph — unchanged

Rewrite the §4.6 Decision-rule prose in `vote_ballot.j2` (lines 140-149, the `_max >= _thr` imperative on :143;
preserve the `_susp`/`_max`/`_thr` derivation at :131-137) from the pre-computed MUST-vote-to-eject /
MUST-set-SKIP command into a **non-directive** evidence line:
render the max-suspicion + the 0.60 reference threshold as ONE input among the transcript, contradiction
flags, and memory, and ask the model to weigh them and emit its OWN target + confidence. **Keep the
deterministic tally floor** (`voting.py::tally_ballots`) exactly as-is — it silently prevents a tie /
below-threshold / SKIP-plurality eject regardless of the prompt, so removing the imperative CANNOT lower
the floor (Probe 1 confirms the floor lives in the tally, not the prompt). **Constrain the emitted confidence
in PROSE (not a code clamp):** the model's emitted `confidence` must reflect the named target's rendered
suspicion and may not report ≥0.60 on a sub-0.60 target (the bidirectional-imperative cascade vector Probe 1
flags) — the tally leader-confidence floor (`voting.py:211`) is the deterministic backstop; a code clamp would
be a NEW deterministic gate the plan does not intend. Bump the prompt version: the `.j2` version marker +
`orchestrator/game.py::DEFAULT_PROMPT_VERSIONS` + the ONE live version pin at
`tests/agents/test_strategic_prompts.py:1223` (`vote_ballot/v6`→`v7`); `tests/orchestrator/` has NO
`vote_ballot` version assertion (the "two orchestrator pins" do not exist), and the manifest pin
(`vote_ballot/v5`) reads as-recorded and does NOT break (no re-record).

**Firewall:** prompt-only change; no new agent-visible field; the teammate firewall (the SKIP-coercion of a
teammate ballot) is untouched. **Determinism:** the committed replays (recorded under the old prompt
version) re-walk byte-identically — A-1 changes only NEW recordings; engine determinism untouched.
**Definition of done:** `vote_ballot.j2` presents the gate as evidence not a command; the deterministic
tally floor in `voting.py` is unchanged; the emitted-confidence PROSE constraint is added (no code clamp);
the prompt version + the `test_strategic_prompts.py:1223` pin are bumped (`v6`→`v7`); the committed sets +
state-hash verify stay byte-identical (no re-record); a 6–10-seed real-`qwen3.5:9b` smoke — measured against a
pinned PRE-CHANGE baseline (null-reason-id share + count of under-gate / ≥0.60 ballots) so the criteria are
falsifiable — shows null `primary_reason_id` share DOWN, verbatim-threshold-number echo
→ ~0, and the ballot-confidence distribution NOT clustering a sub-threshold target across the gate;
`scripts/check.sh` green.

## Implementation hint
edit only the decision-rule prose at `vote_ballot.j2:140-149` (the imperative on :143), preserving the
:131-137 derivation, to a descriptive "here is the strongest suspicion and the 0.60 reference; weigh it with
the transcript and flags and decide"; leave the schema + the reason-id machinery intact; for the smoke reuse
the local-Ollama fixture path from Task 13.6 — this is a recording, not a committed-set reconstruction.

## Integration risk
the bidirectional imperative is the cascade vector — removing the MUST-vote half WITHOUT pinning confidence
lets a self-rated confidence ≥ 0.6 on a sub-threshold target eject where it cannot today; the pin is
load-bearing. The desk test (Probe 1) bounds but does not measure the live effect — the real-LLM smoke is
the gate. Do NOT touch `voting.py::tally_ballots` OR `guard_ballot_target_graph` (the deterministic floors must
stay). The version-bump cascade is ONE pin (`test_strategic_prompts.py:1223`, in scope), NOT two orchestrator
pins; the manifest/regression tests read as-recorded literals and are unaffected.

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
Open a PR from branch `phase-13-deimperative-gate` with a title like `task 13.13: de-imperative the §4.6 vote gate (non-directive prompt; deterministic tally floor stays)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.6 + §5.5 (reconciled — the gate is a deterministic tally backstop, the prompt non-directive); experiments/lab/report-forward-redesign-probes.md Probe 1 (the imperative is an OUTCOME lever: 9/39 ejections accused-by-nobody, 13–38/39 flip to SKIP without it); agents/strategic/prompts/vote_ballot.j2:131-149 (the pre-computed MUST-vote/MUST-skip block); meetings/voting.py:120-213 (`tally_ballots` — the floor that STAYS); orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
