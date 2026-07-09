# Agent Prompt — 15.16 The crew track: a learned scorer over observable crew options

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.16 — The crew track: a learned scorer over observable crew options, anchored to audits/post-phase-14-ML-planning.md §4.1, §5.2 (crew FSM gaps + the observability blocker); audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms); agents/tactical/crewmate_policy.py (the ladder :343-423; EmergencyPacingTracker); experiments/lab/ml_spike/fo8_crew_buddy.py (the small-gain prior). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-crew-track`
**Depends on:** 15.10, 15.13, 15.14, 15.15
**Section refs:** audits/post-phase-14-ML-planning.md §4.1, §5.2 (crew FSM gaps + the observability blocker); audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms); agents/tactical/crewmate_policy.py (the ladder :343-423; EmergencyPacingTracker); experiments/lab/ml_spike/fo8_crew_buddy.py (the small-gain prior)
**Complexity:** Medium

The secondary track, run on 15.15's shared machinery (files disjoint from the bake-off; the harness +
ES core consumed strictly read-only — the 15.15 edge exists so the harness is present, not because
files collide): a learned utility scorer over a FIXED, observable-only crew option set — continue-to-task, buddy-toward the nearest
visible/belief-trusted group (co-presence + low own-suspicion keyed, never role — roles are hidden),
patrol-toward last-seen suspect, report, emergency (through the existing `EmergencyPacingTracker` gate
semantics, not bypassing them), repair, hold. Trained with the 15.14 ES core against the frozen scripted
impostor, anchored (KL) to `CrewmatePolicy`, evaluated under the 15.15 protocol shape
(gate/referee/fitness/determinism/leak) into its own report + jsonl. Task-ordering is EXPLICITLY OUT:
the packet exposes a single engine-fed `pending_task_id` and no owned-task set, so ordering is
un-observable — this track must not widen the observation surface; instead its report states the precise
surface ask (what field, what firewall review, what expected gain) as an input to the pause's
owner-gated decision. The honest prior is FO-8's small gain (buddy/task gate: +1 game vs the FSM) — the
deliverable is a clean measurement of what observable-option learning buys the crew, not a mandated win.

**Files in scope:**
- training/crew/__init__.py (new)
- training/env.py (build_action_mask emergency-intent canonicalization region ONLY — close the documented 15.8 exact-equality gap (`eval/leak_test.py:608-616`): the mask's emergency entry carries a default payload while the crew FSM stamps `reason='suspicion_accumulation'`/kill-witness, and `is_submission_legal` compares exact, so a scorer delegating the FSM emergency raises; a mask-legal crew emergency carrying the FSM's `reason` payload must validate as submission-legal; behind this task's 15.15 edge — 15.14/15.15 consume env.py read-only)
- training/crew/options.py (new: the observable option set + per-option features)
- training/crew/scorer.py (new: the learned scorer + training entry)
- training/reports/report-crew-track.md (new)
- training/reports/results-crew-track.jsonl (new)
- training/artifacts/crew/ (new: frozen candidate weights + sha256)
- tests/training/test_crew_options.py (new)
- tests/training/test_crew_scorer.py (new)

**Files NOT in scope:**
- agents/tactical/crewmate_policy.py (the anchor is read-only)
- observation/packet.py + observation/public_map.py (NO surface widening — the pause owns that decision)
- training/bakeoff/harness.py + training/bakeoff/es.py (consumed read-only; if the harness needs generalizing for crew, that change lands behind 15.15's edge, and this task documents the ask instead of editing)

**Definition of done:**
- [ ] The option set is proven observable-only: every per-option feature derives from the packet + the crew agent's own memory (a test sweeps committed-corpus packets; the leak-test factory mode passes for the crew wrapper).
- [ ] Emergency semantics preserved: the learned scorer routes emergency intent through the same `EmergencyPacingTracker` gate the FSM uses — a test proves the tracker's pacing/announce bookkeeping is untouched — AND the emitted emergency intent (with the FSM's `reason` payload) is proven `submission_legal` under `build_action_mask` by a button-room fixture (the 15.8 exact-equality gap this task's env.py region closes; today's `tests/training/test_env.py` emergency fixture only round-trips the mask's own default-payload object and cannot fail on it).
- [ ] The trained scorer vs the FSM crew is measured on the fixed eval seed set against the frozen scripted impostor: mis-eject-relevant deltas (meeting-trigger quality, correct-report rate), survival, task-completion pace, win rate — reported with gate/referee/determinism columns in the jsonl, same tuple shape as 15.15.
- [ ] Anchor-KL to `CrewmatePolicy` (the anchor cross-entropy — log-loss at the FSM's deterministic choice, as 15.15 defines it) reported for every candidate; the FO-8 prior is quoted and the measured delta stated against it.
- [ ] The crew report DISCLOSES the reward-definition divergence: `training/rewards.py`'s `patrol_coverage` measures co-location with an impostor's ACTUAL room (a deliberate, in-code-documented engine-truth proxy) rather than the doctrine phrase "coverage of last-seen suspects"; the observable-only DoD above governs the POLICY's inputs, not the reward channel, and the leak-test factory mode does not scan rewards — any belief-keyed re-definition of the term is a named ask for the pause, not an edit here.
- [ ] The report's final section is the crew-surface ask for the pause: the exact observation field proposed (owned-task set), the firewall/leak review it needs, and the expected-gain argument — with this track's measured ceiling as the evidence.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The crew reward terms are the tactically-reachable set from the training-signal doc: task progress,
survival, correctly-routed reports, buddy/patrol coverage of last-seen suspects — through the 15.8
reward channel, plus the terminal win. "Belief-trusted group" keys on the crew agent's OWN
suspicion/trust floats (quantized, via the encoder) — the same information class that already reaches
crew tactics through the emergency gate; nothing role-derived. Files are disjoint from 15.15 by
construction; the harness and ES core are consumed strictly read-only, and any generalization the
harness needs for crew is documented as an ask, not edited here.

## Public types this task introduces
- `training.crew.options.CrewOption`
- `training.crew.scorer.CrewOptionScorer`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.bakeoff.es"`
- `uv run python -c "import training.bakeoff.goodhart"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.determinism"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`
- `uv run python -c "import training.surrogate.ballots"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import engine.rng"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-15-crew-track` with a title like `task 15.16: the crew track: a learned scorer over observable crew options`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §4.1, §5.2 (crew FSM gaps + the observability blocker); audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms); agents/tactical/crewmate_policy.py (the ladder :343-423; EmergencyPacingTracker); experiments/lab/ml_spike/fo8_crew_buddy.py (the small-gain prior)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
