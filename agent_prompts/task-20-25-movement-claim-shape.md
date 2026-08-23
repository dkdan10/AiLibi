# Agent Prompt — 20.25 Movement is a first-class claim: the detector reads 'A at T−1 → B at T' as B at T

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.25 — Movement is a first-class claim: the detector reads 'A at T−1 → B at T' as B at T, anchored to G-9(a) CONFIRMED-BUG — audits/review-2026-08-19/A/verdicts.md §G-9 (the twelve-claim adversarial verification; 313 `alibi_vs_sighting` flags over 300 committed games, 124 backed by a move line in the speaker's own memory, 86 spoke the destination, 38 spoke the origin (32 STRONG), ground truth 38/38 memory-true / speech-false, 25 games / 27 meetings, subjects 31 CREWMATE / 7 IMPOSTOR, 10 meetings ejected the falsely-flagged crewmate; per set 7/76, 0/3, 30/233, 1/1); audits/review-2026-08-19/A/collated-findings.md §G-9 (P0, corrob 8); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.3 (the routed change and its bar: "those 38 flags → 0, with no new flag class in their place"); agents/memory/store.py:1695-1747 (`_render_saw_player_move`; the rendered line at :1742-1745); agents/perception.py:74 (`EVENT_SAW_PLAYER_MOVE`) and :203-215 (each `packet.moved_players` entry becomes one first-hand episodic row); orchestrator/game.py:1778-1791 (packets built at the top of tick N from post-advance state plus tick N−1 events — the +1 agent-clock convention that makes `(T, from_room)` unrepresentable); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:204-209 (five observation shapes, no transition; the same five at crewmate_report.j2:105-110 and accusation_round_roll_call.j2:202-207); meetings/schemas.py:57-63 (`SawPlayerObservation`), :142-149 (the `ObservationClaim` discriminated union), :157-180 (`VentWitnessRecord`), :183-216 (`SightingRecord`); meetings/transcript.py:160-182 (the 16.7 grounding channel and its "ships INERT" precedent), :655 + :666 (the two grounding tick tolerances), :1354-1409 (the resolver homes and the resolver signature this lever clones), :1414-1567 (`detect_contradictions` — takes `vent_witness_records`, has no movement channel), :2170-2180 (`_iter_sightings`, unfiltered), :2380-2390 (`_detect_alibi_vs_sightings`); tasks/phase-13-5.md:271 (Task 13.5.4 shipped the render and deferred exactly this: "A movement-driven belief/contradiction rule is a deliberate later item"); tasks/phase-13.md:700-704 (the 13.14 owner LONE-STRONG ruling that lets one of these flags eject alone); tasks/phase-18.md Task 18.9 (the default-OFF flag-minting lever precedent and its committed-bytes counterfactual pattern); tests/meetings/test_contradictions.py:2071-2108 (the committed byte-identity walk and `_committed_meeting_entries`); tests/meetings/test_vote_tally_parity.py:107-137 (the four-set corpus pin: 707 meetings, all four sets baseline-6).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-movement-claim-shape`
**Depends on:** 20.15, 20.24 — the evidence-honesty instrument set lands first because this task pins its counterfactual against that module's committed cells instead of re-deriving a definition of its own; the self-location trail lands first because it edits the same evidence-honesty test module and because the truthful self-placement it renders is the other half of every flag pair this lever adjudicates.
**Section refs:** G-9(a) CONFIRMED-BUG — audits/review-2026-08-19/A/verdicts.md §G-9 (the twelve-claim adversarial verification; 313 `alibi_vs_sighting` flags over 300 committed games, 124 backed by a move line in the speaker's own memory, 86 spoke the destination, 38 spoke the origin (32 STRONG), ground truth 38/38 memory-true / speech-false, 25 games / 27 meetings, subjects 31 CREWMATE / 7 IMPOSTOR, 10 meetings ejected the falsely-flagged crewmate; per set 7/76, 0/3, 30/233, 1/1); audits/review-2026-08-19/A/collated-findings.md §G-9 (P0, corrob 8); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.3 (the routed change and its bar: "those 38 flags → 0, with no new flag class in their place"); agents/memory/store.py:1695-1747 (`_render_saw_player_move`; the rendered line at :1742-1745); agents/perception.py:74 (`EVENT_SAW_PLAYER_MOVE`) and :203-215 (each `packet.moved_players` entry becomes one first-hand episodic row); orchestrator/game.py:1778-1791 (packets built at the top of tick N from post-advance state plus tick N−1 events — the +1 agent-clock convention that makes `(T, from_room)` unrepresentable); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:204-209 (five observation shapes, no transition; the same five at crewmate_report.j2:105-110 and accusation_round_roll_call.j2:202-207); meetings/schemas.py:57-63 (`SawPlayerObservation`), :142-149 (the `ObservationClaim` discriminated union), :157-180 (`VentWitnessRecord`), :183-216 (`SightingRecord`); meetings/transcript.py:160-182 (the 16.7 grounding channel and its "ships INERT" precedent), :655 + :666 (the two grounding tick tolerances), :1354-1409 (the resolver homes and the resolver signature this lever clones), :1414-1567 (`detect_contradictions` — takes `vent_witness_records`, has no movement channel), :2170-2180 (`_iter_sightings`, unfiltered), :2380-2390 (`_detect_alibi_vs_sightings`); tasks/phase-13-5.md:271 (Task 13.5.4 shipped the render and deferred exactly this: "A movement-driven belief/contradiction rule is a deliberate later item"); tasks/phase-13.md:700-704 (the 13.14 owner LONE-STRONG ruling that lets one of these flags eject alone); tasks/phase-18.md Task 18.9 (the default-OFF flag-minting lever precedent and its committed-bytes counterfactual pattern); tests/meetings/test_contradictions.py:2071-2108 (the committed byte-identity walk and `_committed_meeting_entries`); tests/meetings/test_vote_tally_parity.py:107-137 (the four-set corpus pin: 707 meetings, all four sets baseline-6).
**Complexity:** Medium
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record
**Measurement:** `uv run pytest tests/meetings tests/eval/test_evidence_honesty.py -q` green; the counterfactual pin reads origin-spoken movement flags 38 → 0 over the four committed sets under the lever ON, with the reverse census (newly minted flags by subject role) and the total STRONG `alibi_vs_sighting` count before/after quoted in the PR Summary.

Memory can say a thing the speech schema cannot. `_render_saw_player_move` puts a witnessed transition into a
crewmate's prompt as "[tick T] You saw p-3 move from MEDBAY to LABS." (agents/memory/store.py:1742-1745), and in
the agent clock that line asserts two facts: p-3 was in MEDBAY at T−1 and in LABS at T. The five observation
shapes the model may answer with carry no transition (accusation_round.j2:205-209), so the witness re-encodes the
line as the one static placement that is never true — `saw_player(p-3, MEDBAY, T)` — and the referee compares that
placement to the subject's truthful roll-call answer. Over the 300 committed games the review measured 313
`alibi_vs_sighting` flags, 124 of them backed by a move line the speaker actually holds; 86 spoke the destination
and are fine, 38 spoke the origin and are wrong in exactly this way, 32 of them STRONG, ground truth 38/38 memory
truthful and speech false (audits/review-2026-08-19/A/verdicts.md §G-9).

Ten of those meetings ejected the person the flag framed. In seed 12 m0 the witness holds the MEDBAY→LABS line,
speaks MEDBAY at tick 3, the subject truthfully answers LABS at tick 3, the detector mints
`[alibi_vs_sighting/strong]`, and the table votes the innocent out 6–0–1 while a voter cites "the flag proves they
were in Medbay". In seed 39 m0 an IMPOSTOR holds a true EAST_HALL→CAFETERIA line about the body reporter, speaks
the origin half, and manufactures a 7–1 ejection of the reporter with both impostors riding the flag; the
impostors win the game. Because the 13.14 owner ruling lets a lone `alibi_vs_sighting` cross the ejection gate
(tasks/phase-13.md:700-704), one mis-encoded word converts straight into a lost game — and none of these ten sat
inside the probe that priced that ruling.

This is unsanctioned drift rather than a design choice: Task 13.5.4 shipped the movement render and wrote the
deferral down in its own contract — "A movement-driven belief/contradiction rule is a deliberate later item"
(tasks/phase-13-5.md:271). This task is that item, in the narrowest form that closes the defect. It ships one
default-OFF lever, `AILIBI_MOVEMENT_CLAIM_SHAPE`, with two arms. The resolution arm is what carries the 38: when a
spoken `saw_player` names a subject the SPEAKER's own first-hand movement record moved OUT of that room at that
exact tick, the placement is re-indexed at the DESTINATION before pairing — the encoding the witness meant. The
shape arm makes the transition sayable: an additive `SawMoveObservation` the turn schema accepts, which under the
lever participates as the destination placement, so once the prompt set names the shape the model no longer has to
choose between two half-truths. Grounding is the whole firewall, exactly as the vent channel draws it: a spoken
sighting with no matching record in the speaker's own channel is never rewritten, so the lever can only ever
re-read testimony the speaker demonstrably held — it can never launder a fabrication into a different room.

The bar is two-directional and pre-registered. Dissolving 38 wrong flags is only half the measurement; the other
half is the census of flags that NEWLY mint because a resolved destination placement now contradicts a subject who
was agreeing with the mis-spoken origin. Both numbers, by subject role, over the four committed sets, before any
recording — the 18.9 counterfactual pattern, and the honest price of the change in both directions.

**Files in scope:**
- meetings/schemas.py; (an additive `SawMoveObservation` shape: subject, from_room, to_room, tick — accepted by the turn schema — plus the typed `MoveWitnessRecord` grounding channel, the third sibling of the vent and sighting records)
- meetings/transcript.py; (the lever: a spoken saw_player whose speaker holds a move-line for that subject at that tick is resolved as the DESTINATION placement before contradiction detection; saw_move observations participate as 'B at T' placements; OFF-path byte-identical)
- meetings/render_contract.py; (the contract documents the new shape)
- tests/meetings/test_schemas.py
- tests/meetings/test_contradictions.py; (OFF byte-identity over committed transcripts; ON: the seed-12/39 shapes no longer mint; a true destination-vs-alibi conflict still does)
- tests/eval/test_evidence_honesty.py; (counterfactual: the 38 origin-spoken flags → 0 with no new flag class in their place)
- orchestrator/game.py; (a move-witness records accessor on the meeting-aware agent, beside the sighting/vent accessors — the LIVE feed for the movement channel)
- meetings/manager.py; (the call site that passes the move records into detection — call-site only)

Recorded deviation at merge (PR #377, orchestrator-ratified): two names (from_room/to_room) added to EXPECTED_EVAL_REPORT_FIELDS in tests/api/test_leak.py — forced by SawMoveObservation joining the ObservationClaim union; FORBIDDEN_EVAL_ENGINE_FIELDS untouched. A prose record, not a scope entry.

**Files NOT in scope:**
- agents/strategic/prompts/ (the schema line in the templates lands in 20.31's single bump; until then the model cannot emit saw_move and the detector-side resolution carries the lever)
- agents/memory/ (the move line render is unchanged)
- orchestrator/replay.py (20.33)
- api/ and frontend/ (the spectator mirror of the new observation shape; `api/replay_loader.py:2445-2496` raises `TypeError` on an unmapped claim, so the mirror must exist before any record can carry a saw_move — it belongs with the turn-annotation task that already opens those files)
- meetings/constants.py (the two threshold-owning tasks in this wave own it; this lever's one constant lives beside the existing grounding tolerances in transcript.py)
- eval/evidence_honesty.py (the cell definitions are the instrument set's; this task pins a lever-ON value, it does not define a metric)

**Definition of done:**
- [ ] With the lever OFF, `detect_contradictions` re-derives every recorded flag byte-identically over the committed corpus, and the walk is widened from the samples-only set to all four committed sets (707 meetings — the samples-only restriction and its "deferred to 18.13" comment in `tests/meetings/test_contradictions.py:2071-2096` are stale; both manifests now carry the same baseline-6 flag slate). A set that cannot re-derive is named in the PR with its cause, never silently dropped.
- [ ] OFF-path bytes are pinned elsewhere too: `tests/meetings/test_prompt_byte_golden.py` stays green and `bash scripts/verify_samples.sh` stays 100/100.
- [ ] ON, the resolution arm fires under a stated conjunction and only then: the speaker holds a `MoveWitnessRecord` for that subject whose tick EQUALS the spoken tick (no tolerance — a window could match a different transition of the same subject), whose `from_room` canonically intersects the spoken room, and whose `to_room` is canonically disjoint from it; the indexed sighting is then re-read at `to_room`. Fixtures in `tests/meetings/test_contradictions.py` reproduce the seed-12 m0 and seed-39 m0 shapes and assert no flag mints.
- [ ] ON, the three non-firing cases each have their own fixture: a spoken room matching `to_room` is untouched; a spoken origin at tick T−1 (truthful under the agent clock) is untouched; an UNGROUNDED spoken sighting — no matching record in that speaker's channel — is never rewritten. Plus the perturbation that shows the rule bites: a genuine conflict (the subject claims room C at T while the speaker's own record places them in `to_room` B at T) still mints its STRONG `alibi_vs_sighting`.
- [ ] Id-invariance is asserted, not assumed: the resolution rewrites only the indexed sighting's room, never its event id, so the direct-sighting exclusion set, the proxy-intra-turn guard, `reconstruct_stated_paths`, the absent-set derivation and every id-keyed downstream surface are untouched — pinned by `tests/meetings/test_absent_set.py` and `tests/meetings/test_transcript_reconstruct.py` staying green with the lever ON.
- [ ] `SawMoveObservation` round-trips through the turn schema (accepted unconditionally — the widen-the-contract-inert pattern, so nothing depends on the lever to PARSE it) and under the lever participates as exactly ONE placement, the destination "subject in `to_room` at T". The origin half is deliberately NOT placed at T−1; the docstring states why in one line (a second placement per shape re-opens the off-by-one class this task closes). `tests/meetings/test_schemas.py` pins acceptance, the discriminator, and that the OFF detector ignores the shape entirely.
- [ ] The committed-bytes counterfactual is pinned in `tests/eval/test_evidence_honesty.py` over all four sets, in both directions: origin-spoken movement flags 38 → 0 (20.15's I-7 cell `MovementOriginFlagCells.spoke_origin`, whose per-set 7/76, 30/233, 0/3, 1/1 `test_i7_movement_origin_flag_pins` already pins); the number of flags that NEWLY mint from a resolved destination placement, split by subject role; and the total STRONG `alibi_vs_sighting` count before and after. No new contradiction KIND appears in the ON output (asserted over the kind set, which is the review's "no new flag class in their place").
- [ ] The resolver `movement_claim_shape_enabled(env: Mapping[str, str] | None = None) -> bool` reads `AILIBI_MOVEMENT_CLAIM_SHAPE`, is read ONCE in `detect_contradictions` and threaded down as a boolean (the one-resolver-read convention at meetings/transcript.py:1554-1555), and defaults to False with no environment set. Registration into the substrate stamp is deliberately absent — Task 20.33 registers every Phase-20 lever at once.
- [ ] `meetings/render_contract.py` documents the new observation shape in the renderer contract and stays a leaf (imports only `meetings.schemas` and the stdlib).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — re-verify the defect before changing anything. Read one of the named exemplar meetings out of the
committed bytes, print the speaker's rendered memory line and the spoken observation beside the minted flag, and
quote that triple in the PR. The clock is the trap: the packet is built at the top of tick N from post-advance
state plus tick N−1 events (orchestrator/game.py:1778-1791), so the rendered "[tick T]" transition means
from_room at T−1 and to_room at T. Every comparison in this task is in that agent frame; no engine-frame tick
arithmetic appears anywhere in the diff.

Step 2 — the channel. Add `MoveWitnessRecord` (subject, from_room, to_room, tick) to meetings/schemas.py as the
third sibling of `VentWitnessRecord` and `SightingRecord`, sourced from the speaker's own first-hand
`saw_player_move` episodic rows, and give `detect_contradictions` an optional per-speaker mapping keyed by speaker
id, defaulting to None. None or an absent speaker entry grounds nothing — that default is what makes every legacy
caller and every committed re-derivation byte-identical, the same convention the vent channel uses. Do NOT widen
`SightingRecord` with from_room/to_room: it feeds the exculpatory vouch channel, and a transition is not a vouch.

Step 3 — one chokepoint. Resolve the indexed sightings once, immediately after `_iter_sightings` filtering and
before they reach `_detect_alibi_vs_sightings`, by rebuilding the `_IndexedSighting` with the destination room and
its canonical room set; keep the event id, the speaker and the observation object's identity semantics intact so
nothing id-keyed downstream can notice. Match on exact tick equality — introduce the tolerance as a named
constant beside `VENT_GROUNDING_TICK_TOLERANCE` / `SIGHTING_GROUNDING_TICK_TOLERANCE` with the value 0 and a
sentence saying why a window is unsafe here. If two of a speaker's records name the same subject at the same tick
with different destinations (engine truth forbids it; defend anyway), leave the sighting untouched and say so in
the docstring rather than picking one.

Step 4 — the shape. Add `SawMoveObservation` to the `ObservationClaim` union (meetings/schemas.py:142-149). There
is no `assert_never` over that union in production, so the addition is inert for existing consumers — but grep
before you trust that, and note in the PR that the spectator mirror (`_observation_claim_view`'s `TypeError` tail
at api/replay_loader.py:2445-2496) is out of scope and must exist before any record carries the shape. Under the
lever, index a spoken `saw_move` as a destination placement grounded the same way as the resolution arm; under
OFF, ignore it entirely.

Step 5 — the counterfactual. Reconstruct each speaker's movement records offline from the committed replays the
way the instrument set's harness rebuilds agent state — replay the recorded actions, rebuild each agent's packets
tick by tick, ingest them, and collect the first-hand movement rows — then re-run the detector with the lever ON
through the resolver's `env` parameter. Never mutate `os.environ`; every resolver in this codebase takes `env` for
exactly this reason. Report both directions: the 38 that dissolve and the flags that newly mint, by subject role.

Step 6 — what not to do. Do not consult omniscient state, the engine, or any other agent's memory: the speaker's
own record is the only admissible source, which is what keeps the lever firewall-clean and what stops it becoming
a way to correct testimony the speaker never held. Do not touch the memory render, the prompt templates, or the
weak/strong banding rules. Do not register the lever in the substrate stamp. And leave one line in the module
docstring recording that this closes the movement rule Task 13.5.4 deferred — history as history, one sentence,
no narration.

## Public types this task introduces
- `meetings.transcript.movement_claim_shape_enabled`
- `meetings.transcript.ENV_MOVEMENT_CLAIM_SHAPE`
- `meetings.schemas.SawMoveObservation`
- `meetings.schemas.MoveWitnessRecord`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.memory.store"`
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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-20-movement-claim-shape` with a title like `task 20.25: movement is a first-class claim: the detector reads 'a at t−1 → b at t' as b at t`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing G-9(a) CONFIRMED-BUG — audits/review-2026-08-19/A/verdicts.md §G-9 (the twelve-claim adversarial verification; 313 `alibi_vs_sighting` flags over 300 committed games, 124 backed by a move line in the speaker's own memory, 86 spoke the destination, 38 spoke the origin (32 STRONG), ground truth 38/38 memory-true / speech-false, 25 games / 27 meetings, subjects 31 CREWMATE / 7 IMPOSTOR, 10 meetings ejected the falsely-flagged crewmate; per set 7/76, 0/3, 30/233, 1/1); audits/review-2026-08-19/A/collated-findings.md §G-9 (P0, corrob 8); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-2 row 2.3 (the routed change and its bar: "those 38 flags → 0, with no new flag class in their place"); agents/memory/store.py:1695-1747 (`_render_saw_player_move`; the rendered line at :1742-1745); agents/perception.py:74 (`EVENT_SAW_PLAYER_MOVE`) and :203-215 (each `packet.moved_players` entry becomes one first-hand episodic row); orchestrator/game.py:1778-1791 (packets built at the top of tick N from post-advance state plus tick N−1 events — the +1 agent-clock convention that makes `(T, from_room)` unrepresentable); agents/strategic/prompts/qwen3_6_27b/accusation_round.j2:204-209 (five observation shapes, no transition; the same five at crewmate_report.j2:105-110 and accusation_round_roll_call.j2:202-207); meetings/schemas.py:57-63 (`SawPlayerObservation`), :142-149 (the `ObservationClaim` discriminated union), :157-180 (`VentWitnessRecord`), :183-216 (`SightingRecord`); meetings/transcript.py:160-182 (the 16.7 grounding channel and its "ships INERT" precedent), :655 + :666 (the two grounding tick tolerances), :1354-1409 (the resolver homes and the resolver signature this lever clones), :1414-1567 (`detect_contradictions` — takes `vent_witness_records`, has no movement channel), :2170-2180 (`_iter_sightings`, unfiltered), :2380-2390 (`_detect_alibi_vs_sightings`); tasks/phase-13-5.md:271 (Task 13.5.4 shipped the render and deferred exactly this: "A movement-driven belief/contradiction rule is a deliberate later item"); tasks/phase-13.md:700-704 (the 13.14 owner LONE-STRONG ruling that lets one of these flags eject alone); tasks/phase-18.md Task 18.9 (the default-OFF flag-minting lever precedent and its committed-bytes counterfactual pattern); tests/meetings/test_contradictions.py:2071-2108 (the committed byte-identity walk and `_committed_meeting_entries`); tests/meetings/test_vote_tally_parity.py:107-137 (the four-set corpus pin: 707 meetings, all four sets baseline-6).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
