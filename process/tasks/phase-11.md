# Phase 11 — Impostor Information Economy (deception works, then balance)

Goal: make deduction AND deception load-bearing by giving the impostor the genre-standard information
counterplay it has never had — measured by the interestingness SCORE, not the win split (the lab proved the
split is "purchasable wholesale"). The diagnosis is the anchor: the 2% impostor win is an INFORMATION
ceiling, structurally caused — a model upgrade was ruled out (7B/9B/frontier head-to-head), and the impostor
FSM emits only Kill/Move/DoTask/Wait while vents/sabotage/self-report sit implemented-but-unused.

Anchor: experiments/lab/report-model-ceiling-probe.md (model-upgrade ruled out), report-vent-escape-lab.md
(vents validated: hiding the post-kill sighting trail eliminates 91% of impostor contradiction flags, 25/28
go flag-clean), report-memory-fix-probe.md (kill-memory falsified as a survival lever — legibility only),
report-rubric-interestingness.md (the W2 baseline the waves must move). Diagnosis bundle committed @ 33d4180.

Locked decisions (2026-06-15, owner):
- Gameplay rework BEFORE the front-end (front-end → Phase 12). This phase.
- Wave 1 = the minimal validated toolkit ONLY (vents + cover-on-reply + kill-memory), one combined re-record.
- Balance: retune-first (Wave 2, task-clock) → task-gating sabotage as the structural follow-up (Wave 3).
- Self-report DEFERRED (rides after Wave 1, needs an R4 ballot-target/railroad guard) — not in this phase's
  Waves 0–1.
- FROZEN throughout Waves 0–1: the §4.6 vote gate render + threshold, the tally + tie→SKIP rule, the
  2048/1024 turn/vote caps, the §6.3 accumulator constants (+0.05/−0.05/25% decay), and the TASK CLOCK
  (Wave 1 is deception, not balance). The firewall (roles/teammates/kill-attribution never leak) and
  byte-identical determinism are inviolable.
- Gate: the win split is EXCLUDED from every gate; progress is gated on the interestingness score
  (Wave 1 → R2 up; Wave 2 → eject-decided share > 0 / R1 up; Wave 3 → R5 ≥3 win shapes) and the substrate
  HARD checks (game_over, firewall/leak, byte-reconstruction).

Sequencing (the file-scope validator forces it): 11.1 is the wave root; 11.3 depends on 11.1 (shares the
SelfView/packet/service/perception self-channel seam); 11.2 is file-disjoint (prompt layer) and dispatches
in parallel; 11.4 is the operator re-record after all three. Track with
`python3 scripts/compute_next_task.py --phase 11`.

## Wave 0 — Interestingness ruler (DONE 2026-06-15, offline, no dispatch)

Score the rubric so "interesting" is measurable and decoupled from the win split. DONE in the design thread
(offline, $0) and committed @ f66de84 — `experiments/lab/rubric_score.py` gained `interestingness()` /
`_game_interestingness()` (per-game 0–100 = 0.35·R1 decisive + 0.25·R2 deception + 0.20·R3 arcs + 0.20·R7
legible) + a set-level R5 win-shape diversity summary; `report-rubric-interestingness.md` records the W2
baseline (mean 38.2, 0/50 eject-decided, R5 = 2 shapes) — the number Waves 1–3 must move. It is the primary
success metric for the rest of the phase; the win split is demoted to a sentinel. No re-record (reads
committed replays); re-run on each wave's re-record via
`uv run python experiments/lab/rubric_score.py FACTS_JSON`.

## Wave 1 — Deception works (R2): the minimal validated toolkit

### Task 11.1 — Wire vents into the impostor policy
**Branch:** `phase-11-impostor-vents`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §1.3 (observation firewall), §3.4 (vents/visibility); experiments/lab/report-vent-escape-lab.md
**Complexity:** Integration

The impostor FSM (`agents/tactical/impostor_policy.py`) emits only Kill/Move/DoTask/Wait, so the impostor
walks away from every kill and is SEEN — the offline counterfactual proved ~91% of the structured evidence
against impostors (35→3 flags) is exactly this post-kill sighting trail, which a vent would hide. The engine
already supports vents end-to-end (VERIFIED: `engine/tick.py:452-453` dispatches `VentAction` →
`_apply_vent`; `engine/rules.py:102-179` `resolve_vent`; 6 vents in `engine/maps/canonical_1.yaml:218-260`;
`orchestrator/boundary.py` round-trips any intent generically), so this task is policy logic + a self-state
field — NO engine or boundary edit. Add the impostor's vent decision: (a) POST-KILL VENT-ENTER — redesign
the COVER branch (`impostor_policy.py:196-198`, currently a move to the alphabetically-first neighbor) to
emit `VentIntent` when a vent is in the impostor's room, the impostor is not already `in_vent`, and NO
non-teammate witness is co-present this tick (reuse the kill gate's `latest_events` `saw_player` scan,
`impostor_policy.py:359-470` pattern; teammates in `fellow_impostor_ids` never count as witnesses) — else
fall back to the existing move-away; (b) IN-VENT VENT-EXIT — a new high-priority branch (gated on
`in_vent`, before the body/kill logic) that emits `VentIntent` to a connected vent whose room holds no
visible body, preferring the room toward the current best isolated target (`_scored_targets`), else the
alphabetically-first connected vent (deterministic, id/room-sorted, no RNG). `heard_vent_use` stays
observable (`observation/service.py` audible events), so a careless vent near a witness is a NEW catchable
tell — desirable (rubric R2 "deception sometimes fails"), do not suppress it beyond the witness guard above.
The impostor reads its own `in_vent` from a new `SelfView.in_vent` bool (the one shared-file seam with 11.3).

**Files in scope:**
- agents/tactical/impostor_policy.py (the COVER-or-vent rewrite, the in-vent vent-exit branch, a `_vent(vent_id)` intent builder mirroring `_kill`, a room→vent lookup over the public map's vent_rooms/vent_graph, and the FSM docstring update; all tie-breaks deterministic)
- observation/packet.py (add `in_vent: bool` to `SelfView` — a non-role-bearing self-state bool, firewall-clean)
- observation/service.py (populate `SelfView.in_vent` from `player.in_vent` at the self-view build)
- agents/perception.py (carry `in_vent` through the self-state payload)
- tests/agents/test_impostor_policy.py (the acceptance pins below; the `_public_map` helper currently sets vent_graph/vent_rooms empty — populate them)
- tests/observation/test_service.py + tests/observation/test_leak_property.py (in_vent surfaces only on SelfView; never leaks)

**Files NOT in scope:**
- engine/** (resolve_vent/_apply_vent/visibility VERIFIED correct — no engine edit)
- agents/strategic/prompts/**, meetings/** (11.2 owns prompt wiring)
- agents/memory/store.py (11.3 owns the kill-memory render)
- replays/samples/**, tests/fixtures/** (re-record is 11.4)

**Definition of done:**
- Vent-enter fires at the body when the impostor is alone (no non-teammate co-present), is suppressed when a non-teammate witness is co-present (falls back to move-away), and is skipped when no vent is in the room.
- In-vent vent-exit moves toward an isolated / non-body room; all choices deterministic and replay-stable.
- `SelfView.in_vent` is populated; the leak sweep confirms it appears only on the recipient's own SelfView.
- `bash scripts/check.sh` green; firewall + leak-property sweeps pass; no impostor can be left pathologically stuck in a vent (an in-vent impostor always has an exit branch).

**Public types introduced:**
- `observation.packet.SelfView.in_vent` (new field on the existing privileged self channel)

**Implementation hint:**
Reuse the existing co-presence/witness scan the kill gate already runs on `latest_events` rather than a
parallel scan, so "no witness" means the same thing for kill and for vent. The vent-enter guard should
prefer a quiet WALK over a vent only when a walk is genuinely unseen; when a witness is already present, a
vent and a walk are equivalent exposure, so keep the simpler move-away fallback. Do not add a kill-cooldown
interaction (venting does not set cooldown) — the body-in-own-room check already precedes the kill check, so
vent-cover never competes with a same-tick kill.

**Integration risk:**
The shared SelfView/packet/service/perception edit with 11.3 is the dependency edge (11.3 depends on this
task) — keep `in_vent` a plain bool so 11.3's `own_kill` addition is orthogonal. A vent changes recorded
bytes for policy-driven sample runs (handled at 11.4), but NOT the hand-scripted determinism/firewall
fixtures (action-driven, recomputed at runtime). Watch for an impostor that vents every tick and never
kills — the exit branch must resume normal stalking once repositioned.

**Ready-to-paste prompt:** `agent_prompts/task-11-1-impostor-vents.md`

### Task 11.3 — Kill-memory privileged self-channel (legibility)
**Branch:** `phase-11-kill-memory`
**Depends on:** 11.1 (shares the SelfView/packet/service/perception self-channel seam; sequence after it)
**Section refs:** DESIGN.md §1.3 (firewall), §6.2 (memory rendering); experiments/lab/report-memory-fix-probe.md
**Complexity:** Integration

An impostor's own kill is never recorded as a kill: `engine/rules.py:96` excludes the actor from its own
kill's witnesses, so `observation/service.py:306-307` (a kill is observed only `if agent_id in
event.witnesses`) never logs it, and the body it created surfaces through the ordinary `saw_body` channel as
"You discovered {victim}'s body in {room}" (`agents/memory/store.py:493`) — the killer narrates finding the
body it made. Surface the kill as an explicit PRIVILEGED self-channel line. SCOPE HONESTY: the memory-fix
probe FALSIFIED this as a survival/deflection lever (self-flags 17→17 — they come from OTHERS' sightings the
impostor never saw, not its own memory); ship it for LEGIBILITY only and claim NO interestingness-score
movement from it. The channel MUST be on `SelfView`, not `PlayerView` (VERIFIED: `eval/leak_test.py:115-128`
requires every visible kill/vent action to be witness-permitted, and the killer is excluded from its own
witnesses — a PlayerView kill action would fail the leak test; `SelfView` is the established privileged
channel where role/fellow_impostor_ids live).

**Files in scope:**
- observation/packet.py (new `OwnKillView{victim_id: PlayerId, room: RoomId}`; `SelfView.own_kill: OwnKillView | None`. `victim_id` is leak-allowed per the BodyView precedent; no role-bearing field names)
- observation/service.py (populate `own_kill` in the KilledEvent path ONLY when `event.actor == agent_id`, WITHOUT the witness gate — by construction it is never in any other agent's packet)
- agents/perception.py (ingest a new `EVENT_OWN_KILL` episodic event from `packet.self_state.own_kill`)
- agents/memory/store.py (render "[tick N] You (IMPOSTOR) killed {victim} in {room}." at a new salience above witnessed-kill; SUPPRESS the self-victim `saw_body` line — collect own-kill victim ids up front like the existing body-sightings set and skip the "discovered ... body" render for the killer's own victim)
- tests/observation/test_leak_property.py + tests/test_firewall.py (every crewmate packet has `own_kill is None`; the kill string is produced only in store rendering, never in packet JSON)
- tests/agents/test_memory_store.py (the killer's memory shows the kill line and NOT the self-victim "discovered body" line)

**Files NOT in scope:**
- engine/** (the witness-exclusion is correct as-is; this task reads the KilledEvent, it does not change kill resolution)
- agents/tactical/** , agents/strategic/prompts/** , meetings/**
- replays/samples/**, tests/fixtures/** (re-record is 11.4)

**Definition of done:**
- The killer's rendered memory reads "You (IMPOSTOR) killed {victim} in {room}" for its own victim and no
  longer renders that victim as a discovered body; other bodies render normally.
- `SelfView.own_kill` is populated only for the actor; the leak sweep + firewall test confirm crewmate (and
  fellow-impostor) packets never carry another agent's `own_kill`, and no packet JSON contains the substring
  "impostor" outside `self_state.role`.
- `bash scripts/check.sh` green.

**Public types introduced:**
- `observation.packet.OwnKillView`

**Implementation hint:**
Model `OwnKillView` exactly on the existing privileged self-state pattern (`SelfView.role` /
`fellow_impostor_ids`) — populated for the entitled recipient only, never mirrored into `PlayerView`. In the
store, suppress the self-victim body line by reusing the up-front body-sightings collection rather than a
second pass, so the salience ordering and dedup stay intact.

**Integration risk:**
This shares packet.py/service.py/perception.py with 11.1 — the depends-on edge above serializes them; keep
`own_kill` orthogonal to `in_vent`. It changes recorded bytes for policy-driven runs (11.4) but the
event-driven memory golden (`impostor_minimal.*`) is unaffected (no own-kill event in its hand-authored
events) — grep for any observation/packet golden pinning the SelfView shape and regenerate if found.

**Ready-to-paste prompt:** `agent_prompts/task-11-3-kill-memory-self-channel.md`

### Task 11.2 — Cover-consistency directive on the reply turn
**Branch:** `phase-11-cover-on-reply`
**Depends on:** none (prompt layer; file-disjoint from the policy and self-channel work)
**Section refs:** DESIGN.md §5.2 (accusation round); experiments/lab/report-vent-escape-lab.md (the 3 residual self-pair-drift flags)
**Complexity:** Integration

The impostor "cover" directive ("DECIDE on ONE room and tick-window AWAY from the body's room and the tick
it happened; state the SAME room and window every time you are asked; never place yourself in the body's
room") is stranded at `agents/strategic/prompts/impostor_report.j2:115-124`, gated on the body-report
OPENING that impostors never take — so on the REPLY turn (the only turn an impostor speaks) it gets no cover
guidance, and its account drifts across turns (the residual `alibi_conflict` self-pair flags the vent fix
cannot remove). Port the directive into the `accusation_round.j2` reply branch, gated on the impostor role.
VERIFIED current state: `accusation_round` is at v7 (`DEFAULT_PROMPT_VERSIONS` `orchestrator/game.py:226`;
template header `version: 7`); the reply branch is `{% if turn_kind == "reply" %}` at `accusation_round.j2:79`;
`participant.role` is available at `meetings/manager.py:1379`.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2 (add an `{% if is_impostor %}` cover block inside the reply branch porting the impostor_report directive — generic, never naming a teammate; bump the version marker to v8)
- agents/strategic/prompts/loader.py (add `is_impostor: bool = False` to `accusation_round_prompt`, threaded to the render)
- meetings/manager.py (the StatementPromptRenderer Protocol + `_render_turn_prompt` reply path: pass `is_impostor=(participant.role == "IMPOSTOR")`; default False keeps the crewmate_report conformance)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS`: accusation_round v7 → v8, with a dated comment paragraph)
- tests/agents/test_strategic_prompts.py (version pins v7→v8; the impostor reply renders the cover block, the crewmate reply and the opt_in branch do not, and a raw render without `is_impostor` validates under StrictUndefined)

**Files NOT in scope:**
- the §4.6 vote-gate render (FROZEN), vote_ballot.j2, crewmate_report.j2 content
- agents/tactical/**, observation/**, agents/memory/** (11.1/11.3 own those)
- tests/fixtures/prompt_regression/baseline.json (moves only at the 11.4 re-record — it reads versions from the recorded replays, still v7 until then)

**Definition of done:**
- An impostor reply renders the cover directive; crewmate replies and opt-in turns do not.
- accusation_round is v8 across the template marker, `DEFAULT_PROMPT_VERSIONS`, and the version test pins.
- `uv run python scripts/generate_prompts.py --check` clean (the paste-ready prompt regenerated).
- `bash scripts/check.sh` green; do NOT touch `baseline.json` (it moves at 11.4).

**Implementation hint:**
Add an explicit `is_impostor` kwarg rather than reusing `fellow_impostor_ids` — a SOLE impostor has empty
fellows but must still get the directive (mirroring how impostor_report fires for sole impostors). Scope the
block to the reply branch only (the lab residual is opening↔reply drift; opt-in is terminal). Reuse the
exact directive text from impostor_report.j2 so the two paths stay one wording.

**Integration risk:**
The version fan-out (template marker + DEFAULT_PROMPT_VERSIONS + the live-version smoke test) must move
together or generate_prompts --check / the version test fails. The recorded replays still carry v7 until
11.4, so the prompt-regression baseline must NOT be regenerated in this task.

**Ready-to-paste prompt:** `agent_prompts/task-11-2-cover-on-reply.md`

### Task 11.4 — Wave-1 combined re-record and gate
**Branch:** `phase-11-wave1-rerecord`
**Depends on:** 11.1, 11.3, 11.2
**Section refs:** tasks/phase-10.md (the 10.5/10.9 re-record protocol); experiments/lab/report-rubric-interestingness.md
**Complexity:** Integration

After 11.1/11.2/11.3 merge, ONE combined re-record of BOTH sample sets (flat 4p/1i + 9p2i) on qwen3.5:9b,
smoke-first — never per-task. Then regenerate the determinism/prompt-regression fixtures and gate on the
interestingness score (R2), not the win split.

**Files in scope:**
- replays/samples/** (both sets re-recorded; MANIFEST + tournament-eval-report.json rebuilt)
- tests/fixtures/prompt_regression/** (baseline.json + v_a/v_b rebuilt from the fresh recorded bytes; the recorded accusation_round version shifts v7→v8 here)
- any committed observation/memory golden whose SelfView shape changed (regenerate if 11.1/11.3 added fields to a pinned fixture)

**Files NOT in scope:**
- all production source (frozen at the merge of 11.1/11.2/11.3 — a re-record changes data, not code)
- the §4.6 gate / tally / caps / §6.3 constants / task clock (FROZEN through Wave 1)

**Definition of done:**
- Smoke-first: 3 meeting-bearing 9p2i seeds dry-run→live; confirm meeting_rate, `grep VentEntered` > 0, and no impostor stuck in a vent, before the full run (STOP-and-escalate if a turn truncates or a vent loops).
- Full re-record of both sets; `scripts/verify_samples.sh` byte-reconstructs both (the state-hash determinism gate); `determinism` + firewall/leak sweeps green.
- HARD substrate gate: game_over 100%, friendly-fire 0, betrayal 0, byte-identical ×2, inversions 0.
- `uv run python experiments/lab/rubric_score.py` on the fresh facts shows R2 UP (accused-impostor survival ↑, impostor flag-clean ↑) vs the W2 baseline (mean 38.2); R1/clock untouched (Wave 1 is deception, not balance).
- Re-run the close audit on the new 9p2i set; verdict stays substrate-VALID with no new degeneracy.

**Implementation hint:**
Mirror the 10.9 protocol exactly (smoke STOP-for-go, then `scripts/refresh_samples.sh --full`,
`AILIBI_LLM_PROVIDER=ollama`). The prompt-regression v_b reconstruction shifts when the recorded versions
move to v8 — update the attribution asserts deliberately, not silently.

**Integration risk:**
This is the only task that rewrites committed bytes; a determinism break here means an upstream
non-determinism slipped in (vent tie-break RNG, unsorted set iteration) — bisect against 11.1's sort keys.
Spend is $0 (ollama); smoke 3 seeds before the multi-hour full run.

**Ready-to-paste prompt:** `agent_prompts/task-11-4-wave1-rerecord.md`

## Merge Criteria (Phase 11 Wave 1 — deception works)

- 11.1/11.2/11.3 each merge with `bash scripts/check.sh` green + the firewall and leak-property sweeps
  passing; no production change touches the FROZEN list (§4.6 render/threshold, tally + tie→SKIP, 2048/1024
  caps, §6.3 constants, the task clock).
- 11.4 is the sole re-record: both sets byte-reconstruct, the HARD substrate gate is green, and the
  interestingness score's R2 component rises off the W2 baseline (deception now works — accused impostors
  survive via vents) without R4 regressions (no railroads; firewall intact).
- The close audit re-run confirms the baseline stays VALID; its findings + the new R2 number set up Wave 3
  below. (Wave 1 over-delivered — eject-decided 0→6/50 and R5 hit 3 shapes — so the owner promoted the
  structural sabotage wave ahead of the now-deferred, held-in-reserve task-clock retune.)

## Wave 3 — Structural counterplay: task-gating sabotage

The sabotage subsystem is ~fully built (resolve_sabotage / resolve_repair_sabotage, the `IMPOSTOR_SABOTAGE`
win condition that fires on `active && remaining_ticks==0` in the §3.5 order, and the PUBLIC alarm +
`GlobalView.sabotage_active/kind` broadcast — all wired and tested). Two links are missing: no policy emits
`SabotageIntent`, and no sabotage gates the task race (`lights` only degrades visibility; `_apply_do_task` /
`_advance_tasks` never read `state.sabotage`). Wave 3 adds a new `reactor` task-gating sabotage + the
impostor emitter + crew repair, so the dormant impostor win becomes a live, contestable clock lever —
balance that emerges from PLAY. Gate: rubric **R1 + R5 (≥3 win shapes)**, NOT the win split. FROZEN: §4.6
render/threshold, tally + tie→SKIP, 2048/1024 caps, §6.3 constants, AND the task clock (the reactor timer is
a sabotage parameter, explicitly NOT `tasks_per_crewmate`/task durations). Sequencing (file-scope validator):
11.5 (root) → {11.6 crew ∥ 11.7 impostor} (file-disjoint policies, both depend on 11.5's public channel) →
11.8 re-record.

### Task 11.5 — Task-gating sabotage: engine gate + reactor kind + public repair channel
**Branch:** `phase-11-task-gating-sabotage`
**Depends on:** none (wave root)
**Section refs:** DESIGN.md §3.1 (tick loop), §3.5 (win order), §8.3 (sabotage); engine/win_conditions.py:30-35 (the dormant IMPOSTOR_SABOTAGE)
**Complexity:** Integration

Make a sabotage able to STALL the task race and surface its repair location publicly. ADD A NEW KIND
`reactor` (do NOT repurpose `lights`, which is load-bearing for the visibility system) declared in
`engine/maps/canonical_1.yaml` under `sabotages:` with a short fix-or-impostors-win `duration_ticks` (anchor
it to the map diameter — CAFETERIA→REACTOR hop count + `repair_ticks` — the way
`IMPOSTOR_PRETEND_TASK_DWELL_TICKS` is diameter-anchored; document the anchor in a YAML comment; it is NOT
the frozen task clock), `affected_visibility: same_room_and_adjacent` (base mode — reactor contests the
clock, not sightlines), two `repair_rooms` (e.g. REACTOR + ENGINEERING), and a new optional defaulted field
`gates_tasks: bool = False` on `SabotageDefinition` (so gating is declared in data, not by string-matching
`kind`, which the codebase deliberately avoids). Add `_tasks_gated(state, game_map)` returning
`sab.active and game_map.sabotages[sab.kind].gates_tasks`, and gate BOTH task paths: `_apply_do_task`
(reject with an `ActionRejectedError` when gated) and `_advance_tasks` (skip the progress increment / no
`TaskProgressed` event when gated). Thread `game_map` into both (the other appliers already receive it from
`_apply_action`/`advance_tick`). **No `engine/win_conditions.py` change** — `IMPOSTOR_SABOTAGE` already
fires on `active && remaining_ticks==0`; it becomes live purely through emission (11.7) + the short timer +
the gate. Surface the active sabotage's repair rooms + gating flag on the PUBLIC, role-blind `GlobalView`
so the crew (11.6) can route without `agents/`→`engine/` coupling.

**Files in scope:**
- engine/world.py (add `gates_tasks: bool = False` to `SabotageDefinition`; default keeps the loader contract byte-stable)
- engine/maps/canonical_1.yaml (add the `reactor` entry under `sabotages:`; do NOT touch the `tasks:` block / clock or the `lights` entry)
- engine/tick.py (the `_tasks_gated` helper; thread `game_map` into `_apply_do_task` + `_advance_tasks`; gate both the initiation and continuation paths; leave `_apply_sabotage`/`_advance_sabotage`/the win check unchanged)
- observation/packet.py (add `sabotage_repair_rooms: tuple[RoomId, ...] = ()` and `sabotage_is_gating: bool = False` to `GlobalView` — public, role-blind)
- observation/service.py (`_global_view`: populate the two new fields from `game_map.sabotages[kind]` when a sabotage is active)
- agents/perception.py (carry the two new fields through the `global_status` payload)
- tests/engine/test_tick.py (a `do_task` is rejected while a gating sabotage is active via BOTH paths; non-gating `lights` does NOT gate; repair clears the gate; IMPOSTOR_SABOTAGE fires end-to-end under a short reactor timer; same-tick repair still saves the crew)
- tests/engine/test_map_loader.py (the `reactor` kind loads; `gates_tasks` defaults False for `lights`)
- tests/observation/test_service.py (the new GlobalView fields populate only when a sabotage is active; default empty/false otherwise)

**Files NOT in scope:**
- agents/tactical/** (11.6/11.7 own the policies)
- engine/win_conditions.py (already correct — IMPOSTOR_SABOTAGE fires on active && remaining==0; no edit)
- engine/visibility.py (reactor uses base visibility — no visibility change)
- replays/samples/**, tests/fixtures/** (re-record is 11.8)
- the FROZEN list (§4.6 gate/threshold, tally/tie→SKIP, 2048/1024 caps, §6.3 constants, the task clock)

**Definition of done:**
- A gating sabotage halts task progress through BOTH `_apply_do_task` (rejection) and `_advance_tasks` (no progress event) while active; `lights` (non-gating) leaves task progress byte-identical to today.
- A reactor sabotage left to `remaining_ticks==0` with `active` true yields `IMPOSTOR_SABOTAGE`; a repair completing on the timer-expiry tick still saves the crew (the existing same-tick test still passes).
- `GlobalView.sabotage_repair_rooms`/`sabotage_is_gating` populate only when active and are identical across roles (leak-clean).
- `bash scripts/check.sh` green; firewall + leak-property sweeps pass.

**Public types introduced:**
- `observation.packet.GlobalView.sabotage_repair_rooms`
- `observation.packet.GlobalView.sabotage_is_gating`

**Implementation hint:**
Make `_tasks_gated` the single source of truth so the two task paths cannot drift. Thread `game_map` as a
pure pass-through (the other appliers already get it). Anchor reactor `duration_ticks` to map geometry and
document it; it is a sabotage timer, not the frozen task clock. Keep `gates_tasks` defaulted so `lights` and
every existing map-loader pin stay byte-stable.

**Integration risk:**
The `game_map` signature change touches the hottest engine path — keep it a pure pass-through and confirm
the hand-scripted determinism/firewall fixtures (action-driven) still recompute identically (they are NOT
re-recorded; only policy-driven samples change, handled at 11.8). A reactor timer set too low is unwinnable
for crew, too high is unreachable — derive from geometry and validate at the 11.8 smoke; do NOT tune the
frozen task clock to compensate.

**Ready-to-paste prompt:** `agent_prompts/task-11-5-task-gating-sabotage.md`

### Task 11.6 — Crew repair behavior in the crewmate policy
**Branch:** `phase-11-crew-repair`
**Depends on:** 11.5 (consumes the new public GlobalView repair-rooms / gating channel)
**Section refs:** DESIGN.md §1.3 (firewall), §4.4 (crewmate FSM)
**Complexity:** Integration

Give the crew a reason to respond to a gating sabotage. The crewmate FSM (`crewmate_policy.py`) is a
priority cascade; add a REPAIR_SABOTAGE interrupt BELOW the body/kill interrupts (a meeting ends the round
anyway) but ABOVE the suspicion-walk and task routing (an unrepaired gating sabotage is a hard loss timer).
Detect via the freshest `global_status` (`sabotage_active`, `sabotage_kind`, and the new public
`sabotage_repair_rooms`/`sabotage_is_gating`) — reuse the existing memory-accessor pattern; the policy is
engine-free, so it reads repair rooms ONLY from the public `GlobalView` channel, never importing from
`engine/` and never hardcoding room names. When an active GATING sabotage exists: take one deterministic A*
step toward the nearest surfaced repair room (sorted-id tie-break), and emit `RepairSabotageIntent(kind)`
once in a repair room. Scope the diversion to `sabotage_is_gating` so `lights`-only games stay byte-identical.

**Files in scope:**
- agents/tactical/crewmate_policy.py (the REPAIR_SABOTAGE interrupt; an `_active_gating_sabotage(events)` accessor over the freshest `global_status`; a `_repair(kind)` intent builder mirroring `_do_task`; deterministic nearest-repair-room A* routing; docstring update; add `RepairSabotageIntent` to the action-intent import)
- tests/agents/test_crewmate_policy.py (the crewmate diverts + emits `RepairSabotageIntent` only for an active gating sabotage; ignores non-gating `lights`; deterministic room choice; body/kill interrupts still pre-empt repair)
- tests/observation/test_leak_property.py (the new GlobalView sabotage fields never differ by role; never carry role-bearing substrings)
- tests/api/test_leak.py (same role-invariance assertion through the packet API)

**Files NOT in scope:**
- engine/**, observation/** (11.5 owns the engine + the public channel)
- agents/tactical/impostor_policy.py (11.7)
- replays/samples/**, tests/fixtures/** (11.8)
- the FROZEN list

**Definition of done:**
- A crewmate observing an active gating sabotage walks one A* step/tick toward the nearest surfaced repair room and emits `RepairSabotageIntent(kind)` once there; the choice is deterministic and replay-stable.
- A non-gating sabotage (`lights`) does NOT trigger the diversion (lights-era crew behavior byte-identical).
- BODY_VISIBLE and KILL_WITNESSED interrupts still out-prioritize repair; the policy stays a pure function of memory + `PublicMapView` + `GlobalView`.
- `bash scripts/check.sh` green; the leak sweep confirms the new fields are role-invariant.

**Implementation hint:**
Mirror the existing accessor/interrupt structure and the deterministic min-hop tie-break used in
`ImpostorPolicy._choose_exit_vent`. Read repair rooms from the public `GlobalView` only. No cross-tick
tracker is needed — re-read the active-sabotage signal fresh each tick.

**Integration risk:**
Changes recorded bytes for policy-driven samples (11.8), not the hand-scripted fixtures. Watch for a
crewmate ping-ponging between equidistant repair rooms — the sorted tie-break must make the choice stable
across ticks. Keep the diversion gated on `sabotage_is_gating` so lights-only games stay byte-identical and
R5 attribution stays clean.

**Ready-to-paste prompt:** `agent_prompts/task-11-6-crew-repair.md`

### Task 11.7 — Impostor SabotageIntent emission in the impostor policy
**Branch:** `phase-11-impostor-sabotage`
**Depends on:** 11.5 (needs the working gating target + reads the public GlobalView task/sabotage fields)
**Section refs:** DESIGN.md §3.4 (impostor actions), §4.4 (impostor FSM); experiments/lab/report-vent-escape-lab.md (the 11.1 vent-wiring precedent)
**Complexity:** Integration

Make the impostor USE the lever. Mirror the 11.1 vent wiring: a new SABOTAGE branch in the `decide` cascade,
placed BELOW the in-vent-exit and COVER-or-vent branches but ABOVE the kill/stalk block, with a
`_sabotage(kind)` intent builder mirroring `_kill`/`_vent` and the FSM docstring updated. Trigger
deterministically from already-observed signals: emit `SabotageIntent("reactor")` when no sabotage is
active (guard via the public `global_status`) AND the crew is near a task win (read `tasks_completed`/
`tasks_total` from `global_status`, threshold anchored to "imminent crew win") — the strongest structural
use: it converts a near-certain task-win into a forced crew scramble + a hard loss timer. Keep it
conservative (do NOT sabotage every cooldown tick — that starves kills and is a degenerate low-interest
pattern); the impostor still hunts. The predicate MUST be a pure function of observed `global_status`/
`cooldown_status` (no RNG, no module state) so replays stay byte-identical.

**Files in scope:**
- agents/tactical/impostor_policy.py (the SABOTAGE branch; an `_active_sabotage(events)` guard; a `_sabotage(kind)` intent builder mirroring `_kill`/`_vent`; the deterministic trigger predicate over `global_status`; FSM docstring update; add `SabotageIntent` to the action-intent import)
- tests/agents/test_impostor_policy.py (emits `SabotageIntent("reactor")` when the crew is near a task win and no sabotage is active; does NOT emit when one is already active; the predicate is a pure function of observed `global_status`; in-vent/COVER/kill still pre-empt sabotage; sole- and multi-impostor cases)

**Files NOT in scope:**
- engine/**, observation/** (11.5)
- agents/tactical/crewmate_policy.py (11.6)
- agents/strategic/prompts/**, meetings/** (no meeting-layer change this wave)
- replays/samples/**, tests/fixtures/** (11.8)
- the FROZEN list

**Definition of done:**
- The impostor emits `SabotageIntent("reactor")` strategically (primary: deny an imminent crew task win; the predicate is deterministic + documented), never when a sabotage is already active, and never as per-tick spam that starves kills.
- In-vent exit, COVER-or-vent, and an available kill all out-prioritize sabotage; the decision stays a pure function of memory + `PublicMapView`.
- `bash scripts/check.sh` green.

**Implementation hint:**
Mirror the 11.1 vent wiring (a new cascade branch + an intent builder + a docstring rewrite), reading only
memory/`PublicMapView`, all tie-breaks deterministic, no RNG. Anchor the task-completion threshold to
"imminent crew win" and document the anchor. Avoid the degenerate "sabotage every cooldown tick" loop.

**Integration risk:**
Shares no file with 11.6, so they parallelize after 11.5. The danger is a low-interestingness degenerate
loop (sabotage-spam or sabotage-then-camp) — keep the predicate conservative and verify at 11.8 that R5
diversity RISES (a new IMPOSTOR_SABOTAGE shape appears) rather than collapsing into a farmed pattern.
Changes recorded bytes (11.8), not the hand-scripted fixtures.

**Ready-to-paste prompt:** `agent_prompts/task-11-7-impostor-sabotage.md`

### Task 11.8 — Wave-3 combined re-record, era-pin re-anchor, and rubric gate
**Branch:** `phase-11-wave3-rerecord`
**Depends on:** 11.4, 11.5, 11.6, 11.7
**Section refs:** tasks/phase-11.md Task 11.4 (the Wave-1 re-record + 39-test re-anchor protocol, commits 853a601/9753a4b); experiments/lab/report-rubric-interestingness.md
**Complexity:** Integration

After 11.5/11.6/11.7 merge, ONE combined re-record of both sample sets (flat 4p/1i + 9p2i) on qwen3.5:9b,
smoke-first, then re-anchor the committed-bytes era-pin tests to the new baseline (the 11.4 cadence) and
gate on the interestingness score (R1 + R5), not the win split.

**Files in scope:**
- replays/samples/** (both sets re-recorded; each MANIFEST + tournament-eval-report.json rebuilt)
- tests/eval/test_balance_eval.py, tests/eval/test_win_condition_selfcheck.py, tests/eval/test_gate_metrics.py, tests/eval/test_gate_spec_metrics.py, tests/eval/test_wave2_metrics.py (era-pin re-anchor to the new baseline)
- tests/meetings/test_transcript.py, tests/meetings/test_manager.py, tests/agents/test_beliefs.py (committed-bytes detector/fold pins re-anchored)
- tests/scripts/test_manifest_writer.py, tests/scripts/test_refresh_samples.py, tests/api/test_eval.py (manifest/version + meetings-seed-list pins re-anchored)
- any committed observation/memory golden whose GlobalView shape changed (regenerate if 11.5's two new fields appear in a pinned packet fixture)

**Files NOT in scope:**
- all production source (frozen at the merge of 11.5/11.6/11.7 — a re-record changes data, not code)
- the §4.6 gate / tally / caps / §6.3 constants / the task clock (FROZEN)

**Definition of done:**
- Smoke-first: 3 meeting-bearing 9p2i seeds dry-run→live; confirm a sabotage actually fires (`grep SabotageStarted` > 0), the crew diverts to repair (`grep SabotageRepair` present), and at least one game ends `IMPOSTOR_SABOTAGE` or a gated task race flips an eject-decided/parity outcome — before the full run (STOP-and-escalate if a sabotage loops or none ever fires).
- Full re-record of both sets; `scripts/verify_samples.sh` byte-reconstructs both; the firewall/leak sweeps + win-condition selfcheck stay green.
- HARD substrate gate (the 11.4 standard): game_over 100%, friendly-fire 0, betrayal 0, byte-identical ×2, inversions 0.
- `uv run python experiments/lab/rubric_score.py` on the fresh facts shows **R1 holds/rises (eject-decided share) AND R5 ≥ 3 win shapes** with a new gating-attributable win shape; the win split is a sentinel, not a gate.
- Re-run the close audit on the new 9p2i set; verdict stays substrate-VALID with no sabotage-spam degeneracy.

**Implementation hint:**
Mirror the 11.4 protocol exactly: smoke STOP-for-go, then `scripts/refresh_samples.sh --full` for flat and
the `AILIBI_SAMPLE_DIR=replays/samples/9p2i ...` env for the 2i set, `AILIBI_LLM_PROVIDER=ollama` ($0).
Re-anchor the era-pin tests in a single deliberate commit after a byte-clean baseline (as 9753a4b followed
853a601) — update the expected hashes/versions to the new baseline; do NOT weaken the assertions.

**Integration risk:**
The only task that rewrites committed bytes; a determinism break means upstream non-determinism slipped in
(a sabotage tie-break RNG, unsorted repair-room iteration, or a `_tasks_gated` read depending on dict
order) — bisect against 11.5's helper and 11.6/11.7's sort keys. Spend is $0 (ollama); smoke 3 seeds before
the multi-hour full run. If R5 does not reach 3 shapes, the lever fires too rarely/degenerately — escalate
to re-anchor the reactor timer or the impostor trigger threshold (still NOT the frozen task clock), then
re-smoke.

**Ready-to-paste prompt:** `agent_prompts/task-11-8-wave3-rerecord.md`

## Merge Criteria (Phase 11 Wave 3 — structural counterplay)

- 11.5/11.6/11.7 each merge with `bash scripts/check.sh` green + the firewall/leak-property sweeps passing;
  no production change touches the FROZEN list (§4.6 render/threshold, tally + tie→SKIP, 2048/1024 caps,
  §6.3 constants, the task clock — the reactor timer is a sabotage parameter, not the clock).
- 11.8 is the sole re-record: both sets byte-reconstruct, the HARD substrate gate is green, and the
  interestingness score shows **R5 ≥ 3 win shapes with a new gating-attributable shape and R1 holding/rising**
  — without R4 regressions (no railroads; firewall intact; sabotage is role-blind public).
- The close audit re-run confirms the baseline stays VALID with no sabotage-spam degeneracy. With Wave 3
  landed, the task-clock retune remains a held-in-reserve final wave — applied only if the owner wants to
  push balance further, gated on the rubric, never on the win split.
