# Protect recordings from tournament report destinations

**Status:** done

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

- [x] Review correction: report and progress destinations protect existing
  unselected replay/audit files in the output directory, including aliases,
  before evaluator or provider work.
- [x] Review correction: new planted collision cases and the combined project
  gate pass on the corrected implementation.

- [x] Preflight the report destination against all selected replay and audit
  paths before running games; cover normalized paths and filesystem aliases.
- [x] Invalid, unwritable, or colliding destinations preserve existing files
  and do not start provider work; valid destinations retain CLI behavior.
- [x] Publish the report with atomic replacement so a write failure does not
  truncate an existing report. Report failures remain explicit.
- [x] Adverse cases fail against the prior implementation; focused checks and
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

## Results

Targeted implementation verification:

- Tournament CLI, factory/artifact variants, report destinations, and sample
  report tests: 97 passed. The 22 destination cases cover aliases, preflight
  refusal, a valid custom output, and injected publication/cleanup failures.
- Ruff, formatting, strict mypy for the three changed Python files, and
  `git diff --check` passed.
- With only `run_tournament.py` imported from `bbe8e2fc`, the same destination
  suite gives 21 failures and one valid-output control passing. A separate
  two-tick fake-provider invocation against that module exits zero after
  overwriting `replay-seed-1.jsonl` with the report document; its audit has eight
  packets. No historical artifacts or live providers were used.

Reproduce the affected test selection with:

```sh
UV_CACHE_DIR=/tmp/ailibi-review-uv uv run pytest -q --tb=short \
  tests/scripts/test_run_tournament.py \
  tests/scripts/test_run_tournament_agent_factory.py \
  tests/scripts/test_run_tournament_candidate_artifact.py \
  tests/scripts/test_report_destinations.py \
  tests/scripts/test_build_sample_report.py
```

The portfolio-review agent independently reviewed the implementation, ran 36
destination/CLI tests, and probed an unwritable parent, FIFO, and interrupted
publication. Existing bytes survived and invalid paths refused before evaluator
work; no blocking findings remained.

The coordinating agent ran the combined gate on 2026-09-05:
`UV_CACHE_DIR=/tmp/ailibi-review-uv npm_config_cache=/tmp/ailibi-review-npm bash scripts/check.sh`
passed with 6,292 Python tests (20 skipped, 3 expected failures), 440 frontend
tests, strict typing, lint, formatting, task validation, and production build.
`UV_CACHE_DIR=/tmp/ailibi-review-uv bash scripts/verify_samples.sh` verified all
100 canonical recordings without modifying their bytes.

The CLI preflights every selected replay/audit before evaluation and again before
publication. Reports use a sibling temporary file and replacement after a
complete write; an additional cleanup failure preserves the original exception
in an exception group and identifies the retained temporary file. Serialization
and `build_sample_report.py`'s matching JSON format remain unchanged.

This follows the architecture's privileged script/evaluation layering. Existing
artifact bytes survive refusal; newly created parent directories may remain.
Concurrent writers, later filesystem changes, and crash durability are outside
the guarantee. No multi-game transaction or recording lifecycle was changed.

### Independent review correction (2026-09-06)

Reopened for C2-4 in the
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md).
The original selected-seed guarantee was too narrow for output-directory
integrity. Report and progress preflight now include every existing
`replay-seed-*.jsonl` file in the output directory, covering both replay and
audit names in addition to selected future paths and archived-attempt storage.
Direct paths, hardlinks and parent-directory symlinks to unselected evidence
are refused before evaluator work. The report cases require no force flag;
progress cases explicitly exercise force so ordinary existence refusal cannot
disguise missing alias protection. The original valid custom-output and selected
recording controls remain unchanged.

Focused command:

```sh
.venv/bin/pytest tests/scripts/test_report_destinations.py tests/scripts/test_run_tournament.py tests/scripts/test_tournament_progress.py -q --tb=short
```

All 12 new unselected-file alias controls fail against `9b333a76` and pass with
the repair. The broader lifecycle/CLI/observation selection passed 235 tests;
[shared correction verification](recording-replacement.md#independent-review-correction-2026-09-06)
records commands, source-isolation controls and strict typing/lint results.

This extends preflight scope without changing atomic publication, schemas,
canonical evidence or engine behavior. Later filesystem changes and concurrent
writers remain outside the stated contract. Scope follows architecture Packages
and Determinism. Combined project verification and independent review are pending.

The correction checkpoint passed `bash scripts/check.sh`: 6,833 Python tests,
20 optional skips, three expected failures, 500 frontend tests, strict typing,
lint/format, import/document contracts and the production build. All 100
canonical recordings verified. The [durable correction record](../../audits/review-2026-09-06/correction-record.md)
records the independent reviews, discovered rollback repair and integration
checks. This completion is on cleanup, awaiting owner review and merge.
