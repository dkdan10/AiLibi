# Agent Prompt — 15.15 The impostor bake-off: BC/DAgger, utility-scorer+ES, policy-net+ES, MAP-Elites

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.15 — The impostor bake-off: BC/DAgger, utility-scorer+ES, policy-net+ES, MAP-Elites, anchored to audits/post-phase-14-ML-planning.md §5.2, §9 (the option vocabulary + paradigm comparison); audits/post-phase-14-ML-training-signal.md §4 (the objective spine: competence + anchor-KL + QD; referee as gate); agents/tactical/impostor_policy.py (_scored_targets :937-1009, the ladder :261); experiments/lab/ml_spike/check2_learnability.py + fo9_diversity.py (the ES priors). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-impostor-bakeoff`
**Depends on:** 15.8.1, 15.10, 15.13, 15.14
**Section refs:** audits/post-phase-14-ML-planning.md §5.2, §9 (the option vocabulary + paradigm comparison); audits/post-phase-14-ML-training-signal.md §4 (the objective spine: competence + anchor-KL + QD; referee as gate); agents/tactical/impostor_policy.py (_scored_targets :937-1009, the ladder :261); experiments/lab/ml_spike/check2_learnability.py + fo9_diversity.py (the ES priors)
**Complexity:** Integration

The wave's centerpiece: four training methods, one harness, one seed set, one report — so the pause
compares methods, not evaluation protocols. Entrants, all impostor-side, all trained and evaluated
against the baseline-3 substrate: (1) **BC/DAgger** from the FSM oracle — behavior-clone
`ImpostorPolicy.decide` on encoder-v2 features with DAgger corrections (the FSM is a free queryable
expert), reported against a pre-stated intent-agreement bar; this is the encoder-sufficiency test — if
v2 features cannot reproduce the scripted ladder, the encoder gaps are the finding; (2) **learned
utility scorer over FSM-proposed options + ES** — the conservative bounded path: keep the FSM's option
generation and replace exactly the `_scored_targets` ranking (isolation × (1−witness_risk) × cooldown,
lexical tie-break) plus the option-level choices (kill now / stalk-toward / vent-exit choice / cover /
fake-task / reposition-during-cooldown), structurally unable to emit illegal or off-menu actions; (3)
**direct masked policy net + ES** — the higher-ceiling path over the full masked intent space; (4)
**MAP-Elites** over the 15.8 behavioral descriptors with competence as cell quality — diversity as
measured archive coverage. Every ES/QD entrant optimizes the SAME fitness: the tactically-reachable
side-specific terms + potential shaping, with an anchor-KL penalty toward the frozen FSM (measured as
divergence from the FSM's choice distribution over the same states); the validity gate and the 15.2
referee are SELECTION filters applied to candidates after training — never terms in any fitness. The
crew side stays the frozen scripted FSM throughout (no co-evolution this wave). Every candidate that
reaches the report passes the 15.10 determinism harness and the leak-test factory mode; fitness may use
the 15.13 surrogate within its staleness cap, but every reported number is re-scored on a real meeting
path (fake-provider meetings on the fixed eval seed set). Also discharge the 15.14 obligation: re-run
the Goodhart probe under the surrogate meeting path and append the delta to the probe's findings in this
report.

**Files in scope:**
- training/bakeoff/harness.py (new: the entrant protocol, the fixed eval protocol, the report emitter)
- training/bakeoff/bc.py (new)
- training/bakeoff/utility_es.py (new)
- training/bakeoff/policy_es.py (new)
- training/bakeoff/map_elites.py (new)
- training/bakeoff/es.py (shared-core extensions — behind the 15.14 dependency edge)
- training/reports/report-impostor-bakeoff.md (new)
- training/reports/results-impostor-bakeoff.jsonl (new: the machine-readable per-entrant rows 15.18 consumes)
- training/artifacts/impostor/ (new: frozen candidate weights, float-hex JSON + sha256 sidecars)
- tests/training/test_bakeoff_harness.py (new)
- tests/training/test_bakeoff_methods.py (new: each entrant's train/eval loop on tiny budgets)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the anchor and oracle is read-only — nothing ships into agents/ before the PAUSE)
- eval/ (gates consumed via the 15.1/15.2 JSON contracts)
- experiments/lab/ (the torch probe is 15.17)
- training/crew/ (15.16's parallel track)

**Definition of done:**
- [ ] One harness: every entrant trains and evaluates through `training/bakeoff/harness.py` on the same fixed seed set — entrants carry no private eval loops (asserted structurally: the harness is the only module that computes reported metrics).
- [ ] Every entrant row in `results-impostor-bakeoff.jsonl` carries the full tuple: validity-gate pass, referee result (score distribution + floor-trip rate + supply floors), inner fitness, anchor-KL, impostor win rate + take-rate (reported, never gated), determinism-harness hash, leak-test pass, surrogate-staleness usage, and wall-clock.
- [ ] The BC entrant reports held-out intent agreement with the FSM against its pre-stated bar (≥0.90 top-1 unless the contract PR documents a different bar BEFORE training) and names the encoder gaps if it misses.
- [ ] The utility-scorer entrant consumes exactly the FSM's option set (a test enumerates the options on fixture states and pins the menu) — the bounded path is real, not aspirational.
- [ ] The MAP-Elites entrant reports archive coverage over the named descriptors + best-per-cell quality; single-objective entrants report their descriptor footprint for comparison.
- [ ] No unregularized champion: anchor-KL is computed for every reported candidate; candidates above the documented KL ceiling are flagged in the report, not silently dropped.
- [ ] The Goodhart probe re-run under the surrogate path is appended with a delta verdict vs the 15.14 baseline.
- [ ] The report ends with a ranked recommendation + open risks FOR THE PAUSE — explicitly not a self-declared winner; every quoted number regenerates from the committed CLIs + jsonl.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Warm-start the ES entrants from the BC solution where shapes align (the spike's BC-then-ES lesson: BC
alone caps below FSM parity on a weak encoder; ES climbs from it). The anchor-KL is cheap in pure form:
sample states from rollouts, compare the candidate's choice distribution to the FSM's deterministic
choice (a log-loss against the anchor's action works as the piKL-style penalty at this scale). Respect
the 15.13 staleness cap in the training loop config, and log every surrogate use into the jsonl rows.
Tiny-budget CI tests train for a handful of generations on 1–2 seeds — the full runs are
operator-executed and their budgets recorded in the report ($0, CPU, hours-scale).

## Public types this task introduces
- `training.bakeoff.harness.BakeoffEntrant`
- `training.bakeoff.harness.BakeoffResult`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Two failure modes. (a) Protocol drift between entrants — the single-harness rule exists because one
entrant evaluating on different seeds or a different meeting path silently un-ranks the whole
comparison; the harness owning all metric computation is the enforcement. (b) Surrogate exploitation —
a candidate that looks strong on surrogate-scored fitness and collapses on the real meeting path is the
expected shape of failure; the re-score-on-real-path rule plus the staleness cap are the guards, and the
report must show both numbers where they diverge. Also: keep every candidate's weights + config
committed under `training/artifacts/impostor/` with sha256 — the pause's finalist evaluation and any
Wave-2 productization must be able to reload the exact artifact.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-15-impostor-bakeoff` with a title like `task 15.15: the impostor bake-off: bc/dagger, utility-scorer+es, policy-net+es, map-elites`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §5.2, §9 (the option vocabulary + paradigm comparison); audits/post-phase-14-ML-training-signal.md §4 (the objective spine: competence + anchor-KL + QD; referee as gate); agents/tactical/impostor_policy.py (_scored_targets :937-1009, the ladder :261); experiments/lab/ml_spike/check2_learnability.py + fo9_diversity.py (the ES priors)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
