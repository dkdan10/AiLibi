# Preserve tournament progress and enforce run limits

**Status:** done

## Outcome

Interrupted CLI tournaments retain inspectable progress and bind published
reports to their recording inputs. Explicit continuation verifies the same
configuration and input bytes, skips completed seeds, and retains earlier
attempts when an interrupted seed is explicitly retried. Optional whole-run
cost, token, and wall limits cover all attempts, including resumed work.

## Evidence

Injecting KeyboardInterrupt into the second HeadlessGame.run call of a two-seed,
two-tick CLI tournament leaves the first replay/audit pair, but no report or
progress artifact. The existing evaluator creates a fresh budget per seed and
the CLI exposes no cumulative token, cost, or wall limit. Existing report
destination and recording-pair protections must survive the follow-through.

## Acceptance

- [x] Review correction: first-seed failure preserves an existing report and
  never publishes an empty replacement; progress binds its previous bytes.
- [x] Review correction: missing/empty attempt recordings leave usage unresolved,
  preserve known counters, and block retry and cumulative-budget calculations.
  Restoring genuine evidence permits inspection without inventing zero spend.
- [x] Review correction: targeted adverse controls and the combined project gate
  pass on the corrected implementation.

- [x] Atomic progress and report snapshots survive a later-seed interruption;
  progress identifies pending, running, finished, and interrupted attempts.
- [x] Explicit continuation verifies configuration and recording/report hashes,
  skips finished seeds, and rejects mismatched or stale inputs before calls.
- [x] Explicit retry retains prior replay/audit bytes and reported spend; no
  completed seed is silently replayed and no retry restores budget headroom.
- [x] Optional cumulative cost, input/output token, and elapsed wall limits
  reject new work at the limit and cancel awaited provider work safely.
- [x] Adverse regression cases, targeted tests, type/lint checks, full project
  validation, and committed-sample verification pass.

## Constraints

Work directly on codex/cleanup. Follow docs/architecture.md Packages and
Determinism and the substrate ladder. No live calls, dependencies, provider
protocol changes, engine clock, or historical record edits. Keep existing report
DTO compatibility. The completion-classification task owns eval/balance_eval.py
and replay schemas until explicit handover; coordinate additive hooks. Root
owns final card status and the full gate. Whole wall enforcement is cooperative
between synchronous ticks and cancels asynchronous meeting calls; it cannot
preempt blocked synchronous Python or recover usage a provider never reports.

## Expected scope

scripts/run_tournament.py, focused progress/publication helpers, llm/budget.py,
orchestrator/run_limits.py, orchestrator/game.py, coordinated eval/balance_eval.py
hooks, scripts/_report_output.py, focused scripts/LLM/orchestrator tests, and this card. Retain atomic report
publication and preflight alias protections for progress and archived attempts.

## Record impact

Post-record operational repair. CLI sidecars add configuration/input provenance;
existing report DTOs and committed replay bytes remain unchanged. Normal stop
record production belongs to the coordinated completion-classification card.
Opt-in run limits can end future runs early without inventing outcomes or spend.

## Validation

Inject second-seed failure, cancellation, retries, changed configuration/bytes,
destination aliases, and cumulative cap overruns using offline providers. Run
the affected script, budget, and game suites, ruff, strict mypy,
bash scripts/check.sh, and bash scripts/verify_samples.sh.

## Results

The CLI checkpoints an atomic tournament-progress.json sidecar before each seed
and publishes an input-bound report snapshot after each attempt. The sidecar
records configuration, completed and interrupted attempts, exact replay/audit
hashes, cumulative usage, elapsed time, and the report hash. Pending seeds are
the selected seeds without an attempt. Publication records both sides of its
two-file transition so interruption between report and progress writes remains
recoverable. A second checkpoint failure adds diagnostics without hiding the
original interruption.

`--resume` verifies configuration and input bytes and reconstructs saved reports
before skipping finished seeds. A killed process that already wrote a verified
terminal/normal-stop record is recovered as finished. Interrupted work requires
`--resume --retry-incomplete`: its exact recording pair is archived and that
ownership checkpointed before canonical names are cleared for another attempt.
Identical retry bytes still represent another paid attempt. Partial archive-copy
and pair-clear failures preserve a recoverable prior pair. Untracked files for
pending seeds are refused; continuation never implicitly overwrites unrelated
recordings, including later files left by an interrupted fresh `--force` run.

Independent review found and corrected two concrete defects before acceptance:
YAML map bytes were missing from the fingerprint, and text-mode archival could
normalize CRLF. Fingerprints now bind map/templates/source, dependency locks,
CLI helpers, registered factory implementations, and selected external policy
config/stamp/weight files. SDK routing, proxy/TLS, credential, and AILIBI settings
are hashed without persisting secret values. The CLI supports its registered
factory choices and explicit artifacts; arbitrary in-process injected factories
are outside this continuation contract. Archives use the existing atomic writer
with a byte-preserving path; its text API and cleanup-error semantics remain.

Optional `--max-total-cost-usd`, `--max-total-input-tokens`,
`--max-total-output-tokens`, and `--max-wall-seconds` apply across seeds and
resumed attempts. Fresh per-game budgets retain their existing caps and charge a
shared parent. Preflight prevents new calls that exceed the estimate-based
allowance; a returned response can still report more usage than estimated, and
its entire incurred charge is retained before an overrun raises. The external
wall clock checks synchronous boundaries and cancels awaited meeting work,
retaining reported responses/failures. It cannot preempt blocked synchronous
Python or recover usage never reported by a provider. After a hard kill, the
unobserved interval conservatively includes downtime in the wall allowance.

The report evaluates each seed's latest attempt. Sidecar totals and the CLI's
all-attempts line additionally include archived attempts; they are the cumulative
budget authority. Corrupt/uninspectable inputs remain fail-loud, with incomplete
accounting marked explicitly. Source/input hashes detect drift, not malicious
rewriting of both data and hashes. Concurrent writers remain unsupported.

Validation on 2026-09-05 passed 305 affected tests:

```sh
UV_CACHE_DIR=/private/tmp/ailibi-consumer-uv-cache uv run pytest \
  tests/scripts/test_tournament_progress.py \
  tests/scripts/test_report_destinations.py \
  tests/scripts/test_run_tournament.py \
  tests/scripts/test_run_tournament_agent_factory.py \
  tests/scripts/test_run_tournament_candidate_artifact.py \
  tests/scripts/test_build_sample_report.py \
  tests/llm/test_budget.py tests/llm/test_budgeted_client.py \
  tests/llm/test_parent_budget.py tests/orchestrator/test_run_limits.py \
  tests/orchestrator/test_game.py \
  tests/orchestrator/test_aborted_meeting_records.py \
  tests/eval/test_balance_eval.py \
  tests/eval/test_balance_eval_meeting_runner.py \
  tests/eval/test_tournament_report.py -q --tb=short
```

Ruff, formatting, strict mypy, and diff whitespace checks pass on the ten
changed/new Python files. Six adverse selections fail against the previous CLI:
write `git show 6d3c56e9:scripts/run_tournament.py` into a temporary directory,
prepend that directory and repository scripts/ to sys.path, assert
run_tournament.__file__ selects the temporary copy, then invoke pytest.main on
test_tournament_progress.py with `-k 'second_seed_interruption or shared_cap or
zero_cap or zero_wall_limit'`. The result is six failures; the repaired selections
pass. No shared source was replaced for this baseline probe.

The evaluator hooks were added after explicit file handover. Normal-stop record
production follows the separate completion-status contract. This implementation
keeps clock and budget control in orchestration/LLM layers, as required by
docs/architecture.md Packages and Determinism and the substrate ladder. No live
provider, commit, historical artifact edit, or full-project run occurred in this
subtask; the combined full gate and final acceptance are recorded below.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Portfolio-review agent; source fingerprint coverage and byte-preserving archival findings were repaired and independently rechecked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.

### Independent review corrections (2026-09-06)

Reopened for C7b-2 and GC-2 in the
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md).
The earlier verification missed zero-row failures: the CLI published an empty
report before its first seed, and capture declared a missing or empty replay to
have completely accounted zero usage. Reproductions now exercise both paths.

The initial checkpoint binds the existing report hash without replacing its
bytes. Publication waits for at least one inspectable game. A first-seed failure
therefore preserves an earlier report, including failure after forced recording
replacement restores the earlier pair. Starting identities distinguish unchanged
prior files from new attempt evidence on a failed forced run; ambiguous identical
bytes fail closed rather than attributing old work to the new attempt.

Capture stages validated usage and source hashes before replacing known counters.
Missing/empty inputs, a valid prefix with less usage than its checkpoint, and
bytes changed during inspection leave accounting unresolved. Resume, retry and
cumulative allowance calculations refuse unresolved attempts before provider
work or archival. Existing known charges and evidence identities remain intact;
restoring genuine partial recording bytes lets the same checkpoint reconcile.
This deliberately refuses a zero-row retry whose incurred usage cannot be
established. It does not claim to recover unreported provider usage, or silently
certify zero after a process kill. Complete prior attempts, normal partial retry,
identical paid attempts and interrupted publication retain their existing tests.

The second-seed continuation test now interrupts after a genuine first tick,
so its interrupted attempt has inspectable evidence; assuming a missing file
means zero would recreate the defect. Its report truthfully includes the
unfinished game alongside the completed first seed. A separate missing/empty
crash test verifies refusal without provider calls.

Focused reproduction and positive controls:

```sh
.venv/bin/pytest tests/scripts/test_tournament_progress.py tests/scripts/test_report_destinations.py tests/orchestrator/test_recording_replacement.py -q --tb=short
```

The broader lifecycle/CLI/observation selection passed 235 tests. The shared
[correction verification](recording-replacement.md#independent-review-correction-2026-09-06)
records the exact command, strict typing/lint result and the 24-failure,
two-positive-control comparison against `9b333a76`.

Record impact remains operational and post-record: no report DTO, prompt,
engine behavior, historical evidence or adopted experiment changes. Sidecar
fields are unchanged. Scope follows architecture Packages and Determinism.
Combined project verification and independent review are pending coordination.

The correction checkpoint passed `bash scripts/check.sh`: 6,833 Python tests,
20 optional skips, three expected failures, 500 frontend tests, strict typing,
lint/format, import/document contracts and the production build. All 100
canonical recordings verified. The [durable correction record](../../audits/review-2026-09-06/correction-record.md)
records the independent reviews, discovered rollback repair and integration
checks. This completion is on cleanup, awaiting owner review and merge.
