# Correct evidence timing in one recorded deduction case

**Status:** done

## Outcome

A recorded, default-OFF v2 experiment gives agents a coherent account of what
they observed, when they observed it, and what remains unknown. One canonical
four-player case carries an unwitnessed kill, subsequent body discovery and a
disputed route through the actual observation, memory, meeting-prompt and viewer
pipeline. Honest, impossible-account and insufficient-evidence variants expose
different information without manufacturing certainty. Existing OFF and stamped
v1 recordings retain their original interpretation.

## Evidence

Milestone 3 in [the authorized plan](../post-review-plan.md) follows the
maintenance and evaluation corrections. The
[owner review](../../audits/review-2026-09-06/REVIEW_REPORT.md), sections 8 and 12,
identifies contradictory source-event and snapshot-route clocks (G4-2), an
unwatched transition rendered as movement (G1-02), public death knowledge ignored
by proximity suspicion (M3-01), and earlier relevant travel intervals omitted
from counterevidence (M3-02). Movement witness lists lack independent semantic
checking (C1-03/G4-4). The review labels same-tick order dependence and delivery
to witnesses who later died separately; those observations do not authorize
randomized action order or deletion of legitimately acquired memory.

The [temporal contract](temporal-observation-contract.md),
[reasoning contract](reasoning-evidence-experiments.md), and
[observation contract](../../docs/observation-contract.md) describe the current
v1 behavior. Its live/reader parity does not establish correct timing. Current
readers collapse temporal versions to a boolean; changing v1 producers in place
would silently reinterpret previously stamped ON recordings.

## Acceptance

- [x] Freeze the finite scenario inputs, scripted actions, expected entitled
  evidence and comparison profiles before measuring the candidate. Use the
  existing canonical map and four-player/one-impostor rules; the primary case
  contains neither a witnessed kill nor a witnessed vent.
- [x] Reproduce the clock, breadcrumb, known-death proximity and omitted-interval
  defects. Keep old behavior as explicit OFF/v1 compatibility controls; v2
  rejects the defect without changing their interpretation.
- [x] Resolve temporal version and evidence version as explicit integers before
  play. Preserve absent/OFF and version 1; stamp version 2 on the actual evidence
  path, including interrupted recordings. Reject unknown, coerced, mixed and
  conflicting versions. Environment changes after construction cannot change
  live delivery or recorded reconstruction.
- [x] Distinguish pre-action snapshots, source events and delivery time in v2
  memory and citations. An agent's own route and witnessed-event lines agree
  about within-tick ordering; imminent meetings receive entitled evidence once.
  Retain observations acquired before a witness dies, without giving dead
  agents further tactical decisions or meeting turns.
- [x] Independently reconstruct movement entitlement from event-local positions,
  life, vent occupancy and visibility. Missing/extra witnesses and forged
  movement endpoints fail semantic controls. Probe both action orders for a
  same-tick crossing and state the sequential boundary honestly; do not change
  engine action order to manufacture identifier-invariant outcomes.
- [x] Two separated sightings render as two sightings, never a watched
  transition. Only an entitled movement event supports movement testimony.
  Gaps and unknown legacy timing remain explicit rather than being filled in.
- [x] V2 opening descriptions and rendered memory contain no death-tick-bearing
  body identifiers. Public last-alive/dead-by bounds remain distinct from
  discovery time. A later sighting after an already announced death cannot add
  murder-opportunity suspicion for that victim.
- [x] Assess the interval relevant to the disputed account, including an earlier
  interval followed by newer harmless sightings. A legal one-door journey
  contests an impossibility allegation without proving innocence. An impossible
  account is identified conditionally on its cited placements; missing evidence
  yields uncertainty. The engine must never execute an impossible movement to
  construct this control.
- [x] Run honest, impossible-account, insufficient-evidence and already-known-dead
  variants through real `HeadlessGame` recording, observation delivery, memory
  rendering, opening prompts and the recorded API/viewer projection. Match live
  and reader text, source IDs and scene citations. Scripted speech remains
  testimony, not engine-certified truth or evidence of model improvement.
- [x] Focused semantic tests, independent adverse review, the shared project
  gate and canonical replay checks pass. Record source/input identities,
  commands, observed differences, limitations and the separate adoption state.

## Constraints

Work stays on `codex/cleanup`; no main merge, deployment, adoption, live-provider
call, dependency, map, role, training change or historical re-recording. Follow
architecture Layering, Enforced boundaries, and Determinism and the substrate
ladder. Engine state transitions remain pure and ordered as today. Agents and
meetings remain engine-free; tactical behavior makes no LLM calls.

Start runtime edits only after the coordinator releases the correction batch
and hands over the version/delivery interface below. Scenario scaffolding must
reuse the evaluation milestone's source-bound inventory rather than create a
second unbound measurement mechanism. This card establishes evidence mechanics;
the later accusation/reply and investigation milestones own those behaviors.
Use deterministic fake/scripted providers only, with bounded test runs and
temporary outputs. No fresh-model quality or adoption claim follows from them.

## Expected scope

One writer owns each file; transfers require explicit handover.

| Owner | Files and responsibilities |
| --- | --- |
| Coordinator | `orchestrator/experiment_config.py`, `meetings/evidence_profile.py`, `orchestrator/replay.py`, `orchestrator/game.py`: frozen version selection, stamps, factory binding and core wiring. Also `orchestrator/observation_delivery.py`, API/replay reader adaptation, source-reference projection, architecture/env/index/ledger follow-through and integration gates, unless explicitly handed over. |
| Evidence worker after handover | `observation/version.py`, `observation/packet.py`, `observation/service.py`; `engine/events.py`, `engine/tick.py` for entitled event metadata only; `agents/perception.py`, `agents/memory/store.py`, `agents/memory/beliefs.py`, `agents/memory/evidence_context.py`; `eval/witness_entitlement.py`, `eval/leak_scan.py`, `scripts/scan_recording_packets.py`; their focused semantic tests, `tests/orchestrator/test_temporal_evidence_v2.py`, this card and `docs/observation-contract.md`. |
| Other active workers | Retain their assigned evaluation, report and viewer files until the coordinator explicitly transfers them. No parallel edits to shared readers, schemas or fixtures. |

Required interface handover before implementation:

1. An explicit temporal version `None | Literal[1, 2]` reaches the observation
   service and delivery path. A boolean may describe enabled status but cannot
   select reconstruction semantics. The recorded integer resolver is the
   authority for live/read parity; old true/1 selection retains v1.
2. Evidence context receives an independent version `None | Literal[1, 2]` and
   public topology through the existing engine-free memory construction. The
   coordinator defines supported combinations; unsupported combinations raise.
   Version 2 must not silently relabel a v1 evidence path.
3. The transport contract supplies enough source tick, observation phase and
   event ordering information to reconcile the observer's own route with event
   evidence. Any additive fields are emitted only for v2 and retain source
   provenance through ingestion and citation lookup. Confirm exact field names
   with the coordinator before producer and consumer edits diverge.
4. The same version-specific projection and ingestion functions serve the live
   runner, recorded API reconstruction and semantic scan. Frozen instruments
   continue refusing unsupported evidence; no broad boolean opt-in substitutes
   for a v2 adapter. Scenario recording uses real legal actions, not a privileged
   memory injection masquerading as observed evidence.

## Record impact

New versioned, default-OFF experiment until a separate adopting decision and
record. V2 may change future observation/memory/prompt/detector bytes and actions;
stamp those semantics explicitly. OFF and v1 replay hashes, prompts, source-ID
meaning, historical artifacts and previous experimental verdicts stay intact.
Retain a narrow v1 compatibility path where necessary to interpret real stamped
records, rather than relabeling them as repaired v2 behavior.

## Validation

Use fake/scripted real-run scenarios and paired semantic plants. Freeze the
scenario inventory and per-run limits before capture; write only new temporary
outputs. Report what reached each agent and the viewer, not merely whether a
schema parsed. The initial focused commands are:

```sh
.venv/bin/pytest tests/observation/test_temporal_observations.py tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_temporal_evidence_v2.py tests/agents/test_evidence_context.py tests/agents/test_memory_rendering.py -q --tb=short
.venv/bin/pytest tests/engine tests/observation/test_leak_property.py tests/agents/test_perception.py tests/agents/test_beliefs.py tests/orchestrator/test_substrate_binding.py -q --tb=short
.venv/bin/python scripts/validate_task_docs.py
bash scripts/check.sh
bash scripts/verify_samples.sh
```

The end-to-end tests exercise the reusable scenario definitions below. The
coordinator owns the source-bound evaluation matrix and its capture identity.
Gate completion on both mechanics and preserved OFF/v1 controls, not fake win
rates or the number of new observations.


## Results

Implementation is active pending the coordinator's combined gate and independent
review. Architecture references: Layering, Enforced boundaries, Determinism and
the substrate ladder, and Observation timing/public identities. The durable
wire/clock contract is in `docs/observation-contract.md`, Explicit temporal
version 2. OFF/v1 remain explicit compatibility controls; no adoption or model
quality verdict is claimed.

- `observation/temporal.py` folds actual source state, ordered engine events and
  submitted actions. It preserves observer-local order, position, own transition
  and actor task receipts; other-player task activity is source-time and
  role-blind. No engine transition/producer changes were required. Version 1
  still uses its existing witness projection and serialized fields.
- V2 perception/rendering separates snapshots from events and public claims from
  observations. It removes inferred watched movement, co-presence and completion
  from the v2 renderer. Earlier travel intervals survive newer harmless sightings;
  tick-only public placements remain conditional. The public death bound gates
  later proximity inputs without weakening legitimate earlier opportunity.
- The independent ordered-channel oracle lives in `eval/temporal_entitlement.py`.
  Existing witness checking now verifies legacy movement lists/endpoints against
  event-local visibility without changing them. The scan supports recorded
  experiments explicitly; it adds no hidden integrity policy to the historical
  no-check replay-walk profile. Packet census format 2 counts temporal batches and
  task receipts as well as snapshots.
- Independent review planted stripped snapshot version, altered tick and invented
  task activity that the initial scanner accepted. The repaired scanner binds
  version/tick/own position and rejects every v2 snapshot action channel; four
  plants include those cases and a forged own position. Review also identified
  hub regroup crossing a walking interval. `public_regroup` retains the actual
  public relocation and bounds the affected interval; the coordinator supplies
  the live/reader call sites, and independent recheck remains required.

`experiments/deduction_scenarios.py::scenario_definition` freezes seven bounded
cases before matrix capture: honest, impossible_account, insufficient_evidence,
already_known_dead, witnessed_kill, witnessed_vent and late_accusation. Each uses
canonical seed 1, four players/one impostor, one task per crewmate and at most 14
ticks through real HeadlessGame recording. There is no injected initial state,
engine event or agent observation. The ADMIN route respects the seeded four-tick
kill cooldown and allows the real `upload_logs` task receipt. In the primary case,
p-2 leaves at tick 3, p-4 kills p-1 unwitnessed at 4, and p-2 returns before p-4's
ordered departure to WEST_HALL at 5, reporting the body at 6. A claimed REACTOR
placement at 5 conflicts conditionally with the actual WEST_HALL observation;
those rooms are four walking doors apart. The insufficient variant misses that
window. The direct controls add actual witnessed kill/vent testimony. The late
accusation targets the already-spoken reporter, exercising the optional reply.
Every default provider vote is a deliberately scripted SKIP; outcomes/call counts
measure mechanics only.

The known-dead case has a real public emergency at tick 5 and later discovery at
8. Canonical same-room vision and the existing exclusion of current-tick
proximity sightings do not produce the reviewed scalar false lift on that route.
The scalar defect is therefore isolated by an explicitly adversarial **rule
input** in `test_public_death_bound_filters_only_post_announcement_proximity`,
with old +0.2 and repaired zero-lift controls and a legitimate earlier opportunity
control. This unit input is not presented as a real emitted observation or an
end-to-end reproduction.

Development verification (full gate remains the coordinator's responsibility):

```sh
.venv/bin/pytest tests/observation/test_temporal_v2.py tests/orchestrator/test_temporal_evidence_v2.py tests/scripts/test_scan_recording_packets.py -q --tb=short
.venv/bin/pytest tests/observation/test_temporal_observations.py tests/agents/test_perception.py tests/agents/test_evidence_context.py tests/agents/test_memory_rendering.py -q --tb=short
```

The first group passed 38 tests before the four reviewed snapshot plants were
added; the second passed 209 compatibility checks. Later final counts and the
combined check are to be recorded after the runtime freeze. Each real scenario
checks live opening prompt/reader memory equality, privacy, explicit v2 stamps,
terminal recording, no repeated-output overwrite, and independent batch/snapshot
entitlement. Source identifiers are compared by recorded citation lookup, never
by extracting dates from their text. The coordinator's matrix binds exact final
sources, config, prompts, input identities and outputs before an evaluation claim.

Final worker checkpoint before the coordinator's combined gate: the eight-suite
command covering new v2/scenario tests, legacy temporal delivery, perception,
evidence/memory rendering and packet census passed **272 tests** in 16.95 s.
Ruff lint and format checks passed for all 15 owned Python files; strict mypy
passed all 20 selected source/test files. Task documentation validation passed
390 historical tasks/prompts and 31 work cards. No commit, push, full-gate or
adoption claim is made by this worker checkpoint.

The independent reviewer reran 58 focused tests after the snapshot correction
and found no remaining bounded entitlement/clock blocker. Its new
`tests/orchestrator/test_public_regroup_evidence.py` runs a legal four-player,
two-meeting schedule. Removing only its public regroup record reproduces the
old false ADMIN tick 2 → CAFETERIA tick 3 walking accusation; retaining the record
suppresses that allegation while preserving a later impossible public account.
The test also matches next-meeting API memory to the actual live opening prompt.
The coordinator should include it in the final combined verification:

```sh
.venv/bin/pytest tests/orchestrator/test_public_regroup_evidence.py tests/observation/test_temporal_v2.py tests/orchestrator/test_temporal_evidence_v2.py -q --tb=short
```

### Verified checkpoint

The [source-bound checkpoint](../../audits/deduction-candidate/checkpoint.md)
records implementation decisions, separate review findings, synthesis, measured
denominators, the full project gate, all 300 reconstructions, four historical
report checks and both browser journeys. Its measurement binds the exact runtime
source and frozen inputs. Architecture references are Layering, Enforced
boundaries and Explicit cleanup experiments. All acceptance work for this card
has passed; earlier provisional Results above record the state at their writing.
No default adoption, main merge, historical re-recording or live spending occurred.
