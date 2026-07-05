# Agent Prompt — 15.10 Encoder v2 (memory-carrying), the determinism harness, and the leak-test factory mode

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.10 — Encoder v2 (memory-carrying), the determinism harness, and the leak-test factory mode, anchored to audits/post-phase-14-ML-planning.md §6 (observation surface, encoder shape, determinism hazards); observation/packet.py:159-188; observation/public_map.py:14-32; agents/memory/beliefs.py + agents/memory/working.py (the carried state); experiments/lab/ml_spike/core.py:60-83 (the 34-dim memoryless baseline); eval/leak_test.py; tests/test_firewall.py:64-75. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-encoder-v2`
**Depends on:** 15.8
**Section refs:** audits/post-phase-14-ML-planning.md §6 (observation surface, encoder shape, determinism hazards); observation/packet.py:159-188; observation/public_map.py:14-32; agents/memory/beliefs.py + agents/memory/working.py (the carried state); experiments/lab/ml_spike/core.py:60-83 (the 34-dim memoryless baseline); eval/leak_test.py; tests/test_firewall.py:64-75
**Complexity:** Integration

The spike's 34-dim encoder is memoryless — the structural reason its behavior clone capped below FSM
parity (the FSM's stalk is history-dependent). Build the versioned production encoder in
`agents/tactical/features.py`: pure-Python, deterministic, firewall-legal, consuming `ObservationPacket`
+ `PublicMapView` + the agent's OWN memory (`MemoryStore` episodic recency, `WorkingMemory.last_seen`
(tick, room) ages, own `BeliefState` suspicion/trust floats — quantized to a fixed grid before they
touch any feature, per the §6.3 determinism hazard), with an `ENCODER_VERSION` constant that feeds the
15.9 stamp. Ship the two harnesses every candidate must pass: `training/determinism.py` (double-run
SHA-256 over the full (feature-vector, logits, chosen-intent) stream of a frozen policy across a fixed
seed set, plus frozen-genome full-game state-hash equality) and an agent-factory mode for
`eval/leak_test.py` — today it walks 3 scripted fixtures with no factory parameter, so a learned mover
that drives the engine into regions those fixtures never reach is unscanned; the extension runs
factory-built agents through full games and applies the existing recursive role-leak scanners to every
packet the encoder consumes. Extend `tests/test_firewall.py` with the pure-Python inference doctrine: no
`numpy`/`torch` import anywhere under `agents/`.

**Files in scope:**
- agents/tactical/features.py (new: the versioned encoder)
- training/determinism.py (new: the policy determinism harness)
- eval/leak_test.py (agent-factory mode region — the 3 scripted fixtures stay byte-identical)
- tests/test_firewall.py (extend: numpy/torch ban under agents/)
- tests/agents/test_features.py (new)
- tests/training/test_determinism.py (new)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py + crewmate_policy.py (the FSMs are the anchor and the BC oracle — untouched)
- observation/ (NO packet surface change: the un-observable crew task-set stays un-observable pending the pause decision)
- agents/memory/ (read-only: the encoder consumes the stores, never mutates them)
- .importlinter (contracts landed in 15.6/15.8)

**Definition of done:**
- [ ] The encoder is engine-free (existing `agents ↛ engine` contract + the schema-file firewall test cover it) and total over every packet shape in the committed corpora: a sweep test feeds all committed games' packets through it without error.
- [ ] Feature layout + dimension count are documented and pinned by a golden test; `ENCODER_VERSION` bumps are the only way the layout may change.
- [ ] Belief-derived features are integer-quantized with lexical tie-breaking documented — no raw-float comparison anywhere in the encoder (the residue-flips-argmax hazard).
- [ ] Determinism harness: two runs of a frozen policy over a fixed seed set produce identical SHA-256 over (features, logits, intents); the harness is a library any bake-off entrant invokes, and its report is the artifact 15.15 quotes.
- [ ] Leak-test factory mode passes for the FSM default factory AND a learned-wrapper factory; a planted role-leak fixture trips it (the scanner still bites).
- [ ] The firewall test rejects a synthetic `import numpy` planted under `agents/` (asserted via the same source-scan mechanism as the engine-import check).
- [ ] Weights serialization is fixed for Wave 1: float64-hex JSON, exact round-trip pinned by test; the int-quantization decision is explicitly deferred to the PAUSE (stated in the module docstring).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The memory features already exist and are cheap: per-player `(suspicion, trust)` floats
(`agents/memory/beliefs.py:440-457`), `LastSeen(tick, room)` (`agents/memory/working.py:49-55`), and
episodic recency from `MemoryStore.recent()`. `moved_players` is omitted from the packet JSON when
empty — treat it as optional, never `[]`-assumed. Roster-dependent features need fixed-slot encoding
sorted by `player_id` (the repo's lexical-tie-break idiom). The crew side may only consume belief state
the crew agent legitimately holds — the same information that already reaches crew tactics through
`EmergencyPacingTracker._over_gate`; document any widening explicitly in the docstring so the leak
review has one place to look.

## Public types this task introduces
- `agents.tactical.features.TacticalFeatureEncoder`
- `agents.tactical.features.ENCODER_VERSION`
- `training.determinism.PolicyDeterminismReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The encoder is the one place role-blind observation and role-private memory meet: a feature that folds
in another agent's private state is a firewall breach the import-linter cannot see — which is why the
leak-test factory extension lands in the SAME task, not later. Second risk: determinism — belief floats
accumulate non-power-of-two deltas and `known_players()` is dict-insertion-ordered; quantize-then-compare
and sorted iteration are mandatory, and the harness hashes features+logits precisely so a violation is
caught at the artifact, not in a downstream replay.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`

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
Open a PR from branch `phase-15-encoder-v2` with a title like `task 15.10: encoder v2 (memory-carrying), the determinism harness, and the leak-test factory mode`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §6 (observation surface, encoder shape, determinism hazards); observation/packet.py:159-188; observation/public_map.py:14-32; agents/memory/beliefs.py + agents/memory/working.py (the carried state); experiments/lab/ml_spike/core.py:60-83 (the 34-dim memoryless baseline); eval/leak_test.py; tests/test_firewall.py:64-75), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
