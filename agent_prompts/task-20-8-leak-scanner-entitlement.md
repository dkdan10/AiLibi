# Agent Prompt — 20.8 The leak scanner checks entitlement, not shape

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.8 — The leak scanner checks entitlement, not shape, anchored to C-31 — audits/review-2026-08-19/B/collated-findings.md row C-31; audits/review-2026-08-19/B/observation-firewall.md §2 F1 (the mutation table), §4 (channel coverage: "visibility gating of players/bodies (absent)"), §5 recommendation 1; audits/review-2026-08-19/B/verdicts.md claim 2 CONFIRMED P1 (the M6 repro: packets 534→564, body_views 33→249, cross-room body views 7→222, whole-suite diff EMPTY); audits/review-2026-08-19/D/cross-track-map.md row C-31; audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 and §4 Wave 1 row 1.1. Anchors re-verified at HEAD: eval/leak_scan.py:609-650 (`assert_packet_is_leak_clean`, signature 609-611), :626-640 (the kill/vent witness cross-check), :641-644 (the body key-set pin), :460 (`PacketRecord`), :486-556 (`_reconstruct_factory_records`, which already holds `walk_event.state` and `game_map`), :354 (`_assert_owned_tasks_match_engine_truth` — the in-repo engine-truth-cross-check precedent, `(packet, *, state, game_map)`), :189-280 (`assert_moved_players_are_witness_gated`, whose docstring at :215-217 gives "callers hold packets and events but no world state" as the reason it is NOT folded into the main scanner); engine/visibility.py:64-80 (`_visible_player_ids`, the vent filter at :78), :83-95 (`_visible_body_ids`), :130-168 (`compute_visibility_for_player`, keyword-only `observer_id`/`world_state`/`game_map`), :141-147 (a dead observer's empty entitlement); observation/service.py:298-305 (bodies copied verbatim from `visibility.visible_body_ids`), :330-361 (`_visible_players`) with the action-actor allowance at :348-356 — the review's "365-372" anchor is stale, that range is inside `_audible_events` at HEAD; eval/leak_test.py:112-158 (`_run_scripted_game`, holds `state` + `game_map`), :229-269 (the scripted sweep), :351-424 (the factory sweeps and the planted-leak self-tests); tests/observation/test_leak_property.py:240-396 (the main sweep, which holds `state` + `game_map`), :609-631 (the movement-vocabulary rationale), :674-741 (the movement sweep) and :744-819 (the deterministic non-vacuity companion); training/crew/scorer.py:1730-1744 and training/bakeoff/harness.py:1823-1837 (the champion-gate call sites, both `scan_factory_packets(...)` inside `try/except AssertionError`); tests/eval/test_replay_walk.py:733-734 and :767-768 (the four `for packet, _ in records` comprehensions that fix `PacketRecord`'s arity) and :714, :723, :749, :758 (its `_reconstruct_factory_records` calls); DESIGN.md:933 (§11.2 "the most important test") and :944 ("no field whose value should be hidden ever appears"); README.md:47 ("zero observation-firewall violations") and :74 ("the leak test walks every emitted packet recursively").. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-leak-scanner-entitlement`
**Depends on:** 20.9 (the firewall test is restructured first so its planted files live in a temp tree instead of fixed paths under the agent and observation packages; this task appends another planted leg to that same file and must land on the restructured version)
**Section refs:** C-31 — audits/review-2026-08-19/B/collated-findings.md row C-31; audits/review-2026-08-19/B/observation-firewall.md §2 F1 (the mutation table), §4 (channel coverage: "visibility gating of players/bodies (absent)"), §5 recommendation 1; audits/review-2026-08-19/B/verdicts.md claim 2 CONFIRMED P1 (the M6 repro: packets 534→564, body_views 33→249, cross-room body views 7→222, whole-suite diff EMPTY); audits/review-2026-08-19/D/cross-track-map.md row C-31; audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 and §4 Wave 1 row 1.1. Anchors re-verified at HEAD: eval/leak_scan.py:609-650 (`assert_packet_is_leak_clean`, signature 609-611), :626-640 (the kill/vent witness cross-check), :641-644 (the body key-set pin), :460 (`PacketRecord`), :486-556 (`_reconstruct_factory_records`, which already holds `walk_event.state` and `game_map`), :354 (`_assert_owned_tasks_match_engine_truth` — the in-repo engine-truth-cross-check precedent, `(packet, *, state, game_map)`), :189-280 (`assert_moved_players_are_witness_gated`, whose docstring at :215-217 gives "callers hold packets and events but no world state" as the reason it is NOT folded into the main scanner); engine/visibility.py:64-80 (`_visible_player_ids`, the vent filter at :78), :83-95 (`_visible_body_ids`), :130-168 (`compute_visibility_for_player`, keyword-only `observer_id`/`world_state`/`game_map`), :141-147 (a dead observer's empty entitlement); observation/service.py:298-305 (bodies copied verbatim from `visibility.visible_body_ids`), :330-361 (`_visible_players`) with the action-actor allowance at :348-356 — the review's "365-372" anchor is stale, that range is inside `_audible_events` at HEAD; eval/leak_test.py:112-158 (`_run_scripted_game`, holds `state` + `game_map`), :229-269 (the scripted sweep), :351-424 (the factory sweeps and the planted-leak self-tests); tests/observation/test_leak_property.py:240-396 (the main sweep, which holds `state` + `game_map`), :609-631 (the movement-vocabulary rationale), :674-741 (the movement sweep) and :744-819 (the deterministic non-vacuity companion); training/crew/scorer.py:1730-1744 and training/bakeoff/harness.py:1823-1837 (the champion-gate call sites, both `scan_factory_packets(...)` inside `try/except AssertionError`); tests/eval/test_replay_walk.py:733-734 and :767-768 (the four `for packet, _ in records` comprehensions that fix `PacketRecord`'s arity) and :714, :723, :749, :758 (its `_reconstruct_factory_records` calls); DESIGN.md:933 (§11.2 "the most important test") and :944 ("no field whose value should be hidden ever appears"); README.md:47 ("zero observation-firewall violations") and :74 ("the leak test walks every emitted packet recursively").
**Complexity:** Medium
**Record impact:** none
**Measurement:** `uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py tests/training/test_leak_gate.py -q` green, and each planted-mutation leg (M6, M1, M10, widened rooms) FAILS when the entitlement assertion alone is commented out — the PR pastes both runs.

The repo's loudest test does not test the thing it is named for. `assert_packet_is_leak_clean`
(eval/leak_scan.py:609-611) takes `(packet, engine_events)` and nothing else, so it can validate
packet SHAPE (key sets, forbidden field names), packet STRINGS (role-bearing substrings) and
WITNESS PERMISSION for `kill`/`vent` actions — but it has no world state, and therefore cannot
ask the only question that matters: was this observer ENTITLED to see these players and these
bodies? The review planted the obvious regression and measured the answer. Mutation M6 (drop the
room filter in `engine/visibility.py::_visible_body_ids`, so every undiscovered corpse is visible
to everyone) takes body views from 33 to 249 over the factory walk and passes eval/leak_test.py,
tests/observation/test_leak_property.py, tests/observation/test_service.py and
tests/test_firewall.py — with an EMPTY whole-suite diff. Zero tests in the repo catch it. M1
(every alive player visible) and M10 (the vent filter dropped) are caught only by
single-scenario unit tests in tests/observation/test_service.py — two for M1, one for M10 — and by
no gate that runs outside pytest. All numbers here are review-derived from audits/review-2026-08-19/B/verdicts.md claim 2.

That gap is load-bearing in three places at once. DESIGN.md:933 titles §11.2 "Information-leakage
test (the most important test)" and :944 asks for a version that "asserts no field whose value
should be hidden ever appears in a packet for a non-self agent" — a presence check, which is
exactly what is missing. README.md:47 advertises "zero observation-firewall violations" and :74
describes the leak test as the thing that makes the agent surface safe; the front-door rewrite
(20.12) amplifies both claims, which is why this repair lands first. And `scan_factory_packets` is
not merely a test: it is the leak gate the ML champion path runs OUTSIDE pytest
(training/crew/scorer.py:1735, training/bakeoff/harness.py:1828, both converting an
`AssertionError` into a recorded `leak_passed=False`), so a learned agent that reached bodies
differently would be admitted as champion with a total hidden-information leak. Later in this
phase the same scanner becomes the instrument that adjudicates the firewall's one sanctioned
widening — the confirm-ejects rule at 20.29, where an ejected player's role enters memory after
its meeting and never before — so the scanner has to be able to state entitlement in both
directions before that widening is drafted.

The design question this contract settles is what "independent" means. `assert_moved_players_are_witness_gated`
already states the principle in its own docstring: it takes the room sets as arguments "so the
check is INDEPENDENT of the service's own gating — a scanner that reused the code under test would
prove nothing". For entitlement the code under test is wider than the service: M6, M1 and M10 all
live inside `engine/visibility.py`'s private entity filters, so a scanner that simply called
`compute_visibility_for_player` and compared id sets would inherit the mutation and catch NONE of
the three. The ruling: the scanner takes the observer's ROOM SET from the engine
(`compute_visibility_for_player(...).visible_rooms`, the same posture the movement scanner already
uses, bounded by an independent adjacency check so a widened room rule is caught too) and
re-derives the ENTITY filters itself from `WorldState` — alive, not in a vent, in a visible room
for players; undiscovered and in a visible room for bodies. Ten lines of oracle, no duplication of
the role-asymmetric mode ruling, and every mutation the review planted bites.

Two properties of the existing scan must survive the change. The kill/vent witness allowance is
REAL: observation/service.py:348-356 adds any actor carrying an observed kill or vent action to
`visible_players` even when the actor is not in `visibility.visible_player_ids` (a vented killer
surfaces as `('p-3','ADMIN','kill')` — the review's secondary C-1 finding). That is intended
kill-attribution, so it is asserted as a NAMED allowance whose members must each pass
`_action_is_permitted_by_witness_event`, never as a silent superset. And `PacketRecord` must stay a
two-element tuple: tests/eval/test_replay_walk.py unpacks `for packet, _ in records` in four
comprehensions across two assertions (:733-734 and :767-768) and is not in this task's scope, so
the tick context rides as the SECOND element rather than a third. Nothing under `engine/`,
`observation/` or `agents/` changes: this is a gate repair, replay bytes cannot move, and there is
no lever and no record.

**Files in scope:**
- eval/leak_scan.py; (the scanner gains the tick context, re-derives entitlement, folds in the movement gate; the docstrings state what it now asserts)
- eval/leak_test.py; (the scripted sweep and the planted-leak self-tests pass the context they already hold)
- tests/observation/test_leak_property.py; (the two Hypothesis sweeps assert entitlement; the observer-class legs; the non-vacuity counter)
- tests/test_firewall.py; (the planted-mutation leg: M6, M1, M10 and a widened room rule each caught — the gate proves it can fail)
- training/crew/scorer.py; (call site only — expect a zero-line or comment-only diff)
- training/bakeoff/harness.py; (call site only — expect a zero-line or comment-only diff)
- tests/training/test_leak_gate.py; (new — the champion-gate contract pinned: same function object, positive packet count, an entitlement failure recorded as a failed gate)

**Files NOT in scope:**
- engine/visibility.py (correct on main; the scanner recomputes independently and never changes visibility — a mutation here is planted in a test, never in the tree)
- observation/service.py (no behaviour change; the vented-actor-in-`visible_players` allowance is DOCUMENTED by this task and CHANGED by none)
- agents/ (the packet consumers are untouched)
- tests/eval/test_replay_walk.py (its four `for packet, _ in records` comprehensions at :733-734 and :767-768 must keep working unchanged — that constraint shapes the record type; if they need editing, STOP and report it under Questions)
- tests/observation/test_service.py (the incidental M1/M10 catches stay exactly as they are)
- DESIGN.md and docs/architecture.md (§11.2's sketch is a historical design record and docs/architecture.md belongs to 20.20; the truth-up lands in the scanner's own docstring)
- README.md (20.12 restates the firewall claim in verifiable shape, using the wording this task's PR records)
- replays/ and any prompt template (no bytes move; template edits belong to 20.31 alone)

**Definition of done:**
- [ ] `eval.leak_scan.assert_packet_is_leak_clean` takes the tick context (engine events + `WorldState` + `Map`) as a REQUIRED argument; the `engine_events: Sequence[EngineEvent] = ()` default is gone so no caller can silently reduce the gate to shape-only, and `PacketRecord` stays a two-element tuple whose second element is the context (the PR quotes the blast-radius grep for `PacketRecord`, `assert_packet_is_leak_clean` and `assert_no_factory_packet_leaks` across the tree).
- [ ] `eval.leak_scan.assert_visible_entities_match_engine_truth` asserts, deriving the entity filters from `WorldState` and NOT from `engine.visibility`'s private helpers: the observer's engine-reported `visible_rooms` contains the observer's own room and is contained in that room plus its map neighbours; the packet's visible player ids EQUAL the set of alive, non-vented, in-visible-room players other than the observer, PLUS exactly the named witness allowance (ids whose `PlayerView.action` is `kill` or `vent` AND that pass `_action_is_permitted_by_witness_event`) — an equality, never a superset; the packet's visible body ids EQUAL the undiscovered bodies in visible rooms, with no allowance; and every `PlayerView.room` and `BodyView.room` lies in `visible_rooms`.
- [ ] Four observer classes are covered by hand-built world states in tests/observation/test_leak_property.py: a crewmate (same-room-only), an impostor (same-room-and-adjacent), a VENTED observer (the engine grants a vented observer the full room set — restated in the module docstring as a rule the scanner asserts, not an accident), and a DEAD observer (empty entitlement; any visible player or body trips).
- [ ] `assert_moved_players_are_witness_gated` is called from `assert_packet_is_leak_clean` using the context's `visible_rooms`, so the ML champion gate scans `moved_players` for the first time; the docstring at eval/leak_scan.py:215-217 that gives "no world state" as the reason it is not folded in is corrected to state what is now true.
- [ ] The planted-mutation leg in tests/test_firewall.py proves the gate can fail: M6 (`_visible_body_ids` drops the room filter), M1 (`_visible_player_ids` returns every alive player), M10 (the vent filter dropped) and a widened `visible_rooms_for_player` are each planted by monkeypatching the named symbol INSIDE the test — never by writing a file into the tree — and each is asserted to raise `AssertionError` from the scanner with a message naming the observer and the offending ids; the unmutated tree is green.
- [ ] The scripted sweep (eval/leak_test.py), both Hypothesis sweeps and the factory walk all pass the context, and the sweep whose vocabulary separates players carries a NON-VACUITY counter — at least one scanned packet whose entitled-player set is a proper subset of the living others — mirroring `scan_factory_packets`'s `bodies_seen > 0` coverage assertion; a sweep in which everyone stands in the spawn room proves nothing about M6, which is why the review called the existing sweeps' visibility coverage vacuous.
- [ ] The ML champion gate keeps its contract: `scan_factory_packets` keeps its signature and still runs outside pytest, training/crew/scorer.py and training/bakeoff/harness.py carry at most a comment-only diff, and tests/training/test_leak_gate.py pins that both call sites bind `eval.leak_scan.scan_factory_packets`, that a scan returns a positive packet count under the entitlement check, and that an entitlement `AssertionError` is recorded as a failed gate rather than escaping the run.
- [ ] `assert_packet_is_leak_clean`'s docstring leads with what the scanner asserts — shape, strings, witness permission, movement gating and ENTITLEMENT — in the shape DESIGN.md:944 describes, with one provenance line and no history narration.
- [ ] No production bytes move: `git diff --name-only` contains nothing under `engine/`, `observation/`, `agents/`, `orchestrator/` or `replays/`, and `bash scripts/verify_samples.sh` stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — verify-then-fix. Before editing, reproduce the defect: monkeypatch
`engine.visibility._visible_body_ids` to drop its room filter, run
`uv run pytest eval/leak_test.py tests/observation tests/test_firewall.py -q`, and confirm green.
Paste that into the PR beside the red run at the end. This is the evidence that the gate could not
fail; without it the fix is unfalsifiable.

Step 2 — the record type. Add a frozen dataclass `PacketContext` with `engine_events:
Sequence[EngineEvent]`, `world_state: WorldState` and `game_map: Map`, then redefine
`PacketRecord: TypeAlias = tuple[ObservationPacket, PacketContext]`. Two elements, deliberately:
tests/eval/test_replay_walk.py (out of scope) unpacks `for packet, _ in records` in four
comprehensions at :733-734 and :767-768 and must keep compiling. `_reconstruct_factory_records`
already has `walk_event.state` and `game_map` in hand at eval/leak_scan.py:542-551, and
`_run_scripted_game` has `state` + `game_map` at eval/leak_test.py:119-148 — both build the
context where they build the packet.

Step 3 — the oracle. Write `assert_visible_entities_match_engine_truth(packet, *, state, game_map)`,
mirroring the naming and signature of the existing `_assert_owned_tasks_match_engine_truth` at
eval/leak_scan.py:354. Take `visible_rooms` from `compute_visibility_for_player(observer_id=...,
world_state=..., game_map=...)` (keyword-only — the review's shorthand signature is not the real
one), bound it independently with `game_map.room_neighbors(observer.room)`, then derive the entity
sets yourself from `state.players` and `state.bodies`. Do NOT call `_visible_player_ids` or
`_visible_body_ids`, and do NOT compare against `visibility.visible_player_ids` /
`visible_body_ids`: those are the mutated symbols in M1, M6 and M10, and a scanner that reads them
catches nothing. Compute the witness allowance as a set first, assert the packet's ids equal
`entitled | allowance`, and put the allowance in the failure message so a future widening reads as
a decision rather than a mystery.

Step 4 — fold in the movement gate. With the context in hand, call
`assert_moved_players_are_witness_gated(packet, engine_events=..., visible_rooms=...)` from
`assert_packet_is_leak_clean` with `departure_visible_rooms=None` (today's service rule, already
pinned on both sides by tests/observation/test_leak_property.py:822). Then fix the docstring at
:215-217 that says the fold-in is impossible.

Step 5 — the planted mutations. Prefer `monkeypatch.setattr(engine.visibility, "_visible_body_ids",
...)` over copying a scratch tree: `compute_visibility_for_player` resolves those helpers as module
globals, so the patch reaches the SERVICE while the scanner's own oracle stays clean — which is
precisely the asymmetry the fix creates. Nothing is written into the working tree, so the
concurrent-run hazard the firewall test is being restructured to remove is not reintroduced. Build
one small helper that runs a handful of ticks and scans, and parameterize it over the four
mutations.

Step 6 — if a real counterexample appears. If the room-membership assertion or the equality trips
on the unmutated tree over the committed scripted fixtures or the factory walk, STOP: that is
either a genuine leak (a finding for the PR's Questions, not a silent weakening) or a real
allowance that must be named, justified and asserted explicitly. Do not relax an equality to a
subset to get green. Keep runtime honest — if the new sweeps push the file past its budget, mark
the heaviest test `slow` (registered in pyproject.toml) and quote the before/after wall time.

## Public types this task introduces
- `eval.leak_scan.PacketContext`
- `eval.leak_scan.assert_visible_entities_match_engine_truth`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-20-leak-scanner-entitlement` with a title like `task 20.8: the leak scanner checks entitlement, not shape`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-31 — audits/review-2026-08-19/B/collated-findings.md row C-31; audits/review-2026-08-19/B/observation-firewall.md §2 F1 (the mutation table), §4 (channel coverage: "visibility gating of players/bodies (absent)"), §5 recommendation 1; audits/review-2026-08-19/B/verdicts.md claim 2 CONFIRMED P1 (the M6 repro: packets 534→564, body_views 33→249, cross-room body views 7→222, whole-suite diff EMPTY); audits/review-2026-08-19/D/cross-track-map.md row C-31; audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC7 and §4 Wave 1 row 1.1. Anchors re-verified at HEAD: eval/leak_scan.py:609-650 (`assert_packet_is_leak_clean`, signature 609-611), :626-640 (the kill/vent witness cross-check), :641-644 (the body key-set pin), :460 (`PacketRecord`), :486-556 (`_reconstruct_factory_records`, which already holds `walk_event.state` and `game_map`), :354 (`_assert_owned_tasks_match_engine_truth` — the in-repo engine-truth-cross-check precedent, `(packet, *, state, game_map)`), :189-280 (`assert_moved_players_are_witness_gated`, whose docstring at :215-217 gives "callers hold packets and events but no world state" as the reason it is NOT folded into the main scanner); engine/visibility.py:64-80 (`_visible_player_ids`, the vent filter at :78), :83-95 (`_visible_body_ids`), :130-168 (`compute_visibility_for_player`, keyword-only `observer_id`/`world_state`/`game_map`), :141-147 (a dead observer's empty entitlement); observation/service.py:298-305 (bodies copied verbatim from `visibility.visible_body_ids`), :330-361 (`_visible_players`) with the action-actor allowance at :348-356 — the review's "365-372" anchor is stale, that range is inside `_audible_events` at HEAD; eval/leak_test.py:112-158 (`_run_scripted_game`, holds `state` + `game_map`), :229-269 (the scripted sweep), :351-424 (the factory sweeps and the planted-leak self-tests); tests/observation/test_leak_property.py:240-396 (the main sweep, which holds `state` + `game_map`), :609-631 (the movement-vocabulary rationale), :674-741 (the movement sweep) and :744-819 (the deterministic non-vacuity companion); training/crew/scorer.py:1730-1744 and training/bakeoff/harness.py:1823-1837 (the champion-gate call sites, both `scan_factory_packets(...)` inside `try/except AssertionError`); tests/eval/test_replay_walk.py:733-734 and :767-768 (the four `for packet, _ in records` comprehensions that fix `PacketRecord`'s arity) and :714, :723, :749, :758 (its `_reconstruct_factory_records` calls); DESIGN.md:933 (§11.2 "the most important test") and :944 ("no field whose value should be hidden ever appears"); README.md:47 ("zero observation-firewall violations") and :74 ("the leak test walks every emitted packet recursively").), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
