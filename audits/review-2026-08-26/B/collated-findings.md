# Wave-0 Track B — collated findings with per-claim verdicts

**Date:** 2026-08-26. **Method:** 8 blind finder dimensions -> dedup/collation -> independent adversarial verification (every finding re-run against fresh code/bytes; default REFUTED when evidence does not reproduce). All workers Opus; the parallel track was invisible to this one.

**Tally: 56 canonical findings — 18 CONFIRMED, 37 ADJUSTED (core observation stands; claim, severity, or classification corrected by the verifier), 1 REFUTED.** Severity and classification below are POST-verification (the verifier's correction wins); the finder's original is shown when it moved.

| id | severity | classification | verdict | title |
|---|---|---|---|---|
| B-1 | P2 | defect | ADJUSTED | A meeting trigger silently discards every later-ordered action in the same tick, and the replay records those never-applied actions as if they happened |
| B-2 | P2 | defect | ADJUSTED | Win conditions are never evaluated on a meeting-trigger tick, so a state that already satisfies IMPOSTOR_PARITY can enter a meeting and exit as a CREWMATE win |
| B-3 | P1 | design-limitation | CONFIRMED | The entitlement oracle cannot police the engine's witness rule: a widened kill/vent witness set passes the whole leak scan (and the champion gate) |
| B-4 | P2 | quality-debt / test-gate composition gap | ADJUSTED | The champion leak gate never runs the cross-player owned-task engine-truth check; a foreign-task-ownership leak scores 0 failures there and 8 on the scripted-only check |
| B-5 | P3 | quality-debt | ADJUSTED | A roll-call whereabouts on either side makes an alibi_conflict structurally un-STRONG: 60/60 recorded conflicts are WEAK, and the boundary-overlap rule mis-fires on same-tick claims |
| B-6 | P1 | defect | CONFIRMED | Contradictions are re-derived WITHOUT the private grounding channels in four live consumers (the ML conviction label, the referee supply gauge, watchability and vote-correctness), inverting the STRONG/WEAK band on the exact corpus the re-ground fits |
| B-7 | P1 | design-limitation | CONFIRMED | Testimony-as-content drops the two largest structured shapes: WhereaboutsClaim (2,269) and SawMoveObservation (1,160) never reach any listener's memory |
| B-8 | P1 | defect | CONFIRMED | The belief line's "last seen in ROOM at tick T" is fed ONLY by witnessed transitions, so it contradicts the agent's own sightings in 19% of rendered rows |
| B-9 | P1 | defect | ADJUSTED | The referee's "first-hand structured sighting" vocabulary still excludes saw_move, so 29% of spoken placements never back an accusation |
| B-10 | P2 | quality-debt | ADJUSTED | The baseline-7 flags_per_meeting floor the re-ground will adopt is 69% persisted vent sightings, and the module's own docstring says that component is zero |
| B-11 | P2 | design-limitation | ADJUSTED | The surrogate GO bar is already saturated on two axes and structurally blocked on the third — a re-fit-and-re-pin re-ground reproduces NO-GO |
| B-12 | P3 | quality-debt | ADJUSTED | The FO-6 comparator's decision head is tuned by an objective whose plateau value IS the fit-side SKIP count — it tracks meeting mix, not physics |
| B-13 | P2 | design-limitation | ADJUSTED | The crew inner fitness can rank a LOSS above a WIN: unnormalised task-count shaping dwarfs the terminal term |
| B-14 | P2 | design-limitation | ADJUSTED | Impostor fitness pays kills three times and the win term is 1/22 of it — the objective is saturated and cannot discriminate the arms |
| B-15 | P2 | design-limitation | ADJUSTED | The conviction GO bar's conversion axis is recall-only — a degenerate always-positive head passes it by construction |
| B-16 | P2 | design-limitation | ADJUSTED | Three instruments, one fingerprint: the conviction artifact carries no fit-corpus record, so its drift fence and the ML-grounding row are surrogate-only proxies |
| B-17 | P3 | design-limitation | ADJUSTED | The surrogate's GO/NO-GO verdict is the only one of the three with no committed artifact and no loader that gates on it |
| B-18 | P2 | defect | ADJUSTED | The corpus recorder aborts a multi-hour record on ONE dead-owner probe; the sibling recorder needs a 10-poll streak for exactly this reason |
| B-19 | P3 | design-limitation | ADJUSTED | The samples recorder pins the prompt SET but not its per-template VERSIONS, and validity_gate.py has no CLI surface for the pin that would catch it |
| B-20 | P3 | design-limitation | ADJUSTED | The STALE amnesty darkens the two whole-object identity pins, so the committed adoption bars are currently editable with no gate at all |
| B-21 | P1 | quality-debt | CONFIRMED | The corpus recorder's entire recording engine is untested; the identical hardening was applied to the sibling recorder only |
| B-22 | P2 | defect | ADJUSTED | Task 16.7's `:whereabouts:` event-id segment was taught to one contradiction helper and not its sibling — the roll-call half of 31/164 served flags renders with no badge and no accent |
| B-23 | P2 | defect | ADJUSTED | A substrate-mismatched replay is invisible to every collection view — listed by the picker and counted in the served cost/decisive aggregate — and fails only when opened |
| B-24 | P2 | design-limitation | ADJUSTED | The `lights` sabotage is strictly self-harming for impostors: it costs the crew nothing and blinds only the impostor |
| B-25 | P2 | quality-debt | ADJUSTED | The engine's passive task-continuation path is unreachable in every production and training loop — 0 events across the whole baseline-7 corpus |
| B-26 | P2 | quality-debt | CONFIRMED | Every engine tick throws away ~17us re-seeding a `random.Random` from urandom that it immediately overwrites — a one-line, behaviour-identical 9% throughput win |
| B-27 | P2 | enhancement | ADJUSTED | The engine property tests assert only totality — none of the invariants that would have caught the two P1 findings are property-tested |
| B-28 | P2 | quality-debt | CONFIRMED | audible_events is the one packet channel with no entitlement or traceability check anywhere in the leak scan |
| B-29 | P2 | quality-debt | CONFIRMED | The champion leak gate's coverage assertion checks only that a body was seen; the witness-gated KILL channel it exists to police fires once per gate run |
| B-30 | P3 | observation | ADJUSTED | The ML corpus the re-ground fits on has never been leak-scanned, though the machinery exists and the whole 200-replay corpus scans clean in 3.8 s |
| B-31 | P3 | specified-behavior | ADJUSTED | The vent_sighting contradiction flag is a referee-certified truth channel: it is minted from the speaker's PRIVATE episodic record and shown to every voter as engine-certified proof |
| B-32 | P3 | defect | ADJUSTED | Duplicate alibi_vs_sighting mint: 6 of 71 corpus flags, and the surrogate's own feature builder is one of the consumers that still double-counts |
| B-33 | P3 | defect | ADJUSTED | The STRONG/WEAK band is a substring test over a description that interpolates model-authored room text, so a compound room label can self-band its own flag WEAK |
| B-34 | n/a (not a defect) | specified + ratified behaviour | REFUTED | grounded_prosecution is a meeting-global all-or-nothing switch, and arming it silently withdraws the 18.9 interior exemption for unrelated flags |
| B-35 | P3 | defect | ADJUSTED | The directional breadcrumb excludes vent/kill sightings from the subject's path, so "last seen there at tick T" can under-report the room where the agent witnessed a vent |
| B-36 | P2 | defect | CONFIRMED | The §4.7 teammate kill-window suppression punches a hole in the sighting log that `_collect_transitions` reads as movement, fabricating "entered"/"left" lines about a teammate who never moved |
| B-37 | P2 | quality-debt | ADJUSTED | The non-elastic belief block renders rows for DEAD and EJECTED players, spending the fixed budget that the route and the observations are shed against |
| B-38 | P2 | design-limitation | CONFIRMED | §6.3 Rule 1 cannot fire on the strongest circumstantial case: a player found STANDING with the body at the discovery tick takes zero body-proximity suspicion |
| B-39 | P3 | quality-debt | ADJUSTED | Only ONE rendered-memory line class has a fidelity instrument; the belief block and the reconstructed transitions have none |
| B-40 | P2 | defect | CONFIRMED | I-4's grounding search reads the speaker's END-OF-GAME memory, not the memory they held when they spoke |
| B-41 | P3 | known-open re-report | ADJUSTED | The replay_walk substrate-check gap is inert on every committed byte today — the exposure is the CLI path, which never runs the validity gate |
| B-42 | P3 | quality-debt | ADJUSTED | The degeneracy detector is one-sided: `degenerates_to_skip` cannot see an all-EJECT collapse |
| B-43 | P2 | defect | CONFIRMED | TRUNCATED_EPISODE_FITNESS (-10.0) is not below every reachable full-game fitness once the anchor penalty applies |
| B-44 | P2 | design-limitation | ADJUSTED | The co-evolution substrate fence compares two operator-supplied values and never recomputes the substrate from the corpus |
| B-45 | P3 | quality-debt | ADJUSTED | Fit-corpus fingerprint scope stops at recorded bytes — it does not cover the roster, nor the derivation code that turns those bytes into features |
| B-46 | P3 | observation | ADJUSTED | Deleting the STALE amnesty is four code sites plus five tests that PIN 'STALE' as the expected status |
| B-47 | P3 | quality-debt | ADJUSTED | Stale coordination anchors around BAKEOFF_BASELINE_ID: the doc comment names the wrong current value and the committed bake-off rows still stamp baseline-5 |
| B-48 | P2 | defect | CONFIRMED | The IN-TREE sidecar leg descends into nested git worktrees, so content outside the checkout decides the evidence gate's exit code |
| B-49 | P2 | quality-debt | CONFIRMED | check.sh's leg composition is unpinned: six of its seven gates could be deleted with the suite still green |
| B-50 | P2 | quality-debt | ADJUSTED | The corpus recorder mis-states its own substrate in 29 places, including messages it prints at record time |
| B-51 | P2 | defect | CONFIRMED | The substrate- and policy-mismatch errors are documented as "HTTP 500 with the offending game id in the response body" but return an opaque `Internal Server Error` |
| B-52 | P2 | defect | CONFIRMED | The substrate guard is asymmetric: it catches a lever it knows recorded OFF, but silently ignores a recorded lever key it does not know |
| B-53 | P2 | quality-debt | ADJUSTED | The meeting dialog's transcript/evidence half has no automated assertion anywhere — no component tests exist and journey.spec asserts only the ballots region |
| B-54 | P3 | observation | CONFIRMED | Within-tick action priority is the actor's id string, giving a lower-id seat a systematic mechanical edge |
| B-55 | P3 | observation | ADJUSTED | I-10's reporter-killed cell divides a body-meeting-only numerator by the all-meetings denominator |
| B-56 | P3 | quality-debt | CONFIRMED | I-2 compares a model-emitted room label with a raw string equality while every other room comparison in the module canonicalises |

---

## B-1 — A meeting trigger silently discards every later-ordered action in the same tick, and the replay records those never-applied actions as if they happened

**Severity:** P2 (finder: P1). **Classification:** defect (record-fidelity half); re-report of known-open C-25 (engine half). **Verdict:** ADJUSTED. **Area:** engine-core / tick loop + replay record fidelity. **Confidence:** high.
**Merged from:** finder-engine-core.json#1.

**Claim.** TWO findings welded into one, with different standing. (a) THE ENGINE DROP IS A RE-REPORT of a known-open item: `engine/tick.py:599-600` returns mid-loop so every later-ordered action is dropped with no ActionRejectedEvent — filed as C-25 / engine F6 (audits/review-2026-08-19/B/collated-findings.md:49; audits/review-2026-08-19/B/engine.md:67) at P2, and earlier as A-A-3 in audits/audit-2026-06-07-0717-gameplay-data.md ('75 meeting freezes silently drop queued actions including 6 reports and 1 kill'), and it sits in the phase-20 close's un-acted 'roughly 94 P2 code findings' backlog (audits/audit-phase-20-close.md:399). (b) THE RECORD-FIDELITY HALF IS NEW and correct: orchestrator/game.py:1860 records the full submitted batch, so 1,560 of 25,881 corpus actions (6.028%) are recorded but never executed, and eval/action_ingest.py tallies `entry.actions` as fact. The severity should drop to P2 because the demonstrated consumer harm is thin: the ONLY named consumer is the indistinguishability wait-share, a diagnostic gauge with no gate/floor/pin on it, rendered at 2 d.p. by scripts/build_sample_report.py:257-268 where 0.1046 and 0.0990 both print '0.10'; and every ML path that could have been corrupted RE-WALKS the engine with per-tick state_hash verification (training/rollout.py:550-556, training/surrogate/dataset.py:901-907), while training/rollout.py:326-336 `_count_do_task_submissions` documents counting SUBMISSIONS as deliberate. No fit, gate, or pin is shown to move.

**As originally filed.** engine/tick.py:599-600 returns out of the apply-actions loop the instant an action flips the phase to MEETING, so every action ordered after it is dropped with no ActionRejectedEvent and no other trace — yet orchestrator/game.py:1860 records the FULL submitted batch into the replay row, and 1,560 of the baseline-7 corpus's 25,881 recorded actions (6.03%) are actions the engine never applied.

**Finder evidence.**

```
MECHANISM. engine/tick.py:593-604:
```
    for action in actions:
        try:
            working_state, event = _apply_action(working_state, game_map, action)
            events.append(event)
            if event.type == "Killed":
                cooldown_skip_players.add(action.actor)
            if working_state.phase == "MEETING":
                return working_state, events        # <- engine/tick.py:599-600
```
Order is lexicographic by actor id (orchestrator/action_ordering.py:34-40, `_action_order_key` returns `(action.actor, action.type, payload)`), so whether an action survives is decided by the actor's NAME.

DIRECT PROBE (scratchpad/wave0/B, `PYTHONPATH=. uv run python`): p-1 reports an existing body, p-2 (impostor, cooldown 0, co-located) kills p-3, p-3 moves:
```
submitted (ordered): [('p-1', 'report'), ('p-2', 'kill'), ('p-3', 'move')]
events: [('MeetingTriggered', 'p-1')]
p-3 alive after: True room: CAFETERIA
any ActionRejected? False
```
The kill and the move vanish with zero engine record.

RECORDED-BYTES IMPACT. `orchestrator/game.py:1859-1860` writes `replay.record_tick(input_tick, actions, state)` with the full ordered batch. Scanning every corpus tick row and re-sorting with the production key (`sorted(r['actions'], key=(actor, type, canonical-json))`, then counting everything after the first report/emergency):
```
corpus recorded actions total=25881 never-applied=1560 share=6.028%
  do_task    recorded=11541 never-applied= 523 (4.53%)
  move       recorded= 9375 never-applied= 564 (6.02%)
  wait       recorded= 2680 never-applied= 277 (10.34%)
  vent       recorded=  866 never-applied=  78 (9.01%)
  report     recorded=  507 never-applied=  70 (13.81%)
  kill       recorded=  724 never-applied=  28 (3.87%)
  emergency  recorded=   54 never-applied=  15 (27.78%)
```
438 of 4,242 tick rows carry at least one never-applied action.

THE DROP IS ROLE-CORRELATED (roles re-derived from `orchestrator.seeder.seed_initial_state`):
```
IMPOSTOR move   recorded=2651 never-applied=276 (10.41%)
IMPOSTOR vent   recorded= 866 never-applied= 78 ( 9.01%)
IMPOSTOR kill   recorded= 724 never-applied= 28 ( 3.87%)
CREWMATE move   recorded=6724 never-applied=288 ( 4.28%)
CREWMATE do_task recorded=10357 never-applied=506 ( 4.89%)
```

A CONSUMER READS THE RECORDED ACTIONS AS TRUTH. eval/action_ingest.py:19-21 states "no engine re-run is needed (the replay loader already exposes the tick actions)" and eval/action_ingest.py:58-74 tallies `entry.actions` straight off the rows; `audits/workflows/extract_gameplay_facts.py:3364-3365` publishes that into the audit's indistinguishability gauge. Recomputing its headline wait-share both ways over the corpus:
```
CREWMATE: as-recorded wait_share=0.1046   engine-truth wait_share=0.0990
IMPOSTOR: as-recorded wait_share=0.1000   engine-truth wait_share=0.0982
```
The published crew-vs-impostor gap of 0.0046 is 0.0008 in engine truth — 82% of the measured role separation is an artifact of counting actions that never executed.

RE-WALK FIDELITY CHECK (so the above is not my own reconstruction error): re-seeding 10 9p2i corpus games and re-walking with `advance_tick` + `apply_meeting_result` reproduced `221 / 221` recorded tick `state_hash` values, 0 mismatches — i.e. the engine really did not apply those actions.

Note the impostor-camouflage interaction: observation/service.py:431 turns a REJECTED `do_task` into the visible `action="task"` fake-task lever (Task 13.9). A dropped `do_task` emits no ActionRejectedEvent at all, so the camouflage silently fails on those ticks (17 impostor `do_task` submissions corpus-wide).
```

**Verifier evidence (independent re-run).**

```
MECHANISM — re-read fresh: engine/tick.py:592-604 confirms `if working_state.phase == "MEETING": return working_state, events` at :599-600 inside the apply loop, before step 2 (passive effects) and step 3 (`# 3) Check victory`, :624). orchestrator/action_ordering.py:34-40 `_action_order_key` returns `(actor, type, canonical-json)` — order is by actor NAME. orchestrator/game.py:1860 `replay.record_tick(input_tick, actions, state)` with `actions = list(translate_action_intents_for_tick(intents))` (orchestrator/boundary.py:44-50, already sorted).

MY OWN PROBE (scratchpad/vB1_probe.py, PYTHONPATH=. uv run python) — p-1 reports an existing body, p-2 (impostor, cooldown 0, co-located) kills p-3, p-3 moves:
```
submitted (ordered): [('p-1', 'report'), ('p-2', 'kill'), ('p-3', 'move')]
events: [('MeetingTriggered', 'p-1')]
phase after: MEETING
p-3 alive after: True room: CAFETERIA
any ActionRejected? False
```
REPRODUCES the finder's probe verbatim.

MY OWN CORPUS SCAN (scratchpad/vB1_corpus.py + vB1_corpus2.py, independent re-implementation of the ordering key):
```
tick rows=4242 recorded actions total=25881 never-applied=1560 share=6.028%
rows with >=1 never-applied action: 438
  do_task    recorded=11541 never-applied= 523 (4.53%)
  emergency  recorded=   54 never-applied=  15 (27.78%)
  kill       recorded=  724 never-applied=  28 (3.87%)
  move       recorded= 9375 never-applied= 564 (6.02%)
  report     recorded=  507 never-applied=  70 (13.81%)
  vent       recorded=  866 never-applied=  78 (9.01%)
  wait       recorded= 2680 never-applied= 277 (10.34%)
  (finder omitted: repair_sabotage 108/3, sabotage 26/2)
```
STRONGER THAN THE FINDER'S: I re-ran restricting to tick rows IMMEDIATELY FOLLOWED BY A `kind=meeting` ROW (proof the trigger actually succeeded rather than being rejected). Identical: `never-applied (rows CONFIRMED meeting next) = 1560 (6.028%) over 476 rows`. So the ordering heuristic is exact, and 476 == the corpus meeting count.

WAIT-SHARE RECOMPUTE (scratchpad/vB1_waitshare.py, roles read from each set's committed tournament-eval-report.json — the same source eval/action_ingest.py uses):
```
CREWMATE: as-recorded 0.1046  engine-truth 0.0990  (rec 2074/19824, truth 1853/18721)
IMPOSTOR: as-recorded 0.1000  engine-truth 0.0982  (rec  606/6057, truth  550/5600)
gap as-recorded=0.0046  gap engine-truth=0.0008
IMPOSTOR move  2651/276 (10.41%) | vent 866/78 (9.01%) | kill 724/28 (3.87%)
CREWMATE move  6724/288 ( 4.28%) | do_task 10357/506 (4.89%)
```
EVERY NUMBER IN THE FINDING REPRODUCES VERBATIM, including the role-correlated table.

CONSUMER PATH CONFIRMED: eval/action_ingest.py:19-21 states 'no engine re-run is needed'; :56-74 tallies `entry.actions` directly; audits/workflows/extract_gameplay_facts.py:3364-3365 folds it into compute_indistinguishability and :4355-4357 publishes the raw floats. CAMOUFLAGE NOTE CONFIRMED: observation/service.py:430-431 `elif isinstance(event, ActionRejectedEvent) and event.action == "do_task": task_actor_ids.add(event.actor)` is the sole camouflage source, so a dropped do_task emits nothing.

WHY I DOWNGRADE: no gate/floor/pin reads wait_share (`grep -rn wait_share` returns only the model, the audit workflow JSON and scripts/build_sample_report.py's `.2f` render). The ML consumers re-walk: training/rollout.py:551-556 and training/surrogate/dataset.py:902-907 both `raise` on a state_hash mismatch, i.e. they take engine truth; `_count_do_task_submissions` (training/rollout.py:326-336) counts submissions BY DESIGN and says so.
```

**Verifier note.** Evidence reproduces 100% verbatim — this is a well-measured finding and the record-fidelity half is a genuine new contribution. Two corrections: (1) the engine-drop half is a re-report of known-open C-25/F6 (P2) and of A-A-3 (2026-06-07, LOW); the finder does not cite either, and the merged item should say so. (2) P1 is not supported — every consumer the finder could name is a diagnostic gauge with no gate on it, and the paths that matter for the re-ground (rollout, surrogate dataset) re-walk the engine and hash-verify, so the fit is not exposed. Note also DESIGN.md §3.1 DOES specify 'Invalid actions become no-ops; an ActionRejected event is emitted' and 'A meeting interrupts the tick loop' — so the interrupt is specified but the silent drop violates the same section, which is exactly what C-25 already says. Fix sketch half (b) remains the right and cheap repair.

**Fix sketch.** Two independent halves. (a) Engine: stop returning mid-loop. Finish the batch, converting every remaining action into an `ActionRejectedEvent(reason='meeting opened this tick')` instead of dropping it silently — this satisfies the AGENTS.md no-silent-fallback rule and makes the loss auditable without changing which actions take effect. Because it adds events, it shifts nothing in `state_hash` (events are not hashed) — verify against `_state_hash` before/after on the corpus. (b) Record fidelity: either record the APPLIED action list (or an `applied: [bool]` sidecar) in `ReplayLog.record_tick`, or make `eval/action_ingest.py` walk the engine instead of trusting `entry.actions`. Fixing (b) alone is enough to de-bias the published gauges and does not need a re-record if the ingest re-walks.

## B-2 — Win conditions are never evaluated on a meeting-trigger tick, so a state that already satisfies IMPOSTOR_PARITY can enter a meeting and exit as a CREWMATE win

**Severity:** P2 (finder: P1). **Classification:** defect (latent; zero realized exposure). **Verdict:** ADJUSTED. **Area:** engine-core / win-condition evaluation ordering. **Confidence:** high.
**Merged from:** finder-engine-core.json#2.

**Claim.** The mechanism and both probes are exactly right and this is NOT a re-report of anything in the prior review — but the severity should be P2, not P1. The win-check skip on the meeting branch is a NAMED, PINNED behaviour (tests/engine/test_tick.py:1073 `test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks`, :1118 the emergency twin — the skip is in the test's own name); what is unspecified, and IS the defect, is the CONSEQUENCE: a state already satisfying IMPOSTOR_PARITY can be handed to the meeting and re-scored as CREWMATE_EJECT by `apply_meeting_result`, contradicting the §3.5 ordering rationale written verbatim at engine/win_conditions.py:41-44. Realized exposure is zero and the co-occurrence it needs is rare, so this is a latent correctness bug to schedule, not a blocker.

**As originally filed.** The same early return at engine/tick.py:599-600 skips step 3 (`# 3) Check victory`, engine/tick.py:624-636), so `advance_tick` can hand back a MEETING state on which `evaluate_win_conditions` already returns `IMPOSTOR_PARITY`; the orchestrator then runs a full meeting and `apply_meeting_result` re-checks the win only AFTER applying the ejection, which can convert the impostor win into `CREWMATE_EJECT`.

**Finder evidence.**

```
PROBE 1 — the bypass. 4 players (p-1 IMPOSTOR, p-2/p-3/p-4 CREWMATE, p-4 already dead with an undiscovered body). p-1 kills p-3 (reaching 1 impostor vs 1 crewmate) and p-2 reports the OLD p-4 body in the same tick:
```
ordered actions: [('p-1', 'kill'), ('p-2', 'report')]
phase after tick: MEETING
events: ['Killed', 'MeetingTriggered']
alive: {'p-1': 'IMPOSTOR', 'p-2': 'CREWMATE'}
evaluate_win_conditions on returned state: WinResult(winner='IMPOSTORS', reason='IMPOSTOR_PARITY')
GameOver emitted? False
```
engine/win_conditions.py:27-28 puts parity first precisely so "an offensive impostor action that resolves on the same tick still attributes to the offense per §3.5" (engine/win_conditions.py:42-44) — but the check never runs on this tick.

PROBE 2 — the flip. Feeding that MEETING state through `orchestrator.game.apply_meeting_result` with an `EJECTED p-1` result:
```
post-meeting phase: GAME_OVER
post events: [('GameOver', 'CREWMATES', 'CREWMATE_EJECT')]
```
An already-won impostor game is recorded as a crew win. `apply_meeting_result` re-checks at orchestrator/game.py:1331-1342, i.e. strictly after the ejection at orchestrator/game.py:1284-1311.

DELIBERATE-BUT-UNDER-SPECIFIED. The interrupt itself is pinned: tests/engine/test_tick.py:1073 `test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks` and :1118 (emergency). Both assert only the frozen sabotage clock / rng; neither covers a win already satisfied at the moment of the interrupt, so the flip is unguarded.

CURRENT CORPUS EXPOSURE = 0. Re-walking all 200 baseline-7 corpus games (`replays/ml_corpus/{4p1i,9p2i}`) and calling `evaluate_win_conditions` at every MEETING transition:
```
games walked: 200   meetings: 476
MEETING-trigger ticks whose state already satisfied a win: 0 {}
of those, outcome NOT preserved after the meeting: 0
```
(The walk is faithful: 221/221 recorded tick state hashes reproduced on a 10-game sample.) So this is LATENT under the shipped FSM policies, not realized in baseline 7 — but the re-ground changes exactly those policies, and the win label is the target the surrogate and conviction model are fit against.
```

**Verifier evidence (independent re-run).**

```
MY OWN PROBE (scratchpad/vB2_probe.py) — 4 players, p-1 IMPOSTOR, p-4 already dead with an undiscovered body; p-1 kills p-3 (reaching 1v1) and p-2 reports the OLD body in the same tick:
```
ordered actions: [('p-1', 'kill'), ('p-2', 'report')]
phase after tick: MEETING
events: ['Killed', 'MeetingTriggered']
alive: {'p-1': 'IMPOSTOR', 'p-2': 'CREWMATE'}
evaluate_win_conditions on returned state: WinResult(winner='IMPOSTORS', reason='IMPOSTOR_PARITY')
GameOver emitted? False
post-meeting phase: GAME_OVER
post events: [('GameOver', 'CREWMATES', 'CREWMATE_EJECT')]
```
BOTH PROBES REPRODUCE VERBATIM. Code re-read: engine/win_conditions.py:26-29 puts parity first; :41-44 states the rationale ('an offensive impostor action that resolves on the same tick still attributes to the offense per §3.5'). orchestrator/game.py:1329-1342 re-checks win STRICTLY AFTER the ejection at :1284-1311, and orchestrator/game.py:1868-1875 shows no win check between `advance_tick` and the meeting runner.

SPECIFICATION CHECK: DESIGN.md:263-275 §3.1 lists step 3 'Check victory ... If a side has won, emit GameOver and return' and then says 'A meeting interrupts the tick loop' with no statement about a win already satisfied at the interrupt. The interrupt-before-win-check IS named in the pinned test titles at tests/engine/test_tick.py:1073/1118 (both assert only the frozen sabotage clock + rng, as the finder says), so the skip is deliberate; the inversion is not covered.

MY OWN CORPUS EXPOSURE MEASUREMENT (scratchpad/vB2_corpus.py) — instead of a full re-walk I measured the necessary precondition directly, which is a tighter bound: for a win to be already satisfied at a MEETING interrupt with passive effects frozen, the only live cause is a kill ordered BEFORE the trigger in the same batch (sabotage-timeout and all-tasks-done cannot newly fire on a frozen tick, and 0-impostors requires an ejection).
```
meeting-trigger tick rows: 476
rows with a kill ordered BEFORE the trigger: 9 (9 kills)
  seed-1002 t10, 1015 t16, 1016 t11, 1034 t10, 1046 t11, 1092 t10, 1138 t6, 1142 t10, 1149 t10
```
All nine are 9p2i at ticks 6-16, far from 2v2 or 1v1 parity — consistent with the finder's 0/476. So the pathway is EXERCISED nine times in the committed corpus and never reached a win; 'CURRENT CORPUS EXPOSURE = 0' is corroborated, and I add that the guard is only the parity distance, not the ordering.

NOT A RE-REPORT: `grep -rn 'IMPOSTOR_PARITY|win check|victory check'` over audits/review-2026-08-19/B returns only F4/C-115 (DESIGN.md staleness about the FOUR win conditions), not this. C-25 covers the dropped actions, not the skipped win check.
```

**Verifier note.** Confirmed mechanism, confirmed zero realized exposure, genuinely new. Downgraded to P2 on impact: nothing in the committed record is wrong, the flip needs a kill-reaching-parity ordered before a report in one batch, and the finder's own escalation argument ('the re-ground changes exactly those policies') is speculative. The fix sketch is correct and cheap and should be scheduled; note its own claim is verifiable — turning a MEETING return into a GAME_OVER return only in already-decided states cannot move any committed replay, and my 9-row census shows which rows to re-verify.

**Fix sketch.** Evaluate win conditions BEFORE returning on the meeting branch: in `advance_tick`, when an action sets `phase == 'MEETING'`, run `resolve_win_conditions(working_state)` and, if it fires, emit `GameOverEvent` and return `phase='GAME_OVER'` instead of `MEETING` (§3.5 already says the offensive action wins). Keep the passive-effects freeze as-is so the sabotage-clock pins at tests/engine/test_tick.py:1073/1118 still hold. Because it can only turn a MEETING return into a GAME_OVER return in states that were already decided, no committed replay whose meeting actually ran is affected — but re-verify the corpus state-hash chain (the 0/476 measurement above says nothing changes).

## B-3 — The entitlement oracle cannot police the engine's witness rule: a widened kill/vent witness set passes the whole leak scan (and the champion gate)

**Severity:** P1. **Classification:** design-limitation. **Verdict:** CONFIRMED. **Area:** observation-firewall / eval.leak_scan / engine.rules. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#1.

**Claim.** Task 20.8's entitlement oracle re-derives visible players/bodies from WorldState but reads the kill/vent witness ALLOWANCE straight off the same event tuples the observation service reads, so any widening of engine/rules.py::_witnesses_in_room hands unentitled observers a role-proving kill/vent attribution with zero leak-scan failures.

**Finder evidence.**

```
eval/leak_scan.py:710-715 builds the allowance from the events themselves: `witness_allowance = {event.actor for event in events if isinstance(event, (KilledEvent, VentEnteredEvent, VentExitedEvent)) and agent in event.witnesses} - {agent}`; :718 then asserts `seen_players == entitled_players | witness_allowance`, and the room half (:749-759) uses `_witnessed_action_rooms` (eval/leak_scan.py:111-144), which reads the same tuples. Nothing re-derives WHO could have witnessed. The producing rule is engine/rules.py:29-44 `_witnesses_in_room` (co-located + alive + not in_vent), called at :102-107 (kill) and :146-156 (vent).

PROBE A (room clause dropped). Script /private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/8c686913-6a30-43ad-8ed2-a35d8125a233/scratchpad/wave0/B/witness_probe.py; `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../witness_probe.py`:
```
--- BASELINE ---
kill/vent sightings: none
leak-scan failures: NONE
--- MUTATED (witness room clause dropped) ---
kill/vent sightings: ['t3 p-2 (in ADMIN) sees p-3 kill in CAFETERIA', 't3 p-4 (in ADMIN) sees p-3 kill in CAFETERIA']
leak-scan failures: NONE
```
(assert_packet_is_leak_clean, eval/leak_scan.py:958, was called on every packet.)

PROBE B (the version no other gate catches either). CAFETERIA's map neighbours are EAST_HALL/UPPER_HALL/WEST_HALL, while the engine's own kill-witness unit test (tests/engine/test_tick.py:117, `assert ...['witnesses'] == ('crew-a','crew-b')`) places its out-of-room players in ADMIN and MEDBAY — neither adjacent to CAFETERIA. So a widening to 'same room OR adjacent room' passes that test too. Script .../wave0/B/witness_probe2.py:
```
--- BASELINE ---
engine unit-test assertion witnesses == ('crew-a', 'crew-b')
kill/vent sightings: none
leak-scan failures: NONE
--- MUTATED (witnesses widened to adjacent rooms) ---
engine unit-test assertion witnesses == ('crew-a', 'crew-b')
kill/vent sightings: ['t2 p-2 (in WEST_HALL) sees p-3 kill in CAFETERIA', 't2 p-4 (in WEST_HALL) sees p-3 kill in CAFETERIA']
leak-scan failures: NONE
```
p-2/p-4 are CREWMATES, whose visibility is same_room_only (engine/visibility.py:104-127), so CAFETERIA is not in their room set at all.

Why it reaches the ML program: training/bakeoff/harness.py:1823-1841 and training/crew/scorer.py:1738-1755 call `scan_factory_packets` as the champion leak gate, commenting that it 'checks shape, role strings, witness permission, movement gating and ENTITLEMENT'. And orchestrator/game.py:3010-3049 (`kill_witness_records_for_meeting`, the source of the conviction model's `kill_pin_pairs` / `kill_pinned_candidates` features) states 'Firewall-clean: every row was witness-gated by the engine before it reached this agent's packet (eval/leak_test.py)' — a property the leak test structurally cannot check.

Related but distinct prior record: audits/review-2026-08-19/B/observation-firewall.md §2 F1's mutation table is entirely in engine/visibility.py (M1/M6/M10/M14); no row mutates the witness rule, and agent_prompts/task-20-8-leak-scanner-entitlement.md scopes the fix to the visibility filters.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ (fresh): eval/leak_scan.py:710-715 builds `witness_allowance` from `event.witnesses` on the very KilledEvent/VentEnteredEvent/VentExitedEvent objects the observation service reads; :718 asserts `seen_players == entitled_players | witness_allowance`; the room half at :749-759 calls `_witnessed_action_rooms` (eval/leak_scan.py:111-144), which reads the same tuples. The in-code comment at :706-709 explains why the allowance is EVENT-derived rather than PACKET-derived — a different concern (both sides shrinking together), and it does not address re-deriving WHO could witness. Producer: engine/rules.py:29-44 `_witnesses_in_room` (co-located + alive + not in_vent), called at :102-107 (kill) and :146-156 (vent, source|destination union).

MY OWN PROBE A (scratchpad/vB3_probe.py — I monkeypatched `engine.rules._witnesses_in_room` to drop the room clause; p-3 IMPOSTOR kills p-1 in CAFETERIA, crewmates p-2/p-4 in ADMIN; every packet passed through `assert_packet_is_leak_clean` with its real PacketContext):
```
--- BASELINE ---
  Killed witnesses: ()
  kill/vent sightings: none
  leak-scan failures: NONE
--- MUTATED (witness room clause dropped) ---
  Killed witnesses: ('p-2', 'p-4')
  kill/vent sightings: ['p-2 (in ADMIN) sees p-3 kill in CAFETERIA', 'p-4 (in ADMIN) sees p-3 kill in CAFETERIA']
  leak-scan failures: NONE
```
MY OWN PROBE B (scratchpad/vB3_probe2.py — widened to same-room-OR-ADJACENT, crewmates in WEST_HALL; I also re-ran the engine unit test's exact fixture in-process):
```
--- BASELINE ---
  engine unit-test assertion witnesses == ('crew-a', 'crew-b')
  kill/vent sightings: none
  leak-scan failures: NONE
--- MUTATED (witnesses widened to adjacent rooms) ---
  engine unit-test assertion witnesses == ('crew-a', 'crew-b')
  kill/vent sightings: ['p-2 (in WEST_HALL) sees p-3 kill in CAFETERIA', 'p-4 (in WEST_HALL) sees p-3 kill in CAFETERIA']
  leak-scan failures: NONE
```
I independently verified the adjacency premise: CAFETERIA's map neighbours are exactly ['EAST_HALL','UPPER_HALL','WEST_HALL'], while tests/engine/test_tick.py:60-63 places p-2 in ADMIN and p-4 in MEDBAY — neither adjacent — so the engine's kill-witness pin at :117 genuinely survives the widening. And engine/visibility.py:98-127 confirms a CREWMATE is downgraded to `same_room_only` at base visibility, so WEST_HALL observers have CAFETERIA outside their room set entirely. BOTH PROBES REPRODUCE VERBATIM.

DOWNSTREAM CLAIMS SPOT-CHECKED: training/bakeoff/harness.py:1823-1828 and training/crew/scorer.py:1738-1743 carry the identical comment ('checks shape, role strings, witness permission, movement gating and ENTITLEMENT'); orchestrator/game.py:3041-3042 states 'Firewall-clean: every row was witness-gated by the engine before it reached this agent's packet (eval/leak_test.py)' — the overclaim the finding names.

NOT A RE-REPORT: audits/review-2026-08-19/B/observation-firewall.md §2 F1's mutation table is M1/M6/M10/M14 + M2/M3/M12/M4/M5/M8/M9/M11/M13/M16 — every row is a visibility/packet-field mutation; none mutates `_witnesses_in_room`. F1 was the item Task 20.8's entitlement oracle closed; B-3 is the residual half that oracle structurally cannot close.
```

**Verifier note.** Fully confirmed, both probes, verbatim. Correctly classified as design-limitation rather than defect: no live leak exists, the oracle simply cannot police the rule it depends on. The fix_sketch is muddled prose (it argues itself out of one form mid-sentence) but lands on the right answer — an engine-side property test asserting `set(KilledEvent.witnesses) == {alive, non-vented players in event.room} - {actor, target}` plus the vent source/destination analogue, cited from eval/leak_scan.py:710. The comment corrections it asks for at training/bakeoff/harness.py:1823, training/crew/scorer.py:1738 and orchestrator/game.py:3041 are all warranted.

**Fix sketch.** Give the oracle an independent witness bound instead of trusting the tuples: inside assert_visible_entities_match_engine_truth, before using `event.witnesses`, assert each named witness satisfies the rule re-derived from WorldState — for a KilledEvent, `state.players[w].alive and not in_vent and w in {actor's room occupants}` reconstructed from the packet's own tick is not available post-advance, so the cheapest correct form is to bound the allowance by the observer's own entitled room set plus the event room: assert `event.room in room_set or observer was co-located` is too strong for the walk-away case, so instead add a dedicated engine-side property test (Hypothesis over tests/observation/test_leak_property.py's existing vocabularies) asserting `set(KilledEvent.witnesses) == {alive, non-vented players in event.room} - {actor, target}` and the vent analogue for source/destination, and cite it from eval/leak_scan.py:710 as the layer the allowance leans on. Also correct the champion-gate comments (training/bakeoff/harness.py:1823, training/crew/scorer.py:1738) and orchestrator/game.py:3033 so they do not claim a guarantee the scan does not give.

## B-4 — The champion leak gate never runs the cross-player owned-task engine-truth check; a foreign-task-ownership leak scores 0 failures there and 8 on the scripted-only check

**Severity:** P2 (finder: P1). **Classification:** quality-debt / test-gate composition gap. **Verdict:** ADJUSTED. **Area:** observation-firewall / eval.leak_scan / training champion gate. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#2.

**Claim.** The structural fact and the mutation both reproduce: `_assert_owned_tasks_match_engine_truth` has exactly one call site outside its definition (eval/leak_test.py:157, inside `_run_scripted_game`, which walks only the 3 `_SCRIPTED_GAMES`), and `assert_packet_is_leak_clean` runs only `_assert_owned_task_discipline` (shape) + `assert_visible_entities_match_engine_truth` (players/bodies). But the IMPACT framing must go. (1) The exact mutation IS caught in CI, by a dedicated in-repo unit test the finding does not mention: tests/observation/test_packet_owned_tasks.py:205 `test_owned_task_ids_never_carry_another_players_tasks` asserts `packet.self_state.owned_task_ids == (own_map_id,)` per crewmate plus whole-packet foreign-id absence — it bites on precisely the widening the probe applies. (2) The champion-gate framing is close to vacuous: `_reconstruct_factory_records` (eval/leak_scan.py:858) constructs its OWN production `ObservationService`, so a candidate POLICY cannot influence `owned_task_ids` at all — the gate could only ever catch a production-code regression, which is what the unit test already covers. So this is a gate-composition gap plus a correction to audits/review-2026-08-19/B/observation-firewall.md §4's 'owned-task ownership (strong, engine-truth cross-check)' (true that the check exists, wrong about where it runs) — a one-line defence-in-depth fix, not a live regression risk for the re-ground. P2.

**As originally filed.** `_assert_owned_tasks_match_engine_truth` — the only check that compares SelfView.owned_task_ids against per-tick engine truth and hunts foreign task ids in the packet JSON — is called solely from the 3 scripted 4p/1i fixtures in eval/leak_test.py, not from `assert_packet_is_leak_clean`, so the factory sweeps and the ML champion gate see only the weak shape discipline.

**Finder evidence.**

```
Call sites: `grep -n "_assert_owned_tasks_match_engine_truth" eval/leak_test.py` -> `41: _assert_owned_tasks_match_engine_truth,` and `157: _assert_owned_tasks_match_engine_truth(` (inside `_run_scripted_game`, eval/leak_test.py:119-170, which walks only `_SCRIPTED_GAMES` at :86-90). `assert_packet_is_leak_clean` (eval/leak_scan.py:958-1030) runs `_assert_owned_task_discipline(packet)` (:1012, shape/sort/no-':'/pending-in-owned only) and `assert_visible_entities_match_engine_truth` (:1013, players+bodies only) — the engine-truth task check at :503 is never invoked. `scan_factory_packets` (:1040) -> `assert_no_factory_packet_leaks` (:1033) -> the same function is what training/bakeoff/harness.py:1833 and training/crew/scorer.py:1748 call.

MUTATION PROBE. Script .../wave0/B/owned_task_probe.py widens `ObservationService._owned_task_ids_for_agent` to `own set | every player's unfinished map ids` (keeping pending a member so the shape invariant still holds). `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../owned_task_probe.py`:
```
--- BASELINE ---
assert_packet_is_leak_clean (champion-gate path) failures: 0 NONE
_assert_owned_tasks_match_engine_truth (scripted-only) failures: 0 NONE
--- MUTATED (owner scope dropped) ---
sample owned sets: ["p-1 owned=('empty_trash', 'submit_scan', 'swipe_card')", "p-2 owned=('empty_trash', 'submit_scan', 'swipe_card')", ...]
assert_packet_is_leak_clean (champion-gate path) failures: 0 NONE
_assert_owned_tasks_match_engine_truth (scripted-only) failures: 8 ["p-1: p-1 owned_task_ids ('empty_trash', 'submit_scan', 'swipe_card') != engine-truth own unfinished set ('swipe_card',)"]
```
Every crewmate is handed every other crewmate's task list and the champion path is silent.

This is a live regression risk for the re-ground because a learned mover's encoder consumes the self channel (agents/tactical/features.py reads packet.self_state throughout, e.g. :399-400), and the prior audit already recorded this coverage as adequate — audits/review-2026-08-19/B/observation-firewall.md §4: 'owned-task ownership (strong, engine-truth cross-check)' — which is true only for the 3 scripted fixtures. agent_prompts/task-20-8-leak-scanner-entitlement.md cites `_assert_owned_tasks_match_engine_truth` as 'the in-repo engine-truth-cross-check precedent' and copies its signature shape, but its checklist never folds the precedent itself into the scan.
```

**Verifier evidence (independent re-run).**

```
CALL-SITE CHECK (fresh, whole repo): `grep -rn "_assert_owned_tasks_match_engine_truth" --include="*.py" .` -> exactly 3 hits: eval/leak_scan.py:503 (def), eval/leak_test.py:41 (import), eval/leak_test.py:157 (call). eval/leak_test.py:119-170 `_run_scripted_game` is driven only by `_SCRIPTED_GAMES` (:86-90, three fixtures). eval/leak_scan.py:1012-1013 confirms `assert_packet_is_leak_clean` calls `_assert_owned_task_discipline(packet)` then `assert_visible_entities_match_engine_truth(...)`, and never :503. `scan_factory_packets` (:1040) -> `assert_no_factory_packet_leaks` (:1033) -> `assert_packet_is_leak_clean`; called from training/bakeoff/harness.py:1833 and training/crew/scorer.py:1748. STRUCTURE CONFIRMED.

MY OWN MUTATION PROBE (scratchpad/vB4_probe.py — I patched `ObservationService._owned_task_ids_for_agent` to return `own | every unfinished map id`, keeping pending a member; 4p1i seed 3, 3 tasks/crewmate):
```
--- BASELINE ---
  sample owned sets: ["p-1 owned=('analyze_specimen','log_findings','swipe_card')", "p-2 owned=('align_engine_output','inspect_samples','upload_logs')", ...]
  assert_packet_is_leak_clean (champion-gate path) failures: 0 NONE
  _assert_owned_tasks_match_engine_truth (scripted-only) failures: 0 NONE
--- MUTATED (owner scope dropped) ---
  sample owned sets: every player -> all 9 unfinished map ids
  assert_packet_is_leak_clean (champion-gate path) failures: 0 NONE
  _assert_owned_tasks_match_engine_truth (scripted-only) failures: 4
```
REPRODUCES (my roster is 4 players so 4 not 8 failures; the escape is identical).

WHAT THE FINDING MISSES — I looked for other gates: `grep -rn owned_task_ids tests/observation/` surfaces tests/observation/test_packet_owned_tasks.py with `test_owned_task_ids_never_carry_another_players_tasks` (:205-254), which for each of three crewmates with DISJOINT map ids asserts `packet.self_state.owned_task_ids == (own_map_id,)` and that no foreign id (including the impostor's pretend window) appears anywhere in the packet JSON. That test fails immediately under the probe's mutation. Also `test_impostor_owned_task_ids_are_the_camouflage_window` (:258) and the multi-impostor variant (:310). So the leak surface is NOT unguarded in CI.

AND the gate cannot see candidate-specific behaviour anyway: eval/leak_scan.py:858 `service = ObservationService(game_map=game_map, audit_log_path=audit_path)` — the scanner builds the production service itself; the `agent_factory` only supplies policies, which have no path to `owned_task_ids`.
```

**Verifier note.** Core observation CONFIRMED and the one-line fix (add the engine-truth owned-task check next to eval/leak_scan.py:1013; PacketContext already carries state+map in both producers) is correct and worth doing. Downgraded from P1 because the finding's two impact arguments do not survive: the mutation it uses is caught by tests/observation/test_packet_owned_tasks.py:205 in ordinary CI, and no candidate policy can produce this leak in the first place. The genuinely useful part is the documentation correction to audits/review-2026-08-19/B/observation-firewall.md §4 and to agent_prompts/task-20-8-leak-scanner-entitlement.md, which cite the check as covering more than it does.

**Fix sketch.** Add `_assert_owned_tasks_match_engine_truth(packet, state=context.world_state, game_map=context.game_map)` to `assert_packet_is_leak_clean` (eval/leak_scan.py, next to the :1013 entitlement call). PacketContext already carries both, in both producers (eval/leak_test.py:143-145 post-advance state; eval/leak_scan.py:886-892 pre-advance state), and both are the state the packet was built from, so no signature change is needed. Then drop the now-redundant call at eval/leak_test.py:157 or leave it as the scripted-path belt-and-braces, and re-run the mutation above as the acceptance test.

## B-5 — A roll-call whereabouts on either side makes an alibi_conflict structurally un-STRONG: 60/60 recorded conflicts are WEAK, and the boundary-overlap rule mis-fires on same-tick claims

**Severity:** P3 (finder: P1). **Classification:** quality-debt (boundary-overlap reason mis-fire, behaviourally inert); the narrow-window band is WORKING AS DESIGNED, not a defect. **Verdict:** ADJUSTED. **Area:** meetings-detector / meetings/transcript.py — alibi_conflict banding (_conflict_weak_reasons / _weak_signal_reasons). **Confidence:** high.
**Merged from:** finder-meetings-detector.json#1.

**Claim.** Every mechanical claim reproduces verbatim, but the DEFECT framing is wrong and the severity is far too high. Two separable halves. (1) The narrow-window half is NOT a defect: Task 18.9's contract deliberately scoped the degenerate-single-tick exemption to `alibi_vs_sighting` ('Scope the exemption to the degenerate `from_tick == to_tick` self-alibi class only', tasks/phase-18.md implementation hint; DoD says 'mints a STRONG `alibi_vs_sighting` flag'), and the SAME contract already measured the price of promoting this class — 'today: 25 corpus lies, 20 crew-authored / 5 impostor-authored, all weak' (tasks/phase-18.md:697-699), i.e. 4:1 against innocents. I measured the analogous number for the 60 recorded alibi_conflicts and it is WORSE: 51 of 60 flagged subjects are CREWMATES, 9 are IMPOSTORS (15%) — BELOW the 22% (9p2i) / 25% (4p1i) impostor base rate. Promoting them would lift 51 innocents from 0.58 to 0.80, straight over the 0.6 gate: the weak band is the anti-railroad machinery from audit-2026-06-10 C-1 / phase-10 doing its job, not a bug. Further, production ALREADY withdraws the 18.9 exemption on the sightings path whenever grounding records are supplied (`grounded_prosecution = bool(sighting_records)`, meetings/transcript.py:1668; the withdrawal is documented at :2759-2764) — which is why 0 of 100 recorded `alibi_vs_sighting` flags are STRONG either. Making the CONFLICT path more permissive than the SIGHTING path would invert the shipped design. (2) The boundary-overlap half IS a genuine, unambiguous bug — `left.to == right.from or right.to == left.from` (meetings/transcript.py:3568-3572) is trivially true when both claims are the SAME single tick, appending WEAK_REASON_BOUNDARY_OVERLAP against its own documented rationale ('a movement pair ... not two incompatible accounts', :3539-3541). But it is BEHAVIOURALLY INERT: narrow-window already weak-bands 60/60, so removing it changes no band, only the audit-trail reason list. That makes the confirmed residue an audit-trail correctness / quality-debt item at P3, not a P1 defect requiring a re-record before the re-ground.

**As originally filed.** Task 16.7 indexes every WhereaboutsClaim as a degenerate single-tick alibi (span 0), which unconditionally trips the narrow-window band and — when both sides name the same tick — the boundary-overlap band whose stated rationale is the opposite case, so the flat contradiction "you said LABS at t5 and REACTOR at t5" prices at the sub-gate weak delta and the alibi_conflict kind mints zero STRONG evidence anywhere in the committed baseline-7 bytes.

**Finder evidence.**

```
meetings/transcript.py:3509 `if alibi.claim.to_tick - alibi.claim.from_tick < NARROW_ALIBI_WINDOW_TICKS:` with NARROW_ALIBI_WINDOW_TICKS=2 (:617) — a whereabouts indexes with from_tick==to_tick (:2291-2304), span 0 < 2, so it ALWAYS carries WEAK_REASON_NARROW_WINDOW. meetings/transcript.py:3554-3558 ORs that reason across the pair (`if WEAK_REASON_NARROW_WINDOW in left_reasons or ... in right_reasons`), so one roll-call answer weak-bands the whole conflict. meetings/transcript.py:3568-3572 `if (left.claim.to_tick == right.claim.from_tick or right.claim.to_tick == left.claim.from_tick)` is trivially true when both claims are the SAME single tick, appending WEAK_REASON_BOUNDARY_OVERLAP whose docstring rationale (:3539-3541) is "a movement pair (\"CAFETERIA t0-6\" + \"STORAGE t6-9\"), not two incompatible accounts" — exactly inverted here.

Demonstrated (scratch script, `uv run python .../whereabouts_band.py`):
```
--- A same-speaker roll-call pair
   kind=alibi_conflict weak=True
    Alibis place p-1 in LABS (ticks 5-5) and in REACTOR (ticks 5-5); intervals overlap. [weak signal: self-stated alibi pair; narrow alibi window; endpoint-tick overlap]
--- B roll-call vs proxy single-tick alibi
   kind=alibi_conflict weak=True
    Alibis place p-1 in LABS (ticks 5-5) and in REACTOR (ticks 5-5); intervals overlap. [weak signal: narrow alibi window; endpoint-tick overlap]
```

Corpus census over replays/ml_corpus + replays/samples (`uv run python .../reasons.py`, splitting each recorded flag with meetings.transcript._split_weak_marker):
```
kind / is_weak counts:
   ('alibi_conflict', True) 60
   ('alibi_vs_physical', False) 12
   ('alibi_vs_physical', True) 1
   ('alibi_vs_sighting', True) 100
   ('vent_sighting', False) 448
reason counts:
   ('alibi_conflict', 'narrow alibi window') 60
   ('alibi_conflict', 'self-stated alibi pair') 59
   ('alibi_conflict', 'endpoint-tick overlap') 58
```
Every recorded alibi_conflict (60/60) carries narrow-window; 58 also carry boundary-overlap. Zero are STRONG. Shape census over the same corpus (`uv run python .../testimony_gap.py`): WhereaboutsClaim 2269 vs AlibiClaim 706, i.e. 76% of all location accounts are the span-0 shape.

Band consequence measured against the production rule (`uv run python .../marker_spoof2.py`, agents.memory.beliefs.apply_contradiction_rule on a 0.5 prior): STRONG -> 0.800, WEAK -> 0.580, against the §4.6 gate of 0.6 (meetings/constants.py:29 DEFAULT_SKIP_CONFIDENCE_THRESHOLD=0.6). A weak flag can never cross the gate alone.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ — every cited line is exact: meetings/transcript.py:3509 `if alibi.claim.to_tick - alibi.claim.from_tick < NARROW_ALIBI_WINDOW_TICKS`, :617 `NARROW_ALIBI_WINDOW_TICKS: Final[int] = 2`, :2291-2304 indexes WhereaboutsClaim as `AlibiClaim(from_tick=observation.tick, to_tick=observation.tick)`, :3554-3558 ORs narrow-window across the pair, :3568-3572 the boundary-overlap append, :3539-3541 the inverted rationale.

MY OWN BAND DEMONSTRATION (scratchpad/vB5_band.py) — I added a CONTROL the finder did not run:
```
--- A same-speaker roll-call pair
   kind=alibi_conflict weak=True
    Alibis place p-1 in LABS (ticks 5-5) and in REACTOR (ticks 5-5); intervals overlap. [weak signal: self-stated alibi pair; narrow alibi window; endpoint-tick overlap]
--- B roll-call vs proxy single-tick alibi
   kind=alibi_conflict weak=True
    ... [weak signal: narrow alibi window; endpoint-tick overlap]
--- C control: two multi-tick PROXY alibis (no degenerate side)
   kind=alibi_conflict weak=False
    Alibis place p-1 in LABS (ticks 2-8) and in REACTOR (ticks 3-9); intervals overlap.
```
A and B REPRODUCE VERBATIM; C confirms STRONG is reachable for genuine multi-tick pairs, so the mechanism is exactly the degenerate class.

MY OWN CORPUS CENSUS (scratchpad/vB5_census.py, replays/ml_corpus + replays/samples, 300 files / 668 meetings, splitting with meetings.transcript._split_weak_marker):
```
('alibi_conflict', True) 60 | ('alibi_vs_physical', False) 12 | ('alibi_vs_physical', True) 1
('alibi_vs_sighting', True) 100 | ('vent_sighting', False) 448
('alibi_conflict','narrow alibi window') 60 | ('alibi_conflict','self-stated alibi pair') 59 | ('alibi_conflict','endpoint-tick overlap') 58
```
EXACT MATCH. Shape census (scratchpad/vB5_shapes.py, ml_corpus 476 meetings): whereabouts 2269, alibi 706 (76.3%) — EXACT MATCH. Arithmetic: agents/memory/beliefs.py:104 CONTRADICTION_SUSPICION_DELTA=0.3, :108 WEAK_CONTRADICTION_SUSPICION_DELTA=0.08, vs meetings/constants.py:28 DEFAULT_SKIP_CONFIDENCE_THRESHOLD=0.6 -> 0.5+0.3=0.80 STRONG, 0.5+0.08=0.58 WEAK. EXACT MATCH.

THE NEW MEASUREMENT THAT CHANGES THE VERDICT (mine; roles read per-set from each directory's tournament-eval-report.json, keyed by (dir, filename) so the 9p2i/4p1i basename collision does not corrupt it):
```
alibi_conflict flags: 60   subject roles: {'CREWMATE': 51, 'IMPOSTOR': 9}
impostor share 9/60 = 0.150
```
Against impostor base rates of 2/9=0.222 (9p2i) and 1/4=0.250 (4p1i), this class fires BELOW chance on impostors. Promoting all 60 to STRONG would push 51 innocents to 0.80 vs 9 impostors.

DECLARED-SCOPE CHECK: tasks/phase-18.md Task 18.9 'Implementation hint' — 'Scope the exemption to the degenerate `from_tick == to_tick` self-alibi class only — the narrow-window weak reason and the two-source discipline for genuine multi-tick alibis do not move'; DoD — 'exemption ON, a contradicted single-tick whereabouts claim mints a STRONG `alibi_vs_sighting` flag'. The conflict path was never in scope, and the same contract records the 20-crew/5-impostor counterfactual. meetings/transcript.py:1668 `grounded_prosecution = bool(sighting_records)` and :2759-2764 document the production withdrawal of even the sightings-path exemption.
```

**Verifier note.** Mechanics: fully confirmed, verbatim, on every number. Verdict: the finding reads a working anti-railroad band as a defect. The decisive counter-evidence is in the repo already (tasks/phase-18.md's 20-crew/5-impostor counterfactual) and in my own recount (51 crew / 9 impostor across the 60 recorded flags, below base rate) — the finder measured volume and band but never precision, which is the number that decides whether a band is mis-priced. What survives is narrow and cheap: WEAK_REASON_BOUNDARY_OVERLAP fires against its own docstring rationale on same-single-tick pairs (58 of 60 flags carry it), which is an audit-trail/reason-list bug with zero behavioural effect since narrow-window already bands all 60. Fix sketch part (a) is worth taking on those grounds alone and needs NO re-record if the reason list is treated as derived; part (b) should be REJECTED absent a precision study showing the promoted subset is impostor-enriched.

**Fix sketch.** Give _conflict_weak_reasons the same degenerate-claim adjudication Task 18.9 gave the sightings path: (a) suppress WEAK_REASON_BOUNDARY_OVERLAP when the two windows are the SAME single tick (left.from==left.to==right.from==right.to) — a shared junction tick is only movement fuzz when at least one side is a real multi-tick window; (b) suppress WEAK_REASON_NARROW_WINDOW for a side that is a degenerate single-tick SELF-placement (the whereabouts class), whose one tick is the claim's interior, not a transit window. Keep both bands verbatim for genuine 1-2 tick AlibiClaims. Re-record is required (recorded bytes move), so this belongs in the same wave as the re-ground, not after it.

## B-6 — Contradictions are re-derived WITHOUT the private grounding channels in four live consumers (the ML conviction label, the referee supply gauge, watchability and vote-correctness), inverting the STRONG/WEAK band on the exact corpus the re-ground fits

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** meetings-detector + eval-instruments / training/conviction/dataset.py + eval/meeting_quality.py — flags_minted label vs meetings/transcript.detect_contradictions  ||  eval-instruments / meeting_quality + watchability + the conviction fit. **Confidence:** high.
**Merged from:** finder-meetings-detector.json#2, finder-eval-instruments.json#2.

**Claim.** MERGED CLAIM. `detect_contradictions(transcript, roster=...)` is called with no vent_witness_records / move_witness_records / sighting_records and no trigger_kind at four live sites -- training/conviction/dataset.py:491 (the conviction model's `flags_minted` referee label), eval/meeting_quality.py:2382 (`compute_supply_gauges`, the flag census behind `flags_per_meeting`), eval/watchability.py:1470 (`contradictions_by_subject`) and eval/vote_correctness.py:595 (the genuine-class census) -- while production threads all four channels (meetings/manager.py:1225-1232). At baseline 7 the two re-derivations disagree with the recorded flag set on 61 of 476 corpus meetings (12.8%), lose 43 of 120 recorded non-vent flags and mint 46 the game never had on replays/ml_corpus/9p2i, and INVERT the band on the whole alibi_vs_sighting class (8 STRONG re-derived vs 0 recorded). So a Layer-1 selection floor, a referee supply gauge and the conviction model's own label all measure a detector counterfactual rather than the recorded evidence supply.

AS FILED BY finder-meetings-detector: `flags_minted` (the conviction model's referee label) and `compute_supply_gauges`'s flag census both call detect_contradictions with roster only — no vent/move/sighting records and no trigger_kind — which at baseline 7 (all those levers unconditional) disagrees with the recorded flag set in 61 of 476 corpus meetings and reports 8 STRONG alibi_vs_sighting flags in a class production minted zero of.

AS FILED BY finder-eval-instruments: `compute_supply_gauges` (and watchability's `contradictions_by_subject`, vote_correctness's genuine-class census and training/conviction/dataset.py's `rederived` label) call `detect_contradictions(transcript, roster=...)` with no vent/move/sighting grounding channels, which on the committed bytes loses 43 of 120 recorded non-vent flags and mints 46 the game never had — so `flags_per_meeting`, a Layer-1 selection floor and a conviction feature, measures a detector counterfactual rather than the recorded evidence supply.

**Finder evidence.**

```
MERGE NOTE. Two finders reached this independently from opposite ends (meetings-detector from the detector's band logic; eval-instruments from the instrument census). Both filed P1 / defect -- NO severity disagreement. Both evidence blocks are kept verbatim below because they measure different, complementary quantities: meetings-detector measures the per-meeting id-set delta and the STRONG/WEAK band inversion with a flag-by-flag cause attribution; eval-instruments measures the lost/spurious split per kind across four committed sets and names the two additional consumers (watchability, vote_correctness) plus the in-repo standard (scripts/counterfactual_phase20.py's `off_flags_match_recorded` self-check).

========== EVIDENCE FROM finder-meetings-detector (finder-meetings-detector.json#2) ==========
training/conviction/dataset.py:491 `rederived = len(detect_contradictions(entry.transcript, roster=roster))` — no vent_witness_records / move_witness_records / sighting_records / trigger_kind. eval/meeting_quality.py:2382 `flags = detect_contradictions(meeting.transcript, roster=roster)` — the gauge the label mirrors (dataset docstring :78-85). Production passes all four: meetings/manager.py:1225-1232.

Measured on replays/ml_corpus (`uv run python .../label_gap.py`):
```
meetings: 476
records-free rederived flags total: 124
recorded non-vent flags total: 121
meetings whose rederived id-set != recorded id-set: 61
count-delta histogram (rederived - recorded): {-2: 7, -1: 21, 0: 418, 1: 23, 2: 6, 3: 1}
```
Band inversion (`uv run python .../band_gap.py`):
```
RECORDED  non-vent: strong 10 weak 111 | STRONG alibi_vs_sighting 0
REDERIVED records-free: strong 8 weak 116 | STRONG alibi_vs_sighting 8
```
Cause, flag by flag (`uv run python .../strong_cause.py`) — SAME contradiction_id, opposite band. 6 of the 8 are the 18.9 interior exemption, which meetings/transcript.py:2765 `interior_exempt = not grounded_prosecution and (...)` re-enables the moment the caller supplies no sighting records; 2 are grounded-prosecution demotions:
```
replay-seed-1008.jsonl headless-seed-1008:meeting-0 whereabouts_side=True
   rederived: Alibi places p-8 in ADMIN (ticks 10-10); sighting reports p-8 in MEDBAY at tick 10.
   recorded : ... [weak signal: narrow alibi window; endpoint-ti...
replay-seed-1038.jsonl headless-seed-1038:meeting-0 whereabouts_side=False
   rederived: Alibi places p-8 in LABS (ticks 3-9); sighting reports p-8 in WEST_HALL at tick 8.
   recorded : ... [weak signal: ungrounded sighting]
replay-seed-1064.jsonl headless-seed-1064:meeting-0 whereabouts_side=False
   recorded : ... [weak signal: single grounded source]
```
This materially DEEPENS the declared audits/audit-phase-20-baseline-7.md §10.3 loss (which names the two TEST re-derivations) by naming two live consumers it does not: the ML conviction label and the referee supply gauge.

========== EVIDENCE FROM finder-eval-instruments (finder-eval-instruments.json#2) ==========
Re-derivation sites: eval/meeting_quality.py:2382 `flags = detect_contradictions(meeting.transcript, roster=roster)`, eval/watchability.py:1470, eval/vote_correctness.py:595, training/conviction/dataset.py:491 `rederived = len(detect_contradictions(entry.transcript, roster=roster))`. The signature that shows what is being dropped: meetings/transcript.py:1490-1500 (`vent_witness_records`, `move_witness_records`, `sighting_records` all default None). Per-flag-id set difference over the committed bytes (`detect_contradictions(transcript, roster=ballot voters)` vs the recorded `contradictions` array, vent_sighting excluded): replays/ml_corpus/9p2i recorded_non_vent=120 reproduced=77 lost=43 spurious=46; replays/samples/9p2i recorded_non_vent=52 reproduced=33 lost=19 spurious=9; ml_corpus/4p1i 1/1/0/0. By kind on ml_corpus/9p2i: recorded alibi_conflict 38 / alibi_vs_physical 11 / alibi_vs_sighting 71 vs re-derived 38 / 1 / 84. Aggregate through the real instrument (`assemble_tournament_report` + `compute_supply_gauges` + `watchability._persisted_vent_flag_count`): ml_corpus/9p2i merged=431 vs recorded_total=428; samples/9p2i merged=134 vs recorded_total=144. That the project's own standard is the grounded re-derivation is visible at scripts/counterfactual_phase20.py:775-781, which threads all three channels and then self-checks `if tuple(flags_by_leg["off"]) == tuple(entry.contradictions): walk.off_flags_match_recorded += 1` (:786-787); eval/funnel.py:1385 and eval/deception_instruments.py:644 already pass `sighting_records`.
```

**Verifier evidence (independent re-run).**

```
ALL FOUR CALL SITES REPRODUCE AT HEAD d8ec0a1c, roster-only, no vent/move/sighting records and no trigger_kind: training/conviction/dataset.py:491 `rederived = len(detect_contradictions(entry.transcript, roster=roster))`; eval/meeting_quality.py:2382 `flags = detect_contradictions(meeting.transcript, roster=roster)`; eval/watchability.py:1470 `for flag in detect_contradictions(meeting.transcript, roster=roster):`; eval/vote_correctness.py:595 same shape. Production threads all four channels at meetings/manager.py:1225-1232. Signature with the three defaulted-None channels at meetings/transcript.py:1490-1500.

MY OWN RE-DERIVATION (scratchpad/wave0/B/v1/b6_rederive.py, `PYTHONPATH=. uv run python`, per-flag contradiction_id set difference against the recorded non-vent flags) reproduces BOTH finders' numbers EXACTLY, digit for digit:
```
replays/ml_corpus/9p2i: recorded_non_vent=120 reproduced=77 lost=43 spurious=46
    recorded kinds {alibi_conflict:38, alibi_vs_sighting:71, alibi_vs_physical:11}
    rederived kinds {alibi_vs_sighting:84, alibi_conflict:38, alibi_vs_physical:1}
replays/ml_corpus/4p1i: recorded_non_vent=1 reproduced=1 lost=0 spurious=0
replays/samples/9p2i: recorded_non_vent=52 reproduced=33 lost=19 spurious=9
ml_corpus meetings: 476
records-free rederived flags total: 124
recorded non-vent flags total: 121
meetings whose rederived id-set != recorded id-set: 61
count-delta histogram (rederived - recorded): {-2: 7, -1: 21, 0: 418, 1: 23, 2: 6, 3: 1}
RECORDED  non-vent: strong 10 weak 111 | STRONG alibi_vs_sighting 0
REDERIVED records-free: strong 8 weak 116 | STRONG alibi_vs_sighting 8
```
Aggregate half also reproduces exactly via the real instruments (`compute_watchability` + `assemble_tournament_report` + `compute_supply_gauges` + `_persisted_vent_flag_count`): ml_corpus/9p2i rederived 123 + persisted_vent 308 = merged 431 vs recorded_total 428 (json census 308+38+71+11); samples/9p2i 42 + 92 = 134 vs recorded_total 144 (92+29+21+2).

NEW EVIDENCE I FOUND THAT STRENGTHENS THE FINDING: eval/watchability.py:269-272 asserts of `contradictions_by_subject` that it is 'RE-DERIVED via detect_contradictions under the ballot-voter roster ... -- ON THE COMMITTED SET RECORDED == RE-DERIVED, VERIFIED BY THE PARITY TEST'. That identity is FALSE on the baseline-7 committed bytes (61 of 476 ml_corpus meetings diverge; samples/9p2i loses 19 and mints 9), and the only parity test in tests/eval/test_watchability.py is `test_historical_15_2_geomean_parity_frozen_pin_on_9p2i` (:126), a geomean roll-up pin against the lab scorer -- it does not verify flag identity. So the module documents a guarantee it neither holds nor checks.

NOT SPECIFIED / NOT A DECLARED CARRY: audits/audit-phase-20-baseline-7.md §10.3 ('What the re-derivation can no longer prove, and why') declares this loss for exactly THREE committed-bytes mirrors, all of them TESTS (tests/meetings/test_contradictions.py, tests/meetings/test_transcript.py, and the three retired 20.26 exemplars). It names no live consumer. eval/watchability.py:2000-2012 (`_persisted_vent_flag_count`) documents the vent channel as the ONE thing the re-derivation cannot reproduce, i.e. the declared design intent is that everything else reproduces -- which is what breaks here.

NOT A RE-REPORT of any listed known-open item (C-46/C-83/C-126/C-130/C-79/C-80/C-101/C-107/C-62/C-33/C-45 are the serial tournament loop, import-time side effects, the operator env surface, dead prompt-set weight, the frontend God module / derivation layer / component tests / test-infrastructure layer, the God-module split refusal, the C-33 duplication and the history rewrite -- audits/audit-phase-20-close.md:399,411-416 and audits/review-2026-08-19/README.md:148-179). F1-F5 are the red campaign tier, two stale narrations, three word budgets, the audits-index ladder tip and the carried staging ref. The duplicate alibi_vs_sighting mint is 20.43's production-side dedup, a different object.

FEASIBILITY CORROBORATION: the reconstruction the fix needs already exists in a sibling instrument -- eval/funnel.py:1230-1263 rebuilds `sighting_records_by_speaker` from a replay walk (`agent.sighting_records_for_meeting()`), and scripts/counterfactual_phase20.py:775-787 threads all three channels and self-checks `off_flags_match_recorded`.
```

**Verifier note.** Every number in both merged evidence blocks reproduced exactly on fresh code. Two precision notes, neither changing the verdict: (1) 'INVERT the band on the whole alibi_vs_sighting class' is precisely 0 -> 8 STRONG within a class of 71 recorded / 84 re-derived flags -- an inversion of that class's STRONG cell, not of the whole class's banding. (2) The eval-instruments half's 'eval/funnel.py:1385 and eval/deception_instruments.py:644 already pass sighting_records' is true but those calls go to `grounded_vouch_subjects`, not `detect_contradictions`; the point they support (the channel is available in the eval layer) still holds, and eval/funnel.py:1230-1263 is the stronger citation.

**Fix sketch.** FROM finder-meetings-detector: Two independent choices, both cheap. (1) Label fidelity: read the RECORDED entry.contradictions for the flag census instead of re-deriving (the recorded set IS what the meeting priced), or thread the invertible channels the way tests/_helpers/committed.py already reconstructs them, and pin the divergence at 0. (2) Guard: add a committed pin asserting `len(detect_contradictions(entry.transcript, roster=...)) == len([f for f in entry.contradictions if f.kind != 'vent_sighting'])` over the corpus, so a future lever graduation cannot silently re-open the gap. Do this BEFORE the re-fit — a label wrong on 12.8% of rows, with the band inverted on the whole alibi_vs_sighting class, is fit noise the model will chase.

FROM finder-eval-instruments: Either (a) reconstruct the three grounding channels the way scripts/counterfactual_phase20.py does and thread them into the supply-gauge / conviction re-derivations, or (b) stop re-deriving and read `meeting.contradictions` (the bytes the game recorded), keeping the re-derivation only where a counterfactual is wanted. Whichever is chosen, add the counterfactual script's `off_flags_match_recorded` identity as an assertion so the census can never silently diverge from the record again. This must land before the conviction model is re-fit: the label it learns is this census.

COLLATION NOTE: the two sketches agree on the choice (read the recorded `entry.contradictions` bytes, or reconstruct and thread the three grounding channels the way scripts/counterfactual_phase20.py:775-787 already does) and on the guard (pin the re-derived-vs-recorded identity so the census cannot silently diverge again). Both insist it lands BEFORE the conviction re-fit, since the label the model learns IS this census.

## B-7 — Testimony-as-content drops the two largest structured shapes: WhereaboutsClaim (2,269) and SawMoveObservation (1,160) never reach any listener's memory

**Severity:** P1. **Classification:** design-limitation. **Verdict:** CONFIRMED. **Area:** meetings-detector / meetings/manager.py::derive_reported_testimony + meetings/schemas.py::ReportedStatementKind. **Confidence:** high.
**Merged from:** finder-meetings-detector.json#3.

**Claim.** The reduction that exists to stop social info collapsing to a scalar carries only the five kinds that existed when it was written, so the 3,429 roll-call self-placements and witnessed transitions in the baseline-7 corpus — more statements than the saw_player channel it does carry — are visible inside the meeting and then vanish, never entering episodic memory or the alibi_map.

**Finder evidence.**

```
meetings/schemas.py:539-541 `ReportedStatementKind: TypeAlias = Literal["saw_player", "saw_vent", "alibi", "accusation", "corroboration"]` — no whereabouts, no saw_move. meetings/manager.py:3822-3875: the observation loop handles only SawPlayerObservation (:3823) and SawVentObservation (:3835); the claim loop only AlibiClaim (:3847), AccusationClaim (:3858), CorroborationClaim (:3866). WhereaboutsClaim and SawMoveObservation fall through silently.

Neither shape is picked up anywhere else on the ingest side:
```
$ grep -rn "WhereaboutsClaim\|SawMoveObservation" --include="*.py" agents/ orchestrator/ | grep -v test
(no output)
```

Volume on the corpus the re-ground fits (`uv run python .../testimony_gap.py`, 476 meetings):
```
  SawPlayerObservation: 2794
  WhereaboutsClaim: 2269      <- dropped
  AccusationClaim: 2243
  SawMoveObservation: 1160    <- dropped
  CorroborationClaim: 1074
  AlibiClaim: 706
```
Second-order: agents/memory/store.py:575-588 populates `alibi_map` via `BeliefState.record_alibi` from `alibi` statements only, so the alibi map is fed by 706 of the 2,975 location accounts (24%) — the roll-call channel the substrate elicits most is exactly the one it forgets.
```

**Verifier evidence (independent re-run).**

```
CODE REPRODUCES AT HEAD. meetings/schemas.py:539-541 `ReportedStatementKind: TypeAlias = Literal["saw_player", "saw_vent", "alibi", "accusation", "corroboration"]` -- five members, no whereabouts, no saw_move. meetings/manager.py:3822-3875 (`derive_reported_testimony`): the observation loop handles only `SawPlayerObservation` and `SawVentObservation`; the claim loop only `AlibiClaim`, `AccusationClaim`, `CorroborationClaim`. Everything else falls through with no else-branch and no raise.

`grep -rn "WhereaboutsClaim\|SawMoveObservation" --include="*.py" agents/ orchestrator/ | grep -v test` -> EMPTY (my own run). Neither shape has any ingest-side reader.

MY OWN CORPUS CENSUS (json walk over replays/ml_corpus/{9p2i,4p1i}, transcript turn observations+claims by discriminator) reproduces the finder's table EXACTLY:
```
meetings 476
  saw_player 2794
  whereabouts 2269   <- dropped
  accusation 2243
  saw_move 1160      <- dropped
  corroboration 1074
  alibi 706
  found_body 586
  saw_vent 391
  completed_task 310
```
2269 + 1160 = 3429 > 2794 (saw_player), so 'more statements than the saw_player channel it does carry' holds. 706 / (2269+706) = 23.7% for the alibi_map arithmetic. Per-set: ml_corpus/9p2i whereabouts 2177 / saw_move 1136; samples/9p2i 763 / 468.

NOT A DECLARED CARRY -- and the repo's own precedent points the other way. meetings/schemas.py:95-116 (`SawVentObservation`) used to read 'deliberately NOT reduced to a ReportedStatement'; Task 20.29 ADDED the `saw_vent` kind and CORRECTED that line (tasks/phase-20.md:4647 'a ReportedStatementKind member for the spoken vent; the SawVentObservation docstring correction'; agent_prompts/task-20-29-*.md cites ':537-539 (ReportedStatementKind, the closed FOUR)'). So widening the kind set when a new sayable shape lands is the established pattern. By contrast meetings/schemas.py:124-148 (`WhereaboutsClaim`) and :154-181 (`SawMoveObservation`) say nothing at all about the reduction -- the exclusion is silent, not declared. tasks/phase-13-5.md:145-152 (the originating 13.5.2 contract) specifies the reduction over the shapes that existed then and never scopes out later ones.

NOT A RE-REPORT: no listed known-open id covers testimony-as-content coverage.
```

**Verifier note.** Confirmed as filed. One completeness note the finding does not make: `CompletedTaskObservation` (310 occurrences) and `FoundBodyObservation` (586) ALSO fall through `derive_reported_testimony` unhandled, so the gap is four shapes, not two -- the two named are simply the largest. One precision note: whereabouts DO reach listeners indirectly through the SCALAR channel (the detector indexes them as degenerate single-tick self-alibis, meetings/transcript.py:2291-2304, so a whereabouts-derived contradiction still moves suspicion), so the title's 'never reach any listener's memory' is shorthand; the claim body's precise form ('never entering episodic memory or the alibi_map') is what I verified and it is exactly right.

**Fix sketch.** Add "whereabouts" and "saw_move" to ReportedStatementKind and emit them in derive_reported_testimony: a whereabouts maps cleanly onto the existing (subject=speaker, from_tick==to_tick, room) shape and should also feed record_alibi like an `alibi` does; a saw_move needs either a second room field or the DESTINATION placement the detector already reads it as (meetings/transcript.py:2520-2531 builds exactly that SawPlayerObservation). Both move recorded bytes at rest (new episodic rows), so this is a re-record-class change — schedule it with the re-ground wave and state the before/after memory-row count.

## B-8 — The belief line's "last seen in ROOM at tick T" is fed ONLY by witnessed transitions, so it contradicts the agent's own sightings in 19% of rendered rows

**Severity:** P1. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** memory-render / belief-line suffix (agents/memory/store.py, agents/memory/working.py). **Confidence:** high.
**Merged from:** finder-memory-render.json#1.

**Claim.** `working.last_seen` has exactly one production writer, `_record_movement_sightings`, which reads `saw_player_move` rows only, so the non-elastic belief block asserts a room/tick that the same prompt's own `saw_player` observations contradict at a strictly later tick.

**Finder evidence.**

```
CODE. agents/memory/store.py:2036-2038 — `for event in episodic.recent(since_tick=0):` / `if event.type != EVENT_SAW_PLAYER_MOVE:` / `continue` (ordinary `saw_player` rows never reach `working.record_sighting`). agents/memory/store.py:2126 — `last_seen_suffix = _format_last_seen_suffix(working.last_seen(player_id))`; store.py:2198-2201 renders `f"last seen in {last_seen.room} at tick {last_seen.tick}"`. agents/memory/working.py:11-20 confirms the single writer: "``record_sighting`` is called by ``agents/memory/store.py`` (``_record_movement_sightings``, at render time) for every witnessed room->room transition". `grep -rn "record_sighting" --include="*.py" . | grep -v tests` returns only that call site.

REPRO (scratchpad/wave0/B/repro_lastseen.py; `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../repro_lastseen.py`) — one witnessed move at tick 2 into ADMIN, then ordinary sightings in LABS at ticks 3-5:
```
## Recent observations (most salient first):
- [obs p-1:2:1] [tick 2] You saw p-3 move from CAFETERIA to ADMIN.
- [obs p-1:3:1] You saw p-3 in LABS ticks 3-5.

## Your current beliefs:
- p-3: suspicion 0.80 (last seen in ADMIN at tick 2)
```

CORPUS. Scan of every recorded prompt in replays/ml_corpus (scratchpad/wave0/B/scan_lastseen.py, plus a wrong-room refinement): extract each `- p-N: ... (last seen in ROOM at tick T)` row and compare with the LATEST sighting of that player visible in the SAME rendered memory (span, single, witnessed vent/kill, or witnessed move):
```
files: 200
belief rows carrying a last-seen suffix: 7863
rows whose SAME-PROMPT observations show a LATER sighting: 2533  (32.2 %)
stale AND wrong room: 1523  (19.4 %)
```
A verbatim recorded case (replays/ml_corpus/9p2i/replay-seed-1001.jsonl, agent p-6) carries both `- [obs p-6:13:1] [tick 13] You saw p-3 in MEDBAY (with p-7) ...` and `- p-3: suspicion 1.00 (last seen in MEDBAY at tick 8)` — 5 ticks stale.

WHY IT MATTERS STRUCTURALLY. The belief block is the NON-elastic carve-out (store.py:2296-2302 `non_elastic_blocks`; :2314-2330 charges it first and sheds trail then observations against the remainder), so under a tight budget the model can be left with ONLY the false statement. The correct derivation already exists in the codebase for the ML side: agents/tactical/features.py:456-482 `_episodic_last_seen` scans BOTH `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE` and keeps the latest — so the tactical feature encoder and the LLM prompt disagree about the same fact.

UNGATED. No test covers the `saw_player`-only case: tests/agents/test_memory_rendering.py:1323-1400 (`TestMovementPerceptionRender`) exercises `_saw_player_move_event` exclusively.
```

**Verifier evidence (independent re-run).**

```
CODE REPRODUCES AT HEAD. agents/memory/store.py:2036-2038 (`_record_movement_sightings`): `for event in episodic.recent(since_tick=0): / if event.type != EVENT_SAW_PLAYER_MOVE: / continue`. store.py:2126 `last_seen_suffix = _format_last_seen_suffix(working.last_seen(player_id))`; store.py:2197-2201 `return f"last seen in {last_seen.room} at tick {last_seen.tick}"`. Single writer confirmed by my own `grep -rn "record_sighting" --include="*.py" . | grep -v tests` -> zero non-test hits besides the store call. agents/memory/working.py:11-22 states the same.

MY OWN INDEPENDENT PROBE (scratchpad/wave0/B/v1/probe_lastseen.py -- hand-built memory: one saw_player_move into ADMIN at t2, then plain saw_player rows in LABS at t3/t4/t5; `PYTHONPATH=. uv run python`):
```
## Recent observations (most salient first):
- [tick 2] You saw p-3 move from CAFETERIA to ADMIN.
- You saw p-3 in LABS ticks 3-5.

## Your current beliefs:
- p-3: suspicion 0.80 (last seen in ADMIN at tick 2)
```
The rendered belief line contradicts the observation two lines above it.

MY OWN CORPUS SCAN (scratchpad/wave0/B/v1/lastseen.py -- independently written regex extraction of every `- p-N: ... (last seen in ROOM at tick T)` belief row and every placement-bearing `- [obs ...]` line in the SAME recorded prompt: move -> destination, span -> end tick, single sighting, roll-call 'every other player in R', witnessed vent, witnessed kill, own kill), over replays/ml_corpus/{9p2i,4p1i}:
```
files: 200
belief rows carrying a last-seen suffix: 7863
rows whose SAME-PROMPT observations show a LATER sighting: 2703 (34.4 %)
stale AND wrong room: 1539 (19.6 %)
```
The denominator (7863) and the headline 19% figure reproduce; my staleness counts run slightly HIGHER than the finder's (2533 / 32.2% and 1523 / 19.4%), which is parse-vocabulary drift in the more-inclusive direction, not a refutation.

VERBATIM EXEMPLAR REPRODUCES BYTE-FOR-BYTE (replays/ml_corpus/9p2i/replay-seed-1001.jsonl, agent p-6, same prompt):
```
- [obs p-6:13:1] [tick 13] You saw p-3 in MEDBAY (with p-7) (moved from LABS, last seen there at tick 7).
- p-3: suspicion 1.00 (last seen in MEDBAY at tick 8)
```

STRUCTURAL HALF REPRODUCES: agents/memory/store.py:2295-2301 puts `beliefs_block` in `non_elastic_blocks`; :2314-2330 charges the non-elastic text first and sheds the trail then the observations against the remainder -- so under a tight budget the contradicting observation is the half that is dropped. The correct derivation does exist for the ML side: agents/tactical/features.py:454-481 `_episodic_last_seen` scans BOTH EVENT_SAW_PLAYER and EVENT_SAW_PLAYER_MOVE and keeps the latest, and :484+ `_combined_last_seen` reconciles it with the render cache -- so the feature encoder and the LLM prompt genuinely disagree about the same fact.

NOT SPECIFIED. DESIGN.md:651-653 only records that Task 13.5.4 wires last_seen from movement perception; nothing states that a plain sighting must NOT refresh it, and the rendered phrase 'last seen in ROOM at tick T' has no other honest reading.

EXTRA CORROBORATION I FOUND: tests/agents/test_memory_rendering.py:1169-1176 (`test_last_seen_suffix_renders_for_confirmed_dead_player`) appends a `saw_player` row and then HAND-CALLS `memory.working.record_sighting(player_id="p-2", room="MEDBAY", tick=10)` -- the test simulates exactly the wiring production does not have, which is why no test catches the gap. tasks/phase-3.md:690/803-813 shows that pin was authored on the assumption a saw_player row feeds last_seen.

NOT A RE-REPORT of any listed known-open item.
```

**Verifier note.** Confirmed. The one numeric drift is in the finder's secondary figure: I measure 2703 stale rows (34.4%) against their 2533 (32.2%); the title's 19% figure and the 7863 denominator both reproduce to the digit. Targeted run `uv run pytest tests/agents/test_memory_rendering.py -k 'last_seen or MovementPerception'` -> 12 passed, i.e. the existing suite is green with the defect present.

**Fix sketch.** Replace the `working.last_seen` read in `_build_belief_lines` (store.py:2126) with the already-correct `agents/tactical/features.py::_episodic_last_seen` derivation (or extend `_record_movement_sightings` to fold `EVENT_SAW_PLAYER` rows using the same `_sighting_is_suppressed` firewall it already applies), and add an evidence-honesty instrument that asserts every rendered `last seen in R at tick T` is the argmax-tick sighting in the agent's own episodic log. NOTE FOR THE RE-GROUND: this changes rendered prompt bytes, so under the freeze-during-measurement rule it is a re-record change, not a re-fit change — the decision (fix now and re-record, or freeze the defect for baseline 7 and route the fix to the next record) belongs in the phase contract, not in the fit.

## B-9 — The referee's "first-hand structured sighting" vocabulary still excludes saw_move, so 29% of spoken placements never back an accusation

**Severity:** P1. **Classification:** defect. **Verdict:** ADJUSTED. **Area:** eval-instruments / watchability + vote_correctness + the conviction fit. **Confidence:** high.
**Merged from:** finder-eval-instruments.json#1.

**Claim.** Task 20.43 taught eval/evidence_honesty.py to read a SawMoveObservation as a placement, but every LIVE first-hand-sighting predicate outside that module still isinstance-checks a vocabulary that omits it -- eval/watchability.py:1357-1361 (`subject_observed`, the LIVE subject-aware bit) and training/conviction/dataset.py:466 check SawPlayerObservation/SawVentObservation, while eval/vote_correctness.py:456-461, eval/funnel.py:779-783 and :1361-1365, and eval/deception_instruments.py:588 and :686 check SawPlayerObservation ALONE. The 1136 saw_move observations in replays/ml_corpus/9p2i (29% of spoken placements) are therefore invisible to the observation-backed predicate that drives D2 conversion, the testimony_backed_conversion Layer-1 floor and the conviction label. EXCLUDED from the claim: `has_observation` / `observation_backed_any` in the same function (eval/watchability.py:1353-1356), which is a DECLARED FROZEN 15.2-era subject-agnostic parity bit -- widening it is a regression, not a fix.

**As originally filed.** Task 20.43 taught eval/evidence_honesty.py to read a SawMoveObservation as a placement, but every other instrument (and the conviction model's own label mirror) still isinstance-checks SawPlayerObservation/SawVentObservation only, so the 1136 saw_move observations in replays/ml_corpus/9p2i (29% of all spoken placements) are invisible to the observation-backed predicate that drives D2 conversion, the testimony_backed_conversion Layer-1 floor, and the conviction label.

**Finder evidence.**

```
Channel census over the committed bytes (python over replays/**/*.jsonl, transcript turn.observations types): ml_corpus/9p2i saw_player 2722, saw_move 1136, saw_vent 363; samples/9p2i saw_player 914, saw_move 468. The fixed site: eval/evidence_honesty.py:2181-2209 `_sighting_placement` — "a ``saw_move`` ... places the subject at the DESTINATION, ``to_room`` at ``tick``" — with `if isinstance(artifact, SawMoveObservation): return SawPlayerObservation(...)` at :2202-2208. The unfixed sites, all `isinstance(obs, (SawPlayerObservation, ...))` with no SawMoveObservation arm: eval/watchability.py:1354-1359 (`has_observation` / `subject_observed` inside `_testimony_vehicle`), eval/vote_correctness.py:452-461 (`_has_kill_witness_chain`), eval/funnel.py:777-783 (`_killer_placed_at_scene`) and :1361-1365 (`_spoken_vouches`), eval/deception_instruments.py:588 and :686, training/conviction/dataset.py:466 (`_observation_backed_impostor_subjects`, which the docstring at :434-437 declares a mirror of watchability). `grep -rn "SawMoveObservation" --include="*.py" eval/ training/ scripts/` returns hits only in eval/evidence_honesty.py and scripts/gen_frontend_types.py. Measured delta (script: scratchpad/wave0/B, mirror of `_observation_backed_impostor_subjects` with and without a SawMoveObservation arm, over the recorded meeting rows + re-seeded roles): ml_corpus/9p2i backed_attempted 336 -> 373, converted 239 -> 249 (testimony_backed_conversion 0.7113 -> 0.6676); samples/9p2i 115 -> 132 attempted, 80 -> 84 converted (0.6957 -> 0.6364 — and 0.6956521739130435/numerator 80 is exactly the pinned baseline-7 9p2i floor at eval/watchability.py:_BASELINE_SUPPLY_FLOORS); 229 accusation turns in ml_corpus/9p2i carry a first-hand structured sighting of the accused via saw_move ONLY. Same mirror for vote-correctness: my independent recount reproduces the four documented rates exactly (78/85=0.9176, 19/20=0.9500, 229/254=0.9016, 26/28=0.9286, eval/vote_correctness.py:39-42) and admitting a saw_move placement at (to_room, tick) moves them to 0.9294 / 1.0000 / 0.9173 / 0.9286.
```

**Verifier evidence (independent re-run).**

```
ALL SITES REPRODUCE AT HEAD. `grep -rn "SawMoveObservation" --include="*.py" eval/ training/ scripts/` (my own run) -> eval/evidence_honesty.py:198,2202,2236 and scripts/gen_frontend_types.py:147 ONLY -- exactly as claimed. The fixed resolver is eval/evidence_honesty.py:2181-2209 (`_sighting_placement`, `if isinstance(artifact, SawMoveObservation): return SawPlayerObservation(... room=artifact.to_room ...)`).

MY OWN CENSUS (json walk, transcript turn observations by discriminator) reproduces exactly: ml_corpus/9p2i saw_player 2722, saw_move 1136, saw_vent 363; samples/9p2i saw_player 914, saw_move 468. (1136/(2722+1136) = 29.4%, so '29% of all spoken placements' reads placements as saw_player+saw_move.)

MY OWN DELTA MEASUREMENT (scratchpad/wave0/B/v1/b9_delta.py -- independently re-implemented mirror of `_observation_backed_impostor_subjects` with and without a SawMoveObservation arm, roles from `training.conviction.dataset._roles_for_seed`, entries from `orchestrator.replay.read_all_entries`) reproduces the finder's numbers TO THE DIGIT:
```
replays/ml_corpus/9p2i: attempted 336 -> 373, converted 239 -> 249, rate 0.7113095238095238 -> 0.6675603217158177
   accusation turns backed via saw_move ONLY: 229
replays/samples/9p2i: attempted 115 -> 132, converted 80 -> 84, rate 0.6956521739130435 -> 0.6363636363636364
   accusation turns backed via saw_move ONLY: 96
```
And 0.6956521739130435 / numerator 80 IS the pinned baseline-7 9p2i floor: eval/watchability.py:868-873 `testimony_backed_conversion=FloorPin(value=0.6956521739130435, numerator=80)`. My `compute_watchability(Path('replays/samples/9p2i'))` run returns `testimony_backed_conversion measured 0.6956521739130435 floor 0.6956521739130435 passed True`, i.e. the pin passes at exact self-equality today and would fail on a widened vocabulary.

The four documented vote-correctness rates are present as claimed at eval/vote_correctness.py:35-38 (78/85 = 0.9176, 19/20 = 0.9500, 229/254 = 0.9016, 26/28 = 0.9286) and are gated by scripts/check_doc_facts.py; I did not independently re-derive the four counterfactual rates (0.9294 / 1.0000 / 0.9173 / 0.9286) -- that half of the evidence is UNVERIFIED, though `_has_kill_witness_chain` (eval/vote_correctness.py:451-461) structurally cannot see a saw_move, so the direction is certain.

WHY ADJUSTED -- one cited surface is SPECIFIED. eval/watchability.py:1332-1352 documents `observation_backed_any` (fed by the `has_observation` isinstance tuple `(SawPlayerObservation, FoundBodyObservation)`) as the FROZEN pre-15.19 subject-agnostic bit 'retained ONLY for the 15.2 historical parity pin', and records that widening it to the 15.4 vent type 'silently broke the bit-exact geomean parity ... Task 16.14's re-pin found the drift'. Widening THAT bit for saw_move would re-break the same pin. The LIVE `observation_backed` bit WAS widened for saw_vent at 15.4 -- which is the precedent the finding correctly invokes -- so the omission of saw_move from the live bit is undeclared and is the real defect.

20.43 IS NOT A DECLARED CARRY FOR THE OTHER SITES: tasks/phase-20.md:6991-7024 scopes it to eval/evidence_honesty.py + its tests + the §11 erratum, files-NOT-in-scope names meetings/, scripts/measure_baseline.py and scripts/counterfactual_phase20.py; nothing there declares the other instruments' vocabulary as a deliberate carry. The one thing 20.43 DID route post-record is the production-side duplicate alibi_vs_sighting mint, which is on the known-open list and is a DIFFERENT object from this finding.
```

**Verifier note.** Core observation and every primary number verified exactly. Two scope corrections: (1) the fix must NOT touch `has_observation` / `observation_backed_any` -- that isinstance tuple is a declared frozen historical parity bit (eval/watchability.py:1338-1352, re-pinned by 16.14) and widening it is the regression that pin exists to prevent; the finding's fix_sketch ('route watchability._testimony_vehicle ... through it') is too coarse as written. (2) The claim's 'isinstance-checks SawPlayerObservation/SawVentObservation only' is accurate for watchability's live bit and the conviction mirror, but eval/funnel.py:779-783, :1361-1365 and eval/deception_instruments.py:588, :686 check SawPlayerObservation ALONE -- narrower than stated, which strengthens rather than weakens the point. Severity P1 stands (the fix moves a pinned floor and the conviction label, so it must precede the re-fit).

**Fix sketch.** Lift eval/evidence_honesty.py:_sighting_placement into a shared helper (meetings/transcript.py already owns the same normalisation for the detector via `_iter_move_placements`) and route watchability._testimony_vehicle, vote_correctness._has_kill_witness_chain, funnel's two sites, deception_instruments' two sites and training/conviction/dataset._observation_backed_impostor_subjects through it. Because this moves the baseline-7 floor pins and the conviction label, do it BEFORE the re-ground re-fits and re-pins, not after — otherwise the new arms are fitted against the old vocabulary and the fix becomes a second, un-attributable re-pin.

## B-10 — The baseline-7 flags_per_meeting floor the re-ground will adopt is 69% persisted vent sightings, and the module's own docstring says that component is zero

**Severity:** P2 (finder: P1). **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** eval-instruments / watchability supply floors. **Confidence:** high.
**Merged from:** finder-eval-instruments.json#3.

**Claim.** `_supply_gauge_values`'s docstring (eval/watchability.py:2062) asserts the merged persisted-vent component is 'Zero on the committed v4 sets (no vent turns)', which is FALSE on the committed baseline-7 bytes: it is 92 of the 134 flags behind the pinned samples/9p2i floor (68.7%) and 308 of 431 on the fit corpus (71.5%), leaving the re-derived transcript-flag component at only 0.276 flags/meeting. The defect is (a) that one stale docstring sentence and (b) that `flags_per_meeting` is a single un-split gauge, so a candidate could clear the evidence floor by minting vent sightings while its deduction-flag supply collapses. NOT part of the claim: that the floor's composition is undisclosed -- every baseline block states its own split in the pin comment (eval/watchability.py:850-852 for baseline-7 9p2i: '92 persisted vent flags + 42 re-derived transcript flags'; :787-789 for baseline-6: '96 ... + 84 ...'), and audits/audit-phase-20-baseline-7.md §8's gauge table publishes the same split.

**As originally filed.** `_supply_gauge_values`'s docstring asserts the merged persisted-vent component is "Zero on the committed v4 sets (no vent turns)", but it measures 92 of the 134 flags behind the pinned baseline-7 9p2i floor (68.7%) and 308 of 431 on the fit corpus, so the evidence floor BAKEOFF_BASELINE_ID is about to move onto is dominated by vent sightings while its re-derived transcript-flag component is only 0.276 flags/meeting.

**Finder evidence.**

```
The claim: eval/watchability.py:2057-2065 — "...so the persisted vent flags are MERGED in ... Zero on the committed v4 sets (no vent turns), so the pinned baseline-2 floors are unchanged...". Contradicted inside the same module at eval/watchability.py:890-892 — "The small 4p1i games carry no re-derived transcript flag at all, so every flag here is a persisted vent sighting." Measured (`assemble_tournament_report` + `compute_supply_gauges` + `_persisted_vent_flag_count`): samples/9p2i rederived_total_flags=42 persisted_vent=92 merged=134 over 152 meetings (0.881578947368421); ml_corpus/9p2i 123 + 308 = 431 over 432 (0.9977); ml_corpus/4p1i 1 + 28 = 29 over 44. Recorded vent_sighting flags per set (json census over the meeting rows): ml_corpus/9p2i 308, samples/9p2i 92, ml_corpus/4p1i 28, samples/4p1i 20. `compute_watchability(Path('replays/samples/9p2i'))` returns `SupplyFloorGauge(name='flags_per_meeting', measured=0.881578947368421, floor=0.881578947368421, passed=True)` — i.e. the pin IS this 69%-vent number, and `_BASELINE_SUPPLY_FLOORS['baseline-7']['9p2i']` carries `FloorPin(value=0.881578947368421, numerator=134)` (eval/watchability.py:538ff). Today's selection floor is baseline-6's 1.0909 (training/bakeoff/harness.py:181 `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"`), so the re-ground both lowers the floor 19% and re-bases it on a mostly-vent census.
```

**Verifier evidence (independent re-run).**

```
THE STALE DOCSTRING REPRODUCES VERBATIM at eval/watchability.py:2062 (inside `_supply_gauge_values`, def at :2050): '... else a vent-rich baseline-3 candidate's strongest evidence would be undercounted as evidence-starved. Zero on the committed v4 sets (no vent turns), so the pinned baseline-2 floors are unchanged ...'. The in-module contradiction reproduces at eval/watchability.py:891-892: 'The small 4p1i games carry no re-derived transcript flag at all, so every flag here is a persisted vent sighting.'

MY OWN MEASUREMENT through the real instruments (`compute_watchability` + `assemble_tournament_report` + `compute_supply_gauges` + `_persisted_vent_flag_count`, `PYTHONPATH=. uv run python`) reproduces every figure EXACTLY:
```
=== replays/samples/9p2i  baseline_id baseline-7  supply_floors_passed True
    flags_per_meeting measured 0.881578947368421 floor 0.881578947368421 passed True
    testimony_backed_conversion measured 0.6956521739130435 floor 0.6956521739130435 passed True
    rederived total_flags 42 meetings 152 persisted_vent 92 merged 134 -> 0.881578947368421
=== replays/ml_corpus/9p2i   rederived 123 meetings 432 persisted_vent 308 merged 431 -> 0.9976851851851852
=== replays/ml_corpus/4p1i   rederived   1 meetings  44 persisted_vent  28 merged  29 -> 0.6590909090909091
=== replays/samples/4p1i     rederived   0 meetings  40 persisted_vent  20 merged  20 -> 0.5
```
92/134 = 68.7%; 308/431 = 71.5%; 42/152 = 0.2763 flags/meeting.
Recorded vent_sighting flags per set (my own json census of the meeting rows' `contradictions`): ml_corpus/9p2i 308, samples/9p2i 92, ml_corpus/4p1i 28, samples/4p1i 20 -- all four exact.
The pin reproduces: eval/watchability.py:866-874 `flags_per_meeting=FloorPin(value=0.881578947368421, numerator=134)`. `_DEFAULT_BASELINE_ID` is 'baseline-7' (:917). `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"` at training/bakeoff/harness.py:181, whose floor is `FloorPin(value=1.0909090909090908, numerator=180)` (:808) -- 0.8816/1.0909 = 0.808, so the 19% drop reproduces.

WHY ADJUSTED. (1) The composition is NOT unstated. Every baseline block in `_BASELINE_SUPPLY_FLOORS` publishes its own vent/transcript split in the pin comment -- baseline-7 9p2i at :850-852 ('92 persisted vent flags + 42 re-derived transcript flags'), baseline-7 4p1i at :882-883, baseline-6 9p2i at :787-789 ('96 ... + 84 ...') -- and audits/audit-phase-20-baseline-7.md:628 publishes the same cell in the record audit's §8 table. The Goodhart-surface framing in the fix_sketch ('a floor whose composition is unstated') is therefore wrong; what is wrong is one stale sentence in a helper docstring.
(2) Severity. Nothing is currently selected against the vent-dominated floor: `BAKEOFF_BASELINE_ID` has NOT moved (still 'baseline-6'), and audits/audit-phase-20-baseline-7.md §8 explicitly records that the training-side selection constants 'deliberately lag' and that the ML re-ground is a future owner decision. The remaining content is one false docstring sentence plus a forward design decision for the re-ground contract -- P2 quality-debt, not P1.
(3) The stale sentence's own scope is narrower than the finding reads it: its conclusion is 'so the pinned BASELINE-2 floors are unchanged', i.e. it was a scoped historical statement about the baseline-2-era `qwen3_32b.v4` sets, now read as a general claim. It still needs correcting -- it is plainly false as written today -- but it never was a claim about the baseline-7 census.

NOT A RE-REPORT of any listed known-open item; and the audit-declared §10.3 carry covers the contradiction re-derivations, not this gauge's composition.
```

**Verifier note.** Both halves of the title reproduce exactly (69% vent share; the docstring does say zero). Adjusted on severity P1 -> P2 and on the 'composition unstated' framing, which the pin comments at eval/watchability.py:850-852 / :787-789 and audits/audit-phase-20-baseline-7.md:628 refute. The surviving actionable items -- correct the docstring, and split `flags_per_meeting` into its two components with a floor on each before BAKEOFF_BASELINE_ID moves -- are both worth doing and both belong in the re-ground contract, which is where the finding already routes them.

**Fix sketch.** Correct the stale docstring, and split the gauge into its two measured components (re-derived transcript flags vs persisted vent flags) with a floor on each, so a candidate cannot clear the evidence floor by minting vent sightings while its deduction-flag supply collapses. Decide this at the same moment BAKEOFF_BASELINE_ID moves — a floor whose composition is unstated is the classic Goodhart surface, and this one is about to become the selection floor.

## B-11 — The surrogate GO bar is already saturated on two axes and structurally blocked on the third — a re-fit-and-re-pin re-ground reproduces NO-GO

**Severity:** P2 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/surrogate (fidelity harness, GO/NO-GO bar). **Confidence:** high.
**Merged from:** finder-training-path.json#1.

**Claim.** On the baseline-7 corpus a genuine held-out RE-FIT of the ballot surrogate scores top-1 EXACTLY at the measured honest ceiling (0.8000 == 0.8000, 44/55) and beats the FO-6 re-baseline (0.4182), while axis 3 (SKIP-vs-eject 0.3908 vs always-eject 0.6322) fails because the decision channel is the real tally over predicted per-voter ballots and the predictor casts SKIP on 85 of 87 meetings — a channel the routed re-ground scope (audits/audit-phase-20-baseline-7.md §10.2: re-fit, re-stamp fingerprints, move BAKEOFF_BASELINE_ID, re-publish docs) does not touch. The NO-GO is therefore already MEASURED on the re-ground's own target corpus, not merely forecast. TWO CORRECTIONS TO THE FILED CLAIM: (1) the evidence's 'frozen weights' label is wrong — run_surrogate_fidelity calls model.fit(train_views) on every fold (fidelity.py:726) and BallotSurrogateModel.fit REPLACES any pre-installed predictor (ballots.py:833-834), so the numbers are a live re-fit; the committed artifact's fit-corpus fingerprint is itself declared STALE by §10.2. (2) 'axis 1 can no longer discriminate' is overstated: the bar is 0.75 x ceiling = 0.6000 and the surrogate sits at 0.8000, so a weaker candidate still fails the axis; what is saturated is the surrogate's HEADROOM, not the axis's discriminative power.

**As originally filed.** On the live baseline-7 corpus the frozen ballot surrogate already scores top-1 EXACTLY at the measured honest ceiling (0.8000 == 0.8000) and beats the FO-6 floor, while the only failing axis (SKIP-vs-eject > always-eject) fails for a structural reason the scoped re-ground does not touch — so re-fitting on the new corpus will re-produce NO-GO / diagnostic-only unless the contract changes the decision channel itself.

**Finder evidence.**

```
Command:
  uv run python - <<'EOF'
  from pathlib import Path
  from training.surrogate.dataset import build_meeting_table
  from training.surrogate.fidelity import run_surrogate_fidelity, fo6_rebaseline, decide_go_no_go
  from training.surrogate.ballots import BallotSurrogateModel, load_ballot_predictor_artifact
  tbl = build_meeting_table(Path('replays/ml_corpus/9p2i'))
  pred, sha = load_ballot_predictor_artifact(Path('training/artifacts/surrogate'))
  s = run_surrogate_fidelity(tbl, lambda: BallotSurrogateModel(tbl, predictor=pred), model_name='frozen')
  print(decide_go_no_go(s, fo6_rebaseline(tbl)).model_dump_json(indent=1))
  EOF
Output (verbatim, live corpus, frozen weights):
  SURROGATE (frozen weights, live corpus): top1=0.8000 dec=0.3908 always_eject=0.6322 degen_skip=True pred_ej=2 pred_skip=85 ceiling=0.8000
  "surrogate_top1": 0.8,  "ceiling_top1": 0.8,  "top1_bar": 0.6000000000000001, "meets_ceiling_bar": true,
  "baseline_top1": 0.41818181818181815, "beats_prior_baseline": true,
  "surrogate_skip_vs_eject_accuracy": 0.39080459770114945, "always_eject_baseline": 0.632183908045977,
  "beats_always_eject": false, "verdict": "NO-GO", "surrogate_role": "diagnostic-only"
The decision channel is not a tunable head: training/surrogate/ballots.py:737-760 states the decision is only ever the REAL tally's output over predicted per-voter ballots, and the predictor casts SKIP on nearly every ballot (pred_ej=2 of 87 meetings here). The three-axis bar is at training/surrogate/fidelity.py:894-941 (decide_go_no_go at :942). The committed record shows the same shape on the previous corpus: training/reports/report-ballot-surrogate.md:316-318 (axis 1 PASS, axis 2 PASS, axis 3 FAIL 0.3750 vs 0.6250).
```

**Verifier evidence (independent re-run).**

```
Re-ran the filed command verbatim (PYTHONPATH=. uv run python, build_meeting_table('replays/ml_corpus/9p2i') + load_ballot_predictor_artifact + run_surrogate_fidelity + fo6_rebaseline + decide_go_no_go). Output reproduces the filed block EXACTLY: top1=0.8000 dec=0.3908 always_eject=0.6322 pred_ej=2 pred_skip=85 meetings_scored=87 ejection_meetings=55; verdict JSON {surrogate_top1 0.8, ceiling_top1 0.8, top1_bar 0.6000000000000001, meets_ceiling_bar true, baseline_top1 0.41818181818181815, beats_prior_baseline true, surrogate_skip_vs_eject_accuracy 0.39080459770114945, always_eject_baseline 0.632183908045977, beats_always_eject false, verdict NO-GO, surrogate_role diagnostic-only}. honest_ceiling dump: {ejections_total 55, flag_present 45, proximity_present 48, belief_lead 43, reachable 44, max_achievable_top1 0.8, voice_driven_share 0.2}. INDEPENDENT CONTROL (mine, not the finder's): re-ran with model_factory=lambda: BallotSurrogateModel(tbl) i.e. NO pre-installed predictor -> top1 0.8, dec 0.39080459770114945, predej 2, predskip 85 — byte-identical to the 'frozen' run, proving the harness refits and the 'frozen weights' label is inoperative. _game_folds returns 1 fold (committed splits.json, test block 30 games of 150). replays/ml_corpus/9p2i/MANIFEST.md:163 confirms the set is the baseline-7 re-record (Task 20.36). Bar code read at training/surrogate/fidelity.py:946-1020 (decide_go_no_go); decision channel at training/surrogate/ballots.py:756-761 + 859-866 ('the DECISION is the real tally on the predicted ballots ... Never re-implemented, never a tuned threshold').
```

**Verifier note.** SPECIFIED, not a defect. NO-GO is a PRE-REGISTERED outcome with a pre-committed consequence mapping: training/reports/report-ballot-surrogate.md §1 ('NO-GO => fallback (a)'), §5 ('the bake-off is not blocked in either direction — a NO-GO keeps the default fake-provider runner, it re-plans nothing downstream'), §6 (the ladder). The same report's §5 'Honest diagnosis' already states the exact failure mechanism the finding names ('What fails is the decision channel ... its 37.5% decision accuracy is exactly the trivial always-SKIP constant ... the ratified bar named always-eject as axis 3's constant and warned it was the STRONGER trivial constant'). The ML re-ground is an explicitly ROUTED follow-up (audits/audit-phase-20-baseline-7.md §10.2), not a silent debt. NOT a re-report of any named known-open id (C-46/C-83/C-126/C-130/F1-F5/replay_walk/1440x900/duplicate alibi_vs_sighting/C-79/C-80/C-101/C-107/C-62/C-33/C-45). Severity lowered P1 -> P2: nothing is gated, nothing is blocked, and the fallback is already the shipped state. RESIDUAL VALUE, and it is real: the axis-1 saturation datum (top-1 == ceiling exactly, first time on any record — the report's baseline-6 pair was 0.7667 vs 0.8500) is new and undeclared, and the recommendation to pre-register an axis-3 disposition BEFORE the re-fit is sound contract-shaping advice given the re-fit's verdict is now known in advance.

**Fix sketch.** The re-ground contract must state, BEFORE the re-fit, what changes about axis 3 — otherwise it is a bookkeeping exercise with a pre-known verdict. Concretely, pick one and pre-register it: (a) fit the SKIP alternative against the tally's realized decision rather than per-ballot targets (train the decision the bar measures); (b) calibrate the predicted ballot confidences so the DEFAULT_SKIP_CONFIDENCE_THRESHOLD gate is reachable (today the predicted confidences never clear 0.60 in plurality); or (c) formally retire axis 3 as a GO axis and re-register the surrogate as a RANKING instrument with a decision-channel diagnostic. Also note top-1 has hit the ceiling exactly — axis 1 can no longer discriminate, so the re-ground should replace `>= 0.75 x ceiling` with a margin-below-ceiling or a per-channel decomposition.

## B-12 — The FO-6 comparator's decision head is tuned by an objective whose plateau value IS the fit-side SKIP count — it tracks meeting mix, not physics

**Severity:** P3 (finder: P1). **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** training-path / training/surrogate/fidelity.py (Fo6Logistic comparator). **Confidence:** high.
**Merged from:** finder-training-path.json#2.

**Claim.** MECHANISM CONFIRMED VERBATIM: Fo6Logistic._tune_threshold (training/surrogate/fidelity.py:390-402) maximises EXACT-TARGET accuracy over all meetings including SKIP meetings, where meeting.ejected is None and _decide returns None above the leader's probability — so for the whole upper half of the tau grid the score is exactly the fit-side SKIP count (120 of 345), the winning tau=0.20 beats that trivial always-SKIP constant by 7 meetings (2.0%), and the strict `correct > best_acc` scan ascending breaks ties toward the LOWER tau (0.20 and 0.25 both score 127). IMPACT CLAIM REFUTED AND REPLACED: the finding asserts 'the comparator's headline moves with it' and 'Axis 2 of the surrogate GO bar is a strict `>` against this number'. Both are non-sequiturs. run_surrogate_fidelity computes top1_hits from prediction.ranking[0] (fidelity.py:748), and Fo6Logistic.predict builds ranking by probability sort with tau touching only `ejected` (fidelity.py:415-421) — so FO-6's top-1 is threshold-INDEPENDENT and the tuned head cannot move it; the 64%->26%->22%->65%->41.8% sequence tracks the CORPUS/population change, not tau. And decide_go_no_go reads prior_baseline.TOP1 for axis 2 and the SURROGATE's own skip_vs_eject_accuracy vs the population's always_eject_baseline for axis 3 — FO-6's tuned decision head enters NO axis of the bar at all. The finding's own fix sketch concedes threshold-independence ('its top-1/top-2 are threshold-independent'), contradicting its claim paragraph. What survives: a PUBLISHED comparator DIAGNOSTIC (the FO-6 decision census: dec_acc 0.4138, predicted_skips 75, predicted_ejections 12, degenerates_to_skip True) is produced by a head tuned on a degenerate objective with a 7-of-345 margin — a reporting-quality defect with zero gate exposure.

**As originally filed.** Fo6Logistic._tune_threshold maximises exact-target accuracy over ALL meetings including SKIP meetings, so for the entire upper half of its tau grid the score is exactly the fit-side SKIP count, and the winning tau beats that trivial always-SKIP constant by 7 meetings out of 345 (2.0%) — which is why the comparator's verdict flips SKIP / all-EJECT / SKIP across records.

**Finder evidence.**

```
Code: training/surrogate/fidelity.py:390-403
  def _tune_threshold(self, meetings): best_tau, best_acc = 0.5, -1.0
      for step in range(1, 20): tau = step / 20.0
          correct = sum over meetings of (self._decide(meeting, probs, tau) == meeting.ejected)
(`meeting.ejected` is None on a SKIP meeting, so every SKIP meeting is a free point for a high tau; `_decide` at :405-411 returns None when the leader's prob < tau.)
Reproduced on the live corpus:
  uv run python - <<'EOF'
  from training.surrogate.fidelity import build_meeting_views, Fo6Logistic, _game_folds, fo6_rebaseline
  ... m = Fo6Logistic(); m.fit(train_views); print('tuned tau =', m._tau)
  for step in range(1,20): tau=step/20; correct=sum(1 for v in train_views if m._decide(v, m._prob(v), tau)==v.ejected)
  EOF
Output (verbatim):
  tuned tau = 0.2
  fit-side meetings=345  skip=120  eject=225
  tau -> fit-side exact-target correct (out of 345):
    0.05:81  0.10:86  0.15:105  0.20:127  0.25:127  0.30:121  0.35:118  0.40:120  0.45:120  0.50:120
    0.55:120  0.60:120  0.65:120  0.70:120  0.75:120  0.80:120  0.85:120  0.90:120  0.95:120
The flat 120 across tau in [0.40, 0.95] is EXACTLY the fit-side SKIP count (120) — a pure always-SKIP head. The chosen tau=0.20 scores 127, i.e. 7 meetings (2.0%) above the trivial constant, and ties are broken toward the LOWEST tau (`correct > best_acc`, strict, scanning tau ascending), i.e. toward the all-EJECT end. Move the SKIP/eject mix a few meetings and the argmax jumps between the two poles.
The comparator's headline moves with it: FO-6 top-1 across records is 64% -> 26% -> 22% -> 65% (training/reports/report-ballot-surrogate.md:60) and NOW 41.8% on the live corpus (`fo6_rebaseline` output: `top1=0.4182 (23/55) dec_acc=0.4138 always_eject=0.6322 predicted_skips=75 predicted_ejections=12 degenerates_to_skip=True`). Axis 2 of the surrogate GO bar (training/surrogate/fidelity.py:930-941) is a strict `>` against this number.
```

**Verifier evidence (independent re-run).**

```
Re-ran the filed probe independently (PYTHONPATH=. uv run python; build_meeting_views + _game_folds(folds=5) -> the single committed-split fold; Fo6Logistic().fit(train_views)). Output reproduces the filed block EXACTLY, digit for digit: 'tuned tau = 0.2'; 'fit-side meetings=345 skip=120 eject=225'; tau curve 0.05:81 0.10:86 0.15:105 0.20:127 0.25:127 0.30:121 0.35:118 0.40:120 0.45:120 0.50:120 0.55:120 0.60:120 0.65:120 0.70:120 0.75:120 0.80:120 0.85:120 0.90:120 0.95:120 — the flat 120 across [0.40,0.95] IS the fit-side SKIP count. fo6_rebaseline: top1=0.4182 (23/55) dec_acc=0.4138 always_eject=0.6322 pred_skips=75 pred_ej=12 degen=True. MY OWN REFUTATION EVIDENCE (not in the filing): read fidelity.py:748 `if prediction.ranking and prediction.ranking[0] == true_eject: top1_hits += 1` and fidelity.py:415-421 `ranking = tuple(sorted(meeting.candidates, key=lambda cand: (-probs[cand], cand))); ejected = self._decide(meeting, probs, self._tau)` — top-1 is computed off `ranking`, which never sees tau. Read decide_go_no_go (fidelity.py:992-996): `meets_ceiling_bar = surrogate.top1 >= top1_bar; beats_prior_baseline = surrogate.top1 > prior_baseline.top1; beats_always_eject = surrogate.skip_vs_eject_accuracy > surrogate.always_eject_baseline` — no field of prior_baseline other than top1 (and the population-identity fields) is read. Report line confirmed at training/reports/report-ballot-surrogate.md §1 (the 64% -> 26% -> 22% -> 65% sequence, attributed there to POPULATION change, not to the head).
```

**Verifier note.** RE-REPORT of an already-DECLARED and dispositioned item — not one of the named known-open ids, but committed prose: audits/audit-phase-20-baseline-7.md §10.2 states verbatim 'the FO-6 comparator head has now flipped three records running (SKIP -> all-EJECT -> SKIP), which says it tracks the meeting mix rather than the physics and should not be read as a physical baseline', and lists it as one of 'two things ... worth carrying into the re-ground'. The finding's genuinely new contribution is the MECHANISM (the plateau equals the fit-side SKIP count; the 7/345 margin; the lower-tau tie-break) behind that already-published conclusion — worth keeping as evidence, not as a new finding. Severity dropped P1 -> P3 because the corrected blast radius is one published diagnostic number, not any gate, floor, or verdict axis. Classification moved defect -> quality-debt for the same reason.

**Fix sketch.** Do not carry FO-6's tuned DECISION head into the re-ground at all — it is a mix estimator wearing a physics comparator's clothes. Keep FO-6 only as a RANKING floor (its top-1/top-2 are threshold-independent: `predict` ranks by probability, tau touches only `ejected`), and replace the decision comparator with the two constants the report already computes on the same population — `always_eject_baseline` and its complement (always-SKIP = skip_meetings/meetings_scored). Then the axis-2 floor is a stated pair of trivial constants that move transparently with the mix instead of a tuned head that flips. If a tuned FO-6 head must stay, tune tau on the BINARY skip/eject decision (the quantity the report scores) with a documented tie-break toward the higher tau, and report the tau curve beside the number so a 7-of-345 margin is visible.

## B-13 — The crew inner fitness can rank a LOSS above a WIN: unnormalised task-count shaping dwarfs the terminal term

**Severity:** P2 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/rewards.py + training/crew/scorer.py (objective shape). **Confidence:** high.
**Merged from:** finder-training-path.json#4.

**Claim.** CORE CONFIRMED AND SHARPENED: crew_inner_episode_fitness (training/crew/scorer.py:998) calls compute_shaped_reward(rollout,'CREWMATE').total() with no weights, so terminal(+/-1) + sum(dense) + shaping are summed at 1/1/1, and the gamma=1 shaping sum is the raw unnormalised completed-task COUNT. The pinned real-engine literals (tests/training/test_rewards.py:478-491) give a crew LOSS scoring 12.829131652661065, of which the shaping is 12.0 (93.5%). The rigorous ordering bound (mine, tighter than the filing's illustrative 7.1): a crew WIN with k of 14 tasks scores at most 1.0 + [k/14 + 1.0 + correct_reports + 1.0] + k with correct_reports <= num_impostors = 2, i.e. <= 5 + k + k/14 — so EVERY crew WIN with k <= 7 completed tasks scores strictly below that recorded LOSS (k=7 -> 12.500 < 12.829). The objective is therefore not a win proxy. THREE CORRECTIONS. (1) The doc sub-claim 'the public description does not disclose this' is REFUTED: docs/ml-program.md:32-39 explicitly says the shaping is 'not policy-invariant, as that module now says ... Telescoping is not invariance — it is a real +1-per-kill incentive that can change the optimal policy, a correction the campaign report carries as errata'; the filing cites :61-62 and :194 while the disclosure sits 27 lines earlier in the same file. (2) 'no seam' is wrong at module level: compute_shaped_reward already accepts dense_weight/shaping_weight/terminal_weight (training/rewards.py:301-306) and ShapedReward carries them as fields — the missing seam is only that crew_inner_episode_fitness / inner_episode_fitness do not FORWARD them. (3) The underlying mechanism is a DECLARED, dated, dispositioned carry, so only the win/loss ORDERING consequence is new.

**As originally filed.** `crew_inner_episode_fitness` sums a raw integer task COUNT (the gamma=1 shaping) with a +-1 terminal win, so a losing crew episode that completed 12 tasks scores 12.83 while a winning episode that ejected both impostors early with few tasks scores well under that — the optimizer is paid to task, not to deduce.

**Finder evidence.**

```
Composition: training/rewards.py:203-210
  def total(self): dense = sum(self.dense_terms.values()); return terminal_weight*terminal_reward + dense_weight*dense + shaping_weight*shaping_sum
Weights are never plumbed: training/crew/scorer.py:998 `shaped = compute_shaped_reward(rollout, "CREWMATE").total()` (defaults dense_weight=shaping_weight=terminal_weight=1.0, training/rewards.py:302-306). Phi is the CUMULATIVE completed-task count (training/rewards.py:116-118), so shaping_sum == terminal task count.
Pinned real-engine numbers, tests/training/test_rewards.py:478-491 (seed 0, exact `==` literals):
  crew.terminal_reward == -1.0        # the crew LOST
  crew.dense_terms == {task_progress: 0.857..., survival: 0.2857..., correct_reports: 0.0, patrol_coverage: 0.686...}
  crew.shaping_sum == 12.0            # 12 completed tasks, unnormalised
  crew.total() == 12.829131652661065
So a LOSS scores +12.83. The dense terms are all normalised to [0,1] except `correct_reports`; the only unbounded term is the raw task count, at 93.5% of the total. An early double-ejection win with 2 tasks done scores at most 1.0 + (0.14 + 1.0 + 2.0 + 1.0) + 2.0 = ~7.1 < 12.83. Note `task_progress` (0.857) already measures task completion at weight 1 — the shaping re-pays the same quantity 14x larger and unnormalised.
The public description does not disclose this: docs/ml-program.md:61-62 says only "tactically-reachable impostor terms plus the shaping, minus a cross-entropy anchor", and :194 cites Ng, Harada & Russell (1999) as "the shaping analysis" while training/rewards.py:26-45 records that the Ng-1999 invariance hypothesis is NOT satisfied here.
```

**Verifier evidence (independent re-run).**

```
Read training/rewards.py:196-210 (ShapedReward.total = terminal_weight*terminal + dense_weight*sum(dense) + shaping_weight*shaping_sum, defaults 1.0/1.0/1.0), :100-118 (_side_potential returns frame.tasks_completed for CREWMATE), :244-276 (_crew_terms: task_progress = tasks_completed/tasks_total in [0,1], survival in [0,1], correct_reports = a raw COUNT bounded by the number of crew-report meetings that ejected an impostor <= num_impostors, patrol_coverage in [0,1]), :301-306 (compute_shaped_reward DOES expose the three weights). Read training/crew/scorer.py:961-1003 — `shaped = compute_shaped_reward(rollout, 'CREWMATE').total()`, no weight arguments. Read tests/training/test_rewards.py:478-491 and confirmed the exact `==` literals: terminal -1.0; dense {task_progress 0.8571428571428571, survival 0.2857142857142857, correct_reports 0.0, patrol_coverage 0.6862745098039216}; shaping_sum 12.0; total 12.829131652661065. Arithmetic check: -1 + 1.8291316526610652 + 12 = 12.829131652661065, and 12/12.829131652661065 = 0.9354 (the filing's 93.5%). tasks_total recovered as 14 from task_progress 12/14, consistent with shaping_sum 12. MY OWN REFUTATION EVIDENCE: sed -n '28,45p' docs/ml-program.md prints the non-invariance disclosure in full at lines 32-39.
```

**Verifier note.** MECHANISM IS A DECLARED DELIBERATE CARRY. training/rewards.py:26-45 records it at length ('The prior claim here ("so it cannot change the optimal policy") was mathematically FALSE ... Finding + disposition: Task 19.4, audits/audit-phase-19-triage.md §7 item 4 (§8 row 2, VERIFIED) — DOCUMENTED, NOT REPAIRED. The ML program is frozen'), and _side_potential:108-113 repeats it. audits/audit-phase-19-triage.md:65 and :148 carry the dispositioned item ('fix the claim, do not retrain'). A related PRIOR finding also exists and is P2: audits/review-2026-08-19/B/collated-findings.md:192 C-127 names 'the live +1/kill, +1/task shaping deserves a warning at _side_potential itself'. NOT a re-report of any named known-open id in the parent's list. WHAT IS GENUINELY NEW AND UNDECLARED: the win/loss ORDERING inversion — nothing in rewards.py, docs/ml-program.md, the triage, or C-127 says a losing episode can outrank a winning one. That is a sharper instance of the already-declared 'it CAN change the optimal policy', which is why I hold it at P2 rather than P1: the ML program is frozen, the crew ES is not currently being optimised, and the re-ground is a routed follow-up (audits/audit-phase-20-baseline-7.md §10.2). It IS correct contract-shaping input for that re-ground, and the fix sketch's items (2) and (3) remain sound; item (1) should be narrowed to 'forward the existing weights through the two fitness functions', and the docs/ml-program.md paragraph of the sketch should be dropped as already-satisfied except for the crew-side (+1-per-task) and magnitude disclosures.

**Fix sketch.** Before any re-optimisation: (1) plumb `dense_weight`/`shaping_weight`/`terminal_weight` through `crew_inner_episode_fitness` and `inner_episode_fitness` so the objective is expressible without editing the function (today it is hard-wired at 1/1/1 with no seam); (2) normalise Phi (tasks_completed / tasks_total) so the shaping is bounded by 1 and stops double-paying `task_progress`; (3) re-scale the terminal term so a win strictly dominates any loss, or state explicitly that the crew objective is a task-throughput proxy and not a win proxy. Whichever is chosen, docs/ml-program.md's fitness paragraph and its Ng-1999 citation must be re-published to match (the re-ground already re-publishes that file).

## B-14 — Impostor fitness pays kills three times and the win term is 1/22 of it — the objective is saturated and cannot discriminate the arms

**Severity:** P2 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/bakeoff/harness.py + training/rewards.py (objective shape). **Confidence:** high.
**Merged from:** finder-training-path.json#5.

**Claim.** NUMBERS CONFIRMED VERBATIM: kill volume enters the impostor fitness twice unconditionally (dense `kills` + the gamma=1 shaping, whose sum is the terminal cumulative kill count) and a THIRD time for each kill with no crew witness (dense `unwitnessed_kills` <= kills — the filing's flat 'three times' is exact only when every kill is unwitnessed, which is the case in the pinned episode). The pinned decomposition (tests/training/test_rewards.py:466-476) is terminal 1.0, dense {kills 5.0, unwitnessed_kills 5.0, survival 1.0, meetings_survived 5.0}, shaping 5.0, total 22.0 — kill-derived 15/22 = 68%, win/loss level 1/22 = 4.5% (a +/-1 swing on a ~22 scale). Three of four recorded arms sit at or near the win-rate ceiling (1.0 / 1.0 / 0.9333) while their fitness spread is 18.198 / 18.671 / 19.066, so that spread cannot be read as 'better at winning' — the substantive and valid core. ONE FACTUAL ERROR TO CORRECT: the filing says the highest-fitness arm 'policy-es ... has the worst FSM agreement' — FALSE. map-elites has fsm_intent_agreement 0.19455 < policy-es's 0.25551; the filing's OWN evidence table prints both numbers (agree=0.256 vs agree=0.195) and contradicts its prose. ONE FIX-SKETCH ITEM ALREADY SATISFIED: 'state that the ceiling is advisory and stop calling it a ceiling' — training/bakeoff/harness.py:187-194 already says in terms that rows above ANCHOR_CE_CEILING are 'FLAGGED (``anchor_ce_flagged``), never dropped (definition of done)'.

**As originally filed.** Kill count enters the impostor fitness three times (dense `kills`, dense `unwitnessed_kills`, and the shaping sum) while the terminal win is +-1, so the recorded bake-off's fitness spread is a kill-volume ranking with the win term already at ceiling for three of four arms — leaving the re-ground no headroom to demonstrate 'better', only 'different'.

**Finder evidence.**

```
training/rewards.py:219-236 (`_impostor_terms` returns kills, unwitnessed_kills, survival, meetings_survived) + :116-117 (Phi = cumulative_kills) + :203-210 (total = terminal + sum(dense) + shaping).
Pinned real-engine decomposition, tests/training/test_rewards.py:466-476 (exact `==`):
  impostor.terminal_reward == 1.0
  impostor.dense_terms == {kills: 5.0, unwitnessed_kills: 5.0, survival: 1.0, meetings_survived: 5.0}
  impostor.shaping_sum == 5.0
  impostor.total() == 22.0
Kill-derived terms are 15 of 22 (68%); the win/loss term is 1 of 22 (4.5%).
Recorded arms (uv run python over training/reports/results-impostor-bakeoff.jsonl):
  bc-dagger   real_fit=5.167  shaped=7.1   win=0.0667  ce=1.959  agree=0.304
  utility-es  real_fit=18.671 shaped=19.67 win=1.0     ce=0.995  agree=0.397
  policy-es   real_fit=19.066 shaped=21.1  win=1.0     ce=2.016  agree=0.256  (anchor_ce_flagged=True)
  map-elites  real_fit=18.198 shaped=20.17 win=0.933   ce=1.974  agree=0.195
Three of four arms are at or near win-rate ceiling, so the fitness differences among them are pure kill volume. Note also that the highest-fitness arm (policy-es, 19.07) is the one that BREACHED the anchor ceiling (2.0157 > ANCHOR_CE_CEILING 2.0, harness.py:197) and has the worst FSM agreement — the anchor penalty at DEFAULT_ANCHOR_PENALTY_WEIGHT=1.0 (harness.py:205) against a ~20-magnitude shaped reward is a ~10% leash, and breaching it only FLAGS, never drops (harness.py:193-197). The fitness itself is hard-wired: training/bakeoff/harness.py:944 `shaped = compute_shaped_reward(rollout, "IMPOSTOR").total()` with no weight arguments, and `inner_episode_fitness` (:911) is called directly at :1624 with only `anchor_weight` and `conviction` exposed.
```

**Verifier evidence (independent re-run).**

```
Read training/rewards.py:213-236 (_impostor_terms: kills = len(KilledEvent list); unwitnessed = count with no crew witness; survival = impostors_alive/num_impostors in [0,1]; meetings_survived = a raw COUNT) and :116-118 (_side_potential returns frame.cumulative_kills for IMPOSTOR). Read tests/training/test_rewards.py:466-476 and confirmed the exact `==` literals listed above; 1.0 + (5+5+1+5) + 5 = 22.0. Read training/bakeoff/harness.py:911-948 — inner_episode_fitness(rollout, trace, *, anchor_weight=DEFAULT_ANCHOR_PENALTY_WEIGHT, conviction=None) and line 944 `shaped = compute_shaped_reward(rollout, 'IMPOSTOR').total()` with no weight arguments; :186-194 ANCHOR_CE_CEILING = 2.0 with the flag-never-drop wording; :205 DEFAULT_ANCHOR_PENALTY_WEIGHT = 1.0. INDEPENDENT RECOUNT of the recorded arms (python over training/reports/results-impostor-bakeoff.jsonl, 4 rows): bc-dagger inner_fitness_real 5.167026399377675, mean_shaped_reward_real 7.1, impostor_win_rate 0.06666666666666667, anchor_cross_entropy 1.958995585807314, fsm_intent_agreement 0.3042959427207637, anchor_ce_flagged False; utility-es 18.67066179678415 / 19.666666666666668 / 1.0 / 0.9953009725077251 / 0.39724310776942356 / False; policy-es 19.066056680854565 / 21.1 / 1.0 / 2.0156995883839897 / 0.25551294343240655 / True; map-elites 18.197966582100857 / 20.166666666666668 / 0.9333333333333333 / 1.9736115335402116 / 0.19455252918287938 / False. Every filed figure reproduces; the 'worst FSM agreement' prose does not.
```

**Verifier note.** The shaping half of this finding is the SAME declared carry as B-13 (training/rewards.py:26-45; audits/audit-phase-19-triage.md §7 item 4 / §8 row 2 — DOCUMENTED, NOT REPAIRED, ML program frozen), and the flag-never-drop behaviour of ANCHOR_CE_CEILING is an explicit definition-of-done, i.e. SPECIFIED. What is new and undeclared is the OBJECTIVE-SATURATION reading: that with three arms at win-rate ceiling and the terminal term at 1/22 of the level, the recorded fitness ordering is a kill-volume ordering. That is legitimate contract-shaping input for the routed re-ground (audits/audit-phase-20-baseline-7.md §10.2). NOT a re-report of any named known-open id. Severity P1 -> P2 for the same reasons as B-13 (frozen program, routed follow-up, no live gate). Classification defect -> design-limitation: nothing here computes a wrong value; the objective's shape is a stated choice whose consequence was never quantified. The fix sketch survives with items (1) and (2); item (3) should be reduced to 'raise anchor_weight if the ceiling is meant to bind' since the advisory wording is already in the code.

**Fix sketch.** Name in the re-ground contract: (1) collapse the kill triple-count — keep ONE of dense `kills` or the shaping, and keep `unwitnessed_kills` as a strictly-bounded stealth ratio (unwitnessed/kills) rather than a second raw count; (2) raise the terminal weight (or normalise the dense/shaping block) so win/loss is a first-order term, since three arms already saturate win-rate and the current objective cannot separate them on anything the project cares about; (3) either raise `anchor_weight` so ANCHOR_CE_CEILING actually binds, or state that the ceiling is advisory and stop calling it a ceiling. All three require the weight seam from the crew finding — today `inner_episode_fitness` cannot express any of them without an edit.

## B-15 — The conviction GO bar's conversion axis is recall-only — a degenerate always-positive head passes it by construction

**Severity:** P2 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/conviction/fidelity.py (decide_conviction_go). **Confidence:** high.
**Merged from:** finder-training-path.json#7.

**Claim.** STRUCTURE CONFIRMED: decide_conviction_go (training/conviction/fidelity.py:346-386) computes conversion_bar = 0.75 * (1 - voice_driven_share) <= 0.75 < 1.0 and tests it against conversion_recall only, so a head that calls conversion on every meeting has FN = 0, recall = 1.0, and passes AXIS 2 on any corpus. THREE CORRECTIONS. (1) The recall-only choice is EXPLICITLY SPECIFIED with a written rationale, not an oversight: the module docstring at training/conviction/fidelity.py:15-24 states 'Fidelity is the held-out RECALL on the actual testimony-backed-conversion meetings ... the ceiling's structure is a recall bound — a conversion that formed from the current meeting's spoken narrative carries no pre-meeting physical signal, so a fenced model structurally cannot flag it, exactly as the honest ceiling bounds the surrogate's top-1 ... Precision and accuracy are reported beside it, NEVER SUBSTITUTED FOR IT.' (2) The filing understates what the report already publishes: conversion_PRECISION is computed too (fidelity.py:175, :287-291; live value 0.9362), alongside the full confusion matrix (true_positives/false_positives/false_negatives/true_negatives, :169-172) — so every quantity needed to spot a degenerate head is already reported; the bar simply does not read them, by declared design. An always-positive head would drop precision to 47/87 = 0.540 in the published report. (3) 'would be certified GO' over-claims: is_go = meets_spearman AND meets_conversion, so a degenerate CONVERSION head passes axis 2 unconditionally but the conjunction still requires the separate flag channel's Spearman >= 0.5. Scope the claim to axis 2.

**As originally filed.** Axis 2 is `conversion_recall >= 0.75 * (1 - voice_driven_share)` with no precision, accuracy, or trivial-constant comparator, so a head that predicts conversion on every meeting scores recall 1.0 and passes unconditionally — the exact degeneracy the surrogate's own bar guards against with `always_eject_baseline` and the FO-6 comparator.

**Finder evidence.**

```
training/conviction/fidelity.py:357-362
  meets_spearman = report.flag_spearman >= CONVICTION_SPEARMAN_BAR
  conversion_ceiling = 1.0 - report.voice_driven_share
  conversion_bar = CONVICTION_CONVERSION_CEILING_RATIO * conversion_ceiling
  meets_conversion = report.conversion_recall >= conversion_bar
  is_go = meets_spearman and meets_conversion
Since `conversion_ceiling <= 1.0` and the ratio is 0.75, `conversion_bar <= 0.75 < 1.0`; an always-positive head has FN = 0 hence recall = 1.0, so `meets_conversion` is True on any corpus. `conversion_accuracy` and `conversion_attempts_test` ARE computed (:292, :280) and simply not read by the bar.
Live numbers (re-run on the current corpus, read-only):
  uv run python -c "...run_conviction_fidelity(build_conviction_table(Path('replays/ml_corpus/9p2i')), model=model)..."
  LIVE      : GO | spearman 0.6991 meets True | recall 0.9362 bar 0.6 meets True
  COMMITTED : GO | spearman 0.5782 | recall 0.9574 | bar 0.6375
  live accuracy 0.931 attempts 63 test_meetings 87 conversions 47 test_ejections 55
The conversion base rate on the held-out side is 47/87 = 0.54, so an always-positive head would score recall 1.0 / accuracy 0.54 and be certified GO. The verdict is load-bearing: under GO it sets `prescreen_role="gating"` and `fitness_term="ships"` (:381-386), and training/composed_runner.py:307-315 hard-refuses to build unless the committed verdict reads GO.
```

**Verifier evidence (independent re-run).**

```
Re-ran the live evaluation independently (PYTHONPATH=. uv run python; build_conviction_table('replays/ml_corpus/9p2i') + load_conviction_model_artifact('training/artifacts/conviction') + run_conviction_fidelity(model=frozen) + decide_conviction_go + load_conviction_verdict). LIVE FROZEN: test_meetings 87, test_ejections 55, conversions_test 47, conversion_attempts_test 63, flag_spearman 0.6991081211401057, conversion_recall 0.9361702127659575, conversion_precision 0.9361702127659575, conversion_accuracy 0.9310344827586207, voice_driven_share 0.19999999999999996; verdict GO, bar 0.6000000000000001. COMMITTED verdict.json: GO, spearman 0.5781584982719424, recall 0.9574468085106383, bar 0.6375, 96 meetings / 60 ejections / 47 conversions. Every filed number reproduces exactly. Base rate 47/87 = 0.5402 confirmed. Code read at fidelity.py:356-362 (the two-axis bar), :286-292 (recall/precision/accuracy), :280 (conversion_attempts_test), :73-74 (CONVICTION_SPEARMAN_BAR 0.5, CONVICTION_CONVERSION_CEILING_RATIO 0.75), :381-386 (fitness_term 'ships' / prescreen_role 'gating' / model_role 'training-signal' under GO). Load-bearing-ness confirmed at training/composed_runner.py:307-315: a non-GO committed verdict raises ValueError ('the composed runner is structurally unbuildable').
```

**Verifier note.** SPECIFIED design choice with a stated rationale, so classification moves defect -> design-limitation. NOT a re-report of any named known-open id, but the LIVE NUMBERS are already published: audits/audit-phase-20-baseline-7.md §10.2 states 'the conviction model, evaluated fully out-of-sample on a corpus it has never seen, still returns GO on both bars with a HIGHER flag Spearman (0.699 vs the recorded 0.578) on a smaller held-out split (87 meetings vs 96)' — so the finding's LIVE/COMMITTED comparison duplicates a committed audit figure and only the bar-structure argument is new. RESIDUAL VALUE, and it is genuine: the ASYMMETRY with the surrogate's own bar is real and undeclared — training/surrogate/fidelity.py axis 3 carries a trivial-constant comparator (always_eject_baseline) precisely to defeat a degenerate head, while the conviction bar carries none even though precision, accuracy and the confusion matrix are all in hand. Adding a trivial-constant axis is sound advice, and the filing is right that it must be PRE-REGISTERED before the re-ground's first held-out evaluation (fidelity.py:352-355 records the first-evaluation discipline). Severity P1 -> P2: the degeneracy is hypothetical (the live and committed models are not degenerate — precision 0.936 and 0.957), the report already exposes every number that would reveal it, and the choice is documented; but the GO verdict does gate composed_runner, so this is more than cosmetic.

**Fix sketch.** Add a third axis to `decide_conviction_go` before the re-ground re-takes the verdict: `conversion_accuracy > max(base_rate, 1 - base_rate)` measured on the SAME held-out population (the direct analogue of the surrogate's `always_eject_baseline` axis), or require precision at a stated floor alongside recall. Pre-register it in the contract, since the verdict is taken on the FIRST held-out evaluation (:352-355) and cannot be iterated afterwards.

## B-16 — Three instruments, one fingerprint: the conviction artifact carries no fit-corpus record, so its drift fence and the ML-grounding row are surrogate-only proxies

**Severity:** P2 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/artifacts + training/composed_runner.py + scripts/verify_ml_evidence.py. **Confidence:** high.
**Merged from:** finder-training-path.json#8.

**Claim.** The conviction artifact carries no machine-readable fit-corpus record, so (a) no conviction-side loader can fence against substrate drift and (b) scripts/verify_ml_evidence.py's single 'ML grounding' row extrapolates the surrogate's provenance onto the four conviction/composed rows. Both facts are exactly as reported. What must be corrected is the CONSEQUENCE the claim implies: the composed and bake-off paths ARE hard-fenced today, transitively through the surrogate leg, and the conviction fidelity divergence is separately pinned loud by a green DEFAULT-tier test — so the live gap is a missing provenance RECORD plus an unmeasured transitivity assumption, not an unfenced scoring path.

**As originally filed.** Only `training/artifacts/surrogate/` commits a `fit-corpus.json`; the conviction model has no corpus fingerprint, so `load_composed_components` fences only the surrogate against substrate drift and `verify_ml_evidence`'s single 'ML grounding' row uses the surrogate's record to decide the staleness reading for the conviction and composed rows as well.

**Finder evidence.**

```
ls training/artifacts/surrogate/ -> ballot-predictor.json, ballot-predictor.json.sha256, fit-corpus.json, max-uses.json
ls training/artifacts/conviction/ -> conviction-model.json, conviction-model.json.sha256, max-uses.json, verdict.json   (no fit-corpus.json)
cat training/artifacts/conviction/verdict.json -> records `"replay_set_dir": "replays/ml_corpus/9p2i"` (a PATH) and no `corpus_sha256`.
training/composed_runner.py:275-282 passes `corpus_dir=corpus_dir` only into `load_surrogate_runner_factory`; the conviction block at :288-315 verifies weights sha, cap keying and the GO verdict, and nothing corpus-related. training/conviction/model.py's `load_conviction_model_artifact` (:452-479) verifies only the sha256 sidecar.
scripts/verify_ml_evidence.py:1577-1601 `_grounding_row` reads ONLY `load_fit_corpus_record(repo_root / SURROGATE_DIR)` and uses that one answer to downgrade nine rows (`_CORPUS_DEPENDENT_RECOMPUTE_ROWS`, :1554-1566) that include "conviction flag-count Spearman", "conviction conversion-label accuracy", "conviction verdict.json reproduces", and the three composed rows.
The surrogate fence itself works and is live today:
  uv run python -c "load_surrogate_runner_factory(Path('training/artifacts/surrogate'), corpus_dir=Path('replays/ml_corpus/9p2i'))"
  ValueError : the surrogate ... was fitted on corpus '9p2i' (fingerprint 164ef00c16fa...) but replays/ml_corpus/9p2i fingerprints to 45b11993d7ba... - the substrate drifted; re-ground before scoring against this corpus
The bake-off does opt in (training/bakeoff/harness.py:1766-1768 and :2079-2081 pass `corpus_dir=CORPUS_SPLITS_PATH.parent`), so the surrogate path is correctly hard-blocked — the conviction path has no equivalent block.
```

**Verifier evidence (independent re-run).**

```
ALL of the finding's evidence reproduces at HEAD d8ec0a1c.
(1) `ls training/artifacts/{surrogate,conviction,composed}/` -> surrogate: ballot-predictor.json, ballot-predictor.json.sha256, fit-corpus.json, max-uses.json | conviction: conviction-model.json, conviction-model.json.sha256, max-uses.json, verdict.json (NO fit-corpus.json) | composed: manifest.json, verdict.json.
(2) `cat training/artifacts/conviction/verdict.json` -> 18 keys; `"replay_set_dir": "replays/ml_corpus/9p2i"` (a PATH); no corpus_sha256. `cat training/artifacts/surrogate/fit-corpus.json` -> {corpus_set 9p2i, corpus_sha256 164ef00c16fa5108..., fit_side_meetings 367, weights_sha256 611771a4...}.
(3) training/composed_runner.py: the ONLY `corpus_dir=corpus_dir` pass-through is at :281 into load_surrogate_runner_factory; the conviction block :288-330 verifies weights sha, cap keying and the GO verdict and nothing corpus-related. training/conviction/model.py::load_conviction_model_artifact (:452-479) verifies ONLY the sha256 sidecar.
(4) scripts/verify_ml_evidence.py:1577 `_grounding_row` reads only `load_fit_corpus_record(repo_root / SURROGATE_DIR)`; :1554-1566 `_CORPUS_DEPENDENT_RECOMPUTE_ROWS` names 9 rows including the three conviction rows and the three composed rows; :1936-1948 downgrades them.
(5) Live probe reproduces the surrogate fence verbatim: `load_surrogate_runner_factory(Path('training/artifacts/surrogate'), corpus_dir=Path('replays/ml_corpus/9p2i'))` -> ValueError: "...fitted on corpus '9p2i' (fingerprint 164ef00c16fa...) but replays/ml_corpus/9p2i fingerprints to 45b11993d7ba... - the substrate drifted; re-ground before scoring against this corpus".
MY ADDITIONS that move the severity:
(6) The fence is not merely opt-in-and-hoped-for on the harness path: tests/training/test_bakeoff_harness.py::test_harness_surrogate_loads_always_wire_the_corpus_fingerprint_fence is an AST pin asserting EVERY harness call site passes `corpus_dir`. Both harness sites (:1768, :2082) pass `corpus_dir=CORPUS_SPLITS_PATH.parent`.
(7) Because load_composed_components ALWAYS calls the surrogate loader first (:277-282, the returned factory discarded — the comment says the call IS the fence), any composed load with corpus_dir set raises before the conviction block is reached. Both fits were made on the same corpus, so the surrogate fence covers the composed path in practice.
(8) The conviction-side drift is separately measured and loud: tests/training/test_conviction_model.py:860 `test_the_committed_verdict_is_baseline6_and_the_weights_still_clear_the_bar` (DEFAULT tier, `uv run pytest ... -q` -> "1 passed in 9.44s") asserts the committed record (test_meetings 96, conversion_bar 0.6375, flag_spearman 0.578...) AND the baseline-7 re-derivation (87, 0.6, 0.699...) AND their inequality.
(9) Conviction-only load paths with no fence do exist: training/bakeoff/harness.py:756, training/crew/scorer.py:1034/:1291, training/coevo/driver.py:445 — none takes a corpus_dir. That is the residual real gap.
SPECIFIED? No. audits/audit-phase-20-baseline-7.md §10.2 names "re-stamp the fit-corpus fingerprint" (singular, the surrogate's) and never declares the conviction artifact's absence of one. The extrapolation half IS documented as intentional in _grounding_row's own docstring (:1578-1592: "Everything this leg re-derives reads the SAME corpus and the SAME frozen weights, so one question decides how to read all of it") — a stated rationale, not a measured fact.
RE-REPORT? No. Not F1 (that is the nine campaign-tier test pins), not any of C-46/C-83/C-126/C-130/F2-F5/replay_walk/1440x900/alibi_vs_sighting/C-79/C-80/C-101/C-107/C-62/C-33/C-45.
```

**Verifier note.** Evidence 100% reproducible; claim as literally worded is accurate. Severity dropped P1 -> P2 because every path that actually SCORES against the corpus is fenced today (surrogate leg, AST-pinned at both harness sites; composed transitively) and the conviction staleness is asserted explicitly by a green default-tier test. The live defect is a provenance-record gap plus an unmeasured transitivity assumption, both of which the fix_sketch correctly routes into the re-ground. Note also that B-20's closing 'Asymmetry worth naming' paragraph restates this same finding — the two items overlap and should be merged before ranking.

**Fix sketch.** Give the conviction artifact its own `fit-corpus.json` (reuse `SurrogateFitCorpus`'s shape and `fit_corpus_fingerprint`), have `load_conviction_model_artifact` / `load_composed_components` verify it against `corpus_dir`, and make `_grounding_row` read all three records and report per-instrument grounding rather than extrapolating from one. Do this IN the re-ground, while the artifacts are being rewritten — retrofitting a provenance record onto weights nobody can re-derive later is strictly harder.

## B-17 — The surrogate's GO/NO-GO verdict is the only one of the three with no committed artifact and no loader that gates on it

**Severity:** P3 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** training-path / training/surrogate (verdict plumbing). **Confidence:** high.
**Merged from:** finder-training-path.json#11.

**Claim.** There is no committed surrogate verdict.json and no loader that refuses a NO-GO surrogate, so the WIRING half of the pre-committed consequence (nothing may install the surrogate as a training-time meeting runner) is ungated — unlike the conviction and composed verdicts, whose loaders hard-refuse. But the VERDICT VALUE and its consequence MAPPING are not held by convention: an always-on DEFAULT-tier test re-derives them from committed bytes and pins them, a second default-tier test pins the recorded consequence on the committed bake-off rows, and the role is documented with citations in training/README.md §2a.

**As originally filed.** `decide_go_no_go` has no artifact writer, no loader and no consumer anywhere in training/ or scripts/, so the pre-committed NO-GO consequence ('nothing trains against it') is enforced by convention — while the conviction and composed verdicts are committed JSON that their loaders hard-refuse on.

**Finder evidence.**

```
grep -rn "decide_go_no_go|SurrogateGoVerdict" --include='*.py' training/ scripts/ -> only training/surrogate/fidelity.py:942 (the definition) and :1037 (the __all__ entry). No call site.
find training/artifacts -name verdict.json -> training/artifacts/conviction/verdict.json, training/artifacts/composed/verdict.json  (no surrogate verdict)
The other two ARE mechanical: training/conviction/fidelity.py:404-412 `load_conviction_verdict` and training/composed_runner.py:307-315 raise unless the committed verdict reads GO. `scripts/verify_ml_evidence.py`'s recompute rows include "conviction verdict.json reproduces" and "composed verdict.json reproduces" (:1554-1566) and no surrogate equivalent.
The convention is currently honoured — `training/reports/results-impostor-bakeoff.jsonl` shows `surrogate_uses_training = 0` for all four arms, with the surrogate used only as an eval-time diagnostic column (training/bakeoff/harness.py:1763-1782) — but `BakeoffProtocolConfig.surrogate_artifact_dir` defaults to `SURROGATE_ARTIFACT_DIR` unconditionally (:1437) and nothing reads a verdict before wiring it.
```

**Verifier evidence (independent re-run).**

```
The finding's evidence reproduces as scoped.
(1) `grep -rn "decide_go_no_go|SurrogateGoVerdict" --include='*.py' .` (repo-wide, wider than the finding's training/+scripts/ scope) -> training/surrogate/fidelity.py:942 (def) and :1037 (__all__), PLUS tests/training/test_surrogate_runner.py:93 (import), :796, :807. So: no production call site anywhere, as claimed — but a test call site the finding's scoping hid.
(2) `ls training/artifacts/*/verdict.json` -> conviction/verdict.json, composed/verdict.json only. No surrogate verdict.
(3) The other two loaders do hard-refuse: training/composed_runner.py:296-315 raises unless the committed conviction verdict reads GO ('a NO-GO conviction model is DIAGNOSTIC-ONLY, so the composed runner is structurally unbuildable'), and the composed verdict has the mirror at :370+. scripts/verify_ml_evidence.py:1554-1566 names 'conviction verdict.json reproduces' and 'composed verdict.json reproduces' and no surrogate equivalent; my `--only recompute` run emits 14 rows, none surrogate-verdict.
(4) `training/reports/results-impostor-bakeoff.jsonl` -> all 4 rows carry `surrogate_uses_training: 0` with `surrogate_uses_eval` 44/103/133/123. BakeoffProtocolConfig.surrogate_artifact_dir defaults to SURROGATE_ARTIFACT_DIR unconditionally (training/bakeoff/harness.py:1437) and nothing reads a verdict before wiring it. Reproduced.
MY ADDITIONS that move the severity:
(5) tests/training/test_surrogate_runner.py:792 `test_go_no_go_reproduces_the_re_measured_no_go_verdict` is DEFAULT tier (the module has no pytestmark and no @pytest.mark.campaign precedes it). `uv run pytest <nodeid> -q` -> "1 passed in 4.03s". It re-derives the verdict from the two same-population fidelity reports and asserts `verdict == 'NO-GO'`, `training_time_runner == 'fake-provider-meeting-manager'`, `surrogate_role == 'diagnostic-only'`, `top1_bar == 0.6000000000000001`. So a silent flip of the verdict or the mapping goes red in check.sh.
(6) tests/training/test_bakeoff_harness.py:692 `test_rerun_rows_pin_the_baseline_5_protocol` (DEFAULT tier) asserts `row['surrogate_uses_training'] == 0` and `surrogate_uses_eval > 0` on every committed bake-off row — the recorded consequence is pinned, not just observed.
(7) training/README.md §2a (:88-125) documents the split by name with line citations: RANKING kept, 'the standalone DECISION arm is retired (19.19)', verdict NO-GO, surrogate_role='diagnostic-only', and an explicit HEAD-verified census of the three production importers, with the composed_runner call named as 'purely as the sha/staleness verification fence'.
SPECIFIED? The role and the retirement are specified (training/README.md §2a, report-ballot-surrogate.md :309-325). The absence of a committed verdict artifact is not specified either way.
RE-REPORT? No — not on the known-open list.
```

**Verifier note.** The structural asymmetry is real and the fix_sketch is cheap and sensible. But 'enforced by convention' is materially overstated: the value and the mapping are pinned by an always-on green test and the recorded consequence by a second one, and the only thing genuinely ungated is the wiring (no loader refuses to install a NO-GO surrogate as a training-time runner). Given that the ML program is under an explicit FREEZE and the boundary is documented with a HEAD-verified importer census, P1 is too high; P3.

**Fix sketch.** As part of the re-ground, commit `training/artifacts/surrogate/verdict.json` from `decide_go_no_go`, keyed on `weights_sha256` exactly as the conviction verdict is, add a `load_surrogate_verdict`, and have any path that installs the surrogate as a TRAINING-time meeting runner refuse under NO-GO (the eval-time diagnostic column stays legal). Add the matching "surrogate verdict.json reproduces" row to `verify_ml_evidence`'s recompute leg so the third instrument is checked like the other two.

## B-18 — The corpus recorder aborts a multi-hour record on ONE dead-owner probe; the sibling recorder needs a 10-poll streak for exactly this reason

**Severity:** P2 (finder: P1). **Classification:** defect. **Verdict:** ADJUSTED. **Area:** gates-scripts / recorders (scripts/record_ml_corpus.sh). **Confidence:** high.
**Merged from:** finder-gates-scripts.json#1.

**Claim.** scripts/record_ml_corpus.sh::acquire_lock declares the run failed on ONE dead-owner probe, while the structurally identical race in scripts/refresh_samples.sh::_acquire_lock was fixed with a 10-poll streak. The race is real and empirically observed (it flaked CI three times on the sibling). Two corrections: (a) the mirror was not overlooked, it was ROUTED — the 20.21 contract sends it to Task 20.36 and the #388 follow-up explicitly descoped it — and 20.36 merged without executing it, which no close audit records as open; (b) the blast radius is a spurious abort plus operator restart latency, not the ~19h leg, because the recorder has a resume skip-scan and each seed lands by an atomic mv from a private stage.

**As originally filed.** scripts/record_ml_corpus.sh::acquire_lock declares the run failed the first time it observes a lock owner pid that no longer exists, but the benign release-then-exit race that produces that observation is structural in this script (the owner pid is written by a command-substitution subshell that dies immediately), so a ~22-23h hosted corpus re-record can be aborted spuriously — the fix for this exact race already exists in scripts/refresh_samples.sh and was never back-ported.

**Finder evidence.**

```
Command: `grep -n "acquire_lock\|dead_polls\|last_dead_owner" scripts/record_ml_corpus.sh scripts/refresh_samples.sh`
Output:
  scripts/record_ml_corpus.sh:1032:  acquire_lock() {
  scripts/record_ml_corpus.sh:1057:    acquire_lock || return 1
  scripts/record_ml_corpus.sh:1124:    if ! acquire_lock; then
  scripts/refresh_samples.sh:776:_acquire_lock() {
  scripts/refresh_samples.sh:777:  local owner last_dead_owner dead_polls
  scripts/refresh_samples.sh:798:      if [[ "$owner" == "$last_dead_owner" ]]; then
  scripts/refresh_samples.sh:804:      if [[ "$dead_polls" -ge 10 ]]; then

scripts/record_ml_corpus.sh:1032-1049 (the whole body, no streak):
    acquire_lock() {
      local owner
      [[ -e "$stage_dir/.failed" ]] && return 1
      while ! mkdir "$lockdir" 2>/dev/null; do
        if [[ -e "$stage_dir/.failed" ]]; then
          return 1
        fi
        owner="$(cat "$lockdir/owner" 2>/dev/null || true)"
        if [[ -n "$owner" ]] && ! kill -0 "$owner" 2>/dev/null; then
          echo "ERROR: corpus lock owner (pid $owner) died holding the lock" \
            "(killed/crashed mid critical section); the set is incomplete." >&2
          touch "$stage_dir/.failed"
          return 1
        fi
        sleep 0.1
      done
      printf '%s' "${BASHPID:-$$}" >"$lockdir/owner"

scripts/refresh_samples.sh:791-806 states the race verbatim and why one probe is not a verdict:
    # One dead probe is a race, not a verdict: between this waiter's cat and
    # its kill -0 the holder may have released the lock and exited (a worker
    # draining the queue, or a seed-claim command-substitution subshell whose
    # pid dies with the claim). ... the same dead pid must stay the recorded
    # owner across 10 consecutive polls (~1s) before the refresh is failed.

The race is structural in record_ml_corpus.sh, not hypothetical: `claim_next_seed` (scripts/record_ml_corpus.sh:1055-1066) calls `acquire_lock` and then `release_lock` INSIDE the function, and its only call site is a command substitution — scripts/record_ml_corpus.sh:1166 `seed="$(claim_next_seed)"`. `${BASHPID:-$$}` inside that substitution is the substitution subshell's pid, which is released (rm -rf lockdir) and then exits within microseconds. A waiter that cats the owner just before the release and runs kill -0 just after sees a dead pid and immediately `touch "$stage_dir/.failed"`.

The ledgered limitation is a DIFFERENT one and does not cover this. Command: `grep -n "lock-race\|dead-owner" audits/audit-phase-18-close.md training/README.md`
Output: audits/audit-phase-18-close.md:1005 — "the recorded limitation: *\"On 3.2 every worker shares `$$` … so dead-owner detection degrades to a no-op…\"*" (the Bash-3.2 degradation only); training/README.md:247 row 5 points at the same comment block.

Blast radius: default AILIBI_REFRESH_WORKERS=2 (scripts/record_ml_corpus.sh:313), so two workers contend on every seed claim and every MANIFEST merge across the whole run; the recorder's own header measures the 9p2i leg at 19h26m (scripts/record_ml_corpus.sh:26-27).
```

**Verifier evidence (independent re-run).**

```
The finding's evidence reproduces verbatim at HEAD d8ec0a1c.
(1) scripts/record_ml_corpus.sh:1032-1049 `acquire_lock` — read in full: `local owner` only; on `[[ -n "$owner" ]] && ! kill -0 "$owner"` it echoes ERROR, `touch "$stage_dir/.failed"`, `return 1` on the FIRST observation. Owner written at :1049 as `${BASHPID:-$$}`.
(2) scripts/refresh_samples.sh:776-817 `_acquire_lock` — `local owner last_dead_owner dead_polls`, streak increment at :798-803, `if [[ "$dead_polls" -ge 10 ]]` at :804, reset on a live probe or a changed owner. Its comment (:791-797) names the exact race including 'a seed-claim command-substitution subshell whose pid dies with the claim'.
(3) The race is structural in record_ml_corpus.sh: `claim_next_seed` (:1053-1066) calls acquire_lock and release_lock INSIDE itself, and its only call site is `seed="$(claim_next_seed)"` (:1166, inside run_worker). `${BASHPID:-$$}` there is the command-substitution subshell's pid, and `release_lock` (`rm -rf lockdir`) removes the owner file microseconds before that pid dies. Confirmed by reading run_worker (:1163-1170) and record_one_seed's manifest-lock section (:1124-1140) — the latter runs in the long-lived worker subshell, so only claim_next_seed mints the transient owner.
(4) Contention is the default: `REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"` at :320, pool spawn at :1172-1180. Header :25-27 measures the 9p2i leg at 19h26m within a ~22-23h two-set run.
(5) The ledgered limitation is a DIFFERENT one, exactly as the finding says: audits/audit-phase-18-close.md §7 row 5 quotes only the Bash-3.2 `$$`-sharing degradation; training/README.md §6 row 5 points at the same comment block.
MY ADDITIONS:
(6) DECISIVE PROVENANCE. `git log -S dead_polls -- scripts/refresh_samples.sh` -> ONE commit, 28599ec3 'task 20.21 follow-up: the lock's dead-owner verdict must survive a release racing the probe (#388)'. Its body: 'Same fix for the twin lock in record_ml_corpus.sh' — then a later review commit in the same PR reads 'review: descope the corpus-recorder mirror (20.36 owns it per the 20.21 contract)'. tasks/phase-20.md:3384 carries that routing verbatim: 'scripts/record_ml_corpus.sh (... mirror any fix there in 20.36, not here)'.
(7) THE ROUTE WAS DROPPED. `git log --oneline -- scripts/record_ml_corpus.sh` -> the most recent commit is efcd43b8 (task 20.36, #389), which merged AFTER 28599ec3 and DID edit the file — without the mirror. audits/audit-phase-20-close.md:224 records 20.21 (#359, #388) as VERIFIED and names no open mirror.
(8) EMPIRICAL SUPPORT. 28599ec3's message attributes the fix to 'the CI flake on test_two_workers_lose_no_manifest_row (PRs #369/#372/#378)' — the race fired three times in CI on the sibling script.
(9) MITIGATION the finding omits: scripts/record_ml_corpus.sh:991 prints 'Resume: $already/$count seed(s) already recorded; $total_seeds remaining.' with a provenance-checked skip-scan (:952-990), and the `.failed` sentinel lives under a per-run mktemp stage dir, so a fresh invocation resumes. Combined with per-seed atomic `mv` staging, a spurious abort costs the in-flight seed plus the idle time until the operator notices, not the completed hours.
(10) tests/scripts/test_record_ml_corpus.py contains no acquire_lock / dead-owner test at all (grep for 'acquire_lock|dead' -> zero hits), so the mirror also lacks the two verbatim-extracted tests refresh_samples.sh gained.
RE-REPORT? No. Not C-74 (that is the zero-coverage-of-worker-paths item, closed by 20.21) and not the Bash-3.2 ledger row. Not on the supplied known-open list.
```

**Verifier note.** Core defect CONFIRMED with strong new provenance: this is a routed-and-dropped mirror (20.21 -> 20.36), not an unnoticed gap, and the fix is a ~10-line verbatim back-port plus the two tests. Severity dropped P1 -> P2 on the resume path: the exposure is a spurious mid-run abort requiring an operator restart, not loss of the ~19h leg. Worth flagging to the owner as 'the ML re-ground runs this exact recorder next'.

**Fix sketch.** Back-port the streak logic from scripts/refresh_samples.sh:776-817 verbatim into scripts/record_ml_corpus.sh:1032-1049 — `local owner last_dead_owner dead_polls`, increment on a repeated dead owner, reset when the owner changes or the probe is live, and only `touch .failed` at `dead_polls >= 10`. It is a ~10-line diff and the two functions should then be byte-comparable modulo the `_`-prefixed names; consider extracting the mutex into a sourced helper so the two recorders cannot diverge again.

## B-19 — The samples recorder pins the prompt SET but not its per-template VERSIONS, and validity_gate.py has no CLI surface for the pin that would catch it

**Severity:** P3 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** gates-scripts / recorders + acceptance gate (scripts/refresh_samples.sh, scripts/validity_gate.py). **Confidence:** high.
**Merged from:** finder-gates-scripts.json#2.

**Claim.** Only the second half survives as a gap: eval/validity.py implements expected_prompt_versions but scripts/validity_gate.py exposes no CLI flag for it, so the acceptance command both recorders print cannot pin per-template versions. The first half must be withdrawn as a defect — scripts/refresh_samples.sh carrying no version literal is a DECLARED design decision stated in the script's own comment ('the registry in orchestrator/game.py is the version authority — this script carries no version literal', :555-557), and the finding's supporting quote is misattributed: 'cannot be mis-set — the guard only pins the prompt set' (:559-560) is about the substrate LEVERS being unconditionally ON, not about prompt versions. A registry bump is also not silent repo-wide: two default-tier tests go red on any bump.

**As originally filed.** A prompt-version bump inside the qwen3_6_27b registry entry (exactly what Task 20.31 did, v3 to v4) would let scripts/refresh_samples.sh re-record replays/samples/ on a different rendered-prompt substrate with every preflight green, and the one check that could catch it — eval.validity's expected_prompt_versions — is unreachable from scripts/validity_gate.py's argparse.

**Finder evidence.**

```
Command: `grep -n "REQUIRED_PROMPT_VERSIONS\|check_prompt_version_registry\|check_recorded_prompt_versions" scripts/refresh_samples.sh`
Output: (no matches for any of the three)

refresh_samples.sh pins only the set name and the owner model, and says so in its own comment at scripts/refresh_samples.sh:560:
    # cannot be mis-set — the guard only pins the prompt set.
  scripts/refresh_samples.sh:566  REQUIRED_PROMPT_SET="qwen3_6_27b"
  scripts/refresh_samples.sh:588  REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B"

The sibling recorder DOES carry both halves of the pin. scripts/record_ml_corpus.sh:155:
    REQUIRED_PROMPT_VERSIONS="accusation_round.qwen3_6_27b.v4, crewmate_report.qwen3_6_27b.v4, impostor_report.qwen3_6_27b.v4, vote_ballot.qwen3_6_27b.v4"
  with a FORWARD registry assertion at preflight (check_prompt_version_registry, scripts/record_ml_corpus.sh:495-520, echoed at :913) and a BACKWARD freeze assertion over the MANIFEST cells (check_recorded_prompt_versions, scripts/record_ml_corpus.sh:522-560). The constant's own comment states the hazard the samples recorder is exposed to (scripts/record_ml_corpus.sh:150-154): "The set NAME alone is not a version pin — the registry entry can be bumped by a later task".

The registry is live and bumpable. Command: `uv run python -c "from orchestrator.game import PROMPT_VERSION_SETS; m=PROMPT_VERSION_SETS['qwen3_6_27b']; print(', '.join(sorted(f'{k}.{v}' for k,v in m.items())))"`
Output: accusation_round.accusation_round.qwen3_6_27b.v4, crewmate_report.crewmate_report.qwen3_6_27b.v4, impostor_report.impostor_report.qwen3_6_27b.v4, vote_ballot.vote_ballot.qwen3_6_27b.v4

The downstream acceptance gate can express the pin but the CLI cannot pass it. eval/validity.py:905 and :1142 both take `expected_prompt_versions: Mapping[str, str] | None = None`, and eval/validity.py:1001-1012 turns it into an exact violation. Command: `grep -n "add_argument" scripts/validity_gate.py` → four flags only; the full file (read at HEAD) exposes `replay_set_dir`, `--json`, `--expected-model` (:78) and `--require-zero-cost` (:86). There is no `--expected-prompt-versions`, so the acceptance command the recorders themselves print (scripts/record_ml_corpus.sh:825: "acceptance (per set, before merge): scripts/validity_gate.py <set> --expected-model … --require-zero-cost") cannot pin versions.

What IS caught: a MIXED set (eval/validity.py:988-992, "multiple prompt-version sets across the set"). What is NOT caught: a set recorded HOMOGENEOUSLY at the wrong version — precisely the shape a full re-record after a bump produces.
```

**Verifier evidence (independent re-run).**

```
Every factual command in the finding reproduces at HEAD d8ec0a1c.
(1) `grep -n "REQUIRED_PROMPT_VERSIONS|check_prompt_version_registry|check_recorded_prompt_versions" scripts/refresh_samples.sh` -> zero hits. The same grep on scripts/record_ml_corpus.sh -> :156 (the constant), :499 check_prompt_version_registry, :530 check_recorded_prompt_versions, :910/:913 the preflight call, :1248-1249 the freeze-time call. Reproduced.
(2) refresh_samples.sh:566 REQUIRED_PROMPT_SET="qwen3_6_27b"; :588 REQUIRED_SET_OWNER_MODEL="Qwen/Qwen3.6-27B". Reproduced.
(3) `grep -n add_argument scripts/validity_gate.py` -> exactly four (:68 replay_set_dir, :73 --json, :78 --expected-model, :86 --require-zero-cost). No --expected-prompt-versions. eval/validity.py:905 and :1142 both accept `expected_prompt_versions: Mapping[str, str] | None = None`, threaded at :1240, turned into an exact violation at :1001-1012. record_ml_corpus.sh:825 prints the acceptance line with only --expected-model and --require-zero-cost. Reproduced.
(4) The registry probe reproduces byte-for-byte, doubled prefixes and all: 'accusation_round.accusation_round.qwen3_6_27b.v4, crewmate_report.crewmate_report.qwen3_6_27b.v4, impostor_report.impostor_report.qwen3_6_27b.v4, vote_ballot.vote_ballot.qwen3_6_27b.v4'.
(5) The mixed-vs-homogeneous asymmetry reproduces: eval/validity.py:988-992 flags 'multiple prompt-version sets across the set'; a homogeneous set at the wrong version is caught only by the opt-in expected_prompt_versions leg.
WHY THE FIRST HALF IS NOT A DEFECT:
(6) SPECIFIED. scripts/refresh_samples.sh:552-566, read in full, states the intent: '...the registry in orchestrator/game.py is the version authority — this script carries no version literal.' The mirror comment in record_ml_corpus.sh:147-155 states why the CORPUS recorder is different: 'A corpus recorded before this constant moved carries the older stamps in its own MANIFEST; re-locking it is an owner decision (re-record + re-freeze).' The corpus is a frozen ML substrate under committed fits; replays/samples/ is the canonical set that is MEANT to re-record with the substrate — which is exactly what 20.31 -> 20.36 did on purpose.
(7) MISQUOTE. The finding quotes ':560  # cannot be mis-set — the guard only pins the prompt set.' as evidence about versions. Read in context (:558-560) the sentence is: 'The substrate levers are ALL unconditionally ON ... so they need no export and cannot be mis-set — the guard only pins the prompt set.' It is about levers.
(8) A BUMP IS NOT SILENT. tests/scripts/test_record_ml_corpus.py:600 test_prompt_version_registry_matches_locked_script_constant asserts PROMPT_VERSION_SETS['qwen3_6_27b'] equals the locked script constant ('Re-locking is an owner decision'); tests/agents/test_bespoke_prompt_sets.py:522-529 test_registry_stamps_all_four_templates_v4 pins the four v4 stamps exactly; both are DEFAULT tier. tests/meetings/test_prompt_byte_golden.py re-renders committed sample meetings through the live registry (the class of failure audits/audit-phase-20-baseline-7.md §10.1 item 1 describes).
RE-REPORT? No.
```

**Verifier note.** The observation is real but the framing inverts a stated design decision, and one quoted line is taken from a sentence about substrate levers rather than prompt versions. Reduce to the validity_gate CLI gap alone: a capability eval/validity.py already implements that no operator-facing command can reach. That is a small, cheap, genuine hole — P3, design-limitation — and the fix_sketch's item (2) is the right one; item (1) should be dropped or re-argued against the script's own stated authority model.

**Fix sketch.** Two small, independent edits. (1) Give scripts/refresh_samples.sh the same REQUIRED_PROMPT_VERSIONS constant plus the forward registry assertion record_ml_corpus.sh:495-520 already implements (the function is self-contained; both recorders should call one shared helper rather than a second copy). (2) Add `--expected-prompt-versions KEY=VER,…` to scripts/validity_gate.py's parser and thread it into run_validity_gate's existing `expected_prompt_versions` parameter, then update the acceptance line both recorders echo. Neither costs a re-record.

## B-20 — The STALE amnesty darkens the two whole-object identity pins, so the committed adoption bars are currently editable with no gate at all

**Severity:** P3 (finder: P1). **Classification:** design-limitation. **Verdict:** ADJUSTED. **Area:** gates-scripts / verify_ml_evidence.py structure. **Confidence:** high.
**Merged from:** finder-gates-scripts.json#3.

**Claim.** The amnesty is row-scoped, so both verdict-identity rows report STALE and cannot FAIL, and neither training/artifacts/conviction/verdict.json nor training/artifacts/composed/verdict.json has a .sha256 sidecar — both reproduce. The headline consequence does NOT: of the five named adoption bars, conversion_bar IS gated in the DEFAULT tier by a green test that loads the committed artifact directly. The corrected statement is narrower: conversion_ceiling has no value pin anywhere, and top1_bar / top1_ceiling / decision_accuracy_bar are pinned only inside a campaign-tier test whose value assertions are unreachable today behind the identity assertion that fails first — which is a consequence of the already-known-open F1, not an independent hole.

**As originally filed.** The grounding amnesty downgrades whole verdict-identity ROWS rather than the corpus-derived FIELDS inside them, and only 6 of the 9 amnestied rows have their values pinned by a test — so `conviction verdict.json reproduces` (11/18 fields already disagreeing) and `composed verdict.json reproduces` (9/17) enforce nothing today, and the adoption bars they exist to protect (top1_bar, top1_ceiling, conversion_bar, conversion_ceiling, decision_accuracy_bar) can be edited without any check going red.

**Finder evidence.**

```
Command: `uv run python scripts/verify_ml_evidence.py --only recompute`
Output (excerpt):
  [STALE ] conviction verdict.json reproduces
            measured : 11/18 fields identical
            note     : conversion_bar: re-derived 0.6000000000000001 != committed 0.6375
            note     : conversion_ceiling: re-derived 0.8 != committed 0.85
            note     : test_meetings: re-derived 87 != committed 96
  [STALE ] composed verdict.json reproduces
            measured : 9/17 fields identical
            note     : decision_accuracy_bar: re-derived 0.632183908045977 != committed 0.625
            note     : top1_bar: re-derived 0.6000000000000001 != committed 0.6375
            note     : top1_ceiling: re-derived 0.8 != committed 0.85
  checks: 14 | OK 4 | FAIL 0 | STALE 10 | ABSENT 0 | INFO 0
  verify-ml-evidence: every check passed.

These rows are the STRONGEST pins by the module's own account — scripts/verify_ml_evidence.py:1952-1960 `_verdict_identity_row`: "The strongest pin: the whole committed verdict object, field for field." The downgrade is applied wholesale at scripts/verify_ml_evidence.py:1934-1948 (`replace(row, status="STALE", …)` for any FAIL row named in `_CORPUS_DEPENDENT_RECOMPUTE_ROWS`), and the membership list at :1554-1569 includes both identity rows.

The test backstop covers 6 of the 9. Command: `grep -n "verdict.json reproduces\|convicting top-1\|composed exact-outcome\|composed decision accuracy" tests/scripts/test_verify_ml_evidence.py`
Output:
  409:        "composed decision accuracy",
  410:        "composed exact-outcome match",
  419:        ("composed decision accuracy", "0.8620689", "0.8645833"),
  420:        ("composed exact-outcome match", "0.8160919", "0.7916666"),
(no hit for "verdict.json reproduces" or "convicting top-1"). tests/scripts/test_verify_ml_evidence.py:415-424 pins six (measured, committed) pairs; the three amnestied rows with NO value pin anywhere are `conviction verdict.json reproduces`, `composed convicting top-1`, `composed verdict.json reproduces`.

And nothing else covers those bytes. Command: `uv run python scripts/verify_ml_evidence.py --only sidecars 2>&1 | grep -c "verdict.json"` → `0`. Confirmed by `ls training/artifacts/composed/ training/artifacts/conviction/`: composed/ holds manifest.json + verdict.json with NO .sha256 sidecar; conviction/ sidecars only conviction-model.json.

Secondary loudness note: with 10 STALE rows standing, the command's last line is still "verify-ml-evidence: every check passed." (scripts/verify_ml_evidence.py:3047).

Asymmetry worth naming while the fix is open: the grounding row that governs all of this reads ONLY the surrogate's provenance (scripts/verify_ml_evidence.py:1578-1600 loads `training/artifacts/surrogate/fit-corpus.json`). `cat training/artifacts/surrogate/fit-corpus.json` shows the record; `ls training/artifacts/conviction/` shows the conviction model has no fit-corpus record at all, so "the conviction model is grounded on this corpus" is asserted transitively, never measured.
```

**Verifier evidence (independent re-run).**

```
The mechanism evidence reproduces exactly.
(1) `uv run python scripts/verify_ml_evidence.py --only recompute` at HEAD d8ec0a1c -> 'checks: 14 | OK 4 | FAIL 0 | STALE 10 | ABSENT 0 | INFO 0'. '[STALE ] conviction verdict.json reproduces / measured: 11/18 fields identical' with the seven drifted fields listed (conversion_bar 0.6000000000000001 != 0.6375; conversion_ceiling 0.8 != 0.85; conversion_recall; flag_spearman; test_ejections 55 != 60; test_meetings 87 != 96; voice_driven_share). '[STALE ] composed verdict.json reproduces / measured: 9/17 fields identical' with eight drifted (convicting_top1, decision_accuracy, decision_accuracy_bar 0.632... != 0.625, exact_outcome_match, test_ejections, test_meetings, top1_bar 0.6000000000000001 != 0.6375, top1_ceiling 0.8 != 0.85).
(2) scripts/verify_ml_evidence.py:1936-1948 applies `replace(row, status='STALE', ...)` to any FAIL row named in _CORPUS_DEPENDENT_RECOMPUTE_ROWS (:1554-1566, which includes both identity rows). :1953 _verdict_identity_row's docstring reads 'The strongest pin: the whole committed verdict object, field for field.'
(3) `--only sidecars` -> 6 checks, zero mention of verdict.json; `ls` confirms composed/ has manifest.json + verdict.json with no sidecar and conviction/ sidecars only conviction-model.json.
WHERE THE CLAIM BREAKS:
(4) The finding's test-backstop grep was scoped to tests/scripts/test_verify_ml_evidence.py only. Broader coverage exists. tests/training/test_conviction_model.py:860 test_the_committed_verdict_is_baseline6_and_the_weights_still_clear_the_bar loads _ARTIFACT_DIR = <repo>/training/artifacts/conviction (:92) and asserts, on the COMMITTED object: test_meetings==96, test_ejections==60, conversions_test==47, flag_spearman==0.5781584982719424, conversion_recall==45/47, voice_driven_share==0.15, conversion_bar==pytest.approx(0.6375), meets_conversion_bar, and the (fitness_term, prescreen_role, model_role) triple. It has NO campaign marker (module has no pytestmark; the last @pytest.mark.campaign in the file is at :720, before an earlier def) -> DEFAULT tier. I ran it: '1 passed in 9.44s'. Editing conversion_bar in the committed verdict turns check.sh red.
(5) tests/training/test_composed_runner.py:1586 test_committed_composed_verdict_is_rederivable loads _COMPOSED_ARTIFACT_DIR (:133) and at :1626-1634 asserts decision_accuracy_bar==0.625, top1_bar==0.6375, top1_ceiling==0.85, convicting_top1==46/60. BUT the module is `pytestmark = pytest.mark.campaign` (:127) and I ran the node with -m campaign: it FAILS at :1612 on the identity splice (convicting_top1 0.7667 vs 0.8182, test_meetings 96 vs 87, top1_bar 0.6375 vs 0.6000, decision_accuracy ...), so :1626+ never executes. Those three bars are therefore effectively ungated TODAY — and that short-circuit is exactly F1's fifth corpus-derived fit pin (audits/audit-phase-20-close.md:97 names this test and quotes 'top1_bar 0.6375 -> 0.6000'). Partly a re-report of F1.
(6) conversion_ceiling: repo-wide `grep -rn conversion_ceiling tests/ training/ scripts/ --include='*.py'` (minus conversion_ceiling_ratio) -> only tests/training/test_bakeoff_harness.py:913 and tests/training/test_crew_scorer.py:279, both synthetic report constructions. No pin on the committed value. That one stands unqualified.
(7) ARITHMETIC INVERSION in the claim text: it reads 'conviction verdict.json reproduces (11/18 fields already disagreeing) ... composed (9/17)'. The tool's own output, which the finding quotes, says '11/18 fields IDENTICAL' and '9/17 fields IDENTICAL' — i.e. 7 and 8 disagree.
(8) LOUDNESS understated: immediately above the closing line the command prints '10 check(s) report STALE — the committed ML fits and the corpus under them are grounded on different recordings, so those rows measure a declared gap rather than a defect. Re-grounding is a named follow-up (audits/audit-phase-20-baseline-7.md §10.2); the ML grounding row above carries the two fingerprints.' Only the very last line reads 'every check passed.'
SPECIFIED / DECLARED?
(9) The ten-STALE state is EXPLICITLY RATIFIED: audits/audit-phase-20-baseline-7.md §10.2 — 'The command runs green with ten rows reporting STALE, each naming this section' and 'How the interim state is held, so it is loud without being red.'
(10) The row-scoping is a JUST-LANDED REVIEWED DECISION, not an oversight: commit 3b4533ee ('task 20.36: Codex round 1 — the stale amnesty gets a boundary') converted a BLANKET amnesty into the named list precisely so corpus-INDEPENDENT rows keep FAILING, with two tests holding the boundary (tests/scripts/test_verify_ml_evidence.py::test_the_stale_amnesty_stops_at_the_corpus_dependent_rows, plus a perturbed-digest case). The module's own comment at :1540-1553 states the rationale.
(11) The closing 'Asymmetry worth naming' paragraph is B-16 restated.
```

**Verifier note.** Headline REFUTED, residual observation ADJUSTED and kept. The true residual: (a) the two identity rows bundle corpus-dependent and corpus-independent FIELDS, so the row-scoped amnesty darkens the latter — a real granularity gap in a design that landed three commits ago explicitly to stop exactly that class of blindness; (b) neither verdict.json has a sha256 sidecar; (c) conversion_ceiling on the committed conviction verdict has no pin anywhere. The cheap interim fix in the sketch (emit .sha256 sidecars beside both verdict.json files) is the right one-commit close. P1 -> P3: the strongest named bar is gated in the default tier and green, the composed half is F1, and the whole state is ratified in §10.2.

**Fix sketch.** Make the amnesty field-scoped rather than row-scoped: have `_verdict_identity_row` take the set of corpus-derived field names the gap explains, downgrade only those, and keep the row FAIL on any OTHER drifted field. Cheaper interim that closes the same hole in one commit: emit `<name>.sha256` sidecars beside training/artifacts/{conviction,composed}/verdict.json so the corpus-independent sidecar leg pins their bytes while the identity rows are dark. Also give the conviction artifact its own fit-corpus.json at the re-ground so the grounding row measures both fits instead of one, and change the closing line to "every check passed (N STALE)" when stale is non-empty.

## B-21 — The corpus recorder's entire recording engine is untested; the identical hardening was applied to the sibling recorder only

**Severity:** P1. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** gates-scripts / recorder test coverage. **Confidence:** high.
**Merged from:** finder-gates-scripts.json#4.

**Claim.** Every one of the 54 tests in tests/scripts/test_record_ml_corpus.py is engineered to stop before any seed stages, so the ~355 lines of scripts/record_ml_corpus.sh::record_set (worker pool, mkdir mutex, per-seed crash retry, lock-guarded MANIFEST merge, freeze) execute in no test — while the sibling scripts/refresh_samples.sh got a hermetic recording family that drives exactly those functions.

**Finder evidence.**

```
Command: `wc -l scripts/record_ml_corpus.sh; grep -n "^record_set()\|run_worker()" scripts/record_ml_corpus.sh`
Output: 1307 scripts/record_ml_corpus.sh; 929:record_set() {; 1162:  run_worker() {  (record_set spans :929-1284, ~355 lines)

Command: `grep -c "def test_" tests/scripts/test_refresh_samples.py tests/scripts/test_record_ml_corpus.py`
Output: tests/scripts/test_refresh_samples.py:82 / tests/scripts/test_record_ml_corpus.py:54

Command: `grep -n "acquire_lock\|run_worker\|record_one_seed\|claim_next_seed" tests/scripts/test_refresh_samples.py`
Output includes tests/scripts/test_refresh_samples.py:1055-1056 — "so these cases are what cover run_worker / claim_next_seed / _acquire_lock / record_one_seed and the lock-guarded MANIFEST merge" — and tests/scripts/test_refresh_samples.py:1357-1362 asserts each function by name off a `bash -x` trace:
    for function in ("run_worker", "claim_next_seed", "record_one_seed", "_acquire_lock"):
        assert re.search(rf"^\++ {function}\b", proc.stderr, re.MULTILINE), function

The same grep over tests/scripts/test_record_ml_corpus.py matches none of those four names — only `worker` in dry-run knob tests (:378-406, "seed workers: 2 parallel").

The record-path tests state their own stopping point. tests/scripts/test_record_ml_corpus.py:625-626: "Several guards in one hermetic run of the REAL record path (no network: the run stops before any tournament invocation)"; :668-669 "Hermetic: fails before any tournament invocation." They cannot proceed further by construction — the script refuses every non-featherless provider (scripts/record_ml_corpus.sh:840, pinned by tests/scripts/test_record_ml_corpus.py:442 `test_preflight_refuses_fake_provider`) and the tests supply `FEATHERLESS_API_KEY="test-key-unused"`.

This is the direct cause of finding 1 above: the lock-race fix landed in the recorder that has a recording test family and not in the one that does not.
```

**Verifier evidence (independent re-run).**

```
HEAD d8ec0a1c (clean main).

(1) Script shape reproduces. `wc -l scripts/record_ml_corpus.sh` -> 1307. `grep -n '^\s*[a-z_]*() {' scripts/record_ml_corpus.sh` -> ... 740:freeze_manifest() {, 929:record_set() {, 1032:  acquire_lock() {, 1051:  release_lock() {, 1055:  claim_next_seed() {, 1073:  record_one_seed() {, 1162:  run_worker() {, closing `}` at 1284. So record_set spans 929-1284 (356 lines) and the FOUR worker-pool functions are NESTED inside it -- unreachable except by entering record_set.

(2) Test counts reproduce. `grep -c 'def test_' tests/scripts/test_record_ml_corpus.py tests/scripts/test_refresh_samples.py` -> 54 / 82.

(3) The name grep reproduces. `grep -n 'acquire_lock\|run_worker\|record_one_seed\|claim_next_seed' tests/scripts/test_record_ml_corpus.py` -> ONE line, `388:def test_dry_run_worker_count_is_overridable()` (a dry-run knob, not the pool). The same grep over tests/scripts/test_refresh_samples.py -> 12 hits including the module docstring at :10-11, the coverage comment at :1055-1056, the bash -x trace assertion list at :1358-1361 ("run_worker", "claim_next_seed", "record_one_seed", "_acquire_lock"), the fail-loud case at :1554, and the dedicated `_acquire_lock` liveness-probe driver at :1605-1636.

(4) The stopping point reproduces, and I walked every record-path test to find the DEEPEST one. The two positive cases are the deepest: test_record_path_accepts_stamped_present_replay (:693-724) and test_record_path_accepts_a_replay_stamped_with_the_declared_slate (:898-926). Both assert the run fails at `"disagrees with the requested roster"` -- i.e. at the roster pin (scripts/record_ml_corpus.sh:966-975), which is BEFORE the seed-list build (:975-991), before the mktemp stage dir (:1001), and before any of acquire_lock/claim_next_seed/record_one_seed/run_worker. Every other record-path test fails earlier still (check_seed_range at :621, check_replay_provenance at :662/:727/:763/:795/:833/:929/:957). The provider gate at scripts/record_ml_corpus.sh:839-843 ('records ONLY on featherless') is pinned by :442 test_preflight_refuses_fake_provider, so no fake-provider seam exists.

(5) Extra confirmation the finding did not make: `freeze_manifest` (top-level, :740) is invoked ONLY at :1279, inside record_set's finalize -- the `--splits-only` path at :781 calls write_splits alone. So the freeze is untested too, exactly as the claim lists. write_splits IS covered, but only through --splits-only (tests :1000-1114), never through record_set.

(6) Not specified / not a declared carry: no tasks/ or audits/ text declares the corpus recorder's worker pool deliberately untested. audits/review-2026-08-19/B/eval-and-scripts.md:125 recommends 'allow the fake provider so the worker path gets tests' -- for refresh_samples.sh, which since got that family; the corpus recorder did not.

(7) Not a re-report: absent from the enumerated known-open set (C-46/C-83/C-126/C-130/F1-F5/replay_walk/1440x900/duplicate alibi_vs_sighting mint/C-79/C-80/C-101/C-107/C-62/C-33/C-45) and from audits/review-2026-08-19/B/collated-findings.md.
```

**Verifier note.** Every evidence line reproduces verbatim against fresh code, and I strengthened it: the four functions are NESTED inside record_set (scripts/record_ml_corpus.sh:1032/1055/1073/1162), so no test can reach them without entering record_set, and freeze_manifest is likewise reachable only from record_set:1279. I independently walked all 54 tests to find the deepest record-path case; the two positive stamp tests are it, and both stop at the roster pin (:966-975), upstream of the stage dir and the pool. Claim, P1 severity and quality-debt classification all stand as written.

**Fix sketch.** Port the fake-provider recording family from tests/scripts/test_refresh_samples.py:1055 onward to tests/scripts/test_record_ml_corpus.py — the corpus recorder's provider refusal is a preflight `if`, so the family needs one seam (an AILIBI_* test-provider allowance behind the same guard refresh_samples uses, or a stubbed `run_tournament.py` on PATH). Assert the four function names off a `bash -x` trace the same way, and add a two-worker contention case that would have caught the single-poll abort.

## B-22 — Task 16.7's `:whereabouts:` event-id segment was taught to one contradiction helper and not its sibling — the roll-call half of 31/164 served flags renders with no badge and no accent

**Severity:** P2 (finder: P1). **Classification:** defect (re-report of open C-120). **Verdict:** ADJUSTED. **Area:** api-frontend / frontend/src/lib/contradictions.ts + frontend/src/components/TurnCard.tsx (meeting rendering / backend-id mirroring, C-80 class). **Confidence:** high.
**Merged from:** finder-api-frontend.json#1.

**Claim.** STILL OPEN: C-120 (audits/review-2026-08-19/B/collated-findings.md:185, P2) -- `frontend/src/lib/contradictions.ts` still knows only `:claim:` and `:obs:`, so a contradiction endpoint landing on a Task-16.7 `WhereaboutsClaim` observation is unmatchable and its badge never renders on the contradicted account's own line. Current served numbers (recomputed at HEAD after the baseline-7 re-record, so they supersede C-120's 61/404): 31 of 164 committed `replays/samples` contradictions (18.9%) carry a whereabouts endpoint, all 31 half-linked, spread over 7 turns whose ONLY endpoint is a whereabouts id. The accent half is narrower than stated: under Task 19.11's taxonomy (TurnCard.tsx:315-325) only `role_proof` and `cross_statement` change the accent, and 5 of those 7 turns are `weak_signal` -- which already renders in the speaker identity colour whether or not the flag matches. So exactly 2 turns (seed-32 meeting-0 turn-3, seed-33 meeting-1 turn-3) lose a real fuchsia contradiction accent; the other 5 lose only their badges and flag count. The transcript.py:2259-2262 docstring half of C-120 is also still wrong (it says the synthesized whereabouts alibi's event id is `_turn_observation_id`; the code at :2294 uses `_turn_whereabouts_id`).

**As originally filed.** `lib/contradictions.ts` builds per-observation contradiction event ids as `turn:<id>:obs:<i>` for EVERY observation, but the backend mints `turn:<id>:whereabouts:<i>` for a `WhereaboutsClaim` observation, so every contradiction endpoint that lands on a roll-call self-placement is unmatchable — the badge is missing on the contradicted account's own line, and a turn flagged ONLY through a whereabouts endpoint also loses its contradiction accent and renders as a clean card in the speaker's identity colour.

**Finder evidence.**

```
BACKEND MINTS THREE SEGMENTS. `sed -n 4062,4080p meetings/transcript.py` -> meetings/transcript.py:4065 `def _turn_claim_id(...): return f"turn:{turn.turn_id}:claim:{index}"`; :4069 `_turn_observation_id -> f"turn:{turn.turn_id}:obs:{index}"`; :4073 `_turn_whereabouts_id -> f"turn:{turn.turn_id}:whereabouts:{index}"` with the comment "Task 16.7: a whereabouts self-placement ... gets its OWN segment (not ``:obs:``)". meetings/transcript.py:3750-3753 confirms the per-observation-index branch is exclusive (`if isinstance(observation, WhereaboutsClaim): index[_turn_whereabouts_id(...)] else: index[_turn_observation_id(...)]`).

FRONTEND KNOWS ONLY TWO. frontend/src/lib/contradictions.ts:12-18 — `turnClaimEventId` returns `turn:${turn.turn_id}:claim:${index}`, `turnObsEventId` returns `turn:${turn.turn_id}:obs:${index}`; no whereabouts form exists. frontend/src/components/TurnCard.tsx:292-298 maps EVERY observation through `turnObsEventId(turn, index)`:
```
const observations = turn.observations.map((obs, index) => ({
  obs,
  contras: findContradictions(turnObsEventId(turn, index), contradictions),
}));
```
`ObservationClaimView` includes `WhereaboutsClaimView` (frontend/src/types/api.ts:747; api/schemas.py:563-577, :599-604), so a whereabouts observation at index i yields the dead id `turn:X:obs:i` while the flag references `turn:X:whereabouts:i`.

THE FIX WAS ALREADY APPLIED NEXT DOOR. frontend/src/components/MeetingView.tsx:312-324 documents this exact class and fixes it in the sibling helper: "`whereabouts` is Task 16.7's roll-call self-placement segment, added to the meeting layer after this helper was written and never taught to it" — `eventTurnId` matches `/^turn:(.+):(?:claim|obs|whereabouts):\d+$/`. `lib/contradictions.ts` was not updated in the same pass.

SERVED-PAYLOAD IMPACT (committed spectator sets, `replays/samples/{4p1i,9p2i}`):
`uv run python` over the committed bytes -> `served sets: contradictions 164 with a whereabouts endpoint 31 18.9 %` / `Counter({'alibi_conflict': 21, 'alibi_vs_sighting': 8, 'alibi_vs_physical': 2})`; all 31 are half-linked (`both endpoints whereabouts (fully invisible): 0`, `exactly one endpoint whereabouts (half-linked): 31`). Per-turn: `turns with >=1 endpoint: 158  only-whereabouts turns: 7`, all in the DEFAULT-served 9p2i set — e.g. `replays/samples/9p2i/replay-seed-1.jsonl` turns `headless-seed-1:meeting-0:turn-4` and `:turn-6`, plus seeds 32, 33, 36, 44, 46.

CONFIRMED THROUGH THE REAL LOADER (not raw bytes): `uv run python -c` with `ReplayLoader(replay_dir=Path('replays/samples/9p2i')).load_replay('headless-seed-1')` prints
```
headless-seed-1:meeting-0 | turn:headless-seed-1:meeting-0:turn-2:obs:1 | turn:headless-seed-1:meeting-0:turn-4:whereabouts:0 | weak_signal
  turn headless-seed-1:meeting-0:turn-4 ['whereabouts', 'saw_player']
```
so `TurnView.observations[0].type == "whereabouts"` and the frontend computes `turn:...:turn-4:obs:0` — a phantom id.

ACCENT CONSEQUENCE: frontend/src/components/TurnCard.tsx:299-302 builds `flagged` from `observations.flatMap(o => o.contras)` + claims, and :321-325 derives the card's left accent from `flagged[0]?.category`, falling back to `playerColor(turn.speaker, players)`. A turn whose only endpoint is a whereabouts id therefore renders with zero flags and the neutral identity accent.

NO TEST GUARDS IT: `find frontend/src -name '*.test.ts*'` lists 8 files, none for `lib/contradictions.ts`; `grep -rn 'contradiction' frontend/e2e/*.ts` prints nothing.
```

**Verifier evidence (independent re-run).**

```
(1) Backend three-segment mint reproduces: meetings/transcript.py:4065 `_turn_claim_id`, :4069 `_turn_observation_id`, :4073 `_turn_whereabouts_id` with the Task-16.7 comment; the exclusive branch at :3746-3753 (`if isinstance(observation, WhereaboutsClaim): index[_turn_whereabouts_id(...)] else: index[_turn_observation_id(...)]`).

(2) Frontend two-segment helper reproduces: frontend/src/lib/contradictions.ts:12-18 exports only turnClaimEventId / turnObsEventId; `grep -rn 'turnObsEventId|turnClaimEventId|turnWhereabouts' frontend/src` returns 6 hits, no whereabouts form anywhere. TurnCard.tsx:291-294 maps EVERY observation through turnObsEventId. WhereaboutsClaimView is in ObservationClaimView (api/schemas.py:563-577, :599-604; frontend/src/types/api.ts:282).

(3) The sibling fix reproduces: MeetingView.tsx:312-323 carries the comment naming the exact class and the three-segment regex `/^turn:(.+):(?:claim|obs|whereabouts):\d+$/`.

(4) My own served-payload census over the committed bytes (script scratchpad/v4_b22.py, 100 files under replays/samples/*) reproduces the finding's numbers EXACTLY: `files 100 | total contradictions 164 | with a whereabouts endpoint 31 18.9 % | kinds {'alibi_vs_sighting': 8, 'alibi_conflict': 21, 'alibi_vs_physical': 2} | both whereabouts (fully invisible) 0 | exactly one (half-linked) 31 | turns with >=1 endpoint 158 | only-whereabouts turns 7`, and the same 7 turn ids (9p2i seeds 1 x2, 32, 33, 36, 44, 46).

(5) Through the REAL loader (scratchpad/v4_b22b.py, ReplayLoader on replays/samples/9p2i): `headless-seed-1:meeting-0 | turn:...:turn-2:obs:1 | turn:...:turn-4:whereabouts:0 | weak_signal | alibi_vs_sighting` and ` turn headless-seed-1:meeting-0:turn-4 ['whereabouts', 'saw_player']` -- observations[0].type == 'whereabouts', so the frontend computes the phantom `turn:...:turn-4:obs:0`. Confirmed.

(6) WHERE I DIVERGE. Loader-resolved categories over all served sets (scratchpad/v4_b22c.py): `ALL whereabouts endpoints, categories: {'weak_signal': 29, 'cross_statement': 2}` and `categories on only-whereabouts turns: {'weak_signal': 5, 'cross_statement': 2}`. TurnCard.tsx:315-325 (Task 19.11) is a THREE-way accent: role_proof -> tokens.ink[900], cross_statement -> tokens.contradiction, ELSE playerColor. A weak_signal flag therefore paints the identity colour even when it DOES match, so 5 of the 7 turns suffer no accent change at all -- only 2 do. The finding's accent sentence overstates by 3.5x.

(7) RE-REPORT. `grep -rn 'contradictions.ts' audits/` -> audits/review-2026-08-19/B/collated-findings.md:185 C-120, P2: 'The whereabouts-id docstring error has a live frontend consequence ... `lib/contradictions.ts:12-18` never resolves a badge for whereabouts-anchored observations ... `MeetingView.tsx:315` was patched, `lib/contradictions.ts` was not'. Same defect, same two files, same diagnosis, plus the same fix (audits/review-2026-08-19/B/meetings-transcript-voting.md:133 already prescribes `turnWhereaboutsEventId` + the docstring fix + a cross-layer test). C-120 falls in the phase-20 close's 'roughly 94 P2 code findings' backlog (audits/audit-phase-20-close.md:399) and is verifiably still open. I confirmed the docstring half too: meetings/transcript.py:2259-2262 still names `_turn_observation_id` while :2294 uses `_turn_whereabouts_id`.

(8) 'No test guards it' reproduces: `find frontend/src -name '*.test.ts*'` -> 8 files, none for lib/contradictions.ts; `grep -rn 'contradiction' frontend/e2e/*.ts` -> nothing.
```

**Verifier note.** Every code and payload fact reproduces exactly, including the 164/31/18.9%/0-both/31-half/158/7 census and the same seven turn ids. Two corrections. (a) It is a re-report: C-120 (P2) names this defect, these two files and this fix; it is still open, so this should be filed as 'C-120 still open, with current-corpus numbers' rather than as new. C-120's own 61/404 figure is stale -- the corpus was re-recorded since -- so the 31/164 measurement is a genuine refresh. (b) Severity P1 -> P2, matching C-120's triage and the actual scope: display-only, the flag still renders in MeetingView's EvidenceSection, and the accent consequence covers 2 turns not 7 because Task 19.11 already paints weak_signal in the identity colour. The badge-loss half (31 lines) is fully confirmed.

**Fix sketch.** Add `turnWhereaboutsEventId(turn, index)` to frontend/src/lib/contradictions.ts and, in TurnCard.tsx:292-295, dispatch on the discriminant: `obs.type === "whereabouts" ? turnWhereaboutsEventId(turn, index) : turnObsEventId(turn, index)`. Better: export ONE `observationEventId(turn, obs, index)` from lib/ so the three-segment rule lives in a single place, have MeetingView.tsx's `eventTurnId` regex derive from the same segment list, and add a vitest that walks a committed served payload (the pattern `frontend/src/lib/bodies.test.ts` already uses with `bodies.fixture.json`) asserting every `ContradictionView` endpoint in the fixture resolves to exactly one rendered line.

## B-23 — A substrate-mismatched replay is invisible to every collection view — listed by the picker and counted in the served cost/decisive aggregate — and fails only when opened

**Severity:** P2 (finder: P1). **Classification:** defect (listing half only; scoped). **Verdict:** ADJUSTED. **Area:** api-frontend / api/replay_loader.py (list_replays / cost_summary containment vs. the Task-14.7 substrate guard). **Confidence:** high.
**Merged from:** finder-api-frontend.json#2.

**Claim.** `_assert_substrate_matches` runs only inside `_walk`, so a replay stamped with a substrate this build cannot reproduce is advertised by `GET /replays` as an ordinary openable game while `GET /replays/{id}` 500s -- the skip-and-log containment `list_replays` documents for the three corrupt/empty classes does not extend to the substrate class. That listing half is the defect. The `cost-summary` half should be dropped from the claim: `_ReplaySummary` (api/replay_loader.py:667-694) is a pure reduction of RECORDED bytes -- cost, winner, tick and meeting counts -- none of which depends on reconstruction, so a substrate-mismatched replay's contribution to `total_replays` and `decisive_split` is real recorded data and counting it is defensible rather than wrong. Severity P2, not P1: impact today is zero (I re-verified all 300 committed replay files stamp identically to the build snapshot), the trigger state is a transitional mixed-substrate directory that does not exist in the repo, and the 500 itself is the Task-14.7 guard behaving as designed. Same open class as the already-routed `eval/replay_walk.py` substrate gap (audits/audit-phase-20-close.md:408), which names the identical one-line predicate this fix sketch names.

**As originally filed.** `_assert_substrate_matches` runs only inside `_walk`, so a replay stamped with a substrate this build cannot reproduce is advertised by `GET /replays` as an ordinary openable game and is folded into `GET /eval/cost-summary`'s `total_replays` and `decisive_split`, while `GET /replays/{id}` 500s — the skip-and-log containment the collection views document for corrupt/empty files does not extend to the substrate class.

**Finder evidence.**

```
CODE. api/replay_loader.py:1101-1103 places the guard inside `_walk` only. api/replay_loader.py:753-785 `list_replays` catches `(ReplayLog.CorruptedFileError, ValueError)` and its docstring names exactly three contained classes ("the doubled-write ... any unparseable or schema-invalid row ... and EmptyReplayError"); `ReplaySubstrateMismatchError` subclasses `RuntimeError` (api/replay_loader.py:354) and is not among them — but it never reaches the listing anyway, because `list_replays`/`cost_summary` reduce via `_metadata_view`/`_file_summary`, which read entries and never walk. api/replay_loader.py:806-844 `cost_summary` uses the same `(CorruptedFileError, ValueError)` filter.

REPRODUCED. Built a mixed-substrate set under the scratchpad: `replay-seed-0.jsonl` copied verbatim from `replays/samples/9p2i`, `replay-seed-1.jsonl` copied with one retired lever flipped in its `game_over` stamp (`substrate_flags['testimony_as_content'] = False`), plus the set's `roster.json`/`MANIFEST.md`. Then via `fastapi.testclient.TestClient(create_app(replay_dir=...), raise_server_exceptions=False)`:
```
GET /replays -> 200 ['headless-seed-0', 'headless-seed-1']
GET /eval/cost-summary -> 200 {"total_replays":2,...,"decisive_split":{"CREWMATES":1.0,"IMPOSTORS":0.0}}
GET /replays/headless-seed-1 -> 500 Internal Server Error
```
The unreconstructable seed is listed, is one of the two replays the mean is divided by, and contributes its winner to the served crew/impostor split.

WHY IT MATTERS FOR THE RE-GROUND. A piecemeal re-record is exactly a transitional mixed-substrate directory — the committed 9p2i already carries three distinct recording shas (tests/api/test_sets.py:352-361, `test_committed_9p2i_manifest_is_mixed_provenance`). Today's corpus is clean: over all 300 committed files (`replays/samples/*/*.jsonl` + `replays/ml_corpus/**/*.jsonl`) a diff of each stamp against `orchestrator.replay.substrate_flag_snapshot()` gives `files 300` / `300 ((), ())` — zero differing keys, zero extra keys. So this is a guard-shape gap, not a live corruption.

USER-VISIBLE PATH. frontend/src/store/replayStore.ts:433-435 turns the 500 into `replayLoadError: errorMessage(error)`, i.e. the raw `API request to /api/replays/headless-seed-1 failed (status 500): Internal Server Error` — see the sibling finding on the opaque body.
```

**Verifier evidence (independent re-run).**

```
(1) Code reproduces. api/replay_loader.py:1101-1103 places `_assert_substrate_matches` inside `_walk` only. :753-785 `list_replays` catches `(ReplayLog.CorruptedFileError, ValueError)` and its docstring names exactly three contained classes ('the doubled-write ... any unparseable or schema-invalid row ... and EmptyReplayError'). :806-825 `cost_summary` uses the same two-class filter. `ReplaySubstrateMismatchError(RuntimeError)` at :354 is in neither tuple.

(2) REPRODUCED END TO END, independently (scratchpad/v4_b23.py). Built `<scratch>/v4mix/9p2i/` with replay-seed-0.jsonl + roster.json + MANIFEST.md copied verbatim from replays/samples/9p2i, and replay-seed-1.jsonl rewritten with `substrate_flags['testimony_as_content'] = False` on its game_over stamp. Through `fastapi.testclient.TestClient(create_app(replay_dir=<parent>), raise_server_exceptions=False)`:
    GET /replays              -> 200 ['headless-seed-0', 'headless-seed-1']
    GET /eval/cost-summary    -> 200 {"total_replays":2,...,"decisive_split":{"CREWMATES":1.0,"IMPOSTORS":0.0}}
    GET /replays/headless-seed-1 -> 500 Internal Server Error
    GET /replays/headless-seed-0 -> 200 (opens normally)
Identical to the finding's transcript.

(3) 'Corpus is clean today' reproduces (scratchpad/v4_b23b.py): over all 300 committed files (replays/samples/*/*.jsonl + replays/ml_corpus/**/*.jsonl), diffing each recorded stamp against `orchestrator.replay.substrate_flag_snapshot()` gives `files 300` / `300 ((), ())` -- zero differing keys, zero extra keys. So live impact is nil.

(4) Frontend consequence reproduces: frontend/src/store/replayStore.ts:432-435 sets `replayLoadError: errorMessage(error)` on the 500.

(5) WHERE I DIVERGE. api/replay_loader.py:667-694 `_ReplaySummary` holds total_ticks, meeting_count, winner, winner_reason, final_tick, total_cost_usd, prompt_versions -- built from one `read_all_entries`, with NO engine playback and NO memory reconstruction. Every field is a recorded fact. A substrate-mismatched replay is a game that really happened, really cost that much and really ended that way; only its MEMORY RECONSTRUCTION is impossible under this build. Calling its inclusion in `total_replays`/`decisive_split` a defect (and the docstring's 'a mean over real games' a violation) does not follow -- it IS a real game. The defensible half is narrower: the picker advertises an entry that cannot be opened.

(6) Not a re-report of the enumerated set, and distinct from its two nearest neighbours: C-5 (P1, 'Corrupt replay files 500 the listing and cost endpoints', collated-findings.md:29) is the SAME SHAPE but was FIXED -- the ValueError catch is now present at :783 and :824; C-121 (collated-findings.md:186) is the opaque-HTTP-body sibling, a different defect. It IS however the same open class as the routed `eval/replay_walk.py performs no substrate check` item (audits/audit-phase-20-close.md:408), which prescribes the same `orchestrator.replay.retired_levers_stamped_off` predicate this fix sketch names -- different module, same gap, and worth folding into that item rather than opening a second one.

(7) No task contract or DESIGN.md text declares the substrate class a deliberate exclusion from the collection views; the docstring simply enumerates three classes without addressing a fourth. So it is a genuine guard-shape gap, not a declared carry.
```

**Verifier note.** The repro is exact -- I rebuilt the mixed-substrate set from scratch and got the same 200/200/500 triple -- and the '300/300 clean' counter-evidence checks out. Two corrections. (a) Drop the cost-summary half: `_ReplaySummary` reduces only recorded bytes (cost, winner, ticks), none reconstruction-dependent, so aggregating a substrate-mismatched game is arguably CORRECT, not a defect; the real gap is that the picker lists a game that 500s when opened. (b) P1 -> P2: zero live impact (verified over all 300 committed files), the trigger is a transitional directory that does not exist, and the 500 is the Task-14.7 guard working as designed. Also flag it as the same open class as the already-routed replay_walk substrate gap (close audit line 408), which names the identical fix predicate.

**Fix sketch.** Read the stamp in the cheap summary pass (`_recorded_substrate_flags` already works off loaded entries) and make it a first-class collection-view outcome: either (a) drop-and-log a substrate-mismatched file the way the three corrupt classes are dropped, so the picker never advertises a game that cannot open and the aggregate counts only reconstructable games; or (b) keep listing it but carry an explicit `substrate_mismatch` field on `ReplayMetadataView` so the picker can render it disabled with a reason, and exclude it from `cost_summary`'s `total_replays`/`decisive_split`. `orchestrator.replay.retired_levers_stamped_off` is the ready-made predicate for the retired half.

## B-24 — The `lights` sabotage is strictly self-harming for impostors: it costs the crew nothing and blinds only the impostor

**Severity:** P2. **Classification:** design-limitation (re-report of open V14, with a new ML-action-space consequence). **Verdict:** ADJUSTED. **Area:** engine-core / visibility + sabotage mechanics. **Confidence:** high.
**Merged from:** finder-engine-core.json#3.

**Claim.** STILL OPEN: V14 (audits/review-2026-08-19/A/ideas-among-us-veteran.md:494-520, rank 14, 'Make the lights sabotage worth pressing') -- as shipped, `lights` is a self-harm button: the Task-13.8 asymmetry already floors crewmates at `same_room_only`, so an active lights sabotage costs the crew nothing and strips the impostor from 4 visible rooms to 1. Everything up to that point is a re-report; V14 states it in those words. The NEW increment this finding adds, and the reason it matters for the re-ground, is the ML action space: `training/env.py:344-353` marks EVERY map sabotage kind legal for an impostor over `sabotage_kinds = ('lights','reactor')`, so a learned/ES/MAP-Elites impostor will spend search capacity on a strictly-dominated arm, and any fitted advantage attributed to `sabotage` will in fact be a `reactor`-only effect. Note also that the mechanism is SPECIFIED, not accidental: tasks/phase-13.md:394-433 (Task 13.8) explicitly requires that 'an ACTIVE sabotage degrade ... still degrades EVERYONE' and that the map base stay `same_room_and_adjacent` 'so the lights sabotage + the default stay intact'. What is unacknowledged is the consequence -- that a degrade to a floor the crew already occupies is not a degrade at all.

**As originally filed.** Since the Task 13.8 asymmetric-visibility rule (engine/visibility.py:124-127) downgrades crewmates to `same_room_only` at BASE visibility, and `lights.affected_visibility` is also `same_room_only`, an active lights sabotage leaves crew sight unchanged while stripping the impostor from 4 visible rooms to 1 — a dominated action that is nonetheless marked engine-legal for a learned policy.

**Finder evidence.**

```
engine/visibility.py:124-127:
```
    mode = resolve_visibility_mode(world_state, game_map)
    if mode == game_map.visibility_defaults.base and observer.role != "IMPOSTOR":
        return "same_room_only"
    return mode
```
engine/maps/canonical_1.yaml:55-57 `base: same_room_and_adjacent`; :387-388 `lights: affected_visibility: same_room_only`; :394-396 `reactor: affected_visibility: same_room_and_adjacent`.

PROBE (`compute_visibility_for_player`, one crewmate + one impostor in CAFETERIA):
```
none     crew rooms=1 ('CAFETERIA',)  impostor rooms=4 ('CAFETERIA','EAST_HALL','UPPER_HALL','WEST_HALL')
lights   crew rooms=1 ('CAFETERIA',)  impostor rooms=1 ('CAFETERIA',)
reactor  crew rooms=1 ('CAFETERIA',)  impostor rooms=4 ('CAFETERIA','EAST_HALL','UPPER_HALL','WEST_HALL')
```
Lights: crew loses 0 rooms, impostor loses 3. `reactor` (the gating one) leaves both unchanged, so `lights` is the only visibility sabotage and it points the wrong way.

IT IS IN THE ML ACTION SPACE. training/env.py:344-353 marks EVERY map sabotage kind legal for an impostor:
```
    if role == "IMPOSTOR":
        for kind in sabotage_kinds:
            add(SabotageIntent...(kind), legal=(not in_vent) and not sabotage_active)
```
with `sabotage_kinds = tuple(sorted(self._game_map.sabotages))` (training/env.py:658-659) = `('lights', 'reactor')`.

THE SHIPPED FSM NEVER USES IT, so the corpus carries no counter-evidence: scanning every sabotage action in `replays/ml_corpus/*`: `Counter({'reactor': 26})` — 0 lights across 200 games. A learned/ES/MAP-Elites impostor exploring the mask therefore burns search capacity on a strictly-dominated arm whose only effect is to handicap itself, and any fitted advantage for `sabotage` will be a `reactor`-only effect mislabelled as a sabotage effect.
```

**Verifier evidence (independent re-run).**

```
(1) Code reproduces. engine/visibility.py:124-127 is verbatim as quoted. engine/maps/canonical_1.yaml:55-57 `base: same_room_and_adjacent`; :387-388 `lights: affected_visibility: same_room_only`; :394-396 `reactor: affected_visibility: same_room_and_adjacent`.

(2) MY OWN PROBE (scratchpad/v4_b24.py -- built a WorldState with one CREWMATE and one IMPOSTOR both in CAFETERIA, ran `resolve_visibility_mode` + `compute_visibility_for_player`):
    base same_room_and_adjacent | sabotages {'lights': 'same_room_only', 'reactor': 'same_room_and_adjacent'}
    None     mode=same_room_and_adjacent  crew rooms=1 ('CAFETERIA',)  impostor rooms=4 ('CAFETERIA','EAST_HALL','UPPER_HALL','WEST_HALL')
    lights   mode=same_room_only          crew rooms=1 ('CAFETERIA',)  impostor rooms=1 ('CAFETERIA',)
    reactor  mode=same_room_and_adjacent  crew rooms=1 ('CAFETERIA',)  impostor rooms=4 (...)
Identical to the finding. Crew loses 0 rooms; impostor loses 3.

(3) STRENGTHENED -- lights costs the crew zero TIME as well as zero sight. agents/tactical/crewmate_policy.py:25-26 and :507-518: the repair diversion is scoped to `sabotage_is_gating`, so 'a non-gating `lights` sabotage leaves crew behavior byte-identical to the pre-11.6 FSM'. The crew never even walks to ADMIN. And agents/tactical/impostor_policy.py:449 emits only `_REACTOR_SABOTAGE_KIND`, so the shipped FSM cannot generate counter-evidence.

(4) ML action space reproduces: training/env.py:347-353 adds a SabotageIntent for every kind in `sabotage_kinds`, and :658-659 defines `sabotage_kinds = tuple(sorted(self._game_map.sabotages))` = ('lights','reactor').

(5) MY OWN CORPUS SCAN (scratchpad/v4_b24b.py, every `type: sabotage` action in the recorded bytes): `corpus games 200 sabotage actions {'reactor': 26}` and `samples games 100 sabotage actions {'reactor': 5}`. Zero `lights` across all 300 committed games -- the finding's 26/0 for ml_corpus reproduces exactly.

(6) SPECIFIED. tasks/phase-13.md:394-433 (Task 13.8) puts BOTH halves in the contract: 'engine/maps/canonical_1.yaml -- the BASE stays `same_room_and_adjacent` ... (so the lights sabotage + the default stay intact)'; 'an ACTIVE sabotage degrade (mode != base, e.g. lights -> `same_room_only`) still degrades EVERYONE'; and the implementation hint 'otherwise keep the resolved mode (so an active lights degrade still hits the impostor too)'. The DoD requires exactly the shipped behaviour. So the code matches its contract precisely -- design-limitation is the right class, not defect.

(7) RE-REPORT. audits/review-2026-08-19/A/ideas-among-us-veteran.md:494-520 V14: 'As shipped it is a self-harm button. ... crew are already downgraded to `same_room_only` by the Task-13.8 asymmetry, while `lights` "still degrades EVERYONE, the impostor included" (the code's own docstring). So pressing it costs the impostor its adjacent vision and costs the crew nothing. It is strictly negative-value, and the policy has correctly never touched it.' Backed by M8 (:83) '110 reactor, 0 lights -- the lights sabotage has never been used in 300 games'. V14's fix options are the finding's fix options. `grep -rn 'V14' audits/audit-phase-20-close.md tasks/phase-20.md` -> no hits, so it was never acted on and remains open. (My action-count 31 across 300 games differs from M8's 110, which appears to count sabotage EVENT rows rather than submitted actions; the 0-lights half agrees.)
```

**Verifier note.** Every measurement reproduces -- I re-ran the visibility probe and got the identical 1/4, 1/1, 1/4 table, and my own corpus scan gives 26 reactor / 0 lights over ml_corpus and 5 reactor / 0 lights over samples. I also strengthened it: lights costs the crew zero task-clock time too, because crewmate_policy.py:507-518 scopes the repair diversion to gating sabotages only. Two corrections. (a) It is a re-report of V14 (rank 14, still open, never referenced in the phase-20 close or tasks/phase-20.md), which makes the self-harm argument in the same words off the same code lines; the genuinely new content is the training/env.py action-mask consequence for the re-ground, and that is what should be filed. (b) The mechanism is SPECIFIED by Task 13.8's contract (tasks/phase-13.md:394-433) down to the implementation hint, so design-limitation/P2 is right and no code-vs-contract defect exists -- what is unacknowledged is only the consequence, that degrading to a floor the crew already occupies is not a degrade.

**Fix sketch.** Decide explicitly before the re-ground rather than leaving it implicit. Either (a) give `lights` a crew-relevant degrade that survives the asymmetry — e.g. add a `blinds_impostor: bool` / per-role visibility field to `SabotageDefinition` so lights degrades the CREW below `same_room_only` (or suppresses body visibility) rather than only clipping the impostor; or (b) if lights is meant to stay a no-op, remove it from `build_action_mask`'s legal sabotage set (and say so in the map YAML) so the ML search does not spend capacity on a dominated arm. Either way add a unit test asserting the crew's visible-room count strictly shrinks under every sabotage marked as a visibility degrade.

## B-25 — The engine's passive task-continuation path is unreachable in every production and training loop — 0 events across the whole baseline-7 corpus

**Severity:** P2. **Classification:** quality-debt (spec-internal contradiction, not dead code). **Verdict:** ADJUSTED. **Area:** engine-core / task system. **Confidence:** high.
**Merged from:** finder-engine-core.json#4.

**Claim.** The engine's passive task-continuation path is unreachable in every production and training loop and fires 0 times corpus-wide -- all of which reproduces. What must change is the framing and the remedy: `_advance_tasks` is NOT stray dead code, it is a DESIGN.md-specified rule. DESIGN.md:268 (S3.1 'Single tick', step 2) reads 'Resolve passive effects: kill cooldown decrement, sabotage timer countdown, task progress on continuing tasks.' The six unit tests therefore pin a documented design rule, not an accidental branch, and the fix sketch's preferred branch ('delete `_advance_tasks` ... its six tests go with it') would silently drop a published spec clause. The real finding is an internal DESIGN.md contradiction: step 2 promises passive continuation while steps 1/4/5 of the same section promise exactly one submitted action per living agent per tick, and the shipped orchestrator honours the latter -- so step 2's rule can never fire. The remedy is therefore the finding's SECOND branch (assert in `_run_loop` that `{a.actor for a in actions}` equals the alive set, so a future partial-dispatch mover fails loudly), plus a DESIGN.md amendment if the rule is to be removed. Severity P2 and the quality-debt classification stand.

**As originally filed.** `_advance_tasks` (engine/tick.py:141-198) only advances an actor NOT in `submitted_actors`, but `orchestrator/game.py:_build_packets`/`_collect_intents` produce exactly one intent per ALIVE player every tick, so the set always covers every actor who could continue a task; re-walking all 200 corpus games it fired 0 times in 3,766 calls.

**Finder evidence.**

```
engine/tick.py:157-159:
```
    for player_id in sorted(state.players):
        if player_id in submitted_actors:
            continue
```
and `submitted_actors = {action.actor for action in actions}` (engine/tick.py:590).

Production always fills that set: orchestrator/game.py:2091-2100 builds one packet per alive player, orchestrator/game.py:2128-2137 returns one intent per packet, and `translate_action_intents_for_tick` is 1:1. Dead players have `last_action=None` (cleared in `_apply_kill`, engine/tick.py:382, and in `apply_meeting_result`, orchestrator/game.py:1286), so they `continue` too.

MEASURED over the corpus (monkeypatched counter around `engine.tick._advance_tasks` while re-walking all 200 games through `advance_tick` + `apply_meeting_result`):
```
tick rows walked: 4242   rows where an ALIVE player submitted no action: 0
_advance_tasks stats: {'calls': 3766, 'nonempty': 0, 'events': 0, 'gated': 74}
```
Zero `TaskProgressed`/`TaskCompleted` events from the continuation path; every task tick in the corpus came from an explicit `do_task` through `_apply_do_task`.

Six unit tests pin the dead path anyway (tests/engine/test_tick.py:149, :184, :211, :238, :274, :697), all by hand-building batches that omit an actor — a shape the loop cannot produce. So the tests read green while the behaviour is unreachable.

WHY IT MATTERS FOR THE RE-GROUND: it is a live trap, not just dead weight. Any re-ground-era mover that stops submitting for some seat on some tick (a masked no-op that returns nothing rather than a `wait` intent, a batched/partial dispatch, a subset-rollout env) instantly switches on free crew task progress and shifts the whole crew task clock — silently, with no flag and no gate, because nothing asserts the coupling.
```

**Verifier evidence (independent re-run).**

```
(1) Code reproduces verbatim. engine/tick.py:157-159 is the `if player_id in submitted_actors: continue` skip; :590 `submitted_actors = {action.actor for action in actions}`. The gating early-return is at :151-153.

(2) Production coupling reproduces. orchestrator/game.py:2090-2100 `_build_packets` builds one packet per player where `alive`; :2128-2138 `_collect_intents` returns exactly one intent per packet and raises if an agent acts as anyone else. Dead players are cleared: engine/tick.py:382 `replace(target, alive=False, last_action=None)` in `_apply_kill`, and orchestrator/game.py:1286 the same in the ejection path.

(3) Training loops too. training/env.py:711/:753 drives `HeadlessGame.run_unrecorded` -- the real production loop -- so its batches are full. training/rollout.py:547-550 and training/anchor_study.py:562 replay RECORDED action batches, which are also full.

(4) MY OWN STATIC CENSUS over all 300 committed replay files (scratchpad/v4_b25a.py): for every tick row I took the actor set, and looked for any actor absent at tick t but present at some later tick t' > t -- the exact signature of a live player skipping a submission. Result: `files 300 tick rows 5960 | submission gaps (actor absent at t but present at some t'>t): 0`. Zero, corpus-wide.

(5) MY OWN INSTRUMENTED WALK (scratchpad/v4_b25c.py -- monkeypatched `engine.tick._advance_tasks`, then replayed 20 ml_corpus games through `ReplayLoader.load_replay`, which does full engine playback): `games walked 20 {'calls': 289, 'nonempty_skipset': 0, 'events': 0, 'gated': 3}`. Zero calls where an alive player was missing from `submitted_actors`; zero TaskProgressed/TaskCompleted events from the continuation path.

(6) The finding's own tick-row count checks out: `ml_corpus 200 files 4242 tick rows` (scratchpad/v4_b25b.py) matches its 'tick rows walked: 4242' exactly.

(7) All six test line numbers are exact: tests/engine/test_tick.py:149 test_continuing_task_progresses_without_repeated_action, :184 ..._completes_and_can_trigger_crew_win, :211 test_submitted_wait_suppresses..., :238 test_submitted_move_suppresses..., :274 test_rejected_action_suppresses..., :697 test_gating_sabotage_suppresses_task_continuation.

(8) WHERE I DIVERGE -- the SPECIFIED check the finding did not run. DESIGN.md:268 (S3.1, step 2): 'Resolve passive effects: kill cooldown decrement, sabotage timer countdown, **task progress on continuing tasks**.' The behaviour is published design. And DESIGN.md:266 (step 1) plus :271 (step 4, 'for each living agent') plus :272 (step 5, 'validates one intent per actor') publish the coupling that makes it unreachable. So the same section specifies both halves of the contradiction, and 'delete it, the corpus proves this is byte-neutral' would remove a spec clause without touching the spec. tests/engine/test_tick.py:697's own comment cites 'DESIGN.md S3.1, S8.3' for the rule it pins.

(9) Not a re-report: absent from the enumerated known-open set and from collated-findings.md. audits/review-2026-08-19/B/engine.md:73 mentions `_advance_tasks` only for one defensive `raise` at tick.py:174, and :104/:152 only for determinism ordering and cyclomatic complexity -- neither is this observation.
```

**Verifier note.** The measurement is solid and I reproduced it two independent ways: a static census over all 300 committed files (5960 tick rows, ZERO submission gaps) and an instrumented replay of 20 ml_corpus games (289 calls, 0 alive-player skips, 0 events). The 4242 ml_corpus tick-row count and all six test line numbers are exact. One correction, and it is the check the task asks for: the behaviour IS specified -- DESIGN.md:268 lists 'task progress on continuing tasks' as a passive effect of the tick loop -- so this is a spec-internal contradiction (step 2 vs steps 1/4/5 of the same section), not stray dead code, and the fix sketch's preferred 'delete it' branch would drop a published rule without amending DESIGN.md. Route the second branch instead: assert the alive-set/submitted-set equality in `_run_loop`, which also closes the forward-looking trap the finding correctly identifies for a re-ground-era partial-dispatch mover. Severity P2 and quality-debt stand.

**Fix sketch.** Pick one and make it explicit. Preferred: delete `_advance_tasks` and its `submitted_actors` plumbing and let `_apply_do_task` be the only task-progress path (its six tests become tests of an intentionally-removed rule and go with it) — the corpus proves this is byte-neutral. If the rule is meant to stay, add the missing invariant instead: assert in `_run_loop` that `{a.actor for a in actions}` equals the alive set, so the day a mover stops submitting is a loud failure rather than a silent clock change.

## B-26 — Every engine tick throws away ~17us re-seeding a `random.Random` from urandom that it immediately overwrites — a one-line, behaviour-identical 9% throughput win

**Severity:** P2. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** engine-core / determinism plumbing + rollout throughput. **Confidence:** high.
**Merged from:** finder-engine-core.json#5.

**Claim.** `EngineRng.from_state` constructs `random.Random()` (engine/rng.py:100 and :114) — which seeds from `os.urandom` at 17.1us — and then discards that seeding with `setstate`; `random.Random.__new__(random.Random)` costs 0.12us and produces provably identical draws, worth a measured 9.3% engine-throughput gain, on top of `_readonly_mapping` re-copying all five WorldState mappings on every `dataclasses.replace`.

**Finder evidence.**

```
engine/rng.py:99-102 and :113-116:
```
        payload = json.loads(state.decode("utf-8"))
        inner = random.Random()
        inner.setstate((payload["v"], tuple(payload["s"]), payload["g"]))
```
`advance_tick` calls it once per tick (engine/tick.py:648) and `apply_meeting_result` once per meeting (orchestrator/game.py:1351).

MICROBENCH (`timeit`, n=20000):
```
random.Random()           : 17.14 us
random.Random(0)          :  6.83 us
Random.__new__(Random)    :  0.12 us
EngineRng.from_state FULL : 66.06 us
EngineRng.from_state FAST : 30.48 us
snapshot FULL             : 40.20 us
snapshot FAST             : 13.06 us
__new__+setstate equivalent draws: True
```
The discarded seeding is 26% of the FULL restore and 56% of the TRAINING_FAST restore — i.e. the Task 15.8.1 fast path is now dominated by the waste it did not remove.

END-TO-END (re-walking the 9p2i corpus tick stream, actions pre-parsed so only the engine is timed; best of 3):
```
baseline                             289.1 ms for 1550 ticks  ->  186.5 us/tick
Random.__new__ instead of Random()   262.2 ms for 1550 ticks  ->  169.2 us/tick
```
= 9.3% off bare-engine cost, with the draw sequence unchanged (`__new__+setstate` equivalence proven above).

SECOND, SMALLER ITEM. engine/world.py:81-84:
```
def _readonly_mapping(source):
    return MappingProxyType(dict(source))
```
`WorldState.__post_init__` (engine/world.py:71-78) re-wraps ALL FIVE mappings on every construction, and `dataclasses.replace` is called ~19x per tick. cProfile over the corpus re-walk:
```
69659 calls  0.216 tottime / 0.471 cumtime  dataclasses.py:1455(replace)
144175 calls 0.054 tottime                  engine/world.py:81(_readonly_mapping)
  3713 calls 0.044 tottime / 1.179 cumtime  engine/tick.py:565(advance_tick)
```
`replace` is 40% of engine cumtime. Returning the existing proxy unchanged when the source is already a `MappingProxyType` (safe: the wrapped dict is created inside `_readonly_mapping` and is unreachable, and every mutation path already does `dict(state.X)` first) measures:
```
replace(WorldState) as-is       : 3.81 us
replace(WorldState) proxy-reuse : 2.35 us  (38% faster)
```
```

**Verifier evidence (independent re-run).**

```
CODE ANCHORS EXACT. engine/rng.py:100 and :114 both `inner = random.Random()` immediately followed by `inner.setstate(...)`; engine/tick.py:648 `rng = EngineRng.from_state(state.rng_state)` once per tick; engine/world.py:71-78 __post_init__ wraps all FIVE mappings via :81-84 `_readonly_mapping` = `MappingProxyType(dict(source))`.

MY MICROBENCH (timeit n=20000, uv run, py3.11.15): random.Random() 17.99us (claim 17.14); random.Random(0) 6.98us (claim 6.83); Random.__new__(Random) 0.118us (claim 0.12); from_state FULL 58.47us (claim 66.06); from_state FAST 27.34us (claim 30.48); snapshot FULL 37.51us (claim 40.20); snapshot FAST 15.33us (claim 13.06). Discarded seeding = 31% of FULL restore / 66% of FAST restore (claim 26%/56%) -- my ratios are LARGER, so the claim is conservative.

EQUIVALENCE PROVEN: same getstate tuple into `random.Random()+setstate` vs `Random.__new__(Random)+setstate` -> 1000 randint draws identical AND getstate() equal after the 1000 draws. Mechanism confirmed: `_random.Random.getstate()` on a bare `__new__` object is all zeros ((0,0,0,...)), i.e. `__new__` does NOT seed; the 17.5us lives in `__init__ -> seed(None)`.

END-TO-END (my own harness, /private/tmp/.../wave0/B/b26_e2e.py: 60 corpus 9p2i replays walked via eval.replay_walk to collect (pre_state, parsed actions), then only advance_tick timed; interleaved A/B/A/B x4, min-of-4): 1507 ticks; baseline 318.0ms = 211.0us/tick, patched 253.6ms = 168.3us/tick -> 20.2% faster. A simpler best-of-3 run gave 154.8 -> 138.9us/tick = 10.2%. Both exceed the claimed 9.3%; the claimed 289.1ms/1550-tick baseline matches my 278.5ms/1507 ticks.

SECOND ITEM REPRODUCES: cProfile over the same 1507-tick re-walk: dataclasses.replace 27182 calls (18.0/tick; claim ~19/tick), 0.153s cumtime vs advance_tick 0.395s cumtime = 39% (claim 40%); engine/world.py:81 _readonly_mapping 55085 calls (36.6/tick). `replace(WorldState)` as-is 4.08us vs proxy-reuse short-circuit 2.42us = 41% faster (claim 38%).

FIX SAFETY VERIFIED BEYOND THE CLAIM: I monkeypatched engine.rng to use `Random.__new__` and re-walked 20 committed replays/ml_corpus/9p2i replays through eval.replay_walk with verify_tick_hashes + verify_meeting_pre_hashes + verify_meeting_post_hashes ALL ON: 20/20 clean, zero violations, identical to the baseline walk. The state_hash chain is provably untouched.

NOT A RE-REPORT: not among C-46/C-83/C-126/C-130/F1-F5/replay_walk/1440x900/alibi_vs_sighting/C-79/C-80/C-101/C-107/C-62/C-33/C-45. Nearest prior art is audits/review-2026-08-19/B/engine.md:41-42,157, which measured from_state FULL at 54.8us and observed the drawn value is unconsumed -- it never identifies the discarded urandom seeding nor the __new__ fix. NOT SPECIFIED: engine/rng.py:11-46 and engine/tick.py:640-649 make the rng_state SERIALIZATION load-bearing, never the construction of the throwaway generator.

SAFETY CHECK ON THE PROXY-REUSE HALF: `grep -rn MappingProxyType` shows no production path constructs a WorldState from a proxy over a dict the caller still holds (only training/coevo and tests, all `MappingProxyType(dict(...))`), so the short-circuit's stated safety argument holds.
```

**Verifier note.** Confirmed at full strength; every number reproduces and my end-to-end delta (10-20%) is at or above the claimed 9.3%. Two precision notes that do not change the verdict. (1) Cost attribution: the claim says random.Random() 'seeds from os.urandom at 17.1us', but os.urandom(32) is only 1.06us on this box -- the 17.5us is dominated by the 624-word Mersenne init_by_array inside seed(). Magnitude and conclusion are right; the named culprit is not. (2) A real gotcha the fix_sketch does not name: `random.Random.__new__(random.Random)` yields an object with NO `gauss_next` attribute, so `getstate()` on it raises AttributeError before any setstate. The substitution is safe here only because both call sites setstate immediately (setstate assigns gauss_next); the guard test in the fix sketch should include that, not just the 1000-draw equality. Also note the fix_sketch's 'multiplies straight into every rollout budget' is optimistic for RECORDED paths -- the prior review measured _state_hash at ~168us/tick, comparable to the tick itself, so recorded runs see roughly half the headline percentage. LLM-free ES/MAP-Elites rollouts do get the full gain.

**Fix sketch.** In `engine/rng.py`, replace both `random.Random()` calls with `random.Random.__new__(random.Random)` before `setstate` (the object is fully defined by `setstate`; nothing else on `Random.__init__` is used). Guard it with an equality test that a FULL-restored and a `__new__`-restored generator emit the same 1000 draws, and re-run the committed-replay state-hash gate to show the chain is untouched. Separately, add the `isinstance(source, MappingProxyType) -> return source` short-circuit in `engine/world.py::_readonly_mapping`. Both are behaviour-preserving and stack to roughly a 12-13% engine speedup, which multiplies straight into every ES / MAP-Elites / bakeoff rollout budget in the re-ground.

## B-27 — The engine property tests assert only totality — none of the invariants that would have caught the two P1 findings are property-tested

**Severity:** P2. **Classification:** enhancement (test-coverage), not quality-debt against a contract. **Verdict:** ADJUSTED. **Area:** engine-core / test coverage. **Confidence:** high.
**Merged from:** finder-engine-core.json#6.

**Claim.** tests/engine/test_tick_properties.py (243 lines) contains exactly three `@given` properties, all of which assert only totality plus structural well-formedness; both batch strategies feed a plain `_unique_actions_per_actor` de-dup rather than the production `orchestrator.action_ordering.order_actions_for_tick`, and both loops `break` on leaving PLAY, so the meeting-trigger tick is outside the explored space. Six named invariants (action conservation, win completeness, task-instance conservation, progress monotonicity, RNG lockstep, policy equivalence) are NOT PROPERTY-TESTED -- but several of them DO have example-based coverage elsewhere, and the narrow shape of the third property is the shape its own contract specified.

**As originally filed.** tests/engine/test_tick_properties.py contains three properties, all of the form "advance_tick does not raise and players stay in known rooms"; no property asserts action conservation, win-condition completeness, task-instance conservation, or replay/determinism equivalence, and the strategies never apply the production ordering.

**Finder evidence.**

```
tests/engine/test_tick_properties.py is 244 lines with exactly three `@given` properties:
- :108 `test_advance_tick_is_total_under_arbitrary_safe_actions` — asserts `phase in {PLAY, MEETING, GAME_OVER}`, `tick >= state.tick`, `set(players)` stable, `player.room in game_map.rooms` (tests/engine/test_tick_properties.py:125-132).
- :139 `test_empty_action_batch_advances_tick_without_crashing`.
- :220 `test_advance_tick_does_not_raise_under_role_aware_actions` — the docstring itself says "this property remains narrow: advance_tick must never raise" (:224-231).

Both batch strategies feed `_unique_actions_per_actor(batch)` (tests/engine/test_tick_properties.py:90-100), a plain de-dup that does NOT call `orchestrator.action_ordering.order_actions_for_tick` — so the lexicographic-by-actor ordering that decides which actions survive a meeting trigger (finding 1) is never exercised. Both loops also `break` the moment `state.phase != "PLAY"` (:116-117, :237-238), so the entire meeting-trigger tick is outside the explored space, which is why findings 1 and 2 are invisible to them.

Invariants that are property-shaped, currently untested, and would each have caught a real finding above:
1. ACTION CONSERVATION — every submitted action produces exactly one event attributable to it (a resolution event or an `ActionRejectedEvent`). Falsified by finding 1's probe: 3 actions in, 1 event out.
2. WIN COMPLETENESS — for every returned state, `evaluate_win_conditions(next_state) is None` OR a `GameOverEvent` is in the returned events. Falsified by finding 2's probe: parity satisfied, `GameOver emitted? False`.
3. TASK-INSTANCE CONSERVATION under `dead_task_rule: redistribute` (active on the canonical map, engine/maps/canonical_1.yaml:45): `len(tasks)` is non-increasing, `completed_tasks` is non-decreasing, and no instance key ever changes owner while `completed`.
4. PROGRESS MONOTONICITY — `task.progress` never decreases and never exceeds `required_ticks` for a fixed instance id.
5. RNG LOCKSTEP — `rng_state` changes iff `tick` changes, across both `advance_tick` and `apply_meeting_result` (this is what keeps the meeting boundary in sync, orchestrator/game.py:1344-1358, and it is asserted nowhere).
6. POLICY EQUIVALENCE — a FULL-policy and a TRAINING_FAST-policy run over the same seed/action stream produce identical action and event streams (engine/rng.py:44-46 claims it; tests/engine/test_rng_fast_path.py should own it as a property, and it is the precondition for the finding-5 fix).
```

**Verifier evidence (independent re-run).**

```
FILE FACTS ALL REPRODUCE. `wc -l` = 243 (claim says 244). Exactly three `@given` blocks at :103/:108, :137/:139, :215/:220 -- the fourth test at :150 is not a property. Assertions of property 1 at :125-132 are exactly `phase in _VALID_PHASES`, `tick >= state.tick`, `isinstance(events, list)`, `set(players)` stable, `player.room in game_map.rooms`. Property 3's BODY (:233-243) contains ZERO assertions. `_unique_actions_per_actor` at :90-100 is a plain per-actor de-dup. `break` on non-PLAY at :116-117 and :237-238. `order_actions_for_tick` lives at orchestrator/action_ordering.py:13 and is called only from orchestrator/boundary.py:50 -- never from the property file (grep confirms). `dead_task_rule: redistribute` is at engine/maps/canonical_1.yaml:45 as claimed. Repo-wide only 5 files use @given; only one is an engine property file.

THREE EVIDENCE DEFECTS FOUND.
(a) FABRICATED QUOTE. The claim states ':224-231 the docstring itself says "this property remains narrow: advance_tick must never raise"'. I read :224-231 verbatim: it says 'R-12: ``advance_tick`` must not raise on any role-aware batch. / Pairs with ``test_advance_tick_is_total_under_arbitrary_safe_actions`` above: that property covers ``move`` / ``wait`` sequences; this one covers the previously unexplored ``kill`` / ``vent`` / ``report`` / ``wait`` interleavings. Engine rejections must surface as ``ActionRejectedEvent``s (see ``engine/tick.py``), not exceptions.' The phrase 'this property remains narrow' appears nowhere in the file. The paraphrase is faithful to the substance (the body asserts nothing), but it is presented as a quotation and is not one.
(b) 'CURRENTLY UNTESTED' IS FALSE FOR AT LEAST THREE OF THE SIX. Invariant 6 (POLICY EQUIVALENCE) is covered by tests/engine/test_rng_fast_path.py:180-218 `test_advance_tick_fast_preserves_the_draw_sequence_and_events`, which runs 25 ticks under FULL vs TRAINING_FAST and asserts identical events, identical decoded Mersenne state, and identical non-rng fields -- exactly the invariant, as an example test over a wait-only stream. Invariant 4 (PROGRESS MONOTONICITY) has example coverage at tests/engine/test_tick.py:149-179. Invariant 2 (WIN COMPLETENESS) has seven example tests in tests/engine/test_win_conditions.py:68-189 plus 10 GameOverEvent assertions in tests/engine/test_tick.py. The accurate framing is 'not PROPERTY-tested', which is what the title says but not what the list header says.
(c) THE NARROW SHAPE IS SPECIFIED. tasks/phase-2.md:1506 (R-12 acceptance) requires 'a property covering the new vocabulary (AT MINIMUM: `advance_tick` does not raise on any drawn batch where roles and aliveness allow the action)'. audits/audit-2026-05-16-0009-pre-phase-3-verification.md:55 closes R-12 on precisely that basis, citing :181-212 and :215-243. So the third property meets its contract exactly; the gap is a further ambition, not a shortfall. (audits/audit-2026-05-10-0721.md:146 shows the prior, narrower version of this same item was tracked and then closed by R-12.)

NOT A RE-REPORT of any named known-open item.
```

**Verifier note.** The core observation stands and is worth acting on -- the engine's only property tests really do stop at totality, really do bypass the production ordering, and really do break before the meeting-trigger tick, which is the interesting boundary. Adjusted on three counts: the docstring quotation is fabricated (substance right, quote wrong), the list header's 'currently untested' is wrong for invariants 2, 4 and 6 (they have example-based coverage; what is missing is property coverage), and the narrowness of property 3 is a specified contract deliverable (tasks/phase-2.md:1506 'at minimum', closed by audit-2026-05-16-0009 R-12) rather than an omission. Reclassify from quality-debt to a test-coverage enhancement: no shipped code is defective and the tests meet the contract they were written against. Severity P2 is right. One further caveat: the finding's stated payoff -- 'would each have caught a real finding above' -- is entirely contingent on the two P1 findings it references, which are outside my verification scope; if those are refuted, invariants 1 and 2 lose their motivating evidence.

**Fix sketch.** Extend tests/engine/test_tick_properties.py with the six invariants above, and change the strategies to (a) route every drawn batch through `orchestrator.action_ordering.order_actions_for_tick` so the production ordering is what is explored, and (b) continue through MEETING via `apply_meeting_result` with a synthesized EJECTED/SKIPPED result instead of `break`ing, so the meeting boundary enters the explored space. Invariants 1 and 2 should be added BEFORE the corresponding fixes so the fixes are demonstrably driven by a failing property.

## B-28 — audible_events is the one packet channel with no entitlement or traceability check anywhere in the leak scan

**Severity:** P2. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** observation-firewall / eval.leak_scan / observation.service. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#3.

**Claim.** Nothing in the scan ties `audible_events` to an engine event or to the observer's entitlement, so a fabricated or over-disclosing audible row (e.g. a vent heard in a room the observer never witnessed) passes the full scan — the same gap `moved_players` had before Task 19.24.

**Finder evidence.**

```
`grep -n audible eval/leak_scan.py` returns nothing: the scan's channel list in `assert_packet_is_leak_clean` (eval/leak_scan.py:958-1030) covers visible_players, visible_bodies, self_state, owned tasks and moved_players only. Planted-packet probe:
```
PYTHONPATH=. uv run python -c "... p = svc.build_packet(world_state=state, agent_id='p-2', engine_events=events); poisoned = p.model_copy(update={'audible_events': (AudibleEvent(kind='vent_use_heard', room='REACTOR'),)}); assert_packet_is_leak_clean(poisoned, ctx)"
observer room: CAFETERIA baseline audible: ()
LEAK SCAN VERDICT: PASS (no assertion) for vent_use_heard in REACTOR, a room p-2 cannot see and no vent event backs
```
The live derivation IS witness-gated today — observation/service.py:359-381 `_audible_events` builds vent rooms only from `observed_actions` whose action is 'vent', and those come from `_vent_observation_for_agent` (observation/service.py:526-543), which requires membership in `source_witnesses` / `destination_witnesses` — so this is a scanner coverage hole, not a live leak. It matters because the channel is a live ML input: agents/tactical/features.py:374 (`event.kind == 'vent_use_heard'`) and :377 (`sabotage_alarm`) are encoder features. The prior review noted only the redundancy, not the coverage gap (audits/review-2026-08-19/B/observation-firewall.md F13: 'the audible channel is redundant with the visual one').
```

**Verifier evidence (independent re-run).**

```
`grep -c audible eval/leak_scan.py` -> 0. Confirmed by reading assert_packet_is_leak_clean (eval/leak_scan.py:958-1030): its five documented families cover visible_players key-set + forbidden fields + kill/vent witness permission (:988-1002), visible_bodies key-set (:1003-1006), the crew fellow_impostor_ids firewall, _assert_owned_task_discipline, assert_visible_entities_match_engine_truth, and assert_moved_players_are_witness_gated. Nothing reads packet.audible_events.

MY PLANTED-PACKET PROBE (independent script, seed_initial_state(seed=7, 9p/2i/2tpc), observer p-2): baseline packet clean, 'observer room: CAFETERIA | baseline audible: ()' -- identical to the finding's reported line. Then:
  planted vent_use_heard room=REACTOR    -> PASS (no assertion) -- LEAK NOT CAUGHT
  planted vent_use_heard room=ELECTRICAL -> PASS (no assertion) -- LEAK NOT CAUGHT
  planted sabotage_alarm  room=REACTOR   -> PASS (no assertion) -- LEAK NOT CAUGHT
The third is stronger than the finding's probe: observation/service.py:379 emits sabotage_alarm with room=None unconditionally, so a room-bearing sabotage_alarm is a shape the live derivation can never produce, and the scan still accepts it.

LIVE DERIVATION IS WITNESS-GATED, as the finding says: observation/service.py:359-381 `_audible_events` builds vent rooms only from observed_actions with action=='vent' and audible_room not None; those come from :526-543 `_vent_observation_for_agent`, which returns None unless agent_id is in event.source_witnesses or event.destination_witnesses. So this is a scanner coverage hole, not a live leak -- the finding's own framing.

LIVE ML INPUT CONFIRMED: agents/tactical/features.py:374 (`event.kind == 'vent_use_heard'`) and :377 (`sabotage_alarm`) are encoder features, as claimed.

PRIOR-ART CITATION ACCURATE: audits/review-2026-08-19/B/observation-firewall.md:155 says only 'the audible channel is redundant with the visual one (DESIGN 4.2 hints at "heard", i.e. wider than seen)' -- redundancy, not coverage. No named known-open item covers this.

EXTRA CORROBORATION I FOUND: tests/observation/test_leak_property.py:46 states the sweep exercises 'the events that populate ``visible_players`` / ``visible_bodies`` / ``audible_events`` where a leak would surface' -- but that sweep's only gate is assert_packet_is_leak_clean, which has no audible check. The test docstring claims coverage the scan does not deliver. eval/leak_test.py:223-238 touches audible_events only through the recursive role-string scanner on a synthetic dict, never on a real packet.
```

**Verifier note.** Strongest of the five. Reproduces exactly, including the baseline observer room and empty baseline audible tuple, and my extra sabotage_alarm probe strengthens it: the scan accepts a room-bearing sabotage_alarm, a shape observation/service.py:379 cannot emit. The 'not a live leak' framing is correct and honestly stated, so P2 quality-debt is the right severity and classification. Two additions for the fix: (1) tests/observation/test_leak_property.py:46's docstring already asserts audible coverage in prose, so it should be corrected or made true by the same change; (2) the sabotage_alarm gate should pin room IS None as well as requiring world_state.sabotage.active, since room=None is the only shape the service produces.

**Fix sketch.** Add `assert_audible_events_are_witness_gated(packet, engine_events=..., visible_rooms=...)` alongside the moved_players gate in eval/leak_scan.py: every `vent_use_heard` room must equal a source_room/destination_room of a Vent*Event of this tick whose corresponding witness tuple names `packet.agent_id`; `sabotage_alarm` must carry `room is None` and require `world_state.sabotage.active`. Call it from `assert_packet_is_leak_clean` and add two planted-leak self-tests in eval/leak_test.py mirroring the moved_players ones.

## B-29 — The champion leak gate's coverage assertion checks only that a body was seen; the witness-gated KILL channel it exists to police fires once per gate run

**Severity:** P2. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** observation-firewall / eval.leak_scan coverage. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#4.

**Claim.** `scan_factory_packets` claims to prove the games reached 'the kill -> body -> report -> meeting -> vent regions' but asserts only `bodies_seen > 0`, and measured on the FSM default factory the sweep yields exactly 1 kill-stamped PlayerView across 550 packets.

**Finder evidence.**

```
eval/leak_scan.py:1066-1070: `bodies_seen = sum(len(packet.visible_bodies) for packet, _ in records)` / `assert bodies_seen > 0, ('factory games never reached a body — the kill → body → meeting regions the factory leak scan exists to cover went unexercised')` — the only coverage assertion. Measured:
```
PYTHONPATH=. uv run python -c "from eval.leak_scan import collect_factory_packet_records; from orchestrator.game import build_default_agent_factory; recs=collect_factory_packet_records(build_default_agent_factory()); ..."
packets 550 body_views 33 vent_views 13 kill_views 1 moved_entries 301 audible_events 33
```
(seeds (0,1), 9p/2i — eval/leak_scan.py:795-798.) One kill view means the witness-permission branch at eval/leak_scan.py:993-1002 and the witness allowance at :710 are each exercised on a single packet per champion-gate run; a candidate policy that kills less would exercise them zero times and still pass, since only bodies are asserted. For scale, the committed corpus over 150 9p2i games yields 47 kill views (see the corpus finding), i.e. ~0.3 per game.
```

**Verifier evidence (independent re-run).**

```
ANCHORS EXACT. eval/leak_scan.py:1066 `bodies_seen = sum(len(packet.visible_bodies) for packet, _ in records)` and :1067-1070 the single assert with exactly the quoted message. It is the ONLY coverage assertion in scan_factory_packets (:1040-1071); the other assert is `records` non-empty. The docstring at :1048-1055 does claim the games 'must reach at least one body (proof they got past task-rush into the kill -> body -> report -> meeting -> vent regions the scan claims to cover)'. `_FACTORY_MODE_SEEDS = (0, 1)` at :795 with 9 players / 2 impostors / 2 tasks at :796-798. The witness-permission branch is at :993-1002 and the witness_allowance at :705-714, both as cited.

MY MEASUREMENT REPRODUCES THE FINDING'S NUMBERS EXACTLY. `collect_factory_packet_records(build_default_agent_factory())`:
  packets 550  body_views 33  vent_views 13  kill_views 1  moved_entries 301  audible_events 33
(the finding reported packets 550, body_views 33, vent_views 13, kill_views 1, moved_entries 301, audible_events 33 -- identical in every field). I additionally counted packets_with_moved = 137.

So across a whole champion-gate run the kill arm of the :993-1002 witness branch and the KilledEvent arm of the :710 allowance each fire on exactly ONE packet out of 550, while nothing asserts they fire at all.

CALL SITES CONFIRMED: training/bakeoff/harness.py:1823-1832 and training/crew/scorer.py:1730-1744 both wrap scan_factory_packets in try/except AssertionError as the champion leak gate, so this IS the gate's coverage bar.

SCALE COMPARISON VERIFIED INDEPENDENTLY (see my B-30 run): the committed 9p2i corpus yields 47 kill views over 150 games = 0.31/game, matching the finding's cited ~0.3/game.

NOT SPECIFIED AS SUFFICIENT: tasks/phase-20.md:1362 cites `bodies_seen > 0` as the PRECEDENT to mirror for a new non-vacuity counter, never as an adequate bar for the kill/vent regions. Not among the named known-open items.
```

**Verifier note.** Confirmed; my channel counts are identical to the finding's in all six fields. One imprecision in the supporting prose, not in the claim: 'a candidate policy that kills less would exercise them zero times and still pass, since only bodies are asserted' is not quite right -- a policy that kills less produces fewer bodies and eventually FAILS the existing assertion. training/crew/scorer.py:1049-1060 documents exactly that starvation ('most draws are the marathon survive-and-grind shape ... their games run to the eval tick cap without a single kill, so ... emits a row with leak_test_passed=false -- not a leak, but the factory scan's coverage assertion starving'), and is why the ci seed moved 0->7. The precise gap is a policy whose kills are never WITNESSED: bodies are discovered later regardless, so bodies_seen stays healthy while kill_views goes to zero. The FSM default already demonstrates that split (33 body views, 1 kill view). The claim as written, the severity and the classification all stand; only that one sentence needs rewording, and rewording it makes the finding sharper rather than weaker.

**Fix sketch.** Widen the coverage assertion in `scan_factory_packets` to the regions the docstring names — assert at least one witnessed kill PlayerView, at least one vent PlayerView, at least one non-empty moved_players and at least one meeting-resume packet — and, if the default seeds cannot reach them, widen `_FACTORY_MODE_SEEDS` (eval/leak_scan.py:795) until they do. Report the per-channel counts in the champion-gate record next to `leak_packets` so a shrinking channel is visible in the bakeoff artifact rather than silent.

## B-30 — The ML corpus the re-ground fits on has never been leak-scanned, though the machinery exists and the whole 200-replay corpus scans clean in 3.8 s

**Severity:** P3 (finder: P2). **Classification:** observation (unchanged). **Verdict:** ADJUSTED. **Area:** observation-firewall / ML re-ground hygiene. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#5.

**Claim.** No leak gate is ever run over replays/ml_corpus/: every entry point (scan_factory_packets, the three eval/leak_test.py scripted fixtures) generates its own games in-process. Reconstructing the corpus's packets through the existing `_reconstruct_factory_records` + `assert_no_factory_packet_leaks` helpers is a six-line loop that scans all 200 committed replays clean in ~4s and yields 47 kill views / 356 vent views over 9p2i (vs 1 kill view in the whole champion gate). Its value is a WIDE-STREAM regression guard on ObservationService and a direct answer to the champion gate's channel thinness -- NOT, as the finding states, a hygiene gate on the bytes the surrogate and conviction models are fit on: neither fit path builds an ObservationPacket at all.

**As originally filed.** Every leak gate runs on games generated fresh in-process; nothing ever scans the recorded packets of replays/ml_corpus/, which is exactly the byte set the surrogate and conviction models are about to be re-fit on.

**Finder evidence.**

```
`grep -rn "ml_corpus" --include="*.py" scripts training eval tests | grep -i "leak\|scan"` returns nothing. The only leak entry points are `scan_factory_packets` (eval/leak_scan.py:1040), which generates its own games via `HeadlessGame` (:929-943), and the 3 scripted fixtures in eval/leak_test.py:86-90. Yet the reconstruction helper already accepts an arbitrary replay path — `_reconstruct_factory_records(replay_path, game_map=..., seed=..., num_players=..., ...)` (eval/leak_scan.py:830-904) — so the scan is a six-line loop. Run over the committed corpus (roster parameters from replays/ml_corpus/README.md:69-70):
```
PYTHONPATH=. uv run python -c "...for sub, np_, ni, tpc in (('9p2i',9,2,2), ('4p1i',4,1,1)): ... assert_no_factory_packet_leaks(recs)..."
9p2i: 150 replays, 23992 packets, kill_views=47 vent_views=356 body_views=2526, failures=[] n_fail=0
4p1i: 50 replays, 1889 packets, kill_views=0 vent_views=31 body_views=156, failures=[] n_fail=0
total 3.8s
```
So the current corpus is clean — a positive result worth recording — but nothing keeps it that way across the re-record, and the two channels the leak scan most depends on are thin in it (47 kill views over 150 games; ZERO in the entire 4p1i set, so no 4p1i packet ever exercises the kill-witness allowance).
```

**Verifier evidence (independent re-run).**

```
GREP REPRODUCES: `grep -rn ml_corpus --include=*.py scripts training eval tests | grep -i 'leak|scan'` returns nothing (exit 1). Entry points confirmed: scan_factory_packets at eval/leak_scan.py:1040 generating via HeadlessGame at :929-943, and `_SCRIPTED_GAMES` = exactly three fixtures at eval/leak_test.py:86-90. `_reconstruct_factory_records(replay_path, *, game_map, seed, num_players, num_impostors, tasks_per_crewmate, audit_dir)` at :830-838 does take an arbitrary path, as claimed.

MY CORPUS SWEEP REPRODUCES EVERY NUMBER EXACTLY (independent script, roster params from replays/ml_corpus/README.md:69-70):
  9p2i: 150 replays, 23992 packets, kill_views=47 vent_views=356 body_views=2526 moved=12605, n_fail=0
  4p1i:  50 replays,  1889 packets, kill_views=0  vent_views=31  body_views=156  moved=655,  n_fail=0
  total 3.9s   (finding: identical counts, 3.8s)
So the corpus IS clean today, and the 4p1i set really does exercise the kill-witness allowance zero times.

WHERE THE CLAIM OVERREACHES -- two corrections.
(1) 'the recorded packets of replays/ml_corpus/'. There are no recorded packets. orchestrator/replay.py's ReplayEntry (:159-168) records kind/game_id/tick/actions/state_hash only; the packets are RECONSTRUCTED by re-seeding and re-walking. The finding's own evidence uses _reconstruct_factory_records, so it knows, but the claim sentence asserts a byte set that does not exist.
(2) 'exactly the byte set the surrogate and conviction models are about to be re-fit on' -- misleading about what the proposed scan would guard. `grep -n 'build_packet|ObservationService|walk_replay|_reconstruct' training/surrogate/dataset.py training/conviction/dataset.py` returns ONE comment line and no code: neither fit path constructs an ObservationPacket. training/surrogate/dataset.py:873-900 reads raw entries, re-runs advance_tick, verifies the state_hash, and feeds `_WindowStats.absorb_tick(state, events, roles, beliefs=...)` (:579-601), which re-derives per-player observability ITSELF from WorldState -- with ground-truth `roles` passed in -- and whose comment at :597-601 says it is hand-mirroring `_observed_actions_for_agent`. So the models are fit on features derived by a PARALLEL observability implementation, and a clean packet scan says nothing about it. The real leak-risk surface for the re-ground is drift between that mirror and the production rules, which this proposal does not touch.

NOT A RE-REPORT: distinct from the routed 'eval/replay_walk.py performs no substrate check' item (that is about retired_levers_stamped_off, not leaks) and from every other named known-open item.
```

**Verifier note.** Every measurement reproduces to the digit, and the underlying gap is real: nothing leak-scans the corpus, and the six-line sweep is cheap and passes. Adjusted on scope and framing. The claim's motivating sentence -- that this is 'exactly the byte set the surrogate and conviction models are about to be re-fit on' -- does not survive checking: neither training/surrogate/dataset.py nor training/conviction/dataset.py builds a packet, and the surrogate re-derives observability itself from WorldState with ground-truth roles in hand. A corpus packet scan therefore guards ObservationService, not the ML fit inputs. Reframed honestly the item still earns its place, and arguably earns more: it is the widest available regression stream for the observation firewall (23992 packets, 47 kill views, 356 vent views) and is the natural fix for B-29's one-kill-view thinness -- the two should be merged into a single recommendation. Severity lowered P2 -> P3: the finding's own result is a PASS, it names no defect, and its stated risk-to-the-re-ground does not hold as written. Classification 'observation' was already correct and honest.

**Fix sketch.** Add a corpus leak sweep to the re-ground preconditions: a small script (or a test marked `campaign`) that walks `replays/ml_corpus/{9p2i,4p1i}` through `_reconstruct_factory_records` + `assert_no_factory_packet_leaks`, asserts zero failures, and prints the per-channel counts (packets / kill_views / vent_views / body_views / moved entries) so the corpus's evidence density is a recorded number the fit reports can cite. At 3.8 s it is cheap enough for the default tier; wire it next to scripts/verify_ml_evidence.py so the corpus fingerprint and the corpus leak verdict are re-stamped together.

## B-31 — The vent_sighting contradiction flag is a referee-certified truth channel: it is minted from the speaker's PRIVATE episodic record and shown to every voter as engine-certified proof

**Severity:** P3 (finder: P2). **Classification:** specified-behavior (measurement recommendation + separate DESIGN.md drift), not a design-limitation finding. **Verdict:** ADJUSTED. **Area:** observation-firewall / meetings referee surface. **Confidence:** high.
**Merged from:** finder-observation-firewall.json#6.

**Claim.** The mechanism is exactly as described and reproduces verbatim, but it is NOT an uncovered surface: the referee-certified vent channel is fully specified, contracted and fixture-pinned by tasks/phase-15.md Task 15.4, which designs the typed self-channel accessor, the grounding chokepoint, the STRONG band and the 'firewall-clean, since an agent reporting its own witnessed events leaks nothing' judgement in those words. The only residue that survives verification is (a) the fix_sketch's ML measurement recommendation (split conviction/surrogate evaluation by presence of a grounded vent_sighting flag before re-fitting) and (b) a genuine but DIFFERENT doc drift the finding does not name: DESIGN.md 5.4 still enumerates only three flag kinds (alibi_conflict / alibi_vs_sighting / alibi_vs_physical) and never mentions vent_sighting or the grounding channel at all, so the design doc does not describe the strongest evidence channel in the game.

**As originally filed.** A spoken vent claim is flagged only when the manager can match it against the SPEAKER's own private VentWitnessRecord channel, and the resulting flag is rendered to every voter under the heading 'Proof. The engine certified these' — so all voters receive a truth signal derived from another agent's private memory that no agent's own perception entitles it to.

**Finder evidence.**

```
The pooling: orchestrator/game.py:1029-1155 `_build_participants` collects each agent's OWN `vent_witness_records_for_meeting()` (:1136-1139) into `MeetingParticipant`; meetings/manager.py:1024-1029 pools them into a per-speaker mapping and threads it into every `detect_contradictions` call (:1109-1115, :1145-1150, :1181-1186, :1226-1231). The grounding is keyed by the claim's own speaker — `grep -n "records = vent_witness_records.get" meetings/transcript.py` -> :3307, :3394, :3461, and meetings/transcript.py:3306-3325 skips a speaker with no records and yields a flag only on a `matched` record. Its docstring is explicit (meetings/transcript.py:3295-3299): 'an unmatched observation yields NOTHING (testimony, not evidence), and a matched one is STRONG -- the grounding chain ... means a grounded flag can only name a genuine venter, so the "STRONG flag naming a CREWMATE" false-positive class is structurally unreachable.' The flags then go to the NEXT speaker's prompt (`contradictions=contradictions_so_far`, meetings/manager.py:1128 / :1174 / :1213) and into the ballot, where the canonical v4 template renders them: agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:123 — 'Proof. The engine certified these: only an impostor can vent, so a flag here names one outright, and nothing said at this table outweighs it.'

Nothing in the observation firewall covers this surface: eval/leak_scan.py's memory-render gate (:263-320) polices only ROLE tokens in a render, and the packet scanners never see the meeting layer. The absence of a flag is equally informative (a fabricated vent claim silently raises none), so the channel is a two-sided lie detector.
```

**Verifier evidence (independent re-run).**

```
Every cited anchor re-read at HEAD d8ec0a1c and reproduces. orchestrator/game.py::_build_participants pulls `vent_witness_records=agent.vent_witness_records_for_meeting()` per living agent with the comment 'Task 15.4: the typed grounding channel -- ... a meeting-open snapshot of the agent's OWN witnessed-vent episodic records'. meetings/manager.py:1024-1029 pools them per speaker and threads the SAME mapping into all four detect_contradictions call sites (verified at the reply-chain, opt-in, roll-call and final-recompute sites). `grep -n "records = vent_witness_records.get" meetings/transcript.py` -> 3307, 3394, 3461 (unchanged). meetings/transcript.py:3306-3325: speakers with no records `continue`; a flag yields only on `matched is not None`. The docstring quoted in the finding is present verbatim at :3295-3299. _describe_vent_sighting (:3672-3682) quotes the RECORD not the spoken values, by explicit comment. Render path independently confirmed end-to-end: agents/strategic/prompts/loader.py:411 `_ROLE_PROOF_KINDS = frozenset({'vent_sighting'})` -> classify_flag_for_prompt returns 'role_proof' -> _group_flags puts it in `flag_groups.proof` -> vote_ballot.j2:123 renders 'Proof. The engine certified these: only an impostor can vent, so a flag here names one outright, and nothing said at this table outweighs it.' (also accusation_round.j2:163-167). The firewall sub-claim also holds: eval/leak_scan.py:263-290 `assert_memory_render_role_disclosure_is_entitled` matches ROLE TOKENS against allowed grammars only and never sees a ContradictionRef. WHAT REFUTES THE FRAMING: tasks/phase-15.md:388-497 Task 15.4 specifies the whole mechanism in advance -- 'the MeetingAwareAgent protocol gains ONE self-channel accessor, vent_witness_records_for_meeting() ... (the agent's OWN witnessed-vent episodic records ...); firewall-clean, since an agent reporting its own witnessed events leaks nothing'; 'The STRONG flag fires only when the speaker's spoken observation matches one of the speaker's own typed records'; 'An UNGROUNDED vent claim is accepted as ordinary testimony ... but raises NO flag' (i.e. the two-sided lie-detector property the finding names is the contracted DoD, pinned as 'the task's most important test'). Separately verified drift: `grep -n "vent_sighting" DESIGN.md docs/architecture.md` returns NOTHING, and DESIGN.md 5.4 (read at :571-580) still says 'in three kinds'.
```

**Verifier note.** Core observation stands and is technically exact -- listeners do receive an engine oracle no perception entitles them to. But the finding's own fix_sketch concedes 'No code change proposed -- this is a locked mechanism', and verification shows it is specified at contract level, not merely 'locked' by convention, so it cannot carry P2 as a finding. Downgraded to P3 and re-cast as (i) an ML measurement recommendation (worth carrying into the re-ground unchanged) and (ii) a DESIGN.md 5.4 completeness gap that the finding did not identify but that its own evidence establishes -- 336 of the 457 recorded flags in replays/ml_corpus are vent_sighting (measured this pass), i.e. the design doc omits 74% of the corpus's flag mass.

**Fix sketch.** No code change proposed — this is a locked mechanism (DESIGN.md §5.4, Task 15.4) and the template states it plainly. What the re-ground should add is measurement: before re-fitting, split the conviction/surrogate evaluation by whether the meeting carried a grounded `vent_sighting` flag, and report the eject-decision and conviction-fit metrics with and without those meetings. Otherwise the re-fit models (and the campaign that optimizes against them) will credit a referee-certified oracle as 'deduction', and a policy can climb the fitness by farming certifiable vent sightings rather than by arguing. Record the split in docs/ml-program.md alongside the re-published arms.

## B-32 — Duplicate alibi_vs_sighting mint: 6 of 71 corpus flags, and the surrogate's own feature builder is one of the consumers that still double-counts

**Severity:** P3 (finder: P2). **Classification:** defect (consumer-side only; the production mint is a declared carry, not a new finding). **Verdict:** ADJUSTED. **Area:** meetings-detector / meetings/transcript.py::_apply_movement_claim_shape -> training/surrogate/dataset.py::_flag_counts. **Confidence:** high.
**Merged from:** finder-meetings-detector.json#4.

**Claim.** The duplicate mint reproduces but measures HIGHER than filed: 7 same-speaker duplicate extras across 7 meetings (9.9% of the 71-flag alibi_vs_sighting class), not 6 across 6 -- the finding's scan missed replays/ml_corpus/9p2i/replay-seed-1097.jsonl meeting-0, where p-6 mints the pair and a third flag from a DIFFERENT speaker (p-9) shares the description, which is presumably what collapsed it into the cross-speaker bucket. The production-mint half of the claim is a re-report of a declared, dated, deliberate carry (audits/audit-phase-20-baseline-7.md:778-782, named verbatim in the known-open list). The genuinely NEW half is the consumer census, and it must be split: training/surrogate/dataset.py::_flag_counts is a LIVE double-counter feeding the re-fit and is the whole actionable residue; training/anchor_study.py:669-671 is declared FROZEN, report-only, concluded-campaign code (training/README.md:131: 'Concluded campaigns ... The anchor study is report-only -- no champion ships'), so its inflated flags_per_meeting has no live consumer and should not be priced as a re-ground risk. All three 'FOLDS CORRECTLY' legs re-verified and hold.

**As originally filed.** The declared production-side duplicate mint measures at 6 extra flags across 6 meetings (8.5% of the corpus's alibi_vs_sighting class); the belief lift and the grounded-prosecution carrier count both fold it correctly, but the surrogate dataset's per-subject weak-flag feature and anchor_study's per-meeting flag total do not — so the re-fit reads an inflated weak count on those rows.

**Finder evidence.**

```
DEEPENS the declared carry (audits/audit-phase-20-baseline-7.md:778-782), which states the shape but no magnitude and names only the instrument side as repaired.

Mechanism: meetings/transcript.py:2349-2359 returns `resolved + tuple(_iter_move_placements(...))` — a spoken saw_player the speaker's own MoveWitnessRecord re-aims to the destination (:2362-2381) AND the same speaker's SawMoveObservation for that transition (:2520-2531) both survive as distinct _IndexedSighting rows on distinct observation event ids, so _build_contradiction (:3592-3593) mints two distinct contradiction_ids for one witnessed event.

Measured on replays/ml_corpus (`uv run python .../dup_scan2.py`, resolving each flag's sighting-side event id back to its turn/observation):
```
alibi_vs_sighting recorded total: 71
same-speaker duplicate extras: 6 in meetings: 6
cross-speaker same-description extras (legit distinct witnesses): 9
EX ('replay-seed-1023.jsonl', 'headless-seed-1023:meeting-0', 'Alibi places p-8 in LABS (ticks 3-8); sighting reports p-8 in MEDBAY at tick 8...', ['p-2', 'p-2'], ['SawPlayerObservation', 'SawMoveObservation'], ['turn:...:turn-5:obs:1|turn:...:turn-7:claim:0', 'turn:...:turn-5:obs:2|turn:...:turn-7:claim:0'])
```
(also seeds 1044, 1046, 1049, 1053, 1123 — every one is one speaker, one SawPlayerObservation + one SawMoveObservation, same alibi claim.)

Blast radius, seam by seam:
* FOLDS CORRECTLY — belief Rule 2: both flags share the alibi claim event id, so meetings/transcript.py:987-993 contradiction_lift_key returns the same key and the (subject, key) dedup collapses them to one delta.
* FOLDS CORRECTLY — grounded prosecution: meetings/transcript.py:3930/3948 keys carriers on the SPEAKER id in a set, so one narrator saying it twice is still one carrier.
* FOLDS CORRECTLY — instrument: eval/evidence_honesty.py:2011-2043 `_dedupe_flags` (20.43's repair).
* DOUBLE-COUNTS — training/surrogate/dataset.py:450-472 `_flag_counts`, called at :958 on `result.contradictions`, increments `weak` per flag per subject with no dedup. (Its sibling `_contradiction_lifts` at :475-490 explicitly warns "Raw count sums would double a duplicated weak flag (0.16 vs the rendered 0.08)" — the warning was applied to the lift and not to the count.)
* DOUBLE-COUNTS — training/anchor_study.py:669-671 `persisted_flags = sum(len(entry.contradictions) ...)`, i.e. the flags-per-meeting corpus fact.
```

**Verifier evidence (independent re-run).**

```
INDEPENDENT CORPUS MEASUREMENT (my own scan, resolving each flag's sighting side by matching the ':obs:' event id back through `turn:{turn_id}:obs:{i}` into the recorded transcript's turn speaker + observation type): alibi_vs_sighting recorded total 71 over replays/ml_corpus (0 unresolvable). Same-speaker groups keyed on (claim event id, description, speaker) with >1 member: 7 groups, 7 extras -- seeds 1023 m0 (p-2), 1044 m0 (p-5), 1046 m1 (p-1), 1049 m0 (p-9), 1053 m0 (p-6), 1097 m0 (p-6), 1123 m0 (p-2). EVERY one is exactly one speaker contributing one SawPlayerObservation + one SawMoveObservation against the same alibi claim, confirming the mechanism. Cross-speaker same-description extras: 9 (8 groups, one of size 3) -- matches the finding's 9. All 14 flags in the 7 duplicate groups carry '[weak signal: ' (endpoint-tick / narrow-window / adjacent-room), so the inflation lands on the WEAK column as claimed. MECHANISM: meetings/transcript.py:2349-2359 `_apply_movement_claim_shape` returns `resolved + tuple(_iter_move_placements(...))`; _resolve_movement_sighting (:2362-2381) preserves the ORIGINAL event id while rewriting the room, and _iter_move_placements (:2520-2531) mints a second _IndexedSighting on a distinct obs id -- two surviving rows, two contradiction_ids. FOLDS-CORRECTLY legs re-verified: (a) meetings/transcript.py:954-995 contradiction_lift_key filters event ids to the ':claim:'/':whereabouts:' segments and joins them, so both duplicates return the SAME key and belief Rule 2's (subject, key) dedup collapses them -- confirmed by reading the code, and the sibling _contradiction_lifts docstring at training/surrogate/dataset.py:475-490 states the same fold; (b) meetings/transcript.py:3929-3948 grounded prosecution keys `sources` as a set of SPEAKER ids, so one narrator counts once; (c) eval/evidence_honesty.py:2011-2043 `_dedupe_flags` docstring explicitly encodes 'a transition and ONE OF ITS ENDPOINTS ... The TRANSITION survives'. DOUBLE-COUNT legs re-verified: training/surrogate/dataset.py:450-472 increments per flag per subject with no dedup and is called at :958 on `result.contradictions`; the counts land in the row features `strong_flags`/`weak_flags`/`vent_flags` (:246-248, :819-836). training/anchor_study.py:669-671 is `persisted_flags = sum(len(entry.contradictions) ...)`. FREEZE STATUS: training/README.md:131 lists `training/anchor_study.py` in the FREEZE column ('Concluded campaigns ... report-only -- no champion ships'); training/surrogate/dataset.py is NOT in the 13-file frozen list at :184-190.
```

**Verifier note.** Scale: 7 of 476 corpus meetings (1.5%) carry one phantom weak flag on one subject in the surrogate feature builder. Real, cheap to fix, and correctly diagnosed -- but the magnitude the finding uses to argue P2 is both slightly understated (7 not 6) and, on the consumer side, halved by anchor_study being frozen. P3. The production-side fix sketch (lift eval/evidence_honesty.py::_dedupe_flags into meetings/transcript.py) remains correct but is a re-record-wave item and duplicates a carry already ratified in the baseline-7 record, so it should be routed as 'close the declared carry', not filed as a new defect.

**Fix sketch.** Production fix (moves bytes, so re-record wave): in _apply_movement_claim_shape, drop a re-aimed static placement when the same speaker also contributes a grounded SawMoveObservation with the same subject/tick/destination — the transition is the fuller statement, exactly the rule eval/evidence_honesty.py::_dedupe_flags already encodes; lift that helper into meetings/transcript.py so instrument and production share one definition. Consumer fix (no byte movement, do it now): route training/surrogate/dataset.py::_flag_counts and training/anchor_study.py's census through the same dedup before the re-fit, so the ML features stop reading 6 phantom weak flags.

## B-33 — The STRONG/WEAK band is a substring test over a description that interpolates model-authored room text, so a compound room label can self-band its own flag WEAK

**Severity:** P3 (finder: P2). **Classification:** defect (latent input-validation / band-carrier fragility). **Verdict:** ADJUSTED. **Area:** meetings-detector / meetings/transcript.py::is_weak_contradiction / _describe_alibi_vs_sighting. **Confidence:** high.
**Merged from:** finder-meetings-detector.json#5.

**Claim.** Every technical element reproduces exactly, including the corpus-clean scan. Only the severity is wrong: this is a latent robustness hole with zero instances in any committed byte, whose trigger requires the model to emit the detector's exact internal literal '[weak signal: ' (lower-case, trailing space) INSIDE a room field, in a compound label whose other member is a canonical room. Its only direction is self-downgrade (STRONG -> WEAK); no label can upgrade a flag. Fix cost is one line. P3, not P2.

**As originally filed.** `is_weak_contradiction` returns True iff the literal "[weak signal: " appears anywhere in the description, and the description interpolates the RAW room label (never the canonical set), so a label like "LABS/MEDBAY [weak signal: transit]" — which canonicalises to a valid room set and therefore still mints the flag — flips the flag to WEAK and cuts the belief lift from +0.30 to +0.08.

**Finder evidence.**

```
meetings/transcript.py:924 `return WEAK_CONTRADICTION_MARKER_PREFIX in flag.description`. meetings/transcript.py:3631-3635 interpolates `{alibi.room}` / `{sighting.room}` — the raw label, not `alibi.rooms`. Rooms are unvalidated free text: meetings/schemas.py:50 `RoomId: TypeAlias = str`, with no enum on the LLM side and no parse-time rewrite (canonical_rooms is a comparison helper only; tests/meetings/test_transcript.py:696 pins `canonical_rooms("CAFETERIA/UNKNOWN") == frozenset({"CAFETERIA"})`, i.e. junk after a separator is tolerated).

Demonstrated (`uv run python .../marker_spoof2.py`), same transcript twice, belief delta via the production agents.memory.beliefs.apply_contradiction_rule on a 0.5 prior:
```
--- control: canonical_rooms('LABS') = ['LABS']
    kind=alibi_vs_sighting is_weak=False suspicion=0.800
    desc: Alibi places p-1 in LABS (ticks 2-8); sighting reports p-1 in CAFETERIA at tick 5.
--- compound label carrying the marker: canonical_rooms('LABS/MEDBAY [weak signal: transit]') = ['LABS']
    kind=alibi_vs_sighting is_weak=True suspicion=0.580
    desc: Alibi places p-1 in LABS/MEDBAY [weak signal: transit] (ticks 2-8); sighting reports p-1 in CAFETERIA at tick 5.
```
0.80 is over the §4.6 gate of 0.6; 0.58 is under it. A bare junk label (no "/") is inert because canonical_rooms returns the empty set and no flag mints — the compound form is what threads the needle.

NOT exploited in the committed bytes: over replays/ml_corpus + replays/samples (`uv run python .../marker_wild.py`) 12,978 room labels were scanned and every one is a member of CANONICAL_ROOMS; 0 recorded flags carry an unrecognised weak reason. So this is latent, not corpus poison — but the re-ground's whole point is to change what the models optimise toward.

The codebase already defends this exact pattern one layer up: meetings/manager.py:1992-1993 notes that "Splitting on marker SHAPE instead would let a rationale that opens with marker-shaped prose smuggle that payload through" — the detector's marker has no equivalent guard.
```

**Verifier evidence (independent re-run).**

```
CODE: meetings/transcript.py:924 `return WEAK_CONTRADICTION_MARKER_PREFIX in flag.description` with the literal defined at :628 as '[weak signal: '. _describe_alibi_vs_sighting (:3625-3638) interpolates `{alibi.room}` and `{sighting.room}` -- the RAW labels; canonical_rooms (:868-902) is a pure comparison helper that upper-cases, splits on the compound joiners, and keeps only CANONICAL_ROOMS members. meetings/schemas.py:50 `RoomId: TypeAlias = str` with no validator on any of the 13 room fields. Independently confirmed there is NO parse-time rewrite: the only production import of `canonical_rooms` into meetings/manager.py is at :149 and its only uses are :2169/:2186 (vent-scene room sets); no normalization/validation of observation or claim rooms exists anywhere in the manager's turn path. MY OWN REPRO (scratchpad/v6/b33.py, one transcript, three room labels, real detect_contradictions + is_weak_contradiction): control 'LABS' -> canonical ['LABS'], kind=alibi_vs_sighting is_weak=False; 'LABS/MEDBAY [weak signal: transit]' -> canonical ['LABS'] (still comparable, still mints), is_weak=TRUE, desc 'Alibi places p-1 in LABS/MEDBAY [weak signal: transit] (ticks 2-8); sighting reports p-1 in CAFETERIA at tick 5.'; bare junk 'TOTALJUNK' -> canonical [] -> NO FLAG (so the compound form is indeed the only needle-threading shape, exactly as filed). Belief arithmetic confirmed from constants rather than a re-run: agents/memory/beliefs.py:104/108 give 0.30 / 0.08, and :117 + :292 + :328 state 0.5+0.08=0.58 and 0.5+0.30=0.80 against the 0.60 gate. CORPUS: my own scan of every room/from_room/to_room/claim-room in replays/ml_corpus + replays/samples = 12,978 labels (the finding's exact figure), 9 distinct values, ZERO non-canonical -- so 0 exploitation in committed bytes, as filed. The manager's marker-shape precedent quoted by the finding is real (meetings/manager.py:1992-1993, 'Splitting on marker SHAPE instead would let a rationale that opens with marker-shaped prose smuggle that payload through'). NOT A DECLARED CARRY: audits/audit-phase-19-triage.md item 18 and the training/README.md:135 freeze row cover the EVAL-side English-substring weak-reason classification (eval/vote_correctness.py, eval/meeting_quality.py) and are about drift under prompt-shape change -- neither names meetings/transcript.py::is_weak_contradiction nor this spoofing shape.
```

**Verifier note.** Confirmed on every factual point; I could not find any way to break the repro. Downgraded on exposure only: latent, never observed, self-harming direction, and gated behind an exact-literal emission that the corpus shows the deployed model has never come close to. The preferred fix (carry the band as a `weak_reasons` tuple on ContradictionRef and read `bool(flag.weak_reasons)`) is right and additive; note it would also fix the eval-side substring readers the phase-19 triage froze, so it is worth routing as one repair rather than two.

**Fix sketch.** Two options, both small. Preferred: carry the band as data — add a `weak_reasons: tuple[str, ...]` field to ContradictionRef, have is_weak_contradiction read `bool(flag.weak_reasons)`, and keep the marker text as pure render (the field is additive, defaults to () and re-derives, so committed replays still load). Minimal: sanitise the interpolated room in the _describe_* helpers to `"/".join(sorted(canonical_rooms(room)))`, which is already the only part of the label any rule reads. Add a pin that a marker-shaped room label cannot change is_weak_contradiction.

## B-34 — grounded_prosecution is a meeting-global all-or-nothing switch, and arming it silently withdraws the 18.9 interior exemption for unrelated flags

**Severity:** n/a (not a defect) (finder: P2). **Classification:** specified + ratified behaviour. **Verdict:** REFUTED. **Area:** meetings-detector / meetings/transcript.py::detect_contradictions + meetings/manager.py sighting-record assembly. **Confidence:** medium.
**Merged from:** finder-meetings-detector.json#6.

**Claim.** The code observation reproduces exactly, but the behaviour is not an undeclared design limitation -- it is the explicitly contracted, owner-ratified design of Task 20.26, stated in the phase doc in the finding's own terms, and the docstring change the finding requests is already present in the code.

**As originally filed.** `grounded_prosecution = bool(sighting_records)` is true whenever ANY participant holds ANY non-teammate sighting record about ANY player, and that one global bit both arms the grounding rules and withdraws the single-tick interior exemption — so the band of a flag about p-1 depends on whether an unrelated p-7 happened to see somebody.

**Finder evidence.**

```
meetings/transcript.py:1668 `grounded_prosecution = bool(sighting_records)` — truthiness of the MAPPING, not of any record relevant to the flag being banded. meetings/manager.py:1049-1058 builds it as `if rows: sighting_records[participant.agent_id] = rows`, so the mapping is empty only when NO living participant holds a single non-teammate SightingRecord. meetings/transcript.py:2765-2768 then reads that same bit to decide the exemption:
```
interior_exempt = not grounded_prosecution and (
    alibi.claim.from_tick == alibi.claim.to_tick
    and alibi.speaker == alibi.claim.subject
)
```
So two byte-identical transcripts with byte-identical flags band differently on a condition external to both the alibi and the sighting in question. The docstring at :2759-2764 states the withdrawal is deliberate but frames it as "with records to ground against" — the records in question need not touch this subject, this claim, or this speaker.

This is the mechanism behind finding 2's band inversion: every records-free consumer takes the `not grounded_prosecution` branch and mints STRONG flags production minted WEAK (6 of the 8 cases in .../strong_cause.py output are exactly this).

Same paragraph, second-order: the withdrawal is total, not conditional on the flag's own sighting being groundable, so at baseline 7 (where the manager always threads the channel in a populated game) the 18.9 exemption is effectively dead code in production while staying live in every offline re-derivation — which is why the two disagree.
```

**Verifier evidence (independent re-run).**

```
MECHANISM REPRODUCES: meetings/transcript.py:1668 `grounded_prosecution = bool(sighting_records)` (truthiness of the mapping); meetings/manager.py:1049-1058 builds it as `if rows: sighting_records[participant.agent_id] = rows` after the 4.7 teammate filter; meetings/transcript.py:2765-2768 `interior_exempt = not grounded_prosecution and (alibi.claim.from_tick == alibi.claim.to_tick and alibi.speaker == alibi.claim.subject)`. The 18.9 lever resolvers are gone from the module (`grep -n "whereabouts_interior_flags_enabled"` -> no hits), so the exemption is unconditional-except-withdrawn, as described. WHAT REFUTES IT: tasks/phase-20.md Task 20.26 specifies precisely this shape in advance -- ':4118-4121' region: 'The lever is inert twice over: OFF by default, and a NO-OP when the caller supplies no per-speaker mapping -- ONE PREDICATE GATES ALL THREE RULES, so the record-free re-derivers (eval, audit workflows) keep the pre-20.26 rules rather than silently reading every sighting as fabricated.' That is the meeting-global switch, named as the deliberate mechanism and given its reason. Rule (c) is spelled out ('the degenerate from_tick == to_tick self-placement stops being adjudicated as its own interior, so it keeps the pre-18.9 narrow-window / endpoint band') and the supersession is explicit: 'Rules (b) and (c) knowingly SUPERSEDE two owner rulings ... the Task 18.9 endpoint-band exemption that promoted roll-call whereabouts answers to STRONG. Both were adopted on evidence and are being reversed on more of it.' It is re-ratified a second time at tasks/phase-20.md:6079 ruling (4): 'The grounded_prosecution parameter of _detect_alibi_vs_sightings is DATA-gated (`and bool(sighting_records)`), not lever-gated -- folding it to True kills the 18.9 interior exemption; the reverifier's edit stands.' DOC ASK ALREADY SATISFIED: the docstring the finding calls misleading in fact opens (meetings/transcript.py:2759-2762) '``grounded_prosecution`` -- true exactly when the caller handed :func:`detect_contradictions` per-speaker sighting records -- WITHDRAWS the exemption', i.e. it already states the call-level, not flag-level, condition in the words requested. SECOND-ORDER CLAIM IS ALSO THE DECLARED INTENT: 'the 18.9 exemption is effectively dead code in production while staying live in every offline re-derivation' is verbatim what 'the record-free re-derivers keep the pre-20.26 rules' contracts for; the production/offline band divergence is the separately-filed B-6 (records-free re-derivation), already canonical at P1.
```

**Verifier note.** The residual sting -- 'the band of a flag about p-1 depends on whether an unrelated p-7 saw somebody' -- is true only in the empty-mapping mode, which IS the declared caller-mode switch, and the finding itself concedes that mode is unreachable in a populated production game. So the coupling it warns about has no production instance and no undeclared surface. Filed at confidence 'medium'; verification resolves it against the finding. If anything survives, it is a docs-only wish (repeat the phase-20 sentence in the module docstring), which does not carry a severity.

**Fix sketch.** Make the switch per-flag rather than per-meeting: decide the interior exemption on whether THIS flag's sighting side is groundable (`_sighting_is_grounded(sighting, records=sighting_records.get(sighting.speaker, ()))`), not on whether the mapping is non-empty. That keeps the record-free re-derivers' contract (no records -> nothing groundable -> exemption applies uniformly) while removing the dependence on unrelated players' memory. If the current behaviour is intended, say so in the docstring in those words ("any record held by anyone arms this") and add a pin, because today the prose reads as if the flag's own grounding decides it.

## B-35 — The directional breadcrumb excludes vent/kill sightings from the subject's path, so "last seen there at tick T" can under-report the room where the agent witnessed a vent

**Severity:** P3 (finder: P2). **Classification:** defect (render self-consistency; no measured downstream effect). **Verdict:** ADJUSTED. **Area:** memory-render / movement breadcrumb (agents/memory/store.py::_collect_movement_breadcrumbs). **Confidence:** high.
**Merged from:** finder-memory-render.json#2.

**Claim.** The code path, the repro and the corpus class all reproduce -- I measure the rate slightly HIGHER than filed (213 of 19,729 breadcrumb suffixes over replays/ml_corpus + replays/samples, 1.1%; 166 of 14,509 over ml_corpus alone, also 1.1%, vs the filed 173/19,119 = 0.9%), and every contradicting later line is a witnessed VENT (zero kill cases). The finding's seed-1001 p-6 example reproduces verbatim. What does NOT survive is the impact half of the claim: across all 213 affected prompts, ZERO recorded responses ever spoke the stale (subject, prior_room, prior_tick) placement, so the asserted landing 'precisely on the game's single strongest piece of evidence' has no measured consequence -- the correct vent tick sits one line above at higher salience and the template instructs the model to copy the vent line exactly, which is what every affected agent in fact did. Also missing from the fix sketch: the repair moves RENDERED PROMPT BYTES, so it is a re-record-wave item, not a free consumer-side patch.

**As originally filed.** `_collect_movement_breadcrumbs` skips `action in ("vent", "kill")` rows when building each subject's path, so the "(moved from X, last seen there at tick T)" suffix can name a tick strictly earlier than a witnessed vent/kill the same render states for that subject in that same room.

**Finder evidence.**

```
CODE. agents/memory/store.py:950-953 —
```
        action = event.payload.get("action")
        action_str = action if isinstance(action, str) else None
        if action_str in ("vent", "kill"):
            continue
```
and store.py:971-984 then takes `ordered[-1]` as the current sighting and the most-recent DIFFERENT-room entry as `prior`, which the suffix renders at store.py:1011-1014.

REPRO (scratchpad/wave0/B/repro_breadcrumb.py; `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../repro_breadcrumb.py`):
```
- [obs p-1:2:1] [tick 2] You witnessed p-3 vent in LABS.
- [obs p-1:3:1] [tick 3] You saw p-3 in MEDBAY (moved from LABS, last seen there at tick 1).
```
The render simultaneously states the agent saw p-3 in LABS at tick 2 and that p-3 was last seen in LABS at tick 1.

CORPUS. Scanning every recorded prompt for `(moved from PRIOR, last seen there at tick T)` and looking for a strictly later sighting of that same subject in PRIOR within the same rendered memory:
```
breadcrumb suffixes: 19119 contradicted by a later sighting in the SAME prior room: 173 (0.9 %)
EX ('replays/ml_corpus/9p2i/replay-seed-1001.jsonl', 'p-6', 'You saw p-3 in MEDBAY (with p-7) (moved from LABS, last seen there at tick 7)', ('p-3', 12, 'LABS'))
```
The seed-1001 p-6 render carries `- [obs p-6:12:1] [tick 12] You witnessed p-3 vent in LABS.` and `- [tick 12] p-3 entered LABS.` beside the breadcrumb claiming tick 7 — the contradiction lands precisely on the game's single strongest piece of evidence, which is the line the prompt instructs the model to speak first.
```

**Verifier evidence (independent re-run).**

```
CODE re-read at HEAD: agents/memory/store.py:948-953 skips `action_str in ('vent','kill')` before `paths.setdefault(...)`; :966-984 takes `ordered[-1]` as current and the most-recent DIFFERENT-room entry as prior; _movement_suffix_for (:985-1014) renders '(moved from {prior_room}, last seen there at tick {prior_tick})'. The docstring at :928-939 states the intent as 'vent / kill are witnessed events rendered as their own high-salience lines, NEVER SUFFIXED' -- a statement about decorating the vent line, which is NOT what the exclusion does; the exclusion also removes the vent row from the path used to compute OTHER lines' prior, which is the undeclared half. MY OWN CORPUS SCAN (scratchpad/v6/b35_scan.py; regex over every llm_calls[].prompt in both replay trees, indexing every '[tick t] You witnessed|saw <subj> ... in <ROOM>' line and testing each suffix for a same-subject same-prior-room sighting at prior_tick < t <= current_tick): ml_corpus 166/14,509 (1.1%), corpus+samples 213/19,729 (1.1%), contradicting-line kinds {vent: 213, kill: 0}. DIRECT VERBATIM CHECK of the filed example, replays/ml_corpus/9p2i/replay-seed-1001.jsonl, p-6's tick-13 meeting prompt: '- [obs p-6:12:1] [tick 12] You witnessed p-3 vent in LABS.' / '- [obs p-6:13:1] [tick 13] You saw p-3 in MEDBAY (with p-7) (moved from LABS, last seen there at tick 7).' / '- [tick 12] p-3 entered LABS.' -- exactly as filed. The same render's NEXT line makes the asymmetry self-evident: '- [obs p-6:13:2] [tick 13] You saw p-7 in MEDBAY (with p-3) (moved from LABS, last seen there at tick 12)' -- p-7's ordinary tick-12 LABS sighting is kept while p-3's tick-12 LABS vent is dropped. UPTAKE MEASUREMENT (scratchpad/v6/b35_uptake.py): of the 213 llm_calls whose prompt carries a stale breadcrumb, 213 responses parsed as JSON and 0 contained an observation with (subject, room, tick) == the stale triple. NOT SPECIFIED: tasks/phase-13.md Task 13.6 (:283-345) contracts only 'store.py emits the directional breadcrumb (byte-deterministic, no new packet field)' and says nothing about the vent/kill path exclusion, so the behaviour is a code-level choice whose only rationale on record is the (satisfied but non-implying) 'never suffixed' clause.
```

**Verifier note.** Confirmed as a real render self-inconsistency with a correct one-line fix, and my scan is slightly harsher on the rate than the finding's. Downgraded to P3 because the consequence the finding argues for is measurably absent in every committed byte: no model ever propagated the stale tick, and the vent tick reaches the transcript correctly (seed-1001 p-6's opening states 'I saw p-3 vent in Labs at tick 12'). Add the re-record cost to the fix sketch -- feeding vent/kill rows into `paths` changes rendered prompt bytes, so it must ride a re-record wave and cannot land as a quiet patch.

**Fix sketch.** Feed the vent/kill sighting's (tick, room) into `paths` for the purpose of computing `last_tick`/`prior`, while keeping the suffix off the vent/kill LINE itself (the current suppression is about not decorating a witnessed-event line, not about erasing the placement it proves). One-line change at store.py:952: record the row, then filter the suffix attachment in `_movement_suffix_for` instead.

## B-36 — The §4.7 teammate kill-window suppression punches a hole in the sighting log that `_collect_transitions` reads as movement, fabricating "entered"/"left" lines about a teammate who never moved

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** memory-render / within-vision transitions (agents/memory/store.py::_collect_transitions). **Confidence:** high.
**Merged from:** finder-memory-render.json#3.

**Claim.** `_collect_transitions` derives entry/exit from set differences over `seen_in_own_room`, which `_sighting_is_suppressed` has already emptied for a teammate inside a body-proximity window, so the render asserts two movements that the event log does not contain.

**Finder evidence.**

```
CODE. agents/memory/store.py:1343-1353 applies `_sighting_is_suppressed` when BUILDING `seen_in_own_room`; store.py:1368-1394 then emits `entered` on `now_seen - prev_seen` and `left` on `prev_seen - now_seen`. The suppression predicate (store.py:1076-1081 with store.py:1039-1042) fires exactly on the tick window `0 <= body_tick - tick <= BODY_PROXIMITY_WINDOW_TICKS` (=3, agents/memory/beliefs.py:100), so a teammate standing still across that window disappears at its first tick and reappears after its last.

REPRO (scratchpad/wave0/B/repro_transitions.py; `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../repro_transitions.py`). Impostor p-1 and teammate p-2 both stand in ROOM_A for ticks 0-6; p-1 sees a body there at tick 4:
```
## Recent observations (most salient first):
- [obs p-1:4:2] [tick 4] You discovered p-3's body in ROOM_A.
- [obs p-1:5:1] You saw p-2 in ROOM_A ticks 5-6.
- [obs p-1:0:1] [tick 0] You saw p-2 in ROOM_A.
- [tick 5] p-2 entered ROOM_A.
- [tick 1] p-2 left ROOM_A.
```
p-2 never left ROOM_A. Worse, the fabricated pair reads as a false ALIBI for the teammate across the kill window — the firewall drops the incriminating sighting and then manufactures an exculpating movement in its place, which is speakable public testimony the impostor believes.

CORPUS REACHABILITY (checked, negative). Deriving each game's impostor pair from the recorded kill actors and looking for a transition line naming the observer's teammate inside a same-room body window across all 200 replays:
```
games: 200 impostor renders with a known teammate: 1242
teammate transition lines inside a same-room body window: 0
```
So the defect did NOT fire in the committed baseline-7 corpus — it does not poison the existing fit — but it is live in the code for any re-record.
```

**Verifier evidence (independent re-run).**

```
INDEPENDENT REPRO (my own fixture, not the finder's; /private/tmp/.../wave0/B/v7_b36.py, `PYTHONPATH=. uv run python v7_b36.py` against HEAD d8ec0a1c). Impostor p-1 and teammate p-2 both stationary in ROOM_A ticks 0-6, p-1 discovers p-3's body there at tick 4:
```
## Recent observations (most salient first):
- [obs p-1:5:1] You saw p-2 task in ROOM_A ticks 5-6.
- [obs p-1:0:1] [tick 0] You saw p-2 task in ROOM_A.
- [tick 5] p-2 entered ROOM_A.
- [tick 1] p-2 left ROOM_A.
```
p-2 never moved. The window arithmetic matches: `_is_kill_window_sighting` (store.py:1040) fires for `0 <= body_tick - tick <= 3` (BODY_PROXIMITY_WINDOW_TICKS=3, beliefs.py:100), so ticks 1-4 are emptied, and `_collect_transitions` (suppression applied while BUILDING seen_in_own_room at store.py:1343; deltas emitted at store.py:1375+) reads the hole as movement.

CODE PATH re-read at HEAD: store.py:1343 `if _sighting_is_suppressed(...): continue` inside the `seen_in_own_room` build; store.py:1375/1385 emit `entered` on `now_seen - prev_seen` and `left` on `prev_seen - now_seen`. The `killed_in_room` guard at store.py:1370 only exempts a victim whose body is in that room/tick, so a live teammate is not covered.

NOT SPECIFIED: the shared predicate's own docstring states the OPPOSITE invariant -- store.py:1067-1071: "Shared by `_render_saw_player` ..., `_collect_co_presence` ... and `_collect_transitions` (the entered/left deltas) so a suppressed subject never re-surfaces through co-presence or a transition -- the firewall holds across all three Task 13.9 surfaces." The teammate DOES re-surface, by name, in two fabricated lines. No test pins the transition side: tests/agents/test_memory_rendering.py:553-611 covers only the sighting line (`test_impostor_teammate_at_body_scene_row_is_suppressed` asserts `"You saw p-1 in ADMIN" not in view` and nothing about transitions).

CORPUS REACHABILITY re-derived independently (my /private/tmp/.../wave0/B/v7_corpus.py + follow-ups, all 200 committed replays, impostor pair derived from kill/vent/sabotage actors): 5225 rendered prompts; 1242 impostor renders with a uniquely-known teammate (exactly the finder's 1242); 15,650 transition lines total; 462 naming the observer's teammate; 0 inside a same-room body window. Stronger negative control: 214 impostor renders carry BOTH a body-discovery line and a teammate transition line, and 0 of those pairs share a room. So the defect is live in code and absent from the committed baseline-7 corpus, exactly as claimed.

NOT A RE-REPORT: none of C-46/C-83/C-126/C-130/C-79/C-80/C-101/C-107/C-62/C-33/C-45, F1-F5, the replay_walk substrate gap, the 1440x900 gap or the duplicate alibi_vs_sighting mint. `grep -rn 'transition' audits/review-2026-08-19/B/agents-memory.md` returns only volume/complexity notes (:69,:76,:126,:167,:171,:183), never a fidelity claim.
```

**Verifier note.** Evidence reproduces on my own fixture and my own corpus scan; claim, P2 severity and 'defect' classification all stand. The strongest part of the finding is the one it states almost in passing: the fabricated pair is EXCULPATORY for the teammate across exactly the kill window, so the §4.7 firewall does not merely fail to hide the teammate, it mints a false alibi in the suppressed row's place -- and the render carries no [obs ...] id on a reconstructed line, so nothing downstream can trace it back. Zero corpus incidence means it cannot have poisoned the baseline-7 fit; it is a re-record hazard.

**Fix sketch.** Build `seen_in_own_room` from the UNSUPPRESSED sighting set (presence is the physical fact), and apply `_sighting_is_suppressed` to the emitted transition line instead — i.e. drop an `entered`/`left` whose subject is suppressed at either endpoint tick, rather than letting the suppression masquerade as absence. Add a test that a stationary teammate across a body window emits no transition line.

## B-37 — The non-elastic belief block renders rows for DEAD and EJECTED players, spending the fixed budget that the route and the observations are shed against

**Severity:** P2. **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** memory-render / belief block roster filter (agents/memory/store.py::_build_belief_lines, _known_roster_ids, _assemble_view). **Confidence:** high.
**Merged from:** finder-memory-render.json#4.

**Claim.** `_build_belief_lines` filters on `_known_roster_ids`, which deliberately keeps dead players, so belief rows about players the same prompt marks 'Dead or ejected -- never accuse' render unmarked inside the memory block, and are charged to the non-elastic budget ahead of the route and the observations. Measured on the committed corpus: of the 1715 rendered prompts that carry both a beliefs block and a dead/ejected roster line, 2335 of 6750 belief rows (34.6%) name a dead or ejected player and 1275 prompts (74.3%) carry at least one -- NOT the 25.8%/62.9% stated. The budget displacement lands on the ELASTIC OBSERVATIONS block, not the route: every truncated route in the corpus is the 12-span cap, not budget shedding.

**As originally filed.** `_build_belief_lines` filters on `_known_roster_ids`, which deliberately keeps dead players, so 25.8% of rendered belief rows name a player the same prompt tells the model it may never accuse — and those rows are charged to the non-elastic budget before the route and the observations are budgeted.

**Finder evidence.**

```
CODE. agents/memory/store.py:2099-2101 —
```
    for player_id in sorted(beliefs.known_players()):
        if roster is not None and player_id not in roster:
            continue
```
agents/memory/store.py:844-847 states the roster keeps the dead by design: "dead players stay in it, matching \"roster id\" (liveness is the meeting chokepoint's rule, not this set's)". No liveness channel reaches the render at all. Budget order: store.py:2296-2306 folds the belief block into `non_elastic_blocks`/`non_elastic_cost`; store.py:2314-2330 computes `remaining = token_budget - non_elastic_cost`, then charges the trail, then the observations.

CORPUS. Joining each prompt's `<players>` "Dead or ejected — never accuse: ..." line against its own `## Your current beliefs:` rows across all 200 replays:
```
prompts with a beliefs block: 1715
belief rows total: 6750 rows naming a DEAD/EJECTED player: 1744 (25.8 %)
prompts carrying >=1 dead belief row: 1078 (62.9 %)
```
and the displacement is measurable:
```
truncated routes: 166 of which carry >=1 dead belief row: 150
mean chars of dead belief rows per render: 56.6 = approx tokens: 14.1
```
(route truncation detected by the literal `Earlier parts of your route are not listed.` line, store.py:221.) A verbatim case: replays/ml_corpus/9p2i/replay-seed-1001.jsonl agent p-6 renders `- Meeting 1 (tick 10): p-2 EJECTED 5-1 — p-2 was an IMPOSTOR.` and, three lines later, `- p-2: suspicion 0.55` — a live suspicion row about a confirmed, already-ejected impostor.
```

**Verifier evidence (independent re-run).**

```
CODE (reproduces at HEAD): store.py:2100 `if roster is not None and player_id not in roster: continue` (and the twin contradiction filter at :2224); `_known_roster_ids` docstring store.py:844-847 keeps the dead by design; no liveness argument reaches `render_for_prompt` at all. Budget order confirmed: store.py:2296-2306 fold the beliefs block into `non_elastic_blocks`; :2314 `remaining = token_budget - non_elastic_cost`; :2318 charges the trail; :2326-2330 charges the observations. DEFAULT_TOKEN_BUDGET=1500 (store.py:45).

CORPUS recount (mine, all 200 replays, block parsed between `## Your current beliefs:` and the next blank line; dead set read from the prompt's own `Dead or ejected -- never accuse:` line):
```
blocks with a beliefs block AND a dead-line: 1715   <- finder's number, exact
belief rows in them:                        6750   <- finder's number, exact
rows naming a dead/ejected player:          2335 (34.6%)  <- finder said 1744 (25.8%)
  ... restricted to rows carrying a suspicion number: 1901 (28.2%)
blocks with >=1 dead row:                   1275 (74.3%)  <- finder said 1078 (62.9%)
across ALL 3427 rendered belief blocks:     2335/13558 rows (17.2%)
```
The denominators reproduce byte-exactly, so the derivation is the same; the dead-row numerators are UNDERSTATED by the finding under every reading I can construct. The claim is therefore conservative, not inflated.

DISPLACEMENT EVIDENCE REFUTED AS STATED: `_select_trail_within_budget` (store.py:2371-2386) emits `Earlier parts of your route are not listed.` for `shed = truncated or first > 0` -- i.e. the SAME line for the upstream 12-span cap (`SELF_LOCATION_TRAIL_MAX_SPANS=12`, store.py:218) and for budget shedding, so the literal cannot distinguish them. Counting spans in every truncated route in the corpus: 332 truncated routes, ALL 332 carrying exactly 12 spans (`{'spans_12': 332, 'trunc': 332}`). Zero committed renders show a budget-shed route. (332 vs the finder's 166 is the two-calls-per-agent-meeting factor: 332/2 = 166.) Where displacement is real is the elastic observations block: 963 of 5225 renders (18.4%) land within 50 tokens of the 1500-token budget (max observed 1486), so the ~74 chars/render of dead belief rows I measured are shed observations, not shed route.

VERBATIM CASE re-verified: replays/ml_corpus/9p2i/replay-seed-1001.jsonl agent p-6 renders `- Meeting 1 (tick 10): p-2 EJECTED 5-1 -- p-2 was an IMPOSTOR. 1 impostor remains.` and, in the same memory block, `- p-2: suspicion 0.55`, while `<players>` says `Dead or ejected -- never accuse: p-2, p-5`.

PARTIAL PRIOR REPORT (not one of the named known-open ids): Track A of the 2026-08-19 review already recorded this as `The dead never leave` -- audits/review-2026-08-19/A/s3-meeting-decisions.md:517, A/s4-info-economy-beliefs.md:30, A/w3-9p2i-random-a.md:112, A/w4-9p2i-random-b.md:147. Phase 20 shipped the mitigation on two OTHER surfaces -- the `<players>` `Dead or ejected -- never accuse` line, and the ballot suspicion graph's `-- OUT OF THE GAME (dead or ejected; voting them is wasted)` marker (agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:153, pinned at tests/agents/test_bespoke_prompt_sets.py:331-332) -- but not on the memory belief block. So B-37 is the residual of a partially-closed prior item, not net-new.
```

**Verifier note.** Core observation stands and the mechanism is exactly as described; three things must change. (1) The percentages are wrong and wrong in the finding's own disfavour -- 34.6%/74.3%, not 25.8%/62.9% (28.2% if you count only suspicion-bearing rows). (2) The 'displacement is measurable' evidence does not support the route half at all: 100% of corpus route truncations are the SELF_LOCATION_TRAIL_MAX_SPANS=12 cap, which the belief block's budget cannot cause; the honest displacement statement is about the observations block (18.4% of renders are budget-bound). (3) It is a residual of a known, partially-closed prior-review item, and the sharpest framing is the INCONSISTENCY the Phase-20 fix left behind: in a single vote_ballot prompt the suspicion-graph block marks a dead player `-- OUT OF THE GAME` while the memory belief block three blocks above lists the same player unmarked. Severity P2 / quality-debt unchanged.

**Fix sketch.** Thread the agent's own known-dead set (already derivable from `MeetingHistory.ejected_id` plus `saw_body` victim ids — both first-hand/public, no engine read) into `render_for_prompt` and skip belief + contradiction rows for it, or move the dead rows below the elastic line so they are shed first. Free budget goes straight to the route and the observations, which is the surface the physical-timeline testimony is copied from.

## B-38 — §6.3 Rule 1 cannot fire on the strongest circumstantial case: a player found STANDING with the body at the discovery tick takes zero body-proximity suspicion

**Severity:** P2. **Classification:** design-limitation. **Verdict:** CONFIRMED. **Area:** memory-render / belief pipeline / Rule 1 co-presence window (agents/perception.py::_recent_co_presence, agents/memory/beliefs.py::apply_observation_rules). **Confidence:** high.
**Merged from:** finder-memory-render.json#5.

**Claim.** The proximity window is built from strictly-prior ticks, and Rule 1 fires only on a body's FIRST sighting, so a subject the observer sees for the first time in the body's room on the discovery tick is never in `recent_co_presence` and never pinned — while a subject merely seen there one tick earlier is pinned to 0.70.

**Finder evidence.**

```
CODE. agents/perception.py:313-317 —
```
    earliest_tick = current_tick - BODY_PROXIMITY_WINDOW_TICKS
    for event in memory.recent(since_tick=earliest_tick):
        if event.type != EVENT_SAW_PLAYER or event.tick >= current_tick:
            continue
```
agents/memory/beliefs.py:1162-1178 then pins only players in that map, and skips any body already in `previous_visible_bodies` (perception.py:273-286), so the next tick — when the standing subject IS in the prior window — the body is no longer fresh and the rule never fires.

REPRO (scratchpad/wave0/B/repro_rule1.py; `PYTHONPATH=/Users/danielkeinan/projects/AiLibi uv run python .../repro_rule1.py`), driving the real `ingest_packet`:
```
standing-over-the-body p-2 suspicion: 0.5 SuspicionProvenance(... body_proximity=0.0 ...)
prior-tick co-presence p-2 suspicion: 0.7 SuspicionProvenance(... body_proximity=0.19999999999999996 ...)
```

CORPUS REACHABILITY. Counting rendered memories that state a body discovery at tick T in room R AND a sighting of another player at the same tick T in the same room R:
```
renders: 5225
same-tick 'found the body WITH someone standing there' pairs: 613
  ... of which the subject carries NO belief row at all (neutral 0.50): 296
```
A verbatim case (replays/ml_corpus/9p2i/replay-seed-1001.jsonl, agent p-6): `- [obs p-6:13:3] [tick 13] You discovered p-5's body in MEDBAY.` and `- [obs p-6:13:2] [tick 13] You saw p-7 in MEDBAY (with p-3).`, with no `p-7` row anywhere in that prompt's `## Your current beliefs:` block.

DESIGN CHECK. DESIGN.md:676 says `+0.2 suspicion` if seen near a body "shortly before discovery", so the implementation matches the letter of the design — this is headroom the design left, not a violation of it.
```

**Verifier evidence (independent re-run).**

```
CODE re-read at HEAD: agents/perception.py:313 `earliest_tick = current_tick - BODY_PROXIMITY_WINDOW_TICKS` and :316 `if event.type != EVENT_SAW_PLAYER or event.tick >= current_tick: continue` -- the window is `[T-3, T-1]`, strictly prior. agents/memory/beliefs.py:1163-1178 derives `co_present` EXCLUSIVELY from `recent_co_presence.get(body.room, ())`, so an empty map is an unconditional no-pin. agents/perception.py:273-286 `_previously_seen_body_ids` makes Rule 1 first-sighting-only, so the next tick -- when the standing subject IS in the prior window -- cannot recover it.

INDEPENDENT DIRECT PROBE (my own, calling the real function):
```
$ PYTHONPATH=. uv run python -c "..."
current_tick=5 (same tick as discovery): {}
current_tick=6 (body one tick later):   {'MEDBAY': [(5, 'p-2')]}
```
One `saw_player` row for p-2 in MEDBAY at tick 5: invisible to Rule 1 when the body surfaces at tick 5, worth the full `BODY_PROXIMITY_SUSPICION_DELTA=0.2` HARD pin when it surfaces at tick 6. That is the finding's 0.50-vs-0.70 result, obtained without its fixture.

CORPUS: my scan reproduces the headline pair count EXACTLY -- 613 same-tick 'body in R at tick T' + 'saw X in R at tick T' pairs over 5225 renders. My count of subjects carrying no belief row at all is 339, vs the finding's 296 (a sighting-line regex difference; same direction, same order). VERBATIM CASE re-verified in replays/ml_corpus/9p2i/replay-seed-1001.jsonl agent p-6: `- [obs p-6:13:3] [tick 13] You discovered p-5's body in MEDBAY.` and `- [obs p-6:13:2] [tick 13] You saw p-7 in MEDBAY (with p-3) ...`, with the whole beliefs block reading `p-1 / p-2 / p-3 / p-4` and no p-7 row.

SPECIFIED, AND THE FINDING SAYS SO: DESIGN.md:676 `+0.2 suspicion if seen near a body shortly before discovery. (Rule 1 -- live.)`. The strictly-before window is deliberately mirrored in two more places -- orchestrator/game.py:3072-3099 `body_proximity_records_for_meeting` ("within BODY_PROXIMITY_WINDOW_TICKS ticks strictly before the discovery") and its offline twin `training/surrogate/dataset.py::_absorb_body_proximity` -- so widening it is a three-site substrate change, not a bug fix. `design-limitation` is the correct classification and the finding assigns it.

NOT A RE-REPORT: `grep -rn 'BODY_PROXIMITY|body_proximity|Rule 1' audits/review-2026-08-19/` returns only orchestrator.md:39 (cyclomatic complexity) and perf-runtime.md:253 (a full-log-scan perf note). Not in the named known-open list either.
```

**Verifier note.** Confirmed as written, including its own honest DESIGN CHECK. Two things worth carrying forward to whoever prices the lever. (1) The gap is not rare-by-construction: it bites hardest exactly when the observer WALKS IN and finds a body, because then every player in that room is a first sighting at the discovery tick -- the reporter's own scene. (2) The fix is not the one-line `>` -> `>=` the sketch implies: the same strictly-before join is re-derived in orchestrator/game.py:3072-3099 and training/surrogate/dataset.py, and the docstring at perception.py:300-303 leans on the exclusion for call-order independence (`safe to call after the tick's rows are appended`), so widening it must be done at all three sites plus that ordering guarantee, or the live belief graph and the conviction model's features silently disagree.

**Fix sketch.** Widen the Rule-1 window to `[current_tick - BODY_PROXIMITY_WINDOW_TICKS, current_tick]` inclusive (one `>` -> `>=` and dropping the `event.tick >= current_tick` guard in perception.py:316), keeping the victim and teammate exclusions. It is a candidate re-ground lever rather than a bug fix: it is a HARD (`body_proximity`) channel, so it moves the J1 hard/soft split and the conviction model's most informative physical feature — size it against the 15.5 reporter cap first, since the reporter is always at the body by construction.

## B-39 — Only ONE rendered-memory line class has a fidelity instrument; the belief block and the reconstructed transitions have none

**Severity:** P3 (finder: P2). **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** memory-render / machinery / eval instrumentation (eval/evidence_honesty.py). **Confidence:** high.
**Merged from:** finder-memory-render.json#6.

**Claim.** The evidence-honesty suite's only render-FIDELITY gauge is I-5 over `You completed` lines: of the ten pre-registered cells, one scores a rendered line against engine truth and the rest score spoken claims, transcript/prompt text or engine facts. The other derived render surfaces -- the belief block's last-seen and alibi suffixes, the directional breadcrumb, the reconstructed entered/left transitions, the coalesced span tick ranges -- have no corpus-scale re-derivation instrument. This is the structural reason B-36 (the fabricated transitions) could ship unnoticed; it is NOT the reason B-37 or B-38 survived, since neither is a render-fidelity failure.

**As originally filed.** The evidence-honesty suite's only render-fidelity gauge is I-5 over `You completed` lines, so every other derived render surface — the belief block's last-seen and alibi suffixes, the directional breadcrumb, the reconstructed `entered`/`left` transitions, the coalesced span tick ranges — ships un-audited, which is the structural reason the three defects above survived.

**Finder evidence.**

```
CODE. eval/evidence_honesty.py:268-271 defines the one render-line pattern:
```
_COMPLETED_LINE: Final[re.Pattern[str]] = re.compile(
    r"^- \[obs (?P<observation_id>[^\]]+)\] \[tick (?P<tick>\d+)\] "
    r"You completed (?P<task>\S+) \(you were in (?P<room>[^)]+)\)\.$",
```
and eval/evidence_honesty.py:294-365 enumerates the ten pre-registered instruments I-2..I-11; only I-5 reads a rendered memory line ("numerator: distinct rendered You completed memory rows with no task_completed engine event for that agent at any earlier tick"). I-2/I-4/I-7 audit SPOKEN claims, not the render they were copied from. `grep -rn "last seen\|last_seen" --include="*.py" eval/` returns only eval/funnel.py's unrelated `last_seen_with_killer` funnel cell — nothing reads the belief-line suffix.

CORROBORATION that instrumenting works: I-5's own calibration constant `AGENT_CLOCK_OFFSET: Final[int] = 1` (eval/evidence_honesty.py:215) correctly captures the packet-clock convention — packets are built from the PRE-`advance_tick` state (orchestrator/game.py:1844-1856) while `TaskCompletedEvent` carries `tick=state.tick` (engine/tick.py:99-106) — verified against a recorded game: p-6's `do_task log_findings` actions run ticks 7-11 in replays/ml_corpus/9p2i/replay-seed-1001.jsonl and the render states `[tick 12] You completed log_findings`. That surface is right BECAUSE it has an instrument; the surfaces without one are not.
```

**Verifier evidence (independent re-run).**

```
CODE reproduces at HEAD. eval/evidence_honesty.py:268-272 `_COMPLETED_LINE` is the only rendered-line pattern scored against engine truth (`_fold_completion_rows` at :1865-1900 joins it to `completions` and increments `fabricated_lines` / `render_offset_matches`). The two other render-touching patterns are pure VOLUME census, not fidelity: `_RENDERED_ROW` (:285) and `_TESTIMONY_ROW` (:289) are consumed only at :1839-1843 as `tallies.rendered_lines` / `tallies.testimony_rows`. CELL_DEFINITIONS (:294-365) enumerates I-2..I-11 and exactly one -- I-5 -- is defined over a rendered memory row; I-2/I-4/I-7 are defined over SPOKEN claims joined to the reconstructed episodic store, not to the render bytes. The `last_seen` grep reproduces: `grep -rn 'last seen|last_seen' eval/*.py` hits only eval/funnel.py's unrelated `last_seen_with_killer` funnel cell (:97,:683,:704,:731,:841,:883,:935,:1012).

I-5's calibration corroboration also reproduces: `AGENT_CLOCK_OFFSET: Final[int] = 1` is real and load-bearing at :1897-1899, and the corpus bears the convention out (an impostor prompt in replays/ml_corpus/9p2i shows `[tick 2] You saw p-2 move from WEST_HALL to MEDBAY` for a tick-1 move action).

WHY ADJUSTED -- two overreaches. (a) 'ships un-audited' is too strong: eval/leak_scan.py:263 `assert_memory_render_role_disclosure_is_entitled` DOES audit the rendered memory string (role-disclosure entitlement, stated independently of the render code -- store.py:340-345 cites it as the second statement of the rule), and the derived surfaces carry unit coverage in tests/agents/test_memory_rendering.py. What is missing is a corpus-scale re-derivation gauge, not all auditing. (b) The causal claim 'the structural reason the three defects above survived' holds for B-36 only. B-38 lives entirely in agents/perception.py + agents/memory/beliefs.py and never touches the render, so no render instrument could see it. B-37's dead rows are FAITHFUL renderings of the belief state -- a policy question about what to render, which a fidelity check by construction passes. Of the four sketched instruments (a)-(d), only (c) targets a defect actually demonstrated in this wave.

SEVERITY: lowered P2 -> P3. This is a coverage-gap meta-finding, not a code defect; its single demonstrated miss (B-36) has zero incidence in the committed corpus, so no published gate number is wrong today and nothing blocks. P3 also matches how the set treats non-blocking meta items (3 of 56 canonical items are already P3).

NOT A RE-REPORT of any named known-open item.
```

**Verifier note.** The core observation is real, cheap to act on, and correctly aimed -- one instrument family over the walk's own episodic reconstruction would turn B-36 into a counter. But the finding borrows severity from the two neighbours it cannot actually explain: strip B-37 and B-38 out of its causal claim and what remains is 'one of four derived render surfaces has a gauge', with one zero-incidence latent miss to show for it. Keep it, at P3, and scope its sketch to (c) plus (a)/(b)/(d) as speculative coverage.

**Fix sketch.** Add a render-fidelity instrument family alongside I-5, each a pure re-derivation from the walk's own episodic reconstruction rather than from the render code: (a) every `last seen in R at tick T` equals the argmax-tick sighting in that agent's log; (b) every `(moved from X, last seen there at tick T)` names the agent's true latest sighting in X; (c) every `[tick T] S entered/left R` has a corresponding presence delta in the agent's UNSUPPRESSED sighting log; (d) every coalesced `ticks A-B` span has a row at every tick in [A,B]. These are cheap regex-plus-log checks over the same recorded prompts the corpus already carries, and they turn the three defects above into gate-visible counters before the re-ground touches the fit.

## B-40 — I-4's grounding search reads the speaker's END-OF-GAME memory, not the memory they held when they spoke

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** eval-instruments / evidence_honesty I-4. **Confidence:** high.
**Merged from:** finder-eval-instruments.json#4.

**Claim.** `_fold_meetings` runs after the whole walk and hands `_fold_grounding` the final MemoryStore, so a STRONG sighting can be scored "grounded" by a perception the speaker only acquired after the meeting — a look-ahead the cell's own definition ("whether the speaker COULD have seen it") forbids.

**Finder evidence.**

```
eval/evidence_honesty.py:1441-1461: the walk's `for walk_event in walk_replay(...)` loop closes at :1439 and only then does `_fold_meetings(... memories=memories ...)` run at :1450-1461; `memories` is the same dict mutated by `_perceive_tick` on every TickOpened (:1392-1393). `_fold_grounding` then scans `memory.recent(since_tick=0)` (eval/evidence_honesty.py:2360-2364), i.e. the whole game's log, and admits any supporting row with `abs(event.tick - resolved.sighting.tick) <= 2` (:2361, :2368-2370). Blast radius today is ZERO and unobservable: every alibi_vs_sighting flag in all four committed sets is WEAK (`is_weak_contradiction` True for 71/71 in ml_corpus/9p2i and 29/29 in samples/9p2i), so `compute_evidence_honesty(Path('replays/ml_corpus/9p2i')).grounded_sighting` reads `strong_sides=0, resolvable_sides=0` and every I-4 cell is 0/0 (matching the committed pin at tests/eval/test_evidence_honesty.py:1356-1360, `assert sides == [0, 0, 0, 0]`). I verified the same exposure on the populated sibling cell: a per-meeting memory-prefix replay (snapshot `len(memories[pid])` at MeetingOpened, then re-fold I-7 over the prefix vs the full log) returns identical counts on both 9p2i sets (`move_backed_full`=`move_backed_prefix`=31 on ml_corpus, 16 on samples; `spoken_tick_after_meeting`=0), so no committed number moves — the defect is latent, not live.
```

**Verifier evidence (independent re-run).**

```
CODE reproduces at HEAD, line-for-line. eval/evidence_honesty.py:1383 opens `for walk_event in walk_replay(...)`; the loop body ends and `finally:` lands at :1437; `_fold_meetings(... memories=memories ...)` runs at :1450, i.e. after the whole walk. `memories` is the same dict `_perceive_tick` mutates on every TickOpened (:1392-1393). `_fold_grounding` then scans the WHOLE log -- :2362 `for event in memory.recent(since_tick=0)` -- and scores at :2367-2370 (`nearest = min(gaps)`, `grounded_within_2/1/at_tick`), with `gaps` built from `abs(event.tick - resolved.sighting.tick)` at :2358-2363. So a supporting first-hand row the speaker only acquired AFTER the meeting is admissible, which contradicts the cell's own definition at :311-317 ('only whether the speaker could have seen it').

BLAST RADIUS ZERO -- independently corroborated two ways. (1) My own scan of the committed contradiction records: all 71 `alibi_vs_sighting` flags in replays/ml_corpus/9p2i and all 29 in replays/samples/9p2i carry the `[weak signal: ...]` marker in their description; 0 STRONG in either set (and 0 alibi_vs_sighting at all in the 4p1i sets). (2) The committed pin tests/eval/test_evidence_honesty.py:1355-1360 asserts `sides == [0, 0, 0, 0]` and `unresolvable_sides == 0`, so every I-4 cell is 0/0 across all four sets. No committed number moves.

SCOPE NARROWING (tightens, does not refute): the look-ahead window is bounded by the tolerance, not open-ended. A supporting row must satisfy `abs(event.tick - sighting.tick) <= 2` (:2368), and a spoken sighting tick is at or before the meeting, so only a sighting spoken about a tick within 2 of the meeting can be grounded by post-meeting perception. Narrow, but real and unguarded.

A POSITIVE worth recording alongside it: hearsay CANNOT contaminate this cell. `_fold_meeting_into_memories` (:1299) runs inside the loop and `absorb_reported_testimony` (agents/memory/store.py:575-640) appends `EVENT_REPORTED_TESTIMONY` rows, while `_supports_placement` (:2325-2340) admits only `EVENT_SAW_PLAYER` and `EVENT_SAW_PLAYER_MOVE` -- so a LATER meeting's absorbed testimony is not a second look-ahead vector.

NOT VERIFIED BY ME: the finding's I-7 memory-prefix corroboration experiment (a full re-walk; out of scope for a read-only pass). It is not load-bearing -- the committed 0/0 pin already establishes zero blast radius for I-4 itself.

NOT A RE-REPORT: distinct from the named 'duplicate alibi_vs_sighting mint' known-open item (that one is about the same flag being minted twice; this is about which memory prefix I-4 reads) and from every other named id.
```

**Verifier note.** Confirmed as written -- a latent correctness bug in an instrument, with the blast radius honestly stated by the finding itself and independently re-verified here from both the raw flag records and the committed test pin. P2 is defensible on the finding's own argument: the cell is 0/0 today, so nothing is wrong on any published page, but the first lever that repopulates the STRONG alibi_vs_sighting class publishes an inflated grounded rate with no earlier number to compare it against. The fix is small and local (snapshot `len(memories[pid])` at MeetingOpened, which `_fold_game` already visits, and bound the row scan) and should ride ahead of any balance-wave re-record rather than after it.

**Fix sketch.** Snapshot each speaker's memory length at MeetingOpened (the walk already yields that event and `_fold_game` already collects `_MeetingFacts` there) and pass the prefix to `_fold_grounding` / `_fold_movement_origin`, or equivalently bound the row scan at the meeting's trigger tick. Worth fixing before any lever re-populates the STRONG alibi_vs_sighting class, because the first re-record that does will silently publish an inflated grounded rate with nothing to compare it against.

## B-41 — The replay_walk substrate-check gap is inert on every committed byte today — the exposure is the CLI path, which never runs the validity gate

**Severity:** P3 (finder: P2). **Classification:** known-open re-report (design-limitation, latent). **Verdict:** ADJUSTED. **Area:** eval-instruments / replay_walk (DEEPENS the known-open substrate-check gap). **Confidence:** high.
**Merged from:** finder-eval-instruments.json#5.

**Claim.** RE-REPORT of the known-open replay_walk substrate-check gap, already routed in-repo. The mechanism reproduces (eval/replay_walk.py:406-412 re-seeds with no stamp read; `retired_levers_stamped_off` has exactly one production caller, audits/workflows/extract_gameplay_facts.py:169,2169; none of compute_evidence_honesty / compute_solvability_report / compute_watchability reads a stamp) and the finder's own census confirms it is INERT on every committed byte. Two corrections: (a) the census line is mislabeled -- `retired_levers_stamped_off` returns [] (empty) on all 300 files, NOT ('impostor_roll_call',); impostor_roll_call is the single LIVE TOGGLE (TOGGLEABLE_SUBSTRATE_FLAG_KEYS == ('impostor_roll_call',)), default-OFF, and is not one of the 21 retired levers -- the finder printed 'flags that read False', not the function's output. The conclusion it draws (21/21 retired levers True on every file) is nevertheless correct. (b) The named 'exposed path' is weak: scripts/measure_baseline.py's own module docstring declares it 'a MEASUREMENT on a valid baseline ... not a gate', with the gate living in the separate scripts/validity_gate.py CLI -- so its lack of a validity-gate call is the documented division of labour, not a new hole.

**As originally filed.** Known item, current state verified: `walk_replay` still re-seeds and re-advances with no substrate-stamp read, but all 300 committed replays stamp the 21 retired levers ON, so the blast radius is entirely on operator-supplied dirs — and the exposed path is `scripts/measure_baseline.py`, which calls the instruments directly and never runs the one guard that does check (`eval.validity.run_validity_gate`).

**Finder evidence.**

```
The gap: eval/replay_walk.py:406-412 seeds via `seed_initial_state(...)` with no stamp read, and `retired_levers_stamped_off` has exactly one production caller — `grep -rn "retired_levers_stamped_off" --include="*.py" .` returns audits/workflows/extract_gameplay_facts.py:169,2169 plus orchestrator/replay.py:623 and tests. Stamp census over every committed recording (json read of the `game_over` row's `substrate_flags`, 300 files under replays/): all 300 read `n=22 off=('impostor_roll_call',)` — i.e. 21/21 retired levers True on every file, so no committed consumer mis-reconstructs. The guard that does exist is `run_validity_gate` (eval/validity.py:1138ff; the per-seed stamp read at :1187 feeding `check_cost_and_provenance` at :900, whose stamp comparison against `substrate_flag_snapshot()` runs at :931-962), reached by training/bakeoff/harness.py:110 and training/crew/scorer.py:117 — but `grep -n "run_validity_gate" scripts/measure_baseline.py` returns nothing, and neither `compute_evidence_honesty` (eval/evidence_honesty.py:861) nor `compute_solvability_report` (eval/solvability.py:396) nor `compute_watchability` (eval/watchability.py:2096) reads the stamp.
```

**Verifier evidence (independent re-run).**

```
1) `grep -rn retired_levers_stamped_off --include=*.py .` -> audits/workflows/extract_gameplay_facts.py:169,2169; orchestrator/replay.py:623 (def); rest are tests. No eval/ or scripts/ caller. REPRODUCES.
2) eval/replay_walk.py:406-412 read: `state = seed_initial_state(seed=..., game_map=..., num_players=..., num_impostors=..., tasks_per_crewmate=...)` with no substrate read. REPRODUCES.
3) My own census, `PYTHONPATH=. uv run python` over all `replays/**/replay-seed-*.jsonl`, calling orchestrator.replay.retired_levers_stamped_off on each file's substrate_flags row:
   files 300
   (22, ()) 300
   i.e. every file: 22 keys, ZERO retired levers stamped off. Spot-check of replays/ml_corpus/9p2i/replay-seed-1001.jsonl shows the only False key is `impostor_roll_call`.
   `PYTHONPATH=. uv run python -c "from orchestrator.replay import _RETIRED_ALWAYS_ON_LEVERS, TOGGLEABLE_SUBSTRATE_FLAG_KEYS, SUBSTRATE_FLAG_KEYS; ..."` -> retired 21, toggleable ('impostor_roll_call',), all 22. So the finder's `off=('impostor_roll_call',)` is a mislabel of its own census, not the function's return.
4) `grep -n run_validity_gate scripts/measure_baseline.py` -> no match (exit 1). CONFIRMED. Production callers of run_validity_gate: training/crew/scorer.py:117/1700, training/bakeoff/harness.py:110/1757, training/bakeoff/goodhart.py:91/455/1582, scripts/validity_gate.py:104. eval/validity.py:1186-1191 reads the per-seed stamp; :931-962 compares it to substrate_flag_snapshot(). REPRODUCES.
5) `grep -n substrate eval/evidence_honesty.py eval/solvability.py eval/watchability.py` -> only prose mentions, no read_substrate_flags call. REPRODUCES.
6) Known-open provenance: audits/audit-phase-20-close.md:408 -- "**`eval/replay_walk.py` performs no substrate check.** ... The one-line fix is the now-public `orchestrator.replay.retired_levers_stamped_off`. Routed with 20.37's merge record (`a9952d29`); a next-phase item, not a close edit." This is the same item, already recorded and routed.
7) scripts/measure_baseline.py:1-6 docstring: "The R-gate is a MEASUREMENT on a valid baseline ... not a gate".
```

**Verifier note.** Verdict is ADJUSTED, not REFUTED: the code gap is real and reproduces exactly as filed. But it is the named known-open item on the reviewer's exclusion list, the finder's own measurement establishes zero realized exposure on 300/300 committed recordings, the census label in its evidence block is wrong, and the one piece of genuinely new content (the measure_baseline CLI path) is contradicted by that file's own declared scope. P2 -> P3, and it should be filed under the existing routed item rather than as a fresh finding.

**Fix sketch.** The routed one-liner belongs at the three sample_dir entry points, not only inside walk_replay: refuse on a non-empty `retired_levers_stamped_off(read_substrate_flags(path))` in `compute_evidence_honesty` / `compute_solvability_report` / `compute_watchability` (all three already fail loud on a dir with no replay-seed files, so the refusal shape exists). Cheap now, and it is the only thing standing between a re-ground operator pointing an instrument at an archived pre-graduation dir and a silently re-scored cell.

## B-42 — The degeneracy detector is one-sided: `degenerates_to_skip` cannot see an all-EJECT collapse

**Severity:** P3 (finder: P2). **Classification:** quality-debt (incomplete diagnostic, already recorded in prose). **Verdict:** ADJUSTED. **Area:** training-path / training/surrogate/fidelity.py (SurrogateFidelityReport). **Confidence:** high.
**Merged from:** finder-training-path.json#3.

**Claim.** The asymmetry is real and reproduces exactly: `degenerates_to_skip` (training/surrogate/fidelity.py:820-822) requires `2 * ejection_pred_skips > ejection_meetings`, which an all-EJECT head (ejection_pred_skips == 0) can never satisfy, and its decision accuracy is EXACTLY always_eject_baseline because the decision is binary on None-ness (fidelity.py:740-746) so correct_skip == 0 and correct_eject == ejection_meetings. No `degenerates_to_eject` field exists in SurrogateFidelityReport. HOWEVER the claim's framing must be narrowed: this is a DIAGNOSTIC-only blind spot, not a gate hole. `degenerates_to_skip` is consumed by no verdict -- decide_go_no_go (fidelity.py:1027-1031) reads only meets_ceiling_bar / beats_prior_baseline / beats_always_eject, and axis 3 is a STRICT `>` (`surrogate.skip_vs_eject_accuracy > surrogate.always_eject_baseline`), so an all-EJECT SURROGATE ties the constant and is rejected NO-GO by construction. And the field is documented as one-sided by its own docstrings (fidelity.py:513-515 and :818-819 both scope it to 'the FO-6 always-SKIP collapse'), so nothing in the code makes a false claim. The residual gap is that the FO-6 COMPARATOR's degeneracy (whose top-1 still sets the axis-2 floor) is recorded only in prose.

**As originally filed.** The report has a flag for the always-SKIP collapse but none for the opposite always-EJECT collapse, and an all-EJECT head scores decision accuracy EXACTLY equal to `always_eject_baseline`, so on the previous corpus a degenerate FO-6 head shipped with `degenerates_to_skip=False` and no flag at all.

**Finder evidence.**

```
training/surrogate/fidelity.py:819-822
  degenerates_to_skip=ejection_meetings > 0
  and 2 * ejection_pred_skips > ejection_meetings
  and decision_accuracy <= always_eject_baseline,
There is no `degenerates_to_eject` field anywhere in SurrogateFidelityReport (:509-560). An always-EJECT head has `predicted_skips == 0`, so `ejection_pred_skips == 0` and the first conjunct is False regardless of how degenerate it is; its decision accuracy is exactly `ejection_meetings / meetings_scored == always_eject_baseline`.
The committed record documents the resulting blind spot in prose but nothing gates on it — training/reports/report-ballot-surrogate.md:274:
  | `degenerates_to_skip` | **False** - the head degenerates the OTHER way (all-EJECT), which on an eject-majority mix ties the always-eject constant, so the skip-era flag reads False by its own formula |
```

**Verifier evidence (independent re-run).**

```
1) training/surrogate/fidelity.py:818-822 read verbatim:
     # Always-SKIP collapse: the decision head skips the MAJORITY of true
     # ejection meetings AND is no better than the trivial always-eject constant.
     degenerates_to_skip=ejection_meetings > 0
     and 2 * ejection_pred_skips > ejection_meetings
     and decision_accuracy <= always_eject_baseline,
   REPRODUCES verbatim.
2) `grep -n degenerates_to_eject -r training/ tests/ scripts/ docs/ audits/` -> no match. No symmetric field. CONFIRMED.
3) Arithmetic re-derived from source: fidelity.py:740-746 counts the decision as correct iff `(predicted is None) == (true_eject is None)`; :788-793 `decision_accuracy = (correct_skip + correct_eject)/meetings_scored`, `always_eject_baseline = ejection_meetings/meetings_scored`. All-EJECT head => predicted never None => correct_skip=0, correct_eject=ejection_meetings => decision_accuracy == always_eject_baseline EXACTLY, and ejection_pred_skips == 0 so conjunct 2 is False. CONFIRMED.
4) training/reports/report-ballot-surrogate.md:274 reproduces verbatim: "| `degenerates_to_skip` | **False** - the head degenerates the OTHER way (all-EJECT), which on an eject-majority mix ties the always-eject constant, so the skip-era flag reads False by its own formula |" (with :273 recording 'decision census (predicted) | 96 ejections . 0 skips').
5) NEW (mine): fidelity.py:1027-1031 `beats_always_eject = surrogate.skip_vs_eject_accuracy > surrogate.always_eject_baseline` -- STRICT. is_go = meets_ceiling_bar and beats_prior_baseline and beats_always_eject. `degenerates_to_skip` appears nowhere in decide_go_no_go or GoNoGoVerdict. So an all-EJECT surrogate scores exactly the constant, fails axis 3, and gets NO-GO regardless of the missing flag.
6) fidelity.py:513-515 field docstring: "``degenerates_to_skip`` trips when the tuned decision head predicts SKIP on EVERY ejection meeting (the FO-6 always-SKIP collapse, SS5.2)" -- explicitly scoped, no over-claim.
```

**Verifier note.** Observation fully confirmed; only the consequence is overstated. Because no GO/NO-GO verdict can be wrong from this (axis 3's strict inequality already rejects an exactly-tying all-EJECT surrogate) and the blind spot is already written down in the committed report, this is an instrument-completeness item rather than a defect. Worth doing exactly as sketched before the re-ground re-takes the reading on a new mix, but at P3.

**Fix sketch.** Add the symmetric field (`degenerates_to_eject`: `skip_meetings > 0 and 2 * skip_predicted_ejections > skip_meetings and decision_accuracy <= max(always_eject_baseline, 1 - always_eject_baseline)`), or replace both with one `decision_head_degenerate` computed against BOTH trivial constants. The re-ground re-takes this reading on a new mix, so shipping with only the skip-side flag means the next collapse is again invisible in the machine-readable row and visible only in prose.

## B-43 — TRUNCATED_EPISODE_FITNESS (-10.0) is not below every reachable full-game fitness once the anchor penalty applies

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** training-path / training/bakeoff/harness.py (fitness floor). **Confidence:** high.
**Merged from:** finder-training-path.json#6.

**Claim.** The anchor cross-entropy is clamped at -log(1e-6) = 13.8155 nats and subtracted at weight 1.0, so a legitimate complete episode can score as low as -14.82 — below the -10.0 assigned to a truncated episode — giving the optimizer a degenerate escape hatch in which stalling the scheduler outranks playing a full but off-anchor game.

**Finder evidence.**

```
training/bakeoff/harness.py:207-212
  # The explicit fitness assigned to a truncated (tick-budget-capped) episode. ... scores this
  # documented constant - well below any reachable full-game fitness - ...
  TRUNCATED_EPISODE_FITNESS: Final[float] = -10.0
harness.py:199 `ANCHOR_CE_EPSILON: Final[float] = 1e-6`; :488-491 clamps `probability` to that epsilon and accumulates `-math.log(probability)` = 13.8155 per off-menu decision; :512-517 `mean_anchor_ce` is the plain mean, so its range is [0, 13.8155].
harness.py:943-948
  if not rollout.complete: return TRUNCATED_EPISODE_FITNESS
  shaped = compute_shaped_reward(rollout, "IMPOSTOR").total()
  fitness = shaped - anchor_weight * trace.mean_anchor_ce()
Minimum reachable `shaped` for a complete impostor episode is -1.0 (terminal loss, zero kills, zero unwitnessed, survival 0 with both impostors ejected, zero meetings survived, shaping 0 — every dense term in training/rewards.py:219-236 is non-negative and floors at 0). So min full-game fitness = -1.0 - 1.0 * 13.8155 = -14.8155 < -10.0. `crew_inner_episode_fitness` (training/crew/scorer.py:996-998) uses the same constant and the same unbounded penalty.
```

**Verifier evidence (independent re-run).**

```
1) Constants read verbatim. training/bakeoff/harness.py:199 `ANCHOR_CE_EPSILON: Final[float] = 1e-6`; :207-212 comment "The explicit fitness assigned to a truncated (tick-budget-capped) episode ... scores this documented constant - well below any reachable full-game fitness -" then `TRUNCATED_EPISODE_FITNESS: Final[float] = -10.0`. REPRODUCES.
2) harness.py:488-491 `probability = distribution.get(anchor_key, 0.0)` / `if probability < ANCHOR_CE_EPSILON: probability = ANCHOR_CE_EPSILON; self.offmenu_decisions += 1` / `self.anchor_ce_sum += -math.log(probability)`; :512-517 `mean_anchor_ce` is the plain mean. So the per-decision term is clamped at -log(1e-6) = 13.815510557964274 and the mean's range is [0, 13.8155]. REPRODUCES.
3) harness.py:943-948 `if not rollout.complete: return TRUNCATED_EPISODE_FITNESS` / `shaped = compute_shaped_reward(rollout, "IMPOSTOR").total()` / `fitness = shaped - anchor_weight * trace.mean_anchor_ce()`; DEFAULT_ANCHOR_PENALTY_WEIGHT = 1.0 (:205). REPRODUCES.
4) Floor of `shaped` INDEPENDENTLY re-derived from training/rewards.py rather than taken on trust: ShapedReward.total() = terminal + dense + shaping at 1/1/1 (:203-210, :198-201). `_impostor_terms` (:214-232) returns kills>=0, unwitnessed_kills>=0, survival = impostors_alive/max(1,num_impostors) >= 0, meetings_survived>=0 -- every term non-negative. `_side_potential` (:99-117) returns `float(frame.cumulative_kills)` for IMPOSTOR, so at gamma=1 shaping_sum = terminal kill count >= 0. `_terminal_reward` (:296-300) is exactly +-1.0. => min complete-episode shaped = -1.0. Same for crew (`_crew_terms` :234-278 all non-negative; potential = tasks_completed >= 0).
   => min full-game fitness = -1.0 - 1.0 * 13.8155 = -14.8155 < -10.0. The comment's invariant is FALSE. CONFIRMED.
5) No pin exists: `grep -rn TRUNCATED_EPISODE_FITNESS tests/` -> tests/training/test_crew_scorer.py:70,617; tests/training/test_coevo_rollout.py:22,57,247,248 -- all assert the sentinel is RETURNED on truncation; none asserts the ordering invariant. CONFIRMED.
6) Not a declared carry: `grep -rn TRUNCATED_EPISODE_FITNESS --include=*.md .` -> only audits/review-2026-08-19/B/verdicts.md:219, which is about a DIFFERENT point (silent floor score vs the docstring's implied loud raise), not the ordering. Not a re-report.
7) CALIBRATION (mine, added): the hatch needs mean anchor CE > 9.0 nats (since -1 - ce < -10). Measured over every committed results row -- `results-impostor-bakeoff.jsonl` max anchor_cross_entropy 2.0157, `results-crew-track.jsonl` 0.6756, `results-crew-owned-tasks.jsonl` 0.4414, campaign `moving_anchor_ce_mean` max 2.9715 -- and `anchor_offmenu_decisions` is 0 on EVERY row, truncated_episodes_real 0/0/1. The documented ANCHOR_CE_CEILING = 2.0 (harness.py:194) FLAGS (never drops, :193) 4.5x before the inversion bites.
```

**Verifier note.** Arithmetic, code, and absence-of-pin all reproduce exactly, and the source comment states an invariant that is provably false. Kept at P2 rather than downgraded despite zero realized exposure, because off-menu is a STEP function, not a drift: `distribution.get(anchor_key, 0.0)` jumps straight to the 13.8155 clamp whenever the candidate's intent menu simply does not contain the FSM's proposal, so ~65% off-menu decisions is enough to invert the ordering -- exactly the kind of discontinuity a re-ground with a moved intent vocabulary can trip wholesale, and nothing would catch it. The fix sketch's clamp-at-ANCHOR_CE_CEILING option is the cheaper of the two (that constant already exists at harness.py:194).

**Fix sketch.** Either derive the truncation constant from the reachable floor (e.g. `min_full_game_fitness - 1.0`, computed from the terminal weight and `anchor_weight * -log(ANCHOR_CE_EPSILON)`) or clamp the per-decision anchor CE at ANCHOR_CE_CEILING (2.0) rather than at -log(epsilon), which also stops one off-menu decision from dominating an episode's mean. Add a test that asserts `TRUNCATED_EPISODE_FITNESS < terminal_min - anchor_weight * -log(ANCHOR_CE_EPSILON)` so the invariant the comment claims is actually pinned.

## B-44 — The co-evolution substrate fence compares two operator-supplied values and never recomputes the substrate from the corpus

**Severity:** P2. **Classification:** design-limitation (unverified declaration; the check is placed at the operator layer by precedent, not absent from the program). **Verdict:** ADJUSTED. **Area:** training-path / training/coevo/driver.py + training/bakeoff/map_elites.py (stale-cell fence). **Confidence:** high.
**Merged from:** finder-training-path.json#9.

**Claim.** The library-level gap reproduces exactly: `_validate_campaign_config` regex-checks `substrate_sha256` only (training/coevo/driver.py:1156-1160) and validates `substrate_sha_kind` as a Literal only (:1116-1126); neither driver.py nor hall_of_fame.py imports or calls `compute_substrate_sha` / `bakeoff_substrate_sha`, so the MAP-Elites stale-cell refusal compares an operator-DECLARED string against the pool index's stamp. But one sub-claim is wrong and materially understates the existing mitigation: 'no committed production entry point pins the value, so it is supplied per-run' misses training/README.md:422-447 and the five committed provenance harnesses under training/artifacts/coevo/provenance/harnesses/*.txt, ALL of which do `composite = compute_substrate_sha()`, then `assert composite.startswith("9bc00af0"), f"substrate moved since 18.24: {composite}"`, and pass `substrate_sha256=composite`. So the fence exists -- it just lives in the operator harness rather than the library, and training/README.md:360-368 already RECORDS that the four real-path leg scripts omit it ('none of them imports `compute_substrate_sha`, so the legs ran with no substrate fence of their own ... That is recorded rather than smoothed over'). The correct claim is therefore: the pin the CoevoCampaignConfig docstring (:516-519) presents as pinning the campaign substrate is an unverified DECLARATION, and a new harness (the re-ground's) can silently omit the assertion the committed ones carry -- which the README records as having already happened once.

**As originally filed.** `CoevoCampaignConfig.substrate_sha256` is validated only as 64 lowercase hex characters and is never checked against `bakeoff_substrate_sha()` or `compute_substrate_sha()`, so the MAP-Elites stale-cell refusal compares the pool's stamp against a declared string — a re-stamped pool plus a matching declared sha passes the fence with no grounding to the corpus on disk.

**Finder evidence.**

```
training/coevo/driver.py:1156-1160 — the ONLY check on the value:
  if _SHA256_HEX_RE.fullmatch(config.substrate_sha256) is None:
      raise ValueError("substrate_sha256 must be exactly 64 lowercase hex chars; got ...")
:1116-1126 validates only that `substrate_sha_kind` is one of the two literals; nothing recomputes either function. `grep -rn "compute_substrate_sha|bakeoff_substrate_sha" training/` shows no call from driver.py or hall_of_fame.py — both consume `config.substrate_sha256` (:1408-1411, :1425; training/coevo/hall_of_fame.py:1457-1458) and pass it as `expected_substrate_sha` to `load_archive_cell_genomes` (training/bakeoff/map_elites.py:889-933), which compares it to the pool index's recorded stamp.
Both sides of that comparison are writable by the operator: the stamp is written at map_elites.py:878-881 from `bakeoff_substrate_sha()` at write time, and the expectation comes from the config.
Current drift is real and confirms the pool is stale:
  live  bakeoff_substrate_sha() = ff7afd851b12ec5da3f595014a69489e9f90574e6a2d0c39d0836f154dfe4410
  training/artifacts/impostor/map-elites/cells/index.json -> substrate_sha256 = e4547789167039aea0cecb7c48522eed6e09e0d7b8d27a970ccbc76b251dedf2, baseline_id = baseline-6, filled_cells = 30
(`grep -rn "substrate_sha256=" training/ scripts/ tests/` finds construction sites only in tests — no committed production entry point pins the value, so it is supplied per-run.)
```

**Verifier evidence (independent re-run).**

```
1) training/coevo/driver.py:1156-1160 read verbatim: `if _SHA256_HEX_RE.fullmatch(config.substrate_sha256) is None: raise ValueError("substrate_sha256 must be exactly 64 lowercase hex chars; got " f"{config.substrate_sha256!r}")`. :1116-1126 is the Literal-only check on substrate_sha_kind. REPRODUCES.
2) `grep -rn "compute_substrate_sha|bakeoff_substrate_sha" training/ scripts/` -> defs/callers in training/anchor_study.py:212,1386; training/bakeoff/map_elites.py:711,880; training/README.md; the provenance .txt harnesses. ZERO hits in training/coevo/driver.py or training/coevo/hall_of_fame.py. REPRODUCES.
3) The comparison path: driver.py:1408-1411 `load_archive_cell_genomes(side_config.founder_cells_dir, expected_substrate_sha=config.substrate_sha256)`; :1425 `HallOfFame.create(..., substrate_sha256=config.substrate_sha256, ...)`; hall_of_fame.py:1457-1458 `load_archive_cell_genomes(cell_artifact_dir, expected_substrate_sha=self._substrate_sha256)`; map_elites.py:889-933 raises only on `expected_substrate_sha != recorded_substrate`, and :878-881 writes the recorded side from `bakeoff_substrate_sha()`. REPRODUCES.
4) Live drift re-measured: `PYTHONPATH=. uv run python -c "from training.bakeoff.map_elites import bakeoff_substrate_sha; from training.anchor_study import compute_substrate_sha; ..."` ->
     bakeoff_substrate_sha = ff7afd851b12ec5da3f595014a69489e9f90574e6a2d0c39d0836f154dfe4410
     compute_substrate_sha = f5865c538c1ec02c000fcfb0c854824a9b8c59ba1e727e08cd3d3a9e1a7e4738
   training/artifacts/impostor/map-elites/cells/index.json -> substrate.substrate_sha256 = e4547789167039aea0cecb7c48522eed6e09e0d7b8d27a970ccbc76b251dedf2, baseline_id = baseline-6, filled_cells = 30. The pool IS stale (and training/reports/report-impostor-campaign.md:1229 confirms the 18.24 campaign ran `substrate_sha256=e4547789...` kind `bakeoff_substrate_sha`). REPRODUCES exactly as filed.
5) CORRECTION (mine): `grep -rn "substrate_sha256=" training/ scripts/ tests/` -> training/README.md:446 in ADDITION to the test sites; and training/README.md:422-427 carries `composite = compute_substrate_sha()` + the `assert composite.startswith("9bc00af0")` stale-substrate guard, reproduced verbatim in all five training/artifacts/coevo/provenance/harnesses/*.txt files. training/README.md:360-368 states the omission on the four leg scripts explicitly.
6) ADDITIONAL (mine, strengthens the finding): the two sha definitions are not interchangeable, and the fence crosses them. The committed harnesses declare `substrate_sha_kind="compute_substrate_sha"` and pass the composite, while every MAP-Elites index records `bakeoff_substrate_sha()` (map_elites.py:880). A campaign configured that way with a non-None `founder_cells_dir` would compare a composite against a raw-MANIFEST stamp and refuse unconditionally. `grep -n founder_cells_dir training/artifacts/coevo/provenance/harnesses/*.txt training/README.md` -> no match: NO committed campaign sets founder_cells_dir, so the stale-cell refusal path has never actually been exercised, and the definition-mismatch hazard is untested.
```

**Verifier note.** ADJUSTED rather than CONFIRMED because the evidence block's 'construction sites only in tests' is factually wrong and hides the operator-layer fence that the committed campaigns all carry. Severity held at P2: the substance -- a config field the docstring calls a pin, never verified against either named definition, guarding a pool that is demonstrably stale -- stands, and the re-ground writes a NEW harness where the assertion is opt-in. The fix sketch (recompute per `substrate_sha_kind` inside `_validate_campaign_config`) is right and should additionally reconcile the definition mismatch surfaced in evidence item 6 before founder ingest is ever used.

**Fix sketch.** In `_validate_campaign_config`, recompute the named definition and require equality: `expected = compute_substrate_sha(...) if kind == 'compute_substrate_sha' else bakeoff_substrate_sha()`, then fail loud when `config.substrate_sha256 != expected`. That turns `substrate_sha_kind` from a label into a verified claim and makes the re-ground's pool re-stamp self-checking instead of self-asserting.

## B-45 — Fit-corpus fingerprint scope stops at recorded bytes — it does not cover the roster, nor the derivation code that turns those bytes into features

**Severity:** P3 (finder: P2). **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** training-path / training/surrogate/runner.py::fit_corpus_fingerprint. **Confidence:** medium.
**Merged from:** finder-training-path.json#10.

**Claim.** The corpus-side half reproduces and is real: `fit_corpus_fingerprint` (training/surrogate/runner.py:388-415) folds only `replay-seed-*.jsonl` + `splits.json` + `MANIFEST.md`, so `roster.json` is unhashed -- and roster.json IS load-bearing, since `build_meeting_table` re-seeds every game from it (training/surrogate/dataset.py:1043-1044 and :1062 `resolve_roster_knobs(sample_dir)`). The derivation-side half is substantially OVERSTATED. `BALLOT_FEATURE_NAMES`, `SKIP_FEATURE_NAMES`, `epochs` and `lr` are all serialized into the committed weights artifact and VALIDATED ON LOAD with a fail-loud raise (training/surrogate/ballots.py:667-670 write, :700-707 verify against the live constants) -- I confirmed all four are present in training/artifacts/surrogate/ballot-predictor.json -- so the fix sketch's proposed `feature_schema` digest of exactly those four is redundant with machinery that already ships. `tournament-eval-report.json` is inert: eval/validity.py:21 states assemble_tournament_report 'does not read the committed `tournament-eval-report.json` at all'. The genuine residual hole is narrower than filed: the feature-VALUE derivation (the training/surrogate/dataset.py belief fold) can move with no name change, no fingerprint change, and no load-time refusal.

**As originally filed.** The fingerprint folds `replay-seed-*.jsonl` plus `splits.json` and `MANIFEST.md` only, so `roster.json` (which declares the corpus's 9p2i shape) and, more importantly, every line of the feature-derivation pipeline that produced the fit are outside its scope — a change to the belief fold or the feature set leaves the committed provenance reading 'grounded' on weights it no longer explains.

**Finder evidence.**

```
training/surrogate/runner.py:388-415
  for path in sorted(corpus_dir.glob("replay-seed-*.jsonl")): ...
  for meta_name in ("splits.json", "MANIFEST.md"): ...
ls replays/ml_corpus/9p2i | grep -v '^replay-seed-.*\.jsonl$' -> MANIFEST.md, roster.json, splits.json, tournament-eval-report.json
  cat replays/ml_corpus/9p2i/roster.json -> {"num_impostors": 2, "num_players": 9, "tasks_per_crewmate": 2}
Neither `roster.json` nor `tournament-eval-report.json` is hashed. Nothing in `SurrogateFitCorpus` (:378-385: corpus_set, corpus_sha256, fit_side_meetings, weights_sha256) records a version of the derivation path — `BALLOT_FEATURE_NAMES` (training/surrogate/ballots.py:114-121), `SKIP_FEATURE_NAMES` (:127-131), `DEFAULT_EPOCHS`/`DEFAULT_LEARNING_RATE` (:135-136) and the whole `training/surrogate/dataset.py` belief fold can all move without moving the fingerprint. Contrast the MAP-Elites index, which at least records `encoder_version` and the full descriptor configuration (training/bakeoff/map_elites.py:854-885).
```

**Verifier evidence (independent re-run).**

```
1) training/surrogate/runner.py:388-415 read verbatim -- the glob is `replay-seed-*.jsonl` and the metadata loop is `for meta_name in ("splits.json", "MANIFEST.md")`. `ls replays/ml_corpus/9p2i | grep -v '^replay-seed-.*\.jsonl$'` -> MANIFEST.md, roster.json, splits.json, tournament-eval-report.json. `cat replays/ml_corpus/9p2i/roster.json` -> {"num_impostors": 2, "num_players": 9, "tasks_per_crewmate": 2}. Neither roster.json nor tournament-eval-report.json is hashed. REPRODUCES.
2) SurrogateFitCorpus fields (runner.py:382-385): corpus_set, corpus_sha256, fit_side_meetings, weights_sha256 -- no derivation-version field. REPRODUCES.
3) roster.json IS consumed: training/surrogate/dataset.py:1043-1044 docstring 'Re-seeds every game from the set's roster (``roster.json`` via :func:`eval.validity.resolve_roster_knobs`)' and :1062 `num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(sample_dir)`. So the hole is load-bearing, not decorative. CONFIRMS the finding's roster point.
4) REFUTES the derivation-schema point: `training/artifacts/surrogate/ballot-predictor.json` keys read from disk = ['confidence_weights','epochs','feature_names','format','lr','mean','skip_bias','skip_confidence','skip_feature_names','skip_mean','skip_std','skip_weights','std','weights'], with feature_names = the six BALLOT_FEATURE_NAMES, skip_feature_names = the three SKIP_FEATURE_NAMES, epochs = 300, lr = 0x1.3333333333333p-2. training/surrogate/ballots.py:700-707: `if tuple(raw.get("feature_names", ())) != BALLOT_FEATURE_NAMES: raise ...` and the same for skip_feature_names. training/artifacts/surrogate/fit-corpus.json carries weights_sha256 = 611771a4... keying the record to those exact bytes. So a moved feature layout or hyperparameter is already caught.
5) REFUTES the tournament-eval-report.json point: eval/validity.py:21 -- the assembler 'does not read the committed ``tournament-eval-report.json`` at all'; `grep -n "tournament-eval-report" eval/validity.py eval/balance_eval.py` finds only that line.
6) MITIGATION on the roster hole (mine): a wrong roster.json would almost certainly fail loud before it could silently move a fit -- training/surrogate/dataset.py:1100-1112 raises MeetingTableReconstructionError unless the reconstructed meeting count equals the assembled report's and the ballot join rate is exactly 100%, and roles come from the report (`report_roles.get(seed, per_seed_roles[seed])`, :1085) rather than from the re-seed.
```

**Verifier note.** ADJUSTED: the fingerprint-scope observation is correct and the roster.json omission is a genuine (if defended-in-depth) provenance hole, but the headline 'every line of the feature-derivation pipeline is outside its scope' is not true as filed -- the feature-name layout and hyperparameters are committed to the weights artifact and refused on drift, and one of the two named unhashed files is inert. Confidence 'medium' on the original was well judged. What survives is worth a line in the re-ground contract at P3: hash the corpus dir's non-replay files, and (the part with no existing cover) version the dataset.py belief fold.

**Fix sketch.** Extend the fingerprint's metadata leg to every non-replay file in the corpus dir (sorted, name + digest — cheap and closes the roster hole), and add a separate `feature_schema` field to `SurrogateFitCorpus` carrying a digest of `BALLOT_FEATURE_NAMES + SKIP_FEATURE_NAMES + epochs + lr` (the same idiom as `encoder_version`), verified on load. That way 'the corpus moved' and 'the derivation moved' are two distinguishable failures instead of one silent one.

## B-46 — Deleting the STALE amnesty is four code sites plus five tests that PIN 'STALE' as the expected status

**Severity:** P3 (finder: P2). **Classification:** observation. **Verdict:** ADJUSTED. **Area:** training-path / scripts/verify_ml_evidence.py + tests/scripts/test_verify_ml_evidence.py. **Confidence:** high.
**Merged from:** finder-training-path.json#12.

**Claim.** The STALE amnesty is cleanly localised and its declared digest pair IS the live drift (re-derived, exact). Deleting it touches six code sites plus test assertions. But the finding's test enumeration is wrong for two of the five tests it cites: THREE tests assert `status == "STALE"` as the expected answer (test_recompute_reads_every_committed_verdict_against_the_declared_gap at :395 plus its `assert len(stale) > 1` at :399; test_a_perturbed_weight_hash_fails_even_while_the_fits_are_stale at :495; the sampled-recompute test at :684). The test at :427 (test_the_stale_amnesty_stops_at_the_corpus_dependent_rows) uses STALE only as a SCOPING FILTER at :456 (`if row.status == "STALE" and row.name != "ML grounding": assert row.name in _CORPUS_DEPENDENT_RECOMPUTE_ROWS`) — it never asserts STALE is correct, and survives the deletion unchanged in meaning. The test at :500 (test_an_undeclared_corpus_still_fails_the_grounding_row) asserts the OPPOSITE — :527-529 are `assert not stale`, `assert row.status == "FAIL"`, `assert "undeclared substrate" in row.detail`; the finding's own fix_sketch says this correctly while its evidence line mislabels :526 as a STALE assertion. There is no present defect: the amnesty is correct, live, declared in audits/audit-phase-20-baseline-7.md §10.2, and scripts/verify_ml_evidence.py:194-196 already documents its own deletion ("the constant can be deleted along with every branch that reads it"). This is a contract-authoring note about a FUTURE change's blast radius, not a defect in HEAD.

**As originally filed.** The amnesty is cleanly localised and its declared digest pair is exactly the live drift, but four of the tests that guard it assert `status == "STALE"` as the correct answer, so a contract that says only 'delete the amnesty' invites those guards to be deleted rather than inverted to OK — silently removing the proof that the two fingerprints now agree.

**Finder evidence.**

```
The gap is exactly one declared pair and it is live:
  scripts/verify_ml_evidence.py:197-201 _DECLARED_GROUNDING_GAP = ("164ef00c...bc3170", "45b11993...1e59a8")
  uv run python -c "..." -> live 45b11993d7badcc9c413ff6db0ee0b5e693006173185d0295bb3a16f221e59a8 ; fit rec 164ef00c16fa5108aa2d2a691f2f9a65d5ea60faa10f7bbd1604e93f36bc3170 ; match False
Code sites that read it: :203-206 (`_is_declared_grounding_gap`), :1459-1462 (fingerprint row -> STALE), :1602-1610 (`_grounding_row`), :1938-1946 (the recompute downgrade). Plus the `Status` literal at :181 and the summary counter at :3018-3031.
Tests that assert STALE as correct (tests/scripts/test_verify_ml_evidence.py):
  :372 test_recompute_reads_every_committed_verdict_against_the_declared_gap  -> :395 assert grounding.status == "STALE"
  :427 test_the_stale_amnesty_stops_at_the_corpus_dependent_rows              -> :456
  :460 test_a_perturbed_weight_hash_fails_even_while_the_fits_are_stale       -> :495
  :500 test_an_undeclared_corpus_still_fails_the_grounding_row                -> :526
  :684 assert _row(result.rows, "fit-corpus identity fingerprint").status == "STALE"
The three of these that assert the AMNESTY BOUNDARY (:427, :460, :500) are the ones worth keeping in inverted form; the two that assert the gap itself become OK assertions.
```

**Verifier evidence (independent re-run).**

```
Re-derived the gap live (HEAD d8ec0a1c):
  uv run python -c "...load_fit_corpus_record / fit_corpus_fingerprint..."
  rec  164ef00c16fa5108aa2d2a691f2f9a65d5ea60faa10f7bbd1604e93f36bc3170
  live 45b11993d7badcc9c413ff6db0ee0b5e693006173185d0295bb3a16f221e59a8
  match False ; _is_declared_grounding_gap -> True ; _DECLARED_GROUNDING_GAP == that exact pair
Code sites all confirmed present: scripts/verify_ml_evidence.py:181 (`Status = Literal["OK","FAIL","ABSENT","INFO","STALE"]`), :197-200 (_DECLARED_GROUNDING_GAP), :203-206 (_is_declared_grounding_gap), :1459-1462 (fingerprint row -> STALE), :1569-1575 (_STALE_GROUNDING_NOTE), :1602 (_grounding_row's `stale = _is_declared_grounding_gap(...)`), :1935-1948 (the recompute downgrade loop), :3018-3035 (summary counter + the STALE epilogue).
Test enumeration re-read directly: `grep -n STALE tests/scripts/test_verify_ml_evidence.py` -> 373,382,395,397,456,468,495,501,506,680,684. `sed -n '498,530p'` shows the :500 test's assertions are `assert not stale` / `assert row.status == "FAIL"` / `assert "undeclared substrate" in row.detail` at :527-529 — the finding's cited ":500 ... -> :526" is `row, stale = vme._grounding_row(root)`, not an assertion. `sed -n '425,460p'` shows :456 is an `if` condition inside a loop, not an assertion.
Declared-carry check: audits/audit-phase-20-baseline-7.md §10.2 ("The ML re-ground — A NAMED FOLLOW-UP, not a silent debt") specifies the STALE status, the ONE-declared-pair rule, and that the tests/training pins are tripwires that FAIL when the re-ground lands. audits/audit-phase-20-close.md:57 records the leg green with 11 STALE rows as the expected state.
```

**Verifier note.** Not a re-report of any named open item (C-46/C-83/C-126/C-130/F1-F5/etc. do not cover it); it is adjacent to the routed ML re-ground (§10.2) but adds the test-inversion point. Severity dropped P2 -> P3: zero current defect, and the code already carries its own deletion instruction. The one durable contribution — the assertion that must survive deletion is 'a fingerprint MISMATCH fails' — stands and is worth carrying into the re-ground contract.

**Fix sketch.** Write the contract item as: delete `_DECLARED_GROUNDING_GAP` / `_is_declared_grounding_gap` / `_STALE_GROUNDING_NOTE` and the four branches; drop "STALE" from the `Status` literal and the summary counter; RE-POINT (do not delete) tests at :372, :460 and :684 to assert `OK`; keep :500 as the 'a drifted corpus FAILS the grounding row' guard with the amnesty branch gone; and keep :427's per-row scoping test as the proof that a corpus-independent row still FAILs. The one thing that must survive deletion is the assertion that a fingerprint MISMATCH fails — that is the whole gate.

## B-47 — Stale coordination anchors around BAKEOFF_BASELINE_ID: the doc comment names the wrong current value and the committed bake-off rows still stamp baseline-5

**Severity:** P3 (finder: P2). **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** training-path / eval/watchability.py + training/reports/results-impostor-bakeoff.jsonl. **Confidence:** high.
**Merged from:** finder-training-path.json#13.

**Claim.** Only the comment error survives. eval/watchability.py:908-912 states `BAKEOFF_BASELINE_ID` (training/bakeoff/harness.py) "still reads ``baseline-5``" while training/bakeoff/harness.py:181 reads "baseline-6" — a factually wrong sentence in a note whose whole job is to tell the next re-ground which constant lags. That much is real, one comment, no behaviour. The rest of the finding does NOT stand: (1) the constant's value is SPECIFIED as correct, not stale — audits/audit-phase-20-baseline-7.md §10.2 says verbatim "`BAKEOFF_BASELINE_ID` (`training/bakeoff/harness.py`) still reads `baseline-6`, which is correct — it names the baseline the bake-off is GROUNDED on, not the substrate baseline", and moving it is an explicitly ROUTED item of the ML re-ground ("move `BAKEOFF_BASELINE_ID`"), so the fix sketch's "move it to baseline-7" prescribes the routed work as if it were a repair, on a constant the audit declares correct today; (2) "nothing gating the disagreement" / "the rows read as current" is false — tests/training/test_bakeoff_harness.py:164-174 pins `BAKEOFF_BASELINE_ID == "baseline-6"` coupled to the goodhart probe default, and :692-697 pins `row["baseline_id"] == "baseline-5"` for every committed bake-off row, while training/reports/report-impostor-bakeoff.md is TITLED "the baseline-5 re-run" and its header states "**Substrate:** baseline 5". The rows are correct provenance stamps of a Task-17.12 recording, not stale current claims.

**As originally filed.** The comment that tells the re-ground which constant to move states that `BAKEOFF_BASELINE_ID` 'still reads baseline-5' when it reads baseline-6, and the committed bake-off results rows still carry `baseline_id: "baseline-5"` — so the constant, its documentation, and the evidence it produced name three different baselines with nothing gating the disagreement.

**Finder evidence.**

```
training/bakeoff/harness.py:181
  BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"
eval/watchability.py:908-912 (the note attached to `_DEFAULT_BASELINE_ID = "baseline-7"` at :914):
  # ... NOTE the bake-off lag: the training-side selection floors deliberately lag this default -
  # ``BAKEOFF_BASELINE_ID`` (training/bakeoff/harness.py) still reads
  # ``baseline-5`` - until the surrogate is re-ground on the new corpus ...
(By contrast audits/audit-phase-20-baseline-7.md:734 states it correctly as baseline-6.)
training/reports/results-impostor-bakeoff.jsonl -> every one of the four rows carries baseline_id = baseline-5; training/artifacts/impostor/map-elites/cells/index.json carries baseline_id = baseline-6.
The destination exists and the move is mechanically available: eval/watchability.py:841-901 registers the full baseline-7 floor block for both 9p2i and 4p1i.
Also relevant to the move's blast radius: the baseline-7 comment at :866-869 records that the flag census FALLS against baseline 6 (1.0909 -> 0.8816) while conversion RISES, so 'a baseline-6 floor scored against these bytes therefore FAILS' — moving the constant changes which candidates clear `supply_floors_passed`, and all four recorded rows already read False.
```

**Verifier evidence (independent re-run).**

```
training/bakeoff/harness.py:181 -> `BAKEOFF_BASELINE_ID: Final[str] = "baseline-6"` (confirmed).
eval/watchability.py:908-912 -> "NOTE the bake-off lag: ... ``BAKEOFF_BASELINE_ID`` (training/bakeoff/harness.py) still reads ``baseline-5`` — until the surrogate is re-ground" with `_DEFAULT_BASELINE_ID: Final[str] = "baseline-7"` at :914 (confirmed — the note names the wrong value).
Rows: uv run python over training/reports/results-impostor-bakeoff.jsonl -> 4 rows, all baseline_id=baseline-5, supply_floors_passed=False (confirmed). training/artifacts/impostor/map-elites/cells/index.json -> baseline-6 (confirmed).
But the narration exists: training/reports/report-impostor-bakeoff.md:1 "# The impostor bake-off — the baseline-5 re-run...", :22 "**Substrate:** baseline 5."; git log on the jsonl -> last regenerated by b55550e1 "task 17.12" (the baseline-5 re-run).
Gates exist: `grep -n baseline tests/training/test_bakeoff_harness.py` -> :164 test_selection_bar_pins_the_baseline_6_floors / :172 `assert BAKEOFF_BASELINE_ID == "baseline-6"`; :692 test_rerun_rows_pin_the_baseline_5_protocol / :697 `assert row["baseline_id"] == "baseline-5"`; :711 test_rerun_rows_carry_the_baseline_5_supply_floors.
Specified-carry: audits/audit-phase-20-baseline-7.md:656-658 ("The training-side selection constants deliberately lag ... untouched by this record") and :734-742 (§10.2's routed list, quoted above). audits/audit-phase-20-close.md:111 repeats "move `BAKEOFF_BASELINE_ID`" as routed.
```

**Verifier note.** The surviving defect is a single stale comment line — the same CLASS the close audit already routed as F2 ("two stale narrations whose own committed pins already disagree with them ... Routed to the next phase's inputs as a prose-sweep item"), though this specific site is NOT one of F2's two (orchestrator/game.py:388-391 and frontend/src/lib/bodies.test.ts:9). So: a new site inside an already-routed class. Severity P2 -> P3 because two of the three legs of the claim are refuted and the third is one comment. Useful residue for the fix: the note should reference the symbol rather than restate its value.

**Fix sketch.** Move `BAKEOFF_BASELINE_ID` to "baseline-7" and, in the same change, correct the eval/watchability.py note (or delete it — once the lag is gone the note is the only thing that can go stale again). Add a test that asserts the note's named value equals the imported constant, or drop the value from the prose entirely and reference the symbol. Re-record `results-impostor-bakeoff.jsonl` under the new floors, or state in the report that the committed rows are a baseline-5 snapshot not re-scored — today neither is stated and the rows read as current.

## B-48 — The IN-TREE sidecar leg descends into nested git worktrees, so content outside the checkout decides the evidence gate's exit code

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** gates-scripts / verify_ml_evidence.py structure. **Confidence:** high.
**Merged from:** finder-gates-scripts.json#5.

**Claim.** WALK_SKIP_DIRS omits `.claude`, so scripts/verify_ml_evidence.py's sidecar walk verifies every *.sha256 inside sibling worktrees checked out under .claude/worktrees/ — 758 of the 817 sidecars it hashes on this checkout — and a broken sidecar in any of them fails the leg even though the inventory row correctly ignores them.

**Finder evidence.**

```
Command: `uv run python scripts/verify_ml_evidence.py --only sidecars`
Output:
  [  OK  ] sidecars[IN-TREE]
            measured : 817 sidecars / 817 targets verified, 0 failure(s)
  [  OK  ] sidecars[IN-TREE] inventory
            measured : 817 on disk, 0 tracked but absent
            committed: 59 tracked in-tree sidecars
            note     : 758 untracked sidecar(s) on disk: .claude/worktrees/relaxed-bun-52901b/agents/tactical/learned/crew_weights.json.sha256, .claude/worktrees/relaxed-bun-52901b/agents/tactical/learned/weights.json.sha256, …

Command: `sed -n '143,155p' scripts/verify_ml_evidence.py`
Output:
  WALK_SKIP_DIRS: Final[frozenset[str]] = frozenset(
      {".git", ".hypothesis", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__", "dist", "node_modules"}
  )

The asymmetry is in run_sidecars (scripts/verify_ml_evidence.py:980-1024): the failing row iterates `in_tree`, which is the raw walk minus only the evidence-branch `moved_paths` (:995-997), and any `_verify_sidecar` failure sets `status="FAIL"` (:1021). The inventory row directly below (:1027-1050) DOES restrict to `git_tracked_sidecars(...)` and reports the 758 extras as a note rather than a failure. So the row that can fail the gate is the one that is not tracked-scoped.

59 tracked vs 817 hashed: 93% of what this leg's exit code depends on is not in this checkout's index.
```

**Verifier evidence (independent re-run).**

```
Reproduced exactly at HEAD d8ec0a1c.
1) `uv run python scripts/verify_ml_evidence.py --only sidecars` ->
   [  OK  ] sidecars[IN-TREE]  measured: 817 sidecars / 817 targets verified, 0 failure(s)
   [  OK  ] sidecars[IN-TREE] inventory  measured: 817 on disk, 0 tracked but absent / committed: 59 tracked in-tree sidecars / note: 758 untracked sidecar(s) on disk: .claude/worktrees/relaxed-bun-52901b/...
2) Independent split of the walk (not the note): uv run python -c "...vme.walk_sidecars(Path('.'))..." ->
   total 817 | under .claude 758 | outside 59 | Counter({'.claude': 758, 'training': 53, 'experiments': 4, 'agents': 2}) — 93% of the hashed set is nested worktrees. `ls .claude/worktrees | wc -l` -> 14 checkouts.
3) WALK_SKIP_DIRS at scripts/verify_ml_evidence.py:143-155 = {.git, .hypothesis, .mypy_cache, .pytest_cache, .ruff_cache, .venv, __pycache__, dist, node_modules} — no `.claude`; the only consumer is :910 `dirnames[:] = sorted(name for name in dirnames if name not in WALK_SKIP_DIRS)`.
4) The asymmetry is in run_sidecars: :994-997 `in_tree = [path for path in on_disk if _relative(...) not in moved_paths]` (raw walk minus only the evidence-branch moved set) -> :1001-1005 any `_verify_sidecar` failure appends -> :1021 `status="FAIL" if in_tree_failures else "OK"`; the inventory row at :1027-1050 DOES use `git_tracked_sidecars(...)` and reports extras as a note (:1045 `status="FAIL" if missing else "OK"` — extras never fail).
5) PLANTED CASE (in scratchpad, nothing in the repo touched): built /…/scratchpad/probe/.claude/worktrees/nested/{.git/HEAD, agents/w.json, agents/w.json.sha256 with an all-zero digest} ->
   vme.walk_sidecars -> ['.claude/worktrees/nested/agents/w.json.sha256']
   vme._verify_sidecar -> (1, ['.claude/worktrees/nested/agents/w.json: sha256 5891b5b522d5… != sidecar 000000000000… (…)'])
   i.e. a mismatched sidecar in a nested worktree is walked and produces the failure string that sets the row to FAIL.
Specified? No. The row's own source string is "the working tree (every *.sha256 outside caches/build output)" and the :140-142 comment justifies the skip set as "build output, caches and dependency trees" — a nested git worktree is none of those and is not named anywhere. DESIGN.md / docs/architecture.md / audits/ carry no declaration that nested checkouts are in scope.
```

**Verifier note.** Not a re-report (nothing in C-46/C-83/C-126/C-130/F1-F5/C-79/C-80/C-101/C-107/C-62/C-33/C-45 or the replay_walk / 1440x900 / alibi_vs_sighting items covers it). One scope caveat the finding does not state, which bounds but does not remove it: `.gitignore:8` is `.claude/`, so CI never has these directories and the false-red is developer-local — but this gate is explicitly the offline one-command local truth and the close audit runs it by hand on exactly the machine that carries 14 worktrees (audits/audit-phase-20-close.md:57, :516), so P2 stands. The suggested fix that generalises is the right one: skip any directory containing a `.git` entry below the root — a nested worktree marks itself, which `.claude` in WALK_SKIP_DIRS would not (a worktree elsewhere still leaks in).

**Fix sketch.** Either add `.claude` to WALK_SKIP_DIRS, or (better, and covers any future nested checkout) skip any directory that contains a `.git` entry other than the repo root — a nested worktree marks itself. Alternatively scope the FAILING row to tracked paths the way the inventory row already does, and keep the untracked walk as an INFO row.

## B-49 — check.sh's leg composition is unpinned: six of its seven gates could be deleted with the suite still green

**Severity:** P2. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** gates-scripts / check.sh composition. **Confidence:** high.
**Merged from:** finder-gates-scripts.json#6.

**Claim.** tests/scripts/test_gate_invocation.py records the full argv of every leg check.sh runs but then filters to lines starting with "run pytest", so removing ruff, ruff format, lint-imports, validate_task_docs.py, generate_prompts.py --check or mypy from scripts/check.sh fails nothing.

**Finder evidence.**

```
Command (replicating the test's own stub-uv harness in scratch, AILIBI_SKIP_FRONTEND=1):
  printf '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$UV_ARGV_LOG"\nexit 0\n' > $SCRATCH/bin/uv
  PATH="$SCRATCH/bin:$PATH" UV_ARGV_LOG="$SCRATCH/uv-argv.log" AILIBI_SKIP_FRONTEND=1 bash scripts/check.sh
Output (the complete recorded log):
  run ruff check .
  run ruff format --check .
  run lint-imports
  run python scripts/validate_task_docs.py
  run python scripts/generate_prompts.py --check
  run mypy .
  run pytest -n auto --dist loadfile

The test throws six of those seven away. tests/scripts/test_gate_invocation.py:83-84:
    def _pytest_lines(recorded: list[str]) -> list[str]:
        return [line for line in recorded if line.startswith("run pytest")]
and every assertion goes through it — :90 `assert _pytest_lines(recorded) == ["run pytest -n auto --dist loadfile"]`, :97, :112. `recorded` (the full list above) is otherwise asserted only as `assert recorded == []` on the early-exit path (:107).

No other test references the missing legs as check.sh legs. Command: `grep -rn "check.sh" --include="*.py" tests/` returns docstring mentions only (tests/conftest.py:34,47; tests/training/test_suite_tiers.py:4; tests/api/test_view_model.py:15,1312) plus this file. CI runs the same script (.github/workflows/ci.yml, step "Run checks: bash scripts/check.sh"), so there is no second copy of the leg list to disagree with.

This is the Craft-rule-2 shape: the gate that guards the gate reads only one of its seven legs.
```

**Verifier evidence (independent re-run).**

```
Reproduced independently at HEAD d8ec0a1c with my own stub-uv harness (scratchpad, repo untouched):
  printf '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$UV_ARGV_LOG"\nexit 0\n' > $SP/bin/uv ; chmod +x
  PATH="$SP/bin:$PATH" UV_ARGV_LOG=... AILIBI_SKIP_FRONTEND=1 bash scripts/check.sh  -> exit=0, log:
    run ruff check .
    run ruff format --check .
    run lint-imports
    run python scripts/validate_task_docs.py
    run python scripts/generate_prompts.py --check
    run mypy .
    run pytest -n auto --dist loadfile
  (matches scripts/check.sh:27-42 exactly.)
The filter is real: tests/scripts/test_gate_invocation.py:83-84 `def _pytest_lines(recorded): return [line for line in recorded if line.startswith("run pytest")]`, and every assertion goes through it — :90, :96, :112. The full `recorded` list is asserted only as `assert recorded == []` on the early-exit path (:107). Nothing in the file names ruff / ruff format / lint-imports / validate_task_docs / generate_prompts --check / mypy.
No second owner: `grep -rn "check.sh" --include="*.py" tests/ scripts/` returns docstring mentions only (tests/conftest.py:34,47; tests/_helpers/test_committed_single_home.py:573; tests/llm/test_provider.py:416; tests/training/test_suite_tiers.py:4; tests/api/test_replay_loader.py:1014; tests/api/test_view_model.py:15,1312; scripts/build_sample_report.py:6; scripts/gen_frontend_types.py:7,294) plus test_gate_invocation.py itself. `grep -rn "ruff check|ruff format|validate_task_docs|generate_prompts.py --check|run mypy" tests/` finds no leg assertion — only prose and direct module imports (tests/scripts/test_task_doc_guards.py imports validate_task_docs/generate_prompts to unit-test helper functions; nothing runs `--check` tree-wide).
CI has no second copy: .github/workflows/ci.yml runs `bash scripts/setup_env.sh` then `bash scripts/check.sh` for the whole Python job (:45, :54), so a leg deleted from check.sh leaves CI entirely. The separate frontend-checks job duplicates only the four npm commands (:80-89).
```

**Verifier note.** Not a re-report; no named open item covers check.sh composition. Two framing notes that do not change the verdict: (a) the test file's own docstring scopes itself to pytest invocation, so this is an un-taken coverage opportunity rather than a broken promise — but the log is already captured, so the fix really is one assertion; (b) the 'Craft rule 2' invocation is a stretch — AGENTS.md:102-105 rule 2 is 'a gate must be able to fail', and this gate does bite for what it claims; the accurate framing is that the ONE home for the gate's leg list (ci.yml:47 says so explicitly) has no membership pin. The finding's own fix sketch (assert the full `recorded` list) is correct and also pins ORDER, which matters here: check.sh:33-34's comment makes the cheap-signal-first ordering deliberate.

**Fix sketch.** One assertion in tests/scripts/test_gate_invocation.py: `assert recorded == ["run ruff check .", "run ruff format --check .", "run lint-imports", "run python scripts/validate_task_docs.py", "run python scripts/generate_prompts.py --check", "run mypy .", "run pytest -n auto --dist loadfile"]` — the log is already captured, so this pins order and membership at zero extra cost, and a deliberate leg change becomes a one-line test edit that shows up in review.

## B-50 — The corpus recorder mis-states its own substrate in 29 places, including messages it prints at record time

**Severity:** P2. **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** gates-scripts / recorders (scripts/record_ml_corpus.sh). **Confidence:** high.
**Merged from:** finder-gates-scripts.json#7.

**Claim.** The core stands and reproduces: scripts/record_ml_corpus.sh's PIN BLOCK (:105-127) correctly names baseline-7 / prompt set v4 / twenty-one retired always-on levers, while its header, usage text, dry-run preview and several runtime messages still narrate baseline-6, "all four templates at v3" and "the thirteen retired always-on levers" — including :913, which prints "resolves to the baseline-6 map" followed by four v4 version strings. Two corrections. (1) The count is inflated: `grep -c` returns 29, but at least four of those hits are CORRECT baseline-6 references, not staleness — :9 is the audit filename `audits/audit-phase-18-baseline-6.md`; :127, inside the correct PIN BLOCK, deliberately cites "a prior baseline-6 recording" as the thing the freeze-path guards must refuse; :27 and :83 are historical wall-clock notes about the Task-18.13 baseline-6 run. The stale-site count is ~25, and the title's "29 places" should be stated as a grep count, not a defect count. (2) "No gate covers recorder prose" is false as written: check_doc_facts.py does not (confirmed, markdown-only), but tests/scripts/test_record_ml_corpus.py PINS several of the stale operator-facing strings verbatim — :324/:513/:574 `assert "locked baseline-6 model" in out`, :486 `assert "locked baseline-6 substrate" in out`, :615 asserts the "…has moved off the locked baseline-6 versions" registry error. So the sweep is not a free sed pass: those assertions must move in lockstep, and the suite currently RE-ASSERTS the stale labels every run.

**As originally filed.** scripts/record_ml_corpus.sh's PIN BLOCK is correct at baseline-7/v4/twenty-one levers, but its header, usage text, dry-run preview and success echoes still say baseline-6, "all four templates at v3" and "the thirteen retired always-on levers" — including one runtime line that announces the v4 map as "the baseline-6 map".

**Finder evidence.**

```
Command: `grep -c "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` → `29`

The pin block itself is right (scripts/record_ml_corpus.sh:107-114): "PIN BLOCK — the baseline-7 substrate … the qwen3_6_27b prompt set at v4 (the Task-20.31 evidence-honesty bump…)" and :155 carries the four v4 template versions.

The surrounding prose is not. scripts/record_ml_corpus.sh:7-8 — "record the frozen ML-calibration corpus at baseline-6 config"; :13-15 — "recorded at EXACT baseline-6 config — the locked substrate: … the qwen3_6_27b prompt set (all four templates at v3), the baseline-6 lever slate (the thirteen retired always-on levers…".

Three of these are printed to the operator during a run, not just read in source:
  :185 (usage/--help)      "Records the frozen ML-calibration corpus at baseline-6 config into …"
  :791 (--dry-run)         echo "[dry-run] provider: featherless (LOCKED — the corpus is baseline-6)"
  :913 (real path, post-preflight, self-contradicting)
      echo "Locked prompt versions OK: $REQUIRED_PROMPT_SET resolves to the baseline-6 map ($REQUIRED_PROMPT_VERSIONS)."
    which renders as: "Locked prompt versions OK: qwen3_6_27b resolves to the baseline-6 map (accusation_round.qwen3_6_27b.v4, crewmate_report.qwen3_6_27b.v4, impostor_report.qwen3_6_27b.v4, vote_ballot.qwen3_6_27b.v4)."

The lever count is wrong by 8. Command: `uv run python -c "from orchestrator.replay import SUBSTRATE_FLAG_KEYS,_RETIRED_ALWAYS_ON_LEVERS,TOGGLEABLE_SUBSTRATE_FLAG_KEYS as T; print(len(SUBSTRATE_FLAG_KEYS), len(_RETIRED_ALWAYS_ON_LEVERS), T)"` → `22 21 ('impostor_roll_call',)`, against the header's "thirteen retired always-on levers".

No gate covers recorder prose: `grep -n "record_ml_corpus\|refresh_samples" scripts/check_doc_facts.py` returns nothing, and check_doc_facts' document set is markdown-only.

Behaviour is correct throughout — only the operator-facing narration is stale — but this is the script the re-ground's combined re-record runs, under a substrate whose exact identity is the point of the exercise.
```

**Verifier evidence (independent re-run).**

```
Reproduced at HEAD d8ec0a1c.
`grep -c "baseline-6\|baseline 6" scripts/record_ml_corpus.sh` -> 29 (matches). Line list confirms the split:
  STALE narration: :7-8 ("record the frozen ML-calibration corpus at baseline-6 config"), :13-15 ("EXACT baseline-6 config … all four templates at v3 … the baseline-6 lever slate (the thirteen retired always-on levers"), :72, :78, :91, :185 (usage/--help: "Records the frozen ML-calibration corpus at baseline-6 config into $CORPUS_ROOT"), :495, :510, :513, :522, :556, :566, :791 (dry-run: "[dry-run] provider: featherless (LOCKED — the corpus is baseline-6)"), :834, :840, :852, :875, :887, :903 ("the corpus contract freezes the baseline-6 versions (all four templates at v3)"), :913, :957, :1254, :1259.
  CORRECT/historical: :9 (audit filename), :27 + :83 (Task-18.13 wall-clock history), :127 ("a prior baseline-6 recording, whose stamp carries the eight Phase-20 levers OFF" — the deliberate refusal example inside the baseline-7 PIN BLOCK).
The PIN BLOCK is right: :105-114 "PIN BLOCK — the baseline-7 substrate; the committed corpus IS current … the qwen3_6_27b prompt set at v4 (the Task-20.31 evidence-honesty bump…) + the baseline-7 lever slate: the twenty-one retired always-on levers"; :155 REQUIRED_PROMPT_VERSIONS = "accusation_round.qwen3_6_27b.v4, crewmate_report.qwen3_6_27b.v4, impostor_report.qwen3_6_27b.v4, vote_ballot.qwen3_6_27b.v4".
The self-contradicting runtime line verified in source: :913 `echo "Locked prompt versions OK: $REQUIRED_PROMPT_SET resolves to the baseline-6 map ($REQUIRED_PROMPT_VERSIONS)."` — renders baseline-6 label + four v4 strings.
Lever count: `uv run python -c "from orchestrator.replay import SUBSTRATE_FLAG_KEYS,_RETIRED_ALWAYS_ON_LEVERS,TOGGLEABLE_SUBSTRATE_FLAG_KEYS as T; print(len(SUBSTRATE_FLAG_KEYS), len(_RETIRED_ALWAYS_ON_LEVERS), T)"` -> `22 21 ('impostor_roll_call',)` — the header's "thirteen" is wrong by 8 (confirmed).
Gate coverage re-checked, and this is where the finding is wrong: `grep -n "record_ml_corpus\|refresh_samples" scripts/check_doc_facts.py` -> no output (exit 1) — confirmed. BUT `grep -n "baseline-6" tests/scripts/test_record_ml_corpus.py` -> :324, :486, :513, :574, :615 are string assertions over the recorder's own stderr, plus explanatory comments at :34, :37, :50, :64, :98, :101, :189, :428, :526, :601, :703, :770, :800, :804 that also narrate the file as the baseline-6 recorder.
Sibling claim checked: training/reports/report-ballot-surrogate.md:23 does read "baseline-6 lever slate — the thirteen retired always-on levers" (confirmed).
```

**Verifier note.** Not a re-report of a named open item; same CLASS as the close audit's F2 (stale narration, routed as a prose-sweep item, audits/audit-phase-20-close.md:115-121) but neither of F2's two sites. Severity held at P2 — three of the stale strings are printed to the operator at record time by the script the routed ML re-ground must run, and the substrate's exact identity is the point of that exercise — but the fix sketch must be widened from "one sed-shaped pass over the 29 sites" to "~25 prose sites + the five verbatim assertions in tests/scripts/test_record_ml_corpus.py, leaving the four correct historical baseline-6 references alone". The finding's better half — derive the runtime lines from the already-correct constants (:913 should say "the locked map" and let $REQUIRED_PROMPT_VERSIONS speak) — is the part that stops this recurring.

**Fix sketch.** One sed-shaped pass over the 29 sites: baseline-6 → baseline-7, "all four templates at v3" → v4, "thirteen retired always-on levers" → "twenty-one". Prefer deriving the runtime lines from the constants that are already correct (e.g. :913 should say "resolves to the locked map" and let $REQUIRED_PROMPT_VERSIONS speak), so the next re-lock cannot re-open the gap. Same sweep should re-check the sibling claim at training/reports/report-ballot-surrogate.md:23 ("baseline-6 lever slate — the thirteen retired always-on levers"), which the re-ground re-publishes anyway.

## B-51 — The substrate- and policy-mismatch errors are documented as "HTTP 500 with the offending game id in the response body" but return an opaque `Internal Server Error`

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** api-frontend / api/main.py exception handlers vs api/replay_loader.py error contracts. **Confidence:** high.
**Merged from:** finder-api-frontend.json#3.

**Claim.** unchanged

**As originally filed.** `api.main.create_app` registers an exception handler only for `ReplayStateMismatchError`, so `ReplaySubstrateMismatchError` and `ReplayPolicyMismatchError` — whose carefully-written remediation text names the divergent levers and the exact env vars to export — never reach the client, contradicting their own stated contract and leaving an operator with nothing but a stack trace in the server log.

**Finder evidence.**

```
CONTRACT. api/replay_loader.py:373-374 (`ReplaySubstrateMismatchError`): "Surfaced as HTTP 500 with the offending game id in the response body." api/replay_loader.py:441-442 (`ReplayPolicyMismatchError`): the same sentence. Both errors build a long, actionable message (api/replay_loader.py:392-421 branches the hint on toggleable-vs-retired and names `env_var_for_lever(key)`).

HANDLER REGISTRATION. api/main.py:231 is the only `add_exception_handler` call: `app.add_exception_handler(ReplayStateMismatchError, _handle_state_mismatch)`; `_handle_state_mismatch` (api/main.py:157-165) returns `JSONResponse(status_code=500, content={"detail": str(exc), "tick": exc.tick, "game_id": exc.game_id})`. There is no analogous handler for the other two, so Starlette's `ServerErrorMiddleware` answers them.

REPRODUCED. Same scratchpad set as the sibling finding (one committed 9p2i replay with `substrate_flags['testimony_as_content']` flipped to False), served through `TestClient(create_app(...), raise_server_exceptions=False)`:
```
status 500
content-type text/plain; charset=utf-8
body[:400] Internal Server Error
```
The game id, the differing levers and the remediation hint are all absent.

NO TEST COVERS THE HTTP SURFACING. `grep -rn 'ReplaySubstrateMismatchError|ReplayPolicyMismatchError' --include='*.py' .` outside `api/replay_loader.py` returns only unit-level `pytest.raises` sites (tests/api/test_replay_loader.py:1207, :1233, :1307, :1338, :1387; tests/api/test_replay_loader_policy_stamp.py:110, :134; tests/orchestrator/test_replay.py:1247-1304) — every one asserts the exception object, none asserts a response body.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ AT HEAD (clean main, d8ec0a1c). `grep -n add_exception_handler api/main.py` -> exactly one hit, api/main.py:231 `app.add_exception_handler(ReplayStateMismatchError, _handle_state_mismatch)`; `_handle_state_mismatch` at api/main.py:157-165 returns JSONResponse(500, {detail, tick, game_id}). `grep -n 'Surfaced as HTTP 500' api/replay_loader.py` -> :339 (state), :373 (substrate), :441 (policy) — all three docstrings promise the same body; only the first has a handler.

MY OWN HTTP REPRO (clean, and NOT the finder's single-file setup — see note): copied the WHOLE committed set `replays/samples/9p2i` (52 files + MANIFEST.md) to a scratchpad parent named `samples/`, rewrote ONLY the `game_over` line of replay-seed-0.jsonl to flip `substrate_flags['testimony_as_content']` to False (every other line kept byte-identical), served it through `AILIBI_REPLAY_DIR` + `TestClient(api.main.app, raise_server_exceptions=False)`:
```
[flip] status=500 ctype=text/plain; charset=utf-8
[flip] body[:300]=Internal Server Error
```
With `raise_server_exceptions=True` the propagating exception is identified positively:
```
EXC TYPE: ReplaySubstrateMismatchError
MSG: replay substrate mismatch for 'headless-seed-0': recorded with {...'testimony_as_content': False...}
```
So the game id, the differing-lever list and the env-var remediation hint (api/replay_loader.py:392-421) are all built and all discarded. Control: the same set unmutated serves 200 application/json.

SPEC CHECK: DESIGN.md has zero 'substrate' hits; docs/architecture.md has none; no tasks/ contract declares an opaque-500 carry. The docstring sentence IS the contract and it is violated.

COVERAGE CLAIM RE-RUN: `grep -rn 'ReplaySubstrateMismatchError|ReplayPolicyMismatchError' --include='*.py' .` outside api/replay_loader.py hits only tests/api/test_replay_loader.py:1207,1233,1307,1338,1387, tests/api/test_replay_loader_policy_stamp.py:110,134, tests/orchestrator/test_replay.py:1259,1304 — all `pytest.raises` on the exception object. No response-body assertion anywhere.
```

**Verifier note.** Reproduces exactly; nothing in the claim needs changing. Two qualifications a reader should carry, neither of which weakens it: (1) ReplayPolicyMismatchError is UNREACHABLE from HTTP today — it fires only when a caller sets `expected_tactical_policy` (api/replay_loader.py:561), and `SetLoaderRegistry` builds every served loader as bare `ReplayLoader(replay_dir=...)` (api/replay_loader.py:3354), so that half is a LATENT contract violation while the substrate half is live and demonstrated; (2) the missing-test half of the finding is already named inside review finding C-112 ('none that a substrate/policy mismatch yields a useful HTTP body', audits/review-2026-08-19/B/collated-findings.md:170), which sits in the phase-20 close's 'roughly 94 P2 code findings' triaged backlog (audits/audit-phase-20-close.md:394). C-112 is NOT on the known-open list I was given, and it never states the handler-registration defect or shows the actual response — so this finding is more than a re-report, but its remediation should be booked against C-112 rather than as a new coverage item.

Incidental discovery while building the repro, reported so the next reader is not misled: a BYTE-IDENTICAL copy of one committed replay served from a directory containing only that one file fails its own tick-0 state hash (500 ReplayStateMismatchError), while a copy of the whole 52-file set serves 200. Reconstruction of a single game therefore depends on the other files present in its set directory. That confounds any single-file scratchpad repro (it silently poisoned my first attempt), and is outside this batch's five ids — flagging it, not filing it.

**Fix sketch.** Register two more handlers in `create_app` beside the existing one (or generalise `_handle_state_mismatch` into a small table): return `JSONResponse(500, {"detail": str(exc), "game_id": exc.game_id, "differing_levers": [...]})` for `ReplaySubstrateMismatchError` and the analogous shape for `ReplayPolicyMismatchError`. Add one API-level test per class asserting the game id appears in the body — the missing test is what let the docstring claim go unchecked.

## B-52 — The substrate guard is asymmetric: it catches a lever it knows recorded OFF, but silently ignores a recorded lever key it does not know

**Severity:** P2. **Classification:** defect. **Verdict:** CONFIRMED. **Area:** api-frontend / api/replay_loader.py::_assert_substrate_matches + orchestrator/replay.py::retired_levers_stamped_off. **Confidence:** high.
**Merged from:** finder-api-frontend.json#4.

**Claim.** unchanged

**As originally filed.** Both the loader's guard and the audit spine's `retired_levers_stamped_off` iterate only the keys the CURRENT build declares, so a recording stamped by a build carrying an extra lever reconstructs silently under a build that has no notion of it — the forward direction of exactly the cross-build mismatch the stamp exists to catch.

**Finder evidence.**

```
CODE. api/replay_loader.py:631-635 computes the diff as `sorted(key for key in SUBSTRATE_FLAG_KEYS if bool(recorded.get(key)) != bool(ambient.get(key)))` — the comprehension is over the build's registry, never over `recorded`'s own keys. orchestrator/replay.py:645-648 has the same shape: `[key for key in _RETIRED_ALWAYS_ON_LEVERS if not bool(substrate_flags.get(key))]`. The registry is append-only by design (orchestrator/replay.py:585-589, "Both halves only ever grow at their own end"), which is precisely what makes a newer build's stamp a strict superset.

REPRODUCED.
```
uv run python -c "..."
recorded keys not in registry: ['future_lever_from_a_branch']
guard passed: an unknown recorded lever is silently ignored
```
(built a `GameEndReplayEntry` whose `substrate_flags` equals `substrate_flag_snapshot()` plus one unknown key set True, then called `_assert_substrate_matches('g', [entry])` — it returned without raising).

SCOPE TODAY. Not live: over all 300 committed replays the extra-key set is empty (`300 ((), ())` for the `(differing, extra)` pair). The exposure is procedural — a branch/worktree or container run that graduates or adds a lever, records, and has its bytes read back on `main`. AGENTS.md's "no silent fallbacks" is the rule this violates.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ AT HEAD. api/replay_loader.py:630-635: `differing = sorted(key for key in SUBSTRATE_FLAG_KEYS if bool(recorded.get(key)) != bool(ambient.get(key)))` — the comprehension iterates the BUILD's registry, never `recorded`'s own key set. orchestrator/replay.py:646-648: `return [key for key in _RETIRED_ALWAYS_ON_LEVERS if not bool(substrate_flags.get(key))]` — same shape. `substrate_flags: Mapping[str, bool] | None` (orchestrator/replay.py:431), so an unknown key round-trips through pydantic intact rather than being stripped.

UNIT REPRO (mine): built a GameEndReplayEntry whose substrate_flags = `substrate_flag_snapshot()` plus `future_lever_from_a_branch: True`, then called `_assert_substrate_matches('g', [entry])`:
```
recorded keys not in registry: ['future_lever_from_a_branch']
guard passed: unknown recorded lever silently ignored
retired_levers_stamped_off: []
```

HTTP REPRO (mine, stronger than the finding's): full 52-file copy of `replays/samples/9p2i`, only the `game_over` line rewritten to ADD `future_lever_from_a_branch: true`:
```
[unknown] status=200 ctype=application/json
[unknown] body={"viewModelVersion":"2","metadata":{"game_id":"headless-seed-0",...
```
Served clean, no warning, no log line. The paired mutation (a KNOWN lever flipped OFF) on the identical setup 500s — so the asymmetry is demonstrated side by side in one experiment.

CORPUS SCOPE RE-MEASURED (mine): over all 300 committed `replay-seed-*.jsonl` under replays/: `files 300 unstamped 0 / extra keys across corpus: [] / differing keys across corpus: []`. Matches the finding's '300 ((), ())'.

SPEC CHECK: DESIGN.md contains no 'substrate' hit; docs/architecture.md none; tasks/phase-14.md's stamp contracts (:829, :843, :907, :924) require the machinery stay 'generic for future levers' and never declare forward-compat as out of scope. `retired_levers_stamped_off`'s docstring (orchestrator/replay.py:626-642) explicitly resolves only the BACKWARD case ('a MISSING key reads OFF ... a recording made before a lever existed'); the forward case is unaddressed, not waived.
```

**Verifier note.** Not a re-report. The listed known-open `eval/replay_walk.py` gap (audits/audit-phase-20-close.md:408) is 'that consumer performs NO substrate check at all'; this is a different defect — the checks that DO exist read the wrong key set — and the finding names the replay_walk item itself in its fix sketch rather than restating it.

Severity held at P2 rather than dropped for being latent: the exposure window is a live workflow in this repo, not a hypothetical. Levers are graduated and recordings made on branches / in the container (phase 20 graduated eight and re-recorded), and lab bytes get read by audit spines before the branch merges; under a reader that lacks the lever the reconstruction silently uses the OLD derivation, and the state hash cannot catch it because the stamp's own docstring states the per-tick hash is substrate-independent (api/replay_loader.py:415-421). That is precisely the silent cross-substrate reconstruction the guard exists to prevent, and AGENTS.md 'no silent fallbacks' is the rule violated.

One thing the finding UNDERSTATES: `retired_levers_stamped_off` is not merely blind to unknown keys, it is blind to every TOGGLEABLE lever too (it iterates `_RETIRED_ALWAYS_ON_LEVERS` only), so the audit spine that uses it as its only substrate check would also miss `evidence_quality_lift` stamped OFF against an ambient-ON build — a wider hole than the one filed, and an argument for the single shared `substrate_stamp_mismatches(recorded, ambient)` helper the fix sketch proposes.

**Fix sketch.** Treat unknown recorded keys as divergent in both places: in `_assert_substrate_matches`, extend `differing` with `sorted(set(recorded) - set(SUBSTRATE_FLAG_KEYS))` and give `ReplaySubstrateMismatchError` a third hint branch ("lever(s) X are not in this build's registry — the recording was made by a build this one is behind"); mirror it in `retired_levers_stamped_off` (or, better, factor one `substrate_stamp_mismatches(recorded, ambient)` helper in orchestrator/replay.py that both the loader and the audit spine call, which also closes the known eval/replay_walk.py gap with the same call).

## B-53 — The meeting dialog's transcript/evidence half has no automated assertion anywhere — no component tests exist and journey.spec asserts only the ballots region

**Severity:** P2. **Classification:** quality-debt. **Verdict:** ADJUSTED. **Area:** api-frontend / frontend test shape (frontend/src/**/*.test.ts*, frontend/e2e/*.spec.ts). **Confidence:** high.
**Merged from:** finder-api-frontend.json#5.

**Claim.** The viewer's most reconstruction-load-bearing surface — TurnCards, contradiction badges, the evidence taxonomy and the verdict/gate readout — carries zero unit tests and zero assertions in any STANDING gate leg. (Correction: `frontend/e2e/media.spec.ts` DOES assert on a TurnCard — `expect(card).toHaveCount(1)` and `expect(card).toContainText(`accuses${HERO.accused}`)` at :836-838 — but its whole describe block is `test.skip(!CAPTURE_REQUESTED, ...)` at :731-734, gated on AILIBI_CAPTURE_MEDIA=1, so it never runs in `npm run e2e` / `scripts/check.sh`. 'Zero e2e assertions' is true of the standing gate, not of the e2e tree.) Second correction: the contradiction census is 31 of 144, not 31 of 164, over the default-served spectator sets.

**As originally filed.** The viewer's single most reconstruction-load-bearing surface — TurnCards, contradiction badges, the evidence taxonomy, and the verdict/gate readout — is covered by zero unit tests and zero e2e assertions, which is the direct reason the `:whereabouts:` badge defect above survived from Task 16.7 to HEAD.

**Finder evidence.**

```
NO COMPONENT TESTS. `find frontend/src -name '*.test.ts*' | sort` -> `api/client.test.ts`, `components/CostChips.test.ts`, `components/EventTicker.test.ts`, `lib/bodies.test.ts`, `lib/copy.test.ts`, `lib/playback.test.ts`, `store/replayStore.test.ts`, `tokens.test.ts`. All eight are pure-function/store tests; nothing renders `MeetingView.tsx` (a 600+-line component) or `TurnCard.tsx`, and `lib/contradictions.ts` has no test file at all.

E2E STOPS AT THE BALLOTS. `grep -n 'test(' frontend/e2e/journey.spec.ts` -> 6 tests (featured journey, keyboard transport, guided-tour focus, transport dock at laptop heights, As-agent fog leak, reduced motion); `bundle.spec.ts` 3 (static bundle); `media.spec.ts` 3 (README capture). Inside the one test that opens the meeting (journey.spec.ts:282-425), the only meeting assertions are frontend/e2e/journey.spec.ts:344-352: `const ballots = meeting.getByRole("region", { name: /^Ballots \(\d+\)$/ }); await expect(ballots).toContainText("confidence"); await expect(ballots.getByText(/^p-\d+$/).first()).toBeVisible();` — then `Escape`. `grep -rn 'contradiction|Contradiction' frontend/e2e/*.ts` prints nothing; `grep -rn 'Evidence|Resolution|tally' frontend/e2e/*.ts` finds no meeting assertion (media.spec.ts:835-839 only LOCATES a turn card by its `free_text` in order to screenshot it).

CONSEQUENCE, MEASURED. The gap is not hypothetical: 31 of the 164 contradictions in the committed spectator sets render only half their link, and 7 turns in the default-served 9p2i set render with no flag and no accent (see the whereabouts finding), with a green `bash scripts/check.sh` and a green `npm run e2e`.

NOTE: this DEEPENS the known F3/1440x900/e2e-shape items rather than restating them — the named gap is the meeting transcript surface specifically, and it has a demonstrated live defect behind it.
```

**Verifier evidence (independent re-run).**

```
COMPONENT TESTS — RE-RUN. `find frontend/src -name '*.test.ts*' | sort` returns exactly the eight files listed: api/client.test.ts, components/CostChips.test.ts, components/EventTicker.test.ts, lib/bodies.test.ts, lib/copy.test.ts, lib/playback.test.ts, store/replayStore.test.ts, tokens.test.ts. `wc -l` : MeetingView.tsx 701, TurnCard.tsx 430, lib/contradictions.ts 44 — none has a test file, and I read contradictions.ts end to end (44 lines, three exported pure functions, no coverage).

E2E SHAPE — RE-RUN. per-file `test(` counts: journey.spec.ts 6, bundle.spec.ts 3, media.spec.ts 3. `grep -rn 'contradiction|Contradiction' frontend/e2e/*.ts` -> NO OUTPUT. `grep -rn 'Evidence|Resolution|tally' frontend/e2e/*.ts` -> NO OUTPUT. journey.spec.ts:344-352 is verbatim as quoted (Ballots region, 'confidence', one /^p-\d+$/, then Escape at :356). playwright.config.ts testDir './e2e' with no testMatch, so media.spec.ts is nominally in the run — but :731-734 skips the entire describe unless AILIBI_CAPTURE_MEDIA=1.

CONSEQUENCE — INDEPENDENTLY MEASURED (mine, not inherited). Served the default `replays/samples` parent through TestClient and, for every meeting of every game, rebuilt the frontend's own id vocabulary (`turn:<turn_id>:claim:<i>` / `turn:<turn_id>:obs:<i>` from frontend/src/lib/contradictions.ts:12-18) and matched each ContradictionView endpoint against it:
```
total contradictions: 144  half-resolved: 31  neither: 0
sample unresolved endpoints: ['turn:headless-seed-10:meeting-0:turn-6:whereabouts:0', 'turn:headless-seed-12:meeting-0:turn-5:whereabouts:0', ...]
```
31 contradictions have exactly one endpoint whose id kind is `:whereabouts:` — a kind lib/contradictions.ts never mints — so the load-bearing 31 reproduces exactly; only the 164 denominator does not.
```

**Verifier note.** The gap is real, unspecified, and not a re-report of any listed known-open item. The finding's own note calls it a deepening of 'the known F3/1440x900/e2e-shape items' — F3 is a MIS-CITATION: audits/audit-phase-20-close.md:181-200 defines F3 as three front-door word budgets, nothing to do with the frontend. The listed 1440x900 gap (audit-phase-20-close.md:409) is a viewport-coverage item on journey.spec.ts, disjoint from the meeting-transcript surface; C-112's coverage list (collated-findings.md:170) names eleven gaps and none of them is this one. So the finding is new at its own scope.

ADJUSTED rather than CONFIRMED for two precision defects a reader would act on: 'zero e2e assertions' is false as written (media.spec.ts asserts a unique TurnCard and its accusation text) and only becomes true once restricted to the standing gate — which is the honest and still-damning form, since a capture-only spec gated on an env var cannot catch a regression; and the 164 census denominator is 144 on the sets the API serves by default. Severity P2 / quality-debt both stand: 31 half-linked contradictions ship green through `bash scripts/check.sh` and `npm run e2e`.

**Fix sketch.** Cheapest high-value coverage, in order: (1) a vitest over a committed served-payload fixture (reuse the `lib/bodies.fixture.json` pattern) asserting every `ContradictionView` endpoint in a real `MeetingView` resolves to exactly one rendered event id — this is a pure-function test needing no DOM and would have caught the whereabouts miss; (2) extend journey.spec's meeting step with two assertions on the transcript region: at least one TurnCard visible, and the Evidence section's count matching `meeting.contradictions.length` for the featured seed; (3) a `role_proof`/`weak_signal` accent assertion if a suitable featured seed exists.

## B-54 — Within-tick action priority is the actor's id string, giving a lower-id seat a systematic mechanical edge

**Severity:** P3. **Classification:** observation. **Verdict:** CONFIRMED. **Area:** engine-core / action ordering. **Confidence:** high.
**Merged from:** finder-engine-core.json#7.

**Claim.** unchanged

**As originally filed.** `_action_order_key` sorts by `action.actor` first, so in any within-tick race — a kill against the victim's escape move, a report against a kill, two impostors' kills — the seat whose id sorts earlier wins, and `p-10` sorts before `p-2`.

**Finder evidence.**

```
orchestrator/action_ordering.py:34-40:
```
def _action_order_key(action: Action) -> tuple[str, str, str]:
    action_payload = json.dumps(action.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return action.actor, action.type, action_payload
```
Ids are `p-1 ... p-{n}` in fixed lexical order (orchestrator/seeder.py:136-137), so at the 9p roster the string order is `p-1, p-2, ..., p-9` (no zero padding; a 10+ roster would order `p-1, p-10, p-2, ...`).

CONSEQUENCE, demonstrated by the finding-1 probe: `[('p-1','report'), ('p-2','kill'), ('p-3','move')]` — p-2's legal kill never lands solely because `'p-1' < 'p-2'`. Reverse the seat assignment and the kill lands. In the corpus this decided 28 kill submissions and 78 vent submissions.

MITIGATING FACT: roles are seed-shuffled (orchestrator/seeder.py:140-152), so across the 200-game corpus the impostor seat is uniform and the bias does not systematically favour a side in aggregate. Determinism is not at risk — the order is a pure function of the batch. The concern is per-game fairness and, for the re-ground, that seat index is a stable, learnable, mechanically-meaningful feature that has nothing to do with strategy.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ AT HEAD. orchestrator/action_ordering.py:34-40 is verbatim as quoted — `_action_order_key` returns `(action.actor, action.type, action_payload)`, actor first; `order_actions_for_tick` (:13-17) sorts by it. orchestrator/seeder.py:136-137: `tuple(f"p-{index + 1}" for index in range(num_players))` — no zero padding. `_assign_roles` (:140-152) seed-shuffles, confirming the finding's own mitigating fact.

ORDERING REPRO (mine), same batch with the two seats swapped:
```
reporter p-1, killer p-2 -> [('p-1','report'), ('p-2','kill'), ('p-3','move')]
reporter p-2, killer p-1 -> [('p-1','kill'),   ('p-2','report'), ('p-3','move')]
11-seat lexical order: ['p-1','p-10','p-11','p-2','p-3',...]
```
Both halves of the claim land in one experiment: the race outcome flips purely on the id string, and `p-10` sorts before `p-2`.

THE CONSEQUENCE IS LOAD-BEARING, not decorative — I verified the engine actually honours position. engine/tick.py:593-604 applies the ordered batch sequentially and `if working_state.phase == "MEETING": return working_state, events` — a lower-id `report` ABORTS the tick and every later action in the batch is never applied (not even rejected-with-event). A lower-id `kill` likewise removes the victim before the victim's own later `move` is attempted, which then raises ActionRejectedError. orchestrator/boundary.py:44-50 is the only producer, so every batch reaching the engine is in this order.

SPEC CHECK: DESIGN.md mentions `orchestrator/action_ordering.py` only as an undrawn module (:257) and 'action ordering' once in passing (:426); no §3.1 statement of the tie-break rule, which is exactly what the fix sketch proposes adding. tests/orchestrator/test_action_ordering.py:19 pins the rule as intentional (`test_order_actions_for_tick_sorts_by_actor_without_mutating_input`).
```

**Verifier note.** Correctly graded by the finder and I did not move it. The behaviour is deliberate and pinned by a test, so it is not a defect; determinism is genuinely not at risk (the key is a pure function of the batch); and role-shuffling genuinely removes the aggregate side-bias. What remains — and what the observation is worth — is per-game fairness plus a stable, mechanically-meaningful seat feature for the ML re-ground, and the latent `p-10 < p-2` hazard at any 10+ roster (no committed set is 10+ today: only 4p1i and 9p2i exist).

Not independently verified: the '28 kill submissions and 78 vent submissions' corpus counts, which are inherited from the sibling finding-1 probe rather than restated here. They are not load-bearing for the verdict — the mechanism and its flip are demonstrated directly.

**Fix sketch.** No change needed for determinism. If the seat edge is unwanted, derive the tick's actor order from the engine rng (a seeded permutation drawn inside `advance_tick`) rather than the id string — but note that changes every committed `state_hash`, so it belongs to a re-record, not to the re-ground. The cheap interim step is to state the rule in DESIGN.md §3.1 and to zero-pad player ids (`p-01`) so a 10+ roster does not order `p-10` before `p-2`.

## B-55 — I-10's reporter-killed cell divides a body-meeting-only numerator by the all-meetings denominator

**Severity:** P3. **Classification:** observation. **Verdict:** ADJUSTED. **Area:** eval-instruments / evidence_honesty I-10. **Confidence:** high.
**Merged from:** finder-eval-instruments.json#6.

**Claim.** `reporter_killed_within_three` gates its numerator on `facts.body_triggered` but divides by every resolved meeting, so the published rate understates the phenomenon it measures by the emergency-meeting share — 7.4% relative on the fit corpus. CORRECTION to the stated rationale: the restriction is a SEMANTIC scoping choice (an emergency caller is not a body reporter), NOT a structural impossibility. `MeetingReplayEntry.triggered_by` is a REQUIRED field (orchestrator/replay.py:191) populated for every meeting, emergency ones included, so the emergency caller is fully countable — which means restricting the denominator and extending the numerator are BOTH available fixes, not just the additive second cell the sketch proposes.

**As originally filed.** `reporter_killed_within_three` counts only body-triggered meetings in its numerator (the reporter of an emergency meeting is structurally uncountable) but divides by every resolved meeting, so the published rate understates the measured phenomenon by the emergency-meeting share — 7.4% on the fit corpus.

**Finder evidence.**

```
Numerator gate: eval/evidence_honesty.py:1762-1766 `if facts.body_triggered and any(entry.tick < tick <= entry.tick + 3 ...)`. Denominator: eval/evidence_honesty.py:1036-1038 `reporter_killed_within_three=cell(tallies.reporter_killed_meetings, tallies.meetings)`. The definition sentence declares the mismatch rather than resolving it (eval/evidence_honesty.py:352-359, CELL_DEFINITIONS['I-10']: "denominator: all resolved meetings ... the reporter cell is restricted to body-triggered meetings"). Measured: `compute_evidence_honesty(Path('replays/ml_corpus/9p2i')).meeting_physicality` -> meetings 432, body_triggered 400, reporter_killed (60, 432) rate 0.1389 — the coherent 60/400 is 0.15; samples/9p2i (17, 152) 0.1118 against 17/144 = 0.1181.
```

**Verifier evidence (independent re-run).**

```
CODE RE-READ AT HEAD. eval/evidence_honesty.py:1762-1766 — numerator gated `if facts.body_triggered and any(entry.tick < tick <= entry.tick + 3 and victim == entry.triggered_by ...)`. eval/evidence_honesty.py:1036-1038 — `reporter_killed_within_three=cell(tallies.reporter_killed_meetings, tallies.meetings)`, while `body_triggered_meetings=tallies.body_meetings` sits two lines above it at :1034 (so the coherent denominator is already an emitted field). CELL_DEFINITIONS['I-10'] at :352-359 declares the mismatch in words: 'denominator: all resolved meetings ... the reporter cell is restricted to body-triggered meetings and does NOT measure emergency meetings.'

NUMBERS RECOMPUTED (mine, fresh `compute_evidence_honesty`):
```
replays/ml_corpus/9p2i: meetings 432 body_triggered 400
  cell: 60 432 0.1389   body-restricted: 60/400 = 0.15   emergency share: 0.0741
replays/samples/9p2i:   meetings 152 body_triggered 144
  cell: numerator=17 denominator=152 rate=0.11184 (body-restricted 17/144 = 0.1181)
```
Every figure in the finding reproduces to the digit, and 0.1389/0.15 = 0.9259 confirms the relative understatement equals the emergency share exactly.

THE CELL IS PUBLISHED IN THIS SHAPE: audits/audit-phase-20-baseline-7.md:450 states 'I-10 reporter killed <= 3 ticks after | 111/707 | 80/668' — the all-meetings denominator — and tests/eval/test_evidence_honesty.py:1548-1554 pins the four per-set pairs [(17,152),(60,432),(1,40),(2,44)] summing to (80,668), plus `body_triggered_meetings == 144` at :1554. The fix-sketch claim that an additive second cell 'moves no existing pin' checks out against that pin's shape.
```

**Verifier note.** The measurement observation stands and is arithmetically exact; the classification 'observation' and severity P3 are right and I did not move them — the shape is DISCLOSED in CELL_DEFINITIONS rather than hidden, which is what keeps it out of defect territory (there is no spec it contradicts, and I found no DESIGN.md / docs/architecture.md statement to the contrary).

ADJUSTED only for the rationale: 'the reporter of an emergency meeting is structurally uncountable' is wrong, and it matters because it forecloses a fix the finding never considers. `triggered_by: PlayerId` is required on every MeetingReplayEntry and `body_triggered` is derived separately from `walk_event.body_id is not None` (eval/evidence_honesty.py:1428), so nothing prevents counting an emergency caller killed within three ticks — the choice not to is editorial. Not a re-report: I-10 appears in review finding G-5 and in the phase-20 pre-registration only as VALUE pins, never as a denominator question, and it is on none of the listed known-open items.

**Fix sketch.** Emit the body-restricted rate beside the current one (both inputs — `meetings` and `body_triggered_meetings` — are already fields on MeetingPhysicalityCells, so this is additive and moves no existing pin), and say in CELL_DEFINITIONS which of the two a bar is stated on.

## B-56 — I-2 compares a model-emitted room label with a raw string equality while every other room comparison in the module canonicalises

**Severity:** P3. **Classification:** quality-debt. **Verdict:** CONFIRMED. **Area:** eval-instruments / evidence_honesty I-2. **Confidence:** high.
**Merged from:** finder-eval-instruments.json#7.

**Claim.** `eval/evidence_honesty.py:1952` decides I-2 truth with `false_here = observation.room not in engine_rooms` — a bare string compare of a model-written room label against engine RoomIds — while the module's other spoken-label room comparisons (I-6 :2283-2284, I-4 :2335/:2339/:2359, I-7 :2399-2403) all route through `meetings.transcript.canonical_rooms`, with the in-module comment at :2278-2280 stating exactly why ("a spoken label may be lower-case or a compound ``A/B`` account, and a raw string compare would move this cell on formatting alone"). `WhereaboutsClaim.room` is a bare `RoomId = str` (meetings/schemas.py:50, :151) with no normalising validator, and nothing on the elicitation path constrains or canonicalises it — yet the detector itself canonicalises the SAME label at both of its indexing sites (meetings/transcript.py:1365, :2303). Inert on committed bytes today: all 3117 committed whereabouts labels are already self-canonical uppercase single rooms. Note two accuracy nuances, neither of which refutes: (a) I-7 carries a second raw compare at :2417 (`was_at_destination != resolved.sighting.room`), but it is provably inert — it is reachable only after `canonical_rooms(destination) & spoken` and `canonical_rooms(origin) & spoken` have already been evaluated with a non-empty `spoken`, so a raw-equal pair could not reach it; (b) the third cell in the same fold, `copyable_self_location` (:1960), is exact by SPECIFICATION ("the exact (tick, room) pair"), so it is not a departure.

**As originally filed.** `_fold_whereabouts` decides truth with `observation.room not in engine_rooms`, a bare string compare against a label the model wrote, in the one module whose other three room cells route through `canonical_rooms` precisely because "a raw string compare would move this cell on formatting alone".

**Finder evidence.**

```
The raw compare: eval/evidence_honesty.py:1952 `false_here = observation.room not in engine_rooms`. The stated discipline it departs from: eval/evidence_honesty.py:2278-2285 — "Canonical room SETS, the comparison the detector itself made: a spoken label may be lower-case or a compound ``A/B`` account, and a raw string compare would move this cell on formatting alone" — with `canonical_rooms` also used at :2335, :2359 and :2400. `meetings/schemas.py:124-152` shows `WhereaboutsClaim.room: RoomId` carries no normalising validator. Currently inert: a census of all 3117 WhereaboutsClaim labels across the four committed sets returns 9 distinct values, every one an already-canonical single-room uppercase name (CAFETERIA 541, ENGINEERING 514, MEDBAY 433, ADMIN 404, LABS 363, EAST_HALL 267, STORAGE 246, REACTOR 234, WEST_HALL 115), so no committed I-2 number moves today.
```

**Verifier evidence (independent re-run).**

```
Repo clean at HEAD d8ec0a1c. (1) Line anchors exact: `grep -n 'false_here = observation.room not in engine_rooms' eval/evidence_honesty.py` -> 1952; `sed -n '2276,2286p'` prints the stated discipline comment at 2278-2280 followed by `canonical_rooms(...)` at 2283-2284; `grep -n canonical_rooms eval/evidence_honesty.py` -> 202 (import), 2060, 2061, 2070, 2283, 2284, 2335, 2339, 2359, 2399, 2400, 2403 — line 1952 is the only spoken-label truth compare with no canonicalisation. (2) No validator: meetings/schemas.py:50 `RoomId: TypeAlias = str`; :151 `room: RoomId` inside `class WhereaboutsClaim` (:124); no upper()/canonical_rooms anywhere in the elicitation path (`grep -rn 'upper()|canonical_rooms|CANONICAL_ROOMS' meetings/manager.py agents/strategic/*.py llm/*.py` -> only manager.py:2169/2186, the vent-scene fold); the prompt asks free-form for `"room": "<room id>"` (agents/strategic/prompts/qwen3_6_27b/accusation_round_roll_call.j2:197,207) and the model output is not enum-constrained. Meanwhile the detector canonicalises the same label at meetings/transcript.py:1365 (`rooms = canonical_rooms(observation.room)` in `reconstruct_stated_paths`) and :2303 (`rooms=canonical_rooms(observation.room)` in the whereabouts-as-degenerate-alibi index). (3) MY OWN behavioural repro (scratchpad/wave0/B/b56_probe.py, .venv/bin/python), engine room = LABS at both admitted ticks, speaker CREWMATE: label 'LABS' -> crew_false=0; 'labs' -> 1; 'Labs' -> 1; 'LABS_TRANSITION' -> 1; 'LABS/MEDBAY' -> 1 — every one of those labels canonicalises to a set containing the speaker's TRUE room, i.e. a formatting variant is scored as a crewmate lie by the very cell that is under pre-registered bar 3 (audits/audit-phase-20-preregistration.md:247 'I-2 ... < 5% on samples/9p2i, and every set < 8%'). (4) MY OWN census (scratchpad/wave0/B/b56_census.py, walk of every dict with type=='whereabouts' across all four committed sets) reproduces the finding's numbers verbatim: 3117 observations, 9 distinct labels — CAFETERIA 541, ENGINEERING 514, MEDBAY 433, ADMIN 404, LABS 363, EAST_HALL 267, STORAGE 246, REACTOR 234, WEST_HALL 115; per set 763 / 2177 / 85 / 92, which reconciles exactly with the committed pins (samples/9p2i crew 659 + impostor 104 = 763; tests/eval/test_evidence_honesty.py:1262-1274). All 9 are members of CANONICAL_ROOMS and `canonical_rooms(l) == {l}` for each (checked with .venv/bin/python), so the fix sketch is byte-identical on the committed corpus — no pinned I-2 number moves. (5) Not specified: the pinned cell sentence (eval/evidence_honesty.py:294-299 CELL_DEFINITIONS, echoed at :25-30 and :399-405, and audits/audit-phase-20-preregistration.md:100) says only 'whose room MATCHES the speaker's true room at NEITHER engine tick N nor N-1' — it nowhere states string identity, and a canonical fix leaves the sentence (and the test that pins it) untouched. No task contract or audit mentions `_fold_whereabouts` or an exactness rationale (`grep -rln '_fold_whereabouts|crew_false_agent_frame' tasks/ audits/ docs/` -> no hits). No unit test pins raw-string behaviour: every `_fold_whereabouts` test uses canonical 'LABS' (tests/eval/test_evidence_honesty.py:275-360). (6) Not a re-report: no known-open item covers it — `grep -rn 'canonical_rooms' audits/` returns only audit-2026-06-11-2218 (the allowlist flip), review B/meetings-transcript-voting.md:48 (the weak-marker-in-room-label issue, a different module and a different failure) and :99/:112; the five named-open items (C-46 tournament, C-83, C-126 operator env, C-130 dead prompt-set weight, C-36, C-72) and the six begun-not-finished (C-79, C-80, C-101, C-107, C-126, G-29) per audits/audit-phase-20-close.md:399-416 are unrelated, as are F1-F5, the replay_walk gap, the 1440x900 gap and the duplicate alibi_vs_sighting mint.
```

**Verifier note.** Evidence reproduces exactly, including the 3117-label census down to every per-room count, and I added a behavioural repro the finding did not have: 'labs', 'Labs', 'LABS_TRANSITION' and 'LABS/MEDBAY' each score as a crewmate LIE against a true LABS placement. Genuine defect, not specified anywhere and not a declared carry; latent rather than live because today's labels all come from the uppercase rendered memory the prompt tells the model to copy — nothing enforces that, so the first prompt-set, renderer or parser change that lets a lower-case or compound label through silently inflates a pre-registered gate metric. P3/quality-debt held: zero committed bytes move, and the fix is a no-op on the corpus. Two framing nuances recorded in the corrected claim (the provably-inert second raw compare at :2417; `copyable_self_location`'s exactness being specified) — neither changes the verdict or the severity.

**Fix sketch.** Route I-2 through `canonical_rooms` like its four siblings (`canonical_rooms(observation.room) & {canonical of each engine room}`), which is a no-op on the committed bytes and immunises the cell against the first prompt-set or parser change that lets a compound or lower-case label through.

---

## Coverage notes (the finders' own, attributed)

```
COLLATION NOTE (Track B dedup/collation editor). 57 findings were filed across the 8 dimension finders. Exactly ONE true cross-finder duplicate was identified and merged (B-6: the records-free `detect_contradictions` re-derivation, filed by finder-meetings-detector and finder-eval-instruments against the same call sites eval/meeting_quality.py:2382 and training/conviction/dataset.py:491); both filed it P1/defect, so there was NO severity disagreement to resolve, and the strongest evidence from each was kept verbatim. Canonical count: 56. Duplicate detection was run two ways over all 57 findings -- shared file:line tokens across claim+evidence, and title+claim Jaccard -- and both surfaced the same single pair. Two near-misses were checked and deliberately NOT merged, being distinct defects that happen to touch a shared symbol: (a) B-10 (eval-instruments, the flags_per_meeting floor is 69% persisted vent sightings) and B-47 (training-path, BAKEOFF_BASELINE_ID names three different baselines across constant/doc/rows) both reference training/bakeoff/harness.py:181; (b) B-20 (gates-scripts, the STALE amnesty is row-scoped so the two verdict-identity pins enforce nothing) and B-46 (training-path, the amnesty's deletion inventory pins 'STALE' as the expected status in five tests) are opposite halves of the same machinery, not the same defect. Ordering is severity (P1 > P2 > P3) then area, with areas ordered engine-core, observation-firewall, meetings-detector, memory-render, eval-instruments, training-path, gates-scripts, api-frontend; within a dimension each finder's own filed order is preserved. All field text is carried through verbatim.

===== COVERAGE NOTES FROM finder-engine-core.json (7 findings) =====
SCOPE WALKED. Read in full: engine/tick.py, engine/rules.py, engine/win_conditions.py, engine/world.py, engine/entities.py, engine/rng.py, engine/visibility.py, orchestrator/action_ordering.py, orchestrator/boundary.py, orchestrator/scheduler.py, orchestrator/seeder.py, and orchestrator/game.py's loop surface (run/run_unrecorded/_run_loop/_run_and_apply_meeting/_build_packets/_collect_intents/apply_meeting_result). Cross-checked training/env.py's action mask, observation/service.py's observed-action derivation, eval/action_ingest.py, and training/surrogate/dataset.py's re-walk. All work read-only; scratch under scratchpad/wave0/B (probe_meeting_winskip.py, probe_flip.py, scan_corpus_bypass.py). No tracked file touched; no pytest run beyond reading test sources; the full suite, `-m campaign`, and check.sh were NOT run.

METHOD. Every corpus claim comes from re-seeding with `orchestrator.seeder.seed_initial_state` and re-walking with `engine.tick.advance_tick` + `orchestrator.game.apply_meeting_result` over all 200 games in replays/ml_corpus/{4p1i,9p2i} (4,242 tick rows, 476 meetings). The walk was validated against the recorded bytes: 221/221 tick `state_hash` values reproduced exactly on a 10-game 9p2i sample, so "the engine did/did not do X" statements are grounded in the committed hashes, not in my reconstruction.

CHECKED AND CLEAN (no finding). Determinism: no module-level mutable state in engine/ or orchestrator/ (only `Final` mappings and `__all__`); no set/frozenset iteration whose order reaches state — every ordering-sensitive site sorts (`_witnesses_in_room`, `_advance_tasks`, `redistribute_dead_tasks`, `_build_agents`, `_build_packets`, `_collect_intents`, `room_neighbors`, `vent_neighbors`, the visibility id lists). Frozen-dataclass promise holds: `WorldState.__post_init__` and `SabotageState.__post_init__` re-wrap through `MappingProxyType(dict(...))` on every `replace`, and no mutation path writes through a live state's mapping. Body-id minting (`body-{target}-{tick}`) cannot collide (a player dies once) and the duplicate guard at engine/tick.py:374-375 is defence-in-depth. Kill/vent/sabotage/repair/emergency/report rule guards are consistent and all carry the vent ("no physical presence") gate. The sabotage state machine is sound: a repair completing in step 1 clears `active` before the step-3 `remaining_ticks == 0` win check, and a fresh sabotage always mints an empty `repair_progress`. RNG lockstep across the meeting boundary is correct (the trigger tick advances neither tick nor rng; `apply_meeting_result` advances both once).

NOT RE-REPORTED (known-open, verified current in one line each): C-46 tournament loop still serial (`training/env.rollouts` is a plain generator); C-83 import-time prompt-loader side effects unchanged; the eval/replay_walk.py substrate-check gap unchanged; C-130 unused prompt-set weight/sweep sets unchanged. The `advance_tick` RNG draw whose value is discarded (engine/tick.py:638-649) is the declared FROZEN hash-chain apparatus and is correct as written — finding 5 touches only the restore path around it, never the draw.

NOT COVERED (out of dimension or out of budget). Meeting internals (meetings/manager.py, the accusation chain, vote tallying) — Track B has other finders; agent belief/memory substrate; the replay writer's schema and the substrate-flag stamping; the nine red campaign-tier pins themselves (declared). I did not attempt to price the finding-1 fix against the committed `state_hash` chain beyond arguing that events are not hashed — that needs a real gate run before the fix lands.

===== COVERAGE NOTES FROM finder-observation-firewall.json (6 findings) =====
Scope walked: the import contracts (.importlinter — root_packages now include orchestrator/eval/api/scripts, closing the prior F2 two-hop hole; tests/test_firewall.py's two-layer covering assertion and its plant-detect legs look sound and I found no way past them); the packet schema (observation/packet.py) and its build (observation/service.py, every channel read line by line); the scanners (eval/leak_scan.py in full, eval/leak_test.py in full) and their consumers (training/bakeoff/harness.py:1823-1841, training/crew/scorer.py:1738-1755, tests/observation/test_leak_property.py, tests/test_firewall.py §5); the memory-render role-disclosure gate and its call sites; the meeting seam (orchestrator/game.py::_build_participants, _absorb_meeting_beliefs, _notify_meeting_concluded, TacticalAgent's *_for_meeting accessors; meetings/manager.py's prompt-context build) for cross-agent information flow; the learned-policy encoder inputs (agents/tactical/features.py reads only packet + own memory); and the corpus reconstruction path. Everything was verified by running code, never from prose: five scratch probes live under .../scratchpad/wave0/B/ (witness_probe.py, witness_probe2.py, owned_task_probe.py, room_probe.py, plus inline snippets). No tracked file was modified.

Checked and found CLEAN (worth recording as negative results): roles/cooldown/fellow_impostor_ids/own_kill never reach a non-entitled recipient and the planted-leak self-tests all still bite; the do_task vision gate is role-blind for resolved and rejected attempts alike; `_visible_players` never contains the observer itself (the engine excludes the actor from its own kill's and its own vent's witness sets); post-meeting fan-out (`extract_belief_evidence`, `derive_reported_testimony`, `dead_ids`, the confirm-ejects `revealed_role`) is public-at-the-table only, and the role translation happens in exactly one place; the meeting grounding channels are all keyed by the claim's OWN speaker, never a third party's records; and I looked for duplicate perception across the meeting-resume seam (orchestrator/game.py:1888 concatenates the pre-meeting tick's events onto the resume packet's `last_events`, and eval/replay_walk.py:532 reproduces it) — over all 150 9p2i corpus replays there are ZERO cases of the same (observer, killer, room) kill stamped at two different ticks, so the latent double-count I suspected does not occur on the recorded substrate.

One further boundary of the 20.8 oracle, folded into finding 1 rather than filed separately: the observer's ROOM SET is read from the engine and bounded only by `{own room} U map neighbours` (eval/leak_scan.py:681-690), so a ONE-HOP widening of the crewmate rule — i.e. a silent flip of the Task 13.8 asymmetric-visibility substrate the whole impostor information economy rests on — passes the leak scan with no failures (probe: .../wave0/B/room_probe.py; mutated run shows a CREWMATE in CAFETERIA seeing p-2 in WEST_HALL and p-4 in UPPER_HALL, `leak-scan failures: NONE`). That specific flip IS caught by the default gate, by the hand-written legs of tests/observation/test_leak_property.py:1039-1080 (`test_each_observer_class_sees_exactly_its_entitlement`) — but not by any gate a training run consults.

Declared items verified in one line and not re-reported: the eval/replay_walk.py substrate-check gap is real at HEAD (the `leak-scan-factory` profile at eval/leak_scan.py:823-827 deliberately runs no hash or substrate verification — harmless for factory mode, which records and re-walks in the same process, but it is what a corpus sweep would need if it is ever pointed at foreign bytes); C-83's import-time prompt-loader side effects, C-126's operator env surface, and the production-side duplicate alibi_vs_sighting mint were left alone. Not covered: api/ and frontend/ (spectator surfaces are entitled to omniscience by design), the leak scan's behaviour under `python -O` (documented footgun, prior review F13), and any transcript content analysis (Track A's material).

===== COVERAGE NOTES FROM finder-meetings-detector.json (6 findings) =====
Scope walked: meetings/transcript.py (detector, banding, lift key, echo dedup, movement chokepoint, grounded prosecution, map-aware arbitration, proxy guards, independent_voices), meetings/voting.py, meetings/constants.py, meetings/schemas.py testimony DTOs, the manager's flag/ballot seams (detect_contradictions call site :1225, the ballot guard chain :1948-2033, guard_ballot_target_graph, guard_ballot_citation, _tally, derive_reported_testimony, _suspicion_graph_with_contradictions), and the reporter_exculpation implementation in agents/memory/beliefs.py:1655-1714. Measurements ran over the full replays/ml_corpus (200 files / 476 meetings) and replays/samples via short scratch scripts under .../scratchpad/wave0/B/ (dup_scan2.py, label_gap.py, band_gap.py, strong_cause.py, reasons.py, testimony_gap.py, marker_wild.py, marker_spoof2.py, whereabouts_band.py, selfreport.py). No tracked file was modified; no pytest run, no check.sh, no campaign tier.

VERIFIED CLEAN (checked, no finding): (1) The tally is order-independent and tie-safe — meetings/voting.py:218-238 counts into a dict, sorts leaders, treats SKIP as a first-class target, ties -> SKIPPED, and the confidence cutoff is inclusive; the manager delegates to it (manager.py:2066). (2) guard_ballot_target_graph's gate test runs on the rendered 2-decimal grid while the redirect picks the RAW argmax (manager.py:3207-3235) — rounding is monotone, so the raw argmax always carries the max rounded value and the two can never disagree; ties break lexicographically. (3) contradiction_lift_key folds the duplicate mint and the whereabouts shape correctly (transcript.py:981-994). (4) _apply_grounded_prosecution counts carriers as a SET of speaker ids, so neither the duplicate mint nor one narrator's two channels can manufacture the two-source bar (transcript.py:3930-3948). (5) reporter_exculpation's load-bearing empirical premise still holds on the baseline-7 bytes — the constant's justification is pinned to the BASELINE-2 corpus (agents/memory/beliefs.py:191-201), so I re-measured with eval.funnel.compute_information_funnel: samples/9p2i 144 report meetings, samples/4p1i 37, ml_corpus/9p2i 400, ml_corpus/4p1i 37, `killer_self_reported=0` on all four (618 report meetings), reporter_ejected_innocent == reporter_ejected everywhere (10/10, 1/1, 18/18, 1/1). No re-grounding action needed there, but the docstring's baseline-2 provenance should be refreshed to cite these numbers.

HEADLINE FOR THE RE-GROUND: two of the four detector kinds are structurally incapable of deciding a meeting at baseline 7 — 100/100 recorded alibi_vs_sighting and 60/60 recorded alibi_conflict flags are WEAK, and the only STRONG evidence in the whole corpus is vent_sighting (448) and alibi_vs_physical (12), both grounded in PRIVATE channels the replay does not persist. Baseline 7 is canon by explicit owner override of a FINDING verdict (pre-registered bars 1 and 2 missed), and bars 4 and 7 read 0/0 for exactly this reason. Any conviction/surrogate re-fit therefore learns a substrate in which spoken alibi contradiction never convicts; findings 1 and 3 name the two repairable causes (degenerate-claim band misfire; the dropped whereabouts/saw_move content channels), and finding 2 names the label that is measuring a different detector than the one that ran.

NOT RE-REPORTED (verified current, per the known-open list): the production-side duplicate alibi_vs_sighting mint is the declared carry — finding 4 supplies its magnitude and the two ML consumers that still double-count, labelled as a deepening. The audit §10.3 records-free re-derivation loss is declared for the two TEST re-derivations; finding 2 is labelled as a deepening because it names two LIVE consumers (the conviction label, the referee supply gauge) that the audit does not.

NOT COVERED (time/scope): the render side of the flag surface (meetings/render_contract.py and the prompt templates) beyond confirming that descriptions render verbatim; the transcript reconstruction path (reconstruct_stated_paths / absent_players) beyond its call from detect_contradictions; corroboration detection (detect_corroborations) and grounded_vouch_subjects; the frontend flag surface.

===== COVERAGE NOTES FROM finder-memory-render.json (6 findings) =====
SCOPE WALKED. agents/memory/store.py (2442 lines, read in full across the render, coalescer, breadcrumb/co-presence/transition collectors, trail, belief/contradiction line builders, budget assembler, and the three absorb wrappers), agents/memory/episodic.py, agents/memory/working.py, agents/memory/beliefs.py (constants, SuspicionProvenance, BeliefState, apply_observation_rules, apply_contradiction_rule, apply_meeting_evidence_rules), agents/perception.py::ingest_packet and its two Rule-1 input builders, plus the consumers that read the same stores: orchestrator/game.py (TacticalAgent's suspicion_graph_for_meeting / absorb / note_meeting_concluded and _absorb_meeting_beliefs), meetings/manager.py::_suspicion_graph_with_contradictions and the ballot re-render, agents/tactical/features.py's last-seen and meeting-history reads, training/surrogate/dataset.py's hand-mirrored fold, orchestrator/replay.py::fold_meeting_outcome_into_memories, and eval/evidence_honesty.py + eval/leak_scan.py as the audit machinery.

EVIDENCE BASE. Corpus scans ran over all 200 committed replays in replays/ml_corpus (154 x 9p2i + 46 x 4p1i), 5225 rendered memories inside recorded prompts. All scan scripts and the four repro scripts are under /private/tmp/claude-501/.../scratchpad/wave0/B/. Three findings carry a runnable repro against the real `render_for_prompt` / `ingest_packet`; no tracked file was modified and the full suite / campaign tier were not run.

CHECKED AND CLEARED (no finding). (1) Token-budget arithmetic: `_assemble_view` charges every separator piecewise with ceiling estimates, so the sum over-counts and the render cannot overrun `token_budget` except when the non-elastic block alone exceeds it (documented, deliberate). (2) Coalescing never DROPS a row: only rows covered by the spawn-group summary are elided, and `spawn_end = min(last ticks)` guarantees the summary's range is covered by every member (store.py:1673-1688). (3) Render determinism: `grouped` iteration is episodic-append-ordered and the final sort key `(-salience, -tick, line)` is total. (4) The `[obs ...]` id universe: `observation_ids_for_meeting` (game.py:3176-3182) returns every stamped row, so a span citing its FIRST row's id is always resolvable. (5) The packet-clock +1 offset on completed-task and witnessed-kill lines is a real, systematic convention, but it is DECLARED and calibrated (`AGENT_CLOCK_OFFSET`, eval/evidence_honesty.py:215) and mirrored in training/surrogate/dataset.py:909-912 — not a defect. (6) Task redistribution cannot give one crewmate two instances of the same `map_task_id` (engine/tick.py:349-353), so the frozenset-based completion diff at store.py:1502-1512 cannot silently swallow a completion. (7) `derive_observation_id` seq continuation and the duplicate-id guard (episodic.py:36-50, 109-136) are sound. (8) The role-disclosure entitlement of the `## Meetings so far:` block is independently asserted by eval/leak_scan.py:263-321 and is wired into eval/leak_test.py. (9) The meeting-index tag and the `## Meetings so far:` numbering agree because the orchestrator folds evidence before testimony (orchestrator/game.py:2365-2380) — verified against a recorded prompt. (10) The persistent absorb bumps each accused subject exactly once: the pre-vote fold runs on a manager-local seeded copy (meetings/manager.py:2448-2489), never on the stored state, so there is no double count.

KNOWN-OPEN ITEMS TOUCHED, NOT RE-REPORTED. C-83 (import-time prompt-loader side effects) and C-107 (test-infrastructure layer) were visible but untouched; the five independent hand-rolled perceive->absorb reconstruction loops (eval/evidence_honesty.py, eval/off_menu.py, eval/funnel.py, scripts/counterfactual_phase20.py, training/surrogate/dataset.py) are a C-107-adjacent duplication that already carries its own parity gauge (`measure_belief_render_parity`, training/surrogate/dataset.py:1140-1200), so I did not open it as new.

NOT COVERED. I did not run `pytest -m campaign`, the full suite, or scripts/check.sh (per the brief), so the nine declared red pins were not re-observed. I did not analyze transcript social content (Track A's material). The suspicion-provenance sum invariant was read but not numerically stress-tested across a full replay; the surrogate mirror's `_absorb_body_proximity` omits the `source=` kwarg that production passes (training/surrogate/dataset.py:736-738 vs agents/memory/beliefs.py:1174-1178), which lands the lift in `unattributed` rather than `body_proximity` — inert today because the J1 predicate exempts `unattributed` and no surrogate feature reads the split, so I left it out of the findings rather than inflate the count.

===== COVERAGE NOTES FROM finder-eval-instruments.json (7 findings) =====
Read in full: eval/replay_walk.py (all 602 lines, all 9 profiles), eval/solvability.py, and the resolver/fold regions of eval/evidence_honesty.py (compute/_report/_fold_game/_fold_meetings/_fold_flags/_resolve_flag/_dedupe_flags/_sighting_placement/_supports_placement/_fold_grounding/_fold_movement_origin/_fold_whereabouts/_fold_prompts/_assert_clock_alignment), eval/vote_correctness.py's compute+predicates, eval/watchability.py's _testimony_vehicle / D2 / supply-gauge / floor-pin regions, and eval/leak_test.py's header (it is a pytest wrapper; the scanners live in eval/leak_scan.py and the leak-scan-factory profile is deliberately check-free over replays the harness just wrote in-process — no re-ground exposure found).

Independent recomputation, run rather than asserted: (1) solvability — a from-scratch same-room candidate-set implementation that never calls eval.solvability's own `candidate_set_for_body_meeting` reproduces EVERY headline cell exactly on three sets (ml_corpus/4p1i killer_in_set 37/37, singleton 4/37, singleton_correct 4/4, cleared_ejections 0/22; samples/9p2i 126/144, 20/144, 14/20, 19/91; ml_corpus/9p2i 355/400, 51/400, 49/51, 49/248) — the fold agrees; (2) vote_correctness — a mirror over the raw meeting rows reproduces all four documented rates to the digit (0.9176 / 0.9500 / 0.9016 / 0.9286); (3) watchability — my recomputation of the two Layer-1 gauges reproduces the pinned baseline-7 9p2i floors exactly (flags_per_meeting 134/152 = 0.881578947368421, testimony_backed_conversion 80/115 = 0.6956521739130435), and compute_watchability itself returns measured == floor on all three. So the arithmetic is sound everywhere I checked; the findings above are about what the folds READ, not how they add.

Also checked and found clean, so as not to be re-audited: the 20.43 dedup (`_dedupe_flags`) drops 7 of 71 alibi_vs_sighting on ml_corpus/9p2i and 2 of 29 on samples/9p2i, leaves every other kind untouched, and leaves no unresolvable flag behind (the `_fold_flags` guard at :2141 never fires on committed bytes); `_persisted_vent_flag_count` and the re-derived census are genuinely disjoint (the re-derivation minted zero vent_sighting in 604 meetings), so the merge is not a double count; MemoryStore.recent(since_tick=0) is uncapped, so no grounding search is silently windowed.

Context the re-ground should carry, not re-discovered as a finding: on baseline-7 bytes 100% of alibi_vs_sighting flags are WEAK (71/71 and 29/29), so three evidence-honesty cell families (I-3 sole-flag precision, I-4 grounded sighting, I-6 adjacent-room) are 0/0 across all four sets. That is already committed and pinned (tests/eval/test_evidence_honesty.py:1335-1367, "The class emptied"), but it means the instruments most likely to catch a detector regression are currently blind, and finding 4 above is unobservable for exactly that reason.

Seams the fit touches that I did not audit in depth (out of dimension, flagged for whoever owns them): training/surrogate/dataset.py:126 imports `eval.funnel._walk_game_vj` for the 17.10 belief-render parity cross-check, and training/bakeoff/{harness,goodhart}.py + training/crew/scorer.py import `eval.validity.run_validity_gate`, `eval.watchability.compute_watchability` and `eval.leak_scan.scan_factory_packets` — the watchability seam is where findings 1 and 3 land. Not run, per the ground rules: the full suite, `pytest -m campaign`, and scripts/check.sh; no tracked file was created or modified.

===== COVERAGE NOTES FROM finder-training-path.json (13 findings) =====
Scope covered: training/surrogate/{dataset,fidelity,ballots,runner}.py, training/conviction/{dataset,fidelity,model,serving}.py, training/composed_runner.py, training/rewards.py, training/bakeoff/{harness,map_elites}.py, training/crew/scorer.py, training/coevo/{driver,hall_of_fame}.py, scripts/verify_ml_evidence.py, eval/watchability.py's baseline registry, and the committed artifacts under training/artifacts/ + training/reports/. All work was read-only; no tracked file was modified. Live recomputations run: the fit-corpus fingerprint, the surrogate fence, `fo6_rebaseline` + the FO-6 tau curve, `run_surrogate_fidelity` + `decide_go_no_go` on the frozen predictor, and `run_conviction_fidelity` + `decide_conviction_go` — all offline, pure, and cheap (the corpus table builds in ~6s). No full suite, no `-m campaign`, no check.sh.

SPLIT HYGIENE / LABEL LEAKAGE: audited and found CLEAN, deliberately so. `_game_folds` (training/surrogate/fidelity.py:567-651) validates a committed split for disjointness, full partition, and non-empty SCOREABLE meetings on both sides; the ballot model's leakage fence (training/surrogate/ballots.py:43-52, :798-835) reads label columns only on the fit side and refuses views from outside the declared fit seeds; coerced-SKIP rows are excluded fit-side only; the conviction side re-validates the same split (training/conviction/dataset.py:352-401) and never scores the fit side. `replays/ml_corpus/9p2i/splits.json` verifies clean: 90/30/30, rule 'seed mod 5: {0,1,2}=train, {3}=val, {4}=test', zero overlaps, test side is exactly the seed%5==4 bucket, and the bake-off's eval seeds (`load_eval_seeds`, harness.py:289-316) come from that same bucket while the committed MAP-Elites `fitness_seeds` [1000,1001,1002,1005] are disjoint from it. The honest ceiling is measured on the scored (test-side) population only. I found nothing to report on this sub-dimension — the defects are all in the BARS and the OBJECTIVE, not in the splits.

KNOWN-OPEN ITEMS verified in passing, not re-reported: the declared corpus grounding gap is exactly the one pair of digests (live 45b11993… vs fit-record 164ef00c…) and the surrogate load fence fails loud on it, so the surrogate-path bake-off is correctly hard-blocked today; the nine red campaign pins' underlying disagreements reproduce as expected (conviction spearman 0.578->0.699, recall 0.957->0.936, FO-6 top-1 0.650->0.418, MAP-Elites pool stamp e454… vs live ff7a…).

WHAT THE RE-GROUND CONTRACT MUST INCLUDE (the concrete ask): (1) a pre-registered decision about axis 3 of the surrogate bar — re-fitting alone re-produces NO-GO; (2) retire FO-6's tuned decision head as a comparator and state the two trivial constants instead; (3) a weight seam on `inner_episode_fitness` / `crew_inner_episode_fitness` plus a decision on the kill triple-count and the loss-outranks-win crew objective, since 'optimise better' is not expressible today; (4) a third (accuracy/precision) axis on the conviction verdict before it is re-taken; (5) a `fit-corpus.json` for the conviction artifact and a per-instrument grounding row; (6) a committed surrogate `verdict.json` with a loader that gates; (7) recompute-and-compare validation of `CoevoCampaignConfig.substrate_sha256`; (8) the STALE deletion spelled out as invert-these-five-tests, not delete-them; (9) `BAKEOFF_BASELINE_ID` -> baseline-7 together with the stale note at eval/watchability.py:908-912 and a statement about the baseline-5 bake-off rows.

NOT COVERED (out of budget or out of dimension): training/anchor_study.py's own substrate composite, training/bakeoff/goodhart.py's probe internals beyond its entry points, training/bakeoff/{es,bc,policy_es,utility_es}.py search internals, training/coevo PFSP sampler dynamics and hall-of-fame retirement policy (the co-evolution STABILITY question is only partly answered here — I audited the substrate fence, not the population dynamics), and training/scenarios.py.

===== COVERAGE NOTES FROM finder-gates-scripts.json (7 findings) =====
Dimension: gates and operator scripts. Read at HEAD (d8ec0a1c, clean tree): scripts/check.sh in full, scripts/verify_samples.sh, scripts/setup_env.sh, scripts/validity_gate.py in full, both CI workflows (.github/workflows/ci.yml, campaign-tier.yml), the argument-parse + preflight + splits-only + dry-run + lock/worker sections of scripts/record_ml_corpus.sh and scripts/refresh_samples.sh, the leg registry / grounding / amnesty / sidecar / exit-code machinery of scripts/verify_ml_evidence.py, check_doc_facts.py's check registry and check_ml_results_table in full, scripts/validate_task_docs.py + scripts/_task_parser.py's parse_all_tasks, and the matching test files (test_gate_invocation, test_record_ml_corpus, test_refresh_samples, test_verify_ml_evidence, test_check_doc_facts headers).

Commands actually run (all read-only): `uv run python scripts/verify_ml_evidence.py --only corpus --fast`, `--only recompute`, `--only sidecars`; `uv run python -c` probes of orchestrator.replay.substrate_slate_mismatches / SUBSTRATE_FLAG_KEYS / orchestrator.game.PROMPT_VERSION_SETS; a stub-uv replay of scripts/check.sh (scratch only, AILIBI_SKIP_FRONTEND=1) to enumerate its legs. No pytest run, no check.sh gate run, no campaign tier, nothing written outside the scratchpad.

Verified-and-cleared (no finding): orchestrator.replay.substrate_slate_mismatches is correct for the empty slate and refuses a graduated lever name in both branches (`substrate_slate_mismatches([])` → `[]`; the wanted-minus-toggleable loop at orchestrator/replay.py:687-694 names a registry lever as graduated and anything else as unknown), so the recorders' pre-spend guard is sound now that --expect-levers must be empty, and audits/audit-phase-20-baseline-7.md:901-905 already documents the `--expect-levers ""` invocation. record_ml_corpus.sh's --expect-levers parse treats an explicitly empty value as the bare slate and only a MISSING argument as an error (:227-238), pinned by tests. The dry-run path does run the preflight (:826) as its comment claims. verify_samples.sh's bare-invocation walk aggregates status across sets and exits 2 on an empty root — no set can be silently skipped. check.sh's env validation is loud for both AILIBI_SKIP_FRONTEND and AILIBI_PYTEST_SERIAL, and `set -euo pipefail` masks nothing I could find (the frontend leg's `&&` chain runs in a subshell whose failure propagates). fit_corpus_fingerprint covers replay bytes + splits.json + MANIFEST.md over the single set the fits actually use (9p2i everywhere: training/anchor_study.py:143, training/bakeoff/harness.py:168, training/surrogate/runner.py), so its single-set scope is not a gap. The amnesty _DECLARED_GROUNDING_GAP is a digit-for-digit pin (scripts/verify_ml_evidence.py:196-206) and run_recompute raises EvidenceError if a named amnesty row stops being emitted (:1927-1934) — both good.

Answer to 'which checks would a Wave-1 fix + combined re-record trip, and are they all loud?': the default tier DOES carry the tripwire — tests/scripts/test_verify_ml_evidence.py:372 asserts `grounding.status == "STALE"` and pins six (measured, committed) figure pairs, so a re-record makes _is_declared_grounding_gap false, the grounding row FAIL, and that test red; tests/training/test_surrogate_runner.py:504 and tests/training/_regrounding.py hold the mismatch from the model side. Those are loud. The gaps are the three amnestied rows with no value pin (finding 3), the samples-side prompt-version drift class with no gate at all (finding 2), and the fact that neither scripts/verify_ml_evidence.py nor scripts/verify_samples.sh is invoked by scripts/check.sh or by either CI workflow — they are close-audit commands an operator must remember, which is fine as a declared design but means findings 3 and 5 are only ever seen when someone runs them by hand.

Known-open items re-verified in passing and NOT re-reported: the nine campaign-tier failures (declared, routed to the re-ground); BAKEOFF_BASELINE_ID still "baseline-6" at training/bakeoff/harness.py:181 against eval/watchability.py:914 "baseline-7" (the declared move); F4 (audits/README.md absent from _LADDER_TIP_DOCUMENTS); C-46, C-83, C-126, C-130. One adjacent observation not raised to a finding: tests/training/_regrounding.py has no self-expiry — its helper keeps working unchanged after the re-ground (it re-points corpus_sha256 to a fingerprint that will then already match), so nothing forces its deletion and its two callers at tests/training/test_bakeoff_harness.py:361,560 would silently keep bypassing the Task-18.14 fit-corpus fence forever; worth a deletion line on the re-ground checklist.

Not covered by me (out of dimension or deliberately skipped): scripts/fetch_evidence.sh (39KB, evidence-branch restore — touched only via verify_ml_evidence's ABSENT rows), scripts/counterfactual_phase20.py, scripts/generate_campaign_tables.py, scripts/measure_baseline.py, scripts/build_demo_bundle.py, and the bulk of check_doc_facts.py's ~30 individual checks beyond the ML results table (I sampled the registry and the one check the re-ground republishes into).

===== COVERAGE NOTES FROM finder-api-frontend.json (5 findings) =====
SCOPE COVERED. api/main.py (whole file: CORS posture, replay-dir anchoring ladder, exception handlers), api/routes/{replays,sets,eval}.py (whole), api/replay_loader.py (substrate/policy stamps and their guards, collection-view containment, LRU cache keying, SetLoaderRegistry + set-name validation + default_set resolver, rubric staleness + set fingerprint), api/schemas.py (TurnView/ObservationClaimView/GateView/BeliefFrameView/MeetingView), frontend/src/{lib/*.ts, store/replayStore.ts, api/client.ts, types/api.ts} and the meeting/map/belief/cost components, frontend/e2e/*.

VERIFIED CLEAN (checked, no finding). (a) Substrate integrity of the corpora: all 300 committed replays under replays/samples + replays/ml_corpus are stamped and every stamp equals `substrate_flag_snapshot()` exactly, with no extra keys — nothing in the recorded bytes will poison the re-ground on the API side. (b) The set-name path-traversal guard (`_validate_set_name` at api/replay_loader.py:3348) and the `_is_set_dir` leaf-vs-parent rule correctly keep `replays/ml_corpus/` from being served as a set by the default resolution ladder. (c) The Python->TS codegen drift gate IS enforced in pytest (tests/api/test_view_model.py:1313-1330 diffs the committed `api.ts` / `api.fidelity.ts` against a fresh render), even though `gen_frontend_types.py --check` is absent from scripts/check.sh. (d) The rubric provenance key is fresh for the served 9p2i set (`stale=False`, `git_head=multi:fbdfaedea493`) and its producer/loader lockstep is pinned (tests/api/test_sets.py:364-372); the duplicated `_set_fingerprint` in experiments/lab/rubric_score.py:1289 is covered by that pin. (e) The staleness banner IS rendered in both consumers (ReplayPicker.tsx:481, TournamentDashboard.tsx:855). (f) `GateView.passed`/`leader` are read, not recomputed, by MeetingView's `gateReadout`, and their agreement with the recorded outcome is pinned in tests/api/test_view_model.py. (g) The sabotage overlay reads `tick.sabotage` per frame (no forward accumulation), so it is not a second phantom-bodies class. (h) `?set=` is threaded at every call site, and replayStore's mid-flight game-id+set guards are unit-tested (replayStore.test.ts:181-207).

OBSERVATIONS NOT RAISED AS FINDINGS. (i) `_substrate_cache_key` (api/replay_loader.py:985-1000) returns None for the default loader on the reasoning that "its guard raises on any mismatch before a wrong-substrate reconstruction could be cached" — true only for STAMPED replays; an UNSTAMPED one skips the guard yet still reconstructs under ambient levers. Latent only: every committed replay is stamped, and the single live toggle (`impostor_roll_call`) is prompt-side and does not affect reconstruction. Worth a one-line docstring correction when the guard is touched. (ii) `getEvalCostSummary` (frontend/src/api/client.ts:315) is dead in the app (referenced only by a stale vi.fn() in replayStore.test.ts:34) and would be set-unaware if revived. (iii) `windowReplay` (replayStore.ts:248) blanks `prompt_text`/`response_text` to `""` rather than a sentinel, so "windowed out" is indistinguishable from "genuinely empty" — no consumer depends on the difference today.

NOT RE-REPORTED (known-open, verified current in passing): C-80 (the frontend derivation layer half-built — the whereabouts finding is a NEW instance of that class, labelled as such), C-101 (frontend coverage gap — the meeting-transcript finding names a specific, defect-backed slice of it), the 1440x900 e2e gap, F2 stale narrations, C-79, C-107. Not run per the ground rules: the full suite, `pytest -m campaign`, `scripts/check.sh`, and the Playwright e2e.
```
