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

`bash scripts/check.sh` passed 6,833 Python tests, 20 optional skips, three
expected failures and 500 frontend tests plus all static/build gates.
`bash scripts/verify_samples.sh` verified 100 canonical recordings. Existing
recordings, reports and DTO bytes were not rewritten. Owner review remains
pending; experimental adoption is not applicable to this reader optimization.
