# Cleanup review ledger

This ledger locates focused implementation commits and their evidence for the
owner's final Claude review. Cards own acceptance and current work status.
All rows remain **unmerged into main** and **awaiting the owner's final review**.
Independent implementation review is a separate earlier check. No cleanup
experiment is adopted by appearing in this ledger.

## Inherited foundation

| Card | Commit / review record | Local verification |
| --- | --- | --- |
| [Workflow pilot](work/workflow-pilot.md) | `ccf42166`, PR 431 | Results records the full gate and reviewer-found parser repairs. |
| [Budget accounting](work/budget-accounting.md) | `b64e29b5`, PR 431 | Results records injected provider failures and the full gate. |
| [Aborted calls](work/aborted-meeting-calls.md) | `26386914`, PR 432 | Results records retained attempt accounting and the full gate. |
| [Replay integrity](work/replay-integrity.md) | `55ed6d9a`, PR 433 | Results records corruption checks and canonical replay verification. |
| [Recording replacement](work/recording-replacement.md) | `62ba0162`, PR 434 | Results records paired replacement and failure-path verification. |
| [Cleanup delivery](work/cleanup-delivery.md) | `bbe8e2fc` | Full gate; CI runs on cleanup pushes. |

## First parallel implementation batch

| Card | Implemented | Verified | Independent review |
| --- | --- | --- | --- |
| [Report destinations](work/report-destinations.md) | `27885b10` | 97 focused tests; combined gate | Portfolio-review agent, no blockers |
| [Completed attempts](work/completed-meeting-attempts.md) | `9bfe86d0` | 255 focused tests; combined gate | Workflow-redesign agent, no blockers |
| [Evaluation integrity](work/evaluation-replay-integrity.md) | `bf2689f9` | 256 focused tests; combined gate | Code-review agent, no blockers |

Combined gate: 6,292 Python tests, 440 frontend tests, 100 canonical recordings,
strict typing, lint, formatting, contract checks, and build. These are recording
repairs, so experimental adoption is not applicable. The planning and index
commits are `45652c45` and `6d3c56e9`.

## Recording, reproduction, and maintenance batch

| Card | Implemented | Verified | Independent review |
| --- | --- | --- | --- |
| [Dependencies](work/dependency-advisories.md) | `172926f9` | Dated zero-finding audits; fresh install/build/browser; combined gate | Code-review agent |
| [Map traversal](work/map-traversal-contract.md) | `ae8761dd` | 107 focused tests; actual map mutations; combined gate | Portfolio-review agent |
| [Completion status](work/report-completion-status.md) | `c99a842c` | Stop/forged-outcome/paid-cost cases; historical census retained; combined gate | Workflow-redesign agent |
| [Tournament lifecycle](work/tournament-lifecycle.md) | `3d0a0a12` | Interruption/resume/retry/caps/deadlines and byte preservation; combined gate | Portfolio-review agent |
| [Public provenance](work/public-recording-provenance.md) | `996864c0` | Source/media fingerprints, stale-score rejection, clean-source journey; combined gate | Coordinator |
| [Audit fact gates](work/audit-fact-gates.md) | `a08f5727` | Exact-byte and rendered-link adverse cases; combined gate | Code-review agent |
| [Cleanup iteration](work/cleanup-iteration.md) | `5006a32f` | Rule move, ledger, next ownership; 37 workflow guards plus combined gate | Code-review agent |

Combined gate: **6,409 Python tests**, 20 optional skips, three expected
failures; **455 frontend tests**; strict typing, lint, formatting, import
boundaries, historical contracts/prompts, and production build. All **100
canonical recordings** verify. The clean-source browser journey passed 11 tests
with three opt-in media captures skipped; its source preceded the final narrow
post-meeting-stop correction, which has actual-runner regression coverage.

Independent review found and resolved missing run-fingerprint inputs,
line-ending changes during archival, post-meeting stop chronology, incompatible
playback verification labels, and Markdown links hidden across paragraph
boundaries. The first combined gate caught three consumer/test integration
regressions; all were fixed before the successful final gate. Cards retain
specific commands, decisions, and limitations. No experiment was adopted.

[GitHub CI](https://github.com/dkdan10/AiLibi/actions/runs/34002563135)
also passed at exact cleanup head `5006a32fb31b62e52ff6a29909baeba661fe86ac`.
Main remained `cfde4c8960a865eeaa39a004b2c33d302cbe4733`.

## Observation and portfolio batch

| Card | Implemented | Verified | Independent review |
| --- | --- | --- | --- |
| [Temporal observations](work/temporal-observation-contract.md) | `c59cfefe` | Source-time and entitlement controls; 210 live/reader memory snapshots; combined gate | Code-review agent |
| [Portfolio evidence experience](work/portfolio-evidence-experience.md) | `3a1e64ac` | Three real cases, five API/static journeys, clean-source browser checks; combined gate | Coordinator and code-review agent |
| [Replay loading](work/replay-loading-performance.md) | `3a1e64ac`, `e805ddd6` | Source-bound before/after captures, failed-usage preservation, exact references; combined gate | Portfolio-review agent |
| [Carried audit dispositions](work/carried-audit-dispositions.md), partial | `3a1e64ac` | Source-claim and routing mutations; 82 mandatory-gate execution controls | Code-review and portfolio-review agents |

Combined `bash scripts/check.sh`: **6,599 Python tests**, 20 optional skips,
three expected failures; **467 frontend tests**; typing, formatting, lint,
import/document contracts and production build. `bash scripts/verify_samples.sh`
passed all **100 canonical recordings**. The isolated first-commit snapshot also
passed 80 focused compatibility tests, one optional skip, and document facts.

Review found two additional temporal boundaries: opening descriptions exposed
the internal body ID, and frozen surrogate derivation accepted temporal inputs
without supporting their timing. Both have explicit compatibility treatment.
The default opening-prompt exposure remains until an adopting decision; the
implemented temporal repair is OFF. Initial meeting replay payloads shrink
71.7–86.2% in the measured cases; cold request coalescing remains unimplemented.
No CPU, memory, deployed-latency or model-quality improvement is inferred.

The first combined run found 13 integration fixtures; the next found one shared
copy assertion. All were fixed before the successful final gate. Browser
reproduction preceded narrow final copy/disclosure changes, which passed the
combined gate. Further carried findings remain active, and no experiment is
adopted. Cards retain commands, source identities and exact limitations.

## Current work

The [task index](README.md) names the next active ownership. Add implementation
commits only when delivered; distinguish verification and review from the
owner's pending final review, merge, and experimental adoption.
