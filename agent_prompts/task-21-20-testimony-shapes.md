# Agent Prompt — 21.20 What you saw is what you can say (lever `testimony_shapes`, default OFF)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.20 — What you saw is what you can say (lever `testimony_shapes`, default OFF), anchored to B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it. The CONTRACT's own strikeability was resolved at the #396 ratification — the owner kept it IN and it dispatches. What remains an owner decision point is the ARM: whether the lever ships ON at the adopting record, which 21.22's pre-registration and 21.24's record decide, not this task). Anchors RE-VERIFIED at HEAD `3d1b41e9` (the drafting session read `d8ec0a1c`, 48 commits back — every line number below moved, and four empirical premises moved with them; see the re-anchor rulings): meetings/schemas.py:574-584 (`ReportedStatementKind`, the closed FIVE), :118-144 (`SawVentObservation`, whose docstring states the reduction to a `saw_vent` `ReportedStatement` — the 20.29 precedent for widening the kind set when a new sayable shape lands, though the task id itself is not in the text), :147-174 (`WhereaboutsClaim` — silent about the reduction), :177-205 (`SawMoveObservation` — its "contributes EXACTLY ONE placement, the destination" ruling at :188-195 is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" at :195-198 is the parse/offer split this task reuses), :208-216 (the `ObservationClaim` discriminated union — six members), :587-620 (`ReportedStatement`, whose optional fields are populated per kind, the per-kind list at :599-608); meetings/manager.py:4027-4135 (`derive_reported_testimony`: the observation loop at :4081-4104 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :4105-4134 only the three claims, no else-branch and no raise; the sorted return at :4135; the docstring's own "``completed_task`` / ``found_body`` observations and all free-text are dropped" at :4044-4045); agents/memory/store.py:578-703 (`absorb_reported_testimony`; the `alibi_map` write at :691-703 is gated on `statement.kind == "alibi"` at :692), :1611-1615 (the render dispatch) + :1939-2001 (`_render_reported_testimony`, the five per-kind bodies at :1973-1993 and the `[meeting n] CLAIM by X (unverified):` frame at :1972), :1835-1841 (the witnessed-kill memory line at :1839 — killer, room and tick, no victim), :1035-1099 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` returns True at :1055-1056 and is dropped before it is ever rendered); meetings/transcript.py:2289-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2517-2569 (`_iter_move_placements`: a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:129 (the vent-first mandate the kill line parallels) + :143-152 (the shape menu — SIX observation shapes at :143-148, three claim shapes at :150-152) and accusation_round.j2:252 / :255 (the mandate on the opening and reply branches) + :271-280 (the same six-shape menu); agents/strategic/prompts/loader.py:309-320 (the four default + two roll-call filename constants) + :332-366 (`impostor_roll_call_enabled`, the standing resolver SHAPE) + :751-753 / :888-890 / :1012-1090 (the Task-18.10 file-swap routing — cited as the shape this task must NOT clone, see the re-anchor ruling) and orchestrator/game.py:353-412 (`PROMPT_VERSION_SETS` at v5, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`) + :415-437 (`_lever_arm_versions` — 21.18's RE-BODY helper, which IS this task's precedent) + :441-471 (the two landed re-body arms to clone) + :478-503 (`_PROMPT_VERSION_OVERLAYS` / `_PROMPT_OVERLAY_LABELS`) + :506-590 (`enabled_prompt_version_overlays`, `_overlay_entry`, `prompt_versions_for_set` — the composition rules at :569-579, the FILE-SWAPPING-ARM rule at :581-589, the per-template composite fold at :606-621); orchestrator/game.py:2598 and api/replay_loader.py:1490 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale at :3-15; NOTE the module imports only `typing.Final` today — the resolver adds `os` and `collections.abc`); eval/deduction_metrics.py:250-270 + :470-505 (the nets and their documented scope) + :1623-1743 (`ScaffoldLeakageCells`, the docstring's leakage block at :1650-1690 and the int fields at :1717-1743) + :2474-2504 (the turn loop, `role = roles[turn.speaker]` at :2476, the partner increment at :2492-2493, and the TWO oracle-register increments 21.9 added at :2494-2495 / :2503-2504).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-testimony-shapes`
**Depends on:** 21.19
**Section refs:** B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it. The CONTRACT's own strikeability was resolved at the #396 ratification — the owner kept it IN and it dispatches. What remains an owner decision point is the ARM: whether the lever ships ON at the adopting record, which 21.22's pre-registration and 21.24's record decide, not this task). Anchors RE-VERIFIED at HEAD `3d1b41e9` (the drafting session read `d8ec0a1c`, 48 commits back — every line number below moved, and four empirical premises moved with them; see the re-anchor rulings): meetings/schemas.py:574-584 (`ReportedStatementKind`, the closed FIVE), :118-144 (`SawVentObservation`, whose docstring states the reduction to a `saw_vent` `ReportedStatement` — the 20.29 precedent for widening the kind set when a new sayable shape lands, though the task id itself is not in the text), :147-174 (`WhereaboutsClaim` — silent about the reduction), :177-205 (`SawMoveObservation` — its "contributes EXACTLY ONE placement, the destination" ruling at :188-195 is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" at :195-198 is the parse/offer split this task reuses), :208-216 (the `ObservationClaim` discriminated union — six members), :587-620 (`ReportedStatement`, whose optional fields are populated per kind, the per-kind list at :599-608); meetings/manager.py:4027-4135 (`derive_reported_testimony`: the observation loop at :4081-4104 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :4105-4134 only the three claims, no else-branch and no raise; the sorted return at :4135; the docstring's own "``completed_task`` / ``found_body`` observations and all free-text are dropped" at :4044-4045); agents/memory/store.py:578-703 (`absorb_reported_testimony`; the `alibi_map` write at :691-703 is gated on `statement.kind == "alibi"` at :692), :1611-1615 (the render dispatch) + :1939-2001 (`_render_reported_testimony`, the five per-kind bodies at :1973-1993 and the `[meeting n] CLAIM by X (unverified):` frame at :1972), :1835-1841 (the witnessed-kill memory line at :1839 — killer, room and tick, no victim), :1035-1099 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` returns True at :1055-1056 and is dropped before it is ever rendered); meetings/transcript.py:2289-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2517-2569 (`_iter_move_placements`: a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:129 (the vent-first mandate the kill line parallels) + :143-152 (the shape menu — SIX observation shapes at :143-148, three claim shapes at :150-152) and accusation_round.j2:252 / :255 (the mandate on the opening and reply branches) + :271-280 (the same six-shape menu); agents/strategic/prompts/loader.py:309-320 (the four default + two roll-call filename constants) + :332-366 (`impostor_roll_call_enabled`, the standing resolver SHAPE) + :751-753 / :888-890 / :1012-1090 (the Task-18.10 file-swap routing — cited as the shape this task must NOT clone, see the re-anchor ruling) and orchestrator/game.py:353-412 (`PROMPT_VERSION_SETS` at v5, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`) + :415-437 (`_lever_arm_versions` — 21.18's RE-BODY helper, which IS this task's precedent) + :441-471 (the two landed re-body arms to clone) + :478-503 (`_PROMPT_VERSION_OVERLAYS` / `_PROMPT_OVERLAY_LABELS`) + :506-590 (`enabled_prompt_version_overlays`, `_overlay_entry`, `prompt_versions_for_set` — the composition rules at :569-579, the FILE-SWAPPING-ARM rule at :581-589, the per-template composite fold at :606-621); orchestrator/game.py:2598 and api/replay_loader.py:1490 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale at :3-15; NOTE the module imports only `typing.Final` today — the resolver adds `os` and `collections.abc`); eval/deduction_metrics.py:250-270 + :470-505 (the nets and their documented scope) + :1623-1743 (`ScaffoldLeakageCells`, the docstring's leakage block at :1650-1690 and the int fields at :1717-1743) + :2474-2504 (the turn loop, `role = roles[turn.speaker]` at :2476, the partner increment at :2492-2493, and the TWO oracle-register increments 21.9 added at :2494-2495 / :2503-2504).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-21 adopting record — ON moves episodic rows, therefore rendered memory, therefore prompt bytes; the instrument half is record-free and unconditional
**Measurement:** `uv run pytest tests/meetings tests/agents tests/orchestrator/test_replay.py tests/orchestrator/test_replay_meetings.py tests/orchestrator/test_meeting_integration.py tests/experiments/test_probe_backends.py tests/eval/test_deduction_metrics.py -q` green (the two-package subset the contract originally named misses the whole registration blast radius — `tests/orchestrator/test_replay.py`'s literal registration pins and `tests/experiments/test_probe_backends.py`'s `_FLAGS_ON` both break on the registration alone, as they did at 21.18 and 21.19); `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green with the lever unset (the OFF-path proof over the committed meetings); `bash scripts/verify_samples.sh` 100/100; the PR quotes, from the fixtures and from a lever-ON re-derivation over the committed bytes, how many reported rows each arm adds per meeting and what the alibi-map coverage becomes — never a bar, never a verdict.

The substrate elicits an answer it then forgets. Every meeting asks each
player for a roll-call self-placement and every crew template offers the
witnessed-transition shape, and both arrive: re-derived at THIS HEAD over the
BASELINE-8 bytes 21.15 recorded, across the two `replays/ml_corpus/` sets (482
meetings), the spoken census is `saw_player` 2,868, **`whereabouts` 2,306**,
`accusation` 2,273, **`saw_move` 1,136**, `corroboration` 1,064, `alibi` 724.
The two bolded shapes are dropped whole by `derive_reported_testimony`: 3,442
statements, more than the `saw_player` channel the reduction does carry, are
spoken in public,
rendered into every later listener's transcript, and then never enter any
listener's episodic memory. The reduction was written over the shapes that
existed in 2026-06 and has never been widened since; `WhereaboutsClaim` and
`SawMoveObservation` fall through both loops with no else-branch and no raise,
and `grep -rn "WhereaboutsClaim\|SawMoveObservation" --include="*.py" agents/
orchestrator/ | grep -v test` returns nothing — there is no second ingest path.
The second-order cost is arithmetic: `alibi_map` is fed only by `kind ==
"alibi"` (agents/memory/store.py:691-703), so the map an agent consults for
"where did they say they were" holds 724 of the 3,030 location accounts spoken
in that corpus — **23.9%** — and the channel the prompts ask for hardest is the
one memory keeps least. The verifier's two corrections bind this contract: the
gap is four shapes, not two (`found_body` 596 and `completed_task` 342 also fall
through, and stay out of scope here — see below), and a whereabouts is not
invisible, it reaches listeners as a degenerate single-tick self-alibi through
the SCALAR detector path (meetings/transcript.py:2291-2304), so the true claim
is the narrow one: it never becomes CONTENT.

The kill has no shape at all. Across the four committed sets (672 meetings,
3,631 turns, re-derived at THIS HEAD over the baseline-8 bytes) the turn
schema's observation census is `saw_player` 3,880, `whereabouts` 3,157,
`saw_move` 1,606, `found_body` 828, `saw_vent` 512, `completed_task` 467 — and
zero of anything naming a witnessed murder, because no such shape exists
anywhere in the repo (re-verified: `grep -rn "saw_kill\|SawKillObservation"
--include="*.py" --include="*.j2" .` returns nothing at HEAD). A crewmate who
watched a kill holds the memory line
`[tick 11] You witnessed p-8 kill in ADMIN.` and, offered six shapes, files it
as the one that is role-proving — or, having no shape for it, says nothing
structured at all. On the BASELINE-7 bytes A-22 read, the verifier's independent
scan found 5 spoken `saw_vent` rows naming a subject who never vented anywhere
in that game, all 5 joining that same speaker's own witnessed kill on killer +
room + tick exactly, against a denominator of 512-of-517 genuine and a clean
structured channel (448 `vent_sighting` flags, 448 engine-backed, 0 unbacked).
**That class does not reproduce at this HEAD.** Re-derived over the baseline-8
bytes: 512 spoken `saw_vent` rows across the four sets, **0** of them naming a
subject who never vented in that game, and 453 `vent_sighting` flags. So the
DISPLACEMENT half of A-22 — a witnessed murder filed as a vent — is a class of
size ZERO on the bytes this task lands on, and no surface in this task may quote
the 5. What survives, and is what this contract is actually chartered on, is the
SILENCE: there is no shape for a witnessed kill, so the strongest testimony the
game produces has no structured form and can only reach the table as free text
the reduction discards outright. This is a LEGIBILITY repair, not a justice
repair, and a repair to an ABSENCE rather than to a measured misfiling — the PR
must say so in one line and must not price it off the retired 5.

The `saw_kill` shape was named and declared OUT at Phase 20 —
tasks/phase-20.md:65-67 routes it, with six siblings, to "a separate chartered
balance wave with its own record". This contract is that charter for this one
shape, and it is deliberately the smallest possible version of it. The new
observation carries `{type, tick, subject, room}` — killer, room, tick, mirroring
`SawVentObservation` field-for-field — and NOT the victim, because naming the
victim would require widening the perception packet (`observation/service.py`
builds `_ObservedAction(action="kill", room=event.room)` and drops
`KilledEvent.target`), which is a firewall-crossing change with its own
entitlement question and is out of scope. The shape mints no contradiction
flag, no new band, and no suspicion delta: it is testimony content, standing
exactly where a spoken `saw_vent` stands before grounding. The impostor
templates never offer it, and they do not need to — an impostor's own kill
already renders as its own first-person line, and an impostor's sighting of a
TEAMMATE killing is suppressed before render by the §4.7 firewall
(`_is_kill_window_sighting` returns True on `action == "kill"`,
agents/memory/store.py:1037-1038), so no impostor holds a witnessed-kill row it
could honestly speak. Offering the shape only to the crew is the narrow reading
of the evidence and it also keeps the shape from becoming a confession prompt.

Confessions are the third strand, and only their instrument is in scope. ONE
impostor in the baseline-8 corpus narrates their own kill in player-visible text
— `replays/ml_corpus/9p2i` `headless-seed-1079`, p-7, meeting-2, in an
accusation claim's `reason`: "p-8 moved into Engineering at tick 13, right
after I killed p-1, and was seen near the kill zone again at tick 15". That
placement is itself the finding's sharpest evidence for the surface this task
scans: the confession is NOT in `free_text`, whose half of the same turn is a
denial, so a net over `free_text` alone would never see it. The text reaches
every later speaker and every ballot, and no shipped cell counts it. Re-derived
at THIS HEAD from the committed `tournament-eval-report.json` blocks:
`player_visible_leak_turns` reads 0 on every committed set (it is the PARTNER
net, over `free_text` only), the two oracle-register nets 21.9 added over
`free_text` / claim `reason` are the module's other player-visible increments
and catch nothing of this class (`oracle_register_turns` 0 on all four sets),
and the self-kill net runs over BALLOT bodies alone —
`model_self_kill_disclosure_ballots` reads 6 on samples/9p2i, 0 on samples/4p1i,
17 on ml_corpus/9p2i and 3 on ml_corpus/4p1i. A zero that means "we did not
look" is the failure this task fixes, and the fix carries the verifier's
constraint re-measured on these bytes: the raw net over the visible surface
(`free_text` + each claim's `reason` and `evidence`) catches 10 of 3,631 turns —
7 CREWMATE, 3 IMPOSTOR — of which exactly 1 is a genuine confession on a hand
read, so precision is 1/10 pooled and 1/3 within impostor speakers. The
documented exclusion list drops 5 of the 10 quotation/conditional forms, leaving
5 (4 crew, 1 impostor) and taking within-impostor precision to 1/1 — the
exclusion is therefore a gate that DEMONSTRABLY bites on these bytes, in both
directions, which is what the planted case must pin. What ships is a ROLE-SPLIT,
explicitly labelled UPPER BOUND with its crew false-positive control published
beside it — the shape `model_machinery_vocabulary_ballots` already uses in this
module — never a bare substring count read as a leak rate. The gameplay half of
that finding (block or flag a confession at the chokepoint) is NOT executed
here: the one confessor WAS ejected in the meeting they confessed in
(`headless-seed-1079:meeting-2`, ejected p-7, an impostor), so the corpus still
does not show that confession is free, and re-pricing a behaviour on 1
occurrence in 3,631 turns would be a balance change wearing an instrument's
clothes.

One discipline binds every number above, and it has already bitten once. The
contract as drafted measured every cell over the baseline-7 committed bytes;
Task 21.15 (#412) replaced those bytes, and this re-anchor re-derived every
number above over the baseline-8 replacements — one class (the A-22 vent
fabrication) went to ZERO, one confession count halved, and the self-kill ballot
cell moved 11 → 6. Baseline 8 is the ground the counterfactual, the
pre-registration and the adopting record all stand on, and the justice premises
this task inherits are 21.15 §5.1's (innocent ejections 42 → 46, non-direct
conviction accuracy 0.5922 → 0.5208, the sole-flag wrongful-conviction class
re-opened 0 → 4) plus the two landed instruments' cells (21.18: the reporter is
34 of the 46 innocent ejections = 73.9%, 5.48% per slot against 0.65%, relative
risk 8.50x; 21.19: 475 of 1,525 accused rows carry no first-hand source, 11 of
425 row-carrying ejections carry none, 33 ejections answer the ejectee's own
charge, 48 ejected subjects carry a map-satisfied placement pair). Still no
Definition-of-done item pins a corpus count: the gates are fixtures, class
invariants and OFF-path byte identity, and the corpus reading of this lever is
the offline counterfactual's, published before any bar is written.

**Files in scope:**
- meetings/constants.py; (the lever's `ENV_TESTIMONY_SHAPES` + `testimony_shapes_enabled(env)` resolver — homed in the stdlib-only leaf because BOTH sides need it and `agents/` may not import `meetings.manager`)
- meetings/schemas.py; (`SawKillObservation` + its union member, added unconditionally on the parse side; `ReportedStatementKind` gains `whereabouts`, `saw_move`, `saw_kill`; the two silent docstrings state what the reduction now does)
- meetings/manager.py; (`derive_reported_testimony` reads the lever ONCE and emits the three new kinds under it; OFF returns the current tuple byte-for-byte)
- agents/memory/store.py; (`absorb_reported_testimony`: a `whereabouts` feeds `record_alibi` as an `alibi` does; `_render_reported_testimony` gains one body per new kind)
- agents/strategic/prompts/loader.py; (the lever resolved ONCE in `build_prompt_renderers` beside 18.10's read at :1048, and bound into the `crewmate_report` / `statement` `functools.partial`s at :1067-1084 — a construction-bound render kwarg, NOT a swapped filename. Binding through the partial is what keeps this task out of the `render_contract` Protocols entirely: no `ReportPromptRenderer` / `StatementPromptRenderer` signature moves and none of the FIVE conforming test stubs is forced. The 18.10 file-swap routing at :751-753 / :888-890 is the shape this task must NOT clone — see the re-anchor ruling)
- agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2; (RE-BODIED, 21.18's shape: the shape menu at :143-148 gains a guarded `saw_kill` row and one guarded instruction line beside the vent mandate at :129. Lever OFF renders the committed bytes exactly)
- agents/strategic/prompts/qwen3_6_27b/accusation_round.j2; (RE-BODIED: the same two guarded insertions on the CREW branch only — the menu at :271-276 and the mandate at :252 / :255. The impostor branch and every unguarded byte are untouched)
- orchestrator/game.py; (`TESTIMONY_SHAPES_PROMPT_VERSION_SETS` built with `_lever_arm_versions("qwen3_6_27b", "testimony_shapes")` (:415-437) overriding `crewmate_report` and `accusation_round` ALONE — 21.18's RE-BODY shape, the same one 21.19 cloned — so the ON stamps read `crewmate_report.qwen3_6_27b.v5.testimony_shapes` / `accusation_round.qwen3_6_27b.v5.testimony_shapes` and the other two keys inherit the default registry's values. Plus one row in `_PROMPT_VERSION_OVERLAYS` (:478-482) and one in `_PROMPT_OVERLAY_LABELS` (:486-490). NOT the 18.10 `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` file-swap shape. The default `PROMPT_VERSION_SETS` entry is NOT re-bumped — v5 was spent once this phase at 21.1)
- eval/deduction_metrics.py; (the player-visible confession cells, record-free and unconditional, plus the one-line correction of the adjacent false control claim)
- tests/meetings/test_reported_testimony_derive.py; (OFF identity, ON emission per kind, the destination-only rule, determinism)
- tests/agents/test_reported_testimony.py; (ingest + render + `alibi_map` under the lever, and the own-statement/roster guards still holding)
- tests/meetings/test_schemas.py; (the new observation parses, round-trips, and rejects a malformed payload)
- tests/agents/test_prompt_loader.py; (routing: OFF renders the committed bytes, ON renders them plus exactly the two guarded insertions, and ON with a set whose bodies carry no guard fails loud at construction)
- tests/agents/test_bespoke_prompt_sets.py; (the ON render equals the OFF render plus exactly the two named insertions, asserted as a DIFF and not as containment — the gate that would be prose otherwise. NOTE the empirical case for the re-body shape lives right here: `accusation_round_roll_call.j2` at HEAD is missing the `saw_move` menu row its default has carried since 20.31 and still carries the pre-F2-sweep "a contradiction flag corroborates" wording the 21.11 sweep fixed in the default — TWO default fixes one copied body has already missed, with `tests/agents/test_impostor_answer_arm.py::test_the_variant_arm_has_diverged_from_the_live_default_set` (:555) pinning the divergence rather than preventing it. Authoring two more copies would be the third and fourth)
- tests/meetings/test_prompt_byte_golden.py; (the OFF-PATH GOLDEN half is RUN UNCHANGED, never edited — an edited golden proves nothing. The OVERLAY-SEAM half IS in scope for exactly ONE edit: `_ALL_ON_STAMPS` (:1107-1115) is materialised BY NAME and asserted at :1263, so a fourth overlay makes it stale by construction. `_OVERLAY_KEYS` (:1097), `_contributors` / `_templates_touched_by` (:1118-1143), `_resolve_every_subset` (:1145-1153) and `overlay_stamp_violations` (:1156-1220) are all registry-derived and need NO edit — the enumeration grows from 8 to 16 subsets on its own. The `_ALL_ON_STAMPS` rows this task must write are: `crewmate_report` → `crewmate_report.qwen3_6_27b.v5.reporter_reasoning+crewmate_report.qwen3_6_27b.v5.testimony_shapes`; `accusation_round` → `accusation_round_roll_call.qwen3_6_27b.v1+accusation_round.qwen3_6_27b.v5.reporter_reasoning+accusation_round.qwen3_6_27b.v5.testimony_shapes`; `impostor_report` and `vote_ballot` unchanged)
- tests/eval/test_deduction_metrics.py; (the new cells, their crew control, and the exclusion list's planted case)
- orchestrator/replay.py; (register `testimony_shapes` in `_TOGGLEABLE_LEVER_RESOLVERS`, newest last — this lever registers ITSELF, the same as its two siblings)
- .env.example; (the new toggle's commented bare default and its paragraph, in the voice of the two entries above it)
- tests/orchestrator/test_replay.py; (NOT an incidental forced touch — it is where the registration is PROVED, the 21.18/21.19 disposition. Its literal pins break on the registration alone, verified at HEAD: `_BARE_STAMP` at :162-166, `assert len(_TOGGLEABLE_LEVER_RESOLVERS) == 3` at :380, the two `TOGGLEABLE_SUBSTRATE_FLAG_KEYS == (...)` tuples at :356 and :395, the registration-order list at :428-431, and the `set(_BARE_STAMP) - set(_BASELINE7_STAMP)` difference assertion at :464-468. Add the key constant beside :88-89, extend `_BARE_STAMP`, move the count to 4, add the identity assertion beside :391, and add a `test_a_committed_stamp_predating_testimony_shapes_still_reads_false`)

**Files NOT in scope:**
- `SUBSTRATE_FLAG_KEYS`' ordering convention and the retired half of the registry (this task appends ONE live-toggle entry; the retired block is 21.24's on ADOPTED and no key changes index here)
- observation/service.py, agents/perception.py (naming the victim in the witnessed-kill line needs the perception packet widened; that is a firewall-crossing entitlement change and is deliberately not this task's — the shape carries killer/room/tick, which is exactly what the memory line already holds)
- meetings/transcript.py (this task mints NO contradiction flag and changes NO band; a spoken `saw_kill` is content, and the detector is untouched)
- agents/memory/beliefs.py (`record_alibi` is CALLED with a new source, never redefined; no suspicion delta moves)
- agents/strategic/prompts/qwen3_6_27b/impostor_report.j2 and vote_ballot.j2 (the impostor never holds a speakable witnessed-kill row, and 21.19's `<testimony_sources>` block owns the ballot; neither body moves here)
- agents/strategic/prompts/qwen3_6_27b/accusation_round_roll_call.j2 and impostor_report_roll_call.j2 (18.10's frozen v1 variant bodies. Because this task RE-BODIES rather than swaps, it inherits no obligation to author its blocks into them, and `tests/meetings/test_prompt_byte_golden.py::test_a_file_swapping_arm_serves_a_body_its_siblings_do_not_reach` (:1266-1311) stays green and stays pinned-open. Do NOT touch either file or that test — closing that gap is 21.24's, per the re-anchor ruling)
- meetings/render_contract.py and the FIVE conforming renderer-stub sites (`tests/meetings/_manager_helpers.py`, `tests/meetings/test_manager.py`, `tests/orchestrator/test_meeting_integration.py`, `tests/orchestrator/test_replay_meetings.py`, `tests/agents/test_beliefs.py`) — no Protocol widens here, because the lever is bound into the loader's `partial` at construction rather than threaded by the caller
- the other six prompt sets under agents/strategic/prompts/ (the guarded insertions are authored only in the served set's bodies, exactly as 21.18's and 21.19's are; `_lever_arm_versions` scopes the overlay to `qwen3_6_27b` alone)
- eval/evidence_honesty.py, eval/meeting_quality.py, eval/vote_correctness.py (instruments that CONSUME cells; this task must not redefine one — if a needed cell is missing, say so in the PR)
- replays/ (no committed byte moves here; the counterfactual reads them and writes nothing)

**Merge-reality expectation (forced touches outside Files-in-scope, the #403 precedent):** The
REGISTRATION alone forces four files, expected in the diff and flagged in the PR's Questions
rather than absorbed silently — the disposition 21.4, 21.5, 21.18 and 21.19 all used. (1)
`tests/experiments/test_probe_backends.py`: `_FLAGS_ON` (:78-113) is an INDEPENDENT literal of the
bare snapshot compared by dict equality, so ANY registration breaks it — append
`"testimony_shapes": False` after :112, move the comments at :76-77 and :106-108 from THREE to
FOUR, add the `monkeypatch.delenv("AILIBI_TESTIMONY_SHAPES", …)` guard beside :559 and :617, and
grow the grid in `test_active_substrate_flags_reads_env_for_the_live_toggles` (:609+) by its
fourth row. (2)-(4) THREE prose sites carry a live-toggle COUNT this registration falsifies and no
gate catches: `docs/architecture.md`:151-152 ("plus three live toggles
(`TOGGLEABLE_SUBSTRATE_FLAG_KEYS` — `impostor_roll_call`, …)"), `docs/glossary.md`:66 ("Twenty-one
have graduated; three live toggles remain — …") and `scripts/record_ml_corpus.sh`:122-124 ("the
live toggles (impostor_roll_call, reporter_reasoning, corroboration_discipline) recorded OFF unless
--expect-levers declares one ON"). Each is ONE clause, not a new paragraph; `docs/architecture.md`
is exactly **1,296** words at HEAD (`wc -w`), a self-imposed size no gate enforces, so any growth
there must be paid for on the same page (21.19's Decision 9 is the worked precedent). NOT forced,
and this is the point of the loader-partial binding: the FIVE conforming renderer stubs
(`tests/meetings/_manager_helpers.py`, `tests/meetings/test_manager.py`,
`tests/orchestrator/test_meeting_integration.py`, `tests/orchestrator/test_replay_meetings.py`,
`tests/agents/test_beliefs.py` — the fifth is the one 21.19 discovered outside its own block) stay
untouched, because no Protocol widens. If a Protocol DOES end up widening, all five move together
and the PR must say so. Run
`uv run pytest tests/orchestrator/test_replay.py tests/experiments/test_probe_backends.py -q`
WITH the registration step rather than discovering it at `check.sh`.

**Definition of done:**
- [ ] `meetings.constants.testimony_shapes_enabled(env)` follows the standing resolver signature — default OFF on unset/empty/unrecognised, `1/true/yes/on` case-insensitively, `env` threaded so tests never mutate `os.environ` — and `meetings/constants.py` stays a stdlib-only leaf (its entire import set today is `typing.Final`; the resolver adds `os` and `collections.abc.Mapping` and nothing else — no `meetings.*` / `agents.*` / `engine.*` edge, which is the rule its own docstring states at :14-15), with its module docstring stating why a resolver is homed there: `agents/strategic/prompts/loader.py` and `meetings/manager.py` must read ONE lever, and the `agents ↛ meetings.manager` import contract forbids the obvious home.
- [ ] OFF-path identity is proved before anything else: with the lever unset, `derive_reported_testimony` returns a tuple equal element-for-element to HEAD's over every committed meeting in the four sets, `tests/meetings/test_prompt_byte_golden.py` is green, and `bash scripts/verify_samples.sh` reports 100/100 — the three proofs that no rendered or recorded byte moved.
- [ ] Under the lever, `derive_reported_testimony` emits a `whereabouts` statement per `WhereaboutsClaim` with `subject == turn.speaker` and `from_tick == to_tick == observation.tick`, and a `saw_move` statement per `SawMoveObservation` carrying the DESTINATION placement only (`room == observation.to_room`, `from_tick == to_tick == observation.tick`) — the origin half is not carried, and the reduction's docstring states the shape's own reason (meetings/schemas.py:154-181: a second placement per shape re-opens the off-by-one class the shape closes).
- [ ] `tests/meetings/test_reported_testimony_derive.py` pins ON/OFF for each new kind on the same fixture transcript, pins that repeated calls return equal tuples (the determinism the module promises), and pins the sort key still totally orders a mixed statement set — the reduction stays a pure, replay-deterministic function of the recorded `MeetingResult` with the lever as its only other input.
- [ ] `absorb_reported_testimony` folds a `whereabouts` statement into `alibi_map` through `BeliefState.record_alibi` exactly as an `alibi` does, with the existing guards unchanged and re-pinned: an own statement is skipped, a non-roster speaker or subject is skipped, and a self-placement about the recipient never materialises a SELF belief row. `tests/agents/test_reported_testimony.py` carries the perturbation — the same fixture with the lever OFF leaves `alibi_map` exactly as HEAD leaves it.
- [ ] `_render_reported_testimony` gains one body per new kind inside the existing `[meeting n] CLAIM by X (unverified):` frame, and a malformed payload for any of the three still renders nothing (the module's defensive `.get` convention, pinned by a test that plants a row with a missing room).
- [ ] `meetings.schemas.SawKillObservation` carries `{type: "saw_kill", tick, subject, room}` — no victim field — is a member of `ObservationClaim`, and is accepted by the turn parser UNCONDITIONALLY (the `SawMoveObservation` precedent: parsing never depends on which templates offer a shape). Its docstring states in one line that it mints no contradiction flag and no band, and that the grounded role-proof channel is `saw_vent`'s alone.
- [ ] The two guarded insertions are authored INSIDE the current default bodies of the served set (`{% if testimony_shapes %}`-style guards, 21.18's shape — no new template file exists), and `tests/agents/test_bespoke_prompt_sets.py` pins that the ON render equals the OFF render plus exactly the shape-menu row and the one paired instruction line, asserted as a DIFF and never as containment — a failable gate against the guard leaking bytes into the OFF path. The `accusation_round` insertion sits on the CREW branch only; the impostor-facing branch renders byte-identically under both lever states.
- [ ] Routing is bound once, at construction, on both halves: `build_prompt_renderers` binds the lever's resolved boolean into the `crewmate_report` / `statement` `functools.partial`s, and `prompt_versions_for_set` serves `TESTIMONY_SHAPES_PROMPT_VERSION_SETS` under the same read — so a recording's rendered bytes and its recorded stamps can never come from two different routing decisions (audits/audit-phase-17-absence-gate.md Ruling 3(d)). Lever ON with a set whose bodies carry no `testimony_shapes` guard raises `ValueError` at construction — a MISSING body, which is a real defect, and the message must be about the missing body and never about a sibling being on (the shape `_overlay_entry` already uses at orchestrator/game.py:523-545, and which `tests/agents/test_impostor_answer_arm.py::test_lever_on_fails_loud_for_a_set_without_a_variant_entry` (:728) pins for 18.10). Lever ON together with a sibling overlay does NOT raise: this lever registers COMPOSITIONALLY into the seam Task 21.18 built, because the all-ON slate is precisely what 21.23 smokes and 21.24 records, and a seam that refused a sibling could not construct a renderer for the only configuration this phase spends a record on. Composition follows 21.18's three rules unchanged — application order is `_TOGGLEABLE_LEVER_RESOLVERS` order, each enabled combination resolves to a composite per-template stamp derived from the participating overlay names in that order, and the all-ON composite is materialised and pinned by name. This task adds its overlay to the fold and one row to the exhaustive subset test; it adds no branch and no pairwise special case.
- [ ] The arm stamps are the set's own values with the arm key appended, per `_lever_arm_versions`' convention (orchestrator/game.py:415-437): `crewmate_report.qwen3_6_27b.v5.testimony_shapes` and `accusation_round.qwen3_6_27b.v5.testimony_shapes`. `impostor_report` and `vote_ballot` inherit the default registry's values, because this arm does not re-body them. No arm value contains `+`, so an arm stamp can never collide with a composite, and `overlay_stamp_violations` (tests/meetings/test_prompt_byte_golden.py:1156-1220) proves exhaustively over all 16 subsets that no two distinct subsets share a version string on any template either re-bodies and that no non-empty subset resolves a template IT re-bodies to a default value — registry-derived, so it grows from 8 subsets to 16 with no edit to its enumeration.
- [ ] `eval/deduction_metrics.py` runs the self-kill and role nets over the PLAYER-VISIBLE surface — `turn.free_text` plus each claim's `reason` and `evidence`, since the turn render puts the reason on the table — and publishes them as role-split cells beside `player_visible_leak_turns`, with the impostor-side cell documented as an explicit UPPER BOUND and the crew-side cell as its false-positive control. A documented exclusion list drops the quotation/conditional forms the verifier measured as the noise ("how do you know I killed", "if I killed", "you claim I killed"), and a planted case proves the exclusion bites in both directions.
- [ ] The adjacent `crew_omniscient_control_ballots` claim was ALREADY corrected — Task 21.9 (#402, commit `22193d8b`) replaced "both 0 on every committed set" with the per-set reading now standing at eval/deduction_metrics.py:257-261 and :481-484. But 21.9 measured it on the BASELINE-7 bytes and 21.15 replaced them, so the standing sentence is now WRONG in one cell: re-derived at THIS HEAD from the committed reports it reads **1 on samples/9p2i, 0 on samples/4p1i, 2 on ml_corpus/9p2i, 0 on ml_corpus/4p1i** — not "1 on each of the two 9p2i sets". Correct BOTH sites in the same edit to the true per-set reading, and name the command that recomputes it (craft rule 5). Correct in the same pass the module's own "``player_visible_leak_turns`` is the partner net over player-visible ``free_text``" framing where this contract's prose relied on it being the module's ONLY player-visible net: 21.9 added `oracle_register_turns` and `oracle_register_claim_reasons` over the same surfaces (:2494-2495, :2503-2504).
- [ ] The lever REGISTERS itself: `testimony_shapes` is appended to `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` bound to `meetings.constants.testimony_shapes_enabled` (no local mirror), so `SUBSTRATE_FLAG_KEYS` grows by a pure append at the live-toggle end and every already-recorded key keeps its index. `tests/orchestrator/test_replay.py` pins that a bare env stamps the key `False` and that a stamp recorded before the key existed still reads `False` through the missing-key rule — `bool(recorded.get(key))` in `api/replay_loader.py::_assert_substrate_matches` (:817), whose contract the registry comment states at `orchestrator/replay.py:660-662` and `substrate_flag_snapshot`'s docstring at :707-715. Registering here rather than in a later collecting task is what lets the offline counterfactual price the full Wave-2 slate: it reads the live registry (FOUR keys after this task) and refuses before printing if a priced lever is absent.
- [ ] The re-derivation seam is closed by that registration and the closure is pinned, not promised: a recording whose `game_over` stamp carries `testimony_shapes: False` loaded with the lever ON is REFUSED by `api/replay_loader.py`'s substrate check rather than silently re-derived through `derive_reported_testimony`, and the test asserts the refusal names the diverging key. The PR states which consumers re-derive at load time and that all of them now sit behind that guard.
- [ ] `.env.example` documents `AILIBI_TESTIMONY_SHAPES` as a commented `# AILIBI_TESTIMONY_SHAPES=0` bare default appended after 21.19's entry (which ends at :188), in the voice of the three entries above it, including the warning that flipping it for a serving or verify run against committed bytes produces a substrate mismatch. THREE existing count sentences are falsified and must move to FOUR in the same edit, verified at HEAD: :120-122 ("one of the THREE substrate variables this build still reads (the others are the reporter-voice and source-count arms below)"), :144-145 ("the second of the THREE substrate variables this build still reads") and :167-168 ("the third substrate variable this build still reads"). `uv run python scripts/check_doc_facts.py` is green, since `check_lever_registry` (scripts/check_doc_facts.py:1554-1666) demands a commented bare default PER REGISTERED KEY and refuses any uncommented `AILIBI_<KEY>=` anywhere in the file; its "N-lever substrate registry" string at :761 is derived from `len(SUBSTRATE_FLAG_KEYS)` and needs no edit.
- [ ] `tests/meetings/test_lever_registry.py` stays green with **NO edit at all** — 21.18 rewrote it to derive the live set from `_TOGGLEABLE_LEVER_RESOLVERS` (`test_every_live_resolver_in_the_tree_is_not_reported` :298-316, `test_the_live_toggle_registry_is_the_key_order` :318-326), 21.19 confirmed a later registration needs none, and no count is typed in prose there. That generalisation imposes TWO gates this task satisfies by construction: `assert resolver.__name__.lstrip("_") == f"{key}_enabled"` (:313), so the resolver MUST be named `testimony_shapes_enabled`; and `inspect.getsourcefile` (:307) must resolve its module — `meetings/constants.py` does, and it sits inside `_SWEPT_PACKAGES` (:52), so the `ast` sweep that fails any `*_enabled` ignoring its `env` argument WILL read it.
- [ ] No cell, count or threshold in this task is pinned to a committed-corpus number: every gate is a fixture or a class invariant, because the bytes those numbers describe are replaced by the re-record this task depends on. The PR states this in one line.
- [ ] The PR quotes a lever-ON re-derivation over the committed bytes for orientation only — reported rows added per meeting by each arm, and the alibi-map coverage before and after — labelled as an OFFLINE re-derivation of superseded bytes, with no bar, no verdict and no claim about what the record will show.
- [ ] The blast radius is stated in the PR from a fresh grep of every `derive_reported_testimony` / `absorb_reported_testimony` consumer. Re-grepped at HEAD there are SEVEN, not six — the contract's list missed `training/anchor_study.py`: orchestrator/game.py:2598, api/replay_loader.py:1490, eval/off_menu.py:509, eval/funnel.py:1301, eval/evidence_honesty.py:1365, scripts/counterfactual_phase20.py:527, **training/anchor_study.py:637**. Name which of them read the ambient environment and which are handed one, and say explicitly whether `training/anchor_study.py` (which is outside `api/replay_loader.py`'s substrate guard) can re-derive with the lever ON over OFF-stamped bytes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

BLOCK 1 — the lever, before any behaviour. Add `ENV_TESTIMONY_SHAPES =
"AILIBI_TESTIMONY_SHAPES"` and `testimony_shapes_enabled(env=None)` to
`meetings/constants.py`, mirroring `impostor_roll_call_enabled`
(agents/strategic/prompts/loader.py:359-363) line for line. The home is forced,
not stylistic: `meetings/manager.py` needs it for the reduction and
`agents/strategic/prompts/loader.py` needs it for routing, and
`.importlinter`'s `agents_must_not_import_meetings_manager` contract makes the
manager unavailable to the loader. Extend the leaf's docstring rather than
leaving the reader to infer it. `tests/meetings/test_lever_registry.py` walks
this tree with `ast` and fails any `*_enabled` that ignores its `env` argument,
so write the resolver to read `env` on the first pass.

BLOCK 2 — the ingest arm (B-7), the cheap half. `derive_reported_testimony`
gains a keyword-only `env: Mapping[str, str] | None = None`, reads the resolver
ONCE at the top into a local, and adds three branches: `WhereaboutsClaim` and
`SawMoveObservation` in the observation loop (they are observations, not
claims — the discriminated union puts both there), and `SawKillObservation`
beside `SawVentObservation`. Every new branch is inside `if lever_on:` so the
OFF tuple is produced by exactly the code that produces it today. Widen
`ReportedStatementKind` with the three members and state the population rule
per kind in the `ReportedStatement` docstring's existing per-kind list, in its
voice: `whereabouts` — `from_tick == to_tick`, room, subject IS the speaker;
`saw_move` — `from_tick == to_tick`, room is the DESTINATION; `saw_kill` —
`from_tick == to_tick`, room, no companions. Then correct the two schema
docstrings that are silent about the reduction (`WhereaboutsClaim`,
`SawMoveObservation`) the way Task 20.29 corrected `SawVentObservation`'s.

BLOCK 3 — ingest and render. In `absorb_reported_testimony`, the `alibi_map`
write is one condition: `statement.kind in ("alibi", "whereabouts")`. Nothing
else in that function changes — the own-statement guard already drops a
speaker's own roll-call before it reaches the write, and the roster gate is
unchanged. In `_render_reported_testimony` add three bodies in the existing
`elif` chain, each guarding its own payload types exactly as its siblings do:
`whereabouts` → `{subject} placed themselves in {room} @ tick {t}`; `saw_move`
→ `saw {subject} arrive in {room} @ tick {t}`; `saw_kill` → `saw {subject} KILL
in {room} @ tick {t}`, capitalised like the vent body because it is the same
class of assertion. Keep the frame and the salience untouched: these are
unverified third-party claims and must read as such.

BLOCK 4 — the speakable kill (A-22). `SawKillObservation` is a copy of
`SawVentObservation`'s fields with a `saw_kill` discriminator; add it to
`ObservationClaim` and nothing else. Then the two guarded insertions, INSIDE the
default bodies (the re-body ruling): behind the lever's guard, add ONE menu line —
`{"type": "saw_kill", "tick": <int>, "subject": "<player id>", "room": "<room
id>"} — only for a kill you watched happen, copied exactly from your memory
line; name the killer, not the victim.` — and ONE instruction line beside the
existing vent mandate telling the reader to use it instead of `saw_vent` for a
witnessed murder. Do not touch the impostor branch of the accusation-round
body, and no unguarded byte moves. The diff test in
`tests/agents/test_bespoke_prompt_sets.py` is what stops the guard rotting:
assert the ON render equals the OFF render with exactly those insertions, so a
guard that leaks bytes into the OFF path, or an insertion that swallows a
neighbouring line, turns it red.

BLOCK 5 — routing and stamps, the pairing that must not split. Resolve the lever
ONCE in `build_prompt_renderers` beside 18.10's read (loader.py:1048) and bind
the resulting boolean into the `crewmate_report` and `statement`
`functools.partial`s (:1067-1084) so the render decision is frozen at
construction, exactly where `prompt_versions_for_set` is read — a mid-run export
must not be able to move rendered bytes while the stamp stays frozen (21.18's
Codex round-2 fix; 21.19 Decision 12 went further and REFUSES a
version/environment disagreement, which is routed to 21.24 for generalisation).
Pre-check at construction that the served set's bodies actually carry the guard,
so an unauthored set fails there and never at render. Then
`TESTIMONY_SHAPES_PROMPT_VERSION_SETS` in `orchestrator/game.py` beside
`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, registering into the overlay seam
Task 21.18 built in `prompt_versions_for_set` rather than forking it, and
leaving the default `PROMPT_VERSION_SETS` entry alone — it moved once this
phase, at 21.1's v5, and no lever re-bumps it. FOUR levers now feed one
lookup (the 18.10 arm plus the three Wave-2 overlays — verified at HEAD:
`_PROMPT_VERSION_OVERLAYS` carries three entries, the roll-call arm among them,
and this task's is the fourth), and they COMPOSE
rather than exclude: 21.24 records with all three Wave-2 keys True, so a
raise on a sibling would refuse the only slate this phase spends a record
on. Add this overlay to 21.18's fold — do not write a pairwise precedence
rule, and do not add a branch — then extend the exhaustive subset test by
its row. What must stay impossible is two distinct subsets resolving to the
same stamp, or any subset colliding with a default value; that is the
render-one-stamp-another failure the 18.10 docstring warns about, and the
subset enumeration is what proves it cannot happen. The only `ValueError`
this lever raises at construction is for a set with no variant BODY.

BLOCK 6 — the instrument (A-16), record-free and independent of the lever. The
partner increment at :2492-2493 stays; add the role split beside it inside the
same turn loop (:2474-2504), which already holds `role = roles[turn.speaker]`
at :2476 and already scans claim `reason` for the oracle register at :2503-2504
— reuse that claim walk rather than opening a second one. Build the visible
text once per turn — `free_text` plus each claim's `reason` and `evidence` —
and run the self-kill and role nets over it. Two new int fields on
`ScaffoldLeakageCells` with their `_require_non_negative` entries, documented in
the module docstring's leakage block: the impostor cell as an UPPER BOUND (the
module's own precedent for a net it cannot fully disambiguate is
`model_machinery_vocabulary_ballots`, :277-279) and the crew cell as its control.
The exclusion list is a module constant with a docstring stating what it drops
and why, and its planted case asserts both directions — an excluded quotation
does not count, and a bare first-person admission does. While in that
docstring, RE-derive the control sentence 21.9 already corrected at :257-261 (and its twin at :481-484): it is now stale in one cell against the baseline-8 bytes — see the Definition-of-done item.

BLOCK 7 — registration, last and in one commit with the resolver. Append
`("testimony_shapes", testimony_shapes_enabled)` to `_TOGGLEABLE_LEVER_RESOLVERS`
(orchestrator/replay.py:669-675, appending after :674), and grow the registry
comment block at :636-668 from THREE live toggles to FOUR with a fourth bullet in
the same voice, importing the resolver from `meetings.constants` —
that module is a stdlib-only leaf, so there is no import-contract obstacle and no
local mirror is needed. Two sibling levers registered ahead of you, so read the
tuple at HEAD rather than at this contract's line number, and append at the live
end so no already-recorded key moves index. Then `.env.example` in the voice of
the two entries above yours, and the `tests/orchestrator/test_replay.py` pair
(bare env stamps False; a pre-key recording reads False). This is what makes the
downstream counterfactual able to price the FOUR-key registry (three of them
Wave-2's slate) — it reads the live registry and refuses before printing if a
priced lever is missing.

BLOCK 8 — before pushing. Run the byte-golden and `verify_samples.sh` with a
clean environment FIRST; if either moves with the lever unset, the OFF path is
not identical and nothing else matters. Then run the ON path over the committed
bytes to produce the PR's orientation numbers, toggling through the resolver's
`env` argument and never through `os.environ`.

## Public types this task introduces
- `meetings.constants.ENV_TESTIMONY_SHAPES`
- `meetings.constants.testimony_shapes_enabled`
- `meetings.schemas.SawKillObservation`
- `orchestrator.game.TESTIMONY_SHAPES_PROMPT_VERSION_SETS`
- `eval.deduction_metrics.CONFESSION_QUOTATION_EXCLUSIONS`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This lever reaches three layers that normally move separately — the meeting
reduction, agent memory, and the rendered prompt — and it is the only Wave-2
lever that changes what a template OFFERS.

Risk 1 — the re-derivation seam. `derive_reported_testimony` is re-run at LOAD
time by `api/replay_loader.py:1378` and by four eval consumers, so a recording
made with the lever OFF and re-derived with it ON would reconstruct memory the
game never held. The substrate stamp is the defence and this task installs it:
the registration above is in scope precisely because the seam it closes is this
task's own. Ship the two together or neither — a resolver without a registered
key is a behaviour change no recording identifies, and the pin that proves the
closure (an OFF-stamped recording loaded with the lever ON is REFUSED, not
silently re-derived) is a DoD item here rather than a promise made to a later
task.

Risk 2 — three levers, one prompt surface, landing in a fixed order. The
dependency graph serializes them 21.18 → 21.19 → 21.20, so this is NOT a merge
race: it is inherited serial edits. This task lands LAST on `meetings/manager.py`,
`agents/strategic/prompts/loader.py`, `orchestrator/replay.py`, `.env.example`
and the `prompt_versions_for_set` overlay seam, so every surface it touches
already carries two levers' worth of changes and the anchors in this contract
were read at the pre-Wave-2 HEAD. Re-read each one before editing rather than
trusting a line number, extend the seam 21.18 built rather than forking it, and
keep this lever's read local — resolve once per entry point, never store a
module-level boolean, never widen a shared signature for two levers at once. If
a sibling's edit has already changed the shape this contract assumes, say so in
the PR and stop; do not reshape a merged lever to fit this one.

Risk 3 — variant drift, DESIGNED OUT rather than mitigated. The drafted contract
copied two template bodies; the re-anchor replaced that with 21.18's re-body
shape precisely because the drift risk is not hypothetical here. At HEAD,
18.10's `accusation_round_roll_call.j2` — the one copied body this repo already
carries — is missing the `saw_move` menu row its default has had since 20.31 and
still carries the pre-F2-sweep "a contradiction flag corroborates" wording the
21.11 sweep fixed in the default. Two missed fixes, in one copy, in one phase.
Guarding a block inside the default body cannot drift from it. What replaces the
diff gate is the OFF-path proof: the ON render must equal the OFF render plus
exactly the two named insertions, asserted as a DIFF and never as containment. A
gate that cannot fail is prose. If the implementer nonetheless proposes a
variant FILE, they must first read `orchestrator.game.prompt_versions_for_set`'s
docstring at :581-589 and stop — see Risk 6.

Risk 4 — the shape becoming evidence by accident. `saw_kill` mints no flag and
no band, and `meetings/transcript.py` is out of scope. The temptation at review
time will be "a witnessed kill should be at least as strong as a witnessed
vent" — but a spoken vent earns STRONG only through the typed grounding
channel, and no equivalent channel exists for kills. Adding one is a separate,
larger task with its own entitlement question; promoting an ungrounded kill
claim would hand the fabrication class a stronger shape than the one it already
misuses. Pin the census: under the lever, over the committed bytes, no
contradiction kind's count changes.

Risk 5 — the confession instrument reading as a rate. The cell is an upper
bound over a net re-measured at 1/10 precision pooled (1/3 within impostor
speakers, 1/1 after the documented exclusions), on a base of 1 genuine
confession in 3,631 turns. It must ship labelled, role-split, with its control
beside it, and no downstream doc may quote the impostor cell alone as a leak
count. This is the same failure the module already documents for its vent
exclusion at :265-270 — the precedent to follow, not to re-litigate.

Risk 6 — the two-file-swap collision, which is why the shape reversal is not a
style call. `impostor_roll_call` ALREADY swaps `accusation_round.j2` for
`accusation_round_roll_call.j2` (loader.py:1052-1053). Had this task swapped a
second variant of the same template, the two arms could not both be served: the
loader can bind exactly one filename, while `prompt_versions_for_set`'s fold
(:606-621) would happily compose BOTH lineages into one stamp, and
`_ALL_ON_STAMPS` — materialised by name and asserted at
tests/meetings/test_prompt_byte_golden.py:1263 — would then pin a stamp claiming
two bodies the render cannot both have. That is the render-one-stamp-another
failure the seam exists to prevent, arriving through the seam's own front door.
The re-body shape dissolves it: a guarded block inside the default body composes
with a sibling's guarded block in the SAME body, and with a file swap it simply
does not reach the variant — the KNOWN, PINNED gap, unchanged. Under no
circumstance may this task add a pairwise precedence rule, a second branch in
`prompt_versions_for_set`, or a cross-product variant file.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.corroboration"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import orchestrator.game.TacticalAgent"`
- `uv run python -c "import eval.reporter_justice"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import eval.vj_instruments"`
- `uv run python -c "import eval.vj_instruments.VJInstrumentReport"`
- `uv run python -c "import eval.vj_instruments.VJMeetingRow"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import frontend/src/lib/contradictions"`
- `uv run python -c "import check_doc_facts"`

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
Open a PR from branch `phase-21-testimony-shapes` with a title like `task 21.20: what you saw is what you can say (lever `testimony_shapes`, default off)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it. The CONTRACT's own strikeability was resolved at the #396 ratification — the owner kept it IN and it dispatches. What remains an owner decision point is the ARM: whether the lever ships ON at the adopting record, which 21.22's pre-registration and 21.24's record decide, not this task). Anchors RE-VERIFIED at HEAD `3d1b41e9` (the drafting session read `d8ec0a1c`, 48 commits back — every line number below moved, and four empirical premises moved with them; see the re-anchor rulings): meetings/schemas.py:574-584 (`ReportedStatementKind`, the closed FIVE), :118-144 (`SawVentObservation`, whose docstring states the reduction to a `saw_vent` `ReportedStatement` — the 20.29 precedent for widening the kind set when a new sayable shape lands, though the task id itself is not in the text), :147-174 (`WhereaboutsClaim` — silent about the reduction), :177-205 (`SawMoveObservation` — its "contributes EXACTLY ONE placement, the destination" ruling at :188-195 is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" at :195-198 is the parse/offer split this task reuses), :208-216 (the `ObservationClaim` discriminated union — six members), :587-620 (`ReportedStatement`, whose optional fields are populated per kind, the per-kind list at :599-608); meetings/manager.py:4027-4135 (`derive_reported_testimony`: the observation loop at :4081-4104 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :4105-4134 only the three claims, no else-branch and no raise; the sorted return at :4135; the docstring's own "``completed_task`` / ``found_body`` observations and all free-text are dropped" at :4044-4045); agents/memory/store.py:578-703 (`absorb_reported_testimony`; the `alibi_map` write at :691-703 is gated on `statement.kind == "alibi"` at :692), :1611-1615 (the render dispatch) + :1939-2001 (`_render_reported_testimony`, the five per-kind bodies at :1973-1993 and the `[meeting n] CLAIM by X (unverified):` frame at :1972), :1835-1841 (the witnessed-kill memory line at :1839 — killer, room and tick, no victim), :1035-1099 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` returns True at :1055-1056 and is dropped before it is ever rendered); meetings/transcript.py:2289-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2517-2569 (`_iter_move_placements`: a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:129 (the vent-first mandate the kill line parallels) + :143-152 (the shape menu — SIX observation shapes at :143-148, three claim shapes at :150-152) and accusation_round.j2:252 / :255 (the mandate on the opening and reply branches) + :271-280 (the same six-shape menu); agents/strategic/prompts/loader.py:309-320 (the four default + two roll-call filename constants) + :332-366 (`impostor_roll_call_enabled`, the standing resolver SHAPE) + :751-753 / :888-890 / :1012-1090 (the Task-18.10 file-swap routing — cited as the shape this task must NOT clone, see the re-anchor ruling) and orchestrator/game.py:353-412 (`PROMPT_VERSION_SETS` at v5, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`) + :415-437 (`_lever_arm_versions` — 21.18's RE-BODY helper, which IS this task's precedent) + :441-471 (the two landed re-body arms to clone) + :478-503 (`_PROMPT_VERSION_OVERLAYS` / `_PROMPT_OVERLAY_LABELS`) + :506-590 (`enabled_prompt_version_overlays`, `_overlay_entry`, `prompt_versions_for_set` — the composition rules at :569-579, the FILE-SWAPPING-ARM rule at :581-589, the per-template composite fold at :606-621); orchestrator/game.py:2598 and api/replay_loader.py:1490 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale at :3-15; NOTE the module imports only `typing.Final` today — the resolver adds `os` and `collections.abc`); eval/deduction_metrics.py:250-270 + :470-505 (the nets and their documented scope) + :1623-1743 (`ScaffoldLeakageCells`, the docstring's leakage block at :1650-1690 and the int fields at :1717-1743) + :2474-2504 (the turn loop, `role = roles[turn.speaker]` at :2476, the partner increment at :2492-2493, and the TWO oracle-register increments 21.9 added at :2494-2495 / :2503-2504).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
