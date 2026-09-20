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

Run from a clean worktree at the head of this branch.

| command | result |
| --- | --- |
| `bash scripts/check.sh` | exit 0 — 8,113 Python passed, 20 skipped, 3 xfailed; 528 frontend tests; 73 work cards validated |
| `uv run pytest tests/meetings tests/agents -q` | 2,696 passed |
| `uv run pytest tests/api tests/llm -q` | 764 passed, 19 skipped |
| `uv run pytest tests/orchestrator tests/experiments -q` | 1,213 passed, 3 xfailed |
| `uv run pytest tests/scripts/test_counterfactual_phase21.py -q` | 112 passed |
| `uv run mypy .` | Success: no issues found in 491 source files |
| `uv run ruff check .` / `uv run ruff format --check .` | clean |
| `uv run python scripts/gen_frontend_types.py` | regenerated; `api.ts` only |
| `npm --prefix frontend run tsc:check` | exit 0 |
| `npm --prefix frontend test` | 20 files, 528 tests passed |
| `cd frontend && npm run e2e` (a served DTO moved) | 13 passed, 3 skipped |
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
yields four of the five -- this meeting is one of the seventeen
`_MOVEMENT_CHANNEL_DIVERGING_MEETINGS` whose fifth flag rests on the private
movement channel a replay cannot rebuild, which the corpus walk already pins.

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
  `TestEveryRegisteredSetRendersAnAlibi` red for that set (`2 failed, 13 passed`
  over the selected ids); reverted, `15 passed`.
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
