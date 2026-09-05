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
