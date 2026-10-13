# Accusation, answer and vote from attributed accounts

**Status:** done

## Outcome

Implement the fourth outcome in [the post-review plan](../post-review-plan.md)
as an unadopted comparison: both roles can state the same kinds of public
accounts, listeners retain who said what, and a consequential new accusation
can receive one bounded answer before voting. A listener's own observations
remain reliable; another speaker's private records never certify that speaker's
account to the listener in the new attributed mode.

## Evidence

The [owner-supplied review](../../audits/review-2026-09-06/REVIEW_REPORT.md),
sections 8 and 10, describes role-dependent account precision, silent kill
testimony and missing answers. The existing
[reasoning experiments](reasoning-evidence-experiments.md) retain earlier
FINDING verdicts and implement a separately selectable one-reply mechanism.

Current `MeetingManager.run` supplies private vent, sighting and movement
records to contradiction detection; resulting bands reach prompts and shared
belief updates. The corroboration summary can also tell listeners whether
another speaker's record supports their story. Hiding a label alone therefore
does not remove certification. Default impostor templates request empty
observations while crew templates expose structured accounts. The testimony
reducer drops task activity; rotating pretend tasks correctly never produce
completed-task memory. Reproduce these paths before changing them.

## Acceptance

- [x] Bind independent `public_account_version=1` and
  `attributed_testimony_version=1` selections in the immutable meeting profile
  and recorded configuration. Omitted means OFF. Reject unknown/coerced
  versions, inconsistent stamps and incompatible served templates before
  provider work. Preserve exact OFF and existing version-1 recording bytes.
- [x] Give both roles the same public vocabulary for whereabouts, task
  activity, player sightings, witnessed movement, body discovery, vent and kill
  accounts, alibis, accusations and corroboration. Keep role-private objectives
  private. New templates have explicit versions; legacy templates remain exact.
- [x] Validate account structure, public identities and clocks without treating
  a speaker assertion as an engine fact. Private observation references resolve
  only against their owner's typed records. A claim inconsistent with private
  history is not automatically rejected or publicly labeled false; conflicting
  public accounts remain available for analysis. Preserve source attribution
  and do not infer event time from identifiers.
- [x] Retain actor-owned task-attempt history with task, room and time through
  live play and reconstruction. A planned, interrupted or rejected attempt must
  not become successful completion; pretend activity never creates completed
  work or changes the task counter. Public activity claims do not reveal task
  ownership, role or a private completion certificate.
- [x] Analyze shared accounts from public transcript, roster and topology only
  in attributed mode. Neither detector bands, corroboration summaries, prompt
  text nor scalar belief updates may reveal another speaker's private
  grounding. Reported kill/vent content never becomes a listener's first-hand
  observation. The observer's own entitled observations remain usable.
- [x] Prove noninterference through the real manager and post-meeting fold:
  hold public speech and one listener's observations fixed, perturb a different
  speaker's private grounding, and require identical listener prompt inputs,
  public analysis and belief updates. Plant a private-grounding read and show
  failure. A separate positive control changes that listener's own observation
  and demonstrates its legitimate effect without changing others' knowledge.
- [x] Reuse `bounded_rebuttal_version=1` independently. Test a late new
  allegation, repeated/hearsay accusations, an already answered charge, dead
  targets and no charge. At most one extra reply uses existing call accounting,
  retry, cancellation and deadline rules; it cannot recurse into another reply.
- [x] Exercise the repaired four-player canonical-map case through actual
  observations, memory, manager, recording and reader: unseen Admin kill,
  reporter departure and return around the kill, no witnessed kill or vent, and a
  late charge against the reporter. Include legal-route, contradictory-account
  and insufficient-timing variants. Conditional walking feasibility is not
  innocence or role proof; fixed provider responses establish mechanics only.
- [x] Compare common-account and attributed modes independently before their
  combination, holding other candidate settings explicit and constant. Strict
  readers reconstruct partial and completed runs using recorded settings;
  historical instruments and baseline-only training reject unsupported modes.
  Source-bound evidence distinguishes these experimental controls from the
  certified baseline and retains every earlier failed verdict.
- [x] Independent review attempts the private-record plant and genuine
  live-to-reader cases; targeted checks, all canonical reconstructions and
  `bash scripts/check.sh` pass. Record unresolved quality questions and the
  later fresh-evaluation decision point without claiming adoption.

## Constraints

Follow [architecture](../../docs/architecture.md), especially layering,
structured memory, observation entitlement and the substrate ladder. The
maintenance gate is complete. Independent meeting work may run alongside the
evaluation/clock repairs; end-to-end acceptance waits for their handovers.
Use the actual canonical four-player map,
deterministic scripted provider responses and temporary outputs. No new map,
role, dependency, training, live call, historical re-recording or adoption.

Certified vent behavior remains the baseline. Do not reinterpret
`testimony_shapes`, `impostor_roll_call`, `corroboration_discipline` or
`reporter_reasoning`, or revise their historical decisions. Initially reject
their overlapping combinations with the new account profiles rather than
silently composing incompatible templates or private-record summaries.
Clock-repaired experimental controls are labeled separately from certified
baseline controls. New behavior remains OFF pending the plan's separately
authorized, preregistered fresh evaluation; rejection retires the candidate
unless a further comparison is explicitly authorized.

## Expected scope

One writer per file, with these handovers before implementation:

| Owner | Scope and required interface |
| --- | --- |
| Meeting worker | `meetings/schemas.py`, manager, transcript/corroboration reducers, render contracts, a public-account analysis helper, strategic prompt loader/new templates, and focused tests. Reuse `meetings/rebuttal.py`. Public analysis accepts transcript, roster and public topology, never participant-private record maps. |
| Coordinator | `meetings/evidence_profile.py`, `orchestrator/experiment_config.py`, `game.py` and `replay.py`: frozen versions, renderer identity, compatibility preflight, stamped transport and production integration. |
| Observation/memory worker | Actor-owned activity receipt, temporal delivery and memory ingestion/rendering. Agree an engine-free receipt and separate attempted activity from completion before either worker edits shared memory code. |
| Coordinator-assigned reader worker | API/eval reconstruction, baseline-only training refusals and any directly necessary generated DTO/viewer follow-through after schema handoff. No separate inference of modes from ambient environment. |

The coordinator supplies a version-2 experiment envelope for the new fields
while retaining exact version-1 encoding and interpretation. Both versions are
optional integer literal 1 in the meeting profile. Freeze profile and prompt
selection together; repeat enabled configuration on tick and terminal rows.
The public-account worker supplies narrow pure reductions taking the captured
profile, so live and reader paths use identical content and belief semantics.
Do not pass empty private maps to the existing grounded detector as a substitute
for the new public analysis: its empty-map behavior is not this contract.

## Record impact

Lever-gated until an adopting record. New prompt, detector, memory and reply
combinations are explicitly versioned experiments. Existing recordings, prompt
bytes, fitted weights, scorecards and experiment verdicts remain unchanged.
This card establishes executable mechanisms and privacy semantics, not improved
model decisions. Adoption or rejection requires the later fresh-evaluation
record and its authorized run budget.

## Validation

Run focused manager/schema/renderer, reported-memory, profile-binding and
replay/API/eval tests. Cover missing/foreign private references, all public
account kinds, attempted versus completed tasks, partial recordings, invalid
versions and the noninterference plant. Record exact new test paths and commands
in Results. Use the actual four-player pipeline and verify emitted witnesses,
not only hand-built transcript fixtures. Pair OFF prompt/replay byte controls
with independently selected ON controls; measure calls and returned tokens.

The coordinator runs `bash scripts/check.sh` and
`bash scripts/verify_samples.sh` after handovers and independent review. Any
new public projection receives focused frontend and live/static browser checks.

## Results (implementation awaiting combined verification)

The meeting implementation follows [layering and the observation boundary](../../docs/architecture.md#layering):
the new public analyzer accepts only transcript, public roster and public walking
topology. Account validation checks public identities, map/task names and clocks;
it deliberately accepts potentially false but well-formed statements. No private
witness maps enter attributed analysis. All resulting route conflicts remain
conditional, weak comparisons; tick-only speech allows one additional within-tick
move and cannot exclude an unseen vent. Same-tick adjacent placements have an
honest-walk control.

The explicit Qwen3.6 account templates give both roles the same account menu,
preserve private objectives, and keep independently selected common-account and
attributed-only arms. Four legacy overlaps are refused. Baseline renderers and
their golden tests remain unchanged. Public task activity carries task, room and
interval; the persistent reducer retains speaker and transcript source without
certifying completion. The directly necessary viewer union handling labels it
"claimed task activity" and sorts its interval without inventing a point timestamp.

`tests/meetings/test_public_accounts.py` exercises the actual manager, retries,
deadline/default handling, cancellation, bounded replies and pure post-meeting
reductions. Its public-context and private-grounding plants prove those guards
can fail. `tests/orchestrator/test_public_account_scenario.py` adds real seeded
actions and recordings using the shared four-player scenario: two meetings at
ticks 5 and 8 establish live-to-reader post-fold noninterference. Perturbing only
p-3's private vent-grounding accessor changes neither p-2's prompts, public
meeting artifacts, scalar beliefs nor second-meeting API memory. A planted
private detector produces the specifically asserted artifact mismatch. Reported
vent/task content stays attributed; actual own kill/vent observations retain
their direct-evidence belief through API reconstruction. Three independently
selected profile combinations complete and validate. The actual late p-3 charge
against reporter p-2 adds exactly one reply and one call before identical SKIP
ballots when the separate bounded-reply arm is enabled.

Direct runner construction now validates the actual bound account callables,
captured profile values, template filenames and bundled environment, in addition
to version labels. Legacy/lambda renderers, a wrong environment and mixed or
coerced arm bindings cannot claim the new profile; OFF still accepts the original
custom-renderer extension point. This is constructor compatibility validation,
not protection against arbitrary later Python monkeypatching.

Focused verification:

- `.venv/bin/python -m pytest tests/orchestrator/test_public_account_scenario.py tests/orchestrator/test_temporal_evidence_v2.py tests/meetings tests/agents/test_public_account_prompts.py tests/agents/test_prompt_loader.py tests/agents/test_strategic_prompts.py -q --tb=short`: **1,481 passed**. The shared observation worker owns the real scenario and temporal tests; all outputs use temporary directories and deterministic scripted responses.
- Ruff check/format and strict mypy passed for the 11 owned Python source/test files: meeting schemas, manager, transcript, render contract, public-account helper; strategic prompt loader/package export; public-account manager/prompt/scenario tests; and the existing reasoning-profile version tests.
- `npm run tsc:check` and targeted ESLint passed for `ObservationLine`, its new tests, `MemoryPanel`, and the observation-union fixture in `contradictions.test.ts`.
- `npm test -- src/ui/ObservationLine.test.tsx src/lib/contradictions.test.ts src/components/PrivateReasoning.test.tsx`: **28 passed**. `npm test -- src/lib/copy.test.ts`: **239 passed**.
- Final `.venv/bin/python -m pytest tests/agents/test_public_account_prompts.py tests/orchestrator/test_public_account_scenario.py -q --tb=short`: **34 passed**, including the constructor-binding additions and three independently reproduced report-identity regressions. The latter first failed on forged valid-source identity, missing source and invalid source, then passed with the coordinator's source rebinding. Targeted strict mypy and Ruff remained green.

No provider-quality improvement, adoption, fresh evaluation or historical
re-recording is claimed. Actor receipts and live/replay profile transport are
coordinated dependencies documented in their own cards. Independent review,
the coordinator's final combined gate, canonical checks and final browser
follow-through remain pending; this card remains active.

## Results

The [source-bound checkpoint](../../audits/deduction-candidate/checkpoint.md)
records implementation decisions, separate review findings, synthesis, measured
denominators, the full project gate, all 300 reconstructions, four historical
report checks and both browser journeys. Its measurement binds the exact runtime
source and frozen inputs. Architecture references are Layering, Enforced
boundaries and Explicit cleanup experiments. All acceptance work for this card
has passed; earlier provisional Results above record the state at their writing.
No default adoption, main merge, historical re-recording or live spending occurred.
