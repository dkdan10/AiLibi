# Verify outcomes before building current evaluation reports

**Status:** done

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

- [x] Current outcome-certifying report paths validate chronology, meetings,
  state hashes, and terminal winner/reason using the shared integrity mechanism.
- [x] Validation uses the caller's actual seed, roster, task count, and map;
  supplied role truth cannot disagree silently with that setup.
- [x] Valid complete and supported partial recordings remain usable; explicitly
  historical analysis retains a clearly named compatibility path where needed.
- [x] Planted winner, chronology, and ordering corruption is rejected by modern
  report entry points even when optional derived metrics are disabled.
- [x] Focused tests, the full project gate, and canonical sample verification
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

## Results

- Current directory loading, live tournament completion and parse-abort
  recovery, and the sample-report builder now validate through the existing
  replay walker with the shared spectator integrity validator. The walker
  receives the caller's actual setup and rejects conflicting supplied roles.
  Disabling optional kill-gift metrics still performs the integrity walk.
- Historical prompt regression and validity report assembly explicitly call
  `load_historical_tournament_report`; their recorded-output contracts and
  existing walk profiles remain unchanged. The whole validity gate still
  rejects a forged winner through its independent sample-integrity check,
  demonstrated against a clean genuine-recording control. No current publishing
  entry point selects the historical fold. Raw cost reduction remains available
  after outcome validation fails, without rewriting the recording.
- Before/after proof loaded the `eval/` Python package from `bbe8e2fc` in a
  temporary directory and supplied the same genuine recording to both versions.
  Forged winner, altered tick label, reordered meetings, and swapped role truth
  were each accepted before and rejected now, with both values of
  `derive_kill_gift` (eight adverse comparisons; no collection-failure proxy).
- Targeted verification: `.venv/bin/pytest -q
  tests/eval/test_report_replay_integrity.py tests/eval/test_tournament_report.py
  tests/eval/test_balance_eval.py tests/eval/test_replay_walk.py
  tests/eval/test_validity.py tests/eval/test_prompt_regression.py
  tests/scripts/test_build_sample_report.py
  tests/orchestrator/test_meeting_integration.py` passed **256 tests**, with
  **3 existing expected failures**. Ruff and strict mypy passed on the seven
  changed Python files.
- Layering follows `docs/architecture.md` Packages and Determinism and the
  substrate ladder: privileged evaluation reuses orchestration validation;
  no engine loop, public schema, prompt, detector, dependency, or recording
  changes were introduced by this repair. The old synthetic parse-abort test
  now injects a failure into a genuine meeting, proving real partial recovery.

The code-review agent independently reviewed the implementation and reran the
256-test selection. Additional genuine-recording probes rejected altered state
hashes, meeting hashes, action dispositions, duplicate attempt identities, and
incorrect map setup; an interrupted prefix retained its reported cost without
inventing an outcome. The review confirmed that only the two named historical
consumers select the compatibility fold. No blocking findings remained.
Concurrent file replacement between validation and consumption is outside this
repair's guarantee; it does not introduce a recording transaction protocol.

The coordinating agent ran the combined gate on 2026-09-05:
`UV_CACHE_DIR=/tmp/ailibi-review-uv npm_config_cache=/tmp/ailibi-review-npm bash scripts/check.sh`
passed with 6,292 Python tests (20 skipped, 3 expected failures), 440 frontend
tests, strict typing, lint, formatting, task validation, and production build.
`UV_CACHE_DIR=/tmp/ailibi-review-uv bash scripts/verify_samples.sh` verified all
100 canonical recordings without modifying their bytes.
