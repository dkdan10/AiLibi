# Cleanup review ledger

This ledger locates focused implementation commits and their evidence for the
owner's final Claude review. Cards own acceptance and current work status.
All rows remain **unmerged into main**. The owner supplied an independent Claude
review of `9b333a76`; the [original report and appendix](../audits/review-2026-09-06/README.md)
are preserved verbatim. Reproduced findings reopen the affected cards under the
[post-review plan](post-review-plan.md). Earlier verification and reviewer
attributions below are historical claims, not certification that the newly
reported defects were absent. No experiment is adopted by appearing here.

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
combined gate. Further carried findings remained active at that batch boundary. The final
batch below closes their dispositions without adopting experiments. Cards
retain commands, source identities and exact limitations.

The observation/portfolio batch also passed [GitHub CI](https://github.com/dkdan10/AiLibi/actions/runs/34006295048)
at exact head `ee7cbe7a319ba6ede5612be4a348d8a1cec71c79`.

## Final implementation and synthesis

| Slice | Implementation commit | Independent review and evidence |
| --- | --- | --- |
| Independent entitlement and corpus gates | `713f8163` | Portfolio-review agent approved real corpus/task/witness controls; isolated staged snapshot passed 16 tests. |
| Audio retirement and private spectator views | `9b0735ba` | Portfolio-review agent approved version compatibility and cached-private-data controls; isolated snapshot passed 134 Python checks, two golden/layout checks and 43 frontend checks. |
| Recorded reasoning/tactical experiments and offline measurements | `ee46d114` | Coordinator reviewed reasoning; workflow-redesign agent reviewed tactics; code-review agent reviewed shared provenance. Isolated snapshot passed strict mypy on 436 files and 235 selected tests. |
| Current model evidence and historical compatibility | `a0285760` | Code-review agent verified current refusals, historical/synthetic distinctions and scope metadata after the additional campaign-tier repairs. |
| Final integration, disposition ledger and completion | `1843b1b2` | All three agents reviewed their independent scopes; coordinator ran the complete gates below. |

Final local verification on 2026-09-06:

- `bash scripts/check.sh`: **6,775 Python tests passed**, 20 optional skips,
  three expected failures; **489 frontend tests**; strict mypy, Ruff/format,
  four import contracts, historical task/prompt checks and production build.
- `uv run pytest -m campaign -q`: **335 passed**. This explicitly runs the tier
  excluded by the ordinary gate. Temporary fake-provider fits are validation,
  not new research or published campaign evidence.
- `bash scripts/verify_samples.sh`: **100 canonical recordings verified**.
  The default suite also strictly scans both unchanged ML corpora through the
  real observation service: 200 games and 26,171 packet snapshots.
- Refreshed isolated-copy README and browser journey: **13 browser tests passed**,
  three intentional historical-media capture skips, zero retries. Both API and
  Vite processes were proved copy-owned. Fake seed-42 runs were byte-identical;
  static bundle generation and the documented HTTP smoke passed.
- `uv run python scripts/verify_ml_evidence.py`: 60 checks, **48 OK**, seven
  explicitly absent archived-evidence checks and five informational checks;
  zero failures. This is not the archive-restored `--complete` claim.
- Current experiment-source equality verified: reasoning’s 152 source files
  match its committed report; tactical fingerprint remains
  `d93f9d096e4b23572915e0ab128ee4ad266420bbbc266231eb7d49322d09bbd8`.

Retained logs: `/tmp/ailibi-cleanup-final-check-complete.log`,
`/tmp/ailibi-cleanup-final-all-campaign-complete.log`,
`/tmp/ailibi-cleanup-final-samples.log`, and
`/tmp/ailibi-cleanup-final-ml-complete.log`. The isolated-copy locator is
`/tmp/ailibi-public-clean-copy-path`; its `clean-final-verification.json` records
commands, server ownership, source identities and browser/offline logs.
Committed experiment artifacts and their commands live in
[audits/reasoning-evidence](../audits/reasoning-evidence/scorecard-plan.md) and
[audits/tactical-gameplay](../audits/tactical-gameplay/README.md).

The first integrated gate exposed 16 fixture, field-inventory and documentation
failures. Broader campaign checks exposed additional historical/current caller
mismatches. All were repaired before the successful complete runs. Independent
review also found typed-version forgery, misleading alive-time bounds, two
roster fingerprint races, cached private-memory exposure and a synthetic-probe
gate that accepted rebinding. Their positive and adverse controls now pass.
The static shared-link test waits for the selected meeting to reach the URL;
it does not hide failures with retries or sleeps.

## Original handoff boundary and remaining decisions

At the `9b333a76` handoff, all **26 cards** were marked done and all **49 roadmap priorities** had an implemented,
experimental or supported retained disposition. The
[current finding ledger](../docs/cleanup-dispositions.md) covers all 104 original
IDs, named close residue and the hardening routes. It does not relabel every
historical finding as a newly repaired defect.

The reasoning scorecard passes **36/36 mechanics cases** over strictly verified
inputs; it has no fresh-model correction or wrongful-ejection result. Tactical
screens cover **432 fake games**, 100 canonical folds and 3,550 coherent identity
interventions, including losses and the deleted inert reversal guard. All
experimental profiles remain OFF; the default opening body-ID timing limitation
remains until adoption. No historical recordings, weights, metrics or failed
adoption verdicts were rewritten.

The measured payload reduction remains scoped to its before/after captures.
Cold concurrent requests still reconstruct separately; no CPU, RSS, deployed
latency or model-quality improvement is inferred. Q1 search, Phase C co-evolution
resumption and a corpus-triggered refit are separate retained owner decisions.
No live provider, deployment, remote deletion or main merge occurred.

The subsequent Claude review required corrections; final merge remains pending. Local `main` and
`origin/main` remain `cfde4c8960a865eeaa39a004b2c33d302cbe4733`. Future work starts
from a new evidence-backed card or reopens an existing card whose acceptance
the review disproves. The current queue is in the task index.

## Maintenance correction checkpoint (2026-09-06)

The nine required review corrections, output-directory-wide recording
protection, unresolved usage accounting and source-bound summary caching are
verified on cleanup. The [correction record](../audits/review-2026-09-06/correction-record.md)
contains finding-to-card links, independent adverse reviews and verification.
The full gate passed 6,833 Python and 500 frontend tests, with 20 optional skips
and three expected failures; 100 canonical recordings and two API/static browser
journeys passed. Main, historical evidence and adoption decisions are unchanged.
This checkpoint completes maintenance and the summary-cache slice only. The
[remaining plan](post-review-plan.md) proceeds through experimental provenance,
evidence v2, attributed accounts and investigation before budgeted live evaluation.

## Post-review evidence and investigation checkpoint (2026-09-06)

The [authorized offline implementation](post-review-plan.md) is verified on
cleanup: actual evaluation identity and ballot entitlement; corrected temporal
evidence; common public accounts and attributed testimony; bounded replies;
typed missing-player search and independent contextual self-report. The new
accompaniment option was deferred because the existing follow-versus-patrol
comparison did not demonstrate useful later information. Existing historical
options and failed verdicts remain intact.

The [source-bound checkpoint](../audits/investigation-candidate/checkpoint.md)
contains 35 exact normal-policy games and 42 meeting mechanism controls sharing
the final source inventory, separate review methods, measured task costs and
semantic controls. It distinguishes changed submitted actions from changed
engine states, including discarded attempts. The earlier evidence/meeting
checkpoint remains committed at `e12b6180` with its own historical capture.

The final full gate passed 7,137 Python tests and 514 frontend tests, strict mypy
on 466 sources, lint/format, four import contracts, document/generated-type
checks and production build. Python has 20 optional skips and three expected
failures. All 300 historical recordings, four derived report checks and both
API/static browser journeys passed. No live provider was called.

Implemented and verified are complete for the offline cards. Independent bounded
reviews and final coordinator dispositions are preserved; external Claude review
is pending. The fresh-evaluation card completes preregistration only. The
[candidate handoff](../audits/investigation-candidate/candidate-handoff.json) lists
the still-required provider, token/time/cost authorization, held-out inputs and
decision rubric. It is not an execution manifest, adoption or merge permission.
Local and remote main remain `cfde4c8960a865eeaa39a004b2c33d302cbe4733`.
