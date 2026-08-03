# Agent Prompt — 15.20 Champion productization: `agents/tactical/learned/`, the pure-Python forward pass

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.20 — Champion productization: `agents/tactical/learned/`, the pure-Python forward pass, anchored to audits/audit-phase-15-pause.md decisions 1 + 6 (champion = `utility-es`; float-hex retained; the Q4 bit-exact cross-implementation gate); training/artifacts/impostor/utility-es/ (the committed champion artifact, sha256 `6d327dcb…`); training/bakeoff/utility_es.py (the training-side reference the shipped pass must equal bit-exactly — itself pure-Python `math.fsum`; the Q4 ruling's "numpy-trained" is shorthand for training-side); training/bakeoff/harness.py::build_candidate_factory (the wrapper pattern being productized); tests/test_firewall.py (the no-numpy/torch-under-agents/ doctrine). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-champion-productization`
**Depends on:** 15.18
**Section refs:** audits/audit-phase-15-pause.md decisions 1 + 6 (champion = `utility-es`; float-hex retained; the Q4 bit-exact cross-implementation gate); training/artifacts/impostor/utility-es/ (the committed champion artifact, sha256 `6d327dcb…`); training/bakeoff/utility_es.py (the training-side reference the shipped pass must equal bit-exactly — itself pure-Python `math.fsum`; the Q4 ruling's "numpy-trained" is shorthand for training-side); training/bakeoff/harness.py::build_candidate_factory (the wrapper pattern being productized); tests/test_firewall.py (the no-numpy/torch-under-agents/ doctrine)
**Complexity:** Integration

Promote the pause's champion — the `utility-es` learned utility scorer over FSM-proposed impostor
options — into production inference: a new `agents/tactical/learned/` package holding (a) the champion
weights as a committed float-hex artifact + sha256 sidecar, value-identical to
`training/artifacts/impostor/utility-es/weights.json` (a test pins byte equality of the weights payload
and sha equality with the training-side sidecar); (b) a pure-Python forward pass — the 19-weight linear
scorer over the `impostor-option-features-v1` option-feature basis, ported from
`training/bakeoff/utility_es.py` with NO numpy/torch import (the champion's pass is a `math.fsum`
linear score; it contains no transcendental, so the decision-6 libm scope note is discharged by
construction); (c) `build_learned_agent_factory()` beside the scripted default — impostors run the
learned scorer, crew delegate to the FSM, meeting protocol forwarded to the wrapped `TacticalAgent`
exactly as `build_candidate_factory` does today, and the factory exposes its five stamp fields
(policy_id `utility-es`, method, encoder `impostor-option-features-v1`, the committed sha, the anchor)
as PLAIN STRINGS on an engine-free local record — importing `orchestrator.replay`'s
`TacticalPolicyStamp` from `agents/` would chain `agents → orchestrator → engine` and break the
firewall contract, so the real stamp object is constructed by 15.21's CLI in `scripts/`, which may
import orchestrator freely. The scripted FSM stays in-tree untouched as the
default, the anchor, the BC oracle, and the fallback. The Q4 gate is the task's spine: a committed test
drives BOTH implementations — the training-side scorer and the shipped pure-Python pass — over the
committed weights across a recorded decision stream (fixed seeds, full option menus) and asserts
BIT-EXACT equality of every score and every chosen intent; plus the full 15.10 acceptance stack through
the learned factory (determinism harness double-run, leak-test factory mode, firewall test extension).

**Files in scope:**
- agents/tactical/learned/ (new package: forward pass, weights loader + committed weights artifact + sha256 sidecar, factory)
- tests/agents/test_learned_policy.py (new: forward-pass unit tests, weights/sha parity pins, the Q4 bit-exact cross-implementation test)
- tests/training/test_learned_factory_acceptance.py (new: determinism-harness + leak-test runs through `build_learned_agent_factory()`)
- tests/test_firewall.py (extension region: `agents/tactical/learned/` explicitly swept by the no-numpy/torch check)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py + crewmate_policy.py (the FSM default is untouched — anchor, oracle, fallback)
- training/bakeoff/ (the numpy reference is consumed read-only by tests; porting means re-implementing, not importing, under agents/)
- training/artifacts/ (the training-side artifact is the frozen source of truth; the agents-side copy pins to it by test)
- orchestrator/game.py + scripts/ (the CLI/config selection surface is 15.21's)

**Definition of done:**
- [ ] `agents/tactical/learned/` imports nothing from `engine/`, `training/`, numpy, or torch (import-linter + the extended firewall test prove it), and `uv run python -c "import agents.tactical.learned.factory"` succeeds on a bare tree.
- [ ] The committed agents-side weights artifact is value-identical to `training/artifacts/impostor/utility-es/weights.json` and its sha256 sidecar equals the training-side sidecar (`6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`) — both pinned by test.
- [ ] The Q4 bit-exact gate: over the committed float-hex weights and a fixed recorded decision stream, the training-side scorer and the shipped pure-Python pass produce bit-identical float64 scores and identical chosen intents (a test, not an architecture change — the owner-ratified libm posture, whose "numpy-trained" reads training-side: the reference is itself pure-Python `math.fsum`).
- [ ] The learned factory passes the 15.10 determinism harness (double-run hash equality over the (feature, score, intent) stream plus frozen-policy full-game state-hash equality) and the leak-test factory mode through `build_learned_agent_factory()` itself.
- [ ] The factory's stamp accessor returns the five stamp fields (policy_id, method, encoder_version, weights_sha256, anchor_policy) as plain strings on an engine-free record, with `weights_sha256` equal to the committed sidecar digest — 15.21 constructs the real `TacticalPolicyStamp` from them — so the recording surfaces cannot mis-stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The champion is deliberately the SMALL one: 19 float64 weights over 18 option features + bias, linear,
no activation — the reference forward pass is `math.fsum(weight*feature for …) + bias` per option
(`training/bakeoff/utility_es.py::_score`) and an argmax with the menu's deterministic tie-break. Port
the accumulation VERBATIM: `math.fsum` is correctly rounded and order-independent, so the bit-exact
hazard is not summation order — it is substituting a naive `sum()` loop (or numpy) for `fsum`, which
diverges in the last ULP. Two porting snags the faithful port must handle: (a) the reference module's
one live `engine.world` import feeds only `_sabotage_kinds`, which `enumerate_options` immediately
discards — drop it, or the firewall contract breaks; (b) the argmax tie-break uses
`training.bakeoff.harness.intent_key` (a pure `ActionIntent.model_dump` serialization) — reimplement it
agents-side, don't import it. The 18 feature names are in the committed `config.json`. Mirror
`build_candidate_factory`'s wrapper pattern (wrap the real `TacticalAgent`, override the impostor
intent, `__getattr__`-forward the meeting protocol) rather than inventing a new agent class.

## Public types this task introduces
- `agents.tactical.learned.forward.LearnedImpostorScorer`
- `agents.tactical.learned.factory.build_learned_agent_factory`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The one real hazard is silent divergence between the two forward passes — an `fsum` swapped for a
naive sum, a float32 intermediate, a quantization mismatch in a feature — which the Q4 bit-exact test
exists to make loud.
Keep the agents-side artifact a COPY pinned by test, not a cross-package import: `agents/` importing
`training/` would breach the dependency posture the firewall enforces. The determinism harness and leak
test must run through the REAL factory (`build_learned_agent_factory()`), not a test double — the
15.15 lesson that acceptance through one's own factory is what makes the result transferable.

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
Open a PR from branch `phase-15-champion-productization` with a title like `task 15.20: champion productization: `agents/tactical/learned/`, the pure-python forward pass`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md decisions 1 + 6 (champion = `utility-es`; float-hex retained; the Q4 bit-exact cross-implementation gate); training/artifacts/impostor/utility-es/ (the committed champion artifact, sha256 `6d327dcb…`); training/bakeoff/utility_es.py (the training-side reference the shipped pass must equal bit-exactly — itself pure-Python `math.fsum`; the Q4 ruling's "numpy-trained" is shorthand for training-side); training/bakeoff/harness.py::build_candidate_factory (the wrapper pattern being productized); tests/test_firewall.py (the no-numpy/torch-under-agents/ doctrine)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
