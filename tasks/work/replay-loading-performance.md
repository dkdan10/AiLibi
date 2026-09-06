# Fetch model-call bodies on demand and characterize replay loading

**Status:** done

## Outcome

Opening a replay transfers its timeline and meeting structure without model-call
prompt/response bodies. Opening the inspector retrieves the recorded bodies on
demand in both API and static modes. A reproducible offline measurement reports
payload, latency, belief reconstruction, memory and concurrent cache misses
before any further optimization is selected.

## Evidence

The [replay route](../../api/routes/replays.py) returns the complete `ReplayView`.
[`_llm_call_view`](../../api/replay_loader.py) includes both text
bodies; [`windowReplay`](../../frontend/src/store/replayStore.ts) then blanks
them after download. The inspector already fetches the existing per-meeting
detail route when its prompt/response tab is opened. The
[static builder](../../scripts/build_demo_bundle.py) writes those full bodies
into both the bulk replay JSON and the individual meeting JSON.

The loader has separate bounded LRU caches for playback, meeting memories,
belief frames and summaries. Opening beliefs is already lazy in the browser,
but its first server request performs another engine/memory walk. Concurrent
misses can repeat that work before the first result enters the cache. The
[existing benchmark](../../tests/eval/test_performance.py) measures generation
throughput, not this reader path.

Preliminary characterization on 2026-09-05 used the frozen working tree awaiting
the combined gate, based on `6d3c56e9`, Python 3.11.15, macOS 15.7.3 arm64.
Selection was deterministic: largest raw recording in 4p1i, median raw recording
in 9p2i, and largest raw recording in 9p2i, from the 50 numeric files in each set.
Each row below ran in a separate process. Cold means a fresh application cache;
the operating-system page cache was not flushed. These are single-run diagnostic
values, with other development work on the machine, not latency targets.

| Set / seed | Ticks / meetings / calls | Full JSON bytes | Body-free JSON bytes | Cold / warm load ms | First beliefs ms |
| --- | --- | --- | --- | --- | --- |
| 4p1i / 29 | 12 / 1 / 6 | 91,717 | 25,946 | 8.47 / 0.40 | 8.37 |
| 9p2i / 31 | 22 / 3 / 36 | 635,998 | 101,114 | 26.29 / 0.36 | 36.01 |
| 9p2i / 23 | 29 / 4 / 52 | 966,404 | 133,445 | 29.19 / 0.35 | 73.95 |

The proposed projection in this probe changed only `prompt_text` and
`response_text` to empty strings. For seed 23, this removes 86.2% of serialized
bytes; diagnostic gzip sizes were 77,476 and 12,267 bytes. This is an estimated
projection benefit, not a shipped improvement or a claim about HTTP compression.
Seed 23's process peak RSS rose from 54.9 MiB after imports to 67.2 MiB after
playback serialization and 76.8 MiB after beliefs. This includes temporary probe
allocations and is not retained-cache size. Its 43,580-byte beliefs response
required the separate memory walk; warm beliefs took 0.40 ms.

Four simultaneous in-process ASGI requests to `/replays/headless-seed-23`
returned 966,404 bytes each and performed four visibility walks, with individual
latencies of 239–258 ms. Four concurrent `/beliefs` misses performed four memory
walks, taking 362–378 ms. Repeating either batch warm caused no additional walk.
The framework's synchronous-route dispatch provided concurrency; the probe
started no application threads and used no live provider. This demonstrates
duplicate work, not an incorrect result or a production capacity limit.

The temporary probes are reproducible in the current environment with:

```sh
PYTHONPATH=. .venv/bin/python /tmp/ailibi-replay-performance-probe.py 4p1i 29
PYTHONPATH=. .venv/bin/python /tmp/ailibi-replay-performance-probe.py 9p2i 31
PYTHONPATH=. .venv/bin/python /tmp/ailibi-replay-performance-probe.py 9p2i 23
PYTHONPATH=. .venv/bin/python /tmp/ailibi-replay-concurrent-probe.py
```

These temporary files are local investigation aids. The implementation must
replace them with the bounded, committed measurement harness below before using
its results as durable performance evidence.

## Acceptance

- [x] A bounded offline harness records source identity, interpreter/platform,
  selected recordings and repetitions. It measures fresh-process/application
  cold and warm load/serialization, actual API and static JSON bytes, optional
  diagnostic compression, belief/memory walk counts and timing, peak RSS, and
  simultaneous same-key cache misses. Separate memory instrumentation from timed
  samples where instrumentation materially changes runtime; distinguish retained
  memory from process peak. Include no-meeting, multi-meeting and larger samples.
- [x] Preserve the existing full-body public API default. Add an explicit
  opt-in body-free replay projection used by the current browser, retaining all
  other timeline, transcript, call identity, usage/cost and completion fields.
  The bulk response itself must omit body content; client-side stripping alone
  does not satisfy this item.
- [x] Reuse the existing per-meeting detail endpoint/file for complete recorded
  bodies unless measurements establish a need for finer granularity. Fetching
  detail preserves exact original prompt/response text and accounting; missing
  detail produces the established visible error state.
- [x] New static bundles bake the same lean initial replay and full per-meeting
  detail. Current clients still open old full-body static bundles. Any added
  DTO marker is optional/defaulted for historical bundles, generated through
  the existing type pipeline, and tested alongside the view-model version guard.
  Do not silently reinterpret a breaking contract under the same version.
- [x] Tests assert actual response/file bytes using distinctive long body
  sentinels, including a planted full-body response that fails the projection
  assertion. Verify exact equivalence of all non-body fields and full detail,
  set/game/meeting isolation, no-meeting and failed-attempt accounting, and
  stale async response/error handling through the existing frontend seam.
- [x] Repeat the same measurement matrix after the payload change. Report
  measured benefit and limits; choose any additional cache or belief-work repair
  from that evidence, or explicitly leave it deferred. Hardware timing is
  recorded, not a tight CI threshold. No cache refactor is required merely
  because duplicate misses were observed.
- [x] API/static inspector journeys, focused tests, generated types, lint/type
  checks, all canonical reconstructions and the combined project gate pass.

## Constraints

Production begins only after the current combined gate/commits and coordinating
dispatch. Work directly on `codex/cleanup`; root owns commits and the full gate.
Follow [architecture](../../docs/architecture.md) Packages, Enforced boundaries,
and Determinism and the substrate ladder. No provider calls, dependencies,
prompt/gameplay/engine changes, canonical-record rewrites or broad rewrite.

The first optimization is the characterized transfer boundary. Keep cache
freshness, replay integrity and substrate checks intact. Do not eagerly compute
beliefs to make their later request appear faster. Item 35's coherent
extractions follow characterization and need their own bounded scope. A cache
coalescing change requires an explicit concurrency/error/cancellation design and
ownership decision after measurements; this card does not pre-authorize new
threads, global mutable state or an unbounded cache.

## Expected scope

The performance owner owns `api/replay_loader.py`, `api/routes/replays.py`,
`api/schemas.py`, `scripts/gen_frontend_types.py`, generated frontend API types,
`frontend/src/api/client.ts`, focused API/client tests, and a narrow reusable
`scripts/measure_replay_loading.py` with focused harness tests. Additive public
follow-through is authorized within the compatibility contract above.
Durable before/after JSON measurements live in
`audits/replay-loading-performance/`; root owns their audit/artifact index updates.

The portfolio owner owns `frontend/src/store/replayStore.ts`, inspector and
navigation UI, `scripts/build_demo_bundle.py`, bundle/browser tests, and summary
generation under its own card. Coordinate the lean projection helper/interface
first; that owner applies the static-bake and any store follow-through. Both
agents have agreed to this one-writer split. Its citation resolver also needs
API/generated types; sequence that additive work explicitly and keep its
semantic assertions and commit scope separate from performance measurements.
Root owns the roadmap/index, source-gate work and final combined verification.

## Record impact

Post-record reader/transport repair. Existing replay, audit, prompt and report
bytes are unchanged. Newly built static artifacts use a body-free initial
projection; retained per-meeting artifacts preserve full recorded bodies.
The current browser opts into lean live responses while old API callers keep
the prior full response, and old static bundles remain readable. No claim that
prompt text was absent from the recording or that failed usage disappeared.

## Validation

Run the committed offline measurement command on the same selected sources
before and after implementation and save its machine-readable output with
source identities. Use targeted pytest for API routes/loader, DTO inventories,
the measurement harness and static bundle; run frontend client/store/inspector
tests, generated-type drift, strict mypy, Ruff, TypeScript and targeted ESLint.
The portfolio owner verifies API/static prompt and response journeys; root runs
`bash scripts/check.sh` and `bash scripts/verify_samples.sh`. Results must name
measured gains, unresolved work, compatibility decisions and review evidence.

## Results

Implemented the opt-in `include_llm_bodies=false` query and matching loader
argument. The current browser requests this projection; the existing public API
default and meeting-detail response still include exact recorded text. A
defaulted `llm_bodies_included` marker is optional in generated TypeScript so old
static bundles remain readable. No view-model version change is needed for this
additive contract. The portfolio owner applied the same lean projection to bulk
static files while retaining full per-meeting files. The server still caches its
full reconstructed view: this repair reduces transfer, not source parsing or
retained model-text memory.

The committed `scripts/measure_replay_loading.py` runs each repetition in a
fresh interpreter, uses actual ASGI routes and the real static data baker, and
records source hashes, platform, wall-clock scope, serialization, requests,
walks and process peak RSS. It rejects changed sources, failed HTTP requests,
invalid bounds and existing output files. No network, provider, npm build or
hardware-sensitive pass threshold is involved. The existing Starlette route
dispatch supplies concurrent calls; the harness starts no application threads.

Durable measurements are [before.json](../../audits/replay-loading-performance/before.json)
and [after.json](../../audits/replay-loading-performance/after.json), captured by:

```sh
uv run python scripts/measure_replay_loading.py --output audits/replay-loading-performance/before.json
uv run python scripts/measure_replay_loading.py --output audits/replay-loading-performance/after.json
```

The first capture preceded the API change at `5006a32f`; the final after capture
at `2026-09-06T01:41:37Z` followed the reader/static integration and independent
temporal-review repairs. It replaced the provisional after measurement once
runtime sources froze; the before capture remains unchanged. Each has three repetitions of four recordings and
four simultaneous cold/warm requests. Selected-recording and complete-set input
hashes match across captures. Reader implementation hashes intentionally differ;
the after capture also includes the coordinated citation/temporal reader work.
Timing changes cannot be attributed solely to body projection.

| Set / seed | Initial API/static bytes before | After | Reduction | Median API cold / warm ms before | After |
| --- | --- | --- | --- | --- | --- |
| 4p1i / 31, no meeting | 11,992 | 12,020 | adds 28 bytes | 4.03 / 0.85 | 4.01 / 0.86 |
| 4p1i / 29 | 91,717 | 25,966 | 71.7% | 7.21 / 1.01 | 6.97 / 0.99 |
| 9p2i / 31 | 635,998 | 101,098 | 84.1% | 21.10 / 1.77 | 20.50 / 1.41 |
| 9p2i / 23 | 966,404 | 133,442 | 86.2% | 26.94 / 2.14 | 27.50 / 1.59 |

Seed 23's after-capture full versus lean diagnostic gzip size is
77,488 versus 12,276 bytes. Its median first-belief time changed from 43.21 to
45.13 ms; median peak process RSS through the concurrent batches was 109.58
versus 104.80 MiB. These small-sample figures are descriptive, not CPU/memory
improvement claims. Every after-capture cold batch still performed four walks,
and warm batches performed none. Coalescing those in-flight requests remains a
bounded follow-up; broad cache or loader decomposition is deferred.

Follow-through was coordinated with the
[portfolio card](portfolio-evidence-experience.md): added public result DTOs,
`/eval/summary`, generated/client wiring and numeric JSON-literal codegen support.
The portfolio owner owns the summary helper, builder and UI. The new pure
`api/observation_references.py` projects only IDs cited by that observer's ballot
from their actual meeting snapshot, retaining explicit unresolved IDs. Scene
time comes from delivered-event-to-frame mappings, separately from observation
time, never from ID parsing. The
[temporal observation card](temporal-observation-contract.md) supplies the shared
delivery helper; this owner applied its narrow API adapter and kept controlled
integrity errors for conflicting temporal versions. No protected prompt or
committed replay bytes were rewritten.

Verification before the combined gate:

- 207 focused Python tests passed, one skipped, across lazy bytes, references,
  API loader/routes/contracts/accounting, the harness and generated literals.
- 70 frontend client/store tests passed; TypeScript and targeted ESLint passed.
  Ruff/format passed on 12 source/test files; strict mypy passed on 11.
- The paid invalid-response/success/transport-abort case retains its failed-call
  rows, aborted status and recorded cost equal to `GameBudget` in both views.
- The actual-wire regression fails against isolated pre-change `5006a32f`
  because the lean response contains the distinctive prompt sentinel; it passes
  on this patch. Archive: `/tmp/ailibi-lazy-baseline-rgu185h9`; output:
  `/tmp/ailibi-lazy-baseline-red.log`. No shared source was replaced.
- Genuine references from seeds 23 and 46 resolve the vent witness, room move
  and different co-presence sighting independently. Foreign/missing IDs remain
  unresolved; an opaque ID containing `999` does not invent observation time.
- Independent review found no API/performance blocker. A separate census resolved
  all 176 ballot-cited observations to text and their exact scene. The portfolio
  owner verified five real-API/static browser cases and the clean-copy browser
  suite (13 passed, three intentional media skips), including full detail after
  lean loading. The combined project gate remains the root's final check.

Final `bash scripts/check.sh` passed: 6,599 Python tests, 20 optional skips,
three expected failures, 467 frontend tests, strict typing, lint, formatting,
import/document contracts and production build. `bash scripts/verify_samples.sh`
passed all 100 canonical recordings. The owner’s final branch review remains
pending. The measurements concern initial replay JSON and local ASGI execution,
not total bundle size, network latency, browser rendering or a deployment SLO.
