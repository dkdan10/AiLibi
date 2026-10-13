# Investigate missing players without inventing evidence

**Status:** done

## Outcome

Implement the fifth outcome in [the post-review plan](../post-review-plan.md):
a crewmate can pursue a short, typed search based on its own last-known sighting,
retain or cancel that plan across meetings, and resume ordinary work. Compare
bounded accompaniment and context-dependent impostor self-report independently.
All candidates remain OFF; finding someone later never certifies a past alibi.

## Evidence

The [independent review](../../audits/review-2026-09-06/REVIEW_REPORT.md), coverage
row 22, identifies the missing investigation disposition. Current
`agents/tactical/experimental.py` changes finished-crewmate idling to patrol or
recent-player accompaniment. It does not create a search objective and returns
the anchor while tasks remain. Its `self_report` option reports any visible
body, without comparing context. Preserve those existing comparisons and their
earlier verdicts.

`agents/memory/working.py` has untyped goal/path scaffolding and a last-seen cache;
the production cache writer runs during prompt rendering. Tactics must not treat
that render-dependent cache as fresh observation state. The repaired temporal
event stream and [attributed accounts](attributed-public-accounts.md) provide the
source identity and clock foundation, not a private truth certificate for speech.

## Acceptance

- [x] Add immutable, independently recorded `investigation_version=1` and
  `contextual_self_report_version=1` selections. Introduce an accompaniment
  version only after search demonstrates distinct useful information.
  Require the clock-corrected evidence profile. OFF and old experiment envelopes
  preserve their exact behavior and encoding; reject coerced versions, mixed
  stamps and conflicting old tactical options before recording/provider work.
- [x] Derive search candidates from the agent's own typed sightings/movements,
  current observations and public death announcements. Record the supporting
  observation identity, its actual source time, target, last-known room, start,
  expiry and bounded visited-room set. No raw engine position, hidden living
  status, another speaker's private record, inferred death time or rendered-text
  parsing may influence selection. A missing player is an uncertainty to inspect,
  not an accusation or belief lift.
- [x] Execute a deterministic bounded plan. Version-1 constants are
  four ticks without a fresh sighting, at most twelve ticks of source age, six
  elapsed ticks per search and three inspected rooms. Start at the last-known
  room, then unvisited adjacent rooms with deterministic distance/room tie-breaks.
  Record these as mechanics parameters before comparison; changing them requires
  a new version or an explicit preregistered revision.
- [x] A plan may interrupt ordinary task travel, but it never interrupts a task
  already progressing. Visible-body reporting, witnessed-danger handling and
  urgent sabotage repair take precedence. Expiry advances during interruptions;
  completion, reacquisition, new public death, unreachable paths and exhausted
  room allowance end the plan. Repeated decision calls on one tick are idempotent.
  Meetings preserve only still-valid plans under the original expiry, and task
  routing resumes afterward. Do not loop on the same stale source observation.
- [x] Investigate an independent bounded accompaniment comparison after a real
  search control demonstrates changed routes and new observations. First compare
  the existing accompaniment option with its patrol fallback. A new follow
  candidate needs a distinct information opportunity, follows only a recent own
  sighting for at most three elapsed ticks, and keeps urgent overrides without
  mutual-follow waiting. If that evidence is absent, record deferral and expose
  no version. Retire an implemented follow candidate without useful distinct
  trajectories rather than leave an inert option.
- [x] Compare context-dependent self-report separately from the existing
  unconditional `self_report` arm. Base its explicit decision only on the
  impostor's own observed body, witnessed nearby players and available escape
  route/cooldown state. Do not consult hidden observer positions or another
  agent's suspicion. Pin a finite decision table before measurement, with both
  report and escape controls; reports still consume the ordinary meeting path.
- [x] Keep plans and observations distinct in memory and any viewer projection.
  Search/accompaniment intentions are not witness evidence. Newly acquired
  observations retain their actual later time and cannot corroborate a past
  whereabouts or completion claim. Respect own-agent versus other-agent fog
  display. No extra tactical LLM call is introduced.
- [x] Run actual canonical-map scenarios with a genuinely absent-but-living
  player, a discoverable body, stale/unreachable information, newly announced
  death, urgent interruptions, resumed tasks and the independent accompaniment
  investigation. Use the
  smallest legal roster that permits the intended post-meeting trajectory; a
  four-player parity ending must not be bypassed to fabricate a second search.
  Strict API/eval readers reconstruct the actual goals/evidence from recorded
  settings. Include prefix/aborted compatibility and baseline-only training
  refusal for unsupported candidates.
- [x] Each gate has a semantic plant: hidden-position input changes no decision;
  another player's private record changes no plan; stale/future timestamps cannot
  start a search; an expired or interrupted plan cannot keep moving; a later
  sighting cannot certify an older alibi. Compare OFF and independent arms with
  fixed scripted provider responses, effective changed trajectories, information
  gained, task delay, reports, wrongful accusations and call/token accounting.
- [x] Independent review attempts the plants and actual live-to-reader paths.
  Targeted checks, canonical reconstruction and `bash scripts/check.sh` pass.
  Record implemented, investigated/retired and unresolved quality outcomes
  separately; offline mechanics do not establish improved model decisions.

## Constraints

Read [architecture](../../docs/architecture.md), especially the observation
boundary, deterministic tactics and recorded experiment ladder. Begin runtime
changes only after the current evidence/account checkpoint and owner dispatch.
No engine import in agents, new map/role/provider/dependency, historical
re-recording, model fitting, live call or default adoption. Use temporary outputs.
Preserve all previous tactical and meeting verdicts. Fresh decision evaluation
is the separately authorized sixth milestone with a frozen candidate and budget.

## Expected scope

| Owner | Scope and handover |
| --- | --- |
| Observation/memory worker | New engine-free typed search/accompaniment state and pure latest-entitled-observation reducer; `working.py`, perception/store/evidence-context follow-through. Supply source IDs and event-local time, not a render-dependent last-seen cache. |
| Tactical worker | A small explicit planner and `agents/tactical/experimental.py` integration, urgent overrides, bounded search/accompaniment and contextual self-report. Keep original policies/old option semantics intact and write actual changed-trajectory controls. |
| Coordinator | Next closed experiment-envelope version preserving version-1/2 bytes, factory/config validation, recorded writer/game lifecycle and reader reconstruction integration. Own per-meeting lifecycle handover. |
| Evaluation/viewer workers | Necessary typed goal projection, own-lens rendering, source-bound matrix/report consumers and planted backward-alibi check. No public claim is promoted to private evidence. |

Prefer a pure planner transition over a per-agent typed plan and explicit inputs,
with the runtime owning that state. Reuse the existing action intents and pathing;
do not add a second simulation or a speculative natural-language plan protocol.
Finalize the exact cross-package interface and independent option-conflict table
before concurrent edits. Keep each shared file under one writer.

### Proposed reconstruction interface

One optional typed `InvestigationState` in each agent's `WorkingMemory` owns the
active plan, last processed tick and latest consumed source identity per known
player. Its active plan stores target, source observation ID/time, last-known
room, creation/expiry and inspected rooms. The consumed-source index is bounded
by the public roster and prevents cycling through the same stale sightings;
clearing an active goal must not erase that index. Plan state is intention,
not an observed event or a suspicion input.

An engine-free pure transition takes that prior state, current entitled typed
observations, announced dead IDs, own current state, public map, ordinary policy
intent and an immutable narrow planner profile. It returns the next typed state
and selected `ActionIntent`. It updates visits from actual observations rather
than assuming its previous move executed. Duplicate calls on the same tick are
idempotent. Urgent actions bypass movement selection while expiry still advances.
Version 1 selects the oldest eligible latest sighting, breaking ties by target
and citation ID. It first inspects the last-known room, then its unvisited
neighbors by reachable distance and room ID. Transit rooms before that first
inspection do not consume the inspection allowance. A newer sighting cancels the
old plan without restarting on that same tick; another eligible source may be
considered on a later tick. Failed/unreachable searches still consume their source.

For version 3, the reader constructs the actual supported `TacticalAgent` objects
bound to its reconstructed `AgentMemory` and drives the same `decide(packet)`
before ordered actions. This runs the shared planner together with the ordinary
policy, emergency tracker and urgent fallbacks; the reader must not implement
a second partial planner. Both paths use the identical recorded configuration
and meeting lifecycle notifications. Packet and event ingestion still has exactly
one owner: do not run the old reader's packet fold and `decide` ingestion twice.
The reader checks the resulting intent against the recorded actor action through
the existing privileged action adapter, including rejected/discarded actions;
it still applies the original recorded engine actions. A mismatch is refused,
never healed by substituting the recomputed action.

| Option | Reconstruction contract | Proposed choice |
| --- | --- | --- |
| Require built-in version-3 planner semantics | Only exact supported agent/policy classes with matching options may enable investigation. Readers reproduce each plan and verify its action; unsupported custom/subclass agents fail before output preparation. Custom fake model providers remain allowed. | Recommended initial scope; avoids inventing intentions for arbitrary scripted agents. |
| Add explicit plan-record transport | Custom agents would emit typed plan transitions with source references; readers validate ownership, clocks, bounds and the selected action, and label the plan as custom rather than reproduced built-in policy. | Defer unless custom-plan support is explicitly requested; do not add a spectator-only guessed goal. |

Version 3 must retain exact version-1/2 serialization and decoding. Investigation
initially conflicts with the old finished-crew `patrol`/`accompany` selector;
contextual self-report conflicts with the old unconditional self-report flag.
Search and contextual self-report remain independent. No accompaniment field or
rendered claim exists until its conditional comparison is justified and scoped.
Normal-policy seeded controls are required for the built-in route; existing
custom fixed-action scenarios cannot masquerade as exercising the new planner.

### Frozen contextual self-report comparison

Version 1 uses this ordered table, fixed before the normal-policy comparison.
An escape is the ordinary policy's move along a public map edge or its valid
vent entry; this selection says nothing about unseen observers or route safety.
A nearby player means a current first-hand snapshot in the actor's room,
excluding self and known teammates. Past sightings and reported claims do not
count as current presence.

| Own available information | Decision |
| --- | --- |
| Already in a vent, or no currently visible body in own room | Keep ordinary action. |
| Body present, no available ordinary escape | Report the body. |
| Body present, nearby non-teammate, own kill cooldown still active | Report the body. |
| Body present, all remaining cases | Keep ordinary escape, including a ready kill cooldown, teammate-only presence, or no current non-teammate sighting. |

This finite comparison is independent of unconditional self-report. Its report
branch is not a claim that an observer is suspicious or that reporting improves
survival. Discretionary search preserves every ordinary task-execution action, a stronger
protection than checking only tasks that have already made progress. Actual
visible-body reporting/approach and immediate witnessed danger retain urgent priority.
A body approach follows only current positive visibility; it never guesses a
hidden corpse location or latches a stale route. Source-tick kill observations
receive an immediate next-decision response even when the next snapshot does not
repeat that action. No persistent new flight strategy is claimed.

### Comparison scope finalized before capture

The five development seeds are 0, 1, 6, 7 and 14, selected after inspecting the
0–15 ordinary-policy scan. Use five players, one impostor, two tasks per crew and
a cap of 80 ticks. Compare ordinary behavior, search, contextual reporting,
unconditional reporting, old patrol, old accompaniment, then the search/report
combination. Existing accompaniment and patrol provide a direct comparison for
whether a follow-specific information opportunity exists. The inspected data
cannot be held-out confirmation. These bounds and the reporting table above
precede the final source-bound capture.

## Record impact

Lever-gated until an adopting record. Explicit versions change tactical actions,
future observations and optional rendered plan context only for new experiments.
Existing prompt/replay/model bytes and historical verdicts remain unchanged.
The finite offline comparison establishes mechanics and changed information;
adoption requires the later fresh-evaluation decision.

## Validation

Run focused typed-plan, perception, tactical-priority, actual scenario,
recorded-profile, API/eval and viewer tests after dispatch. Pin byte-identical
OFF controls and meaningful adverse plants. Reconstruct every candidate recording
from its actual map/roster/settings, and bind separate matrix artifacts to source
and recording bytes. The coordinator runs `bash scripts/verify_samples.sh`,
`bash scripts/check.sh` and the final live/static browser journey. Record exact
commands, effective arm sizes, source scope and limitations in Results.

## Results

Implementation, source-bound comparisons and the combined project gate are
complete. The [checkpoint](../../audits/investigation-candidate/checkpoint.md)
links exact measured inputs, ownership and separate review methods, semantic
controls, decisions and limits. Architecture references: Layering, Enforced
boundaries and Explicit cleanup experiments.

The coordinator adopted the conditional accompaniment disposition: investigate
the existing recent-sighting behavior against its patrol fallback first; expose
no new three-tick follow version when no useful later information is demonstrated.
This follows the authorized plan's “if justified” scope. The five-seed comparison
is development evidence, not a general rejection of accompaniment.

Normal-policy and meeting source inventories are identical in the final captures.
All 35 normal-policy games and 42 scripted meeting controls reconstruct strictly.
The candidate handoff records hashes and remaining fresh-evaluation prerequisites;
it is explicitly not an execution manifest or live-spending authorization.

Directly necessary follow-through adds a shared privileged policy-reconstruction
helper, exact-factory validation, typed own-lens goal projections, generated types,
source-bound measurement scripts and their semantic controls. No package boundary
was bypassed, no historical model/report was rewritten and all candidates remain
OFF. The final coordinator refinements have targeted checks; the original
independent reviews remain frozen and external Claude review is pending.

Final verification: `bash scripts/check.sh` passed 7,137 Python tests and 514
frontend tests, with strict mypy on 466 sources, lint/format, import/document/type
checks and production build. Twenty Python tests are optional skips and three
are expected failures. All 300 historical reconstructions, four derived report
checks and both actual API/static browser journeys passed. The final captured
source inventories were recomputed against the workspace and match exactly.

Delivery state: implemented and verified on cleanup; independent bounded reviews
and their coordinator dispositions are preserved. External owner/Claude review,
main merge and adoption remain pending. All offline work under this card is done;
fresh provider evaluation is a separately budgeted execution decision.
