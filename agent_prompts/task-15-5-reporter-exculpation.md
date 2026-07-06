# Agent Prompt — 15.5 Reporter exculpation: stop convicting the messenger (default-OFF lever)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.5 — Reporter exculpation: stop convicting the messenger (default-OFF lever), anchored to tasks/post-phase-14-clean-up.md H5; audits/audit-phase-14-close.md §4 (the zero-flag channel this hole dominates); agents/memory/beliefs.py (the accumulator/cap structure); audits/post-phase-14-pause.md §4.3 (the boundary-sum IEEE hazard, pinned here before deltas are touched). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-reporter-exculpation`
**Depends on:** 15.4, 15.6
**Section refs:** tasks/post-phase-14-clean-up.md H5; audits/audit-phase-14-close.md §4 (the zero-flag channel this hole dominates); agents/memory/beliefs.py (the accumulator/cap structure); audits/post-phase-14-pause.md §4.3 (the boundary-sum IEEE hazard, pinned here before deltas are touched)
**Complexity:** Integration

Close the second measured hole: 22 of baseline-2's 106 report-meeting ejections removed the meeting's
own reporter — all 22 innocent (impostors essentially never self-report in the corpus; verify and cite
the measured rate in the PR). The mechanism is structural: proximity-at-discovery reads as guilt, and
the reporter is definitionally at the body. Ship a default-OFF `reporter_exculpation` lever in the
13.5/14.10 pattern with two coordinated parts: (a) BELIEF-side — during the meeting a body-report
triggered, cap/dampen accusation-driven suspicion lift against that meeting's REPORTER (the
testimony-spread and accusation-carry channels), while leaving hard-flag-backed lift fully intact — a
reporter caught by a real contradiction or a vent/kill flag is still convictable; no immunity, only
removal of the proximity prior; (b) RENDER-side — the vote surface names the reporter and states the
base rate ("p-N reported the body; self-report is weakly exculpatory in this game"), layered onto the
vote template — WITH its own per-template provenance bump: this task edits `vote_ballot.j2` after 15.4
already stamped the set v5 while keeping that template byte-identical, so without a distinct version
two different vote-prompt bodies would both stamp `vote_ballot.qwen3_32b.v5` and any recording made
between the two merges would be unattributable; this task therefore bumps ONLY the `vote_ballot`
registry entry to v6 (per-template versioning is exactly what the provenance mapping exists for). The
render plumbing is explicit and inert-when-OFF: the vote
renderer's contract (in `meetings/render_contract.py`, the leaf home 15.6 creates) and
`agents/strategic/prompts/loader.py` gain a DEFAULTED reporter/lever render input (the Voice-doc 15.0
widen-the-contract-inert pattern), and the template renders the annotation only when the lever supplies
it — so lever-OFF prompts stay byte-identical and no template edit leaks into the OFF path. Because
this task edits belief deltas' surroundings, it FIRST pins the boundary-sum hazard: tests asserting
every documented delta combination that is designed to cross the 0.60 gate actually crosses it (the
`0.5 + 0.05 + 0.05` IEEE-luck case), so a later retune cannot silently break the two-signal eject.

**Files in scope:**
- agents/memory/beliefs.py (reporter-damp rule + `reporter_exculpation_enabled` resolver)
- orchestrator/replay.py (lever registration region — `_TOGGLEABLE_LEVER_RESOLVERS` + `substrate_flag_snapshot`)
- meetings/manager.py (vote-surface reporter annotation region — reporter identity into the render inputs)
- meetings/render_contract.py (vote-renderer contract widening region — the DEFAULTED reporter/lever render input; 15.6 creates the module)
- agents/strategic/prompts/loader.py (vote-renderer reporter kwarg region — defaulted/inert pass-through)
- agents/strategic/prompts/qwen3_32b/ (vote_ballot template reporter line — layered on 15.4's v5 set)
- orchestrator/game.py (PROMPT_VERSION_SETS vote_ballot entry only — the v5 → v6 per-template bump; disjoint from 15.4's set-bump line)
- .env.example (the lever env)
- tests/agents/test_beliefs.py (boundary-sum pins + damp-rule tests)
- tests/orchestrator/test_replay.py (lever stamp)
- tests/meetings/test_manager_reporter_render.py (new)

**Files NOT in scope:**
- meetings/voting.py (tally untouched — this is a belief/render lever, not a tally change)
- replays/samples/ (the re-record is 15.7; OFF must be byte-identical)
- eval/ (the 22/106 instrument is 15.3's)
- orchestrator/game.py outside the single vote_ballot registry entry (15.4 owns the set bump; 15.8.1/15.9 own their plumbing regions)

**Definition of done:**
- [ ] Lever OFF = byte-identical: `bash scripts/verify_samples.sh` reconstructs both committed sets clean with the lever merged OFF.
- [ ] Boundary-sum pins land BEFORE the rule change (separate commits): every documented gate-crossing delta combination is asserted against the 0.60 gate.
- [ ] The offline counterfactual (the 14.8 `allow_substrate_mismatch` analysis-only machinery) reports, over the committed baseline-2 bytes: how many of the 22 innocent-reporter convictions' deciding lifts the damp keeps below the gate, and that ZERO hard-flag-backed convictions (vent/kill/contradiction-flagged subjects) change outcome — the over-damping canary.
- [ ] The measured impostor self-report rate on the committed corpus is computed and cited in the rule's docstring (the empirical justification for treating self-report as weakly exculpatory).
- [ ] The lever is registered and stamped (`substrate_flag_snapshot` + MANIFEST provenance path), and the vote-surface annotation renders ONLY lever-ON (OFF renders byte-identical prompts).
- [ ] The `vote_ballot` registry entry is bumped to v6 in this task (the other three templates stay v5), so the pre-15.5 and post-15.5 vote-prompt bodies can never share a provenance stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone the 14.10 evidence-quality lever end-to-end: resolver + registration + stamp + offline
counterfactual + byte-coupled OFF tests — the pattern has shipped five times. The damp targets the
SOFT channels only (accusation spread / carry against the reporter within the triggered meeting); the
hard-flag path (`apply_contradiction_rule` strong flags) must be provably untouched. Reporter identity
already exists at meeting scope (`MeetingTriggeredEvent.actor` / the trigger the manager receives) —
thread it through the render inputs, do not re-derive it from the transcript.

## Public types this task introduces
- `agents.memory.beliefs.reporter_exculpation_enabled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Over-damping is the real risk: an impostor who self-reports to launder suspicion would gain cover. The
measured base rate (~zero self-reports in 160 kills) says the prior is currently safe, but the
counterfactual canary (zero hard-flag outcome changes) is the contract's hard line, and the lever stays
default-OFF until 15.7 measures it live. Second risk: the joint suspicion cap (`_joint_capped_suspicion`)
interacts with any new damp — the damp must compose with the existing caps, not bypass them.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`

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
Open a PR from branch `phase-15-reporter-exculpation` with a title like `task 15.5: reporter exculpation: stop convicting the messenger (default-off lever)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H5; audits/audit-phase-14-close.md §4 (the zero-flag channel this hole dominates); agents/memory/beliefs.py (the accumulator/cap structure); audits/post-phase-14-pause.md §4.3 (the boundary-sum IEEE hazard, pinned here before deltas are touched)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
