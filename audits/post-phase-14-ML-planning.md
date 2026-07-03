# Post-Phase-14 planning — machine-learned tactical play between meetings

**Date:** 2026-07-03
**Author task:** map everything needed to implement ML-driven intelligence (NN / RL / NEAT / ES / …)
into the agents' **tactical** layer (movement, task routing, witness avoidance, kill timing, cross-round
strategy) — the deterministic play **between** meetings. The meeting/LLM layer is out of scope and stays.
**Status:** PLANNING DOCUMENT. Read-only with respect to source; the only repo output is this file.
**Baseline:** Phase 14 is closed on **baseline 2** — `replays/samples/9p2i` (50 games) + `replays/samples/4p1i`
(50 games), recorded on `Qwen/Qwen3-32B` (Featherless, $0), prompt set `qwen3_32b.v4`, MANIFEST
`git_sha a6e8783`, refreshed 2026-07-03, all five substrate levers unconditionally ON
(`audits/audit-phase-14-close.md`).

## Evidence discipline

Every claim below is labelled:

- **[VERIFIED]** — confirmed against the code (with `file:line`) or against the recorded seeds (with
  seed/tick evidence). Some are additionally marked **[V-ran]** where a probe was re-executed on current HEAD.
- **[INFERRED]** — a reasoned consequence of verified facts, not directly observed.
- **[PROPOSED]** — a design suggestion for the ML build; nothing in the repo implements it today.
- **[OPEN]** — something asked about that does not exist, or could not be confirmed.

Where a prior artifact's number is superseded by the committed bytes, it is flagged **[STALE]**.

---

## 0. TL;DR and the one recommended path

**The substrate is genuinely ML-ready and this is explicitly on the design roadmap** — [VERIFIED] DESIGN.md:940
already rosters *"Reinforcement learning for tactical policies. The strategic LLM stays put; the FSM is
replaced with a small neural policy trained against scripted opponents."* A prior throwaway ML feasibility
spike (`experiments/lab/ml_spike/`, `ml-spike-charter.md`, `report-ml-spike.md`) proved the plumbing: a
learned policy injects through the existing `agent_factory` seam with **zero engine edits**, the engine is
byte-deterministic given recorded actions, and $0 CPU self-play runs at ~8–25 games/s.

**But the one number the spike's "GO" rested on has REGRESSED on the current baseline.** [V-ran] The spike's
linchpin — an LLM-free physical "suspicion-rank" surrogate that would let you train the impostor offline with
no LLM in the loop — was reported at top-1 64% / top-2 82%; re-run against the **currently committed**
baseline-2 corpus it reproduces at **top-1 26% / top-2 43%** (≈ base rate). The corpus was re-recorded after
the spike (meetings flipped from 39-eject/75-skip to 118-eject/24-skip; ejections became more voice/testimony
driven — matching the close audit's rising zero-flag mis-eject channel). **So the cheap-offline-fitness thesis
is no longer established and must be re-validated before it is relied on** (§8, §10-S3).

**Recommended path — harness-first, then a conservative learned policy, then bounded co-evolution:**

1. **Build the reusable evaluation harness first** — it is algorithm-agnostic and, critically, *does not exist
   yet as code*: the phase-14 "validity gate" and "R-gate" live only as audit prose ([VERIFIED] §8). This is
   the acceptance test every later stage runs against.
2. **Start with a learned utility scorer over the FSM's own legal options** (not a from-scratch policy net) —
   trivially warm-started, determinism-friendly, and structurally bounded so it cannot invent degenerate or
   un-watchable exploits (§9 Option 1).
3. **Train it with ES** (not PPO) — the reward is sparse/non-differentiable, rollouts are cheap and CPU-parallel,
   the net is tiny, and the repo has no torch/numpy dependency to justify PPO's machinery yet (§9 Option 2).
4. **Gate every champion on watchability** (the D1–D4 geomean referee + validity meeting-rate bar), because
   the deepest risk here is not a weak learner — it is a *strong* one: a perfect-stealth impostor starves the
   meetings of testimony and un-makes the social game (§12).
5. **Attempt co-evolution only last**, with the literature's stabilizers (Hall-of-Fame, PFSP, reduced
   virulence), because the naive 2-population setup provably collapses here ([V-ran] FO-2; §9, §12).

Full staged plan in §10; open questions for the owner in §13.

---

## 1. Scope and method

**What was verified.** The engine (`engine/`), the tactical policies (`agents/tactical/`), the observation
firewall (`observation/`), memory/beliefs (`agents/memory/`), the orchestrator + replay/provenance
(`orchestrator/`, `api/replay_loader.py`), the meeting handoff + LLM cost layer (`meetings/`, `llm/`), the eval
harness (`eval/`, `scripts/`), the rubric/interestingness tooling (`experiments/lab/rubric*`), and the prior ML
spike (`experiments/lab/ml_spike/`). Throughput was measured on this host; six spike probes were re-run on
current HEAD; five 9p2i seeds + two 4p1i seeds were read end-to-end with a scratch pretty-printer, and the
50-seed aggregate was recomputed by re-seeding + replaying through the real engine.

**Host caveat.** All timings are on a **4-core** container. They establish order-of-magnitude feasibility,
not production throughput.

---

## 2. Mechanics inventory — implemented vs design-only

The core principles (kills, tasks, movement, meetings, and the vent/sabotage concept space) are design intent.
Here is what is actually **built** today, because the prompt is right not to trust prior claims — DESIGN.md's
prose is stale on sabotage.

| Mechanic | Status | Evidence |
|---|---|---|
| **9 engine actions**: `move, do_task, kill, vent, report, emergency, sabotage, repair_sabotage, wait` | [VERIFIED] implemented | `engine/actions.py:127-138` (discriminated union); mirrored engine-free as `ActionIntent` `observation/action_intent.py:114-125` |
| **Kill**: impostor-only, target must be crew, same room, cooldown 0 (seeded to 4) | [VERIFIED] implemented | `engine/rules.py:56-99`; cooldown `engine/maps/canonical_1.yaml:34`; no tick-1 kill (`seeder.py:107-112`) |
| **Vents**: impostor-only, 6-vent Hamiltonian ring, explicit enter/exit, emits `vent_use_heard` | [VERIFIED] implemented **and used by the impostor policy** | `engine/rules.py:102-179`; `canonical_1.yaml:229-271`; policy vents post-kill `impostor_policy.py:1011-1104` (the −91% catchability lever) |
| **Sabotage `lights`** (visibility → same-room-only, duration 90) | [VERIFIED] implemented | `canonical_1.yaml:379-388`; overrides vision symmetrically `visibility.py:25-34` |
| **Sabotage `reactor`** (task-gating, duration 6, `gates_tasks:true`) + crew repair | [VERIFIED] implemented — **DESIGN.md prose is STALE** | map `canonical_1.yaml` (reactor def); impostor fires it at ≥6/7 completion `impostor_policy.py:340-352`; crew repairs gating sabotage `crewmate_policy.py:396-402`; win path `win_conditions.py:30-35`. DESIGN.md:759 ("lights only … task counter still progresses") predates it |
| **Sabotage as a WIN lever** | [VERIFIED] implemented but **tactically dead** | 0 IMPOSTOR_SABOTAGE wins across 100 seeds ([V-ran] §4); FO-7 finds it dominated/timer-gated |
| **Meetings**: body-report or emergency button; deterministic tally | [VERIFIED] implemented | action-triggered `engine/tick.py:432-462`; tally `meetings/voting.py:120-213` |
| **Role-asymmetric vision** (crew same-room-only; impostor same-room-**and-adjacent**) | [VERIFIED] implemented | `visibility.py:98-127` — the deliberate "predator keeps the sight edge; crew must infer kills from testimony" design |
| **Emergency-on-suspicion / witnessed-kill flee** (crew) | [VERIFIED] implemented | `crewmate_policy.py:382-409` |
| **Triggered strategic LLM call** (witness-a-kill → immediate LLM) | [OPEN] design-only, **not wired** | `agents/strategic/reasoner.py` maps triggers but is not invoked by the run loop (`orchestrator/game.py` has 0 references); only meetings call the LLM |
| **Wider-vision / crew-vents / task-gating-that-wins** | [OPEN] design-space, owner-gated | discussed in `audit-2026-06-22-1558-forward-redesign.md`; none built as a balance-shifting lever |

**Takeaway for ML:** vents and sabotage are *not* new mechanics to invent — they are implemented action
primitives the learner can already emit; the open question is whether they are *tactically reachable* (vents:
yes, used; sabotage: yes but dominated by the frozen timer, §11).

---

## 3. The constraints that shape any ML design (quoted)

These are non-negotiable; a learned policy must fit inside all of them.

**3.1 — Deterministic engine + observation firewall (DESIGN.md:25, [VERIFIED]).**
> "Tick-based deterministic engine with a strict observation firewall. The engine ticks at a fixed rate
> (target 2 Hz). Agents never touch engine state directly — they receive `ObservationPacket`s filtered by
> visibility rules. Replays are bit-exact from a seed. This is non-negotiable."

- [VERIFIED] `advance_tick(state, actions, *, game_map) -> (WorldState, events)` is a pure function
  (`engine/tick.py:565-636`); `WorldState` is a frozen dataclass with `MappingProxyType` members
  (`engine/world.py:52`, `:71-78`).
- [VERIFIED] The engine draws RNG **once per tick and discards it** (`engine/tick.py:626-627`); there are **no
  stochastic state transitions** — outcomes are a pure function of `state + actions`. Real randomness enters
  only at seed time via a *separate* `random.Random(seed)` (`seeder.py:146-149`, `:237-239`). [VERIFIED]
  Tactical policies use no RNG (grep `agents/` → none). This is a gift for ML determinism: the only new float
  nondeterminism a learned policy could introduce is its own inference.
- [VERIFIED] Action resolution order is imposed by the orchestrator, sorted **ascending by actor id**
  (`orchestrator/action_ordering.py:34-40`), one action per actor per tick. Lower-id actors resolve first; a
  low-id actor's report/emergency **preempts the rest of the tick** (`engine/tick.py:586-587`), silently
  dropping higher-id actors' same-tick actions — [INFERRED] an ML edge case to encode.

**3.2 — Two-tier reasoning: LLM only at meetings (DESIGN.md:27, [VERIFIED]).**
> "Tactical decisions (move, do task, follow, vent) are rule-based and run every tick. Strategic decisions
> (meeting reports, voting, suspicion updates) use an LLM and run only at meetings or specific triggers …
> Without this split, cost and latency make the system unviable."

- [VERIFIED] The **import-linter firewall** forbids `agents/` → `engine/` (`.importlinter:7-13`), tested live
  (`tests/test_firewall.py:19-61`). A learned policy lives in agent-space and may import **only** the
  engine-free schemas (`observation/packet.py`, `action_intent.py`, `public_map.py`) — [VERIFIED] these have no
  engine imports (`tests/test_firewall.py:64-75`).
- [VERIFIED] Cost math for *why* per-tick LLM is banned: `DEFAULT_MAX_TICKS=1000` × 2 Hz × 9 agents ⇒ ~9,000
  LLM calls/game if tactical were LLM-driven — ~90× the ≤100-calls/game design target, and it would blow the
  ~$0.20–0.30/game ceiling by two orders of magnitude (`llm/budget.py:32-34`; DESIGN.md:116, :878). A **local
  NN forward pass** is entirely outside the budget: `decide()` never touches `LLMClient`, so a learned policy's
  inference is off-budget, at the microsecond "budget per agent per tick" DESIGN.md:116 already allots. [VERIFIED]

**3.3 — Structured memory first (DESIGN.md:29, [VERIFIED]).** Each agent keeps a typed event log + a derived
belief state; the LLM sees a rendered view. [INFERRED] This is the source of "memory features" for a recurrent
encoder (§6.3).

**3.4 — Replay provenance (byte-identical reconstruction, [VERIFIED]).**
- Each tick records `{actions (submitted), state_hash}` (`orchestrator/replay.py:363-371`); reconstruction
  re-feeds the **recorded discrete actions** through `advance_tick` and byte-verifies a SHA-256 of the entire
  `WorldState` per tick (`api/replay_loader.py:936-949`). **Policies are not re-invoked on replay.**
- The 5 substrate levers are stamped into `game_over.substrate_flags` (`orchestrator/replay.py:277-299`,
  `:434-441`); a loader guard **raises** `ReplaySubstrateMismatchError` (HTTP 500) if a stamped replay is
  reconstructed under a different substrate (`api/replay_loader.py:377-425`) — "no silent fallbacks."
- [INFERRED, load-bearing] **Determinism = seed + recorded actions + state_hash checkpoints, and it is
  policy-agnostic.** A learned policy changes only *which* actions get submitted; the recording format and the
  reconstruction path do not change. This is the single most important fact for provenance (§7).

**3.5 — Throughput budget ([V-ran], this host).**

| Path | Measurement |
|---|---|
| Full loop, fake provider, meetings ON — `run_throughput_benchmark` | **9p2i 7.7 games/s** (~31 ticks/game); **4p1i 25.3 games/s** (~16 ticks/game) |
| Full loop incl. report fold — `run_tournament_eval` (this author) | 9p2i 5.6 games/s; 4p1i 19.1 games/s (corroborating) |
| Bare engine `advance_tick` only, 9p2i all-Wait | **2,703 ticks/s** (370 µs/tick) |
| ML-spike `core.py` substrate (lighter) | ~0.06 s/game ≈ ~16 games/s (`report-ml-spike.md:21`) |

- [INFERRED] A tick is a few-hundred-µs of Python; a tiny-MLP forward is microseconds; an LLM meeting call is
  seconds + dollars. That gap **is** the two-tier doctrine, and it is why a learned tactical net fits and a
  per-tick LLM does not.
- [VERIFIED] **Cheap engine speedup available:** the vestigial per-tick RNG draw does a `json.dumps` of the full
  625-int Mersenne state every tick = **161 µs ≈ 43%** of engine-core cost (`engine/rng.py:31-38`), buying
  nothing (the value is discarded). Replacing it with a counter/Philox RNG is a ~1.7× engine-core speedup for
  training (§11).

---

## 4. The tactical layer today — the scripted FSM, and where it is visibly dumb

These are the improvement targets and the reward-design inputs. All [VERIFIED] against the code and the
committed seeds (pretty-printer + 50-seed aggregate written to scratch and re-run through the engine).

**4.1 — Crewmate FSM** (`agents/tactical/crewmate_policy.py`): a priority ladder
`REPORT > FLEE-witnessed-kill > REPAIR-gating-sabotage > EMERGENCY-on-suspicion > {route-to-task | idle}`
(`:343-423`), A* one-hop/tick (`pathing.py`). Emits `Move/DoTask/Report/Emergency/Repair/Wait` — never
Vent/Sabotage/Kill (`:87-96`).

- [VERIFIED] **No witness/buddy/safety awareness at all.** Movement never reads other players' positions; it
  will path a lone crewmate straight into a room with a suspected impostor (`:343-423`, `:565-689`). Prime
  reward target.
- [VERIFIED] **No task selection or ordering.** It acts only on the single engine-fed `pending_task_id`
  (`:376`); it cannot pick the nearest of several tasks, batch same-room tasks, or re-prioritize — selection
  isn't even in the policy.
- [VERIFIED] **Idle = walk to the meeting room and Wait.** On `pending_task_id is None` it routes to the hub and
  `WaitIntent`s (`:411-412`, `:667-689`), which the docstring admits exists only to force headless termination,
  "not because it's good play." Empirically: crew waits are **13% of all 9p2i actions**, concentrated late-game
  (seed 5: p-6 and p-9 idle in CAFETERIA ticks 22→45 — free bodies, zero patrol/alibi value). [V-ran]
- [VERIFIED] Reports only *same-room* bodies (ignores an adjacent-room body it can see), picks the
  alphabetically-first body, ignores positional info in sightings, ignores non-gating (`lights`) sabotage.

**4.2 — Impostor FSM** (`agents/tactical/impostor_policy.py`): priority
`VENT_EXIT > COVER/vent > SABOTAGE > KILL/opportunity > STALK > IDLE` (`:261`). Kill target scoring
(`_scored_targets`, `:936-1009`): `score = isolation·(1−witness_risk)·[cooldown==0]` where
`isolation = 1/(1+co_present)` (`:997-999`), sorted `(-score, player_id)` (lexical tie-break). Kill fires only
when co-located *this tick* with `co_present==0` and not deferring to a lower-id fellow (`:354-385`).

- [VERIFIED] **No stalking during cooldown — the biggest lost lever.** `cooldown_factor` zeroes every target's
  score while `cooldown>0` (`:989`) and the kill/stalk block is gated `if cooldown==0` (`:354`); during cooldown
  the impostor falls to idle and just `_wait()`s (`:1224`). It never repositions to set up the *next* kill.
- [VERIFIED] **Greedy kill timing, no escape-route check.** It kills the instant cooldown hits 0 and a target is
  alone (`:375-385`) — it does not check whether the room has a vent/safe exit first, so it can kill in a
  dead-end and then blindly `_cover` by walking to the alphabetically-first neighbor (`:1048-1057`).
- [VERIFIED] **Local-only, same-tick witness model.** It only counts players it currently sees in the same room;
  it models no adjacent-room player who could walk in next tick, so kills can be witnessed after the fact.
- [VERIFIED] Deferral to a lower-id fellow wastes the tick as a `_wait()` (`:384`); the "pretend-task" blend
  emits a `DoTaskIntent` the engine rejects (impostors own no task) — a cosmetic no-op tick (`:1240-1247`).
- [VERIFIED] **Sabotage is a late, defensive, dominated afterthought:** fires only `reactor`, only at ≥6/7 crew
  completion, only if no kill is available (`:340-352`); never uses `lights` offensively to *create* kills.

**4.3 — What the committed seeds show ([V-ran], 50 seeds/set):**

- **Impostor win rate = 0.40** (20/50, 9p2i) — [VERIFIED] by MANIFEST winner column + engine re-replay; the
  baseline-1 audit's **0.32** is the *pre-re-record* number ([STALE] for the committed bytes). Win reasons
  `{CREWMATE_EJECT:24, IMPOSTOR_PARITY:20, CREWMATE_TASKS:6}`, **0 IMPOSTOR_SABOTAGE**.
- **Kills are essentially never crew-witnessed:** 6/160 (3.75%) 9p2i, 1/64 4p1i had a living **crew** witness;
  20 more had only a *fellow-impostor* co-present (the witness set doesn't filter role — `engine/rules.py:29-45`
  — inflating any naive metric). This is *why* the kill-scene detector is unmeasured at n=1 (§below): witnessed
  kills barely exist under role-asymmetric single-room crew vision, and the scripted impostor self-selects
  `co_present==0` kills.
- **Impostor take-rate ≈ 0.48:** on ~405 clean tick-opportunities (cooldown 0, exactly one crewmate in room,
  unwitnessed) it killed on only 195. The canonical failure is seed 5: p-3 paces STORAGE↔ENGINEERING for ~28
  ticks *adjacent to* isolated p-5 doing a 10-tick REACTOR task and never steps in — a navigation/stalk failure,
  not perception lag (p-5 is in adjacent vision). ~5+ free kills declined; the game dragged 40 ticks.
- **48% of ejections hit an innocent** (CREW 56 / IMP 62 of 118 ejections). The close audit's clean Phase-15
  target — the **zero-flag / voice-driven mis-eject channel** — rose 22→31 (`audit-phase-14-close.md:§4`); it is
  outside every belief-fold lever and is *why* the FO-6 surrogate regressed (§8).
- **`compute_indistinguishability` fingerprint** ([VERIFIED] `eval/meeting_quality.py:2371-2411`): impostor
  wait-share ~52% vs crew ~10% — the scripted impostor is trivially distinguishable by idling. A learned
  impostor that *mimics crew task-traffic* (indistinguishability) is a rich, watchable tactical target — and
  the "impostor never does tasks" branch is currently dormant.

---

## 5. The action space for a learned tactical policy

**5.1 — Raw engine vocabulary ([VERIFIED] `engine/actions.py`).** Nine discriminated action types. For a
single agent on a single tick the *legal* set is tiny and enumerable:

| Action | Payload | Legality (pure boolean of `state,map,actor`) | file:line |
|---|---|---|---|
| `move` | `to_room` | not in vent; `to_room ∈ {room} ∪ neighbors(room)` (~2–5 options) | `tick.py:239-268` |
| `do_task` | `task_id` (map id) | crew only owns instances; not gated by sabotage; in the task's room; not done | `tick.py:271-311` |
| `kill` | `target` | impostor; target is crew; same room; cooldown 0 | `rules.py:56-99` |
| `vent` | `vent_id` | impostor; enter = vent in current room; exit = connected vent | `rules.py:102-179` |
| `report` | `body_id` | body in current room | `rules.py:182-197` |
| `emergency` | — | not in vent; uses < cap; in the emergency-button room | `rules.py:200-222` |
| `sabotage` | `kind` | impostor; none already active; kind exists (no location req.) | `rules.py:225-245` |
| `repair_sabotage` | `kind` | active gating sabotage matches; in a repair room | `rules.py:248-265` |
| `wait` | — | always legal for a live actor | `tick.py:530-536` |

- [INFERRED] **A `legal_actions(packet, public_map) -> mask` is low-medium effort** because every predicate is a
  pure boolean of `(state, map, params)` with zero RNG/hidden state. Two build paths: (a) refactor the
  `resolve_*`/`_apply_*` checks into pure `is_legal_*` helpers the resolvers also call (clean, ~1 day; touches
  both `engine/rules.py` and `engine/tick.py` since Move/DoTask validate in `tick.py`); (b) try/except each
  candidate through the resolver (works today, allocates wastefully). **Masking is standard and load-bearing at
  scale** — the masked policy gradient is valid, matters more as the invalid space grows, and a masked policy
  degrades if the mask is dropped at inference (Huang & Ontañón 2020, arXiv:2006.14171). [PROPOSED]

**5.2 — The recommended action interface: a high-level OPTION vocabulary, not the raw grid. [PROPOSED]**
Learning directly over `{move-to-each-room} ∪ …` is a ~10-way-per-tick masked head (the spike's `mlp_pick_room`
argmaxes over `{stay} ∪ adjacent`, `core.py:129-144`). But the *value* is in the sparse, conjunctive
decisions, and the FSM already generates good candidates. So the first-cut action space should be a **learned
selection over FSM-proposed options**:

- **Impostor options:** {kill best target, stalk-toward target *k*, vent (which exit), cover-move, sabotage now,
  wait/hold, reposition-during-cooldown-toward *k*}. The FSM's `_scored_targets` already enumerates ranked kill
  targets (`impostor_policy.py:936-1009`); the learner scores/chooses among them.
- **Crew options:** {continue-to-task, buddy-toward nearest crew group, patrol-toward last-seen suspect,
  report, call-emergency, repair, hold}. The engine-fed `pending_task_id` plus the visible roster give the
  candidate set.

[INFERRED] This bounds the learner to *legal, sensible* actions (it cannot emit illegal moves or wander off
into un-watchable degeneracy), makes behavior-cloning trivial (the FSM's own choice is a label), and keeps
determinism easy (score a fixed candidate list, integer-quantize, lexical tie-break). The raw masked grid
(§5.1) stays available as a later, higher-ceiling option (§9 Option 2/3).

---

## 6. The observation space — the firewall-legal feature surface

**6.1 — The complete `ObservationPacket` ([VERIFIED] `observation/packet.py:159-188`).** This is the entire legal
input to any learned policy. Nothing outside it may be read.

- `tick:int`, `agent_id`, `cooldown:int|None` (impostor-only).
- `self_state` (**private channel**): `room`, `role`, `pending_task_id` (map id; a *pretend* id for impostors),
  `fellow_impostor_ids` (impostor-only), `in_vent:bool`, `own_kill:{victim_id,room}|None`.
- `visible_players`: tuple of `{id, room, action}` — witness/vision-gated (`action ∈ {kill, vent, task}`, kill/
  vent only if witness-permitted).
- `visible_bodies`: tuple of `{id, room, victim_id}` (undiscovered bodies in visible rooms).
- `moved_players`: tuple of `{id, from_room, to_room}` — witnessed transitions (gated on seeing the *departure*
  room). Omitted from the JSON when empty (`:176-188`) — an encoder must treat it as optional, not `[]`.
- `audible_events`: `{kind ∈ {vent_use_heard, sabotage_alarm}, room|None}` (vent is room-gated; sabotage alarm
  is global).
- `global_state` (role-blind): `tasks_completed/total` (per-player instances), `task_completion_percent`,
  `sabotage_active/kind/repair_rooms/is_gating`.
- Plus `PublicMapView` ([VERIFIED] `observation/public_map.py`): `room_ids`, `room_neighbors`, `vent_graph`,
  `vent_rooms`, `task_locations`, `spawn/meeting/emergency_button_room` — the static map, known before the game.

**6.2 — The information ceiling (role-asymmetric). [VERIFIED] `visibility.py:98-127`.** Crewmates are downgraded
to `same_room_only`; impostors keep `same_room_and_adjacent`. Vented players are invisible; dead players see
nothing; co-present crew *do* witness kills (surfaced as `action="kill"`). This asymmetry is deliberate ("the
predator keeps the sight edge; crew must infer kills from testimony") and it is the root of the detection
ceiling — the crew's *entire* deduction signal is "the impostor was seen where it shouldn't be" (112/112
committed contradictions are `alibi_vs_sighting`; `audit-2026-06-22-1558-forward-redesign.md`). [INFERRED, load-
bearing] **This is the interestingness trap in structural form:** a smarter stealth impostor directly attacks
the only signal the crew has, so raw stealth optimization is exactly what un-makes the game (§12).

**6.3 — Encoder shape and the memory problem. [VERIFIED] + [PROPOSED].**

- **Fixed-cardinality** (stable one-hot/embedding tables from `PublicMapView`): 10 rooms, 6 vents, 12 map
  tasks, sabotage kinds. **Roster-dependent** (variable-length, up to roster size; needs set-invariant or
  fixed-slot encoding): player ids in `visible_players`/`moved_players`/`visible_bodies`/`fellow_impostor_ids`,
  and the per-player-instance task counts. `role` is a 2-way self-only categorical. [VERIFIED] `observation/
  service.py`, `boundary.py`.
- The spike's encoder is **34 dims** = 10-room self one-hot + per-room player counts (10) + per-room body counts
  (10) + 4 scalars (cooldown, in_vent, tasks%, sabotage) ([VERIFIED] `ml_spike/core.py:60-83`). It is
  **memoryless** and stores per-room *counts*, not target identity — [VERIFIED] the structural reason BC caps
  below FSM parity (the FSM's stalk is history-dependent; a single-packet encoder cannot represent it).
- **The memory features a stateful encoder needs are already accumulated** ([VERIFIED] `agents/memory/`): the
  persisted, carried-across-ticks state is essentially **2 floats per player (suspicion, trust) +
  `WorkingMemory.last_seen (tick,room)` + per-player alibi/contradiction lists** (`beliefs.py:427-443`,
  `working.py:49-55`); everything else (co-presence groups, breadcrumbs, transitions, roster) is recomputed by
  a full-log rescan each render (`store.py`). [PROPOSED] The production encoder should carry these memory
  features (a recurrent state, or the belief floats + last-seen as explicit inputs), which is exactly what the
  spike flagged as TODO.
- **Determinism hazard to design around** ([VERIFIED] `agents/memory/`): belief suspicion/trust are **floats**
  with non-power-of-two deltas (0.05/0.08/0.2/0.3/0.5/1.0) accumulated and clamped; float residue is masked at
  the *render* layer (0.005 neutral band, `store.py:1558-1567`) but **not at the decision gate** (crewmate reads
  raw `>=0.60`, `crewmate_policy.py:290`), and `known_players()` is dict-insertion-ordered
  (`beliefs.py:508-509`), safe today only because every consumer wraps it in `sorted()`. [INFERRED] Any learned
  encoder that reads belief floats re-opens the determinism question — it must quantize the belief-derived
  features and use lexical tie-breaks (the mitigation ladder, §7).

---

## 7. Where a policy plugs in, and how provenance works

**7.1 — The injection seam ([VERIFIED], zero engine edits).**
`AgentFactory = Callable[[PlayerId, Role], AgentInterface]` (`orchestrator/game.py:93`), consumed once per
player at `game.py:1447-1453`, and a **first-class keyword param** on `run_tournament_eval` /
`run_balance_eval` / `run_throughput_benchmark` (`eval/balance_eval.py:227-238`, `:411`; `eval/benchmark.py:70`).
The only mandatory method is `decide(packet, public_map) -> ActionIntent` (`agents/base.py:19-23`); to take part
in meetings the agent additionally needs the two `MeetingAwareAgent` methods (`render_memory_for_meeting`,
`suspicion_graph_for_meeting`, `game.py:426-450`) — three belief-fold hooks are optional. The spike proves the
swap works by wrapping the real `TacticalAgent` and delegating the whole meeting protocol via `__getattr__`
(`ml_spike/core.py:148-200`). [VERIFIED] **A learned policy is a drop-in `agent_factory`; no engine, orchestrator,
or meeting code changes.**

**7.2 — Provenance: the "record actions" path needs zero stamping for byte-identity. [VERIFIED]+[INFERRED].**
Because reconstruction re-feeds the *recorded discrete actions* and never re-invokes the policy (§3.4), a
learned policy's chosen actions are frozen into the replay and the per-tick `state_hash` catches any
divergence — so **replay is byte-identical regardless of the net's inference determinism.** Only *live
re-record* is exposed to float nondeterminism, and it shares that exposure with today's float kill-scoring
(`impostor_policy.py:999`).

**7.3 — What must be added for provenance (design-only today; [PROPOSED]).**
- Nothing today stamps a policy identity ([VERIFIED] grep `orchestrator/replay.py` for policy/weights/net →
  none). To answer *"which policy produced these bytes,"* stamp a **policy-id + weights content-hash** into the
  replay/MANIFEST, mirroring the two existing precedents: `MeetingReplayEntry.prompt_versions`
  (`replay.py:138`) and `game_over.substrate_flags` (`replay.py:181`). This is the cheap, architecturally
  consistent path.
- **Recommendation: RECORD actions, do not re-run the net on replay.** The "re-run net" path would additionally
  require a bit-reproducible inference (weights hash + arch version + featurization version + a sampling seed
  and recorded sampled actions) *and* a new guard mirroring `_assert_substrate_matches` that refuses
  reconstruction under a mismatched weights-hash. It is only worth that burden if you must re-derive actions
  under a changed input pipeline — which recording forecloses. [INFERRED]
- **Live re-record determinism (the mitigation ladder, [VERIFIED] `ml-spike-charter.md:56-62`):** (1) quantize
  logits to a fixed integer grid + break ties with the existing lexical `player_id` sort (partially in-code
  already — `mlp_pick_room` sorts candidates, `core.py:138-144`); (2) backstop — recorded-action replay is
  immune regardless. The cross-machine residual is the real risk, and the general fix is
  **integer/fixed-point arithmetic with a fixed accumulation order** (float addition is non-associative, so
  cross-hardware bit-identity in float is essentially unattainable — Gaffer-On-Games; PyTorch reproducibility
  notes; arXiv:2408.05148). FO-4 already shows byte-identity holds *same-machine* even with a numpy backend and
  a stateful encoder ([V-ran]).

---

## 8. Training without LLM meetings, and evaluating with them

**8.1 — Training inner loop must be LLM-free ($0, fast).** [VERIFIED] gameplay between meetings is already
LLM-free (grep `agents/tactical/` for llm → none; `FakeProvider` cost 0.0). Two knobs make a fully LLM-free
training loop:

- **Stubbed meetings.** [VERIFIED] `meeting_runner=None` makes `HeadlessGame` return `MEETING_PHASE_REACHED` at
  the first meeting (`game.py:1266-1270`) — an engine-only rollout that never reaches an LLM. But the win is
  then decided only by kills/tasks, which starves the *social* reward. [PROPOSED] Instead, plug a **surrogate
  meeting runner** (satisfies the runner protocol, no LLM): it computes each meeting's ejection from a cheap
  model of the vote, feeds the deterministic tally (`meetings/voting.py::tally_ballots`, [VERIFIED] pure,
  LLM-free), and returns a normal `MeetingResult`. The tally is already deterministic given ballots, so a
  surrogate only has to predict *ballots* (or the suspicion-rank that drives plurality).
- **The surrogate is the linchpin — and it has REGRESSED.** [V-ran] The spike's LLM-free physical suspicion-
  rank surrogate (reconstructed sightings + proximity-to-kill + reporter → rank the likely ejectee) was reported
  at top-1 64% / top-2 82% and is the entire basis for "the impostor side is cheaply trainable offline." On the
  **currently committed** baseline-2 corpus it reproduces at **top-1 26% / top-2 43%** (≈ chance ~14% top-1).
  Why: the corpus was re-recorded after the spike; ejections shifted toward the voice/testimony-driven
  zero-flag channel that rose 22→31 in the close audit — i.e. *less physically predictable*, by construction.
  [INFERRED] **The offline-trainability thesis is no longer established.** S3 (§10) makes re-validating it a
  GO/NO-GO gate, not an assumption; if it stays low, the fallbacks are (a) a *learned* vote surrogate
  behavior-cloned from the committed ballots (FO-6 flag-feature variant reproduced at top-1 57%/top-2 77% on
  current data — usable but LLM-flag-dependent), or (b) a periodic **real-LLM selection gate** in the outer loop
  (train against the surrogate, re-ground on real meetings every N generations). Never train indefinitely
  against a frozen surrogate — surrogates get exploited (MBPO/Dreamer literature; §9).

**8.2 — Proxy rewards from engine events (the tactically-reachable signal).** [VERIFIED] FO-3 showed tactical
play alone cannot move the meeting-dependent rubric terms (R1/R7 flat at 0 under fake meetings). So the inner-
loop fitness must be *tactically reachable*:

- **Impostor:** minimize its own learned physical-suspicion rank (the FO-6 objective) + resolved-kill count +
  meetings-survived; penalize being witnessed/venting-in-view. [PROPOSED] Add **potential-based shaping**
  (Ng, Harada & Russell 1999 — leaves the optimal policy invariant) toward legible setups so stealth doesn't
  collapse the game (§12).
- **Crew:** task-completion progress + surviving + correctly-routed reports + buddy/patrol coverage of
  last-seen suspects. FO-8 showed a learned crew buddy/task gate is real but small (11/12 vs FSM 10/12).
- **Both:** the win as the terminal sparse reward.

**8.3 — Evaluation must use REAL LLM meetings, on the existing harness. [VERIFIED].** A champion is judged by
running `run_tournament_eval(agent_factory=<learned>)` on the canonical 9p2i + 4p1i seed sets with a real
provider, then scoring:

- **The HARD validity gate** — [OPEN] `scripts/validity_gate.py` **does not exist**; it is audit prose. Its
  criteria (`audit-phase-14-close.md:§1`) — every game reaches `game_over`; 0 friendly-fire / betrayal-firewall
  breaches; **meeting-rate ≥ 0.60 and ≥ 30 resolved meetings**; 0 tick-1 kills; 0 dangling reason-ids; exact
  provenance rows — must be **built** from the live folds that do exist (`eval/win_condition_selfcheck.py`,
  `eval/leak_test.py`, `eval/meeting_quality.py::compute_meeting_rate`, `scripts/verify_samples.sh`).
- **The R-gate (a measurement, not a pass/fail)** — [OPEN] `scripts/measure_baseline.py` **does not exist**
  either. Its metrics have live homes — ejection accuracy (`vote_correctness.py:302`), genuine-class conversion
  (`vote_correctness.py:558`), impostor win rate (`balance_eval.py:894`), accusation calibration
  (`accusation_calibration.py`) — **except R1 eject-decided win share, which has no live fold at all.**
- **The interestingness rubric** — the D1–D4 geomean referee (§9/§12) + `rubric_score.py` + the
  `audits/workflows/extract_gameplay_facts.py` fact extractor.
- **The firewall check** — [VERIFIED] `eval/leak_test.py` runs on scripted fixtures and takes **no
  `agent_factory`**; extend it to accept a factory so the learned agent's packets are leak-scanned (the spike's
  Gap #7). Enforcement is test-time only (no runtime guard rejects a leaky packet at build time — §6).

[INFERRED] **This is why the plan is harness-first (§10-S0): the acceptance test the ML work is graded on is
not yet a committed, reusable artifact.**

---

## 9. Paradigm comparison

The problem shape: a **POMDP**, **multi-agent, two-team, asymmetric-role** game, **determinism-critical**, run
by a **solo maintainer on CPU at $0**, where the reward is **sparse, delayed, and ~80% controlled by the
frozen LLM meeting layer** (FO-3), the only cheaply-reachable signal is physical suspicion (FO-6, now
regressed), and the crew's only detection signal is the impostor's imperfect stealth (§6.2). No torch/numpy is
in the dependency set today (`pyproject.toml` is pydantic + fastapi; the spike is pure-Python).

**Option 1 — Learned utility scorer over the FSM's own legal options. [RECOMMENDED entry point].**
Keep the FSM's option-generation; replace only the scoring/selection with a small learned function over
firewall-legal features (§5.2).
- *Fit:* minimal surface; **behavior-cloning is trivial and reaches parity by construction** (clone the FSM's
  own argmax, unlike the spike's from-scratch clone that capped out); determinism easy (fixed candidate list +
  quantize + lexical tie-break); interpretable; **structurally bounded** so it cannot emit illegal or wildly
  off-distribution actions — which caps reward-hacking and keeps games watchable.
- *Trade-off:* ceiling is bounded by the FSM's option menu (it can't discover an option the FSM never proposes,
  e.g. a novel bluff). It is policy-improvement-within-the-menu, not open-ended discovery.
- *Evidence:* a strict superset of the spike's Move/Wait-override proxy (`core.py:164-181`).

**Option 2 — ES / neuroevolution on a tiny MLP. [RECOMMENDED optimizer].**
Direct policy net over the encoder → masked action head, optimized by `(1+λ)`-ES / CMA-ES / OpenAI-ES on the
proxy fitness.
- *Fit:* **exactly the regime where ES beats PPO** — sparse/non-differentiable black-box reward, cheap
  embarrassingly-parallel CPU rollouts, tiny nets; no backprop, no value function, invariant to long horizons
  and delayed rewards (Salimans et al. 2017, arXiv:1703.03864; ARS matches PPO on control at linear-policy
  scale, Mania et al. 2018, arXiv:1803.07055). Determinism is proven ([V-ran] Check-1, FO-4). Single-population
  ES does **not** monoculture ([V-ran] FO-9, cosine 0.45 < 0.7). It climbs and partially generalizes ([V-ran]
  Check-2: 14→24 kills, FSM 32). ES's shared-seed parallelism fits the $0-CPU posture natively.
- *Trade-off:* 2–10× less sample-efficient than a well-tuned policy gradient (Sigaud 2022, arXiv:2203.14009),
  and needs many seeds per fitness eval to beat the chaotic task-clock (Check-2 averaged over K seeds). BC-init
  requires the encoder to carry memory (Check-2 finding).
- *NEAT vs fixed MLP:* topology search is **not worth it** for a single fixed-I/O task at this scale — a fixed
  small MLP + ES/CMA-ES/ARS is simpler and competitive (arXiv:1912.05239); defer NEAT/HyperNEAT unless
  architecture search itself becomes the point.

**Option 3 — PPO self-play (+ recurrent policy) with league/exploiters. [DEFER].**
Gradient RL; LSTM/GRU for POMDP memory (DRQN, R2D2, OpenAI-Five; recurrent model-free RL is a strong POMDP
baseline, Ni et al. 2022, arXiv:2110.05038); MaskablePPO for legality (sb3-contrib); self-play with a
Hall-of-Fame / PSRO pool + explicit exploiters (AlphaStar, Nature 2019).
- *Fit:* strongest asymptotic policies; recurrence is the natural memory answer.
- *Trade-off:* heavy new deps (torch), **cross-machine float-determinism re-opened** (mitigated only on the
  record path), sample-hungry, and **co-evolution instability is real here** ([V-ran] FO-2 collapsed). High
  tuning burden for a solo maintainer. Worth it only if Options 1–2 ceiling out.

**Option 4 — Behavior cloning + DAgger from the scripted expert. [Warm-start only, not standalone].**
- *Fit:* cheap competent init; the FSM is a **queryable scripted expert — the ideal DAgger oracle** (free
  labels at the learner's own states, turning BC's O(T²ε) distribution-shift regret into O(Tε); Ross et al.
  2011, arXiv:1011.0686). This is the right way to warm-start Options 1/2/3.
- *Trade-off:* caps at the demonstrator (spike BC 13 kills < FSM 27, from a memoryless encoder) — a bootstrap,
  not an answer.

**Cross-cutting: co-evolution is the one un-de-risked blocker.** [V-ran] FO-2's naive 2-population opposing-
fitness ES collapses to a degenerate equilibrium in round 0 (crew trivially denies all kills → impostor gets
zero gradient). This is the textbook **coevolutionary disengagement / loss-of-gradient** (Cartlidge & Bullock
2004). The literature's stabilizers, to be applied together (S6): a **shared role/team-conditioned policy**
(one net plays both sides — the biggest CPU saver and it structurally couples the two populations), a
**Hall-of-Fame** of frozen snapshots (window ~10–20), **~50/50 latest/past opponent mixing** with **PFSP
variance-weighting** (∝ `x(1−x)`, concentrate on ~50%-win-rate opponents), one periodically-reset **exploiter**
to break non-transitive cycles, **ELO across the whole pool** to detect cycling, **reduced virulence** (reward
~0.75 not crush-1.0) if one side dominates, and **quality-diversity** (MAP-Elites/Novelty) to hold behavioral
diversity (AlphaStar Nature 2019; OpenAI Five 2019; Real-World-Games-Spinning-Tops, Czarnecki 2020;
MAP-Elites, Mouret & Clune 2015).

**Prior art to lean on:** DeepMind's **Hidden Agenda** (arXiv:2201.01816) is a 2D Among-Us-like MARL
environment with diverse learned equilibria and no NL channel — the closest published precedent. **Social-
Deduction-via-MARL** (AAMAS 2025, arXiv:2502.06060) uses *"predict the impostor"* as a dense listening reward —
a template for a tactically-reachable crew reward. **DeepRole** (arXiv:1906.02330) is CFR + deep value nets for
Avalon. Caveat to flag: CFR/Nash guarantees are **2p-zero-sum only**; hidden-role team games are general-sum,
so treat "solved poker" results as non-transferable.

---

## 10. Recommendation and staged plan (sized like this repo's phase tasks)

**Recommended path: harness-first → learned scorer (Option 1, BC/DAgger-init, ES-refined) against the frozen
FSM → watchability-gated → bounded co-evolution last. Defer PPO/torch. Keep pure-Python/quantized inference.**

Each stage is one contract-shaped PR (branch, in/out-of-scope files, definition-of-done), in the repo's
existing style. Stages S0–S3 are algorithm-agnostic; they pay off no matter which optimizer wins.

- **S0 — Productize the gate (NO learning).** Turn the audit-only "validity gate" + "R-gate" into committed,
  reusable code that scores any `run_tournament_eval` output: assemble the criteria in §8.3 from the existing
  `eval/` folds; add the missing **R1 eject-decided win-share** fold; wire the D1–D4 geomean referee. *DoD:* a
  one-command gate that reproduces every baseline-2 number from the committed bytes. This is the acceptance
  test every later stage runs against.
- **S1 — Gym-style env wrapper + `legal_actions` mask + policy-id provenance.** A thin
  Gymnasium/PettingZoo-Parallel-shaped wrapper around `HeadlessGame` via `agent_factory` (zero engine edits);
  a `legal_actions(packet, public_map)` mask refactored from the pure `rules.py`/`tick.py` predicates; a
  policy-id + weights-hash stamp in the replay/MANIFEST mirroring `substrate_flags`. *DoD:* a random-genome
  policy runs through the wrapper and its replays reconstruct byte-identically and carry the policy stamp.
- **S2 — Memory-carrying feature encoder + determinism harness.** Extend the spike's 34-dim encoder with the
  belief/last-seen memory features (§6.3); re-run Check-1 hashing the **encoder-vector + logits** (not just
  WorldState); apply quantize + lexical tie-break; **extend `eval/leak_test.py` to accept an `agent_factory`**
  and run the learned agent through it (Gap #7). *DoD:* byte-identical same-machine + leak-clean.
- **S3 — Re-validate the offline fitness (GO/NO-GO).** Re-measure the FO-6 physical suspicion-rank surrogate on
  a *frozen* baseline-2 corpus; if it clears a bar (say ≥ 60% top-2), use it as the LLM-free inner-loop fitness;
  if not, fall back to a BC'd learned vote surrogate and/or a periodic real-LLM selection gate (§8.1). *DoD:* a
  documented surrogate with a measured fidelity number and a re-grounding cadence.
- **S4 — Learned scorer impostor (Option 1), BC/DAgger-init from `_scored_targets`, ES-refined on S3 fitness
  against the frozen FSM crew.** Watchability guard baked in: reject any champion that drops meeting-rate below
  the S0 validity bar or lowers R5/R7 (anti-perfect-stealth). *DoD:* beats the FSM impostor on take-rate/win
  without failing S0.
- **S5 — Rubric-in-the-loop ES + eyeball (closes the open FO-3 Goodhart check).** Optimize against the literal
  D1–D4 geomean referee with a periodic real-LLM meeting gate; manually review the top champion's games for
  Goodhart (the charter's mandated guardrail, never actually run). *DoD:* a champion whose geomean rises with no
  eyeballed degeneracy.
- **S6 — Bounded co-evolution (the FO-2 blocker).** Shared role-conditioned policy + Hall-of-Fame + PFSP +
  reduced virulence + ELO monitoring + QD diversity (§9). *DoD:* stable, non-degenerate, watchability held vs a
  fixed held-out opponent.
- **S7 (optional/deferred) — PPO + recurrent + league** if S4–S6 ceiling out; accept the torch dep + record-
  path quantization.
- **S8 (owner-gated, orthogonal to ML) — structural-information levers.** A task-gating-that-*wins* sabotage
  retune, crew vents, or wider vision — the balance changes that would give the kill-scene detector a
  measurable scenario (n=1 today) and lift the detection ceiling. Not an ML task, but the change that makes
  richer learned tactics legible (§11, §13).

---

## 11. Engine modifications that would make training tractable

None are required to *start* (the spike ran with zero engine edits); these are accelerators/enablers, ordered
by leverage. All are [PROPOSED].

1. **Gym/PettingZoo-Parallel wrapper (S1).** AiLibi is simultaneous-move per tick, so the PettingZoo Parallel
   API is the natural shape; keep the wrapper thin over `agent_factory` (wrap, don't fork — Gymnasium wrapper
   discipline). Expose `action_mask` in the observation for MaskablePPO compatibility later.
2. **Speed: replace the vestigial per-tick RNG snapshot.** [VERIFIED] it eats ~43% of engine-core cost
   (`engine/rng.py:31-38`) and the drawn value is discarded — a counter/Philox RNG (or dropping the per-tick
   draw) is a ~1.7× engine-core speedup. Combined with multiprocessing over seeds (as ES already does), this
   lifts the effective training throughput materially on a multi-core host.
3. **Reward instrumentation.** [VERIFIED] the typed event log (`engine/events.py`, 14 event types incl.
   `Killed.witnesses`, `Moved`, `TaskCompleted`, `MeetingTriggered`) already carries every signal a dense proxy
   reward needs — surface a per-tick reward vector (kills, witnessed-ness, task progress, co-presence coverage)
   as an env `info` channel so ES/PPO don't have to re-derive it from the replay.
4. **A surrogate meeting runner** (S3) implementing the runner protocol with no LLM — the enabler for a fully
   $0 inner loop (§8.1).
5. **Vents/sabotage for ML depth (owner-gated).** Vents already serve (the −91% deflection lever). Sabotage is
   the interesting one: it is *implemented* but *dominated* by the frozen `reactor` timer=6 ([V-ran] FO-7: ES
   learns to *avoid* it because it craters kills without winning). [INFERRED] Making sabotage a live tactical
   lever is a **balance change (the timer), not an ML problem** — an owner call (S8). Adding a *third* mechanic
   is unnecessary; the depth is unlocking the two that exist.

**Note on dependencies.** Options 1–2 (scorer + ES) can stay **pure-Python or a single numpy dep**, preserving
the $0 / determinism / low-dep posture the repo values. PPO/torch (S7) is a heavier commitment deliberately
deferred.

---

## 12. Risks and guards

**12.1 — The interestingness constraint is the deepest risk (a *strong* learner, not a weak one).** [VERIFIED]
+ [INFERRED]. The social game currently rides on the impostor being *forced* to garble testimony (~100% of
flagged impostor alibis are false — `audit-2026-07-01…:§3`) and on its imperfect stealth (kills 3.75%
crew-witnessed, take-rate 0.48 — §4). A learned impostor that achieves *perfect* stealth (kills only when truly
alone, vents the trail, mimics crew task-traffic) produces **no flags → meetings starve of testimony → R1/R5/R7
collapse → the deduction game un-makes itself.** This is not hypothetical: it is the game-theoretic norm —
optimal imperfect-information play is randomized, minimally-communicative, and *illegible* ("secret handshake"
conventions; Pluribus's "alien" strategies; Other-Play / OBL). **The field's response is to regularize away
from pure optimality toward human-likeness** (CICERO's honest-message filtering; piKL/Diplodocus human-
regularization; AIWolf's NL division judged on *humanness* not win rate; "Winning Isn't Everything," Zhao et al.
2020).
- **Guard (the good news — the tooling exists).** [VERIFIED] The implemented per-game score is the **floor-gated
  weighted geomean of D1–D4** (Task 13.15, `rubric_score.py:823`, weights .40/.25/.15/.20), which is
  *multiplicative* — a meeting-starved game drives D1 (needs a contested meeting), D2 (needs testimony
  separation) and D4 (needs ≥2 meetings) toward 0 and the product collapses to ~0. So a perfect-stealth genome
  **scores ~0 on the referee by construction.** Plus `compute_meeting_rate` (≥0.60 bar) and the R5 win-shape
  diversity sentinel.
- **The unresolved tension to flag for the owner** ([VERIFIED] `report-rubric-design.md`): the geomean is
  designed as an **offline referee / selection gate, never the inner-loop fitness** — and the impostor's
  intended inner-loop objective (minimize its own physical-suspicion rank) *rewards exactly the stealth that
  starves meetings.* Nothing in the $0 inner loop pulls toward generating testimony. **So watchability must be a
  HARD selection GATE, not a soft reward:** reject any champion whose replays fail the validity meeting-rate bar
  / drop R5 below ≥3 win-shapes / lower R7, even if it wins more. Optimize "tactics that create legible
  situations," not win rate. [PROPOSED] Add **potential-based shaping** (Ng 1999, policy-invariant) toward
  legibility, and **co-evolve the crew** (S6) so stealth is *contested* rather than free — otherwise the
  impostor climbs stealth and the referee floors the whole set.

**12.2 — Reward hacking / Goodhart.** [VERIFIED] The old additive-rubric Goodhart the spike flagged ("R7 rewards
flag presence") is **closed** in the geomean (R7 dropped as an input; the multiplicative composition prevents a
live term masking a dead one). Residual: D4's `contest = min(1,(n_meetings-1)/2)` is kill-rate-manufacturable
but tiny (≤0.04 effective) and the geomean requires the other dead dimensions to be nonzero, so meeting-farming
alone can't lift the score. General guards: reward hacking **worsens with capability and shows phase
transitions** (Pan et al. 2022, arXiv:2201.03544) and no reward is fully hack-proof (Skalse et al. 2022) — so
cap optimization pressure / early-stop, treat "proxy up + true-reward down" as an anomaly to detect, and
**eyeball the top champion's games** (the charter guardrail, still un-run — S5). Option 1's bounded action menu
is itself a strong anti-hacking guard.

**12.3 — Exploiter / co-evolution dynamics.** [V-ran] FO-2 collapse is real; do **not** run naive 2-population
opposing-fitness ES. Use the §9 stabilizer stack (S6). Also budget some training against deliberately
out-of-distribution opponents — self-play policies are exploitable by adversarial policies a co-trained
opponent never explores (Gleave et al. 2020, arXiv:1905.10615).

**12.4 — The surrogate is a moving target.** [V-ran] FO-6 already regressed once on a re-record. A learned
mover changes the sighting/contradiction distribution *by construction*, so the surrogate must be **re-calibrated
after any mover change and any meeting-layer change**, and the inner loop must periodically **re-ground on real
LLM meetings** (never train indefinitely against a frozen surrogate — MBPO/Dreamer model-exploitation caveat).

**12.5 — Determinism regressions.** A learned encoder that reads belief floats re-opens the residue-flips-argmax
hazard (§6.3); the `known_players()` insertion order is only safe under `sorted()` guards. Quantize belief-
derived features; keep lexical tie-breaks; hash encoder-vector+logits in the determinism test (S2).

**12.6 — Balance is a finding, not a failure — but watchability is the line.** [VERIFIED] DESIGN.md:338: the
crew/impostor split is "reported and re-baselined on each re-record, not gated to a fixed band … closing the
crew-skill gap is the agent-intelligence work, not a balance dial." So a rise in impostor win from *smarter*
tactics is acceptable **iff watchability holds**; whether a given rise is acceptable is the owner call (§13).

---

## 13. Open questions for the owner

1. **Which side first?** The impostor tactical lever is the higher-signal, better-studied one (kill timing,
   witness avoidance, vent cover) but also the one that most threatens watchability. The crew lever (buddy,
   patrol, task routing) is lower-ceiling (FO-8: +1 game) but safe. Recommend impostor-first *with* the
   watchability gate live from S4 — confirm?
2. **The watchability contract.** Is a rise in impostor win-rate from smarter stealth acceptable, and up to
   what ceiling, *provided* the meeting-rate / R5 / R7 gates hold? This is the single decision that most shapes
   the reward/gate design (§12.1).
3. **Structural-information levers (S8).** Are you willing to make owner-gated balance changes — a
   task-gating-that-*wins* sabotage retune, crew vents, wider/foggier vision, BotC-style physical
   misinformation — to give richer learned tactics something legible to produce (and finally measure the n=1
   kill-scene detector)? The forward-redesign audit prefers physical-substrate richness over out-talking the
   model; this is the biggest lever on both interestingness and the detection ceiling.
4. **Dependency posture.** Hold the line at pure-Python + (optionally) numpy for ES (S0–S6), or accept torch
   now to keep PPO/recurrent (S7) on the table? Recommend holding the line until S4–S6 demonstrably ceiling.
5. **Re-record cadence vs. the moving surrogate.** The FO-6 regression shows any prompt/lever re-record shifts
   the ejection distribution and invalidates a physical surrogate. Do you want the surrogate re-calibration + a
   frozen-corpus "ML baseline" pinned as an explicit release artifact, separate from the LLM-prompt baseline?
6. **Scope of "cross-round strategy."** The prompt asks for strategy that persists across a round. Beyond the
   already-carried belief state, do you want the learned policy to carry an *explicit* cross-meeting plan
   (e.g., an impostor committing to frame a specific crewmate over several rounds)? That raises the ceiling but
   also the reward-hacking and determinism surface.

---

## 14. Method, reproduction, and references

**Verification method.** Direct reads of `engine/`, `agents/`, `observation/`, `orchestrator/`,
`api/replay_loader.py`, `meetings/`, `llm/`, `eval/`, `scripts/`, `experiments/lab/`. Throughput measured via
`eval.benchmark.run_throughput_benchmark` and `eval.balance_eval.run_tournament_eval` under
`AILIBI_LLM_PROVIDER=fake`. Six spike probes (`check1`, `check2`, `check3`, `fo2`, `fo4`, `fo5`, `fo6`, `fo7`)
re-run on current HEAD via `uv run`. Replays characterized with a scratch pretty-printer that re-seeds +
replays through the real engine (mirroring `api/replay_loader.py::_walk`); 50-seed winner/kill/witness/meeting
aggregate recomputed from the committed bytes.

**Key in-repo artifacts.**
- `experiments/lab/ml_spike/` + `ml-spike-charter.md` + `report-ml-spike.md` — the prior feasibility spike (its
  magnitudes are [STALE]; conclusions robust *except* the FO-6 linchpin, now [OPEN/REGRESSED]).
- `experiments/lab/rubric.md`, `rubric_score.py` (D1–D4 geomean), `report-rubric-design.md`,
  `report-rubric-interestingness.md` — the fitness/referee.
- `audits/audit-phase-14-close.md` (baseline-2, impostor win 0.40), `audit-2026-07-01-…baseline1-…md`
  (baseline-1, 0.32 — [STALE] for committed bytes), `audit-2026-06-22-1558-forward-redesign.md`,
  `experiments/lab/report-vent-escape-lab.md`, `report-grounding-audit.md`, `report-stopwatch-lab.md`.

**External references (year; primary sources).** ES: Salimans et al. 2017 (arXiv:1703.03864); ARS: Mania et al.
2018 (arXiv:1803.07055); ES-vs-RL survey: Sigaud 2022 (arXiv:2203.14009); NEAT: Stanley & Miikkulainen 2002;
CMA-ES: Hansen 2016 (arXiv:1604.00772); QD/MAP-Elites: Mouret & Clune 2015 (arXiv:1504.04909), Novelty Search:
Lehman & Stanley 2011. Self-play/league: AlphaStar Nature 2019; OpenAI Five 2019 (arXiv:1912.06680); PSRO:
Lanctot et al. 2017 (arXiv:1711.00832); NFSP: Heinrich & Silver 2016 (arXiv:1603.01121); Spinning Tops:
Czarnecki et al. 2020 (arXiv:2004.09468); disengagement/reduced-virulence: Cartlidge & Bullock 2004; adversarial
policies: Gleave et al. 2020 (arXiv:1905.10615). Hidden-role / social-deduction: DeepRole, Serrino et al. 2019
(arXiv:1906.02330); Hidden Agenda, Kopparapu et al. 2022 (arXiv:2201.01816); Social-Deduction-via-MARL, Sarkar
et al. 2025 (arXiv:2502.06060); AIWolf/AIWolfDial. POMDP/recurrence: DRQN, Hausknecht & Stone 2015
(arXiv:1507.06527); recurrent-model-free baseline, Ni et al. 2022 (arXiv:2110.05038); Hanabi/BAD/Other-Play/OBL.
Imperfect-info: CFR (Zinkevich et al. 2007), Deep CFR (Brown et al. 2019), ReBeL (Brown et al. 2020), Pluribus
(Brown & Sandholm 2019). Reward shaping/hacking: potential-based shaping, Ng, Harada & Russell 1999;
specification gaming, Krakovna et al. 2020; reward-misspecification phase transitions, Pan et al. 2022
(arXiv:2201.03544); defining reward hacking, Skalse et al. 2022 (arXiv:2209.13085). Human-regularization: piKL/
Diplodocus (arXiv:2210.05492), CICERO (Science 2022). Tooling: Gymnasium & PettingZoo (Terry et al. 2021,
arXiv:2009.14471); invalid-action masking, Huang & Ontañón 2020 (arXiv:2006.14171); DAgger, Ross et al. 2011
(arXiv:1011.0686); World Models (Ha & Schmidhuber 2018), MBPO (Janner et al. 2019), DreamerV3 (Hafner et al.
2023); offline RL: CQL (Kumar et al. 2020), IQL (Kostrikov et al. 2021). Determinism: FP non-associativity
(arXiv:2408.05148); PyTorch reproducibility notes; Gaffer-On-Games "Floating Point Determinism."
