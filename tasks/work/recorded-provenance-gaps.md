# Close the recorded-provenance gaps the follow-up review found

**Status:** ready

## Outcome

A recording states which observation clock produced it, a committed evaluation
artifact hashes only reproducible bytes, the live-versus-reconstructed memory
guard is bound to the meeting it checks, and the v3 policy re-decision is a
profile option rather than an unconditional core check. A candidate measurement
can then be labelled and reproduced instead of pooling two clocks into one arm.

## Evidence

Review claims are leads, not measurements of this tree. Reproduce each claim
from the archived follow-up review
([report](../../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md), findings
NC4-3, NC6-1, NC6-2, NC3-1 and FU-ORA-2) on this checkout before implementing.

- **NC4-3.** `eval/report_schema.py:224-236` — `GameProvenance` carries the
  factory kind, experiment config, substrate flags and both tactical policy
  stamps, but no observation-clock version, so v1 and v2 recordings fold into
  one arm. The replay rows already carry it: `experiments/deduction_evaluation.py`
  reads `row.temporal_observation_version` when it checks an arm's clock.
- **NC6-1.** `experiments/investigation_evaluation.py:509` writes `view.json`
  including an mtime-derived `metadata.created_at`, and `:771` then hashes every
  file in the output directory into `artifact_hashes`, so committed hashes are
  timestamps and cannot reproduce. The reader projection already excludes
  `created_at`; the writer does not.
- **NC6-2.** The live-versus-reconstructed memory guards at
  `experiments/investigation_evaluation.py:465-472` and
  `experiments/deduction_evaluation.py:233-248` are existential substring
  matches over every prompt the agent ever received, so serving meeting 0's
  memory for meeting 1 passes silently. A mutation survived both harnesses'
  adverse tests.
- **NC3-1.** `eval/replay_walk.py:577` invokes the v3 policy re-decision for
  every `supports_experiments` profile on a format-3 recording (constructed at
  `:545-561`), and `orchestrator/policy_reconstruction.py` raises a bare
  `ValueError` that bypasses the profile's `on_violation` hook, contradicting the
  walker's documented "no check is core-mandatory" contract.
- **FU-ORA-2.** The committed investigation captures record and reconstruct in
  one process at one commit, so `outcome_verified=True` attests self-consistency.
  A refuter showed the oracle does catch an injected policy defect when the
  recording and the tree differ — that cross-tree walk is simply never run.

## Acceptance

- [ ] `GameProvenance` gains `temporal_observation_version: int | None`, carried
  through `ReplayMetadataView` and `ReportProvenanceGroupView` in
  `api/schemas.py`. Absent stays unknown — a historical recording is not
  relabelled — and mixed v1/v2 inputs no longer group into one arm.
- [ ] All four committed `--check` runs stay green through
  `scripts/build_sample_report.py`'s historical projection
  (`_historical_report_exclusions` at `:203`, `_can_project_historical` at
  `:230`); no committed report is regenerated to accommodate the new field.
- [ ] `view.json` is written without the mtime-derived `created_at` before it is
  hashed, matching what the reader projection already excludes. A rebuild on a
  different machine reproduces the artifact hashes; the current bytes do not.
- [ ] Both memory guards are keyed by meeting (and voter), with a planted
  cross-meeting case: serving meeting 0's memory for meeting 1 fails where it
  passes today.
- [ ] `ReplayWalkConfig` gains `reconstruct_v3_policies: bool = False` and
  `WalkViolationKind` (`eval/replay_walk.py:237-251`) gains a
  `v3_policy_mismatch` member; a disagreement routes through `on_violation`
  instead of raising. Both are public-type changes — enumerate the consumers of
  each and name which profiles enable the option.
- [ ] A cross-tree reproduction check exists: walk a committed format-3
  recording under a later tree so a policy change is detected, and a planted
  policy defect makes it fail. A same-process, same-commit capture is not
  accepted as evidence for that check.
- [ ] Every new gate has a planted or perturbed failure proving it detects the
  claimed defect, not merely that the implementation exists.

## Constraints

No committed report or recording is rewritten, re-recorded or regenerated; all
four `--check` runs must be green on the existing bytes. No provider calls, new
dependencies or new levers. Candidates stay default-OFF; nothing here adopts an
experiment. Follow `docs/architecture.md` Layering, Enforced boundaries and
Determinism, and keep the privileged reader boundary intact. Prerequisite: none,
but the schema field is a semantic prerequisite for the fresh-model instrument
card, so land it before that card's arms are labelled.

## Expected scope

`eval/report_schema.py`, `eval/replay_walk.py`, `eval/balance_eval.py`,
`api/schemas.py`, `api/replay_loader.py`, `api/public_results.py`,
`scripts/build_sample_report.py`, `experiments/investigation_evaluation.py`,
`experiments/deduction_evaluation.py`, and their tests under `tests/eval`,
`tests/api` and `tests/scripts`. Generated frontend types and the type-fidelity
fixture may follow through when a served DTO gains the field.

## Record impact

Added provenance fields only; absent means unknown and no historical stamp
changes meaning. Future recordings carry the observation-clock version, so
reports produced after this card group differently from reports produced before
it — that is the point of NC4-3 and must be stated wherever the two are
compared. A new `v3_policy_mismatch` violation kind can newly fail a profile
that previously passed: name in Results which profiles enable
`reconstruct_v3_policies` and which keep the default `False`. Committed
`artifact_hashes` in the investigation evaluation become reproducible only for
artifacts regenerated after the writer change; the existing committed values
stay historical and are not retro-certified.

## Validation

`uv run pytest tests/eval tests/api tests/scripts -q` for the planted
cross-meeting, cross-tree and violation-routing cases, then
`bash scripts/check.sh`, then `bash scripts/verify_samples.sh`, then the four
derived report checks:

```sh
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

Then the browser journeys with `cd frontend && npm run e2e`, because the served
provenance views change shape.
