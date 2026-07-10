# Agent Prompt — 15.22 Crew owned-task surface: the `SelfView` widening + the gate-valid crew retrain

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.22 — Crew owned-task surface: the `SelfView` widening + the gate-valid crew retrain, anchored to audits/audit-phase-15-pause.md decision 5 (YES, with the four-item review) ; training/reports/report-crew-track.md §5 (the unmeasured gate-valid ceiling) + §7 (the surface ask this task lands); observation/packet.py (`SelfView`, the privileged self channel); observation/service.py (the packet assembly this widening must scope); eval/leak_test.py (the suite the new field extends); DESIGN.md §1.3 (the observation firewall this rides behind). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-crew-owned-tasks`
**Depends on:** 15.18, 15.19
**Section refs:** audits/audit-phase-15-pause.md decision 5 (YES, with the four-item review) ; training/reports/report-crew-track.md §5 (the unmeasured gate-valid ceiling) + §7 (the surface ask this task lands); observation/packet.py (`SelfView`, the privileged self channel); observation/service.py (the packet assembly this widening must scope); eval/leak_test.py (the suite the new field extends); DESIGN.md §1.3 (the observation firewall this rides behind)
**Complexity:** Integration

Execute decision 5: widen the crewmate's observation surface by exactly one self-channel field and
re-measure the crew track's gate-valid ceiling on it. Part 1, the surface (the 15.16 §7 ask, four-item
review honored): `SelfView` gains `owned_task_ids: tuple[TaskId, ...]` — the recipient's OWN unfinished
task instances as map task ids, assembled in `observation/service.py` strictly from the recipient's own
engine-side task state (never another player's, never impostor fake-task state — an impostor's view
carries its camouflage task ids exactly as `pending_task_id` does today, so the field leaks no role
bit); the leak suite gains the owned-task assertions (no cross-player task ids anywhere in any packet;
the field's byte shape is stable and versioned by the existing packet discipline); committed v4/v5
transcripts and all committed replays still parse and byte-verify (additive field, default-empty for
reconstruction of old bytes). Part 2, the retrain (the §5 ceiling measurement, run under the SAME
protocol shape as 15.16): re-run the crew utility-scorer ES with (a) the widened option basis —
nearest-of-N owned-task selection and same-room batching features over `owned_task_ids` — and (b) the
FO-8-style interrupt-preserving constraint the pause scoped: the `report` interrupt is NOT suppressible
by the learned scorer (a body sighting always routes to report, exactly the FSM's interrupt semantics),
so the 15.16 failure mode — win-by-meeting-starvation — is structurally unreachable and the gate-valid
ceiling finally gets a number. Evaluated under the 15.15 protocol (gate / hardened 15.19 referee /
fitness / anchor-CE / determinism / leak), reported in the same tuple shape to its own report + jsonl.
Crew champion adoption is NOT a goal of this task: the deliverable is the surface + the honest
gate-valid measurement; any crew deployment is a phase-close/Phase-17 call on this task's numbers.

**Files in scope:**
- observation/packet.py (`SelfView.owned_task_ids` — additive, engine-free)
- observation/service.py (own-task assembly + the impostor-camouflage scoping)
- eval/leak_test.py (owned-task leak assertions region)
- training/crew/options.py (owned-task option features + the interrupt-preserving constraint)
- training/crew/scorer.py (basis widening only — the ES loop is 15.14's core, consumed as-is)
- training/reports/report-crew-owned-tasks.md (new) + training/reports/results-crew-owned-tasks.jsonl (new)
- tests/observation/test_packet_owned_tasks.py (new) + tests/training/test_crew_owned_tasks.py (new)

**Files NOT in scope:**
- agents/tactical/ (the crew FSM and the learned impostor package are untouched; this is a training-track measurement over a widened surface)
- engine/ (task state is already engine-side; the widening is packet-assembly only)
- meetings/ (no meeting-layer change — one layer per baseline)
- replays/ (committed bytes untouched; old replays reconstruct with the default-empty field)

**Definition of done:**
- [ ] `SelfView.owned_task_ids` carries exactly the recipient's own unfinished map task ids; an impostor's packet carries its camouflage set (no role bit); the leak suite proves no packet ever contains another player's task ids, and all committed replays still byte-verify bare.
- [ ] The interrupt-preserving constraint is structural: a test proves the learned scorer CANNOT select away from `report` when a body is visible (the option is not offered for suppression, mirroring the FSM interrupt), and the retrained candidate's games consequently cannot reproduce the 15.16 meeting-starvation validity failure.
- [ ] The retrain reports in the 15.15 tuple shape (gate / referee / fitness / anchor-CE / determinism hash / leak) on the frozen corpus test split, referee scored under the HARDENED 15.19 definition, with the crew-fsm-baseline re-measured through the identical protocol as the comparator row.
- [ ] The report states the gate-valid ceiling finding — the win-rate/fitness delta that survives the validity gate and the hardened referee — and the task-pace cell (tasks/100 ticks) that decision 5 predicted the owned-task basis would move, each cited to the jsonl.
- [ ] The report ends with the deployment posture: no crew default change in this phase; the numbers are Phase-17 scoping inputs.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The four-item review from the 15.16 §7 ask is the checklist: (1) `ObservationService` scoping — the
field is assembled from the recipient's own task state only; (2) leak-suite extension — assert absence
of foreign task ids in EVERY packet field, not just the new one; (3) byte-shape discipline — additive
Pydantic field with a default, so old bytes parse; (4) the encoder note — the crew option basis
consumes the field training-side (`crew-option-features` bumps its version string); the production
encoder (`agents/tactical/features.py`) is NOT touched this task. For the constraint, remove `report`
from the scorer's selectable set rather than penalizing it — structural unreachability, not a reward
term (the Goodhart lesson). Expect the honest outcome to be smaller than 15.16's 0.6 win rate — that
number was bought with the starvation exploit; the gate-valid delta is the real measurement.

## Public types this task introduces
- `training.crew.options.OwnedTaskOptionBasis`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Two hazards. First, the leak surface: `owned_task_ids` is the first packet widening since the firewall
audit — the impostor-camouflage path must be scoped so the field is indistinguishable between roles
(the packet already solves this for `pending_task_id`; mirror it exactly). Second, byte-compatibility:
the additive field must default-parse for every committed replay and transcript — run the full
byte-verification walk locally before the PR, because a shape error here fails 100 committed samples at
once.

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
- `uv run python -c "import training.crew.options"`
- `uv run python -c "import training.crew.scorer"`

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
Open a PR from branch `phase-15-crew-owned-tasks` with a title like `task 15.22: crew owned-task surface: the `selfview` widening + the gate-valid crew retrain`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md decision 5 (YES, with the four-item review) ; training/reports/report-crew-track.md §5 (the unmeasured gate-valid ceiling) + §7 (the surface ask this task lands); observation/packet.py (`SelfView`, the privileged self channel); observation/service.py (the packet assembly this widening must scope); eval/leak_test.py (the suite the new field extends); DESIGN.md §1.3 (the observation firewall this rides behind)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
