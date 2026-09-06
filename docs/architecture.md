# Architecture (as built)

This note defines current layering, enforced boundaries and determinism.
`AGENTS.md` routes here; `DESIGN.md` records historical rationale.

## Layering

![The engine, observation firewall, agents, meetings, orchestrator and privileged readers](media/architecture.svg)

```text
  engine/             pure deterministic tick; owns hidden state
    v
  observation/        firewall: audited packets + public map
    v
  agents/  meetings/  engine-free reasoning; ActionIntent / MeetingResult out
    ^                 llm/ supplies provider adapters
  orchestrator/       wires actions, meetings and recording
    v
  eval/   api/        privileged readers; api/ -> frontend/ on generated types
```

Arrows show data flow. The orchestrator is the privileged wiring layer; agents
must never import it to reach engine state.

## Packages

**`engine/`** — `tick.py::advance_tick` is a pure function of frozen state and
actions, without wall clock or globals. It owns roles, kill attribution and vent
occupancy. `rng.py` serializes the full Mersenne state into every committed
`state_hash`; the default `FULL` hash policy preserves byte identity.

**`observation/`** — `service.py` builds `ObservationPacket` through
`engine/visibility.py`, strips hidden fields and writes packets through
`audit.py`. Its engine-free schemas include `PublicMapView` and `ActionIntent`.
`orchestrator/boundary.py::public_map_from_engine_map` projects the shared public
topology. Observation imports none of agents, meetings or llm.

**`agents/`** — tactical policies make deterministic per-tick decisions; learned
movers remain opt-in. Strategic reasoning renders strict-undefined Jinja prompts
at meetings. Memory holds typed episodic events and derived beliefs.
`orchestrator/game.py::TacticalAgent` is the production agent;
`agents/runtime.py` is a test harness.

**`meetings/`** — `manager.py` runs opening, reactive accusation chain, optional
info-share, remaining-speaker roll-call, voting and resolution. The chain ends
on no new accusation, a cycle or the living-player cap. Contradictions are
recomputed over the transcript before voting. The manager returns
`MeetingResult`; it never mutates engine state.

**`llm/`** — `client.py` defines `LLMClient`. Fake, Anthropic, Ollama and
Featherless adapters share budget/deadline wrappers. Featherless's locked
`Qwen/Qwen3.6-27B` is the canonical evaluation model; ordinary checks use the
deterministic fake. This package imports nothing else in the repository.
Provider setup and evaluation history are in `llm/README.md`.

**`orchestrator/`** — `game.py::HeadlessGame` dispatches ticks and meetings;
`apply_meeting_result` applies their results. `boundary.py` and
`action_ordering.py` translate intents deterministically. `replay.py` records
actions and state hashes and owns the substrate registry.

**`eval/`** — `balance_eval.py` strictly folds recordings into typed `GameReport`
and `TournamentReport` data; analyzers consume these reports. Roles come from
the privileged game result, never an agent packet. Determinism, leak and prompt
regression checks also live here.

**`api/`** — FastAPI serves spectator DTOs from `schemas.py`. It is a privileged
post-game reader: roles, attribution and vents are intentionally available.
`tests/api/test_leak.py` pins that inventory. The unauthenticated API remains
loopback-only; see `docs/deployment.md`.

**`frontend/`** — React, Vite, Tailwind and PixiJS consume
`src/types/api.ts`, generated from Python DTOs by `scripts/gen_frontend_types.py`.
`tests/api/test_view_model.py` rejects stale generated types. The browser never
imports Python. Agent-lens controls constrain presentation, not server access.

**`training/`** — rollout, ES, surrogate, conviction and co-evolution machinery.
NumPy stays here because BLAS reduction order is not portable byte identity.
The default mover remains the scripted FSM; historical NO-FLIP/NO-GO verdicts
are preserved.

**`experiments/`** — offline measurement harnesses write separate artifacts.
Only the explicit spikes listed in `pyproject.toml`'s mypy exclusion, plus
one-off `design/` generators, bypass strict typing.

## Enforced boundaries

Four import-linter contracts forbid agents importing engine, training or
`meetings.manager`, and observation importing agents, meetings or llm. Agents
may use meeting schemas. Meetings and llm are engine-free in fact, without
separate contracts. All shipping root packages appear in `.importlinter`, so
transitive paths through privileged packages are checked too.

`tests/test_firewall.py` plants a forbidden import in an isolated copy and
requires rejection. `tests/observation/test_leak_property.py` and
`eval/leak_test.py` scan real/generated factory packets, including planted leaks.
`eval/witness_entitlement.py` independently reconstructs event-local positions,
life and vent occupancy before checking witness lists. Factory checks also
compare owned tasks to engine truth. Strict mypy covers the repository;
`eval/determinism_test.py` compares scripted replays byte for byte.

## Determinism and the substrate ladder

A seed, configuration, agent factory and provider responses determine replay
bytes within their recorded runtime scope. The fake provider is deterministic;
fresh hosted generation is not. For hosted runs, the recording is the
reproducibility boundary. The README distinguishes replay integrity,
same-runtime repeatability and optimizer portability; these claims are separate.

`orchestrator/replay.py` owns twenty-one graduated keys in
`_RETIRED_ALWAYS_ON_LEVERS` and five live toggles:
`impostor_roll_call`, `reporter_reasoning`, `corroboration_discipline`,
`testimony_shapes` and `temporal_observations`. Each toggle has a default-OFF
`AILIBI_*` variable. Recordings and manifests stamp the substrate; readers refuse
incompatible settings. Graduation deletes the resolver and env mechanism while
retaining its provenance key, following `docs/agent-procedures.md`.

Baselines are adopting records. Baseline 8 is the maintenance re-record on
corrected behavior (`audits/audit-phase-21-rerecord.md`). Baseline 7 followed an
explicit FINDING override (`audits/audit-phase-20-baseline-7.md` §6.1), not a
claim that its missed bars passed.

### Observation timing and public identities

Packets use victim-derived body handles; privileged report translation retains
engine IDs. Default-OFF `temporal_observations` adds event-local movement
entitlement and source-tick kill/vent/move delivery before meetings, including
witnesses killed later that tick. Shared delivery helpers preserve exact-once
ingestion in live play and supported readers. Tick-row versions identify partial
runs; missing means legacy, conflicts fail and unsupported instruments refuse ON.

Complete model-facing body-ID privacy remains gated: legacy OFF opening prompts
still expose internal body IDs until adoption. Typed packet handles are repaired
unconditionally. The current audio wire allows only global sabotage alarms.
Spectator version 3 explicitly reads compatible version-2 audio and rejects
unsupported cues. The historical learned-vector audio position stays reserved zero.

[The observation contract](observation-contract.md) defines entitlement, clocks,
citations and compatibility. `api/observation_references.py` projects stable
citations and exact spectator scene frames within the privileged-reader boundary.

### Explicit cleanup experiments

`orchestrator/experiment_config.py` defines a closed immutable configuration for
redistribution, finished-crew behavior, vent exits, meeting follow-through,
self-report, sabotage timing, coherent reset and two meeting-evidence profiles.
Default configuration is omitted from recordings. Enabled tick and game-over stamps
must agree; unknown versions fail. The orchestrator passes narrow engine-free
options to engine and agent functions.

`meetings/evidence_profile.py` binds context/reply versions before play.
`meetings/rebuttal.py` selects at most one additional reply.
`agents/memory/evidence_context.py` derives public death bounds and conditional
walking feasibility from the observer's own records and public topology.
`engine/meeting_reset.py` owns the reset transition. These helpers have actual
callers and semantic controls; their experiments remain OFF and unadopted.

### Current model evidence

`training/provenance.py` binds corpus, roster, feature-derivation import closure,
map, dependency locks and runtime. Version-1 evidence restores only through
explicit historical diagnostics. Current scoring/installation recomputes the
named source; an operator-supplied digest alone cannot certify it. Synthetic
fixtures declare their scope. Current campaigns bind the fake provider and
current prompt family to an explicit baseline environment, refusing enabled or
unbound experimental profiles. Scope metadata stays with newly produced results.
