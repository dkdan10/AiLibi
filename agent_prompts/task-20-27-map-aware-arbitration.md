# Agent Prompt — 20.27 Map-aware flag arbitration: adjacent rooms within one tick are not a contradiction

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.27 — Map-aware flag arbitration: adjacent rooms within one tick are not a contradiction, anchored to audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2 (the geometry-blind aggregation; the 234-flag adjacency census) and §R1 (rank 1, "kill the corridor artifact"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave-2 row 2.5; audits/review-2026-08-19/A/verdicts.md §(d) (0/16,905 move intents ever named a non-adjacent room — the engine enforces the geometry the detector ignores); audits/audit-phase-20-preregistration.md §2 instrument I-6, §3 baseline cell (148/234 = 63.2% pooled), §4 bar 7 (63.2% → ≤ 5%), §6 (this lever is a named partial-adoption candidate), §8 (the offline counterfactual reads I-6); meetings/transcript.py:2836-2961 (`_detect_alibi_vs_sightings`, the single read-site), :2939-2950 (the `weak_reasons` assignment and the endpoint band it must join), :597 + :608 + :626-631 (`NARROW_ALIBI_WINDOW_TICKS`, `WEAK_CONTRADICTION_MARKER_PREFIX`, the `WEAK_REASON_*` literals), :758-789 (`CANONICAL_ROOMS` — the frozen "DATA, not an engine import" precedent this task extends), :812-846 (`canonical_rooms`), :849-868 (`is_weak_contradiction`), :1444-1501 (the Task-18.9 `ENV_*` + resolver pair whose shape this lever mirrors), :1580-1591 + :1754-1765 + :1792-1802 (`detect_contradictions`: the signature, the read-the-resolver-once block, the call that threads the boolean down); meetings/constants.py:1-22 (the stdlib-only leaf rule) and :54-73 (the resolver/threshold homing precedent); tests/meetings/test_contradictions.py:1571-1656 (the resolver-test shape), :3238-3266 (`_COMMITTED_SETS` / `_committed_meeting_entries` — all FOUR sets, `_COMMITTED_MEETINGS = 707`, since 20.25), :3412-3458 (the committed-bytes re-derivation pin), :3542-3543 (`_L1_ENV` / `_L2_ENV`), :3629-3755 (the lever-census harness); tests/meetings/test_transcript.py:715 (the sibling `CANONICAL_ROOMS == load_canonical_map().rooms` pin); engine/maps/canonical_1.yaml:178-203 (the 11 room edges, every one `traversal_ticks: 1`) and :184 (EAST_HALL↔ENGINEERING, the exemplar doorway); replays/samples/9p2i/replay-seed-17.jsonl (the exemplar flag text, present in the committed bytes). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-map-aware-arbitration`
**Depends on:** 20.26 — the grounded-prosecution rules rewrite the same `alibi_vs_sighting` read-site and re-band its STRONG tier, so this lever must compose with the banding that survives that task rather than with the one it replaces
**Section refs:** audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2 (the geometry-blind aggregation; the 234-flag adjacency census) and §R1 (rank 1, "kill the corridor artifact"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave-2 row 2.5; audits/review-2026-08-19/A/verdicts.md §(d) (0/16,905 move intents ever named a non-adjacent room — the engine enforces the geometry the detector ignores); audits/audit-phase-20-preregistration.md §2 instrument I-6, §3 baseline cell (148/234 = 63.2% pooled), §4 bar 7 (63.2% → ≤ 5%), §6 (this lever is a named partial-adoption candidate), §8 (the offline counterfactual reads I-6); meetings/transcript.py:2836-2961 (`_detect_alibi_vs_sightings`, the single read-site), :2939-2950 (the `weak_reasons` assignment and the endpoint band it must join), :597 + :608 + :626-631 (`NARROW_ALIBI_WINDOW_TICKS`, `WEAK_CONTRADICTION_MARKER_PREFIX`, the `WEAK_REASON_*` literals), :758-789 (`CANONICAL_ROOMS` — the frozen "DATA, not an engine import" precedent this task extends), :812-846 (`canonical_rooms`), :849-868 (`is_weak_contradiction`), :1444-1501 (the Task-18.9 `ENV_*` + resolver pair whose shape this lever mirrors), :1580-1591 + :1754-1765 + :1792-1802 (`detect_contradictions`: the signature, the read-the-resolver-once block, the call that threads the boolean down); meetings/constants.py:1-22 (the stdlib-only leaf rule) and :54-73 (the resolver/threshold homing precedent); tests/meetings/test_contradictions.py:1571-1656 (the resolver-test shape), :3238-3266 (`_COMMITTED_SETS` / `_committed_meeting_entries` — all FOUR sets, `_COMMITTED_MEETINGS = 707`, since 20.25), :3412-3458 (the committed-bytes re-derivation pin), :3542-3543 (`_L1_ENV` / `_L2_ENV`), :3629-3755 (the lever-census harness); tests/meetings/test_transcript.py:715 (the sibling `CANONICAL_ROOMS == load_canonical_map().rooms` pin); engine/maps/canonical_1.yaml:178-203 (the 11 room edges, every one `traversal_ticks: 1`) and :184 (EAST_HALL↔ENGINEERING, the exemplar doorway); replays/samples/9p2i/replay-seed-17.jsonl (the exemplar flag text, present in the committed bytes)
**Complexity:** Small
**Record impact:** lever-gated (default-OFF) until the Phase-20 adopting record — ON re-bands flag descriptions, and those strings render into turn and ballot prompts and drive belief Rule 2's graduated delta, so the changed bytes wait for the record
**Measurement:** `uv run pytest tests/meetings tests/eval/test_evidence_honesty.py -q` green and `bash scripts/verify_samples.sh` 100/100 with the key unset; then the I-6 cell over the four committed sets under `AILIBI_MAP_AWARE_ARBITRATION=1` — pooled baseline 148/234 = 63.2%, bar 7 asks for ≤ 5% but a re-derivation against this task's own predicate lands at 8/94 = 8.5% (a MISS, reported as a miss) — pasted into the PR Summary with per-set numerators, the un-gated `adjacent_any_gap` beside the registered cell (bar 7 requires both), and the count of ejections that lose their only STRONG flag

The one cross-agent aggregation the project has is geometry-blind. `_detect_alibi_vs_sightings`
compares a room-at-a-tick to a room-at-a-tick, and nothing under `meetings/` knows that the
station is a graph. Review-measured over the committed baseline-6 bytes and pinned as
instrument I-6 by the evidence-honesty instrument task: **148 of 234 (63.2%) STRONG
`alibi_vs_sighting` flags name two rooms that share a doorway** — one tick of walking
reconciles both statements — **130 of those 148 name innocents**, 187/234 rest on a
single-tick alibi window, and the 234 drove 126 ejections of which **78 were adjacent-room
and 68 of those 78 (87.2%) ejected an innocent**
(audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2). The same census found **0
of 7,458 meeting prompts carrying a room list, an adjacency table or a travel time**, so
neither the detector nor the reader it feeds can tell a corridor from a lie. This is the
largest single measured defect in the gameplay track and the review ranks its repair first.

The exemplar is in the committed bytes. `replays/samples/9p2i/replay-seed-17.jsonl` carries,
verbatim, `Alibi places p-1 in ENGINEERING (ticks 6-6); sighting reports p-1 in EAST_HALL at
tick 6.` — printed twice in the same flag block, one line under a *grounded* `vent_sighting`
naming the real impostor. EAST_HALL and ENGINEERING are joined by a doorway with
`traversal_ticks: 1` (engine/maps/canonical_1.yaml:184). `p-1` was truthfully in EAST_HALL at
t4 and ENGINEERING at t5–t6; an impostor re-dated a true sighting by one tick and manufactured
a STRONG, prompt-labelled "VERIFIED" contradiction out of a corridor. `p-1` was ejected 7–1,
both impostors survived, and a crewmate who had named the right suspect in its own turn voted
against itself because a label outranked its own reasoning. The polarity is worth stating: the
engine never permits a non-adjacent step — the review re-derived **0 of 16,905 move intents
naming a non-adjacent room** (audits/review-2026-08-19/A/verdicts.md §(d)) — so the geometry
the detector ignores is the geometry the engine enforces on every tick of every game.

What ships is the detector half, behind a default-OFF lever. `AILIBI_MAP_AWARE_ARBITRATION`
resolves through `meetings.transcript.map_aware_arbitration_enabled` with the 13.5 signature,
is read ONCE in `detect_contradictions` and threaded down as a boolean — the Task-18.9
convention at meetings/transcript.py:1754-1802, one resolver read, one read-site. ON, an
alibi/sighting pair whose canonical room sets are **one doorway hop apart** AND whose sighting
tick sits **within one tick of an edge of the alibi window** carries a new weak reason instead
of standing STRONG. The flag is demoted, never dropped: flags are information (DESIGN.md §5.4),
the id set is identical between OFF and ON, and `is_weak_contradiction` then routes the pair
through belief Rule 2's graduated down-weight — a corridor informs, and can no longer eject
alone. A two-hop pair keeps its STRONG band, and so does a sighting buried two or more ticks
inside a multi-tick claim of continuous presence, because one hop cannot reconcile that: an
out-and-back excursion costs two ticks and contradicts the claim's interior anyway.

Adjacency arrives the way `CANONICAL_ROOMS` already does, and for the same reason. That
constant (meetings/transcript.py:758-789) is a frozen room allowlist duplicated out of the map
under an explicit "This is DATA, not an engine import" rationale — `meetings` must stay
engine-free because `agents` imports it — and it is kept honest by an equality pin against
`engine.world.load_canonical_map()` at tests/meetings/test_transcript.py:715. This task adds
the neighbour table beside it under the same discipline, with a pin that additionally asserts
every room edge costs exactly one tick, so the phrase "one hop = one tick" cannot quietly stop
being true. No signature widening, no call-site wiring, no new detector input: the rule stays a
pure function of the transcript and a frozen table, which is what keeps the replay-stability
invariant (DESIGN.md §0 rule 1) untouched. The map card in the meeting prompt is the agent-side
half of this repair and belongs to the single prompt-set bump; this task ships no template byte.

**Files in scope:**
- meetings/transcript.py; (the lever: the env key and resolver beside the Task-18.9 pair, the frozen `CANONICAL_ROOM_NEIGHBORS` table beside `CANONICAL_ROOMS`, the new weak reason, and the one read-site inside `_detect_alibi_vs_sightings`)
- meetings/constants.py; (the lever's two thresholds as named constants — the module stays a stdlib-only leaf)
- tests/meetings/test_contradictions.py; (OFF byte-identity over the committed sample bytes; ON: the adjacent-room one-tick shape demotes, a two-hop or two-tick pair still mints; the engine-equality pin for the table and its perturbation)
- tests/eval/test_evidence_honesty.py; (the counterfactual: the I-6 adjacent-room STRONG share OFF and ON over the four committed sets, plus the drift guard between the instrument's classifier and the detector's predicate)

**Files NOT in scope:**
- engine/ (the map is read as pinned data, never imported from `meetings`)
- agents/strategic/prompts/ (the adjacency card in the meeting prompt is the single prompt-set bump; no template byte moves here)
- orchestrator/replay.py (the substrate-stamp registration is done for all Phase-20 levers at once by the stamp-registration task; do NOT add the key to `_TOGGLEABLE_LEVER_RESOLVERS` here)
- meetings/manager.py, orchestrator/game.py (no call-site change is needed: the rule is a pure function of the transcript and the frozen table, so the four live `detect_contradictions` calls are untouched)
- eval/evidence_honesty.py (the I-6 instrument already exists; this task reads it and pins its cells, it does not re-implement or re-define it)
- tests/meetings/test_transcript.py (the sibling room-allowlist pin is cited as precedent, not edited)

**Definition of done:**
- [ ] `meetings.transcript.map_aware_arbitration_enabled(env: Mapping[str, str] | None = None) -> bool` reads `AILIBI_MAP_AWARE_ARBITRATION`, returns False in a bare environment, and is read exactly once in `detect_contradictions` and threaded down as a boolean parameter; `tests/meetings/test_contradictions.py` pins default-OFF, the truthy/falsey value table, and that the passed mapping is neither mutated nor consulted twice — mirroring the resolver tests at :1571-1656.
- [ ] OFF-path byte identity: the committed-bytes walk at `tests/meetings/test_contradictions.py:3412-3458` is extended so re-deriving `detect_contradictions` with the key absent and with `env={}` still reproduces the recorded flags byte-identically on every one of the 707 committed meetings across all four sets; `uv run pytest tests/meetings/test_prompt_byte_golden.py` and `bash scripts/verify_samples.sh` (100/100) stay green.
- [ ] ON behaviour, fixture-pinned in `tests/meetings/test_contradictions.py`: a single-tick alibi in ENGINEERING contradicted by a sighting in EAST_HALL at the same tick demotes to weak carrying `WEAK_REASON_ADJACENT_ONE_TICK`, and `is_weak_contradiction` returns True for it; a two-hop pair (ENGINEERING versus CAFETERIA) still mints STRONG; a sighting two or more ticks inside a multi-tick window still mints STRONG; a pair already weak for another reason gains the new reason in a fixed, byte-stable position rather than replacing the existing marker text.
- [ ] The flag set is re-banded, never thinned: a test asserts the OFF and ON legs over the committed sample bytes carry the identical `contradiction_id` set, and that every flag whose band changes is an `alibi_vs_sighting` (no other kind moves).
- [ ] The table is pinned and the pin bites: `CANONICAL_ROOM_NEIGHBORS` equals `{room: load_canonical_map().room_neighbors(room)}` for every canonical room, and every room edge in the canonical map has `traversal_ticks == 1`; a perturbation case (one flipped neighbour entry) is shown to fail the pin, so the gate cannot silently pass.
- [ ] Counterfactual pin in `tests/eval/test_evidence_honesty.py` over the four committed sets: the I-6 adjacent-room STRONG share OFF and ON per set and pooled, and the count of ejections whose only STRONG flag is an adjacent-room one — the flags that would lose their sole STRONG backing. The review's pooled 148/234 = 63.2% is re-derived rather than restated, and any difference from the pre-registration cell is quoted and explained in the PR.
- [ ] Instrument/detector drift guard: a test asserts the ADJACENCY half of the detector's new predicate agrees flag-for-flag with the I-6 classifier's `distance == 1` reading in `eval/evidence_honesty.py` over the committed bytes (148 of 234 pooled), and pins the tick half as the KNOWN, enumerated difference — the registered `adjacent` cell's gap term measures ticks OUTSIDE the alibi window (always 0 on a minted flag, which is why `adjacent` and `adjacent_any_gap` both read 148), whereas `MAP_ARBITRATION_MAX_TICK_GAP` measures distance to the nearest window ENDPOINT, so 8 adjacent flags sit ≥ 2 ticks inside their window and are deliberately NOT demoted. A disagreement outside that enumerated set of 8 fails loud instead of letting the gauge and the mechanism measure two different rules.
- [ ] `meetings/` remains engine-free: `uv run lint-imports` passes and a grep of `meetings/` for `engine` returns only the data-not-an-import comments; `meetings/constants.py` gains no import.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `meetings.transcript.map_aware_arbitration_enabled`
- `meetings.transcript.ENV_MAP_AWARE_ARBITRATION`
- `meetings.transcript.CANONICAL_ROOM_NEIGHBORS`
- `meetings.transcript.WEAK_REASON_ADJACENT_ONE_TICK`
- `meetings.constants.MAP_ARBITRATION_MAX_HOPS`
- `meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
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
Open a PR from branch `phase-20-map-aware-arbitration` with a title like `task 20.27: map-aware flag arbitration: adjacent rooms within one tick are not a contradiction`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/A/ideas-multi-agent-researcher.md §D2 (the geometry-blind aggregation; the 234-flag adjacency census) and §R1 (rank 1, "kill the corridor artifact"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 Wave-2 row 2.5; audits/review-2026-08-19/A/verdicts.md §(d) (0/16,905 move intents ever named a non-adjacent room — the engine enforces the geometry the detector ignores); audits/audit-phase-20-preregistration.md §2 instrument I-6, §3 baseline cell (148/234 = 63.2% pooled), §4 bar 7 (63.2% → ≤ 5%), §6 (this lever is a named partial-adoption candidate), §8 (the offline counterfactual reads I-6); meetings/transcript.py:2836-2961 (`_detect_alibi_vs_sightings`, the single read-site), :2939-2950 (the `weak_reasons` assignment and the endpoint band it must join), :597 + :608 + :626-631 (`NARROW_ALIBI_WINDOW_TICKS`, `WEAK_CONTRADICTION_MARKER_PREFIX`, the `WEAK_REASON_*` literals), :758-789 (`CANONICAL_ROOMS` — the frozen "DATA, not an engine import" precedent this task extends), :812-846 (`canonical_rooms`), :849-868 (`is_weak_contradiction`), :1444-1501 (the Task-18.9 `ENV_*` + resolver pair whose shape this lever mirrors), :1580-1591 + :1754-1765 + :1792-1802 (`detect_contradictions`: the signature, the read-the-resolver-once block, the call that threads the boolean down); meetings/constants.py:1-22 (the stdlib-only leaf rule) and :54-73 (the resolver/threshold homing precedent); tests/meetings/test_contradictions.py:1571-1656 (the resolver-test shape), :3238-3266 (`_COMMITTED_SETS` / `_committed_meeting_entries` — all FOUR sets, `_COMMITTED_MEETINGS = 707`, since 20.25), :3412-3458 (the committed-bytes re-derivation pin), :3542-3543 (`_L1_ENV` / `_L2_ENV`), :3629-3755 (the lever-census harness); tests/meetings/test_transcript.py:715 (the sibling `CANONICAL_ROOMS == load_canonical_map().rooms` pin); engine/maps/canonical_1.yaml:178-203 (the 11 room edges, every one `traversal_ticks: 1`) and :184 (EAST_HALL↔ENGINEERING, the exemplar doorway); replays/samples/9p2i/replay-seed-17.jsonl (the exemplar flag text, present in the committed bytes)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
