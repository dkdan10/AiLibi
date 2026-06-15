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
- The close audit re-run confirms the baseline stays VALID; its findings + the new R2 number set up Wave 2
  (the task-clock retune, gated on the interestingness R1 / eject-decided share, not the win split).
