# Phase 13.5 — Memory correctness: truth-up → substrate (before the Phase 14 model migration)

> **STATUS: AUTHORING (2026-06-25).** The complete memory-correctness work that precedes the
> Phase 14 model migration, in ONE phase. Grounded in the 2026-06-25 memory-pipeline diagnosis
> (workflow `wg54kfoxy`: 7 subsystem maps, 33 confirmed + 7 partial discrepancies, 3 prior claims
> refuted-as-already-fixed). Plan: `~/.claude/plans/i-want-to-create-twinkling-firefly.md`.

Goal: make the memory subsystem deliver CORRECT information to the model — fix the docs/dead-code
that mislead, then fix the substrate that collapses social/spoken information to a numeric scalar
(testimony never content, witnessed kill mints no flag, movement unperceived, rendered memory
frozen). Three waves, ordered by risk:

- **Wave A — doc reconciliation** (design-thread, not dispatched). Behavior-neutral.
- **Wave B — dead-code truth-up** (`13.5.1`). Behavior-neutral; `scripts/check.sh` only.
- **Wave C — correct-information substrate** (`13.5.2`–`13.5.5`). Behavior-CHANGING; each behind a
  config flag, validated by structural tests + a 9B SMOKE, **not** a 50-game R1 re-record.

Validation cadence is per-task, not per-phase: the neutral waves (A/B) change no recorded game
outcome and need **no eval** (`replays/samples/**` untouched; `verify_samples.sh` still byte-
identical); the substrate wave (C) is smoke-validated for correctness, with its gameplay value
measured for the first time on the new model in Phase 14's ONE combined re-record. The phase-end
gate is: substrate smoke green + byte-identical reconstruction + corrected-substrate 9B prompts
pinned as the Phase-14 reference.

---

## Wave A — Doc reconciliation (DESIGN-THREAD work, NOT a dispatched task)

The full `DESIGN.md` + `AGENT_IMPLEMENTATION.md` reconciliation is executed by the design thread,
**not** materialized as an `agent_prompts/` task — the prompt generator hard-codes
`Do not modify DESIGN.md` / `Do not modify AGENT_IMPLEMENTATION.md` into every prompt
(`scripts/generate_prompts.py::_constraints_for`), so a task whose job is to edit those files
cannot be expressed through it. `DESIGN.md` is the design thread's own artifact. Tracked here for
completeness; committed to main with the rest of 13.5.

Stale claims to reconcile against HEAD (anchor cases, not exhaustive — the owner chose the full
sweep):
- belief Rule 3 (corroboration) + Rule 5 (decay) marked **deferred** (`DESIGN.md:631, :633`;
  reading-note `:14–15`) but **live** (`agents/memory/beliefs.py` `CORROBORATION_SUSPICION_DELTA`,
  `MEETING_SUSPICION_DECAY_RATE`, applied in `apply_meeting_evidence_rules`) → flip to live.
- `"reported"` provenance documented on `EpisodicEvent` but never written; "working memory rebuilt
  each tick" (store unwired); per-tick coalescing, meeting memo, 4th strategic trigger
  (unimplemented); the hallucination-guard validator (correctly noted deferred — leave) → state
  each accurately.
- Agent-memory notes (non-repo) — **already truthed-up this session**: own-kill "discovered the
  body" bug is FIXED by Task 11.3; the impostor-info-ceiling "never emits vents/sabotage" claim is
  superseded by Phase 11. No further action.

---

## Wave B — Dead-code disposition (behavior-neutral, dispatched)

### Task 13.5.1 — Dead-code truth-up: relabel AgentRuntime + earmark WorkingMemory/alibi docstrings
**Branch:** `phase-13-5-dead-code-truthup`
**Depends on:** none
**Section refs:** the 2026-06-25 memory-pipeline diagnosis (workflow `wg54kfoxy`; the cited structures verified to have ZERO production writers — a NEUTRAL classification); agents/runtime.py; agents/memory/working.py; agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis`); agents/memory/store.py (the `last_seen` render hook); orchestrator/game.py (`TacticalAgent`, the real production agent)
**Complexity:** Small
**Files in scope:**
- agents/runtime.py
- agents/memory/working.py
- agents/memory/beliefs.py
- agents/memory/store.py
**Files NOT in scope:**
- tests/ — the relabel is docstring-only and keeps every public API byte-identical, so no test changes are needed; if a test breaks, STOP and report (the edit was not neutral)
- DESIGN.md and AGENT_IMPLEMENTATION.md — the doc reconciliation is the design thread's Wave A, not this task
- the substrate wiring — Wave C (13.5.2–13.5.5) wires these structures; this task only DOCUMENTS their current status and earmark, and must neither wire nor delete them

Three memory structures are wired into the composite memory surface but never written in
production (diagnosis-verified: zero non-test callers of `WorkingMemory.set_goal` /
`set_path` / `record_sighting` and `BeliefState.record_alibi`; `AgentRuntime` is a Phase-2 glue
stub whose `_choose_action` always returns `WaitIntent` and whose `_update_memory` is a no-op,
imported only by tests — the production agent is `orchestrator/game.py::TacticalAgent`). They are
NOT bugs and must NOT be deleted: they are the scaffolding Wave C wires (the alibi list ←
testimony-as-content; `working.last_seen` ← movement perception). This task makes the code
self-documenting about that status so a reader — and the Phase-14 migration author — is not
misled into thinking they are live or into deleting them. Strictly docstrings and `#` comments:
no logic, no signature, no public type, no render-output change.

Specifics: (1) `agents/runtime.py` — a loud module + class docstring stating `AgentRuntime` is a
TEST-ONLY harness (a Phase-2 scaffold), NOT the production agent, and naming
`orchestrator/game.py::TacticalAgent` as the real one; note `_choose_action` is a hardcoded
`WaitIntent` and `_update_memory` a no-op. (2) `agents/memory/working.py` — docstring states
`WorkingMemory` currently has no production writer (`_last_seen` is always empty at runtime) and
earmarks `last_seen` as wired by Wave C (movement perception). (3) `agents/memory/beliefs.py` —
docstrings on `record_alibi` and `PlayerBelief.alibis` state the list is written by no production
path and rendered nowhere today, earmarked for Wave C (testimony-as-content). (4)
`agents/memory/store.py` — a comment at the `last_seen` render hook noting the suffix never renders
today (no writer), populated by Wave C (movement perception).

**Definition of done:** `AgentRuntime` carries a module + class docstring identifying it as a
test-only harness and naming `orchestrator/game.py::TacticalAgent` as the production agent;
`WorkingMemory`, `record_alibi` / `PlayerBelief.alibis`, and the `store.py` `last_seen` hook each
carry a docstring or comment stating current dead status plus the Wave-C lever that will wire
them; NO logic, signature, public-type, or render-output change (a memory-render fixture is
byte-identical before and after); `git diff` shows only docstring/comment lines; the full
`scripts/check.sh` is green.
**Implementation hint:**
Before documenting anything as dead, CONFIRM zero production writers yourself —
`grep -rn "record_alibi\|set_goal\|set_path\|record_sighting" agents/ orchestrator/ meetings/ api/ | grep -v tests/`
and `grep -rn "AgentRuntime\|agents.runtime" --include=*.py . | grep -v tests/` — and if any
production writer exists, STOP and report (the diagnosis would be wrong). Edit only docstrings and
`#` comments; touch no executable line. Run a memory-render fixture test
(`tests/agents/test_memory_rendering.py`) before and after to confirm byte-identical output. The
relabel is in-place (a docstring); relocating `AgentRuntime` under `tests/` is OUT of scope (it
would change test imports and is not neutral).
**Ready-to-paste prompt:** `agent_prompts/task-13-5-1-dead-code-truthup.md`

---

## Wave C — Correct-information substrate (roadmap; behavior-CHANGING, smoke-validated)

The behavior-changing core. Each item is elaborated to a full `### Task` contract immediately
before dispatch (each depends on substrate interfaces the prior lever introduces, so the
contracts firm up as the spine lands). Each lever ships **behind a config flag** and must fit the
salience render budget (`DEFAULT_TOKEN_BUDGET=1500`, `agents/memory/store.py`) under the frozen
generation caps (turn 2048 / vote 1024). New content is framed for the model in the RENDERED memory
(self-describing lines from `store.py`) rather than a `.j2` edit where possible, to avoid a
prompt-version-bump cascade. Validation is structural tests + a 9B SMOKE (parse-success, leak suite,
meeting-rate ≥ 0.60, byte-identical reconstruction) — NOT a 50-game R1 re-record; gameplay value is
measured for the first time on the new model in Phase 14's combined re-record.

### Task 13.5.2 — Testimony as reported episodic content (+ wire alibi_map)
**Branch:** `phase-13-5-testimony-content`
**Depends on:** 13.5.1
**Section refs:** the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`; the "social info is a scalar, not content" root) + this file's Wave C; meetings/schemas.py (`MeetingTurn.claims`/`observations`, the `Claim`/`ObservationClaim` unions); meetings/manager.py (`derive_belief_evidence` / `extract_belief_evidence`, the scalar twin this mirrors, ~:2630-2740); agents/perception.py (`PROVENANCE_OBSERVED`/`INFERRED`); agents/memory/store.py (`absorb_meeting_evidence` ~:204, `render_for_prompt` ~:127, the `_SALIENCE_*` band, `_known_roster_ids`, `_latest_self_guard_fields`); agents/memory/beliefs.py (`record_alibi`, `PlayerBelief.alibis` — wired here, not modified); orchestrator/game.py (`extract_belief_evidence`→`absorb_meeting_evidence` per living agent, ~:1539); api/replay_loader.py (~:839-843); llm/provider.py (the `AILIBI_*` env-flag convention, ~:31)
**Complexity:** Integration
**Files in scope:**
- meetings/schemas.py
- meetings/manager.py
- agents/perception.py
- agents/memory/store.py
- orchestrator/game.py
- api/replay_loader.py
- tests/meetings/test_reported_testimony_derive.py
- tests/agents/test_reported_testimony.py
**Files NOT in scope:**
- the scalar belief path (`derive_belief_evidence` accused/corroborated/contradicted → `apply_meeting_evidence_rules`) — UNCHANGED. Reported content is additive narrative, never a suspicion Δ, so the §4.6 eject gate, decay, and the "no single signal ejects" principle are untouched
- agents/memory/beliefs.py — `record_alibi` / `PlayerBelief.alibis` already exist (earmarked by 13.5.1); this task CALLS `record_alibi` from the store ingest and READS `.alibis` to render, but does not modify the module
- agents/strategic/prompts/*.j2 — reported rows are self-framed as unverified claims in the rendered memory (`store.py`), so NO template edit and NO prompt-version bump; an explicit template directive is deferred to Phase-14 prompt authoring
- the witnessed-kill flag (13.5.3), movement (13.5.4), unfreeze-mid-meeting (13.5.5) — separate Wave-C tasks
- engine/ and the recorded replays — no engine change; reported-ingest derives purely from the recorded `MeetingResult`, so committed replays reconstruct byte-identically; NO re-record

Today a meeting moves only a scalar suspicion Δ (`absorb_meeting_evidence`); WHAT players said — who they placed where, who they accused, whose alibi they backed — evaporates when the meeting closes (`render_for_prompt` shows only first-hand `observed`/`inferred` rows + the suspicion table). This task gives each living agent a memory of public testimony: after a meeting the speakers' STRUCTURED claims/observations become `provenance="reported"` episodic rows, attributed to the speaker and self-framed as unverified claims, so the next round's prompt carries `[meeting] CLAIM by p-3 (unverified): saw p-5 in ELECTRICAL @ tick 12` — testimony the model weighs, not ground truth. It also finally populates the dead `alibi_map`. Owner decisions (locked 2026-06-25): (1) scope = structured claims + sightings only (`SawPlayerObservation`, `AlibiClaim`, `AccusationClaim`, `CorroborationClaim`); free-text is excluded. (2) firewall = FAITHFUL RECORD — reported content is PUBLIC speech, so it is NOT teammate-firewalled (an impostor records what was publicly said about its team); only the SCALAR suspicion firewall stays, unchanged (the impostor still accrues no suspicion Δ vs a teammate).

Pipeline, mirroring the scalar twin: (1) `meetings/schemas.py` — a frozen, engine-free `ReportedStatement` DTO (speaker, kind, subject, tick(s)/room). (2) `meetings/manager.py` — `derive_reported_testimony(result) -> tuple[ReportedStatement, ...]`, a pure replay-deterministic reduction of `result.transcript.turns`, sorted, roster-only, free-text dropped — sitting beside `derive_belief_evidence`. (3) `agents/perception.py` — `PROVENANCE_REPORTED` + an `EVENT_REPORTED_TESTIMONY` type. (4) `agents/memory/store.py` — `absorb_reported_testimony(memory, *, statements, ...)`: appends one `provenance="reported"` row per statement at the meeting-boundary tick (`_latest_self_state_tick + 1`, the tick `absorb_meeting_evidence` already uses), SKIPPING the recipient's own statements; for each `AlibiClaim` statement also calls `memory.beliefs.record_alibi(...)`; roster-only; NOT teammate-firewalled. (5) `store.py` render — `_build_observations` gains a reported branch (the self-framed `CLAIM by X (unverified): …` line) at a salience strictly BELOW first-hand (band ~20–40, under `_SALIENCE_SAW_PLAYER`=50, above `_SALIENCE_COOLDOWN_STATUS`=10), and the belief render surfaces the now-populated `alibi_map`. (6) `orchestrator/game.py` + `api/replay_loader.py` — call `absorb_reported_testimony` per LIVING agent in the SAME loop as `absorb_meeting_evidence`, gated on the flag. (7) flag `AILIBI_TESTIMONY_AS_CONTENT`, resolved once like `AILIBI_LLM_PROVIDER`, default OFF (= byte-identical to today); the 9B smoke + Phase-14 re-record run it ON.

**Definition of done:** `derive_reported_testimony` is a pure function of a `MeetingResult` (no engine/perception import; run twice → byte-identical; free-text excluded; only roster ids appear). With the flag ON, after a meeting each LIVING agent's memory carries `provenance="reported"` rows for OTHER speakers' structured claims/observations (never its own), self-framed as unverified claims, and `PlayerBelief.alibis` is populated for every `AlibiClaim` about a roster subject; the render shows reported lines BELOW first-hand observations (a budget-tight render sheds reported rows before first-hand sightings) and the alibi view renders. The scalar path is byte-identical (accused/corroborated/contradicted deltas, the §4.6 gate, decay) — reported content moves NO suspicion; the impostor scalar firewall is unchanged while reported CONTENT is NOT teammate-firewalled (a teammate-incriminating public statement DOES appear in an impostor's reported memory). Replay-deterministic: both `orchestrator/game.py` and `api/replay_loader.py` ingest per living agent; `scripts/verify_samples.sh` reconstructs the committed replays byte-identically. With the flag OFF every memory render and game outcome is byte-identical to pre-task HEAD (the regression boundary); the existing golden suite passes unchanged. New tests cover derivation (pure/deterministic/free-text-excluded/roster-only), ingest (own-statements skipped, alibi_map wired, NOT teammate-firewalled), render (reported below first-hand; flag-off byte-identical), and replay determinism. The PR description NOTES that DESIGN.md §6.1/§6.5 need a design-thread follow-up to mark reported-provenance + alibi_map as now-wired (this task must not edit DESIGN.md). Full `scripts/check.sh` green; a 9B smoke (3–5 seeds, flag ON) shows parse-success ≈ 100%, leak suite passing, meeting-rate ≥ 0.60, render within the 1500-tok budget, and byte-identical reconstruction.
**Implementation hint:**
Mirror the scalar twin exactly so determinism and the per-agent wiring come for free: put `derive_reported_testimony` beside `derive_belief_evidence` (reduced from the SAME `result.transcript`), and `absorb_reported_testimony` beside `absorb_meeting_evidence`, called from the SAME per-living-agent loops (`orchestrator/game.py` ~:1539, `api/replay_loader.py` ~:843) using the roster (`_known_roster_ids`) and own-id self channel (`_latest_self_guard_fields`) the scalar fold already reads — add NO new orchestrator channel. Append reported rows at the meeting-boundary tick so episodic non-decreasing-tick order holds and they render under a meeting tag. Read the flag once like `llm/provider.py` reads `AILIBI_LLM_PROVIDER`; default OFF. Salience is strictly below first-hand by construction — add a golden test that a budget-tight render drops reported rows before first-hand sightings. `meetings.schemas` is engine-free and already imported by `agents/memory/beliefs.py`, so importing it from `agents/` keeps the import-linter green. The leak suite must still pass — reported content is PUBLIC transcript speech and carries no role, but assert it. Do NOT edit any `.j2`: the `CLAIM by X (unverified)` framing lives in the rendered line, so flag-off output is byte-identical and no prompt version bumps.
**Public types introduced:**
- meetings.schemas.ReportedStatement
- meetings.manager.derive_reported_testimony
- agents.memory.store.absorb_reported_testimony
- agents.perception.PROVENANCE_REPORTED
**Integration risk:**
Cross-module, multi-consumer: a new episodic event type + provenance flows into the salience-budgeted render (token competition — the band must keep first-hand facts), the alibi_map render, and the live + replay per-agent folds (determinism). Behind `AILIBI_TESTIMONY_AS_CONTENT` (default OFF) so the merge is byte-identical and the existing golden/regression suite is untouched; the lever's gameplay value is measured for the first time on the new model in Phase 14's combined re-record, not here. The one hard invariant: reported content is ADDITIVE narrative — it must never touch the scalar suspicion graph, the §4.6 eject gate, or the teammate scalar firewall, so "no single signal ejects" and replay byte-identity both hold. The self-framing (`CLAIM … (unverified)`) is load-bearing: without it a weaker model may treat reported sightings as things it witnessed.
**Ready-to-paste prompt:** `agent_prompts/task-13-5-2-testimony-content.md`

### Task 13.5.3 — Witnessed kill becomes real evidence (witness belief + kill-scene STRONG flag)
**Branch:** `phase-13-5-witnessed-kill`
**Depends on:** 13.5.1
**Section refs:** the 2026-06-25 design-thread eyewitness-strength decision (a first-hand kill view makes the WITNESS near-certain); agents/memory/beliefs.py (`apply_observation_rules` Rule 4 vent precedent + `VENTING_SUSPICION_DELTA`, `apply_contradiction_rule`); observation/service.py (the witness-gated kill stamp `PlayerView.action == "kill"`, ~:351); meetings/transcript.py (`_detect_alibi_vs_physical` / `reconstruct_stated_paths` ~:833 / `detect_contradictions` ~:922 / `PHYSICAL_CONTRADICTION_MIN_VOICES` ~:517 / `WEAK_REASON_LONE_PHYSICAL` ~:502 / `triggering_body_rooms` / `is_weak_contradiction` ~:610); audits/workflows/extract_gameplay_facts.py (the $0 R7 re-extraction); [[project_ejection_suspicion_principle]]
**Complexity:** Integration
**Files in scope:**
- agents/memory/beliefs.py
- meetings/transcript.py
- tests/agents/test_beliefs.py
- tests/meetings/test_contradictions.py
**Files NOT in scope:**
- meetings/schemas.py, the LLM output schema, and agents/strategic/prompts/*.j2 — (b) REUSES the existing `alibi_vs_physical` kind + `reconstruct_stated_paths` with a kill-scene marker, NOT a new observation type or contradiction kind, so there is NO LLM-output-schema change and NO prompt-version-bump cascade. Literally surfacing "I witnessed the kill act" as a new public structured claim is the heavier alternative below; deferred.
- the scalar vote tally and the §4.6 gate value — unchanged; (a) moves suspicion through the existing perception rule, (b) through the unchanged `apply_contradiction_rule`
- engine/ and the recorded replays — re-extraction + a smoke only; NO re-record (the Phase-13 $0 R7 gate)
- 13.5.4 (movement), 13.5.5 (unfreeze)

A witnessed kill is the single most conclusive act in the game (only impostors kill), yet it moves
NO structured belief today: `apply_observation_rules` has rules for a witnessed VENT (+0.5,
"almost certain") and body-proximity (+0.2) but NONE for a witnessed KILL, so a crewmate who
directly sees the kill weights it BELOW a vent — backwards — and relies on the LLM reading a memory
line. This task makes a witnessed kill real evidence in two separable halves (land + validate (a)
first; (b) is the heavier detector change):

(a) WITNESS BELIEF — a perception-time rule keyed on the existing witness-gated stamp: when the
agent's packet carries a `PlayerView` with `action == "kill"`, lift the killer's suspicion over the
§4.6 gate to near-certain (`WITNESSED_KILL_SUSPICION_DELTA`, >= `VENTING_SUSPICION_DELTA`, pinning
to the ~1.0 clamp). Team-internal firewall (§4.7): an impostor that witnessed a TEAMMATE's kill
accrues NO suspicion against the teammate (exclude `self_state.fellow_impostor_ids`), mirroring
Rule 1's co-presence guard. The witness reasons from its OWN memory — unforgeable, no corroboration
needed (the owner decision: a first-hand kill view IS conclusive for the witness). The bump
persists into the meeting suspicion graph, so the witness votes the killer over-gate.

(b) MEETING PROPAGATION — a kill-scene intensification of the 13.4 `alibi_vs_physical` detector:
when independent public sightings place the accused at the BODY's room within the kill window (the
kill scene, from `triggering_body_rooms` / the `found_body` trigger) and the accused's stated alibi
places them elsewhere, mint a STRONG contradiction that crosses listeners' gate via the unchanged
`apply_contradiction_rule`. REUSE `reconstruct_stated_paths` + the existing kind; add a kill-scene
marker only. **(b)-strictness = STRICT (owner-LOCKED 2026-06-26):** a SINGLE kill-scene placement
INFORMS (sub-gate `WEAK_REASON_*`) and needs a second independent source (another placement, or the
body+placement two-source conjunction) to cross — so a FABRICATED kill-accusation cannot railroad a
crewmate ("no single signal ejects" on the forgeable spoken channel). The permissive
single-witness-convicts-listeners alternative was REJECTED. (a) is unconditional regardless — the
witness believes on its own first-hand kill; (b)-strictness only governs whether that testimony
moves OTHER crewmates.

Both halves behind `AILIBI_WITNESSED_KILL_EVIDENCE` (default OFF → byte-identical to HEAD).

**Definition of done:** (a) a witnessed kill (`PlayerView.action == "kill"`) lifts the witness's
suspicion of the killer over the §4.6 gate (near-certain), teammate-firewalled (an impostor
witnessing a teammate kill accrues nothing), and the bump persists into the meeting suspicion
graph; with both a vent and a kill witnessed, the kill weighs >= the vent. (b) a $0 re-extraction of
the committed replays shows the kill-scene `alibi_vs_physical` flag firing STRONG for an accused
placed at the kill scene with a contradicting alibi, every STRONG flag role-gated to a true impostor
(ZERO STRONG-on-crewmate), and the R4 wrong-ejection floor holds; (b)-strictness is STRICT
(owner-locked): a lone kill-scene placement is sub-gate and requires a second independent source to
cross. NO new LLM
observation type / contradiction kind / `.j2` edit / prompt-version bump. Flag OFF → every belief
render, suspicion graph, and re-extraction is byte-identical to pre-task HEAD and committed replays
reconstruct identically (`scripts/verify_samples.sh`). New tests cover (a) (kill → over-gate;
teammate firewall; kill >= vent) and (b) (kill-scene STRONG vs the strictness gate; lone/weak
sub-gate; no STRONG-on-crewmate). Full `scripts/check.sh` green; a 9B smoke (flag ON) lights R7 on
kill-scene flags with zero STRONG-on-crewmate and the wrong-ejection floor held.
**Implementation hint:**
(a) mirror the vent branch in `apply_observation_rules` exactly — a new `action == "kill"` clause
applying `WITNESSED_KILL_SUSPICION_DELTA` (>= 0.5, lands at the 1.0 clamp) — but ALSO read
`observation.self_state.fellow_impostor_ids` and SKIP a teammate killer (the vent branch needs no
such guard; the kill guard is load-bearing because an impostor frequently co-locates with a
teammate's kill). The rule runs at perception via `ingest_packet`, so the bump persists into the
stored `BeliefState` the meeting graph reads. (b) extend `_detect_alibi_vs_physical`: when a
contradicting placement falls in a `triggering_body_rooms` room within the kill window, classify it
kill-scene and apply the LOCKED strict rule: a single kill-scene placement stays sub-gate; STRONG
requires `PHYSICAL_CONTRADICTION_MIN_VOICES` or a body+placement two-source conjunction. Add a
`KILL_SCENE` reason read by `is_weak_contradiction` so the delta routes through the unchanged
`apply_contradiction_rule` — no new kind, no schema/api/frontend change. Validate by re-extracting
the committed replays (R7 up; zero STRONG-on-crewmate; R4 floor) — NO re-record. Keep `agents/`
engine-free.
**Public types introduced:**
- agents.memory.beliefs.WITNESSED_KILL_SUSPICION_DELTA
**Integration risk:**
Two suspicion paths gain a new source. (a) is low-risk (a pure perception rule on existing
witness-gated data; the only subtlety is the teammate firewall, which a test must pin). (b) touches
the live contradiction detector, so the hard guards are: ZERO STRONG-on-crewmate on re-extraction
(a kill-scene flag must never fire on an innocent — verify role-gated), the R4 wrong-ejection floor
holds, and the (b)-strictness keeps a lone forgeable kill-accusation sub-gate. Behind
`AILIBI_WITNESSED_KILL_EVIDENCE` (default OFF) so the merge is byte-identical and the existing suite
+ committed replays are untouched; gameplay value is measured on the new model in Phase 14's
re-record. No re-record here (the $0 R7 re-extraction is the gate, per the Phase-13 cadence).
**Ready-to-paste prompt:** `agent_prompts/task-13-5-3-witnessed-kill.md`

> **Parallel-dispatch note (2026-06-26).** `13.5.3` / `13.5.4` / `13.5.5` have DELIBERATELY DISJOINT
> file scopes (3.3 = `beliefs.py` + `transcript.py`; 3.4 = `observation/` + `perception.py` +
> `store.py` + `working.py`; 3.5 = `game.py` + `manager.py`), so the validator clears them as
> parallel-safe and `13.5.3 ∥ 13.5.4` can be dispatched concurrently. `13.5.5` is file-disjoint too
> but RECOMMENDED LAST — it re-renders the memory the other two enrich and is the replay-determinism
> risk. The `Depends on` lines point only at the MERGED `13.5.1` / `13.5.2` (shared files), never at
> each other, so there is no inter-task ordering among the three.

### Task 13.5.4 — Movement perception (perceive room transitions; wire last_seen)
**Branch:** `phase-13-5-movement-perception`
**Depends on:** 13.5.1, 13.5.2
**Section refs:** the 2026-06-25 memory diagnosis (workflow `wg54kfoxy`: "movement is never perceived — agents learn only an actor's CURRENT room; the engine emits `MovedEvent` + maintains `last_action` but the observation layer reads neither"); engine/tick.py (`MovedEvent` from_room/to_room ~:261-267, `PlayerState.last_action`); observation/service.py (`_observed_actions_for_agent`, the witness gate); observation/packet.py (`PlayerView`); agents/perception.py (`ingest_packet`, the `EVENT_*` types); agents/memory/store.py (`render_for_prompt`, the existing within-vision `_collect_transitions` / `_SALIENCE_TRANSITION` + `_collect_movement_breadcrumbs`, and the dead `last_seen` render hook ~:1323); agents/memory/working.py (`record_sighting` / `last_seen`, dead — wired here, earmarked by 13.5.1)
**Complexity:** Integration
**Files in scope:**
- observation/service.py
- observation/packet.py
- agents/perception.py
- agents/memory/store.py
- agents/memory/working.py
- tests/observation/test_service.py
- tests/agents/test_perception.py
- tests/agents/test_memory_rendering.py
**Files NOT in scope:**
- agents/memory/beliefs.py and meetings/transcript.py — movement here is PERCEPTION + RENDER only; NO belief rule and NO detector change, which is what keeps this task file-disjoint from 13.5.3 so the two dispatch in parallel. A movement-driven belief/contradiction rule is a deliberate later item.
- orchestrator/game.py, meetings/manager.py — disjoint from 13.5.5
- the scalar belief path and the §4.6 gate — untouched
- engine/ and the recorded replays — observation reads the EXISTING `MovedEvent`; NO engine change, NO re-record

Today an agent perceives only a position SNAPSHOT (the actor's current room); the engine's
`MovedEvent` (room→room each tick) and `last_action` are never read, so a witness cannot perceive a
transition it directly saw, and the `WorkingMemory.last_seen` field (dead since Phase 2) never
populates. The render reconstructs coarse "moved from A" breadcrumbs from consecutive `saw_player`
deltas (Tasks 13.6/13.9), but a single-tick transit the agent witnessed is lost. This task surfaces
witnessed movement: `observation/service.py` derives a movement signal for a CO-LOCATED witness
from the engine `MovedEvent` (an actor the witness can see moving room→room), `agents/perception.py`
ingests it as a new first-hand event, `agents/memory/store.py` renders "You saw p-3 move from
CAFETERIA to ADMIN at tick 5", and the same path calls `working.record_sighting` → the now-live
"last seen in ROOM at tick T" belief-line suffix. Behind `AILIBI_MOVEMENT_PERCEPTION` (default OFF →
no movement event, `record_sighting` uncalled, render byte-identical to HEAD).

**Definition of done:** with the flag ON, a witness who could see an actor transition rooms gets a
first-hand perceived-movement episodic event (witness-gated exactly like `saw_player` — never for an
observer who could not see the actor, so no firewall/leak regression), rendered as a first-hand
sighting-class line; `working.last_seen` is populated via `record_sighting`, so the "last seen in
ROOM at tick T" belief suffix finally renders. Replay-deterministic: the movement signal is
re-derived from the recorded `MovedEvent` on the replay path, so committed replays reconstruct
byte-identically (`scripts/verify_samples.sh`). Flag OFF → every packet, episodic store, and memory
render is byte-identical to pre-task HEAD; the existing within-vision transition/breadcrumb renders
are unchanged. NO `agents/memory/beliefs.py` or `meetings/transcript.py` edit (the parallel-safety
boundary). New tests cover the witness gate, the movement render, the `last_seen` wiring, flag-off
byte-identity, and determinism. Full `scripts/check.sh` green; a 9B smoke (flag ON) shows the leak
suite passing and the render within the 1500-tok budget.
**Implementation hint:**
Mirror the `saw_player` witness gate: surface movement only for an observer already entitled to see
the actor (reuse the same visibility/witness path `_observed_actions_for_agent` uses), so the §4.7
firewall and the leak suite hold for free. Carry the transition on a new `observation/packet.py`
field (e.g. a `moved_from` on `PlayerView` or a small `moved_players` list) and ingest it in
`ingest_packet` as a new `EVENT_*`; gate the `record_sighting` call on the flag so `last_seen` stays
empty (and its suffix absent) when OFF — that is the byte-identity boundary. Salience is first-hand
class (a witnessed transition is direct observation, distinct from the reconstructed
`_SALIENCE_TRANSITION` breadcrumb). Keep `agents/` engine-free (read the engine `MovedEvent` only in
`observation/service.py`, the orchestrator-owned boundary). Run a memory-render fixture before/after
with the flag OFF to confirm byte-identity.
**Integration risk:**
A new first-hand perception channel + the first live writer of `WorkingMemory.last_seen`. The
firewall/leak surface is the main risk: movement MUST be witness-gated identically to `saw_player`
(a movement the observer could not see must never appear), so the leak suite is the hard gate.
Behind `AILIBI_MOVEMENT_PERCEPTION` (default OFF) so the merge is byte-identical and committed
replays are untouched; determinism holds because the signal re-derives from the recorded
`MovedEvent`. File-disjoint from 13.5.3 and 13.5.5 by construction (no `beliefs.py` / `transcript.py`
/ `game.py` / `manager.py`), so all three dispatch in parallel. No re-record (smoke only).
**Ready-to-paste prompt:** `agent_prompts/task-13-5-4-movement-perception.md`

### Task 13.5.5 — Unfreeze rendered memory mid-meeting (refresh per turn)
**Branch:** `phase-13-5-unfreeze-memory`
**Depends on:** 13.5.2
**Section refs:** the 2026-06-25 diagnosis + PR #198 review (rendered_memory frozen at meeting-open while only `suspicion_graph` is recomputed pre-vote, so the belief lines and the `suspicion_graph` kwarg diverge); orchestrator/game.py (`render_memory_for_meeting`, the one-time frozen render ~:733-743); meetings/manager.py (`MeetingParticipant` frozen dataclass ~:486-507, the turn loop + the ballot render); [[project_substrate_cadence_doctrine]] (replay determinism)
**Complexity:** Integration
**Files in scope:**
- orchestrator/game.py
- meetings/manager.py
- tests/orchestrator/test_meeting_integration.py
- tests/meetings/test_manager.py
**Files NOT in scope:**
- agents/memory/store.py (`render_for_prompt`) — UNCHANGED; this task CALLS the renderer per turn, it does not edit it, which keeps it file-disjoint from 13.5.4
- agents/memory/beliefs.py, meetings/transcript.py — disjoint from 13.5.3
- observation/, agents/perception.py — disjoint from 13.5.4
- the scalar fold and the §4.6 gate value — untouched
- engine/ and the recorded replays — NO re-record; `verify_samples.sh` must stay byte-identical

Today `render_memory_for_meeting` runs ONCE per participant at meeting open
(`orchestrator/game.py` ~:733-743) into the frozen `MeetingParticipant.rendered_memory`; every turn
AND the ballot reuse that open-tick snapshot, while the pre-vote fold updates the `suspicion_graph`
separately — so a speaker's later turn/ballot reads STALE belief lines that diverge from the
recomputed `suspicion_graph` (the PR #198 review inconsistency). This task re-renders a participant's
memory before their later turns and their ballot, from the CURRENT (pre-vote-folded) `BeliefState` +
episodic, so the belief lines are internally consistent with the suspicion graph the ballot reads.
HIGHEST RISK in Wave C: the per-turn re-render MUST be replay-deterministic (a pure function of the
deterministic `BeliefState` + episodic at that point, with the renderer's existing stable salience
tie-breaks), so `verify_samples.sh` reconstructs the committed replays byte-identically. Behind
`AILIBI_UNFREEZE_MEMORY` (default OFF → the one-time frozen render, byte-identical to HEAD). LAND
LAST (after 13.5.2–13.5.4) so the re-render is exercised against the real richer content.

**Definition of done:** with the flag ON, a participant's `rendered_memory` is recomputed before each
of their turns and their ballot from the current `BeliefState` / episodic (not the open-tick freeze),
so the rendered belief lines match the pre-vote `suspicion_graph` the ballot consumes; the
`MeetingParticipant` carries a refresh mechanism (a re-render hook / per-turn recompute) rather than a
single frozen string, without breaking the existing frozen-default call path. Replay-deterministic:
run twice → byte-identical; `scripts/verify_samples.sh` reconstructs all committed samples cleanly.
Flag OFF → the one-time frozen render, byte-identical to pre-task HEAD (the existing meeting suite
passes unchanged). NO `agents/memory/store.py` edit (the renderer is called, not changed — the
parallel-safety boundary with 13.5.4). New tests cover the refresh (a later turn sees updated belief
lines consistent with the suspicion graph), determinism (twice → identical; `verify_samples`), and
flag-off byte-identity. Full `scripts/check.sh` green; a 9B smoke (flag ON) holds the meeting-rate
floor and byte-identical reconstruction.
**Implementation hint:**
The frozen-default path is the byte-identity boundary: keep `MeetingParticipant.rendered_memory` as
the open-tick render when the flag is OFF, and ONLY when ON recompute it per the speaker's turn via a
re-render hook (a callable the participant holds, or a manager-side recompute that reads the live
`BeliefState`). The recompute calls the UNCHANGED `agents.memory.store.render_for_prompt` — do not
edit the renderer. Determinism is the hard part: the re-render must read only the deterministic
stored state at that point (no wall-clock, no RNG, no set iteration order), so a replay rebuilds the
identical string; pin it with a `verify_samples` run in the task. Because the per-meeting fold that
moves suspicion pre-vote already exists, the new content the re-render surfaces is just the
up-to-date belief lines — no new belief math here.
**Integration risk:**
The replay-determinism hazard is the reason this lands LAST. Re-rendering mid-meeting changes WHEN a
speaker sees its belief lines; if the re-render is not a pure function of the deterministic stored
state, a replay diverges and `verify_samples` breaks — so that check is the hard gate, not just
`check.sh`. Behind `AILIBI_UNFREEZE_MEMORY` (default OFF) so the merge is the frozen path,
byte-identical, with the existing meeting suite untouched; gameplay value is measured on the new
model in Phase 14. File-disjoint from 13.5.3 (`beliefs`/`transcript`) and 13.5.4 (`observation`/
`store`) — it touches only `game.py` + `manager.py` — so it can run in parallel, though landing it
after 13.5.3/13.5.4 exercises the re-render against the real richer memory. No re-record (smoke only).
**Ready-to-paste prompt:** `agent_prompts/task-13-5-5-unfreeze-memory.md`

The phase closes when Wave C's smoke is green and the corrected-substrate 9B prompts are pinned;
then **Phase 14** (model migration, PR #196) selects + re-baselines on this corrected substrate.
