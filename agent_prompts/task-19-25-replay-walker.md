# Agent Prompt — 19.25 The parameterized replay walker + the eval consumer migration

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.25 — The parameterized replay walker + the eval consumer migration, anchored to audits/audit-phase-19-triage.md §7 item 25 [C; count VERIFIED §8 row 15 — eight modules, nine loop bodies] + C3 + close §7 items 1–2 (the disclosed duplication); the loop bodies re-verified at HEAD: eval/watchability.py:1229-1231/1290, eval/validity.py:402-404/453, eval/funnel.py:365/471 + :1217/1324, eval/kill_craft.py:474-519, eval/win_condition_selfcheck.py:191-225, eval/balance_eval.py:760-796, eval/leak_scan.py:512-527 (the leak walk, relocated from eval/leak_test.py by 19.24's library promotion); eval/deception_instruments.py:169 (the one module that already imports a shared walk — the consumption exemplar); eval/off_menu.py EXCLUDED (frozen, 19.18). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-replay-walker`
**Depends on:** 19.24
**Section refs:** audits/audit-phase-19-triage.md §7 item 25 [C; count VERIFIED §8 row 15 — eight modules, nine loop bodies] + C3 + close §7 items 1–2 (the disclosed duplication); the loop bodies re-verified at HEAD: eval/watchability.py:1229-1231/1290, eval/validity.py:402-404/453, eval/funnel.py:365/471 + :1217/1324, eval/kill_craft.py:474-519, eval/win_condition_selfcheck.py:191-225, eval/balance_eval.py:760-796, eval/leak_scan.py:512-527 (the leak walk, relocated from eval/leak_test.py by 19.24's library promotion); eval/deception_instruments.py:169 (the one module that already imports a shared walk — the consumption exemplar); eval/off_menu.py EXCLUDED (frozen, 19.18)
**Complexity:** Integration

"Reconstructs cleanly" currently denotes eight subtly different predicates — and the
owner review established the differences are partly DELIBERATE, not drift:
`eval/validity.py:430` tolerates a partial-meeting replay by design while
`eval/funnel.py:398` fails it loudly, and funnel's comment declares its divergence
deliberate. A union of checks would therefore CHANGE validation behavior — exactly what
locked decision 1 forbids. Build `eval/replay_walk.py` as shared MECHANICS with
per-consumer PROFILES: the walker's core is the reconstruction MECHANICS ONLY (re-seed →
`advance_tick` → `apply_meeting_result`, pluggable fact collectors) — EVERY integrity
check, state-hash verification and doubled-record detection included, is a
profile-declared OPTION, because at least one consumer (the leak-scan walk at
`leak_scan.py:512-527`, post-19.24 home) performs neither today and mandatory core checks would change
what it accepts — and each consumer declares a NAMED validation
profile that preserves its current, deliberate semantics — the drift record documents
per profile which checks it enforces, which it deliberately relaxes, and why, each with
a negative fixture proving the profile still bites (or still tolerates) what it did
before. Migrate the eight live call sites one consumer at a time with BYTE-PARITY: no
committed pin, report cell, or metric value may change — parity is the deliverable, and
a profile-semantics change is out of scope. `off_menu.py` stays frozen and unmigrated
(labeled by 19.18); the API and training walks are backlog by the cut line.

**Files in scope:**
- eval/replay_walk.py (new)
- eval/watchability.py
- eval/validity.py
- eval/funnel.py
- eval/kill_craft.py
- eval/win_condition_selfcheck.py
- eval/balance_eval.py
- eval/leak_scan.py; (after 19.24 the leak walk lives HERE — the migration targets the relocated loop)
- eval/leak_test.py; (the thin wrapper — only if walk residue remains)
- tests/eval/test_replay_walk.py (new)
- tests/eval/test_watchability.py
- tests/eval/test_validity.py
- tests/eval/test_funnel.py
- tests/eval/test_kill_craft.py
- tests/eval/test_win_condition_selfcheck.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- eval/off_menu.py (frozen — not migrated)
- api/replay_loader.py + training/env.py (backlog per the cut line)
- eval/deception_instruments.py (already consumes a shared walk; not churned)

**Definition of done:**
- [ ] The walker's docstring tables the mechanics core plus every named profile: which checks each profile enforces, which it deliberately omits or relaxes (validity's partial-meeting tolerance vs funnel's fail-loud; leak-scan's no-hash-no-dedup walk), and why — with a negative fixture per profile proving its semantics are unchanged; NO check is core-mandatory.
- [ ] All eight call sites consume the walker under their own profile; a repo grep proves no independent `advance_tick` reconstruction loop remains in the migrated modules.
- [ ] BYTE-PARITY: every committed pin and regenerated-report byte is unchanged across the migration (the four derived reports regenerate identical; the diff proves it); any behavior difference discovered between a consumer's old walk and its declared profile STOPS the migration and is recorded as a finding — never silently reconciled in either direction.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

One consumer per commit, suite green between commits, `funnel.py`'s two walks last (they
are the memory-augmented ones — the walker's collector seam must serve the
reconstructed-`TacticalAgent` pattern before they migrate). The walker API shape that
works: a config of enabled collectors + a generator of typed per-tick events, so callers
fold rather than subclass.

## Public types this task introduces
- `eval.replay_walk.walk_replay`
- `eval.replay_walk.ReplayWalkConfig`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Eight load-bearing eval modules on one branch. The parity discipline is the guard
(committed pins are the oracle at every step), plus the profile discipline: deliberate
per-consumer semantics are preserved, never unified — a union would be an
evidence-validation behavior change, which locked decision 1 forbids. If the branch runs
long, land the walker + the first three consumers and split the rest into a follow-up on
the same contract (coordination notes the split) rather than letting the branch drift.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import training.realpath_schema"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-replay-walker` with a title like `task 19.25: the parameterized replay walker + the eval consumer migration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 25 [C; count VERIFIED §8 row 15 — eight modules, nine loop bodies] + C3 + close §7 items 1–2 (the disclosed duplication); the loop bodies re-verified at HEAD: eval/watchability.py:1229-1231/1290, eval/validity.py:402-404/453, eval/funnel.py:365/471 + :1217/1324, eval/kill_craft.py:474-519, eval/win_condition_selfcheck.py:191-225, eval/balance_eval.py:760-796, eval/leak_scan.py:512-527 (the leak walk, relocated from eval/leak_test.py by 19.24's library promotion); eval/deception_instruments.py:169 (the one module that already imports a shared walk — the consumption exemplar); eval/off_menu.py EXCLUDED (frozen, 19.18)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
