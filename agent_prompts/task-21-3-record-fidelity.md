# Agent Prompt — 21.3 The replay stops recording fiction: discarded actions are marked, redirected ballots carry provenance

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.3 — The replay stops recording fiction: discarded actions are marked, redirected ballots carry provenance, anchored to A-14 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-14 (the merged flow-edges + legibility-pacing finding: the mid-loop return, the 2,166-of-35,350 census with its per-set rates, the 116 dropped report/emergency actions classified 73 duplicate-body / 26 distinct-discovery / 17 emergency, the gap==1 pacing artifact, and the verifier's three-command re-run confirming numbers, mechanism and both code sites); B-1 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md §B-1 (the same defect from the engine-core track: the independent 25,881-action corpus fold, the role-correlated drop table, the named consumer `eval/action_ingest.py`, the wait-share recompute 0.1046 → 0.0990 crew / 0.1000 → 0.0982 impostor, and the verifier's ruling that the engine-drop half is a re-report of known-open C-25 while the RECORDING half is new); A-3 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-3 (the three-finder merge: 120 redirected ballots of 3,602, 84 meetings carrying at least one, 25 flipped outcomes, the 16/3/6 recorded versus 1/13 counterfactual ledger, the 3 phantom-consensus ejections, the case-insensitive 107-of-120 estimator the verifier corrected from 101, and the verifier's KNOWN-OPEN note that the redirect/rationale contradiction itself is G-26, triaged P2 at audits/audit-phase-20-close.md:399); A-26 [ADJUSTED, P2] — same file §A-26, for the consumer this task's ballot field exists to serve (21.8 owns that fix; this task ships the field it reads). Anchors re-verified at HEAD `4002f19b` by reading the current tree: engine/tick.py:592-604 (the apply loop; `if working_state.phase == "MEETING": return working_state, events` at :599-600, above the `except ActionRejectedError` handler, so a later-ordered action is never visited); orchestrator/action_ordering.py:13-31 (`order_actions_for_tick` sorts on `_action_order_key` = `(actor, type, canonical-json)` AND enforces one action per actor per tick, raising `ActionBatchValidationError` on a duplicate — the invariant that makes an actor-keyed disposition index sound); orchestrator/game.py:1850-1860 (`actions = list(translate_action_intents_for_tick(intents))`, `state, events = advance_tick(...)`, then `replay.record_tick(input_tick, actions, state)` — the SUBMITTED list, with `events` in hand and passed to `trace.record_tick` on the very next line); orchestrator/replay.py:159-169 (`ReplayEntry`, frozen, `extra="forbid"`) and :845-853 (`record_tick` writes `kind/game_id/tick/actions/state_hash`, no disposition and no event stream); eval/replay_walk.py:424 (the walker re-validates `entry.actions` and feeds them to `advance_tick`); api/replay_loader.py:1219 and :2340-2377 (`_tick_intents` already reconstructs the meeting cutoff from `MeetingTriggeredEvent` and projects it as `CurrentAction == "BLOCKED"` — the one consumer that gets this right, by re-deriving it); eval/action_ingest.py:17-18 ("no engine re-run is needed") and :56-74 (tallies `entry.actions` as fact); meetings/manager.py:275 (`BALLOT_TARGET_REDIRECT_MARKER`), :3132-3187 (`guard_ballot_target_graph`'s docstring), :3226-3234 (the SKIP branch) and :3235-3241 (the redirect branch — `confidence` absent from both `model_copy` updates), :3041 (`coerce_teammate_ballot_to_skip`), :3244/:3326 (`guard_ballot_citation`, `UNCITED_ZERO_FLAG_EJECT_MARKER`), :2738-2756 (the manager-side invalid-target copy) and :2578 (`_vote_parse_default`); meetings/voting.py:90-140 (the canonical `INVALID_VOTE_TARGET_MARKER` normalization); meetings/schemas.py:58-59 (`_FrozenModel`) and :617-623 (`VoteBallot`'s fields, with :611-614 stating the additive-`None`-default precedent Task 16.5 set for `primary_reason_observation_id`); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the five-member class) and :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six marker kinds); eval/report_schema.py:100-124 (the `CURRENT_FORMAT_VERSION` policy and its two recorded "STAYS at 2" rulings, Task 9.6 at :110 and Task 10.4 at :119); DESIGN.md:267 ("Invalid actions become no-ops; an `ActionRejected` event is emitted") and :275 ("A meeting interrupts the tick loop"), :987-994 §11.4 ("The per-game replay JSONL is intentionally unversioned").. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-record-fidelity`
**Depends on:** none (root)
**Section refs:** A-14 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-14 (the merged flow-edges + legibility-pacing finding: the mid-loop return, the 2,166-of-35,350 census with its per-set rates, the 116 dropped report/emergency actions classified 73 duplicate-body / 26 distinct-discovery / 17 emergency, the gap==1 pacing artifact, and the verifier's three-command re-run confirming numbers, mechanism and both code sites); B-1 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md §B-1 (the same defect from the engine-core track: the independent 25,881-action corpus fold, the role-correlated drop table, the named consumer `eval/action_ingest.py`, the wait-share recompute 0.1046 → 0.0990 crew / 0.1000 → 0.0982 impostor, and the verifier's ruling that the engine-drop half is a re-report of known-open C-25 while the RECORDING half is new); A-3 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-3 (the three-finder merge: 120 redirected ballots of 3,602, 84 meetings carrying at least one, 25 flipped outcomes, the 16/3/6 recorded versus 1/13 counterfactual ledger, the 3 phantom-consensus ejections, the case-insensitive 107-of-120 estimator the verifier corrected from 101, and the verifier's KNOWN-OPEN note that the redirect/rationale contradiction itself is G-26, triaged P2 at audits/audit-phase-20-close.md:399); A-26 [ADJUSTED, P2] — same file §A-26, for the consumer this task's ballot field exists to serve (21.8 owns that fix; this task ships the field it reads). Anchors re-verified at HEAD `4002f19b` by reading the current tree: engine/tick.py:592-604 (the apply loop; `if working_state.phase == "MEETING": return working_state, events` at :599-600, above the `except ActionRejectedError` handler, so a later-ordered action is never visited); orchestrator/action_ordering.py:13-31 (`order_actions_for_tick` sorts on `_action_order_key` = `(actor, type, canonical-json)` AND enforces one action per actor per tick, raising `ActionBatchValidationError` on a duplicate — the invariant that makes an actor-keyed disposition index sound); orchestrator/game.py:1850-1860 (`actions = list(translate_action_intents_for_tick(intents))`, `state, events = advance_tick(...)`, then `replay.record_tick(input_tick, actions, state)` — the SUBMITTED list, with `events` in hand and passed to `trace.record_tick` on the very next line); orchestrator/replay.py:159-169 (`ReplayEntry`, frozen, `extra="forbid"`) and :845-853 (`record_tick` writes `kind/game_id/tick/actions/state_hash`, no disposition and no event stream); eval/replay_walk.py:424 (the walker re-validates `entry.actions` and feeds them to `advance_tick`); api/replay_loader.py:1219 and :2340-2377 (`_tick_intents` already reconstructs the meeting cutoff from `MeetingTriggeredEvent` and projects it as `CurrentAction == "BLOCKED"` — the one consumer that gets this right, by re-deriving it); eval/action_ingest.py:17-18 ("no engine re-run is needed") and :56-74 (tallies `entry.actions` as fact); meetings/manager.py:275 (`BALLOT_TARGET_REDIRECT_MARKER`), :3132-3187 (`guard_ballot_target_graph`'s docstring), :3226-3234 (the SKIP branch) and :3235-3241 (the redirect branch — `confidence` absent from both `model_copy` updates), :3041 (`coerce_teammate_ballot_to_skip`), :3244/:3326 (`guard_ballot_citation`, `UNCITED_ZERO_FLAG_EJECT_MARKER`), :2738-2756 (the manager-side invalid-target copy) and :2578 (`_vote_parse_default`); meetings/voting.py:90-140 (the canonical `INVALID_VOTE_TARGET_MARKER` normalization); meetings/schemas.py:58-59 (`_FrozenModel`) and :617-623 (`VoteBallot`'s fields, with :611-614 stating the additive-`None`-default precedent Task 16.5 set for `primary_reason_observation_id`); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the five-member class) and :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six marker kinds); eval/report_schema.py:100-124 (the `CURRENT_FORMAT_VERSION` policy and its two recorded "STAYS at 2" rulings, Task 9.6 at :110 and Task 10.4 at :119); DESIGN.md:267 ("Invalid actions become no-ops; an `ActionRejected` event is emitted") and :275 ("A meeting interrupts the tick loop"), :987-994 §11.4 ("The per-game replay JSONL is intentionally unversioned").
**Complexity:** Integration
**Record impact:** the record itself. Two recorded shapes change for FUTURE recordings — the tick row gains a per-action disposition tuple, and a guard-rewritten ballot gains two typed provenance fields — so the bytes move at Task 21.15 and nowhere earlier. The 300 committed replays are read-only here: they carry neither field, every consumer this task touches falls back to exactly its current behaviour when the field is absent, and every committed cell is pinned unchanged.
**Measurement:** `uv run pytest tests/orchestrator/test_replay.py tests/orchestrator/test_game.py tests/eval/test_replay_walk.py tests/eval/test_wave2_metrics.py tests/meetings/test_manager.py tests/meetings/test_voting.py tests/api/test_replay_loader.py -q` green, including the planted-mismatch case that proves the walker's disposition check bites; `bash scripts/verify_samples.sh` reports 100/100 committed samples reconstructing byte-identically; the PR quotes the disposition census recomputed from a freshly recorded fake-provider game AND the unchanged committed-byte census — 668 meetings, 35,350 recorded actions, 2,166 discarded (6.13%), per set 541/7,515, 1,502/23,992, 65/1,954, 58/1,889 — plus the recorded ballot census 3,602 ballots / 120 `under_gate_redirect` / 18 `teammate_coerced` / 8 `uncited_coerced` / 4 `invalid_target` / 0 `parse_default`, with the command that produced them.

The replay log is the project's factual record, and on two of its rows it records
intentions as events. When any action in a tick's queue convenes a meeting,
`engine/tick.py:599-600` returns from inside the apply loop, so every later-ordered
action is neither applied nor rejected — no `_apply_action`, no
`ActionRejectedError`, no event of any kind. One line later in the orchestrator,
`orchestrator/game.py:1860` records the SUBMITTED batch. Re-run at HEAD over all
four committed sets, that is 2,166 of 35,350 recorded actions — 6.13% — that never
happened: 787 moves, 745 do_tasks, 364 waits, 112 vents, 99 reports, 36 kills, 17
emergency presses, 4 repairs, 2 sabotages. Per set: samples/9p2i 541/7,515 (7.20%),
ml_corpus/9p2i 1,502/23,992 (6.26%), samples/4p1i 65/1,954 (3.33%), ml_corpus/4p1i
58/1,889 (3.07%). Twenty-six of the 99 dropped reports are a DISTINCT body
discovery erased — samples/9p2i seed 3 tick 12 submits `p-1 report body-p-4-8` and
`p-5 report body-p-3-8`, and p-5's discovery of p-3 leaves no trace anywhere — and
17 emergency presses read as pressed while the caller's `emergency_uses` was never
incremented.

The corruption is invisible to the determinism gate by construction, which is why
it survived two prior reviews. The dropped actions were not applied, so the tick's
`state_hash` is correct and a re-walk verifies byte-identically; the record is
wrong only to a consumer that reads `actions` as "what happened". Exactly one
consumer does not: `api/replay_loader.py:2340-2377` re-derives the cutoff from the
`MeetingTriggeredEvent`'s actor index and renders those actors as `BLOCKED`. Every
other consumer trusts the row. `eval/action_ingest.py:17-18` says so in its own
docstring — "no engine re-run is needed" — and :56-74 tallies `entry.actions`
straight into the indistinguishability gauge; B-1 recomputed that gauge both ways
and found the published crew-versus-impostor wait-share gap of 0.0046 is 0.0008 in
engine truth, i.e. 82% of the measured role separation is an artifact of counting
actions that never executed. Track B's verifier is right that no gate, floor or
pin reads that number today, which is why B-1 sits at P2 — but the ML re-ground
this phase exists to run (21.17) fits on these bytes, and a corpus that cannot
distinguish an intent from a transition is the wrong ground to re-fit on.

The repair this task ships is the recording half, not the engine half. Both
finders propose draining the queue into explicit `ActionRejectedEvent`s, and that
is the right long-run shape — but `engine/tick.py` is not this task's file, the
early return is what DESIGN.md:275 specifies ("a meeting interrupts the tick
loop"), and the recording layer's semantics are specified nowhere, which is where
the gap actually lives. So the record learns to say what it knows: `record_tick`
receives the engine event list it is already handed one line away (the orchestrator
passes it to `trace.record_tick` on the very next line and to the replay log never),
and writes a positional `action_dispositions` tuple beside `actions` — `applied`,
`rejected`, `discarded_by_meeting`, one entry per submitted action. The
classification is exact rather than heuristic: the orchestrator boundary enforces
one action per actor per tick (`orchestrator/action_ordering.py:20-31` raises on a
duplicate), so an actor-keyed index over the tick's events is total, and the
meeting cutoff is the same `MeetingTriggeredEvent` rule the spectator has been
running in production since Phase 12. The additive shape is the one DESIGN.md
§11.4 already prescribes for this file — "the per-game replay JSONL is
intentionally unversioned" — and the one Task 16.5 used when it grew
`VoteBallot.primary_reason_observation_id`: an optional field with a `None`
default, so every committed replay parses unchanged and a reader can tell
"this recording predates the field" from "this action was applied".

The ballot half is the same disease on the meeting row. `guard_ballot_target_graph`
(meetings/manager.py:3132) rewrites an under-gate eject target to the argmax
rendered candidate and preserves the model's rationale and confidence verbatim, so
120 of 3,602 committed ballots record a target the voter never authored beside
prose arguing for someone else — one of them reads "p-2 lies about vent. Vote p-2."
with its target field set to p-1. Case-insensitively, 107 of the 120 rationales
name the AUTHORED target and 26 the recorded one. Un-winding just this guard flips
25 of 668 meeting outcomes, and the ledger is why nothing here weakens it: the
recorded results eject 16 impostors and 3 innocents where the un-redirected tally
would eject 1 impostor and 13 innocents. Three ejections have phantom consensus —
every ballot naming the ejectee is a rewrite — and in all three the victim was
never publicly accused at all (samples/9p2i seed 2 m0 → p-5, ml_corpus/9p2i 1044 m0
→ p-7, ml_corpus/9p2i 1085 m0 → p-1). The guard stays exactly as it is. What
changes is that the authored target stops being recoverable only by regex. Today
three separate modules parse the marker string to get it back
(`api/replay_loader.py:2878-2886`, `audits/workflows/extract_gameplay_facts.py:208-221`,
`eval/deduction_metrics.py`), and the training layer parses one of the six kinds
and rides the other five into the fit (A-26). This task adds
`guard_redirected_from` and `guard_rewrite_reason` to `VoteBallot`, populated at
all five target-rewriting sites, so 21.8 can read a field instead of a regex.

The marker is NOT removed and the display contract does not move. The bracketed
marker is the self-declaring human channel — it is what the spectator strips to a
chip (`api/replay_loader.py::_parse_rewrite_reasons`) and what
`eval.vj_instruments._strip_leading_markers` drops before a ballot body enters the
model-voice fold — and it is the only channel the 300 committed replays have. The
typed fields are the machine channel for recordings that carry them. Every reader
this task touches follows one rule, stated once and tested: prefer the structured
field; fall back to the marker parse when it is absent; never disagree. That
fallback is what keeps every committed number in this repo byte-stable through a
change whose whole point is that the next record will be honest — and the next
record is Task 21.15, which is maintenance of the baseline-7 record that is canon
by explicit owner override of a FINDING verdict, not a re-pricing of it.

**Files in scope:**
- orchestrator/replay.py; (`ActionDisposition`, `classify_action_dispositions`, `ReplayEntry.action_dispositions` with its length validator, and `record_tick`'s keyword-only `events`)
- orchestrator/game.py; (ONE call site: `replay.record_tick(input_tick, actions, state, events=events)` at :1860 — the events are already in scope for `trace.record_tick` on the next line)
- meetings/schemas.py; (`BallotTargetRewriteReason` and the two additive `VoteBallot` fields, with the docstring stating that `confidence` is the voter's confidence in `guard_redirected_from` when that is set)
- meetings/manager.py; (the five rewrite sites populate the fields; the parse path neutralizes any model-authored value before any guard runs)
- meetings/voting.py; (the canonical invalid-target normalization at :118-140 sets the same two fields as its manager-side copy)
- api/replay_loader.py; (`_tick_intents` reads the recorded disposition when present and keeps its event derivation as the fallback; `_TARGET_REWRITE_LABELS` derives from the typed union instead of restating it)
- eval/replay_walk.py; (the walk verifies a recorded disposition tuple against the engine's own, under a `ReplayWalkConfig` flag — the gate that makes the field trustworthy)
- eval/action_ingest.py; (the tally excludes `discarded_by_meeting` actions when the recording says which they are, and publishes how many it excluded)
- eval/report_schema.py; (the `CURRENT_FORMAT_VERSION` comment block records this task's STAYS-at-2 ruling in the file's own convention — no value change)
- eval/determinism_test.py; (the scripted byte-identity helper passes the engine events it currently discards, so its recorded rows carry the production shape)
- tests/orchestrator/test_replay.py; (the classifier's table, the length validator, the omitted-field path)
- tests/orchestrator/test_game.py; (a freshly recorded game's tick rows all carry the field)
- tests/eval/test_replay_walk.py; (the planted mismatch)
- tests/eval/test_wave2_metrics.py; (the existing home of the action-ingest tests: committed-byte numbers unchanged, a disposition-bearing fixture de-biases)
- tests/meetings/test_manager.py; (the five sites, and the model-authored-provenance neutralization)
- tests/meetings/test_voting.py; (the canonical normalization sets the fields)
- tests/api/test_replay_loader.py; (recorded-disposition read, marker fallback, and the two channels agreeing on the committed bytes)

**Files NOT in scope:**
- engine/tick.py (the mid-loop return stays: DESIGN.md:275 specifies the interrupt, the drain half is known-open C-25/engine-F6 from the preceding review, and this phase's engine-tick edit is Task 21.6's — this task must not collide with it. The record learns the fact instead of the engine changing to tell it.)
- training/surrogate/dataset.py, training/surrogate/ballots.py (A-26's coerced-row filter is Task 21.8's; this task ships the field 21.8 reads and pins the census it will read it against — widening the filter here would duplicate that contract)
- eval/accusation_calibration.py (A-3's un-applied calibration unwind belongs with Task 21.9's re-aim of that same module; naming it here would put two tasks in one file)
- eval/deduction_metrics.py (`guard_rewritten_ballots_unwound` already unwinds the guard correctly by marker; its cells are pinned on committed bytes that carry no field, so migrating it buys nothing and risks a published number)
- audits/workflows/extract_gameplay_facts.py (the redirect-recovery regex at :208-221 keeps working on committed bytes; the workflow re-derives at the record, not here)
- replays/ (no re-record: the committed bytes are read as evidence and pinned unchanged; the shapes this task adds first appear at Task 21.15)
- agents/strategic/prompts/ (no rendered prompt byte moves — the two `VoteBallot` fields are optional with `None` defaults, so `llm/fake_provider.py::_minimal_valid_instance` skips them and the canonical Featherless path sends no schema at all)
- orchestrator/trace.py (already receives `events`; unchanged)

**Definition of done:**
- [ ] `orchestrator.replay.ActionDisposition` is `Literal["applied", "rejected", "discarded_by_meeting"]` and `classify_action_dispositions(actions, events)` is a pure function returning one entry per action in submitted order, with no RNG and no clock — `rejected` iff the tick's events carry an `ActionRejectedEvent` for that actor, `discarded_by_meeting` iff the action sorts after the `MeetingTriggeredEvent`'s actor in the submitted list, `applied` otherwise.
- [ ] The classifier is exhaustively pinned in `tests/orchestrator/test_replay.py` against real engine output, not hand-built events: a tick with a mixed batch (one applied, one rejected, one discarded behind a meeting trigger) is driven through `engine.tick.advance_tick` and the three dispositions asserted by actor; a no-meeting tick returns no `discarded_by_meeting`; a tick whose `MeetingTriggeredEvent` actor is LAST in the batch returns none either.
- [ ] `ReplayEntry.action_dispositions: tuple[ActionDisposition, ...] | None = None` is additive per the DESIGN.md §11.4 policy and the Task-16.5 precedent, with a model validator that REJECTS a non-`None` tuple whose length differs from `len(actions)` (AGENTS.md "no silent fallbacks"); the perturbation — a hand-written row with three actions and two dispositions — raises, and a row with the key absent parses to `None` with no error. All 5,960 committed tick rows across the four sets parse to `None`, asserted over the real files.
- [ ] `ReplayLog.record_tick` takes `events` keyword-only with a `None` default: given events it writes the disposition tuple, given none it OMITS the key entirely and says so in the docstring — a recorder with no event stream may not claim a disposition. The 33 existing positional call sites — nine files outside `orchestrator/game.py`, the two non-test ones being `eval/determinism_test.py` (six calls) and `scripts/gen_frontend_types.py:416` — keep working unchanged.
- [ ] `orchestrator/game.py:1860` passes the `events` it already holds, and `tests/orchestrator/test_game.py` pins that EVERY tick row of a freshly recorded fake-provider game carries `action_dispositions` of the right length — so the production path can never silently regress to the omitted shape.
- [ ] `eval/replay_walk.py` gains a `ReplayWalkConfig` flag that, when the recorded row carries dispositions, re-classifies the re-walked tick with `classify_action_dispositions` and raises a `WalkViolation` on any disagreement. The gate ships with a PLANTED case (a fixture replay whose disposition tuple is edited to call a discarded action `applied`) proving it bites, and a second case proving a row with the field absent is skipped rather than failed.
- [ ] `eval/action_ingest.py` skips actions the recording marks `discarded_by_meeting` and counts them, publishing the count through a carrier defined in `eval/action_ingest.py` itself — a new function beside `tally_actions_by_role` returning the tally plus `discarded_excluded`, with `tally_actions_by_role` delegating to it so its own signature and return type stay unchanged for its three out-of-scope callers (`scripts/build_sample_report.py:249` and `:390`, `audits/workflows/extract_gameplay_facts.py:3364`). The count must NOT become a field on `ActionRoleTally`: that model is defined at `eval/meeting_quality.py:2815`, and `eval/meeting_quality.py` is in Task 21.7's Files-in-scope (tasks/phase-21.md:1681) with no ordering edge between 21.3 and 21.7 in the ratified DAG. Pinned both ways in `tests/eval/test_wave2_metrics.py`: over the committed sets the excluded count is 0 and every published tally is byte-identical to today's; over a disposition-bearing fixture the excluded actions leave the tally. The PR states the consequence for Task 21.15 — the indistinguishability wait-share will move on the new record (B-1 measured crew 0.1046 → 0.0990, impostor 0.1000 → 0.0982, gap 0.0046 → 0.0008) and that move is a correction to be reported in the record audit, not a surprise.
- [ ] `api/replay_loader.py::_tick_intents` prefers the recorded disposition for its `preempted` set and falls back to its existing `MeetingTriggeredEvent` derivation when the field is absent; the killed-victim preemption arm is untouched. `tests/api/test_replay_loader.py` pins that both paths produce the identical `_TickIntents` on a disposition-bearing fixture, so the served `CurrentAction` labels are provably unchanged by the migration.
- [ ] `meetings.schemas.BallotTargetRewriteReason` is `Literal["under_gate_redirect", "teammate_coerced", "uncited_coerced", "invalid_target", "parse_default"]` — the five labels `api/replay_loader.py:253-261` already names — and `api/replay_loader.py::_TARGET_REWRITE_LABELS` is DERIVED from it (`frozenset(get_args(...))`) rather than restating it, with a test asserting the derived set still equals the five literals so the display contract is pinned, not merely inherited.
- [ ] `VoteBallot` gains `guard_redirected_from: str | None = None` and `guard_rewrite_reason: BallotTargetRewriteReason | None = None`, both additive with `None` defaults so every committed replay and every committed `tournament-eval-report.json` parses unchanged (asserted over all four sets). The field docstring states the two facts a consumer needs: `guard_redirected_from` holds the target as the voter authored it — which for `invalid_target` is the bounded original and need not name a live player — and `confidence` is the voter's confidence in THAT target, not in the recorded one.
- [ ] The five rewrite sites populate both fields: `guard_ballot_target_graph` on both its redirect (:3235-3241) and its no-eligible-candidate SKIP branch (:3226-3234), `coerce_teammate_ballot_to_skip` (:3041), `guard_ballot_citation` (:3244-3326), the manager-side invalid-target normalization (:2738-2756) and its canonical twin in `meetings/voting.py:118-140`, and `_vote_parse_default` (:2578) with `guard_redirected_from=None` because an unparseable ballot authored no target. Each site keeps its marker byte-identical — the marker is the display channel and stays.
- [ ] A model-authored provenance value cannot survive: the parsed ballot at `meetings/manager.py:1890` is normalized to `guard_redirected_from=None, guard_rewrite_reason=None` before any guard runs, and `tests/meetings/test_manager.py` pins it with a stub client returning a ballot that sets both fields itself. This is the laundering guard — the fields are the meeting layer's testimony about its own rewrite, never the model's.
- [ ] A consistency invariant is pinned over freshly recorded bytes and is perturbation-proved: a ballot whose `rationale_text` carries a target-rewrite marker carries the matching `guard_rewrite_reason`, and vice versa — for recordings that carry the field. The perturbation (strip the field from one ballot of a recorded fixture) fails the check; the committed sets, which carry no field at all, are skipped by the same predicate rather than failed by it.
- [ ] `eval/report_schema.py`'s `CURRENT_FORMAT_VERSION` STAYS at 2, with the reason recorded as a paragraph in the existing comment block in that block's own voice (the 9.6 and 10.4 precedents): the two `VoteBallot` fields are additive with defaults, so a reader on this build interprets both a pre-21.3 and a post-21.3 report, which is the only condition §11.4 makes the bump depend on.
- [ ] `bash scripts/verify_samples.sh` reports all 100 committed samples reconstructing byte-identically, and the PR quotes the two censuses side by side from a re-run command: the committed-byte disposition census (668 meetings, 35,350 actions, 2,166 discarded = 6.13%, per-set 7.20/6.26/3.33/3.07%) reproduced from the ordering rule alone, and the same census read off a freshly recorded game's own `action_dispositions` — the two must agree on the fresh game.
- [ ] The corpus cost is measured and stated rather than assumed: the PR quotes the added bytes for a full re-record from the fresh recording (the dense positional tuple is ~0.5 MB over a 35,350-action corpus against ~203 MB of committed replays, ~0.25%), so Task 21.15's disk projection is grounded.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK A — the classifier, first and alone. Write
`classify_action_dispositions(actions: Sequence[Action], events: Sequence[EngineEvent])`
in `orchestrator/replay.py` before touching any recorder. Build
`index_by_actor = {action.actor: i for i, action in enumerate(actions)}` — sound
because `order_actions_for_tick` (`orchestrator/action_ordering.py:20-31`) raises
`ActionBatchValidationError` on a duplicate actor, so state that invariant in the
docstring rather than defending against it. Collect the rejected actors from
`ActionRejectedEvent`, find the cutoff from the `MeetingTriggeredEvent`'s actor
index, and classify positionally. Do NOT try to recover disposition from event
ORDER: `advance_tick` appends passive-effect events (step 2) and a possible
`GameOverEvent` (step 3) after the apply loop, so the event list is not
positionally aligned with the action list and any index arithmetic over it is
wrong on exactly the ticks that matter. `api/replay_loader.py:2340-2377` is the
working precedent for the actor-index shape; read it before writing this.

BLOCK B — the record. Widen `record_tick` to
`record_tick(self, tick, actions, state, *, events=None)`. Keyword-only with a
default is load-bearing: 33 call sites outside `orchestrator/game.py` call it
positionally with three arguments — `eval/determinism_test.py` (six, including
the fixture writer at :52-66), the non-test `scripts/gen_frontend_types.py:416`,
and seven test modules (`tests/api/fixtures/sample_replay.py` alone has 10) — and
a required parameter would break every one of them for no gain. When `events is None`, write today's five-key entry unchanged —
the key is OMITTED, not written as `null`, so a recorder without an event stream
is distinguishable from one that recorded all-applied. Then the model: add
`action_dispositions` to `ReplayEntry` with a `model_validator(mode="after")`
comparing lengths. `_stable_json` sorts keys, so the new key lands after
`actions`; nothing about `_state_hash` moves, because it hashes the state, not the
row.

BLOCK C — the walker gate, and write the planted case first. Add the flag to
`ReplayWalkConfig` beside `verify_tick_hashes`, and in `walk_replay`
(`eval/replay_walk.py:424`) call the classifier on the events `advance_tick`
returns for that tick, comparing against `entry.action_dispositions` when it is
not `None`. Route a disagreement through `_violate` with a new `WalkViolation`
kind, the same shape the duplicate-meeting-rows check uses at :400-404. The
planted fixture is the point of the whole block: copy one committed replay into
`tmp_path`, rewrite one tick's disposition tuple so a `discarded_by_meeting`
entry reads `applied`, and assert the walk raises. A gate nobody can fail is
prose (AGENTS.md craft rule 2).

BLOCK D — the ballot fields, and the neutralization before them. Add both fields
to `VoteBallot` in `meetings/schemas.py`, then find every construction site of a
rewritten ballot. There are six functions across two modules — the list is in the
DoD and each one already computes the original target for its marker, so the field
value is `_bounded_original(ballot.target)` in five of them and `None` in
`_vote_parse_default`. Set both fields in the SAME `model_copy(update={...})` that
sets the marker; do not add a second copy. Then the neutralization: immediately
after `VoteBallot.model_validate_json(response.text)` at `meetings/manager.py:1890`,
force both fields to `None` on the parsed ballot. `VoteBallot` is the schema
handed to `LLMClient.complete` (`meetings/manager.py:1881`), so under the Ollama
adapter — which sends `schema.model_json_schema()` as `format` — the model can see
these field names, and `extra="forbid"` does not stop a model from filling a field
that exists. The canonical Featherless path sends no schema (`json_object` mode,
`llm/featherless_client.py:155-181`) and the fake provider skips defaulted fields
(`llm/fake_provider.py::_minimal_valid_instance`), so nothing changes on either —
but the neutralization is what makes that true by construction rather than by
provider luck, and it is the one test in this task that must not be dropped.

BLOCK E — the consumers, each with its fallback pinned. Three readers migrate and
all three follow one rule: prefer the field, fall back to today's derivation, never
disagree. `api/replay_loader.py::_tick_intents` takes the recorded disposition for
`preempted` (leaving the killed-victim arm alone); `eval/action_ingest.py` skips
`discarded_by_meeting` and counts the skips; `_TARGET_REWRITE_LABELS` derives from
`get_args(BallotTargetRewriteReason)`. For each, the test that matters is the one
asserting the two paths AGREE on a disposition-bearing fixture — that is what
proves the migration is a no-op on behaviour and lets the committed numbers stay
pinned to the digit.

BLOCK F — blast radius before you widen anything (AGENTS.md craft rule 6). Grep
every reader of `ReplayEntry` and of `entry.actions` before editing: at HEAD the
non-test hits are `eval/action_ingest.py:57`, `eval/replay_walk.py:424`,
`api/replay_loader.py:1219`/`:2182`,
`audits/workflows/extract_gameplay_facts.py:2142`/`:2232`,
`training/anchor_study.py:432`/`:485`/`:564`, `training/determinism.py:433`,
`training/rollout.py:499`/`:548-549`, `training/surrogate/dataset.py:874`/`:900`,
`eval/off_menu.py:393`/`:432`, `eval/kill_craft.py:563`/`:580`,
`eval/balance_eval.py:1035`, `eval/evidence_honesty.py:1241`/`:1490` and
`scripts/_manifest_writer.py:644` — thirteen modules, not eight. The ten outside
this task's scope are each correct as they stand: they re-walk the engine and
hash-verify, score the agent's own DECISION rather than the transition
(`eval/off_menu.py`, `eval/kill_craft.py`, `eval/evidence_honesty.py`), scrape
actor ids only (`scripts/_manifest_writer.py`), disambiguate the trigger against
`MeetingReplayEntry.triggered_by` (`eval/balance_eval.py`), or count submissions
by declared design (`training/rollout.py:326-336`), so they stay untouched — say so in the PR with the grep, and if a hit appears that this
list does not cover, stop and ask rather than widening scope.

## Public types this task introduces
- `orchestrator.replay.ActionDisposition`
- `orchestrator.replay.classify_action_dispositions`
- `meetings.schemas.BallotTargetRewriteReason`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task edits the two typed records every other consumer in the repo reads —
the tick row and the ballot — and its whole value depends on the committed bytes
not moving while it does.

Risk 1 — an additive field that is not actually additive. `ReplayEntry` and
`VoteBallot` are both frozen with `extra="forbid"`, so a field without a default
would reject all 300 committed replays and every committed
`tournament-eval-report.json` on load. The defaults are `None`, the DoD asserts
all 5,960 committed tick rows and all 3,602 committed ballots parse to `None`
over the real files, and `bash scripts/verify_samples.sh` is the standing proof
that reconstruction did not move. Task 16.5's `primary_reason_observation_id` is
the precedent and its docstring at `meetings/schemas.py:611-614` states the rule.

Risk 2 — the model authoring its own provenance. `VoteBallot` is the schema passed
to the LLM client, so adding fields to it puts their names in the Ollama adapter's
constrained-decoding schema, where a model could fill them and launder a fabricated
rewrite into the record. The parse-time neutralization at `meetings/manager.py:1890`
is the guard and it carries its own test with a stub client that tries exactly that.
This is the risk that would be invisible in review and only visible in a real-provider
record — treat the test as load-bearing, not decorative.

Risk 3 — a consumer that changes a published number. `eval/action_ingest.py` is
the one reader whose OUTPUT this task deliberately changes, and only for
recordings that carry dispositions. On the committed bytes the excluded count is
0 and every cell is byte-identical, pinned both directions. At Task 21.15 the
indistinguishability wait-share WILL move, by roughly the amount B-1 measured, and
that must appear in the record audit as a corrected instrument rather than as a
surprising move — flag it to the 21.15 owner in the PR.

Risk 4 — file collisions inside Wave 1a/1b. Four files this task edits are
plausibly also named by a sibling contract with no dependency edge between them:
`meetings/manager.py` (Task 21.2's guard-redaction sentence), `orchestrator/game.py`
(Task 21.11's F2 class), `eval/replay_walk.py` (Task 21.11's substrate check) and
`api/replay_loader.py` (Task 21.10's B-23/B-51 listing and error work).
`scripts/validate_task_docs.py::validate_parallel_file_scope` fails on an
unordered overlap, so the phase assembler must either add the ordering edges or
move the overlapping item; nothing in this contract's content depends on which
way it goes. `engine/tick.py` is deliberately NOT in scope, which is what keeps
this task clear of Task 21.6.

Risk 5 — the two provenance channels drifting apart. After this task a rewritten
ballot carries the fact twice: as a bracketed marker in `rationale_text` (the
display and pre-field channel) and as typed fields (the machine channel). Two
copies of a fact drift. The consistency invariant in the DoD — marker present iff
reason present, on recordings that carry the field, with a stripped-field
perturbation proving it bites — is what stops that, and it is why the marker is
NOT deleted here: 300 committed replays have only the marker, and Task 21.8 reads
the field precisely because the marker parse is what A-26 found the training layer
getting wrong.

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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-21-record-fidelity` with a title like `task 21.3: the replay stops recording fiction: discarded actions are marked, redirected ballots carry provenance`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing A-14 [CONFIRMED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-14 (the merged flow-edges + legibility-pacing finding: the mid-loop return, the 2,166-of-35,350 census with its per-set rates, the 116 dropped report/emergency actions classified 73 duplicate-body / 26 distinct-discovery / 17 emergency, the gap==1 pacing artifact, and the verifier's three-command re-run confirming numbers, mechanism and both code sites); B-1 [ADJUSTED, P2] — audits/review-2026-08-26/B/collated-findings.md §B-1 (the same defect from the engine-core track: the independent 25,881-action corpus fold, the role-correlated drop table, the named consumer `eval/action_ingest.py`, the wait-share recompute 0.1046 → 0.0990 crew / 0.1000 → 0.0982 impostor, and the verifier's ruling that the engine-drop half is a re-report of known-open C-25 while the RECORDING half is new); A-3 [ADJUSTED, P1] — audits/review-2026-08-26/A/collated-findings.md §A-3 (the three-finder merge: 120 redirected ballots of 3,602, 84 meetings carrying at least one, 25 flipped outcomes, the 16/3/6 recorded versus 1/13 counterfactual ledger, the 3 phantom-consensus ejections, the case-insensitive 107-of-120 estimator the verifier corrected from 101, and the verifier's KNOWN-OPEN note that the redirect/rationale contradiction itself is G-26, triaged P2 at audits/audit-phase-20-close.md:399); A-26 [ADJUSTED, P2] — same file §A-26, for the consumer this task's ballot field exists to serve (21.8 owns that fix; this task ships the field it reads). Anchors re-verified at HEAD `4002f19b` by reading the current tree: engine/tick.py:592-604 (the apply loop; `if working_state.phase == "MEETING": return working_state, events` at :599-600, above the `except ActionRejectedError` handler, so a later-ordered action is never visited); orchestrator/action_ordering.py:13-31 (`order_actions_for_tick` sorts on `_action_order_key` = `(actor, type, canonical-json)` AND enforces one action per actor per tick, raising `ActionBatchValidationError` on a duplicate — the invariant that makes an actor-keyed disposition index sound); orchestrator/game.py:1850-1860 (`actions = list(translate_action_intents_for_tick(intents))`, `state, events = advance_tick(...)`, then `replay.record_tick(input_tick, actions, state)` — the SUBMITTED list, with `events` in hand and passed to `trace.record_tick` on the very next line); orchestrator/replay.py:159-169 (`ReplayEntry`, frozen, `extra="forbid"`) and :845-853 (`record_tick` writes `kind/game_id/tick/actions/state_hash`, no disposition and no event stream); eval/replay_walk.py:424 (the walker re-validates `entry.actions` and feeds them to `advance_tick`); api/replay_loader.py:1219 and :2340-2377 (`_tick_intents` already reconstructs the meeting cutoff from `MeetingTriggeredEvent` and projects it as `CurrentAction == "BLOCKED"` — the one consumer that gets this right, by re-deriving it); eval/action_ingest.py:17-18 ("no engine re-run is needed") and :56-74 (tallies `entry.actions` as fact); meetings/manager.py:275 (`BALLOT_TARGET_REDIRECT_MARKER`), :3132-3187 (`guard_ballot_target_graph`'s docstring), :3226-3234 (the SKIP branch) and :3235-3241 (the redirect branch — `confidence` absent from both `model_copy` updates), :3041 (`coerce_teammate_ballot_to_skip`), :3244/:3326 (`guard_ballot_citation`, `UNCITED_ZERO_FLAG_EJECT_MARKER`), :2738-2756 (the manager-side invalid-target copy) and :2578 (`_vote_parse_default`); meetings/voting.py:90-140 (the canonical `INVALID_VOTE_TARGET_MARKER` normalization); meetings/schemas.py:58-59 (`_FrozenModel`) and :617-623 (`VoteBallot`'s fields, with :611-614 stating the additive-`None`-default precedent Task 16.5 set for `primary_reason_observation_id`); api/replay_loader.py:253-261 (`_TARGET_REWRITE_LABELS`, the five-member class) and :2878-2886 (`_BALLOT_PREFIX_MARKERS`, the six marker kinds); eval/report_schema.py:100-124 (the `CURRENT_FORMAT_VERSION` policy and its two recorded "STAYS at 2" rulings, Task 9.6 at :110 and Task 10.4 at :119); DESIGN.md:267 ("Invalid actions become no-ops; an `ActionRejected` event is emitted") and :275 ("A meeting interrupts the tick loop"), :987-994 §11.4 ("The per-game replay JSONL is intentionally unversioned").), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
