# Reuse verified public results while their sources are unchanged

**Status:** done

## Outcome

Repeated public-results requests reuse a bounded per-loader summary instead of
reconstructing the whole replay set. Changed inputs and substrate settings still
require validation; cached results cannot hide corrupted recordings.

## Evidence

The [independent review](../../audits/review-2026-09-06/REVIEW_REPORT.md) finding
C6-1 reports repeated walks for every `/eval/summary` request. The authorized
[post-review plan](../post-review-plan.md) includes fingerprint-based caching.
The existing `recording_fingerprint` includes all replay bytes, roster and
manifest. Existing lower-level caches use mtimes, so a content change must also
invalidate those cached inputs before deriving a new result.

## Acceptance

- [x] Review correction: the warm summary and a cold rebuild answer the same way
  for the same directory. A recording the loader serves but the previous
  fingerprint ignored now invalidates the cache instead of being served around.

- [x] A repeated same-source request performs no additional replay walk and
  returns identical public results. Explicit cache clearing forces revalidation.
- [x] Replay, roster, manifest and ambient-substrate changes cannot reuse a
  previous summary. Same-mtime semantic corruption is refused, and a failed
  generation never populates the cache.
- [x] The cache is bounded to one result per loader and retains no global state.
  Before/after source and substrate checks reject drift during generation.
- [x] Publish a scoped local cold/warm measurement bound to source bytes; keep
  hardware timing outside CI pass thresholds and do not claim request coalescing.
- [x] Focused adverse tests, strict typing/format and `bash scripts/check.sh`
  pass. Existing recordings, API DTOs and public results remain unchanged.

## Constraints

Read docs/architecture.md for privileged reader boundaries. No game/prompt
changes, providers, dependencies, new threads, asynchronous coalescing, or
historical evidence replacement. Root owns this card and its runtime/tests;
other workers own the viewer components and generated type fixture.

## Expected scope

`api/public_results.py`, `api/replay_loader.py`,
`tests/api/test_public_results.py`, a scoped reproducible measurement script
and correction evidence under `audits/review-2026-09-06/`. Necessary cache
invalidation consumers may follow through within the reader boundary.

## Record impact

Post-record reader optimization only. No replay, model, prompt or schema bytes
change. Previously committed timing captures remain historical measurements.

## Validation

Run `uv run pytest tests/api/test_public_results.py -q`, strict mypy and Ruff
over changed sources, and `bash scripts/check.sh`. Record exact input and
implementation identities with the local measurement. A planted same-mtime
winner change must fail after warming the cache.

## Results

The per-loader summary cache holds one immutable result keyed by exact recording,
roster, manifest and substrate identity. Changed bytes clear lower reader caches
before reconstruction. Before/after input checks reject drift during a build;
analysis overrides are refused before a cache lookup. No global state, threads
or request coalescing were added. This follows architecture Packages and
Determinism and the substrate ladder in the privileged reader boundary.

Seventeen API tests and four measurement tests passed, including same-mtime
winner/roster corruption, manifest change, substrate drift, source mutation
while building, explicit clearing and independent loader instances. Independent
review also exercised membership changes, warmed analysis overrides and entry
replacement and found no blocking defect.

Three repetitions per set are retained in
[4p1i](../../audits/review-2026-09-06/public-results-4p1i.json) and
[9p2i](../../audits/review-2026-09-06/public-results-9p2i.json). Each compares the
same reader with whole-summary reuse bypassed or enabled, then makes a cold and
warm sequential request. All corresponding serialized responses are identical.

| Set | Warm walks, bypass / reuse | Median warm ms, bypass / reuse | Response bytes |
| --- | --- | --- | --- |
| 4p1i | 50 / 0 | 520.12 / 2.56 | 864 |
| 9p2i | 50 / 0 | 2104.54 / 25.17 | 3618 |

Reproduce using `uv run python scripts/measure_public_results.py --set-dir
replays/samples/<set> --output <new-path>`. The instrument refuses existing
outputs, input-directory outputs and changed sources. Captures contain the
instrument and reader hashes, complete input-set identity, platform and Python.
They describe this correction checkpoint, not later gameplay implementations.
The full check was running on the machine during capture: hardware timings are
local diagnostics, not CI targets. Cold reconstruction remains; no HTTP, RSS,
concurrent throughput or browser performance improvement is claimed.

At `144fc2e1`, `bash scripts/check.sh` passed 6,833 Python tests, 20 optional
skips, three expected failures and 500 frontend tests plus all static/build gates.
`bash scripts/verify_samples.sh` verified 100 canonical recordings. Existing
recordings, reports and DTO bytes were not rewritten. Owner review remains
pending; experimental adoption is not applicable to this reader optimization.

### Warm-cache invalidation correction (2026-09-07)

Reopened for FU-B-01, the follow-up to pre-existing finding M2-F1 in the
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md). The cache key is
`recording_fingerprint`, so the cache was only ever as complete as that
fingerprint's idea of a recording. It was narrower than the loader's: a
negative-seed recording the loader serves left the key unchanged, so a warm
summary returned the previous view while a cold `ReplayLoader` over the same
directory raised `Public results cannot omit invalid or unverified recordings`.
The earlier verification exercised same-mtime corruption and roster, manifest and
substrate changes -- every one of them a change to a file the fingerprint already
matched -- so it could not surface a file the fingerprint never looked at.

Nothing in the caching logic changed. The repair is the shared filename contract
recorded under [Shared recording-filename contract
(2026-09-07)](public-recording-provenance.md), which the cache key now inherits.
`tests/api/test_public_results.py` adds
`test_warm_summary_refuses_after_a_negative_seed_recording_appears`, mirroring
the same-mtime corruption case: the warm loader and a fresh loader over the same
directory now both refuse, and removing the file restores the original summary
byte-for-byte.

Focused command:

```sh
.venv/bin/pytest tests/orchestrator/test_recording_fingerprint.py tests/api/test_public_results.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_verify_samples.py tests/scripts/test_manifest_writer.py tests/api/test_view_model.py -q --tb=short
```

That selection passed 172 tests with one optional skip; 20 of them are this
card's API suite. Under the negative control described on the provenance card --
the pre-repair fingerprint predicate loaded under its own module name inside the
current tree -- the new warm-summary case fails with `DID NOT RAISE`, which is
the stale warm view itself.

Record impact: post-record reader repair only. No replay, roster, manifest or
report bytes changed, and the retained cold/warm measurements remain valid: the
cache still holds one immutable result per loader and still adds no threads,
global state or request coalescing.

Limitations: the correction widens what invalidates the cache, not how quickly a
cold rebuild runs. Concurrent cold requests may still each reconstruct, and
crash durability and concurrent writers stay outside the contract.

The follow-up correction gate ran on the tree at `93bf7d54`, the last commit before this record; the only edits after that gate are the checkpoint records in the commit that carries this paragraph. `bash scripts/check.sh` passed 7,173 Python tests, 20 optional skips and three expected failures; 514 frontend tests; strict typing on 467 sources; lint/format; four import contracts; document and generated-type checks; and the production build. `bash scripts/verify_samples.sh` verified all 300 canonical recordings (100 under `replays/samples/`, 200 under `replays/ml_corpus/`); all four `scripts/build_sample_report.py --check` runs are consistent; `pytest tests/orchestrator/ --collect-only` collects in a fresh interpreter; the API and static browser journeys passed (13 passed, 3 skipped). No committed recording, report, metric, weight or adoption verdict was rewritten, and every experiment candidate remains default-OFF.
