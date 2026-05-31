# Phase 7 — Plan (Agent Intelligence)

> This is a PLAN, not a contract set. It records the Phase 7 shape, the locked
> decisions, and the open questions. Per-task contracts (`### Task 7.x`) get
> written into `tasks/phase-7.md` once the open questions below are resolved.
> Do NOT add `### Task 7.x` headers to this file — `tasks/phase-*.md` is parsed
> by `scripts/validate_task_docs.py`.

## Goal
Make the agents demonstrably smarter (better lying, deeper contradiction
detection, real impostor tactics) AND measurable. The MVP-close direction is
agent-intelligence; the Phase 7 pre-planning diagnosis
(`audits/audit-2026-05-30-1952-phase-7-meeting-frequency-diagnosis.md`) showed the
blocker is that games rarely reach meetings (4/50), so agent-intelligence metrics
run on n=4 and are noise. Phase 7 therefore opens with an enablement gate that
makes meetings frequent, then ships agent-intelligence on a measurable denominator.

## Root cause (see the diagnosis audit)
Structural game-brevity, not poor killing: 1 task/crewmate + the dead-crewmate
task-drop end 28/50 games by `CREWMATE_TASKS` at median tick 9; cheap 2-kill
parity ends 18 more; bodies always exist but go unreported because crewmates
report only same-room bodies and idle back to the Cafeteria hub. Measured
counterfactual: 4p/1i ≈ 10% meeting rate vs **7p/2i = 63%**. `num_impostors>1`
is already fully wired and CLI-exposed.

## Locked decisions (Daniel, 2026-05-30)
1. **Roster is configurable, surfaced in the frontend, with two presets:
   4p/1i and 7p/2i.** (See open question Q1 on frontend scope.)
2. **Tasks-per-crewmate is configurable; default ≥ 2** (replacing the hardcoded 1
   in `orchestrator/seeder.py`).
3. **Multiple impostors know who each other are** (shared impostor identity,
   delivered impostor-only), but have **no private conversation channel** —
   coordination happens only through public play (e.g. defending each other in
   meetings, never accusing a teammate).
4. **Keep the dead-crewmate task-drop rule** as-is (`engine/tick.py:261-265`); not
   revisited in Phase 7.
5. **Crewmate wander/patrol idle: implement** (so survivors re-traverse kill rooms
   and discover bodies). **Adjacent-room reporting: NO** — keep reports
   same-room only (adjacent is too large a sensing range).
6. **Assess a cheaper provider/model for high-volume eval** (the 7p/2i set runs
   7–10× more meeting LLM calls). (See open question Q2.)
7. **The 4p/1i set is FROZEN as the determinism + leak regression baseline.** It is
   not re-recorded on prompt-revs or substrate changes; it refreshes ONLY on a
   deliberate baseline-rotation event (an explicit design-thread decision to move
   the regression anchor). The 7p/2i set is the live, evolving meeting-rich eval
   set; the 4p/1i set is the stable A/B reference that keeps determinism + leak
   regressions honest across phases.

---

## Wave 0 — Enablement gate (config + prerequisites + eval-infra)
**Nothing in agent-intelligence is measurable until this clears.** Mostly
config/substrate; low risk.

> **Contract mapping** (`tasks/phase-7.md`, written 2026-05-30): W0.1→Task 7.1,
> W0.2→Task 7.2, W0.3→Task 7.3; W0.4 is split into Task 7.4 (roster-aware loader +
> two-committed-set layout — dispatchable plumbing, fake-validated) and Task 7.5
> (generate + commit the 7p/2i set — design-thread, real spend); W0.5 (balance
> validation) is folded into Task 7.5. Dispatch order: (7.1 ∥ 7.2) → (7.3 ∥ 7.4) → 7.5.

### W0.1 — Configurable roster + tasks-per-crewmate
- Add a `tasks_per_crewmate` parameter to `orchestrator/seeder.py::_build_tasks` /
  `seed_initial_state` (currently hardcodes 1 task/crewmate at lines 165-176),
  thread it through `HeadlessGame` and `scripts/run_tournament.py` as
  `--tasks-per-crewmate` (**default 2**, per decision 2).
- Define two named roster presets — `4p/1i` and `7p/2i` — usable by the eval
  harness and surfaced to the frontend (decision 1). `num_players` /
  `num_impostors` are already CLI-exposed; presets bundle them with the task count.
- Category: engine-balance / config. Priority **p0**. Deps: none.

### W0.2 — Impostor mutual-awareness substrate (firewall-sensitive)
- Each impostor must know the identity of its fellow impostors (decision 3) so
  two impostors at 7p/2i don't accuse/vote each other. Deliver the impostor
  roster **impostor-only** through the observation/self-state path — crewmates
  must never receive it.
- **No private channel** — impostors coordinate only via public meeting behavior.
- **Delivery (Q4 resolved):** add an impostor-only field to `SelfView` — e.g.
  `fellow_impostor_ids: tuple[PlayerId, ...]` — populated by `ObservationService`
  ONLY when the recipient is an impostor, empty otherwise (and in solo-impostor
  games). `self_state` is the already-privileged self channel where `role` lives,
  so this reuses the audited boundary and never touches `visible_players`.
- Extend the leak test with a new invariant: `self_state.fellow_impostor_ids == ()`
  for every crewmate-recipient packet (plus the existing "no `PlayerView` carries
  role"). An impostor seeing its OWN teammates is allowed, like seeing its own
  role. This is the prerequisite that makes the 7p/2i eval coherent.
- Category: agent-intelligence / firewall. Priority **p0**. Deps: none.
  (Prerequisite for trusting any 7p/2i result.)

### W0.3 — `meeting_rate` as a first-class tracked metric
- Add `meeting_rate` / `meetings_total` + a meeting-trigger breakdown (body-report
  vs emergency-button) to `TournamentEvalReport`
  (`eval/meeting_quality.py::build_tournament_eval_report`); surface in
  `run_tournament.py` summary and the regression close-gate.
- The trigger breakdown makes the currently-dead emergency pathway (0/50) visible
  so any feature that revives it is measurable.
- Category: eval-infra. Priority **p0**. Deps: none.

### W0.4 — Commit a meeting-heavy 7p/2i + 2-task sample set
- Regenerate via `scripts/refresh_samples.sh` with the new roster + task flags;
  commit the 7p/2i set **alongside** (not replacing) the existing 4p/1i baseline
  (which stays for determinism/leak regression + the A/B reference).
- Category: eval-set. Priority **p0**. Deps: W0.1, W0.2.

### W0.5 — Balance validation of 7p/2i + 2 tasks (Q3 resolved: required)
- Validate the decisive crew/impostor split on the 7p/2i + 2-task config is
  near-even, not just that meetings happen. If degenerate, sweep tasks-per-crewmate
  (2 vs 3) and/or roster until the split is balanced AND `meeting_rate ≥ 0.60`.
  Reference points from the diagnosis: 10p/1i degenerates to all-crew-task wins;
  10p/3i collapses meetings. Canonical Phase 7 eval config is whatever clears both
  bars.
- Category: engine-balance / eval. Priority **p0**. Deps: W0.1, W0.4.

> **Provider (Q2 resolved):** stick with Anthropic for Phase 7 (canonical model =
> Sonnet for meetings, as today). Reassess cheaper/other models for cost AFTER
> this phase. Bound Phase 7 cost by iterating on the fake/deterministic provider
> and reserving real-provider runs for the Wave-1 / Wave-2 exit A/Bs only (per the
> eval-cadence rule); cap N / sample seeds for those real-provider A/Bs if needed.

**Wave 0 exit criteria:** on the chosen config (7p/2i + 2 tasks unless W0.5
re-balances it), `meeting_rate ≥ 0.60` with **≥ 30 resolved meetings**; the
decisive crew/impostor split is non-degenerate (not all-`CREWMATE_TASKS`, not
all-parity); and the W0.2 mutual-awareness **substrate** is delivered with its
crew-empty leak invariant (`self_state.fellow_impostor_ids == ()` for every
crew-recipient packet) green on both committed sets. NOTE: this bar is the
substrate + firewall invariant, NOT observed meeting behavior — the *behavior*
(impostors defend / never accuse a teammate) is Wave 2 (J-5) and is deliberately
not asserted in Wave 0 (Wave 0 changes no meeting behavior). Until this holds, do
not start Wave 1.

---

## Wave 1 — Crew intelligence (p1)
- **J-2 — new contradiction-detector kinds:** temporal-impossibility,
  body-found-without-report timing, mutual-witness sighting-vs-sighting; index
  statement-borne `saw_player` claims. Builds on the Phase-6-wired detector +
  belief Rule 2 + BeliefState-into-perception (live substrate).
- **Crewmate wander/patrol idle** (decision 5): replace hub-camping
  `_return_to_hub` (`crewmate_policy.py:220-242`) with a wander/patrol that
  re-traverses kill rooms. **No adjacent-room reporting** — same-room reports
  retained. **Determinism is a hard constraint (Q6):** the wander must be a
  deterministic tactical decision (seeded/rule-based over the room graph) so
  byte-identical replay holds and the firewall is untouched; the detailed wander
  design can be revisited at implementation time.
- **Headline target:** `alibi_survival` 0.6 → **≤ 0.45** (crew catches more
  impostor lies) with `vote_correctness` holding **≥ 0.85** at n ≥ 30.
- Deps: Wave 0.

## Wave 2 — Impostor intelligence (p1)
- **J-5 — impostor vent + sabotage tactical branches** (today
  `impostor_policy.py` is KILL/COVER/STALK/IDLE only): unlocks belief Rule 4
  (witnessed-vent) and the never-reached `IMPOSTOR_SABOTAGE` win path; sabotage
  also extends games (more report windows).
- **Impostor meeting behavior using W0.2 mutual-awareness:** defend a teammate,
  never accuse a teammate (decision 3) — coordination via public play only.
- **Target:** a ≥ 8-point, feature-attributable swing in impostor win rate off
  the post-Wave-1 number, with `meeting_rate` not regressing.
- Deps: Wave 0, Wave 1 (sequence crew-before-impostor so the crew gain is read
  before the impostor gets stronger — otherwise the win-rate swings cancel).

## Wave 3 — Depth / content (p2)
- Richer `AlibiClaim` vocabulary (calling-bluff, partial-corroboration,
  hedged-accusation, request-for-clarification) + prompt deepening (stronger
  deception framing in the impostor template, thicker contradiction handling in
  the accusation template).
- Belief Rule 3 (verifiable-shared-task trust — now meaningful with ≥2
  tasks/crew) and Rule 5 (time-decay — matters in the longer games the roster
  produces).
- Adaptive meeting round count (J-7).
- Deps: Wave 0 + J-2.

---

## Frontend track (parallelizable; p1/p2)  — Q1 resolved
- **Phase 7 scope = BROWSE only.** A roster/config selector in the replay picker
  to browse the committed 4p/1i vs 7p/2i sets (decision 1). Surface roster
  metadata (`num_players`, `num_impostors`, `tasks_per_crewmate`) on the
  replay-list DTO + picker so a viewer can pick a preset and see each game's
  config. Achievable on the current spectator architecture (no live layer needed).
- **DEFERRED to the later live track:** *launching* a game with a chosen config
  from the UI. That needs a game-creation API + the single-process live-broadcast
  layer (DESIGN §1.1 / H-1), and stays behind Phase 7 with the rest of the
  live/human-player track.

## Provider / eval-infra track
- Cheaper-provider option (decision 6) for volume; canonical-model decision (Q2).

---

## Close gate (two-stage)
- **Stage A (enablement):** `meeting_rate ≥ 0.60` and ≥ 30 resolved meetings on
  the 7p/2i + 2-task set. Non-negotiable — agent-intelligence metrics are noise
  below it.
- **Stage B (smarter agents):** on the meeting-rich set, a **single-variable A/B**
  (pre- vs post-feature, same seeds/roster, only ONE side changed per wave — the
  crew-before-impostor sequencing enforces this) shows a statistically legible
  move attributable to a named feature. **Headline = `alibi_survival` falling
  (0.6 → ≤ 0.45)** while `vote_correctness` holds ≥ 0.85 (Q5: side-specific
  metrics are the headline because they don't cancel; impostor win-rate is a
  secondary/sanity number, with a J-5-attributable swing expected in Wave 2). An
  end-of-phase fixed-opponent matrix (smart-crew vs baseline-impostor and vice
  versa) is optional, only if the final win-rate is ambiguous. Reserve
  real-provider eval for the Wave-1 and Wave-2 exit A/Bs (eval-cadence rule);
  config-only Wave 0 validates on the fake provider.

## Sequencing
1. **Wave 0** (enablement gate) → must hit Stage A.
2. **Wave 1** (crew: J-2 + wander) → `alibi_survival` ↓.
3. **Wave 2** (impostor: J-5 + teammate defense) → attributable win-rate swing.
4. **Wave 3** (depth) → refine on a stable, meeting-rich denominator.
Frontend + provider tracks run in parallel as capacity allows.

## Decisions resolved (Daniel, 2026-05-30) — Q1–Q6
- **Q1 Frontend scope — RESOLVED.** Phase 7 = browse the committed 4p/1i vs 7p/2i
  sets by preset (see Frontend track). Live game-launch-from-UI is deferred to the
  later live/broadcast track.
- **Q2 Provider/model — RESOLVED.** Stick with Anthropic (canonical Sonnet) for
  Phase 7; reassess cheaper models for cost after the phase. Bound cost via
  fake-provider iteration + real-provider only at wave-exit A/Bs (see W0.5 note).
- **Q3 Balance — RESOLVED (must validate).** W0.5 validates the 7p/2i + 2-task
  decisive split is near-even; re-balance (tasks 2↔3 / roster) if degenerate.
- **Q4 Impostor-roster delivery — RESOLVED.** Impostor-only `fellow_impostor_ids`
  field on `SelfView`, populated only for impostor recipients, empty for crew; new
  leak-test invariant `self_state.fellow_impostor_ids == ()` for crew packets (see
  W0.2). Reuses the audited self-channel; `visible_players` untouched.
- **Q5 Win-rate attribution — RESOLVED.** `alibi_survival` is the headline
  (side-specific metrics don't cancel); win-rate is secondary; crew-before-impostor
  sequencing makes each wave A/B single-variable; full fixed-opponent matrix is an
  optional end-of-phase check only (see Close gate Stage B).
- **Q6 Wander vs determinism — RESOLVED (constraint).** Determinism is a hard
  constraint: the wander idle must be a deterministic tactical decision; detailed
  design revisited at implementation (see Wave 1).

## Still open (lower-stakes, settle during contract-writing)
- The exact deterministic wander rule (seeded RNG vs fixed patrol order over the
  room graph) — pick at Wave 1 implementation; both preserve byte-identical replay.
- Whether the privileged spectator UI should visually surface impostor coordination
  (`fellow_impostor_ids`) — nice-to-have, not gating.
