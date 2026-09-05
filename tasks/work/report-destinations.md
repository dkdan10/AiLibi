# Protect recordings from tournament report destinations

**Status:** active

## Outcome

A tournament report cannot overwrite any replay or observation audit in the
requested run. Invalid output destinations fail before simulations consume
provider calls or replace existing records.

## Evidence

At `bbe8e2fc`, `scripts/run_tournament.py` resolves the report destination after
running the games and writes it directly. A one-seed fake-provider run with
`--report-output <output-dir>/replay-seed-1.jsonl` exits successfully after
replacing its genuine replay with report JSON.

## Acceptance

- [ ] Preflight the report destination against all selected replay and audit
  paths before running games; cover normalized paths and filesystem aliases.
- [ ] Invalid, unwritable, or colliding destinations preserve existing files
  and do not start provider work; valid destinations retain CLI behavior.
- [ ] Publish the report with atomic replacement so a write failure does not
  truncate an existing report. Report failures remain explicit.
- [ ] Adverse cases fail against the prior implementation; focused checks and
  the full project gate pass.

## Constraints

Work on `codex/cleanup`. Follow `docs/architecture.md` Packages and Determinism
and the substrate ladder. Preserve simulations, report schema, prior recordings,
and paired recording replacement. No live calls, new dependencies, concurrency
locking, or multi-game transaction protocol. Coordinate before touching another
agent's assigned files. Root owns the task index and final card status.

## Expected scope

`scripts/run_tournament.py`, a focused helper in `scripts/` if needed,
`tests/scripts/test_run_tournament.py`, new destination-focused script tests,
and this card's Results. Inspect recording-path consumers without editing
`orchestrator/game.py`, `orchestrator/replay.py`, or `eval/balance_eval.py` while
their parallel tasks are active. Request coordination for necessary follow-through.

## Record impact

Post-record, unconditional output-integrity repair. No prompt, detector, game,
report-schema, or historical recording byte changes.

## Validation

Use fake-provider CLI runs and injected filesystem failures. Prove destination
rejection happens before the evaluator runs, verify previous artifact bytes,
and test the report's atomic-write failure path. Run affected script tests,
ruff, formatting, strict mypy, `git diff --check`, and `bash scripts/check.sh`.
