# Make an alibi a route so honest movers stop contradicting themselves

**Status:** ready

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

- [ ] `AlibiClaim` is a route, in ONE claim type: it gains
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
- [ ] The detectors read SEGMENTS, and the one-segment case is bit-identical.
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
- [ ] The seed-41 shape is the adverse pair. A fixture from that meeting raises
  ZERO flags when `p-9`'s account is the four-segment route and still raises
  the five recorded flags when the same turn states the ENGINEERING 12-15
  envelope; a second fixture plants a flat lie (a one-segment route whose room
  the speaker held at no covered tick) and asserts one `alibi_vs_sighting`
  against it at today's band. Planted: dropping the segment comparison turns
  the honest route red, dropping the envelope case turns the liar green.
- [ ] The route crosses the firewall intact, with `ReportedStatement`
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
- [ ] The operational family asks for a route and shows one, every path below
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
- [ ] The version cascade is complete and this card takes the wave's FIRST
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
- [ ] The committed record is untouched and shown to be.
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
