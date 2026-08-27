# Agent Prompt — 21.20 What you saw is what you can say (lever `testimony_shapes`, default OFF)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.20 — What you saw is what you can say (lever `testimony_shapes`, default OFF), anchored to B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it, and the arm is an owner decision point). Anchors re-verified at HEAD `d8ec0a1c` by the drafting session: meetings/schemas.py:539-541 (`ReportedStatementKind`, the closed FIVE), :95-116 (`SawVentObservation`, whose docstring records the 20.29 precedent of widening the kind set when a new sayable shape lands), :124-148 (`WhereaboutsClaim` — silent about the reduction), :154-181 (`SawMoveObservation` — its "EXACTLY ONE placement, the destination" ruling is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" is the parse/offer split this task reuses), :185-193 (the `ObservationClaim` discriminated union), :552-585 (`ReportedStatement`, whose optional fields are populated per kind); meetings/manager.py:3768-3876 (`derive_reported_testimony`: the observation loop at :3822-3844 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :3846-3875 only the three claims, no else-branch and no raise; the sorted return at :3876); agents/memory/store.py:575-700 (`absorb_reported_testimony`; the `alibi_map` write at :688-700 is gated on `kind == "alibi"`), :1593-1597 + :1921-1983 (`_render_reported_testimony`, the five per-kind bodies and the `[meeting n] CLAIM by X (unverified):` frame), :1817-1823 (the witnessed-kill memory line — killer, room and tick, no victim), :1017-1081 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` is dropped before it is ever rendered); meetings/transcript.py:2291-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2512-2531 (a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:115 + :125-131 and accusation_round.j2:243-249 (the six-shape menus and the vent-first mandate the kill line parallels); agents/strategic/prompts/loader.py:306-317 + :679-687 + :923-971 (the Task-18.10 variant-routing precedent) and orchestrator/game.py:349-421 + :424-470 (`PROMPT_VERSION_SETS`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, `prompt_versions_for_set` — the registry that keeps variant bytes off default stamps, audits/audit-phase-17-absence-gate.md Ruling 3(d)); orchestrator/game.py:2357-2380 and api/replay_loader.py:1369-1388 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale); eval/deduction_metrics.py:250-268 + :474-504 + :1550-1568 + :2350-2351 (the nets, their documented scope, and the ONE player-visible increment).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-testimony-shapes`
**Depends on:** 21.19
**Section refs:** B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it, and the arm is an owner decision point). Anchors re-verified at HEAD `d8ec0a1c` by the drafting session: meetings/schemas.py:539-541 (`ReportedStatementKind`, the closed FIVE), :95-116 (`SawVentObservation`, whose docstring records the 20.29 precedent of widening the kind set when a new sayable shape lands), :124-148 (`WhereaboutsClaim` — silent about the reduction), :154-181 (`SawMoveObservation` — its "EXACTLY ONE placement, the destination" ruling is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" is the parse/offer split this task reuses), :185-193 (the `ObservationClaim` discriminated union), :552-585 (`ReportedStatement`, whose optional fields are populated per kind); meetings/manager.py:3768-3876 (`derive_reported_testimony`: the observation loop at :3822-3844 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :3846-3875 only the three claims, no else-branch and no raise; the sorted return at :3876); agents/memory/store.py:575-700 (`absorb_reported_testimony`; the `alibi_map` write at :688-700 is gated on `kind == "alibi"`), :1593-1597 + :1921-1983 (`_render_reported_testimony`, the five per-kind bodies and the `[meeting n] CLAIM by X (unverified):` frame), :1817-1823 (the witnessed-kill memory line — killer, room and tick, no victim), :1017-1081 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` is dropped before it is ever rendered); meetings/transcript.py:2291-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2512-2531 (a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:115 + :125-131 and accusation_round.j2:243-249 (the six-shape menus and the vent-first mandate the kill line parallels); agents/strategic/prompts/loader.py:306-317 + :679-687 + :923-971 (the Task-18.10 variant-routing precedent) and orchestrator/game.py:349-421 + :424-470 (`PROMPT_VERSION_SETS`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, `prompt_versions_for_set` — the registry that keeps variant bytes off default stamps, audits/audit-phase-17-absence-gate.md Ruling 3(d)); orchestrator/game.py:2357-2380 and api/replay_loader.py:1369-1388 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale); eval/deduction_metrics.py:250-268 + :474-504 + :1550-1568 + :2350-2351 (the nets, their documented scope, and the ONE player-visible increment).
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-21 adopting record — ON moves episodic rows, therefore rendered memory, therefore prompt bytes; the instrument half is record-free and unconditional
**Measurement:** `uv run pytest tests/meetings tests/agents -q` green; `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` green with the lever unset (the OFF-path proof over the committed meetings); `bash scripts/verify_samples.sh` 100/100; the PR quotes, from the fixtures and from a lever-ON re-derivation over the committed bytes, how many reported rows each arm adds per meeting and what the alibi-map coverage becomes — never a bar, never a verdict.

The substrate elicits an answer it then forgets. Every meeting asks each
player for a roll-call self-placement and every crew template offers the
witnessed-transition shape, and both arrive: re-derived at HEAD by the drafting
session over the two `replays/ml_corpus/` sets (476 meetings), the spoken census
is `saw_player` 2,794, **`whereabouts` 2,269**, `accusation` 2,243,
**`saw_move` 1,160**, `corroboration` 1,074, `alibi` 706. The two bolded shapes
are dropped whole by `derive_reported_testimony`: 3,429 statements, more than
the `saw_player` channel the reduction does carry, are spoken in public,
rendered into every later listener's transcript, and then never enter any
listener's episodic memory. The reduction was written over the shapes that
existed in 2026-06 and has never been widened since; `WhereaboutsClaim` and
`SawMoveObservation` fall through both loops with no else-branch and no raise,
and `grep -rn "WhereaboutsClaim\|SawMoveObservation" --include="*.py" agents/
orchestrator/ | grep -v test` returns nothing — there is no second ingest path.
The second-order cost is arithmetic: `alibi_map` is fed only by `kind ==
"alibi"` (agents/memory/store.py:688-700), so the map an agent consults for
"where did they say they were" holds 706 of the 2,975 location accounts spoken
in that corpus — **23.7%** — and the channel the prompts ask for hardest is the
one memory keeps least. The verifier's two corrections bind this contract: the
gap is four shapes, not two (`found_body` 586 and `completed_task` 310 also fall
through, and stay out of scope here — see below), and a whereabouts is not
invisible, it reaches listeners as a degenerate single-tick self-alibi through
the SCALAR detector path (meetings/transcript.py:2291-2304), so the true claim
is the narrow one: it never becomes CONTENT.

The kill has no shape at all. Across the four committed sets (668 meetings,
3,602 turns, re-derived at HEAD) the turn schema's observation census is
`saw_player` 3,775, `whereabouts` 3,117, `saw_move` 1,657, `found_body` 833,
`saw_vent` 517, `completed_task` 421 — and zero of anything naming a witnessed
murder, because no such shape exists anywhere in the repo. A crewmate who
watched a kill holds the memory line
`[tick 11] You witnessed p-8 kill in ADMIN.` and, offered six shapes, files it
as the one that is role-proving: the verifier's independent scan found 5 spoken
`saw_vent` rows naming a subject who never vented anywhere in that game, and
**all 5 join that same speaker's own witnessed kill on killer + room + tick
exactly**. The verifier also corrected the filing twice, and both corrections
are load-bearing here. First, the denominator: 512 of 517 spoken vent rows name
a genuinely venting subject, so the fabrication class is 5, not 65. Second, the
damage: all 5 named a real impostor and all 5 meetings ejected that impostor,
and the structured channel never followed the fabrication — 448 `vent_sighting`
flags, 448 engine-backed, 0 unbacked. So this is a LEGIBILITY repair, not a
justice repair, and no surface in this task may claim otherwise: what is lost is
that the record says a vent happened where a murder was witnessed, and the
strongest testimony the game produces is destroyed in the transcript on its way
to the ballot.

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

Confessions are the third strand, and only their instrument is in scope. Two
impostors in the committed corpus narrate their own kill in player-visible text
("...immediately after I killed p-1 at tick 12..."), the text reaches every
later speaker and every ballot, and no shipped cell counts it: the ONLY
player-visible increment in the module is the partner net
(eval/deduction_metrics.py:2350-2351), so `player_visible_leak_turns` reads 0 on
every committed set — verified at HEAD — while `model_self_kill_disclosure_ballots`
reads 11 on samples/9p2i. A zero that means "we did not look" is the failure
this task fixes, and the fix carries the verifier's constraint: the raw net is
2/10 precise pooled and 2/4 within impostor speakers, so what ships is a
ROLE-SPLIT, explicitly labelled UPPER BOUND with its crew false-positive control
published beside it — the shape `model_machinery_vocabulary_ballots` already
uses in this module — never a bare substring count read as a leak rate. The
gameplay half of that finding (block or flag a confession at the chokepoint) is
NOT executed here: both confessors were ejected in the meeting they confessed
in, so the corpus does not show that confession is free, and re-pricing a
behaviour on 2 occurrences in 3,602 turns would be a balance change wearing an
instrument's clothes.

One discipline binds every number above. All of them are measured over the
baseline-7 committed bytes — canon by explicit owner override of a FINDING
verdict — and Task 21.15 replaces those bytes before this task lands. So no
Definition-of-done item pins a corpus count: the gates are fixtures, class
invariants and OFF-path byte identity, and the corpus reading of this lever is
the offline counterfactual's, published before any bar is written.

**Files in scope:**
- meetings/constants.py; (the lever's `ENV_TESTIMONY_SHAPES` + `testimony_shapes_enabled(env)` resolver — homed in the stdlib-only leaf because BOTH sides need it and `agents/` may not import `meetings.manager`)
- meetings/schemas.py; (`SawKillObservation` + its union member, added unconditionally on the parse side; `ReportedStatementKind` gains `whereabouts`, `saw_move`, `saw_kill`; the two silent docstrings state what the reduction now does)
- meetings/manager.py; (`derive_reported_testimony` reads the lever ONCE and emits the three new kinds under it; OFF returns the current tuple byte-for-byte)
- agents/memory/store.py; (`absorb_reported_testimony`: a `whereabouts` feeds `record_alibi` as an `alibi` does; `_render_reported_testimony` gains one body per new kind)
- agents/strategic/prompts/loader.py; (two variant template constants and the lever-resolved routing, copying the 18.10 shape at :679-687 and :944-971)
- agents/strategic/prompts/qwen3_6_27b/crewmate_report_testimony_shapes.j2; (NEW — the crew opener variant: the shape menu gains `saw_kill`, one instruction line pairs it with the vent mandate)
- agents/strategic/prompts/qwen3_6_27b/accusation_round_testimony_shapes.j2; (NEW — the turn variant, crew branch only; the impostor branch is byte-identical to the default)
- orchestrator/game.py; (`TESTIMONY_SHAPES_PROMPT_VERSION_SETS` and the `prompt_versions_for_set` arm, so variant bytes never wear a default stamp)
- eval/deduction_metrics.py; (the player-visible confession cells, record-free and unconditional, plus the one-line correction of the adjacent false control claim)
- tests/meetings/test_reported_testimony_derive.py; (OFF identity, ON emission per kind, the destination-only rule, determinism)
- tests/agents/test_reported_testimony.py; (ingest + render + `alibi_map` under the lever, and the own-statement/roster guards still holding)
- tests/meetings/test_schemas.py; (the new observation parses, round-trips, and rejects a malformed payload)
- tests/agents/test_prompt_loader.py; (routing: OFF binds the default filenames, ON binds the variants, ON with a set that has no variant fails loud)
- tests/agents/test_bespoke_prompt_sets.py; (the variant bodies differ from the default bodies ONLY in the two named regions)
- tests/eval/test_deduction_metrics.py; (the new cells, their crew control, and the exclusion list's planted case)
- orchestrator/replay.py; (register `testimony_shapes` in `_TOGGLEABLE_LEVER_RESOLVERS`, newest last — this lever registers ITSELF, the same as its two siblings)
- .env.example; (the new toggle's commented bare default and its paragraph, in the voice of the two entries above it)
- tests/orchestrator/test_replay.py; (the stamp key appears, a bare env stamps it False, and a recording predating the key still reads False)

**Files NOT in scope:**
- `SUBSTRATE_FLAG_KEYS`' ordering convention and the retired half of the registry (this task appends ONE live-toggle entry; the retired block is 21.24's on ADOPTED and no key changes index here)
- observation/service.py, agents/perception.py (naming the victim in the witnessed-kill line needs the perception packet widened; that is a firewall-crossing entitlement change and is deliberately not this task's — the shape carries killer/room/tick, which is exactly what the memory line already holds)
- meetings/transcript.py (this task mints NO contradiction flag and changes NO band; a spoken `saw_kill` is content, and the detector is untouched)
- agents/memory/beliefs.py (`record_alibi` is CALLED with a new source, never redefined; no suspicion delta moves)
- agents/strategic/prompts/qwen3_6_27b/impostor_report.j2, vote_ballot.j2 and the two `*_roll_call.j2` variants (the impostor never holds a speakable witnessed-kill row; no default template body moves in this task)
- the other six prompt sets under agents/strategic/prompts/ (the variants are authored only for the locked set, exactly as the 18.10 variants are)
- eval/evidence_honesty.py, eval/meeting_quality.py, eval/vote_correctness.py (instruments that CONSUME cells; this task must not redefine one — if a needed cell is missing, say so in the PR)
- replays/ (no committed byte moves here; the counterfactual reads them and writes nothing)

**Definition of done:**
- [ ] `meetings.constants.testimony_shapes_enabled(env)` follows the standing resolver signature — default OFF on unset/empty/unrecognised, `1/true/yes/on` case-insensitively, `env` threaded so tests never mutate `os.environ` — and `meetings/constants.py` stays a stdlib-only leaf (`os` and `collections.abc` only), with its module docstring stating why a resolver is homed there: `agents/strategic/prompts/loader.py` and `meetings/manager.py` must read ONE lever, and the `agents ↛ meetings.manager` import contract forbids the obvious home.
- [ ] OFF-path identity is proved before anything else: with the lever unset, `derive_reported_testimony` returns a tuple equal element-for-element to HEAD's over every committed meeting in the four sets, `tests/meetings/test_prompt_byte_golden.py` is green, and `bash scripts/verify_samples.sh` reports 100/100 — the three proofs that no rendered or recorded byte moved.
- [ ] Under the lever, `derive_reported_testimony` emits a `whereabouts` statement per `WhereaboutsClaim` with `subject == turn.speaker` and `from_tick == to_tick == observation.tick`, and a `saw_move` statement per `SawMoveObservation` carrying the DESTINATION placement only (`room == observation.to_room`, `from_tick == to_tick == observation.tick`) — the origin half is not carried, and the reduction's docstring states the shape's own reason (meetings/schemas.py:154-181: a second placement per shape re-opens the off-by-one class the shape closes).
- [ ] `tests/meetings/test_reported_testimony_derive.py` pins ON/OFF for each new kind on the same fixture transcript, pins that repeated calls return equal tuples (the determinism the module promises), and pins the sort key still totally orders a mixed statement set — the reduction stays a pure, replay-deterministic function of the recorded `MeetingResult` with the lever as its only other input.
- [ ] `absorb_reported_testimony` folds a `whereabouts` statement into `alibi_map` through `BeliefState.record_alibi` exactly as an `alibi` does, with the existing guards unchanged and re-pinned: an own statement is skipped, a non-roster speaker or subject is skipped, and a self-placement about the recipient never materialises a SELF belief row. `tests/agents/test_reported_testimony.py` carries the perturbation — the same fixture with the lever OFF leaves `alibi_map` exactly as HEAD leaves it.
- [ ] `_render_reported_testimony` gains one body per new kind inside the existing `[meeting n] CLAIM by X (unverified):` frame, and a malformed payload for any of the three still renders nothing (the module's defensive `.get` convention, pinned by a test that plants a row with a missing room).
- [ ] `meetings.schemas.SawKillObservation` carries `{type: "saw_kill", tick, subject, room}` — no victim field — is a member of `ObservationClaim`, and is accepted by the turn parser UNCONDITIONALLY (the `SawMoveObservation` precedent: parsing never depends on which templates offer a shape). Its docstring states in one line that it mints no contradiction flag and no band, and that the grounded role-proof channel is `saw_vent`'s alone.
- [ ] The two variant templates are authored FROM the current default bodies of the same set, and `tests/agents/test_bespoke_prompt_sets.py` pins that the only differences are the shape-menu line and the one paired instruction line — a failable gate against the variant silently missing a later default fix. The `accusation_round` variant's impostor-facing branch renders byte-identically to the default's.
- [ ] Routing is bound once, at construction, on both halves: `build_prompt_renderers` binds the variant filenames when the lever reads ON and the exact default filenames when it reads OFF, and `prompt_versions_for_set` serves `TESTIMONY_SHAPES_PROMPT_VERSION_SETS` under the same read — so a recording's rendered bytes and its recorded stamps can never come from two different routing decisions (audits/audit-phase-17-absence-gate.md Ruling 3(d)). Lever ON with a set that carries no variant raises `ValueError` at construction; lever ON together with ANY other version-overlay lever — the 18.10 impostor-answer arm or either sibling Wave-2 overlay — raises rather than silently picking one registry, with a message naming the variables involved.
- [ ] The variant stamps name the variant FILES on their own `v1` lineage (`crewmate_report_testimony_shapes.qwen3_6_27b.v1`, `accusation_round_testimony_shapes.qwen3_6_27b.v1`), the other two keys inherit the default registry's values, and `tests/agents/test_prompt_loader.py` pins that no variant body can ever share a stamp with any default body of that set, past or future.
- [ ] `eval/deduction_metrics.py` runs the self-kill and role nets over the PLAYER-VISIBLE surface — `turn.free_text` plus each claim's `reason` and `evidence`, since the turn render puts the reason on the table — and publishes them as role-split cells beside `player_visible_leak_turns`, with the impostor-side cell documented as an explicit UPPER BOUND and the crew-side cell as its false-positive control. A documented exclusion list drops the quotation/conditional forms the verifier measured as the noise ("how do you know I killed", "if I killed", "you claim I killed"), and a planted case proves the exclusion bites in both directions.
- [ ] The adjacent claim in the same docstring block is corrected in the same edit: `crew_omniscient_control_ballots` is NOT "0 on every committed set" — re-derived at HEAD it reads 1 on both 9p2i sets and 0 on both 4p1i sets. The corrected sentence names the control's actual reading and the command that recomputes it (craft rule 5).
- [ ] The lever REGISTERS itself: `testimony_shapes` is appended to `orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS` bound to `meetings.constants.testimony_shapes_enabled` (no local mirror), so `SUBSTRATE_FLAG_KEYS` grows by a pure append at the live-toggle end and every already-recorded key keeps its index. `tests/orchestrator/test_replay.py` pins that a bare env stamps the key `False` and that a stamp recorded before the key existed still reads `False` through the missing-key rule at `orchestrator/replay.py:562-564`. Registering here rather than in a later collecting task is what lets the offline counterfactual price a three-lever slate: it reads the live registry and refuses before printing if a priced lever is absent.
- [ ] The re-derivation seam is closed by that registration and the closure is pinned, not promised: a recording whose `game_over` stamp carries `testimony_shapes: False` loaded with the lever ON is REFUSED by `api/replay_loader.py`'s substrate check rather than silently re-derived through `derive_reported_testimony`, and the test asserts the refusal names the diverging key. The PR states which consumers re-derive at load time and that all of them now sit behind that guard.
- [ ] `.env.example` documents `AILIBI_TESTIMONY_SHAPES` as a commented bare default in the voice of the two Wave-2 entries above it, including the warning that flipping it for a serving or verify run against committed bytes produces a substrate mismatch; `uv run python scripts/check_doc_facts.py` is green, since `check_lever_registry` couples that file to the registry.
- [ ] `tests/meetings/test_lever_registry.py`'s resolver sweep is re-run and still reports zero accept-and-ignore resolvers with the third Wave-2 key present; the count assertions its siblings generalised are updated to name all live resolvers rather than a number typed in prose.
- [ ] No cell, count or threshold in this task is pinned to a committed-corpus number: every gate is a fixture or a class invariant, because the bytes those numbers describe are replaced by the re-record this task depends on. The PR states this in one line.
- [ ] The PR quotes a lever-ON re-derivation over the committed bytes for orientation only — reported rows added per meeting by each arm, and the alibi-map coverage before and after — labelled as an OFFLINE re-derivation of superseded bytes, with no bar, no verdict and no claim about what the record will show.
- [ ] The blast radius is stated in the PR from a fresh grep of every `derive_reported_testimony` / `absorb_reported_testimony` consumer: orchestrator/game.py:2363, api/replay_loader.py:1378, eval/off_menu.py:509, eval/funnel.py, eval/evidence_honesty.py:1321, scripts/counterfactual_phase20.py:527 — naming which of them read the ambient environment and which are handed one.
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
`ObservationClaim` and nothing else. Then the two variants. Copy each default
body verbatim, add ONE menu line —
`{"type": "saw_kill", "tick": <int>, "subject": "<player id>", "room": "<room
id>"} — only for a kill you watched happen, copied exactly from your memory
line; name the killer, not the victim.` — and ONE instruction line beside the
existing vent mandate telling the reader to use it instead of `saw_vent` for a
witnessed murder. Do not touch the impostor branch of the accusation-round
body. The diff-shape test in `tests/agents/test_bespoke_prompt_sets.py` is what
stops the copies rotting: assert the variant equals the default with exactly
those insertions, so a later default fix that misses the variant turns it red.

BLOCK 5 — routing and stamps, the pairing that must not split. Add the two
template constants beside `IMPOSTOR_REPORT_ROLL_CALL_TEMPLATE`
(loader.py:316-317), resolve the lever once in `build_prompt_renderers` exactly
where the 18.10 lever is resolved (:952-953), and pre-check
`environment.get_template(name)` for both variants so an unauthored set fails
at construction, never at render. Then
`TESTIMONY_SHAPES_PROMPT_VERSION_SETS` in `orchestrator/game.py` beside
`IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, registering into the overlay seam
Task 21.18 built in `prompt_versions_for_set` rather than forking it, and
leaving the default `PROMPT_VERSION_SETS` entry alone — it moved once this
phase, at 21.1's v5, and no lever re-bumps it. FOUR levers now feed one
lookup (the 18.10 arm plus the three Wave-2 overlays): decide every
more-than-one-ON case explicitly and raise, with a message naming the
variables involved — a silent precedence rule here is the
render-one-stamp-another failure that docstring already warns about.

BLOCK 6 — the instrument (A-16), record-free and independent of the lever. The
increment at :2350-2351 stays; add the role split beside it inside the same
turn loop, which already holds `role = roles[turn.speaker]`. Build the visible
text once per turn — `free_text` plus each claim's `reason` and `evidence` —
and run the self-kill and role nets over it. Two new int fields on
`ScaffoldLeakageCells` with their `_require_non_negative` entries, documented in
the module docstring's leakage block: the impostor cell as an UPPER BOUND (the
module's own precedent for a net it cannot fully disambiguate is
`model_machinery_vocabulary_ballots`, :274-277) and the crew cell as its control.
The exclusion list is a module constant with a docstring stating what it drops
and why, and its planted case asserts both directions — an excluded quotation
does not count, and a bare first-person admission does. While in that
docstring, fix the false control sentence at :257-258.

BLOCK 7 — registration, last and in one commit with the resolver. Append
`("testimony_shapes", testimony_shapes_enabled)` to `_TOGGLEABLE_LEVER_RESOLVERS`
(orchestrator/replay.py:568), importing the resolver from `meetings.constants` —
that module is a stdlib-only leaf, so there is no import-contract obstacle and no
local mirror is needed. Two sibling levers registered ahead of you, so read the
tuple at HEAD rather than at this contract's line number, and append at the live
end so no already-recorded key moves index. Then `.env.example` in the voice of
the two entries above yours, and the `tests/orchestrator/test_replay.py` pair
(bare env stamps False; a pre-key recording reads False). This is what makes the
downstream counterfactual able to price a three-lever slate — it reads the live
registry and refuses before printing if a priced lever is missing.

BLOCK 8 — before pushing. Run the byte-golden and `verify_samples.sh` with a
clean environment FIRST; if either moves with the lever unset, the OFF path is
not identical and nothing else matters. Then run the ON path over the committed
bytes to produce the PR's orientation numbers, toggling through the resolver's
`env` argument and never through `os.environ`.

## Public types this task introduces
- `meetings.constants.ENV_TESTIMONY_SHAPES`
- `meetings.constants.testimony_shapes_enabled`
- `meetings.schemas.SawKillObservation`
- `agents.strategic.prompts.loader.CREWMATE_REPORT_TESTIMONY_SHAPES_TEMPLATE`
- `agents.strategic.prompts.loader.ACCUSATION_ROUND_TESTIMONY_SHAPES_TEMPLATE`
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

Risk 3 — variant drift. Two copied template bodies are two future places for a
default fix to miss, and this phase's own Wave-1 work rewrites those defaults.
The diff-shape gate in BLOCK 4 is the only thing that makes the copies safe;
it must assert the variant EQUALS the default plus the named insertions, not
merely that both contain the new lines. A gate that cannot fail is prose.

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
bound over a net measured at 2/10 precision pooled, on a base of 2 genuine
confessions in 3,602 turns. It must ship labelled, role-split, with its control
beside it, and no downstream doc may quote the impostor cell alone as a leak
count. This is the same failure the module already documents for its vent
exclusion at :262-268 — the precedent to follow, not to re-litigate.

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
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import eval.replay_walk.ReplayWalkConfig"`
- `uv run python -c "import engine.tick"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.watchability.SupplyFloors"`
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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing B-7 [CONFIRMED, P1] — audits/review-2026-08-26/B/collated-findings.md §B-7 (the ingest half: the reduction carries five kinds, and the two largest spoken shapes fall through it silently; the verifier's own corpus census plus its two corrections — `CompletedTaskObservation` and `FoundBodyObservation` fall through as well, so the gap is FOUR shapes not two, and whereabouts DO reach listeners through the SCALAR channel, so the precise claim is "never entering episodic memory or the alibi_map"); A-22 [ADJUSTED, P3] — audits/review-2026-08-26/A/collated-findings.md §A-22 (the speakable-kill half: the verifier's 5/5 exact killer+room+tick join, its correction of the "65 ungrounded" denominator, and its bounding of the damage to LEGIBILITY — all 5 fabricated rows named a real impostor, all 5 meetings ejected that impostor, and the structured channel stayed clean at 448 engine-backed `vent_sighting` flags with 0 unbacked); A-16 [ADJUSTED, P2] — audits/review-2026-08-26/A/collated-findings.md §A-16 (the instrument half only: the gameplay half of that finding is NOT executed here, and the verifier's precision measurement binds the cell's shape); tasks/phase-20.md:65-67 (the Phase-20 ruling that declared `saw_kill` OUT and routed it to a chartered balance wave — this contract is the charter, as a default-OFF lever with an offline counterfactual and a pre-registration ahead of it, and the arm is an owner decision point). Anchors re-verified at HEAD `d8ec0a1c` by the drafting session: meetings/schemas.py:539-541 (`ReportedStatementKind`, the closed FIVE), :95-116 (`SawVentObservation`, whose docstring records the 20.29 precedent of widening the kind set when a new sayable shape lands), :124-148 (`WhereaboutsClaim` — silent about the reduction), :154-181 (`SawMoveObservation` — its "EXACTLY ONE placement, the destination" ruling is the rule this task's reduction copies; its "the turn schema accepts the shape unconditionally, so parsing never depends on which templates offer it" is the parse/offer split this task reuses), :185-193 (the `ObservationClaim` discriminated union), :552-585 (`ReportedStatement`, whose optional fields are populated per kind); meetings/manager.py:3768-3876 (`derive_reported_testimony`: the observation loop at :3822-3844 handles only `SawPlayerObservation` and `SawVentObservation`, the claim loop at :3846-3875 only the three claims, no else-branch and no raise; the sorted return at :3876); agents/memory/store.py:575-700 (`absorb_reported_testimony`; the `alibi_map` write at :688-700 is gated on `kind == "alibi"`), :1593-1597 + :1921-1983 (`_render_reported_testimony`, the five per-kind bodies and the `[meeting n] CLAIM by X (unverified):` frame), :1817-1823 (the witnessed-kill memory line — killer, room and tick, no victim), :1017-1081 (`_is_kill_window_sighting` / `_sighting_is_suppressed`: an impostor's sighting of a teammate with `action == "kill"` is dropped before it is ever rendered); meetings/transcript.py:2291-2304 (a whereabouts is indexed as a degenerate single-tick self-alibi — the scalar path the verifier names) and :2512-2531 (a grounded `saw_move` becomes the destination placement); agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:115 + :125-131 and accusation_round.j2:243-249 (the six-shape menus and the vent-first mandate the kill line parallels); agents/strategic/prompts/loader.py:306-317 + :679-687 + :923-971 (the Task-18.10 variant-routing precedent) and orchestrator/game.py:349-421 + :424-470 (`PROMPT_VERSION_SETS`, `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS`, `prompt_versions_for_set` — the registry that keeps variant bytes off default stamps, audits/audit-phase-17-absence-gate.md Ruling 3(d)); orchestrator/game.py:2357-2380 and api/replay_loader.py:1369-1388 (the two production folds of the derivation); meetings/constants.py:1-20 (the stdlib-only leaf and its own constant-homing rationale); eval/deduction_metrics.py:250-268 + :474-504 + :1550-1568 + :2350-2351 (the nets, their documented scope, and the ONE player-visible increment).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
