# Bind experimental results to actual agents and meeting decisions

**Status:** done

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

- [x] Review correction: recordings stamp agent-factory/substrate identity once
  on the first tick row instead of on every tick row; the first tick row stays
  authoritative and a later or terminal row that contradicts it, or a stamp that
  appears only after an unstamped first row, is still refused.
- [x] Review correction: the tick-row key set is pinned, the interrupted-prefix
  retired-lever check reads the resolved stamp, and no committed recording or
  report byte is rewritten.

- [x] Validate actual factory/config agreement even when the requested config
  is absent or all-default, before a recording is created. Ordinary custom
  scripted factories remain usable without falsely certifying their identity.
- [x] Current game and aggregate outputs retain recorded experiment/substrate
  identity. Historical absence means unknown, not invented current provenance;
  mixed arms cannot receive a single misleading baseline label.
- [x] Current strict readers/reports validate the ballot reduction against
  recorded outcome/ejectee using the applicable recorded or explicitly supported
  threshold. Forged targets with unchanged engine hashes are refused.
- [x] Test real candidate recording-to-report/API paths, partial runs, absent
  historical fields and deliberately conflicting identities/outcomes. Preserve
  historical projection bytes and current redaction/type-field inventories.
- [x] Canonical and ML corpus reports/replays still verify; targeted tests,
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
Recording writes the agent-factory/substrate identity pair once, on the first
tick row, instead of on every tick row; readers keep the first tick row
authoritative, still refuse a conflicting later or terminal stamp, and now also
refuse a stamp that first appears after an unstamped first tick row. No committed
recording, report or engine byte changes, and no reader loses provenance on an
interrupted prefix; new recordings are smaller.

## Validation

Run `uv run pytest tests/eval/test_balance_eval.py tests/orchestrator/test_experiment_config.py tests/orchestrator/test_replay_integrity.py tests/api/test_eval_routes.py -q`
after confirming current test filenames. Also run all four
`scripts/build_sample_report.py --sample-dir <set> --check` commands,
`bash scripts/verify_samples.sh`, generated-type checks and `bash scripts/check.sh`.
Plant inconsistent ballots and an experimental factory with absent config.

## Results (implementation in progress)

Architecture: [layering and enforced boundaries](../../docs/architecture.md#layering),
[substrate identity](../../docs/architecture.md#determinism-and-the-substrate-ladder)
and [explicit cleanup experiments](../../docs/architecture.md#explicit-cleanup-experiments).
The engine still consumes recorded actions and meeting outcomes; these changes
bind claims to their recorded inputs without changing tactical or model decisions.

Factory validation now compares actual tactical options even when the requested
configuration is absent or all-default, before either output is prepared. Only
exact built-in agent and role-appropriate policy classes receive `scripted` or
`experimental` identity; wrappers and subclasses remain usable as `custom` when
no tactical experiment is requested. The kind describes those policy classes,
not an independent certificate of every runtime behavior or a baseline label.

Current reports retain recorded factory, experiment, substrate and optional crew
and impostor policy identities. Deterministic aggregate groups keep different
identities separate and reject groups that contradict their games. Missing
historical identity remains null; a missing aggregate field remains null rather
than claiming an empty or baseline population. Current API report mirrors and
replay metadata retain these fields without widening failed-call disclosures.

Resolved meeting records and reports retain the configured confidence cutoff.
The default runner captures its actual resolved configuration; custom runners
can supply their cutoff explicitly. Current strict reconstruction re-tallies
before applying the meeting result. Missing cutoffs use the named frozen legacy
`0.6` compatibility rule, and the API labels this interpretation separately from
a recorded cutoff. Historical walker profiles keep their declared checks and
legacy cutoff; explicit recorded cutoffs take precedence where tally validation
is enabled. Outcome verification does not manufacture historical provenance.

Independent review then demonstrated malformed voter lists and low-confidence
illegal targets that retained the same skipped outcome and every engine hash.
Strict reconstruction now first requires exactly one ballot from every living
player and normalized targets naming either `SKIP` or another living player.
The original authored target remains separate guard provenance; an invalid
normalized target is refused rather than silently rewritten during validation.

Normal `build_sample_report.write_report` output now serializes the full current
DTO, including unknown historical fields. The explicit historical projection
preserves earlier report bytes. `--check` accepts that projection only for an
old report shape backed by unstamped, nonexperimental source data; removing
identity from a newly stamped candidate cannot select compatibility mode.

The authorized public task-activity account widens the spoken observation union,
so the spectator contract is version 4. Generated types and the shared live/static
client retain explicit version-2/3 compatibility and the existing audio refusal.
Optional source tick, phase, local observation order and observer position fields
support the adjacent version-2 evidence reader; they do not expose a global event
index. These changes are necessary API follow-through for the authorized public
account and observation work, not an adoption of either experimental profile.

Development verification so far:

- `.venv/bin/python -m pytest tests/orchestrator/test_experimental_evaluation_integrity.py tests/orchestrator/test_replay_integrity.py tests/eval/test_report_schema.py tests/scripts/test_build_sample_report.py tests/eval/test_balance_eval.py tests/api/test_eval_routes.py tests/eval/test_replay_walk.py tests/api/test_view_model.py tests/api/test_leak.py -q --tb=short`: 220 passed, 2 skipped before the final custom-policy-footer control; the expanded integration file then passed all 20 tests.
- All four `.venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check` commands passed for `replays/{samples,ml_corpus}/{4p1i,9p2i}`. No committed report or replay was rewritten.
- `UV_CACHE_DIR=/tmp/ailibi-evaluation-uv-cache UV_NO_SYNC=1 bash scripts/verify_samples.sh`: all 100 canonical recordings verified. The isolated cache avoids sandbox access to the user cache and does not change dependencies.
- `AILIBI_SAMPLES_ROOT=replays/ml_corpus UV_CACHE_DIR=/tmp/ailibi-evaluation-uv-cache UV_NO_SYNC=1 bash scripts/verify_samples.sh`: all 200 ML corpus recordings verified.
- Targeted strict mypy on the 14 changed Python consumers/tests and Ruff passed. Code generation completed. `npm test -- src/api/client.test.ts src/api/replayBodies.test.ts`: 41 passed, including compatible version-2/3 static reads and planted unsupported audio.
- Controls reject experimental factories under absent/default configuration while preserving prior replay/audit bytes; preserve custom/subclass identity; carry a real partial candidate through report and API; separate mixed and historical identities; reject changed prefix stamps; preserve a custom policy footer; reject altered ballot targets/confidence/cutoffs with unchanged engine hashes; and refuse stripped candidate labels in a legacy-shaped report.
- Final focused follow-through: 102 passed, 2 skipped across integration, eval API, disclosure inventory, generated view-model and serializer tests; expanded policy-side serializer controls passed all 17 script tests; the final integration file passed all 22 tests, including partial/completed custom factories refused under an explicit default-policy claim and recorded cutoffs overriding a walker's legacy cutoff. Generated-type `--check`, `npm run tsc:check`, and targeted strict mypy passed.
- Independent ballot correction: `.venv/bin/pytest tests/orchestrator/test_experimental_evaluation_integrity.py tests/orchestrator/test_replay_integrity.py -q --tb=short` passed all 55 tests. Seven additional real-record mutations cover duplicate, missing, empty and foreign voters plus dead, self and foreign normalized targets; each proves its tally and engine hashes remain unchanged before both strict readers refuse it. All four historical report `--check` commands still pass after this tightening.
- Full-gate fixture follow-through: `.venv/bin/pytest tests/eval/test_balance_eval_meeting_runner.py tests/orchestrator/test_completion_status.py -q --tb=short` passed all 25 tests. The canned skip runner now supplies its actual living roster's ballots; the conflicting-terminal plant retains matching identity fields so it continues testing chronology refusal rather than failing an earlier provenance check. Validator behavior was not weakened. Strict mypy and Ruff passed on both files.

Remaining: independent review and the coordinator's full `bash scripts/check.sh`
gate, including the public summary grouping/render integration. No
live provider calls, default gameplay changes, experimental adoption or merge.

## Results

The [source-bound checkpoint](../../audits/deduction-candidate/checkpoint.md)
records implementation decisions, separate review findings, synthesis, measured
denominators, the full project gate, all 300 reconstructions, four historical
report checks and both browser journeys. Its measurement binds the exact runtime
source and frozen inputs. Architecture references are Layering, Enforced
boundaries and Explicit cleanup experiments. All acceptance work for this card
has passed; earlier provisional Results above record the state at their writing.
No default adoption, main merge, historical re-recording or live spending occurred.

### Recording envelope correction (2026-09-07)

Reopened for FU-D2 (also carried as NC4-4 and FU-APPX-5) in the follow-up
review archived beside the [owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md)
as `REVIEW_REPORT_FOLLOWUP.md`. This card introduced the prefix identity stamp,
and the earlier verification checked only that the stamp was PRESENT and that a
contradicting row was refused. It never asked how often the stamp was written.
The recorder was repeating the coupled `agent_factory_kind` + `substrate_flags`
pair — 794 bytes of an unchanging slate — on every tick row. Measured against the
committed corpora that repetition is +3.5% on the 9p2i sample set, +13-15% on the
two 4p1i sets, and up to +166% on the smallest committed 4p1i file, where a dozen
copies of one slate outweigh the game they describe. Nothing read past the first
row, so every repetition bought nothing.

The pair is now written on the FIRST tick row and the `game_over` row only. Row 0
is authoritative: rows 1..N-1 carry neither key and inherit it, so the prefix
guarantee is unchanged — a recording killed before `game_over` still names its
factory and substrate from its very first row. A later tick row or a terminal row
that CONTRADICTS row 0 is refused with the unchanged wording, and a stamp that
appears only after an UNSTAMPED row 0 is now refused too, because inheriting it
backwards would let a re-stamped suffix claim provenance the recorded prefix never
carried. `orchestrator/replay.py` grows one module-private `_first_tick_stamp`
helper that both readers share; `read_substrate_flags` stays deliberately
terminal-only and now says so. `eval/replay_walk.py` reads the RESOLVED stamp
rather than the `game_over` row, so an interrupted prefix stamped with a retired
lever OFF is refused exactly like a completed recording — its `ValueError`
propagates out of the walk the way `recorded_temporal_observation_version`'s
already does, so no caller changed.

Focused command and counts:

```sh
.venv/bin/pytest tests/orchestrator/test_experimental_evaluation_integrity.py \
  tests/orchestrator/test_replay.py tests/eval/test_replay_walk.py \
  tests/orchestrator/test_completion_status.py \
  tests/orchestrator/test_substrate_binding.py \
  tests/orchestrator/test_temporal_delivery.py \
  tests/orchestrator/test_replay_policy_stamp.py \
  tests/orchestrator/test_replay_integrity.py \
  tests/eval/test_balance_eval.py tests/eval/test_validity.py \
  tests/api/test_replay_loader.py tests/api/test_main.py \
  tests/api/test_cost_integrity.py tests/api/test_public_results.py \
  tests/scripts/test_manifest_writer.py tests/scripts/test_build_sample_report.py \
  -q --tb=short
```

That selection passed 604 tests in 53.61 seconds. `tests/orchestrator/`
collects 580 tests with no collection error. Ruff check/format and strict mypy
pass on the three changed source modules and the three changed test modules.

Zero of the 300 committed recordings carried a tick-row stamp, so no committed
byte moves: all four `scripts/build_sample_report.py --sample-dir <set> --check`
runs report consistent, and `git status --porcelain replays docs/artifacts.md
audits` prints nothing. A default-path byte-identity spot check recorded seeds 0
and 3 at `--max-ticks 12` under the fake provider at three trees — `cfde4c89`,
this card's `fd1f923c` and the corrected tree. State-hash sequences are identical
across all three for both seeds (12 ticks each). Tick rows 1..N-1 are
byte-identical to `cfde4c89`; row 0 differs from it by exactly the coupled pair
and nothing else. Against `fd1f923c` the entire delta on rows 1..N-1 is the
removed pair, with row 0, the meeting rows and the terminal row byte-identical.
Recorded bytes fall 8,723 per seed, -15.3% on seed 0 and -15.4% on seed 3.

Negative control, by the isolated module-copy recipe at
`tasks/work/recording-replacement.md`: `git show fd1f923c:orchestrator/replay.py`
loaded under its own module name, asserted to resolve to the temporary copy.
Under the selector `stamp_appears_late or rides_only_the_first_tick_row or
silent_later_tick or prefix_stamped_with_a_retired_lever` the pre-change module
fails all 5 of the new envelope cases (182 deselected). The clean discrimination
is the reader-only class, whose cases build entry objects directly and so do not
depend on the writer: `TestOnceStampedTickIdentity` runs 3 failed / 3 passed
against the pre-change reader — it fails the two inherit clauses and the new
late-stamp message, and PASSES the contradicting-later-row, terminal-disagreement
and wholly-unstamped clauses, which is the statement that those three refusals
are unchanged by this commit. The writer-level conflict cases also fail under the
old module, but at their new envelope precondition (`field not in rows[second]`)
rather than at the refusal, so they are not evidence either way about the
refusals.

Limitations. The saving is a recording-size property only; no engine rule,
prompt, provider, schema version or historical byte changed, and no live provider
ran. The measured percentages are the committed corpora's shapes, not a
projection onto future sets. `read_substrate_flags` still returns `None` for an
interrupted prefix by design — callers that must not lose provenance there use
`recorded_substrate_flags`, and this commit did not audit every existing call
site for that distinction beyond the retired-lever check it repaired. Process
termination between the first tick row and its flush is outside this contract, as
before.

<!-- gate paragraph added by the checkpoint commit -->
