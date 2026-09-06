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

The final `bash scripts/check.sh` passed **6,833 Python tests**, 20 optional
skips and three expected failures; **500 frontend tests**, strict typing,
lint/format, import/document contracts and the production build. Four committed
reports are checked by the default suite; isolated orchestrator collection is
covered by its fresh-interpreter regression. The API/static browser checks and
all 100 canonical reconstructions also passed. No runtime sources changed
after this successful gate; subsequent edits recorded these results.

## Boundaries

No existing recording, report, metric, fitted weight or adoption verdict was
rewritten. No live provider, deployment or main merge occurred. Replacements
are exception-safe, not a two-file power-loss transaction. Summary measurements
cover sequential in-process work, not concurrent coalescing or deployed latency.
The remaining deduction experiments follow the [authorized plan](../../tasks/post-review-plan.md).
