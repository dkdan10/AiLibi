# Agent Prompt — 18.7 The crew deployment surface (opt-in, adoption gated)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.7 — The crew deployment surface (opt-in, adoption gated), anchored to audits/audit-phase-18-planning.md §4 (#7); agents/tactical/learned/factory.py:141-152 (the impostor-only wrapper), :199-232 (the factory + stamp); training/crew/scorer.py:197-230, 681-745 (the crew menu's re-validation + emergency bookkeeping the shipped wrapper must carry), :747-769 (`_CrewCandidateAgent`, the hook precedent); training/crew/options.py (the portable menu); audits/audit-phase-15-pause.md decision 6 (the Q4 bit-exact gate). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-crew-surface`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §4 (#7); agents/tactical/learned/factory.py:141-152 (the impostor-only wrapper), :199-232 (the factory + stamp); training/crew/scorer.py:197-230, 681-745 (the crew menu's re-validation + emergency bookkeeping the shipped wrapper must carry), :747-769 (`_CrewCandidateAgent`, the hook precedent); training/crew/options.py (the portable menu); audits/audit-phase-15-pause.md decision 6 (the Q4 bit-exact gate)
**Complexity:** Integration

The missing half of co-evolution: a production-tier, opt-in crew scorer surface beside the
untouched scripted default — the 15.20/15.21 pattern on the crew side. Port the crew option
scorer to a firewall-clean shipped forward pass (`agents/tactical/learned/crew_forward.py`),
commit the owned-task-base measurement-tier weights as the loadable artifact (adoption
stays gated — this ships a SURFACE, not a champion), add the crew stamp, the factory entry,
and the `--agent-factory learned-crew` CLI arm. The crew wrapper carries what the impostor
wrapper never needed: override re-validation against the submission mask and the
emergency-uses bookkeeping via the meeting-concluded hook.

**Files in scope:**
- agents/tactical/learned/crew_forward.py (new) + agents/tactical/learned/factory.py (the crew factory + stamp) + the committed crew weights artifact under agents/tactical/learned/
- orchestrator/replay.py; (the ADDITIVE crew-stamp record + reader — `CrewTacticalPolicyStamp` lands HERE so a learned-crew recording has a schema slot from day one; a game with no crew stamp parses byte-identically, committed-set round-trip pinned; 18.19 consumes this for dual-stamp recordings)
- eval/balance_eval.py; (the ADDITIVE `crew_policy_stamp` kwarg on `run_tournament_eval` — the recording path only threads the single tactical stamp today; default None is byte-identical)
- orchestrator/game.py; (the crew-stamp threading into the `ReplayLog` construction ONLY — the mirror of the existing tactical-stamp plumbing)
- scripts/run_tournament.py; (the `learned-crew` factory arm + stamp wiring)
- tests/training/test_learned_factory_acceptance.py (the crew twin: Q4 bit-exact gate vs `CrewOptionScorer`, determinism double-run, leak-mode scan)
- tests/scripts/test_run_tournament_candidate_artifact.py; (the crew factory arm's guards)

**Files NOT in scope:**
- training/crew/ (the training-side scorer is the reference implementation — mirrored, never moved)
- agents/tactical/crewmate_policy.py (the scripted default is untouched; it remains the anchor and the default)

**Definition of done:**
- [ ] The shipped crew forward pass is bit-exact against `training.crew.scorer.CrewOptionScorer` over the committed weights on a committed-bytes decision sweep (the Q4 gate, crew edition), pure-Python, firewall-clean (no numpy/torch/engine imports — the existing firewall test extends).
- [ ] A `learned-crew` recording carries the crew stamp read back from bytes (never echoed), sha-verified against the committed sidecar; the default path is byte-identical with the factory unset (pinned).
- [ ] The wrapper re-validates every override against the submission mask and carries `emergency_uses_remaining` across meetings via the concluded hook, fixture-pinned including the mask-violation fail-loud case.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the `utility_es.py` → `forward.py` port line-for-line where possible: drop the
`engine.world`/`training` imports, freeze the weights as float-hex + sha sidecar, and gate
on bit-exactness rather than approximate equality (the forward pass is pure float64
arithmetic). The crew menu module already imports only firewall-legal packages.

## Public types this task introduces
- `agents.tactical.learned.crew_forward.LearnedCrewScorer`
- `agents.tactical.learned.factory.build_learned_crew_factory`
- `agents.tactical.learned.factory.LearnedCrewPolicyStamp`
- `orchestrator.replay.CrewTacticalPolicyStamp`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This touches production `agents/` and the recording CLI in one PR. The two guards that keep
it safe: the default path byte-identity pin (no factory ⇒ scripted crew, proven on committed
bytes), and the stamp conflation guard (a crew recording must never wear the impostor
champion's stamp — assert distinct `policy_id`/`weights_sha256` namespaces in the CLI arm).

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
Open a PR from branch `phase-18-crew-surface` with a title like `task 18.7: the crew deployment surface (opt-in, adoption gated)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#7); agents/tactical/learned/factory.py:141-152 (the impostor-only wrapper), :199-232 (the factory + stamp); training/crew/scorer.py:197-230, 681-745 (the crew menu's re-validation + emergency bookkeeping the shipped wrapper must carry), :747-769 (`_CrewCandidateAgent`, the hook precedent); training/crew/options.py (the portable menu); audits/audit-phase-15-pause.md decision 6 (the Q4 bit-exact gate)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
