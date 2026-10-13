# Code review — orchestrator/ (game loop, boundary, replay format, seeder, scheduler, personas)

Reviewer label: **orchestrator**. Scope: `orchestrator/*.py` (5,106 lines) + `tests/orchestrator/` (8,628 lines, 11 files, 225 tests + 3 xfail).
Read-only review on `main` @ b809b19c, 2026-08-18. Machine load during timings: `uptime` load avg 6.5–8.9 on 10 cores (other reviewers running); all timings are relative/rough.

Legend: **[VERIFIED]** = I ran/observed it; **[JUDGMENT]** = assessment from reading.

---

## 1. Executive read (10 lines)

1. The orchestrator does what the project claims: a deterministic, sorted-iteration tick loop; same seed twice → byte-identical replay AND audit JSONL **[VERIFIED]** (`scripts/run_game.py --seed 42`, 9p2i, `cmp` clean on both files); all 50 committed 9p2i samples re-verify through the state-hash chain in ~2 s **[VERIFIED]**.
2. Its own tests are fast (225 tests in 4 s), behavioural where it matters (trajectory identity recorded vs no-replay, fast vs full RNG policy, replay byte-identity, actor-forgery refusal), give 89 % line coverage of the package, and `mypy --strict` + ruff are clean **[VERIFIED]**.
3. `game.py` (3,193 lines) is a God module carrying seven unrelated concerns: prompt-version registry, five agent Protocols, meeting runner + LLM recording adapter, `apply_meeting_result`, the `HeadlessGame` loop with two run modes, meeting side-record persistence, and the 650-line production `TacticalAgent`. Maintainability index 11 (B), `HeadlessGame.__init__` cyclomatic 21 (D) **[VERIFIED]**.
4. Comment/docstring sprawl is severe and partly stale: `game.py` is 46 % code (1,463 code lines vs 928 docstring + 494 comment lines, 112 "Task N.M" references); `replay.py` is 37 % code. A 5-line dict (`DEFAULT_PROMPT_VERSIONS`) sits under 122 lines of changelog comment **[VERIFIED]**.
5. The replay format itself (`replay.py`) is sound: discriminated-union JSONL, additive optional fields, doubled-file detection, force/AlreadyExists guard, byte-identity carve-outs. Its two provenance stamp classes are copy-paste twins and its eight `read_*` helpers each re-parse the whole file (3.1× measured for the manifest writer's pattern) — small in absolute cost.
6. The substrate-flag "registry" (`_RETIRED_ALWAYS_ON_LEVERS` / `_TOGGLEABLE_LEVER_RESOLVERS`) is 13 constants that are always `True` plus one env read; ~540 lines of tests pin that constants are constants, with stale comments inside them.
7. Env-var configuration is not sprawling *inside* orchestrator (one env read, `AILIBI_IMPOSTOR_ROLL_CALL`, mirrored from the loader to dodge the loader's import-time side effect); the sprawl is upstream (`agents/strategic/prompts/loader.py`), and orchestrator pays for it with a duplicated resolver + an equivalence test.
8. Error handling is fail-loud and consistent (30 raise sites in game.py), but one telemetry claim is false: LLM calls that *succeeded* before a meeting aborts are dropped from the replay, so `compute_cost_usd` under-reports a crashed run **[VERIFIED: $0.10 burned → 0.0 recorded]**.
9. Async usage is minimal and safe (`asyncio.run` per meeting, clients open a fresh transport per call), but the design forbids ever driving a game from inside an event loop and the guard path leaks an un-awaited coroutine (RuntimeWarning) **[VERIFIED]**.
10. Nothing P0. Two P1s (God module; sprawl-with-staleness). The rest is P2 cleanup with clear, local fixes.

---

## 2. Findings (ranked)

### P1-1 — `orchestrator/game.py` is a God module (maintainability)  [VERIFIED metrics / JUDGMENT on remedy]
- **Where:** whole file; structure at `game.py:154` (RosterPreset) … `:3141` (factory).
- **What:** seven concerns in one 3,193-line file:
  | lines | concern |
  |---|---|
  | 154–460 | roster presets + per-model prompt-version registry (`PROMPT_VERSION_SETS`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, `prompt_versions_for_set`) |
  | 487–692 | 5 Protocols (`MeetingRunner`, `MeetingAwareAgent`, `BeliefPersistingAgent`, `ReportedTestimonyAgent`, `MeetingPacingAgent`) |
  | 694–1097 | `_RecordingLLMClient`, `DefaultMeetingRunner`, `build_default_meeting_runner`, `_build_participants` |
  | 1100–1290 | `_validate_runner_result`, `apply_meeting_result` (the seam every replay consumer re-uses) |
  | 1302–2082 | `HeadlessGame` + result/trace dataclasses (two run modes) |
  | 2084–2495 | meeting side-record helpers, belief fold fan-out, trigger builder, `_drive_async` |
  | 2498–3160 | `KillWitnessRecord`, `BodyProximityRecord`, `TacticalAgent` (production agent), factory |
- **Evidence:** `radon mi` → game.py 11.33 (B; every other file A); `radon cc` → `HeadlessGame.__init__` D(21), `body_proximity_records_for_meeting` C(18), `apply_meeting_result` C(13). vulture flags nothing dead of substance (`_RecordingLLMClient.calls` property unused, `game.py:709`).
- **Why it matters:** every agent-authored task touches this file; merge conflicts and "where does X live" cost compound; the production `TacticalAgent` is hidden inside the game-loop module and its own docstring gives a stale reason for being there (`game.py:2557-2560`: "without leaking that wiring back into agents/runtime.py; that file's stubs are owned by future tasks" — `agents/runtime.py:1-16` says it is a TEST-ONLY scaffold never to be wired **[VERIFIED drift]**).
- **Fix sketch:** see §3.

### P1-2 — Comment/docstring sprawl restating task history, with demonstrable staleness  [VERIFIED counts]
- **Where:** `game.py:179-311` (122 comment lines above a 5-line dict), `game.py:340-407` (registry commentary), `replay.py:497-580` (58 comment lines for a 13-string tuple + a 1-tuple), most function docstrings (e.g. `TacticalAgent.suspicion_graph_for_meeting` docstring is 40 lines for a 20-line loop; `sighting_records_for_meeting` 45 lines).
- **Measured:** game.py total 3,193 = code 1,463 / docstring 928 / comment 494 / blank 308 → 45.8 % code, 112 `Task N.M` refs; replay.py 36.5 % code, 61 task refs; personas.py 34 %; scheduler.py 31 %.
- **Staleness found:** (a) `TacticalAgent` location rationale (above); (b) test comments `tests/orchestrator/test_replay.py:707,728` still say "Task 16.8's live default-OFF absence_prior … is the only non-retired lever" while `absence_prior` is in `_RETIRED_ALWAYS_ON_LEVERS` and the live toggle is `impostor_roll_call` **[VERIFIED]**; (c) `run_meeting`'s except-branch comment "so a retry against the same runner does not double-count" (`game.py:823-825`) describes a retry that no caller performs; (d) `hard_evidence_gate_enabled(env)` docstring/comments in `game.py:2688-2707` narrate a lever that "hard-returns True".
- **Why it matters:** the comments encode *history*, not *invariants*; a reader must read the audit trail to find the two lines that do the work; stale statements actively mislead. The history already lives in `audits/` and `tasks/`.

### P2-1 — Successful LLM calls before a meeting abort are dropped; `compute_cost_usd` under-reports  [VERIFIED]
- **Where:** `game.py:819-836` (`DefaultMeetingRunner.run_meeting` except-branch: `self._recording_client.drain()` discards captures) and `game.py:1874-1913` (`_run_and_apply_meeting` records only `extract_parse_failure(exc)` + side records).
- **Repro:** `scratchpad/work/orchestrator/abort_probe.py` — a client whose 3rd call raises `ConnectionError`; calls 1–2 returned `cost_usd=0.05` each. Result: `replay row kinds: ['ReplayEntry','FailedCallReplayEntry']`, `compute_cost_usd(replay) = 0.0`; the only failed row is a zero-spend `deadline_default` marker.
- **Contradicts:** `replay.py:1071-1076` (`compute_cost_usd`: "a crashed run's spend is not silently undercounted") and the audit-gp-2 intent throughout.
- **Fix:** on abort, attach the drained `LLMCallRecord`s to the exception alongside `_MeetingSideRecords` and persist them (either as `failed_call` rows with `error_type="meeting_aborted"` or a partial `meeting` row); or simply do not drain on the exception path.

### P2-2 — `HeadlessGame` mode combinatorics (recorded vs no-replay) are accidental complexity  [JUDGMENT, metrics VERIFIED]
- **Where:** `game.py:1435-1611` (`__init__`: 10 `raise ValueError` guards over `replay_path × rng_hash_policy × tactical_policy_stamp × crew_tactical_policy_stamp × initial_state × audit_log_path`), `run()`/`run_unrecorded()` mirror pairs, `_run_loop(replay: ReplayLog|None, trace: _EpisodeTraceCollector|None)` with 7 `if replay/trace is not None` branches.
- **Why:** invalid combinations are representable, so they must be guarded and tested one by one; each new knob multiplies guards. A `Recorder` protocol (`ReplayRecorder`, `TraceRecorder`, `NullRecorder`) or two small classes (`RecordedGame(seed, map, factory, replay_path, stamps…)` / `UnrecordedGame(seed|initial_state, rng_policy)`) makes the invalid states unrepresentable and deletes ~120 lines of guard+comment.

### P2-3 — Prompt-version registry lives in the orchestrator, coupled to the loader by convention  [JUDGMENT + VERIFIED details]
- **Where:** `game.py:179-460`; consumer `build_default_meeting_runner` (`game.py:911-917`) calls `resolve_prompt_set()` and `build_prompt_renderers(...)` and `prompt_versions_for_set(...)`, each reading `os.environ` independently; the "render-one-stamp-another" invariant (`game.py:420-433`) is guaranteed by *both sides reading the same env at nearly the same time*, not by construction.
- **Also:** three different version-separator conventions inside one frozen mapping (`crewmate_report.v8`, `impostor_report_v6`, `vote_ballot/v7`) **[VERIFIED at game.py:312-317]**; the lockstep with the `Prompt: <id>` marker inside each `.j2` is manual ("Bump the string here whenever the matching template header is bumped", `game.py:184`) and pinned only for one template (`tests/agents/test_strategic_prompts.py:402`).
- **Fix:** move the registry to `agents/strategic/prompts/versions.py` next to the templates; have `build_prompt_renderers` return `(renderers, prompt_versions)` from ONE resolution; add one parametrised test asserting `PROMPT_VERSION_SETS[set][template]` appears in that set's `.j2` marker.

### P2-4 — Duplicated env resolver in `replay.py` to dodge an import-time side effect upstream  [VERIFIED]
- **Where:** `replay.py:92-116` (`_impostor_roll_call_enabled` mirrors `agents.strategic.prompts.loader.impostor_roll_call_enabled` "byte-for-byte") + the CI equivalence test `tests/orchestrator/test_replay.py:573`.
- **Root cause:** the loader builds a Jinja `Environment` at import (`loader.py:238 _ENV = build_environment()`), raising on an unknown `AILIBI_PROMPT_SET` and printing a stderr notice (observed twice per process in my profile run). Fix the loader (lazy env), then delete the mirror + test.

### P2-5 — `_state_hash` is private-by-name but a cross-package public contract  [VERIFIED]
- 8 non-test modules import it (`api/replay_loader.py:167`, `eval/replay_walk.py:183`, `training/env.py:111`, `training/rollout.py`, `training/anchor_study.py`, `training/surrogate/dataset.py`, `audits/workflows/extract_gameplay_facts.py`, `game.py`) plus 18 test files. It is *the* determinism contract. Rename to `state_hash` (keep alias), add to `__all__`, and pin a golden `state_hash(seed_initial_state(...))` hex so serialization drift is caught by a unit test and not only by the committed-sample walk.

### P2-6 — `_action_order_key` does dead work  [VERIFIED]
- `action_ordering.py:34-40` sorts by `(actor, type, json.dumps(payload))`, but `_validate_unique_actors` (line 15) already guarantees unique actors, so `type`/payload never break a tie. Property probe (`scratchpad/work/orchestrator/order_probe.py`): 2,000 random batches, actor-only sort ≡ full-key sort; 21.6 µs vs 0.7 µs per 9-actor tick. Cost is negligible in absolute terms; the finding is that the code claims an ordering rule it never exercises.

### P2-7 — `_drive_async` leaks the coroutine on its guard path; game cannot run inside an event loop  [VERIFIED]
- `game.py:2472-2495`: when a loop is already running it raises without closing `coro` → `RuntimeWarning: coroutine 'run_meeting' was never awaited` (reproduced with `-W error::RuntimeWarning`). The branch is uncovered (`--cov` missing 2486) and no test names it. `asyncio.run` per meeting also means `HeadlessGame.run()` can never be called from FastAPI/Jupyter/an async harness. Fix: take a coroutine *factory* (`Callable[[], Coroutine]`) or `coro.close()` before raising; longer term, make `run` async-capable.

### P2-8 — Retired-lever residue  [VERIFIED]
- `agents/memory/beliefs.py:292-313` `hard_evidence_gate_enabled(env)` → `del env; return True`; `TacticalAgent.suspicion_graph_for_meeting(self, *, env=None)` (`game.py:2666`) threads a dead parameter with a 40-line docstring explaining why. `_RETIRED_ALWAYS_ON_LEVERS` (13 keys) is stamped `True` on every game_over row forever. `tests/orchestrator/test_replay.py:212-750` (~540 lines, 14 tests) assert that constants are constant. Keep the stamp (provenance) but collapse the tests to one, delete the dead kwarg, and stop threading `env` where nothing reads it.

### P2-9 — Duplication in `replay.py`  [VERIFIED]
- `TacticalPolicyStamp` (`replay.py:236-303`) and `CrewTacticalPolicyStamp` (`:344-389`) are field-for-field identical incl. validator; a shared base with two subclasses keeps the type distinction with one definition.
- Eight readers (`read_replay_entries`, `read_meeting_entries`, `read_failed_call_entries`, `read_game_outcome`, `read_substrate_flags`, `read_tactical_policy_stamp`, `read_crew_tactical_policy_stamp`, `read_policy_stamps`, `compute_cost_usd`) each call `read_all_entries` (full pydantic parse). `scripts/_manifest_writer.py:261-270` calls five per replay: 12.7 ms vs 4.1 ms single parse (3.1×) on a 700 KB sample. Suggest one `ReplaySummary.from_path()` walk.
- In `game.py`, the `LLMCallFailure → record_failed_call(10 kwargs)` mapping is written out three times (`:1874-1888`, `:2136-2151`, `:2202-2229`); a `ReplayLog.record_llm_failure(meeting_id, tick, failure, *, error_type, message, rendered_vote_max)` collapses them.

### P2-10 — Three strict-xfail tests have been dead since Task 13.8 (~2 months, 6 phases)  [VERIFIED]
- `tests/orchestrator/test_meeting_integration.py:2452-2620` (`TestEmergencySuspicionMeetingEndToEnd`, 3 tests + ~200 lines of scenario scaffolding) xfail(strict) "until Wave B redesign lands". Phases 13.5–19 have closed; nothing redesigned them. Either delete or re-scope; strict xfails that never flip are dead code with a green badge.

### P2-11 — Test-quality items  [VERIFIED]
- Tautological pins: `test_game.py:756` (`DEFAULT_NUM_PLAYERS == 4`), `:835` (`DEFAULT_TASKS_PER_CREWMATE == 2`).
- Implementation-detail spies: `test_game.py:762-832` monkeypatch `orchestrator.game.seed_initial_state` to assert a kwarg was threaded, instead of asserting the seeded state has N tasks per crewmate.
- 9 hand-rolled fake LLM clients (`async def complete` ×4 in `test_meeting_integration.py`, ×5 in `test_game.py`; 32 across 8 test files repo-wide) each re-typing the 7-kwarg signature; one configurable `ScriptedLLMClient` in `tests/_helpers/` would do.
- Missing pin: `ActionIntent` and `Action` unions are structurally identical today (json-schema modulo class names **[VERIFIED]**) and `translate_action_intent` relies on it, but no test asserts the parity; drift would surface only at runtime on the first rare intent kind.
- A gameplay test lives in the loop's test file (`test_headless_game_seed_0_impostor_does_not_oscillate_after_kill`, `test_game.py:564`) — belongs with `agents/tactical`.

### P2-12 — Small perf/hygiene  [VERIFIED]
- `assign_personas` re-reads and re-validates `data/personas.json` on every meeting (`personas.py:215`, called from `_build_participants` `game.py:1039`); trivial cost (12 ms / 76 meetings) but pointless.
- `build_default_meeting_runner` → `build_prompt_renderers` compiles a fresh Jinja `Environment` per game: 100 `compile()` calls over 20 games ≈ 10 % of a fake-provider run (0.39 s / 3.9 s). Cache per prompt set.
- Meeting-side cost when a real provider is used: per-tick engine + hashing is ~0.4 ms/tick (`_state_hash` 0.255 s / 629 ticks); the loop is not the bottleneck — the LLM is.
- `_infer_role_from_policy` + optional `role` in `TacticalAgent.__init__` exist "because legacy Phase-2 tests construct without it" (`game.py:2582-2588`) — fix the tests, require `role`.
- `TickScheduler` (`scheduler.py`, 35 lines, 31 % code) is a class + module for `current_tick < max_ticks`, "reserving a boundary" for a live mode that does not exist.
- `seeder.py:146` and `:237` create two `random.Random(seed)` streams from the *same* seed for roles and tasks (correlated shuffles). Harmless (different list lengths) but a `seed ^ NAMESPACE` split like personas uses would be cleaner; must not change now (byte-identity).

---

## 3. Architecture / design assessment

**Well-designed (keep):**
- The seam `ActionIntent → translate → order → advance_tick → record` is small, pure, and fully covered (`boundary.py`, `action_ordering.py` 100 % coverage). Sorted iteration everywhere (`_build_agents`, `_build_packets`, `_collect_intents`, `_build_participants`, belief fold, pacing fan-out) — I found no unseeded RNG, wall-clock, or set-order hazard in the package **[VERIFIED grep + run-twice]**.
- `apply_meeting_result` as the single, engine-free-input, engine-owned-output function that every consumer (loader, eval walkers, training) re-applies is the right shape and the doc says so honestly (incl. the "Historical note").
- Fail-loud posture at the trust boundaries: actor forgery (`_collect_intents`), runner result drift (`_validate_runner_result`), replay path collision (`AlreadyExistsError`), doubled-file detection, `MeetingAwareAgent` isinstance at participant build.
- Replay format: additive optional fields with omit-when-None carve-outs; per-tick hash + roster sidecar as the de-facto version; `FailedCallReplayEntry` de-dup on the frozen entry. Legacy rows still parse (tests prove it).
- Side-records-on-exception (`_MeetingSideRecords`) keeps the `MeetingRunner` Protocol stable while persisting defaults from an aborted meeting — a neat pattern (it just needs to carry the successful calls too, P2-1).
- The recorded/no-replay trajectory-identity tests (`test_no_replay_mode.py`) are exactly the kind of behavioural pin this codebase needs.

**Accidental complexity:**
- Mode flags on one class (P2-2); a version registry that belongs to the templates it versions (P2-3); a mirrored env resolver (P2-4); provenance stamps as twin classes (P2-9); a 13-constant "registry" whose only remaining behaviour is `dict.fromkeys(..., True)` (P2-8); ordering keys that can never tie-break (P2-6).
- Comments as changelog. The project has `audits/` and `tasks/`; the source should carry the invariant and a pointer, not the narrative.

**Refactor I would do (in order, each independently landable, byte-identity preserved):**
1. **Split `game.py`** into `orchestrator/protocols.py` (5 Protocols), `orchestrator/meeting_runner.py` (`_RecordingLLMClient`, `DefaultMeetingRunner`, `build_default_meeting_runner`, `_build_participants`, side-record helpers, `_build_meeting_trigger`), `orchestrator/meeting_apply.py` (`apply_meeting_result` + `_validate_runner_result`), `orchestrator/game.py` (`HeadlessGame` + results, ~800 lines), and move `TacticalAgent` + the two record dataclasses to `agents/tactical_agent.py` (requires `SuspicionEntry` → `meetings/schemas.py`, since `agents` may import `meetings.schemas` but not `meetings.manager`; `PlayerId/RoomId/Role` are str aliases already available on the observation side) and delete the dead `agents/runtime.py`. Re-export from `orchestrator.game` for one phase.
2. **Move the prompt-version registry** to `agents/strategic/prompts/versions.py`; make `build_prompt_renderers` return renderers + versions from one resolution; add the marker-parity test.
3. **Recorder strategy** for recorded/no-replay (P2-2); collapse the constructor guards.
4. **Comment diet**: replace each "Task N.M (date; audit …) …" block with one line + pointer; target ≥ 65 % code lines in `game.py`/`replay.py`.
5. Small: promote `state_hash`; base-class the stamps; one `ReplaySummary` walk; fix `_drive_async`; drop the `_action_order_key` payload component (or, if the "future async dispatch" really wants payload ordering, remove the unique-actor precondition — pick one).

---

## 4. Test assessment (tests/orchestrator/, 225 pass / 3 xfail, 4 s)

- **Strengths:** behavioural coverage of the loop's contracts (byte-identity, trajectory identity, forgery refusal, meeting dispatch/pause, redistribute-rule resim, deadline/validation defaults recorded end-to-end incl. abort-after-default, single-write guard, doubled-file detection, legacy-row parsing, seeder invariants, persona disjointness/role-neutrality). Package coverage 89 % from its own tests; the uncovered lines are the `initial_state` guards (covered by `tests/training`), the conviction accessors (covered elsewhere), and the `_drive_async` guard (uncovered anywhere).
- **Weaknesses:** (a) ~540 lines pin the substrate-flag graduation history; (b) tautological constant pins; (c) monkeypatch spies on internal wiring; (d) 9 bespoke fake clients; (e) 3 strict xfails frozen for 6 phases; (f) `test_meeting_integration.py` at 2,896 lines mixes unit (apply_meeting_result), integration (full game), and gameplay scenarios; (g) no `ActionIntent`/`Action` schema-parity pin; (h) no unit golden for `_state_hash` (only the committed-sample walk protects it); (i) test comments have drifted (P1-2b).
- **Net:** trustworthy as a regression net for the loop; expensive to read; would shrink ~30 % with a shared client helper and the history-pin collapse without losing a real check.

---

## 5. Recommendations (prioritised)

1. **Split `game.py`** per §3.1 (P1-1). Highest leverage; mechanical; keep re-exports one phase.
2. **Comment diet with a staleness pass** (P1-2): fix the four verified stale statements now; convert history blocks to one-line pointers.
3. **Persist successful calls of an aborted meeting** (P2-1) — small change in `run_meeting`'s except branch + `_run_and_apply_meeting`; add the abort-probe as a test.
4. **Move the prompt-version registry next to the templates + one marker-parity test** (P2-3); fix the loader's import-time env build and delete the mirrored resolver + equivalence test (P2-4).
5. **Recorder strategy** for the two run modes (P2-2); collapse the 10 constructor guards.
6. **Test hygiene**: delete/redesign the 3 strict xfails; collapse the substrate-flag tests to one; add the `ActionIntent≡Action` schema pin and a `state_hash` golden; introduce `tests/_helpers/llm.py::ScriptedLLMClient` (P2-10/11).
7. **Small mechanical cleanups**: promote `state_hash`; stamp base class; `ReplaySummary` single walk; `_drive_async` coroutine-factory; drop dead `env` kwarg / payload sort key; cache persona bank + Jinja env per set (P2-5..9, P2-12).

---

## Appendix — evidence artefacts (all under scratchpad/work/orchestrator/)
- `prof.py`, `prof2.py` — cProfile of 1 and 20 fake-provider 9p2i games (4.03 s / 609 ticks; jinja compile 0.39 s; `_state_hash` 0.255 s).
- `order_probe.py` — 2,000-batch property (actor-only ≡ full-key) + timing.
- `abort_probe.py` — meeting abort on 3rd call; `compute_cost_usd == 0.0` despite $0.10 burned.
- `lines.py` — code/doc/comment/blank census + Task-ref counts.
- `det/` — run-twice replay + audit byte comparison (`cmp` clean).
- Commands: `uv run pytest tests/orchestrator -q` (225 passed, 3 xfailed, 3.99 s); `uv run --with pytest-cov pytest tests/orchestrator --cov=orchestrator` (89 %); `uv run mypy orchestrator/` (clean); `uv run ruff check orchestrator tests/orchestrator` (clean); `uv run --with radon radon mi/cc orchestrator/`; `uv run --with vulture vulture orchestrator/`; `bash scripts/verify_samples.sh replays/samples/9p2i` (50/50 clean, 2.2 s).
