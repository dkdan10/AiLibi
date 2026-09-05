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
