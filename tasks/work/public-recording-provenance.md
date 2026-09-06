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
canonical recording or historical report bytes changed. Logs: `/tmp/ailibi-cleanup-
batch2-check-final.log` and `/tmp/ailibi-cleanup-batch2-samples.log`.

Independent review: Coordinator; source and asset identity, stale-score mutations, and clean-source results checked.
Implemented and verified for cleanup; the owner's final Claude review and merge
remain pending. This work does not adopt an experimental behavior.
