# Agent Prompt — 20.29 Meetings leave a record: outcomes, revealed roles and testimony as content in memory

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.29 — Meetings leave a record: outcomes, revealed roles and testimony as content in memory, anchored to G-35 and G-23 (audits/review-2026-08-19/A/collated-findings.md §G-35, §G-23); R4 and R5 and D5 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R4, §R5, §D5); V1 and M1 (audits/review-2026-08-19/A/ideas-among-us-veteran.md §V1, §1 row M1); idea #9 (audits/review-2026-08-19/A/ideas-game-designer.md §9); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §3; the roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §Wave 2 row 2.10. Re-verified at HEAD 1ceab2c4: agents/memory/working.py:57-73 (`MeetingOutcome`, exactly `end_tick` + `ejected_id`), :133-185 (`MeetingHistory`, `record` at :176); agents/memory/store.py:685-711 (`record_meeting_outcome`, "inert to `render_for_prompt` … no prompt-byte impact anywhere"), :579-682 (`absorb_reported_testimony`), :1750-1804 (`_render_reported_testimony`, the `CLAIM by X (unverified):` prefix at :1777, `accused {subject}` at :1792), :86 (`_SALIENCE_REPORTED_TESTIMONY = 25`), :2070-2163 (`_assemble_view`, the fixed/elastic split); orchestrator/game.py:674-715 (the `MeetingPacingAgent` protocol), :2020-2035 (the belief fold then the pacing fold), :2328-2345 (the testimony fan-out), :2392-2432 (`_notify_meeting_concluded`), :3188-3228 (`TacticalAgent.note_meeting_concluded`); meetings/manager.py:3597 (`MeetingBeliefEvidence`, the sibling reduction DTO), :3913-4004 (`derive_reported_testimony`); meetings/schemas.py:537-539 (`ReportedStatementKind`, the closed four), :95-119 (`SawVentObservation`, ":112-113 deliberately NOT reduced to a `ReportedStatement`"), :721 (`MeetingResult.ejected_player_id`); eval/leak_scan.py:68-80 (the forbidden role-value constants and their single allowed path), :185-210 (`_assert_no_role_bearing_values`), :848-920 (`assert_packet_is_leak_clean`, whose signature 20.8 changed to `(packet, context: PacketContext)`); tests/agents/test_memory_meeting_history.py:249-260 (the field-set provenance pin), :301-308 (the render-inertness pin); DESIGN.md:463 §4.7, :702 §6.6; .importlinter (agents must not import engine, agents must not import meetings.manager). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-meeting-outcome-memory`
**Depends on:** 20.24 — the self-location trail lands its own non-elastic block in the same render assembly first, so this block stacks on a settled layout instead of racing it; 20.8 — the entitlement-checking leak scanner must exist before this task widens it with a role-disclosure allowance, or the allowance is written against a scanner that cannot check entitlement at all; 20.28 — the structured turn annotations settle the manager's public reduction surface before an additive outcome payload is added beside it.
**Section refs:** G-35 and G-23 (audits/review-2026-08-19/A/collated-findings.md §G-35, §G-23); R4 and R5 and D5 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R4, §R5, §D5); V1 and M1 (audits/review-2026-08-19/A/ideas-among-us-veteran.md §V1, §1 row M1); idea #9 (audits/review-2026-08-19/A/ideas-game-designer.md §9); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §3; the roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §Wave 2 row 2.10. Re-verified at HEAD 1ceab2c4: agents/memory/working.py:57-73 (`MeetingOutcome`, exactly `end_tick` + `ejected_id`), :133-185 (`MeetingHistory`, `record` at :176); agents/memory/store.py:685-711 (`record_meeting_outcome`, "inert to `render_for_prompt` … no prompt-byte impact anywhere"), :579-682 (`absorb_reported_testimony`), :1750-1804 (`_render_reported_testimony`, the `CLAIM by X (unverified):` prefix at :1777, `accused {subject}` at :1792), :86 (`_SALIENCE_REPORTED_TESTIMONY = 25`), :2070-2163 (`_assemble_view`, the fixed/elastic split); orchestrator/game.py:674-715 (the `MeetingPacingAgent` protocol), :2020-2035 (the belief fold then the pacing fold), :2328-2345 (the testimony fan-out), :2392-2432 (`_notify_meeting_concluded`), :3188-3228 (`TacticalAgent.note_meeting_concluded`); meetings/manager.py:3597 (`MeetingBeliefEvidence`, the sibling reduction DTO), :3913-4004 (`derive_reported_testimony`); meetings/schemas.py:537-539 (`ReportedStatementKind`, the closed four), :95-119 (`SawVentObservation`, ":112-113 deliberately NOT reduced to a `ReportedStatement`"), :721 (`MeetingResult.ejected_player_id`); eval/leak_scan.py:68-80 (the forbidden role-value constants and their single allowed path), :185-210 (`_assert_no_role_bearing_values`), :848-920 (`assert_packet_is_leak_clean`, whose signature 20.8 changed to `(packet, context: PacketContext)`); tests/agents/test_memory_meeting_history.py:249-260 (the field-set provenance pin), :301-308 (the render-inertness pin); DESIGN.md:463 §4.7, :702 §6.6; .importlinter (agents must not import engine, agents must not import meetings.manager)
**Complexity:** Integration
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/agents tests/orchestrator tests/observation eval/leak_test.py -q` green; a fake-provider 9p2i game with `AILIBI_MEETING_OUTCOME_MEMORY=1` renders the meetings block in every living agent's memory after its first meeting, pasted into the PR Summary alongside the committed-bytes counterfactual census.

Nothing survives a meeting. Across the 300 committed baseline-6 games the review grepped every
rendered memory for any trace of an ejection outcome — "ejected", "voted out", "was not",
"remain" — and found 0 of 3,934, including the 1,799 that were rendered *after* an ejection had
already happened (A/ideas-among-us-veteran.md §1 row M1, all four sets, VERIFIED); the same
census over the prompt bytes reads 0 of 7,458 meeting LLM calls carrying any record of a prior
ejection or its revealed role (A/ideas-multi-agent-researcher.md §D5). This is not a missing
channel — the channel was built and left inert. `MeetingOutcome` at
agents/memory/working.py:57-73 already carries the concluded meeting's public result,
`record_meeting_outcome` at agents/memory/store.py:685-711 already folds it per living agent
off the `note_meeting_concluded` hook, and its own docstring states the terminal fact: it "is
consumed ONLY by the v3 tactical feature encoder's meeting-history channel and is inert to
`render_for_prompt` … it carries no prompt-byte impact anywhere". Three survived meetings
currently reach the model as three floats in a feature vector no LLM ever reads.

The cost is measured, and it is the corpus's least watchable behaviour. With no record that a
case is closed, the crew re-prosecutes corpses: 68 `saw_vent` observations in samples/9p2i and
232 in ml/9p2i name a player already dead or ejected, and 5.0–5.5% of all turns have their
accusation struck for naming an out-of-game player (A/collated-findings.md §G-23). Seed 2
spends meeting 2 *and* meeting 3 re-arguing p-4, ejected at meeting 1; seeds 13 and 15 spend
their last three-alive meeting entirely on an already-ejected impostor; in seed 6 the crew end
up branding their own two vent witnesses liars (A/ideas-among-us-veteran.md §V1;
A/ideas-game-designer.md §9). In the real game "X was not the Impostor. 1 Impostor remains." is
the sentence the whole mid- and endgame is built on: without it there is no cleared player, no
parity count, and no reason for a skip to feel expensive.

The second half is the testimony content. `_render_reported_testimony`
(agents/memory/store.py:1750-1804) reduces an accusation to `accused {subject}` at :1792, and
`SawVentObservation` is deliberately excluded from the reduction altogether —
meetings/schemas.py:112-113 says so in as many words, because the Task 13.5.2 scope was
owner-locked to four kinds. The consequence is exactly inverted from the design intent: the
game's one 100%-precise signal is destroyed on the way into memory (a witnessed vent becomes
`CLAIM by p-8 (unverified): accused p-4`) while the impostor's fabricated *sighting* keeps its
room and its tick. Testimony is 16.8–17.2% of all rendered lines, and its only mechanical
effect on belief is a flat asserted-alibi discount that is *larger* for the liar — −0.086 for
an impostor subject against −0.038 for a crew subject in corpus9p2i
(A/s4-info-economy-beliefs.md §3). Restoring the vent's content costs one statement kind and
one render branch.

The disclosure is deliberate and it is narrow. Confirm-ejects is the Among Us rule, and the
revealed role of an EJECTED player is public at the table on exactly the same footing as
`dead_ids` and the announced tally — the footing on which `ejected_id` already crosses into
memory (DESIGN.md §4.7; the 18.22 argument recorded at orchestrator/game.py:2392-2414). A
player killed rather than ejected reveals nothing, and no living player's role is ever
disclosed. Because `agents/` may not import `engine` (.importlinter), the translation happens
where it already belongs: the orchestrator, which holds post-meeting `WorldState`, reads the
ejected player's role and passes it through the existing hook; the manager contributes only the
public tally, derived from the recorded ballots the way `derive_reported_testimony` and
`extract_belief_evidence` already derive their reductions. That split is what makes the
allowance auditable rather than a hole, and 20.8's entitlement-checking scanner is extended to
assert it in both directions.

Everything ships behind `AILIBI_MEETING_OUTCOME_MEMORY`, default OFF: OFF-path render bytes are
byte-identical over all 300 committed games, so `tests/meetings/test_prompt_byte_golden.py` and
`bash scripts/verify_samples.sh` stay green and the Phase-20 gate slate is undisturbed until
the adopting record flips it. The honest price is quoted in advance from the committed bytes
rather than promised: how many renders would gain a prior-ejection line, how many of those
would tell the crew it had ejected a crewmate, and how many `saw_vent` rows name a player the
block would already have closed out.

**Files in scope:**
- agents/memory/store.py; (the lever, its resolver and its env key: a non-elastic `## Meetings so far:` block rendered above observations — `Meeting 1 (tick 14): p-4 EJECTED 7-1 — p-4 was an IMPOSTOR. 1 impostor remains.` / `Meeting 2 (tick 27): no ejection (6 skip). 1 impostor remains.` — plus reported testimony kept as CONTENT with its speaker, its meeting index and the restored vent body; OFF-path bytes identical)
- agents/memory/working.py; (`MeetingOutcome` gains optional revealed-role and tally fields, all defaulting to None so every existing construction and the v3 three-scalar channel are untouched; `impostors_remaining` derived on `MeetingHistory`, engine-free and pure-Python as the module's own import pin requires)
- orchestrator/game.py; (after `apply_meeting_result`, `_notify_meeting_concluded` passes the ejected player's role read off the post-meeting state plus the public tally and the roster impostor count into the memory fold — the orchestrator is the only module allowed to translate engine roles; the `MeetingPacingAgent` protocol and `TacticalAgent.note_meeting_concluded` widen additively with None defaults)
- meetings/manager.py; (the additive public outcome payload the orchestrator hands to the fold: a pure, engine-free tally reduction over the recorded ballots, the sibling of `derive_reported_testimony`; plus the reduction of a spoken vent sighting into reported testimony)
- eval/leak_scan.py; (a memory-render scanner with one explicit, named allowance: a role word may name an EJECTED player only in a render taken at or after that player's ejection tick, and the agent's own `## Your role:` line; every other role disclosure fails)
- tests/agents/test_memory_meeting_history.py; (OFF byte-identity; ON: the block renders, the impostors-remaining arithmetic, a role never appears before its ejection tick, and the restated field-set provenance pin)
- tests/agents/test_reported_testimony.py; (the content lines: the vent body survives, the speaker and meeting index render, the OFF path is byte-identical)
- tests/orchestrator/test_meeting_integration.py; (the payload: the hook carries the revealed role and the tally end to end, and carries nothing for a kill victim)
- eval/leak_test.py; (the planted-leak legs: a pre-ejection role disclosure FAILS the scanner)
- tests/observation/test_leak_property.py; (the other direction: with the lever ON the observation packets are unchanged — the disclosure never travels through perception)
- meetings/schemas.py; (a ReportedStatementKind member for the spoken vent; the SawVentObservation docstring correction)

Recorded deviation at merge (PR #381, orchestrator-ratified): four files outside scope forward the widened note_meeting_concluded keywords verbatim — training/env.py:466, training/crew/scorer.py:814, agents/tactical/learned/factory.py:293 + :388, tests/training/test_learned_factory_acceptance.py:769 — because runtime_checkable capability gates check attribute presence, not signature, so the wrapper implementations had to accept what the orchestrator now passes. A prose record, not scope entries.

**Files NOT in scope:**
- engine/ (no engine change — the orchestrator already holds the post-meeting state and its roles)
- agents/strategic/prompts/ (no template may move in this task; the dead-subject exemption to the speak-your-vent-first mandate is the prompt-set bump's, and it is the only task in the phase permitted to touch a `.j2`)
- agents/tactical/ (the FSM's dead-set fold is the impostor-mover task)
- orchestrator/replay.py (the substrate stamp registration is Task 20.33 — this task ships the resolver and the env key and registers nothing; a bare-environment snapshot is unchanged here by construction)
- agents/tactical/features.py and tests/training/test_bakeoff_harness.py (the v3 `meeting_history_scalars` channel stays exactly three floats — the widened dataclass must not move a single feature byte, which is a DoD assertion, not an edit)
- api/replay_loader.py and tests/meetings/test_prompt_byte_golden.py (both reconstruct memories without the outcome fold; under the default OFF lever their bytes cannot move, and ON-path reconstruction parity is carried by the stamp registration and the adopting record — see Integration risk)
- the belief-line alibi suffix and `record_alibi` de-duplication (register id C-3 class, a separate P2 living in the same file; touching it here would move OFF-path belief bytes)
- DESIGN.md (§6.6's prose stays true while the lever is OFF; the adopting record's sweep restates it)

**Definition of done:**
- [ ] `agents.memory.store.meeting_outcome_memory_enabled(env)` reads `AILIBI_MEETING_OUTCOME_MEMORY`, accepts `1/true/yes/on` case-insensitively, defaults False on unset/empty/unrecognised, and takes `env` so tests toggle without mutating `os.environ` — mirroring the resolver at agents/strategic/prompts/loader.py:327 (and the in-file sibling 20.24 landed, `self_location_trail_enabled` at agents/memory/store.py:290). `render_for_prompt` reads it once and threads the boolean down.
- [ ] OFF-path byte-identity: `tests/agents/test_memory_meeting_history.py` pins that a memory populated with outcomes carrying roles and tallies renders byte-identically to the same memory without them, and `bash scripts/verify_samples.sh` plus `uv run pytest tests/meetings/test_prompt_byte_golden.py` stay green over all 300 committed games.
- [ ] ON-path render: every post-meeting render carries the `## Meetings so far:` block as a non-elastic block placed above the observations block, one line per concluded meeting, naming the meeting index, the resume tick, the ejection or the skip with its tally, the revealed role of the ejected player, and the impostors-remaining count — pinned line-for-line in `tests/agents/test_memory_meeting_history.py` for an eject-an-impostor, an eject-a-crewmate and a skip.
- [ ] The impostors-remaining arithmetic is derived, not asserted: it equals the roster impostor count minus the number of recorded outcomes whose revealed role is IMPOSTOR, is never decremented by a kill, and is pinned across a two-impostor game where the first ejection is wrong and the second is right.
- [ ] ON-path testimony content: a spoken vent sighting reaches memory as content — `[tick 15] [meeting 1] CLAIM by p-8 (unverified): saw p-4 VENT in ENGINEERING @ tick 11.` — with the load-bearing `CLAIM by X (unverified):` frame preserved verbatim, and every reported line names the meeting it was spoken at; pinned in `tests/agents/test_reported_testimony.py`, with the OFF path byte-identical to HEAD in the same file.
- [ ] The widened `MeetingOutcome` field set is re-pinned as a provenance assertion, not merely updated: `tests/agents/test_memory_meeting_history.py`'s field-set test states the new exact tuple and asserts each added field is a fact announced at the table, and `tests/agents/test_memory_meeting_history.py`'s working-module import pin still shows no `engine`, numpy or torch import.
- [ ] The v3 encoder is untouched: `TacticalFeatureEncoder.encode` over a memory whose outcomes carry roles and tallies is byte-identical to the same memory without them, and the `meeting_history_scalars` segment is still three floats — asserted in `tests/agents/test_memory_meeting_history.py`.
- [ ] The orchestrator payload: `tests/orchestrator/test_meeting_integration.py` drives a real meeting to an ejection and asserts every living agent's memory holds the ejected player's true role and the true tally, that a player killed rather than ejected contributes no role anywhere in any agent's memory, and that an agent that died before the meeting receives nothing.
- [ ] The leak allowance is narrow and asserted in both directions: `eval/leak_scan.py`'s memory-render scanner passes a render taken after an ejection that names the ejected player's role, and FAILS on the same disclosure taken before the ejection tick, on a living player's role, and on a kill victim's role — the failing legs planted in `eval/leak_test.py`, and `tests/observation/test_leak_property.py` asserting that turning the lever ON changes no observation packet byte.
- [ ] The §6.6 render contract in `render_for_prompt`'s docstring documents the block: its position in the non-elastic set, its line grammar, and the entitlement rule that makes the role disclosure legal.
- [ ] The committed-bytes counterfactual is pinned and quoted in the PR Summary: over all four committed sets, the count of rendered memories that would now carry at least one prior-ejection line (review-measured 1,799 of 3,934 over the committed baseline-6 bytes; re-derived per set here), that count split by whether the revealed role is IMPOSTOR or CREWMATE, and the count of `saw_vent` observations naming an already-ejected player (review-measured 68 in samples/9p2i and 232 in ml/9p2i) as the re-litigation denominator the record is judged against.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Illustrative, not exhaustive — the anchors are re-verified at HEAD, the shapes are yours to
settle.

Step 1 — blast-radius grep before anything moves. `record_meeting_outcome`, `MeetingOutcome`
and `meeting_history` reach agents/memory/working.py, agents/memory/store.py,
agents/tactical/features.py, orchestrator/game.py, tests/agents/test_memory_meeting_history.py
and tests/training/test_bakeoff_harness.py; the `note_meeting_concluded` hook additionally has
protocol fakes in tests/training/test_crew_scorer.py,
tests/training/test_learned_factory_acceptance.py and tests/training/test_surrogate_runner.py,
which is why the widened parameters must be keyword-only with None defaults. Note that
`meetings.schemas.MeetingOutcome` is a DIFFERENT symbol (a `Literal["EJECTED", "SKIPPED"]`
alias at meetings/schemas.py:674) imported by meetings/voting.py, meetings/manager.py,
training/rollout.py and training/surrogate/dataset.py — do not widen that one.

Step 2 — the payload, orchestrator-side. `_notify_meeting_concluded` at
orchestrator/game.py:2392-2432 already holds the post-meeting `next_state`, so the ejected
player's role is one lookup away; the roster impostor count is `self._num_impostors`, held at
orchestrator/game.py:1634. Widen `MeetingPacingAgent.note_meeting_concluded` and
`TacticalAgent.note_meeting_concluded` with keyword-only additive parameters defaulting to
None, exactly as `ejected_id` was added at :708-715 — every existing direct caller keeps
working untouched and the capability gate is unchanged. Read the role from the post-meeting
state rather than from the meeting result: the result is engine-free by design and must stay
so.

Step 3 — the tally, manager-side. Add a pure reduction beside `derive_reported_testimony`
(meetings/manager.py:3913) that turns a recorded `MeetingResult` into the public tally — votes
for the ejected target and the skip count, over `result.ballots`, remembering `SKIP_TARGET` is
a first-class tally target (meetings/voting.py:145-215) and that a tie resolves to SKIPPED.
Keep it engine-free, deterministic and role-blind; the manager must never see a role.
`MeetingBeliefEvidence` at meetings/manager.py:3597 is the precedent for the DTO's home. The
orchestrator flattens it into the hook's keyword arguments so `agents/` never imports
`meetings.manager` (.importlinter forbids it).

Step 4 — the fold and the carrier. `agents/memory/working.py` is engine-free and its own test
pins that it imports no engine: type the revealed role as a local string literal alias in that
module, not `engine.entities.Role`. Give `MeetingHistory` the impostors-remaining derivation so
the arithmetic lives next to the data it reads; a kill never moves it.

Step 5 — the render. `_assemble_view` (agents/memory/store.py:2070-2163) is where the
elastic/non-elastic split lives: the meetings block joins `fixed_lines` and the
beliefs/contradictions blocks, NOT the salience-sorted observation list, so a tight budget can
never shed it. Keep it short — one line per concluded meeting; the coalescing task that follows
is what buys back the room, and this block must not be what makes the budget bind. The OFF path
must not merely produce equal bytes but take the same code path shape it takes today.

Step 6 — the testimony content. `SawVentObservation` is currently excluded from the reduction
on purpose (meetings/schemas.py:112-113); widening the reduction is the point of R5's half, and
the schema's own docstring is one of the false claims that must be corrected in the same PR.
Preserve the `CLAIM by X (unverified):` frame verbatim — agents/memory/store.py:1753-1757
documents it as load-bearing, and replacing the frame is a legibility decision this task is not
making. The meeting index is available at absorb time as the length of the agent's own
`meeting_history` (the fold order at orchestrator/game.py:2020-2035 is beliefs, then testimony,
then the outcome). R5's second half — a citable `[tst …]` id a later ballot can quote — is
deliberately NOT built here: minting new ids collides with the coalescing task's span ids and
the citation gate; leave `observation_id` as it is.

Step 7 — the scanner. The existing packet scanner's shape is the model: a frozen set of
forbidden role substrings with one named allowed path (eval/leak_scan.py:68-80, :185-226). The
render scanner is a pure function over the rendered string plus an ejection ledger of player id
to ejection tick plus the render tick; assert every role-bearing disclosure resolves to an
entitled one and fail loud with the offending line quoted. A gate that cannot fail is not a
gate — the planted legs in `eval/leak_test.py` are the proof, not the decoration.

Step 8 — the counterfactual. Roles are NOT in the replay JSONL (the leak firewall keeps them
out); re-derive them deterministically from the seeded setup via
`orchestrator.seeder.seed_initial_state`, the same route eval/balance_eval.py:612-643 takes on
its meeting-abort path. Walk the committed replays, count the renders that would gain a line
and the `saw_vent` rows naming an already-ejected subject, and pin the census in
`tests/agents/test_memory_meeting_history.py` behind the registered `slow` marker with the
session-scoped replay fixture in `tests/conftest.py`. Where a re-derived number differs from
the review's, state the cause in the pin's comment rather than moving the bar.

## Public types this task introduces
- `agents.memory.store.meeting_outcome_memory_enabled`
- `agents.memory.store.ENV_MEETING_OUTCOME_MEMORY`
- `meetings.manager.MeetingOutcomeSummary`
- `meetings.manager.derive_meeting_outcome_summary`
- `eval.leak_scan.assert_memory_render_role_disclosure_is_entitled`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

Role disclosure crosses the §4.7 firewall boundary by design, and that is the whole risk.
Confirm-ejects is the rule being implemented, but the allowance has to be exactly as wide as
the rule and no wider: ejected players only, only at or after their ejection tick, never a
living player and never a kill victim, whose role stays hidden precisely because nobody at the
table saw it. If the allowance is written as "roles may appear in memory renders" rather than
as an entitlement check, this lever converts the project's most-defended invariant into a hole,
and the scanner is the only thing standing between the two readings — which is why the failing
legs are a DoD item and not a nicety. Keep the translation in the orchestrator: the moment
`agents/` or `meetings/` learns to read a role, the import contracts stop being the argument.

Second risk, the token budget. The memory render is already 66% co-presence noise and sheds
prior-meeting testimony first under pressure (365 of 456 measured budget-pressure transitions
cut testimony while keeping the tick-0 spawn block at full size — A/collated-findings.md
§G-34), so a meetings block appended to the elastic observation list would be shed exactly in
the long games that need it. It must join the non-elastic set above observations, and it must
stay one line per meeting; the coalescing task that depends on this one is what frees the room,
and it inherits a block that is already small.

Third risk, reconstruction parity. Neither `api/replay_loader.py`'s memory walk nor the prompt
byte-golden's mirror of it folds meeting outcomes today, because the channel was inert. While
the lever is OFF that is invisible and their bytes cannot move; the day the adopting record
turns it ON, a served or re-golden'd memory that omits the block diverges from the recorded
prompt. Both files are out of scope here by dependency ordering, so the ON-path parity gap must
be stated explicitly in the PR description and handed forward to the stamp-registration and
record tasks rather than discovered during a 23-hour recording.

Fourth risk, the v3 encoder. `agents/tactical/features.py:678-700` reads
`memory.meeting_history` for three scalars and the bakeoff harness pins the segment width. The
widened dataclass must be additive with None defaults and the encoder must not learn to read
the new fields in this task; a single moved feature byte silently invalidates the shipped
champion comparison.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.manager"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.leak_scan"`

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
Open a PR from branch `phase-20-meeting-outcome-memory` with a title like `task 20.29: meetings leave a record: outcomes, revealed roles and testimony as content in memory`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-35 and G-23 (audits/review-2026-08-19/A/collated-findings.md §G-35, §G-23); R4 and R5 and D5 (audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §R4, §R5, §D5); V1 and M1 (audits/review-2026-08-19/A/ideas-among-us-veteran.md §V1, §1 row M1); idea #9 (audits/review-2026-08-19/A/ideas-game-designer.md §9); audits/review-2026-08-19/A/s4-info-economy-beliefs.md §3; the roadmap item audits/review-2026-08-19/D/FINAL-synthesis.md §Wave 2 row 2.10. Re-verified at HEAD 1ceab2c4: agents/memory/working.py:57-73 (`MeetingOutcome`, exactly `end_tick` + `ejected_id`), :133-185 (`MeetingHistory`, `record` at :176); agents/memory/store.py:685-711 (`record_meeting_outcome`, "inert to `render_for_prompt` … no prompt-byte impact anywhere"), :579-682 (`absorb_reported_testimony`), :1750-1804 (`_render_reported_testimony`, the `CLAIM by X (unverified):` prefix at :1777, `accused {subject}` at :1792), :86 (`_SALIENCE_REPORTED_TESTIMONY = 25`), :2070-2163 (`_assemble_view`, the fixed/elastic split); orchestrator/game.py:674-715 (the `MeetingPacingAgent` protocol), :2020-2035 (the belief fold then the pacing fold), :2328-2345 (the testimony fan-out), :2392-2432 (`_notify_meeting_concluded`), :3188-3228 (`TacticalAgent.note_meeting_concluded`); meetings/manager.py:3597 (`MeetingBeliefEvidence`, the sibling reduction DTO), :3913-4004 (`derive_reported_testimony`); meetings/schemas.py:537-539 (`ReportedStatementKind`, the closed four), :95-119 (`SawVentObservation`, ":112-113 deliberately NOT reduced to a `ReportedStatement`"), :721 (`MeetingResult.ejected_player_id`); eval/leak_scan.py:68-80 (the forbidden role-value constants and their single allowed path), :185-210 (`_assert_no_role_bearing_values`), :848-920 (`assert_packet_is_leak_clean`, whose signature 20.8 changed to `(packet, context: PacketContext)`); tests/agents/test_memory_meeting_history.py:249-260 (the field-set provenance pin), :301-308 (the render-inertness pin); DESIGN.md:463 §4.7, :702 §6.6; .importlinter (agents must not import engine, agents must not import meetings.manager)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
