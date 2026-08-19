# Agent Prompt — 9.3 Teammate-perception firewall (input side)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.3 — Teammate-perception firewall (input side), anchored to DESIGN.md §1.3, §4.7; audits/audit-2026-06-06-0632-gameplay-data.md gp-7; audits/audit-2026-06-07-0717-gameplay-data.md gp-8 item 6. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-teammate-perception-firewall`
**Depends on:** none (hygiene root)
**Section refs:** DESIGN.md §1.3, §4.7; audits/audit-2026-06-06-0632-gameplay-data.md gp-7; audits/audit-2026-06-07-0717-gameplay-data.md gp-8 item 6
**Complexity:** Medium

The 7.12 firewall guards the meeting OUTPUT side (no impostor accuses/votes a teammate), but the
INPUT side still manufactures evidence against the team: a witnessed teammate kill generates
suspicion of the teammate in the witness's own belief graph, teammate-incriminating sightings flow
into the impostor's meeting inputs (seed 47: impostor p-9's opt-in placed teammate p-1 at the kill
room/tick, generating both alibi_vs_sighting contradiction flags), and self-subject sighting rows
render into a player's own prompt as third-person garble. Once conversion works, these own-goals
corrupt the crew-intel read. Implement DESIGN.md §4.7's team-internal guard.

**Files in scope:**
- agents/perception.py (the impostor's own-witness path: a `saw_player` co-located with a kill it knows is a teammate's generates no teammate-suspicion belief; `fellow_impostor_ids` already rides the privileged self channel)
- agents/memory/store.py (`render_for_prompt` / `_render_saw_player`: suppress self-subject sighting rows in a player's own rendered memory; drop teammate-incriminating kill-window sightings from an IMPOSTOR's rendered meeting inputs)
- meetings/manager.py (`_suspicion_graph_with_contradictions`: deterministic backstop — an impostor voter's graph carries no edge against a fellow impostor; mirrors the existing 7.12 coercion precedent)
- tests/agents/test_perception.py + tests/agents/test_memory_rendering.py + tests/agents/test_beliefs.py + tests/meetings/test_manager.py (the seed-47-shaped case: teammate kill witnessed → no self-team suspicion, no teammate-incriminating render row, graph edge masked; crew behavior unchanged; the §1.3 observation firewall suite stays green)

**Files NOT in scope:**
- agents/strategic/prompts/** (NO prompt edits — the teammate-alibi consistency instruction is deferred to the conversion wave; the impostor build freeze holds)
- observation/service.py (the packet already carries what is needed; no schema change)
- meetings/voting.py, replays/samples/**

**Definition of done:**
- [ ] An impostor witnessing a teammate's kill generates no suspicion of the teammate in its own belief state; teammate-incriminating kill-window `saw_player` rows do not render into the impostor's meeting inputs; self-subject sighting rows never render into any player's own prompt.
- [ ] `_suspicion_graph_with_contradictions` masks fellow-impostor edges for impostor voters (deterministic backstop, 7.12-style). Auditable invariant, pinned: the recorded contradiction set of any game contains NO alibi_vs_sighting entry whose supporting sighting is an impostor's own observation of a fellow impostor (the seed-47 class) — assert it in tests; downstream audits verify it from recorded contradictions + re-derived roles (input-side masking leaves no recorded marker text, so the invariant IS the gateable surface).
- [ ] Crew perception/render behavior is byte-identical for non-impostors, regression-tested in this pinned shape: the existing memory-render goldens pass UNCHANGED for crewmate fixtures (no golden regeneration), plus a synthetic role-flip test — one 9p/2i-shaped fixture rendered twice, as CREWMATE and as IMPOSTOR-with-fellow-ids — asserting the renders are identical except for the teammate-guard suppressions. The observation-firewall and leak suites pass unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Three small guards, one per layer, all keyed off `fellow_impostor_ids` on the privileged self
channel (the reasoner's leak-guard at agents/strategic/reasoner.py shows the role-gating
precedent — non-impostors must never observe these code paths firing). The graph mask in
meetings/manager.py is the cheapest and most load-bearing: even if a sighting slips through
memory, the voter-side graph carries no team edge. Keep each guard independently tested so the
defense-in-depth claim is real.

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
Open a PR from branch `phase-9-teammate-perception-firewall` with a title like `task 9.3: teammate-perception firewall (input side)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, §4.7; audits/audit-2026-06-06-0632-gameplay-data.md gp-7; audits/audit-2026-06-07-0717-gameplay-data.md gp-8 item 6), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
