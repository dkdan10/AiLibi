# AiLibi code review — track B, area `perf-runtime`

**Scope:** runtime performance of the core loop, measured from the code up.
**Repo:** `/Users/danielkeinan/projects/AiLibi` @ `main` (b809b19c), read-only. Python 3.11 via `uv`, macOS arm64 (10 cores).
**Machine caveat:** other reviewers ran concurrently. `uptime` load average is recorded beside every timing; it ranged **4.3 – 9.8** through the session. All comparative numbers (A/B experiments) were taken back-to-back in one process so the load applies equally to both arms.

---

## 1. Executive read (10 lines)

1. **The core loop is fast and lean.** A canonical 9p/2i game with the fake provider is **~90 ms** (~2.7 ms/tick, ~47 LLM calls); 4p/1i is ~26 ms. 100 games = **10.5 s**. Nothing here is a bottleneck for the project's actual workloads.
2. **Memory per game is trivial** — 1.6 MB tracemalloc peak, ~7 MB RSS above the bare import. The engine is not the memory story.
3. **The two real per-game hot spots are both accidental, both free to fix, and both byte-identity-preserving** (verified by identical replay SHA-256s): a Jinja `Environment` rebuilt per game (**15–19 % of a game**), and a full-log rescan in `MemoryStore.recent()` (**Θ(T²)** in game length).
4. **Agent decision cost is quadratic in game length.** `_collect_intents` measured 0.35 ms/tick at tick 0 rising linearly to 2.11 ms/tick at tick 120. At the default `--max-ticks 1000` budget this is ~20x worse than flat.
5. **Determinism bookkeeping is ~half the engine cost** (`advance_tick` 113 µs → 51 µs with the binary RNG codec) but only ~3 % of a whole game — the documented "43 % of engine cost" note is correct and simultaneously misleading about impact.
6. **The genuinely scary number is not CPU, it is the eval report:** the 100-game tournament writes a **47 MB JSON** that is 99 % verbatim prompts already stored in the sibling replay files it references, and peaks at **584 MB RSS**. A 1000-game campaign extrapolates to ~470 MB of JSON and multi-GB RSS.
7. **A 29 MB `tournament-eval-report.json` is committed to git** and is byte-for-byte duplicated by the 55 MB of committed replays next to it (verified: identical prompt sets).
8. **The 2–5x is available and is not micro-optimization: it is process parallelism.** Games are independent and seeded; an 8-process pool over the same 100 seeds measured **4.98x** under load.
9. **pydantic is not a problem** (1.2 µs per `ObservationPacket`), the **import is not a problem** (0.18 s cold), the **frontend is not a problem** (3.8 s build, 1.3 MB dist), and **`verify_samples.sh` is excellent** (3.14 s to re-walk + hash-verify all 100 committed replays).
10. **The suite is the slowest thing a developer touches**: 320 s serial for 4 596 tests on a 10-core box, with no `xdist`.

---

## 2. Measurement log

All commands run as `uv run ...` unless noted. Scratch: `…/scratchpad/work/perf-runtime/`.

### 2.1 Single game — CLI wall clock

`uv run python scripts/run_game.py --seed N --replay-path <scratch>/…` (fake provider — `build_default_client()` defaults to `FakeProvider` when `AILIBI_LLM_PROVIDER` is unset, `orchestrator/game.py:875-880`).

| roster | seeds | wall (real) | ticks | replay bytes | load avg |
|---|---|---|---|---|---|
| 4p1i (`--tasks-per-crewmate 3` default) | 1,7,13,21,42 | 0.21–0.24 s | 12–18 | 15–21 rows | 7.40 |
| 9p2i (`--num-players 9 --num-impostors 2 --tasks-per-crewmate 2`) | 1,7,13,21,42 | 0.29–0.33 s | 25–47 | 412–669 kB | 6.74 |

Of that wall clock, **0.18 s is process start + import** (§2.5) — so the game itself is 30–60 ms (4p1i) and 110–150 ms (9p2i).

### 2.2 In-process game timing (warm, import excluded)

`work/perf-runtime/prof_game.py`, load avg 6.9:

```
9p2i seed=1  wall= 125.8ms ticks= 47 ms/tick= 2.68 outcome=CREWMATES
9p2i seed=7  wall=  97.4ms ticks= 35 ms/tick= 2.78 outcome=IMPOSTORS
9p2i seed=13 wall=  68.3ms ticks= 25 ms/tick= 2.73 outcome=IMPOSTORS
9p2i seed=21 wall=  74.9ms ticks= 36 ms/tick= 2.08 outcome=IMPOSTORS
9p2i seed=42 wall=  82.0ms ticks= 32 ms/tick= 2.56 outcome=IMPOSTORS
mean 9p2i: 89.7 ms/game
4p1i: 5.7 – 26.5 ms/game (9–19 ticks)
```

**LLM-call counts** (fake provider, parsed out of the replays):

| roster | mean ticks | mean meetings | mean LLM calls/game | max seen |
|---|---|---|---|---|
| 4p1i | 16.2 | 1.0 | 6.0 | 6 |
| 9p2i (5 seeds) | 36.0 | 4.0 | 50.8 | 64 |
| 9p2i (100-game tournament) | — | 3.7 | 46.8 | — |

DESIGN.md:39 targets "≤ 100 LLM calls" per game — **met** (46.8 mean, 64 max observed).

### 2.3 cProfile — one 9p2i game ×3 (top cumulative)

`work/perf-runtime/game9p2i.prof`, 0.585 s / 3 games, load avg 6.9:

```
  0.600  one()                                        (3 games)
  0.599    orchestrator/game.py:1622(run)
  0.597      orchestrator/game.py:1750(_run_loop)
  0.385        game.py:1847(_run_and_apply_meeting)   ← 64 % of a game is the meeting
  0.343          _drive_async / asyncio.run           (12 meetings)
  0.240            meetings/manager.py:992(run)
  0.144              manager.py:1691(_collect_ballots)
  0.142                game.py:2646(render_memory_for_meeting)  (148 calls)
  0.141                  agents/memory/store.py:211(render_for_prompt)
  0.124                    jinja2 get_template
  0.121                      jinja2 loaders.py:107(load)  ← 9 loads = 3 templates × 3 games
  0.092              manager.py:1300(_collect_turn)
  0.092        game.py:971(_build_participants)
  0.080          store.py:1117(_build_observations)
  0.074        game.py:2035(_collect_intents)
```

tottime top-5: `episodic.py:122(<genexpr>)` **391 597 calls / 0.032 s**; `json/encoder.py:205(iterencode)` 0.027; `episodic.py:119(recent)` 5 759 calls / 0.022; `isinstance` 365 270 calls; `dataclasses.replace` 9 366 calls.

### 2.4 cProfile — 10-game 9p2i tournament

`scripts/run_tournament.py --num-games 10 --roster-preset 9p2i`, 2.52 s profiled / 2.43 s real, 132 MB peak RSS, load avg 5.7–7.0:

| component | cum | share |
|---|---|---|
| 10 × `HeadlessGame.run` | 2.126 s | 84 % |
| ↳ meetings (`_run_and_apply_meeting`) | 1.392 s | 55 % |
| ↳ **Jinja template compilation** (`loaders.load`, 30 loads) | **0.405 s** | **16 %** |
| ↳ `_state_hash` (697 calls) | 0.307 s | 12 % |
| ↳ `_to_jsonable` (190 398 calls) | 0.249 s | 10 % |
| ↳ `advance_tick` (586 calls) | 0.193 s | 8 % |
| ↳ `episodic.recent` (18 142 calls) | 0.185 s | 7 % |
| ↳ `observation.build_packet` (2 014 calls) | 0.184 s | 7 % |
| eval fold (report + `_kill_gift_accounting`) | 0.414 s | 16 % |
| ↳ `_kill_gift_accounting` (full engine re-walk per game) | 0.261 s | 10 % |

### 2.5 Cold import

| what | real | load |
|---|---|---|
| `uv run python -c "pass"` | 0.02 s | 8.78 |
| `uv run python -c "import orchestrator.game"` | 0.18 s | 8.78 |

`-X importtime` cumulative: `orchestrator.game` 143 ms — `agents.base` 52, `observation.action_intent` 48, `asyncio` 23, `engine.actions` 16, `agents.strategic.prompts.loader` 15 (jinja2 13 / pydantic 12), `agents.memory.beliefs` 10, `meetings.schemas` 5.7. Nothing pathological; pydantic + jinja2 + yaml are the floor.

### 2.6 Memory

| measurement | value | load |
|---|---|---|
| bare `import orchestrator.game` | 41.7 MB RSS | 5.2 |
| one 9p2i game (CLI) | 48.6 MB RSS; tracemalloc peak **1.6 MB**, retained 0.4 MB | 5.2 |
| 10-game tournament (CLI) | 132 MB RSS, 11 MB on disk | 5.7 |
| **100-game tournament (CLI)** | **584 MB RSS**, 109 MB on disk, **47 MB report JSON** | 5.3 |
| 100-game tournament (in-process, no report write) | 162 MB RSS (~0.5 MB/game marginal) | 5.3 |
| `ReplayLoader` × 50 4p1i samples | 0.31 MB/view retained, 72 MB RSS | 6.8 |
| `ReplayLoader` × 50 9p2i samples | **1.63 MB/view** retained (573 kB on disk → 2.8x), 186 MB RSS | 6.8 |
| `model_validate_json` of the committed 29 MB 9p2i report | 0.08 s, **258 MB RSS** | 5.5 |

### 2.7 ReplayLoader latency

Load avg 6.8. `cache_size` default is 16 (`api/replay_loader.py:176`).

| | mean | p50 | p95 | max |
|---|---|---|---|---|
| 4p1i (50) | 7.5 ms | 7.2 | 11.9 | 13.6 |
| 9p2i (50) | 31.1 ms | 30.3 | 51.4 | 82.6 |
| warm cache hit | **0.21 ms** | | | |

Loader profile (10 × 9p2i): `_walk` 92 %, of which `_agent_visibility_map` 34 %, `build_packet` 31 %, `_state_hash` 27 %, `advance_tick` 18 %, pydantic `validate_python` 10 %.

**Methodology warning worth recording:** my first pass reported 176 ms/replay because `tracemalloc` was running during the timed loop. `tracemalloc` inflated this allocation-heavy path **5.7x**. Never time and trace in the same loop.

### 2.8 FastAPI spectator endpoints (`TestClient`, `AILIBI_REPLAY_DIR=replays/samples`)

| endpoint | warm | payload | cold |
|---|---|---|---|
| `GET /replays` | 2.3 ms | 20 kB | — |
| `GET /replays/{id}` | 2.8 ms | **671 kB** | 15–30 ms |
| `GET /replays/{id}/ticks/5` | 1.7 ms | 2.9 kB | — |
| `GET /replays/{id}/beliefs` | 1.9 ms | 31 kB | — |

### 2.9 `bash scripts/verify_samples.sh`

**3.14 s real, 137 MB RSS**, load avg 7.4. Walks and hash-verifies all 100 committed replays across both sets. This is a very good gate for the money.

### 2.10 Frontend

`cd frontend && npm run build` = `tsc --noEmit && vite build`, load avg 6.4–7.7:

| leg | wall | CPU |
|---|---|---|
| `tsc --noEmit` | 3.01 s | 4.63 s user (166 %) |
| `vite build` (rolldown) | 0.81 s | "built in 239 ms" |
| **total `npm run build`** | **3.22 s** | 5.24 s user (177 %) |

`dist/` = **1.3 MB** (35 assets, 1.03 MB JS). Largest chunks: `MapView` 378 kB (113 kB gz, PixiJS), `react-vendor` 193 kB (61 gz), `index` 134 kB, CSS 59 kB (21 gz). Route-level code splitting is in place (`ReplayPicker`, `TournamentDashboard`, Pixi renderers all split out).

### 2.11 Dev-loop gates

| gate | wall | load |
|---|---|---|
| `uv run mypy .` (warm cache) | 0.54 s — 354 files, clean | 7.9 |
| `uv run pytest tests` (default tier) | **320.6 s**, 4 596 passed / 20 skipped / 317 deselected | 4.7 → 9.2 |
| `uv run pytest tests/engine tests/observation tests/orchestrator` | 13.0 s, 425 passed | 4.6 |
| `AILIBI_RUN_PERF_BENCHMARK=1 pytest tests/eval/test_performance.py` | 1.83 s → **2 308.7 games/min (25.99 ms/game)** at 4p1i | 5.5 |

---

## 3. Findings

### F1 — [P1][VERIFIED, high confidence] A fresh Jinja `Environment` is built per game, so every prompt template is recompiled every game

**Where:** `agents/strategic/prompts/loader.py:204-232` (`build_environment`), `:677` (`build_prompt_renderers` calls it), `orchestrator/game.py:910-911` (`build_default_meeting_runner` calls `build_prompt_renderers` on every construction), and `build_default_meeting_runner` is documented at `orchestrator/game.py:895-899` as *"Production callers construct a fresh runner … per game."*

**What is wrong:** `jinja2.Environment` caches compiled templates *per instance*. A new `Environment` starts with an empty cache, so the 3–4 templates the meeting path renders are re-lexed, re-parsed and re-compiled on **every game**.

**Evidence:**
- 10-game tournament profile: `jinja2/loaders.py:107(load)` = **30 calls, 0.405 s cumulative = 16 % of the whole 2.52 s tournament**. 30 loads / 10 games = 3 template compiles per game.
- Isolated micro-benchmark (`work/perf-runtime/bench_jinja.py`, load 6.4):
  ```
  fresh Environment + compile 4 templates: 15.6 ms/game
  warm cache get_template x4:               0.010 ms/game   (1560x)
  build_environment() alone:                0.012 ms
  ```
- `pstats.print_callers` confirms the loads come from `_load_template` under `crewmate_report_prompt` / `accusation_round_prompt` / `vote_ballot_prompt`.
- The module already builds a process-level `_ENV` at `loader.py:238` — **which the production path never uses**, because `build_prompt_renderers` always makes its own.

**Why it matters:** 13–17 ms of an ~90 ms 9p2i game. Free to remove.

**Measured fix** (`work/perf-runtime/patch_bench.py`, monkeypatch only — nothing in the repo was edited): `lru_cache` on `build_environment` keyed by resolved set name + root:

```
MODE=base   short 9p2i (5 seeds) mean/game= 88.7ms   long 9p2i (2 seeds) mean/game=316.1ms
MODE=jinja  short 9p2i (5 seeds) mean/game= 71.7ms   long 9p2i (2 seeds) mean/game=306.1ms
                                  → 1.24x                                  → 1.03x
```
**Replay SHA-256s were identical across all modes** — the change is byte-preserving, so no re-record is needed.

**Caveat to respect:** the per-game freshness the docstring insists on is about the `GameBudget` and the `_RecordingLLMClient`, not the template cache. The cache key must include the resolved prompt-set name and the `impostor_roll_call` lever so `AILIBI_PROMPT_SET` switching in-process still re-resolves (the PR #203 binding discipline). `Environment` objects are safe to share for rendering.

---

### F2 — [P1][VERIFIED, high confidence] Agent decision cost is quadratic in game length: `MemoryStore.recent()` linearly rescans the whole log, ~30 call sites pass `since_tick=0`

**Where:** `agents/memory/episodic.py:119-122`

```python
def recent(self, *, since_tick: int) -> tuple[EpisodicEvent, ...]:
    """Return events with ``tick >= since_tick`` in append order."""
    return tuple(event for event in self._events if event.tick >= since_tick)
```

`MemoryStore.append` (`episodic.py:95-99`) **already enforces non-decreasing tick order** and raises otherwise — so `self._events` is sorted by tick, and this scan could be a `bisect`. The invariant exists and is unused.

Call sites: 13 in `agents/memory/store.py` alone (`grep -c "episodic.recent(since_tick=0)"` → 13), plus `agents/perception.py:143,284,315`, `agents/tactical/{crewmate,impostor}_policy.py`, `agents/tactical/features.py`, `agents/tactical/learned/{forward,crew_forward}.py`, `orchestrator/game.py:2758,2819,2870,2921,2988,3049`, `api/replay_loader.py:2247`. Each is an independent full pass that materialises a fresh tuple.

**Evidence — the growth curve.** Instrumenting `HeadlessGame._collect_intents` (9 players, `tasks_per_crewmate=12`, two seeds, load 6.9):

```
seed 11 (120 ticks)          seed 5 (120 ticks)
ticks   0- 14: 0.35 ms       0.36 ms
ticks  15- 29: 0.56          0.66
ticks  30- 44: 0.81          0.88
ticks  45- 59: 1.07          1.10
ticks  60- 74: 1.29          1.31
ticks  75- 89: 1.56          1.72
ticks  90-104: 1.81          1.88
ticks 105-119: 2.11          2.18
```

Cleanly linear in tick index (slope ≈ 0.0155 ms/tick²) ⇒ **Θ(T²) total**. Extrapolated to the default `--max-ticks 1000` (`orchestrator/game.py` `DEFAULT_MAX_TICKS`, exposed as `--max-ticks` default 1000 in `run_tournament.py`), the last tick would cost ~15.5 ms and the game ~7.8 s of agent time versus ~0.35 s if flat.

**Evidence — the volume.** A single 119-tick 9p2i game: **5 160 `recent()` calls, 3 158 709 event-visits**, attributed by caller frame:

```
agents/perception.py:284   calls=1080  events_visited=674,668   (_previously_seen_body_ids)
agents/perception.py:315   calls=1080  events_visited=674,668   (_recent_co_presence)
agents/perception.py:143   calls=1080  events_visited=663,457   (per-tick observation-id `seq` counter)
agents/tactical/crewmate_policy.py:304  calls=840  events_visited=471,248
agents/tactical/crewmate_policy.py:361  calls=840  events_visited=471,248
agents/tactical/impostor_policy.py:266  calls=240  events_visited=203,420
```

Three of these are especially wasteful:
- `perception.py:143` scans the entire log to compute a per-tick `seq` counter that the store could maintain in O(1).
- `perception.py:315` `_recent_co_presence` asks for a **5-tick window** (`since_tick=current_tick - BODY_PROXIMITY_WINDOW_TICKS`) and gets a full-log scan.
- `perception.py:284` `_previously_seen_body_ids` rebuilds a set that could be maintained incrementally.

**Measured fix** (monkeypatch: `bisect_left` over a parallel tick list + a cached tuple for `since_tick<=0`, invalidated on append):

```
MODE=base    long 9p2i mean/game=316.1ms   short 9p2i mean/game=88.7ms
MODE=recent  long 9p2i mean/game=247.3ms   short 9p2i mean/game=80.0ms
                        → 1.28x                       → 1.11x
MODE=recent,jinja  long=238.2ms (1.33x)  short=69.0ms (1.29x)
```
Again **byte-identical replay SHA-256s**.

The bisect is the cheap half. The structural fix — one pass over the log building the derived views the 13 `store.py` helpers each rebuild — is where the rest lives (see §5 R3).

---

### F3 — [P1][VERIFIED, high confidence] The tournament is strictly serial over independent games; 8 processes measure 4.98x

**Where:** `eval/balance_eval.py:345` (`for seed in seeds_tuple:`) and `:567`.

Games are fully independent: each gets its own seed, its own `HeadlessGame`, its own `MeetingRunner`, its own `GameBudget`, and its own `replay-seed-N.jsonl`. There is no cross-game state.

**Evidence** (`work/perf-runtime/par.py`, 100 × 9p2i, load avg 4.34 → 5.07):

```
serial   100 games:   9.72s
4-proc   100 games:   2.85s   speedup 3.41x
8-proc   100 games:   1.95s   speedup 4.98x
```

On an idle 10-core box this should land closer to 8x. This is **the** 2–5x the brief asks about, and it is a ~20-line change (`ProcessPoolExecutor` over seeds, results sorted by seed for a deterministic report).

**Caveats:** with a real provider (Ollama) the model server, not the CPU, sets the ceiling — parallelism there should be bounded by the server's concurrency. Determinism is preserved because every game is seeded and writes its own file, but the report assembly must re-sort by seed rather than trust completion order.

---

### F4 — [P1][VERIFIED, high confidence] The eval report duplicates the entire prompt corpus that already lives in the replays it references — 47 MB per 100 games, 29 MB committed to git

**Where:** `scripts/run_tournament.py:1093-1104` (`_emit_report_json` → `eval_report.model_dump_json(indent=2)` into one string, then `write_text`), report model at `eval/meeting_quality.py:2977` (`TournamentEvalReport`).

**Evidence:**

```
100-game 9p2i tournament output dir: 109 MB
  replay-seed-*.jsonl          63 MB
  replay-seed-*.audit.jsonl    16 MB
  tournament-eval-report.json  47 MB     ← 490 kB/game
Peak RSS of the CLI run:      584 MB     (vs 162 MB in-process without the report write)
```

Field breakdown of the report:
```
report.games                47.50 MB  (everything else: 0.00 MB)
  per game: meetings 544.9 kB, roles 0.2 kB, prompt_versions 0.2 kB, cost 0.1 kB, replay_ref 0.0 kB
    per meeting: llm_calls 143.9 kB, ballots 2.0 kB, transcript 1.6 kB
```

So **99 % of the report is `llm_calls[].prompt`** — and each `GameReport` already carries `replay_ref: "replay-seed-N.jsonl"` pointing at the file that holds the same bytes.

**Duplication proven on the committed set** (`replays/samples/9p2i/`, 29.2 MB report + 55 MB replays):
```
report game_id headless-seed-0  replay_ref replay-seed-0.jsonl
n prompts in report: 42   in replay: 42
identical sets: True
prompt bytes duplicated for this one game: 519 kB
```
×50 games ≈ 26 MB of the 29 MB committed report. `.git` is 190 MB / 146 MiB packed; `replays/` is 221 MB working-tree (161 MB `ml_corpus` + 60 MB `samples`).

**Why it matters:**
- **Scaling risk:** a 1 000-game campaign extrapolates to a ~470 MB single Python `str` inside `model_dump_json` plus the model graph. The 100-game run already peaks at 584 MB. This is the most plausible OOM in the codebase.
- **Repo weight:** every clone and every CI checkout carries 29 MB of redundant JSON; loading it costs 258 MB RSS (§2.6) in each test module that reads it.
- **Correctness risk:** two copies of the same bytes can drift; there is already a test whose whole job is to catch a stale committed report (`tests/scripts/test_build_sample_report.py:46` — *"The committed flat 4p/1i tournament-eval-report.json is STALE"*).

**[JUDGMENT] on the fix:** `call.prompt` *is* consumed — `eval/meeting_quality.py:865,1419,1834,2461`, `eval/validity.py:745`, `eval/vj_instruments.py:450`, `eval/watchability.py:1334`, `api/replay_loader.py:2471,2504`. But those read `LLMCallRecord` objects, which the replay reader already produces. The persisted report almost certainly does not need the prompt field; dropping it from the *serialization* (keeping `model`/`input_tokens`/`output_tokens`/`cost_usd`/`response_text`) while keeping the in-memory object intact would shrink the report ~100x. This needs one confirmation pass over the report's consumers before acting — I did not verify every reader.

---

### F5 — [P2][VERIFIED, high confidence] The per-tick determinism hash is 79 % Mersenne-state hex, and `_to_jsonable` re-derives `dataclasses.fields()` on every instance

**Where:** `orchestrator/replay.py:1222-1261` (`_state_hash` / `_serialize_world_state` / `_to_jsonable` / `_stable_json`), `engine/rng.py:117-147` (`EngineRng.snapshot`), `engine/tick.py:565` (`advance_tick`).

**Evidence** (micro-benchmark, load 6.0):
```
rng_state bytes: 6726
rng snapshot FULL(json)   36.2 us    TRAINING_FAST(binary)  12.7 us    ratio 2.8x
_state_hash total        128.8 us  = _serialize 50.5 + _stable_json 66.8 + sha256
serialized json len 16,994 chars; rng hex share 13,452 chars = 79 %
_state_hash WITHOUT rng_state 79.6 us  -> rng_state costs 49.2 us (38 % of the hash)

advance_tick (no actions) FULL          : 112.7 us/tick
advance_tick (no actions) TRAINING_FAST :  50.7 us/tick     ← 55 % of a bare tick
```

So the recorded path spends **~165 µs/tick** (36 snapshot + 129 hash) purely on determinism bookkeeping, versus ~113 µs for the whole `advance_tick`. In the 10-game tournament `_state_hash` is 12 % and `_to_jsonable` 10 % of total.

**What is good here:** this is a *deliberate, documented* trade. The replay format is action-stream + hash-chain (`record_tick` at `replay.py:712` stores only `state_hash`, not the state), which is why replays are small and reconstruction is verifiable. The bytes are frozen by every committed replay, so the encoding cannot change.

**What is still available without touching a byte:**
- `_to_jsonable` calls `dataclasses.fields(value)` on **every dataclass instance** — 190 398 calls in a 10-game tournament. `fields()` builds a fresh tuple each call. Memoizing field tuples per *type* is byte-neutral.
- The same `WorldState` is hashed and (in the loader's verification walk) re-hashed; the hex form of `rng_state` is recomputed each time.

**Doc-vs-behaviour note:** the `advance_tick` docstring (`engine/tick.py:575`) calls the JSON snapshot "~43%-of-engine-cost". Measured it is **55 %** of a bare tick — but only **~3 %** of a whole game (`run_unrecorded` FULL 72.9 ms/game vs TRAINING_FAST 70.8 ms/game, load 5.2). Both statements are true; the docstring invites the reader to over-estimate the lever's value.

---

### F6 — [P2][VERIFIED, high confidence] The observation audit sidecar is mandatory, unconditional, and discarded by its main consumers

**Where:** `observation/service.py:206-207` — `def __init__(self, *, game_map: Map, audit_log_path: Path)`; the parameter is **not** `Path | None`, and `ObservationAuditLog.__init__` (`observation/audit.py:15-17`) immediately does `self._path.parent.mkdir(...)`. `orchestrator/game.py:1596-1599` derives `replay_path.parent / f"{replay_path.stem}.audit.jsonl"` when the caller omits it, so **every recorded game writes one**.

**Evidence:**
- 100-game 9p2i tournament: **16 MB of `*.audit.jsonl`** (20 % of the run's 79 MB of JSONL).
- `training/crew/scorer.py:1620-1624` `_drop_audit_sidecars()` — globs and `unlink()`s them straight after the run.
- `scripts/verify_ml_evidence.py:2239` — *"Audit sidecars (`*.audit.jsonl`) are excluded from the committed tree"*.
- `design/phase-12/stage-0-understand.md:154` — *"`run_tournament.py` never sets it"* (true of the flag; false of the effect — the default derives one anyway).
- Cost: `build_packet` measured **36.6 µs** with a real-file audit and **39.7 µs** to `/dev/null` — i.e. the cost is `model_dump(mode="json")` + `json.dumps(sort_keys=True)` (~10 µs/packet), not the I/O. At ~9 agents × ~35 ticks that is ~3 ms/game plus 160 kB of disk.
- For reference, `compute_visibility_for_player` is only **4.0 µs**, and `ObservationPacket(...)` construction is **1.2 µs** — the audit serialization costs more than the visibility computation it audits.

**Recommendation:** make `audit_log_path: Path | None` a first-class off switch (the plumbing to `os.devnull` at `game.py:1593` already exists for the unrecorded path) and have `run_tournament.py` default it off.

**Nit (P2):** `ObservationService(audit_log_path=None)` fails two frames deep with `AttributeError: 'NoneType' object has no attribute 'parent'` rather than a typed error. mypy catches it in-repo; an external caller gets a confusing traceback.

---

### F7 — [P2][VERIFIED, high confidence] The DESIGN.md §9 perf target is met 570–2 300x over, and the benchmark that "records" it cannot measure the thing the target was about

**Where:** `DESIGN.md:870` — *"Performance pass: target ≥ 1 game/min headless on a laptop."* Harness: `eval/benchmark.py`, gate: `tests/eval/test_performance.py`.

**Evidence:** `AILIBI_RUN_PERF_BENCHMARK=1` → `[perf] 60 games in 1.559s -> 2308.7 games/min (25.99 ms/game)` (load 5.5). 9p2i measures 568 games/min (100 games / 10.55 s).

Two structural problems:
1. `eval/benchmark.py:23-26` **pins `FakeProvider` regardless of `AILIBI_LLM_PROVIDER`**, and its own docstring says it measures "ENGINE + serialization throughput per tick — NOT LLM latency". But "≥ 1 game/min on a laptop" is a *wall-clock, LLM-inclusive* target. The benchmark structurally cannot fail it and structurally cannot verify it.
2. It uses `DEFAULT_NUM_PLAYERS` / `DEFAULT_NUM_IMPOSTORS` (4p1i) rather than the canonical 9p2i eval roster, so the recorded number is for a roster no campaign uses.

**Also stale:** `DESIGN.md:128` — *"the budget per agent per tick is microseconds (rule-based, no LLM)"*. Measured (§F2): ~33 µs/agent at tick 0, ~350 µs/agent by tick 120, and ~1.7 ms/agent extrapolated to the 1 000-tick default budget. True at game start, false by mid-game.

---

### F8 — [P2][VERIFIED, high confidence] Test-suite and test-quality observations in this area

- **The default-tier suite is 320.6 s serial** (4 596 tests) on a 10-core machine, with no `pytest-xdist` in `pyproject.toml`. `scripts/check.sh` runs it plus ruff/lint-imports/mypy/frontend, so the one-command gate is >5.5 minutes and is ~97 % pytest.
- **Slowest items are corpus fixtures, not logic:** `test_recompute_reproduces_every_committed_verdict` 19.08 s, `test_a_fit_corpus_record_keyed_to_other_weights_fails` 11.43 s, `test_crew_factory_passes_the_leak_test_factory_mode` 8.49 s, plus a long tail of 3–8 s *setup* times in `tests/training/`, `tests/eval/`, `tests/agents/` — all reading the large committed corpora (the 29 MB report costs 258 MB RSS to validate, §2.6).
- **`tests/eval/test_performance.py:63 test_perf_benchmark_marker_is_opt_in_skipif` is tautological**: it asserts `perf_benchmark.mark.name == "skipif"` and then re-derives `os.environ.get(...) != "1"` and asserts it `is` the value the module computed from the same expression. It pins an implementation detail of the module it lives in and can never fail for a behavioural reason. Textbook agent-authored over-testing.
- **Registered-but-unused markers**: `pyproject.toml:77-78` registers `slow` and `perf` with the note "carries no default filter … Reserved". `grep -rn "pytest.mark.slow\|pytest.mark.perf" tests/ training/ eval/` returns nothing. Dead configuration reserved for a future that has not arrived.
- **What is genuinely good:** the perf benchmark is correctly opt-in with a *record-only* assertion rather than a hardware-sensitive threshold (`test_records_phase5_throughput`), and a small non-gated smoke test keeps the harness from bitrotting. That is the right pattern; only the tautological marker test and the FakeProvider pin let it down.
- The area's own tests are healthy: `tests/engine tests/observation tests/orchestrator` = **425 passed, 3 xfailed in 12.6 s**.

---

### F9 — [P2][VERIFIED] `_kill_gift_accounting` re-walks every replay through the engine after each game

**Where:** `eval/balance_eval.py:665` → `eval/replay_walk.py:353 walk_replay`. 0.261 s per 10 games = **26 ms/game, +12 % on top of the 213 ms game**, and it round-trips through disk data that was in memory moments earlier.

This is **documented as deliberate** and the reasoning is sound (the §3.5 dead-owner drop means recorded action rows are insufficient; the facts must come from re-running the engine, and the walk verifies every `state_hash` en route). I record it as a cost, not a defect. If the game loop ever needs to be 5x faster, the honest lever is to have `HeadlessGame` surface these facts from the live run (the machinery already exists — `run_unrecorded` returns an `UnrecordedGameResult` with the full trajectory).

---

### F10 — [P2][VERIFIED] Payload and God-module observations touching perf

- `GET /replays/{id}` returns **671 kB** for one 9p2i replay; the viewer loads a whole game up front. Acceptable for a local spectator tool, worth knowing before anyone puts it behind a network.
- `api/routes/replays.py:53` `get_tick` linearly scans `replay.ticks` per request. Fine at 25–50 ticks; O(n) per request by construction.
- `meetings/manager.py` is **3 989 lines with 52 defs** (~77 lines/def) and **55 % prose** (955 comment lines + 1 255 docstring lines). `meetings/transcript.py`: 3 537 lines, 55 % prose. `orchestrator/game.py`: 3 193 lines, 44 %. Much of that prose is history ("Task N.N", "audit gp-2", "PR #203 review") rather than contract. It does not cost runtime — but it is why the meeting path is hard to profile-read, and it is the reason F1 (a per-game `Environment`) survived this long inside a function whose docstring is 34 lines about budget freshness. By contrast `engine/tick.py` is 658 lines at 14 % prose and reads cleanly.

---

## 4. What is genuinely good

1. **Determinism-first replay design.** `record_tick` stores actions + a hash, not state (`orchestrator/replay.py:712`). Reconstruction is a real engine re-walk with per-tick hash verification. This is why a 47-tick 9p2i replay is 557 kB rather than tens of MB — and 92 % of *that* is LLM prompts, not engine state.
2. **The engine is genuinely cheap.** `advance_tick` 113 µs, `compute_visibility_for_player` 4.0 µs, one whole game 1.6 MB tracemalloc peak / 7 MB RSS above import. There is no memory leak and no allocation pathology in the core loop.
3. **pydantic v2 is used correctly and is not a bottleneck.** `ObservationPacket(...)` = **1.2 µs** validated (`model_construct` is actually *slower*, 1.71 µs, so `model_config = {frozen: True, extra: forbid}` costs nothing worth reclaiming). 1.7 % of game time, 10 % of replay loading.
4. **`verify_samples.sh` is an excellent, cheap safety net** — 3.14 s / 137 MB to hash-verify 100 committed replays across both roster sets, with per-set aggregation so a drift in either fails the gate.
5. **`ReplayLoader`'s cache shape is right.** LRU 16 views / 1024 metadata; cold 31 ms vs warm **0.21 ms** (150x). Pagination was added to `list_replays` (Audit G-G-3). At the default cache size a serving process holds ~26 MB of views — sensible.
6. **Real, evidenced perf work has been done before.** `observation/audit.py:26-32` documents replacing a per-packet `open()` with a lazy reused handle after "the Task 5.9 profile surfaced the per-packet open as a hot path". `engine/rng.py`'s `TRAINING_FAST` policy is correctly scoped to the non-recorded path and correctly refused on any replay-writing construction (`orchestrator/game.py:1586-1593`). `HeadlessGame.run_unrecorded` avoids the whole serialization layer for training and measurably saves 18 % (72.9 vs 88.7 ms/game).
7. **Import time is disciplined** — 0.18 s cold for the whole orchestrator, with the floor set by pydantic + jinja2 + yaml, not by the project's own code.
8. **The frontend build is fast and well-split.** 3.2 s total, 1.3 MB dist, route-level chunks with Pixi isolated in `MapView`. `check.sh` even documents ordering the four frontend legs cheapest-signal-first.
9. **mypy `--strict` over 354 files in 0.54 s warm, clean.** Whatever else is true, the type layer is not a drag.

---

## 5. Architecture / design assessment

**Well designed.** The layering is real and it shows up in the profile: `engine/` is small (2 299 lines), pure, and fast; `observation/` is a genuine chokepoint with one `build_packet` entry; `orchestrator/game.py::_run_loop` is a legible seven-step loop; the recorded and unrecorded paths share `_run_loop` with `replay`/`trace` as the only difference. The replay contract (actions + hash chain) is the single best decision in the codebase from a performance standpoint — it is what makes 100 replays verifiable in 3 seconds.

**Accidental complexity, in priority order.**
1. **Per-game construction of process-level resources** (F1). `build_default_meeting_runner` conflates three lifetimes — per-game (budget, recording client), per-prompt-set (templates), and per-process (the map) — and resolves all of them at per-game granularity. The Jinja `Environment` is the visible casualty; `load_canonical_map()` is correctly hoisted by callers, which shows the team already knows the distinction.
2. **Derived-view sprawl over the episodic log** (F2). Thirty independent full scans, thirteen in one module, each rebuilding one projection (roster ids, body sightings, co-presence, movement breadcrumbs, transitions, observations…). This is the classic agent-authored shape: every new task added a helper that starts `for event in episodic.recent(since_tick=0)`. The store has the sortedness invariant needed to make this cheap and does not use it.
3. **Write-then-read-then-re-walk** in the eval fold (F9). The tournament writes a replay, reads it back, and re-runs the engine over it to recover facts the live run already had in hand. Defensible for verification; expensive as the default.
4. **Verbatim prompt storage in three places** (F4): the replay JSONL, the eval report JSON, and the committed samples. One of those is provenance; two are copies.

**What I would refactor, and how.**

- **`MemoryStore` gains an index, not a rewrite** (F2). Keep a parallel `list[int]` of ticks and `bisect_left` in `recent()`; cache the `since_tick<=0` tuple, invalidated on `append`. That is ~10 lines, byte-identical (proven), and worth 1.28x on long games. Then, separately, give the store O(1) accessors for the three things perception recomputes every tick (`seq` counter, seen-body ids, the co-presence window) — those are maintainable incrementally at append time.
- **Split `build_default_meeting_runner` by lifetime** (F1). `lru_cache` `build_environment` on `(resolved_set, root, roll_call_lever)`; leave budget/recording-client construction per game exactly as documented.
- **Parallelise `run_tournament_eval`** (F3). `ProcessPoolExecutor` over seeds, results re-sorted by seed, worker count a CLI flag defaulting to 1 for real providers.
- **Stop persisting prompts in the eval report** (F4). Keep `LLMCallRecord` intact in memory; drop `prompt` at serialization (or replace it with an offset into `replay_ref`). Re-generate the committed sample reports once.
- **Make the observation audit opt-in** (F6). Change the type to `Path | None`, default the tournament to off.
- **Long term, do not "optimize" `_state_hash`** (F5) — it is load-bearing and frozen. Memoize `fields()` per type; leave the encoding alone.

**Where the 2–5x actually is.** For the workload that matters (campaigns of 100–1 000 fake-provider games, and ML rollouts):
`process parallelism 4.98x (measured) × per-game fixes 1.30x (measured) ≈ 6.5x`, of which the parallelism is ~25 lines and the per-game fixes are ~30. Nothing beyond that is worth doing until a profile says so — after both fixes the profile is genuinely flat (top tottime item is 6.5 %), which is the correct end state.

---

## 6. Recommendations (prioritized)

| # | Recommendation | Effort | Measured / estimated win | Risk |
|---|---|---|---|---|
| **R1** | Cache the Jinja `Environment` per resolved prompt set (`lru_cache` on `build_environment`, key = set name + root + roll-call lever). | ~10 lines | **1.24x** on 9p2i games; 16 % of tournament wall | Very low — **replay bytes verified identical** |
| **R2** | `bisect` in `MemoryStore.recent()` + cache the `since_tick<=0` tuple, invalidated on `append`. | ~10 lines | **1.28x** on long games, 1.11x on short | Very low — **replay bytes verified identical**; the sortedness invariant is already enforced in `append` |
| **R3** | Give `MemoryStore` O(1) incremental accessors for the three per-tick recomputations in `perception.py:143,284,315`, and collapse the 13 `store.py` full scans into one pass building all projections. | ~1 day | Removes the remaining Θ(T²) term; matters most at `--max-ticks 1000` | Medium — touches the render path; gate on the prompt-byte golden tests (`tests/meetings/test_prompt_byte_golden.py`) |
| **R4** | Parallelise `run_tournament_eval` with `ProcessPoolExecutor` over seeds (worker flag, default 1 for real providers, results sorted by seed). | ~20 lines | **4.98x measured** at 8 workers under load | Low — games are independent and seeded; verify report determinism against a serial run |
| **R5** | Stop persisting `llm_calls[].prompt` in `tournament-eval-report.json`; keep `replay_ref` as the pointer. Regenerate the committed sample reports. | ~half day + a re-record | Report 47 MB → ~0.5 MB; peak RSS 584 MB → ~160 MB; **~26 MB off the git tree** | Medium — must first confirm no consumer reads prompts from the *persisted* report (only from replays) |
| **R6** | Make the observation audit sidecar opt-in (`audit_log_path: Path \| None`), default off in `run_tournament.py`. | ~10 lines | ~3 ms + 160 kB per game; 16 MB per 100-game run | Low — `os.devnull` plumbing already exists; keep `run_game.py --audit-log-path` working |
| **R7** | Fix the perf gate: run the benchmark at the **9p2i** roster, and either drop the `DESIGN.md:870` "≥ 1 game/min" target or restate it as an LLM-inclusive target the FakeProvider benchmark explicitly does not test. Delete `test_perf_benchmark_marker_is_opt_in_skipif`. Correct `DESIGN.md:128` "microseconds per agent per tick" with the measured curve. | ~1 hour | Docs stop lying; the recorded number describes the roster in use | None |
| **R8** | Add `pytest-xdist` and run the default tier with `-n auto` in `check.sh`/CI. Either use the registered `slow`/`perf` markers or delete them. | ~1 hour | 320 s → likely ~60 s on 10 cores | Low — check for fixture/tmp-path collisions first (memory notes already flag concurrent-session collisions on this repo) |

---

## 7. Reproduction

Scratch scripts (read-only, outside the repo) at
`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/perf-runtime/`:

- `prof_game.py` — in-process game timing + cProfile → `game9p2i.prof`
- `prof_tour.py` — 10-game tournament cProfile → `tourprof/tour.prof`
- `prof_loader.py` — `ReplayLoader` cProfile → `loader.prof`
- `bench_jinja.py` — F1 micro-benchmark
- `scan_sites.py` / `count_scans.py` — F2 episodic-scan attribution
- `scaling.py` — F2 per-tick growth curve
- `patch_bench.py` — F1+F2 A/B with replay-SHA equality check (`MODE=base|recent|jinja|recent,jinja`)
- `par.py` — F3 process-parallel speedup
- `bench_hash.py` — F5 state-hash / RNG decomposition
- `bench_loader3.py`, `bench_api.py`, `bench_unrec.py`, `mem_tour.py` — §2.6–2.8

Nothing in `/Users/danielkeinan/projects/AiLibi` was created, edited, staged or committed. All experiments wrote to the scratch directory; both A/B optimizations were applied by monkeypatch inside a scratch process.
