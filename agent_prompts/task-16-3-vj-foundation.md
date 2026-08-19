# Agent Prompt — 16.3 Foundation: suspicion provenance + inert render-contract widening + the prompt-byte golden

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.3 — Foundation: suspicion provenance + inert render-contract widening + the prompt-byte golden, anchored to audits/post-phase-14-Voice-and-Judgment-planning.md §3.2 + task "15.0" (the foundation design + the C4/C9 catches); agents/memory/beliefs.py (the accumulator this task decomposes); meetings/render_contract.py:38-195 (the three Protocols + SuspicionEntry); agents/strategic/prompts/loader.py (the four wrappers); meetings/manager.py (render seams + MeetingParticipant). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-vj-foundation`
**Depends on:** none
**Section refs:** audits/post-phase-14-Voice-and-Judgment-planning.md §3.2 + task "15.0" (the foundation design + the C4/C9 catches); agents/memory/beliefs.py (the accumulator this task decomposes); meetings/render_contract.py:38-195 (the three Protocols + SuspicionEntry); agents/strategic/prompts/loader.py (the four wrappers); meetings/manager.py (render seams + MeetingParticipant)
**Complexity:** Integration

The seam both tracks need, landed ONCE so Judgment and Voice never collide on the render contract
(the C4 catch). Three parts, all provably inert. (a) **Suspicion provenance**: record a
source-tagged decomposition beside the aggregate scalar in the belief store — per subject, the
accumulated lift attributable to flag-lift / body-proximity / kill-or-vent pin / testimony-spread
/ accusation-carry, with the cross-meeting carry SPLIT into carried-HARD and carried-SOFT
components (the hard/soft attribution PERSISTS through the carry: a grounded vent flag from
meeting 1 is still a hard component of the prior at meeting 3 — collapsing carry into one soft
bucket would let 16.4's clamp suppress persistent hard evidence, the exact outcome its canary
forbids) — WITHOUT changing the scalar's value, the fold's arithmetic, or any rendered byte. This is what 16.4's clamp classifies on and what 16.15's provenance-rendered
surface displays; today a carried soft prior at 0.70 is indistinguishable from a body-proximity
pin at 0.70. (b) **Render-contract widening, inert**: `persona` and `suspicion_provenance` kwargs
through the three `meetings/render_contract.py` Protocols, the four loader wrappers, and the
manager render seams; provenance fields on `SuspicionEntry`; a `MeetingParticipant.persona` field
— every input defaulted so unmodified templates render byte-identically (the widen-the-contract-
inert pattern the reporter lever shipped). (c) **The prompt-byte golden** (the C9 catch):
`verify_samples.sh` re-checks engine state hashes only — it is belief- and prompt-BLIND, so it
cannot prove (a)+(b) left prompts unchanged. Commit a test that re-renders every committed
meeting's opening/turn/ballot prompts (and `rendered_memory`) from the recorded inputs and asserts
byte-equality with the committed `llm_calls[].prompt`. That golden is the OFF-path proof
instrument every later render lever in this phase reuses (16.5's id-rendering, 16.15, 16.16).

**Files in scope:**
- agents/memory/beliefs.py (provenance decomposition region — recorded beside the scalar; arithmetic untouched)
- meetings/render_contract.py (persona + provenance kwargs, SuspicionEntry provenance fields — all defaulted)
- agents/strategic/prompts/loader.py (the four wrapper signatures + render bodies — defaulted pass-through)
- meetings/manager.py (render seams + MeetingParticipant.persona/provenance threading region — disjoint from 16.5/16.6/16.7/16.8's regions per the preamble map)
- orchestrator/game.py (the `suspicion_graph_for_meeting` builder region — POPULATE the new `SuspicionEntry` provenance fields from the belief store; without this, live graphs carry defaults and 16.15's surface has nothing to render; disjoint from 16.7/16.9's regions and the registry line)
- tests/agents/test_beliefs_provenance.py (new: decomposition-sums-to-scalar pins)
- tests/meetings/test_prompt_byte_golden.py (new: the golden over both committed sets)

**Files NOT in scope:**
- agents/strategic/prompts/qwen3_32b/ + every template directory (no template references the new kwargs yet — that is 16.15/16.16)
- meetings/transcript.py + meetings/voting.py (no detection or tally change)
- orchestrator/replay.py (no lever here — everything in this task is inert, not toggleable)
- replays/samples/ (the golden READS them; nothing rewrites them)

**Definition of done:**
- [ ] Provenance decomposition: for every subject in every committed meeting, the recorded source-tagged components sum to the aggregate scalar within documented float tolerance (pinned over both committed sets), and the fold's rendered values are bit-identical to before (the golden proves it).
- [ ] Hard/soft attribution survives the cross-meeting carry: a fixture where a grounded hard flag lands in meeting 1 shows a carried-HARD component (never carried-soft) in meeting 2+'s decomposition, including through decay and the pre-vote re-render path.
- [ ] The prompt-byte golden re-renders EVERY committed meeting prompt (all four template kinds) and `rendered_memory` across `replays/samples/{9p2i,4p1i}` and asserts byte-equality against `llm_calls[].prompt` — and it FAILS on a deliberate one-byte template perturbation (a golden that cannot fail is not a gate).
- [ ] The widened contract is inert: all new kwargs defaulted, `SuspicionEntry` extended additively, `MeetingParticipant.persona` defaults empty, and `bash scripts/verify_samples.sh` reconstructs both committed sets clean.
- [ ] The production graph builder POPULATES the provenance fields (a fixture proves live `MeetingParticipant.suspicion_graph` rows carry the hard/soft split, not defaults) — populated-but-unrendered is the inert contract; defaults-forever would starve 16.15's surface.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Decompose by ACCUMULATING per-source alongside the existing writes — every site that adds to a
subject's suspicion tags its delta with a source enum; do NOT re-derive provenance after the fact
(the fold's ordering and caps make post-hoc attribution wrong). The golden's re-render loop is the
15.3 walk plus the recorded render inputs: reconstruct state, build the participants exactly as
`_build_participants` does, call the SAME renderers production calls, compare bytes. Expect the
golden to be the phase's most-reused test — name its helpers for reuse, not for this task.

## Public types this task introduces
- `agents.memory.beliefs.SuspicionProvenance`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The whole task is a byte-identity claim with three moving layers; the golden is the only honest
proof, so land it FIRST in the commit sequence and keep it green through (a) and (b). The
provenance record must survive the pre-vote re-render path (the 13.5.5 rerender hook) — a
decomposition that drifts from the scalar on re-render poisons 16.4's clamp downstream. The
manager edit sits in the same file four later tasks touch: keep to the render-seam region the
preamble maps to this task.

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
Open a PR from branch `phase-16-vj-foundation` with a title like `task 16.3: foundation: suspicion provenance + inert render-contract widening + the prompt-byte golden`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-Voice-and-Judgment-planning.md §3.2 + task "15.0" (the foundation design + the C4/C9 catches); agents/memory/beliefs.py (the accumulator this task decomposes); meetings/render_contract.py:38-195 (the three Protocols + SuspicionEntry); agents/strategic/prompts/loader.py (the four wrappers); meetings/manager.py (render seams + MeetingParticipant)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
