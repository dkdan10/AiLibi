# Publish facts that identify their recordings

**Status:** done

## Outcome

Public highlights omit obsolete scores and claims. Existing screenshots identify
their historical recording, and the documented installation and offline demo
journey work from a clean source copy with stated prerequisites.

## Evidence

The current highlight artifact describes earlier recordings: 16 of 50 meeting
counts and nine endings disagree with current replays. Its stale banner does not
stop those claims from rendering. Media documents baseline-7/v4 captures beside
the current baseline-8/v5 demo. The README calls dependency installation offline
and assumes a bare `python` executable for serving the bundle.

## Acceptance

- [x] Review correction: one filename pattern decides what a recording is. The
  source fingerprint, the public completeness check, the loader, the sample
  verifier and the manifest reader share it, so a recording the loader will
  serve cannot be invisible to the fingerprint. Every committed set keeps its
  exact published fingerprint.

- [x] Missing or mismatched actual recording fingerprints suppress obsolete
  enrichment in API and static viewing without hiding valid replay metadata.
- [x] Fact production and score publication bind to replay, roster, and manifest
  bytes; mutating an input prevents old facts from receiving a fresh stamp.
- [x] Existing media remains unchanged and is labelled historical, with source
  and asset provenance that can be verified without pretending it is current.
- [x] Stated prerequisites, installation, offline fake-provider verification,
  static serving, and paired replay/audit replacement instructions are accurate.
- [x] A temporary clean source copy completes setup and the documented bounded
  offline run/build journey; focused tests and the coordinating full gate pass.

## Constraints

Work on `codex/cleanup`; keep `main` and committed recordings unchanged. Follow
`docs/architecture.md` Packages and Determinism and the substrate ladder.
Suppress stale scores; do not reinterpret the historical scorer's failing
self-check or regenerate gameplay imagery. No live calls, new dependencies,
API schemas/routes, report-schema changes, or scoring/detector changes. Coordinate
the narrow `ReplayLoader.rubric()` handover with the API owner. Broader portfolio
presentation and compact tournament results remain separate work.

## Expected scope

The review correction additionally owns the shared filename contract in
`orchestrator/recording_fingerprint.py` and its four readers
(`api/public_results.py`, `api/replay_loader.py`, `scripts/_verify_samples.py`,
`scripts/_manifest_writer.py`) plus the new
`tests/orchestrator/test_recording_fingerprint.py`.

A neutral recording-fingerprint helper; rubric producer/extractor stamping;
rubric freshness and bundle/highlight consumers; focused provenance, API, bundle,
and frontend tests; README installation/media sections and directly related
reading/deployment/media documentation. Root owns task index/roadmap and final
status. No dependency changes or shared `frontend/node_modules` installation.

## Record impact

Post-record, unconditional public-reader and documentation repair. Historical
raw artifacts remain preserved; no simulation or experimental verdict changes.

## Validation

Perturb genuine source copies while leaving manifest commit labels unchanged;
verify rejection/suppression and a fresh positive control. Run affected pytest,
ruff, strict mypy, frontend tests/typecheck, documentation checks, and the clean
copy's setup, bounded fake-provider replay comparison, sample verification, and
static bundle build/HTTP smoke check. The root agent runs the full project gate.

## Results

The raw facts and score producer now bind replay filenames/content, roster, and
manifest bytes through a shared versioned fingerprint. API, baked data, and the
client suppress stale score rows. Current recordings remain browseable. Existing
scores were preserved because the historical extractor self-check has not been
reconciled; this change does not relabel or rerate that evidence. Replay cards
also consume the coordinated optional stop classification when outcomes are
revealed; older null-winner metadata reads Unfinished.

The new mutation cases failed before the loader handover, then passed with a
genuine fresh-recording positive control. Final focused verification:

- Provenance, API view model/set, and bundle suites: 113 passed, one optional
  skip. Replay, roster, manifest, added-file, and missing-stamp mutations reject
  score publication and suppress public enrichment.
- Frontend client/copy/card suites: 265 passed; TypeScript and targeted ESLint
  passed. Rendered stop labels preserve the existing spoiler control.
- Seven changed Python files pass ruff and format; the five typed helper,
  consumer, and test modules pass strict mypy. The four affected documentation
  perturbation tests pass after shortening prose instead of raising ceilings.
- Historical replay and all four spectator asset hashes were verified against
  commit `5184417779d26a0ddc26c703574fdcf341e16098`. The new provenance metadata
  records those identities; the asset mutation test detects changed bytes.

A temporary source copy, without `.git`, `.venv`, `node_modules`, or `.env` at
creation, installed both updated locks using fresh package caches. Installation
used network access. Afterward the README's two seed-42 fake runs finished at
tick 12 with identical replay bytes and zero cost, and all 100 samples verified
with offline dependency resolution. The final refreshed source built seven
featured games into 154 JSON files (6.0 MB; 7.2 MB whole bundle). The documented
static server served HTML, a current replay, and an empty stale rubric. The real
browser journey passed all 11 tests; three opt-in media captures stayed skipped.
The sandbox initially blocked package-host DNS and local port binding; identical
commands passed with the necessary installation/loopback permissions.

Logs remain in the temporary `ailibi-clean-source-elmtcui_` directory:
`clean-setup.log`, `offline-verification.log`, `clean-bundle-build.log`,
`clean-static-http.log`, and `clean-browser.log`. No live provider calls,
historical report/replay edits, or media regeneration were performed. Final shared validation passed, as recorded below.

### Combined verification and review

The final `bash scripts/check.sh` run passed: 6,409 Python tests (20 optional
skips, three expected failures), 455 frontend tests, strict typing, lint,
formatting, import boundaries, 390 historical contracts/prompts, and the build.
`bash scripts/verify_samples.sh` verified all 100 canonical recordings. No
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Coordinator; source and asset identity, stale-score mutations, and clean-source results checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.

### Shared recording-filename contract (2026-09-07)

Reopened for FU-B-01, the follow-up to pre-existing finding M2-F1 in the
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md).

The earlier verification perturbed recordings whose names the fingerprint
already matched, so it never asked whether the fingerprint and the loader agree
on what a recording *is*. They did not. The fingerprint and the public
completeness check matched a numeric-only `replay-seed-<n>.jsonl`, while
`api/replay_loader.py` parsed, validated and served the signed spelling
`replay-seed--1.jsonl` as `headless-seed--1`. A negative-seed recording that the
loader publishes therefore left the digest unchanged, so a warm public summary
kept serving the previous view while a cold rebuild refused the same directory.
`scripts/_verify_samples.py` and `scripts/_manifest_writer.py` carried a third
numeric-only parser of their own.

`orchestrator/recording_fingerprint.py` now exports the single contract --
`REPLAY_FILENAME_GLOB`, `REPLAY_FILENAME_PATTERN` and
`replay_seed_from_filename` -- and the fingerprint, the public completeness
check, the loader's `_parse_seed_from_filename`, the sample verifier and the
manifest reader all resolve a name through it. The pattern is deliberately
permissive rather than strict: the loader already serves the signed spelling, so
a fingerprint of the published inputs that ignored a file the loader publishes
would not be a fingerprint of what is published. Narrowing the loader instead
would have withdrawn recordings already served. Numeric-only names match both
spellings identically, so both committed sets keep their exact published
fingerprints, pinned in the new test against the two constants
`api/public_results.py` maps to a source URL.

One deliberate exception: `remove_noncanonical_replays` in
`scripts/_manifest_writer.py` stays numeric-only, with a comment naming
`replay_seed_from_filename` and saying so. Widening a delete predicate is not a
fingerprint fix. Its docstring no longer claims such files are ignored by
`ReplayLoader`; it now says a file whose seed core the pruner does not recognise
is left untouched.

Focused command:

```sh
.venv/bin/pytest tests/orchestrator/test_recording_fingerprint.py tests/api/test_public_results.py tests/scripts/test_public_recording_provenance.py tests/scripts/test_verify_samples.py tests/scripts/test_manifest_writer.py tests/api/test_view_model.py -q --tb=short
```

That selection passed 172 tests with one optional skip. `.venv/bin/pytest
tests/orchestrator/ --collect-only -qq` exits 0 over 30 modules. Ruff check and
format, strict mypy over the five changed modules and the two changed test
modules, and `lint-imports` (four contracts kept) all pass; `api/` already
imported `orchestrator.recording_fingerprint`, so no import contract moved.

Negative control: load an isolated `git show 9b333a76:orchestrator/recording_fingerprint.py`
copy under the module name `orchestrator.recording_fingerprint`, assert the
module resolves to the temporary copy, and run the two test files with the
selector `committed_sets_keep or negative_seed or parsed_the_same_way`. The
baseline copy carries the two new module-level names appended verbatim so the
readers still import -- the only difference under test is the fingerprint's own
numeric-only predicate. That adverse run produced 2 failures and 2 passes: the
negative-seed fingerprint case fails (the digest is unchanged) and the
warm-summary case fails with `DID NOT RAISE` (the warm cache serves the stale
view), while the committed-set fingerprint positive control and the
parser-agreement case pass unchanged. All four pass with the repair. No tracked
source was replaced during the negative run; the copies live only under a
temporary directory.

The two baselines differ in what they can show. The fingerprint module is
byte-identical at `9b333a76` and at this branch's `fd1f923c`, but the warm
per-loader summary cache did not exist at `9b333a76` -- it was added at
`8dd0576c` -- so the stale-warm-view leg is only observable against the current
`api/public_results.py`. Running the old fingerprint predicate inside the
current tree exhibits both legs in one control.

Record impact: post-record reader repair only. No replay, roster, manifest,
prompt, model or report bytes changed, and both committed sets fingerprint to
the values they already published.

Limitations: this settles which names count as recordings, not whether their
contents are trustworthy -- a name the shared pattern accepts still has to pass
the loader's own validation before it is served or counted. Non-canonical
duplicate pruning stays numeric-only by design, so a signed-spelling duplicate
is reported by the completeness check rather than deleted. Concurrent writers
and later filesystem changes remain outside the contract.

The follow-up correction gate ran on the tree at `93bf7d54`, the last commit before this record; the only edits after that gate are the checkpoint records in the commit that carries this paragraph. `bash scripts/check.sh` passed 7,173 Python tests, 20 optional skips and three expected failures; 514 frontend tests; strict typing on 467 sources; lint/format; four import contracts; document and generated-type checks; and the production build. `bash scripts/verify_samples.sh` verified all 300 canonical recordings (100 under `replays/samples/`, 200 under `replays/ml_corpus/`); all four `scripts/build_sample_report.py --check` runs are consistent; `pytest tests/orchestrator/ --collect-only` collects in a fresh interpreter; the API and static browser journeys passed (13 passed, 3 skipped). No committed recording, report, metric, weight or adoption verdict was rewritten, and every experiment candidate remains default-OFF.
