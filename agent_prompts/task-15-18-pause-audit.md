# Agent Prompt — 15.18 The pause: mid-phase audit, the seven decisions, and authoring Wave 2

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.18 — The pause: mid-phase audit, the seven decisions, and authoring Wave 2, anchored to audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; tasks/post-phase-14-plan.md (the roadmap the decisions feed); owner decisions 2026-07-05 (deployment + torch deferred to this pause). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-pause-audit`
**Depends on:** 15.12, 15.13, 15.15, 15.16, 15.17
**Section refs:** audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; tasks/post-phase-14-plan.md (the roadmap the decisions feed); owner decisions 2026-07-05 (deployment + torch deferred to this pause)
**Complexity:** Integration

The wave boundary the phase was designed around: measure, decide, then author Wave 2 from evidence
instead of forecasts. Inputs (all machine-readable, all reproducible by the committed CLIs):
`results-impostor-bakeoff.jsonl` + `results-crew-track.jsonl` + `report-torch-probe.md` (per-entrant
gate/referee/fitness/KL/determinism/cost), `report-ballot-surrogate.md` (fidelity vs honest ceiling +
verdict), `report-goodhart-probe.md` (+ the 15.15 surrogate-path re-run), the corpus MANIFESTs + gate
outputs, and the Wave-0 close audit (the funnel deltas the whole phase now stands on — including its
§5 watch items, which this audit must SETTLE, not re-flag: the 4p1i eject-happiness uptick
(report-meeting ejections 10 → 22, accuracy 0.923 → 0.808 at the 15.7 re-record) is adjudicated
variance-or-shift against the corpus's fresh 50-seed 4p1i evidence via the committed CLIs). Plus ONE fresh
measurement this task runs: the operator-run REAL-LLM finalist evaluation — the top 1–2 bake-off
candidates re-recorded on the canonical 50-seed 9p2i set against `Qwen/Qwen3-32B` (Featherless $0,
~2.5h per finalist), scored by `scripts/validity_gate.py` + `scripts/measure_baseline.py
--watchability --funnel`, so the method decision rests on at least one real-meeting-path measurement,
not only fake-provider/surrogate numbers. The RAW finalist recordings stay uncommitted working
artifacts (they do NOT replace or join `replays/samples/` or `replays/ml_corpus/`, and they are
re-recordable from the documented recipe); what IS committed is their measurement: the per-finalist
gate/referee/funnel CLI outputs land as `training/reports/results-finalist-eval.jsonl`, the artifact
every audit number traces to. The audit
(`audits/audit-phase-15-pause.md`) tabulates every entrant on the single protocol and records the SEVEN
owner decisions with rationale: (1) winning method + champion candidate; (2) deployment end-state —
opt-in factory beside the FSM default vs new default + baseline-4 re-record; (3) torch — promote / keep
experiment-tier / retire, incl. the distillation route; (4) Wave-2 co-evolution GO/NO-GO (scoped only if
GO, with the full stabilizer stack); (5) the crew observation-surface change (owned-task set) YES/NO;
(6) inference weight representation — float-hex vs int-quantized — plus an enumeration of every
determinism loosening now live; (7) the surrogate re-grounding cadence going forward. Then this task
AUTHORS the Wave-2 contracts into this file (IDs 15.19+, every validator rule honored: full contract
fields, scope-overlap edges, the CI tail), regenerates prompts, and replaces the end-of-phase
merge-criteria placeholder with the real criteria for the chosen deployment branch.

**Files in scope:**
- audits/audit-phase-15-pause.md (new)
- training/reports/results-finalist-eval.jsonl (new: the committed per-finalist gate/referee/funnel CLI outputs — measurement data, not code)
- tasks/phase-15.md (Wave-2 contracts + STATUS banner update + end-of-phase merge criteria)
- agent_prompts/ (mechanically regenerated task-15-* prompts for the new Wave-2 contracts — generator output, never hand-edited)

**Files NOT in scope:**
- training/ code + eval/ + agents/ + engine/ + orchestrator/ (measurement is read-only — the finalist jsonl above is CLI output data, not code; any referee patch the Goodhart findings demand becomes a Wave-2 contract, never a pause edit)
- replays/samples/ + replays/ml_corpus/ (untouched; finalist recordings live outside both)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; any design amendment the decisions imply is recorded as an ask in the audit)

**Definition of done:**
- [ ] The audit tabulates every entrant (bake-off, crew, torch, distilled student) on the single metric tuple, with every quoted number regenerated from the committed CLIs/jsonl — zero hand-computed figures (each table cites its source artifact).
- [ ] The real-LLM finalist evaluation is run; its gate + referee + funnel results are committed as `training/reports/results-finalist-eval.jsonl` and quoted from there (the recording recipe — seeds, config, exact commands — documented in the audit for full re-derivation), and its divergence (if any) from the fake-provider/surrogate numbers is analyzed — the method decision explicitly cites it. The recipe names the Python seam (`run_tournament_eval(agent_factory=…, tactical_policy_stamp=…)` — `scripts/run_tournament.py` carries a stamp flag but NO agent-factory flag, so the stamp CLI alone cannot drive a learned policy), and the recorded games' `tactical_policy` stamp `weights_sha256` MUST equal the champion artifact's committed sha256 — the machine-checkable proof that the learned factory, not the FSM default wearing a champion label, produced the recorded bytes. Because the raw recordings stay uncommitted working artifacts, the proof must SURVIVE in the committed output: every `results-finalist-eval.jsonl` row carries the finalist's recorded five-field `tactical_policy` stamp (read back from the recording bytes at measurement time, never echoed from the launch config) plus the committed artifact sha it was verified against, so a post-15.18 reviewer re-checks the equality from the jsonl + the committed sidecar alone.
- [ ] All seven decisions are recorded with owner sign-off and rationale, including the NO paths (what was rejected and why).
- [ ] The Wave-2 contracts are authored into this file per the chosen branch, `uv run python scripts/validate_task_docs.py` + `uv run python scripts/generate_prompts.py --check` pass with the new contracts, and the STATUS banner + end-of-phase merge criteria reflect the decisions.
- [ ] The pause explicitly re-verdicts the referee: for each channel where EITHER probe run found an exploit, the recommended floor is contracted into Wave 2 before any champion selection uses the referee — "cleared" is available only for channels where neither run found an exploit (the 15.14 raw-geomean D2-separation exploit, 6.51 → 16.62, lands its conversion-coupled floor regardless of the composed referee's HELD). The SAME Wave-2 referee-hardening contract bundles the subject-AWARE observation-backing re-anchoring (owner-ratified 2026-07-09, mid-wave review Q2: parity was correct for 15.2's cross-implementation evidence, but a trained impostor can exploit subject-agnostic backing — utter a genuine vent sighting of X in the turn that accuses innocent Y and the Y-accusation counts "backed"): floors re-pinned under the subject-aware definition on the same bytes so relative gates stay sound, the old parity fixture kept as a frozen historical pin, landed before any champion selection leans on fine D2-conversion differences.
- [ ] Canary denominators follow the owner-ratified rule (2026-07-09, Q3): canaries are judged on the LARGEST same-substrate, validity-gated set available (today: the corpus — genuine-class conversion 34/52 = 0.654) with the 50-seed samples figure reported alongside for ladder continuity; the samples sets remain the byte-identity/provenance anchor. Corollary recorded in the decisions: if decision 2 lands on branch B, baseline 4 requires a corpus-scale companion record before its canaries mean anything at n≈13.
- [ ] Decision 6 (weight representation + determinism-loosening enumeration) records the owner-ratified libm posture (2026-07-09, Q4): no libm-free forward pass is demanded; instead the Wave-2 productization contract MUST gate on bit-exact equality of the numpy-trained and pure-Python-shipped forward passes over the committed float-hex weights (a test, not an architecture change); if decision 6 int-quantizes, a fixed-point forward pass makes tanh a table lookup and cross-host generation falls out nearly free — otherwise same-host generation scope is documented and accepted (replay byte-identity is untouched by libm either way).
- [ ] Provenance-durability convention (owner-ratified 2026-07-09, Q5), effective from this task onward: every operator record (the finalist recipe here, any baseline-4 or future corpus) creates an annotated git tag at the recording commit or back-fills the post-squash main sha into its MANIFEST; existing MANIFESTs are left as-is (byte-verification is the operative guarantee). The finalist recipe in this audit demonstrates the convention.
- [ ] The Wave-0 close audit's §5 watch items are settled by data, not carried forward: the 4p1i eject-happiness cell is re-measured on the corpus's 4p1i set (funnel + R-gate via the committed CLIs) with a PRE-REGISTERED adjudication — a two-proportion test (corpus-4p1i vs post-15.7 samples ejection accuracy) whose SHIFT verdict requires the 95% CI to exclude the compared value; if the CI excludes neither (the expected outcome at n≈33 ejections), the audit records UNDERPOWERED with the n rather than a judgment call; if a real shift, its Wave-2 implication (if any) is recorded in the decisions.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Model the audit on `audits/post-phase-14-pause.md` (label discipline, verdict-in-one-line, punch list)
and the decision block on Task 14.6's LOCKED-DECISION shape. The Wave-2 sketch at the bottom of this
file is the authoring skeleton — each bullet becomes a contract or is explicitly dropped with a reason.
When authoring contracts, re-read `scripts/_task_parser.py`'s rules (header em-dash, ID grammar,
contract field order, scope-overlap semantics, globally-unique public types) — the validator is the
gate, and the new prompts must be generator output.

## Integration risk

Self-certification is the trap this task exists to prevent — every number must trace to a committed
artifact, and the referee cannot bless a champion until its own red-team verdict is resolved. The second
trap is validator-invalid Wave-2 contracts: a malformed `tasks/phase-15.md` breaks
`validate_task_docs.py` for the WHOLE repo (the parser aggregates all phases), so the authoring step
must run the full check locally before the PR. Third: the finalist recordings must stay out of
`replays/samples/` and `replays/ml_corpus/` — provenance separation between "the canonical baseline,"
"the frozen training corpus," and "pause working artifacts" is what keeps every later claim
attributable.

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

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-15-pause-audit` with a title like `task 15.18: the pause: mid-phase audit, the seven decisions, and authoring wave 2`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; tasks/post-phase-14-plan.md (the roadmap the decisions feed); owner decisions 2026-07-05 (deployment + torch deferred to this pause)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
