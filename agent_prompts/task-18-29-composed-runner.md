# Agent Prompt — 18.29 The composed meeting-outcome runner (conviction-gated ejections in training rollouts)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.29 — The composed meeting-outcome runner (conviction-gated ejections in training rollouts), anchored to training/reports/report-conviction-model.md (the GO cells: decision accuracy 0.938, recall 45/47 on the 96-meeting held-out split; `training/artifacts/conviction/verdict.json`); training/reports/report-ballot-surrogate.md (the NO-GO diagnosis this composes around: ranking top-1 0.7667 retained, decision channel all-SKIP; `SurrogateMeetingRunner` in training/surrogate/runner.py); training/surrogate/runner.py:105-148 (the use-counter doctrine BOTH components meter through); training/env.py:614-628 (the runner-factory seam). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-composed-runner`
**Depends on:** 18.16, 18.18
**Section refs:** training/reports/report-conviction-model.md (the GO cells: decision accuracy 0.938, recall 45/47 on the 96-meeting held-out split; `training/artifacts/conviction/verdict.json`); training/reports/report-ballot-surrogate.md (the NO-GO diagnosis this composes around: ranking top-1 0.7667 retained, decision channel all-SKIP; `SurrogateMeetingRunner` in training/surrogate/runner.py); training/surrogate/runner.py:105-148 (the use-counter doctrine BOTH components meter through); training/env.py:614-628 (the runner-factory seam)
**Complexity:** Integration

The verdict pair's opening: training rollouts currently run fake meetings that convict
nobody, while 65.2% of real baseline-6 meetings convict — so rosters never shrink, parity
never arises, an impostor never loses a teammate, and crew never wins by ejection inside
training. Compose the two committed instruments into a `MeetingRunner`: the conviction
model decides WHETHER the meeting convicts (the question the surrogate fails at 0.375),
and the surrogate's ranking channel decides WHO (the question it retains at 0.7667
top-1); the predicted ballots are synthesized coherently with that outcome and the
ejection actually happens in the rollout. No new weights — the composed artifact is a
manifest pinning both component shas + the bar verdict. Its OWN pre-registered
population-relative GO bar, stated here before any measurement, on the held-out corpus
test split (96 meetings / 60 ejections): (1) meeting-level decision accuracy **> 0.625**
(the strictest trivial constant on this split — always-eject); (2) among convicting
meetings, ejected-target top-1 **≥ 0.6375** (= 0.75 × the 0.8500 honest ceiling, the
standing axis-1 form); (3) exact-outcome match (ejected id or skip) REPORTED beside the
verdict, informational never gating. Pre-committed: **NO-GO ⇒ diagnostic-only** — the
campaigns run the standing plan (fake provider + conviction term) unchanged, and nothing
downstream re-plans. GO ⇒ the runner becomes an OPTIONAL campaign configuration through
18.21's runner-factory seam, adopted only at a swap boundary (the 18.24 note), with the
standing rules untouched: final champion numbers are never composed-runner-scored, and
both component staleness counters meter every composed meeting. The task also runs the
composed-path Goodhart leg (the standing rule — the probe re-runs when the
training-signal role grows; 18.18's conviction-path arms are the machinery this leg
extends): no lever family may launder composed-outcome artifacts into fitness above the
standing materiality bar, reported before any campaign adoption.

**Files in scope:**
- training/composed_runner.py (new)
- training/artifacts/composed/ (new: the component-sha manifest + verdict.json)
- training/reports/report-composed-runner.md (new)
- tests/training/test_composed_runner.py (new)

**Files NOT in scope:**
- training/surrogate/*.py + training/conviction/*.py (composed via public seams, never edited)
- training/bakeoff/harness.py + training/coevo/ (the driver seam is 18.21's; adoption is a campaign configuration, not a wiring change)
- eval/ (the referee and instruments never move; the runner is training-side only)

**Definition of done:**
- [ ] The composed runner implements the `MeetingRunner` protocol end-to-end on the fake-path test harness: conviction-gated decision, surrogate-ranked target, ballots synthesized coherently with the outcome through the REAL tally semantics, both component artifacts sha-verified on load (fail-loud before any use), both use-counters metered per meeting.
- [ ] The verdict is taken on the FIRST held-out evaluation against the pre-registered bar above, with every cell quoted beside its threshold, the exact-outcome match reported informationally, and the machine-readable consequence committed (`verdict.json`: GO ⇒ optional campaign configuration; NO-GO ⇒ diagnostic-only) — the honest diagnosis stated beside the verdict either way.
- [ ] The composed-path Goodhart leg reports its delta per forced lever against the standing bars, with component-consumption metered and quoted; any above-bar finding is a named blocker for campaign adoption, never a silent caveat.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Compose, never re-fit: both components load through their committed loaders
(`load_surrogate_runner_factory`'s fence semantics; the conviction model's sha-verified
artifact) and the composed module holds NO learned parameters of its own. The decision
gate reads the conviction model's committed P ≥ 0.5 threshold (the pinned fidelity
operating point) — never a re-tuned one. Ballot synthesis must survive the downstream
folds (the cross-meeting belief fold reads `result.ballots`): under a convict decision,
the surrogate's predicted ballots are re-anchored so the plurality lands on the ranked
target through the real `tally_ballots`; under skip, the surrogate's ballots pass through
unchanged. The §7.12 teammate firewall semantics are inherited from the surrogate runner
untouched. The fidelity evaluation mirrors `run_surrogate_fidelity`'s split discipline
(fit-side never evaluated; first-eval verdict). For the Goodhart leg, reuse 18.18's
concrete machinery over the composed runner as the meeting path:
`run_conviction_path_probe`'s arm shapes, the baseline-relative gate split, the
`_signed_relative_gain` laundering convention, and the one-shared-counter discipline —
and note the probe's recorded caveat that `prescreen-substrate-divergence` applies to any
decision-degenerate meeting model equally: the composed runner's own substrate read must
carry the same recorded-bytes pairing rule.

## Public types this task introduces
- `training.composed_runner.ComposedMeetingRunner`
- `training.composed_runner.decide_composed_go`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Compounding component errors laundering into training signal — a conviction-model false
positive plus a wrong surrogate top-1 ejects an innocent the real path would not have,
systematically, and an optimizer could learn to farm that seam. Three fences: the
pre-registered bar (a composed channel worse than the strictest trivial constant never
ships), the composed-path Goodhart leg (adoption blocks on above-bar findings), and the
standing rule that no reported champion number is ever composed-runner-scored. The
fallback is always live: NO-GO or a fired probe leaves the campaigns on the standing plan
with nothing re-planned.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-18-composed-runner` with a title like `task 18.29: the composed meeting-outcome runner (conviction-gated ejections in training rollouts)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/reports/report-conviction-model.md (the GO cells: decision accuracy 0.938, recall 45/47 on the 96-meeting held-out split; `training/artifacts/conviction/verdict.json`); training/reports/report-ballot-surrogate.md (the NO-GO diagnosis this composes around: ranking top-1 0.7667 retained, decision channel all-SKIP; `SurrogateMeetingRunner` in training/surrogate/runner.py); training/surrogate/runner.py:105-148 (the use-counter doctrine BOTH components meter through); training/env.py:614-628 (the runner-factory seam)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
