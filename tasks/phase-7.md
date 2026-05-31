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
  enablement-gate** contracts (7.1–7.5) are written here today. Wave 1 (crew
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
  fake-validated), and 7.5 (generate + balance-validate + commit the meeting-heavy
  eval set — design-thread-run, real spend).
- **The eval-set work is split: dispatchable plumbing (7.4) + design-thread-run
  generation (7.5).** Task 7.4 (roster-aware loader + two-committed-set layout) is
  a normal reviewed PR validated on the FAKE provider — no spend, no committed
  data. Task 7.5 spends real-provider money (`ANTHROPIC_API_KEY`) and needs human
  balance judgment over the decisive crew/impostor split (Q3-resolved: balance
  validation is required), with a possible re-balance sweep (2↔3 tasks / roster)
  implying multiple real runs; per the dispatch-pattern + eval-cadence memory it is
  operated by the design thread, AFTER 7.4's plumbing is merged green. The
  config-only Wave 0 work (7.1, 7.3) and the firewall substrate (7.2) validate on
  the fake provider.
- **Provider stays Anthropic for Phase 7 (Q2-resolved).** Canonical model = Sonnet
  for meetings, as today. Bound cost by iterating on the fake/deterministic
  provider and reserving real-provider runs for 7.5's balance recording (and the
  later Wave-1 / Wave-2 exit A/Bs), per the eval-cadence rule.
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
  7.5 lands the first committed multi-impostor data.

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
- **7.5 (generate + balance-validate + commit the meeting-heavy set) depends on
  7.1 + 7.2 + 7.3 + 7.4 merged** — it consumes 7.4's roster-aware plumbing + 7.1's
  flags, reads 7.3's `meeting_rate` to check the exit gate, and must hold 7.2's
  crew invariant on the new committed multi-impostor data. It is run LAST, by the
  design thread, against the real provider. Scope is the committed
  `replays/samples/7p2i/` data + the committed-set reconstruction test (shared with
  7.4 under the dependency edge).

Sequence: (7.1 ∥ 7.2) → (7.3 ∥ 7.4) → 7.5.

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
7p/2i sample set (Task 7.5), balance validation of the new config (folded into
Task 7.5), the roster-aware loader / two-set layout plumbing (Task 7.4), impostor
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
- replays/samples/ (sample regeneration/commit is Task 7.5; do NOT regenerate fixtures here)
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
- [ ] `tests/observation/test_service.py` adds a multi-impostor (>=2 impostors) case proving each impostor sees the other impostor id (self excluded), each crewmate sees `()`, and a solo-impostor build yields `()` for the impostor. Because all three committed scripted fixtures are 4p/1i (single impostor), this unit case (together with the extended property sweep below) is what exercises a roster where a misroute could surface a non-empty CREW tuple — so this case MUST additionally run the crew-empty leak assertion (`self_state.fellow_impostor_ids == ()`) over each crewmate-recipient packet built from the 2-impostor `WorldState`, not just check the populate logic. End-to-end coverage over a real played multi-impostor game lands with Task 7.5's committed 7p/2i set.
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
tuple is also `()` there). Task 7.5's committed 7p/2i set then adds end-to-end
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
set's own report is generated fresh by Task 7.5 (post-this-task) and carries the
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
committed sample — that re-record is Task 7.5's job, and those files are NOT in
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
+ `eval/balance_eval.py`, which even Task 7.5 explicitly excludes — Task 7.5 only
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
- replays/samples/ and scripts/refresh_samples.sh (sample regeneration is Task 7.5)
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
real-provider OPERATIONAL half, Task 7.5). It teaches the replay loader to
reconstruct a SECOND committed roster set and lays the directory/manifest plumbing
for it, validated entirely on the FAKE provider — NO real-provider spend and NO
committed sample data here (that is Task 7.5). Splitting the plumbing out lets this
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
route to it) and exercises it on tmp dirs; Task 7.5 commits the actual data into it.
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
the 7p/2i set is Task 7.5, which depends on this task.

**Files in scope:**
- scripts/refresh_samples.sh
- scripts/_manifest_writer.py
- api/replay_loader.py
- tests/scripts/test_refresh_samples.py
- tests/scripts/test_manifest_writer.py
- tests/api/test_replay_loader.py

**Files NOT in scope:**
- replays/samples/ (committing the real 7p/2i data is Task 7.5; this task validates on tmp dirs only and commits no sample data)
- scripts/run_tournament.py (the roster/task flags are owned by 7.1; consume them, do not edit)
- orchestrator/seeder.py (the `tasks_per_crewmate` knob is 7.1's; consume it)
- eval/meeting_quality.py (the `meeting_rate` metric is 7.3's; this task does NOT read it — the gate check is Task 7.5)
- scripts/_verify_samples.py (reuses ReplayLoader for reconstruction; it must keep passing, but its own logic is unchanged)
- scripts/verify_samples.sh (NOT edited — it already accepts an optional `SAMPLE_DIR` arg, used per-set by Task 7.5)
- frontend/ (the browse selector for the two sets is a separate later track)
- api/main.py (replay-dir resolution is unchanged; the loader gains per-set roster awareness, not a new env contract)
- DESIGN.md (design-thread-owned)

**Definition of done:**
- [ ] The two-set directory layout + per-set roster-config mechanism is implemented: the loader reads a per-set `roster.json` parsed into a pinned FROZEN `api.replay_loader.RosterConfig` (`num_players`/`num_impostors`/`tasks_per_crewmate`) via a single named helper that FAILS LOUD on a missing key / wrong type / non-positive value; a flat directory with NO descriptor is the only default path (MVP 4p/1i: `num_impostors=DEFAULT_NUM_IMPOSTORS`, `tasks_per_crewmate=1`); a present-but-malformed descriptor raises.
- [ ] `api/replay_loader.py` re-seeds each replay UNCONDITIONALLY with that set's recorded `num_impostors` AND `tasks_per_crewmate` from the descriptor (when present), instead of the hardcoded `DEFAULT_NUM_IMPOSTORS` and the seeder's `tasks_per_crewmate` default. Both feed `seed_initial_state` and the `WorldState` that `orchestrator/replay.py::_state_hash` serializes (incl. `tasks`), so a wrong value ALWAYS raises `ReplayStateMismatchError` (mandatory, not "sometimes"). The flat-directory 4p/1i default re-seed stays byte-identical to today.
- [ ] `scripts/refresh_samples.sh` + `scripts/_manifest_writer.py` route to the correct per-set directory + manifest (via the existing `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST` env hooks) and thread 7.1's `--num-players`/`--num-impostors`/`--tasks-per-crewmate` flags into the `run_tournament.py` invocation; the `--dry-run` echo block additionally prints the resolved roster, the per-set `SAMPLE_DIR`/`MANIFEST`, and the threaded `run_tournament.py` invocation so per-set routing is observable without spend.
- [ ] `tests/api/test_replay_loader.py` covers multi-impostor reconstruction HERMETICALLY: build a tiny `HeadlessGame(num_impostors=2, ...)` on the FAKE provider, persist it to `tmp_path` with a matching `roster.json`, read it back, and assert (a) it reconstructs byte-identically (no `ReplayStateMismatchError`) when the descriptor names 2 impostors; (b) a descriptor naming the WRONG `num_impostors`/`tasks_per_crewmate` raises `ReplayStateMismatchError` (descriptor is load-bearing); (c) a flat dir with no descriptor still defaults to 4p/1i. No dependency on any committed 7p/2i data.
- [ ] `tests/scripts/test_refresh_samples.py` and `tests/scripts/test_manifest_writer.py` cover the per-set directory/manifest routing on tmp dirs (e.g. a `--dry-run` into a 7p2i set targets that set's directory + manifest), without spending on the real provider.
- [ ] No real-provider spend; NO `replays/samples/` data is committed in this task (that is Task 7.5). The existing flat 4p/1i committed set still reconstructs byte-identically.
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
fake provider before Task 7.5's spend.

- **Loader roster contract is the blast radius.** Re-seeding a replay with the
  wrong `num_impostors`/`tasks_per_crewmate` does not corrupt silently — the
  per-tick `state_hash` check in `_walk` raises `ReplayStateMismatchError` — but it
  fails the whole determinism gate. The descriptor must be read before re-seeding,
  and the flat-directory default must stay EXACTLY 4p/1i or the existing committed
  set regresses.
- **Two sets, two manifests, one refresh script.** `refresh_samples.sh` and
  `_manifest_writer.py` must route to the correct per-set directory/manifest via
  the existing `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST` hooks; a mis-routed refresh
  (in Task 7.5, using this plumbing) would overwrite the 4p/1i baseline, so the
  routing must be proven on tmp dirs here.
- **Firewall on multi-impostor reconstruction.** The hermetic 2-impostor test is
  the first multi-impostor reconstruction; confirm the 7.2 `fellow_impostor_ids`
  invariant holds on the rebuilt packets. The end-to-end check on a real committed
  multi-impostor set is Task 7.5.
- **Dispatchable, fake-validated.** Unlike Task 7.5, this task is a normal
  reviewed PR — no `ANTHROPIC_API_KEY`, no committed sample data; the static gates
  + the hermetic tests are the whole acceptance surface.

**Ready-to-paste prompt:** `agent_prompts/task-7-4-roster-aware-loader-layout.md`

### Task 7.5 — Generate, balance-validate, and commit the Phase 7 meeting-heavy eval set
**Branch:** `phase-7-meeting-heavy-eval-set`
**Depends on:** 7.1 merged, 7.2 merged, 7.3 merged, 7.4 merged
**Section refs:** tasks/phase-7-plan.md W0.4, W0.5, "Wave 0 exit criteria", Q2/Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §9, §11.4
**Complexity:** Integration

This is the Wave 0 enablement-gate OPERATIONAL task — the one that converts the
config + metric substrate (7.1, 7.3) and the loader/layout plumbing (7.4) into a
committed, meeting-rich eval denominator. It is run by the DESIGN THREAD, not a
headless dispatched agent, because it spends real-provider money
(`ANTHROPIC_API_KEY`) and needs human balance judgment. It writes NO code — it
consumes 7.4's roster-aware loader + per-set refresh/manifest routing, 7.1's CLI
roster/task flags, and 7.3's `meeting_rate` metric.

It generates a real-provider 7p/2i + 2-task sample set via `scripts/refresh_samples.sh`
into `replays/samples/7p2i/` (with its `roster.json` descriptor + `MANIFEST.md`),
commits it **alongside** the existing 4p/1i baseline (which stays untouched for
determinism/leak regression and as the A/B reference), and confirms the Wave 0 exit
gate: 7.3's `meeting_rate >= 0.60` with **>= 30 resolved meetings**, AND a near-even
decisive crew/impostor split (not all-`CREWMATE_TASKS`, not all-parity). If the
split is degenerate, sweep tasks-per-crewmate (2 vs 3) and/or roster and re-record
(Q3: balance validation is required) — but the sweep is BOUNDED, not open-ended:
**at most 3 re-record attempts**, and **abort if cumulative real-provider spend
exceeds $30**. If both bars are still unmet at the bound, do NOT commit a sub-gate
set as a compromise — STOP, leave the committed sets unchanged, and return to the
design thread for a re-plan (the gate may need a different roster axis, an
engine-balance change, or a revised target). A committed-but-sub-gate set would
silently poison every later agent-intelligence A/B.

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
- [ ] A meeting-heavy 7p/2i + 2-task sample set is generated via `scripts/refresh_samples.sh` against the real provider (using 7.4's roster-aware routing + 7.1's flags) into `replays/samples/7p2i/` with its `roster.json` + `MANIFEST.md`, and committed **alongside** the existing 4p/1i baseline; the 4p/1i set is not deleted or overwritten.
- [ ] **Wave 0 exit gate met on the committed canonical set:** 7.3's `meeting_rate` is `>= 0.60` with `>= 30` resolved meetings, AND the decisive crew/impostor split is near-even (not all-`CREWMATE_TASKS`, not all-parity). The chosen canonical config and the gate numbers are recorded in the PR `## Decisions` block.
- [ ] **Bounded sweep + stopping rule:** the balance sweep is capped at **3 re-record attempts** and aborts if cumulative real-provider spend exceeds **$30**. If both bars are still unmet at the bound, NO set is committed as a sub-gate compromise — the committed sets are left unchanged and the gate is escalated to the design thread for a re-plan. The PR `## Decisions` records the attempts made and the spend.
- [ ] **Real-vs-fake divergence sanity check:** the diagnosis's fake-provider expectation is ~63% meeting rate; if the real-provider `meeting_rate` diverges from that by more than **10pp** (either direction), investigate the cause before committing (it signals a provider-behavior or config discrepancy, not just noise).
- [ ] The determinism / byte-identical replay suite AND the leak suite — including the W0.2 `self_state.fellow_impostor_ids == ()` crew-recipient invariant from 7.2 — pass on **both** committed sets. The **CI-enforced** gate for the new 7p/2i set is a pytest test in `tests/api/test_replay_loader.py` that loads + reconstructs the COMMITTED `replays/samples/7p2i/` set (run under `check.sh`'s pytest, since `check.sh` runs `uv run pytest` but does NOT invoke `verify_samples.sh`), paired with the existing pytest coverage of the flat 4p/1i set — both committed sets thus CI-gated. `scripts/verify_samples.sh <set-dir>` is the MANUAL operator tool (`scripts/verify_samples.sh` for 4p/1i, `scripts/verify_samples.sh replays/samples/7p2i` for the new set), run before committing.
- [ ] The PR `## Decisions` block records: the canonical Phase 7 eval config (roster + tasks-per-crewmate) and whether a re-balance sweep was needed; the measured `meeting_rate` / resolved-meeting count / decisive split; and the total real-provider spend (from the refresh's cost line / MANIFEST sum).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Confirm 7.4's plumbing is merged and green on the fake provider FIRST (the loader
reconstructs a hermetic 2-impostor replay, refresh/manifest route per-set). Then,
and only then, spend: run `scripts/refresh_samples.sh` with 7.1's roster/task flags
targeting `replays/samples/7p2i/` (via the `AILIBI_SAMPLE_DIR`/`AILIBI_MANIFEST`
hooks 7.4 wired), read 7.3's `meeting_rate` off the resulting
`replays/samples/7p2i/tournament-eval-report.json`, and check the exit gate +
balance. A balance re-sweep (2↔3 tasks / roster) means multiple real runs, so honor
the 3-attempt / $30 bound and the stop-and-escalate rule. After committing, add the
pytest test that loads + reconstructs the committed `replays/samples/7p2i/` set so
its determinism is CI-gated, and run `scripts/verify_samples.sh replays/samples/7p2i`
manually. Do NOT edit the 7.4 plumbing or any engine/agent code; this is a
data-generation + gate-confirmation task.

**Integration risk:**

This task spends real money, commits the first multi-impostor fixture set, and
decides whether the Phase 7 roster re-balances — all design-thread judgment.

- **Real-provider spend is one-shot and bounded.** 7.4's plumbing must be merged
  and fake-validated first; the 3-attempt / $30 bound + stop-and-escalate rule
  prevents an open-ended re-balance spend.
- **The 4p/1i baseline must survive untouched.** Commit the 7p/2i set ALONGSIDE; a
  mis-routed refresh that overwrote `replays/samples/` would destroy the
  determinism/leak regression + A/B reference. Verify the flat set still
  reconstructs after the commit.
- **Firewall on the first committed multi-impostor data.** The 7.2
  `fellow_impostor_ids == ()` crew invariant must hold across the new set's
  packets, not just the single-impostor 4p/1i set; run the leak suite over both.
- **Gate honesty.** `meeting_rate` and the decisive split are measured on the real
  provider, not assumed from the fake-provider 63%; the divergence check + bounded
  sweep are what keep an unbalanced or low-meeting set from being committed as a
  false "gate cleared".

**Ready-to-paste prompt:** `agent_prompts/task-7-5-meeting-heavy-eval-set.md`

## Merge Criteria (Wave 0 — enablement gate)
- **Config reachable + deterministic:** Task 7.1 lands the `tasks_per_crewmate` knob (default 2), the `4p1i`/`7p2i` roster presets, and the CLI threading; the `tasks_per_crewmate=1` path stays byte-identical to the committed 4p/1i baseline.
- **Firewall extended for multi-impostor play:** Task 7.2 lands impostor-only `fellow_impostor_ids` on `SelfView`, with the new leak invariant (`self_state.fellow_impostor_ids == ()` for every crew-recipient packet) green; `visible_players` / `PlayerView` unchanged.
- **The gate is measurable:** Task 7.3 lands the `meeting_rate` / `meetings_total` + body/emergency-trigger metric on `TournamentEvalReport`, mirrored across the eval route (`api/routes/eval.py::_TournamentEvalReportView`), the `tests/api/test_leak.py` field-set snapshot, the regression baseline, and `frontend/src/types/api.ts` (`api/schemas.py` is untouched — the metric reports do not live there).
- **Roster-aware loader + two-set layout landed (plumbing, Task 7.4):** the per-set `roster.json` + fail-loud `api.replay_loader.RosterConfig`, the roster-aware `_walk` re-seed, and per-set refresh/manifest routing — dispatchable, fake-validated, no committed data; the flat 4p/1i default re-seed stays byte-identical.
- **Stage-A enablement gate met (Task 7.5):** on the committed canonical set (7p/2i + 2 tasks unless Task 7.5's bounded balance sweep re-balanced it), `meeting_rate >= 0.60` with **>= 30 resolved meetings** and a non-degenerate decisive crew/impostor split (not all-`CREWMATE_TASKS`, not all-parity). The 7p/2i set is committed alongside the untouched 4p/1i baseline.
- **Both committed sets reconstruct + are leak-free:** the determinism / byte-identical replay suite and the leak suite (including the 7.2 crew invariant) pass on **both** the 4p/1i and 7p/2i sets via the per-set roster-aware loader.
- **All gates green:** `bash scripts/check.sh`, determinism tests, leak tests, and (for 7.3) frontend `tsc:check` + `vite build`.
- **Wave boundary respected:** Wave 0 ships config/substrate + the meeting-heavy denominator only — NO new contradiction-detector kinds, crewmate wander idle, impostor vent/sabotage, or teammate-defense meeting behavior land here (those are Wave 1 / Wave 2). Wave 1+ contracts are appended to this file only after this gate clears.
- **Intentional non-changes (NOT regressions — flagged so a Wave-1 reviewer doesn't mistake them for gaps):** (a) the spectator **dashboard renders no new metric** after Task 7.3 — 7.3 only adds the `meeting_rate` type to `frontend/src/types/api.ts` (the 1:1 mirror); surfacing it in the UI is deferred. (b) The live spectator app **continues to serve only the flat 4p/1i set**; the committed 7p/2i set is reachable programmatically (`ReplayLoader(replay_dir="replays/samples/7p2i")`) but not via the app until the deferred browse-selector frontend track lands.
