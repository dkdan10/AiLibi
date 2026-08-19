# Agent Prompt — 18.21 The alternating-freeze driver + stabilizers

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.21 — The alternating-freeze driver + stabilizers, anchored to audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-alternating-driver`
**Depends on:** 18.17, 18.20
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams)
**Complexity:** Integration

The campaign engine: an alternating-freeze loop — evolve one side's population (the
standing ES) against a PFSP-sampled slate of frozen opponents while the other side is
frozen, freeze the champion into the hall of fame, swap sides, repeat — with the full
stabilizer instrumentation emitted per generation: the absolute anchor benchmark (champion
vs scripted FSM, both directions — the cycling detector: oscillating co-matchup with a flat
anchor = cycling, monotone anchor = progress), a per-side short-horizon exploiter probe (a
small ES bred purely to beat the current champion; its found exploits join the hall of
fame), and the anchor-CE term retained toward the FIXED scripted FSM on both sides (never
toward the moving opponent). One side moves at a time, always — the barred simultaneous
form is structurally unreachable. The driver additionally exposes TWO ADDITIVE
seams, each inert when unset (digest-identical): a per-swap scenario-provider callable
(18.23's scenarios) and an optional meeting-runner factory per campaign configuration
(default: the fake provider) — the slot 18.29's composed runner (or any future GO-verdict
runner) plugs into without ever editing the frozen driver. Deterministic end-to-end on the fake/surrogate path;
machine-readable campaign rows.

Three merged hand-offs now bind this contract (18.20 at 4173ef1, 18.22 at ea0eb62, 18.29 at
6339116 — all verified against their contracts). (a) HALL-OF-FAME CONSUMPTION DISCIPLINE:
the driver constructs ONE `OpponentStalenessLedger` per run from the cap + the pool's
member shas, `register`s every freshly frozen champion, and treats a capped opponent as
RETIRE-AND-REPLACE (fresh sha) — never an in-place reset; "one generation use" means one
use per DISTINCT sampled member per driver generation, and `sample_opponents` draws WITH
replacement, so the driver dedupes the slate before metering; payoff maps passed to the
sampler must exactly cover the pool (empty = cold-start uniform is the only exception);
founders ingest through the substrate-fenced `ingest_map_elites_founders` BEFORE any pool
build or sampling; `HallOfFame.create` pins the campaign substrate sha, and TWO sha
definitions exist (the 18.24 block: `compute_substrate_sha` composite vs
`bakeoff_substrate_sha` raw MANIFEST) — the driver names which one it passes, in the row
schema. Per-side campaign constants (caps, floors) are this driver's to own;
`DEFAULT_COEVO_ARTIFACT_ROOT` is exported for it. (b) COMPOSED-RUNNER ADOPTION MECHANICS:
the meeting-runner factory seam adopts 18.29 ONLY via `load_composed_runner_factory` on
its DEFAULT path (the committed-GO gate + sha cross-check; `composed_artifact_dir=None` is
a diagnostics-only escape, never a campaign configuration), and only at a swap boundary;
under a composed configuration the row schema's "conviction/surrogate consumption" means
BOTH component counters (gate reads + probe reads), and
`verdict.json.adoption_constraints` is surfaced verbatim in the campaign meters — composed
pre-screen reads are spend advice paired with recorded-bytes floor reads, composed-substrate
probe reads are diagnostic-grade, and champion numbers are never composed-runner-scored.
(c) V3-FAMILY ENTRANT CONFIGS: the per-side entrant config carries `encoder_version` (v2
default, byte-identical artifacts); a hall/side stays SINGLE-FAMILY per campaign (a mixed
family fails loud only at genome-length reload), so the driver pins the family in config —
HoF rows deliberately carry no encoder stamp.

**Files in scope:**
- training/coevo/driver.py (new)
- tests/training/test_coevo_driver.py; (a miniature two-swap campaign on tiny budgets: freeze/swap mechanics, HoF growth, benchmark emission, exploiter integration, determinism digest)

**Files NOT in scope:**
- training/coevo/hall_of_fame.py + factory.py + rollout.py (consumed)
- training/bakeoff/es.py (the optimizer is imported unchanged)

**Definition of done:**
- [ ] A miniature campaign (2 swaps, tiny budgets) runs deterministically twice with identical digests, grows the hall of fame with full provenance, emits the absolute-benchmark and exploiter rows per generation, and never updates both sides in one step (structurally asserted).
- [ ] The campaign row schema carries everything 18.24's report needs (per-gen fitness, anchor benchmarks both directions, opponent slate shas, exploiter outcomes, conviction/surrogate consumption).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The driver owns ALL the meters (surrogate + conviction use counters threaded once,
cumulative — the harness's one-term/one-counter `resolved_conviction_term()` pattern) — a
campaign that exhausts a cap must stop loudly at a swap boundary, which is the natural
re-grounding point. Consume `CoevoRolloutResult`'s episode-local traces under the 18.19
fold-after-scoring discipline (fresh per-episode traces, fold into accumulators AFTER
scoring, `anchor_policy` inherited from config never from accumulators — the #306 P2 fix
constrains cross-seed accumulation). The exploiter probe is the standing ES at a tiny budget
(e.g. 5×6) with fitness = beat-the-champion only.

## Public types this task introduces
- `training.coevo.driver.run_alternating_freeze`
- `training.coevo.driver.CoevoCampaignRow`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is where compounding budgets can silently explode: population × generations × seeds ×
opponent-slate size. The driver must compute and log its total game count up front and
refuse a configuration whose fake-path game count exceeds a stated ceiling without an
explicit override flag — no accidental week-long runs.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-alternating-driver` with a title like `task 18.21: the alternating-freeze driver + stabilizers`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
