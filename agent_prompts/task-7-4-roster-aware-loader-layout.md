# Agent Prompt — 7.4 Roster-aware replay loader + two-committed-set layout (plumbing)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-7.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 7.4 — Roster-aware replay loader + two-committed-set layout (plumbing), anchored to tasks/phase-7-plan.md W0.4, Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-7.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `api.replay_loader.RosterConfig`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

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

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import observation.packet.SelfView"`
- `uv run python -c "import orchestrator.game"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-7-roster-aware-loader-layout` with a title like `task 7.4: roster-aware replay loader + two-committed-set layout (plumbing)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-7-plan.md W0.4, Q3; audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md §3, §6; DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
