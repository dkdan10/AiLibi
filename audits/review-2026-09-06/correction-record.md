# Maintenance correction evidence

This record concerns the corrections built from `9b333a76` on
`codex/cleanup`. The supplied review and appendix are unchanged. The original
review's verification claims are separate from the reruns recorded here.

| Finding | Repair and adverse control | Owning card |
| --- | --- | --- |
| G5-1 | Historical projection omits absent attempt IDs, preserves genuine IDs and other historical null fields; checks all four committed reports. | [Aborted calls](../../tasks/work/aborted-meeting-calls.md) |
| C2-6 | Isolated orchestrator collection establishes its script import path; a fresh interpreter collects that directory independently. | [Aborted calls](../../tasks/work/aborted-meeting-calls.md) |
| C7a-2 | Generated type fidelity uses a genuinely completed game and includes finale, recap and decisive-event subtrees; removing those subtrees fails. | [Replay integrity](../../tasks/work/replay-integrity.md) |
| C2-1 | Replacement commits only after actual output bytes exist; zero-byte failures restore both prior bytes and prior absence, including genuine empty files. Audit-only partial evidence remains inspectable. | [Recording replacement](../../tasks/work/recording-replacement.md) |
| C7b-2, GC-2 | No empty report publication before an inspectable game. Missing, empty, unreadable or diminished attempt evidence cannot become zero spend or restore budget allowance. | [Tournament lifecycle](../../tasks/work/tournament-lifecycle.md) |
| C2-4 | Reports protect existing recordings and audits for unselected seeds, including path aliases. | [Report destinations](../../tasks/work/report-destinations.md) |
| G6-2 | Agent lenses show only the observer's own relevant ballot confidence, even after outcome reveal; a different voter's higher value cannot appear. | [Portfolio experience](../../tasks/work/portfolio-evidence-experience.md) |
| G6-1, P1-1, C5-1 | Stale scores have accurate explanations, media placements match the actual README, and the certified-proof percentage is described as guaranteed by construction. Removed links and fabricated placement claims fail. | [Portfolio experience](../../tasks/work/portfolio-evidence-experience.md) |
| C6-1, C6-3 | A per-loader, source-bound summary cache eliminates repeated replay walks. Same-mtime corruption fails after warming. Old timing captures are explicitly historical; fresh summary measurements identify their sources. | [Summary cache](../../tasks/work/public-results-cache.md), [historical capture qualification](../../tasks/work/replay-loading-performance.md) |
| NC4-1 (follow-up) | A recording removed by its own correct rollback no longer strands the ledger; `--attest-unknown-usage SEED` retains the attempt as unknown usage, never zero, and is refused alongside any cumulative cap. Pre-fix progress sidecars remain unrescuable because the CLI helper sources are part of their fingerprint. | [Tournament lifecycle](../../tasks/work/tournament-lifecycle.md) |
| FU-2 (follow-up) | The sample-report writer emits the shape `--check` compares, so the remediation it prints reproduces a committed legacy report instead of rewriting it; stamped recordings still receive the complete payload. | [Aborted calls](../../tasks/work/aborted-meeting-calls.md) |
| FU-B-01 (follow-up) | One recording-filename pattern for the fingerprint, the public completeness check, the loader, the verifier and the manifest reader; every committed fingerprint unchanged; the warm summary and a cold rebuild now answer alike. | [Public provenance](../../tasks/work/public-recording-provenance.md), [summary cache](../../tasks/work/public-results-cache.md) |
| FU-D2 (follow-up) | Recordings stamp the agent-factory/substrate identity pair on the first tick row and the terminal row only; the first tick row is authoritative, a contradicting later or terminal stamp and a stamp appearing after an unstamped first row are refused; no committed recording changes. | [Evaluation integrity](../../tasks/work/experimental-evaluation-integrity.md) |
| CONC-1 (follow-up) | A single-game run refuses to report the outcome or cost of a replay path another writer replaced; the read-back is bound to the recorded game identity. | [Recording replacement](../../tasks/work/recording-replacement.md) |

## Independent review

The report worker independently reviewed the recording changes and ran 123
focused tests. Its first review reproduced an absent-output rollback defect in
an actual `HeadlessGame`; the recording worker repaired it. Re-review restored
the exact prior directory state after zero-byte failure and cancellation and
left no blocking finding within ordinary-exception, single-writer scope.

The report worker separately reviewed the viewer changes, running 26 selected
frontend and 43 media/evidence-taxonomy tests. It checked own-ballot selection,
stale/absent score states and the wording against real data. It also reviewed
the summary cache and probed warmed analysis overrides, added/removed recording
membership and single-entry replacement. No blocking finding remained.

The viewer worker ran the actual API/static evidence journeys: two passed with
zero retries, using processes owned by those tests. The report worker checked
all four historical reports and the generated TypeScript fixture. These reviews
cover the stated correction scopes; they are not a fresh gameplay-quality review.

## Verification

`bash scripts/verify_samples.sh` verified all 100 canonical recordings. Targeted
summary checks passed 17 tests; the measurement harness passed four. Strict
typing, formatting and generated-type checks passed in the focused scopes.

The first combined check found an unindexed audit directory and a stale
committed-walk test exemption. Their fixes passed the relevant controls. The
second check passed 6,831 Python tests but failed two artifact-inventory checks:
the edited audit index changed its tracked byte total. No runtime test failed
in that run. The artifact inventory was updated and its two checks passed.

As of `144fc2e1`, the maintenance corrections' final `bash scripts/check.sh`
passed **6,833 Python tests**, 20 optional skips and three expected failures;
**500 frontend tests**, strict typing,
lint/format, import/document contracts and the production build. Four committed
reports are checked by the default suite; isolated orchestrator collection is
covered by its fresh-interpreter regression. The API/static browser checks and
all 100 canonical reconstructions also passed. Those figures describe the tree
at `144fc2e1` and are not a claim about any later commit: the runtime changed
again in `e12b6180` and `fd1f923c`, and the gate at `fd1f923c` is the 7,137
Python and 514 frontend run recorded in the
[review ledger](../../tasks/review-ledger.md). The follow-up corrections below
carry their own gate.

## Follow-up corrections (2026-09-07)

The owner's [follow-up report](REVIEW_REPORT_FOLLOWUP.md) reviews `fd1f923c`
and names four merge blockers plus two items to decide before merge. The
repairs below answer them; the sources they touch are the reopened cards' own.

**NC4-1 — a tournament interrupted before a seed's first recording row could
not be resumed.** The correct zero-byte rollback removes the output the
unresolved ledger attempt points at, so the recovery the error text demands was
unachievable. The repair keeps the attempt recoverable through an explicit
`--attest-unknown-usage SEED` attestation that retains it as unknown usage
rather than a silent zero, and both the error text and the lifecycle card carry
the recovery path. Adverse control: an interruption before the first seed's
first row must resume and retry, the attested attempt must never read as zero
spend, and the flag is refused while any cumulative cap is in force.

**FU-2 — the sample-report writer and the committed-report check disagreed on
the historical projection.** The writer emitted fields the projection excludes,
so the remediation command it printed would have rewritten a committed legacy
report instead of reproducing it. The repair routes the writer through the same
serialization the check compares against. Adverse control: regenerating a
committed set into a scratch directory must reproduce it byte for byte under
both the check and the committed-report assertion, while a stamped recording
whose complete payload is withheld still fails.

**FU-B-01 — the warm public-results summary served stale results for
negative-seed recording filenames.** The fingerprint and the loader's discovery
pattern disagreed about `replay-seed--3.jsonl`, so a mutated recording outside
the fingerprint's view was answered from a warmed summary. The repair derives
the fingerprint, the public completeness check, the loader, the verifier and
the manifest reader from one recording-filename pattern, leaving every
committed fingerprint unchanged. Adverse control: a set holding a negative-seed
recording, warmed and then mutated, must be refused rather than served, and the
warm summary and a cold rebuild must answer alike.

**FU-D2 — the identity stamp was written on every tick row.** Widening the
envelope on every row grew each recording measurably, no gate pinned the
tick-row key set, and the replay documentation still described the stamp as
belonging to the game-over record. The repair stamps the agent-factory and
substrate identity pair on the first tick row and the terminal row only, and
treats the first tick row as authoritative. Adverse control: a later or
terminal stamp that contradicts the first tick row, and a stamp that appears
after an unstamped first row, are both refused; no committed recording changes.

**CONC-1 — a losing concurrent writer reported the winner's game.** Two forced
single-game writers aimed at one replay path could both exit successfully while
one recording was destroyed, and the loser printed the surviving run's outcome
and cost as its own. The repair binds the post-run read-back to the recorded
game identity, so a run whose path was replaced refuses to report an outcome or
a cost. Adverse control: a replacement landing between the write and the
read-back must fail loudly instead of printing another run's figures.

The follow-up correction gate ran on the tree at `93bf7d54`, the last commit before this record; the only edits after that gate are the checkpoint records in the commit that carries this paragraph. `bash scripts/check.sh` passed 7,173 Python tests, 20 optional skips and three expected failures; 514 frontend tests; strict typing on 467 sources; lint/format; four import contracts; document and generated-type checks; and the production build. `bash scripts/verify_samples.sh` verified all 300 canonical recordings (100 under `replays/samples/`, 200 under `replays/ml_corpus/`); all four `scripts/build_sample_report.py --check` runs are consistent; `pytest tests/orchestrator/ --collect-only` collects in a fresh interpreter; the API and static browser journeys passed (13 passed, 3 skipped). No committed recording, report, metric, weight or adoption verdict was rewritten, and every experiment candidate remains default-OFF.

## Boundaries

No existing recording, report, metric, fitted weight or adoption verdict was
rewritten. No live provider, deployment or main merge occurred. Replacements
are exception-safe, not a two-file power-loss transaction. Summary measurements
cover sequential in-process work, not concurrent coalescing or deployed latency.
A progress sidecar written before the attestation flag existed cannot be
continued by it, because the command-line helper sources belong to the
fingerprint those sidecars are bound to. An attestation records that an
attempt's usage is unknown; it does not recover provider usage the interrupted
attempt never reported.
The remaining deduction experiments follow the [authorized plan](../../tasks/post-review-plan.md).
