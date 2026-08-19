# Agent Prompt — 7.1 Configurable roster + tasks-per-crewmate knob

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.1 — Configurable roster + tasks-per-crewmate knob, anchored to Phase 7 plan W0.1 + decisions 1, 2; diagnosis audit `audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md` §1, §3, §4; DESIGN.md §1.4, §3.1, §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `orchestrator.game.RosterPreset`
- `orchestrator.game.DEFAULT_TASKS_PER_CREWMATE`
- `orchestrator.game.ROSTER_PRESETS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-7-configurable-roster-and-tasks-per-crewmate` with a title like `task 7.1: configurable roster + tasks-per-crewmate knob`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Phase 7 plan W0.1 + decisions 1, 2; diagnosis audit `audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md` §1, §3, §4; DESIGN.md §1.4, §3.1, §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
