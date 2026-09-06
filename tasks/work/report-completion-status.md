# Distinguish recorded spend, verified outcomes, and completion status

**Status:** done

## Outcome

Recorded provider spending remains visible when a game cannot certify an
outcome. Reports and API readers distinguish verified outcomes, unverified
claims, aborted meetings, explicit tick limits, and unfinished recordings.

## Evidence

The cost API currently counts a forged terminal winner in its decisive split
even though strict playback rejects that same recording. Report summaries count
every missing winner as tick exhaustion. Normal tick-limited runs currently
leave no durable stop reason, so replay readers cannot distinguish them from
interrupted prefixes.

## Acceptance

- [x] Raw accounting retains readable recorded usage regardless of outcome
  validation; verified outcome rates expose their actual denominator and never
  count forged, incompatible, or unfinished claims as verified wins.
- [x] Reports, API DTOs, generated types, CLI and dashboard distinguish completed,
  aborted, tick-limited, and unfinished games. Old reports remain readable;
  missing metadata never manufactures verification or a tick-limit claim.
- [x] The real runner emits a status-only stop row on normal nonterminal exits.
  Readers reject duplicate/conflicting stops, terminal claims, wrong stop ticks,
  and unexplained continuation. Old partial recordings remain unfinished.
- [x] Genuine completed/partial/aborted controls and planted integrity failures
  demonstrate accounting and denominator semantics through public consumers.
- [x] Focused checks, the full project gate, and all canonical sample checks pass
  without rewriting historical evidence.

## Constraints

Implement directly on `codex/cleanup`; root owns commits and the shared gate.
Follow `docs/architecture.md` Packages and Determinism and the substrate ladder.
No prompt, tactical, meeting-rule, or engine behavior changes; no live calls or
dependencies. Preserve historical metric profiles. Concurrent file replacement
and tournament progress/provenance belong to the parallel lifecycle task.

## Expected scope

`eval/report_schema.py`, status folding and a shared report assembly helper in
`eval/balance_eval.py`; API replay/cost readers, schemas and eval projections;
`orchestrator/replay.py`, the shared integrity validator and directly coupled
stop-row readers; generated frontend API types/generator and dashboard balance
status copy/tests; focused Python tests and necessary schema inventories.
The historical sample serializer and baseline measurement CLI retain their
published projections, with focused compatibility tests and shared sample fixtures.
Coordinate all coupled consumers found by search. Workflow owns `game.py` stop
emission and CLI status summaries, then takes `balance_eval.py` after explicit
handover for run limits. Portfolio owns rubric freshness and supplies its narrow
loader patch separately. Root owns the roadmap/index and final card status.

## Record impact

Post-record, additive status metadata. Future normal nonterminal exits gain
`game_stopped`; no existing recording bytes move. Older readers may reject the
new row kind. Historical reports missing status/verification fields remain
readable with conservative classification. Completed game and prompt bytes are
unchanged. API additions explicitly distinguish recorded and verified claims.

## Validation

Use offline genuine recordings and injected failures. Test forged winners,
chronology, incompatible substrate, explicit and missing stop records, normal
runner exits, and mixed completion batches; compare raw costs before/after
validation. Run focused pytest, Ruff, strict mypy, frontend unit/type checks,
then root runs `scripts/check.sh` and `scripts/verify_samples.sh`.

## Results

Implemented the additive `CompletionStatus`, `GameStopReason`, and
`GameStopReplayEntry` contracts in `orchestrator/replay.py`. Normal stop rows
carry the next engine tick and no winner; the shared integrity validator rejects
wrong labels/phases, terminal replacements, duplicate/conflicting final rows,
and continuation after a stop. The lifecycle task owns runner emission. Bare
historical prefixes remain unfinished; explicit unresolved failed attempts or
aborted meetings retain an aborted classification. Completed meetings with
recovered failures remain completed.

`GameReport` now carries `completion_status` and `outcome_verified`. Legacy
reports infer status only from existing winner or explicit reason evidence;
verification defaults to false. Current validated folds stamp terminal outcomes
only. `BalanceReport` and dashboard counts separate verified crew/impostor wins,
explicit tick limits, aborted, unfinished, and unverified completed outcomes.
The shared `build_tournament_report` assembles retained games for lifecycle
progress without recomputing their identity or changing historical metric cells.
`balance_eval.py` was handed to the lifecycle owner for shared-budget/deadline
hooks after the completion fold settled.

The cost API's new `ReplayAccountingView` rows retain readable recorded spend
and distinguish `recorded_winner`, `verified_winner`, and integrity status.
`verified_outcomes` is the explicit decisive denominator. Incompatible sources
are unverified even under an analysis override; rejected outcome claims retain
their raw costs. Unparseable files report unknown cost (`null`), increment
`unreadable_replays`, and set `accounting_complete=false`; no unknown cost is
invented as zero. The original cost total is the sum of readable recordings.
Valid files retain the existing one-parse/cached-summary behavior. Rejected
files can require an additional raw read to recover accounting.

Serialized report booleans are not trusted. API serving rebinds outcome and
completion status to current replay identity, strict reconstruction, winner,
reason, and terminal tick; repeated game/seed/reference identities cannot gain
multiple verified outcomes. This verification explicitly concerns outcome
metadata, not arbitrary serialized metric or cost cells, which remain readable
historical claims. Generated DTO types, the eval redaction projection and its
field inventory were updated. The picker/highlight owner handles stop labels;
this task handles dashboard partitions and their denominator.

The coupled `scripts/build_sample_report.py` serializer has an explicit
historical projection that omits only the two new report fields. Its producer
still uses the strict current reconstruction loader. Frozen report bytes and
metric cells are preserved; modern tournament output retains the additive
fields. The API rebinds either representation when source bytes are available.
No canonical replay, prompt, or historical report file was rewritten.

Targeted evidence:

- 252 tests passed across new stop, accounting, completion and forged-report
  cases plus existing replay integrity, API readers/redaction, report schema,
  current report integrity and historical sample serialization tests.
- Strict mypy passed for 12 owned Python files. Ruff and format checks passed.
  Frontend type checks passed; completion/copy unit tests passed (241 tests),
  and targeted ESLint passed.
- An isolated archive of pre-change commit
  `6d3c56e96d25d84713f54cc6d79f2d9cdc4b33f8` failed
  `tests/api/test_cost_integrity.py::test_invalid_claim_keeps_paid_recording_but_cannot_change_verified_split[winner]`:
  old code returned a forged 50/50 split instead of the single verified impostor
  outcome. The same test passes on the implementation with the same recorded
  spending. Archive:
  `/var/folders/45/z6kbb3x1103dgy43qkw1s3vw0000gn/T/ailibi-completion-baseline-s7kjbv3c`.
- The injected real Anthropic adapter abort test retains nonzero reported
  spending equal to `GameBudget.snapshot().cost_usd`, with zero verified
  outcomes. No live providers were used.

Root completed the shared gate and all 100 canonical replay checks below. Older executables that do not know `game_stopped` may reject
new nonterminal recordings; existing replay bytes remain readable. Completion
status describes the evidence retained by a recording, and does not manufacture
a terminal outcome for a partial file.

Independent review found two missing cases before the shared gate. A normal
tick limit immediately after a resolved meeting used the trigger state's old
tick in validation; the API and eval walkers now pass the actual verified
post-meeting state through `ReplayIntegrityValidator.check_meeting_result`.
This also keeps a pending meeting pending until its application is observed.
Eight genuine runner cases cover skipped/nonterminal-ejected meetings through
both readers, accepting the real stop tick and rejecting a forged trigger tick.
The new positive cases failed before the correction.

The reviewer also found that an explicit substrate analysis override was
loadable but incorrectly marked its replay metadata outcome as verified. The
override remains available, while both list/open metadata now agree with the
cost endpoint that an incompatible outcome is unverified. The adverse substrate
case covers all three surfaces. Follow-through touched `eval/replay_walk.py`
only at the verified post-meeting hook. After these corrections, 148 focused
stop/accounting/chronology/current-and-historical-walker tests passed; strict
mypy, Ruff and format passed on the five affected files.

The first combined gate exposed a remaining historical consumer of the modern
balance reducer: `scripts/measure_baseline.py` received historical reports whose
outcomes correctly remained unverified, then emitted zero recorded wins. Its
historical census now reduces recorded winners directly, preserving the frozen
null-winner bucket and existing denominator without changing any verification
flag or the modern balance rules. A planted all-unverified report preserves the
35/15 historical split and remains unverified. The serialization-only test now
uses `tests._helpers.committed.report_9p2i()`; reconstructing a second sample set
was unnecessary to establish that exactly the two additive fields are omitted.
The follow-through passed 50 tests across baseline CLI, sample serialization,
shared-cache enforcement, and modern completion partitions. Ruff, format, and
strict mypy passed on the three affected source/test files.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-
batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Workflow-redesign agent; both stop-boundary and compatibility-label findings were repaired and independently rechecked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.

The recording-destination control now injects the same runtime interruption
without backup-retirement failure, preserving exact replay/audit comparisons.
The case-sensitive-filesystem branch expects three ticks plus a typed normal
stop. Four focused tests and typing/lint passed; independent review approved
the change. The Linux branch was inspected locally, not executed on this
case-insensitive filesystem.
