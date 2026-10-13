# Close maintainability and expansion decisions against measured evidence

**Status:** done

## Outcome

Roadmap 35, 47 and 49 receive explicit dispositions, and the independent gameplay
and code findings synthesize into one reviewable portfolio release. Completion
means justified implementation or retention, not enabling every experiment.

## Evidence

The core meeting manager and replay loader are large, but the concrete repairs
expose narrower responsibilities. Payload measurements show a useful delivery
improvement; repeated cold reconstruction remains measurable without an agreed
latency SLO. Earlier tally studies recorded tradeoffs and remained parked. The
current static/API portfolio path does not require another map, provider or
live deployment to demonstrate the project's claims.

## Acceptance

- [x] Document coherent extracted responsibilities, their callers and the
  existing import/determinism controls. Avoid a blanket module rewrite justified
  only by line count.
- [x] Retain vote-rule changes as parked until a separately measured reasoning
  improvement warrants a new comparison; cite the earlier study and limits.
- [x] State that maps/providers/deployment are retained at current scope, with
  concrete triggers for reconsideration. Do not invent an operational need.
- [x] Link complete roadmap/card dispositions and review evidence; distinguish
  implementation, verification, review, merge and experimental adoption.
- [x] Independent review and the complete project gate pass.

## Constraints

Follow docs/architecture.md. No new dependency, scheduler, campaign, provider
spend, recording adoption, remote deletion, deployment or main merge.

## Expected scope

Root owns the synthesis, architecture follow-through,
current disposition ledger, roadmap/index and final review ledger. Runtime source
belongs to the implementing cards.

## Record impact

None. Documentation and decision synthesis only; experimental source stays OFF.

## Validation

Inspect the extracted public contracts and callers, run import-linter and its
planted-leak controls, current strict replay/sample verification, document facts
and the full gate. Match the roadmap's 49 items to cards without double-crediting
historical fixes or treating a retained limitation as repaired.

## Results

The cleanup extracted concrete responsibilities at their existing boundaries:
source-tick delivery shared by live play/readers; independent witness geometry
beside privileged leak scanners; exact observation-reference projection in API;
public memory context inside agents; one bounded-reply selector inside meetings;
coherent reset inside the engine; and a closed experiment contract in the
orchestrator. Current model provenance has its own training helper. Each has
actual callers and focused semantic controls. Four existing import-linter
contracts and the planted transitive-leak test remain the architectural gate.
A line-count target would not justify dismantling the remaining manager/loader.

The measured payload work reduced initial transfer substantially; its card also
reports peak process RSS and repeated concurrent misses without claiming an SLO
or CPU improvement. Four same-key cold requests still produce four walks.
Single-flight caching is retained for a future demonstrated latency need with
explicit cancellation/error ownership; it is not part of this release.
The RNG reseed repair already exists; defensive immutable-state mapping copies
remain until a measured alias-safe alternative earns their replacement.

Roadmap 47 stays parked. The earlier
[tally study](../../experiments/lab/report-tally-lab.md) found that relaxing
abstention could add both correct and innocent ejections, and explicitly warned
that per-meeting counterfactuals did not propagate changed game states. These
historical tradeoffs are not a new current quality measurement. The new reasoning
mechanics do not supply new model judgments, so the stated trigger for changing
the vote rule has not occurred. Keep the production tally unchanged.

Roadmap 49 retains the canonical map, existing providers and current static/API
publication path. New maps need a gameplay question and traversal contract;
a provider needs a model-quality or operational requirement; live deployment
needs an audience, hosting/security scope and operational ownership. No such
need is established by the cleanup findings. The existing reproducible static
experience is sufficient for this portfolio review; deployment and main merge
remain the owner's later actions.

The current disposition ledger preserves the independent gameplay/code source
registers before combining them. The release story is now accurate records,
inspectable claims and bounded evidence checks, with measured experiments and
negative results kept visible. Independent review approved the synthesis and complete routing after adding
Phase C co-evolution resumption as a separate retained owner decision from Q1
and a conditional refit. Final combined checks passed, as recorded below.

Final cleanup verification on 2026-09-06: `bash scripts/check.sh` passed
6,775 Python tests (20 optional skips, three expected failures), 489 frontend
tests, strict typing, lint/format, import/document contracts and production
build. The entire offline campaign tier, `uv run pytest -m campaign -q`,
passed 335 tests. All 100 canonical recordings passed
`bash scripts/verify_samples.sh`. Independent reviews have no remaining blockers.
The [review ledger](../review-ledger.md) records commands, integration repairs,
source-bound measurements and compatibility limits. Main merge and experimental
adoption remain the owner’s separate decisions.
