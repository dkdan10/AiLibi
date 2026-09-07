# Post-merge corrections and candidate readiness

This queue follows the merge of `codex/cleanup` into `main` with every candidate
default-OFF. Nothing here is authorized to spend on a live provider or to adopt
an experimental behaviour; both remain separate owner decisions. The supplied
follow-up review is preserved verbatim in
[the review archive](../audits/review-2026-09-06/REVIEW_REPORT_FOLLOWUP.md) with
its [appendix](../audits/review-2026-09-06/REVIEW_APPENDIX_FOLLOWUP.md). Review
claims require reproduction on the current tree before implementation; their
original severity labels and refuter votes stay intact.

## Ordered outcomes

1. **Disposition the review by id.** Every finding id in both appendices gets one
   stated disposition, and each of the first review's seven workflow
   recommendations gets adopt or decline with a reason.
   [Card](work/followup-review-dispositions.md). Documentation only; starts
   immediately and runs in parallel with everything below.
2. **Repair the renderer before any candidate measurement.** Witnessed vents and
   third-party sightings must outrank the observer's own routine rows, and the
   speaker-controlled account-uncertainty lines must be bounded, pinned by a
   budget-pressure fixture. [Card](work/evidence-renderer-salience.md). Until
   this lands every evidence-v2 arm evaluates a reasoner starved by its own
   renderer.
3. **Close the recorded-provenance gaps.** The observation-clock version in the
   provenance identity, a `view.json` hashed without its mtime, a memory guard
   bound to its meeting, the v3 policy re-decision as a profile option, and a
   cross-tree reconstruction so "verified" means something.
   [Card](work/recorded-provenance-gaps.md).
4. **Harden the accounts channel.** Forgeable section headings, one-speaker
   conflicts against innocents, speakers never placed by their own claims, the
   vent-only teammate firewall, and a reply prompt demanding a placement the
   schema lacks. [Card](work/accounts-channel-hardening.md).
5. **Build the fresh-model deduction instrument and manifest.** A frozen
   held-out design, an offline instrument on the public API, and an execution
   manifest whose owner-authorization fields stay empty.
   [Card](work/fresh-deduction-instrument.md). Planning and offline mechanics
   only; no live call is authorized by it. Its held-out inputs are frozen by a
   separate [freeze card](work/held-out-prefix-freeze.md): a preparer session
   that never runs an arm generates fifty proof-free prefixes from a
   preregistered seed band and commits their hashes, and the owner's merge of
   that pull request is the freeze.
6. **Close the nonblocking improvements.** Operator paths, two untested guards,
   derived doc counts, ledger rows and the concurrency window left open in the
   public-results cache. [Card](work/nonblocking-followup-improvements.md).
7. **Retire temporal v1 and evidence v1.** Four defects and one switch go with
   them. [Card](work/retire-temporal-evidence-v1.md). Blocked until an adopting
   record for evidence v2 exists.

**Sequencing.** Outcome 1 starts immediately and in parallel: it shares no source
file with any other card. Outcomes 2, 3 and 4 are serialised in that order,
because 2 and 4 both reach `agents/memory/store.py` and its meeting-layer
consumers, and because a channel hardened before its renderer is repaired is
measured with its own evidence evicted. Outcome 5 runs in parallel with 3 and 4 —
its instrument is new code — but its held-out arms may not be exercised until 2
and 3 have landed, which its Constraints state as preconditions. The freeze card
starts immediately and in parallel, shares no source file with any other card,
and must be merged before outcome 5's arms run. Outcome 6 fills
the gaps around the others and takes its `meetings/`, `api/` items after 4 and 3
release those files. Outcome 7 does not start before an adopting record for
evidence v2 exists; that record is not part of this plan.

## Ownership

One writer per file at a time. Where two cards name the same file, the earlier
outcome finishes and hands over before the later one begins.

| Writer | Files owned |
| --- | --- |
| Renderer worker (2) | `agents/memory/store.py`, `agents/memory/evidence_context.py`, `tests/agents/test_memory_rendering.py`, `tests/fixtures/memory_rendering/` |
| Provenance worker (3) | `eval/report_schema.py`, `eval/replay_walk.py`, `eval/balance_eval.py`, `api/schemas.py`, `api/replay_loader.py`, `api/public_results.py`, `scripts/build_sample_report.py`, `experiments/*_evaluation.py` |
| Meeting worker (4) | `meetings/public_accounts.py`, `meetings/manager.py`, `agents/strategic/prompts/qwen3_6_27b/`, the two candidate checkpoints under `audits/` |
| Evaluation worker (5) | the new instrument under `experiments/` and its tests, `audits/deduction-candidate/execution-manifest.md` |
| Preparer session (5, freeze) | `experiments/held_out_prefixes.py`, `tests/experiments/test_held_out_prefixes.py`, `audits/deduction-candidate/held-out/manifest.json`, and the `docs/artifacts.md` audits row inside its own pull request |
| Maintenance worker (6) | `scripts/run_tournament.py`, `scripts/_verify_samples.py`, `scripts/check_doc_facts.py`, `orchestrator/recording.py`, `tasks/README.md`, `tasks/review-ledger.md` |
| Documentation worker (1) | `docs/cleanup-dispositions.md`, `audits/review-2026-09-06/followup-correction-record.md` |
| Coordinator | `docs/artifacts.md` audits row, commits, cross-card handovers, this plan |

`docs/artifacts.md`'s audits row is coordinator-owned because three cards move
the `audits/` byte total the row promises, and `verify_ml_evidence.py` compares
that total against disk.

## What the owner must decide

| Decision | State |
| --- | --- |
| **Spending authorization for outcome 5** — provider, exact model, per-call token cap, total token budget (about 2.5 M projected), wall-clock deadline, dollar limit, and a cost statement even on flat-rate service | **Authorized by the owner's merge of #437 on 2026-09-07 (limits only)** — `featherless` / `Qwen/Qwen3.6-27B`, 2,048 output per turn and 1,024 per vote, 2,400,000 input / 200,000 output tokens hard stop, 4 h of model work within a 6 h elapsed deadline, $0.00 marginal against the flat-rate subscription with its fee stated, 4p1i with 3 living voters, sequential. [The authorization card](work/fresh-deduction-authorization.md) carries the values and the conditions; the manifest copies these values verbatim when the instrument card creates it, and no live call, pilot or retry is authorized until that manifest, the preconditions and the frozen held-out set exist. The held-out preparer and runner roles were ruled on 2026-09-07 (memo B.13): a preparer session on [the freeze card](work/held-out-prefix-freeze.md), a separate runner session on the instrument card, and the owner's merge of the freeze pull request as the freeze. |
| Adopting record for evidence reasoning v2 | Outstanding. Outcome 7 is blocked on it and does not create it. |
| Adoption of public accounts or attributed testimony, weighing the deliberate loss of the shared vent certificate | Outstanding. Outcome 4 hardens the channel; hardening is not evidence of better play. |
| The death-tick body handle on the default path — leave as-is and state it, or mask it equally in both arms | **Ruled with the authorization card (#437, 2026-09-07):** left as temporal v2 renders it in both arms, stated in the manifest, and asserted by a regex over the rendered prompts and the frozen prefixes (`body-p-\d+-\d+` absent); the prefix generator is bound to the same temporal version. Outcome 5's manifest records the outcome either way. |
| The probe-descriptor lifetime in `orchestrator/recording.py` — hold for the recording's lifetime, or keep the module's disclaimer | Outstanding, and framed as an explicit item in outcome 6 rather than left implied. |

## Verification and review

Each card runs its own targeted tests with a planted or perturbed failure first,
then `bash scripts/check.sh`, then `bash scripts/verify_samples.sh` over the 100
canonical recordings, then the four derived report checks
(`scripts/build_sample_report.py --sample-dir <set> --check` over
`replays/samples/4p1i`, `replays/samples/9p2i`, `replays/ml_corpus/4p1i` and
`replays/ml_corpus/9p2i`). Cards touching reader or orchestrator modules also run
`pytest tests/orchestrator/` in isolation, which has failed at collection before
when a test imported a `scripts/` module at module scope. Cards changing a served
DTO run the browser journeys with `cd frontend && npm run e2e`.

`scripts/verify_ml_evidence.py` is run for its offline half whenever `audits/`
bytes move. Do not claim its `--complete` gate: the archived ML evidence it needs
is not in this checkout, and a run without those bytes reports the same absent
rows every time. Gameplay-first and code-first reviewers freeze their findings
independently before synthesis. Archive historical findings without rewriting
their verdicts; a new reproduction note describes the implementation now.
