# Agent Prompt — 20.32 The impostor mover stops declining free kills and stalking ejected players

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.32 — The impostor mover stops declining free kills and stalking ejected players, anchored to C-3 [audits/review-2026-08-19/B/verdicts.md claim 5 — CONFIRMED and "understated"; the register row at audits/review-2026-08-19/B/collated-findings.md C-3 still quotes the pre-verification 387/233/126, superseded there by the verified 415/225/190]; C-4 [audits/review-2026-08-19/B/collated-findings.md C-4, measured in audits/review-2026-08-19/B/agents-tactical.md §2 F2 — reviewer-measured, NOT adversarially re-verified, so it is corroborated here by G-12 rather than relied on alone]; G-12 [audits/review-2026-08-19/A/verdicts.md claim 12 — CONFIRMED-BUG over 300 games / 10,335 impostor decisions with 0 mismatches against the recorded action stream]; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.12 (the two-line fix), §5 ruling R3 (defect-not-lever; pre-register as a named co-intervention), §4 row 1.8 and the caveat table row 9 (the ML comparator errata this repair retires); anchors re-verified at HEAD — agents/tactical/impostor_policy.py:413-453 (the kill seam; `best = targets[0]` at :414, the co-location re-validation at :431-434, the walk-toward-best fall-through at :447-451), :825-869 (`_kill_available_now`, the same `targets[0]`-only shape at :858), :872-898 (`_confirmed_dead_from_bodies`, `saw_body` only), :996-1068 (`_scored_targets`, the `(-score, player_id)` sort at :1067), :187 (`_STALENESS_THRESHOLD = 30`), :1275-1312 (`_idle`, the pretend-task blend the fall-through lands in); agents/memory/store.py:110 and :433-440 (the `meeting_boundary` episodic marker every living agent receives at the resume tick), :549-575 (`record_meeting_outcome`), :134 (`AgentMemory.meeting_history`); agents/memory/working.py:176-185 (`MeetingHistory.record`); agents/tactical/features.py:678-696 (the v3 encoder, today's only meeting-history consumer); orchestrator/game.py:2297-2306 (the per-living-agent post-meeting fold), :2644 (the policy is handed `memory.episodic` only); api/replay_loader.py:1352-1379 (the replay-side mirror of that fold — beliefs and testimony, never the meeting outcome); agents/perception.py:62-82 (no ejection event type exists); engine/visibility.py:98-127 (the impostor keeps `same_room_and_adjacent` at base visibility); engine/rules.py:56-107 (the engine kill backstop, `:71-85`, with Task 20.11's in-vent guard at `:60-68`); agents/tactical/learned/forward.py:404-413 and training/bakeoff/utility_es.py:426-430 (both option enumerators call the policy's private statics); orchestrator/replay.py:234 (`TacticalPolicyStamp`), :319 (`FSM_DEFAULT_POLICY_ID`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-impostor-fsm-repair`
**Depends on:** 20.15 (the free-kill and ghost-top cells become committed instruments with pinned baseline values first, so this task re-derives them under the revised policy instead of inventing a second harness; the same task also makes the read-only reconstruction pass over the impostor policy module and its test file, and a read-only pass must land before a behaviour change to the same two files); also after 20.22 (the co-intervention is declared in the ratified memo before it lands)
**Section refs:** C-3 [audits/review-2026-08-19/B/verdicts.md claim 5 — CONFIRMED and "understated"; the register row at audits/review-2026-08-19/B/collated-findings.md C-3 still quotes the pre-verification 387/233/126, superseded there by the verified 415/225/190]; C-4 [audits/review-2026-08-19/B/collated-findings.md C-4, measured in audits/review-2026-08-19/B/agents-tactical.md §2 F2 — reviewer-measured, NOT adversarially re-verified, so it is corroborated here by G-12 rather than relied on alone]; G-12 [audits/review-2026-08-19/A/verdicts.md claim 12 — CONFIRMED-BUG over 300 games / 10,335 impostor decisions with 0 mismatches against the recorded action stream]; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.12 (the two-line fix), §5 ruling R3 (defect-not-lever; pre-register as a named co-intervention), §4 row 1.8 and the caveat table row 9 (the ML comparator errata this repair retires); anchors re-verified at HEAD — agents/tactical/impostor_policy.py:413-453 (the kill seam; `best = targets[0]` at :414, the co-location re-validation at :431-434, the walk-toward-best fall-through at :447-451), :825-869 (`_kill_available_now`, the same `targets[0]`-only shape at :858), :872-898 (`_confirmed_dead_from_bodies`, `saw_body` only), :996-1068 (`_scored_targets`, the `(-score, player_id)` sort at :1067), :187 (`_STALENESS_THRESHOLD = 30`), :1275-1312 (`_idle`, the pretend-task blend the fall-through lands in); agents/memory/store.py:110 and :433-440 (the `meeting_boundary` episodic marker every living agent receives at the resume tick), :549-575 (`record_meeting_outcome`), :134 (`AgentMemory.meeting_history`); agents/memory/working.py:176-185 (`MeetingHistory.record`); agents/tactical/features.py:678-696 (the v3 encoder, today's only meeting-history consumer); orchestrator/game.py:2297-2306 (the per-living-agent post-meeting fold), :2644 (the policy is handed `memory.episodic` only); api/replay_loader.py:1352-1379 (the replay-side mirror of that fold — beliefs and testimony, never the meeting outcome); agents/perception.py:62-82 (no ejection event type exists); engine/visibility.py:98-127 (the impostor keeps `same_room_and_adjacent` at base visibility); engine/rules.py:56-107 (the engine kill backstop, `:71-85`, with Task 20.11's in-vent guard at `:60-68`); agents/tactical/learned/forward.py:404-413 and training/bakeoff/utility_es.py:426-430 (both option enumerators call the policy's private statics); orchestrator/replay.py:234 (`TacticalPolicyStamp`), :319 (`FSM_DEFAULT_POLICY_ID`)
**Complexity:** Medium
**Record impact:** none for committed bytes — reconstruction replays the recorded action stream and never re-invokes a policy, so every committed replay, hash chain and MANIFEST stands; the change is a declared co-intervention in the Phase-20 pre-registration and first reaches recorded bytes at the adopting record.
**Measurement:** `uv run pytest tests/agents/test_impostor_policy.py tests/agents/test_learned_policy.py -q` green and `bash scripts/verify_samples.sh` 100/100; the committed-bytes counterfactual cells over the 50 samples/9p2i replays pasted into the PR's Summary with before beside after — free zero-witness kills declined 190/415 (45.8%) → 22/415 (5.3%), bar `< 10%`; ghost-top decisions 303/2461 (12.3%) → the 222 ejected-subject decisions 0 and the partner's-unseen-victim residual (≤ 81) quoted as measured; blocked kills 30 across 9/50 games → 0.

The impostor FSM declines almost half of its free kills for a string comparison. Over the
50 committed `replays/samples/9p2i` replays the C-3 verification counted 2,461 impostor
decisions, 415 of them carrying a legal zero-witness kill (the predicate derived from
`engine/rules.py:56-107` and `:29-44`, not from the policy's own view), and 190 of those
declined — 45.8%. 168 of the 190 are exact `1.0` score ties broken by the lexicographically
lower player id: `_scored_targets` (`agents/tactical/impostor_policy.py:937-1009`) carries
no proximity term at all, so a victim standing in the impostor's own room and one seen
alone in an adjacent room score identically, and the kill seam re-validates only
`targets[0]` (`:355`, `:372-375`). The unit repro is one line of difference: with the ids
one way the FSM walks out of the room it could have killed in, with them swapped it kills.
`_kill_available_now` (`:766-810`) inherits the same `targets[0]`-only shape at `:799`, so
the SABOTAGE lever can fire on a tick that carried a free kill. All numbers here are
review-measured over the committed baseline-6 bytes and re-pinned by the instrument task.

The same ranking keeps dead players at the top of the hunt. `_confirmed_dead_from_bodies`
(`:813-839`) builds the dead set from seen bodies only; an ejection mints no body and a
partner's victim's body is never seen, so an ejected player stays a maximum-score target
until the sighting ages past `_STALENESS_THRESHOLD = 30` (`:185`). G-12 measured this by
re-running the real `decide()` on rebuilt memory across 300 committed games with 0
mismatches against the recorded actions: on samples/9p2i, 303 of 2,461 decisions (12.3%)
rank a dead player first — 222 of them an ejected player, 81 the partner's unseen victim —
in 22 of 50 games, blocking 30 kills across 9 games. Seed 36 tick 50 is the demonstrable
case: `p-6` was ejected at tick 34 and still outranks `p-7`, alive, isolated, in the
impostor's own room, cooldown 0, on the string `"p-6" < "p-7"`; `p-7` completes the
fourteenth task at tick 51 and the crew wins a game that killing at tick 50 would have
taken to parity. Both 4p1i sets are 0/100 — the defect exists only on the 9p2i roster,
which is to say it biases exactly the canonical eval baseline downward. The ejections are
already in memory (`agents/memory/store.py:549-575` folds them into
`AgentMemory.meeting_history`, `agents/memory/working.py:176-185`); the FSM has simply
never had a channel that reaches them.

The third symptom is the pacing artifact. A sighting whose room the impostor is standing in
and can see is empty stays the best lead for the full 30 ticks, so the FSM walks to a room,
finds nobody, blends one step toward its pretend task, is re-attracted by the same stale
sighting and walks back. C-4 measured 298 of 880 stalk moves (34%) heading toward a
refuted sighting and reproduced a 25-tick oscillation; G-12 independently attributes only
about 42-46% of the A↔B windows to dead subjects, the rest to exactly this fall-through
against a live but refuted stale target — so removing the ghosts alone would leave the
artifact half-standing. C-4 is the one finding in this contract that was not adversarially
re-verified; it is taken here only where G-12 corroborates it.

This is a defect repair, not a balance lever, and that distinction is the reason it ships
in the same phase as the substrate work rather than after it. Ruling R3 in
audits/review-2026-08-19/D/FINAL-synthesis.md is explicit: C-3 and G-12 are bugs that bias
a measured baseline, every design lever stays out, and the repair is pre-registered as a
named co-intervention so the attribution stays honest. The stake is the comparator: the
ML program's headline "+0.12-0.30 win edge over the same-seed FSM" was measured against an
inner loop that discards 45.8% of its free kills and spends 8-12% of its decisions hunting
someone the whole table watched get ejected. Committed bytes do not move here — the replay
walk applies recorded actions and `orchestrator/replay.py:234` stamps the policy rather
than re-running it — so this task's evidence is a per-decision counterfactual over frozen
inputs, and the behaviour first reaches recorded bytes at the adopting record.

One design constraint dominates the implementation. `agents/tactical/learned/forward.py:404-413`
and `training/bakeoff/utility_es.py:426-430` both call the policy's private statics
(`_scored_targets`, `_confirmed_dead_from_bodies`, `_target_colocated_now`,
`_defers_to_colocated_fellow` and six more) to build the ES champion's option menu, and
`tests/agents/test_learned_policy.py:377-406` and `:462` pin the two enumerators bit-exact
against each other. Those statics are frozen: every new behaviour in this task composes
NEW private helpers inside `decide()` over the tuple `_scored_targets` already returns.
That is not merely safe, it is the correct target state — the review's own reading is that
the learned menu already enumerates `kill_now` for every co-located target, "so the ES
champion is not affected — the FSM is" (audits/review-2026-08-19/B/agents-tactical.md §2
F1). This task moves the FSM onto the behaviour the learned menu has had all along.

**Files in scope:**
- agents/tactical/impostor_policy.py; (the kill seam and the sabotage guard re-validate co-location across ALL scored targets; the decision-time target set excludes players ejected at a concluded meeting; a refuted sighting — the room since entered and the subject absent — is dropped for good; proximity enters as a tie-break tier below the score; the shared statics both option enumerators call stay byte-identical)
- tests/agents/test_impostor_policy.py; (the free co-located victim beside a higher-ranked remote one → KillIntent with the ids swapped both ways; an ejected target never ranks; the refuted-sighting drop; the two re-fixtured stalk-ordering tests; the committed-bytes counterfactual cells over samples/9p2i)
- eval/determinism_test.py; (the scripted fixtures stay deterministic — expected to be a zero-line diff, since the fixtures are recorded action streams and no policy runs in this module)
- eval/evidence_honesty.py; (ORCHESTRATOR RULING 2026-08-20 — the I-11 fold gains an explicit policy parameter defaulting to the live policy, and its fidelity guard applies only when the caller asserts it: the ratified I-11 baseline values become frozen constants measured at the pre-repair sha, quoted from the ratified memo, and the live-policy fold over the baseline-6 bytes becomes THIS repair's own counterfactual 'after' cell. I-11 is §5 secondary, observed-not-gated, so no ratified bar moves)
- tests/eval/test_evidence_honesty.py; (the module fixture split so the I-2…I-10 pins never invoke the policy fold; the I-11 pin tests quote the ratified constants and add the repaired-policy 'after' cells)
- tests/scripts/test_measure_baseline_cli.py; (the --honesty emitter labels the I-11 block by mode: ratified-baseline constants vs live-policy fold)
- audits/audit-phase-20-preregistration.md; (§11 amendment log ONLY — one dated entry recording the I-11 instrument-mode change and that no bar rides I-11)

**Files NOT in scope:**
- agents/tactical/learned/ (the ES champion and its option menus are frozen; the parity gates stay green — if a shared option enumerator or any static it calls must change, STOP and report)
- training/ (frozen; the comparator change is recorded in the pre-registration, not in training code — and `training/env.py:441` wraps the FSM as the surrogate's proposal, so a moved training-side value pin is a report, never a silent re-pin here)
- orchestrator/game.py (`:2644` hands the policy `memory.episodic` and this task does not widen that call; the ejection signal is derived from episodic memory instead)
- agents/memory/ (no new memory channel and no new event type; the post-meeting marker is read, never written)
- orchestrator/replay.py (the policy stamp id stays `fsm-default`; the record's MANIFEST git sha is the provenance of the revised FSM, stated in the record audit)
- agents/strategic/prompts/ and every `.j2` (no template edit belongs in any task but the single prompt-set bump)

**Definition of done:**
- [ ] The kill seam and the sabotage guard pick the kill target by scanning the ranked targets for the first co-located, zero-witness, non-deferred candidate instead of testing only `targets[0]`: a free co-located victim beside a higher-ranked remote one yields a `KillIntent` naming the victim, pinned in `tests/agents/test_impostor_policy.py` with the two ids swapped both ways, and the same shared helper backs `_kill_available_now` so SABOTAGE can no longer fire on a tick carrying a free kill (fixture-pinned both directions).
- [ ] No player ejected at a concluded meeting can occupy the ranking on a later decision, derived from episodic memory alone: a sighting recorded before the most recent post-meeting marker cannot rank, pinned as a unit fixture and on the reconstructed seed-36 tick-50 state where the ejected `p-6` outranks the co-located, isolated, cooldown-0 `p-7` at HEAD.
- [ ] A refuted sighting is dropped for good — once the agent has itself been in the sighting's room on a later tick without seeing the subject there, that subject stops driving STALK; pinned as a unit fixture and on the reconstructed seed-31 run (ticks 14-43, the ejected `p-1`), where the fall-through now settles into the pretend-task blend instead of alternating A↔B, asserted as a decision sequence with no room repeated in alternation.
- [ ] Proximity enters the ranking as a tier BELOW the score (`(-score, proximity_rank, player_id)`, own room ahead of adjacent ahead of remote), never above it; `test_stalk_picks_alphabetically_first_id_when_scores_tie` (`tests/agents/test_impostor_policy.py:555`) and `test_stalk_prefers_more_isolated_target_over_witnessed_one` (`:575`) are re-fixtured to pin the new rule, with an equidistant pair still falling to the player id and an isolated remote target still beating a witnessed neighbour.
- [ ] The committed-bytes counterfactual is pinned in `tests/agents/test_impostor_policy.py`, computed per decision over the reconstructed inputs of the 50 committed samples/9p2i replays with no re-simulation, the harness first asserting 0 mismatches between `decide()` and the recorded action stream at HEAD: free zero-witness kills declined 190/415 (45.8%) → only the 22 legitimate misses (15 fellow-impostor defers, 7 COVER-body) = 22/415 (5.3%) against a `< 10%` bar; ghost-top decisions 303/2461 (12.3%) → the 222 ejected-subject decisions go to 0 and the partner's-unseen-victim residual (≤ 81, the half a kill-knowledge channel would be needed to close and the ruling excludes) is pinned as measured; blocked kills 30 across 9/50 games → 0. Every before value is quoted beside its after, and a measured value that differs from the prediction is explained, not re-barred.
- [ ] No recorded kill is lost: at the 225 reconstructed states where the recorded impostor emitted a kill, the revised policy still emits the same `KillIntent`, asserted by the same harness.
- [ ] The frozen learned path does not move: `agents/tactical/learned/forward.py` and `training/bakeoff/utility_es.py` still call `_scored_targets`, `_confirmed_dead_from_bodies`, `_target_colocated_now`, `_defers_to_colocated_fellow`, `_body_visible_rooms`, `_non_teammate_witness_present`, `_crew_near_task_win`, `_sabotage_window_open`, `_active_sabotage` and `_vent_in_room` with unchanged signatures and unchanged returns; `uv run pytest tests/agents/test_learned_policy.py tests/training -q` is green, the bit-exact Q4 parity gate included.
- [ ] Committed bytes are untouched: `bash scripts/verify_samples.sh` is 100/100 and `eval/determinism_test.py` carries a zero-line diff — reconstruction replays recorded actions and the determinism fixtures are scripted action streams, so neither can move; if either does, STOP and report rather than re-pinning.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 0 — blast radius before scope. Run `grep -rn "ImpostorPolicy\._" agents/ training/ experiments/`.
It returns ten private statics consumed from outside the module by BOTH option enumerators
(agents/tactical/learned/forward.py:404-413, training/bakeoff/utility_es.py:426-430). Treat
all nine as frozen — same names, same signatures, same returns for the same inputs. Every
new behaviour in this task belongs in NEW private helpers composed inside `decide()` over
the tuple `_scored_targets` already returns. That single discipline is what keeps the ES
champion's option menu and the bit-exact Q4 parity gate green; touching `_scored_targets`
itself would move both enumerators together and invalidate a frozen artifact.

Step 1 — reproduce the baseline BEFORE changing anything. Rebuild each impostor's memory
tick by tick over the 50 committed samples/9p2i replays: `eval/replay_walk.py` for the
engine walk, `observation.service.ObservationService.build_packet` plus
`agents.perception.ingest_packet` for perception, and at each `MeetingApplied` the SAME
post-meeting fold the replay loader runs at api/replay_loader.py:1352-1379
(`absorb_meeting_evidence` then `absorb_reported_testimony`, per living agent). That fold is
load-bearing here, not cosmetic: the marker step 3 keys on is appended inside
`absorb_meeting_evidence` (agents/memory/store.py:433-440), so a harness that skips the fold
will silently measure the wrong thing. Task 20.15 already ships that reconstruction: `eval/evidence_honesty.py`'s I-11 fold runs
the same walk, the same fold and the same 0-mismatch assertion, and
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` pins 190/415 with
the 168 / 15 / 7 decline split and ghost-top 303/2461 split 222/81 across all four sets.
Re-derive the baseline THROUGH that committed instrument rather than standing up a second
harness; only the 30 blocked kills has no committed cell. Read the Watch items before
editing anything.

Step 2 — the kill seam. Add one helper returning the first co-located, zero-witness
candidate in rank order, and use it in both `decide()` and `_kill_available_now` so the two
copies of the predicate cannot drift apart. Note that at most one target can satisfy it:
`co_present` is counted within the sighting's own tick-and-room bucket, and a target
co-located THIS tick necessarily has its latest sighting this tick in our room, so a second
co-located target lifts both counts above zero. The iteration therefore FINDS the free kill
rather than choosing among several, which is why it is safe and why the ranking order does
not decide which victim dies. Keep the branch order as it stands (vent exit, COVER,
SABOTAGE with the corrected guard, kill / hold / stalk, idle) and keep the fellow-defer and
witness-hold branches exactly as they are. Do NOT take the review's further suggestion to
delete `_kill_available_now` and re-order the ladder — that moves sabotage semantics and
the pins at tests/agents/test_impostor_policy.py:1387-1437, and it is a separate change.

Step 3 — the ejection barrier, derived from episodic memory only. There is no ejection
event in perception (agents/perception.py:62-82) and `decide()` is handed `memory.episodic`
alone (orchestrator/game.py:2644), so `memory.meeting_history` is not reachable from the
policy without a caller change outside this task's files; worse, the replay loader never
populates `meeting_history` at all (api/replay_loader.py:1352-1379 folds beliefs and
testimony, not the outcome), so a meeting-history-based fix would be invisible to every
replay-driven measurement in this repo, including this task's own counterfactual. Use the
signal that IS in episodic memory on both the live and the replay path: the
`meeting_boundary` marker appended at the resume tick for every living agent
(agents/memory/store.py:433-440). Compute the latest marker tick and drop any target whose
latest `saw_player` predates it. An ejected player's last sighting is necessarily
pre-meeting, so the whole ejected class disappears; genuinely stale cross-meeting leads go
with it, which is the intended direction. Mirror the marker string as a module-level `Final`
in the policy with a one-line provenance comment naming agents/memory/store.py:110 as its
producer, and pin the two strings equal in a test — a pinned local mirror is better than
importing a private name across modules.

Step 4 — the refuted-sighting drop, own-room only. A sighting of subject X at tick t in
room R is refuted when a later `self_state` puts the agent in R and no `saw_player` for X
in R is recorded at that tick. Own-room vision is the floor under every visibility mode, so
the rule needs no visibility model and stays correct under a lights sabotage; do not try to
derive adjacent-room vision inside `agents/` (engine/visibility.py:98-127 owns that and
`agents/` may not import `engine/`). The drop must be permanent — a refutation that lapses
the moment the agent leaves the room re-creates the pendulum it exists to remove.

Step 5 — proximity as a tier below the score. Re-sort inside `decide()` on
`(-score, proximity_rank, player_id)`, rank 0 own room / 1 a `public_map.room_neighbors`
entry / 2 otherwise. Do not put proximity ABOVE the score, as one reading of the finding
suggests: a witnessed neighbour would then outrank an isolated remote target and the FSM
would hold beside a crowd instead of hunting — the exact inversion the isolation test
exists to prevent. If a measurement says otherwise, STOP and report instead of ruling on it
here.

Step 6 — re-run the harness and pin the after cells beside the before cells. The predicted
residual is exactly the 22 legitimate declines; a different number means the harness or the
implementation disagrees with the review, and the PR states which.

Watch items. BLOCKER, unresolved at dispatch — read this before starting.
`eval/evidence_honesty.py`'s I-11 fold re-invokes `ImpostorPolicy.decide()` over the
committed bytes and RAISES `EvidenceHonestyReconstructionError` on any mismatch against the
recorded action stream, so this repair does not merely re-price one cell: it makes
`compute_evidence_honesty` raise on every committed set, taking the module-scoped `reports`
fixture in `tests/eval/test_evidence_honesty.py` (all of I-2…I-11),
`tests/agents/test_impostor_policy.py::TestCommittedCorpusTargetingPins` and
`tests/scripts/test_measure_baseline_cli.py::test_honesty_json_emits_array` down with it,
and no committed instrument can then recompute the ratified pre-registration's I-11 before
values. Where that baseline lives once the policy that produced the recorded bytes is no
longer in the tree is an owner decision this contract does not make — STOP and report
rather than widening scope into `eval/evidence_honesty.py`. `training/env.py:441` wraps the FSM as the
surrogate's proposal, so a training-side value pin may move; `training/` is frozen here.
Nothing in this task touches a prompt template or the prompt-set registry — the single
prompt-set bump (Task 20.31) owns every template edit. Keep the docstring discipline: one
provenance line per changed behaviour, no narration of the journey.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`

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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-impostor-fsm-repair` with a title like `task 20.32: the impostor mover stops declining free kills and stalking ejected players`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-3 [audits/review-2026-08-19/B/verdicts.md claim 5 — CONFIRMED and "understated"; the register row at audits/review-2026-08-19/B/collated-findings.md C-3 still quotes the pre-verification 387/233/126, superseded there by the verified 415/225/190]; C-4 [audits/review-2026-08-19/B/collated-findings.md C-4, measured in audits/review-2026-08-19/B/agents-tactical.md §2 F2 — reviewer-measured, NOT adversarially re-verified, so it is corroborated here by G-12 rather than relied on alone]; G-12 [audits/review-2026-08-19/A/verdicts.md claim 12 — CONFIRMED-BUG over 300 games / 10,335 impostor decisions with 0 mismatches against the recorded action stream]; audits/review-2026-08-19/D/FINAL-synthesis.md §4 row 2.12 (the two-line fix), §5 ruling R3 (defect-not-lever; pre-register as a named co-intervention), §4 row 1.8 and the caveat table row 9 (the ML comparator errata this repair retires); anchors re-verified at HEAD — agents/tactical/impostor_policy.py:413-453 (the kill seam; `best = targets[0]` at :414, the co-location re-validation at :431-434, the walk-toward-best fall-through at :447-451), :825-869 (`_kill_available_now`, the same `targets[0]`-only shape at :858), :872-898 (`_confirmed_dead_from_bodies`, `saw_body` only), :996-1068 (`_scored_targets`, the `(-score, player_id)` sort at :1067), :187 (`_STALENESS_THRESHOLD = 30`), :1275-1312 (`_idle`, the pretend-task blend the fall-through lands in); agents/memory/store.py:110 and :433-440 (the `meeting_boundary` episodic marker every living agent receives at the resume tick), :549-575 (`record_meeting_outcome`), :134 (`AgentMemory.meeting_history`); agents/memory/working.py:176-185 (`MeetingHistory.record`); agents/tactical/features.py:678-696 (the v3 encoder, today's only meeting-history consumer); orchestrator/game.py:2297-2306 (the per-living-agent post-meeting fold), :2644 (the policy is handed `memory.episodic` only); api/replay_loader.py:1352-1379 (the replay-side mirror of that fold — beliefs and testimony, never the meeting outcome); agents/perception.py:62-82 (no ejection event type exists); engine/visibility.py:98-127 (the impostor keeps `same_room_and_adjacent` at base visibility); engine/rules.py:56-107 (the engine kill backstop, `:71-85`, with Task 20.11's in-vent guard at `:60-68`); agents/tactical/learned/forward.py:404-413 and training/bakeoff/utility_es.py:426-430 (both option enumerators call the policy's private statics); orchestrator/replay.py:234 (`TacticalPolicyStamp`), :319 (`FSM_DEFAULT_POLICY_ID`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
