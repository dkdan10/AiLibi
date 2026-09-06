# Validate replay chronology and outcomes

**Status:** done

## Outcome

The spectator viewer, game picker, and committed-sample verifier reject replay
labels, meeting placement, and terminal claims that disagree with reconstructed
engine state. A valid interrupted recording remains viewable as a partial game.

## Evidence

At `26386914`, a genuine fake-provider game remains loadable after changing its
first tick label from zero to 9999 or reversing its recorded winner. State
hashes still match: those fields are outside the hash. Filtering rows into tick
and meeting collections also hides their original ordering.

## Acceptance

- [x] Bind tick labels and meeting records to the actual engine transition;
  reject duplicate, orphaned, reordered, mixed-game, and trailing records.
- [x] Check a recorded winner, reason, and optional terminal tick against the
  reconstructed game-over event, including games decided by a meeting.
- [x] Preserve valid unfinished games, interrupted meetings and their retained
  calls, and legacy records without the optional terminal tick.
- [x] The game picker cannot advertise a replay the integrity check rejects;
  viewer requests fail clearly and sample verification reports the failure.
- [x] Adversarial cases demonstrate the old defect; focused tests, the full
  project check, and committed sample verification pass.
- [x] Review correction: the generated fidelity fixture reaches a genuine
  engine terminal and exercises `GameFinale`, agent recaps and decisive events;
  a planted missing terminal/finale fails the gate.
- [x] Regenerated types, targeted tests and the full project gate pass without
  rewriting historical recordings or changing API DTOs.

## Constraints

Follow `docs/architecture.md` Layering and Determinism and the substrate ladder.
Build on the aborted-meeting accounting repair in a separate PR. Reuse the
viewer's engine reconstruction rather than introduce another engine loop.
Keep engine behavior, recording bytes, API DTOs, and historical evidence intact.
Raw parsing/accounting and historical evaluation walker profiles retain their
declared semantics; this card establishes strict spectator/sample validation,
not a new validation policy for every experimental instrument. No live calls,
new dependencies, or re-records.

## Expected scope

A small `orchestrator/replay_integrity.py` validator, `api/replay_loader.py`,
API error handling, sample-verifier follow-through, necessary API/orchestrator/
script tests and fixture corrections, the generated frontend fidelity fixture,
`tasks/README.md`, and this card. The validity gate already delegates to the
sample verifier; update its test expectations for the additional integrity
failures without changing its engine-walk profile. Search consumers before
edits. Keep cache keys sensitive to replay, roster, and substrate changes.

## Record impact

Post-record, unconditional reader repair. Previously accepted contradictory
metadata becomes an explicit integrity failure; valid historical recordings
remain readable without rewriting them. No prompt, detector, or simulation
behavior changes. Report any incompatible committed evidence rather than
silently repairing it.

## Validation

Run adversarial replay tests and affected API/script tests; demonstrate the
new cases fail against isolated preceding modules; run `bash scripts/check.sh`
and `bash scripts/verify_samples.sh`. Use genuine deterministic recordings for
positive controls and mutate metadata while preserving recorded state hashes.

Focused command: `uv run pytest tests/orchestrator/test_replay_integrity.py tests/orchestrator/test_replay_integrity_side_records.py tests/api/ tests/scripts/test_verify_samples.py tests/eval/test_validity.py -q`.


## Results

Verified 2026-09-05. The full `scripts/check.sh` gate passed: 6,182 Python tests
(20 skips, 3 expected failures), 440 frontend tests, lint, formatting, strict
types, architecture boundaries, task validation, and frontend build. Sample
verification passed all 100 canonical recordings without changing their bytes.

All 37 new replay-integrity cases pass. Running the 25 core cases against an
isolated prior loader (`git show 26386914:api/replay_loader.py`) produced 19
adversarial failures and six passing controls. Independent review supplied
planted failures for cross-meeting identities, duplicated attempt IDs, opaque
partial IDs, and empty IDs. A planted substrate-toggle test also exposed and
verified the cache correction across picker, playback, and memory requests.

Necessary follow-through corrected invented outcomes in API/codegen fixtures
and updated validity tests because their existing sample-verifier dependency
now reports more integrity failures. A separate planted verifier exception
preserves crash-wrapper coverage. Historical evaluation walk profiles, API DTO
types, and recorded evidence remain unchanged.

The strict guarantee covers spectator playback, picker metadata, and sample
verification. Raw accounting retains reported usage even when playback refuses
an artifact; its recorded outcome split remains unverified. No live-provider
run, canonical re-record, or gameplay change occurred.

### Review correction in progress

Reopened for [review finding C7a-2](../../audits/review-2026-09-06/REVIEW_REPORT.md#59-type-fidelity-fixture-lost-its-gamefinale-subtree-c7a-2).
The prior Results remain historical. The current generator serves a valid
three-tick unfinished prefix, so its generated fixture no longer exercises the
finale subtree. Finish that fixture through legal engine actions, reuse the
existing terminal-fixture helper, and add an adverse omission control.

The generator now records legal wait/kill actions until the engine emits its
parity terminal. The production loader supplies the generated finale, all four
agent recaps and decisive kill/game-end events. `api.ts` is unchanged;
`api.fidelity.ts` is regenerated. The fidelity gate now checks verified completion
and these populated subtrees. Five planted perturbations remove completion,
verification, finale, recaps or decisive events and must fail those assertions.

Targeted verification on 2026-09-06:

```bash
.venv/bin/python scripts/gen_frontend_types.py --check
.venv/bin/python -m pytest tests/api/test_view_model.py -k fidelity -q
npm --prefix frontend run tsc:check
```

The generation check and TypeScript compile passed; all six fidelity tests
passed, including the five adverse controls. The broader correction run passed
490 tests before adding the final two metadata controls. Ruff and strict mypy
passed on the correction's five Python files. Architecture references remain
Layering and Determinism and the substrate ladder: this fixture passes through
the existing engine, writer and privileged reader, with no invented terminal or
DTO change. No committed recording or simulation default changed. The final
full-project gate remains the coordinator's pending integration check.

The correction checkpoint passed `bash scripts/check.sh`: 6,833 Python tests,
20 optional skips, three expected failures, 500 frontend tests, strict typing,
lint/format, import/document contracts and the production build. All 100
canonical recordings verified. The [durable correction record](../../audits/review-2026-09-06/correction-record.md)
records the independent reviews, discovered rollback repair and integration
checks. This completion is on cleanup, awaiting owner review and merge.
