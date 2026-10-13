# Retain distinct paid failures in completed meetings

**Status:** done

## Outcome

The standard meeting recorder retains each captured provider attempt exactly
once even when a meeting recovers and completes after several identical failed
responses. Live budget, recorded accounting, and downstream summaries reconcile.
Legacy custom runners without an identified ledger keep their compatibility path.

## Evidence

At `bbe8e2fc`, completed meetings still omit failed-attempt identity and use
content deduplication. An injected real-adapter run with two identical failures
followed by recovery records only one paid failure: budget $0.00351 versus
replay $0.00312. Aborted-meeting retention already has attempt identity; this is
the separately deferred completed-meeting path.

## Acceptance

- [x] Distinct captured paid failures survive separately in completed, recovered,
  defaulted, and aborted meetings, without double-counting recovery metadata.
- [x] Budget, replay, API, manifest, and evaluation totals reconcile on injected
  real-adapter failures; repeated runner use does not reuse attempt identities.
- [x] Historical records remain readable and unchanged; successful calls and
  zero-cost default markers retain their existing meanings.
- [x] Regression cases fail against the prior implementation; focused checks,
  the full project gate, and committed-sample verification pass.

## Constraints

Work on `codex/cleanup`. Follow `docs/architecture.md` Packages and Determinism
and the substrate ladder. Preserve provider protocol, prompt bytes, gameplay,
and API DTOs. No live calls, new dependencies, or re-recording. Root owns the
task index and final card status. Coordinate shared consumer edits explicitly.

## Expected scope

`orchestrator/game.py`, `orchestrator/replay.py`, focused new orchestrator tests,
`tests/orchestrator/test_aborted_meeting_records.py`, `tests/orchestrator/test_game.py`,
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

## Results

The default meeting runner now uses its existing captured-attempt ledger for
both completed and aborted meetings. Each provider failure carries its stable
call identity; recovery metadata cannot charge it again. Default markers retain
their participant, phase, rendered vote maximum, and zero usage/cost. Successful
responses retain their existing records. Custom runners without the optional
captured ledger keep the legacy metadata path; old rows remain readable.

Consumer inspection found necessary provenance follow-through in
`scripts/_manifest_writer.py`: identified failures now supply the provider model
even when a completed meeting has no successful calls. Synthetic default models
are excluded, including for zero-dollar providers. Legacy unidentified rows keep
their existing attribution. The coordinating agent assigned this necessary
helper/test follow-through, plus one correction in
`tests/orchestrator/test_game.py`, whose old expectation
incorrectly collapsed two consumed identical opening attempts into one. It now
checks four distinct failed attempts, three zero-spend markers, and exact totals
of 803 input / 39 output tokens including the three successful votes.

Targeted validation on 2026-09-05 passed 255 tests:

```sh
UV_CACHE_DIR=/tmp/ailibi-review-uv uv run pytest -q \
  tests/orchestrator/test_game.py tests/orchestrator/test_replay.py \
  tests/orchestrator/test_aborted_meeting_records.py \
  tests/scripts/test_manifest_writer.py tests/api/test_eval.py \
  tests/eval/test_balance_eval.py
```

The new integration cases exercise a real Anthropic adapter around injected
offline responses: retry recovery, two identical failures, every call defaulting,
two meetings, and runner reuse. Budget, raw replay, playable API metadata,
evaluation token/by-model totals, and manifest cost/provenance agree. Existing
cancellation, aborted-meeting, returned-success overrun, and legacy reader tests
remain green. Ruff, formatting, and strict mypy pass for all six edited code/test
files. No API DTO, provider protocol, prompt, gameplay rule, or historical
artifact changed; the implementation follows `docs/architecture.md` Packages and
Determinism and the substrate ladder.

For the planted baseline check, copied `orchestrator/` and `scripts/` into a
temporary directory, restored `game.py`, `replay.py`, and `_manifest_writer.py`
from `git show bbe8e2fc:<path>`, copied the current tests, and asserted the imported
modules were those isolated copies. Selecting
`completed_meeting_failures or attempt_identity or attributes_identified` yielded
six expected failures and six compatibility passes. The temporary tree was
removed; shared source was never replaced. The same selected cases pass with the
repair.

The workflow-redesign agent independently reviewed the implementation, ran 224
focused tests, and checked ten additional cancellation, invalid-response, and
duplicated-recovery-metadata cases. Recorded costs and tokens matched the budget;
default telemetry survived. No blocking findings remained. Exact attempt
accounting requires the identified ledger: legacy custom runners retain their
content-based compatibility path, and unknown provider usage cannot be inferred
from a transport failure or cancellation.

The coordinating agent ran the combined gate on 2026-09-05:
`UV_CACHE_DIR=/tmp/ailibi-review-uv npm_config_cache=/tmp/ailibi-review-npm bash scripts/check.sh`
passed with 6,292 Python tests (20 skipped, 3 expected failures), 440 frontend
tests, strict typing, lint, formatting, task validation, and production build.
`UV_CACHE_DIR=/tmp/ailibi-review-uv bash scripts/verify_samples.sh` verified all
100 canonical recordings without modifying their bytes.
