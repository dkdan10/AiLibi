# Phase 6 — Repair And Hardening

## Goal
Phase 6 is the repair phase that lands the MVP-close audit's surviving findings
(`audits/audit-2026-05-30-0059-mvp-close.md`, verdict MINOR_REPAIRS_NEEDED, 57
surviving findings). It hardens the deployment surface, reconciles documentation
with HEAD, extends the leak firewall to the Phase 5 eval surface, pins
known-deferred behavior with characterization tests, makes the dormant
agent-intelligence substrate actually run (wire the contradiction detector,
belief Rule 2, and a `BeliefState` into perception), closes the win-condition
impostor-elimination gap, and removes the dominant frontend/backend performance
cliffs. Net-new agent capability and the Claude-Design UI redesign are NOT in
this phase — they are Phase 7+.

**Scope decisions (lock these before dispatching any task):**

- **Phase 6 is repair, Phase 7 is capability.** The cut line: wiring code that
  already exists but is dead, or fixing documentation/metric drift, is repair and
  belongs here. Adding capability that does not exist yet is "smarter agents" and
  belongs to Phase 7. So wiring the existing `detect_contradictions` + belief
  Rule 2 + `BeliefState`-into-perception (Task 6.4) is Phase 6 — it makes the
  *designed* intelligence function, which is dead in live play today. Adding new
  detector kinds, richer claim vocabulary, and impostor vent/sabotage tactics is
  Phase 7.
- **The engine lane is the critical path and serializes on fixtures.** Tasks 6.3
  (win-condition) and 6.4 (contradiction wiring) both change replay determinism
  and regenerate the committed `replays/samples/` fixtures. They integrate
  strictly serially — one fixture regeneration each, in order (6.3 then 6.4).
  Batching both behavior changes into one regeneration would destroy the close
  gate's per-change metric attribution (the Phase 5 regression suite attributes a
  metric delta to a single change). Task 6.2 pins the current win-condition
  behavior with a characterization test that Task 6.3 then flips, so 6.3 depends
  on 6.2.
- **DESIGN.md reconciliation is design-thread-owned, NOT a dispatched task.**
  Generated agent prompts forbid editing DESIGN.md, so the audit's Class A
  reconciliation (A-1..A-10 + H-1) is done in the design thread, not via
  `agent_prompts/`. It is listed under "Design-thread-owned items" below. The
  related auto-memory note fix (F-F-4) was already applied on 2026-05-30.
- **Frontend redesign-coupled work is deferred to Phase 7.** Task 6.7 lands ONLY
  the performance substrate (memoize MapView, window the payload) — it survives a
  redesign. The accessibility rebuild, error-surface polish, roster legend,
  responsive canvas, brand tokens, and motion polish (audit 6.0.8/6.0.9, the
  Class K cluster) fold into the Phase 7 Claude-Design pass rather than polishing
  what gets rebuilt. One exception: the `CorruptedFileError` picker-crash (K-K-8)
  has a backend root-cause that is independent of the redesign — `list_replays`
  500s the whole picker on one bad file. That server-side resilience fix is folded
  into Task 6.6 (which owns the loader/route); the frontend error-display half
  (aria-live, friendly messages, dedicated corrupted-file UI) stays in Phase 7
  with the redesign.
- **Per-task gate is automated; Phase 6 close adds a real-provider eval.** Each
  individual task closes on `bash scripts/check.sh` (static gates + determinism +
  leak + the Phase 5 regression suite over recorded fixtures) — no per-patch
  real-provider eval, per the eval-cadence rule. But Phase 6 as a whole DOES
  require one end-of-phase real-provider eval, because Task 6.4 is a
  substrate-level change: it feeds the live model contradiction flags and
  belief-derived suspicion it has never received, and the recorded-fixture
  regression suite cannot validate live-model behavior. See "Phase 6 close:
  real-provider eval" below. The eval runs ONCE, after 6.4 merges — not per task.

## Phase 6 close: real-provider eval
After Task 6.4 merges (the last substrate-level change in the phase), run one
real-provider tournament eval as the Phase 6 close gate. This is a design-thread
activity, not a dispatched web session.

- **Why:** 6.4 makes the contradiction detector, belief Rule 2, and the
  perception belief path live, so agents now receive prompt content and suspicion
  state they never saw before; and 6.3 changes terminal win attribution, so the
  pre-Phase-6 balance numbers are stale. Only a live model validates that the
  newly-live agent-intelligence substrate behaves sensibly and leak-free, and
  only a fresh tournament re-establishes a trustworthy balance baseline for
  Phase 7 tuning.
- **What to run:** a tournament via `scripts/run_tournament.py` against the real
  provider, at least at the committed-sample scale (50 games; precedent
  `audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md`, ~$0.9). Scale
  up if the balance shift needs tighter confidence; cost/scale is the design
  thread's call.
- **Acceptance checks:** (1) zero leaks across the tournament's observation
  packets and rendered prompts (the property sweep added in 6.2 plus the live
  run); (2) at least one game shows a detected contradiction actually shifting a
  vote, demonstrating the 6.4 wiring is behaviorally live, not just present;
  (3) the new impostor-win-rate / cost aggregates are recorded as the post-Phase-6
  baseline; (4) no cost blow-up versus the Phase 3/5 per-game cost envelope.
- **Artifact:** write the outcome to
  `audits/audit-YYYY-MM-DD-HHMM-post-phase-6-real-provider-eval.md` and update the
  balance baseline the README/dashboard cite (cf. Task 6.8's README reconciliation,
  which should land first so the eval updates an already-corrected number).

## Parallelism
Four lanes run concurrently:

- **Docs lane:** Task 6.8 (README/AGENTS/.env). Independent; fan out anytime.
- **Backend/infra lane:** Tasks 6.1 (deploy hardening), 6.6 (loader efficiency),
  6.9 (format-version guard). Disjoint file scopes; fan out in parallel.
- **Frontend lane:** Task 6.7 (performance). The only Phase 6 frontend task;
  no contention.
- **Correctness → engine lane (critical path):** Tasks 6.2 + 6.5 fan out first
  (test/DTO additions), then 6.3 (win-condition, depends on 6.2), then 6.4
  (contradiction wiring, depends on 6.3 for fixture serialization). Phase 6
  wall-clock is dominated by this lane.

## Design-thread-owned items
These are done in the design thread, not dispatched via `agent_prompts/`:

- **DESIGN.md reconciliation** (audit findings A-A-1..A-A-10, H-H-1). A single
  documentation pass over DESIGN.md: reconcile persistence to JSONL-on-disk
  (Postgres/JSONB deferred to scale, §1.1/§1.2/§6.5/§7/§8.1/§11.1); reframe the
  real-time WebSocket push surface, `api/ws.py`, and `POST /games`/`api/routes/
  games.py` as the implemented static read-only replay+eval REST API with the
  live-broadcast layer deferred to Phase 6+ (record in the design thread that the
  broadcast layer is unbuilt, per H-1); add a §6.3 deferral note (live Rules 1/4,
  deferred 2/3/5) plus the note that the runtime does not yet pass a `BeliefState`
  into perception; downgrade §10.4 anti-hallucination to "prompt-instructed,
  code cross-check deferred"; mark §7 observability (structlog/OTel) and the §2
  docker-compose/file-tree annotations (including the absent `meeting_memo`
  module — verify deferred vs implemented elsewhere) to match HEAD; note
  `render_replay.py` is subsumed by the live UI; record §0.2's ≤100-calls as a
  target, not an enforced invariant.

## Deferred to Phase 7+
- New contradiction-detector kinds — temporal impossibility, body-discovery
  timing, mutual-witness sighting-vs-sighting (audit J-J-2).
- Impostor vent/sabotage tactics + adaptive meeting rounds (audit 6.1.3, J-J-5,
  J-J-7).
- Frontend accessibility rebuild + visual identity/motion polish (audit
  6.0.8/6.0.9, Class K) — fold into the Claude-Design redesign. This includes the
  K-K-8 frontend error-display half (aria-live, friendly messages, dedicated
  corrupted-file UI); the K-K-8 backend crash fix is in Task 6.6.
- Multi-instance port parameterization + async-worker game execution (audit
  post-mvp-2, H-H-4, H-H-5) — scale-phase; no current code to migrate.

## Tasks

### Task 6.1 — Harden the deployment surface (docker-compose bind + CORS posture)
**Branch:** `phase-6-deploy-surface-hardening`
**Depends on:** none
**Section refs:** Audit C-C-1, C-C-2, C-C-4; DESIGN.md §1.1, §7
**Complexity:** Small

The spectator API serves the full GM view — every hidden-information field
(roles, kill attribution, vent state, rendered prompts) with no authentication,
by deliberate design for local single-user spectating. `scripts/run_spectator.sh`
correctly defaults its bind to `127.0.0.1`, but `docker-compose.yml` starts
uvicorn with `--host 0.0.0.0` (lines 13–14) and publishes the port to the host
(line 21), so `docker compose up` exposes every hidden field to the LAN
(audit C-C-1, the single highest-urgency operational finding). There is also no
CORS posture anywhere in `api/` (C-C-2): security relies entirely on the Vite
dev-server same-origin proxy, which exists only under `npm run dev`.

This task makes the local-only privilege model explicit and safe-by-default. It
binds docker-compose to the loopback interface, adds a documented CORS posture,
and records a deploy note stating that the unauthenticated GM-view API must sit
behind authentication and network isolation before any all-interfaces bind. The
rate-limiting concern (C-C-4) is documented as a pre-exposure requirement, not
coded — it lives behind the same "exposed beyond localhost" boundary and touches
`api/replay_loader.py`, which is owned by Task 6.6; do not edit that file here.

CORS handling is additive and must default to a closed posture: if a cross-origin
allowlist is configured (via an environment variable), install
`CORSMiddleware` with that explicit allowlist; if unset, install no permissive
middleware (same-origin static serving needs none). Never ship `allow_origins=
["*"]`.

**Files in scope:**
- docker-compose.yml
- api/main.py
- docs/deployment.md
- tests/api/test_app_config.py

**Files NOT in scope:**
- api/replay_loader.py (rate limiting is documented here, coded in Task 6.6 territory; do not edit the loader)
- api/routes/
- api/schemas.py
- README.md (README drift is Task 6.8)
- scripts/run_spectator.sh (already correct)
- frontend/

**Definition of done:**
- [ ] `docker-compose.yml` binds uvicorn to `127.0.0.1` (loopback) rather than `0.0.0.0`, OR documents in an adjacent comment that the all-interfaces bind is deliberate and gated behind a reverse proxy; the default committed state must not expose the GM view to non-loopback interfaces.
- [ ] `api/main.py` installs `CORSMiddleware` ONLY when a cross-origin allowlist is supplied via an environment variable (e.g. `AILIBI_CORS_ORIGINS`, comma-separated); when unset, no permissive CORS middleware is added. No `allow_origins=["*"]` anywhere.
- [ ] `docs/deployment.md` states: the API is an unauthenticated GM view; it is safe only on loopback or behind auth + network isolation; the production CORS posture (same-origin static serving needs no CORS, cross-origin requires the closed allowlist); and that an edge rate limiter and a short-TTL negative-lookup cache are prerequisites before any network exposure (C-C-4), to be implemented when the exposure path is built.
- [ ] `tests/api/test_app_config.py` asserts the default app installs no permissive CORS middleware, and that supplying `AILIBI_CORS_ORIGINS` installs a closed allowlist (no wildcard).
- [ ] No behavior change to any route handler or DTO; the local `npm run dev` + spectator flow is unaffected.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `docker-compose.yml` (the uvicorn command at lines 13–14 and the port
publish at line 21) and `scripts/run_spectator.sh:84` (the correct loopback
default) before editing. The compose service should mirror the script's
loopback default. For CORS, read how `api/main.py:create_app()` is structured
(line ~96) and add middleware conditionally inside it, reading the allowlist
from the environment with `os.environ.get`. Follow the project's no-silent-
fallback discipline: an explicitly-set-but-empty allowlist should be treated as
"no cross-origin access", not "allow all". The deploy note is the durable
artifact — it is what makes the privilege model legible to a future deployer.

**Integration risk:**

The local spectator workflow must not regress. Confirm `scripts/run_spectator.sh`
and `npm run dev` still serve end-to-end after the change; the CORS middleware
must be a no-op in the default (unset-allowlist) path so the same-origin dev
proxy continues to work unchanged.

**Ready-to-paste prompt:** `agent_prompts/task-6-1-deploy-surface-hardening.md`

### Task 6.2 — Pin known-deferred engine and firewall behavior with characterization tests
**Branch:** `phase-6-deferred-behavior-characterization-tests`
**Depends on:** none
**Section refs:** Audit I-I-1, I-I-2, I-I-3; DESIGN.md §11.2, §6.5
**Complexity:** Medium

Three load-bearing behaviors are currently unprotected by tests, so a future
refactor could silently break them (audit Class I). This task adds
characterization tests ONLY — no production code changes, no replay-byte changes.

First, lights-out sabotage — the sole MVP sabotage — reduces visibility to
same-room-only, but no test exercises the active-sabotage branch
(`engine/visibility.py:25`): `test_visibility.py` has only two tests, both with
`sabotage=None`, and all seven `test_service.py` world states are `sabotage=None`
(I-I-1). A bug dropping the `world_state.sabotage.active` check would pass the
whole suite while letting crewmates see through a blackout.

Second, DESIGN §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep, but the implementation
(`eval/leak_test.py:271`) walks exactly three hand-authored fixtures (I-I-2). A
leak that manifests only under an unseen packet shape would not be caught. Add a
property-based leak sweep reusing the role-aware Hypothesis strategy from
`tests/.../test_tick_properties.py`, running `ObservationService` over every
living agent each tick across many seeds and applying the EXISTING scanners.

Third, no test pins the all-impostors-eliminated outcome
(`engine/win_conditions.py:19`): `evaluate_win_conditions` returns `None` with
zero alive impostors and incomplete tasks (the deferred gap, repro seed 49), and
a future refactor of the parity comparison could flip the zero-impostor case in
either direction with nothing failing (I-I-3). Add a characterization test that
pins the CURRENT deferred behavior with a co-located comment referencing the
design-thread gap, so Task 6.3 can flip it when it closes the gap.

**Files in scope:**
- tests/engine/test_visibility.py
- tests/observation/test_leak_property.py
- tests/engine/test_win_conditions.py

**Files NOT in scope:**
- engine/ (no production change; tests only)
- observation/ (no production change)
- eval/leak_test.py (reuse, do not modify)
- agents/
- meetings/
- replays/ (no fixture regeneration)

**Definition of done:**
- [ ] `tests/engine/test_visibility.py` gains tests asserting that with an ACTIVE lights-out sabotage: (a) `resolve_visibility_mode` returns `same_room_only`, (b) `visible_rooms_for_player` collapses to the observer's own room, (c) a player in an adjacent room becomes invisible; plus a test that an unknown sabotage kind raises `ValueError` (I-I-1).
- [ ] `tests/observation/test_leak_property.py` adds a property-based test that reuses the role-aware Hypothesis strategy from the existing tick-properties test, runs `ObservationService` for every living agent on every tick across many seeds, and applies the existing leak scanners from `eval/leak_test.py`, asserting no role/kill/engine-state field leaks (I-I-2). It imports the scanners; it does not reimplement them.
- [ ] `tests/engine/test_win_conditions.py` adds a characterization test pinning the CURRENT behavior: zero alive impostors + incomplete tasks → `evaluate_win_conditions` returns `None`. A co-located comment states this is the deferred impostor-elimination gap (memory `project_win_condition_impostor_elimination_gap`) and is flipped by Task 6.3.
- [ ] No file under `engine/`, `observation/`, or `eval/` is modified; `git diff --name-only` shows test files only.
- [ ] No replay fixture bytes change.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `engine/visibility.py` (`resolve_visibility_mode`, `visible_rooms_for_
player`, the sabotage branch around line 25), the existing
`tests/engine/test_visibility.py` for the construction idiom, and
`eval/leak_test.py` (the scanner entry points around line 271) plus the
role-aware strategy in the existing tick-properties property test. Construct the
active-sabotage `WorldState` the same way the engine tests already build states;
do not invent a new fixture format. For the leak sweep, drive
`ObservationService` exactly as production does (one packet per living agent per
tick) and feed each packet through the imported scanner functions — the value is
breadth of inputs, not new assertions. The win-condition test must assert the
present `None` return so it goes RED the moment Task 6.3 adds the elimination
case; Task 6.3 owns flipping it to assert the crew win.

**Ready-to-paste prompt:** `agent_prompts/task-6-2-deferred-behavior-characterization-tests.md`

### Task 6.3 — Close the win-condition impostor-elimination gap
**Branch:** `phase-6-win-condition-impostor-elimination`
**Depends on:** 6.2 merged
**Section refs:** Audit J-J-8, I-I-3; DESIGN.md §3, §8.1
**Complexity:** Integration

`evaluate_win_conditions` has no `alive_impostors == 0 → CREWMATES win` case
(`engine/win_conditions.py:17`). After the last impostor is ejected the game runs
on until tasks complete or the tick budget expires — a zombie game with no
possible loser, distorting the eval/balance numbers (games the crew effectively
won record as `TICK_BUDGET_REACHED` or `CREWMATE_TASKS`). Confirmed in
replay-seed-49 (audit J-J-8; memory `project_win_condition_impostor_elimination_
gap`). This is the deferred gap; closing it is a prerequisite for trustworthy
balance numbers before any Phase 7 agent-intelligence tuning.

Add a fourth condition evaluated BEFORE the task-completion check: if there are
zero alive impostors, the crew wins by ejection. Add the corresponding
`WinResultType` literal (the current type is at `engine/win_conditions.py:8`).
This changes the decisive outcome of any game where the last impostor is ejected
before tasks finish, so it alters replay determinism and the committed sample
fixtures — the fixtures must be regenerated and the change needs design-thread
sign-off (recorded here; the design thread approved closing the gap on
2026-05-30). Flip the Task 6.2 characterization test from asserting `None` to
asserting the crew elimination win.

Ordering check before fixture regeneration: this is the FIRST of the two
fixture-regenerating engine tasks (6.3 then 6.4). Regenerate fixtures exactly
once here, in this task, so the close-gate can attribute the resulting metric
delta to this single change. Do not also start Task 6.4's wiring in this branch.

**Files in scope:**
- engine/win_conditions.py
- tests/engine/test_win_conditions.py
- replays/samples/MANIFEST.md
- replays/samples/

**Files NOT in scope:**
- engine/ (other than win_conditions.py)
- meetings/
- agents/
- api/
- frontend/
- eval/
- DESIGN.md (reconciled in the design thread)

**Definition of done:**
- [ ] `engine/win_conditions.py` adds a condition: with zero alive impostors, return `WinResult(CREWMATES, reason="CREWMATE_EJECT")` (or the project's winner-enum equivalent), evaluated BEFORE the existing task-completion check and after the existing parity check ordering is preserved for all other cases.
- [ ] The `WinResultType` literal at line 8 gains the new `CREWMATE_EJECT` reason; the TypeScript mirror and any schema that enumerates win reasons are updated so `generate_prompts.py --check` and the schema-mirror tests stay green.
- [ ] The Task 6.2 characterization test in `tests/engine/test_win_conditions.py` is flipped from asserting `None` to asserting the crew elimination win for zero-impostor + incomplete-tasks; the co-located comment is updated to note the gap is now closed.
- [ ] All other win-condition orderings (impostor parity, sabotage, crew tasks) are unchanged and still tested.
- [ ] The committed `replays/samples/` fixtures are regenerated with the project's refresh-samples workflow and `replays/samples/MANIFEST.md` is updated; the determinism / byte-identical replay tests pass against the regenerated set.
- [ ] The PR `## Decisions` block records: design-thread sign-off to close the gap (2026-05-30); the new reason literal name; and that fixtures were regenerated exactly once in this task.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `engine/win_conditions.py` end-to-end (the `WinResultType` literal at
line 8, `WinResult` at line 14, `evaluate_win_conditions` and its ordering at
lines 17–22) and the win-reason mirror on the TypeScript side plus any schema
enum that lists reasons. The new case is a few lines, but ORDER matters: place
the zero-impostor crew win before the task-completion check so an
already-all-tasks-done-and-no-impostors game attributes to the ejection win per
design intent — confirm the intended precedence in the design thread note if
ambiguous. Use the existing refresh-samples workflow (do not hand-edit JSONL) to
regenerate fixtures, and re-run the determinism tests to confirm byte-identical
reconstruction of the new set. This is the first fixture-regenerating task;
Task 6.4 depends on it precisely so the two regenerations stay serial.

**Public types introduced:**
- engine.win_conditions.WinResultType

**Integration risk:**

This is a determinism-altering engine change with committed-fixture blast radius.

- **Fixture regeneration is the risk surface.** Regenerate exactly once, via the
  refresh-samples workflow, and verify the determinism + leak tests pass on the
  new set before committing. A hand-edited or partially-regenerated
  `replays/samples/` set will fail the byte-identical replay gate.
- **Serial with Task 6.4.** Both tasks rewrite `replays/samples/`. 6.4 depends on
  6.3 so the regenerations never interleave; do not begin 6.4's wiring here.
- **Mirror the new reason everywhere.** The win reason crosses the
  Python↔TypeScript schema mirror; a missed mirror edit fails the schema-sync
  gate. Grep for every enumeration of win reasons before finishing.
- **Eval numbers shift intentionally.** The balance aggregates (impostor win
  rate) will move because zombie games now resolve as crew ejection wins. That is
  the point; note the expected direction in the PR so the shift is not mistaken
  for a regression.

**Ready-to-paste prompt:** `agent_prompts/task-6-3-win-condition-impostor-elimination.md`

### Task 6.4 — Wire the contradiction-detection subsystem into live meetings
**Branch:** `phase-6-contradiction-detection-wiring`
**Depends on:** 6.3 merged
**Section refs:** Audit J-J-1, J-J-9, J-J-4, A-A-4; DESIGN.md §5.4, §6.3, §6.4
**Complexity:** Integration

The contradiction detector, belief Rule 2, and the perception belief-update path
all exist but are dead in live play — this is the hard prerequisite for any
Phase 7 "smarter agents" work, and this task makes the designed intelligence
actually function. Specifically: `detect_contradictions` (the whole §5.4/§6.4
subsystem) is invoked only by tests; `MeetingManager.run` hardcodes
`contradictions=()` and threads that empty tuple into every statement prompt,
vote prompt, and persisted result, so no agent ever sees a contradiction flag
(audit J-J-1, confirmed: all four meeting-bearing samples show contradictions=0).
Belief Rule 2's write-paths (`record_contradiction`, `adjust_suspicion`) are
defined and unit-tested but never called in production (J-J-4). And
`AgentRuntime._perceive` (`agents/runtime.py:56`) calls `ingest_packet` without a
`BeliefState`, so even the two implemented belief rules (1 and 4) are dormant in
headless games (A-A-4). `PlayerId` subject matching uses a hardcoded placeholder
allowlist, so non-roster subjects silently fail to match (J-J-9) — load-bearing
once the detector is live.

This task wires the existing pieces; it does NOT add new detector kinds (temporal
impossibility, body-discovery timing, mutual-witness — those are Phase 7,
J-J-2). Scope:

1. Wire `detect_contradictions` into `MeetingManager.run`: recompute from the
   transcript-so-far before each accusation round and before voting, thread the
   live tuple into the statement and ballot prompts and the persisted result.
2. Replace the hardcoded subject allowlist with roster-aware normalization: map
   self-placeholders to the speaker id and reject/flag any subject not in the
   living-player roster, so contradiction matching never silently drops a claim.
3. Implement belief Rule 2: on a detected contradiction, call
   `record_contradiction` + `adjust_suspicion` so the vote suspicion graph
   reflects detected lies.
4. Pass a `BeliefState` into `AgentRuntime._perceive` → `ingest_packet` so the
   already-implemented Rules 1 and 4 run in headless games.

This changes meeting behavior and therefore replay determinism, so fixtures are
regenerated — the SECOND and last fixture-regenerating task, sequenced after 6.3.

**Files in scope:**
- meetings/manager.py
- meetings/transcript.py
- agents/memory/beliefs.py
- agents/runtime.py
- agents/perception.py
- tests/meetings/test_manager.py
- tests/agents/test_beliefs_wiring.py
- replays/samples/MANIFEST.md
- replays/samples/

**Files NOT in scope:**
- meetings/schemas.py (reuse; do not reshape)
- engine/ (win_conditions.py was Task 6.3)
- api/
- frontend/
- eval/
- agents/strategic/prompts/ (no new detector-kind prompts; that is Phase 7)
- DESIGN.md (reconciled in the design thread)

**Definition of done:**
- [ ] `MeetingManager.run` calls `detect_contradictions` over the transcript-so-far before each accusation round and before voting, threads the resulting tuple into the statement prompts, the ballot prompts, and the persisted meeting result; `contradictions=()` is no longer hardcoded (J-J-1).
- [ ] Subject matching is roster-aware: self-placeholders map to the speaker id and any subject not in the living-player roster is rejected or explicitly flagged, replacing the hardcoded allowlist (J-J-9). A test covers a non-roster subject (e.g. `p-0`/`p-99`) being handled deterministically rather than silently dropped.
- [ ] Belief Rule 2 is wired: on a detected contradiction the meeting/runtime path calls `record_contradiction` + `adjust_suspicion`, and a test asserts the vote suspicion graph reflects a detected contradiction (J-J-4).
- [ ] `AgentRuntime._perceive` passes a `BeliefState` into `ingest_packet` so belief Rules 1 and 4 run in headless games; a test asserts a body-proximity (Rule 1) or witnessed-vent (Rule 4) update occurs in a headless run (A-A-4).
- [ ] No new detector kinds are added (temporal/body-timing/mutual-witness are Phase 7); `_iter_sightings` is extended to index statement-borne claims ONLY insofar as the existing `alibi_conflict`/`alibi_vs_sighting` detectors need it to see statement claims — no new detector enum values.
- [ ] The committed `replays/samples/` fixtures are regenerated with the refresh-samples workflow and `MANIFEST.md` updated; determinism / byte-identical replay tests pass; at least one regenerated meeting-bearing sample now shows a non-zero contradiction count where the transcript warrants it.
- [ ] The leak tests still pass — contradiction flags and belief updates introduce no cross-player role or engine-state exposure in any observation packet or rendered prompt.
- [ ] The PR `## Decisions` block records: that this is wiring-only (no new detector kinds); the `BeliefState` threading approach through `_perceive`; and that fixtures were regenerated once, after Task 6.3.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (the agents↔engine firewall is preserved; `BeliefState` is an agents-side type).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `meetings/transcript.py` (`detect_contradictions` at line 97, `_iter_
sightings`, and the exported detector kinds), `meetings/manager.py` (the `run`
loop, the `contradictions=()` hardcode, and the subject-allowlist around
line 124), `agents/memory/beliefs.py` (Rule 2 write-paths `record_contradiction`
/`adjust_suspicion`, around line 36), and `agents/runtime.py:56` →
`agents/perception.py:58` (the `ingest_packet` call missing the `beliefs=`
argument). Wire in the order the audit's prerequisite chain implies: detector
into `run` → roster-aware subject normalization → Rule 2 on detected
contradictions → `BeliefState` into `_perceive`. Keep the agents↔engine firewall
intact: `BeliefState` and belief updates are agents-side; do not import engine
types into `agents/`. Regenerate fixtures via the refresh-samples workflow, never
by hand, and confirm at least one meeting-bearing sample now records
contradictions so the wiring is demonstrably live (not just present). This is the
second and final fixture-regenerating task — it depends on 6.3 so the two
regenerations never interleave.

**Integration risk:**

This is the highest-blast-radius task in the phase: it changes agent-visible
meeting inputs, belief state, and replay determinism at once.

- **Behavior is now live where it was dead.** Agents that previously saw
  `contradictions=()` now see real flags and update suspicion. Expect meeting
  transcripts, ballots, and outcomes to shift; the regenerated fixtures capture
  the new behavior. Verify the determinism tests pass on the new set.
- **Firewall preservation is non-negotiable.** `BeliefState` threading runs
  entirely on the agents side; an accidental `engine/` import in `agents/` fails
  `lint-imports` and breaks the project's load-bearing invariant. Keep engine
  translation in orchestrator-owned code.
- **Leak surface re-check.** Contradiction flags are derived from transcript
  statements (already public to the meeting) and belief updates are per-agent;
  confirm no rendered prompt or observation packet now embeds another player's
  role or engine state. The leak tests must stay green.
- **Serial with Task 6.3.** Both regenerate `replays/samples/`; 6.4 depends on
  6.3 so the regenerations stay one-at-a-time and the close-gate can attribute
  each metric delta to its own change.
- **No scope creep into Phase 7.** Adding new detector kinds or impostor
  vent/sabotage here would entangle capability work with the wiring repair and
  blur the metric attribution. Keep strictly to wiring the existing pieces.

**Ready-to-paste prompt:** `agent_prompts/task-6-4-contradiction-detection-wiring.md`

### Task 6.5 — Harmonize the eval-report failed-call surface and extend the leak firewall
**Branch:** `phase-6-eval-report-redaction-and-leak-firewall`
**Depends on:** none
**Section refs:** Audit B-B-1, D-D-1, B-B-2, D-D-2; DESIGN.md §11.2, §11.3
**Complexity:** Medium

The Phase 4 spectator DTO `FailedCallView` deliberately drops `raw_response` and
`prompt_length` and truncates `error_message` to 200 chars, but the Phase 5 eval
route `GET /eval/tournament-report` (`api/routes/eval.py:38`) serves
`TournamentEvalReport` directly, transitively embedding `FailedCallReplayEntry`
with all three raw fields — re-exposing over HTTP exactly what the parallel
surface suppresses (audit B-B-1 = D-D-1, a convergent cross-phase finding). Both
surfaces are privileged GM views with no auth per the established model, so this
is a contract asymmetry, not a role/engine-state leak — but the two surfaces must
agree. Separately, the structural leak-test firewall pins only `api.schemas`
(`tests/api/test_leak.py`), so the eval route's `TournamentEvalReport` and its
leaf DTOs ride outside the guard: a future engine-state field added to a replay
leaf type would silently expand the served payload with no tripwire (B-B-2 =
D-D-2).

This task does two things. First, resolve the redaction asymmetry in ONE explicit
direction: either (a) route the eval route's failed-call data through a sanitized
DTO that mirrors `FailedCallView`'s exclusions (drop `raw_response`/
`prompt_length`, truncate `error_message`), or (b) consciously document on the
route that the privileged surface intentionally exposes the raw failed-call
payload and align both surfaces' stated contracts. Pick (a) unless there is a
demonstrated consumer that needs the raw blob; record the choice. Second, extend
the leak firewall to cover the eval route: snapshot the recursive field set of
`TournamentEvalReport` (its leaf DTOs + the four metric reports) and assert no
engine-state field (`state_hash`, `rng_state`, etc.) is reachable, so any future
field addition forces an explicit review touch.

**Files in scope:**
- api/routes/eval.py
- api/schemas.py
- tests/api/test_leak.py
- tests/api/test_eval_routes.py

**Files NOT in scope:**
- api/replay_loader.py (Task 6.6)
- api/main.py (Task 6.1)
- api/routes/replays.py (Task 6.6)
- eval/report_schema.py (Task 6.9)
- frontend/
- orchestrator/replay.py (reuse leaf types; do not reshape)

**Definition of done:**
- [ ] The redaction asymmetry is resolved in one explicit, documented direction. If (a): a sanitized failed-call DTO mirroring `FailedCallView` (no `raw_response`, no `prompt_length`, `error_message` truncated to 200 chars) is served by the eval route, and a test asserts the served payload excludes the raw fields. If (b): the eval route carries a docstring/comment stating the raw failed-call exposure is intentional, and a test pins that the raw fields ARE present so the contract is explicit. The PR `## Decisions` block states which and why (B-B-1/D-D-1).
- [ ] `tests/api/test_leak.py` is extended with a recursive field-set snapshot/assertion over `TournamentEvalReport` and its leaf DTOs + the four metric reports, asserting no `state_hash`/`rng_state`/other engine-internal field is reachable on the served eval surface (B-B-2/D-D-2). The assertion is structured so adding a field to any leaf type forces an explicit update to the snapshot.
- [ ] `tests/api/test_eval_routes.py` covers the chosen redaction direction end-to-end through the route.
- [ ] No change to engine-side replay records; leaf types are reused by import, not redefined.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `api/routes/eval.py:38` (the route returning `TournamentEvalReport`), the
Phase 4 `FailedCallView` in `api/schemas.py` (the exclusion/truncation pattern to
mirror), `orchestrator/replay.py`'s `FailedCallReplayEntry`, and
`tests/api/test_leak.py:34` (how the firewall currently walks `api.schemas`). For
direction (a), define the sanitized DTO next to `FailedCallView` and map at the
route/loader boundary — do not mutate the underlying replay entry. For the
firewall extension, dump the recursive JSON schema of `TournamentEvalReport` and
assert the forbidden engine-internal field names are absent anywhere in the tree;
model it on the existing `api.schemas` forbidden-type assertions so the style is
consistent. The snapshot must fail loudly when a new field appears — that
tripwire is the durable value (D-D-2).

**Public types introduced:**
- api.schemas.FailedCallEvalView

**Ready-to-paste prompt:** `agent_prompts/task-6-5-eval-report-redaction-and-leak-firewall.md`

### Task 6.6 — Backend replay-loader efficiency, pagination, and corrupted-file resilience
**Branch:** `phase-6-replay-loader-efficiency-pagination`
**Depends on:** none
**Section refs:** Audit G-G-2, G-G-3, H-H-2, H-H-3, K-K-8 (backend half); DESIGN.md §11.1
**Complexity:** Medium

The replay loader re-parses files redundantly and has no pagination, which grows
linearly with the replay directory size (audit Class G/H). `cost_summary()`
reads each replay file twice (`api/replay_loader.py:236`), and
`list_replays()` → `_metadata_view` does two full reads plus two Pydantic passes
per file, none memoized — a 200-game directory is ~400 file parses per
`/eval/cost-summary` and per `/replays` request, re-globbed each call (G-G-2).
`GET /replays` has no limit/offset and builds a metadata view for every file in
one synchronous request (G-G-3). The per-process LRU cache key never incorporates
mtime, so an in-place replay rewrite (the refresh-samples workflow already does
this) serves stale data (H-H-2). And `update_manifest` does a non-atomic
read-modify-write with no lock, so a crash mid-write truncates the MANIFEST
(`scripts/_manifest_writer.py:314`, H-H-3).

This task reads each replay file once per request and derives both cost and
outcome from one `read_all_entries`; folds the double read in `_metadata_view`;
adds a per-file metadata cache keyed on `(path, mtime)` given the documented
immutability; folds mtime into the existing LRU cache key so an in-place refresh
invalidates correctly even pre-scale; adds optional `limit`/`offset` pagination to
`GET /replays`; and makes the manifest writer atomic via write-to-temp +
`os.replace`. The cross-worker shared cache and import-time loader construction
(H-H-6) remain documented scale-phase boundaries — do not build the shared cache
here.

This task also fixes the backend root-cause of the picker crash (K-K-8): today
`list_replays` does not catch `CorruptedFileError`, so a single corrupted replay
file throws an uncaught 500 that blocks the entire picker (`Task 4.16` made
`ReplayLog` raise `CorruptedFileError` on a malformed file). Make `list_replays`
tolerate a bad file: catch `CorruptedFileError` per file, exclude that file from
the listing, and emit a warning log so the corruption is recorded rather than
silently swallowed — the picker then still lists every healthy replay. This is
the server-side resilience fix only; the frontend's friendly error surfaces,
`aria-live` regions, and a dedicated corrupted-file UI are the other (a11y) half
of K-K-8 and stay in Phase 7 with the redesign.

**Files in scope:**
- api/replay_loader.py
- api/routes/replays.py
- scripts/_manifest_writer.py
- tests/api/test_replay_loader.py
- tests/scripts/test_manifest_writer.py

**Files NOT in scope:**
- api/main.py (Task 6.1; do not move import-time loader construction here)
- api/routes/eval.py (Task 6.5)
- api/schemas.py (Task 6.5)
- frontend/ (the frontend pagination/windowing is Task 6.7; the K-K-8 error-display/a11y half is Phase 7)
- replays/samples/ (no fixture regeneration)

**Definition of done:**
- [ ] `cost_summary()` and the metadata path read each replay file exactly once per request and derive both cost and outcome from a single `read_all_entries`; the double-read in `_metadata_view` is gone (G-G-2). A test asserts a single read per file (e.g. via a read counter/spy).
- [ ] A per-file metadata cache keyed on `(path, mtime)` memoizes the metadata view, given documented immutability; the existing per-process LRU cache key incorporates mtime so an in-place rewrite invalidates correctly (H-H-2). A test asserts a rewritten file (new mtime) is not served stale.
- [ ] `GET /replays` accepts optional `limit`/`offset` query params and slices `_replay_paths()` before building views; absent params preserve current behavior. A test covers pagination bounds (G-G-3).
- [ ] `update_manifest` (and the sibling `prune_manifest`/`rebuild_manifest`) write to a temp file and `os.replace` for atomicity; a crash mid-write cannot truncate the live MANIFEST (H-H-3). A test asserts the temp-then-replace path.
- [ ] No cross-worker shared cache is added (documented scale boundary, H-H-6); a comment marks the import-time loader construction as the scale boundary.
- [ ] `list_replays` catches `CorruptedFileError` per file, excludes the bad file from the listing, and logs a warning (not a silent drop), so one corrupted replay no longer 500s the whole picker (K-K-8 backend half). A test asserts that a directory containing one corrupted file still lists the healthy replays and logs the corruption.
- [ ] No behavior change to served DTO shapes; existing route tests pass unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `api/replay_loader.py` (the `cost_summary` double read at line 236, the
`_metadata_view` reads at line ~216, the LRU caches `_cached_load`/
`_cached_memories` at line ~209), `api/routes/replays.py` (the `GET /replays`
handler), and `scripts/_manifest_writer.py:314` (`update_manifest`). Derive cost
and outcome from one parsed entry list rather than two passes. For the cache key,
fold `path.stat().st_mtime_ns` into the key so an in-place rewrite is a cache
miss. For pagination, slice the path list before constructing any view so the
work is bounded. For atomicity, write the new MANIFEST to a sibling temp path and
`os.replace` it into place — `os.replace` is atomic on the same filesystem. Keep
the shared cross-worker cache out of scope; it belongs to the scale phase and
would pull in `api/main.py`. For the corrupted-file fix, find where
`list_replays` iterates files and wrap the per-file metadata build in a
try/except for `CorruptedFileError` (the type Task 4.16 added to `ReplayLog`):
skip the offending file, log a warning with its path, and continue — never let
one bad file abort the whole listing.

**Ready-to-paste prompt:** `agent_prompts/task-6-6-replay-loader-efficiency-pagination.md`

### Task 6.7 — Frontend replay performance: memoize the map render path and window the payload
**Branch:** `phase-6-frontend-replay-performance`
**Depends on:** none
**Section refs:** Audit K-K-1, K-K-2, G-G-1, G-G-5; DESIGN.md §11.4
**Complexity:** Medium

`MapView` has no memoization (`frontend/src/components/MapView.tsx:191`): on every
`currentTick` change `visibleBodies` re-scans every tick from 0 to `currentTick`,
and `roomsById`/`playerIndexById`/`colorById`/`ventEdges`/the fit transform are
rebuilt from scratch each render. Full playback of an N-tick replay is O(N²) tick
scans — ~500K at the 1000-tick default, ~50M at 10000 — the dominant frontend
bottleneck, and at 4× playback the scan re-runs roughly eight times a second
(audit K-K-2 = G-G-1). Separately, the entire `ReplayView` (every tick, every
meeting transcript, full LLM prompt/response text, failed_calls) is loaded in one
payload into the Zustand store (`frontend/src/store/replayStore.ts:106`); the
per-tick `getTick` endpoint exists but is never called, so the store grows
linearly with game length with no windowing (K-K-1 = G-G-5).

This task lands the performance substrate only — it must survive the Phase 7
redesign, so no visual/accessibility changes here. Memoize MapView's per-replay
invariants (the lookup Maps, color map, vent edges, fit transform) on
`currentReplay` identity, and replace the O(currentTick) body re-scan with a
per-tick cumulative body-state array computed once per replay (useMemo) and
indexed in O(1). Window the bulk payload: keep only the timeline + roster + map
in the store, drop raw prompt/response text from the bulk view, and lazy-fetch
meetings/memory on demand via the existing `getTick`/`getMeeting` endpoints
(fetch the LLM call body when an `LLMCallCard` is expanded). Backend G-G-1/G-G-5
are the same surface from the API side; this is the frontend half.

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/src/components/LLMCallCard.tsx

**Files NOT in scope:**
- frontend/src/components/ (other than MapView.tsx and LLMCallCard.tsx)
- frontend/src/types/api.ts (no DTO shape change; reuse existing types)
- frontend/src/index.css (no visual change; that is Phase 7)
- api/ (the backend half is Tasks 6.5/6.6)

**Definition of done:**
- [ ] MapView's per-replay invariants (`roomsById`, `playerIndexById`, `colorById`, `ventEdges`, fit transform) are memoized on `currentReplay` identity (useMemo), rebuilt only when the loaded replay changes, not every tick (K-K-2/G-G-1).
- [ ] Body discovery is O(1) per tick step: a per-tick cumulative body-state array is computed once per replay (useMemo) and indexed by `currentTick`, replacing the 0..currentTick re-scan (K-K-2/G-G-1).
- [ ] The bulk store payload is windowed: raw LLM prompt/response bodies are dropped from the bulk `ReplayView` held in the store; meetings/memory and LLM call bodies are lazy-fetched via the existing `getTick`/`getMeeting` endpoints, and an `LLMCallCard` fetches its body on expand (K-K-1/G-G-5).
- [ ] Playback correctness is unchanged: stepping, scrubbing, speed changes, and snap-to-meeting all render the same map state as before, verified against an existing sample replay.
- [ ] No visual restyle, no accessibility change, no DTO shape change — this is performance only (Phase 7 owns the redesign).
- [ ] `cd frontend && npm run tsc:check` passes (no new `any`, no `@ts-ignore`).
- [ ] `cd frontend && npm run build` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally (frontend checks included).

**Implementation hint:**

Read `frontend/src/components/MapView.tsx` (the per-render rebuilds and the
`visibleBodies` scan around line 191), `frontend/src/store/replayStore.ts:106`
(the single-payload load), `frontend/src/api/client.ts` (the existing `getTick`/
`getMeeting` methods, currently unused for windowing), and
`frontend/src/components/LLMCallCard.tsx`. Wrap the static lookups in `useMemo`
keyed on the loaded replay object identity. For bodies, precompute an array where
index `t` holds the set of discovered-body positions as of tick `t` — a single
forward pass per replay — then index it directly. For windowing, trim the store
shape to timeline + roster + map and fetch heavier payloads on demand; keep the
existing component props stable so the Phase 7 redesign can still swap
implementations file-by-file. Confirm there is no behavioral regression by
scrubbing a known sample replay before and after.

**Ready-to-paste prompt:** `agent_prompts/task-6-7-frontend-replay-performance.md`

### Task 6.8 — Correct README, AGENTS.md, and .env documentation drift
**Branch:** `phase-6-documentation-drift`
**Depends on:** none
**Section refs:** Audit F-F-1, F-F-2, F-F-3, F-F-5
**Complexity:** Small

Several in-repo documentation surfaces have drifted from HEAD (audit Class F).
README attributes "38% impostor win rate, $0.886 total spend" to the bundled
samples (`README.md:89`), but those samples were regenerated 2026-05-27 and now
tally 36% (18/50) and ~$0.91 (MANIFEST sum $0.9075); the 38%/$0.886 figures
describe the original 2026-05-26 closing eval, not the shipped artifacts, and
README's two cost sources disagree (F-F-1). README line 32 says "seven reports
… plus the closing" implying eight, but the glob matches six and the total is
seven (F-F-2). `.env.example:29`'s "API server (Phase 4 — not yet live)" is stale
since the spectator API is live (F-F-3). And `AGENTS.md:47` scopes
`mypy --strict` to engine/observation/agents only, while pyproject sets
`strict=true` globally and `check.sh` runs `mypy .` repo-wide, so an agent could
under-annotate new code (F-F-5).

This task is doc-only and edits only in-repo, agent-editable files. The
auto-memory note drift (F-F-4, the `/eval/tournament-report` route name) was
already corrected on 2026-05-30 and is out of scope (the memory store is outside
the repo). DESIGN.md drift is design-thread-owned and out of scope.

**Files in scope:**
- README.md
- AGENTS.md
- .env.example

**Files NOT in scope:**
- DESIGN.md (design-thread-owned)
- AGENT_IMPLEMENTATION.md
- docs/deployment.md (Task 6.1)
- replays/samples/MANIFEST.md (the canonical provenance record; cite it, do not edit it)
- the auto-memory store (outside the repo; F-F-4 already fixed)

**Definition of done:**
- [ ] `README.md:89` is restated to the actual bundled-sample aggregates — 36% impostor win (18/50) and ~$0.91 per the MANIFEST as the canonical provenance record — OR stops attributing the original 2026-05-26 eval's 38%/$0.886 figures to the regenerated samples; the two disagreeing cost sources are reconciled to MANIFEST (F-F-1).
- [ ] `README.md:32` arithmetic is fixed so "six reports … plus the closing" yields seven, consistent with lines 134/148 (F-F-2).
- [ ] `.env.example:29` drops "— not yet live"; optionally notes `AILIBI_API_PORT` is consumed only by docker-compose (F-F-3).
- [ ] `AGENTS.md:47` states that `mypy --strict` is enforced repo-wide (matching pyproject `strict=true` and `check.sh`'s `mypy .`) (F-F-5).
- [ ] No code or test file is modified; `git diff --name-only` shows only the three doc files.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `README.md` (lines 32, 89, 134, 148), `replays/samples/MANIFEST.md` (the
authoritative win-rate and cost provenance), `.env.example:29`, and
`AGENTS.md:47`. Treat the MANIFEST as the source of truth for sample aggregates;
do not re-derive numbers by re-running anything. Keep edits minimal and factual —
this is reconciliation, not rewriting.

**Ready-to-paste prompt:** `agent_prompts/task-6-8-documentation-drift.md`

### Task 6.9 — Stricter format-version read-time guarantee
**Branch:** `phase-6-format-version-read-time-guard`
**Depends on:** none
**Section refs:** Audit E-E-1; DESIGN.md §11.3
**Complexity:** Small

`TournamentReport.format_version` has a default of `CURRENT_FORMAT_VERSION`
(`eval/report_schema.py:241`), so a report JSON with the field entirely absent is
silently coerced to v1 and passes, despite the docstring's fail-loud claim — the
`@field_validator` raises only for an explicit out-of-range value (audit E-E-1).
Harmless while v1 is the only format, but it violates the project's
no-silent-fallback discipline: a report that lost its version marker should fail
loud, not default.

Make `format_version` required on the read/deserialization path — remove the
default, or add a `mode="before"` validator that rejects an input dict lacking
the key — so a missing version marker raises a clear error. Keep the existing
out-of-range rejection. This is a small fail-loud hardening; it touches only the
schema and its test.

**Files in scope:**
- eval/report_schema.py
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- api/ (Tasks 6.1/6.5/6.6)
- eval/ (other than report_schema.py)
- orchestrator/replay.py
- replays/samples/ (no fixture change; committed reports already carry the field)

**Definition of done:**
- [ ] Deserializing a report dict that lacks `format_version` raises a clear error (via a required field on the read path or a `mode="before"` validator), rather than silently defaulting to v1 (E-E-1).
- [ ] The existing out-of-range rejection (a value greater than `CURRENT_FORMAT_VERSION` raises) is preserved.
- [ ] In-process construction of a `TournamentReport` continues to work without callers having to pass `format_version` explicitly if the project prefers (e.g. the writer sets it), OR all construction sites are updated — the PR `## Decisions` block states which approach and confirms no writer path regressed.
- [ ] `tests/eval/test_report_schema.py` covers: a dict missing `format_version` is rejected; an out-of-range version is rejected; the current value `1` round-trips.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `eval/report_schema.py` (the `format_version` field and `@field_validator`
around line 241) and `tests/eval/test_report_schema.py`. The cleanest approach is
a `mode="before"` model validator that raises when the incoming dict omits
`format_version`, leaving the writer free to stamp the current version on
construction; confirm the tournament-report writer and the regression-suite
loader still produce a valid report. Match the existing validator's clear-error
style.

**Ready-to-paste prompt:** `agent_prompts/task-6-9-format-version-read-time-guard.md`

## Merge Criteria
- **DESIGN.md reconciled:** the design-thread DESIGN.md pass (Class A + H-1) lands before Phase 6 closes; the document describes HEAD.
- **Urgent item landed:** Task 6.1 binds the GM-view API to loopback by default.
- **Engine lane complete:** Tasks 6.2 → 6.3 → 6.4 merged in order, each with a single fixture regeneration; the close gate attributes each metric delta to one change.
- **Firewall extended:** Task 6.5's eval-surface leak snapshot is in place; the leak tests cover the `/eval/tournament-report` surface, not just `api.schemas`.
- **Performance cliffs removed:** Task 6.7 (frontend) and Task 6.6 (backend) land; full playback of a sample replay is no longer O(N²) and `GET /replays` paginates.
- **Docs honest:** Tasks 6.8 (README/AGENTS/.env) and 6.9 (format-version guard) merged.
- **All gates green:** `bash scripts/check.sh`, determinism tests, leak tests, frontend `tsc:check` + `vite build`.
- **Close gate — real-provider eval passes:** after Task 6.4 merges, one real-provider tournament (see "Phase 6 close: real-provider eval") shows zero leaks, a contradiction demonstrably shifting a vote, no cost blow-up, and records the post-Phase-6 balance baseline. This is the Phase 6 acceptance gate; it runs once, last.
- **Phase 7 boundary respected:** no new detector kinds, impostor vent/sabotage, accessibility rebuild, visual identity, or scaling work landed in Phase 6.
