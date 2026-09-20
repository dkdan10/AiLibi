# Make an alibi a route so honest movers stop contradicting themselves

**Status:** done

## Outcome

A crewmate who walked through four rooms, said so, and itemised it stops being
convicted for saying it. `AlibiClaim` (`meetings/schemas.py:377-402`) carries
ONE `room` plus one inclusive `from_tick`/`to_tick` window, so any account of
movement compresses into an envelope and the detectors read the speaker's own
true path as a refutation of it. The claim becomes a ROUTE: an ordered list of
`(room, from_tick, to_tick)` segments, exactly one when the player truly did
not move. The `qwen3_6_27b` templates ask for the route; the listener render
prints the route the speaker gave with the `evidence` rows it carried (today it
drops them); the detectors compare a SEGMENT to a sighting, so a truthful mover
mints no flag and a flat lie still mints one. Committed recordings keep loading
and passing `--check`, because a recorded flat payload IS a legal one-segment
route, read and written back as recorded.

## Evidence

[The direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
is the basis; the owner accepted D1 to D8 as a set that date and its section 12
records the rulings. D4 is this card; section 9 calls it the highest-value
process fix. Census over the two shipped 9p2i corpora, counts only, from one
`uv run python -c` walk of their `*.jsonl` counting `kind == "meeting"`
records, `claims` of `type == "alibi"` with `subject == turn.speaker`, and
`contradictions` indexing such a claim:

| corpus | meetings | `alibi_*` | on a span | self-alibis | multi-tick |
| --- | --- | --- | --- | --- | --- |
| `replays/samples/9p2i` | 151 | 57 | 50 | 259 | 210 |
| `replays/ml_corpus/9p2i` | 439 | 134 | 100 | 696 | 559 |
| both | 590 | 191 | 150 | 955 | 769 |

769 of 955 self-alibis (80.5%) state a window longer than one tick, which the
schema forces into one room; 150 of 191 `alibi_*` flags (78.5%) rest on such a
claim.

Seed 41 is the failure, live. In `replays/samples/9p2i/replay-seed-41.jsonl`
meeting `headless-seed-41:meeting-2` turn `turn-4`, `p-9` (crew) states
`{room: ENGINEERING, from_tick: 12, to_tick: 15}` whose own `evidence` reads
`saw p-7 in ENGINEERING @ tick 12`, `moved to EAST_HALL @ tick 13`,
`moved to ADMIN @ tick 14`, `moved to WEST_HALL @ tick 15`; the same turn
carries a `whereabouts` of `WEST_HALL @ 15`. Five flags are recorded, four
naming `p-9`:

| kind | pairs the claim against | band |
| --- | --- | --- |
| `alibi_conflict` | `p-9`'s own whereabouts, same turn | weak |
| `alibi_vs_sighting` | ADMIN at tick 14 (`turn-0:obs:4`) | strong |
| `alibi_vs_sighting` | ADMIN at tick 14 (`turn-3:obs:2`) | strong |
| `alibi_vs_sighting` | WEST_HALL at tick 15 | weak, endpoint |
| `alibi_vs_sighting` | EAST_HALL at tick 13 | weak, adjacent |

`p-9` is ejected. Every sighting is true of `p-9` and names a room the
speaker's own evidence already named. As the segments ENGINEERING 12-12,
EAST_HALL 13-13, ADMIN 14-14, WEST_HALL 15-15 all five disappear: each
sighting's room intersects the segment covering its tick, and the whereabouts
line agrees with the last segment.

The mechanism. `_iter_alibis` (`meetings/transcript.py:2398-2456`) builds one
`_IndexedAlibi` (`:2356-2371`) per claim, carrying its single canonical room
set. `_detect_alibi_vs_sightings` (`:2938-3067`) flags when a sighting's rooms
are disjoint from that set and its tick falls anywhere in the window
(`:2993-3000`); `_detect_alibi_conflicts` (`:2873-2935`) flags two accounts of
one subject with disjoint rooms and overlapping ranges, which is how a route's
last leg indicts its first. The prompts teach the compression and the render
hides the correction (both cited in Acceptance). The defect is in-tree under
another name: `self_refuted_alibi_claim_ids` (`:991-1078`) down-weights "the
audited greedy-span defect".

Backward compatibility has three anchors, and it is the SAME mechanism the two
cards behind this one use: read and write the recorded shape as recorded.
`recorded_contradiction_flags` (`eval/meeting_quality.py:2354-2383`) is "the
byte-exact output of the production `detect_contradictions` call", so what
`build_sample_report.py --check` recomputes is read as recorded and a detector
change cannot move it. `scripts/verify_samples.sh` is engine playback through
`ReplayLoader` (`scripts/_verify_samples.py:1-15`), so only PARSING the old
payload matters. And the format-preserving serializer precedent exists at
`meetings/schemas.py:927-934` and `:708-719`.

## Acceptance

- [x] Review correction: the RE-CUT CLASS is closed at the index, not site by
  site. Three rounds each repaired one detector whose geometry a speaker could
  move by restating one continuous stay as several contiguous same-room legs,
  and round 4 found two more of the same shape. The new
  `meetings/transcript.py::maximal_stays` is one pure helper that merges
  consecutive legs with equal canonical room sets and contiguous windows into
  MAXIMAL STAYS; a room change or a GAP ends a stay. Every DETECTION and
  SCORING index is built from it -- `_IndexedAlibi` via `_iter_alibis` (so
  `segment`, `segment_index`, `route_from_tick`, `route_to_tick` and
  `one_segment_route` all mean the stay), `_claim_route_key` (the echo dedup
  and the self-refutation propagation key), `meetings/public_accounts.py`'s
  `_placements`, `eval/process_scorecard.py::_flag_scored_claim_truth` and
  `eval/evidence_honesty.py::_leg_under_sighting`. Nothing that REPORTS an
  account moves: `AlibiClaim` validation and serialisation, the listener
  render, the served DTO, the one-`ReportedStatement`-per-leg reduction and
  `validate_public_accounts`'s scope walk all keep the legs as the speaker gave
  them. A merged stay keeps the FIRST leg's room text, so every description is
  deterministic. Coalescing is the identity on a one-segment route, which every
  committed recording is, so no recorded flag, band, `contradiction_id`, sample
  report or scorecard figure moves.
  `tests/meetings/test_contradictions.py::TestReCuttingAStayChangesNoDetectorOutput`
  is the durable gate: twelve scenarios covering every kind that reads an
  alibi, each stated as one continuous stay AND as a route with a genuine room
  change, with EVERY re-cut of each account enumerated exhaustively.
- [x] Review correction: a same-account re-cut no longer softens a STRONG
  `alibi_conflict` to WEAK. `_conflict_weak_reasons`'s boundary-overlap test
  reads each side's endpoints, so a rival placing `p-1` in `MEDBAY 8-8` against
  a self-alibi of `STORAGE 2-14` was STRONG while the identical account re-cut
  as `STORAGE 2-8` + `9-14` manufactured a junction at tick 8 and published
  `[weak signal: endpoint-tick overlap]`. Coalescing closes it: a re-cut has no
  junction to find. The site is CORRECTLY classified MEMBERSHIP and keeps
  reading the stay -- after coalescing a surviving boundary is a declared room
  change or a gap, and two DIFFERENT claims meeting at a declared transition is
  exactly the honest movement pair the band exists for -- but round 3's
  justification for that classification was FALSE and is corrected in the
  round-4 table.
- [x] Review correction: the kill-scene arm's Task 13.5.3 repair is ENFORCED.
  Reverting its route-interior line to the leg left `tests/meetings` fully
  green (1,405 passed) at the round-3 head, and after coalescing the round-3
  cases cannot reach the distinction at all, because they state one continuous
  stay. `TestADeclaredTransitionIsNotMovementFuzz` states routes with a GENUINE
  room change, where the stay's window and the route's outer endpoints really
  differ, and holds all four transit-fuzz lines -- both `alibi_vs_physical`
  arms, `_adjacent_within_one_tick` and the endpoint-tick band -- each paired
  with the control at the route's own outer endpoint where the band must still
  fire.
- [x] Review correction: a multi-leg route no longer DELETES an
  `alibi_vs_physical` flag at every leg boundary. `_detect_alibi_vs_physical`
  required a contradicting co-presence at a tick strictly interior to the LEG,
  so a speaker split their way out of the evidence: `STORAGE 2-14` co-placed in
  `MEDBAY` at tick 8 by two independent voices mints two STRONG flags, the same
  account as `STORAGE 2-7` plus `STORAGE 8-14` minted NONE, and as the one-tick
  legs the new prompts ask for no leg has a strict interior at all. The leg
  still decides the room and window MEMBERSHIP; the strict-interior exclusion
  now reads `alibi.route_from_tick` / `alibi.route_to_tick`, because an
  interior boundary is a transition the speaker DECLARED, not movement fuzz.
  The Task 13.5.3 kill-scene arm carried the same leg-interior test and is
  repaired identically (leg membership plus route interior, spelled out because
  it reads `kill_scene_paths` directly). A one-segment route's outer endpoints
  ARE its leg's, so no recorded flag moves.
  `tests/meetings/test_contradictions.py::TestSplittingARouteDoesNotSoftenItsEvidence`
  carries the split-at-the-contradicted-tick case, the one-tick-legs case and
  the outer-endpoint control that must still mint nothing.
- [x] Review correction: splitting a route no longer SOFTENS an
  `alibi_vs_sighting` flag through the map-arbitration band.
  `_adjacent_within_one_tick` measured the gap to `alibi.segment`'s endpoints,
  so every split manufactured a new "edge" beside any interior sighting:
  `REACTOR 2-14` against a sighting of `ENGINEERING` (one doorway away) at tick
  8 is STRONG, and the same account as `REACTOR 2-7` plus `REACTOR 8-14` came
  out WEAK (marker `adjacent room one tick away`) and could no longer eject
  alone. The gap now reads the route's outer endpoints and the docstring states
  the rule and its reason rather than "measured to that leg's ENDPOINTS". The
  band still works: a sighting one tick inside the ROUTE's own last tick stays
  weak in both shapes, and a one-segment route is unchanged by construction.
- [x] Review correction: every remaining `alibi.segment` read in
  `meetings/transcript.py` and `meetings/public_accounts.py` is classified
  MEMBERSHIP/ROOM or FUZZ/EDGE, and the classification is published in the
  round-3 Results below. The two sites above were the only FUZZ/EDGE sites
  still pointed at the leg; the endpoint-tick band (`:3175-3178`) and the
  narrow-window band (`:3907`) already read the route, and every other read --
  corroboration, the subject-account index, the conflict overlap and its
  boundary guard, the vent-grounding window, the public-account placements and
  all five description builders -- is MEMBERSHIP or RENDERING, where the leg is
  the correct unit and was left alone.
- [x] Review correction: a truthful EARLIER leg no longer downgrades a later
  leg's conflict. One flag is minted per pair of CLAIMS, and
  `_detect_alibi_conflicts` built it from the FIRST candidate pair of legs --
  the shape it shipped with when a claim held exactly one leg. A route
  `CAFETERIA 1-10` + `ADMIN 11-20` against a rival `STORAGE 10-15` reaches the
  boundary pair first (`WEAK_REASON_BOUNDARY_OVERLAP`), so the genuinely
  interior `ADMIN`/`STORAGE` disagreement -- STRONG when the same leg is stated
  alone -- was published weak. The detector now collects every candidate pair
  for a claim pair and mints the flag from the one carrying the FEWEST
  `_conflict_weak_reasons`; a one-segment route has exactly one candidate, so no
  recorded flag moves, and ties keep the first candidate so emission order stays
  deterministic.
  `tests/meetings/test_contradictions.py::TestARouteDoesNotSoftenItsOwnConflict`
  carries the band, the lone-leg control, a route that is weak on every leg, and
  the one-flag-per-claim-pair count.
- [x] Review correction: two legs of ONE route no longer mint one
  `contradiction_id`. `_Placement.identity` returned the bare event id for every
  stated row, while `_placements` now emits one stated row per LEG all carrying
  the claim's event id, so a two-leg route disagreeing with a single sighting
  returned two flags under one id with two different descriptions -- the exact
  collision the `identity` docstring (`meetings/public_accounts.py:136-150`)
  exists to prevent. `_Placement` gains a `leg` index that enters `identity` for
  a route of MORE than one leg and stays `None` for a one-leg claim, so every id
  a committed recording carries is byte-identical.
  `tests/meetings/test_public_accounts.py::test_two_legs_of_one_route_mint_two_DISTINCT_contradiction_ids`
  asserts the two distinct ids, that both endpoints still resolve to the turn
  artifact, and the one-leg control against the bare-id hash.
- [x] Review correction: `VIEW_MODEL_VERSION` moves `"4"` to `"5"`, because a
  format-2 `AlibiClaimView` serves `route` and DROPS `room` / `from_tick` /
  `to_tick`, three fields every served alibi used to carry. `api/schemas.py:55`
  says the stamp is bumped on a breaking shape change, and dropping required
  fields is the breaking direction: a build stamped `"4"` would pass the guard
  and then read an alibi with no room. `frontend/src/api/client.ts` adds `"4"`
  to its accepted list (the compatible direction -- every version-4 alibi
  carries the flat triple this build renders), `api.ts` / `api.fidelity.ts` are
  regenerated and the lockstep pin in `tests/api/test_view_model.py` moves with
  it. Gate:
  `tests/api/test_view_model.py::test_an_optional_alibi_surface_forces_the_contract_stamp_past_four`
  (red at `"4"`), plus `client.test.ts`'s version-4 read.
- [x] Review correction: the Verification table below is re-measured at THIS
  head, so each command in it carries one reproducible number. Two cells were
  the PRE-round-1 measurement under a heading claiming the head of this branch:
  `bash scripts/check.sh` read 8,113 and `uv run pytest tests/meetings
  tests/agents -q` read 2,696. Both now read what those commands print at the
  round-2 head, and the round-1 table keeps its own dated figures.
- [x] Review correction: the last two Results figures that did not reproduce are
  corrected in place. `uv run pytest tests/agents/test_bespoke_prompt_sets.py -k
  TestEveryRegisteredSetRendersAnAlibi` collects FOURTEEN (seven sets x two
  methods), so the round-1 planted leg reads `2 failed, 12 passed` perturbed and
  `14 passed` reverted, re-run at this head; and
  `_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` names SEVENTY-EIGHT meetings
  (`_MOVEMENT_CHANNEL_DIVERGENCES = 78`, twenty of them in
  `replays/samples/9p2i`), which this PR does not touch, so Measurements no
  longer says seventeen.
- [x] Review correction: EVERY registered prompt family renders a spoken alibi
  again. The six non-locked `accusation_round.j2` bodies still read
  `claim.room` / `claim.from_tick` / `claim.to_tick` under the loader's
  `StrictUndefined`, so `qwen3_5_9b` (the `DEFAULT_PROMPT_SET` a bare shell
  resolves), `qwen3_32b`, `qwen3_32b_thinking`, `qwen3_30b_a3b`, `glm_4_32b`
  and `cydonia_24b` raised `UndefinedError` on any transcript carrying one, and
  the two `experiments/model_probe/variants/templates/` bodies with them. Each
  alibi line now walks `claim.route`, in a form whose ONE-segment render is the
  byte the pre-route body printed.
  `tests/agents/test_bespoke_prompt_sets.py::TestEveryRegisteredSetRendersAnAlibi`
  walks every name in `PROMPT_VERSION_SETS` over a one-segment and a
  four-segment claim and pins both sentences per set; no stamp moves, because
  no rendered byte moves for any claim the old bodies could render.
- [x] Review correction: the Acceptance claim below that `qwen3_5_9b` is
  unaffected named the wrong surface. Its neutral MENU row does still describe a
  legal format-1 claim, and that half stands; what broke was the LISTENER
  render in the same file, which is the correction above.
- [x] Review correction: `eval/evidence_honesty.py` MEASURES a multi-leg route
  instead of aborting the run. `_resolve_flag` returned `None` for every route
  longer than one leg and the scoring caller raises on `None`, so the first
  re-recorded multi-leg flag would have killed the whole honesty and
  `measure_baseline` run. `_leg_under_sighting` resolves the leg whose window
  covers the sighting's tick -- forced, not chosen, because the detector mints
  the flag from that leg and the schema keeps legs strictly non-overlapping --
  and a one-segment route still answers with its single leg, unconditionally.
  `tests/eval/test_evidence_honesty.py::test_a_multi_leg_route_is_measured_against_the_leg_under_the_sighting`
  and `::test_a_route_that_covers_no_tick_of_the_sighting_still_raises`.
- [x] Review correction: row 3 of the process scorecard no longer scores a
  part-true route as manufactured. `_flag_scored_claim_truth` refuses a
  multi-leg claim, so such a flag is published NOT EVALUABLE rather than folded
  `any(some)` across legs the flag never touched; the row's published definition
  names the third not-evaluable shape and both `docs/process-scorecard.{md,json}`
  are regenerated (definition sentence only -- 159/192 and every other cell are
  byte-identical, `--check` green).
  `tests/eval/test_process_scorecard.py::test_a_part_true_route_is_not_evaluable_rather_than_manufactured`
  and `::test_a_one_segment_route_is_still_scored_by_row_three`.
- [x] Review correction: `eval/deduction_metrics.py::_player_visible_text` reads
  `AlibiClaim.evidence`, because the shipped bodies now print it ("They back it
  with: ..." in the locked set, "(evidence: ...)" in the frozen one). Its
  docstring and the two module-level cell descriptions said the rows are never
  rendered; that is false at this head. No published cell moves -- all four
  `build_sample_report.py --check` runs are consistent.
  `tests/eval/test_deduction_metrics.py::test_the_net_reads_an_alibi_claims_evidence_because_the_table_shows_it`.
- [x] Review correction: `validate_public_accounts` walks every SEGMENT of a
  route. It read only the top level of `model_dump()`, where a format-2 claim
  carries neither room nor tick, so a route naming `NOT_A_ROOM` -- or a tick
  before the game began -- was ACCEPTED while the identical flat envelope was
  refused (AGENTS.md rule 5).
  `tests/meetings/test_public_accounts.py::test_the_context_gate_reads_every_leg_of_an_alibi_route`
  carries the legal route, both refusals and the flat control.
- [x] Review correction: the two Results figures that did not reproduce are
  corrected below -- `uv run pytest tests/orchestrator tests/experiments -q`
  reads `1,213 passed, 3 xfailed`, and the segment-comparison planted leg reads
  `1 failed, 5 passed` perturbed and `6 passed` reverted over the six tests of
  `TestTheAlibiIsARoute`. Both were re-run at this head.
- [x] `AlibiClaim` is a route, in ONE claim type: it gains
  `route: tuple[AlibiSegment, ...]` (a new frozen `AlibiSegment` of `room`,
  `from_tick`, `to_tick`) and `claim_format: Literal[1, 2]`. A `mode="before"`
  validator lifts a legacy flat payload into a one-segment route at format 1,
  accepts a `route` payload at format 2, and RAISES on a payload carrying both
  or neither, on an empty route, and on segments that are not chronological and
  strictly non-overlapping (AGENTS.md rule 5). A wrap serializer writes back
  the format the claim carries, so a format-1 claim emits the flat keys and no
  `route`. No envelope accessors are added; the docstring records why one type
  with an internal format beats a second `type: "alibi_route"` variant, which
  would double the branch in every consumer below and leave two live shapes
  with no retirement date. Planted, each red before and green after: a recorded
  format-1 line round-trips byte-identically through `model_validate_json` then
  `model_dump_json`; overlapping, out-of-order and empty routes each raise.
- [x] The detectors read SEGMENTS, and the one-segment case is bit-identical.
  `_IndexedAlibi` (`meetings/transcript.py:2356-2371`) becomes one entry per
  segment with its own window, rooms, whole claim and index.
  `_detect_alibi_vs_sightings` (`:2938-3067`) and `_detect_alibi_conflicts`
  (`:2873-2935`) compare the SEGMENT, while both weak bands keep reading the
  whole ROUTE: the narrow window (`:3730`) reads
  `route[-1].to_tick - route[0].from_tick`, and the endpoint-tick band
  (`:3041-3045`) fires on the route's outer endpoints only, because an interior
  boundary is a transition the speaker declared, not movement fuzz. The
  `interior_exempt` roll-call class (`:2972-2975`) keys on a ONE-SEGMENT route,
  so a multi-leg route's one-tick legs do not inherit it. `_dedupe_echo_alibis`
  (`:2724-2761`), `_subject_account_index` (`:2783`),
  `self_refuted_alibi_claim_ids` (`:991-1078`) and `_detect_alibi_vs_physical`
  (`:3148`) key on route or segment accordingly. Planted: a property test
  asserts that for EVERY one-segment route the new detector emits the pre-card
  detector's flags, and a segment-level edit breaks it.
- [x] The seed-41 shape is the adverse pair. A fixture from that meeting raises
  ZERO flags when `p-9`'s account is the four-segment route and still raises
  the five recorded flags when the same turn states the ENGINEERING 12-15
  envelope; a second fixture plants a flat lie (a one-segment route whose room
  the speaker held at no covered tick) and asserts one `alibi_vs_sighting`
  against it at today's band. Planted: dropping the segment comparison turns
  the honest route red, dropping the envelope case turns the liar green.
- [x] The route crosses the firewall intact, with `ReportedStatement`
  unchanged: `derive_reported_testimony` (`meetings/manager.py:4478-4488`)
  emits one `kind="alibi"` statement per segment, so
  `absorb_reported_testimony` (`agents/memory/store.py:888-900`) lands one
  belief alibi per leg instead of collapsing the account to `from_tick` alone,
  `_format_alibi_suffix` (`:2556-2581`) renders the path, and the cap
  `_MAX_RENDERED_ALIBIS = 3` (`:151-156`) is re-stated in route terms. Every
  other consumer of the flat fields moves, named so none is found late:
  `AlibiClaimView` (`api/schemas.py:665-673`), `_statement_claim_view`
  (`api/replay_loader.py:3221-3229`), `frontend/src/types/api.ts:354-361` with
  `api.fidelity.ts` regenerated by `scripts/gen_frontend_types.py`,
  `ClaimLine.tsx`, `MindInspector.tsx`, the dedup key at
  `eval/alibi_fabrication.py:238` (now `(author, subject, route)`, a bijection
  on one-segment claims so its counts do not move), `llm/report_normalize.py`
  repairing a reversed range per SEGMENT by field name (`:45`, `:71`), and
  `meetings/render_contract.py`. Planted: over every meeting of both committed
  sample sets the reduction and the served view stay byte-identical.
- [x] The operational family asks for a route and shows one, every path below
  under `agents/strategic/prompts/qwen3_6_27b/`.
  `crewmate_report.j2:156` and `accusation_round.j2:290` offer the route object
  and delete the "ONE room" instruction; `accusation_round.j2:252` drops the
  "gets you ejected" warning and asks for the rooms in order with the ticks
  held; the listener render (`accusation_round.j2:175-176`,
  `vote_ballot.j2:155-156`) prints each segment in order AND the claim's
  `evidence` rows; the default-OFF `accusation_round_roll_call.j2:124-125`,
  `:209` take the same edit. Planted: a render test asserts a four-segment
  route with its evidence rows in the reply and ballot prompts, and a
  one-segment route renders the single-room sentence.
- [x] The version cascade is complete and this card takes the wave's FIRST
  bump. `PROMPT_VERSION_SETS["qwen3_6_27b"]` (`orchestrator/game.py:424`)
  advances v5 to v6 as a unit because this card moves all four bodies, every
  `.j2` header marker moves with it (equality gate:
  `tests/agents/test_bespoke_prompt_sets.py:1000-1013`), the registry pin at
  `:525-541` reads v6 with `.v5` added to its no-collision list, and
  `REQUIRED_PROMPT_VERSIONS_BASE` (`scripts/record_ml_corpus.sh:166`) reads v6.
  The wave takes THREE bumps in all, one per card whose template bytes move, so
  no stamp ever covers two bodies: this card's set-wide v6, then `vote_ballot`
  ALONE to v7 on [the grounded SKIP card](grounded-skip-and-guard-labels.md)
  and to v8 on [the weighing card](ballot-weighing-channel.md), in the Task
  15.5 `qwen3_32b` per-template form at `orchestrator/game.py:401-407`. All 672
  recorded meetings of the four committed sets stamp `*.qwen3_6_27b.v5`, so on
  the Task 21.1 precedent this card BYTE-COPIES the six pre-PR bodies to
  `tests/fixtures/prompt_archive/qwen3_6_27b_v5/` with a per-file byte diff
  quoted in the PR, `ARCHIVED_PROMPT_VERSION_SETS`
  (`tests/meetings/test_prompt_byte_golden.py:193`) and `ARCHIVED_MAP_CARDS`
  (`:199`) gain the entry keyed to those stamps, and
  `test_no_archive_is_needed_because_the_default_registry_did_not_move`
  (`:1296-1312`) is rewritten to assert the window is OPEN. The two cards
  behind this one inherit that archive and add nothing to it.
  `DEFAULT_PROMPT_VERSIONS` (`orchestrator/game.py:352-357`) does NOT move,
  because `qwen3_5_9b` is the frozen reference set (`:360-369`), no committed
  recording stamps it, and its neutral menu row still describes a legal
  format-1 claim; the shipped family is `OPERATIONAL_BASELINE_PROMPT_SET`
  (`agents/strategic/prompts/loader.py:185`). Planted: the perturbation leg is
  re-aimed at the ARCHIVED v5 `crewmate_report.j2` and its failing run quoted,
  because perturbing a live v6 body is a no-op for a golden that walks only v5
  recordings.
- [x] The committed record is untouched and shown to be.
  `bash scripts/verify_samples.sh` reports 100/100, no file under `replays/`
  appears in the diff, all four `--check` runs are consistent, and the PR says
  in one sentence why `--check` cannot move (the census is as-recorded; no
  analysis is re-scored over history). `docs/artifacts.md:101` re-derives the
  `tests/fixtures/` row (today `2,098,563 tracked bytes / 29 files`) and no
  longer says the prompt archive is empty; that row and that sentence are this
  card's, not the later two cards'. `tasks/README.md:43`'s inventory sentence
  is updated.

## Constraints

No live provider call of any kind: fake and replay providers only, no
recording, no re-record, no re-scored report. No held-out band prefix is
generated, printed or opened, band 2100-2999 stays unseen, and
`scripts/verify_ml_evidence.py --complete` is never run.

This card CHANGES SHIPPED DEFAULT BEHAVIOUR, on purpose. AGENTS.md craft rule 7
holds prompt-byte and detector changes default-OFF behind an experimental gate
until an adopting record; the owner's D4 ruling of 2026-09-19 sets that aside
for this wave, so the route ships ON with no lever and no new switch. The flat
shape stays LEGAL on input, because a stationary player's route IS one segment;
`claim_format` records which surface a claim arrived in. The shelved accounts
family is kept compiling and NOT developed: `_account_rules.j2:37` keeps its
bytes, `_account_transcript.j2:22` already dumps `claim.model_dump_json()` so
it shows a route with no edit, and `ACCOUNT_PROMPT_SET_REVISION`
(`agents/strategic/prompts/loader.py:1266`) does not move. Engine determinism
and the firewall are untouched: `agents/` must not import `engine/`,
`meetings/` must not import `experiments/`.

One writer per file: this card owns `meetings/schemas.py`,
`meetings/transcript.py`, the `qwen3_6_27b` templates,
`tests/fixtures/prompt_archive/` and `docs/artifacts.md`'s `tests/fixtures/`
row; the two cards behind it stack on this branch and retarget `main` once it
merges; the re-record card retires the archive this card opens.
`frontend/src/components/BallotCard.tsx` belongs to
[the spectator tour](spectator-tour-and-alternatives.md) and is not touched
here.

## Expected scope

`meetings/schemas.py` (`AlibiClaim`, the new `AlibiSegment`, validators and
serializer), `meetings/transcript.py` (indexing, the two alibi detectors, the
weak bands, the echo dedup, the subject-account index, the self-refutation
classifier), `meetings/manager.py` (the reduction at `:4478-4488`),
`meetings/render_contract.py`, `agents/memory/store.py`,
`agents/strategic/prompts/qwen3_6_27b/` (`crewmate_report.j2`,
`accusation_round.j2`, `vote_ballot.j2`, `impostor_report.j2` for its stamp,
the two `*_roll_call.j2` variants), `orchestrator/game.py`,
`scripts/record_ml_corpus.sh`, `api/schemas.py`, `api/replay_loader.py`,
`llm/report_normalize.py`, `eval/alibi_fabrication.py`,
`frontend/src/types/api.ts` and `api.fidelity.ts` (regenerated),
`frontend/src/ui/ClaimLine.tsx`, `frontend/src/components/MindInspector.tsx`,
the tests for each plus `tests/meetings/test_contradictions.py`,
`test_schemas.py`, `test_prompt_byte_golden.py` and
`tests/agents/test_bespoke_prompt_sets.py`, a new
`tests/fixtures/prompt_archive/qwen3_6_27b_v5/`, `docs/artifacts.md`,
`tasks/README.md`, this card. Delivered on `work/alibi-as-route` and one pull
request into `main`, a merge commit or fast-forward and never a squash, with
the trailer `Card: tasks/work/alibi-as-route.md`.

Order, identical on all seven cards. WAVE 1 is parallel and changes no agent
behaviour: [the process scorecard](process-scorecard.md),
[the spectator tour](spectator-tour-and-alternatives.md) and
[the evaluation close](close-deduction-candidate-evaluation.md); the close
merges FIRST so this wave's `GENERATOR_SOURCES` edits owe no restamp to a
retired band. The SUBSTRATE WAVE is serial, all three moving the `qwen3_6_27b`
prompt stamps and the ballot or claim schema: THIS card, then
[grounded SKIP and guard labels](grounded-skip-and-guard-labels.md), then
[the weighing channel](ballot-weighing-channel.md). Then
[the re-record](process-rerecord.md), once. Deferred and in no card: the body
freshness band, an impostor who reports a body, the `docs/` front door.

## Record impact

Prompt bytes MOVE and detector behaviour MOVES, both on the shipped default
path. That is the departure from AGENTS.md craft rule 7 the owner's D4 ruling
authorises, and the PR says so in those words. No committed recording byte and
no report cell moves: the flat payload is read and written back as recorded at
format 1, the flag census is as-recorded, and the testimony reduction over a
one-segment route is byte-identical. Nothing under `audits/` changes, so no
audits row of `docs/artifacts.md` moves; the `tests/fixtures/` row moves
because the v5 prompt archive is added. The stamps advance v5 to v6 while every
committed replay still stamps v5, so the bump-in-flight window is OPEN from
this merge until [the re-record](process-rerecord.md) closes it, the intended
re-lock.

The measured consequence is for the NEXT recording only, stated rather than
discovered: 150 of 191 `alibi_*` flags on the committed corpora rest on a
multi-tick self-alibi, so a re-recorded set is expected to carry materially
FEWER alibi flags, and the ejection rate may move. That is the point, not a
regression: those flags were evidence the schema manufactured. Alibi
comparisons against older recordings are invalidated, per D4. No experiment is
adopted and no lever graduates.

## Validation

`uv run pytest tests/meetings tests/agents tests/api tests/eval tests/llm
tests/scripts tests/training tests/test_firewall.py -q` (fake and replay
providers only), `uv run mypy .`, `uv run ruff check .`,
`uv run ruff format --check .`, `uv run lint-imports`,
`uv run python scripts/gen_frontend_types.py` with a clean diff,
`npm --prefix frontend run tsc:check`, `npm --prefix frontend test`,
`uv run python scripts/validate_task_docs.py`,
`uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`),
`bash scripts/verify_samples.sh` expecting 100/100, the four
`uv run python scripts/build_sample_report.py --sample-dir <set> --check` runs
over both `replays/samples/` and both `replays/ml_corpus/` sets, the census
command quoted in Evidence, and `bash scripts/check.sh` to the end rather than
to the first gate. No live evaluation, calibration or provider call is a check.

## Results

Delivered on `work/alibi-as-route`. The contract is
[the direction of 2026-09-19](../direction-2026-09-19-process-over-outcome.md)
§5, §7 and ruling D4 of §12; the layering it moves is
[architecture](../../docs/architecture.md)'s meeting layer (DESIGN.md §5.3 claim
shapes, §5.4 contradiction detection, §6.6 the rendered belief view) and the
served view-model contract (DESIGN.md §7).

### What changed

`AlibiClaim` is a route. It carries `route: tuple[AlibiSegment, ...]` and
`claim_format: Literal[1, 2]`; a `mode="before"` validator lifts the legacy flat
payload into a one-segment route at format 1 and a wrap serializer writes that
format back, so a recorded claim is read and re-emitted as the bytes it was
recorded in. The docstring records why one type with an internal format beats a
second `alibi_route` variant of `Claim`.

`_IndexedAlibi` (`meetings/transcript.py`) is now one entry per SEGMENT, all
sharing the claim's event id. The two alibi detectors compare the segment
covering a sighting's tick; the narrow-window band reads the whole route
(`route_from_tick` / `route_to_tick`), the endpoint band fires on the route's
outer endpoints only, and the `interior_exempt` roll-call class keys on a
one-segment route. The echo dedup and the self-refutation classifier key on the
whole route (`_claim_route_key`); the subject-account index, the physical
detector and the grounded vent-placement arm key on the segment. Two new
one-per-pair guards keep the leg split from minting a duplicate
`contradiction_id`, and two legs of ONE route never pair with each other.

The reduction emits one `ReportedStatement` per leg and stamps the claim's
provenance id on every one of them, so `absorb_reported_testimony` lands one
belief alibi per leg instead of collapsing an account to its first tick.
`AlibiClaimView` mirrors the claim's two wire surfaces exactly rather than
inventing a third, so a recorded envelope is served byte-identically and a route
is served as a route; `ClaimLine.tsx` and `MindInspector.tsx` render whichever
arrived. `llm/report_normalize.py` keeps the legacy envelope keys through the
prune and repairs a reversed range per segment, both keyed on field names.

### Decisions

* **The served view mirrors the claim's format** rather than summarising a route
  into flat fields. A summary would re-manufacture the single-room envelope this
  card deletes. The cost is four optional keys in the generated TypeScript, which
  is why `scripts/gen_frontend_types.py` gains four rows in its optional-field
  list; the spectator narrows on `route`.
* **`VIEW_MODEL_VERSION` is bumped `"4"` to `"5"`** (added in round 2). Serving
  an alibi with no `room` / `from_tick` / `to_tick` DROPS three fields that were
  required on every served alibi, and `api/schemas.py:55` reserves the stamp for
  exactly that: a build stamped `"4"` indexes those fields unconditionally, so
  without the bump it would pass the guard and then render an alibi with no
  room. The compatible direction stays open -- `frontend/src/api/client.ts`
  adds `"4"` to `"2"`/`"3"` on its accepted list, because every alibi a
  version-4 server serves carries the flat triple this build still renders. The
  bump is free of record impact: the stamp is computed at serve time and no
  recorded byte carries it.
* **The archived v5 bodies are byte copies except one accessor.** The schema
  renamed the field the render reads, so a pure copy of
  `accusation_round.j2` / `vote_ballot.j2` / `accusation_round_roll_call.j2`
  could not render a recorded claim at all. Their alibi line reads
  `claim.route[0]`, which is the same value a format-1 claim recorded, and the
  byte golden proves the rendered prompts are unchanged across all 192 recorded
  meetings. `crewmate_report.j2`, `impostor_report.j2` and
  `impostor_report_roll_call.j2` are byte-identical copies. Per-file diffs are in
  the pull request.
* **`accusation_round_roll_call.j2` takes its own v1 -> v2 bump.** Its bytes move
  with this card, and the reason the card gives for three bumps -- "no stamp ever
  covers two bodies" -- applies to a variant body as much as to a default one. It
  is an unrecorded default-OFF arm, so no recording resolves through either
  value.
* **The deduction evaluation's dry-run paragraph is an archive.** Its figures are
  a function of the shipped prompt bytes, which this card moves. The evaluation
  is CLOSED (PR #473), so re-measuring the paragraph would re-score a closed
  record; the case now asserts the closed gate's refusal instead, on the same
  shape as the existing re-binding window helper. No `audits/` byte moved.

### Verification

Run from a clean worktree at the head of this branch, re-measured at the
ROUND-4 head (the dated round-1, round-2 and round-3 subsections below keep
their own figures). Two cells moved, both by the fifty-nine tests round 4 adds;
the two frontend cells marked below are the round-2 measurement, because rounds
3 and 4 change detector geometry only and move no served byte.

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,204 Python passed, 20 skipped, 3 xfailed; 532 frontend tests; 73 work cards validated |
| `uv run pytest tests/meetings tests/agents -q` | 2,780 passed |
| `uv run pytest tests/api tests/llm -q` | 765 passed, 19 skipped |
| `uv run pytest tests/orchestrator tests/experiments -q` | 1,213 passed, 3 xfailed |
| `uv run pytest tests/scripts/test_counterfactual_phase21.py -q` | 112 passed |
| `uv run mypy .` | Success: no issues found in 491 source files |
| `uv run ruff check .` / `uv run ruff format --check .` | clean |
| `uv run python scripts/gen_frontend_types.py` (round 2) | regenerated; `api.ts` and `api.fidelity.ts` (the stamp) |
| `npm --prefix frontend run tsc:check` | exit 0 |
| `npm --prefix frontend test` | 20 files, 532 tests passed |
| `cd frontend && npm run e2e` (round 2, a served DTO moved) | 13 passed, 3 skipped |
| `bash scripts/verify_samples.sh` | 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | consistent on all four sets |
| `uv run python scripts/publish_process_scorecard.py --check` | consistent |
| `uv run python scripts/verify_ml_evidence.py` | 61 checks, OK 49, FAIL 0, ABSENT 7, INFO 5 |
| `uv run python scripts/check_doc_facts.py` | verified |

The Evidence census re-runs unchanged on the committed bytes -- the recorded
rows did not move:

```
replays/samples/9p2i   meetings 151  alibi_* 57   on a span 50   self-alibis 259  multi-tick 210
replays/ml_corpus/9p2i meetings 439  alibi_* 134  on a span 100  self-alibis 696  multi-tick 559
```

### The planted failures

Each was applied to the tree, run, and reverted.

* **The route invariant.** Disabling the chronological / non-overlapping check in
  `AlibiClaim._validate_route` turns
  `TestAlibiClaimIsARoute::test_out_of_order_legs_are_refused` and
  `::test_overlapping_legs_are_refused` red (`2 failed, 7 passed`); reverted,
  `9 passed`.
* **The segment comparison.** Pairing a sighting against the route's OUTER window
  instead of the leg covering its tick -- the pre-card envelope rule -- turns
  `TestTheAlibiIsARoute::test_the_truthful_route_mints_nothing` red
  (`1 failed, 5 passed`); reverted, `6 passed`. The honest seed-41 route goes
  from zero flags back to the envelope's.
* **The format-preserving serializer.** Emitting a `route` for a format-1 claim
  turns `test_every_recorded_alibi_round_trips_byte_identically` and
  `test_every_recorded_meeting_line_round_trips_byte_identically` red
  (`2 failed, 2 passed`); reverted, `4 passed`.
* **The listener render.** Dropping the `evidence` rows from
  `accusation_round.j2` turns
  `test_every_leg_and_its_evidence_reach_the_reply_and_ballot_prompts` red
  (`1 failed, 2 passed`); reverted, `3 passed`.
* **The re-aimed byte golden.** Pointing
  `test_one_byte_template_perturbation_breaks_the_golden` back at the LIVE v6
  `crewmate_report.j2` makes it fail (`assert not True`) -- every recorded
  meeting now renders through the ARCHIVED v5 bodies, so perturbing a live body
  is a no-op the leg cannot detect. Aimed at
  `qwen3_6_27b_v5/crewmate_report.j2` it passes.
* **The liar.** `TestTheAlibiIsARoute::test_the_same_turn_stating_a_flat_lie_is_
  still_prosecuted` states the same turn as a one-segment STORAGE route and
  recovers all four `alibi_vs_sighting` flags the envelope minted, and
  `::test_a_flat_lie_reaches_the_strong_band` shows a wide lie contradicted at a
  deeply interior tick still classifies STRONG.

### Measurements

Seed 41 meeting 2, the direction memo's exhibit: the committed record holds five
flags, every one naming `p-9` and every one referencing `p-9`'s own claim. As the
four-segment route `ENGINEERING 12-12 / EAST_HALL 13-13 / ADMIN 14-14 /
WEST_HALL 15-15` the meeting mints ZERO. Re-derivation of the recorded envelope
yields four of the five -- this meeting is one of the seventy-eight
`_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` (`_MOVEMENT_CHANNEL_DIVERGENCES = 78`,
twenty of them in `replays/samples/9p2i`) whose fifth flag rests on the private
movement channel a replay cannot rebuild, which the corpus walk already pins.
Neither the count nor the membership moves on this branch.

### Limitations

* The route ships ON with no lever, by the owner's D4 ruling, which sets aside
  AGENTS.md craft rule 7 for this wave. Nothing measures it until the re-record.
* No route is recorded anywhere yet: every committed claim is a one-segment
  format-1 envelope, so the multi-leg paths are exercised by fixtures and
  property tests only. Row 3 of the process scorecard (159 of 192 alibi flags
  manufactured, 83 percent) is the measure this card is read against AFTER the
  re-record, not here.
* `eval/evidence_honesty.py`'s I-6 geometry fold measures a multi-leg route
  against the leg whose window covers the sighting's tick (corrected in round 1;
  the sentence that stood here claimed a NOT EVALUABLE report the code did not
  make). Every committed claim is one segment, so no committed cell moves.
* The bump-in-flight window is OPEN from this merge until the re-record closes
  it. While it is open the byte golden, the validity-gate pin and the Phase-21
  counterfactual all resolve committed recordings through the archived v5 bodies.

### Review corrections, round 1 (2026-09-20)

Six blocking findings from the independent verifiers, all valid, all repaired on
this branch. None is refuted. Commands below were run from a clean worktree at
this head.

**1. Every registered prompt family could render an alibi again.** The card moved
`AlibiClaim`'s fields but only re-aimed the locked set's bodies, and the loader
binds `jinja2.StrictUndefined`, so the six other registered families raised
`UndefinedError: 'meetings.schemas.AlibiClaim object' has no attribute 'room'`
the moment one alibi reached a transcript -- `qwen3_5_9b` (the
`DEFAULT_PROMPT_SET` a bare shell resolves), `qwen3_32b`, `qwen3_32b_thinking`,
`qwen3_30b_a3b`, `glm_4_32b`, `cydonia_24b`. The suite stayed green because the
reconstructed context the cross-set render smoke test walks carries no alibi
claim. Each family's `accusation_round.j2` alibi line now loops `claim.route`
in that set's own wording, and so do
`experiments/model_probe/variants/templates/reply_decisive.j2` and
`optin_decisive.j2`. Its ONE-segment render is byte-identical to what the
pre-route body printed (`- alibi: p-9 in ENGINEERING, ticks 12–15.` for the five
en-dash sets, `- alibi: p-9 in ENGINEERING from tick 12 to 15.` for
`qwen3_5_9b`), which is why NO stamp moves: no rendered byte moves for any claim
those bodies could render, the same argument this card already makes for the
three archived v5 bodies, and `DEFAULT_PROMPT_VERSIONS` -- which the card's
version cascade forbids moving -- stays put.

**2. The Acceptance claim about `qwen3_5_9b` named the wrong surface.** Its
neutral menu row does still describe a legal format-1 claim; the listener render
in the same file is what broke. Corrected in Acceptance.

**3. Evidence honesty measures a multi-leg route rather than aborting.**
`_resolve_flag` answered `None` for every route longer than one leg and the
scoring caller raises `EvidenceHonestyReconstructionError` on `None`, so the
first re-recorded multi-leg flag would have killed the whole honesty and
`measure_baseline` run -- not reported it NOT EVALUABLE, as the Limitations
sentence claimed. `_leg_under_sighting` resolves the leg whose window covers the
sighting's tick; the leg is forced by the recorded pair (the detector mints the
flag only from the covering leg, and legs cannot overlap), a one-segment route
answers with its single leg unconditionally so no recorded cell can move, and a
pair no leg can carry still fails loud. The Limitations sentence is restated.

**4. Row 3 no longer files a caught lie as manufactured.** `_claim_truth` folds
`(every, some)` across ALL legs and `_flag_is_manufactured` reads
`manufactured = any(some)`, so a route true in its first leg and fabricated in
its second scored the flag as schema-manufactured. A recorded flag names the
CLAIM's event id and not the leg, so `_flag_scored_claim_truth` refuses a
multi-leg claim and the flag is published NOT EVALUABLE; the row's published
definition now names that third shape and
`docs/process-scorecard.{md,json}` are regenerated. The regeneration changes the
definition sentence ONLY -- row 3 is still `159/192 = 0.8281 (not evaluable 32)`
and every other cell is byte-identical, `--check` green. The claim census beside
the row still walks the whole account leg by leg: the refusal is about
attributing a FLAG, not about reading a route.

**5. The visible-text net reads an alibi's `evidence`.** The shipped bodies now
print those rows ("They back it with: ..." in `qwen3_6_27b`, "(evidence: ...)"
in `qwen3_5_9b`), so `_player_visible_text` excluding them would file
table-visible testimony as hidden and make the cell's own name false. The net,
its docstring, the two module-level cell descriptions and the enforcing test are
all corrected. No published cell moves: all four
`build_sample_report.py --check` runs are consistent.

**6. The public-account context gate walks every segment.** It inspected only
the top level of `model_dump()`, where a format-2 claim carries neither a room
nor a tick, so a route naming `NOT_A_ROOM` -- or stating `from_tick` 900 at
`current_tick` 20 -- was ACCEPTED while the identical flat envelope was refused.
`_validated_scopes` hands the room and tick checks the row AND each leg.

**7. The two Results figures.** `uv run pytest tests/orchestrator tests/experiments -q`
reads `1,213 passed, 3 xfailed` (the table said 1,212), and
`TestTheAlibiIsARoute` holds six tests, so the segment-comparison planted leg
reads `1 failed, 5 passed` perturbed and `6 passed` reverted (the bullet said 6
and 7). Both were re-run at this head and corrected in place above.

| command (round 1) | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,133 Python passed, 20 skipped, 3 xfailed; 528 frontend tests; 73 work cards validated |
| `uv run pytest tests/meetings tests/agents tests/api -q` | 3,148 passed, 2 skipped |
| `uv run pytest tests/orchestrator tests/experiments -q` | 1,213 passed, 3 xfailed |
| `uv run mypy .` | Success: no issues found in 491 source files |
| `uv run ruff check .` / `uv run ruff format --check .` | clean |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `bash scripts/verify_samples.sh` | 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | consistent on all four sets |
| `uv run python scripts/publish_process_scorecard.py --check` | consistent |
| `uv run python scripts/verify_ml_evidence.py` | 61 checks, OK 49, FAIL 0, ABSENT 7, INFO 5 |
| `uv run python scripts/validate_task_docs.py` / `check_doc_facts.py` | passed / verified |

**Round-1 planted failures.** Each applied to the tree, run, reverted.

* Restoring `claim.room` in `qwen3_5_9b/accusation_round.j2` turns
  `TestEveryRegisteredSetRendersAnAlibi` red for that set (`2 failed, 12 passed`
  over the fourteen selected ids); reverted, `14 passed`. (Figure corrected in
  round 2 and the leg re-run at that head; the class holds seven sets x two
  methods, not the 15 this bullet first read.)
* Restoring `if len(alibi.route) != 1: return None` in `_leg_under_sighting`
  turns `test_a_multi_leg_route_is_measured_against_the_leg_under_the_sighting`
  red with `EvidenceHonestyReconstructionError` (`1 failed, 1 passed`);
  reverted, `2 passed`.
* Dropping the leg-count refusal from `_flag_scored_claim_truth` turns
  `test_a_part_true_route_is_not_evaluable_rather_than_manufactured` red
  (`1 failed, 1 passed`); reverted, `2 passed`.
* Returning only the top-level scope from `_validated_scopes` turns
  `test_the_context_gate_reads_every_leg_of_an_alibi_route` red (`1 failed,
  4 passed`); reverted, `5 passed`.
* Dropping the `evidence` rows from `_player_visible_text` turns
  `test_the_net_reads_an_alibi_claims_evidence_because_the_table_shows_it` red
  (`1 failed, 1 passed`); reverted, `2 passed`.
* The segment-comparison leg re-run for figure 7 above: perturbed
  `1 failed, 5 passed`, reverted `6 passed`.

**Round-1 record impact.** No recording byte moves and nothing is re-scored. The
only published bytes that move are the process scorecard's row-3 DEFINITION
sentence in `docs/process-scorecard.md` / `.json`, regenerated by the committed
`--check` command with every number unchanged; that row's artifacts entry states
files and not bytes, so no `docs/artifacts.md` row moves. No prompt stamp moves,
because no rendered byte moves for any claim the repaired bodies could already
render. A multi-leg route is now published as not evaluable by row 3 until a
flag carries segment attribution -- a limitation of the row, stated here rather
than discovered at the re-record.

### Review corrections, round 2 (2026-09-20)

Five blocking findings from the independent verifiers, all VALID, all repaired
on this branch; none is refuted, and no Codex comment is skipped. Three are
defects in the route work itself, two are Results figures that did not
reproduce. Commands below were re-run from a clean worktree at this head; the
Codex anchors are quoted as the reviewer gave them, at the PREVIOUS head
`d362792b`, so they name the defect's location and not the repair's.

**1. A truthful EARLIER leg downgraded a later leg's conflict** (Codex P2,
`meetings/transcript.py:3005`). One flag is minted per pair of CLAIMS, and
`_detect_alibi_conflicts` built it from the FIRST candidate pair of legs -- the
shape it shipped with, correct only while a claim held exactly one leg. Repro at
the previous head, `evidence_reasoning_version=1`: a route `CAFETERIA 1-10` plus
`ADMIN 11-20` stated by `p-1` about `p-3`, against a rival `STORAGE 10-15` from
`p-2`, emitted ONE `alibi_conflict` at band **weak**, marker `endpoint-tick
overlap` -- the boundary pair `CAFETERIA`/`STORAGE` is reached first and the
old paired-set guard suppressed the genuinely interior `ADMIN`/`STORAGE` pair.
The control stating the `ADMIN` leg ALONE emitted band **strong**, so prepending
a leg the speaker really walked bought a softer flag: the opposite of what this
card is for. The detector now collects every candidate pair for a claim pair and
mints the flag from the one carrying the FEWEST `_conflict_weak_reasons`; ties
keep the first candidate, so emission order and the quoted description stay
deterministic, and a ONE-segment route has exactly one candidate, so no recorded
flag can move (the 672-meeting byte-identity walk is green). New gate:
`tests/meetings/test_contradictions.py::TestARouteDoesNotSoftenItsOwnConflict`
-- the band, the lone-leg control (same band AND same description), a route weak
on every leg that stays weak, and the one-flag-per-claim-pair count.

**2. Two legs of ONE route minted the same `contradiction_id`** (Codex P2,
`meetings/public_accounts.py:231`). `_Placement.identity` returned the bare
event id for a stated row, while `_placements` now emits one stated row per LEG
all carrying the claim's event id, so the sha256 over
`first.identity|second.identity` collided. Repro at the previous head: a route
`ENGINEERING 1-2` plus `REACTOR 3-4` (`p-1` about `p-3`) against a `saw_player`
of `p-3` in `LABS` at tick 3 returned **2 flags, 1 distinct id**, with two
different descriptions -- exactly the collision the `identity` docstring exists
to prevent. `_Placement` gains a `leg` index that enters `identity` for a route
of MORE than one leg and stays `None` otherwise, so a one-leg claim still hashes
the bare event ids and no committed id moves. The leg index is never an
endpoint: both flags still name `turn:<turn>:claim:<i>`. New gate:
`tests/meetings/test_public_accounts.py::test_two_legs_of_one_route_mint_two_DISTINCT_contradiction_ids`,
which asserts two ids, two descriptions, the unmoved endpoints, and the one-leg
control against the bare-id hash.

**3. The view contract stamp moves for a breaking wire shape** (Codex P2,
`api/schemas.py:730`). A format-2 `AlibiClaimView` serializes to `type`,
`subject`, `route`, `evidence` with `from_tick`, `to_tick` and `room` ABSENT,
and the generated `frontend/src/types/api.ts` turns three previously required
fields optional -- while `VIEW_MODEL_VERSION` stayed `"4"` and the client
accepted `"2"`, `"3"`, `"4"`. An older build stamped `"4"` would therefore pass
the guard and then read an alibi with no room. `api/schemas.py:55` reserves the
stamp for exactly this, so the stamp is now `"5"`: `client.ts` adds `"4"` to its
accepted list (the compatible direction is safe -- every version-4 alibi carries
the flat triple this build renders), `api.ts` / `api.fidelity.ts` are
regenerated, the lockstep pin moves with them, and the card and the PR each
carry a Decisions bullet recording the bump. Two prose sentences that named
version 4 as current (`docs/architecture.md`, `docs/observation-contract.md`)
are restated; the architecture note stays inside its 1,300-word ceiling at
1,295. New gate:
`tests/api/test_view_model.py::test_an_optional_alibi_surface_forces_the_contract_stamp_past_four`,
plus `frontend/src/api/client.test.ts`'s explicit version-4 read. No record
impact: the stamp is computed at serve time and no recorded byte carries it.

**4. The Verification table is re-measured at this head.** Two cells were the
PRE-round-1 measurement under a heading claiming the head of this branch --
`bash scripts/check.sh` read 8,113 where it prints 8,133 at the round-1 head,
and `uv run pytest tests/meetings tests/agents -q` read 2,696 where it printed
2,712. Round-1 correction 7 fixed two figures of this class and left these. The
whole table is now re-measured at the ROUND-2 head (8,139 / 2,717, the six new
tests above included); the dated round-1 table keeps its own figures, per the
rule that a command quoted in a dated subsection is pinned to its commit.

**5. The two remaining stale figures.** `uv run pytest
tests/agents/test_bespoke_prompt_sets.py -k TestEveryRegisteredSetRendersAnAlibi`
collects FOURTEEN (seven registered sets x two methods), so round 1's cross-set
planted leg reads `2 failed, 12 passed` perturbed and `14 passed` reverted, not
13/15; the leg was re-applied and reverted at this head to confirm it. And
`_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` names SEVENTY-EIGHT meetings
(`_MOVEMENT_CHANNEL_DIVERGENCES = 78`, twenty of them in `replays/samples/9p2i`)
and this PR does not touch it, so Measurements no longer says "seventeen". Both
corrected in place above.

**Round-2 planted failures.** Each applied to the tree, run, reverted.

* Forcing `_detect_alibi_conflicts` back to the first candidate leg pair (the
  `min` key made constant) turns
  `TestARouteDoesNotSoftenItsOwnConflict::test_the_interior_leg_carries_the_band_not_the_boundary_leg`
  and `::test_the_lone_interior_leg_is_the_control` red (`2 failed, 2 passed`,
  `assert 'strong' == 'weak'`); reverted, `4 passed`.
* Forcing `multi_leg = False` in `_placements` turns
  `test_two_legs_of_one_route_mint_two_DISTINCT_contradiction_ids` red
  (`1 failed, 1 passed`, `assert 1 == 2`); reverted, `2 passed`.
* Restoring `VIEW_MODEL_VERSION = "4"` turns
  `test_an_optional_alibi_surface_forces_the_contract_stamp_past_four` red
  (`1 failed`); reverted, `2 passed` with the lockstep pin.
* The round-1 cross-set leg, re-run for figure 5: restoring `claim.room` in
  `qwen3_5_9b/accusation_round.j2` gives `2 failed, 12 passed`
  (`UndefinedError` at line 172); reverted, `14 passed`.

**Round-2 record impact.** No recording byte moves, nothing is re-scored, and no
prompt stamp moves: `verify_samples.sh` reports 100/100, all four
`build_sample_report.py --check` runs and `publish_process_scorecard.py --check`
are consistent, and no file under `replays/`, `audits/` or `tests/fixtures/`
appears in the diff, so no `docs/artifacts.md` row moves and the inventory
sentence is unchanged (no Status flips). The only contract byte that moves is
the SERVED view stamp `"4"` to `"5"`, which is computed at serve time. The
conflict-band and placement-identity repairs are unreachable on committed bytes,
because every recorded claim is a one-segment route: one candidate leg pair, and
the bare event id.

### Review corrections, round 3 (2026-09-20)

Two blocking findings, both VALID, both repaired on this branch. They are the
same defect twice: a movement-fuzz band pointed at the LEG rather than at the
ROUTE's outer endpoints, which makes the band's geometry something the SPEAKER
chooses. Because a leg boundary is free to state, either one let a liar weaken
or delete the evidence against themself by narrating one continuous stay as
several legs. The card's own Acceptance rule ("The detectors read SEGMENTS")
already says where the line falls -- the leg decides ROOM and WINDOW
MEMBERSHIP, the fuzz bands read the route's OUTER endpoints, "because an
interior boundary is a transition the speaker declared, not movement fuzz" --
and the endpoint-tick band (`meetings/transcript.py:3175-3178`) already
followed it. These two sites did not.

**1. A multi-leg route deleted `alibi_vs_physical` evidence at every leg
boundary** (`meetings/transcript.py`, `_detect_alibi_vs_physical`). The
detector took `from_tick`/`to_tick` from `alibi.segment` and required
`from_tick < placement.tick < to_tick` for a contradicting placement, so the
strict-interior exclusion measured a window the speaker could re-cut at will.
Repro at the previous head `6dcac993`, `evidence_reasoning_version=1`: `p-1`
self-alibis `STORAGE 2-14` while `p-2` and `p-5` independently co-place `p-1`
in `MEDBAY` at tick 8.

```
                                   BEFORE                   AFTER
envelope STORAGE 2-14              2 flags, both strong     2 flags, both strong
split STORAGE 2-7 + 8-14           0 flags                  2 flags, both strong
one-tick legs 6-6/7-7/8-8/9-9      0 flags                  2 flags, both strong
```

The one-tick shape is the one the operational prompts now ask for, and a
one-tick leg has NO strict interior at all, so under the old geometry the
recommended way to state an account was also the way to become unprosecutable.
The leg still decides the room and the window MEMBERSHIP (`from_tick <=
placement.tick <= to_tick`, and the corroboration check, both unchanged); the
strict-interior exclusion now reads `alibi.route_from_tick` /
`alibi.route_to_tick`. The Task 13.5.3 kill-scene arm just below carried the
same leg-interior test and is repaired identically -- it reads
`kill_scene_paths` directly rather than the already-membership-filtered
`independent`, so it now spells out both halves (`from_tick <= tick <= to_tick`
for membership, `route_from_tick < tick < route_to_tick` for the fuzz
exclusion). On a one-segment route the two tests collapse to the single
original comparison, so the repair is a no-op by construction on every
committed claim.

**2. Splitting a route softened an `alibi_vs_sighting` flag through the
map-arbitration band** (`meetings/transcript.py`,
`_adjacent_within_one_tick`). The gap was measured to `alibi.segment`'s
endpoints, so every split manufactured a fresh "edge" next to whatever interior
tick the speaker chose. Repro at `6dcac993`: `p-1` alibis `REACTOR 2-14` and
`p-2` saw `p-1` in `ENGINEERING`, one doorway away, at tick 8.

```
                                   BEFORE                   AFTER
envelope REACTOR 2-14              1 flag, strong           1 flag, strong
split REACTOR 2-7 + 8-14           1 flag, WEAK             1 flag, strong
                                   [adjacent room one tick away]
```

A weak flag cannot eject alone, so the split was the difference between
evidence that decides a meeting and evidence that only informs it. The gap now
reads the route's outer endpoints, and the docstring states the rule and its
reason instead of the old "The gap is measured to that leg's ENDPOINTS". The
band itself is untouched and still fires where it should: a sighting one tick
inside the route's own last tick (tick 13 of `REACTOR 2-14`) is weak in BOTH
shapes, and the one-tick-legs route `6-6/7-7/8-8/9-9` keeps the marker for a
sighting at tick 8, correctly -- tick 8 really is one tick from that route's
outer endpoint 9.

**The classification sweep.** Every `alibi.segment` read in
`meetings/transcript.py` and `meetings/public_accounts.py`, classified
MEMBERSHIP/ROOM (the leg is the right unit) or FUZZ/EDGE (must read the outer
endpoints). Line numbers are at the round-3 head.

| site | reads | class |
| --- | --- | --- |
| `:2044` `detect_corroborations` window | leg | MEMBERSHIP — a sighting corroborates the room claimed for ITS tick |
| `:2897` `_subject_account_index` | leg | MEMBERSHIP — one account per leg, by the card's own comment |
| `:3008-3011` `_detect_alibi_conflicts` overlap | leg | MEMBERSHIP — the overlap geometry of the two windows actually compared |
| `:3097` interior-exempt single-tick class | leg, guarded by `one_segment_route` | MEMBERSHIP — already route-aware |
| `:3124-3126` sighting window | leg | MEMBERSHIP — the leg is what the sighting can refute |
| `:3146-3147` proxy subject-account agreement | leg | MEMBERSHIP — the card names this check explicitly |
| `:3175-3178` endpoint-tick band | **route** | FUZZ/EDGE — already correct |
| `:3262-3263` `_adjacent_within_one_tick` | leg → **route** | FUZZ/EDGE — **defect 2, fixed** |
| `:3381-3382` + `:3394-3395` + `:3425` + `:3450-3451` `_detect_alibi_vs_physical` | leg (membership) + **route** (interior) | FUZZ/EDGE — **defect 1, fixed, both arms** |
| `:3802-3804` vent-grounding window | leg | MEMBERSHIP — no band; the record either lands in a claimed window or does not |
| `:3907` narrow-window band | **route** | FUZZ/EDGE — already correct |
| `:3969-3973` `_conflict_weak_reasons` boundary overlap | leg | MEMBERSHIP — a junction test between TWO claims; route endpoints would wrongly harden a genuine transit pair, and round 2's fewest-weak-reasons selection already closes the split-softening vector here |
| `:4021-4026`, `:4043-4044`, `:4069-4070`, `:4111-4112`, `:4132-4133` descriptions | leg | RENDERING — quote the leg the flag rests on |
| `public_accounts.py:249-251` one placement row per leg | leg | MEMBERSHIP — and two legs of one route share an event id, so `_placements` never pairs a route against itself |

One residual property, recorded rather than changed: a route may leave GAPS
(the schema requires legs to be chronological and strictly non-overlapping, not
contiguous), and a tick no leg covers is a tick the account makes no claim
about, so nothing contradicts it. That is the card's membership rule working as
designed -- narrowing an account narrows what it asserts -- not a fuzz band, so
it is left alone.

**Round-3 planted failures.** `TestSplittingARouteDoesNotSoftenItsEvidence` in
`tests/meetings/test_contradictions.py`: six tests, `6 passed` at this head.
Each production line was reverted in place, run, and restored.

* Pointing the `alibi_vs_physical` interior exclusion back at
  `alibi.segment` turns
  `::test_splitting_at_the_contradicted_tick_keeps_both_strong_flags` and
  `::test_one_tick_legs_keep_both_strong_flags` red (`2 failed, 4 passed`;
  "Right contains 2 more items"); restored, `6 passed`.
* Pointing the `_adjacent_within_one_tick` gap back at `alibi.segment` turns
  `::test_splitting_does_not_soften_an_interior_adjacent_room_sighting` red
  (`1 failed, 5 passed`; `- strong` / `+ weak`); restored, `6 passed`.

The controls stay green in both probes, which is what makes them controls: the
outer-endpoint exclusion (`::test_the_route_s_own_outer_endpoint_is_still_
transit_fuzz`), the band that must still fire
(`::test_the_band_still_fires_one_tick_from_the_route_s_outer_endpoint`), and
the honest seed-41 route (`::test_the_honest_seed_41_route_still_mints_
nothing`, beside the existing
`TestTheAlibiIsARoute::test_the_truthful_route_mints_nothing` and the
`TestOneSegmentRoutesReadLikeTheEnvelope` property, both green). `uv run pytest
tests/meetings -q` reads 1,399 before the new tests and 1,405 after.

**Round-3 gate.** `bash scripts/check.sh` exits 0: ruff clean (520 files
already formatted), `lint-imports` 4 contracts kept / 0 broken,
`validate_task_docs.py` 390 historical phase tasks and 390 prompts plus 73 work
cards, `mypy` Success on 491 source files, `8,145 passed, 20 skipped, 3
xfailed` in 5:00, frontend 20 test files / 532 tests, build green.
`scripts/verify_samples.sh` 50/50 + 50/50 = 100/100 clean;
`build_sample_report.py --check` consistent on all four committed sets
(`replays/samples/{4p1i,9p2i}`, `replays/ml_corpus/{4p1i,9p2i}`);
`publish_process_scorecard.py --check` consistent; `check_doc_facts.py`
verified; `verify_ml_evidence.py` (offline, never `--complete`) 61 checks, OK
49, FAIL 0, ABSENT 7, INFO 5.

**Round-3 record impact.** None. The diff is two files --
`meetings/transcript.py` and `tests/meetings/test_contradictions.py` -- so
nothing under `replays/`, `audits/` or `tests/fixtures/` moves, no
`docs/artifacts.md` row is touched, no prompt stamp and no served contract
stamp moves. Neither repair is reachable on committed bytes: every recorded
claim is a ONE-segment route, whose outer endpoints are its single leg's, so
both comparisons are identical to the ones that minted the recorded flags. The
672-meeting byte-identity walk and all 1,405 `tests/meetings` tests are green,
which is the mechanical statement of that.

### Review corrections, round 4 (2026-09-20)

Two blocking findings, both VALID, both repaired. They are the SAME defect the
three previous rounds each repaired once, at two more sites, which is the
finding behind the finding: rounds 1-3 patched geometry site by site, and a
fourth pair turned up because nothing closed the CLASS. Round 4 closes it at
the index instead.

**The class.** A leg boundary INSIDE one continuous stay in one room is free:
the speaker chooses where to put a full stop and the account says exactly the
same thing either way. Any flag, band, `contradiction_id`, count or description
whose geometry is a function of the legs is therefore a dial the ACCUSED holds.
Every finding of rounds 3 and 4 is one instance:

| round | site | what a re-cut bought the speaker |
| --- | --- | --- |
| 3 | `_detect_alibi_vs_physical` leg interior | two STRONG flags DELETED |
| 3 | `_adjacent_within_one_tick` leg gap | STRONG softened to weak |
| 4 | `_conflict_weak_reasons` boundary overlap | STRONG softened to weak |
| 4 | the kill-scene arm's repair | (repaired, but enforced by no test) |
| 4 (nonblocking) | `public_accounts._placements` | 1 flag multiplied to 2, then 7 |

**1. A same-account re-cut softened a STRONG `alibi_conflict` to WEAK.**
Repro at the round-3 head `0506d2d7`, `evidence_reasoning_version=1`: a rival
`p-2` proxy-alibis `p-1` as `MEDBAY 8-8` plus `CAFETERIA 20-30` (the far second
leg keeps the rival's own route out of the narrow-window band, so the conflict
band is readable), against `p-1`'s self-alibi `STORAGE 2-14`.

```
                              BEFORE                        AFTER
envelope STORAGE 2-14         1 flag, strong                1 flag, strong
re-cut   2-8 + 9-14           1 flag, WEAK                  1 flag, strong
                              [endpoint-tick overlap]       (description identical)
re-cut   2-7 + 8-14           1 flag, WEAK                  1 flag, strong
one-tick legs 2-2 .. 14-14    1 flag, WEAK                  1 flag, strong
```

The mirror, rival `MEDBAY 12-12` plus `CAFETERIA 20-30` against the cut
`2-11 + 12-14`, flips the same way from the other end. Stated with a ONE-leg
rival `MEDBAY 12-12`, as the verifier first put it, the band is weak in BOTH
shapes -- the rival's own single-tick route trips the narrow-window guard
first -- and what the re-cut moved there was the weak-reason LIST (`narrow
alibi window` gaining `; endpoint-tick overlap`) and so the published
description. Both are output the accused was choosing; both are now identical.

**2. The kill-scene arm's Task 13.5.3 repair was enforced by no test.**
Reverting `meetings/transcript.py`'s kill-scene `interior_from <
placement.tick < interior_to` back to the leg at the round-3 head left
`tests/meetings` at **1,405 passed** -- the round-3 subsection's own figure,
fully green with the line neutered. The line is load-bearing (a body reported
in `MEDBAY`, `p-1` self-alibiing `STORAGE 2-14`, two independent voices
co-placing `p-1` in `MEDBAY` at tick 8: envelope 2 strong, split 2-7 + 8-14 and
one-tick legs 6-6..9-9 zero under the leg rule), but every round-3 case states
ONE CONTINUOUS STAY, and after coalescing those cases cannot reach the
leg/route distinction at all -- they are now identity comparisons. The same is
true of the regular arm and of `_adjacent_within_one_tick`: coalescing makes
the round-3 gates controls rather than enforcement. Round 4 therefore adds
scenarios stating a GENUINE room change, where the stay's window and the
route's outer endpoints really differ, and all four transit-fuzz lines go red
when reverted (probes b-e below).

**The class-closing design.** `meetings/transcript.py::maximal_stays` is one
pure helper (no clock, no RNG, no environment) that merges consecutive legs
with EQUAL canonical room sets and CONTIGUOUS windows (`next.from_tick ==
prev.to_tick + 1`) into maximal stays. A room change or a GAP ends a stay --
an unclaimed tick is a tick the account asserts nothing about, which is the
card's membership rule, recorded in round 3 and unchanged. A merged stay keeps
the FIRST leg's `room` TEXT, so every description builder quotes a deterministic
label the speaker actually used; the detectors compare canonical sets, so no
comparison moves. Coalescing is the IDENTITY on a one-segment route, which
every committed claim is.

Routed through it (DETECTION and SCORING):

| consumer | what the stays decide |
| --- | --- |
| `_iter_alibis` -> `_IndexedAlibi` (`:2582`) | one entry per STAY; `segment`, `segment_index`, `rooms`, `stays`, `route_from_tick`, `route_to_tick`, `one_segment_route` |
| `_claim_route_key` (`:2948`) | the echo-dedup key AND the self-refutation propagation key |
| `public_accounts._placements` (`:259-271`) | one stated row per stay, and the `leg` index inside `_Placement.identity` |
| `eval/process_scorecard._flag_scored_claim_truth` | the multi-leg refusal counts STAYS |
| `eval/evidence_honesty._leg_under_sighting` | the stay a recorded sighting bears on, and its window |

Deliberately NOT routed, each for a stated reason:

| consumer | why the legs as stated are correct |
| --- | --- |
| `AlibiClaim` validation + the wrap serializer | the record is what was SAID; every recorded line still round-trips byte-identically |
| the listener render, the spectator DTO, `derive_reported_testimony`'s one `ReportedStatement` per leg | the meeting layer LABELS an account and never rewrites it |
| `public_accounts._validated_scopes` | the gate asks whether each WORD refers to the public context, so it must read every leg's own spelling |
| `process_scorecard._claim_truth` | already invariant (same ticks, same room per tick) AND it compares the RAW room text to the engine's room id, so coalescing would substitute the first leg's spelling for a contiguous leg's |
| `transcript._route_self_refuted` | already invariant; the normalisation that IS load-bearing on this path lives in `_claim_route_key` |
| `llm/report_normalize.py`, `eval/alibi_fabrication.py`'s dedup key, `experiments/lab/` | wire repair and census of what was said, not detection |

**The corrected classification table.** Round 3's sweep is re-published at the
round-4 head, with line RANGES where an expression spans lines. Two rows are
corrected. `alibi.segment` now means the STAY, so every MEMBERSHIP row is
re-cut-invariant by construction.

| site | reads | class |
| --- | --- | --- |
| `:908-965` `maximal_stays` | the whole route | NORMALISATION — new in round 4; the one place a re-cut is erased |
| `:2111-2113` `detect_corroborations` window | stay | MEMBERSHIP — a sighting corroborates the room claimed for ITS tick |
| `:2948` `_claim_route_key` | **stays** | IDENTITY — two copies of one account are one account, however each was cut |
| `:2997-2998` `_subject_account_index` | stay | MEMBERSHIP — one account per stay |
| `:3111-3114` `_detect_alibi_conflicts` overlap | stay | MEMBERSHIP — the overlap geometry of the two windows actually compared |
| `:3201-3202` interior-exempt single-tick class | stay, guarded by `one_segment_route` | MEMBERSHIP — keyed on the COALESCED account |
| `:3229-3231` sighting window | stay | MEMBERSHIP — the stay is what the sighting can refute |
| `:3251-3252` proxy subject-account agreement | stay | MEMBERSHIP — the card names this check explicitly |
| `:3281-3282` endpoint-tick band | **route** | FUZZ/EDGE — correct, and now ENFORCED (probe e) |
| `:3366-3367` `_adjacent_within_one_tick` | **route** | FUZZ/EDGE — round-3 repair, now ENFORCED (probe d) |
| `:3486-3487` + `:3496-3497` + `:3505` + `:3527` `_detect_alibi_vs_physical` regular arm | stay (membership) + **route** (interior) | FUZZ/EDGE — round-3 repair, now ENFORCED (probe c) |
| `:3552-3553` the Task 13.5.3 kill-scene arm | stay (membership) + **route** (interior) | FUZZ/EDGE — round-3 repair, **round-4 blocking 2**, now ENFORCED (probe b) |
| `:3904-3906` vent-grounding window | stay | MEMBERSHIP — no band; the record either lands in a claimed window or does not |
| `:4009` narrow-window band | **route** | FUZZ/EDGE — already correct |
| `:4086-4092` `_conflict_weak_reasons` boundary overlap | stay | MEMBERSHIP — **round-4 blocking 1's site; the CLASSIFICATION stands, its round-3 JUSTIFICATION was false.** Round 3 said "round 2's fewest-weak-reasons selection already closes the split-softening vector here". It does not: that selection only helps when the rival offers a SECOND overlapping candidate pair, and a rival with one overlapping leg leaves exactly one candidate, so the re-cut's manufactured junction decided the band. What closes it is `maximal_stays`. The site keeps reading the stay because, AFTER coalescing, a surviving boundary is a declared room change or a gap — a separately checkable claim — and two DIFFERENT claims meeting at a declared transition is the honest movement pair the reason exists for. Reading the route's outer endpoints here would harden genuine transit pairs, which no finding asked for |
| `:4128-4149`, `:4152-4168`, `:4171-4200`, `:4216-4233`, `:4236-4257` descriptions | stay | RENDERING — quote the stay the flag rests on; a merged stay takes the FIRST leg's room text, so the sentence is deterministic AND re-cut-invariant |
| `public_accounts.py:259-271` one placement row per stay | **stays** | MEMBERSHIP + IDENTITY — the nonblocking multiplication; two stays of one route still share an event id, so `_placements` never pairs a route against itself |

Two further round-3 statements are corrected here rather than rewritten above.
The round-3 record-impact paragraph says "The diff is two files": that was the
SOURCE diff (`meetings/transcript.py` and
`tests/meetings/test_contradictions.py`) and became three once the card edit
landed in the same commit. And the round-3 table cited a single line for two
two-line expressions (`:2044` covering 2044-2046, `:2897` covering 2897-2898);
the table above cites ranges throughout.

**The durable gate is a PROPERTY test.**
`tests/meetings/test_contradictions.py::TestReCuttingAStayChangesNoDetectorOutput`
follows `TestOneSegmentRoutesReadLikeTheEnvelope`'s place in the file but is
EXHAUSTIVE rather than sampled, because the property is over a finite family:
a stay of `n` ticks has `2 ** (n - 1)` narrations and all of them are
enumerated, the uncut stay and the all-one-tick legs included. Twelve scenarios
-- `alibi_conflict` against a rival with a non-overlapping second leg and its
mirror, `alibi_vs_sighting` plain and through the map-arbitration band,
`alibi_vs_physical` on the regular AND the kill-scene arm, the grounded
vent-placement arm, the corroboration path, the self-refutation classifier, the
echo dedup, the roll-call interior-exempt class, and the public-account channel
-- each stated twice, as ONE continuous stay (`STORAGE 2-8`, 64 narrations) and
as a route with a GENUINE room change (`STORAGE 2-6` + `CAFETERIA 7-11`, 16 x
16 = 256), for 24 parametrised cases and 3,840 meetings. Each asserts the same
flags in the same order with the same kind, `contradiction_id`, both endpoints,
subjects, band, `is_weak_contradiction` reading AND DESCRIPTION -- descriptions
included because the first-leg room-text rule makes them equal. Two meta-tests
keep the family honest: every scenario's baseline is non-empty, and the four
kinds are pinned so a scenario cannot quietly stop minting what it was written
for.

Beside it: `TestTheRoundFourReCutExhibits` (the two findings as the verifier
stated them, plus the genuine transit pair and the declared room change that
must still be weak-banded), `TestADeclaredTransitionIsNotMovementFuzz` (the
four transit-fuzz lines on genuine multi-stay routes, each with its
outer-endpoint control), `TestTheAlibiIndexReadsMaximalStays` (the index
itself, where `one_segment_route` and the route endpoints are observable),
`TestTheAccountKeyIsBlindToTheCut` (echo and self-refutation across copies, with
a narrowing control), `TestMaximalStays` in `test_transcript.py` (ten cases on
the rule: merge, gap, room change, spelling, idempotence, outer endpoints),
`test_recutting_one_stay_mints_the_same_public_account_flags`,
`test_recutting_one_stay_does_not_change_whether_row_three_scores_a_flag` and
`test_recutting_a_stay_resolves_to_the_same_window`. Fifty-nine tests in all.
No existing test is weakened, skipped or deleted.

**Round-4 planted failures.** Each applied to the tree, run, restored. Counts
are what pytest prints; the selection is named per probe because a full
`tests/meetings tests/eval` run is quoted only where the probe reaches that far.

| # | production line neutered | selection | perturbed | restored |
| --- | --- | --- | --- | --- |
| a | `maximal_stays` made the IDENTITY | `tests/meetings tests/eval` | `33 failed, 2,594 passed, 1 skipped` | `2,627 passed, 1 skipped` |
| b | kill-scene arm interior -> the leg | `test_contradictions.py test_transcript.py` | `1 failed, 347 passed` | `348 passed` |
| c | regular physical arm interior -> the leg | same | `1 failed, 347 passed` | `348 passed` |
| d | `_adjacent_within_one_tick` gap -> the leg | same | `1 failed, 347 passed` | `348 passed` |
| e | endpoint-tick band -> the leg | same | `2 failed, 346 passed` | `348 passed` |
| f | `_claim_route_key` -> `claim.route` | same | `4 failed, 344 passed` | `348 passed` |
| g | `_placements` -> `claim.route` | `test_public_accounts.py` | `1 failed, 46 passed` | `47 passed` |
| h | `_flag_scored_claim_truth` -> `len(claim.route)` | `test_process_scorecard.py` | `1 failed, 59 passed` | `60 passed` |
| i | `_leg_under_sighting` -> `alibi.route` | `test_evidence_honesty.py` | `1 failed, 106 passed` | `107 passed` |
| j | `one_segment_route` -> `len(claim.route)` | `test_contradictions.py test_transcript.py` | `2 failed, 346 passed` | `348 passed` |

Probes b-e are the answer to "is each round-3 line still REACHABLE and
ENFORCED": all four are, on a genuine multi-stay route, and none is on a
re-cut. Probes j and i were each run TWICE and the first run is reported here
rather than hidden, because each exposed an unenforced line that the repair
then closed:

* **j** first came back `343 passed` with the line neutered -- green.
  `one_segment_route` has one caller, and there it is conjoined with
  `segment.from_tick == segment.to_tick`; a one-TICK stay cannot be re-cut, so
  at that call site the coalesced and uncoalesced readings are provably equal
  and no detector-level test can tell them apart.
  `TestTheAlibiIndexReadsMaximalStays` pins the index directly, where the
  distinction IS observable, and the probe then reads `2 failed, 346 passed`.
* **i** first came back `107 passed` -- green -- because the test compared only
  the ROOM-distance cells, and the leg and the stay name the same room. The
  window is observable through `single_tick_window` (the leg reading resolves
  the re-cut to a one-tick window the speaker never claimed), which the test now
  asserts; the probe then reads `1 failed, 106 passed`.

`route_from_tick` / `route_to_tick` read `stays` rather than `claim.route` and
no probe can separate the two, because `maximal_stays` merges only INTERIOR
boundaries and so never moves an account's outer endpoints. That is an
equivalence, not an unenforced branch, and the equivalence itself is pinned by
`TestMaximalStays::test_the_outer_endpoints_never_move`; the docstring says so
at the property.

**Round-4 gate.** Measured at this head, from this worktree.

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — ruff `520 files already formatted` + `All checks passed!`, `lint-imports` 4 contracts kept / 0 broken, `validate_task_docs.py` 390 historical phase tasks and 390 prompts plus 73 work cards, `mypy` Success on 491 source files, `8,204 passed, 20 skipped, 3 xfailed` in 3:44, frontend 20 test files / 532 tests, build green |
| `uv run pytest tests/meetings tests/eval tests/experiments -q` | 3,256 passed, 1 skipped |
| `uv run pytest tests/meetings tests/agents -q` | 2,780 passed |
| `uv run pytest tests/api tests/llm -q` | 765 passed, 19 skipped |
| `uv run pytest tests/orchestrator tests/experiments -q` | 1,213 passed, 3 xfailed |
| `uv run pytest tests/scripts/test_counterfactual_phase21.py -q` | 112 passed |
| `bash scripts/verify_samples.sh` | 50/50 + 50/50 = 100/100 clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` x4 | consistent on `replays/{samples,ml_corpus}/{4p1i,9p2i}` |
| `uv run python scripts/publish_process_scorecard.py --check` | consistent |
| `uv run python scripts/check_doc_facts.py` | verified |
| `uv run python scripts/validate_task_docs.py` | passed |
| `uv run python scripts/verify_ml_evidence.py` | 61 checks, OK 49, FAIL 0, ABSENT 7, INFO 5 |

**Round-4 record impact.** None. No file under `replays/`, `audits/` or
`tests/fixtures/` is in the diff, so no `docs/artifacts.md` row moves and no
inventory sentence changes; no prompt stamp and no served contract stamp moves.
`verify_samples.sh` is 100/100, all four `build_sample_report.py --check` runs
and `publish_process_scorecard.py --check` are consistent. The mechanical
reason is that coalescing is the identity on a ONE-SEGMENT route and every
committed claim is one: the stays ARE the legs, so every comparison is the one
that minted the recorded flag. `docs/observation-contract.md` gains one
sentence drawing the line the whole round is about -- the served route, the
listener render and the testimony reduction keep the legs as stated; the
detectors read maximal stays -- and `check_doc_facts.py` stays verified.
`docs/architecture.md` is NOT touched: its route sentence is about the
spectator contract, which this round does not change, and the page sits at
1,295 words against its 1,300-word ceiling.
