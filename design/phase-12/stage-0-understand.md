# Phase 12 — Stage 0: UNDERSTAND

**Status:** Stage-0 deliverable (data-dictionary + renderable-surface map + existing-app teardown). This is the artifact that gates Stage 1 (DESIGN) and is the primary input to Claude Design.
**Date:** 2026-06-16
**Method:** 5 read-only analysis agents over `engine/` + map, `api/` + replay format, `frontend/` (21 components), `experiments/lab/` (rubric/deferred), and `observation/`+`meetings/`+`agents/memory/`+`orchestrator/replay.py` (the firewall/social-deduction/replay-emission model), reconciled against `DESIGN.md` and verified spot-checks. Citations are `file:symbol`/`file:line`.

> **What Phase 12 is.** A complete **rebuild** of the spectator replay viewer. The product is *"a multi-agent reasoning testbed whose game layer happens to look like Among Us"* (`DESIGN.md:31`); the UI exists to **make the observation firewall legible** — to show *what each agent knew vs ground truth*. Phase 12 = the game-rendering **CORE** (ML-independent). The ML-introspection layer is **deferred to Phase D** (see §7.C). Human-player / live-WebSocket remain out of scope (replay scrubbing only).

---

## 0.5 CORRECTIONS (post-Stage-1 adversarial critique, code-verified)

Stage 1's critique pressure-tested this doc against HEAD and overturned one load-bearing claim. Corrected facts (full corrected design in `stage-1-design.md` §0):

- **❗ "Per-tick belief frames recoverable for free in the loader re-walk" was WRONG.** Beliefs are **"timeless"** by an explicit Phase-4 decision (`api/schemas.py:424-433`; `tasks/phase-4.md:2258-2304`). Between meetings only Rules **1 & 4** fire (flat except isolated body/vent bumps); games have a **median of 2 meetings (max 4; 7 of 50 have 1)**; and the **Rule-2 contradiction lift the agent actually votes on is computed on a throwaway copy at vote time and never persisted** — so a reconstructed per-tick frame would be noise *and would disagree with the ballot*. → Belief-vs-truth is **per-MEETING** (use the existing `AgentMemoryView.beliefs`, 2–4 snapshots), not a per-tick sparkline.
- **Map fog ≠ beliefs (and fog is NOT free).** The per-tick `ObservationPacket` is discarded into a temp dir and exposed by **no endpoint**; visibility is graph/lights-dependent (`compute_visibility_for_player`). The Agent-perspective fog needs a **new, genuinely expensive per-tick visibility projection** built as **firewall-simulation code with its own UI leak test** (a naive same-room dim is both wrong and a leak).
- **§4.6 ballot verdict:** the `rendered_max` is template-time, transient, **not persisted** (only on failed calls); the gate compares persisted `ballot.confidence ≥ 0.6` on the plurality leader. → It's a **per-meeting** verdict from recorded ballots; drop `rendered_max`.
- **Kill self-channel needs no new field:** `KillEventView{killer_id,victim_id,room_id}` is **already in `TickView.events`**; `own_kill` is only needed for the Mind-inspector *memory line* (already in `rendered_memory_text`).
- **Served-set reality:** rubric is **9p2i-only**, but the API **default served set is 4p1i** (no rubric; **34/50 games have zero meetings**). → 9p2i is the target; rubric must be **per-set + staleness-guarded**; zero-meeting/empty states are first-class.

---

## 1. System framing (read first)

```
 headless game (CLI) ─► JSONL replay on disk ─► FastAPI loader (RE-EXECUTES engine) ─► typed DTOs ─► React+Pixi replay scrubber
   orchestrator/         replays/samples/*.jsonl   api/replay_loader.py                 api/schemas.py    frontend/
```

Five facts that shape every UI decision:

1. **Deterministic engine, replay-from-actions.** The engine is a pure `(state, actions) -> (state', events)` function (`DESIGN.md:288`). Replays store **only the action stream + a per-tick `state_hash`** — positions/state are *reconstructed* by re-running the engine (`api/replay_loader.py:448`, verifying hashes). The browser computes nothing today; **the loader is the precompute seam** (blind-spot #2's home).
2. **Two-tier agents → "thought" data lives only at meetings.** Tactical decisions are a rule-based FSM every tick (no LLM, no prompt records). Strategic decisions (reports, votes) call the LLM **only at meetings** (`DESIGN.md:27`). So per-tick data is *positional/action* state; rich reasoning (transcripts, ballots, contradictions, prompts) exists **only at meeting boundaries**.
3. **The observation firewall is the centerpiece.** Hidden state (roles, kill attribution, vent use, per-agent beliefs) never leaves the engine except through `ObservationService` (`DESIGN.md:25`, `§1.3`). The spectator is the **privileged** viewer ("spectator UI may peek", `DESIGN.md:98`) — it can render the firewalled fields side-by-side with what each agent believed. **No existing replay viewer does this; ours can. This is the killer feature.**
4. **Map has real geometry.** `canonical_1.yaml` gives all rooms explicit `(x,y)` + size → a **true floor-plan**, not auto-layout. The API already exposes these (`RoomView.position`/`size`), and the current `MapView` already fits them to canvas.
5. **No live mode.** Headless-only; the UI scrubs saved replays. The WebSocket broadcast layer in `DESIGN.md` is unbuilt and out of scope.

---

## 2. DATA DICTIONARY — every datum the sim emits, and where it lives

Visibility legend: **PUBLIC** (any observer) · **WITNESS-GATED** (engine visibility permits) · **SELF-ONLY** (privileged self channel) · **AGENT-LOCAL** (per-agent internal, not in any packet) · **SPECTATOR** (engine ground truth, never to agents) · **DERIVED** (computed, not stored).

### 2.1 Spatial / map — the floor-plan ground truth (`engine/maps/canonical_1.yaml`, `engine/world.py`)

- **10 rooms**, each with `(x,y)` grid coords + `(w,h)` size + `kind` (`hallway`/`task_room`/`meeting_room`/`utility`). Origin top-left. Layout: Cafeteria (hub/spawn/meeting/emergency) ↔ three hallways ↔ Admin / Engineering→Reactor / Engineering→Storage / MedBay→Labs.
- **11 undirected edges** (all `traversal_ticks:1`); hallways vs doorways (`EdgeView.is_door` flattens this).
- **6 vents** (REACTOR, STORAGE, ENGINEERING, ADMIN, MEDBAY, LABS) in a perimeter chain + cross-link; impostor-only.
- **12 map tasks** across rooms (`short`/`long`/`common`, durations 3–10 ticks, weights 1–2).
- **2 sabotages:** `lights` (visibility→same-room, repair@ADMIN, 90 ticks, **non-gating**) and `reactor` (repair@REACTOR/ENGINEERING, **6 ticks, `gates_tasks:true`** — halts all `do_task`, fires `IMPOSTOR_SABOTAGE` at 0).
- Special: spawn/meeting/emergency-button all = CAFETERIA.
- **Coords reach the UI via the API** (`MapLayoutView`→`RoomView{position,size}`, `VentView`, `EdgeView`). Only the *agent-facing* `PublicMapView` omits coords (correct — agents path by graph). **No floor-plan gap on the spectator path.**

### 2.2 World / per-tick state (`engine/world.py`, `engine/entities.py`)

`WorldState`: `tick`, `phase`(PLAY/MEETING/GAME_OVER), `map`, `players`, `bodies`, `tasks`, `sabotage`, `cooldowns`(impostor), `emergency_uses`, `rng_state`, `seed`.
- `PlayerState`: `id`, `role`✦, `alive`, `room`, `position`(float xy, SPECTATOR-only render data), `last_action`, `in_vent`✦.
- `BodyState`: `id`(`body-{victim}-{tick}`), `player_id`, `room`, `position`, `killed_by`✦SPECTATOR, `discovered_by`(None→reporter).
- `TaskState`: per-player **instance** keyed `"{owner}:{map_task_id}"`; `owner`✦, `map_task_id`(agent-facing), `room`, `progress`, `required_ticks`, `completed`. Dead crewmates' *incomplete* instances are removed (affects the task denominator).
- `SabotageState`: `kind`, `remaining_ticks`✦, `affected_rooms`, `active`, `repair_progress`✦.

✦ = firewalled (SPECTATOR or SELF-ONLY) — see §2.4 firewall map.

### 2.3 Actions (9) & engine events (14)

- **Actions** (`engine/actions.py` / agent-side `observation/action_intent.py`): `move`, `do_task`, `kill`, `vent`, `report`, `emergency`, `sabotage`, `repair_sabotage`, `wait`. (Impostor `do_task` is always engine-rejected — a cosmetic "blend"; see §2.7.)
- **Events** (`engine/events.py`): `ActionRejected`, `Moved`, `TaskProgressed`, `TaskCompleted`, `Killed`(+`witnesses`), `VentEntered`/`VentExited`(+source/dest witness sets), `SabotageStarted`, `SabotageRepairProgressed`, `SabotageRepaired`, `MeetingTriggered`(`trigger:report|emergency`, `body_id`), `Waited`, `GameOver`(`winner`,`reason`), `TickAdvanced`.
- **The engine emits no meeting/vote events** — meeting/ballot/ejection data is all orchestrator-layer (§2.5). And vent/repair events exist in the engine stream but are **not** carried into the per-tick DTO (only an `is_venting` bool survives — a key gap, §4).

### 2.4 Per-agent observation — the firewall (`observation/packet.py`, `observation/service.py`)

`ObservationPacket`: `tick`, `agent_id`, `self_state`, `visible_players`, `visible_bodies`, `audible_events`, `global_state`, `cooldown`(impostor SELF-ONLY).

| Schema | Fields | Phase-11 / firewall notes |
|---|---|---|
| `SelfView` | `room`, `role`✦, `pending_task_id`✦, `fellow_impostor_ids`✦(impostor), `in_vent`✦, `own_kill`✦ | **All 5 Phase-11 fields confirmed wired.** `in_vent` (11.1), `own_kill`→`OwnKillView{victim_id,room}` (11.3) populated only for the killer that tick, never mirrored to others (would fail `eval/leak_test.py`). |
| `PlayerView` | `id`, `room`, `action`(`"kill"`/`"vent"`/None) | Witness-gated; **role never present.** |
| `BodyView` | `id`, `room`, `victim_id` | `killed_by` excluded (firewalled). |
| `AudibleEvent` | `kind`(`vent_use_heard`/`sabotage_alarm`), `room` | **`heard_vent_use` confirmed** — carries room only, **no actor** (you hear a vent, not who). |
| `GlobalView` | `tasks_completed`, `tasks_total`, `task_completion_percent`, `sabotage_active`, `sabotage_kind`, `sabotage_repair_rooms`, `sabotage_is_gating` | **`sabotage_repair_rooms`/`sabotage_is_gating` confirmed** (11.5), role-blind. |

**FIREWALL MAP (the legibility surface).** Self/spectator-only data the UI can reveal side-by-side with belief: hidden `role`; impostor `cooldown`; `own_kill` (kill attribution / self-channel); `fellow_impostor_ids`; `in_vent`; impostor `pending_task_id` (a fabricated cover task); per-agent beliefs/memory (AGENT-LOCAL, §2.6); `BodyState.killed_by`; ballots (post-hoc only, never shown to agents mid-meeting).

### 2.5 Meeting / vote / contradiction (`meetings/schemas.py`, `transcript.py`, `voting.py`, `manager.py`)

A meeting = one ordered `transcript.turns` (opening → reactive reply chain → terminal opt-ins) + a vote. The chain is a **pure function of recorded turns** (`walk_chain`), so replay reconstructs it with no LLM.

- `MeetingTurn`: `turn_id`(`{meeting}:turn-{i}`), `turn_index`, `speaker`, `turn_kind`(opening/reply/opt_in), `reply_to`, `observations[]`, `claims[]`, `free_text`. (LLM authors only `observations`/`claims`/`free_text`; identity fields are system-authored.)
  - `ObservationClaim` = `saw_player`{tick,subject,room,co_present} / `completed_task` / `found_body`.
  - `Claim` = `alibi`{subject,from_tick,to_tick,room,evidence} / `accusation`{against,confidence,reason} / `corroboration`{supports,on_tick,reason}.
- `VoteBallot`: `voter`, `target`(PlayerId|`SKIP`), `confidence`, `primary_reason_id`(→turn), `considered_alternatives[]`, `rationale_text`. **Post-hoc only — never shown to agents during the vote.**
- `ContradictionRef`: `contradiction_id`, `kind`(`alibi_conflict`/`alibi_vs_sighting`), `event_a_id`/`event_b_id`(→turn claims/obs), `subjects[]`, `description`. **No weak/strong field** — weakness is a **string marker** in `description` (`"[weak signal: …"`, `is_weak_contradiction()` = substring test). Re-derivable from the transcript.
- `MeetingResult`: `meeting_id`, `triggered_by`, `trigger_tick`, `outcome`(EJECTED/SKIPPED), `ejected_player_id`, `ballots[]`, `contradictions[]`, `transcript`.
- **Tally / resolution** (`voting.py`): SKIP is a first-class target; SKIP plurality → SKIPPED; any tie between non-skip → SKIPPED (no `TIE` outcome); strict plurality **AND** ≥1 leader ballot with `confidence ≥ 0.6` → EJECTED (the **§4.6 gate**, inclusive at 0.6); plurality without a confident ballot → SKIPPED.
- **Teammate (impostor) firewall**, applied every turn/ballot: drop accusations against a teammate, never pass the floor to a teammate, coerce a teammate-targeting ballot to SKIP, redirect under-gate must-vote ballots to the argmax eligible candidate, strip teammate-incriminating sightings. Each rewrite leaves a **prefix marker** in `rationale_text` (`INVALID_VOTE_TARGET_MARKER`, `TEAMMATE_VOTE_TARGET_MARKER`, `BALLOT_TARGET_REDIRECT_MARKER`, `VOTE_PARSE_DEFAULT_MARKER`, …) — string-only "why this got rewritten" signals.
- **No structured trigger-kind at the meetings layer** — emergency vs report is a substring match on the trigger description (`"called an emergency meeting"`); the *loader* bridges this into `MeetingView.trigger_kind`.

### 2.6 Belief / suspicion — the belief-matrix data (`agents/memory/beliefs.py`)

**AGENT-LOCAL.** Each agent owns one `BeliefState{dict[PlayerId, PlayerBelief]}`; `PlayerBelief` = `trust`,`suspicion`∈[0,1], `alibis[]`, `inconsistencies[]`. **Never in any packet, never persisted to the replay** (§3.1).

**§6.3 rules — CORRECTION to stale docs (incl. MEMORY.md): Rules 2, 3, 5 are all LIVE** (Phases 9.7–10.15), not deferred:

| Rule | Effect | Status |
|---|---|---|
| 1 near-body proximity | +0.2 (window 3) | LIVE |
| 2 contradiction | +0.3 strong / +0.08 weak, per-meeting cap 0.3 | **LIVE** |
| 3 corroboration | **−0.05 (verbal)** — *not* DESIGN's −0.4 "verified shared task" (unimplemented) | **LIVE (re-scoped)** |
| 4 venting | +0.5 | LIVE |
| 5 time-decay | 0.25 per **meeting round** (never per gameplay tick) | **LIVE** |
| (extra) accusation +0.05, single-witness inform +0.05, two-witness bar | — | LIVE |

**Carry vs transient:** accusation bump, Rule 3, Rule 5 land on the **persistent** stored state (carry across meetings); Rule 2's contradiction lift is applied to a **copy at vote time only** (transient, never persisted).

### 2.7 Rendered memory / prompt — the prompt-inspector content (`agents/memory/store.py::render_for_prompt`)

A token-budgeted Markdown string = exactly what the LLM sees:
```
## Your role: {role}
## Tasks completed (global): {c}/{t}
## Recent observations (most salient first):   ← ELASTIC (salience-dropped to fit budget 1500)
   found-body 100 · own-kill 96 ("You (IMPOSTOR) killed X in R") · witnessed-kill 95 · witnessed-vent 85 ·
   heard-vent 75 · heard-sabotage 65 · saw-player-active 55 · saw-player 50 · completed-task 30 · cooldown 10
## Your current beliefs:                        ← NON-ELASTIC (always kept)
## Open contradictions:                         ← NON-ELASTIC
```
- Firewall guards inside the renderer: own-victim "discovered body" line suppressed for the killer (shown once as the own-kill line); self-sightings dropped; impostor teammate sightings at kill room/tick dropped; completion inference role-gated to crewmates (impostor pretend-tasks never mint fake "completed").
- **`EpisodicEvent` types:** `self_state`, `own_kill`, `cooldown_status`, `saw_player`, `saw_body`, `heard_vent_use`, `heard_sabotage_alarm`, `global_status`. (No `EnteredRoom`/`CompletedTask` events — inferred.)
- `WorkingMemory` (goal/path/last_seen) is volatile, rebuilt each tick, not persisted.

### 2.8 Strategic outputs & prompt templates (`agents/strategic/`)

`output_schemas.py` is a pure re-export — the only structured LLM outputs are `MeetingTurn` and `VoteBallot` (no separate reasoning schema; chain-of-thought lives in `free_text`/`rationale_text`). Four jinja templates (the "prompt inspector" raw source): `crewmate_report.j2`(v7), `impostor_report.j2`(v5), `accusation_round.j2`(v8), `vote_ballot.j2`(v5). Versions are hand-maintained in `orchestrator/game.py::DEFAULT_PROMPT_VERSIONS` (note inconsistent delimiters `.`/`_`/`/`) and recorded per meeting.

### 2.9 Win conditions (`engine/win_conditions.py`, priority order)

`IMPOSTOR_PARITY` (impostors ≥ crew) → `IMPOSTOR_SABOTAGE` (active sabotage timer 0; ~0/50 in practice) → `CREWMATE_EJECT` (all impostors gone) → `CREWMATE_TASKS` (all live instances done). `GameOver` carries `winner`+`reason`.

### 2.10 Rubric / interestingness (`experiments/lab/rubric_score.py`, `results-rubric-score.json`)

Per-game **interestingness score 0–100, decoupled from who won**: `100 × (0.35·R1_decisive + 0.25·R2_deception + 0.20·R3_arcs + 0.20·R7_legible)`. `results-rubric-score.json → interestingness.per_game[]` is **already sorted best-first**, one entry per seed: `{seed, reason, n_meetings, win_shape, ejected_impostors, accused_impostors, survived_accused, r1_decisive, r2_deception, r3_arcs, r7_legible, score}` (top: seed 5 = 80; mean 45.1). **Offline-only — not in any API/DTO.** Join to a playable replay via `seed → game_id = headless-seed-{N}`. (The audit pipeline regenerates only the *aggregate* scorecard, not per-game — so per-game scores are as fresh as the last manual `rubric_score.py` run.)

---

## 3. Persistence & API surface — where each datum lives on the wire

### 3.1 On-disk: **two** artifacts (one committed, one ephemeral)

- **Replay JSONL** (`orchestrator/replay.py`), one file per game, 4 record `kind`s:
  - `tick`: `game_id`, `tick`, `actions[]` (engine actions, **not** positions), `state_hash`.
  - `meeting`: `transcript`, `ballots[]`, `contradictions[]`, **`llm_calls[]`** (`LLMCallRecord{call_kind, model, prompt, response_text, input/output_tokens, cost_usd, agent_id}` — **full rendered prompt + response PERSISTED**), `prompt_versions`, `outcome`, `ejected_player_id`, hashes.
  - `game_over`: `winner`, `reason`. · `failed_call`: model/cost/error (+`rendered_vote_max`).
  - **Intentionally UNVERSIONED** (guarded by `state_hash` + `roster.json`).
- **`ObservationAuditLog`** (`observation/audit.py`) — every per-agent `ObservationPacket` per tick as JSONL = the authoritative "what each agent knew" feed. **NOT committed with any sample** (verified: `replays/samples/**` has only `replay-seed-*.jsonl`, `roster.json`, `MANIFEST.md`, `tournament-eval-report.json`). It's **optional** (`game.py audit_log_path` default off; `run_tournament.py` never sets it) and the **loader regenerates it into a throwaway temp dir** during its `collect_memory` re-walk (`replay_loader.py:505`), then discards it.
- **Sidecars:** `roster.json`{num_players,num_impostors,tasks_per_crewmate}; `MANIFEST.md`; `tournament-eval-report.json` (**versioned `format_version=2`**, fail-loud, no migration; ~875 kB). Sets: `replays/samples/`=flat 4p/1i (no roster); `replays/samples/9p2i/`=canonical. **One set served per process** (`AILIBI_REPLAY_DIR`).

### 3.2 The loader re-executes the engine (`api/replay_loader.py`)

Re-seed → for each tick `advance_tick` and verify `state_hash` (raises `ReplayStateMismatchError` on drift) → apply meeting results → optionally (`collect_memory=True`, meeting-memory endpoint) re-run perception to reconstruct agent memory **at meeting boundaries only**. LRU-cached (mtime-keyed). **The browser computes nothing.**

### 3.3 Endpoints (9, all read-only GET) & DTO contract

`/`, `/health`, `/replays`(±limit/offset), `/replays/{id}`→`ReplayView`, `/replays/{id}/ticks/{t}`(unused by UI), `/replays/{id}/meetings/{mid}`→`MeetingView`, `/replays/{id}/meetings/{mid}/memory/{aid}`→`AgentMemoryView`, `/eval/cost-summary`, `/eval/tournament-report`. CORS closed by default. DTOs in `api/schemas.py` are **hand-mirrored** in `frontend/src/types/api.ts`.

**Contract is unversioned and drifting — regenerate, don't hand-mirror:**
- `SuspicionGraphView`/`SuspicionEntryView`: defined both sides, **no route** (dead, but a tempting per-tick hook).
- `TournamentEvalReport` (TS) is **missing `conversion` + `gate_metrics`** that the server sends → untyped runtime data.
- `GameReport`/`TournamentReport` (TS) are deliberate stubs (omit `roles`, kill-gift aggregates, meetings, cost).
- `FailedCallEvalView` has no TS mirror. `tick=-1` synthetic "Start" frame is loader-injected (the off-by-one source, §5.2). `prompt_template_id` is a load-time heuristic, not stored.

### 3.4 Precomputed vs on-demand

Everything is server-side: map geometry (built once, shared), roster+colors, per-tick agent states/actions/sabotage/task-progress, meeting trigger-kind, prompt-template-id, costs, belief confidence (`min(1, |suspicion−0.5|·2)`), and (expensive, on the memory endpoint) full perception re-walk for meeting-boundary memory. **Nothing is precomputed per-tick for beliefs/observations** — but it *can* be, in the same re-walk (§6.1).

---

## 4. RENDERABLE-SURFACE MAP — datum → what shows it today (and the gap)

Status: ✅ rendered · ◑ partial/buried · ⊘ data arrives but dropped · ✖ not in DTO. This table is the heart of the rebuild scope.

| Surface / datum | In DTO? | Rendered by today | Status |
|---|---|---|---|
| Floor-plan rooms/edges/vents | ✅ `MapLayoutView` | `MapView`→`RoomRect`/`VentEdge` | ✅ |
| Agent positions over ticks | ✅ `AgentTickStateView` | `AgentToken` (1 tween, single-step only) | ✅ |
| Bodies | ✅ | `BodyMarker` | ✅ |
| Sabotage — **lights** | ✅ | `SabotageOverlay` | ◑ (lights only) |
| Sabotage — **reactor** (gating) + repair race / countdown | ✅ kind; ✖ repair/countdown | nothing for reactor; no repair UI | ⊘/✖ |
| Vent **escapes** (the Phase-11 deception lever) | ✖ (only `is_venting` bool; no enter/exit event) | token just vanishes/reappears | ✖ |
| Meeting transcript / chain | ✅ `MeetingView` | `MeetingView`/`TurnCard` | ✅ |
| Ballots | ✅ | `BallotCard` (client tally) | ◑ (no `considered_alternatives`/`primary_reason_id`/correctness) |
| **Per-ballot §4.6 verdict** (was-this-correct, rendered gate value) | ✖ | — | ✖ |
| Contradictions | ✅ `ContradictionView` | `ContradictionBadge` | ◑ |
| **Weak/strong contradiction class** | ✖ (string marker in `description`) | — | ✖ |
| Ballot-rewrite markers (teammate/parse/redirect) | ◑ (embedded in `rationale_text`) | shown raw if at all | ⊘ |
| Belief matrix (who suspects whom) | ✅ at **meeting boundaries** | `BeliefMatrix`/`BeliefCell` | ◑ |
| **Belief vs ground-truth** (suspicion overlaid on real role) | role ✅, overlay ✖ | — | ✖ **(biggest legibility miss)** |
| **Per-tick belief evolution** | ✖ (meeting-boundary only) | — | ✖ (recoverable in loader re-walk, §6.1) |
| Rendered memory / prompt inspector | ✅ `AgentMemoryView.rendered_memory_text` | `MemoryPanel` (buried 3 clicks deep) | ◑ |
| LLM call traces (prompt/response/cost) | ✅ `LLMCallView` | `LLMCallCard` (lazy, buried) | ◑ |
| **Impostor kill self-channel (`own_kill`)** | ✖ (in engine + rendered memory; not a DTO field) | — | ✖ |
| Crew task-clock progress (the real balance lever) | ✅ `tasks_*_total` | — | ⊘ |
| Win outcome + `winner_reason` | ✅ | `winner` in picker only | ⊘ |
| Per-agent `current_action` (IDLE/MOVING/KILL/…) | ✅ | token is a bare dot | ⊘ |
| `failed_calls` (LLM errors) | ✅ loaded | nothing | ⊘ |
| **Rubric interestingness score / highlights reel** | ✖ (offline JSON) | — | ✖ |
| Dashboard metrics | ✅ `tournament-report` | `TournamentDashboard` | ◑ (no honesty/low-power caveats; `conversion`/`gate_metrics` untyped) |
| Suspicion graph over time | ✖ (dead `SuspicionGraphView`) | — | ✖ |

**Pattern:** the gaps cluster into (a) **not in the DTO** (own_kill, vent events, weak/strong, §4.6 verdict, rubric, per-tick beliefs) → new view-model surfaces; and (b) **arrives but dropped** (reactor, task-clock, failed_calls, current_action, outcome) → pure front-end work. The deep inspectors that exist are buried.

---

## 5. EXISTING-APP TEARDOWN — the rebuild target (`frontend/`, ~4.2k LOC)

### 5.1 Component tree (21 components; one WebGL canvas)
```
App (tabs: replay | dashboard) [DOM]
├ replay: ReplayPicker · MapView[DOM→one Pixi <Application> 800×600]
│         └ RoomRect* · VentEdge* · BodyMarker* · AgentToken* · SabotageOverlay   [all PIXI]
│         · MeetingPill
│  (fixed-position siblings, hand-tuned z 50→65, gated on selectedMeetingId)
│  ├ MeetingView → TurnCard*(→ContradictionBadge) · BallotCard* · ContradictionsSection · MetadataFooter
│  ├ BeliefMatrix → BeliefCell*(N²)
│  ├ ThoughtStream → AgentSelector · MemoryPanel(→BeliefRow) · LLMCallCard*
│  └ ReplayControls  (the playback engine)
└ dashboard: TournamentDashboard → StatTile* · CalibrationCurve(inline SVG)
```

### 5.2 Playback / time model — "the backbone" (carries known traps)
- Whole game fetched in **one payload** and held in `currentReplay`; **`windowReplay` strips `prompt_text`/`response_text`** (lazy-refetched per meeting). No per-tick fetch (the `/ticks/{t}` endpoint is **dead**).
- **`currentTick` is an array index, not the engine tick** — a synthetic `tick=-1` Start frame makes them differ by one; consumers re-derive `ticks[i].tick` independently in **3 places** (recurring off-by-one).
- Auto-advance is a `setInterval` **inside `ReplayControls`** (not the store), reading fresh state to avoid drift. One tween (`AgentToken`, `useTick` lerp 250 ms, **single-step same-replay only**); scrubs/snaps are instant.
- Belief matrix is **meeting-boundary snapshots**, fanned out one fetch per agent, **not tick-synced**.

### 5.3 Stores (Zustand)
`replayStore` (the backbone): list/current/tick/play/speed/selectedMeeting/selectedAgent + `memoryCache`/`meetingCache` (lazy). **Careful, correct async-ordering guards** (monotonic request tokens + post-await game-id checks) — *worth porting*. `tournamentStore`: one report fetch; deliberately isolated from `replayStore`.

### 5.4 Rendering tech
PixiJS v8 via `@pixi/react` v8 `extend()` idiom (`<pixiGraphics>`/`<pixiText>`); **imperative `draw=(g)=>{…}` redraw per render**, no sprites/textures/assets. Clean DOM-vs-canvas split (canvas = spatial map only; everything else DOM).

### 5.5 Styling — **the #1 rebuild target** (currently bare)
`index.css` is **5 lines** (`@import "tailwindcss"` + `color-scheme: dark`). Tailwind v4 utilities inline, **zero design tokens**, **two inconsistent palettes** (slate vs neutral), magic hex/size constants scattered through the Pixi layer, brittle hand-tuned z-index + responsive-gutter math. Re-skinning = a 21-file edit. One real constraint to preserve: **outcome colors are intentionally role-neutral** (coloring EJECTED green/red would leak whether the ejected player was the impostor).

### 5.6 Deps / build
React 19.2.6 · pixi.js 8.18.1 · @pixi/react 8.0.5 · zustand 5.0.13 · Vite 8 (rolldown, SWC) · TS 5.9.3 · Tailwind 4. **Bundle = single ~859 kB chunk** (~72% over the 500 kB default) — Pixi eager + **zero code-splitting / no `React.lazy`**. **CI never builds the frontend** (only Python `check.sh`), so this is invisible.

### 5.7 Keep vs rebuild
- **KEEP/port:** the store's async-ordering guards + payload windowing + per-replay memoization; the DOM/canvas split; `types/api.ts` as the contract seed; the role-neutral-color constraint.
- **REBUILD:** design system (tokens/Storybook/`frontend/CLAUDE.md`); lift playback into a store/hook + a single derived tick-number selector; code-split (peel Pixi, lazy the dashboard); split `ContradictionBadge.tsx`'s smuggled shared utils into proper `ui/`+`lib/`; surface the dropped/buried legibility data front-of-house.

---

## 6. BLIND-SPOTS RECONCILED (kickoff's 6 + new ones found)

**B1 — Legibility (killer feature).** All the firewall data exists (§2.4). **Key resolution:** per-tick belief-vs-truth is a *new view-model surface*, but it's **recoverable for free in the loader's existing deterministic re-walk** (the loader already replays every tick + can replay the belief rules / emit packets), precomputed server-side and cached — **no new persisted file, no replay-format change.** `own_kill` is in the engine + rendered memory but needs a DTO field. Memory/prompt/LLM inspectors exist but must come front-of-house.

**B2 — Versioned view-model + precompute.** Today: unversioned DTOs, hand-mirrored TS, drift, dead schemas. **Introduce a versioned view-model contract and generate TS from Pydantic** (kill hand-mirroring). Precompute into the view-model: per-tick beliefs, weak/strong class, parsed rewrite markers, §4.6 verdicts, rubric score, task-clock.

**B3 — Playback/time backbone.** Fix the index-vs-tick off-by-one with one derived selector; lift the interval into the store/hook; keep windowing + lazy bodies; consider precomputed frames only if perf needs it (payloads are modest — belief data is KB-scale, not tick-multiplied).

**B4 — Rubric-driven highlights.** `interestingness.per_game[]` is reel-ready (sorted). Decide: read `results-rubric-score.json` as a static asset, add a `/eval/rubric` endpoint, or fold per-game scores into the tournament report. Join via `seed`.

**B5 — First-run legibility.** A guided/annotated mode for a complex hidden-info sim (new; Stage-1 design).

**B6 — Accessibility + responsive** (new tokens/components make this tractable).

**New blind-spots surfaced by Stage 0:**
- **Two-artifact split** — the observation audit log isn't persisted; **decide the per-tick legibility data source** (recommend: precompute in the loader re-walk, B1).
- **String-marker facts** — weak/strong class and ballot-rewrite reasons live as substrings; **parse them into structured view-model fields** or the UI mis-renders.
- **Contract drift + dead schemas** — regenerate the contract; add a frontend build + typecheck (and ideally a Playwright visual check) to CI.
- **No structured meeting-trigger kind** at the meetings layer (loader bridges it — keep that).
- **Impostor pretend-task fiction** — the impostor's `pending_task_id`/"tasks" are fabricated cover; **mark as cover in the UI, never as real progress.**

---

## 7. Open questions for Stage 1 (owner / design decisions)

A. **Art direction — vector vs raster.** Real room coords support a clean **vector top-down floor-plan**, which keeps the whole asset pipeline inside Claude (SVG/Pixi Graphics, no external image model). Raster/illustrated needs a separate image model. *(Lean vector unless the art bar demands raster.)*

B. **Per-tick legibility data source** — (a) precompute beliefs/packets in the loader re-walk **[recommended]**, (b) persist the observation audit log alongside replays, or (c) keep meeting-boundary-only and forgo the per-tick scrubber.

C. **View-model contract** — introduce versioning + **codegen TS from Pydantic**? (Strongly implied.) And where does **rubric scoring** live (static asset / endpoint / fold into report)?

D. **Scope confirmation** — spectator replay viewer only (human-player + live WebSocket stay deferred)? Confirm.

E. **Phase-D (ML) forward-compat — defer building, don't block.** Leave the view-model open to: per-tick/per-decision policy action-distributions, a per-meeting suspicion-rank vector, and a per-game fitness scalar + generation id. (Source: `experiments/lab/ml-spike-charter.md`, `report-ml-spike.md`.)

---

## 8. Provenance

Synthesized from 5 read-only agents (engine; api/replay; frontend; rubric/deferred; observation/meeting/belief/replay) + `DESIGN.md` + verification of the observation-audit-log persistence path. Stale-doc corrections recorded inline: **belief Rules 2/3/5 are LIVE** (not deferred; Rule 3 = −0.05 verbal corroboration); **canonical map has 10 rooms** (DESIGN.md's "6 rooms" is stale). Next: **Stage 1 — DESIGN** (IA → art direction → design system/tokens → blind-spot critique + analogous-product survey), gated on this artifact.
