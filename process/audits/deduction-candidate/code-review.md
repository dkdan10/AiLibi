# Independent review of deduction evidence and verification

**Review date:** 2026-09-06. **State:** findings recorded before gameplay-review
synthesis. This is a bounded code-first review of the current cleanup work,
not a fresh-model evaluation or adoption decision. The coordinator will bind the
final matrix capture to its actual source inventory after remaining runtime work.

## Scope and method

The review traced `advance_tick` action order through the v2 observation reducer,
independent entitlement oracle, memory ingestion, travel assessment and recorded
API reconstruction. It also reviewed report identity and ballot verification.
Adverse probes used actual seeded games, legal scripted actions and deterministic
providers. Mutations changed claimed evidence or recorded ballots while retaining
the underlying source states; no live provider, historical rewrite or gameplay
rule change was used to produce a passing case.

The report worker reviewed the observation worker independently. The meeting
worker independently reviewed the report worker's ballot and provenance changes.
The findings below precede any synthesis with a gameplay-first review.

## Findings and corrections

### A matching tally did not establish a valid ballot set

The initial `ReplayIntegrityValidator.check_advance` recomputed the recorded
outcome at the applicable cutoff but did not bind voters or targets to the living
roster. A genuine four-player recording still received `outcome_verified=True`
after duplicated, missing or foreign voters, a dead target, or a self target.
Low confidence or unchanged plurality kept the outcome skipped, leaving all
engine hashes and the outcome comparison unchanged.

The correction requires exactly one ballot from each reconstructed living player
and a normalized target of `SKIP` or another living player before tallying.
Seven actual-record controls additionally cover an empty ballot list and a
foreign target. Each explicitly demonstrates that the forged ballot set still
has the original tally and engine hashes, then requires refusal by both the
strict report and API readers. The independent reviewer reran the five retained
original probes and confirmed both readers now refuse every one.

The existing recorded-cutoff tests separately retain a genuine custom cutoff,
distinguish the named legacy compatibility cutoff, and reject altered targets,
confidence or cutoff with unchanged state hashes. Rewritten authored targets
remain provenance; readers do not silently normalize malformed stored ballots.

### The v2 snapshot scan did not enforce its timing or channel contract

Starting from a genuine v2 snapshot for p-2 in canonical seed 1, the semantic
scanner accepted removal of the v2 stamp, an arbitrary tick of 777, and invented
task activity on visible p-4 despite an empty source-event list. The event-batch
oracle was correctly checking its own channel, but this separate snapshot path
could reintroduce source-clock ambiguity or duplicate action evidence. Recorded
snapshot contexts also omitted their temporal version.

The correction carries the exact version into those contexts, binds the v2
snapshot version, tick and own position to source state, and refuses action,
movement or own-kill evidence in a v2 snapshot. It also refuses a v2 packet under
a non-v2 context. Paired controls preserve a genuine snapshot and reject the
version, clock, invented task and self-position mutations.

The underlying v2 reducer retains actor-private task receipts and gives other
observers only visible task activity. Dense observation order is assigned after
entitlement filtering; hidden actions do not reveal their count through source
IDs. The independent oracle reconstructs positions, life, vents and visibility
without calling the reducer or its visibility helper. Movement metadata retains
a separate legacy witness check. These are enforcing mechanisms, not a claim
that matching live and reader output alone proves privacy.

### Public regrouping was mistaken for impossible walking

A supported combination of evidence v2 and `hub_with_grace` reset produced a
false allegation without any dishonest testimony. In an actual legal run, p-2
and p-4 walked CAFETERIA→UPPER_HALL at tick 0 and →ADMIN at tick 1. P-3 called an
emergency from CAFETERIA at tick 2. After a skipped meeting and public regroup,
p-2's evidence claimed that ADMIN at tick 2 could not be reconciled by walking
with CAFETERIA at tick 3. It ignored the public relocation.

Live and recorded reconstruction now ingest the actual public regroup after a
resumed reset. V2 memory retains the announcement, and travel checks recognize
an interval crossing that boundary. The new real-run regression has two meetings:
removing only the public regroup rows recreates the erroneous allegation;
retaining them prevents it; a later impossible scripted account still receives
a conditional travel warning. The next meeting's API-rendered opening memory
matches the actual provider input. A reset does not make every later interval
uncheckable or certify a claimed past alibi.

### Served report identity needed its own source binding

Independent review changed a report's game identity and matching aggregate group
from custom experimental behavior to scripted, absent-config behavior. The
derived report remained internally consistent while the underlying replay
metadata still named the original profile. Rebinding only outcome verification
therefore left a misleading provenance claim in the served report.

The coordinator owns the correction to rebind identity from validated replay
metadata and rebuild aggregate groups. Its independent source-forgery regression
and shared project gate remain required integration evidence; this note does not
substitute the earlier internally consistent group check for that source check.

## Verification available at this review point

- `.venv/bin/pytest tests/orchestrator/test_experimental_evaluation_integrity.py tests/orchestrator/test_replay_integrity.py -q --tb=short`: 55 passed after the ballot correction. Strict mypy and Ruff passed on those changed consumers.
- `.venv/bin/pytest tests/observation/test_temporal_v2.py tests/orchestrator/test_temporal_evidence_v2.py tests/orchestrator/test_temporal_delivery.py -q --tb=short`: 58 passed after the snapshot correction.
- `.venv/bin/pytest tests/orchestrator/test_public_regroup_evidence.py -q --tb=short`: one real-run regression passed, including the omitted-boundary negative control and later-account/API parity checks; strict mypy passed.
- All four `scripts/build_sample_report.py --sample-dir replays/{samples,ml_corpus}/{4p1i,9p2i} --check` combinations passed after the ballot correction. The four paths are separate commands, not one literal brace-expanded argument. No historical report or replay was rewritten.

## Remaining limits

Engine actions remain sequential. Both crossing orders are tested, but different
orders can legitimately yield different observations. The review does not claim
identifier-invariant simultaneity or alter certified vent rules.

The scenario factories and speech are scripted controls. They establish evidence
transport, conditional reasoning inputs and protocol behavior, not a model's
ability to infer, deceive, correct itself, investigate or vote well. A scenario
with no observed vent may still contain a witnessed kill; direct-proof strata
must check both. A listener's entitlement must remain distinct from an offline
judge's hidden truth.

The shared full gate, final source-bound matrix, normal-policy investigation
work, independent gameplay findings and subsequent synthesis are separate
deliverables. No runtime quality, experimental adoption or merge verdict follows
from this review note.

## Dated integration disposition — 2026-09-06

The report source-binding correction now passes the independent valid-source
forgery, missing-source and invalid-source regressions. Valid identity and groups
are rebuilt from verified recording metadata; absent or invalid sources cannot
retain claimed identity. The coordinator's final project, browser, canonical and
source-bound matrix checks are recorded in [the checkpoint](checkpoint.md). This
appendix preserves the earlier review's findings and scope.
