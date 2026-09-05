# Retain distinct paid failures in completed meetings

**Status:** active

## Outcome

Every consumed provider attempt is recorded exactly once even when a meeting
recovers and completes after several identical failed responses. Live budget,
recorded accounting, and downstream summaries reconcile.

## Evidence

At `bbe8e2fc`, completed meetings still omit failed-attempt identity and use
content deduplication. An injected real-adapter run with two identical failures
followed by recovery records only one paid failure: budget $0.00351 versus
replay $0.00312. Aborted-meeting retention already has attempt identity; this is
the separately deferred completed-meeting path.

## Acceptance

- [ ] Distinct paid failures survive separately in completed, recovered,
  defaulted, and aborted meetings, without double-counting recovery metadata.
- [ ] Budget, replay, API, manifest, and evaluation totals reconcile on injected
  real-adapter failures; repeated runner use does not reuse attempt identities.
- [ ] Historical records remain readable and unchanged; successful calls and
  zero-cost default markers retain their existing meanings.
- [ ] Regression cases fail against the prior implementation; focused checks,
  the full project gate, and committed-sample verification pass.

## Constraints

Work on `codex/cleanup`. Follow `docs/architecture.md` Packages and Determinism
and the substrate ladder. Preserve provider protocol, prompt bytes, gameplay,
and API DTOs. No live calls, new dependencies, or re-recording. Root owns the
task index and final card status. Coordinate shared consumer edits explicitly.

## Expected scope

`orchestrator/game.py`, `orchestrator/replay.py`, focused new orchestrator tests,
`tests/orchestrator/test_aborted_meeting_records.py`,
`scripts/_manifest_writer.py`, `tests/scripts/test_manifest_writer.py`, and
this card's Results. The manifest follow-through retains actual provider
provenance when a completed meeting has no successful calls.
Inspect accounting consumers in API/eval/manifests and test them without editing
`eval/balance_eval.py`, which belongs to the parallel evaluation-integrity task.
Coordinate necessary follow-through before editing other consumers.

## Record impact

Post-record, unconditional accounting repair. Newly recorded failed calls gain
stable attempt identity and accurate totals. No committed historical bytes move;
legacy rows without identity retain their documented reading behavior.

## Validation

Exercise real adapters with injected transports, repeated identical failures,
retry recovery, defaults, cancellation, and multiple meetings. Run affected
orchestrator/accounting tests, ruff, formatting, strict mypy,
`bash scripts/check.sh`, and `bash scripts/verify_samples.sh`.
