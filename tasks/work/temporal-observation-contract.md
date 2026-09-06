# Entitled temporal observations and opaque body IDs

**Status:** ready

## Outcome

Establish an explicit, testable contract for when an agent learns an event and
what that event entitles it to know. Prepare the smallest compatible repair for
movement witnesses, meeting-trigger evidence, audible validation, and body IDs
that expose a hidden death tick. This card begins with characterization and
design; production changes wait for the current cleanup gate and the recorded
temporal/compatibility decisions below.

## Evidence

- `observation/service.py::_moved_players_for_agent` gates a departure on the
  observer's post-tick visible rooms. Existing real-service controls in
  `tests/observation/test_leak_property.py` deliberately pin an arriving
  observer receiving the origin and a departing observer missing it.
  `engine/tick.py::advance_tick` applies actions sequentially; the live
  orchestrator orders them by actor. An event-local snapshot is therefore a
  distinct option from either whole-tick snapshot.
- `orchestrator/game.py::_run_loop` builds packets before advancing, runs a
  triggered meeting immediately, and delivers its trigger-tick events after
  resolution. [The hardening audit](../../audits/audit-phase-21-hardening.md)
  carries H-22/H-54 and H-42/H-43; its measurements are historical evidence,
  not newly recomputed counts.
- A local adverse probe of `eval/leak_scan.py::assert_packet_is_leak_clean`
  accepted both an invented `sabotage_alarm` with no active sabotage and an
  invented `vent_use_heard` with no engine events. The live producer currently
  emits the global alarm alone. This reproduces the B-28 coverage gap without
  claiming that the producer emitted either forged cue.
- `engine/rules.py::resolve_kill` creates `body-{victim}-{tick}` and the
  observation and episodic payloads retain it. The rendered discovery line
  omits that ID; model exploitation has not been demonstrated. Report intents
  round-trip the ID, and tactical body selection sorts it.

## Acceptance

- [ ] Record an entitlement matrix for each observation channel: source state
  or event, event time, delivery time, recipient, permitted fields, and memory
  citation. Distinguish death, discovery, public dead-roster announcements,
  witnessed kills, and the killer's own knowledge.
- [ ] Reproduce movement and same-tick meeting cases through the actual runner
  and reconstruction, including observer arrival/departure, action ordering,
  same-tick vent/report, killed/ejected witnesses, and later delivery. Identify
  missing evidence separately from duplicate evidence and stale timestamps.
- [ ] Record the selected temporal rule and repair boundary before changing
  behavior. Use the observer's actual location when each move resolves under
  the existing sequential engine clock; characterize its difference from both
  whole-tick snapshots and version the behavior explicitly.
- [ ] Specify a deterministic public body-handle scheme and report translation
  that reveals no hidden death time. Check repeated discovery/reporting,
  selection order, multiple bodies, invalid handles, and legacy reconstruction.
  Evaluate `body-{victim_id}`: victim identity is already public and each victim
  dies once. Translate at the privileged action boundary and preserve lexical
  ordering for custom multi-digit rosters. Hashing a small enumerable
  secret-bearing ID is not an opacity guarantee.
- [ ] Add meaningful audible entitlement controls: genuine active/inactive
  alarms, invented cues, wrong room attribution, duplicates, and allowed
  recipients. A planted violation must fail the semantic scan.
- [ ] Identify every producer, live/replay consumer, training path, schema,
  test, and compatibility stamp that the selected repair changes. Record
  subsequent implementation scope and measurements without rewriting frozen
  recordings or earlier experiment verdicts.

## Constraints

Depends on verification of the current completion/lifecycle batch. Work on
`codex/cleanup`; root owns integration and shared-file assignment. Follow
`docs/architecture.md` Layering, Enforced boundaries, and Determinism and the
substrate ladder. Keep the engine deterministic and agents engine-free.

No production edits during the preceding batch gate. Temporal semantics,
public compatibility, and experiment adoption must be resolved explicitly;
the card does not authorize a default prompt/detector change or live calls.
Do not reopen fixed reported-body cleanup or duplicate successful reports.
Dead `vent_use_heard` retirement is a separate coupled-consumer census under
roadmap item 37; absence from replay JSONL alone does not establish deadness.

## Expected scope

This card, a focused observation evidence note or tests, and read-only inspection
of `engine/`, `observation/`, `agents/perception.py`, agent memory/tactical
consumers, orchestration and action translation, current replay walkers,
`eval/leak_scan.py`, and their training/API consumers. Coordinate source-file
ownership and update this section before implementing the selected repair.

## Record impact

Characterization and design have none. A temporal perception repair changes
future agent evidence and can change rendered prompts, detector results,
actions, and replay bytes. Record compatibility explicitly; prompt/detector
differences remain default-OFF until an adopting record. A narrowly contained
identifier exposure repair may be unconditional with its compatibility
treatment recorded. Preserve current and historical reconstruction contracts;
keep internal engine body identity stable if boundary translation can remove
the exposure without changing truth.

## Validation

Use deterministic offline scenarios and planted packet mutations. Run focused
observation, perception, memory, orchestration and reconstruction tests, Ruff,
strict mypy, and `scripts/validate_task_docs.py` for the card. Root runs
`bash scripts/check.sh` and the canonical replay checks for implementation.
Report mechanics evidence separately from recorded-model analysis or a future
budgeted fresh-model evaluation.
