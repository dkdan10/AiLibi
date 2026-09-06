# Bind experimental results to actual agents and meeting decisions

**Status:** ready

## Outcome

New evaluation results identify the behavior that produced them and validate
ballots against outcomes. Candidate games cannot silently appear as baseline
results. Historical reports remain readable with explicit unknown provenance.

## Evidence

The [independent review](../../audits/review-2026-09-06/REVIEW_REPORT.md) records
C4-2/TGE-2 (missing report labels), TGE-1 (unstamped experimental factories) and
C1-01/C2-2/G5-2 (ballots can disagree with an outcome that passes validation).
The owner authorized these prerequisites in the [post-review plan](../post-review-plan.md).

## Acceptance

- [ ] Validate actual factory/config agreement even when the requested config
  is absent or all-default, before a recording is created. Ordinary custom
  scripted factories remain usable without falsely certifying their identity.
- [ ] Current game and aggregate outputs retain recorded experiment/substrate
  identity. Historical absence means unknown, not invented current provenance;
  mixed arms cannot receive a single misleading baseline label.
- [ ] Current strict readers/reports validate the ballot reduction against
  recorded outcome/ejectee using the applicable recorded or explicitly supported
  threshold. Forged targets with unchanged engine hashes are refused.
- [ ] Test real candidate recording-to-report/API paths, partial runs, absent
  historical fields and deliberately conflicting identities/outcomes. Preserve
  historical projection bytes and current redaction/type-field inventories.
- [ ] Canonical and ML corpus reports/replays still verify; targeted tests,
  generated types and `bash scripts/check.sh` pass. No live-model quality claim.

## Constraints

Read docs/architecture.md. Start runtime work after the maintenance correction
checkpoint and explicit file handover. Do not weaken training's baseline-only
guards. Preserve historical verdicts, weights, recordings and report bytes;
unknown identity must never imply certified baseline. No live provider, default
gameplay change, adoption, dependency, deployment or concurrent writer support.

## Expected scope

`eval/report_schema.py`, `eval/balance_eval.py`, `eval/replay_walk.py`,
`orchestrator/replay_integrity.py`, narrow factory checks in `orchestrator/game.py`,
and necessary replay metadata, API report projection, generated type and
historical serializer follow-through. Root coordinates shared schemas, game and
reader ownership with evidence/meeting workers. Include focused semantic tests.

## Record impact

Post-record validation and additive report provenance. New experimental reports
self-identify; legacy JSON is interpreted under an explicit compatibility path.
No engine/prompt byte changes or reinterpretation of historical model behavior.

## Validation

Run `uv run pytest tests/eval/test_balance_eval.py tests/orchestrator/test_experiment_config.py tests/orchestrator/test_replay_integrity.py tests/api/test_eval_routes.py -q`
after confirming current test filenames. Also run all four
`scripts/build_sample_report.py --sample-dir <set> --check` commands,
`bash scripts/verify_samples.sh`, generated-type checks and `bash scripts/check.sh`.
Plant inconsistent ballots and an experimental factory with absent config.
