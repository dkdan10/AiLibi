# Retain provider calls when a meeting aborts

**Status:** done

## Outcome

An interrupted meeting preserves its completed model responses and reported
failed-attempt usage. Replay, API, and evaluation accounting agree about that
spend without inventing a resolved meeting or winner.

## Evidence

At `b64e29b5`, a seeded game with a paid opening followed by a transport error
records only a tick. Its budget reports $0.0123, while `compute_cost_usd` reports
zero: `DefaultMeetingRunner` discards completed captures on failure. Recording
outside the budget wrapper also loses a returned response if charging overruns
the cap. A parse failure awaiting retry can disappear before the manager
publishes its recovery metadata.

## Acceptance

- [x] Successful prefixes survive transport errors and cancellation with their
  exact prompt, response, usage, cost, and provenance; the original error propagates.
- [x] Returned responses that overrun the budget and parse failures pending a
  retry survive an abort. Distinct paid attempts with identical content count
  separately; defaults and recovery records do not charge an attempt twice.
- [x] Reusing a runner does not contaminate the next meeting. Aborts during
  result validation/application retain available artifacts; no-replay mode
  still propagates errors without writing files.
- [x] Replay cost, API summaries, evaluation tokens/by-model totals, and manifest
  provenance include retained calls. An abort is never a resolved meeting or a
  canonical recording; the corpus freeze rejects it.
- [x] Adverse cases fail against the old implementation, focused and full
  project checks pass, and committed sample verification remains green.
- [x] Review correction: historical report projection omits an absent failed-call
  identity but retains a real identity, with all four committed reports passing
  reconstruction checks without rewriting evidence.
- [x] Review correction: the aborted-meeting tests collect and run independently
  of the scripts test package; focused and full project gates pass.

## Constraints

Follow `docs/architecture.md` Packages and Enforced boundaries. Preserve engine
rules, prompt bytes, historical evidence, and successful-meeting record bytes.
Use one additive `meeting_aborted` entry and an optional identity on aborted
failed-call rows; existing readers remain backward compatible. Older readers
may reject the new entry kind. Keep existing API DTOs and typed game reports;
raw retained calls are available in JSONL. No live-provider runs or new dependencies.
The preceding accounting repair is a prerequisite; this is a separate follow-up PR.

## Expected scope

`orchestrator/game.py`, `orchestrator/replay.py`, `api/replay_loader.py`,
`eval/balance_eval.py`, `scripts/_manifest_writer.py`,
`scripts/record_ml_corpus.sh`, directly necessary replay/API/eval/script tests,
`tasks/README.md`, and this card. Check the API's explicit failed-call field
projection when adding attempt identity; no raw-call DTO expansion is authorized.
The review correction also owns `scripts/build_sample_report.py`, its focused
tests, and the isolated import regression in the aborted-meeting test module.

## Record impact

Post-record, unconditional integrity repair. Newly aborted runs gain accurate
call records and cost/provenance totals; they remain incomplete games. No
canonical re-record, prompt/detector change, or experiment adoption occurs.
Legacy completed-meeting failure deduplication remains unchanged.

## Validation

Run the new aborted-meeting integration cases and affected replay, API,
evaluation, and manifest tests; `bash scripts/check.sh`;
`bash scripts/verify_samples.sh`. Use injected transports and deterministic
fakes. Verify the new accounting cases fail against the preceding implementation.

## Results

Verified 2026-09-05. All 11 new integration cases pass; nine fail on replay
accounting against isolated `b64e29b5` orchestrator modules, while two
compatibility controls pass in both versions. The full `scripts/check.sh` gate
passed: 6,135 Python tests (20 skips, 3 expected failures), 440 frontend tests,
lint, formatting, imports, strict types, and build. Sample verification passed
all 100 selected recordings. Historical artifacts are unchanged.

Independent review passed 309 affected tests and three additional actual task
cancellation probes through public evaluation, API, and manifest readers.
The new raw attempt identity triggered the field-inventory gate as intended;
its reviewed inventory and API redaction fixture now cover it. No API DTO grew.

Validation uses injected transports. Unknown provider usage is not invented;
process termination and filesystem-failure durability are not claimed. Existing
completed-meeting failure deduplication remains outside this repair. Full call
details are retained in JSONL; API summaries expose accounting and provenance.

### Review correction in progress

Reopened for [review findings G5-1 and C2-6](../../audits/review-2026-09-06/REVIEW_REPORT.md#5-required-before-merge).
The 2026-09-05 results above describe the prior delivery. Independently reproduced
the ML 9p2i report check failing on two additive `call_id: null` fields and
isolated orchestrator collection failing with `ModuleNotFoundError` for
`_manifest_writer`. This is a historical serialization and test-bootstrap repair;
prompt bytes, simulation defaults and committed evidence remain unchanged.

The historical JSON and comparison projection now share exclusions that remove
only absent attempt identities. A mixed legacy/new-call control verifies that a
real identity survives, other optional fields remain present, and serialization
does not mutate the report. The existing stale-meeting-count plant still fails
the consistency check. Both canonical and both ML sets now participate in that
gate. The test module owns its script import bootstrap and a fresh isolated
Python subprocess proves collection no longer depends on other test packages.

Targeted verification on 2026-09-06:

```bash
.venv/bin/python -m pytest tests/scripts/test_build_sample_report.py tests/orchestrator/ tests/api/test_view_model.py -q
.venv/bin/python -m pytest tests/orchestrator/ --collect-only -qq
.venv/bin/python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
.venv/bin/python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
.venv/bin/python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
.venv/bin/python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
```

The combined targeted run passed 490 tests, with one optional skip and three
expected failures. Isolated collection and all four report checks exited zero.
Ruff and strict mypy passed on the five changed Python files in this correction
group. Architecture references remain Packages and Enforced boundaries: this
changes only the historical report projection and verification, not gameplay or
the observation firewall. The coordinator's final full-project gate is pending;
the card remains active until it passes.

The correction checkpoint passed `bash scripts/check.sh`: 6,833 Python tests,
20 optional skips, three expected failures, 500 frontend tests, strict typing,
lint/format, import/document contracts and the production build. All 100
canonical recordings verified. The [durable correction record](../../audits/review-2026-09-06/correction-record.md)
records the independent reviews, discovered rollback repair and integration
checks. This completion is on cleanup, awaiting owner review and merge.
