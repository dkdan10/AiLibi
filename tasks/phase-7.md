# Phase 7 — Agent Intelligence

## Goal
Make the agents demonstrably smarter (better lying, deeper contradiction
detection, real impostor tactics) AND measurable. The Phase 7 pre-planning
diagnosis (`audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md`)
showed the blocker is structural: games rarely reach meetings (4/50), so every
agent-intelligence metric runs on n≈4 and is noise. Phase 7 therefore opens with
an **enablement gate (Wave 0)** that makes meetings frequent, then ships
agent-intelligence on a measurable denominator in later waves. The full plan,
locked decisions (Daniel, 2026-05-30), and Wave 1–3 shape live in
`tasks/phase-7-plan.md`; this file holds the per-task contracts.

## Scope decisions (lock these before dispatching any task)

- **This file is built incrementally, Wave 0 first.** Per `tasks/phase-7-plan.md`,
  Phase 7 is sequenced Wave 0 → Wave 1 → Wave 2 → Wave 3. Only the **Wave 0
  enablement-gate** contracts (7.1–7.8), plus the **Wave 0.5** audit-driven eval-set repair contracts (7.9–7.11,
  appended 2026-06-01 after the gameplay-data audit), are written here today. Wave 1 (crew
  intelligence: new contradiction-detector kinds + deterministic wander idle),
  Wave 2 (impostor intelligence: vent/sabotage + teammate-defense meeting
  behavior using 7.2's mutual-awareness), and Wave 3 (depth/content) get their
  `### Task 7.x` contracts appended to this file only after Wave 0 clears its
  exit gate. Do NOT pre-author Wave 1+ contracts against substrate that does not
  exist yet.
- **Nothing in agent-intelligence is measurable until Wave 0 clears.** The Stage-A
  close gate (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings on the canonical
  7p/2i + 2-task set) is non-negotiable; agent-intelligence A/Bs are noise below
  it. Wave 0 is mostly config/substrate and low risk: 7.1 (configurable roster +
  tasks-per-crewmate), 7.2 (impostor mutual-awareness substrate), 7.3
  (`meeting_rate` + `meetings_total` + body/emergency trigger-breakdown metric),
  7.4 (roster-aware loader + two-committed-set layout plumbing — dispatchable,
  fake-validated), 7.5 (Ollama provider client + wiring — local `qwen2.5:7b-instruct`,
  $0), 7.6 (parse-tolerance / normalization so near-miss model reports validate),
  7.7 (provider-agnostic refresh + parametrized per-game budget), and 7.8 (generate +
  balance-validate + commit the meeting-heavy eval set — design-thread-run, locally
  on Ollama, no spend).
- **Wave 0.5 is audit-driven repair, not new capability (added 2026-06-01).** The
  gameplay-data audit (`audits/audit-2026-06-01-1425-gameplay-data.md`) found the
  committed 7p/2i baseline was confounded by an impostor friendly-fire bug (39/50
  games self-destruct) plus 3 meeting-abort games, so the Wave-0 balance numbers are
  a PROVISIONAL artifact. Wave 0.5 (7.9 teammate-aware kill + engine guard, 7.10
  fail-soft meetings + R 2→1, 7.11 eval-reporting honesty) repairs the substrate and
  gates the re-record that produces the first trustworthy baseline — it lands NO
  crew/impostor intelligence (that is Wave 1+). Low-risk: a target-selection filter,
  an engine reject, parse fail-soft, and reporting fields/caveats.
- **The eval-set work is split: dispatchable plumbing (7.4) + Ollama substrate
  (7.5–7.7) + design-thread-run generation (7.8).** Task 7.4 (roster-aware loader +
  two-committed-set layout) is a normal reviewed PR validated on the FAKE provider —
  no spend, no committed data. Tasks 7.5–7.7 add and wire the local-Ollama provider,
  the parse-tolerance layer, and the provider-agnostic refresh/budget — all normal
  reviewed PRs, fake/mock-validated, no spend. Task 7.8 runs LOCALLY against a live
  Ollama server (no API key, no real spend — cost is $0) and needs human balance
  judgment over the decisive crew/impostor split (Q3-resolved: balance validation is
  required), with a possible re-balance sweep (2↔3 tasks / roster) implying multiple
  local runs; per the dispatch-pattern + eval-cadence memory it is operated by the
  design thread, AFTER 7.4–7.7 are merged green. The config-only Wave 0 work (7.1,
  7.3) and the firewall substrate (7.2) validate on the fake provider.
- **Provider for Phase 7 is local Ollama, $0 (supersedes Q2's "stay Anthropic").**
  The canonical agent-intelligence provider is now a **local Ollama** open model,
  `qwen2.5:7b-instruct`, which runs on the owner's Mac for free — chosen because a
  hosted frontier model is both expensive (~$150+ over the phase) and brittle on the
  strict report schemas. Task 7.8 therefore runs LOCALLY with no spend and no API
  key. The existing Anthropic path stays supported (7.5 only ADDS the Ollama branch),
  and the 4p/1i Anthropic baseline is kept + **frozen** — replays are model-agnostic,
  so it reconstructs byte-identically regardless of provider. Bound cost trivially
  ($0) and bound the 7.8 sweep by a time-box rather than dollars.
- **Frontend scope = browse only (Q1-resolved), and not in Wave 0.** A
  roster/config selector in the replay picker to browse the committed 4p/1i vs
  7p/2i sets is a later track; launching a game from the UI is deferred to the
  live/broadcast track. No Wave 0 task touches `frontend/` except 7.3's 1:1 type
  mirror of the new `meeting_rate` field into `frontend/src/types/api.ts` (no
  component work).
- **The observation firewall is the project's most important invariant.** Task 7.2
  adds the FIRST self-channel field beyond `role` (`fellow_impostor_ids`); it is
  impostor-only, lives only inside `SelfView`, and never touches
  `visible_players` / `PlayerView`. The new crew-empty leak invariant
  (`self_state.fellow_impostor_ids == ()`) must hold on BOTH committed sets after
  7.8 lands the first committed multi-impostor data.

## Parallelism
Wave 0 has two independent roots and a short dependency chain:

- **7.1 (configurable roster + tasks-per-crewmate)** and **7.2 (impostor
  mutual-awareness substrate)** have no dependencies and fan out in parallel —
  disjoint file scopes (7.1 owns `orchestrator/` + `eval/balance_eval.py` +
  `scripts/run_tournament.py`; 7.2 owns `observation/` + `agents/perception.py` +
  `eval/leak_test.py`).
- **7.3 (`meeting_rate` metric) depends on 7.1 merged** — both edit
  `scripts/run_tournament.py` (7.1 adds the argparse flags + threading into
  `run_tournament_eval`; 7.3 adds the meeting-rate lines to `_format_summary` on
  top of 7.1's merged version), so 7.3 lands after 7.1. The dependency is a
  merge-serialization on a shared FILE, not a hard data dependency: 7.3's metric
  core could otherwise run in parallel. 7.3's own file scope
  (`eval/meeting_quality.py`, `eval/prompt_regression.py`, `api/routes/eval.py`,
  `frontend/src/types/api.ts`, `tests/api/test_leak.py`, fixtures) is otherwise
  disjoint from 7.1/7.2.
- **7.4 (roster-aware loader + two-set layout plumbing) depends on 7.1 + 7.2
  merged** — it consumes 7.1's `tasks_per_crewmate` seeder param and needs 7.2's
  `fellow_impostor_ids` invariant for its hermetic multi-impostor reconstruction
  test. It does NOT depend on 7.3 (no `meeting_rate` use), so it runs in PARALLEL
  with 7.3. Disjoint scope (`api/replay_loader.py`, `scripts/refresh_samples.sh`,
  `scripts/_manifest_writer.py`, + their tests) — dispatchable, fake-validated, no
  spend, no committed data.
- **7.5 (Ollama provider client + wiring) depends on nothing** — it extends the
  merged LLM substrate (`llm/provider.py`, `llm/budgeted_client.py`, `llm/budget.py`)
  with a new `llm/ollama_client.py` + the `pyproject.toml`/`uv.lock`/`.env.example`/
  `README.md`/`AGENTS.md` config, none of which any merged 7.1–7.4 task touches, so
  it has no in-phase scope overlap and fans out as a fresh root after 7.4. It is the
  single gate the rest of the Ollama substrate (7.6, 7.7) and the eval set (7.8)
  build on, hence sequenced after the (7.3 ∥ 7.4) pair.
- **7.6 (parse-tolerance / normalization) depends on 7.5 merged** — it edits the
  SHARED extract→validate path in `llm/provider.py` (which 7.5 also edits) and must
  cover 7.5's new Ollama client, so it lands on 7.5's merged `llm/provider.py`. Its
  own helper (`llm/report_normalize.py`) + tests are otherwise disjoint, so it runs
  in PARALLEL with 7.7.
- **7.7 (provider-agnostic refresh + budget) depends on 7.1 + 7.4 + 7.5 merged** —
  it edits `eval/balance_eval.py` (shared with 7.1, hence the 7.1 edge) and
  `scripts/refresh_samples.sh` (shared with 7.4, hence the 7.4 edge), and it must
  select 7.5's Ollama provider in the preflight (hence the 7.5 edge). Disjoint from
  7.6 (no `llm/provider.py` edit — it only reads an env knob into the per-game
  budget), so it runs in PARALLEL with 7.6.
- **7.8 (generate + balance-validate + commit the meeting-heavy set) depends on
  7.1 + 7.2 + 7.3 + 7.4 + 7.5 + 7.6 + 7.7 merged** — it consumes 7.4's roster-aware
  plumbing + 7.1's flags, reads 7.3's `meeting_rate` to check the exit gate, must
  hold 7.2's crew invariant on the new committed multi-impostor data, and runs the
  whole thing on 7.5's Ollama provider through 7.7's provider-agnostic refresh with
  7.6's parse-tolerance protecting the local model's reports. It is run LAST, by the
  design thread, LOCALLY against a live Ollama server (no spend). Scope is the
  committed `replays/samples/7p2i/` data + the committed-set reconstruction test
  (shared with 7.4 under the dependency edge).

Sequence: (7.1 ∥ 7.2) → (7.3 ∥ 7.4) → 7.5 → (7.6 ∥ 7.7) → 7.8.

Wave 0.5 (eval-set repair, post-2026-06-01 gameplay-data audit) appends three more tasks. 7.9
(impostor kill correctness + engine friendly-fire guard), 7.10 (meeting fail-soft + R 2→1), and 7.11
(eval reporting hardening) have disjoint file scopes — agents/+engine, meetings/+llm, eval/ — and fan
out in PARALLEL. The only edges are merge-serialization on shared files: 7.9 has none; 7.10 depends on
7.6 merged (it extends `llm/report_normalize.py`); 7.11 depends on 7.3 merged (it extends
`eval/meeting_quality.py` and the report mirror). After all three merge, the design thread re-records
the 7p/2i set on Ollama (now friendly-fire-free and R=1) and re-runs the gameplay-data audit before
any Wave-1 work.

Wave 0.5 sequence: (7.9 ∥ 7.10 ∥ 7.11) → re-record → re-audit → Wave 1.

## Tasks

### Task 7.1 — Configurable roster + tasks-per-crewmate knob
**Branch:** `phase-7-configurable-roster-and-tasks-per-crewmate`
**Depends on:** none
**Section refs:** Phase 7 plan W0.1 + decisions 1, 2; diagnosis audit `audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md` §1, §3, §4; DESIGN.md §1.4, §3.1, §11.3
**Complexity:** Medium

This is the first move of the Phase 7 Wave 0 enablement gate. The diagnosis audit
showed games rarely reach meetings (4/50) because they end too fast: the seeder
hardcodes exactly one task per crewmate (`orchestrator/seeder.py:165-176`), so the
4p/1i default has only 3 total tasks and two survivors finish them by median tick 9
before any kill→body→report chain can complete. The measured counterfactual is
decisive — 4p/1i ≈ 10% meeting rate vs **7p/2i = 63%** — and `num_impostors > 1`
is already fully wired (`seed_initial_state` accepts `num_impostors`, the CLI
exposes `--num-impostors`). What is missing is (a) a configurable
`tasks_per_crewmate` (locked default **2**, applied at the harness/CLI layer;
the seeder parameter itself defaults to 1 so the committed-replay loader is
unaffected — see below) so games run
long enough for bodies to outlive the win condition, and (b) two named roster
presets — `4p/1i` and `7p/2i` — that bundle `num_players` / `num_impostors` with the
task count so the eval harness (and, in a later frontend task, the replay picker)
can refer to a config by name.

Add a `tasks_per_crewmate: int` parameter to `seed_initial_state` and the private
`_build_tasks` helper in `orchestrator/seeder.py`. **Keep the seeder's parameter
default at `1`** (the current hardcoded value), NOT 2. The locked default-of-2 is
introduced one layer up, at the harness/CLI (`HeadlessGame` / `run_tournament_eval`
/ the CLI flag, all defaulting to `DEFAULT_TASKS_PER_CREWMATE = 2`). This is a hard
determinism requirement: `api/replay_loader.py::_walk` (line 419) calls
`seed_initial_state(...)` WITHOUT passing `tasks_per_crewmate`, so if the seeder
default flipped to 2 the loader would silently re-seed the committed 4p/1i replays
(recorded at 1 task/crewmate — seed-0 4p/1i = 3 tasks) with 6 tasks, changing
`WorldState.tasks` and therefore every per-tick `state_hash` the loader
reconstructs — `tests/scripts/test_verify_samples.py::test_clean_sample_verifies`
(and `bash scripts/check.sh`) would raise `ReplayStateMismatchError`. Leaving the
seeder default at 1 keeps every existing un-updated caller (the loader) byte-identical;
the loader's full roster-awareness (reading each set's recorded `tasks_per_crewmate`)
is **Task 7.4** and is out of scope here. Today `_build_tasks` assigns each crewmate one map task
id via `map_task_ids[index % len(map_task_ids)]`; with multiple tasks per crewmate
the assignment must give each crewmate `tasks_per_crewmate` **distinct** map task
ids. This is a hard structural constraint: `WorldState.tasks` is keyed by `TaskId`
and the engine enforces `TaskState.id == <dict key>` (`engine/tick.py:111`), so the
same map task id can NOT be owned by two crewmates — every assigned task id must be
unique across the whole roster. Draw `num_crewmates * tasks_per_crewmate` distinct
ids from the seed-shuffled map task pool and partition them across crewmates. The
canonical map has 12 tasks (`engine/maps/canonical_1.yaml`), so 4p/1i (3 crew × 2 =
6) and 7p/2i (5 crew × 2 = 10) both fit; when
`num_crewmates * tasks_per_crewmate > len(game_map.tasks)` the seeder must fail loud
with a clear `ValueError` rather than silently colliding ids (AGENTS.md
"no silent fallbacks"). Also reject `tasks_per_crewmate < 1`.

No change is needed to the observation/policy task path: the observation service
already surfaces the lexically-first owned-unfinished task as `pending_task_id`
(`observation/service.py:241-251`), so a crewmate with two tasks naturally
advances to its second once the first completes. This task only widens the seeder
and threads the knob.

Thread `tasks_per_crewmate` through the call chain so a tournament can be run with
the new config end to end, defaulting to 2 at every layer ABOVE the seeder:
`HeadlessGame.__init__` / `run` in `orchestrator/game.py` (default
`DEFAULT_TASKS_PER_CREWMATE`; it calls `seed_initial_state` at the top of `run` and
passes the value through explicitly); `eval.balance_eval.run_tournament_eval` (the
harness between the CLI and `HeadlessGame`, which also re-seeds roles on the
meeting-abort path via `_seeded_roles`); and `scripts/run_tournament.py` as a new
`--tasks-per-crewmate` flag (default 2). Add a `DEFAULT_TASKS_PER_CREWMATE: Final[int]
= 2` constant next to the existing `DEFAULT_NUM_PLAYERS` / `DEFAULT_NUM_IMPOSTORS` in
`orchestrator/game.py` and export it, so the CLI default and the harness default
share one source of truth. Note the asymmetry is intentional: `seed_initial_state`'s
own parameter default stays 1 (every harness/CLI caller passes the value explicitly,
so they get 2; the only caller that does NOT pass it is the committed-replay loader
in `api/replay_loader.py`, which must keep re-seeding the 4p/1i baseline at 1 task
until Task 7.4 makes it roster-aware).

`eval.balance_eval.run_balance_eval` (the thin Phase-2 compat wrapper at
`balance_eval.py:285` that forwards `num_players` / `num_impostors` into
`run_tournament_eval`) is deliberately left at the seeder default — it has no caller
that needs the knob, so it is NOT extended with a `tasks_per_crewmate` kwarg in this
task (its `run_tournament_eval` call relies on `run_tournament_eval`'s own default of
`DEFAULT_TASKS_PER_CREWMATE`). This omission is intentional, not an oversight.

Define the two named roster presets in `orchestrator/game.py` (where the other
roster defaults live) as a small immutable structure — a frozen dataclass
`RosterPreset` (fields `num_players`, `num_impostors`, `tasks_per_crewmate`) plus a
`ROSTER_PRESETS` mapping `{"4p1i": RosterPreset(num_players=4, num_impostors=1,
tasks_per_crewmate=1), "7p2i": RosterPreset(num_players=7, num_impostors=2,
tasks_per_crewmate=2)}`. The `4p1i` preset is pinned at `tasks_per_crewmate=1`
(NOT the new default of 2) precisely so it reproduces the byte-identical committed
4p/1i baseline (Merge Criteria); `7p2i` is the new meeting-heavy config at
`tasks_per_crewmate=2`. Expose a `--roster-preset {4p1i,7p2i}` flag on
`scripts/run_tournament.py` that, when given, supplies all three values; the
explicit `--num-players` / `--num-impostors` / `--tasks-per-crewmate` flags stay
usable for ad-hoc configs and a preset is mutually exclusive with passing those
explicitly (fail loud on conflict). Keep the preset definition data-only here so a
later frontend task can surface the same names without a code change.

Determinism and the observation firewall are HARD constraints: the existing 4p/1i
committed baseline path must remain byte-identical when run with its original
config (1 task/crewmate), so the seed→task-assignment derivation must stay a pure
function of `(seed, game_map, crewmate_ids, tasks_per_crewmate)` with the same
RNG-draw order it has today for the `tasks_per_crewmate=1` case. Do not change role
assignment, spawns, cooldowns, or the per-task RNG seeding. The leak firewall is
untouched — this task adds no field to any observation packet.

Out of scope: the `meeting_rate` metric (Task 7.3), regenerating / committing the
7p/2i sample set (Task 7.8), balance validation of the new config (folded into
Task 7.8), the roster-aware loader / two-set layout plumbing (Task 7.4), impostor
mutual-awareness (Task 7.2), and any frontend work (the picker
preset selector is a later frontend track). This task only makes the config
reachable and deterministic; it does not run the eval.

**Files in scope:**
- orchestrator/seeder.py
- orchestrator/game.py
- eval/balance_eval.py
- scripts/run_tournament.py
- tests/orchestrator/test_seeder.py
- tests/orchestrator/test_game.py
- tests/eval/test_balance_eval.py
- tests/scripts/test_run_tournament.py

**Files NOT in scope:**
- engine/ (the engine consumes tasks unchanged; TaskState/TaskId shape is fixed)
- observation/service.py (already surfaces multi-task pending correctly; no change)
- agents/tactical/crewmate_policy.py (multi-task sequencing already works via pending_task_id)
- eval/meeting_quality.py (the meeting_rate metric is Task 7.3)
- scripts/run_game.py (single-game CLI; not the tournament path this task threads)
- replays/samples/ (sample regeneration/commit is Task 7.8; do NOT regenerate fixtures here)
- frontend/ (the picker preset selector is a later frontend task)
- observation/packet.py (no new packet field; the firewall surface is unchanged)
- api/replay_loader.py (the loader's `_walk` call to `seed_initial_state` must NOT change in this task; it keeps re-seeding at the seeder default of 1 task/crewmate so the committed 4p/1i baseline stays byte-identical. The loader's full roster-awareness — reading each set's recorded `tasks_per_crewmate` / `num_impostors` — is Task 7.4. The seeder default-driven call site must not silently change here, which is why `seed_initial_state`'s parameter default stays 1 and the default-of-2 lives only at the harness/CLI layer.)
- eval.balance_eval.run_balance_eval (the Phase-2 compat wrapper is left at the default; it has no caller needing the knob — intentional omission, not an oversight)

**Definition of done:**
- [ ] `orchestrator/seeder.py` `seed_initial_state` and `_build_tasks` accept `tasks_per_crewmate: int` with the parameter default kept at `1` (NOT 2 — so `api/replay_loader.py`'s default-driven `_walk` call keeps re-seeding the committed 4p/1i baseline byte-identically); each crewmate is assigned exactly `tasks_per_crewmate` distinct map task ids, and `len(state.tasks) == num_crewmates * tasks_per_crewmate`.
- [ ] Every assigned `TaskState.id` is unique and equals its `WorldState.tasks` dict key (no two crewmates share a map task id), so the `engine/tick.py:111` `task.id == mapping key` invariant holds.
- [ ] `seed_initial_state` raises a clear `ValueError` when `tasks_per_crewmate < 1`, and when `num_crewmates * tasks_per_crewmate > len(game_map.tasks)` (pool exhausted) rather than reusing an id — covered by a test using a pool-exhausting VALID roster (e.g. 10p/1i + `tasks_per_crewmate=2` → 18 > 12, or a small synthetic map); note 0 impostors is rejected by the seeder so cannot be used to exhaust the pool.
- [ ] Running with `tasks_per_crewmate=1` reproduces the pre-task task assignment byte-for-byte for the existing seeds (the committed 4p/1i baseline path is unchanged): a test asserts the `tasks_per_crewmate=1` task set equals the historical one-task-per-crewmate assignment for a fixed seed.
- [ ] `DEFAULT_TASKS_PER_CREWMATE: Final[int] = 2` is defined and exported from `orchestrator/game.py`; `HeadlessGame` accepts `tasks_per_crewmate` (default `DEFAULT_TASKS_PER_CREWMATE`) and threads it into `seed_initial_state`.
- [ ] `eval.balance_eval.run_tournament_eval` (and the `_seeded_roles` re-seed on the abort path) accept and thread `tasks_per_crewmate` (default `DEFAULT_TASKS_PER_CREWMATE`) so the harness seeds the same config the game ran with; a test asserts roles/tasks are consistent for a 7p/2i + 2-task run. `run_balance_eval` is intentionally left at the default (no kwarg added) — it has no caller needing the knob.
- [ ] `api/replay_loader.py` is NOT edited: its existing `_walk` call to `seed_initial_state` (without `tasks_per_crewmate`) continues to re-seed the committed 4p/1i set at the seeder default of 1, so `tests/scripts/test_verify_samples.py` / `bash scripts/check.sh` keep reconstructing byte-identically. (Loader roster-awareness is Task 7.4.)
- [ ] `scripts/run_tournament.py` exposes `--tasks-per-crewmate` (default 2) and `--roster-preset {4p1i,7p2i}`; a preset supplies all three roster values and is mutually exclusive with explicit roster flags (fail loud on conflict). A `tests/scripts/test_run_tournament.py` test drives `main()` for both a preset run and an explicit-flag run on a tiny seed range and asserts the threaded config.
- [ ] `RosterPreset` (frozen, data-only) and `ROSTER_PRESETS` (`{"4p1i", "7p2i"}`) are defined in `orchestrator/game.py`; `ROSTER_PRESETS["4p1i"]` is `num_players=4, num_impostors=1, tasks_per_crewmate=1` (pinned at 1 to match the byte-identical committed baseline, NOT the new default of 2) and `ROSTER_PRESETS["7p2i"]` is `num_players=7, num_impostors=2, tasks_per_crewmate=2`.
- [ ] No observation-packet field is added; the leak tests still pass unchanged. No `replays/samples/` fixture is regenerated in this task.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `orchestrator/seeder.py` `_build_tasks` (lines 155-176) end to end before
touching it — the determinism contract lives in the RNG draw order. The existing
code shuffles `sorted(game_map.tasks)` with `random.Random(seed)` then assigns
`map_task_ids[index % len(map_task_ids)]` per crewmate. To preserve the
`tasks_per_crewmate=1` bytes exactly, keep the same `random.Random(seed)` +
`rng.shuffle(sorted(game_map.tasks))` prefix, then for the general case walk the
shuffled pool assigning the next `tasks_per_crewmate` ids to each crewmate in
`crewmate_ids` order (a flat cursor over the shuffled list, NOT a modulo, so ids
never repeat). Validate the pool size up front:
`num_crewmates * tasks_per_crewmate <= len(game_map.tasks)`. To make the
pool-exhaustion `ValueError` test WRITABLE on the 12-task canonical map, use a
config that actually exhausts it with a VALID roster (the seeder requires
`1 <= num_impostors < num_players`, so 0 impostors is rejected — do NOT use
"7p/0i"): e.g. `seed_initial_state(num_players=10, num_impostors=1,
tasks_per_crewmate=2)` → 9 crew × 2 = 18 > 12, or `num_players=7, num_impostors=1,
tasks_per_crewmate=3` → 18 > 12; alternatively pass a small synthetic `Map`
fixture with few tasks. Because the SEEDER
parameter default stays 1, the existing seeder tests' `tasks_per_crewmate`-omitted
calls (which assert `len(state.tasks) == num_crewmates`) keep passing unchanged —
do NOT bump them. The default-of-2 lives only at `DEFAULT_TASKS_PER_CREWMATE` and
the harness/CLI layer; any test that drives `HeadlessGame` / `run_tournament_eval`
/ the CLI without an explicit `tasks_per_crewmate` now gets 2, so update those
harness/CLI tests instead. Pin the historical 1-task assignment in a dedicated
seeder regression test, and add a separate test that the harness default is 2.

For threading: `HeadlessGame.run` calls `seed_initial_state` at line ~684 —
add the field to `__init__` and forward it there. In `eval/balance_eval.py`,
`run_tournament_eval` constructs each `HeadlessGame` (line ~209) and re-seeds roles
on the abort path through `_seeded_roles`; both need the new kwarg so the recovered
roles match the played game. In `scripts/run_tournament.py`, mirror the existing
`--num-players` / `--num-impostors` argparse blocks (lines 76-87) and add the
preset flag; resolve the preset → (players, impostors, tasks) before calling
`run_tournament_eval`, and `raise SystemExit(...)` if `--roster-preset` is combined
with an explicit roster flag (the script already uses `raise SystemExit` for bad
`--num-games`). Define `RosterPreset` / `ROSTER_PRESETS` alongside the
`DEFAULT_NUM_PLAYERS` block in `orchestrator/game.py` and add the new public symbols
to its `__all__`. For the CLI test, follow `tests/scripts/conftest.py` (bare-module
import of the script) and the `main([...])` driving idiom in
`tests/scripts/test_manifest_writer.py`; keep the seed range tiny (1-2 seeds, low
`--max-ticks`) so the fake provider run is fast.

**Public types introduced:**
- orchestrator.game.RosterPreset
- orchestrator.game.DEFAULT_TASKS_PER_CREWMATE
- orchestrator.game.ROSTER_PRESETS

**Ready-to-paste prompt:** `agent_prompts/task-7-1-configurable-roster-and-tasks-per-crewmate.md`

### Task 7.2 — Impostor mutual-awareness substrate (firewall-safe)
**Branch:** `phase-7-impostor-mutual-awareness`
**Depends on:** none
**Section refs:** tasks/phase-7-plan.md W0.2 + Q4 (decision 3); audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §3 (7p/2i = 63% meeting rate); DESIGN.md §1.3 (observation firewall)
**Complexity:** Integration

Phase 7's enablement gate switches the canonical eval roster to 7p/2i (two
impostors) so that meetings actually happen at volume (the diagnosis audit
measured 4p/1i ≈ 10% vs 7p/2i = 63%). But a 7p/2i game is only coherent if the
two impostors know they are on the same side: per locked decision 3, multiple
impostors must know who each other are, so that in meetings they never accuse or
vote one another. They get NO private conversation channel — coordination happens
only through public play — but each impostor must receive the identity of its
fellow impostor(s). Today nothing delivers this, so two impostors at 7p/2i would
treat each other as suspects and the eval signal would be polluted.

This task adds that mutual-awareness as an impostor-only field on `SelfView`
(`observation/packet.py`) — `fellow_impostor_ids: tuple[PlayerId, ...]` — and
populates it in `ObservationService` (`observation/service.py`) ONLY when the
recipient is an impostor. The field reuses the already-privileged self channel
where `role` lives (the agent is entitled to know its own role; by the same
logic an impostor is entitled to know its own team). It is empty `()` for every
crewmate recipient and empty for an impostor in a solo-impostor game (an impostor
has no fellows). It must NOT touch `visible_players` / `PlayerView` — that is the
public, crew-visible channel and the firewall forbids any role-bearing data
there. The recipient's OWN id is excluded from the tuple; only the other
impostors appear.

The field is delivered to agent code by extending
`agents/perception.py::_self_state_payload` so the impostor policy/prompt layer
can read its teammates from the same self-state payload that already carries
`role`. This is the only consumer wiring in scope; actually USING the teammate
list in meeting behavior (defend a teammate, never accuse one) is Wave 2 (J-5),
not this task.

The leak firewall is the hard constraint. Extend `eval/leak_test.py` with a new
explicit invariant: `self_state.fellow_impostor_ids == ()` for every
crewmate-recipient packet. Because player ids are role-neutral (`p-1`, `p-2`,
…; see `orchestrator/seeder.py`), the existing value scanner
(`_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")`) is not tripped
by id values, and the recursive field-name scanner keys off specific names
(`role`, `killed_by`, …) not the substring "impostor" in a key — so the new
field is firewall-safe by construction, but the test must PIN that an impostor
seeing its own teammates is allowed while a crewmate's tuple is always empty. The
three committed scripted fixtures are all 4p/1i (one impostor), so they already
exercise the crew-empty path; add a focused multi-impostor unit case in
`tests/observation/test_service.py` to exercise the impostor-sees-teammate path
(crew get `()`, each impostor gets the other impostor id, recipient excluded).

Crucially, ALSO extend the project's strongest leak test — the property-based
sweep `tests/observation/test_leak_property.py` (DESIGN.md §11.2's mandated
many-seeds purity check). Today it parametrizes only `seed` at the default 4p/1i
roster (`@given(seed=st.integers(...))`), so it never generates a multi-impostor
game and never touches the new field. Since `fellow_impostor_ids` is the FIRST new
self-channel field in the project's history, it must ride the strongest guarantee,
not just one hand-built unit case: parametrize the sweep over `num_impostors`
(include ≥ 2, with a valid roster, e.g. 7 players) and assert the crew-empty
invariant (`self_state.fellow_impostor_ids == ()` for every crewmate-recipient
packet) inside the per-packet loop, across many seeds. This closes the gap the
single-impostor fixtures leave (where a misroute into a crew tuple cannot surface).

Schema-mirror check (do this, do not assume): `SelfView` is NOT mirrored into the
spectator DTO surface (`api/schemas.py` shadows engine types directly and does not
reference `SelfView`) and is NOT referenced anywhere in
`frontend/src/types/api.ts` or `frontend/src/`. Confirm both before editing; if
the confirmation holds (it does at HEAD), this task stays entirely inside
`observation/`, `agents/perception.py`, `eval/leak_test.py`, and the listed test
files, and touches NO frontend code. Surfacing impostor coordination in the
privileged spectator UI is a deferred nice-to-have (plan §"Still open"), explicitly
NOT this task. Determinism is a hard constraint: the field is a pure deterministic
function of `WorldState.players` roles (no RNG, stable sort), so byte-identical
replay holds.

**Files in scope:**
- observation/packet.py
- observation/service.py
- agents/perception.py
- eval/leak_test.py
- tests/observation/test_service.py
- tests/agents/test_perception.py
- tests/observation/test_leak_property.py

**Files NOT in scope:**
- observation/audit.py (audit log records whatever the packet serializes; no change needed)
- api/schemas.py (SelfView is not mirrored here; verified, do not edit)
- frontend/ (SelfView is not consumed by the frontend; spectator surfacing is deferred)
- agents/impostor_policy.py (consuming the teammate list in meeting behavior is Wave 2 / J-5)
- orchestrator/seeder.py (roster/task config is Task 7.1; this task reads roles off WorldState, it does not assign them)
- meetings/ (no meeting-behavior change in Wave 0)

**Definition of done:**
- [ ] `SelfView` in `observation/packet.py` gains `fellow_impostor_ids: tuple[PlayerId, ...]` with a default of `()` (so existing `SelfView(...)` construction sites stay valid); the model stays frozen with `extra="forbid"`.
- [ ] `ObservationService` populates `fellow_impostor_ids` with the sorted ids of the OTHER impostors when the recipient's role is `IMPOSTOR`, and `()` for every crewmate recipient and for a sole impostor; the recipient's own id is never included.
- [ ] `visible_players` / `PlayerView` are unchanged; no role-bearing field is added to any crew-visible channel.
- [ ] `agents/perception.py::_self_state_payload` surfaces `fellow_impostor_ids` so the self-state payload exposes the teammate list alongside `role`.
- [ ] `eval/leak_test.py` asserts a new invariant: for every packet whose `self_state.role == "CREWMATE"`, `self_state.fellow_impostor_ids == ()`; the existing "no `PlayerView` carries role" and value/field scanners still pass unchanged.
- [ ] `tests/observation/test_service.py` adds a multi-impostor (>=2 impostors) case proving each impostor sees the other impostor id (self excluded), each crewmate sees `()`, and a solo-impostor build yields `()` for the impostor. Because all three committed scripted fixtures are 4p/1i (single impostor), this unit case (together with the extended property sweep below) is what exercises a roster where a misroute could surface a non-empty CREW tuple — so this case MUST additionally run the crew-empty leak assertion (`self_state.fellow_impostor_ids == ()`) over each crewmate-recipient packet built from the 2-impostor `WorldState`, not just check the populate logic. End-to-end coverage over a real played multi-impostor game lands with Task 7.8's committed 7p/2i set.
- [ ] `tests/observation/test_leak_property.py` (the DESIGN §11.2 many-seeds purity sweep) is extended to parametrize `num_impostors` (include ≥ 2 with a valid roster) AND to assert `self_state.fellow_impostor_ids == ()` for every crewmate-recipient packet in its per-packet loop — so the project's strongest leak test, not just one unit case, guards the first new self-channel field across many seeds and multi-impostor rosters.
- [ ] `tests/agents/test_perception.py` updates the pinned self-state payload assertion to include `fellow_impostor_ids`.
- [ ] Byte-identical replay determinism is preserved (the field is a pure function of roles in `WorldState`; no RNG, stable ordering).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Add the field to `SelfView` (`observation/packet.py:18`) as
`fellow_impostor_ids: tuple[PlayerId, ...] = ()`. The default is what keeps the
many existing `SelfView(room=..., role=..., pending_task_id=...)` call sites
(`tests/agents/test_beliefs.py`, `test_runtime.py`, `test_beliefs_wiring.py`,
`test_perception.py`) compiling without edits — only the perception payload test
that pins the dumped dict needs touching. `PlayerId` is already a `TypeAlias` in
this module, so no new import.

In `ObservationService._build_packet_from_visibility`
(`observation/service.py:67-119`), the service already reads
`player.role == "IMPOSTOR"` to compute `cooldown` (line 92) and has
`world_state.players` in hand. Compute the fellows in the same spot, e.g.:
`fellow_impostor_ids = (` `tuple(sorted(pid for pid, p in world_state.players.items()`
`if p.role == "IMPOSTOR" and pid != agent_id))` `if player.role == "IMPOSTOR" else ())`
and pass it into the `SelfView(...)` constructor at line 105. Sorting makes the
tuple deterministic and replay-stable. Do not gate on `alive` — an impostor knows
its teammate even after the teammate dies (it learned the identity at game start);
matching the engine's role-knowledge model and keeping the value independent of
visibility.

In `agents/perception.py::_self_state_payload` (line 195) add
`"fellow_impostor_ids": self_state.fellow_impostor_ids` to the returned mapping
(it serializes to a list in the prompt JSON, same as other tuple fields).

For the leak test, extend the per-packet loop in
`test_no_observation_leaks_hidden_information` (`eval/leak_test.py:271-299`): inside
the `if packet.self_state.role == "CREWMATE":` branch (line 298) add
`assert packet.self_state.fellow_impostor_ids == ()`. The three committed fixtures
are 4p/1i so this exercises the crew-empty path across all of them; the
impostor-sees-teammate path is covered by the new unit test in
`tests/observation/test_service.py`, which can build a 5-player / 2-impostor
`WorldState` (mirror the `_base_world_state` / `_player` helpers already in that
file) and assert the two impostors' packets carry each other's id while the three
crewmates carry `()`.

**Public types introduced:**
- observation.packet.SelfView.fellow_impostor_ids

**Integration risk:**

The observation firewall is the project's "most important test" (DESIGN.md §11.2):
this task adds the FIRST self-channel field beyond `role`, so the risk is leaking
team identity into a crew-visible path. Mitigation is structural — the value lives
only inside `SelfView` (the self channel), is populated only for impostor
recipients, and `visible_players`/`PlayerView` are explicitly out of scope and
unchanged. **Coverage (now first-class via the extended sweep):** the NEW crew-empty
invariant (`self_state.fellow_impostor_ids == ()`) is asserted in BOTH the scripted
`eval/leak_test.py::test_no_observation_leaks_hidden_information` (crew branch) AND
the property sweep `tests/observation/test_leak_property.py`, which THIS task extends
to parametrize `num_impostors` (≥ 2) and run the crew-empty assertion across many
seeds. This is necessary because the generic scanners alone would NOT catch a
crewmate erroneously receiving a non-empty `fellow_impostor_ids`: the recursive
field-name scanner keys off `{killed_by, kill_attribution, player_id}` (plus the
allowed `self_state.role` path), and the value scanner trips only on the substrings
`impostor`/`crewmate`/`crew`, none of which match role-neutral ids like `p-2`. So
the EXPLICIT assertion — not the scanners — is the guard, and the extended
multi-impostor sweep now exercises it across many random games (the single-impostor
4p/1i scripted fixtures cannot surface a crew-tuple misroute, since every impostor's
tuple is also `()` there). Task 7.8's committed 7p/2i set then adds end-to-end
coverage on a real played multi-impostor game. The second risk is determinism: the field must be a
pure, stably-ordered function of `WorldState` roles with no RNG and no dependence
on visibility/alive state, so the committed replay goldens and the audit-log
round-trip stay byte-identical. The third risk is construction-site breakage from
adding a field to a frozen `extra="forbid"` model — the `= ()` default neutralizes
it for every existing call site; verify with `uv run pytest` that no unrelated
`SelfView(...)` site regresses.

**Ready-to-paste prompt:** `agent_prompts/task-7-2-impostor-mutual-awareness.md`

### Task 7.3 — meeting_rate / meetings_total + meeting-trigger breakdown metric
**Branch:** `phase-7-meeting-rate-metric`
**Depends on:** 7.1 merged
**Section refs:** tasks/phase-7-plan.md §"Wave 0 — W0.3"; tasks/phase-7-plan.md §"Close gate — Stage A"; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §1, §4; DESIGN.md §11.3
**Complexity:** Medium

Wave 0 exists to make meetings frequent enough that the agent-intelligence
metrics stop running on n≈4 (the diagnosis found 4/50 games reach a meeting). The
Stage-A close gate is stated numerically — `meeting_rate ≥ 0.60` with ≥ 30
resolved meetings — but there is no metric that computes it today. This task adds
that metric so the gate is measurable, and adds the body-report-vs-emergency
trigger breakdown so the currently-dead emergency-button pathway (0/50 games in
the diagnosis) becomes visible the moment any later feature revives it.

Add a fifth Phase-5-style analyzer, `eval/meeting_quality.py::compute_meeting_rate`,
that folds a `TournamentReport` (or a bare game sequence, matching the
`compute_vote_correctness` signature) into a new frozen `MeetingRateReport`
carrying: `games_total` (number of games), `games_with_meeting` (games whose
`meetings` tuple is non-empty), `meeting_rate` (`games_with_meeting / games_total`,
and `None` when `games_total == 0` — undefined, not `0.0`, mirroring the
`vote_correctness_rate` convention), `meetings_total` (sum of `len(game.meetings)`
across all games), and a trigger breakdown: `body_report_meetings` and
`emergency_meetings` (which partition exactly into `meetings_total`). The report
carries a `model_validator(mode="after")` that fails loud on the bucket invariants
(non-negative counts; `body_report_meetings + emergency_meetings == meetings_total`;
`games_with_meeting <= games_total`; the `None`-rate-iff-`games_total==0` coupling)
exactly as `VoteCorrectnessReport._validate_buckets` does.

Wire the new analyzer into `build_tournament_eval_report` as a fifth field
`meeting_rate: MeetingRateReport` on `TournamentEvalReport` (the frozen,
`extra="forbid"` wrapper), keeping that function pure assembly — it calls the new
`compute_meeting_rate` and packs the result, never re-deriving counts inline.

FORMAT-VERSION POLICY (decide once, here, so reviewers do not re-litigate on PR):
`meeting_rate` is added to the `TournamentEvalReport` WRAPPER
(`eval/meeting_quality.py:46`), which is NOT version-stamped. `format_version` lives
ONLY on the inner persisted `TournamentReport` (`eval/report_schema.py:254`, a
required field) and governs the replay-derived report-record schema — which this
task does NOT change (the metric is a pure derived analyzer over existing
`MeetingReport` data and adds no persisted report/replay field). Therefore
`CURRENT_FORMAT_VERSION` stays `1`; do NOT bump it. The regenerated
`tournament-eval-report.json` simply carries the new wrapper field; consumers read
the freshly-generated report. Record this one-line policy in the PR `## Decisions`.

REGENERATE THE COMMITTED REPORT (a runtime break CI does not catch, so it is
mandatory here). `ReplayLoader.tournament_report()` `model_validate`s the committed
`replays/samples/tournament-eval-report.json` at runtime, and the new `meeting_rate`
is a REQUIRED member of the frozen `extra="forbid"` `TournamentEvalReport`. So the
committed 4p/1i report (generated before this task) will FAIL to load once this task
lands → `GET /eval/tournament-report` 500s and the dashboard breaks. The eval-route
tests write their own report to `tmp_path`, so `uv run pytest` / `bash scripts/check.sh`
stay GREEN and miss it — this is a latent runtime break, not a CI failure. This task
MUST regenerate the committed `replays/samples/tournament-eval-report.json` from the
frozen 4p/1i replays so it carries `meeting_rate` — offline and free via
`eval.balance_eval.load_tournament_report` + `build_tournament_eval_report` (no
provider run; the 4p/1i replays themselves stay byte-identical, only the derived
report JSON gains the field, consistent with the "4p/1i frozen" decision). The 7p/2i
set's own report is generated fresh by Task 7.8 (post-this-task) and carries the
field natively.

Surface the numbers in `scripts/run_tournament.py::_format_summary` (the operator
print) — add `meetings_total`, a `meeting_rate` line (rendered as a percentage,
guarding the `None`/no-games case the way `decisive_split` already guards the
no-decisive-games case), and a trigger line showing `body=… emergency=…`. This is
the file that overlaps Task 7.1 (which threads `--tasks-per-crewmate` / roster
presets through the same CLI), which is why this task declares `Depends on: 7.1
merged`: 7.1 lands its CLI/summary edits first, then this task adds the
meeting-rate lines on top.

Surface the close-gate scalars in the regression suite: add
`meeting_rate`, `meetings_total`, `body_report_meetings`, and `emergency_meetings`
to `eval/prompt_regression.py::PromptRegressionMetrics`, populated in
`run_prompt_regression` from the new `evaluated.meeting_rate.*` fields (never
re-derived). This makes the Stage-A gate a byte-stable, committed-baseline scalar
like the other §11.3 metrics. NOTE: the single committed
`tests/fixtures/prompt_regression/baseline.json` (keyed by fixture name `v_a` /
`v_b`) will need its expected scalars extended to include the new fields;
regenerate it deterministically (the fixtures are frozen recorded replays, the
analyzers are pure — no provider runs) and commit the updated baseline so
`tests/eval/test_prompt_regression.py`'s exact-match assertion passes.

Mirror the new wrapper field across the served-eval-view chain and the frontend so
the schema-mirror stays 1:1. The eval HTTP route (`api/routes/eval.py`) re-models
the wrapper as `_TournamentEvalReportView` with `extra="forbid"` and re-validates
via `model_dump(mode="json")` → `model_validate`; because that view forbids extras,
a new field on `TournamentEvalReport` MUST be added to `_TournamentEvalReportView`
or `_redact_failed_calls` raises. Reuse `MeetingRateReport` verbatim by import there
(the metric reports are reused, only the failed-call leaf is re-typed). Note the
eval metric reports are NOT declared or re-exported in `api/schemas.py` — they are
imported directly from `eval/*` into `api/routes/eval.py` (where
`_TournamentEvalReportView` / `_TournamentReportEvalView` / `_GameReportEvalView`
live); `api/schemas.py` contributes only `EvalCostSummaryView` / `FailedCallEvalView`
to the eval route, neither of which changes here. So `api/schemas.py` needs NO edit
for this field and is NOT in scope.

**Snapshot tripwire — this is the blocking gate, not `api.schemas.__all__`.** Adding
`meeting_rate: MeetingRateReport` to `TournamentEvalReport` changes the recursive
JSON field set of that model, which trips `test_eval_report_field_set_snapshot` in
`tests/api/test_leak.py` (it asserts `actual == EXPECTED_EVAL_REPORT_FIELDS`, a
hardcoded `frozenset`). The six new field names — `meeting_rate`, `meetings_total`,
`games_total`, `games_with_meeting`, `body_report_meetings`, `emergency_meetings` —
are ALL absent from `EXPECTED_EVAL_REPORT_FIELDS` today, so the assertion fails and
`uv run pytest` / `bash scripts/check.sh` break unless the snapshot is extended. Add
`tests/api/test_leak.py` to Files-in-scope and extend `EXPECTED_EVAL_REPORT_FIELDS`
with exactly those six names (confirming none is engine/role state — they are pure
counts, so `FORBIDDEN_EVAL_ENGINE_FIELDS` and
`test_eval_report_surface_exposes_no_engine_state_field` stay green). Since `MeetingRateReport` is a pure aggregate of counts (no roles, no
transcripts, no internal engine types), it carries no leak risk — document that in
the field's docstring. Finally add a `MeetingRateReport` interface
to `frontend/src/types/api.ts` and the `meeting_rate` field to the
`TournamentEvalReport` interface there, with the nullable `meeting_rate: number |
null` faithful to `float | None` (the file's `## Decisions` note warns drift makes
the dashboard render `undefined`).

DESIGN DECISION — trigger breakdown source (read this; it shapes the whole task).
The trigger kind (body-report vs emergency-button) is NOT carried on
`eval.report_schema.MeetingReport` and is NOT on `orchestrator.replay.MeetingReplayEntry`
either — it lives only on the per-tick `engine.events.MeetingTriggeredEvent`
(`trigger: Literal["report","emergency"]`), which the report-building loader
(`eval/balance_eval.py::_meeting_report_from_entry`) does not fold in. Adding a
real `trigger_kind` field to the report would balloon scope (it would touch
`orchestrator/replay.py`, `eval/balance_eval.py`, and force re-recording every
committed sample — that re-record is Task 7.8's job, and those files are NOT in
this task's scope). So derive the breakdown from data already on `MeetingReport`:
classify a meeting as `body_report` iff the report submitted by the meeting's
`triggered_by` player (found in `meeting.transcript.reports`, matched by
`document.agent_id == meeting.triggered_by`) contains at least one
`meetings.schemas.FoundBodyObservation`; classify it `emergency` otherwise. This
matches the diagnosis ground truth (all observed meetings are body-reports; 0
emergency) and keeps the change additive and pure. Document this heuristic and its
TWO-FOLD limitation explicitly in the analyzer docstring: the `emergency` bucket is
a CATCH-ALL, not a positively-identified emergency-button count — it is
{true emergency-button meetings} ∪ {body-report meetings whose triggering report
lacked a `FoundBodyObservation`}. Today both are ~0 (the diagnosis shows 0/50
emergencies and a clean body-report path), so the bucket is accurate now; but a
future Wave that revives emergency-button play MUST NOT trust `emergency` as a pure
emergency count without first adding a real persisted `trigger_kind`. That cleaner
fix is deferred to a LATER PHASE (not Wave 0): it would touch `orchestrator/replay.py`
+ `eval/balance_eval.py`, which even Task 7.8 explicitly excludes — Task 7.8 only
re-records under THIS same derived heuristic, it does not add the field. Do NOT
widen scope to add the field here.

**Files in scope:**
- eval/meeting_quality.py
- eval/prompt_regression.py
- api/routes/eval.py
- frontend/src/types/api.ts
- tests/eval/test_tournament_report.py
- tests/eval/test_prompt_regression.py
- tests/api/test_eval_routes.py
- tests/api/test_leak.py
- tests/fixtures/prompt_regression/baseline.json
- replays/samples/tournament-eval-report.json (regenerate the committed 4p/1i report so it carries `meeting_rate`; offline/free, replays untouched — prevents the runtime load failure)

**Files NOT in scope:**
- api/schemas.py (the eval metric reports are NOT declared/re-exported here — they ride through `api/routes/eval.py`'s `_TournamentEvalReportView`; `api/schemas.py` only contributes `EvalCostSummaryView` / `FailedCallEvalView` to the eval route, neither of which changes for `meeting_rate`. No `api.schemas.__all__` edit is needed.)
- eval/report_schema.py (do NOT add a `trigger_kind` field to MeetingReport; trigger kind is derived, see the design decision)
- orchestrator/replay.py (MeetingReplayEntry stays as-is; no new persisted field)
- eval/balance_eval.py (the report loader is untouched; the metric reads existing MeetingReport data)
- scripts/run_tournament.py (the `_format_summary` surfacing is owned by Task 7.1's CLI edits this task depends on; coordinate the meeting-rate lines onto 7.1's merged version — listed here as the dependency edge, not an independent scope claim)
- replays/samples/ and scripts/refresh_samples.sh (sample regeneration is Task 7.8)
- orchestrator/seeder.py (roster / tasks-per-crewmate config is Task 7.1)
- frontend dashboard components (rendering the new field in the UI is optional/deferred; this task only mirrors the type)

**Definition of done:**
- [ ] `eval/meeting_quality.py` defines `MeetingRateReport` (frozen, `extra="forbid"`, fail-loud bucket validator) and `compute_meeting_rate`, and `build_tournament_eval_report` packs a fifth `meeting_rate` field on `TournamentEvalReport`.
- [ ] `meeting_rate` is `None` when `games_total == 0`; `body_report_meetings + emergency_meetings == meetings_total`; `games_with_meeting <= games_total` — all enforced by the validator and covered by tests.
- [ ] The trigger breakdown is derived from `MeetingReport` data only (triggering reporter's `FoundBodyObservation`); no field is added to `eval/report_schema.py`, `orchestrator/replay.py`, or `eval/balance_eval.py`.
- [ ] `eval/prompt_regression.py::PromptRegressionMetrics` carries `meeting_rate` / `meetings_total` / `body_report_meetings` / `emergency_meetings`, populated from `evaluated.meeting_rate.*`; the committed `tests/fixtures/prompt_regression/baseline.json` is regenerated and `tests/eval/test_prompt_regression.py` exact-match passes.
- [ ] `api/routes/eval.py::_TournamentEvalReportView` mirrors the new wrapper field (reusing `MeetingRateReport` by import); `_redact_failed_calls`'s round-trip and `tests/api/test_eval_routes.py` pass with the new field present. `api/schemas.py` is NOT edited (the metric reports do not live there).
- [ ] `tests/api/test_leak.py`'s `EXPECTED_EVAL_REPORT_FIELDS` (the `test_eval_report_field_set_snapshot` tripwire) is extended with the six new field names (`meeting_rate`, `meetings_total`, `games_total`, `games_with_meeting`, `body_report_meetings`, `emergency_meetings`); none is engine/role state, so `test_eval_report_surface_exposes_no_engine_state_field` still passes. Without this the snapshot assertion fails `uv run pytest`.
- [ ] `frontend/src/types/api.ts` adds a `MeetingRateReport` interface and the `meeting_rate` field on `TournamentEvalReport`, with `meeting_rate: number | null`.
- [ ] `CURRENT_FORMAT_VERSION` is NOT bumped: `meeting_rate` is a wrapper-level metric on `TournamentEvalReport`; the version-stamped inner `TournamentReport` and the persisted replay-record schema are unchanged. The no-bump policy + reason is recorded in the PR `## Decisions`.
- [ ] The committed `replays/samples/tournament-eval-report.json` (4p/1i) is regenerated offline (via `load_tournament_report` + `build_tournament_eval_report` over the frozen 4p/1i replays — no provider run) so it carries `meeting_rate` and re-validates as a `TournamentEvalReport`. Confirm `GET /eval/tournament-report` loads it post-change (e.g. an added test that loads the committed report through `ReplayLoader.tournament_report()`, since the existing eval-route tests use tmp fixtures and would otherwise miss this runtime break).
- [ ] `scripts/run_tournament.py` summary prints `meetings_total`, a `meeting_rate` percentage line (guarded for the no-games case), and a body/emergency trigger line (added onto Task 7.1's merged `_format_summary`).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `cd frontend && npm run tsc:check` passes.
- [ ] `cd frontend && npm run build` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**
Model the new analyzer directly on `eval/vote_correctness.py`: same module shape
(a frozen `*_Report` Pydantic model with a `model_validator(mode="after")` for the
bucket invariants + a pure `compute_*` fold that accepts `TournamentReport |
Sequence[GameReport]`), same `None`-when-undefined rate convention, no I/O and no
imports from `engine`/`agents`/`llm`. The fold is small:

```python
games = report.games if isinstance(report, TournamentReport) else tuple(report)
games_total = len(games)
games_with_meeting = sum(1 for g in games if g.meetings)
meetings_total = sum(len(g.meetings) for g in games)
body = sum(
    1
    for g in games
    for m in g.meetings
    if _is_body_report(m)
)
emergency = meetings_total - body
rate = games_with_meeting / games_total if games_total > 0 else None
```

`_is_body_report(meeting)` scans `meeting.transcript.reports` for the document
whose `agent_id == meeting.triggered_by` and returns `True` iff that document has
any `FoundBodyObservation` in its `observations`. A meeting with no matching
report (malformed/partial replay) classifies as `emergency` and never raises —
match the partial-replay robustness the other analyzers state. The docstring must
state the TWO-fold catch-all nature of the `emergency` bucket (see the design
decision above) so a later emergency-reviving Wave does not trust it blindly. Add `MeetingRateReport`
and `compute_meeting_rate` to `eval/meeting_quality.py`'s `__all__`.

Test-file placement (note the deliberate asymmetry vs. `vote_correctness.py`, which
has its own `tests/eval/test_vote_correctness.py`): `compute_meeting_rate` lives in
`eval/meeting_quality.py` (the wrapper/builder module), so its unit tests go in
`tests/eval/test_tournament_report.py` (already in scope), NOT a new
`test_meeting_quality.py`. Put the focused unit coverage there: the bucket-validator
invariants (`body + emergency == meetings_total`, `games_with_meeting <= games_total`),
the `None`-rate-iff-`games_total==0` edge, and the body-vs-emergency classification
edge cases for `_is_body_report` (matching report with a `FoundBodyObservation`,
matching report WITHOUT one, and no matching report at all → `emergency`).

For the regression fixtures: after extending `PromptRegressionMetrics`, run each
fixture dir (`v_a`, `v_b`) through `run_prompt_regression` and dump the summaries
to regenerate the single `tests/fixtures/prompt_regression/baseline.json` (the
object keyed by fixture name that `_load_baseline` parses) — the suite is
deterministic and model-free, so this is reproducible (see the
`eval/prompt_regression.py` module docstring's "regenerating fixtures" note; you
only re-dump the baseline scalars, you do NOT re-record replays). The new
meeting-rate scalars should be identical across `v_a` and `v_b` (the v_b variant
only flips one alibi contradiction; it changes neither the meeting count nor the
trigger classification), which is a useful sanity check that the metric is
orthogonal to the prompt-version change.

For `api/routes/eval.py`: `_TournamentEvalReportView` already reuses the four
metric reports verbatim by import — add `meeting_rate: MeetingRateReport` to it the
same way (import `MeetingRateReport` from `eval.meeting_quality`). Confirm
`tests/api/test_eval_routes.py` builds its fixture via `build_tournament_eval_report`
so the new field is present in the dumped payload that `_redact_failed_calls`
re-validates; the existing round-trip test exercises the full chain.

**Public types introduced:**
- eval.meeting_quality.MeetingRateReport

**Ready-to-paste prompt:** `agent_prompts/task-7-3-meeting-rate-metric.md`

### Task 7.4 — Roster-aware replay loader + two-committed-set layout (plumbing)
**Branch:** `phase-7-roster-aware-loader-layout`
**Depends on:** 7.1 merged, 7.2 merged
**Section refs:** tasks/phase-7-plan.md W0.4, Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §11.4
**Complexity:** Integration

This is the dispatchable CODE half of Wave 0's eval-set work (split from the
real-provider OPERATIONAL half, Task 7.8). It teaches the replay loader to
reconstruct a SECOND committed roster set and lays the directory/manifest plumbing
for it, validated entirely on the FAKE provider — NO real-provider spend and NO
committed sample data here (that is Task 7.8). Splitting the plumbing out lets this
loader + firewall change land as a normal reviewed PR with the static gates green
BEFORE any money is spent, and it has no dependency on the `meeting_rate` metric so
it can run in PARALLEL with 7.3.

Because the project commits two roster sets, the central design decision in this
task is the **directory layout for two committed sets and the loader change it
forces**. The replay JSONL persists no roster header (a tick row carries only
`game_id`, `tick`, `actions`, `state_hash` — verified against
`replays/samples/replay-seed-0.jsonl`), and `ReplayLoader._walk` re-seeds with
`num_players=_infer_num_players(...)` but a hardcoded
`num_impostors=DEFAULT_NUM_IMPOSTORS` (`api/replay_loader.py:419-424`).
`num_players` is recoverable from the action ids, but `num_impostors` is NOT
inferable, so a 7p/2i replay re-seeded as 7p/1i assigns the wrong roles and the
per-tick `state_hash` check in `_walk` raises `ReplayStateMismatchError`. The same
playback path is what `scripts/_verify_samples.py::verify_samples` drives to prove
byte-identical reconstruction. Therefore the second committed set requires the
loader to learn each set's `num_impostors` AND `tasks_per_crewmate`. Pick a layout
and a roster-config mechanism, and record both in the PR `## Decisions` block.

**Recommended shape (self-consistent with the preserved-default requirement — pick
this unless you record a different one):** keep the existing **4p/1i set FLAT at
`replays/samples/`** with NO roster sidecar — do not move it into a subdir — so the
"flat directory + no sidecar ⇒ MVP 4p/1i re-seed" default holds and the committed
4p/1i set keeps reconstructing unchanged. The new set will live as a subdirectory
`replays/samples/7p2i/` carrying its own `MANIFEST.md` and a small committed roster
sidecar (`roster.json` with `num_players`/`num_impostors`/`tasks_per_crewmate`) —
this task builds the SUPPORT for that layout (loader reads it, refresh/manifest
route to it) and exercises it on tmp dirs; Task 7.8 commits the actual data into it.
The asymmetric shape (flat 4p/1i + one subdir) is deliberate — the symmetric
"both sets in subdirs" layout is REJECTED because it cannot coexist with the
"flat `replays/samples/` default = 4p/1i" invariant (if 4p/1i moves into
`replays/samples/4p1i/`, the flat dir is no longer the 4p/1i set). If you instead
choose the symmetric both-subdirs layout, you MUST drop the flat-default-is-4p1i
preservation claim and update `api/main.py`'s resolution — but `api/main.py` is out
of scope here, so the asymmetric shape is the recommended one.

The roster descriptor is parsed into a pinned, FROZEN `api.replay_loader.RosterConfig`
dataclass (fields exactly `num_players: int`, `num_impostors: int`,
`tasks_per_crewmate: int`) by a single named helper (e.g.
`_load_roster_config(dir) -> RosterConfig`) that FAILS LOUD — raises, never
defaults — on a missing key, a wrong type, or a non-positive value. A flat
directory with NO `roster.json` is the ONLY path that defaults (to MVP 4p/1i:
`num_impostors=DEFAULT_NUM_IMPOSTORS`, `tasks_per_crewmate=1`); a present-but-
malformed descriptor raises rather than falling back (AGENTS.md "no silent
fallbacks").

**How each set is consumed (the non-recursive glob is intentional).** All four
seed-file globs are NON-recursive — `ReplayLoader._replay_paths`
(`api/replay_loader.py:870`: `self._replay_dir.glob("replay-seed-*.jsonl")`),
`scripts/_verify_samples.py::sample_paths` (line 75),
`scripts/_manifest_writer.py::discover_seeds` (line 118), and
`api/main.py::_resolve_replay_dir` (line 83). Do NOT make them recurse. Instead each
committed set is consumed by constructing `ReplayLoader(replay_dir=<that set's dir>)`
with its own root: `replays/samples/` for 4p/1i (descriptor absent ⇒ defaults to
4p/1i), and `replays/samples/7p2i/` for the new set (its `roster.json` is read so
`_walk` re-seeds with `num_impostors=2, tasks_per_crewmate=2` instead of the
`DEFAULT_NUM_IMPOSTORS` constant). `verify_samples` / the new tests pass the subdir
explicitly as the `sample_dir`. The served/default set via `api/main.py` (out of
scope) stays the flat `replays/samples/` 4p/1i.

This task is dispatchable as a normal headless web session — it validates entirely
on the FAKE provider (the hermetic multi-impostor test below builds its own tiny
2-impostor replay in `tmp_path`), commits NO `replays/samples/` data, and does NOT
touch `frontend/`. The real-provider generation, balance validation, and commit of
the 7p/2i set is Task 7.8, which depends on this task.

**Files in scope:**
- scripts/refresh_samples.sh
- scripts/_manifest_writer.py
- api/replay_loader.py
- tests/scripts/test_refresh_samples.py
- tests/scripts/test_manifest_writer.py
- tests/api/test_replay_loader.py

**Files NOT in scope:**
- replays/samples/ (committing the real 7p/2i data is Task 7.8; this task validates on tmp dirs only and commits no sample data)
- scripts/run_tournament.py (the roster/task flags are owned by 7.1; consume them, do not edit)
- orchestrator/seeder.py (the `tasks_per_crewmate` knob is 7.1's; consume it)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's; this task does NOT read it — the gate check is Task 7.8)
- scripts/_verify_samples.py (reuses ReplayLoader for reconstruction; it must keep passing, but its own logic is unchanged)
- scripts/verify_samples.sh (NOT edited — it already accepts an optional `SAMPLE_DIR` arg, used per-set by Task 7.8)
- frontend/ (the browse selector for the two sets is a separate later track)
- api/main.py (replay-dir resolution is unchanged; the loader gains per-set roster awareness, not a new env contract)
- DESIGN.md (design-thread-owned)

**Definition of done:**
- [ ] The two-set directory layout + per-set roster-config mechanism is implemented: the loader reads a per-set `roster.json` parsed into a pinned FROZEN `api.replay_loader.RosterConfig` (`num_players`/`num_impostors`/`tasks_per_crewmate`) via a single named helper that FAILS LOUD on a missing key / wrong type / non-positive value; a flat directory with NO descriptor is the only default path (MVP 4p/1i: `num_impostors=DEFAULT_NUM_IMPOSTORS`, `tasks_per_crewmate=1`); a present-but-malformed descriptor raises.
- [ ] `api/replay_loader.py` re-seeds each replay UNCONDITIONALLY with that set's recorded `num_impostors` AND `tasks_per_crewmate` from the descriptor (when present), instead of the hardcoded `DEFAULT_NUM_IMPOSTORS` and the seeder's `tasks_per_crewmate` default. Both feed `seed_initial_state` and the `WorldState` that `orchestrator/replay.py::_state_hash` serializes (incl. `tasks`), so a wrong value ALWAYS raises `ReplayStateMismatchError` (mandatory, not "sometimes"). The flat-directory 4p/1i default re-seed stays byte-identical to today.
- [ ] `scripts/refresh_samples.sh` + `scripts/_manifest_writer.py` route to the correct per-set directory + manifest (via the existing `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST` env hooks) and thread 7.1's `--num-players`/`--num-impostors`/`--tasks-per-crewmate` flags into the `run_tournament.py` invocation; the `--dry-run` echo block additionally prints the resolved roster, the per-set `SAMPLE_DIR`/`MANIFEST`, and the threaded `run_tournament.py` invocation so per-set routing is observable without spend.
- [ ] `tests/api/test_replay_loader.py` covers multi-impostor reconstruction HERMETICALLY: build a tiny `HeadlessGame(num_impostors=2, ...)` on the FAKE provider, persist it to `tmp_path` with a matching `roster.json`, read it back, and assert (a) it reconstructs byte-identically (no `ReplayStateMismatchError`) when the descriptor names 2 impostors; (b) a descriptor naming the WRONG `num_impostors`/`tasks_per_crewmate` raises `ReplayStateMismatchError` (descriptor is load-bearing); (c) a flat dir with no descriptor still defaults to 4p/1i. No dependency on any committed 7p/2i data.
- [ ] `tests/scripts/test_refresh_samples.py` and `tests/scripts/test_manifest_writer.py` cover the per-set directory/manifest routing on tmp dirs (e.g. a `--dry-run` into a 7p2i set targets that set's directory + manifest), without spending on the real provider.
- [ ] No real-provider spend; NO `replays/samples/` data is committed in this task (that is Task 7.8). The existing flat 4p/1i committed set still reconstructs byte-identically.
- [ ] The PR `## Decisions` block records the chosen two-set directory layout + roster-descriptor format.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `api/replay_loader.py` (`_walk` at lines 402-424 — the `num_impostors=
DEFAULT_NUM_IMPOSTORS` hardcode and the `_infer_num_players` call — plus
`_replay_paths` at line 866 and `_resolve_path`), `scripts/refresh_samples.sh` (the
`SAMPLE_DIR`/`MANIFEST` env overrides at lines 28-30, the per-seed
stage→`mv`→`_manifest_writer.py update` loop at lines 220-242, and the
`run_tournament.py` invocation at lines 226-230 where the new roster/task flags must
be threaded), `scripts/_manifest_writer.py` (`update_manifest`, `build_row`, the
`--sample-dir`/`--manifest` args), and `scripts/_verify_samples.py::verify_samples`
(it builds a `ReplayLoader(sample_dir)` and calls `load_replay`, so the loader's
roster fix is what makes a 7p/2i set verifiable). Keep the roster descriptor minimal
and explicit (no inference) so the loader fails loud on a missing/mismatched roster
rather than silently re-seeding wrong — the per-tick `state_hash` check is the
backstop, but an explicit descriptor makes the cause legible. Do NOT generate or
commit any real sample data, and do NOT batch any engine/agent behavior change in;
this is pure plumbing riding on 7.1/7.2.

**Public types introduced:**
- api.replay_loader.RosterConfig

**Integration risk:**

This task changes a loader contract that the determinism gate and the leak firewall
both ride on — but it spends no money and commits no data, so it lands green on the
fake provider before Task 7.8's spend.

- **Loader roster contract is the blast radius.** Re-seeding a replay with the
  wrong `num_impostors`/`tasks_per_crewmate` does not corrupt silently — the
  per-tick `state_hash` check in `_walk` raises `ReplayStateMismatchError` — but it
  fails the whole determinism gate. The descriptor must be read before re-seeding,
  and the flat-directory default must stay EXACTLY 4p/1i or the existing committed
  set regresses.
- **Two sets, two manifests, one refresh script.** `refresh_samples.sh` and
  `_manifest_writer.py` must route to the correct per-set directory/manifest via
  the existing `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST` hooks; a mis-routed refresh
  (in Task 7.8, using this plumbing) would overwrite the 4p/1i baseline, so the
  routing must be proven on tmp dirs here.
- **Firewall on multi-impostor reconstruction.** The hermetic 2-impostor test is
  the first multi-impostor reconstruction; confirm the 7.2 `fellow_impostor_ids`
  invariant holds on the rebuilt packets. The end-to-end check on a real committed
  multi-impostor set is Task 7.8.
- **Dispatchable, fake-validated.** Unlike Task 7.8, this task is a normal
  reviewed PR — no `ANTHROPIC_API_KEY`, no committed sample data; the static gates
  + the hermetic tests are the whole acceptance surface.

**Ready-to-paste prompt:** `agent_prompts/task-7-4-roster-aware-loader-layout.md`

### Task 7.5 — Ollama provider client + wiring
**Branch:** `phase-7-ollama-provider-client`
**Depends on:** none
**Section refs:** tasks/phase-7-plan.md "Provider / eval-infra track", Q2 (now superseded — provider = local Ollama); the Phase 7 Ollama-enablement plan (model = `qwen2.5:7b-instruct`); DESIGN.md §5, §7 (LLM client contract)
**Complexity:** Integration

Phase 7's eval-set task (7.8) must run a high volume of 7-player meeting calls, and
the diagnosis showed that doing this on a hosted frontier model is both expensive
(~$150+ over the phase) and brittle (real-model meeting reports crash the strict
discriminated-union schemas). The decision is to make the canonical
agent-intelligence provider a **local Ollama** open model — `qwen2.5:7b-instruct`,
free, self-hosted on the owner's Mac — keeping the existing Anthropic path as a
still-supported alternative and the frozen 4p/1i baseline (replays are
model-agnostic) intact. This task adds the provider client and wires it into the
default-client selection so the rest of the substrate (7.6 parse-tolerance, 7.7
provider-agnostic refresh, 7.8 eval set) can target it.

Add a new `llm/ollama_client.py` implementing the `LLMClient` Protocol
(`llm/client.py:157`) — `async def complete(*, prompt, schema, max_tokens,
temperature, call_kind, model, agent_id) -> LLMResponse` — mirroring the shape of
`AnthropicClient` (`llm/provider.py:127`) and `FakeProvider` (`llm/fake_provider.py`).
The client POSTs to the local Ollama server at `AILIBI_OLLAMA_HOST` (default
`localhost:11434`), passing **`format` = `schema.model_json_schema()`** for
constrained (schema-shaped) decoding when a schema is supplied, and an `options`
block carrying `temperature` plus a `seed` for reproducible generation. The Ollama
`options.seed` is derived from the per-GAME seed (so different games don't collide
and a game is reproducible-ish), NOT a single constant or a per-call hash. Map
Ollama's `prompt_eval_count` / `eval_count` response counters onto `TokenUsage`, and
set **`cost_usd = 0.0`** (a local model is free). REUSE the shared helpers from
`llm/provider.py` rather than re-implementing them: `_extract_json_block`
(`llm/provider.py:335`) to pull the JSON out of the raw model text, the existing
`_compute_cost_usd` cost path (with a `$0` Ollama entry / a rate of 0), and the
`LLMCallFailure` / parse-failure-attachment behavior (`llm/provider.py:62,278`) so a
malformed local output becomes a recoverable FailedCall, never a hard crash. The `$0`
rate is keyed by PROVIDER (ollama → `cost_usd` 0 regardless of model), with an
optional per-model override — NOT keyed by model name, so swapping
`qwen2.5:7b`→`llama3.1:8b` for an A/B does not silently fall back to a non-zero rate.

Wire it into `build_default_client` (`llm/provider.py:214`): add a
`PROVIDER_OLLAMA = "ollama"` constant and an env branch that constructs the
`OllamaClient`, reusing the `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL`
model knobs (with an Ollama-appropriate default of `qwen2.5:7b-instruct` for both).
The existing Anthropic branch STAYS in `build_default_client` (it is not dead code):
it is retained for (a) re-recording the frozen 4p/1i baseline if it is ever
deliberately rotated, and (b) optional cross-provider validation — so a future
reader does not delete it.
**Budget nuance (critical, do not skip):** `BudgetedLLMClient` pre-flight estimates
cost from `_DEFAULT_COST_PER_INPUT_TOKEN_USD` / `_DEFAULT_COST_PER_OUTPUT_TOKEN_USD`
(`llm/budgeted_client.py:69`), and `GameBudget` caps USD **and** tokens
(`llm/budget.py:96`). For Ollama the USD dimension must never block a free run: set
the pre-flight estimation rates to **0** for the Ollama client (and/or treat
`max_cost_usd` as effectively infinite for this provider), while KEEPING the token
caps intact (a local model can ramble — the token ceiling is the real backstop,
parametrized in 7.7). Do this in a way that leaves the Anthropic budget behavior
exactly as-is.

Add the `ollama` package (the official Python client) to `pyproject.toml` and refresh
`uv.lock` (only `anthropic==0.104.1` is present today). Add the operator config and
docs: `.env.example` gains `AILIBI_LLM_PROVIDER=ollama`, `AILIBI_OLLAMA_HOST`, and
the model knobs defaulting to `qwen2.5:7b-instruct`; `README.md` gains the local-setup
steps (install Ollama → `ollama pull qwen2.5:7b-instruct` → `ollama serve`); and
`AGENTS.md` gets a short note that Ollama is a supported provider and CI never hits
it. (The DESIGN.md §7 provider note is design-thread-owned and is NOT in this
contract's scope.)

Tests: `tests/llm/test_ollama_client.py` unit-tests the client by MOCKING the HTTP
call (assert the request carries `format = schema.model_json_schema()` and the
seed/temperature options; assert token mapping and `cost_usd == 0.0`; assert a
malformed body surfaces as a FailedCall, not an exception). Add an **opt-in,
server-gated** integration marker mirroring the existing `real_provider` gate
(`tests/llm/test_client.py:790`) — e.g. skip unless `AILIBI_RUN_OLLAMA_TESTS=1` and a
reachable server — so CI (which has no Ollama server) always skips it and never hits
the network.

Determinism note: the recording/replay layer captures the client's outputs, so a
recorded Ollama game replays byte-identically without the server; the `seed`
only matters for fresh generation, not replay. Fresh generation may drift across
Ollama/runtime versions; byte-identical determinism is guaranteed only via the
replay-record path (recorded outputs replay exactly), NOT via re-running a seed
fresh. This task does NOT generate or commit any sample data (that is 7.8) and does
NOT change the `LLMClient` Protocol itself — it implements it.

**Files in scope:**
- llm/ollama_client.py
- llm/provider.py
- llm/budgeted_client.py
- llm/budget.py
- pyproject.toml
- uv.lock
- .env.example
- README.md
- AGENTS.md
- tests/llm/test_ollama_client.py

**Files NOT in scope:**
- llm/client.py (the `LLMClient` Protocol is implemented, not changed)
- llm/fake_provider.py (the fake provider is the CI default and is untouched; mirror its shape, do not edit it)
- llm/cache.py (the response cache is provider-agnostic; no change needed)
- scripts/refresh_samples.sh, eval/balance_eval.py (provider-agnostic refresh + per-game budget knob are Task 7.7)
- replays/samples/ (no sample generation here; that is Task 7.8)
- DESIGN.md (the §7 provider note is design-thread-owned)
- frontend/ (no frontend surface for the provider choice)

**Definition of done:**
- [ ] `llm/ollama_client.py` defines `OllamaClient` implementing the `LLMClient` Protocol's `async def complete(...) -> LLMResponse`; it POSTs to `AILIBI_OLLAMA_HOST` (default `localhost:11434`), passes `format = schema.model_json_schema()` for constrained decoding when a schema is given, and sets `options` with `temperature` + a `seed` derived from the per-game seed (not a constant or per-call hash).
- [ ] Token usage is mapped from Ollama's `prompt_eval_count` / `eval_count` onto `TokenUsage`, and `cost_usd == 0.0` for every Ollama response (a `$0` entry on the cost path / a rate of 0).
- [ ] The client REUSES `_extract_json_block`, the `_compute_cost_usd` path, and the `LLMCallFailure` / parse-failure-attachment behavior from `llm/provider.py` so a malformed local output is a recoverable FailedCall, not a crash (covered by a test).
- [ ] `build_default_client` (`llm/provider.py:214`) gains `PROVIDER_OLLAMA = "ollama"` and an env branch that constructs `OllamaClient`, reusing `AILIBI_LLM_MEETING_MODEL` / `AILIBI_LLM_TRIGGER_MODEL` with an Ollama default of `qwen2.5:7b-instruct`; the existing `fake` and `anthropic` branches are unchanged.
- [ ] The USD budget dimension is disabled for Ollama (pre-flight estimation rates → 0 and/or `max_cost_usd` effectively infinite for this provider) while the **token** caps stay intact; the Anthropic budget behavior is unchanged. Covered by a test asserting an Ollama pre-flight does not trip the USD ceiling.
- [ ] `ollama` is added to `pyproject.toml` and `uv.lock` is refreshed; `.env.example`, `README.md`, and `AGENTS.md` document the Ollama provider, host, and model knobs defaulting to `qwen2.5:7b-instruct`.
- [ ] `tests/llm/test_ollama_client.py` unit-tests the client with the HTTP call mocked (request shape incl. `format`/seed/temperature, token mapping, `cost_usd == 0.0`, malformed-body → FailedCall), plus an opt-in server-gated marker (e.g. `AILIBI_RUN_OLLAMA_TESTS=1` + reachable server) that CI skips — mirroring the `real_provider` gate.
- [ ] The `LLMClient` Protocol (`llm/client.py`) and `llm/fake_provider.py` are unchanged; CI never hits the network (the server-gated test is skipped without the env flag).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `llm/provider.py` end to end first — `AnthropicClient.complete` (line 127), the
shared `_extract_json_block` (line 335), the `_compute_cost_usd` path, the
`_attach_parse_failure` / `LLMCallFailure` behavior (lines 62, 278), and
`build_default_client` (line 214) — and model `OllamaClient.complete` on the
Anthropic one, swapping the transport for an Ollama `/api/generate` (or `/api/chat`)
POST with `format=schema.model_json_schema()`, `stream=False`, and
`options={"temperature": temperature, "seed": <derived-from-per-game-seed>}`. The official `ollama`
Python client returns a dict carrying `response` (the text), `prompt_eval_count`,
and `eval_count`; pull the JSON out of `response` with the SAME `_extract_json_block`
+ `schema.model_validate_json` path the Anthropic client uses, so 7.6's normalization
(applied in that shared path) automatically covers Ollama too. For the budget knob,
look at how `BudgetedLLMClient` is constructed around the provider client and pass
zeroed cost-estimation rates for the Ollama branch (the constructor already accepts
explicit rates — see the `_DEFAULT_COST_PER_*` comment at `llm/budgeted_client.py:69`),
leaving `GameBudget`'s token caps untouched. For the server-gated test, copy the
`real_provider` skip idiom at `tests/llm/test_client.py:790` (an env-flag +
reachability guard) so the integration case is opt-in. Add `ollama` with
`uv add ollama` so `pyproject.toml` + `uv.lock` move together; pin `ollama` to an
exact version in `pyproject.toml` (matching the repo's exact-pin convention, e.g.
`anthropic==0.104.1`), since `ollama` is pre-1.0 and its API can shift across minor
versions. Keep the Anthropic path byte-identical — only ADD the Ollama branch and
the zeroed-rate wiring.

**Public types introduced:**
- llm.ollama_client.OllamaClient

**Integration risk:**

This task adds a second real provider behind the audited `LLMClient` boundary and
touches the budget pre-flight, so the risks are (a) the network: CI must never reach
Ollama, mitigated by the opt-in `AILIBI_RUN_OLLAMA_TESTS` server gate and the unit
tests using a mocked transport; (b) the budget pre-flight: zeroing the USD dimension
must NOT also disable the token caps (a local model can ramble unbounded), so the
token ceiling stays and only the dollar estimate goes to 0, and the Anthropic budget
path must be provably unchanged; (c) determinism: the client must not perturb the
record/replay contract — outputs are captured and replayed model-agnostically, and
the fixed `seed` only affects fresh generation; (d) malformed local output: a weak
local model can emit schema-invalid JSON, so the FailedCall path (not an exception)
must be exercised by a unit test here, with the deeper normalization landing in 7.6.

**Ready-to-paste prompt:** `agent_prompts/task-7-5-ollama-provider-client.md`

### Task 7.6 — Parse-tolerance / normalization layer for model reports
**Branch:** `phase-7-report-parse-tolerance`
**Depends on:** 7.5 merged
**Section refs:** tasks/phase-7-plan.md "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (real-model reports crash the strict discriminated-union schemas); DESIGN.md §5 (LLM client contract), §6 (meeting schemas)
**Complexity:** Medium

The strict meeting/report schemas use discriminated unions with `extra="forbid"`,
and real models — especially the local `qwen2.5:7b-instruct` from Task 7.5 — emit
JSON that is *almost* right but carries fields that do not belong to the matched
union variant (the diagnosed failure: a `co_present` key on a `found_body`
observation). Under `extra="forbid"` that is a hard validation error, which today
becomes a FailedCall and a lost meeting. This task adds a small, well-tested
normalization step that strips keys not valid for the matched discriminated-union
variant *before* `schema.model_validate_json`, so a near-miss model output is
salvaged into a valid report instead of being dropped.

The normalization is applied in the SHARED extract→validate path in
`llm/provider.py` (right after `_extract_json_block`, before
`schema.model_validate_json`), so it protects EVERY provider — Anthropic and the new
Ollama client (7.5) — and the determinism/replay path that runs through the same
code. Because 7.5 routes its parse through that same shared path, this single change
covers both providers without per-client duplication. Put the actual logic in a
small new `llm/` helper module (a pure function over a parsed dict + the target
schema) so it is independently unit-testable and carries no provider/transport
imports; `llm/provider.py` just calls it in the validate path.

The normalization must be CONSERVATIVE and discriminator-aware: it resolves which
union variant the payload matches (via the schema's discriminator / the present
required keys), then drops only keys that are not declared on that variant — it must
NOT invent or rename fields, must NOT touch a payload that already validates, and
must leave non-union schemas untouched. Optionally add a bounded re-ask-on-invalid
retry (one re-prompt when validation still fails after normalization) — keep it
strictly bounded and OFF by default if it complicates determinism; the field-stripping
normalizer is the required core, the retry is the optional extra.

Determinism is a hard constraint: normalization is a pure deterministic function of
the parsed JSON + schema (no RNG, no clock, no network), so a recorded game replays
byte-identically and the frozen 4p/1i baseline is unaffected (its recorded outputs
already validate, so the normalizer is a no-op on them — assert this).

Residual risk (NOT something to fix here): the normalizer TRUSTS the discriminator
value. A payload with a wrong/mismatched discriminator (e.g. `type: saw_player` but
a `found_body`-shaped body) is NOT repaired — stripping to the named variant's
fields would corrupt it — so it remains a FailedCall. The normalizer never infers
the correct variant from body shape.

**Files in scope:**
- llm/provider.py
- llm/report_normalize.py
- tests/llm/test_report_normalize.py
- tests/llm/test_provider.py

**Files NOT in scope:**
- llm/client.py (the `LLMClient` Protocol is unchanged)
- llm/ollama_client.py (7.5's client parses through the shared `llm/provider.py` path; this task does NOT edit the client — the normalization lands in the shared path so it covers Ollama automatically)
- llm/fake_provider.py (the fake provider emits already-valid payloads; untouched)
- meetings/ and the schema definitions themselves (the discriminated-union schemas are NOT relaxed — `extra="forbid"` stays; this task normalizes the payload, it does not loosen the contract)
- replays/samples/ (no re-recording; the normalizer is a no-op on already-valid recorded outputs)
- scripts/refresh_samples.sh, eval/balance_eval.py (provider-agnostic refresh + budget are Task 7.7)
- DESIGN.md (design-thread-owned)
- frontend/ (no frontend surface)

**Definition of done:**
- [ ] A new `llm/report_normalize.py` exposes a pure function that, given a parsed JSON payload and a target (possibly discriminated-union) schema, strips keys not declared on the matched variant — without inventing/renaming fields, without altering a payload that already validates, and leaving non-union schemas untouched.
- [ ] The normalizer is invoked in the SHARED extract→validate path in `llm/provider.py` (after `_extract_json_block`, before `schema.model_validate_json`), so it protects Anthropic, the Ollama client (7.5), and the replay path through one code site.
- [ ] The diagnosed failure is covered: a `found_body` observation carrying a stray `co_present` key validates after normalization (a regression test pins exactly this case); a payload that is already valid is returned byte-identical (no-op); a payload missing a *required* field still fails loud (normalization does not mask genuinely-invalid output).
- [ ] If the optional bounded re-ask-on-invalid retry is implemented, it is strictly bounded (a single re-prompt) and does not break determinism/replay (off by default or pure under replay); if omitted, that omission is noted in the PR `## Decisions`.
- [ ] Determinism holds: the normalizer is a pure function (no RNG/clock/network); the frozen 4p/1i recorded outputs already validate, so the normalizer is a no-op on them and byte-identical replay is preserved (asserted by the existing determinism suite staying green).
- [ ] A test in `tests/llm/` asserts the normalizer is a NO-OP on already-valid recorded outputs by loading + reconstructing the committed 4p/1i baseline set after the normalizer lands (byte-identical) — an explicit assertion, not just relying on `check.sh`.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Find the single place in `llm/provider.py` where extracted text is validated —
`_extract_json_block(...)` followed by `schema.model_validate_json(...)` — and insert
the normalizer between the parse and the validate (parse the extracted text to a
`dict` first, normalize, then `schema.model_validate(normalized)`), so all providers
share it. For the discriminator-aware stripping, use THIS technique (simpler than
Pydantic core-schema internals): the report/observation/claim unions use
`Field(discriminator="type")` and each variant is a model carrying
`type: Literal[...]`. So: read the payload's `type` value, map it to the variant
model whose `type` Literal equals it, and keep ONLY that variant's declared
`model_fields` (stripping extras/misplaced keys), then validate. Build the
`{discriminator value → variant model}` map from the union's members. Keep the helper transport-free and side-effect-free so `tests/llm/test_report_normalize.py`
can table-test it directly: the `co_present`-on-`found_body` case, an already-valid
payload (no-op), a missing-required-field payload (still raises), and a non-union
schema (untouched). The `lint-imports` contract forbids new cross-layer imports, so
keep `llm/report_normalize.py` importing only stdlib + pydantic + the schema types it
already may see — no `engine`/`agents` imports.

**Ready-to-paste prompt:** `agent_prompts/task-7-6-report-parse-tolerance.md`

### Task 7.7 — Provider-agnostic refresh + parametrized per-game budget
**Branch:** `phase-7-provider-agnostic-refresh`
**Depends on:** 7.1 merged, 7.4 merged, 7.5 merged
**Section refs:** tasks/phase-7-plan.md W0.4, "Provider / eval-infra track"; the Phase 7 Ollama-enablement plan (refresh must select Ollama; 7-player meetings need a higher token budget); DESIGN.md §9, §11.4
**Complexity:** Medium

The sample-refresh path is hard-wired to Anthropic and to a tight per-game budget
that the diagnosis showed is too low for 7-player meetings. Task 7.8 runs the
meeting-heavy eval set on the local Ollama provider (7.5), so this task makes the
refresh provider-agnostic and parametrizes the per-game budget so a free, local,
higher-token run is possible without editing the script each time.

`scripts/refresh_samples.sh`: stop forcing `AILIBI_LLM_PROVIDER=anthropic`; allow
`ollama` (and keep `anthropic` working). Replace the hard `ANTHROPIC_API_KEY`
preflight with a **provider-aware** check: for `anthropic`, keep requiring the API
key; for `ollama`, instead ping `AILIBI_OLLAMA_HOST` for reachability AND confirm the
configured model (`qwen2.5:7b-instruct`) is actually pulled (fail loud with a clear
message if the server is down or the model is missing — AGENTS.md "no silent
fallbacks"). The `--dry-run` echo must show the selected provider and which
preflight ran. EXTEND Task 7.4's merged `--dry-run` echo block (the roster /
`SAMPLE_DIR` lines) with the provider + preflight lines — do NOT replace it (7.7
depends on 7.4, so it builds on the merged version).

Parametrize the per-game budget. Today `eval/balance_eval.py:221` constructs
`GameBudget(max_cost_usd=1.00)` with a fixed cost cap and token caps. Introduce an
env knob (e.g. `AILIBI_MAX_COST_USD`) read by `eval/balance_eval.py` so the per-game
USD cap is configurable, and scale the **token** caps to the roster (a 7-player
meeting needs more tokens than a 4-player one) via a named-constant LINEAR form:
`max_input_tokens = BASE_INPUT + PER_PLAYER_INPUT * num_players` and
`max_output_tokens = BASE_OUTPUT + PER_PLAYER_OUTPUT * num_players` with NAMED
constants (not magic numbers). Choose the constants so the **4p/1i preset
reproduces today's `GameBudget` caps exactly** (the frozen baseline path is
unchanged when the knob is unset); 7p/2i then resolves to a larger cap. For the
Ollama provider the USD cap is effectively disabled (per 7.5's zeroed cost
dimension), so on Ollama the token caps are the operative ceiling and must be large
enough to fit 7-player meetings.

This task consumes 7.1's roster/task flags (already threaded into the refresh by
7.4) and 7.5's Ollama provider; it does NOT add new CLI flags to
`scripts/run_tournament.py` (the budget is an env knob on the harness, not a new
tournament flag) and does NOT edit the Ollama client or the loader. It runs in
PARALLEL with 7.6 (disjoint files). No sample data is generated or committed here
(that is 7.8); the refresh changes are validated on the fake provider + dry-run.

**Files in scope:**
- scripts/refresh_samples.sh
- eval/balance_eval.py
- tests/scripts/test_refresh_samples.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- scripts/run_tournament.py (no new tournament CLI flag — the budget is an env knob on the harness; the roster/task flags are 7.1's)
- llm/ollama_client.py, llm/provider.py, llm/budgeted_client.py, llm/budget.py (the provider client + budget-dimension wiring are Task 7.5; this task only reads an env knob into the per-game `GameBudget` construction)
- api/replay_loader.py, scripts/_manifest_writer.py (the roster-aware loader + per-set manifest routing are Task 7.4; consume them, do not edit)
- replays/samples/ (no sample generation; that is Task 7.8)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's)
- DESIGN.md (design-thread-owned)
- frontend/ (no frontend surface)

**Definition of done:**
- [ ] `scripts/refresh_samples.sh` no longer forces `AILIBI_LLM_PROVIDER=anthropic`; it honors `ollama` and `anthropic`, and the `--dry-run` echo shows the selected provider + the preflight that ran.
- [ ] The `ANTHROPIC_API_KEY` preflight is replaced by a provider-aware check: `anthropic` still requires the key; `ollama` instead pings `AILIBI_OLLAMA_HOST` for reachability AND confirms the configured model is pulled, failing loud (clear message, non-zero exit) when the server is down or the model is missing.
- [ ] `eval/balance_eval.py`'s per-game `GameBudget(max_cost_usd=1.00)` (line ~221) is parametrized via an env knob (e.g. `AILIBI_MAX_COST_USD`); the token caps follow the named-constant LINEAR form (`max_input_tokens = BASE_INPUT + PER_PLAYER_INPUT * num_players`, `max_output_tokens = BASE_OUTPUT + PER_PLAYER_OUTPUT * num_players`, no magic numbers) so a 7-player meeting fits; the constants are chosen so the 4p/1i preset reproduces today's `GameBudget` caps exactly, and when the knob is unset the 4p/1i defaults are byte-identical to today (the frozen baseline path is unchanged).
- [ ] On Ollama the USD cap is effectively disabled (per 7.5) and the roster-scaled token caps are the operative ceiling for 7-player meetings; on Anthropic the existing dollar + token caps still apply.
- [ ] `tests/scripts/test_refresh_samples.py` covers the provider-aware preflight (ollama reachable/model-present → proceeds; server-down or model-missing → fails loud; anthropic still requires the key) via `--dry-run`/mocked checks, without real spend.
- [ ] `tests/eval/test_balance_eval.py` covers the parametrized budget (env knob overrides the per-game USD cap; roster-scaled token caps; unset → 4p/1i default unchanged).
- [ ] No sample data is generated or committed (that is Task 7.8); the changes validate on the fake provider + dry-run.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `scripts/refresh_samples.sh` (the forced `AILIBI_LLM_PROVIDER=anthropic` around
line 282 and the `ANTHROPIC_API_KEY` preflight around lines 247-253) and
`eval/balance_eval.py` (the `GameBudget(max_cost_usd=1.00)` construction at line 221
and its token caps). For the preflight, branch on the resolved provider: keep the
key check for `anthropic`; for `ollama` do a reachability ping of
`AILIBI_OLLAMA_HOST` (a `curl`/HTTP GET to the server's tags endpoint) and grep the
pulled-model list for `qwen2.5:7b-instruct`, erroring with a clear remediation
message ("start `ollama serve` / `ollama pull qwen2.5:7b-instruct`") on failure. For
the budget, read `AILIBI_MAX_COST_USD` (falling back to the current `1.00` default
so the unset path is byte-identical) and derive the token caps from the roster size
already available in `balance_eval.py` via the named-constant LINEAR form (`BASE_* +
PER_PLAYER_* * num_players`), with the constants picked so 4p/1i reproduces today's
caps exactly, so 7-player meetings are not truncated. Note
that on Ollama the dollar cap is moot (7.5 zeroes the cost dimension), so the token
caps are what actually matter there — size them for 7p/2i. The `--dry-run` path in
the script is the testable surface (no spend), so assert the provider/preflight
branching there. Coordinate with 7.4 (already merged): the roster/task flags are
threaded by 7.4's refresh edits; this task adds the provider-aware preflight + budget
knob on top of that merged version, which is why it depends on 7.4.

**Ready-to-paste prompt:** `agent_prompts/task-7-7-provider-agnostic-refresh.md`

### Task 7.8 — Generate, balance-validate, and commit the Phase 7 meeting-heavy eval set
**Branch:** `phase-7-meeting-heavy-eval-set`
**Depends on:** 7.1 merged, 7.2 merged, 7.3 merged, 7.4 merged, 7.5 merged, 7.6 merged, 7.7 merged
**Section refs:** tasks/phase-7-plan.md W0.4, W0.5, "Wave 0 exit criteria", Q2/Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §9, §11.4
**Complexity:** Integration

This is the Wave 0 enablement-gate OPERATIONAL task — the one that converts the
config + metric substrate (7.1, 7.3), the loader/layout plumbing (7.4), and the
Ollama provider substrate (7.5/7.6/7.7) into a committed, meeting-rich eval
denominator. It is run by the DESIGN THREAD, not a headless dispatched agent,
because it must run LOCALLY against a live Ollama server (it needs `ollama serve`
plus the model pulled — see 7.5) and needs human balance judgment. It writes NO
code — it consumes 7.4's roster-aware loader + per-set refresh/manifest routing,
7.1's CLI roster/task flags, 7.3's `meeting_rate` metric, and 7.5's Ollama provider
(wired into the provider-agnostic refresh by 7.7).

The canonical agent-intelligence provider for Phase 7 is **local Ollama
(`qwen2.5:7b-instruct`), $0** — there is no API key and no real spend, so the
cost dimension is trivially zero. This task generates a 7p/2i + 2-task sample set
via `scripts/refresh_samples.sh` with `AILIBI_LLM_PROVIDER=ollama` into
`replays/samples/7p2i/` (with its `roster.json` descriptor + `MANIFEST.md`),
commits it **alongside** the existing 4p/1i baseline (which stays untouched + frozen
for determinism/leak regression and as the A/B reference — replays are
model-agnostic, so the Anthropic-recorded 4p/1i set still replays byte-identically),
and confirms the Wave 0 exit gate: 7.3's `meeting_rate >= 0.60` with **>= 30
resolved meetings**, AND a near-even decisive crew/impostor split (not
all-`CREWMATE_TASKS`, not all-parity). If the split is degenerate, sweep
tasks-per-crewmate (2 vs 3) and/or roster and re-record (Q3: balance validation is
required) — but the sweep is BOUNDED, not open-ended: because the run is free, the
bound is **time, not dollars** — **STOP after 3 full 50-game re-record attempts OR
24 hours cumulative wall-clock, whichever comes first**, rather than a spend cap. If
both bars are still unmet at the bound, do
NOT commit a sub-gate set as a compromise — STOP, leave the committed sets
unchanged, and return to the design thread for a re-plan (the gate may need a
different roster axis, an engine-balance change, or a revised target). A
committed-but-sub-gate set would silently poison every later agent-intelligence A/B.

Operational note: the model runs locally, so a full ~5k-call 50-game run is **slow
on the owner's Mac** (tens of minutes to hours), not the wall-clock of a hosted API.
Run the gate small first (a few seeds) to confirm meetings resolve and the model
emits schema-valid reports, then kick the full 50-game run **overnight**. Quality
spot-check that `qwen2.5:7b-instruct` actually resolves meetings (no schema crashes,
coherent accusations) on the small run before committing the full set.

The committed per-set `roster.json` (`num_players`/`num_impostors`/`tasks_per_crewmate`)
this task lands is also the intended metadata source for the deferred frontend
browse track (locked decision 1 / the plan's Frontend track), so that later track
reads this descriptor rather than persisting a new roster field. The frontend
browse selector itself is out of scope here; do not touch `frontend/`.

**Files in scope:**
- replays/samples/7p2i/ (the new committed set: replay JSONLs + `roster.json` + `MANIFEST.md` + its own `tournament-eval-report.json`)
- tests/api/test_replay_loader.py (add the CI gate: a pytest test that loads + reconstructs the COMMITTED `replays/samples/7p2i/` set — shared with 7.4, which this task depends on)

**Files NOT in scope:**
- api/replay_loader.py, scripts/refresh_samples.sh, scripts/_manifest_writer.py (the plumbing is Task 7.4; consume it, do not edit)
- scripts/run_tournament.py, orchestrator/seeder.py (the roster/task flags + seeder are 7.1's; consume them)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's; read its output, do not edit)
- replays/samples/ flat 4p/1i set (committed ALONGSIDE; never deleted or overwritten)
- replays/samples/tournament-eval-report.json (the 4p/1i report is regenerated by Task 7.3; this task generates only the 7p/2i set's own report under `replays/samples/7p2i/`)
- frontend/ (browse selector is a later track)
- DESIGN.md (design-thread-owned)

**Definition of done:**
- [ ] A meeting-heavy 7p/2i + 2-task sample set is generated via `scripts/refresh_samples.sh` against the **local Ollama** provider (`AILIBI_LLM_PROVIDER=ollama`, `qwen2.5:7b-instruct`, using 7.4's roster-aware routing + 7.7's provider-agnostic refresh + 7.1's flags) into `replays/samples/7p2i/` with its `roster.json` + `MANIFEST.md`, and committed **alongside** the existing 4p/1i baseline; the 4p/1i set is not deleted or overwritten (it is the frozen, model-agnostic determinism/leak/A-B reference).
- [ ] **Wave 0 exit gate met on the committed canonical set:** 7.3's `meeting_rate` is `>= 0.60` with `>= 30` resolved meetings, AND the decisive crew/impostor split is near-even (not all-`CREWMATE_TASKS`, not all-parity). The chosen canonical config and the gate numbers are recorded in the PR `## Decisions` block.
- [ ] **Bounded sweep + stopping rule (time-boxed, not spend-capped):** because the Ollama run is **$0**, the balance sweep is bounded by **time, not dollars** — **STOP after 3 full 50-game re-record attempts OR 24 hours cumulative wall-clock, whichever comes first** (not a spend cap). If both bars are still unmet at the bound, NO set is committed as a sub-gate compromise — the committed sets are left unchanged and the gate is escalated to the design thread for a re-plan. The PR `## Decisions` records the attempts made and the wall-clock spent.
- [ ] **Local-model quality + meeting-resolution spot-check:** before the full commit, a small run (a few seeds) confirms `qwen2.5:7b-instruct` resolves meetings without schema crashes (7.6's parse-tolerance must hold on real local output). This is NOT only a schema-validity check — it must also be a **BEHAVIORAL read**: sample a few real Ollama meetings and confirm transcripts read as plausible social deduction and votes are sensible / justified, not just well-formed. The diagnosis's fake-provider expectation is ~63% meeting rate, so if the Ollama `meeting_rate` diverges from that by more than **10pp** (either direction), investigate the cause before committing (it signals a model-behavior or config discrepancy, not just noise). Cross-phase note: the resulting `alibi_survival` / `vote_correctness` are an **Ollama baseline**, NOT comparable to Phase 6's Sonnet numbers (only byte-identical replay reconstruction is model-agnostic).
- [ ] The determinism / byte-identical replay suite AND the leak suite — including the W0.2 `self_state.fellow_impostor_ids == ()` crew-recipient invariant from 7.2 — pass on **both** committed sets. The **CI-enforced** gate for the new 7p/2i set is a pytest test in `tests/api/test_replay_loader.py` that loads + reconstructs the COMMITTED `replays/samples/7p2i/` set (run under `check.sh`'s pytest, since `check.sh` runs `uv run pytest` but does NOT invoke `verify_samples.sh`), paired with the existing pytest coverage of the flat 4p/1i set — both committed sets thus CI-gated. `scripts/verify_samples.sh <set-dir>` is the MANUAL operator tool (`scripts/verify_samples.sh` for 4p/1i, `scripts/verify_samples.sh replays/samples/7p2i` for the new set), run before committing.
- [ ] The PR `## Decisions` block records: the canonical Phase 7 eval config (roster + tasks-per-crewmate) and whether a re-balance sweep was needed; the measured `meeting_rate` / resolved-meeting count / decisive split; the provider/model (`ollama` / `qwen2.5:7b-instruct`); and the wall-clock of the run (cost is $0 — the refresh's cost line / MANIFEST sum should read zero on Ollama, which is itself a useful sanity check that the budget $-dimension is disabled per 7.5).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Confirm the full substrate is merged and green FIRST: 7.4's plumbing (the loader
reconstructs a hermetic 2-impostor replay, refresh/manifest route per-set), 7.5's
Ollama client, 7.6's parse-tolerance, and 7.7's provider-agnostic refresh + budget.
Start `ollama serve` and `ollama pull qwen2.5:7b-instruct`. Then run a SMALL
gate first (a few seeds) with `AILIBI_LLM_PROVIDER=ollama` and 7.1's roster/task
flags targeting `replays/samples/7p2i/` (via the `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST`
hooks 7.4 wired + 7.7's provider-aware preflight), confirm meetings resolve and
reports validate (no schema crashes), then kick the full 50-game run **overnight**
(it is slow locally). Read 7.3's `meeting_rate` off the resulting
`replays/samples/7p2i/tournament-eval-report.json`, and check the exit gate +
balance. A balance re-sweep (2↔3 tasks / roster) means multiple full local runs,
each free but slow, so honor the **time-box / ~3-attempt** bound and the
stop-and-escalate rule (there is no dollar cap — the Ollama run is $0). After
committing, add the pytest test that loads + reconstructs the committed
`replays/samples/7p2i/` set so its determinism is CI-gated, and run
`scripts/verify_samples.sh replays/samples/7p2i` manually. Do NOT edit the 7.4–7.7
substrate or any engine/agent code; this is a data-generation + gate-confirmation
task.

**Integration risk:**

This task runs the model locally (no spend), commits the first multi-impostor
fixture set, and decides whether the Phase 7 roster re-balances — all design-thread
judgment.

- **Local run is free but slow and time-bounded.** The full 7.4–7.7 substrate must
  be merged and fake-validated first, and `ollama serve` + the model must be
  reachable; the **time-box / ~3-attempt** bound + stop-and-escalate rule prevents
  an open-ended re-balance loop. There is NO dollar cap — the Ollama run is $0; the
  bound is wall-clock, and a ~5k-call run is slow locally (run the gate small, the
  full set overnight).
- **The 4p/1i baseline must survive untouched.** Commit the 7p/2i set ALONGSIDE; a
  mis-routed refresh that overwrote `replays/samples/` would destroy the
  determinism/leak regression + A/B reference. The 4p/1i set was recorded on
  Anthropic but replays are model-agnostic, so it reconstructs byte-identically
  regardless of the new provider — verify the flat set still reconstructs after the
  commit.
- **Firewall on the first committed multi-impostor data.** The 7.2
  `fellow_impostor_ids == ()` crew invariant must hold across the new set's
  packets, not just the single-impostor 4p/1i set; run the leak suite over both.
- **Gate honesty + local-model schema risk.** `meeting_rate` and the decisive split
  are measured on the local model, not assumed from the fake-provider 63%; the
  divergence check + bounded sweep keep an unbalanced or low-meeting set from being
  committed as a false "gate cleared". The added local risk is that
  `qwen2.5:7b-instruct` may emit reports that violate the strict
  discriminated-union schemas — 7.6's parse-tolerance is the mitigation, and the
  small spot-check run is where a residual schema-crash surfaces before the full
  commit.

**Ready-to-paste prompt:** `agent_prompts/task-7-8-meeting-heavy-eval-set.md`

### Task 7.9 — Teammate-aware impostor kill + engine friendly-fire guard
**Branch:** `phase-7-impostor-kill-friendly-fire`
**Depends on:** none (Wave 0.5 repair; the Wave-0 substrate 7.1–7.8 is merged)
**Section refs:** audits/audit-2026-06-01-1425-gameplay-data.md (gp-1, gp-3, MECH-B-1, MECH-B-2, D-D-1, F-F-1); DESIGN.md §3.4 (kill resolution); locked decision 6 (FSM tactical determinism)
**Complexity:** Medium

The 2026-06-01 gameplay-data audit found the committed 7p/2i eval set is balance-invalid: in 39 of 50 games an impostor kills its own teammate (35% of all 111 resolved kills), which fully explains the 38-9 / 76%-crew split — in the 39 self-destruct games impostors won 0, in the 11 clean games they won 9. The cause is two-layered and this task closes both. At the agent layer, `agents/tactical/impostor_policy.py::_scored_targets` (audit cites lines 264-329) ranks every sighted player with no teammate filter, even though `self_state.fellow_impostor_ids` is already on the observation packet (`observation/service.py:101`, landed by 7.2). At the engine layer, `engine.rules.resolve_kill` only checks the actor is an IMPOSTOR and never checks the target is a CREWMATE, so a friendly-fire kill is legal and resolves. This is the gating blocker for re-recording a trustworthy eval set.

The task also folds in the audit's gp-3 (co-location gate): 16 kills were queued against an out-of-room target and engine-rejected ("kill requires same room"), wasting the impostor's turn — the policy must not emit a kill intent unless the target is in the actor's current room. And it adds a light coordination heuristic for the tick-1 mutual-spawn case (10 games open with both impostors targeting each other in CAFETERIA on tick 1): two co-located impostors must not both emit a kill on the same tick.

Because the engine guard re-resolves recorded kill actions on playback, the existing committed `replays/samples/7p2i/` set (39 recorded teammate-kills) can no longer reconstruct byte-identically — those kills are now rejected, the per-tick `state_hash` diverges, and `load_replay` raises. This task therefore SKIPS exactly one test — `test_committed_7p2i_set_reconstructs_byte_identically` in `tests/api/test_replay_loader.py` — with an explicit reason; the post-7.9 re-record re-records a clean set and re-enables it (restoring its committed ≥ 30 resolved-meeting floor). The 4p/1i baseline is unaffected (one impostor, no friendly fire). The DESIGN.md §3.4 friendly-fire reconciliation is design-thread-owned and handled separately (the design thread tightens §3.4's kill rule to require a CREWMATE target; tracked in the Wave 0.5 Merge Criteria).

**Files in scope:**
- agents/tactical/impostor_policy.py (exclude `self_state.fellow_impostor_ids` from `_scored_targets`; gate kill intent on target co-location; tick-1 mutual-kill coordination heuristic — all deterministic)
- engine/rules.py (`resolve_kill` rejects a kill whose target is an IMPOSTOR — defense-in-depth; existing actor-is-impostor / same-room / cooldown checks unchanged)
- tests/agents/ + tests/engine/test_rules.py (teammate never selected; out-of-room kill never emitted; engine rejects an IMPOSTOR-target kill; an invariant test that no resolved kill has `victim_role == IMPOSTOR` across seeded games)
- tests/api/test_replay_loader.py (skip ONLY `test_committed_7p2i_set_reconstructs_byte_identically` with a reason referencing this guard + the pending re-record; leave `test_committed_7p2i_set_holds_crew_firewall` and the hermetic tmp_path multi-impostor tests untouched — they do not reconstruct the committed bytes)

**Files NOT in scope:**
- observation/service.py (`fellow_impostor_ids` is plumbed by 7.2 — consume it, do not edit)
- DESIGN.md (design-thread-owned; the §3 friendly-fire note is the design thread's)
- meetings/, eval/, llm/ (untouched)
- replays/samples/ (the re-record is a separate operational step after this merges; do not regenerate data here, and never delete the 4p/1i set)

**Definition of done:**
- [ ] `_scored_targets` excludes every id in `self_state.fellow_impostor_ids` before ranking; an impostor never selects a fellow impostor as a kill target.
- [ ] The policy emits a kill action only when the target is in the actor's current room (no "kill requires same room" rejections originate from the policy's own intents).
- [ ] Two co-located impostors do not both emit a kill on the same tick; the tick-1 mutual-spawn self-destruct cannot occur. Determinism is preserved (no RNG that would break replay reconstruction).
- [ ] `engine.rules.resolve_kill` rejects a kill whose target is an IMPOSTOR with a clear `ActionRejected` reason; the actor-is-impostor, same-room, and cooldown checks are unchanged; the legitimate impostor-kills-crewmate path still resolves.
- [ ] An invariant test asserts no resolved kill has `victim_role == IMPOSTOR` across a representative seeded set. Repro anchors: seed 4 tick 1 (mutual, CAFETERIA), seed 0 tick 7 (mid-game, MEDBAY), seed 32 tick 1.
- [ ] Exactly one test is skipped — `test_committed_7p2i_set_reconstructs_byte_identically` — with an explicit reason (the guard rejects the old set's recorded teammate-kills → `state_hash` drift; re-enabled by the post-7.9 re-record). Its sibling `test_committed_7p2i_set_holds_crew_firewall` is seed-derived and role-pure (it never reconstructs recorded ticks) and stays green; the hermetic tmp_path multi-impostor recon/firewall tests regenerate under the new rules and stay green; the 4p/1i reconstruction + leak suites stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `_scored_targets` and the packet's `self_state.fellow_impostor_ids`; filter teammates from the candidate set, then drop targets not co-located. For the engine guard, mirror the existing same-room/cooldown reject in `resolve_kill` with a target-role check. For the tick-1 coordination heuristic, keep it deterministic with no shared state: when a fellow impostor is co-located and would also emit a kill on the same tick, the lower-id impostor emits and the higher-id defers (`min(actor_id, fellow_id)` acts) — a pure function of ids, replay-safe, no RNG. Keep the FSM tactical layer deterministic (DESIGN.md §4 / locked decision 6) — this is target selection plus a reject, not new LLM behavior. The audit's MECH-B-3 "player is dead" same-tick rejection count shrinks automatically once teammate-kills stop (it was a downstream symptom). Confirm the 4p/1i frozen set still reconstructs after the change (the teammate filter and guard are no-ops at one impostor).

**Integration risk:**

The gating blocker for the re-record. The engine guard is defense-in-depth, not a behavior change for a correct policy, but it must not regress the only valid kill (impostor→crewmate). The coordination heuristic must stay deterministic. The stale-7p2i reconstruction-test skip is intentional and time-bound — the re-record un-skips it; do not leave it skipped indefinitely.

**Ready-to-paste prompt:** `agent_prompts/task-7-9-impostor-kill-friendly-fire.md`

### Task 7.10 — Fail-soft on malformed meeting statements + single accusation round
**Branch:** `phase-7-meeting-failsoft-single-round`
**Depends on:** 7.6 merged
**Section refs:** audits/audit-2026-06-01-1425-gameplay-data.md (gp-2, E-E-1, A-A-2, and the R=2 statement-sink in §6); DESIGN.md §5.2 (meeting protocol)
**Complexity:** Medium

The audit found two independent meeting issues. First (gp-2, blocking): `qwen2.5:7b-instruct` sometimes emits an `AlibiClaim` with `from_tick > to_tick`; the Statement validator rejects it, the meeting aborts, and the game terminates with NO `game_over` record — corrupting 3 of 50 games (seeds 25/36/40) and wasting ~127K input tokens. Second (the owner's speed call): the sequential statement phase runs R=2 rounds — the dominant meeting token sink, roughly a third of meeting LLM calls — the operator's hypothesis is that round 2 is not currently earning its cost, but the audit raised this (E-lens) as an OPEN QUESTION and did not measure a round-2 vote delta — a speed call, not a measured finding; reduce R to 1 for Wave 0.5, readjustable if a Wave-1 measurement later shows round 2 changes outcomes. Both ride the same eval re-record; neither affects replay reconstruction (meetings reconstruct by applying the recorded outcome, so the committed sets are unaffected).

For gp-2 there are two complementary fixes. Parse-tolerance: when an `AlibiClaim` arrives with `from_tick > to_tick`, normalize it (swap the bounds or coerce to a one-tick window at `to_tick`) and retry once — the natural home is 7.6's discriminator-aware normalizer (`llm/report_normalize.py`), extended to the chronological case. Fail-soft: a single rejected `Statement` must degrade to a missed-deadline placeholder (the same default-on-failure mechanism the report/statement collection already uses for timeouts, landed on main as `5407cc7`) so the meeting and game continue to `game_over` — a malformed statement never aborts the run.

R 2→1 is `DEFAULT_ROUND_COUNT` in `meetings/manager.py`; reduce it and update the tests that pin 2 rounds and any round-indexed transcript handling. It is readjustable later if Wave-1 deliberation needs a second round.

**Files in scope:**
- llm/report_normalize.py (extend 7.6's normalizer with the non-chronological-alibi case: swap/coerce `from_tick`/`to_tick`)
- meetings/manager.py (statement collection degrades a rejected `Statement` to a missed-deadline placeholder instead of aborting; `DEFAULT_ROUND_COUNT` 2→1)
- tests/llm/ + tests/meetings/ (a non-chronological alibi normalizes and the meeting reaches `game_over`; a hard-malformed statement fails soft; round count is 1)

**Files NOT in scope:**
- meetings/schemas.py (the `AlibiClaim` chronological validator stays strict — the normalizer fixes the input before validation; the schema is not relaxed)
- engine/, agents/, eval/ (untouched)
- replays/samples/ (no data regeneration here; meetings reconstruct from recorded outcomes, so the committed sets are unaffected by R 2→1)

**Definition of done:**
- [ ] A non-chronological `AlibiClaim` (`from_tick > to_tick`) is normalized (bounds swapped or coerced to a one-tick window) before validation and validates on retry; the strict schema is not relaxed, and a claim still malformed after normalization fails only that single statement, not the run.
- [ ] A single rejected `Statement` degrades to a missed-deadline placeholder and the meeting continues; every game reaches a `game_over` record (no run terminates on a malformed statement). Repro: seed 36 meeting-0 @tick 11 (the recorded `failed_call` with no following `game_over`); also seeds 25 and 40.
- [ ] `DEFAULT_ROUND_COUNT` is 1; the statement phase runs one accusation round; tests pinning 2 rounds and round-indexed handling are updated.
- [ ] The committed 4p/1i and 7p/2i sets still reconstruct byte-identically (meetings apply the recorded outcome; round count does not affect replay) — confirm.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The normalizer (7.6, `llm/report_normalize.py`) already runs in the shared extract→validate path; add a chronological-alibi normalization there so it protects every provider plus the replay path. For fail-soft, reuse the missed-deadline default the sequential report/statement collection already returns on timeout (the `5407cc7` pattern) — catch the `ValidationError` on a single statement and substitute the placeholder rather than propagating. R 2→1 is a one-line constant plus test updates; grep for `round_count` / `DEFAULT_ROUND_COUNT` and round-index assumptions. Reconstruction is unaffected (the loader applies recorded meeting outcomes), so do not touch committed data.

**Integration risk:**

Fail-soft must not mask a genuine systemic parse failure — it degrades ONE statement, not the meeting; if every statement fails the meeting still resolves on whatever reports/votes landed. R 2→1 changes future recordings only (not replay), but it is a deliberate speed trade resting on the operator's hypothesis that round 2 is not currently earning its cost (NOT a measured vote-delta — the audit flagged it as an open question); record it as readjustable in the PR. `meetings/manager.py` is shared only with the merged sequential-collection change on main, not with another open task.

**Ready-to-paste prompt:** `agent_prompts/task-7-10-meeting-failsoft-single-round.md`

### Task 7.11 — Eval reporting hardening (no gameplay-behavior change)
**Branch:** `phase-7-eval-reporting-hardening`
**Depends on:** 7.3 merged
**Section refs:** audits/audit-2026-06-01-1425-gameplay-data.md (gp-7, C-C-4, F-F-2, F-F-3, F-F-5, A-A-3); DESIGN.md §11.3 (eval metrics)
**Complexity:** Medium

The audit found the eval report's headline numbers mislead a Wave-1 reader even when computed correctly. This task hardens the reporting and interpretation surface only — no gameplay or engine behavior changes. The fixes: add a derived `ejection_accuracy` (impostor_ejections / total_ejections) next to `vote_correctness_rate`, because the latter is `evidence_backed_impostor_ejections / impostor_ejections` (1.0 in the artifact set) and silently excludes the wrong crewmate ejections — actual accuracy was 50%; report `vote_correctness` with an explicit small-n flag and a secondary "contradictions flagged but ignored" signal (36/45 SKIPPED meetings had at least one contradiction yet no ejection); report accusation-calibration per-bin counts alongside ECE and flag it low-power when the bins are sparse (qwen2.5 clusters confidences); pair `meeting_rate` with the SKIPPED/EJECTED breakdown and stop presenting `emergency_meetings` as a positive emergency count — it is a documented catch-all (body-report meetings whose triggering report lacked a `FoundBodyObservation`); document `cost_dashboard` as informational-only under Ollama ($0 — token counts are the cost proxy); and keep `first_zero_impostor_tick == game_over_tick` as an automated self-check so a §6.3 win-condition regression is caught.

These make the post-re-record metrics trustworthy and readable. The metric math that is already correct (meeting_rate 0.74, the calibration computation) is not changed — only the surfacing, the new derived field, and the caveats.

**Files in scope:**
- eval/vote_correctness.py (add `ejection_accuracy`; small-n flag; the contradictions-ignored secondary signal)
- eval/accusation_calibration.py (per-bin counts and a low-power flag alongside ECE)
- eval/meeting_quality.py (pair `meeting_rate` with the SKIPPED/EJECTED split; document `emergency_meetings` as a catch-all, not a positive emergency count)
- eval/cost_dashboard.py (document informational-only under a $0 provider)
- eval/report_schema.py + api/routes/eval.py + frontend/src/types/api.ts (mirror any new report field 1:1)
- replays/samples/tournament-eval-report.json (the FROZEN 4p/1i DERIVED report — regenerate offline so it carries the new fields; the `.jsonl` replays stay frozen and are never edited or deleted)
- tests/ — including `tests/api/test_leak.py` (extend `EXPECTED_EVAL_REPORT_FIELDS` with the new field names) — the new field plus caveats; the `first_zero_impostor_tick == game_over_tick` self-check; and a test that the committed 4p/1i report loads/validates against the current model

**Files NOT in scope:**
- engine/, agents/, meetings/, llm/ (no behavior change — reporting only)
- replays/samples/*.jsonl (the recorded replays stay FROZEN — never edited or deleted; only the DERIVED 4p/1i `tournament-eval-report.json` is regenerated offline from them, and the 7p/2i report is regenerated by the post-merge re-record)
- eval/balance_eval.py (the win-bucket reducer is unchanged)

**Definition of done:**
- [ ] `ejection_accuracy` (= impostor_ejections / total_ejections) is reported next to `vote_correctness_rate`, and `vote_correctness` carries an explicit small-n flag plus a "contradictions flagged but ignored" secondary count.
- [ ] accusation-calibration reports per-bin counts alongside ECE and flags low statistical power when bins are sparse.
- [ ] `meeting_rate` is paired with the SKIPPED/EJECTED breakdown, and `emergency_meetings` is documented (schema field doc + route mirror) as a catch-all, not read as a positive emergency count.
- [ ] `cost_dashboard` is documented informational-only under a $0 provider (token counts are the cost proxy).
- [ ] An automated self-check asserts `first_zero_impostor_tick == game_over_tick` (no §6.3 regression).
- [ ] Any new report field is mirrored 1:1 across `eval/report_schema.py` (or `eval/meeting_quality.py`, wherever the leaf model lives), `api/routes/eval.py`, and `frontend/src/types/api.ts`, and `EXPECTED_EVAL_REPORT_FIELDS` in `tests/api/test_leak.py` is extended with the new field names — the field-set snapshot is a deliberate tripwire, so it MUST be updated explicitly (as 7.3 did), and `test_eval_report_surface_exposes_no_engine_state_field` still passes.
- [ ] New fields are added to the report model and the FROZEN committed 4p/1i `replays/samples/tournament-eval-report.json` is regenerated offline from its committed replays (the 7.3 pattern — replays stay frozen, only the derived report moves) so it still loads/serves via `GET /eval/tournament-report`; the model is `frozen=True, extra="forbid"`, so a stale report missing a now-required field would 500 at the route while check.sh (whose route tests use tmp_path) stays green — the regression 7.3 documented. The rebuild reproduces every pre-existing field byte-for-byte (only the new fields added), and a test loads the committed 4p/1i report and asserts it validates against the current model. The 7p/2i report is regenerated by the post-merge re-record.
- [ ] The `vote_correctness_rate` docstring cross-references `ejection_accuracy`: the rate is computed over evidence-backed impostor ejections only, so it must be paired with `ejection_accuracy` for the full ejection denominator (a `1.0` rate read in isolation cannot be mistaken for full accuracy).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

These are derived fields, doc strings, and a self-check — not new computation pipelines. Read `eval/vote_correctness.py` (the rate definition), `eval/accusation_calibration.py` (the binning), and `eval/meeting_quality.py` (the trigger split), and mirror any new field through `eval/report_schema.py` → `api/routes/eval.py` → `frontend/src/types/api.ts` exactly as 7.3 did for `meeting_rate` (the 1:1 type mirror plus the `tests/api/test_leak.py` field-set snapshot). Do not touch any gameplay code; this is the reporting layer only.

**Integration risk:**

Adding report fields touches the api/frontend type-mirror AND the frozen committed 4p/1i report — keep the type-mirror in lockstep (or the field-set snapshot test fails), AND make the new fields land in a regenerated 4p/1i report (or the `frozen`, `extra="forbid"` model 500s at the route while check.sh stays green — the exact regression 7.3 documented). No gameplay behavior changes, so no re-record is required for this task alone — but it should land before the re-record so the re-recorded 7p/2i report carries the hardened fields.

**Ready-to-paste prompt:** `agent_prompts/task-7-11-eval-reporting-hardening.md`

### Task 7.12 — Teammate-aware impostor meeting behavior (J-5)
**Branch:** `phase-7-impostor-meeting-coordination`
**Depends on:** 7.1, 7.2, 7.9, 7.10 (all merged — Wave 0 substrate + Wave 0.5 repair; the 2026-06-02 re-record + re-audit cleared the Wave-1 gate)
**Section refs:** audits/audit-2026-06-02-2112-gameplay-data.md (gp-imp-1, D-D-1, D-D-2, D-D-3, D-D-4, C-C-6); DESIGN.md §5.2–§5.3 (meeting protocol / reports), §6.6 (prompt rendering + leak firewall); the J-5 deferral marker at `agents/perception.py:196`
**Complexity:** Medium

The 2026-06-02 gameplay-data audit on the Wave-0.5 baseline found impostors actively help the crew in meetings. `fellow_impostor_ids` is delivered on the self channel (landed by 7.2) and consumed by the kill policy (7.9, why friendly-fire is now 0) but NOT by the meeting/vote path — `agents/perception.py:196` explicitly defers this to "Wave 2 (J-5)". From the recorded data: impostors voted to eject a fellow impostor in 40/91 ballots (44%), both impostors mutually betrayed each other in 11 meetings, and impostors fabricated eyewitness accusations against a teammate in 48/54 report accusations (0/19 corroborations supported a teammate). All 5 "correct" impostor ejections were aided by a teammate's betrayal vote, and in seed 6 that vote was outcome-pivotal — so the current 68% impostor win rate UNDER-states true impostor strength. This task closes the meeting-side teammate gap so the crew-intelligence A/B that follows is measured against a non-self-sabotaging opponent.

Meeting output is LLM-driven (unlike the FSM kill policy), so the fix is two layers: a prompt layer that tells an impostor who its teammates are and to protect them, and a deterministic guard that hard-excludes a teammate from the produced accusation/ballot regardless of what the model emits — the same belt-and-suspenders the kill policy plus engine guard use. The teammate list is firewall-safe self-channel data: it must enter an impostor's own prompt but NEVER a crewmate's, preserving the 7.2 leak invariant (`self_state.fellow_impostor_ids == ()` for crew). The 4p/1i frozen set is single-impostor, so every change is a no-op there.

This is a recorded-behavior change, so the committed 7p/2i set is re-recorded + re-audited after this merges (a separate operational step in the Wave-1 sequencing section); do not regenerate data here. It does not affect replay reconstruction of existing sets (meetings replay by applying the recorded outcome), so both committed sets stay byte-identical.

**Files in scope:**
- meetings/manager.py (`MeetingParticipant` gains `fellow_impostor_ids: tuple[PlayerId, ...] = ()`, threaded into the report/statement/vote prompt context the reasoner receives)
- orchestrator/game.py (populate `MeetingParticipant.fellow_impostor_ids` at construction — `orchestrator/game.py:434` — from world-state roles when the participant is an impostor; `()` for crewmates and a sole impostor; never the participant's own id)
- agents/strategic/reasoner.py (pass the teammate list into the impostor prompt context; after the LLM returns, hard-exclude teammates — a `VoteBallot` targeting a teammate coerces to `SKIP`, an `AccusationClaim` / `Statement.target` naming a teammate is dropped; allow an impostor's own `fellow_impostor_ids` through the prompt leak scanner the way the `## Your role:` line is already allowlisted)
- agents/strategic/prompts/impostor_report.j2 + accusation_round.j2 + vote_ballot.j2 (surface the teammate list with an instruction never to accuse, incriminate, or vote a teammate, and optionally to corroborate one; render the teammate block only when the list is non-empty, so crewmate prompts stay byte-unchanged)
- tests/agents/ (deterministic-guard unit tests over the reasoner: teammate-ballot coerces to SKIP, teammate-accusation dropped, crew + solo-impostor no-op; an impostor's own teammate ids do not trip the prompt leak scanner while a crewmate prompt carries no teammate block)
- tests/meetings/ + tests/orchestrator/ (`MeetingParticipant` carries the field; the orchestrator populates the other impostors' ids for an impostor and `()` for every crewmate / sole impostor)

**Files NOT in scope:**
- observation/service.py + observation/packet.py + agents/perception.py (`fellow_impostor_ids` is plumbed by 7.2 — consume it, do not edit the substrate)
- agents/tactical/impostor_policy.py + engine/ (the FSM kill layer is already teammate-aware via 7.9; no engine change)
- meetings/schemas.py (the `VoteBallot` / `Statement` / `AccusationClaim` schemas are unchanged — the guard coerces produced values, it never relaxes validation)
- eval/, replays/samples/ (no metric change here; the re-record is a separate step and never deletes the 4p/1i set)

**Definition of done:**
- [ ] `MeetingParticipant` carries `fellow_impostor_ids` (default `()`), populated by the orchestrator from world-state roles: the other impostors' ids for an impostor participant, `()` for every crewmate and for a sole impostor, never the participant's own id.
- [ ] An impostor's meeting prompts surface the teammate list with an instruction never to accuse, incriminate, or vote a teammate (and optionally to corroborate one); the shared accusation/vote prompts render NO teammate block for a crewmate (empty list), so crewmate prompts are byte-unchanged.
- [ ] A deterministic guard in the reasoner hard-excludes teammates from the produced output regardless of the model: a `VoteBallot` whose target is a `fellow_impostor_id` becomes `SKIP`; an `AccusationClaim` or `Statement.target` naming a teammate is dropped. The guard is a no-op for crewmates and a sole impostor, and is deterministic (no RNG, no new LLM call) so replay is unaffected.
- [ ] The prompt leak scanner allows an impostor's own `fellow_impostor_ids` (legitimate self-channel data, like the `## Your role:` line) while every crewmate meeting prompt still carries no teammate-id block; the 7.2 leak invariant (`self_state.fellow_impostor_ids == ()` for crew) and the existing leak suites stay green.
- [ ] Behavioral regression anchors (firewall-known, no role inference): an impostor never produces a ballot or accusation targeting a teammate across a seeded multi-impostor set. Repro fixture: seed 6 meeting-0 (the pivotal teammate-betrayal vote that, removed, turns a 2-vote eject into a 1-1-1-1 SKIP).
- [ ] The frozen 4p/1i set still reconstructs byte-identically (single impostor → every change is a no-op); both committed sets' leak suites stay green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The teammate list already exists on the observation packet (`SelfView.fellow_impostor_ids`, 7.2) and the orchestrator holds the world-state roles where it builds `MeetingParticipant` (`orchestrator/game.py:434`); add the field there rather than re-deriving roles in the meeting layer. The reasoner (`agents/strategic/reasoner.py`) already branches the report prompt on role (crewmate vs impostor) — thread `fellow_impostor_ids` into that same context and into the shared accusation/vote renderers, gating the teammate block on a non-empty list so crewmate prompts are byte-unchanged. For the guard, post-process the parsed `VoteBallot` / `Statement` / `ReportDocument` before returning: coerce a teammate-targeted ballot to `SKIP` and drop teammate accusations — pure functions of `fellow_impostor_ids`, deterministic, replay-safe, mirroring the kill policy's teammate filter. For the leak scanner, the reasoner already allowlists the legitimate `## Your role: X` line before running `eval.leak_test._assert_no_role_bearing_values`; extend that allowlist so an impostor's own teammate ids in their own prompt are not flagged, WITHOUT loosening the scan for crewmate prompts (whose list is empty). Keep everything deterministic so replay reconstruction of the committed sets is unaffected.

**Integration risk:**

This is the first consumer of `fellow_impostor_ids` in the meeting path and it crosses the orchestrator → meeting → reasoner → prompt boundary plus the leak firewall, so the leak invariant is the load-bearing constraint: the teammate list must reach an impostor's prompt and NEVER a crewmate's. Keep the guard belt-and-suspenders (prompt instruction AND deterministic coercion) so the regression anchors hold even when the 7B model ignores the instruction. The change alters recorded meeting behavior, so it gates a re-record + re-audit (Wave-1 sequencing) — but it does not affect replay reconstruction of existing sets (meetings replay by applying the recorded outcome), so the committed 4p/1i and 7p/2i sets are untouched by this task. No schema relaxation: the guard coerces produced values, it never widens `VoteBallot` / `AccusationClaim`.

**Dependency check:**
- `uv run python -c "from observation.packet import SelfView; assert 'fellow_impostor_ids' in SelfView.model_fields"`
- `uv run python -c "from meetings.manager import MeetingParticipant"`

**Ready-to-paste prompt:** `agent_prompts/task-7-12-impostor-meeting-coordination.md`

## Merge Criteria (Wave 0 — enablement gate)
- **Config reachable + deterministic:** Task 7.1 lands the `tasks_per_crewmate` knob (default 2), the `4p1i`/`7p2i` roster presets, and the CLI threading; the `tasks_per_crewmate=1` path stays byte-identical to the committed 4p/1i baseline.
- **Firewall extended for multi-impostor play:** Task 7.2 lands impostor-only `fellow_impostor_ids` on `SelfView`, with the new leak invariant (`self_state.fellow_impostor_ids == ()` for every crew-recipient packet) green; `visible_players` / `PlayerView` unchanged.
- **The gate is measurable:** Task 7.3 lands the `meeting_rate` / `meetings_total` + body/emergency-trigger metric on `TournamentEvalReport`, mirrored across the eval route (`api/routes/eval.py::_TournamentEvalReportView`), the `tests/api/test_leak.py` field-set snapshot, the regression baseline, and `frontend/src/types/api.ts` (`api/schemas.py` is untouched — the metric reports do not live there).
- **Roster-aware loader + two-set layout landed (plumbing, Task 7.4):** the per-set `roster.json` + fail-loud `api.replay_loader.RosterConfig`, the roster-aware `_walk` re-seed, and per-set refresh/manifest routing — dispatchable, fake-validated, no committed data; the flat 4p/1i default re-seed stays byte-identical.
- **Ollama provider + structured output landed (Task 7.5):** `llm.ollama_client.OllamaClient` implements the `LLMClient` Protocol with `format = schema.model_json_schema()` constrained decoding, token mapping, and `cost_usd == 0.0`; `build_default_client` gains the `ollama` branch (`qwen2.5:7b-instruct` default); the USD budget dimension is disabled for Ollama while token caps stay; `ollama` is added to `pyproject.toml`/`uv.lock` with `.env.example`/`README.md`/`AGENTS.md` config; CI never hits the server (opt-in `AILIBI_RUN_OLLAMA_TESTS` gate). The Anthropic path and `llm/fake_provider.py` are unchanged.
- **Parse-tolerance landed (Task 7.6):** a discriminator-aware normalizer (`llm/report_normalize.py`) strips keys not valid for the matched union variant in the SHARED `llm/provider.py` extract→validate path, so near-miss model reports (e.g. `co_present` on `found_body`) validate for every provider + the replay path; `extra="forbid"` is NOT relaxed, already-valid payloads are no-ops, and missing-required fields still fail loud; determinism is preserved.
- **Provider-agnostic refresh + budget landed (Task 7.7):** `scripts/refresh_samples.sh` no longer forces `anthropic`, honors `ollama` with a provider-aware preflight (reachability + model-pulled check), and `eval/balance_eval.py`'s per-game `GameBudget` USD cap is parametrized via an env knob with roster-scaled token caps; the unset/4p1i default path is byte-identical.
- **Stage-A enablement gate met (Task 7.8, on Ollama):** on the committed canonical set (7p/2i + 2 tasks unless Task 7.8's time-boxed balance sweep re-balanced it), generated LOCALLY on Ollama (`qwen2.5:7b-instruct`, $0), `meeting_rate >= 0.60` with **>= 30 resolved meetings** and a non-degenerate decisive crew/impostor split (not all-`CREWMATE_TASKS`, not all-parity). The 7p/2i set is committed alongside the untouched, frozen 4p/1i baseline.
- **Both committed sets reconstruct + are leak-free:** the determinism / byte-identical replay suite and the leak suite (including the 7.2 crew invariant) pass on **both** the 4p/1i and 7p/2i sets via the per-set roster-aware loader.
- **All gates green:** `bash scripts/check.sh`, determinism tests, leak tests, and (for 7.3) frontend `tsc:check` + `vite build`.
- **Wave boundary respected:** Wave 0 ships config/substrate + the meeting-heavy denominator only — NO new contradiction-detector kinds, crewmate wander idle, impostor vent/sabotage, or teammate-defense meeting behavior land here (those are Wave 1 / Wave 2). Wave 1+ contracts are appended to this file only after this gate clears.
- **Intentional non-changes (NOT regressions — flagged so a Wave-1 reviewer doesn't mistake them for gaps):** (a) the spectator **dashboard renders no new metric** after Task 7.3 — 7.3 only adds the `meeting_rate` type to `frontend/src/types/api.ts` (the 1:1 mirror); surfacing it in the UI is deferred. (b) The live spectator app **continues to serve only the flat 4p/1i set**; the committed 7p/2i set is reachable programmatically (`ReplayLoader(replay_dir="replays/samples/7p2i")`) but not via the app until the deferred browse-selector frontend track lands.

## Merge Criteria (Wave 0.5 — eval-set repair, post-audit)
- **Friendly fire is impossible (Task 7.9):** the impostor policy never targets a fellow impostor and never emits an out-of-room kill; `engine.rules.resolve_kill` rejects an IMPOSTOR target; an invariant test confirms no resolved kill has `victim_role == IMPOSTOR`. The stale 7p/2i reconstruction test is skipped (re-enabled by the re-record); the 4p/1i baseline + leak suites stay green.
- **Meetings never abort and run one round (Task 7.10):** a non-chronological alibi is normalized before validation and a malformed statement fails soft, so every game reaches a `game_over` record; `DEFAULT_ROUND_COUNT` is 1. Both committed sets still reconstruct byte-identically (meetings apply recorded outcomes; round count does not affect replay).
- **The eval report is honest (Task 7.11):** `ejection_accuracy` sits beside `vote_correctness_rate`; calibration reports per-bin counts; `meeting_rate` is paired with the SKIPPED/EJECTED split; `emergency_meetings` is documented as a catch-all; `cost_dashboard` is informational-only on Ollama; the `first_zero_impostor_tick == game_over_tick` self-check guards §6.3. No gameplay behavior changed.
- **Re-record validity gate (design thread, after 7.9–7.11 merge) — HARD, numeric:**
  the 7p/2i set is re-recorded on Ollama (R=1) and the gameplay-data audit is re-run;
  the re-record passes ONLY if (a) friendly-fire kills == 0 (no resolved kill has
  `victim_role == IMPOSTOR`), (b) games aborting without a `game_over` record == 0
  (all 50 reach `game_over`), (c) the new set reconstructs byte-identically and the
  leak suite passes via the per-set roster loader, with 7.9's skipped reconstruction
  test re-enabled and green, and (d) the Stage-A floor still holds at R=1
  (`meeting_rate >= 0.60`, >= 30 resolved meetings).
- **Degeneracy tripwire (numeric — catches a NEW artifact, not a balance target):**
  both factions win >= 1 decisive game AND no single win-reason exceeds 70% of
  decisive games — catches a fresh confound (e.g. all-budget-exhaustion or one
  dominating bug). It is NOT a balance-band gate.
- **Balance is measured + reported, NOT gated to a band:** the re-recorded
  crew/impostor split is reported and becomes the anchor for Wave-1 gate targets. An
  impostor-favored-but-valid split (the audit's provisional ~82%-impostor-on-clean
  prediction) is a legitimate pre-Wave-1 baseline, NOT a re-record failure — closing
  the crew-skill gap is precisely Wave 1's job. Do NOT gate the re-record on a
  balanced 30–70% impostor band; that band is a Wave-1 OUTCOME target re-measured on
  this baseline.
- **DESIGN.md §3.4 reconciled (design thread, in this change):** §3.4's kill rule now
  states the target must be a CREWMATE (a fellow impostor is never a valid target),
  matching 7.9's engine guard; the full kill validator is actor IMPOSTOR + target
  CREWMATE + same room + cooldown elapsed. (7.9 implements the guard; DESIGN.md is
  design-thread-owned and edited here, not by 7.9.)
- **Wave boundary respected:** Wave 0.5 repairs the eval substrate, the impostor kill bug, and the reporting surface only — NO crew-intelligence (gp-4), impostor coordination (gp-6), or body-report-rate (gp-5) work lands here (those are Wave 1 / Wave 2 / opportunistic). Wave 1 contracts are appended to this file only after the re-record + re-audit confirm a trustworthy baseline.

## Wave 1 — sequencing + baseline metrics (post 2026-06-02 audit)

The Wave-0.5 re-record (commit `163f786`) and re-audit (`audits/audit-2026-06-02-2112-gameplay-data.md`, verdict MINOR_ISSUES — engine clean, friendly-fire 0/50, win-conditions consistent) cleared the Wave-1 gate. The audit's decisive finding is impostor self-sabotage: `fellow_impostor_ids` reaches the kill policy but not the meeting/vote path, so impostors betray teammates (44% of ballots, 11 mutual-betrayal meetings, 48/54 report accusations against a teammate) and all 5 "correct" impostor ejections were aided by a teammate's betrayal (seed-6 pivotal). The 68% impostor win therefore UNDER-states true impostor strength, and a crew-intel A/B run against this self-defeating opponent would be confounded.

**Sequencing decision (owner, 2026-06-02): impostor-coordination first.** The Wave-2 impostor meeting-coordination work (J-5) is pulled BEFORE Wave-1 crew-intel, on purpose, for baseline validity:

1. Task 7.12 (J-5 impostor meeting coordination) lands.
2. Re-record the 7p/2i set ($0 Ollama, `refresh_samples.sh --full`) + re-run the `gameplay-data-audit` workflow → trustworthy impostor-competitive baseline. Expected: impostor win % rises (true strength), mutual-betrayal 0, the betrayal-aided "correct" ejections drop.
3. Wave-1 crew-intel (gp-4 / audit gp-imp-2) A/B against that baseline — convert flagged contradictions into convictions and fix the threat model (the dominant crew failure is crew-on-crew false accusation, not impostor cascades). The full contract is authored after the re-audit anchors the numbers.

Deferred, opportunistic (non-gating): gp-imp-4 (deterministic SKIP short-circuit — 80% of meeting tokens are spent on meetings that eject nobody; token efficiency only); gp-imp-5 (add seeds exercising the dead deduction-win / silent-game paths — revisit after the re-record, as gp-imp-1 may shift crew toward deduction wins naturally).

### Baseline metrics — reading discipline (audit gp-imp-3; lock before any Wave-1 A/B)

Task 7.11 surfaced the honest fields; this fixes how to READ them so an A/B gates on the right scalar:

- `meeting_rate` is **0.74** (games-with-meeting / total, from `TournamentEvalReport`), NOT the facts-JSON **0.92** (meetings / game) — an 18-point gap from the same data.
- Effective behavioral **n = 37 games / 46 meetings** (13 silent seeds make 0 LLM calls and contribute nothing); size A/B power around 37/46, not 50.
- Do NOT gate on `vote_correctness_rate=0.8` (n=5, `small_n=True`) or `vote_ballot_ece` (`low_power=True`); lead with **`ejection_accuracy`** (0.556, full denominator) and inspect per-bin `impostor_rate` spread.
- `alibi survival_rate=0.45` is a conservative **lower bound** (`alibi_fabrication.py:52-67`); compare only at comparable `total_impostor_alibis`.
- Cost proxy = **tokens, never USD** ($0 structural under Ollama).

Wave-1 crew-intel gates on `contradictions_flagged_but_ignored` (34 ↓) and `ejection_accuracy` (0.556 ↑), re-measured on the post-7.12 re-record — NOT the headline win %.
