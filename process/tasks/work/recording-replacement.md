# Replace replay and observation audit together

**Status:** done

## Outcome

Replacing a recorded simulation starts both its replay and observation audit
fresh. Refused or failed setup preserves the previous pair; an error after the
run begins retains the new partial evidence and recorded provider usage.

## Evidence

At `55ed6d9a`, a seven-player, three-tick run writes 21 audit packets. Reusing
its path with `force=True` for a two-tick game replaces the replay but leaves
35 audit packets instead of the clean run's 14. An orphaned audit is reused
without force. An invalid audit destination or failing agent factory can also
destroy an existing replay before recording starts.

## Acceptance

- [x] Review correction: a single-game run reports only the outcome and cost of
  the recording it wrote. The post-run read-back is bound to the recorded game
  identity, so a replay path replaced or shared by another writer is refused
  with a non-zero exit instead of printing another game's numbers; this detects,
  it does not exclude.

- [x] Review correction: a forced run failing before either output contains
  bytes restores its previous pair; an audit-only partial write is retained.
- [x] Review correction: focused adverse controls and the combined project gate
  pass on the corrected implementation.

- [x] Forced replacement produces the same replay and audit bytes as a clean
  run, for default and explicit audit paths, including shorter and partial runs.
- [x] Without force, either existing output refuses the run and preserves both
  artifacts. Invalid paths, aliases, and seed/agent setup failures preserve them.
- [x] Failure while preparing the pair or constructing its writers restores
  previous outputs; injected failures prove rollback. All acquired log handles
  close on every exit. Errors after recording begins preserve new partial data.
- [x] Destination probes reject actual filesystem aliases and unwritable paths
  before replacement. Retirement failures preserve the new recording and name
  retained backups; combined run/cleanup failures retain both exceptions.
- [x] Standalone audit append behavior, standalone replay semantics, explicit
  audit `/dev/null`, and no-replay mode remain compatible.
- [x] Single-game and tournament CLI replacement use the same lifecycle; focused
  and full checks plus canonical sample verification pass. Adverse cases fail
  against the preceding implementation.

## Constraints

Follow `docs/architecture.md` Layering, Enforced boundaries, and Determinism and
the substrate ladder. Build on the replay-integrity repair in a separate PR.
Keep engine rules, prompt bytes, recorded schemas, and canonical evidence intact.
The orchestrator owns replacement; do not change the observation logger's
intentional append semantics. No live-provider runs or dependencies.

This is exception-safe preparation, not a crash-atomic two-file storage format.
Keep sibling backups through the run to recover ordinary setup failures; retain
recovery files and fail loudly if rollback or retirement fails. Concurrent
writers and machine/process termination are outside the guarantee. Preserve
refresh/corpus wrappers'
intentional replay-only promotion from staging. Tournament report-path collision
and multi-game batch transactions are separate work.

## Expected scope

`orchestrator/game.py`, a small `orchestrator/recording.py` lifecycle helper,
`scripts/run_game.py`, tournament/refresh replacement help and comments,
`eval/balance_eval.py` replacement documentation, directly necessary
orchestrator/observation/CLI tests, `tasks/README.md`, and this card. Search every
consumer first. No public DTO, phase-contract, or generated-prompt changes.

## Record impact

Post-record, unconditional recording-lifecycle repair. Fresh deterministic
recording bytes remain identical; forced reruns stop accumulating old packets.
Existing persistent audit outputs now require force even if their replay is
absent. No canonical re-record, gameplay experiment, or baseline adoption.

## Validation

Use deterministic fake-provider runs and injected setup/I/O failures. Run the
new replacement cases, affected orchestrator/observation/CLI tests,
`bash scripts/check.sh`, and `bash scripts/verify_samples.sh`. Compare both
output files against a clean-control run and preserve byte snapshots on refusal.


## Results

Verified 2026-09-05. `bash scripts/check.sh` passed: 6,214 Python tests
(20 skips, 3 expected failures), 440 frontend tests, strict typing, lint,
formatting, architecture contracts, task validation, and frontend build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings; their
bytes are unchanged.

All 24 replacement tests pass. Against an isolated preceding game module
(`git show 55ed6d9a:orchestrator/game.py`), the same cases produce 18 failures
and six compatibility passes. Four additional destination/recovery cases pass;
actual case-insensitive aliasing and directory permission failures were
exercised on this host. The case test also has a positive branch for distinct
filenames on case-sensitive filesystems. Independent review exposed the fresh
alias, first-open permission, and premature-backup-retirement defects; regression
cases now pin each repair and combined run/cleanup error retention.

Affected game/replay/observation/CLI integration passed 226 tests. Three CLI
replacement cases failed with the preceding core and pass with the repair.
The focused core command is `uv run pytest tests/orchestrator/test_recording_replacement.py tests/orchestrator/test_recording_destinations.py -q`.
CLI coverage uses `uv run pytest tests/scripts/test_run_game.py tests/scripts/test_run_tournament.py -q`, in addition to the full gate above.

The repair preserves new partial evidence after recording begins and old
outputs when setup aborts. Recovery/cleanup failures name retained backup
locations and preserve original exceptions. The guarantee excludes process
termination and concurrent writers. The independent tournament report-output
collision is queued separately in the task index.

### Independent review correction (2026-09-06)

Reopened for C2-1 in the [owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md#54-forced-re-record-that-fails-before-the-first-row-destroys-both-previous-artifacts-c2-1).
The historical verification above missed failure after writer construction but
before either lazy writer produced bytes. A zero-second `RunDeadline` reproduced
deletion of both prior files. Replacement now inspects actual output sizes after
both handles close, while a separate preparation boundary keeps a failed backup
rotation on the rollback path. The unused eager callback and its sole call site
are removed rather than retained as a second, conflicting lifecycle signal.

The semantic controls cover an empty first audit write, an audit-only partial
write, and a buffered partial write flushed while closing after an exception.
Zero-byte failures restore the prior pair; any retained new byte commits the
new partial generation. Existing after-tick/provider failure, clean-control,
backup-rotation, handle-close and rollback/retirement tests remain in the gate.
No log schema, engine rule, provider, prompt, historical recording or observation
append behavior changed. This follows architecture Layering and Determinism.

Focused command:

```sh
.venv/bin/pytest tests/orchestrator/test_recording_replacement.py tests/orchestrator/test_recording_destinations.py tests/orchestrator/test_run_limits.py tests/scripts/test_report_destinations.py tests/scripts/test_tournament_progress.py tests/scripts/test_run_game.py tests/scripts/test_run_tournament.py tests/scripts/test_run_tournament_agent_factory.py tests/scripts/test_run_tournament_candidate_artifact.py tests/observation/test_service.py -q --tb=short
```

The focused selection passed 235 tests in 9.29 seconds. Ruff/format and strict
mypy passed on the seven changed Python files; `git diff --check` passed.
For the negative control, load isolated `git show 9b333a76:<path>` copies of
`orchestrator/recording.py`, `orchestrator/game.py`,
`scripts/_tournament_progress.py` and `scripts/run_tournament.py` under their
original module names, assert each module resolves to the temporary copy, then
run the current replacement, report-destination and tournament-progress tests
with this selector:

```text
deadline_before_first or first_audit_write or outputs_cannot or first_seed_failure or crashed_attempt or failed_forced_run or unresolved_capture or changes_during_inspection
```

That adverse run produced 24 failures and two passing partial-write controls;
the same 26 cases pass with the corrections. No tracked source was replaced
during the negative run.

The correction remains active until the coordinator records the combined
project gate and independent review. Concurrent writers and hard-kill durability
remain outside the exception-safety contract.

The independent correction review found a remaining rollback defect: when an
output was initially absent, a zero-byte failed write left an empty file behind.
Rollback now restores both prior bytes and prior absence, preserving existing
empty files and attempting every restoration even if empty-file cleanup fails.
Cleanup failures retain the original exception and identify the retained path.
The absent-replay, absent-audit, both-absent and pre-existing-empty controls plus
an injected unlink failure pass; the isolated `9b333a76` recording helper fails
seven and passes two of those nine cases. Reproduce with the preceding module
isolation recipe and `-k 'original_absence or empty_output_cleanup'`.

After that review repair, replacement/destination/tournament-progress/report-
destination verification passed 123 tests in 5.13 seconds; Ruff/format, strict
mypy on the two affected files, and whitespace checks passed. The coordinator
owns the full-project recheck on the final integrated runtime.

The correction checkpoint at `144fc2e1` passed `bash scripts/check.sh`: 6,833 Python tests,
20 optional skips, three expected failures, 500 frontend tests, strict typing,
lint/format, import/document contracts and the production build. All 100
canonical recordings verified. The [durable correction record](../../audits/review-2026-09-06/correction-record.md)
records the independent reviews, discovered rollback repair and integration
checks. This completion is on cleanup, awaiting owner review and merge.

### Read-back identity binding (2026-09-07)

Reopened for CONC-1, raised by the round-2 probes of the
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md) and archived
beside it as `REVIEW_REPORT_FOLLOWUP.md`. The review ran two concurrent
`run_game.py --force` writers against a single `--replay-path` forty times: in
four trials both processes exited 0 while only one recording survived on disk,
and the loser printed the winner's cost. That reproduction is the review's, not
this card's.

The verification above checked that a forced replacement writes clean bytes; it
never checked which game those bytes belong to. Every line the single-game CLI
prints after `game.run()` is a READ-BACK of the file rather than of the object
this process holds, so a surviving foreign recording is reported under the
losing process's seed. `read_all_entries` already refuses a CONCATENATION
(duplicate ticks, two `game_over` rows), but a clean REPLACEMENT parses without
complaint and differs only in `game_id`.

`HeadlessGame` now exposes the identity every recorded row carries as a
read-only `game_id` property, beside `replay_path` and unchanged in how it is
derived. `scripts/run_game.py` reads the replay back once and compares each
row's `game_id` against it; any foreign identity is named on stderr and the run
exits 1 without printing an outcome, a replay path or a cost. `scripts/run_game.py`
is not among the paths `scripts/_tournament_progress.py`'s
`configuration_fingerprint` hashes, so no tournament sidecar is invalidated by
the CLI half of this change.

Focused command:

```sh
.venv/bin/pytest tests/scripts/test_run_game.py tests/orchestrator/test_recording_replacement.py -q --tb=short
```

That selection passed 42 tests in 2.88 seconds, one of them the new
`test_a_replaced_replay_is_refused_instead_of_reporting_another_games_cost`,
which stands a subclassed writer in for the concurrent one by overwriting the
just-written replay with a seed-1 recording. The existing
`test_force_replaces_replay_and_audit_without_accumulating_packets` is the
positive control and still exits 0 and still prints a cost. Ruff check, Ruff
format and strict mypy passed on `orchestrator/game.py`, `scripts/run_game.py`
and `tests/scripts/test_run_game.py`.

For the negative control, follow the preceding-module isolation recipe above:
write `git show fd1f923c:scripts/run_game.py` into a temporary directory, load
it under the module name `run_game`, assert `sys.modules["run_game"].__file__`
resolves to that temporary copy, then run the current CLI tests with this
selector:

```text
replaced_replay_is_refused
```

Against the preceding CLI that produced one failure: `main` returned 0 and
printed a `cost_usd` line computed from the foreign recording's bytes. The same
case passes with the repair. No tracked source was replaced during the negative
run.

Record impact: detection only on a path that previously reported silently. No
replay schema, engine rule, prompt byte, recorded identity or canonical
recording changed, and an uncontested single-game run prints exactly what it
printed before.

Limitations: this DETECTS, it does not exclude. Two runs of the SAME seed
against the same path record the same `game_id` and remain indistinguishable to
this check. File locking is out of scope, and concurrent writers and process
termination stay outside the exception-safety contract the Constraints section
already draws.

The follow-up correction gate ran on the tree at `93bf7d54`, the last commit before this record; the only edits after that gate are the checkpoint records in the commit that carries this paragraph. `bash scripts/check.sh` passed 7,173 Python tests, 20 optional skips and three expected failures; 514 frontend tests; strict typing on 467 sources; lint/format; four import contracts; document and generated-type checks; and the production build. `bash scripts/verify_samples.sh` verified all 300 canonical recordings (100 under `replays/samples/`, 200 under `replays/ml_corpus/`); all four `scripts/build_sample_report.py --check` runs are consistent; `pytest tests/orchestrator/ --collect-only` collects in a fresh interpreter; the API and static browser journeys passed (13 passed, 3 skipped). No committed recording, report, metric, weight or adoption verdict was rewritten, and every experiment candidate remains default-OFF.
