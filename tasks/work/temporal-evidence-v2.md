# Correct evidence timing in one recorded deduction case

**Status:** ready

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

- [ ] Freeze the finite scenario inputs, scripted actions, expected entitled
  evidence and comparison profiles before measuring the candidate. Use the
  existing canonical map and four-player/one-impostor rules; the primary case
  contains neither a witnessed kill nor a witnessed vent.
- [ ] Reproduce the clock, breadcrumb, known-death proximity and omitted-interval
  defects. Keep old behavior as explicit OFF/v1 compatibility controls; v2
  rejects the defect without changing their interpretation.
- [ ] Resolve temporal version and evidence version as explicit integers before
  play. Preserve absent/OFF and version 1; stamp version 2 on the actual evidence
  path, including interrupted recordings. Reject unknown, coerced, mixed and
  conflicting versions. Environment changes after construction cannot change
  live delivery or recorded reconstruction.
- [ ] Distinguish pre-action snapshots, source events and delivery time in v2
  memory and citations. An agent's own route and witnessed-event lines agree
  about within-tick ordering; imminent meetings receive entitled evidence once.
  Retain observations acquired before a witness dies, without giving dead
  agents further tactical decisions or meeting turns.
- [ ] Independently reconstruct movement entitlement from event-local positions,
  life, vent occupancy and visibility. Missing/extra witnesses and forged
  movement endpoints fail semantic controls. Probe both action orders for a
  same-tick crossing and state the sequential boundary honestly; do not change
  engine action order to manufacture identifier-invariant outcomes.
- [ ] Two separated sightings render as two sightings, never a watched
  transition. Only an entitled movement event supports movement testimony.
  Gaps and unknown legacy timing remain explicit rather than being filled in.
- [ ] V2 opening descriptions and rendered memory contain no death-tick-bearing
  body identifiers. Public last-alive/dead-by bounds remain distinct from
  discovery time. A later sighting after an already announced death cannot add
  murder-opportunity suspicion for that victim.
- [ ] Assess the interval relevant to the disputed account, including an earlier
  interval followed by newer harmless sightings. A legal one-door journey
  contests an impossibility allegation without proving innocence. An impossible
  account is identified conditionally on its cited placements; missing evidence
  yields uncertainty. The engine must never execute an impossible movement to
  construct this control.
- [ ] Run honest, impossible-account, insufficient-evidence and already-known-dead
  variants through real `HeadlessGame` recording, observation delivery, memory
  rendering, opening prompts and the recorded API/viewer projection. Match live
  and reader text, source IDs and scene citations. Scripted speech remains
  testimony, not engine-certified truth or evidence of model improvement.
- [ ] Focused semantic tests, independent adverse review, the shared project
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

The new end-to-end test file is an implementation deliverable; its absence now
is not a passing check. Add the concrete scenario capture/reconstruction command
and frozen inputs to Results when the evaluation owner hands over that interface.
Gate completion on both mechanics and preserved OFF/v1 controls, not fake win
rates or the number of new observations.
