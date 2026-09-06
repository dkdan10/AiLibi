# Retire the unused vent-audio protocol coherently

**Status:** active

## Outcome

Roadmap 37 removes the dead vent-audio mechanism from current observation,
memory, inference and spectator contracts while preserving real sabotage alarms
and frozen learned-vector layouts. Historical evidence is not rewritten.

## Evidence

The current `ObservationService._audible_events` produces only a global active
sabotage alarm. The retired vent duplicate survives in packet/API literals,
perception and memory rendering, a tactical feature branch, spectator reference
copy and synthetic tests. The close's census explicitly requires a coupled
retirement, not inference from an absence in replay JSONL.

`heard_vent_use` is a named scalar in frozen encoder versions 2 and 3. Canonical
packet sweeps confirm it is zero while the neighboring sabotage feature fires.
Removing that position would invalidate existing weights. B-25's passive task
continuation is separately a documented engine rule with real unit coverage;
production's full action dispatch does not make the engine API branch invalid.

## Acceptance

- [x] Census and remove the vent-audio producer/consumer vocabulary from current
  typed packets, perception, memory rendering and spectator projection. Preserve
  actual witnessed vent evidence and sabotage alarms through their real paths.
- [x] Narrow the spectator contract under version 3. Explicitly accept existing
  version-2 payloads whose audio is compatible; reject a retired or unknown cue
  with a useful error rather than silently dropping it. Cover direct tick reads.
- [x] Retain the old named encoder position as an explicit reserved zero with
  unchanged dimensions/version/weights. Remove the unreachable computation and
  tests that require a fabricated supported cue; keep planted schema/leak checks.
- [x] Record why passive engine task continuation is retained, with current
  controls. The current dispatcher must preserve complete live-agent actions;
  any additional guard is coordinated with its owner.
- [ ] Independent review, focused tests, generated types, full project checks
  and canonical samples pass. Record old and current wire compatibility.

## Constraints

Follow docs/architecture.md layering and determinism. No experiment adoption,
prompt-byte change on valid current inputs, model refit or historic artifact
rewrite. Dead observations are refused, never converted into invented evidence.
The existing opaque packet and temporal entitlement controls remain in force.

## Expected scope

Root owns observation/packet.py, agents/perception.py, agents/tactical/features.py,
API schemas/reference projection, generated frontend types, client version/audio
checks, relevant UI/source comments and focused tests. Reasoning owner applies
the narrow memory/belief removal in its files; tactical owner fixes its stale
impostor comments; provenance owner updates its synthetic training fixture.
Shared orchestrator dispatch guards use that owner's sequential handover.

## Record impact

Post-record protocol retirement. Version-2 payloads with the actually produced
audio remain readable explicitly; unsupported cues fail. Current new payloads
stamp version 3. Frozen encoder layouts keep their reserved zero position.
Valid current observations, prompt bytes and canonical engine hashes do not move.

## Validation

Use genuine service-to-memory sabotage and witnessed-vent paths; reject old and
invented audio at both schema and semantic boundaries. Exercise version-2 and
version-3 browser reads plus wrong/retired kinds. Recompute generated types,
run affected inference/perception/API/client tests and passive-task controls,
then independent review and `bash scripts/check.sh` with all canonical samples.

## Results in progress

The current packet and API literals accept only sabotage_alarm. Perception,
memory and reference rendering no longer carry the unused vent-audio path.
Current consumers were censused across agents/meetings/observation/API/frontend/
orchestrator/eval/tests. Remaining mentions are the reserved historical scalar
and explicit rejected/poisoned inputs; witnessed vent evidence is unchanged.
Generated TypeScript and fidelity declarations match spectator version 3.
The client accepts compatible version-2 recordings explicitly and rejects
retired/unknown cues, including direct tick endpoints and unstamped responses.

The scalar position remains index 50 in the 111-element v2 fixture. Its current
valid-input SHA is c67bd96472ee644243e9abb518c1f3b9f9ec42783e9b67e04be58610eae3b5e5.
The previous golden fixture fabricated unsupported vent audio; replacing only
that scalar with one reproduces its old checksum. More usefully, running the
current valid fixture against the isolated pre-retirement encoder passed the
two golden/reserved-zero controls, showing that valid vectors remain identical.
Existing learned weights and encoder versions are untouched.

The passive engine API remains: test_continuing_task_progresses_without_repeated_action
and test_continuing_task_completes_and_can_trigger_crew_win exercise real empty
follow-up action batches. Production now rejects an incomplete living-agent
intent batch before recording. Both contracts coexist deliberately.

Targeted checks: 132 perception/temporal/features/API tests passed, one optional
skip; 36 client tests passed. The narrowed-schema rejection failed on the old
schema while genuine alarm controls passed. A later 63-test engine/protocol/
witness/corpus selection passed; a separate 82-test API/property/dispatcher
selection passed with one optional skip, including typed-strength projection.
Strict typing, generated types, Ruff, TypeScript and ESLint passed on affected
surfaces. Logs: /tmp/ailibi-retired-audio-python-final.log,
/tmp/ailibi-root-final-targeted.log, /tmp/ailibi-root-validation.log.
Independent review approved the coupled retirement, reserved slot, compatibility
and private-view gates after actual consumer and planted-corruption checks.
The isolated staged protocol/privacy snapshot passed 134 Python checks with one
optional skip, two v3 golden/layout checks and 43 frontend client/privacy checks.
Logs: /tmp/ailibi-final-protocol-python.log and
/tmp/ailibi-final-protocol-browser-unit.log. The new combined gate remains pending.
