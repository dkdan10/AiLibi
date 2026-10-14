# Restructure Impact Map — 2026-06-04 02:23

Read-only blast-radius map for the next-baseline restructure (per-player tasks +
9p/2i roster + meeting accusation-chain), synthesized from six touchpoint lenses
(A–F) plus two completeness critics. Every touchpoint cites a concrete
`file:symbol` confirmed in the tree at this commit. The owner has CONFIRMED all
three change items and the substrate reset (both committed sets re-recorded, the
frozen 4p/1i reference re-baselined). This document feeds the DESIGN.md rewrite
and the task dispatch; it edits nothing.

## 1. Restructure + substrate-reset summary

Three coupled changes land as one baseline:

1. **Per-player tasks (re-key).** `WorldState.tasks` is today a single
   `Mapping[TaskId, TaskState]` with the engine asserting `TaskState.id == <dict
   key>` (`engine/tick.py:111`). The seeder `orchestrator/seeder.py::_build_tasks`
   deals DISTINCT map task ids via a flat cursor and **fails loud** when
   `num_crewmates * tasks_per_crewmate > len(game_map.tasks)` (= 12,
   `seeder.py:196-204`). The change removes that cap so multiple crewmates can hold
   the same map task with INDEPENDENT progress; the task-win count and the on-disk
   task key shape both change.

2. **9p/2i roster (was 7p/2i).** Parity now reaches at 5 crew deaths (7 crew). At
   `tasks_per_crewmate=2` this needs `7 * 2 = 14 > 12` distinct ids — so **9p/2i is
   literally un-seedable today**; the per-player re-key is a HARD PREREQUISITE, not
   a parallel change.

3. **Meeting accusation-chain.** Replace the parallel N-reports + fixed
   `round_count` statement loop + N-vote protocol with a conversational chain
   (reporter accuses-or-unsure → accused counter-claims → continue to N turns,
   terminate early on convergence → opt-in info-share for non-speakers → vote).
   Fewer LLM calls; the meeting RECORD format changes.

**Substrate reset (two independent byte-breakers, ONE coordinated re-record):**
- The task re-key changes `_serialize_world_state` → every game's per-tick
  `state_hash` changes → ALL committed replays stop reconstructing.
- The meeting reshape changes `MeetingReplayEntry.transcript` (`extra='forbid'`) →
  every committed meeting row stops validating.

Either alone forces a re-record; both must share ONE re-record and ONE versioning
decision, because an intermediate PR that re-records only one set leaves the other
with un-reconstructable data. The replay JSONL is currently UNVERSIONED; the only
`format_version` in the system is `eval/report_schema.py::CURRENT_FORMAT_VERSION=1`
on the offline REPORT, with a fail-loud `_validate_format_version` that rejects
`value < CURRENT` ("no migration path").

## 2. Touchpoint inventory

Deduped union of all six lenses + the two critics. Grouped by subsystem.
`breaks` = behavior/shape changes; `modify` = edit required; `verify` = re-confirm
under the new model (may be no-op).

### 2a. Task model (per-player re-key)

| file:symbol | change | note |
|---|---|---|
| `engine/world.py::WorldState.tasks` | breaks | Single `Mapping[TaskId,TaskState]`; two crewmates collide on one map id. Re-key to per-instance ownership OR move task-lists onto `PlayerState`. |
| `engine/world.py::_validate_disjoint_namespaces` | verify | `set(self.tasks)` here is the MAP's ids, not `WorldState.tasks`; re-confirm the two namespaces stay distinct after re-key. |
| `engine/entities.py::TaskState` | modify | If instance-keyed, needs an instance id distinct from `map_task_id`; owner already present. Drives serialization + every `.id` reference. |
| `orchestrator/seeder.py::_build_tasks` | breaks | The cap site (`:196-204`). Remove cap; mint instance ids deterministically; the determinism-prefix docstring contract is void. |
| `orchestrator/seeder.py::_assign_tasks (required > len(map.tasks))` | breaks | The precise un-seedable check: `7*2=14 > 12`. Hard prerequisite for 9p/2i. |
| `orchestrator/seeder.py::seed_initial_state` | modify | "each crewmate owns exactly `tasks_per_crewmate` DISTINCT map task ids" contract changes to per-player independent progress. |
| `engine/tick.py::_advance_tasks` | breaks | `:108 tasks.get(task_id)` + `:111 task.id != task_id` assert. Key must be the per-(actor,task) instance or two owners corrupt each other. |
| `engine/tick.py::_apply_do_task` | breaks | `:215 state.tasks.get(payload.task_id)` + `:230 tasks[task.id]=replace(...)`. Must resolve the ACTOR's own instance. |
| `engine/tick.py::_apply_kill` | modify | `:262-263` owner-filter comprehension dropping victim's incomplete tasks; logic survives, key type changes. |
| `engine/tick.py::_task_progress_event` | verify | `:75,:83 task_id=task.id`. Decide whether the event carries the instance id or the map id (frontend/loader look up `game_map.tasks[event.task_id]`). |
| `engine/events.py::event_to_dict (Task* branch)` | verify | Second task-id serialization site (`:205-214`); test-only today but reads the chosen id encoding. |
| `engine/win_conditions.py::evaluate_win_conditions` | modify | `len(state.tasks)` / completed count is the win target; magnitude scales with the removed cap + 9p, rule unchanged. |
| `observation/service.py::_pending_task_id_for_agent` | breaks | Owner-scoped (good for leak) but returns a single bare id; must return the value the agent maps to a room. |
| `observation/service.py::_global_view (tasks_total + task_completion_percent)` | verify | `:244` denominator = `len(world_state.tasks)`; float + count shift, leaks no ownership today. |
| `observation/packet.py::SelfView.pending_task_id` | breaks | The agent-facing id. LEAK: must remain own-task only. Map id keeps `task_locations` + DoTask leak-safe + human-stable. |
| `observation/packet.py::GlobalView.tasks_total` | verify | Crew-visible aggregate; pure count under the larger pool. |
| `observation/public_map.py::PublicMapView.task_locations` | breaks | `Mapping[TaskId,RoomId]` keyed by MAP id; the keyspace pivot — inherently per-map-task, not per-instance. |
| `orchestrator/boundary.py::public_map_from_engine_map` | verify | Built from MAP tasks; unaffected IF the agent-facing id stays a map id. Confirms map-id is the natural agent key. |
| `agents/perception.py::_self_state_payload` | breaks | `:203` renders `pending_task_id` into prompt-facing JSON — the id render site the prompts actually see (distinct from the field + the reader). |
| `agents/perception.py::_global_state_payload` | verify | `:244-245` renders `tasks_completed`/`tasks_total` into prompt JSON; denominator shifts. |
| `agents/memory/store.py::_build_observations (pending_task completion inference)` | verify | Renders "You completed {task}" on the str→None flip; works on any stable per-agent id; rendered string changes. |
| `agents/memory/store.py::_latest_tasks_summary` | verify | "completed / total" aggregate; values only. |
| `agents/tactical/crewmate_policy.py::CrewmatePolicy.decide` | breaks | `task_locations.get(pending_task_id)` → `_do_task(task_id=...)`; the round-trip id must round-trip. |
| `agents/tactical/impostor_policy.py::ImpostorPolicy._idle` | modify | Same do_task round-trip; impostors fake-do for cover (pending is `()` today). |
| `observation/action_intent.py::_DoTaskPayload.task_id` | modify | The id the agent submits — THE keyspace decision; engine resolution must match. |
| `engine/actions.py::DoTaskAction (_DoTaskPayload.task_id)` | modify | Engine-side mirror; must agree with action_intent + `_apply_do_task`. |
| `orchestrator/replay.py::_serialize_world_state` | breaks | Serializes `WorldState.tasks` into the per-tick `state_hash`; new keyspace + extra TaskState fields change the bytes → byte-identity breaks for ALL games. |
| `orchestrator/replay.py::_to_jsonable` | verify | Mapping branch requires STR keys (raises on non-str). A composite `(player,task)` key must encode to a stable string (e.g. `p-3:wires_upper`). |
| `orchestrator/game.py::_apply_meeting_result (ejection task-drop)` | modify | ~`:606` owner-filter comprehension; mirrors `_apply_kill`; key type changes. |
| `api/replay_loader.py::_task_progress` | modify | Owner-scoped; survives; only per-tick hash assertions in `_walk` break (data, not code). |
| `api/replay_loader.py::_tick_view (tasks_*_total)` | modify | `:664-665` count from `state.tasks.values()`; denominator scales. |
| `api/replay_loader.py::_tick_events (TaskCompletedEvent branch)` | verify | `room_id=self._game_map.tasks[event.task_id].room` (~:716) — KeyErrors if event carries an instance id. Pins the event-id decision. |
| `api/replay_loader.py::_agent_memory_view (tasks_completed/tasks_assigned)` | modify | `owned=[t for t in state.tasks.values() if t.owner==pid]`; survives; counts change. |
| `api/schemas.py::AgentMemoryView / TickView task fields` | verify | Per-agent + spectator counts; values change, shape fine. |
| `observation/service.py + frontend api.ts task fields` | verify | `task_completion_percent` derived float + TS mirrors; display only. |
| `scripts/_manifest_writer.py::_validate_roster_is_seedable` | breaks | Probes the SAME cap before writing a sidecar; must drop/relax or it rejects 9p/2i (`14 > 12`). |

### 2b. Meetings (accusation-chain)

| file:symbol | change | note |
|---|---|---|
| `meetings/manager.py::MeetingManager.run` | modify | Rewrite the 4-phase sequencer: chain (reporter→accused→continue, early-terminate) → opt-in info-share → keep `_collect_ballots` + `_tally`. |
| `meetings/manager.py::DEFAULT_ROUND_COUNT / MeetingConfig.round_count` | breaks | Fixed-round contract removed → max-turn cap + convergence rule; `round_count<1` guard + plumbing change. |
| `meetings/manager.py::_speaker_order` | breaks | Round-robin rotation replaced by reactive turn-passing (next = the accused); the `(round_index, insertion_order)` ordering contract is invalidated. |
| `meetings/manager.py::_collect_statement / _collect_reports / _collect_one_report` | modify | Report intake collapses into the opening chain turn + opt-in; statement collection becomes per-turn with the prior turn threaded; fail-soft (7.10) + self-alibi normalization carry over. |
| `meetings/manager.py::_statement_id` | modify | `{meeting_id}:r{round_index}:{speaker}` collides when a speaker takes multiple turns; needs a turn ordinal. |
| `meetings/manager.py::exclude_teammate_accusation_claims / drop_teammate_statement_target / coerce_teammate_ballot_to_skip` | verify | 7.12 firewall guards must wrap EVERY chain + opt-in turn, not just the old statement slot. |
| `meetings/manager.py::_collect_ballots / _tally` | verify | Vote + plurality survive; confirm contradictions recompute over the FINAL chain transcript before voting. |
| `meetings/manager.py::StatementPromptRenderer / ReportPromptRenderer / VotePromptRenderer Protocols` | modify | Statement renderer grows a "who-accused-me / prior turn" input; a separate opt-in renderer is likely needed; opening + vote renderers reshape. |
| `meetings/manager.py::MeetingDeadlines` | verify | Variable chain needs a per-turn deadline + a total-meeting cap; negative/zero guards + sequential-Ollama rationale carry over. |
| `meetings/transcript.py::is_canonically_ordered / _sorted-by-round_index` | breaks | PRODUCTION C-3 impl (`:77` sort key, `:93-95` predicate) keyed entirely on `round_index`. Must be rewritten to chain-turn order. |
| `meetings/schemas.py::Statement.round_index` | breaks | Meaningless in a chain → `turn_index` + `reply_to`/`responding_to` + possibly `turn_kind`. Frozen-schema change ripples everywhere. |
| `meetings/schemas.py::MeetingTranscript` | modify | `(reports, statements)` → either re-purpose statements as threaded turns OR a tri-field `(opening, chain_turns, opt_in)`. The canonical record-format change that forces the re-record. |
| `meetings/schemas.py::ReportDocument` | verify | May fold into the opening turn; `found_body`/`saw_player` OBSERVATIONS feed vote_correctness — must land somewhere in the new record. |
| `orchestrator/replay.py::MeetingReplayEntry` | modify | `extra='forbid'` → old committed JSONL stops validating. De-facto meeting-format-version bump (replay JSONL unversioned). |
| `agents/strategic/reasoner.py::produce_statement` | modify | Becomes the chain-turn producer; `_scan_prompt_inputs` leak scan + `guarded_claims`/`guarded_target` stay on every turn. |
| `agents/strategic/reasoner.py::produce_report` | modify | `:385` body-reporter OPENING call (`:442 schema=ReportDocument`); squarely on the chain path (the opener IS the reporter). |
| `agents/strategic/reasoner.py::produce_vote / _REPORT_ALLOWED_TRIGGERS / _VOTE_ALLOWED_TRIGGERS` | modify | `:540` vote retained but re-sequenced; sibling allow-lists (`:138,:144`) gate report/vote calls. |
| `agents/strategic/reasoner.py::StrategicTrigger / _STATEMENT_ALLOWED_TRIGGERS / _TRIGGER_CALL_KIND` | modify | Needs a chain-turn / opt-in trigger label so calls route to the meeting tier + cost-attribution stays correct. |
| `agents/strategic/prompts/accusation_round.j2` | breaks | Fixed-round framing + v3 gated teammate block → reactive chain-turn template + separate opt-in template; body + version header change. |
| `agents/strategic/prompts/crewmate_report.j2 / impostor_report.j2 / vote_ballot.j2` | breaks | The reporter-opening + vote templates change to the accuse/unsure form; `impostor_report.j2` + `vote_ballot.j2` carry the 7.12 firewall block. Bumping these bumps `prompt_versions`. |
| `agents/strategic/prompts/loader.py::accusation_round_prompt / crewmate_report_prompt / impostor_report_prompt / vote_ballot_prompt` | modify | `:71,:99,:165` opening + vote loaders + the accusation loader add the reactive-turn / opt-in input; `StrictUndefined` fails loud on a missing kwarg. |
| `orchestrator/game.py::DEFAULT_PROMPT_VERSIONS` | modify | `accusation_round.v3` + `vote_ballot/v2` are the recorded revisions; the chain edit bumps them — the provenance marker attributing the re-record. |
| `orchestrator/game.py::DefaultMeetingRunner / build_default_meeting_runner` | modify | Wires the four prompt callables; the chain drops/renames report+statement, adds opt-in, so the constructor + factory signature change. |
| `orchestrator/game.py::report/vote prompt imports` | modify | `:37-39` import the three report/vote callables; the imported renderer set itself changes if templates split. |
| `orchestrator/game.py::_run_and_apply_meeting / _build_meeting_trigger` | verify | `trigger.triggered_by` = chain opener; `_validate_runner_result` + failed-call path protocol-agnostic; confirm reporter-is-first-speaker holds. |
| `eval/report_schema.py::MeetingReport.transcript` | breaks | Imports `MeetingTranscript` by reference; any reshape flows into all four §11.3 metrics + the committed offline report. |
| `eval/vote_correctness.py::_has_kill_witness_chain / _iter` | verify | `:345` reads `transcript.reports[*].observations` (found_body + saw_player). If reports drop/move, evidence-backed ejections silently read as zero. |
| `eval/accusation_calibration.py::_iter_accusation_claims` | modify | `:238,:242` walk `reports[*].claims` AND `statements[*].claims`; re-point to the chain-turn claim location. |
| `eval/alibi_fabrication.py::_iter_impostor_alibis` | modify | `:207,:214` resolve author from `ReportDocument.agent_id` + `Statement.speaker`; the author location moves. |
| `eval/meeting_quality.py::compute_meeting_rate / MeetingRateReport` | verify | Meeting-granularity (not turn); largely survives; re-baseline ejected/skipped expectations on the re-record. |

### 2c. Roster (9p/2i) + leak firewall + balance/eval gates

| file:symbol | change | note |
|---|---|---|
| `orchestrator/game.py::ROSTER_PRESETS` | modify | `:127-129` add/rename `9p2i = RosterPreset(9,2,?)`; `4p1i` stays. Single named-config surface. |
| `orchestrator/game.py::DEFAULT_NUM_PLAYERS / DEFAULT_NUM_IMPOSTORS / DEFAULT_TASKS_PER_CREWMATE` | verify | Stay 4/1/2 — the harness default is the FLAT 4p/1i baseline, NOT the eval roster; the 9p roster is opt-in via preset/flags. |
| `engine/win_conditions.py::evaluate_win_conditions (parity)` | verify | `alive_impostors >= alive_crewmates` fires at 5 crew deaths at 9p/2i; no code edit but the kill-vs-task-race balance shifts. |
| `tests/observation/test_leak_property.py::_ROSTER_PLAYER_IDS / _VALID_IMPOSTOR_COUNTS / _roster_initial_state` | modify | `:58 range(1,8)` (7 players), `:106 tasks={}`. Widen to 9 to guard 2-of-9; the crew-empty `fellow_impostor_ids` invariant is what matters. |
| `eval/leak_test.py::_assert_no_role_bearing_values / crew-empty invariant` | verify | Fixture-driven over 4p/1i scripted games; roster-agnostic; the `:310` firewall assertion is what the property sweep extends. |
| `tests/observation/test_service.py::_multi_impostor_world_state` | verify | 5p/2i firewall fixture; valid at 2 impostors; lifting to 9p optional. |
| `tasks/phase-7.md::Stage-A close gate (meeting_rate>=0.60, >=30 resolved)` | modify | The floors + degeneracy tripwire + 3-attempt/24h stopping rule re-baseline for 9p/2i. |
| `scripts/run_tournament.py::_resolve_roster / --roster-preset choices` | modify | Choices from `sorted(ROSTER_PRESETS)` so `9p2i` surfaces on rename; verify help-text constants. |
| `scripts/run_game.py::_parse_args (no --tasks-per-crewmate flag)` | modify | GAP: exposes `--num-players`/`--num-impostors` but not `--tasks-per-crewmate`; add to drive a single 9p/2i game at the eval count. |
| `eval/balance_eval.py::_resolve_game_budget / _BASE_*/_PER_PLAYER_* TOKENS` | verify | Linear scaling → 9p auto-resolves to 1.75M in / 350K out; 4p stays byte-identical; confirm 9p transcripts fit. |
| `engine/maps/canonical_1.yaml::tasks (12 across 6 rooms)` | verify | Graph movement ignores coordinates → no player-capacity break at 9p. The 12-task pool is the hinge: per-player re-key alone (shared ownership, map stays 12) OR grow the map. |

### 2d. Determinism + format-version + committed-set reset

| file:symbol | change | note |
|---|---|---|
| `orchestrator/replay.py::ReplayEntry / MeetingReplayEntry / GameEndReplayEntry / FailedCallReplayEntry` | verify | Replay JSONL is UNVERSIONED (only the `kind` discriminator; `_parse_entry` defaults missing `kind`→`tick`). DESIGN must decide: add a `format_version` field (reject/migrate) OR rely on re-record + roster.json. |
| `eval/report_schema.py::CURRENT_FORMAT_VERSION / _validate_format_version` | verify | The ONLY `format_version` (=1), on the REPORT. A bump to 2 rejects committed v1 reports ("no migration path") → REQUIRES regenerating both committed reports + `baseline.json`, not just replays. |
| `api/replay_loader.py::ReplayLoader._walk` | verify | Re-seeds + re-applies, asserts every `state_hash`; rejects ALL old committed replays until re-recorded; generic over roster. |
| `eval/win_condition_selfcheck.py::check_replay_win_condition / first_zero_impostor_tick` | verify | Third reconstruction path; generic over roster; re-runs against new bytes. |
| `scripts/_verify_samples.py::verify_samples / _check_meeting_pre_hashes` | verify | CPU byte-identity verifier; `state_hash_before==tick_hash` cross-check survives; rejects old bytes until re-recorded. |
| `scripts/build_sample_report.py::check_report / build_report / _FLAT_DEFAULT_*` | verify | `--check` diffs committed report vs rebuild; stale until regenerated; `_FLAT_DEFAULT_*`=(4,1,1) hard-code the flat baseline. |
| `scripts/refresh_samples.sh::NUM_PLAYERS/NUM_IMPOSTORS/TASKS_PER_CREWMATE + is_flat_baseline guard` | modify | Doc'd env block updates to 9p/2i; the flat-4p/1i guard refuses non-4p/1i on `replays/samples/`. The operator path driving the re-record. |
| `eval/prompt_regression.py::_seeded_roles / run_prompt_regression` | modify | SOURCE module: `:174-175,:204-207` thread the roster into `seed_initial_state` (roster-sensitive 7→9) AND rebuild over re-recorded meeting seeds (meeting-format-sensitive). Source edit GATES the fixture reset. |
| `eval/benchmark.py::run_throughput_benchmark` | verify | Defaults 4p/1i; runs the full serialization path; the re-key changes per-tick cost. |
| `replays/samples/*.jsonl (4p/1i flat, 50, no roster.json)` | breaks | Frozen reference; both reset vectors invalidate; owner-confirmed re-record. DESIGN must lock what the flat baseline becomes if the canonical roster is 9p/2i. |
| `replays/samples/7p2i/*.jsonl + roster.json + tournament-eval-report.json + MANIFEST.md` | breaks | Re-recorded to 9p/2i; `roster.json`→`{9,2,?}`; dir-rename decision (`7p2i`→`9p2i` cascades to 3 path literals). |
| `replays/samples/tournament-eval-report.json + MANIFEST.md (flat)` | breaks | Embed the round-based transcript + provenance; regenerate post-re-record. |

### 2e. Tests + fixtures

| file:symbol | change | note |
|---|---|---|
| `tests/_helpers/world_state.py::scripted_initial_world_state` | breaks | Highest-fan-out fixture: hand-builds `tasks={'swipe_card':TaskState(id=...)}` keyed by `TaskId`; feeds `determinism_test`, `leak_test`, `test_replay`. |
| `tests/fixtures/scripted_game_basic_tasks.json` | verify | `do_task` payloads ref `swipe_card`/`submit_scan`; survive IF `task_id` stays the action key (only `state_hash` re-records). DESIGN decides do_task addressing. |
| `tests/fixtures/scripted_game_kill_report_meeting.json / scripted_game_vent_and_emergency.json` | verify | Drive determinism + leak harnesses; replayed `state_hash`es re-record. |
| `eval/determinism_test.py::test_identical_seed_..._byte_identical_replay` | breaks | Compares two FRESH recordings (no committed bytes) → stays GREEN; re-confirm + re-validate `scripted_game_basic_tasks.json` against the new task model. |
| `tests/orchestrator/test_seeder.py::test_..._raises_when_task_pool_exhausted (10p/1i)` | breaks | The 12-cap fail-loud INVERTS once removed; delete/rewrite to the uncapped contract. |
| `tests/orchestrator/test_seeder.py::test_..._assigns_distinct_ids_per_crewmate / _multi_task_uses_flat_cursor / _one_task_assignment_matches_historical_bytes` | breaks | Pin distinct-global-id + flat-cursor + golden (owner,task_id) tuples; rewrite to per-player + new golden tuples. |
| `tests/engine/test_tick.py::test_dead_crewmate_..._dropped / _continuing_task_completes / _kill_removing_last_incomplete_task` | modify | Single-owner `state.tasks['swipe_card']` + drop semantics; per-player keying changes addressing + the win count. |
| `tests/engine/test_win_conditions.py::test_all_alive_owned_tasks_complete_returns_crew_win` | modify | Completed/total denominator changes under per-player progress; CREWMATE_TASKS re-derived. |
| `tests/engine/test_world_state.py::test_..._keeps_public_mapping_field_names (+ copy/mutation)` | modify | `tasks` frozen-Mapping keyed `task-1`; tasks-specific assertions update. |
| `tests/engine/test_map_loader.py::assert len(game_map.tasks) == 12` | breaks | `:209` — the load-bearing constant behind the cap. Breaks if the map grows tasks; otherwise the pin DESIGN must consciously keep. |
| `eval/leak_test.py::_run_scripted_game over _SCRIPTED_GAMES` | breaks | Replays the scripted fixtures; fixture inputs regenerate; scanners stay. |
| `tests/observation/test_leak_property.py::test_observation_packets_never_leak_hidden_information` | breaks | Widen 7→9 (necessary) but `tasks={}` means it never exercises `pending_task_id` under the new keyspace — a fixture WITH per-player tasks is required. |
| `tests/api/test_replay_loader.py::test_committed_7p2i_set_reconstructs_byte_identically` | breaks | `_COMMITTED_7P2I_SEED_COUNT=50`, roster `{7,2,2}`, `{p-1..p-7}`, `_GATE_MIN_RESOLVED_MEETINGS=30`; all reset on 9p/2i re-record. |
| `tests/api/test_replay_loader.py::test_committed_7p2i_set_holds_crew_firewall / _write_roster` | breaks | Re-seed each 9p/2i seed; firewall holds at 2-of-9; roster/seed-list assertions update. |
| `tests/api/test_replay_loader.py::Task 7.4 hermetic fixtures (_MI_NUM_PLAYERS, _run_multi_impostor_game, wrong-roster matrix)` | modify | Regenerate at runtime; 7→9 + tasks-per-crewmate constants move; the `{7,2,1}` wrong-task case interacts with the removed cap. |
| `tests/eval/test_win_condition_selfcheck.py::test_committed_4p1i_set_holds_the_invariant` | breaks | Reconstructs 50 committed 4p/1i + `eliminations==4`; re-record breaks recon + the hard-coded count. |
| `tests/eval/test_win_condition_selfcheck.py::test_committed_7p2i_elimination_games_hold_the_invariant` | breaks | Re-point to 9p/2i; the skip-when-no-CREWMATE_EJECT path may flip at 9p. |
| `tests/eval/test_win_condition_selfcheck.py::test_wrong_roster_fails_loud_on_state_hash` | modify | Relies on `tasks_per_crewmate=2` diverging a committed-1-task hash; the re-key REDEFINES how tpc maps to ids — the fail-loud mechanism is altered, not just re-pinned. |
| `tests/scripts/test_build_sample_report.py::test_rebuild_matches_committed_flat_4p1i (+ _check_*)` | breaks | Committed replays + derived report reset. |
| `tests/scripts/test_verify_samples.py::_SEED=0/_MEETING_SEED=22 + accusation_round.v2 manifest rows` | breaks | Seed-22 bytes + meeting record shape + provenance string reset. |
| `tests/scripts/test_manifest_writer.py::7p2i routing + accusation_round.v2 / vote_ballot/v1 provenance (lines 64-109, 352-623)` | modify | Roster values 7→9 + the chain prompt-version bump break the provenance rows. |
| `tests/scripts/test_refresh_samples.py::test_dry_run_routes_per_set_for_7p2i` | modify | Exact dry-run roster preview string updates to 9p/2i. |
| `tests/scripts/test_run_tournament.py::test_main_roster_preset_7p2i` | modify | Pins `{7,2,2}` threading; rename/revalue to 9p/2i. |
| `tests/orchestrator/test_game.py::test_roster_presets / test_default_tasks_per_crewmate_constant_is_two` | breaks | Hard-asserts `set(ROSTER_PRESETS)=={'4p1i','7p2i'}` + `RosterPreset(7,2,2)`; closed-set breaks on a 9p/2i preset. |
| `tests/eval/test_prompt_regression.py::test_*_baseline` | breaks | Asserts the summary == `baseline.json[v_a]`; the meeting reshape changes the metric denominators → reset. |
| `tests/fixtures/prompt_regression/{v_a,v_b}/replay-seed-{22,24,26}.jsonl + baseline.json` | breaks | Six frozen 4p/1i bytes (old protocol + old task serialization) + frozen metrics; format bump + per-player tasks + meeting reshape all invalidate. |
| `tests/meetings/test_manager.py::TestAccusationRounds / TestStatementOrderingContract / TestStatementPromptInputs / TestDefaultRoundCount / _make_manager + stub renderers` | breaks | The OLD protocol's primary pin (round_count→statement-count math, cyclic rotation, `(round_index, insertion_order)`); rewrite for chain + opt-in. |
| `tests/meetings/test_manager.py::TestTeammateGuardOnProductionPath / TestAccusationRoundPromptVersionInReplay` | modify | 7.12 guard tests survive logically; assert `accusation_round.v3` + per-round targets → version + chain-flow update. |
| `tests/meetings/test_schemas.py::TestStatement / TestMeetingResult / TestReportDocument` | modify | Pin `Statement.round_index`, `MeetingTranscript{reports,statements}`; assertion-update if names kept, rewrite if not. |
| `tests/meetings/test_transcript.py::is_canonically_ordered tests` | breaks | `(round_index, insertion_order)` ordering contract; redefined/removed. |
| `tests/meetings/test_voting.py::tally / plurality` | verify | Vote survives; confirm candidate set after chain + info-share, SKIP-in-leaders unchanged. |
| `tests/meetings/test_contradictions.py::_report/_statement builders (round_index, task_id="wiring")` | breaks | 20+ `MeetingTranscript(reports=...)` + a `statements=(round_index=...)` case; detector reads transcript shape. |
| `tests/orchestrator/test_meeting_integration.py::test_meeting_record_carries... / TestSeed6ImpostorMeetingCoordination / TestBuildParticipantsFellowImpostorIds` | breaks | Hard-codes 3 reports + 3 statements + 9 LLM calls AND re-seeds seed-6 at 7p/2i; chain changes counts + 9p reseed changes roles/tasks. |
| `tests/orchestrator/test_replay_meetings.py::TestReplayRecordsMeetingArtifacts` | breaks | `round_count=2` → 4 reports+8 statements+4 ballots=16 calls + `accusation_round.v3`; rewrite counts + re-baseline byte-identity. |
| `tests/orchestrator/test_replay.py::ReportDocument validation-error fixtures (lines 143/161)` | verify | `'1 validation error for ReportDocument'` pins the schema NAME; shifts if ReportDocument is renamed. |
| `tests/agents/test_strategic_reasoner.py::produce_statement / produce_report / produce_vote + trigger allow-lists` | breaks | Exercises all three meeting calls + allow-lists; chain changes the opening-report + vote contracts, not only `produce_statement`. |
| `tests/agents/test_strategic_prompts.py::TestCrewmateReportPrompt / accusation_round / vote_ballot renders` | breaks | Renders each OLD template + asserts version markers + `round_index=0`; rewrite to the chain template set + new version strings. |
| `tests/eval/test_vote_correctness.py / test_accusation_calibration.py / test_alibi_fabrication.py::_meeting/_statement/_report builders (round_index=0)` | modify | Every eval-metric transcript builder moves to the chain record shape. |
| `tests/eval/test_tournament_report.py::compute_meeting_rate + _NUM_PLAYERS` | modify | `_NUM_PLAYERS`→9 + re-probe meeting-rate for the new roster + chain (fewer calls). |
| `tests/eval/test_balance_eval.py::7p/2i seeded-roles + budget-scaling pins` | modify | 7→9 where modeling the eval roster; add a 9p budget pin. |
| `tests/eval/test_report_schema.py::_meeting_report (MeetingTranscript(reports,statements,round_index=0)) + transcript-annotation pins` | breaks | Old transcript shape + asserts the transcript field type. |
| `tests/api/fixtures/sample_replay.py::write_meeting_replay / _build_meeting_result / _meeting_entry` | breaks | Shared replay-fixture builder constructing the OLD record (`MeetingTranscript(reports=, statements=())` + ReportDocument); fans out to `test_replay_loader`, `test_eval`, `test_replays`, `test_eval_routes`. The api-suite blast radius the lens undercounted. |
| `tests/api/test_replays.py::get_meeting route test (reporter derivation, line 165)` | breaks | Exercises `/meetings/`; reshapes with the chain MeetingView + reseeds 7→9. |
| `tests/api/test_schemas.py::_statement (round_index=0) / _meeting_view (reports,statements) / tasks_completed_total / tasks_assigned` | breaks | Pins both the meeting-view shape and the task-count DTO fields. |
| `tests/api/test_leak.py::test_dto_inventory_matches_expected (EXPECTED_DTOS)` | breaks | Exact-set assert on `api.schemas.__all__`; any DTO the chain adds/renames breaks it. Leak tripwire. |
| `tests/api/test_leak.py::test_eval_report_field_set_snapshot (EXPECTED_EVAL_REPORT_FIELDS)` | breaks | `:361 round_index`, `:366 statement_id`, `task_id`, `speaker` in the recursive snapshot; BOTH the meeting reshape AND a new per-player-task field trip it. |
| `tests/llm/test_provider.py::_MEETING_SCHEMAS=(ReportDocument,Statement,VoteBallot) / _bad_report_text (round_index:0) / kinds set` | breaks | Validates against the `Statement` schema; the chain edit changes `Statement` → changes the `format=schema` JSON the LLM is constrained by. Whole `tests/llm` layer absent from the union. |
| `tests/llm/test_report_normalize.py::Statement payload (round_index:0)` | breaks | Parse-tolerance (7.6) fixtures pin `round_index`; `llm/report_normalize.py` itself is schema-agnostic (verify-only). |
| `tests/llm/test_real_provider.py::vote_ballot_prompt + report/statement round-trips` | breaks | Real-Ollama (skip-gated) pins the old template + schema contract. |
| `tests/engine/test_rules.py::num_players=7 + tasks_per_crewmate=2 + tasks={} states (lines 158-160)` | modify | Roster literal + tpc thread update 7→9; not in the lens union. |
| `tests/agents/test_perception.py / test_beliefs.py / test_beliefs_wiring.py / test_runtime.py::GlobalView(tasks_*) + SelfView(pending_task_id)` | modify | `task_completion_percent` float denominator + `pending_task_id` encoding shift; only `test_perception` was in the union. |
| `tests/fixtures/memory_rendering/{crewmate_basic,impostor_minimal,tight_budget_drops_low_salience}.json (+ crewmate_basic.expected.md)` | modify | Golden fixtures hardcode `tasks_total:12` + bare-string `pending_task_id`; `.expected.md` pins "You completed {task}". Regenerate. |
| `tests/api/test_eval_routes.py::prompt_versions={"meeting":"v1"} fixture (line 80)` | verify | Stubs a meeting prompt_versions map; consumes the sample_replay fixture indirectly. |

### 2f. Docs + api/frontend mirrors

| file:symbol | change | note |
|---|---|---|
| `DESIGN.md::§5.2 Protocol (446-467)` | modify | Rewrite the 4-phase block into the accusation-chain. DESIGN-thread-owned; MUST land before dispatch (tasks may not edit DESIGN.md — `generate_prompts.py::_constraints_for` hardcodes "Do not modify DESIGN.md"). |
| `DESIGN.md::§5.3 + Appendix A schema sketches (469-493, 903-916)` | modify | Reconcile the ReportDocument/VoteBallot sketches to the new record. |
| `DESIGN.md::§3.5 Win conditions + balance (308-321)` | modify | Task-win count semantics + the dead-crewmate removal rule re-state under per-player; `:321` "hardcoded to one task per crewmate" + the implicit 12-cap go stale. |
| `DESIGN.md::§3.2 State model (270, 297) + §3.3 Task` | modify | `tasks: dict[TaskId, TaskState]` + "global completion counter" describe single-dict ownership; reflect the re-key. |
| `DESIGN.md::§8.1/§8.2 MVP scope (662, 666, 679)` | modify | "5-7 agents; 1 impostor", "structured reports + 2 accusation rounds", "Multiple impostors OUT of scope" all contradict the next baseline. |
| `DESIGN.md::§2 Core Modules map (161-166, 179)` | modify | Module tree lists `accusation_round.j2` + `meetings/schemas.py {ReportDocument,Statement,VoteBallot}`; drifts if templates/schema rename. |
| `DESIGN.md::§3.4 / §11.2-§11.3 (302, 822-846)` | verify | Friendly-fire + leak/balance prose reference roster implicitly; note 9p/2i parity (5 deaths) + 2-of-9 firewall. |
| `api/schemas.py::StatementView (319-328)` | breaks | Shadows `Statement`; carries `round_index` + single `target`. Chain drops/repurposes `round_index`, adds turn semantics. |
| `api/schemas.py::ReportView + MeetingView.reports/statements (309-316, 377-399)` | breaks | The reports/statements split no longer maps 1:1 to the chain record. |
| `api/replay_loader.py::_statement_view (1341-1350) + _report_view (1331-1338)` | breaks | Copy `round_index` + report/statement fields verbatim; break on schema change. |
| `api/replay_loader.py::RosterConfig / _walk defaults / _infer_num_players (198-200, 466-490, 1062-1110)` | verify | Default/sidecar branching is roster-value-agnostic; the new `{9,2,?}` sidecar flows through; re-check fixtures parse. |
| `frontend/src/types/api.ts::StatementView/ReportView/MeetingView (204-266)` | breaks | 1:1 TS mirror (`round_index` :216; reports/statements :259-260); moves in lockstep; caught by `tsc --noEmit`, NOT pytest. |
| `frontend/src/types/api.ts::AgentMemoryView/TickView task fields (283-284, 141-142)` | modify | Per-player + global task counts; semantics shift, types stay int. |
| `frontend/src/components/MeetingView.tsx::StatementsSection (102-149, byRound)` | breaks | Groups by `round_index` into "Round N" headers; the chain has no rounds → chain/turn-order render. |
| `frontend/src/components/MeetingView.tsx::ReportsSection (73-100, 358-371)` | modify | Distinct "Reports (N)" section ahead of statements; folds into the chain thread. |
| `frontend/src/components/StatementCard.tsx (+ ReportCard.tsx, BallotCard.tsx)` | modify | Per-utterance card props shaped to the old DTOs; add a turn-kind/parent cue. |
| `frontend/src/components/ContradictionBadge.tsx::reportClaimEventId / reportObsEventId / statementClaimEventId` | breaks | `:92-101` build cross-link event ids off the report/statement split; shift if the container renames. |
| `frontend/src/components/MeetingPill.tsx` | verify | Filters by tick only; re-check `meeting.tick` survives. |
| `frontend/src/components/ThoughtStream.tsx::MeetingView.llm_calls` | verify | Renders per-meeting calls; the chain reshapes/reduces the set. |
| `frontend/src/store/replayStore.ts::meetingCache: Record<string, MeetingView>` | verify | Type-only edit once MeetingView changes; verify under tsc. |
| `api/routes/replays.py::get_meeting (66-67, response_model=MeetingView)` | verify | Response contract + OpenAPI schema change with MeetingView. |
| `api/routes/eval.py::TournamentEvalReport mirror (meeting_rate, 114-127) + MeetingReport import` | verify | Route-level mirror drifts if a meeting-rate scalar is added/renamed; re-exposes `MeetingReport` one-for-one. |
| `eval/report_schema.py::MeetingReport (132-164)` | verify | Metric-input DTO; chain effect on its fields owned by the eval-metrics work; the DTO-mirror boundary. |
| `replays/samples/MANIFEST.md + 7p2i/MANIFEST.md + 7p2i/roster.json` | breaks | Provenance tables + `roster.json` (`7→9`); dir-rename cascades to 3 path literals. |
| `scripts/generate_prompts.py::_constraints_for (121-150)` | verify | Hardcodes "Do not modify DESIGN.md / AGENT_IMPLEMENTATION.md / tasks/phase-*.md" into EVERY prompt — the ownership-boundary anchor; no code change. |
| `scripts/_task_parser.py::extract_contract + TaskDoc fields (33-49, 121-156)` | verify | The validated contract shape new tasks author against; no parser change (validator gotcha: bold-at-line-start + parenthetical Public types break the scripts). |
| `scripts/validate_task_docs.py::validate_public_types_unique + validate_parallel_file_scope (86-96, 206-231)` | verify | Cross-task gates: Public-types-unique + parallel tasks must not share `files_in_scope` unless dependency-ordered. The heavy overlap on `meetings/schemas.py` + `api/schemas.py` + `frontend/src/types/api.ts` + `api/replay_loader.py` MUST be sequenced or scoped. |
| `AGENTS.md::Source of truth + DoD (14-25, 73-79)` | modify | DESIGN.md authoritative; each task references a §; light touch if §-numbers shift. |
| `AGENT_IMPLEMENTATION.md::Phase 3 meeting tasks + roster prose (364-394) + README.md:11` | modify | Historical build-plan prose ("5-7 agents, 1 impostor"); accuracy, not correctness. |

## 3. Invariant risks

### 3.1 Determinism / byte-identical reconstruction
**Threat:** TWO independent breakers — (a) the task re-key changes
`_serialize_world_state` → every game's per-tick `state_hash`; (b) the meeting
reshape changes `MeetingReplayEntry.transcript` (`extra='forbid'`). Either alone
invalidates both committed sets. There are THREE reconstruction drivers
(`replay_loader._walk`, `win_condition_selfcheck.check_replay_win_condition`,
`_verify_samples`) that each reject all old bytes until re-recorded.
**Mitigation / re-establish:** Land the engine re-key + meeting reshape, THEN do
ONE coordinated re-record of both sets in a single PR (never two sequential
re-records — the intermediate commit would have un-reconstructable data). Keep
`eval/determinism_test.py` (two fresh recordings, no committed bytes) GREEN
throughout as the running guard, re-validating `scripted_game_basic_tasks.json`
against the new task model. Re-green all three drivers on the re-recorded sets.

### 3.2 Leak firewall
**Threat:** (a) `SelfView.pending_task_id` + `GlobalView` aggregate must expose ONLY
the agent's own task + a count — the re-key must keep `_pending_task_id_for_agent`
owner-scoped under the new keyspace. (b) The 7.12 teammate firewall (impostor never
betrays/incriminates/votes a fellow impostor) must wrap EVERY new chain + opt-in
turn, not just the old statement slot; `_scan_prompt_inputs` must still fail loud if
`fellow_impostor_ids` rides a crewmate prompt. (c) The property sweep must actually
exercise 2-of-9 — and `test_leak_property.py` builds `tasks={}`, so widening
`range(1,8)`→`range(1,10)` is necessary but INSUFFICIENT; a fixture WITH per-player
tasks is required to exercise `pending_task_id` under the new keyspace. (d) The api
tripwires `EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` snapshot the exact public
surface and must be updated in lockstep so a leaked field cannot slip in silently.
**Mitigation / re-establish:** Keep `_pending_task_id_for_agent` owner-scoped by
construction; route the firewall guards through a single chain-turn chokepoint so
every turn-kind inherits them; add a per-player-task leak fixture to the property
sweep at 9 players (3-impostor coverage a DESIGN decision); update both api snapshot
tripwires in the same PR as the schema change.

### 3.3 Format-version
**Threat:** The owner plan says "the replay format_version bumps" but the replay
JSONL has NO version field today — bumping is NET-NEW structure on every replay
entry model, not a value edit. Separately, `eval/report_schema.py` has a fail-loud
monotonic gate: bumping `CURRENT_FORMAT_VERSION` 1→2 makes `_validate_format_version`
REJECT the committed v1 reports ("no migration path"), so a bump mandates
regenerating both `tournament-eval-report.json` AND `tests/fixtures/prompt_regression/
baseline.json`, not just re-recording replays.
**Mitigation / re-establish:** DESIGN must decide, BEFORE any replay-format task
ships, ONE of: (1) add a `format_version` field to the replay entry models with a
reject-vs-migrate rule; or (2) rely solely on re-record + `roster.json` (old replays
just fail the `state_hash` check, which they already do). Decide the
`CURRENT_FORMAT_VERSION` bump together; if bumped, schedule the report + baseline
regeneration in the same re-record PR.

### 3.4 Frozen-baseline reset
**Threat:** The frozen 4p/1i flat reference + the frozen `prompt_regression`
baseline (`v_a`/`v_b` replays + `baseline.json` metrics) are owner-approved for
re-record, but the flat baseline's IDENTITY is an open invariant: `_load_roster_config
== None` ⇒ 4p/1i is the ONLY defaulting path. If the canonical roster moves to 9p/2i,
"what does the descriptor-less flat set reconstruct as" couples the roster default
(`DEFAULT_TASKS_PER_CREWMATE=2`), the preset table (`4p1i` overrides to 1), and the
task model — three knobs that must agree or the flat set silently reconstructs at the
wrong task count.
**Mitigation / re-establish:** DESIGN locks whether a 4p/1i reference survives (and
the flat default stays 4p/1i) before the re-record. After the re-record, re-pass
`build_sample_report --check` + `_verify_samples` + the MANIFEST seed-completeness
gate so a partial re-record cannot leave a gate red. The prompt_regression SOURCE
edit (`eval/prompt_regression.py`) gates its fixture reset — they are ONE unit.

## 4. Cross-change couplings

1. **UN-SEEDABLE ROSTER (A ⟂ C are NOT independent).** 9p/2i cannot seed today —
   `seeder.py:196` `required = 7*2 = 14 > 12` fails loud. The per-player re-key is a
   HARD PREREQUISITE for the roster change. They MUST land together (or task re-key
   strictly first); a roster-only task before cap-removal cannot produce a game.

2. **MEETING RECORD CHANGE == LLM OUTPUT-SCHEMA CHANGE.** `Statement` is both the
   meeting record field AND the pydantic schema fed to the provider
   (`reasoner.py:513 schema=Statement` → `ollama_client.py:168 model_json_schema()` →
   `:270 format=`). One `Statement` edit ripples into the Ollama `format=` constraint
   and the entire `tests/llm` parse-tolerance suite (`test_provider.py`,
   `test_report_normalize.py`, `test_real_provider.py`) — which the per-lens split
   (B=record, D=replay, provider=untouched) missed.

3. **ONE format_version, NONE EXISTS ON REPLAYS, TWO byte-breakers.** The re-key
   (changes `state_hash`) and the meeting reshape (changes the transcript) are TWO
   independent byte-breakers that must share ONE coordinated re-record and ONE
   versioning decision. They cannot be sequenced as separate PRs each re-recording
   the sets.

4. **PROMPT-VERSION SINGLE-BUMP.** The meeting redesign edits FOUR templates in
   lockstep — `accusation_round.j2` + `crewmate_report.j2` + `impostor_report.j2` +
   `vote_ballot.j2`. Their markers all land in `MeetingReplayEntry.prompt_versions`;
   `test_verify_samples` pins `accusation_round.v2`, replay/manager tests pin `.v3`.
   Every changed template must bump together or the manifest/replay cross-check fails.
   `impostor_report.j2` + `vote_ballot.j2` ALSO carry the 7.12 firewall blocks, so the
   meeting-format change and the firewall invariant are entangled in the SAME edits.

5. **RENDER-vs-FIELD-vs-READER TASK-ID TRIAD.** The re-key must move
   `agents/perception.py::_self_state_payload` (render) in lockstep with
   `observation/packet.py::SelfView.pending_task_id` (field) and `agents/memory/store.py`
   (reader) — plus the policies' `DoTaskIntent.task_id`. All must agree the id resolves
   to the ACTING agent's own instance, or do_task silently targets the wrong owner.

6. **SOURCE-vs-FIXTURE RESET FOR PROMPT REGRESSION.** `eval/prompt_regression.py`
   (`_seeded_roles` threads the roster; `run_prompt_regression` rebuilds over meeting
   seeds) must absorb BOTH the 7→9 roster move AND the meeting reshape BEFORE its
   committed `baseline.json` can regenerate — the source edit GATES the fixture reset.

7. **`task_completion_percent` DERIVED-FLOAT DENOMINATOR.** `observation/service.py:244`
   computes `tasks_completed / len(world_state.tasks)`. The re-key changes the
   denominator while 9p changes the number of crewmates owning tasks — both move this
   single float (pinned in `test_perception`, flows to the UI). The leak task-count
   agreement (`TickView.tasks_required_total` / `GlobalView.tasks_total` must equal the
   engine total) must be re-proven under BOTH changes at once.

8. **WRONG-ROSTER DETECTION MECHANISM ALTERED.** `test_wrong_roster_fails_loud_on_state_hash`
   relies on `tasks_per_crewmate=2` producing a DIFFERENT hash on a committed-1-task
   set. The re-key changes how `tasks_per_crewmate` maps to seeded ids, so the
   "wrong roster → divergent hash" guarantee is itself redefined — not just re-pinned.

9. **SHARED FIXTURE BUILDER FANOUT.** `tests/api/fixtures/sample_replay.py`
   (`write_meeting_replay` / `_build_meeting_result`) hand-builds the OLD meeting
   record and fans out to `test_replay_loader`, `test_eval`, `test_replays`,
   `test_eval_routes`. The meeting reshape into the api suite is undercounted if only
   `test_replay_loader` is tracked.

10. **VALIDATOR FILE-SCOPE OVERLAP.** `validate_task_docs.py` requires parallel tasks
    not to share `files_in_scope` (unless dependency-ordered) and Public-types unique.
    `meetings/schemas.py`, `api/schemas.py`, `frontend/src/types/api.ts`, and
    `api/replay_loader.py` are touched by both the task-model and meeting work — the
    task breakdown MUST sequence them so the validator stays green.

## 5. Open DESIGN.md decisions to lock before dispatch

DESIGN.md is design-thread-owned (no task may edit it). The §-rewrite MUST precede
dispatch or tasks reference stale sections. Lock these FIRST:

1. **KEYSPACE.** Does `WorldState.tasks` become keyed by a composite `(player,
   map_task)` instance id, or do task-lists hang off `PlayerState`? What is the
   canonical instance-key STRING (`_to_jsonable` requires str keys; the per-tick hash
   must be stable, e.g. `p-3:wires_upper`)? (DESIGN §3.2/§3.3.)

2. **AGENT-FACING TASK ID.** Does `DoTaskAction.payload.task_id` /
   `SelfView.pending_task_id` / `public_map.task_locations` stay keyed by MAP task id
   (leak-safe, human-stable, `task_locations` unchanged) while the engine resolves it
   to `(actor, map_task_id)`? Or does the agent submit the instance id? This decides
   whether the entire agent/observation/policy layer changes or stays — and whether
   the scripted-fixture `do_task` payloads change or only their `state_hash`es.

3. **EVENT/REPLAY TASK ID.** Does `TaskProgressed/TaskCompletedEvent.task_id` carry the
   MAP id (so `replay_loader` `game_map.tasks[event.task_id].room` + the frontend label
   resolve) or the instance id? If instance, every map-lookup consumer needs a map-id
   accessor.

4. **TASK-WIN COUNT + tasks_per_crewmate FOR 9p/2i.** What is `tasks_per_crewmate` for
   the canonical eval roster, the resulting per-player pool size, and the crew-task-win
   count? Does the 12-task map grow, or does the per-player re-key alone (shared
   ownership, map stays 12) carry it? Re-state the §3.5 dead-crewmate removal rule
   under per-player progress.

5. **MAP 12-TASK PIN.** `len(game_map.tasks) == 12` is pinned in `test_map_loader.py:209`
   and is the hinge behind cap-removal. DESIGN consciously keeps it (shared ownership)
   or grows the map.

6. **MEETING RECORD SHAPE (single biggest driver).** Does `MeetingTranscript` keep
   `(reports, statements)` with statements re-purposed as threaded turns (add
   `turn_index` + `reply_to` + `turn_kind`), or get a new `(opening, chain_turns,
   opt_in)` tri-field? Does `ReportDocument` survive (and where do `found_body`/
   `saw_player` OBSERVATIONS live — vote_correctness depends on them)? This single
   decision drives the schema, replay, api-view, all four eval metrics, the LLM
   `format=` schema, and the frontend.

7. **CHAIN TERMINATION RULE (must be DETERMINISTIC for recording).** Exact convergence
   condition ("no new accusation" vs "re-accusation cycle" vs "max N turns") and how
   ties are ordered. The recorded turn list must let a replay walk the chain without
   re-running the LLM (replay reconstructs from the recorded outcome).

8. **OPT-IN MECHANICS + INCENTIVE.** Who is eligible (only non-speakers?), one round or
   order-sensitive, what stops it being a free extra accusation slot for impostors,
   distinct schema/prompt or a flag on a turn? Whether the opt-in backfills non-speakers'
   vote context; whether contradictions recompute at every chain turn + before voting.

9. **statement_id / turn_id SCHEME.** Lock the new id format (encodes meeting + turn
   ordinal + speaker, unique across repeat speakers) BEFORE any consumer — api
   `StatementView` and ballot `primary_reason_id` reference it.

10. **REPLAY format_version FIELD.** The replay JSONL is unversioned. Add a
    `format_version` to the replay entry models (reject vs migrate) OR rely on re-record
    + sidecar? And does `eval/report_schema.py::CURRENT_FORMAT_VERSION` bump 1→2 (which
    forces regenerating both committed reports + `baseline.json`)? (DESIGN §11.4.)

11. **9p/2i NAMING / DIR.** Is `7p2i` renamed to `9p2i` (cascades to `_COMMITTED_7P2I_DIR`,
    `_SAMPLES_7P2I`, `refresh_samples.sh` docs, both MANIFESTs) or reused with 9p
    contents? Is the preset `7p2i` replaced or kept alongside `9p2i` (decides whether
    `test_game::test_roster_presets` set-equality + the old committed set survive)?

12. **FLAT-DEFAULT IDENTITY + EVAL-GATE RE-BASELINE.** Does a 4p/1i reference survive
    (flat default stays 4p/1i)? Do the Stage-A floors (`meeting_rate≥0.60`, ≥30 resolved
    meetings, the degeneracy tripwire, the 3-attempt/24h stopping rule) hold for 9p/2i
    under the fewer-LLM-call chain + 9-player denominator, or re-tune?

13. **LEAK SWEEP SCOPE.** Does the property sweep widen its hardcoded 7-player roster to
    9 (and is `_VALID_IMPOSTOR_COUNTS` / 3-impostor coverage kept), and does it gain a
    per-player-task fixture to exercise `pending_task_id` under the new keyspace?

## 6. Proposed task breakdown

Dependency-ordered dispatch units. **Sequencing rule (owner): land the engine pieces
with unit tests FIRST, then do the combined re-record as a single unit.** The two
byte-breakers (task re-key, meeting reshape) and the versioning decision converge in
ONE re-record PR. DESIGN.md lock (§5) is the gate for ALL of these.

| id | title | depends_on | complexity | sequence note |
|---|---|---|---|---|
| **R-0** | DESIGN.md rewrite + decisions lock | — | Integration | Design-thread-owned; rewrites §3.2/§3.3/§3.5, §5.2/§5.3 + Appendix A, §8.1/§8.2, §2, §11.4. MUST precede ALL dispatch (tasks may not edit DESIGN.md; `generate_prompts.py` hardcodes that). Locks all 13 §5 decisions. |
| **R-1** | Per-player task re-key (engine core) | R-0 | Integration | `engine/world.py` (tasks shape) + `engine/entities.py::TaskState` + `engine/tick.py` (`_advance_tasks`/`_apply_do_task`/`_apply_kill`/`_task_progress_event`) + `engine/events.py`. Land with `tests/engine/test_tick.py` + `test_world_state.py` + `test_win_conditions.py` (incl. a same-map-task two-owners progress-isolation case) GREEN before anything downstream. |
| **R-2** | Seeder cap removal + deterministic instance minting | R-1 | Medium | `orchestrator/seeder.py::_build_tasks`/`seed_initial_state` (remove `:196-204` cap, mint instance ids) + `scripts/_manifest_writer.py::_validate_roster_is_seedable`. Rewrite `tests/orchestrator/test_seeder.py` (invert the exhausted-pool test; new distinct-instance + golden-tuple contract). UNBLOCKS 9p/2i seeding. |
| **R-3** | Task-id propagation: observation + agents + memory | R-1 | Integration | `observation/service.py` (`_pending_task_id_for_agent`/`_global_view`) + `observation/packet.py` + `observation/public_map.py` + `observation/action_intent.py` + `agents/perception.py` (`_self_state_payload`/`_global_state_payload`) + `agents/memory/store.py` + `agents/tactical/{crewmate,impostor}_policy.py`. The render-field-reader TRIAD must move together. Land with `tests/agents/test_perception.py`/`test_beliefs*.py`/`test_runtime.py` + memory-rendering fixtures + the do_task round-trip tests + `tests/observation/test_service.py`. |
| **R-4** | api/frontend task-count mirrors | R-1, R-3 | Medium | `api/replay_loader.py` (`_task_progress`/`_tick_view`/`_agent_memory_view`) + `api/schemas.py` task fields + `frontend/src/types/api.ts` task fields. Display/count only; `tsc` for the TS side. Update `tests/api/test_schemas.py` task-field assertions. |
| **R-5** | 9p/2i roster knobs + CLI/script threading | R-2 | Small | `orchestrator/game.py::ROSTER_PRESETS` (add/rename `9p2i`) + `scripts/run_tournament.py` + `scripts/run_game.py` (add `--tasks-per-crewmate`) + `scripts/refresh_samples.sh` env block. Update `test_game::test_roster_presets`, `test_run_tournament`, `test_refresh_samples`, `test_manifest_writer` roster rows, `test_rules.py` 7→9. Per DESIGN §11 naming decision. |
| **R-6** | Leak firewall at 2-of-9 + per-player-task sweep fixture | R-1, R-3, R-5 | Medium | `tests/observation/test_leak_property.py` (widen `range(1,8)`→9; ADD a per-player-task fixture so `pending_task_id` is exercised under the new keyspace) + re-confirm `eval/leak_test.py` crew-empty invariant. Update `tests/api/test_leak.py::EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` AFTER R-7's schema lands. |
| **R-7** | Meeting accusation-chain protocol + record schema | R-0 | Integration | `meetings/manager.py` (run/`_speaker_order`/`_collect_*`/`_statement_id`/renderer Protocols/deadlines) + `meetings/schemas.py` (`Statement`→turn fields, `MeetingTranscript`, `ReportDocument`) + `meetings/transcript.py` (rewrite `is_canonically_ordered` to chain-turn order). Land with `tests/meetings/test_manager.py`/`test_schemas.py`/`test_transcript.py`/`test_contradictions.py`/`test_voting.py` rewritten GREEN. Independent of the task re-key; can develop in parallel with R-1..R-4 but the COMBINED re-record (R-12) needs both. |
| **R-8** | Meeting prompts (4 templates) + reasoner chain producers + version bump | R-7 | Integration | `agents/strategic/prompts/{accusation_round,crewmate_report,impostor_report,vote_ballot}.j2` (the FOUR bump in lockstep; 7.12 firewall blocks survive) + `prompts/loader.py` + `agents/strategic/reasoner.py` (`produce_report`/`produce_statement`/`produce_vote` + triggers) + `orchestrator/game.py` (`DEFAULT_PROMPT_VERSIONS`/`DefaultMeetingRunner`/imports). Update `tests/agents/test_strategic_prompts.py`/`test_strategic_reasoner.py`. The `Statement` edit changes the LLM `format=` schema. |
| **R-9** | LLM provider parse-tolerance under new Statement schema | R-7, R-8 | Small | `tests/llm/test_provider.py` (`_MEETING_SCHEMAS`, `_bad_report_text round_index:0`, kinds set) + `test_report_normalize.py` + `test_real_provider.py`. `llm/report_normalize.py` is schema-agnostic (verify). Lands because `schema=Statement → model_json_schema() → format=` changed. |
| **R-10** | Meeting eval-metric re-pointing + api meeting DTOs + frontend | R-7 | Integration | `eval/{vote_correctness,accusation_calibration,alibi_fabrication}.py` (re-point `transcript.reports`/`statements` readers) + `eval/report_schema.py::MeetingReport` + `api/schemas.py` (`StatementView`/`ReportView`/`MeetingView`) + `api/replay_loader.py` (`_statement_view`/`_report_view`/`_meeting_view`/`_classify_template_id`) + `api/routes/{replays,eval}.py` + frontend (`MeetingView.tsx`/`StatementCard`/`ReportCard`/`ContradictionBadge`/`ThoughtStream`/`replayStore.ts`). Update `tests/eval/test_{vote_correctness,accusation_calibration,alibi_fabrication,report_schema,tournament_report}.py` + `tests/api/{test_schemas,test_replays,test_eval_routes}.py` + `tests/api/fixtures/sample_replay.py` (shared builder). |
| **R-11** | Replay format_version decision + report-version bump | R-1, R-7 | Medium | Per DESIGN §11.4: either add `format_version` to the replay entry models (`orchestrator/replay.py`, reject/migrate in `_parse_entry`/`ReplayLoader`) or document reliance on re-record + sidecar; and bump `eval/report_schema.py::CURRENT_FORMAT_VERSION` if the transcript reshape demands it. Land BEFORE the re-record so the new bytes are stamped consistently. |
| **R-12** | COMBINED re-record of BOTH sets + regenerate reports/manifests/baseline | R-1..R-11 | Integration | ONE coordinated re-record (never split): `replays/samples/*.jsonl` (4p/1i flat, 50) + `replays/samples/7p2i/`→9p/2i (50 + `roster.json` `{9,2,?}` + dir rename per §11) + both `tournament-eval-report.json` + both `MANIFEST.md` + `tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl` + `baseline.json`. Requires `eval/prompt_regression.py` source edit (roster + meeting) to land WITH this (gates the baseline). Re-green all committed-data tests (`test_replay_loader`, `test_win_condition_selfcheck`, `test_build_sample_report`, `test_verify_samples`, `test_prompt_regression`) + re-run the Ollama eval gate at 9p/2i. |
| **R-13** | Docs + scope reconciliation | R-0, R-12 | Small | `AGENTS.md` + `AGENT_IMPLEMENTATION.md` + `README.md` prose accuracy (5-7 agents/1 impostor → 9p/2i; report/round → chain). Non-blocking accuracy pass after the substrate settles. |

**Why this order:** R-1 (engine re-key) lands + unit-tests GREEN before R-2/R-3/R-4
build on the new shape; R-2 unblocks 9p/2i seeding which R-5/R-6 need; R-7 (meeting
protocol) is independent of the task chain and can develop in parallel but R-8/R-9/R-10
depend on its schema; R-11 (versioning) lands before the re-record so bytes are stamped;
R-12 is the SINGLE combined re-record gated on everything because the two byte-breakers
+ the versioning decision must converge once. `eval/determinism_test.py` (no committed
bytes) stays GREEN throughout as the running determinism guard.

## 7. Lens coverage notes

- **Lens A (task re-key)** traced every read/mutation of task ownership/state and
  correctly pinned the keyspace + agent-facing-id + event-id + win-count decisions. The
  critics added the missing RENDER leg (`agents/perception.py::_self_state_payload`), the
  second event serialization site (`engine/events.py`), the `task_completion_percent`
  derived float (`observation/service.py:244`), the map-12 pin (`test_map_loader.py:209`),
  and the memory-rendering golden fixtures.
- **Lens B (meeting chain)** mapped the full state-machine + schema + four-metric blast
  radius. The critics added the PRODUCTION `meetings/transcript.py` ordering impl (lens
  had only the test), the three non-`accusation_round` templates + their `produce_report`/
  `produce_vote` reasoner paths, and the `Statement → LLM format=` coupling.
- **Lens C (roster)** correctly identified the HARD un-seedable prerequisite and the eval
  gates. The critics added `eval/prompt_regression.py` as the roster-sensitive SOURCE
  module and `test_rules.py` 7→9.
- **Lens D (determinism/format)** established WHY both sets break (two reset vectors) and
  the format_version decision. The critics sharpened that the replay version is NET-NEW
  and that the two breakers must share ONE re-record.
- **Lens E (test census)** walked all of `tests/` + fixtures + frontend and correctly
  noted there is NO frontend test runner (only `tsc --noEmit`). The critics added the
  `tests/llm` layer, `tests/api/fixtures/sample_replay.py` (shared builder fanout),
  `test_leak.py` snapshot tripwires, `test_contradictions.py`, `test_schemas.py`,
  `test_report_schema.py`, the memory-rendering fixtures, and several packet-field tests.
- **Lens F (docs/mirrors)** mapped the non-logic surface + confirmed the task-doc
  machinery needs no code change and that DESIGN.md is hardcoded design-thread-owned. The
  critics added `ContradictionBadge.tsx`, the `api/routes/*` handlers, and the
  `ThoughtStream`/`replayStore` frontend consumers.
- **Confirmed in-tree at this commit:** seeder cap (`seeder.py:196-204`), C-3 ordering
  (`manager.py` docstring + `transcript.py:77,93-95`), `Statement→format=` chain
  (`reasoner.py:513`→`ollama_client.py:168,270`), `format_version` (`report_schema.py:99`
  fail-loud), engine task resolution (`tick.py:108-132,215-263`), leak `range(1,8)` +
  `tasks={}` (`test_leak_property.py:58,106`), `ROSTER_PRESETS` (`game.py:127-129`), all
  four eval metric transcript readers, both api leak tripwires, `prompt_regression.py:174-207`,
  `len(game_map.tasks)==12` (`test_map_loader.py:209`), and `7p2i/roster.json {7,2,2}`.
