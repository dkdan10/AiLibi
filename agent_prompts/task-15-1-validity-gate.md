# Agent Prompt — 15.1 Validity gate + baseline measurement CLIs (make the audit-cited scripts real)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.1 — Validity gate + baseline measurement CLIs (make the audit-cited scripts real), anchored to tasks/post-phase-14-clean-up.md H1; audits/audit-phase-14-close.md §1, §3, §8 (the gate criteria + R-gate rows this task productizes); audits/post-phase-14-pause.md §2.1 (the missing-harness finding); audits/post-phase-14-ML-training-signal.md §3 (the three-artifact split); eval/vote_correctness.py; eval/meeting_quality.py; eval/balance_eval.py; scripts/_verify_samples.py. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-validity-gate`
**Depends on:** none
**Section refs:** tasks/post-phase-14-clean-up.md H1; audits/audit-phase-14-close.md §1, §3, §8 (the gate criteria + R-gate rows this task productizes); audits/post-phase-14-pause.md §2.1 (the missing-harness finding); audits/post-phase-14-ML-training-signal.md §3 (the three-artifact split); eval/vote_correctness.py; eval/meeting_quality.py; eval/balance_eval.py; scripts/_verify_samples.py
**Complexity:** Medium

Turn the measurement harness from audit prose into committed code. The Phase-14 close audit grounds
every number in `scripts/validity_gate.py` (the HARD validity gate) and `scripts/measure_baseline.py`
(the R-gate measurement) — neither exists in the tree, and `eval/` has no CLI entrypoint at all (no
`__main__`/`argparse` anywhere in the package). This task creates `eval/validity.py` (the library fold)
and the two CLIs under those exact audit-cited filenames, by WIRING the existing committed folds —
ejection accuracy and genuine-class conversion (`eval/vote_correctness.py:302`, `:558`), meeting rate
(`eval/meeting_quality.py::compute_meeting_rate`, `:426`), win counts and reason histogram
(`eval/balance_eval.py:893-894` + `load_tournament_report`), accusation calibration
(`eval/accusation_calibration.py`), win-condition self-check (`eval/win_condition_selfcheck.py`), and
the byte-identity walk (`scripts/_verify_samples.py`) — never re-implementing a metric that already has
a tested home. Both CLIs take ANY replay-set directory (not just `replays/samples/*`), so the Wave-0
close (15.7), the 15.12 corpus, and every Wave-2 candidate recording are first-class inputs; `--json`
emits the machine-readable report the later harnesses and audits consume; a gate failure exits non-zero
and names the failing check. This task executes against the baseline-2 bytes committed at task time;
15.7 re-runs the same CLIs unchanged on baseline 3.

**Files in scope:**
- eval/validity.py (new: the composed validity checks + report types)
- scripts/validity_gate.py (new CLI: hard pass/fail over a replay-set dir)
- scripts/measure_baseline.py (new CLI: core R-gate folds region — the 15.2 watchability and 15.3 funnel folds are later, disjoint regions)
- tests/eval/test_validity.py (new: per-check unit tests + synthetic violation fixtures)
- tests/scripts/test_validity_gate_cli.py (new)
- tests/scripts/test_measure_baseline_cli.py (new)

**Files NOT in scope:**
- eval/vote_correctness.py + eval/meeting_quality.py + eval/accusation_calibration.py + eval/balance_eval.py + eval/win_condition_selfcheck.py (consumed as-is, never edited)
- experiments/lab/rubric_score.py (the referee promotion is 15.2)
- audits/workflows/extract_gameplay_facts.py (audit-tier; mine its reconstruction recipes, do NOT import it)
- replays/samples/ (read-only input)

**Definition of done:**
- [ ] The gate checks, each named and individually reported: every game reaches `game_over`; meeting rate ≥ 0.60 with all triggered meetings resolved; zero tick-1 kills; zero friendly-fire kills; zero railroaded crew ejections (the restored 14.12 tripwire semantics); zero dangling `primary_reason_id`; cost and provenance rows exact (model, prompt set, substrate flags); the recorded state-hash chain reconstructs byte-identically.
- [ ] `uv run python scripts/validity_gate.py replays/samples/9p2i` and `.../4p1i` both PASS from committed bytes alone, reproducing the Phase-14 close verdict (9p2i meeting rate 1.00 / 142 resolved; 4p1i 0.78 / 39; zero violations on every other check).
- [ ] `uv run python scripts/measure_baseline.py` reproduces baseline 2 exactly from committed bytes: 9p2i R1 eject-decided win share 24/50, ejection accuracy 0.525 (62 impostor / 56 crew of 118 ejections), genuine-class conversion 0.625, impostor win 0.40, reason histogram `{CREWMATE_EJECT: 24, IMPOSTOR_PARITY: 20, CREWMATE_TASKS: 6}`; 4p1i ejection accuracy 0.923 (12/1 of 13). Any mismatch is a task failure, not a number to retrofit.
- [ ] Each gate check has a synthetic violation fixture proving it can FAIL (flips the CLI exit code) — a gate that cannot fail is not a gate.
- [ ] Both CLIs accept an arbitrary replay-set directory and emit `--json` machine-readable reports; the JSON schema is documented in the module docstring (the 15.15 harness and the 15.7/15.18 audits consume it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is composition, not metric-writing — roughly 80% wiring of folds that already exist, tested, under
`mypy --strict`. Roles ground truth lives ONLY in each set's `tournament-eval-report.json` (raw replays
are role-free by firewall design; `scripts/build_sample_report.py` shows the re-seed recipe if a set
lacks the report). The R1 eject-decided share is the count of `CREWMATE_EJECT`-reason wins — the same
fold `audits/workflows/extract_gameplay_facts.py:611` emits as `r1_eject_decided_wins`; reproduce the
number from the tournament report's reason histogram rather than importing the 4392-line audit script.
For the byte-identity check, call into the machinery behind `scripts/_verify_samples.py` rather than
shelling out. Note `scripts/` is on `mypy_path` — both CLIs are strict-checked. Keep every check pure
and offline: the whole gate must run on a fresh clone with no network and no `AILIBI_*` env.

## Public types this task introduces
- `eval.validity.ValidityGateReport`
- `eval.validity.ValidityCheck`
- `eval.validity.run_validity_gate`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-15-validity-gate` with a title like `task 15.1: validity gate + baseline measurement clis (make the audit-cited scripts real)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/post-phase-14-clean-up.md H1; audits/audit-phase-14-close.md §1, §3, §8 (the gate criteria + R-gate rows this task productizes); audits/post-phase-14-pause.md §2.1 (the missing-harness finding); audits/post-phase-14-ML-training-signal.md §3 (the three-artifact split); eval/vote_correctness.py; eval/meeting_quality.py; eval/balance_eval.py; scripts/_verify_samples.py), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
