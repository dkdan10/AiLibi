# Entitled temporal observations and opaque body IDs

**Status:** done

## Outcome

Typed observation packets expose no hidden death time through body handles.
Complete model-facing removal, including opening descriptions, is implemented
in the default-OFF temporal experiment; OFF prompts retain the known exposure
until an adopting decision. The semantic
leak gate rejects invented audible cues. An explicitly versioned, default-OFF
temporal observation mode delivers event-local movement, witnessed kill/vent,
and own-kill evidence once at its source tick, before a triggered meeting.

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
  omits that ID, but independent review reproduced the internal ID in a genuine
  opening prompt: seed1/7p1i/1task reports `body-p-3-4` at discovery tick8. This
  is a demonstrated exposure, not demonstrated model exploitation. Report intents
  round-trip the ID, and tactical body selection sorts it.

## Acceptance

- [x] Record an entitlement matrix for each observation channel: source state
  or event, event time, delivery time, recipient, permitted fields, and memory
  citation. Distinguish death, discovery, public dead-roster announcements,
  witnessed kills, and the killer's own knowledge.
- [x] Reproduce movement and same-tick meeting cases through the actual runner
  and reconstruction, including observer arrival/departure, action ordering,
  same-tick vent/report, killed/ejected witnesses, and later delivery. Identify
  missing evidence separately from duplicate evidence and stale timestamps.
- [x] Implement event-local movement witnesses under the existing sequential
  engine clock and source-time event delivery before meetings. The default-OFF
  version preserves current prompt/detector behavior; ON live and replay paths
  agree without duplicate citations or belief updates, including dead witnesses.
- [x] Implement a deterministic public body-handle scheme and report translation
  that reveals no hidden death time. Check repeated discovery/reporting,
  selection order, multiple bodies, invalid handles, and legacy reconstruction.
  Evaluate `body-{victim_id}`: victim identity is already public and each victim
  dies once. Translate at the privileged action boundary and preserve lexical
  ordering for custom multi-digit rosters. Hashing a small enumerable
  secret-bearing ID is not an opacity guarantee.
- [x] Add meaningful audible entitlement controls: genuine active/inactive
  alarms, invented cues, wrong room attribution, duplicates, and allowed
  recipients. A planted violation must fail the semantic scan.
- [x] Preserve historical replay actions, hashes, prompts, and interpretation.
  Stamp temporal mode before a run can abort; reject mixed versions and make
  unsupported frozen instruments refuse ON recordings explicitly.
- [x] Focused tests, independent adverse review, the shared full gate, and all
  canonical replay checks pass without rewriting frozen evidence.

## Constraints

The preceding completion/lifecycle gate passed at `5006a32f`. Work on
`codex/cleanup`; root owns integration and shared-file assignment. Follow
`docs/architecture.md` Layering, Enforced boundaries, and Determinism and the
substrate ladder. Keep the engine deterministic and agents engine-free.

The owner authorized event-local entitlement, source-time deltas, and the public
body boundary repair. The card does not authorize a default prompt/detector
change, experiment adoption, or live calls.
Do not reopen fixed reported-body cleanup or duplicate successful reports.
Dead `vent_use_heard` retirement is a separate coupled-consumer census under
roadmap item 37; absence from replay JSONL alone does not establish deadness.

## Expected scope

Engine event witness metadata and its tick producer; observation schemas,
service, audit and version resolver; agent event ingestion and shared witness
belief reduction; orchestration, action translation, replay version/stamp and a
shared reconstruction adapter; `eval/leak_scan.py`, current replay walkers and
directly coupled training/analysis call sites or unsupported-version guards.
Include focused tests, `.env.example`, and the observation subsection of
`docs/architecture.md`. The API owner applies the narrow reconstruction adapter
and raw-field inventory follow-through. Root owns registry-derived doc-fact
follow-through, integration, the index and final status.

## Record impact

The typed packet body handle is an unconditional privacy repair; internal engine body
IDs and recorded report actions remain unchanged after privileged translation.
Opening-trigger body handles change rendered bytes, so they are enabled only
with the default-OFF temporal version. OFF retains the reproduced model-facing
exposure; implementation is not adoption. A temporal perception repair changes
future agent evidence and can change rendered prompts, detector results,
actions, and replay bytes. Record compatibility explicitly; prompt/detector
differences remain default-OFF until an adopting record. A narrowly contained
identifier exposure repair may be unconditional with its compatibility
treatment recorded. Preserve current and historical reconstruction contracts;
keep internal engine body identity stable if boundary translation can remove
the exposure without changing truth.

Temporal mode has one default-OFF `temporal_observations` substrate key and an
optional tick-row version omitted on the OFF path. This identifies partial
recordings before any meeting or terminal stamp exists. Readers validate one
consistent version and select evidence reconstruction from the recording.

## Decisions

Snapshots retain their current-state meaning. In temporal mode, a separate
typed event batch contains only witnessed kill/vent/move and the actor's own
kill, stamped with the source event tick. It is delivered after each advance
and before meeting construction, without another tactical decision or a second
whole-packet ingestion. The next ordinary snapshot does not repeat those
actions. Live and reconstruction paths share batch construction and ingestion.
Event-local movement witnesses are derived during sequential action resolution;
they do not alter world state, action order, or the existing serialized event
projection. Audible entitlement remains the current global active alarm alone. The owner
resolved the opening-trigger conflict by preserving OFF/historical bytes and
projecting public handles only ON; default model privacy is explicitly unfinished
until an adopting decision. The full matrix is in
[the observation contract](../../docs/observation-contract.md).

## Validation

Use deterministic offline scenarios and planted packet mutations. Run focused
observation, perception, memory, orchestration and reconstruction tests, Ruff,
strict mypy, and `scripts/validate_task_docs.py` for the card. Root runs
`bash scripts/check.sh` and the canonical replay checks for implementation.
Report mechanics evidence separately from recorded-model analysis or a future
budgeted fresh-model evaluation.

## Results

Implementation passed the combined gate and awaits final owner review; temporal
behavior is **not adopted**. Independent review reproduced and resolved two
additional boundaries: internal IDs in opening descriptions (removed ON,
explicitly preserved OFF), and frozen surrogate features silently accepting ON
sources (now refused). Its independent 12-run OFF/ON sweep checked 210
meeting-agent snapshots for identical live/reader rendered memory, suspicion
maps and complete observation-ID sequences. Engine inputs permit one action per
actor; there is no automatic vent-exit path that could silently collapse two
same-actor vent actions into one source identity.

The channel matrix is in [the observation contract](../../docs/observation-contract.md).
Event-local witnesses use deterministic engine state; serialized engine event
projections and internal body IDs stay unchanged. Typed packets always use
public handles. Record-byte mode controls reconstruction, including incomplete
files. Generic frozen walks, prompt-byte reconstruction, surrogate/conviction
tables, anchor/off-menu and counterfactual consumers refuse unsupported ON
inputs; current report folding and the factory leak sweep support them. Raw
spend/report-row readers retain their separate accounting semantics.

Validation (offline, fake provider):

```sh
UV_CACHE_DIR=/private/tmp/ailibi-consumer-uv-cache uv run pytest tests/engine tests/observation tests/orchestrator/test_game.py tests/orchestrator/test_replay.py tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_meeting_integration.py tests/agents/test_perception.py tests/agents/test_beliefs.py tests/eval/test_replay_walk.py tests/eval/test_evidence_honesty.py tests/eval/test_off_menu.py tests/training/test_anchor_study.py tests/training/test_surrogate_dataset.py tests/meetings/test_prompt_byte_golden.py -q --tb=short
# 853 passed, 31 deselected, 3 xfailed; 84.45 seconds.
UV_CACHE_DIR=/private/tmp/ailibi-consumer-uv-cache uv run pytest tests/observation/test_temporal_observations.py tests/orchestrator/test_temporal_delivery.py -q --tb=short
# Final follow-through: 50 passed.
UV_CACHE_DIR=/private/tmp/ailibi-consumer-uv-cache uv run pytest tests/training/test_env.py tests/experiments/test_probe_backends.py tests/test_firewall.py -k 'not linter and not import' -q --tb=short
# Full-gate integration follow-through: 82 passed, 28 deselected.
uv run python scripts/validate_task_docs.py
# 390 historical tasks/prompts and 23 work cards valid.
uv run pytest tests/scripts/test_check_doc_facts.py -k architecture_note -q
# 2 passed; architecture stays below the existing 1,300-word ceiling.
```

Ruff, format and strict mypy passed for all 32 affected implementation/test
files; the final seven-file follow-through also passed. Import-linter kept all four boundaries (167 files, 889 dependencies),
and `git diff --check` passed. New regressions cover
source ordering, immediate meeting evidence, killed/ejected witnesses, exact-once
citations/beliefs, missing/forged batches, audible violations, body ordering and
report legality, legacy/new profile selection, unsupported instruments and
actual recorded opening prompts. Historical prompt-byte tests remain unchanged
except for explicit refusal of unsupported temporal sources.

The first shared gate exposed 13 stale integration fixtures. The training mask
already executes through the repaired production boundary; its test oracle now
passes the actual state to report translation. The in-vent control uses the
public handle, asserts its internal translation in both states, and still
requires vented rejection versus standing acceptance. The planted visibility
mutation still fails on an unentitled corpse; its diagnostic expectation now
uses the public handle. Probe tests independently pin the expanded default
snapshot and exercise the new toggle's OFF/ON isolation. These changes leave
production legality unchanged. Ruff, format, and strict mypy passed on all
three corrected test files; the shared gate remains the final verification.

Baseline isolation is reproducible without changing the checkout:

```sh
TEMPORAL_BASELINE=$(mktemp -d)
git archive 5006a32f | tar -xf - -C "$TEMPORAL_BASELINE"
cp tests/observation/test_temporal_observations.py "$TEMPORAL_BASELINE/tests/observation/"
TEMPORAL_PYTHON="$PWD/.venv/bin/python"
(cd "$TEMPORAL_BASELINE" && "$TEMPORAL_PYTHON" -m pytest tests/observation/test_temporal_observations.py -k 'hidden_death_time or audible_gate' -q --tb=short)
# 9 fail: death tick still exposed; eight forged/missing audio cases accepted.
(cd "$TEMPORAL_BASELINE" && "$TEMPORAL_PYTHON" -m pytest tests/observation/test_service.py -k 'discovered_body_is_hidden or visible_body_carries_victim' -q)
# 2 historical compatibility controls pass.
```

A fresh baseline/current comparison also ran seed1/7players/1impostor/1task,
FakeProvider and max80 ticks with every AILIBI variable absent. All 27 parsed
replay rows matched after removing only the new terminal
`substrate_flags.temporal_observations=False` key: actions, state hashes,
meeting outcomes, prompt/response bodies and usage were identical. The session
reproducer is `/private/tmp/ailibi-temporal-baseline-proof.py`; the recipe is to
run that identical HeadlessGame configuration in the isolated baseline and
current checkout, remove that one current terminal flag, and compare full
parsed row sequences. No committed recording was rewritten.

Limitations: OFF model prompts still disclose tick-bearing engine body handles;
ON removal and temporal evidence delivery need an adopting decision and any
future authorized evaluation. Mechanical correctness does not establish better
LLM accusations or voting. Frozen instrument refusal prevents false feature
claims; it does not make those instruments temporal-aware.

Final combined verification: `bash scripts/check.sh` passed with 6,599 Python
tests, 20 optional skips, three expected failures, and 467 frontend tests, plus
strict typing, formatting, lint, import contracts, document gates and production
build. `bash scripts/verify_samples.sh` passed all 100 canonical recordings.
The owner’s final branch review, merge and any experimental adoption remain pending.
