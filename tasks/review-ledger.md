# Cleanup review ledger

This ledger locates focused implementation commits and their evidence for the
owner's final Claude review. Cards own acceptance and current work status.
All rows are **merged into main** at `8161689a` (PR 435, 2026-09-07); the merge
checkpoint at the end of this file records that landing. The owner supplied an
independent Claude review of `9b333a76`; the [original report and appendix](../audits/review-2026-09-06/README.md)
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

The subsequent Claude review required corrections; at that boundary the final merge was still pending. Local `main` and
`origin/main` were `cfde4c8960a865eeaa39a004b2c33d302cbe4733` then. Future work starts
from a new evidence-backed card or reopens an existing card whose acceptance
the review disproves. The current queue is in the task index.

## Maintenance correction checkpoint (2026-09-06)

The nine required review corrections, output-directory-wide recording
protection, unresolved usage accounting and source-bound summary caching are
verified on cleanup. The [correction record](../audits/review-2026-09-06/correction-record.md)
contains finding-to-card links, independent adverse reviews and verification.
The full gate at `144fc2e1` passed 6,833 Python and 500 frontend tests, with 20 optional skips
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
Local and remote main were `cfde4c8960a865eeaa39a004b2c33d302cbe4733` at that
checkpoint.

## Follow-up correction checkpoint (2026-09-07)

The owner's follow-up review of `fd1f923c` (archived verbatim as
[`REVIEW_REPORT_FOLLOWUP.md`](../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md)
and its appendix beside the first review) named four merge items and one
envelope decision. Each is repaired on cleanup with its own adverse control:
`14249a79` attests unresolved tournament usage instead of stranding the ledger
(NC4-1; `--attest-unknown-usage SEED`, refused with any cumulative cap, never
counts unknown usage as zero); `29b7bb4a` writes each sample report in the shape
`--check` compares (FU-2); `46e74f6d` shares one recording-filename pattern between
the fingerprint, the public completeness check, the loader, the verifier and the
manifest reader (FU-B-01; every committed fingerprint unchanged); `24a0fe6a` stamps
the agent-factory/substrate identity pair on the first tick row and the terminal
row only (FU-D2; state hashes identical to main on the checked seeds, tick rows
1..N byte-identical to main's, new recordings about 15% smaller than at
`fd1f923c`); `ad0f9b5a` binds the single-game cost read-back to the recorded game
identity (CONC-1). `241a5ca9` commit-qualifies the correction record's gate figures
to `144fc2e1`, archives the follow-up review, adds the review directory's index
and correction record to the checked link set, and recomputes the audit
inventory; `93bf7d54` queues the seven post-merge cards and
[`tasks/post-merge-plan.md`](post-merge-plan.md) as planning documents only.
The `6,833 Python tests` paragraphs the earlier checkpoint pasted into seven
cards now name the commit they describe.

The follow-up correction gate ran on the tree at `93bf7d54`, the last commit before this record; the only edits after that gate are the checkpoint records in the commit that carries this paragraph. `bash scripts/check.sh` passed 7,173 Python tests, 20 optional skips and three expected failures; 514 frontend tests; strict typing on 467 sources; lint/format; four import contracts; document and generated-type checks; and the production build. `bash scripts/verify_samples.sh` verified all 300 canonical recordings (100 under `replays/samples/`, 200 under `replays/ml_corpus/`); all four `scripts/build_sample_report.py --check` runs are consistent; `pytest tests/orchestrator/ --collect-only` collects in a fresh interpreter; the API and static browser journeys passed (13 passed, 3 skipped). No committed recording, report, metric, weight or adoption verdict was rewritten, and every experiment candidate remains default-OFF.

Local `main` and `origin/main` remain
`cfde4c8960a865eeaa39a004b2c33d302cbe4733`; all rows remain unmerged into main
at this checkpoint. No live provider was called. The branch-policy documents
(AGENTS.md, the ci.yml push trigger, tasks/README.md, docs/workflow.md and the
"unmerged" sentences above) are deliberately left for the merge's own
coordination record.

## Merge checkpoint (2026-09-07)

The cleanup branch merged into `main` as `8161689a`, a merge of
`cfde4c8960a865eeaa39a004b2c33d302cbe4733` and
`5fea577b89dacdbe66170769333a4d00e6296392` through PR 435. A merge commit rather
than a squash, so every branch SHA this ledger cites — including the public
source pin `5006a32f` the merge message names — stays reachable from `main`. The
last recorded full gate is the follow-up checkpoint's, run at `93bf7d54`: 7,173
Python tests, 514 frontend tests, 300 canonical reconstructions, 20 optional
skips and three expected failures. On the merge commit itself GitHub ran CI
(`34087394033`) and the Pages demo build (`34087394040`); both passed, and the
Pages run republished the demo bundle from the merged bytes.

Every row above advances to **Merged**; none advances to **Adopted**. The
delivery states are defined in [the workflow](../docs/workflow.md): the merge
establishes that the implementation is on `main`, not that any experimental
candidate is on. Every candidate remains default-OFF and the merge created no
adopting record. PR 431 became merged by reachability when its head landed in
`main`; PRs 432, 433 and 434 keep their inherited bases and were not closed,
retargeted or merged. `origin/codex/cleanup` is retained.

The branch-policy deferral recorded at the follow-up checkpoint above is
discharged here: AGENTS.md, `.github/workflows/ci.yml`, the task index,
`docs/workflow.md` and the "unmerged" sentences are corrected in the same commit
as this section, and delivery for new work is a `work/<card-slug>` branch and
one pull request per card. Local `main` and `origin/main` are `8161689a`.

## Post-merge queue checkpoint (2026-09-10)

Every card of the post-merge queue except the blocked retirement card is
implemented, independently verified and delivered as one pull request per card,
stacked in the order the plan serialised them. None is merged; the owner merges
each and retargets its successor to `main`.

| Order | Card | PR | Head | Base |
| --- | --- | --- | --- | --- |
| 1 | followup-review-dispositions | #439 | `cb788692` | `main` |
| 2 | evidence-renderer-salience | #440 | `94c76388` | `work/followup-review-dispositions` |
| 3 | recorded-provenance-gaps | #441 | `42095485` | `work/evidence-renderer-salience` |
| 4 | accounts-channel-hardening | #442 | `cfbf162f` | `work/recorded-provenance-gaps` |
| 5 | fresh-deduction-instrument | #443 | `cca2321c` | `work/accounts-channel-hardening` |
| 6 | nonblocking-followup-improvements | #444 | `60b14244` | `work/fresh-deduction-instrument` |

Each branch carries its predecessors by merge commit, so a PR's diff against
its base is its own card; the `docs/artifacts.md` inventory rows were recomputed
at every link and the frozen held-out set's `accepted` and `skipped` blocks are
byte-identical to `23a23c2d` on every head, with dated `dependency_restamps`
entries for the four commits that touched a hashed source. The retirement card
stays blocked until an adopting record for evidence reasoning v2 exists.

## Owner rulings (2026-09-07)

The two items deferred at the merge were assessed in
[the owner decision memo](owner-decisions-2026-09-07.md) and ruled on the same
day. #436 (`081aee15`) merged the branch-policy flip: delivery for new work is a
`work/<card-slug>` branch and one pull request per card, planning and contract
documents land on `main` directly, the `codex/cleanup` push trigger is gone from
`ci.yml`, and the merge checkpoint above is the ledger's record of that landing.
#437 (`0f49d8e6`) merged
[the authorization card](work/fresh-deduction-authorization.md): the owner
authorized the evaluation's limits — provider, model, per-call caps, token
budget, deadline, dollar limit and cost statement — and nothing else; no run,
pilot or retry is authorized until the renderer repair, the provenance gaps and
the execution manifest exist. The held-out preparer and runner roles were ruled
later the same day and are recorded below. PRs #432, #433 and #434 were closed on the owner's instruction after
each head (`26386914`, `55ed6d9a`, `62ba0162`) was confirmed reachable from
`main` through #435; they remain review records. Both merges were merge
commits, and each push to `main` republished the demo bundle.

Later on 2026-09-07 the owner ruled the two held-out roles (decision memo
B.13): a fresh preparer session, dispatched on
[the freeze card](work/held-out-prefix-freeze.md), builds a deterministic
generator, draws the first fifty proof-free prefixes from the band
preregistered in that card (seeds 3000 to 3999), commits the hashes without the
prefix bytes, and opens the pull request whose owner merge is the freeze; a
separate runner session, started after that merge, regenerates the set,
verifies the hashes and opens no prefix before the run. No run is authorized
by this ruling.

The freeze happened on 2026-09-08 (02:03 UTC): the owner merged #438 (head `f9b8f3bd`) as
merge commit `23a23c2d` after its four Codex review findings were fixed and
independently verified on the branch. `audits/deduction-candidate/held-out/manifest.json`
is the frozen record: fifty accepted seeds (3000 to 3057), eight skips, no
prefix bytes. Any later change to a hashed source follows the restamp rule in
`tasks/post-merge-plan.md`.

## Review disposition pass (2026-09-08)

Every finding id in the two 2026-09-06 appendices now has exactly one stated
disposition — as do the three ids the first review withdrew in its own section 9
without ever filing them in an appendix (`P1-2`, `C7b-9`, `G4-9`) — and each of
the first review's seven workflow recommendations has an adopt-or-decline with a
reason. The first review's ids are dispositioned in
[the cleanup disposition ledger](../docs/cleanup-dispositions.md); the follow-up's
own ids are in
[the follow-up correction record](../audits/review-2026-09-06/followup-correction-record.md),
which also carries three reproduced spot checks. Both are additive: the two
reports, the two appendices and the pre-merge correction record are unchanged.

The commits those dispositions name, all reachable from `main`, are the
finding-to-commit index for this pass. Thirteen commits carry it, in three
groups. Five are already listed by finding in the "Follow-up correction
checkpoint (2026-09-07)" section above — `14249a79` (NC4-1), `29b7bb4a` (FU-2),
`46e74f6d` (FU-B-01), `24a0fe6a` (FU-D2) and `ad0f9b5a` (CONC-1) — and are
repeated below with the further ids this pass attributes to them. Four more are
already named in this register but without a finding id: `241a5ca9`, `e12b6180`,
the merge `8161689a` and #436's `081aee15`. The remaining four — `cb3438ef`,
`b79fc1b7`, `700c0671` and `8dd0576c` — enter this register here. In full:
`cb3438ef` (C2-1, C2-4, C7b-2, GC-2,
M1-F1, C3-03), `b79fc1b7` (G5-1, GM-1, C2-6, CARD-01, C7a-2, GAP-FE-2, C5-7),
`700c0671` (G6-2, GAP-FE-1, G6-1, GAP-FE-3, P1-1, C5-1), `8dd0576c` (C6-1, C6-3,
M6-02), `e12b6180` (C1-01, G5-2, C4-2, TGE-1, TGE-2, G4-4, C7c-4, GL-3, C4-4,
C4-5), `14249a79` (NC4-1, FU-01, NC5-04), `29b7bb4a` (FU-2, NC4-5), `46e74f6d`
(FU-B-01, M2-F1), `24a0fe6a` (FU-D2, FU-APPX-5, NC4-4), `ad0f9b5a` (CONC-1),
`241a5ca9`
(P-02, FU-3), the merge `8161689a` (M5-02, and the published-source-pin filing of
CARD-02, by reachability of that pin; CARD-02's second filing, the stale
validation output in `work/temporal-observation-contract.md`, is retained rather
than repaired) and #436's `081aee15` (P2-6, C7a-6, P2-1, NC5-10). This is
a finding-to-commit index, not a second per-commit register: the per-commit rows
the follow-up's `P-10` asks for stay with
[the nonblocking card](work/nonblocking-followup-improvements.md).

No row above advances a delivery state, no candidate is adopted, and no live
provider was called.

## Post-merge commit register (as of 2026-09-10)

One row per post-review commit, which `P-10` asked for and the
disposition pass above deferred here. A post-review commit is every
non-merge commit reachable from this branch and not from `8161689a`, the
merge that landed the cleanup — the boundary the sections above stop at.
Rows cover every non-merge commit from `8161689a` to `7b25ad36`, which is the last row below; a commit after that tip is uncovered until the tip advances with it.

The tip now sits after `6bcd5e0f`, the merge that brought
`work/fresh-deduction-instrument` into this branch, so the covered range is both
lines of authorship and not just this card's. `5031e735` and `cca2321c` arrived
on that merge and have rows here. Their `Card` column derives as `—` because
git reads trailers only from a message's last paragraph and both put a blank
line between `Card:` and `Co-Authored-By:`; the card they name in their bodies is
`tasks/work/fresh-deduction-instrument.md`, and the column reports what `git log`
resolves rather than what the prose says. The residual is only the structural
one: the commit that writes the register cannot carry its own row, so it is
uncovered until a later commit advances the tip past it.

Nothing here is typed: `tests/scripts/test_review_ledger_register.py`
re-derives every sha, card and subject from `git log` over that range and
fails on a missing row, an invented row, a row out of order, a subject
that does not match the commit, or a coverage tip that is not an ancestor
of the branch. A commit cannot carry its own row, so the register is
advanced by the commit after the one it records.

| Commit | Card | Subject |
| --- | --- | --- |
| `e9c47c76` | — | coordination: record the merge of #435 and retire the cleanup-branch delivery policy |
| `90a410bb` | — | docs: correct the deduction card's output calibration and point it at the memo |
| `7b4c3daa` | — | docs: propose the fresh-model evaluation's authorization limits |
| `aafc947b` | — | docs: assess the open items deferred at the merge |
| `5c5138d1` | — | coordination: record the owner's rulings of 2026-09-07 (#436, #437 merged; #432-#434 closed) |
| `03814585` | — | coordination: complete the record of the 2026-09-07 rulings |
| `f9ce179c` | — | coordination: rule the held-out preparer and runner roles and open the freeze card |
| `86a919f1` | — | feat: generate held-out proof-free prefixes from a preregistered seed band |
| `f9d02ad2` | — | docs: freeze the held-out prefix digests and refresh the audits inventory |
| `2daa5612` | — | docs: complete the held-out prefix freeze card |
| `6f684642` | — | docs: state the restamp rule for the frozen held-out set and bind the runner to it |
| `0c8bc31c` | — | docs: collapse a doubled blank line in the instrument card |
| `92bec106` | — | fix: close the four review findings on the held-out prefix freeze |
| `3eb49dfc` | — | fix: close the certifying seam and stop overclaiming the frozen filter environment |
| `27e6d952` | — | fix: hash only the steps the engine executes and repair the freeze card's digests |
| `b6a4c3d6` | held-out-prefix-freeze | fix: state what dropping the report-tick steps did to the frozen set |
| `f9b8f3bd` | held-out-prefix-freeze | docs: correct the freeze card's bystander count and skip attribution |
| `201849fc` | — | coordination: record the freeze of the held-out set (#438 merged as 23a23c2d) |
| `7bcc79ed` | evidence-renderer-salience | fix: rank witnessed evidence above own routine in the evidence-v2 render |
| `af150ce0` | evidence-renderer-salience | chore: restamp the held-out dependency digests for 7bcc79ed |
| `0c5355a3` | evidence-renderer-salience | style: wrap the salience test's subject list to ruff format |
| `6ea91b69` | — | test: freeze a format-3 recording for the cross-tree policy check |
| `9cacd3fc` | evidence-renderer-salience | docs: close the evidence-renderer-salience card with its evidence |
| `3fae166e` | — | docs: disposition every 2026-09-06 review finding by id |
| `7cbf9786` | — | docs: index the disposition pass and close its card |
| `583eba5d` | — | feat: record the observation clock in the provenance identity |
| `e6b4b9c4` | — | fix: hash the investigation view without its filesystem timestamp |
| `414fa332` | — | fix: bind the live-vs-reconstructed memory guard to its meeting |
| `21640d87` | — | fix: make the v3 policy re-decision a declared profile option |
| `e26045bd` | — | docs: record the recorded-provenance-gaps results |
| `56d3e5fd` | evidence-renderer-salience | fix: count the caveat subjects the render actually drops |
| `73b7f53f` | evidence-renderer-salience | chore: restamp the held-out dependency digests for 56d3e5fd |
| `ab467228` | followup-review-dispositions | docs: correct the disposition pass's routing, counts and coverage claims |
| `bd6f05dc` | evidence-renderer-salience | docs: record the round-1 review corrections and what they enforce |
| `1aaae43e` | followup-review-dispositions | docs: make the round-1 correction proofs reproducible from the card alone |
| `17e929f4` | — | docs: correct the card's trio count and declare the shared inventory row |
| `34a8b8be` | — | docs: correct the counts and proofs round 1 falsified by writing them |
| `db6ffb9e` | — | docs: anchor the merge-tree conflict count so it reproduces on this tree |
| `00ac7fbb` | — | fix: state the withheld account subjects in the prompt the model reads |
| `b4352fb7` | — | fix: refuse a clock version that is not an integer at every provenance boundary |
| `0815333d` | — | chore: restamp the held-out dependency digests for 00ac7fbb |
| `59df8a9e` | — | docs: record the closeout round-1 corrections and what the render now enforces |
| `86e133e3` | — | docs: supersede the round-1 reserve text the closeout correction reverses |
| `864b18a1` | — | docs: name the commit the closeout gate was re-run on |
| `5bde0c95` | followup-review-dispositions | docs: correct the closeout findings this pass's own writes falsified |
| `76f6e777` | — | fix: close the closeout round's non-blocking findings and record the round |
| `af8d7f71` | — | docs: record the base-branch re-merge and its recomputed inventory rows |
| `115b46c5` | — | docs: state the held-out intersection per commit range instead of per worktree |
| `844fbe8d` | — | docs: make the closeout round's self-referential figures stop invalidating |
| `cb788692` | followup-review-dispositions | docs: make the counter that answers recommendation 2 print what is quoted |
| `6ba434fb` | — | docs: correct the ranking headline and pin the bands above the vent |
| `4d2396a3` | — | docs: withdraw a closeout-round-2 claim this worker cannot verify |
| `4e744f63` | — | docs: pin every card figure to the commit it was measured at |
| `b4555f39` | — | docs: make the base-tip claim a command rather than a sha |
| `c3a78366` | — | docs: qualify the withheld-notice guarantee to what the reserve enforces |
| `80fae3e5` | evidence-renderer-salience | docs: name every place the withheld-notice absolute still stands |
| `30fb9083` | — | docs: stop the pinning commit's own figure from drifting |
| `a8974d6f` | — | docs: count every place the withheld-notice absolute still stands |
| `5682ea2a` | — | docs: date the e2e row of the provenance card's verification table |
| `520d5a9b` | — | fix: fence account free text and match the reply ask to the schema |
| `5f496ef3` | — | fix: place a speaker by their own account and impeach a lone contradictor |
| `35e83271` | — | fix: extend the teammate firewall to every role-proving account shape |
| `a260f062` | — | docs: state the vent-certificate trade-off in both candidate checkpoints |
| `96a83a6a` | — | test: pin the vision hop the account comparison grants |
| `28742c2b` | — | docs: record the accounts-channel hardening results |
| `07b962a0` | fresh-deduction-instrument | feat: build the fresh-model deduction instrument on the public API |
| `87c4ef3d` | fresh-deduction-instrument | docs: bind the fresh-model evaluation's execution manifest |
| `87dfd918` | fresh-deduction-instrument | docs: close the fresh-deduction-instrument card with its evidence |
| `987f99b2` | fresh-deduction-instrument | docs: record the gate's own counts and the one load-sensitive failure |
| `4142f661` | — | fix: keep the widened kill firewall behind the account channel |
| `93eeb7d5` | — | fix: fence every line boundary and advance the account prompt revision |
| `f8140c32` | — | fix: repair the account comparison's derived rows and its belief fold |
| `113c046c` | — | docs: record the round-1 review corrections |
| `2dde0c91` | — | fix: enforce the manifest the instrument said it enforced |
| `5503f754` | — | docs: record the round-1 corrections and what they changed |
| `25351035` | — | fix: never pair two account rows read out of one artifact |
| `0769bee9` | — | docs: record the round-2 review corrections |
| `bfd5696b` | — | fix: count the meeting's own defaults and bound the work window in flight |
| `bb44f104` | — | docs: record the round-2 corrections and what they changed |
| `97cc8d62` | — | docs: pin the audits-diff command to the commit it was measured at |
| `3a02ede8` | — | fix: grade what a citation is about, not just that it is present |
| `360b277a` | — | docs: record the round-4 corrections and what they changed |
| `87005a14` | fresh-deduction-instrument | fix: landmine every grader and date every pre-run amendment |
| `44f0b99e` | fresh-deduction-instrument | docs: record the round-5 corrections and what they changed |
| `42ba4db1` | — | docs: recompute the instrument card's registry row on the integrated tree |
| `eddbb643` | — | docs: carry the merged head's tracked-file count into the prefix-secrecy scan |
| `927ceae0` | — | docs: say which round-6 gate rows were re-run at the branch tip |
| `6a6cd3ee` | — | docs: say what the branch's restamps are instead of denying they exist |
| `e945ae6a` | — | docs: argue the flaky-test note from the files that are actually untouched |
| `46a63e52` | — | docs: make the round-6 subsection describe the round it actually became |
| `444a47fd` | nonblocking-followup-improvements | fix: refuse a tournament report destination named like a recording |
| `db885271` | nonblocking-followup-improvements | fix: print the integrity rule code verify_samples already knows |
| `29393cda` | nonblocking-followup-improvements | fix: refuse a meeting whose recorded cutoff cannot be attributed |
| `d282dd06` | nonblocking-followup-improvements | chore: restamp the held-out dependency digests for 29393cda |
| `c8efd12a` | nonblocking-followup-improvements | test: pin the v2 entitlement rule against a vented observer |
| `f8a68519` | nonblocking-followup-improvements | test: pin the off-profile refusal of a task-activity account |
| `666dfbbb` | nonblocking-followup-improvements | feat: hold .env.example to the meeting-experiment registry |
| `54c623e8` | nonblocking-followup-improvements | fix: close the clear-and-install window in the public-results cache |
| `4a7c0071` | nonblocking-followup-improvements | docs: decide the probe-descriptor lifetime and pin what it leaves open |
| `5031e735` | — | docs: carry the merged head's dry-run figure into all three places it is stated |
| `51118004` | nonblocking-followup-improvements | feat: derive the task index's card counts from the cards themselves |
| `2d06e0b4` | nonblocking-followup-improvements | docs: register every post-merge commit and label the ownership section |
| `d210c04c` | nonblocking-followup-improvements | style: import the two registries from the modules that own them |
| `49df18ff` | nonblocking-followup-improvements | docs: close the nonblocking follow-up improvements card |
| `cca2321c` | — | docs: pin the instrument card's round-6 registry figure and refresh its PR summary |
| `9ae7d2a1` | nonblocking-followup-improvements | docs: register the commits the instrument merge brought into the ledger |
| `f23d53cc` | nonblocking-followup-improvements | fix: read the whole card-inventory breakdown, not the pairs in it |
| `7b25ad36` | nonblocking-followup-improvements | fix: refuse an exported assignment of a registered env switch |

No row above advances a delivery state, adopts a candidate or records a
live provider call.
