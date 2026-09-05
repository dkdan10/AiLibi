# Verify outcomes before building current evaluation reports

**Status:** active

## Outcome

Current tournament report generation rejects chronology and outcome metadata
that strict spectator playback rejects. Explicit historical analysis profiles
retain their stated semantics.

## Evidence

At `bbe8e2fc`, changing only the terminal winner of a genuine recording is
rejected by playback with `recorded_outcome_mismatch` but accepted as the
opposite winner by `load_tournament_report`. The existing spectator repair did
not change the historical evaluation walker or all report-building consumers.

## Acceptance

- [ ] Current outcome-certifying report paths validate chronology, meetings,
  state hashes, and terminal winner/reason using the shared integrity mechanism.
- [ ] Validation uses the caller's actual seed, roster, task count, and map;
  supplied role truth cannot disagree silently with that setup.
- [ ] Valid complete and supported partial recordings remain usable; explicitly
  historical analysis retains a clearly named compatibility path where needed.
- [ ] Planted winner, chronology, and ordering corruption is rejected by modern
  report entry points even when optional derived metrics are disabled.
- [ ] Focused tests, the full project gate, and canonical sample verification
  pass without rewriting recorded evidence or relaxing production guarantees.

## Constraints

Work on `codex/cleanup`. Follow `docs/architecture.md` Packages and Determinism
and the substrate ladder. Reuse shared reconstruction/validation rather than
introducing another inconsistent engine loop. No prompt, detector, simulation,
report-schema, or public API DTO changes; no live calls or new dependencies.
Raw spending must not disappear because a recording cannot certify an outcome.
Cost API status/schema and completion classification are separate later tasks.

## Expected scope

`eval/balance_eval.py`, `eval/replay_walk.py` if needed, focused eval tests,
`scripts/build_sample_report.py`, the explicitly historical consumers in
`eval/validity.py` and `eval/prompt_regression.py`, directly necessary
report-loader test consumers after tracing them, and this card's Results.
Root owns the task index
and final card status. Do not edit `scripts/run_tournament.py`,
`orchestrator/game.py`, or `orchestrator/replay.py` during their parallel tasks.
Coordinate any shared-validator edit before changing it.

## Record impact

Post-record, unconditional current-reader integrity repair. Reject previously
accepted corrupt claims; preserve valid historical recording bytes. Any needed
historical compatibility is explicit, not a silent fallback.

## Validation

Use genuine deterministic recordings and perturb metadata while leaving state
hashes intact. Compare playback and report-loading rejection; exercise both
optional-derived-metric settings and actual report-building entry points. Run
affected eval/report tests, ruff, formatting, strict mypy,
`bash scripts/check.sh`, and `bash scripts/verify_samples.sh`.
