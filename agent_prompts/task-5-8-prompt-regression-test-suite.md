# Agent Prompt — 5.8 Prompt regression test suite

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.8 — Prompt regression test suite, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-prompt-regression-test-suite`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

The prompt regression suite — **this task IS the Phase 5 close gate**: it must
demonstrate one full loop, a prompt-template change producing a measurable,
attributable metric delta in the tournament report, deterministically in CI.

The enabling insight: the Phase 5 metrics are pure analyzers over a
`TournamentReport`, which is assembled from replay records — and recorded real
meetings already exist as replay JSONL under `replays/samples/` (the
meeting-bearing seeds carry real transcripts, ballots, and contradictions, with
their prompt-template versions logged in `replays/samples/MANIFEST.md`). So the
regression suite needs NO live model and NO engine re-run: build a
`TournamentReport` from frozen recorded JSONL plus a deterministically-derived
`roles` map, run the four metrics, and compare to a committed baseline. The
`FakeProvider` is NOT usable here — it emits empty/stub outputs, so a fake run
yields trivial metric values; the regression signal must come from recorded
real outputs.

`roles` is the one field not in the JSONL; derive it deterministically from the
seed via `orchestrator.seeder.seed_initial_state(seed, num_players,
num_impostors).players[id].role` — no LLM, no network, fully reproducible.

**Decisions resolved (record any deviation in the PR's `## Decisions` block):**
- **Fixture provenance: a frozen, owned copy under
  `tests/fixtures/prompt_regression/`, NOT the live `replays/samples/`.** The
  live samples are rewritten by `scripts/refresh_samples.sh`; a regression
  baseline must be stable. Copy a small set of meeting-bearing seeds' replay
  JSONL into the fixture dir, tagged by prompt version (from MANIFEST).
- **Report build path: promote a public loader in `eval/balance_eval.py`.**
  Extract the existing per-seed assembly (`_game_report_from_replay` +
  `_game_cost_summary`) into a public `load_tournament_report(replay_dir, *,
  roles_by_seed)` (refactor-only, no behavior change to `run_tournament_eval`,
  which keeps using the same code). The regression module calls it — it does
  NOT duplicate the record→`GameReport` mapping (avoids drift from 5.6).
- **`roles` for fixtures: derived at test time via `seed_initial_state`**, not
  stored in the fixture (decoupled, no duplicated ground truth).
- **Regression signal: exact-match on frozen fixtures.** Because the fixtures
  are recorded and the metrics are deterministic, the baseline metric scalars
  are exact; any drift is a real regression in a metric, the loader, or the
  schema. The `> X%` tolerance is the documented policy for the *manual*
  real-provider re-record comparison (via `refresh_samples.sh`), which is out of
  CI; state the chosen X and that CI uses exact match.

**Files in scope:**
- eval/prompt_regression.py
- eval/balance_eval.py (promote `load_tournament_report` from the existing private assembly; refactor-only)
- tests/fixtures/prompt_regression/ (frozen recorded replay JSONL tagged by prompt version + a committed baseline of expected metric scalars)
- tests/eval/test_prompt_regression.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ provider behavior
- api/
- frontend/
- eval/report_schema.py, eval/vote_correctness.py, eval/accusation_calibration.py, eval/alibi_fabrication.py, eval/cost_dashboard.py, eval/meeting_quality.py (consume their public APIs; do not modify)
- scripts/refresh_samples.sh (the real-provider re-record path; referenced, not modified)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/prompt_regression.py` builds a `TournamentReport` from a fixture directory of recorded replay JSONL (via the promoted `eval.balance_eval.load_tournament_report`, with `roles` derived from `seed_initial_state`), runs `eval.meeting_quality.build_tournament_eval_report`, and produces a metric summary tagged by the prompt-template versions in play (from `GameReport.prompt_versions`). No network, no live/fake model call to generate outputs.
- [ ] A committed baseline (e.g. `tests/fixtures/prompt_regression/baseline.json`) records the expected metric scalars per prompt version. `tests/eval/test_prompt_regression.py` asserts the computed summary matches the baseline EXACTLY for the frozen fixtures; a mismatch fails the test (a real metric/loader/schema regression). The `> X%` tolerance is documented as the policy for the manual real-provider re-record path; CI uses exact match.
- [ ] **Close-gate demonstration:** the suite includes TWO prompt-version fixture sets — a baseline version `v_a` and a variant `v_b` whose recorded meeting outputs differ such that at least one metric (e.g. alibi-fabrication survival rate or vote-correctness rate) measurably changes. A test asserts the regression suite DETECTS the delta and ATTRIBUTES it to the prompt-version change (via `prompt_versions` provenance and/or the cost-per-version breakdown). This is the prompt-change → metric-diff loop, run deterministically without a model.
- [ ] Results are tagged by prompt version (the summary keys by `(template_name, version)` or the per-version provenance), so a delta is traceable to which template changed.
- [ ] Tests use recorded fixtures only and make no network calls; `AILIBI_LLM_PROVIDER` is irrelevant (no provider is invoked).
- [ ] `load_tournament_report` is a behavior-preserving extraction: `run_tournament_eval` and the existing `test_balance_eval.py` / `test_tournament_report.py` still pass unchanged.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` and `uv run python scripts/validate_task_docs.py` pass.
- [ ] `uv run pytest` passes; `bash scripts/check.sh` passes locally.

## Implementation hint

For each fixture seed, derive roles with
`seed_initial_state(seed, num_players=…, num_impostors=…).players` (the same
deterministic setup the loader's `_seeded_roles` uses), call
`load_tournament_report(fixture_dir, roles_by_seed=…)` → `TournamentReport`,
then `build_tournament_eval_report(report)` → pull scalars
(`vote_correctness.vote_correctness_rate`,
`alibi_fabrication` survival rate, `accusation_calibration.*_ece`,
`cost_dashboard.total_cost_usd` + `per_prompt_version`). Pick a couple of
meeting-bearing sample seeds (e.g. 22/24/26 per MANIFEST) and copy their
`replay-seed-N.jsonl` into `tests/fixtures/prompt_regression/v_a/`. For `v_b`,
either copy a different recorded run of the same seeds at a different prompt
version, or hand-author a minimal variant transcript that moves one metric
(e.g. add an `alibi_conflict` contradiction so an impostor alibi flips from
survived to caught); commit it under `…/v_b/` tagged with a distinct
`prompt_versions`. Keep fixtures small — a few seeds is enough to pin the loop.

To regenerate fixtures from a real provider (manual, out of CI): change the
prompt template, run `scripts/refresh_samples.sh --meetings`, copy the new
samples into the fixture dir, and update `baseline.json`. Document this
provenance procedure in the module docstring.

## Public types this task introduces
- `eval.prompt_regression.PromptRegressionSummary`
- `eval.prompt_regression.run_prompt_regression`
- `eval.balance_eval.load_tournament_report`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task is the Phase 5 acceptance gate; getting the loop genuinely
demonstrated (not stubbed) is the point.

- **Determinism is everything.** Recorded fixtures + pure analyzers + derived
  roles = byte-stable metric values. Never invoke a real OR fake model to
  generate outputs in the suite — a fake run produces empty meetings and a
  meaningless signal. If a metric value is not reproducible from the frozen
  fixture, the fixture or the loader is wrong.
- **The `load_tournament_report` extraction must not change `run_tournament_eval`
  behavior.** It is a pure refactor of code 5.6 already shipped; the existing
  loader/integration tests are the guardrail.
- **The close-gate demo must be a REAL delta, not a tautology.** `v_b` must
  differ from `v_a` in recorded outputs such that a metric genuinely moves and
  the suite reports it; a test that asserts `report_a != report_b` by comparing
  unrelated fields does not demonstrate the loop. Tie the asserted delta to a
  specific metric and to the changed prompt version.
- **Fixtures are frozen.** Do not point the suite at `replays/samples/` (those
  get rewritten); copy what you need into `tests/fixtures/prompt_regression/`.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import eval.cost_dashboard"`
- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`
- `uv run python -c "import eval.alibi_fabrication"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.vote_correctness"`

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
Open a PR from branch `phase-5-prompt-regression-test-suite` with a title like `task 5.8: prompt regression test suite`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
