# The route lines, a role-blind recorded field for the ballot

**Status:** ready

## Outcome

On round 2 the table charged players with moves the map or the public regroup in fact allows, and 40 such charges
ended in an ejection, 7 of them at a meeting a kill witness opened. The offline route-check replay found that the
existing walkable-pair clause shows a voter 15 of those 40 and the recorded `evidence_reasoning_version = 2` 16,
while a reference reading, check (c), reaches 29 of 40 and 7 of 7. The owner took round 3 as a spend on the narrow
field that reading sketches, and the orchestrator's reading (2) binds it: versioned, default off, set only from the
declared config file, its own stamp, at most one role-blind line per living candidate, rehearsed before any live
seed.

This card builds that field and proves it offline. It adds one meeting-layer `RecordedExperimentConfig` field,
`route_lines_version: Literal[1] | None = None`, omitted from every payload at its default. Recorded at 1, a
ballot of the served `qwen3_6_27b` set gains one guarded block, `<routes>`, between the `<map>` and `<evidence>`
blocks of `vote_ballot.j2`, whenever a candidate has a line. For each living candidate whose stated places at this
table change room in a way the doors or the public regroup allow, one line lists each such change in tick order and
says one of two things: the map links the two rooms within the ticks between (over any number of doors), or the
public regroup falls between them so walking cannot decide it. A change of room that neither allows is not
rendered, and a candidate with no allowed change has no line, so a line never says that a move was impossible. These
are exactly the pairs check (c) reaches with: the doctrine's two readings (decision memo 8.2 item 2) and nothing
more. The line is a pure function of what the voter already holds:
this meeting's transcript, which the same prompt renders; the map's doors, which the `<map>` card renders; and the
public regroup ticks, which the voter's memory announces. It reads no role, no private record and no engine state.
It never says a statement is true, never says where anyone was, and names, ranks or recommends no one.

The stamp is `vote_ballot.qwen3_6_27b.v8.route_lines_v1`, served through the spine's experiment-arm registry and
joined with `+` after the two adopted ballot arms; no prompt registry bump, and no other prompt moves. Before any
spend, the card measures the field as rendered on round 2's committed bytes through the route-check replay's
harness, against (c)'s 29 of 40 and 7 of 7 rather than assuming it equal, and proves every committed recording
verifies byte-identically. It records nothing and makes no live call; the recording is the record card's.

## Evidence

Every `path:line` below is a citation at `76270d6c`, the head of `main` and this card's base; earlier round-3
merges may move them, so each is re-anchored by its named symbol at dispatch. Every count is count-only, keyed by
(set, meeting), reproducible by the command or committed file beside it, and re-measured at dispatch.

**The ruling.** The owner, 2026-10-06, verbatim, item 2: "What is your recommendation? I slightly lean to spend
with narrow field, but would go with your recommendation". The orchestrator's binding reading (2): round 3 spends
on the narrow role-blind route field (baselines memo D2 option (a)), with planted cases, rehearsals and lab rows
before any live seed, seeds 0-49, the eight rules plus cooldown 6, and `evidence_reasoning_version = 2` unused; it
records only after this card merges, the rehearsals pass, the pre-registration lands and the owner confirms it.

**The measured failure.** `experiments/lab/results-route-check-replay.json`, column `r2`, `all` and `rule_inputs`
(`uv run python -m experiments.lab.route_check_replay --check` reproduces it; it needs history): 66 ejections, 40
misjudged (M), 7 at witness meetings (W); reach over M: (a) 15, (b) 16, (b-snapshot) 20, (c) 29; over W: (a) 2,
(b) 2, (c) 7; (c)'s charge-touching reach 28; (c)'s unreached reasons `kind` 9, `relevance_gate` 2. The Reading
(`tasks/work/route-check-replay.md:1452-1476`) adds that (c) reaches 21 of 21 misjudged innocent ejections and 5
of 5 ejected witnesses, and that reaching is showing a line, not changing a vote.

**Why neither existing check.** (a) is the corroboration ledger's walkable-pair clause, one hop in one tick
(`_walkable_transits`, `meetings/corroboration.py:561`; `meetings/constants.py:62-63`), behind an ambient switch.
(b) renders into the memory block, which holds the store as it stood at the meeting's open; reported testimony is
absorbed only after a meeting (`orchestrator/game.py:3625`; the ballot's memory, `meetings/manager.py:2335-2341`),
so (b) never holds this meeting's own claims, and the memory budget shed 13 of its unreached r2 cases (`cap`). (b)
also needs format 2 and temporal observations version 2 (`orchestrator/experiment_config.py:103-131`;
`orchestrator/game.py:1576-1582`), which the round does not use. So the field renders beside the memory block, as
a ballot render input the meeting layer builds, the way `evidence_rows` are built (`meetings/manager.py:2351`).

**Reference check (c), at `experiments/lab/route_check_replay.py`.** Placements are the spoken kinds
`C_INPUT_KINDS` (`:207`: sightings, their company, movement destinations, whereabouts, alibi stays; never a vent
sighting), read through `reconstruct_stated_paths` with the speakers' own movement records and the relevance gate
(`c_spots`, `:919-949`); a pair reconciles by `reconcilable` (`:562-582`: a walk when `1 <= hops <= elapsed` over
the whole map, `max_hops=len(CANONICAL_ROOMS)` at `:575`; else the regroup when `earlier < tick <= later`); (c)
reaches a case when the ejected has any reconcilable pair (`_read_case`, `:1585-1735`). Like (c), the field shows
only reconcilable pairs, through the same `reconcilable`. It differs from (c) on three points, each forced or chosen
here and measured, never assumed:
- **No speaker's own record.** (c) places a spoken move only where the speaker's record confirms it
  (`meetings/transcript.py:1415-1582`, the `movement_witness_records` argument). A line that moved with a third
  party's private record would tell every voter whether that speaker's account was borne out, which is an honesty
  assertion. The field reads spoken placements only, as `spoken_placements` (`:474-553`) does.
- **No relevance gate.** The gate drops spawn-window and regroup-window sightings because they cannot exculpate
  (`meetings/transcript.py:1250-1310`); a route line exculpates no one, and the regroup branch already names a
  crossing.
- **Consecutive changes of room only.** Every pair of a candidate's placements grows with the square of their
  number; consecutive pairs grow with it linearly, and for single-room placements a chain of walkable steps implies
  every longer pair walks (the doors obey the triangle inequality). A consecutive change of room that neither walks
  nor crosses the regroup is left out of the line, never rendered as a third reading. The instrument's every-pair
  leg reports what the rule gives up, so the choice is reproducible from committed evidence after delivery.

**What the voter already holds.** The ballot renders the meeting's typed turns (`<transcript>`,
`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:190-231`) and the map's doors (`<map>`, `:279-285`, built from
`CANONICAL_MAP_CARD`, `agents/strategic/prompts/loader.py:514`). That card and the adjacency the field reads are
one table, `CANONICAL_ROOM_NEIGHBORS` (`meetings/transcript.py:918`), data inside `meetings/` so that `agents/`
never reaches `engine/`, pinned to the engine map by `TestCanonicalRoomNeighborsPin`
(`tests/meetings/test_contradictions.py:4299`) and to the card by
`test_map_card_is_the_engine_map_and_the_detectors_table` (`tests/agents/test_bespoke_prompt_sets.py:741`).
`room_hops` (`meetings/transcript.py:3474`) walks it. The regroup ticks reach the manager as
`MeetingManager.run(regroup_ticks=...)` (`meetings/manager.py:1264`, public by its docstring at `:1293-1310`),
derived by `derive_regroup_ticks` (`orchestrator/replay.py:1498`); the voter's memory announces each one (the
census cell `prompts_missing_a_regroup_notice` reads 0/722 on the shown set, `docs/gameplay-census.md:221`).

**The spine pattern this field follows.** The ballot arms are `Literal[1] | None` meeting fields
(`orchestrator/experiment_config.py:64-65`), integer-checked (`:70-87`), omitted at default under every format by
value (`OMITTED_AT_DEFAULT`, `:242`; `_omit_wave_fields_at_default`, `:167`), so the wave's config keeps
`format_version` 1 and the decision memo rules out a format 4 (`tasks/decision-2026-09-24-stage-b-wave.md`, 0.3
item 2). The format ladder (`:103-131`) is the pre-wave mechanism: evidence version 2 and the account profiles need
format 2 because their omission keyed on format, and evidence version 2 also needs temporal delivery. This field
needs neither: it reads the public transcript legacy delivery already records. The profile mirrors the meeting
layer (`MeetingEvidenceProfile`, `meetings/evidence_profile.py:75`; `CONFIG_ONLY_PROFILE_FIELDS`, `:69`; the
account refusal, `:103`); `HeadlessGame` holds config-only fields equal both ways (`orchestrator/game.py:2558`).
`EXPERIMENT_ARM_TEMPLATES` (`orchestrator/game.py:536`) derives each stamp suffix (`experiment_arm_suffix`, `:545`);
the fold composes in field-declaration order (`:839-870`); the runner refuses an arm beside a legacy overlay or
for a set with no live guard (`:1605-1625`, `require_guarded_bodies`, `loader.py:1254`) and an explicit pin that
does not credit what the profile renders (`:1663-1679`). The round-2 ballots carry
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1` (its MANIFEST).

**Readers.** `READABLE_SETTINGS` (`eval/recorded_settings.py:40-53`) is read whole by six instruments (evidence
honesty, funnel, kill-craft, solvability, win-condition, the watchability referee) and by the golden
(`tests/meetings/test_prompt_byte_golden.py:765`), pinned by
`test_the_readable_settings_are_the_wave_fields_and_redistribution` (`tests/eval/test_recorded_arm_readers.py:309`).
Ballot parsers read the suspicion block only (`eval/meeting_quality.py:403`; the railroad tripwire,
`eval/validity.py:984`); the census's own-kill pattern reads `<evidence>` rows (`eval/gameplay_census.py:227`).
`FIELD_CLASSIFICATION` (`eval/gameplay_census.py:488`) must name every config field, both ways
(`tests/eval/test_gameplay_census.py:749`), and the census pages print it (`_field_classification_view`, `:3901`).

**The shown bundle carries the view.** `ExperimentConfigView` (`api/schemas.py:1432`) mirrors every config field
(`test_the_view_mirrors_every_config_field_value_and_default`, `tests/orchestrator/test_experiment_arms.py:929`),
and the shown set's served metadata dumps every view key, null defaults included:
`uv run python -c "from pathlib import Path; from api.replay_loader import ReplayLoader;
m=ReplayLoader(replay_dir=Path('replays/samples/9p2i')).list_replays();
print(len(m), sum('\"evidence_reasoning_version\":null' in x.model_dump_json() for x in m))"` prints `50 50`.
The bundle writes those views (`scripts/build_demo_bundle.py:339`, `:365`), so the mirrored field adds one null key
to each served config view: a public-payload byte change, though no behaviour ships.

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written first and fails
at the base for the stated reason; Results quotes that run. Tests over committed bytes compare digests or booleans,
so a failure prints no prompt or transcript text.

- [x] **The field: declared last, validated, omitted at default, format 1.** Mechanism: the model, its validator and
  serializer. `route_lines_version: Literal[1] | None = None` follows `kill_cooldown_ticks`, joins
  `_literal_versions_are_integers`, `FIELD_LAYER` (`meeting`) and `OMITTED_AT_DEFAULT`, and stays out of
  `_PRE_WAVE_VALUES`. Proof, in a new `tests/meetings/test_route_lines_arm.py`: 0, 2, `True`, `1.0` and `"1"` raise;
  1 round-trips and dumps the key; `None` dumps none and `is_default` holds; `wave_settings` names it;
  `has_tactical_changes` is False; round 2's declared file plus `"route_lines_version": 1` validates at format 1,
  and without the key it equals that file byte for byte. Perturbed: the field dropped from `OMITTED_AT_DEFAULT`
  fails `test_every_committed_recorded_payload_reserializes_byte_for_byte` at the first archive row and a new test
  that re-serializes every committed `experiment-config.json` under `replays/`.
- [x] **The profile, config-only, and its refusals.** Mechanism: `MeetingEvidenceProfile` gains the field;
  `CONFIG_ONLY_PROFILE_FIELDS` gains it; the account refusal covers it; a new validator refuses it beside
  `evidence_reasoning_version == 2` (two walking readers with different timing rules on one page). Proof: no
  environment sets it (the existing Hypothesis case, with `AILIBI_ROUTE_LINES` and `AILIBI_ROUTE_LINES_VERSION`
  added to its names); the both-ways `HeadlessGame` check holds for it by parametrization; each refusal raises
  naming the field; the runner refuses it beside each legacy overlay and for a set whose vote body has no live
  guard. Planted: each refusal deleted turns exactly its test red.
- [x] **The stamp, derived and served from one source.** Mechanism: `EXPERIMENT_ARM_TEMPLATES` gains
  `"route_lines_version": ("vote_ballot",)`. Proof: the suffix is `route_lines_v1`; `prompt_versions_for_set`
  serves `vote_ballot.qwen3_6_27b.v8.route_lines_v1` only for a config carrying the field; for round 3's config it
  serves the composite of three arms in declaration order, the two adopted stamps of Evidence then that one; it
  returns the default registries by identity otherwise; no arm stamp equals a default or overlay stamp
  (`tests/agents/test_bespoke_prompt_sets.py`, `_BALLOT_ARM_STAMPS` gains the cases). Perturbed: a hand-written
  suffix fails the derivation test; a pin omitting the arm while the profile renders it is refused.
- [x] **One home for the stated places and the reconcile rule.** Mechanism: `Placement`, `PlacementKind`, its sort
  key, the alibi-stay reader, `spoken_placements`, `placements_of`, `reconcilable` and its spot protocol move from
  `experiments/lab/route_check_replay.py` into a new `meetings/route_lines.py`, bodies byte for byte, and the lab
  imports them back and keeps no copy. Proof: `python -m experiments.lab.route_check_replay --check` reproduces the
  committed JSON and report byte for byte, and `tests/experiments/test_route_check_replay.py` passes unchanged.
  Planted: an `ast` test fails if a module besides `meetings/route_lines.py` defines either of the two functions.
- [x] **The builder is pure and role-blind.** Mechanism: `build_route_lines(*, transcript, candidate_targets,
  regroup_ticks) -> tuple[RouteLine, ...]` in `meetings/route_lines.py`, importing only `meetings.*`, the standard
  library and pydantic. It takes each candidate's placements of `ROUTE_PLACEMENT_KINDS` (pinned equal to the lab's
  `C_INPUT_KINDS`), deduplicates them by tick and rooms, orders them by tick and rooms, and keeps as a step each
  consecutive pair in disjoint rooms that `reconcilable` reconciles: `walking_fits` when the doors are at most the
  ticks between, otherwise `regroup_between` naming the first regroup tick inside (earlier, later]; a walk wins over
  a crossing, and a pair that neither walks nor crosses is no step and is not rendered. A candidate with no step has
  no line, so a candidate has at most one line; lines follow `candidate_targets`. Proof: a test pins
  the signature to exactly those three keywords; an `ast` scan pins the imports; a Hypothesis property
  (`settings(deadline=None)`, the map loaded) over scripted transcripts shows every voter's line for a shared
  candidate identical, and any permutation of roles leaving every block byte-identical. Perturbed: a role read
  planted into the builder breaks that property.
- [x] **The planted cases.** Mechanism: the builder and the rendered block, read back. Each case scripts a meeting
  and asserts the parsed step:
  - WEST_HALL at tick 5, ADMIN at tick 6: one door, `walking_fits`;
  - ADMIN at tick 5, CAFETERIA at tick 7: two doors, `walking_fits`, while `_walkable_transits` links nothing;
  - REACTOR at tick 4, MEDBAY at tick 6 with a regroup at tick 5: `regroup_between`, tick 5, said so;
  - the same pair with no regroup: five doors in two ticks, no step, and a candidate with only that change has no
    line;
  - two rooms at one tick: no step; a pair that walks across a regroup reads as a walk;
  - a line with one non-reconcilable change between two reconcilable ones renders exactly the two;
  - a vent sighting adds no placement; a spawn-window sighting does; a compound label renders both rooms;
  - the voter, a dead player and a candidate with one room have no line.
  Neutered, each red on its own case: `max_hops=1`; the regroup branch removed; the walk-first order swapped; vent
  sightings admitted; the relevance gate applied; a non-reconcilable pair kept as a step.
- [x] **A typed check refuses a line that would name a suspect, assert presence or claim a false link.**
  Mechanism: `RouteStep` and `RouteLine` are frozen, `extra="forbid"` models with no free-text field; a step's rooms
  must be canonical and disjoint, its door count must equal `room_hops`, its reading is
  `Literal["walking_fits", "regroup_between"]` and must follow from doors, ticks and its regroup tick (a walk when
  the doors are at most the ticks; otherwise a regroup tick inside (earlier, later]); a line's steps are non-empty,
  and the builder refuses a subject outside the candidates. Proof: a line carrying a `suspect` key, a step reading
  `walking_fits` for REACTOR to MEDBAY in two ticks, the same step as `regroup_between` with no regroup tick inside,
  a `regroup_between` step where a walk fits, a wrong door count and a reading outside the two (for example
  `walking_does_not_fit`) each raise; a wording scan over the block's fixed text fails on each planted word
  (impostor, crewmate, suspect, guilty, innocent, lying, honest, true, confirmed, was in, were in, impossible). A property (`settings(deadline=None)`) holds every rendered step's doors and reading equal to a
  breadth-first search over `engine.world.load_canonical_map()` in the test; one door flipped in a scratch copy of
  the neighbour table, the sourced constant's planted source change, turns that property red.
- [x] **The block renders only ON, only in the ballot, and parses back.** Mechanism: one guarded block,
  `{% if route_lines_version is defined and route_lines_version and route_lines %}`, between `{% endif %}` of the
  map card (`vote_ballot.j2:285`) and `{% if evidence_rows %}` (`:287`), opening `ROUTE_BLOCK_OPEN` (`<routes>`)
  and closing `ROUTE_BLOCK_CLOSE`. Its fixed text is a header saying the lines read the places this table stated
  against the station's doors, that a line lists only the changes of room the doors or the public regroup allow,
  that a player with no line is not judged by this block, and that a line weighs no statement and says nothing
  about anyone's role; then one line per subject, for example
  `` - `p-3`, places stated at this table: REACTOR at tick 4 to MEDBAY at tick 6, 5 doors apart, the public ``
  `` regroup at tick 5 falls between, walking cannot decide it; MEDBAY at tick 6 to WEST_HALL at tick 7, 1 door ``
  `` apart, walking fits. `` (the implementer may refine the wording; tests pin the served text and Results quote
  it, and the example's two steps are themselves a planted case the typed check accepts). The
  loader raises when lines arrive with the version `None`. Proof: `parse_route_lines(render(lines)) == lines` (a
  Hypothesis property) and a malformed line inside the block raises; removing the block from an ON render gives the
  OFF render byte for byte for crew and impostor voters (a property, `_crew_byte_problems`' precedent); no other
  template of any set references `route_lines`; a dead guard is refused by `require_guarded_bodies`. Planted: a
  template copy that rewords a line parses to nothing and fails the round trip.
- [x] **Every reader of a ballot reads an ON ballot as before.** Mechanism: placement before `<evidence>`, no
  `## ` heading inside the block. Proof: on scripted ON ballots `_parse_suspicion_graph`, the rendered-maximum
  parse, the railroad tripwire and `served_own_kill_rows` return exactly what they return on the same ballots OFF.
  Planted: the block moved under the suspicion header fails the suspicion parse test.
- [x] **The manager threads it to every ballot and to nothing else.** Mechanism: the ballot path calls the builder
  only when its profile's value is not `None`, over the final transcript, the voter's candidate targets and the
  run's regroup ticks, and passes `route_lines` and `route_lines_version` to the vote renderer;
  `VotePromptRenderer` and `vote_ballot_prompt` take both with defaults `()` and `None`. Proof: a recording stub
  captures both keywords at every ballot of a scripted ON meeting and at no report or statement render.
  Perturbed: the manager passing `()` fails the scripted ON golden below.
- [x] **Fake and scripted rehearsals, on and off.** Mechanism: `HeadlessGame` with no environment, on round 2's
  declared config and on it plus the field. A fake turn states no place (the fake answers every list field empty,
  `llm/fake_provider.py:177-185`), so the fake games prove the field inert: at a seed named in Results they hold equal
  state hashes and events, rows that differ only in the config key and the `vote_ballot` stamp, and identical prompts
  with no block served. A scripted game (a new `tests/_helpers/scripted_routes.py` whose named turns state placements,
  with one ejection resting on a walkable pair) proves it served: ON, it serves both readings and states one
  change of room that neither walks nor crosses, which serves no step; against its OFF twin, each ON ballot minus
  its block equals the OFF ballot and the tally is the same. Proof: `ReplayLoader` reports
  `outcome_verified` and the golden's `walk_directory` reproduces every prompt of all four games. Perturbed: the
  scripted ON game walked with the field dropped from its profile fails the golden at every ballot that carries the
  block.
- [x] **The golden's planted OFF leg.** Mechanism: the OFF gate. Proof: forcing the builder ON and the version to 1
  inside `meetings.manager` fails the golden at exactly the committed sample ballots whose transcript states, for
  a candidate, a change of room that walking or the regroup reconciles, a set measured here and pinned like
  `_KILL_HOLDER_MEETINGS`, and at no other.
- [x] **Readers thread or refuse.** Mechanism: `READABLE_SETTINGS` gains the field; the six instruments and the
  golden read an ON recording through the walk; `FIELD_CLASSIFICATION` gains one not-read entry ("adds role-blind
  route lines to a ballot; no cell is forced by it"), which the census card later replaces. Proof: each instrument
  completes on the scripted ON recording; with the field removed from `READABLE_SETTINGS` each refuses naming it;
  the pin test expects the new set; the census classification test is green and the regenerated pages differ by
  that one row.
- [x] **The mirrors and pages state it.** Mechanism: `ExperimentConfigView` gains the field with the same type and
  default; `scripts/gen_frontend_types.py` lists it optional; `frontend/src/types/api.ts` is regenerated;
  `tests/api/test_leak.py` allows the key; `_WAVE_FIELDS` gains it; `docs/experiment-arms.md` gains its row (meeting
  layer, this card), its place in the omitted-at-default list and the config-only and stamp paragraphs;
  `docs/glossary.md` gains "route line". Live-tense sentences that count two ballot arms are fixed
  (`orchestrator/game.py:527`, `meetings/manager.py:2392`, `meetings/render_contract.py:493`, `loader.py:1112`,
  `eval/recorded_settings.py:8` and `:36`, `eval/watchability.py:1595`, the template header). Proof: the
  view-mirror test; the page check bites the row deleted; `npm --prefix frontend run tsc:check`.
- [x] **The pre-spend measurement, against (c).** Mechanism: a new `experiments/lab/route_lines_replay.py`, count
  only, over the route-check harness's columns (s9, r1, r2, each read alone, r2 governing) and its walk, writing
  `report-route-lines-replay.md` and `results-route-lines-replay.json` with `--check`. A renderer wrapper renders
  each recorded ballot twice, as recorded and with the field ON. It reports per column: M, W and (c)'s reach,
  recomputed by the harness's own functions and held equal to the committed route-check JSON (a mismatch raises);
  the field's reach over M and over W read from the parsed ON blocks of the EJECT voters (a case is reached when
  some EJECT voter's block holds a step about the ejected; every rendered step is a reconciling one, so reach counts
  reconciling steps only), its charge-touching reach and its unreached reasons; the every-pair informational leg;
  the consecutive changes of room left out because they neither walk nor cross; steps per reading; block
  characters per ballot; and the projected added input tokens (each call's recorded input tokens times block characters over prompt
  characters), beside round 2's 9,187,880 input tokens and the 17,500,000 ceiling. Proof: every r2 ON render minus
  its block equals the recorded prompt; the outputs carry no rendered line or turn text (the harness's scan, with
  every rendered line added); planted, a (c) parity mismatch raises and a rendered line in an output is refused.
  The reach is reported as measured and gates no item; the pair rule is fixed before the run, never tuned to it.
- [x] **The record card's r3 column.** Mechanism: both instruments accept the label `r3`, declaring
  `replays/candidates/stage-b-r3/experiment-config.json`; on r3 the field instrument reads the served blocks.
  Proof: on a scratch set of scripted ON games, both run at a throwaway commit and the field's served reach equals
  its re-rendered reach; the committed outputs, which hold no r3 column, reproduce byte for byte. Planted: an r3
  set recorded under another config is refused, naming the column.
- [x] **Nothing committed moves; the bundle diff is exactly the view key.** Mechanism: the `None` default and the
  omitted key. Proof at the branch head, in a bare shell: `verify_samples.sh` and `build_sample_report.py --check`
  for `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` and `candidates/stage-b-r1/9p2i`; the
  golden over every committed set; `publish_process_scorecard.py --check`; the census `--check` after
  regeneration; `uv run pytest -m campaign`; `verify_ml_evidence.py` offline. `build_demo_bundle.py` at the merge
  base and the head: `diff -r` shows only `"route_lines_version":null` added to each served config view.
  Planted: the field's default set to 1 turns the committed-payload test and the golden red.
- [x] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or
  changes, using only the eight operator classes F filter, S swap, N comparison, C constant, M message, T tuple
  member, B branch swap and L loaded source to literal. Each mutant runs alone against the touched suites and
  Results lists it; a survivor is killed by a new test or named equivalent with its reason. Results also carries a
  per-line neuter table: each production line and the test that goes red when it is neutered.

## Constraints

**House rules.** The engine stays a pure deterministic tick function, and replays from a seed stay byte-identical
within their recorded scope. LLMs run only at meetings; tactical decisions stay rule-based. Agents reason from
typed event memory and rendered inputs; `agents/` never imports `engine/` (import-linter and the firewall test).
No module-level mutable state; invalid input raises, with no silent fallback. No `AILIBI_*` lever and no
environment switch; the field is set only by a declared config. No prompt registry bump: the header marker stays
`vote_ballot.qwen3_6_27b.v8` and v9 stays unallocated. No recorded byte is edited, no history is re-scored, and the
corpus FROZEN line and the ML artifacts never move. Role-correctness is reported, never a gate: the instrument
splits reach by ejection class as description. Nothing pushes an agent toward the correct answer: the line is a
function of statements, as true for a lie as for an honest account. The meeting layer labels and never rewrites:
no guard, marker, tally or ballot field changes.

**Prompt copy.** The block's fixed text carries no task, audit or ruling id, no unexplained jargon and no
threshold arithmetic; its numbers are ticks and door counts read off the page's own map, and "regroup" is the
memory notice's own word. "route line" gets a glossary entry, named in Results.

**Wave, order and ownership.** Base `main` at `76270d6c` or later, after the orchestrator's doctrine commit and the
commit landing the four round-3 cards. Round 3's first wave is this card, `census-held-data-cells` and
`crew-idle-policy-lab`, dispatched in parallel. This card merges before the census card (an owner merge); the
census card then merges `main` and adds the items that import from this card; the idle-policy card merges whenever
it is ready, before F, re-capturing if this card landed under its fingerprint. F, the record's frozen head, is
`main` after all three merge and this card's rehearsals pass; the record card (`tasks/work/stage-b-record-r3.md`)
dispatches only then. One writer per file at a time, as the orchestrator's one-writer map assigns:
- Alone, and frozen from the record's first seed to its merge: `meetings/route_lines.py` (new),
  `meetings/evidence_profile.py`, `meetings/manager.py`, `meetings/render_contract.py`,
  `orchestrator/experiment_config.py`, `orchestrator/game.py`, the loader, `vote_ballot.j2`,
  `eval/recorded_settings.py`, `eval/watchability.py`, `api/schemas.py`, `scripts/gen_frontend_types.py`,
  `frontend/src/types/api.ts` and `docs/glossary.md`. `retire-temporal-evidence-v1` (ready) writes `meetings/` and
  `orchestrator/` too and stays undispatched while this card and the record are open.
- Alone in this wave: `tests/orchestrator/test_experiment_arms.py`, `tests/eval/test_recorded_arm_readers.py`,
  `tests/agents/test_bespoke_prompt_sets.py`, `tests/api/test_leak.py`; the held `rubric-extractor-era` shares the
  first two and stays undispatched.
- `meetings/route_lines.py` is the one home of `Placement`, `PlacementKind`, `_placement_key` (its sort key),
  `_alibi_stay_placements`, `spoken_placements`, `placements_of`, `reconcilable` (with its spot protocol),
  `ROUTE_PLACEMENT_KINDS`, `RouteStep`, `RouteLine`, the delimiters, `build_route_lines` and `parse_route_lines`.
  The census card imports them and never defines them; `meetings/` imports nothing from `eval/`
  (`test_the_meeting_layer_imports_nothing_from_eval`).
- `eval/gameplay_census.py`: this card writes exactly one not-read `FIELD_CLASSIFICATION` entry, forced by the
  both-ways classification test, and merges first; the census card then merges `main`, owns the file and replaces
  that entry with its route-field predicate. `docs/gameplay-census.md` and `.json` are regenerated, never
  hand-edited: here for that one classification row, then by the census card after it merges `main`.
- `experiments/lab/route_check_replay.py` and `tests/experiments/test_route_check_replay.py`: this card first (the
  seven lifted definitions, `Placement` to `reconcilable`, become imports from `meetings/route_lines.py`, and the
  `r3` label; the test file's
  imports only if strict mypy needs them), then the census card (its four charge functions and
  `is_witness_meeting`). The committed lab JSON and report stay byte-identical; the file is frozen from the first
  round-3 seed.
- `tests/orchestrator/test_experiment_config.py`: this card moves `len(OMITTED_AT_DEFAULT)` from 6 to 7 (`:316`)
  and adds the `_VERSION_PLAN` row; `crew-idle-policy-lab` moves the candidate count from 19 to 21 (`:427`).
  Distinct lines: either may merge first, and the second merges `main`.
- `tests/meetings/test_prompt_byte_golden.py`: this card (the planted OFF leg and its pinned ballot set), then the
  record card (one `_RETIRED_GUARD_PINS` row, after F).
- `docs/experiment-arms.md`: this card (the row, the omitted-at-default list, the config-only and stamp paragraphs),
  then the record card (its "Candidate round 3" heading and sentence); neither edits the Adopted arms paragraph that
  `frontend/src/lib/adoptedRules.test.ts` reads.
- `docs/artifacts.md`: serial, each writer re-deriving its own rows after merging `main`: this card the
  `experiments/lab/` row, the census card its census row (and the lab row's size if it moves), the idle-policy card
  the `audits/` row before F, the record card its `replays/candidates/` and `audits/` rows last.
- `tasks/README.md` (the inventory sentence) and this card's Status line are the orchestrator's, on `main`; the
  worker fills Results only. `tasks/decision-2026-09-24-stage-b-wave.md` and
  `tasks/direction-2026-09-19-process-over-outcome.md` are the doctrine commit's alone and are not edited here.

**The census contract, written by the census card.** The conformance cell is contracted here and written there
(`tasks/work/census-held-data-cells.md`, item 4), on this card's model. It reads the setting
`route_lines_version = 1` and the `vote_ballot` stamp crediting `vote_ballot.qwen3_6_27b.v8.route_lines_v1` (a game
carrying one without the other raises), parses each recorded ballot's block with this card's `ROUTE_BLOCK_OPEN`,
`ROUTE_BLOCK_CLOSE` and `parse_route_lines`, imported and never copied, into `RouteLine` and `RouteStep` values, and
re-checks each step on its own: the door count against its own breadth-first search over the engine map, the
reading against the rule (a walk when the doors are at most the ticks between, otherwise the first regroup tick in
(earlier, later]; a pair with neither is never rendered), and any regroup tick against `derive_regroup_ticks`. It
publishes, per (set, meeting): ballots carrying the block (`ballots_carrying_route_lines`), lines per meeting
(`route_lines_per_meeting`), steps by reading (`route_steps_by_reading`), presence (`meetings_with_a_route_line`)
and two cells guarded at 0 and planted: `route_lines_false_to_the_map` (a step whose doors, reading or regroup tick
disagree) and `route_lines_off_the_table` (a line naming a non-candidate or an unstated place, or a second line for
one candidate). A candidate has at most one line, a line one or more steps, and a step one of the two readings. The
census's charge library imports this card's placement reader and `reconcilable` from `meetings/route_lines.py`. A
line names only a candidate the transcript already places twice, so a holds-nothing reading that takes the block as
its own source changes no label.

**Decisions this card makes, recorded in Results.** (1) The name, type, layer and format 1, and the refusal beside
evidence version 2 (Evidence). (2) The lines are a ballot render input beside the memory block, not memory rows:
the orchestrator's "through the rendered-memory path" is read as the house rule that a model receives rendered
typed inputs, and the memory's open-time state and budget are why the lines cannot live inside it. (3) Spoken
placements only, no relevance gate, consecutive changes of room, no line for a candidate without one; each is
measured by the instrument against (c). (4) The placement reader and the reconcile rule move to one production
home. (5) No cap on lines or steps: the memory budget's shedding is what cost (b) 13 cases. (6) No tactical lab
arm: the field acts only at meetings, and the lab's fake ballots all SKIP. (7) Two readings only, the doctrine's
(decision memo 8.2 item 2): a step is a pair the map links within the ticks between or a move across the public
regroup, and a change of room that is neither is left out rather than rendered as a third, impossible-travel
reading, which would be a contradiction signal about a named candidate that no round-3 cell measures. With it, a
candidate has at most one line and no line when no change of room reconciles, as the memo's 8.2 item 2 states;
the instrument reports the changes left out.

**What stays out.** No live call, no `.env`, no recording, no era registration, no round-3 declared file (the
record card's). No viewer, featured-list or public-results change; no ML training, refit or corpus change; no
scorecard cell; no held-out band; nothing Expected scope rules out. The rubric and the README wait for their cards.

**Delivery and publication.** Branch `work/route-lines-field`, one PR into `main`, merged or fast-forwarded, never
squashed; never amend a pushed commit; merge `main` in, never rebase. Each commit body carries
`Card: tasks/work/route-lines-field.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR fills `.github/pull_request_template.md` and
ends with the Claude Code attribution line; agents post no PR comments. `bash scripts/check.sh` is reported with
its real exit code. The field is off on every committed set and no behaviour ships, but the mirrored view key
reaches the shown bundle's served metadata (Evidence), so the bundle diff is not empty and **the merge is the
owner's**. Omitting the view key at default instead would be a public-compatibility change to the view's serializer
and is not in scope; the orchestrator may route it as its own decision.

**Stop and ask** if: any committed recording, report, prompt stamp, census count or pre-existing honesty pin moves
under OFF; the bundle diff holds anything besides the view key; the route-check `--check` stops reproducing after
the lift; the field's measured reach over W is below (c)'s 7 of 7, or its reach over M is below (c)'s 29 (report
it with the per-reason table, and do not tune the rule to the replay); the projected added input would carry round
2's measured input past the 15,750,000 hard stop; or the wording seems to need a number beyond ticks and doors, a
role word, a citation id or a registry bump.

## Expected scope

- `meetings/route_lines.py` (new): the lifted placement reader and `reconcilable`, `ROUTE_PLACEMENT_KINDS`,
  `RouteStep`, `RouteLine`, the block delimiters and line pattern, `build_route_lines`, `parse_route_lines`.
- `meetings/evidence_profile.py`: the field, `CONFIG_ONLY_PROFILE_FIELDS`, the account refusal, the evidence-v2
  refusal. `meetings/manager.py`: the ballot path's builder call and two keywords, and its comment.
  `meetings/render_contract.py`: `VotePromptRenderer`'s two keywords and docstring.
- `orchestrator/experiment_config.py`: the field, its validator membership, `FIELD_LAYER`, `OMITTED_AT_DEFAULT`.
  `orchestrator/game.py`: the `EXPERIMENT_ARM_TEMPLATES` entry and its comment block, only.
- `agents/strategic/prompts/loader.py`: `vote_ballot_prompt`'s two keywords, the raise, the docstring.
  `agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`: the guarded block and the header comment.
- `eval/recorded_settings.py` (`READABLE_SETTINGS` and docstring), `eval/watchability.py` (the reads comment),
  `eval/gameplay_census.py` (one `FIELD_CLASSIFICATION` entry), `docs/gameplay-census.md` and
  `docs/gameplay-census.json` (regenerated).
- `api/schemas.py`, `scripts/gen_frontend_types.py`, `frontend/src/types/api.ts` (generated).
- `experiments/lab/route_check_replay.py` (the lifted definitions become imports; the `r3` label);
  `experiments/lab/route_lines_replay.py`, `experiments/lab/report-route-lines-replay.md` and
  `experiments/lab/results-route-lines-replay.json` (new); `docs/artifacts.md` (the lab row's count and size).
- `docs/experiment-arms.md` and `docs/glossary.md`.
- Tests: new `tests/meetings/test_route_lines.py` (builder, typed check, planted cases, properties, wording scan),
  `tests/meetings/test_route_lines_arm.py` (field, profile, stamp, runner, manager, rehearsals, readers),
  `tests/_helpers/scripted_routes.py` and `tests/experiments/test_route_lines_replay.py`; edits to
  `tests/orchestrator/test_experiment_arms.py`, `tests/agents/test_bespoke_prompt_sets.py`,
  `tests/meetings/test_prompt_byte_golden.py`, `tests/eval/test_recorded_arm_readers.py` and
  `tests/api/test_leak.py`; `tests/orchestrator/test_experiment_config.py` at two places only, the
  `len(OMITTED_AT_DEFAULT)` literal 6 to 7 (`test_the_omitted_fields_are_exactly_the_fields_the_wave_added`, `:316`)
  and a `_VERSION_PLAN` row naming `route_lines_version` as `meeting` (`:199`);
  `tests/experiments/test_route_check_replay.py` and `tests/meetings/test_ballot_arms.py` only if an import or a
  refusal message needs it.
- This card's Results only; its Status line is the orchestrator's.

Renderer test doubles elsewhere that need the defaulted keywords are permitted follow-through, named in Results.
Not in scope: `replays/`, `audits/`, `eval/validity.py`, `eval/meeting_quality.py`, `eval/process_scorecard.py`,
`eval/eras.py`, `agents/memory/`, `engine/`, `observation/`, `training/`, `frontend/src/components/`, `README.md`
and `tasks/README.md`.

## Record impact

**What moves: no recorded byte.** No committed recording, fixture, report, prompt stamp or count moves; no
committed payload carries the key, and the default renders today's bytes. Derived pages move for wording only: the
census classification row, and new lab outputs that no gate reads. A new field, stamp, block, readers and two
instrument rows exist; the field is recorded ON first by the record card, into `replays/candidates/stage-b-r3/9p2i`.

**Publication.** A push to `main` rebuilds the demo bundle (`.github/workflows/pages.yml`). No shown replay,
viewer component or featured game changes, but each served config view gains one null key, so the PR quotes the
whole-tree bundle diff and the merge is the owner's.

**Reading notes for the record card.** The instrument's r2 reach and token projection are offline counterfactuals
on round-2 bytes and the planning figure, not a prediction of the model; the round reads the field's served reach
on r3 beside (c), and its added-input planning figure is this card's projection on round-2 bytes. The conformance
cell `census-held-data-cells` writes (item 4) is the round's Conf. row for this field: `route_lines_false_to_the_map`
and `route_lines_off_the_table` are Conf. cells, and `meetings_with_a_route_line` is the presence count. A fake turn
states no place, so a fake recording serves no line and reads presence 0 (the field's inertness): served-line
presence comes from the scripted rehearsal, never the fake.

**Adoption, later and not here.** A promotion or re-record carries the key explicitly; graduation deletes the
switch and keeps the recorded key, a missing key meaning off (craft rule 3). Once round 3 records,
`route_lines_version = 1` means exactly this line; a revision adds a new value.

**Limitations that stay.** Reaching is showing a line, not changing a vote; the fake provider proves mechanics,
not reasoning. The field reads statements, so a lie placed at the table yields a line as plain as the truth. It
leaves vent-sighting pairs to the Proof paragraph, so (c)'s 9 vent cases stay unreached by design.

## Validation

```
uv sync --frozen
uv run pytest tests/meetings/test_route_lines.py tests/meetings/test_route_lines_arm.py \
  tests/experiments/test_route_lines_replay.py tests/experiments/test_route_check_replay.py \
  tests/orchestrator/test_experiment_arms.py tests/orchestrator/test_experiment_config.py \
  tests/agents/test_bespoke_prompt_sets.py tests/meetings/test_ballot_arms.py \
  tests/meetings/test_weighing_channel.py tests/meetings/test_prompt_byte_golden.py \
  tests/meetings/test_contradictions.py tests/eval/test_recorded_arm_readers.py \
  tests/eval/test_gameplay_census.py tests/api/test_leak.py -n 6
uv run lint-imports
# the lab: the reference stays reproduced, the field's rows reproduce (both need history)
uv run python -m experiments.lab.route_check_replay --check
uv run python -m experiments.lab.route_lines_replay --check
# nothing committed moves, at the branch head, in a bare shell
for s in samples/9p2i samples/4p1i ml_corpus/9p2i ml_corpus/4p1i candidates/stage-b-r1/9p2i; do
  bash scripts/verify_samples.sh "replays/$s"
  uv run python scripts/build_sample_report.py --sample-dir "replays/$s" --check
done
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py           # regenerate, then:
uv run python scripts/publish_gameplay_census.py --check
git diff --stat -- docs/gameplay-census.md docs/gameplay-census.json
uv run python scripts/gen_frontend_types.py --check
npm --prefix frontend run tsc:check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py               # offline; never --complete
uv run pytest -m campaign
# the bundle, at the merge base and at the head, into scratch outside the tree
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
diff -r <scratch>/bundle-base <scratch>/bundle-head
# the full gate, whole, in a clean worktree, with its real exit code quoted in Results
bash scripts/check.sh; echo "check.sh exit $?"
```

Every gate runs in a bare shell with no `AILIBI_*` export. The Playwright journey is not required (no viewer
component changes; the bundle diff is the publication proof), and `check.sh` runs the frontend legs.

## Results

Implemented on `work/route-lines-field` from `2275bdba`, with `main` merged in at `83806ab0`. Commits:
`6014c883` (the field), `93e8cfb8` (the offline instrument and its outputs), `0a8ad54b` (the merge of
`main`), `be712049` (sharper planted cases), `5b3a7d8d` (the read-off test), `215cebbd` (the page-check
case), and the docs commits that carry this Results section and the full gate's exit code. Nothing was
recorded and no provider was called.

**Sections relied on.** This card; `docs/architecture.md` "Enforced boundaries" (the builder imports only
`meetings.*`, the stdlib and pydantic; `agents/` reaches `meetings.route_lines` and never the engine or the
manager; `uv run lint-imports` green) and "Determinism and the substrate ladder" (the line is a pure function
of recorded bytes; every committed set re-renders byte-identically); `docs/experiment-arms.md`; decision memo
0.3 items 2, 4 and 5 (omit at default, derived stamps, config-only fields), 8.2 item 2 and 8.5; the
route-check card's Reading (`tasks/work/route-check-replay.md`); baselines memo D2 option (a), as the memo's
8.2 item 2 quotes it.

**Decisions.** The card's seven, as built:
1. `route_lines_version: Literal[1] | None = None`, declared last, meeting layer, format 1, omitted at default;
   the profile refuses it beside `evidence_reasoning_version = 2` (two walking readers with different timing
   rules on one ballot) and beside either account profile.
2. The lines are a ballot render input the manager builds beside the evidence rows, not memory rows: the memory
   holds the store as of the meeting's open and is budget-shed, which is what cost (b) its cases.
3. Spoken placements only (no speaker's own record), no relevance gate, consecutive changes of room, and no line
   for a candidate without one. Measured against (c) below.
4. The placement reader and `reconcilable` live in `meetings/route_lines.py`; the lab imports them back and keeps
   no copy (an `ast` test holds it).
5. No cap on lines or steps.
6. No tactical lab arm.
7. Two readings only: a consecutive change of room that neither walks nor crosses the regroup is left out, never
   rendered as an impossible move.

The orchestrator's rulings of 2026-10-06, each applied:
1. At most one line per living candidate with a stated change of room; steps read `walking_fits` or
   `regroup_between` only; the header says a player with no line is not judged by the block.
2. The pre-spend reach was measured before anything else was built (a scratch count over the committed r2
   cases, then the instrument): 31 of 40 and 7 of 7, above 29 and 7, so the build went on and the placement
   universe was not widened.
3. Fake games serve no line: the fake rehearsal proves inertness; the scripted rehearsal proves presence.
4. `RouteStep` and `RouteLine` are frozen, `extra="forbid"`, hold no free text and refuse a step whose door
   count or reading the map does not give; planted cases below.
5. Determinism: the prompt-byte golden re-renders every scripted ON ballot, and a property holds every block
   byte-identical under any permutation of roles.
6. Publication: the field is OFF on every committed set; the bundle diff, built in one checkout, is exactly one
   null `route_lines_version` key per served config view (below). The merge is the owner's.
7. The three baseline-9 sets, the shown set and the r1 candidate verify and rebuild byte-identically; the
   committed-payload test proves the default omits the key; the readers read it or refuse it.

**The served wording.** The block opens `<routes>` after the map card and closes `</routes>` before
`<evidence>`. Its fixed header: "Each line below takes the places this table stated for one player, in tick
order, and reads each change of room against the station's doors. A line lists only the changes of room the
doors allow within the ticks between, or that the public regroup falls between, which walking cannot decide; a
change of room that neither allows is left out. A player with no line is not judged by this block. A line
weighs no statement: a place said here reads the same whether or not the account behind it is accurate, and the
line says nothing about anyone's role." A line, as the card's example renders (a planted case the check
accepts, `test_the_example_line_is_accepted_and_served_as_the_card_words_it`): "- `p-3`, places stated at this
table: REACTOR at tick 4 to MEDBAY at tick 6, 5 doors apart, the public regroup at tick 5 falls between,
walking cannot decide it; MEDBAY at tick 6 to WEST_HALL at tick 7, 1 door apart, walking fits." "route line" is
defined in `docs/glossary.md`.

**The stamp.** `vote_ballot.qwen3_6_27b.v8.route_lines_v1`, derived (`experiment_arm_suffix`); round 3's config
(round 2's declared file plus the field) folds `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1+vote_ballot.qwen3_6_27b.v8.route_lines_v1`.
The header marker stays `vote_ballot.qwen3_6_27b.v8`; no registry moves.

**Tests written first.** Run against an export of `2275bdba` with the three new test files and the helper
copied in, the three modules fail at collection for the stated reason: `ModuleNotFoundError: No module named
'meetings.route_lines'` (twice) and `No module named 'experiments.lab.route_lines_replay'`.

**Planted and perturbed failures, each red at its own case** (test ids, all in the committed suites):
- Omission dropped from `OMITTED_AT_DEFAULT`: `test_without_its_omission_the_committed_payloads_and_files_fail`
  (the first archive row and both committed `experiment-config.json` files mismatch).
- The default planted at 1: `test_every_committed_payload_reads_the_field_off` (every committed payload,
  config file and replay set must read the field OFF), the view mirror test and the golden on all three walked
  sets go red. The byte test `test_every_committed_recorded_payload_reserializes_byte_for_byte` stays green
  under that plant, because the omission keys on the default; the read-off test was added for it.
- The route-lines row deleted from the contract page, or its value: `test_the_page_check_bites_the_route_lines_row`.
- Hand-written stamp: `test_a_hand_written_route_lines_stamp_fails_the_derivation_test`; pin omitting the arm:
  `test_a_pin_that_omits_an_arm_the_manager_renders_fails_the_one_source_check[route-lines]` and `[round-3]`.
- The lifted rule defined twice: `test_only_the_route_lines_module_defines_the_reader_and_the_rule`.
- Foreign imports: `test_the_module_imports_only_meetings_pydantic_and_the_stdlib`.
- A role read planted into the builder: `test_a_role_read_planted_into_the_builder_breaks_the_role_blind_property`.
- One door flipped in a copy of the neighbour table:
  `test_one_door_flipped_in_a_copy_of_the_table_turns_the_map_property_red`; the room table shrunk:
  `test_the_door_bound_follows_the_room_table`.
- Each planted word in the fixed text: `test_the_wording_scan_fails_on_each_planted_word[*]` (12 cases).
- A reworded template copy: `test_a_template_copy_that_rewords_a_line_fails_the_round_trip`; a dead guard:
  `test_a_dead_guard_is_refused`; lines without their version: `test_lines_handed_over_without_their_version_are_refused`.
- The block moved under the suspicion header: `test_the_block_moved_under_the_suspicion_header_fails_the_suspicion_parse_test`.
- The scripted ON game walked with the field dropped from its profile:
  `test_the_scripted_on_game_walked_without_the_field_fails_at_every_block`; the manager passing `()`:
  `test_the_manager_passing_no_lines_fails_the_scripted_on_golden`.
- The golden's OFF leg forced ON inside `meetings.manager`:
  `test_the_route_lines_forced_on_fail_the_golden_at_the_reconciled_ballots` fails at exactly the sample ballots
  whose voter's candidates hold a route line, recomputed from the bytes and pinned as (count, sha256 of the
  sorted `set:seed:meeting:voter` keys): 9p2i 665 ballots, 4p1i 86, no turn prompt.
- The field out of `READABLE_SETTINGS`: `test_each_instrument_refuses_it_once_the_field_leaves_its_reads[*]` (7)
  and `test_the_golden_refuses_it_once_the_field_leaves_its_reads`.
- A (c) parity mismatch: `test_a_parity_mismatch_raises`; a column pinned to other bytes:
  `test_a_column_the_route_check_replay_pins_to_other_bytes_raises`; a rendered line in an output:
  `test_a_rendered_line_in_an_output_is_refused`; an ON render moving more than its block or serving other
  lines: `test_an_on_render_that_moves_more_than_its_block_raises`, `test_an_on_render_whose_block_holds_other_lines_raises`;
  an r3 set recorded under another config: `test_an_r3_set_recorded_under_another_config_is_refused_naming_the_column`.
- A moved state hash in the fake rehearsal: inside `test_the_fake_rehearsal_is_inert`.
- The typed check: `test_the_typed_check_refuses[*]` (21 cases, among them a `suspect` key, `walking_fits` for
  REACTOR to MEDBAY in two ticks, `regroup_between` with no regroup tick inside, `regroup_between` where a walk
  fits, a wrong door count and `walking_does_not_fit`).
- The six neutered builder rules the card names, each red on its own case (mutation table): `max_hops=1`
  (M14's class; `test_the_door_bound_follows_the_room_table`), the regroup branch (M15,
  `test_a_change_across_the_public_regroup_names_the_regroup_tick`), walk-first swapped (M06/M12), vent
  sightings admitted (M01, `test_a_vent_sighting_places_nobody`), the relevance gate applied
  (`test_a_spawn_window_sighting_places_its_subject`), a non-reconcilable pair kept (neuter X29).

**The pre-spend measurement** (`uv run python -m experiments.lab.route_lines_replay --check` reproduces
`experiments/lab/results-route-lines-replay.json` and `report-route-lines-replay.md`; each column's route-check
records were recomputed and equal the committed route-check JSON meeting by meeting). Count only; r2 governs;
reaching is showing a line, not changing a vote, and no model ran.

| column | M | W | (c) over M | field over M | (c) over W | field over W | every pair over M | field's charge-touching | unreached: kind / consecutive / residual |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s9 | 50 | 0 | 32 | 33 | 0 | 0 | 34 | 28 | 17 / 0 / 0 |
| r1 | 29 | 0 | 20 | 22 | 0 | 0 | 23 | 20 | 6 / 1 / 0 |
| r2 | 40 | 7 | 29 | 31 | 7 | 7 | 32 | 29 | 9 / 0 / 0 |

On r2 the field reaches every case (c) reaches and two more (no relevance gate), and 21 of 21 misjudged innocent
ejections and 5 of 5 ejected witnesses, by ejection class as description; its 9 unreached cases all rest on a
vent sighting, which the field does not read. On r1 the field misses one misjudged innocent case (c) reaches:
its reconcilable pair is not a consecutive change of room (the every-pair leg reaches it).

| r2 | value |
| --- | --- |
| ballots / carrying the block | 691 / 665 |
| lines (one per player and meeting) / served over all ballots | 439 / 2,415 |
| steps: walking fits / regroup between | 1,343 / 25 |
| consecutive changes left out (neither walk nor regroup) | 51 |
| block characters per ballot / per ballot carrying it | 1,469.2 / 1,526.7 |
| input tokens: recorded / ballot calls / projected added / projected total | 9,187,880 / 5,681,204 / 331,015 / 9,518,895 |

The projected total sits under the 15,750,000 hard stop and the 17,500,000 ceiling (s9 projects +313,309, r1
+348,993). This is a planning figure on round-2 bytes, not a prediction of the model.

**Rehearsals.** Fake (seed 0, round 2's declared config and the same plus the field, recorded in a bare shell):
every row equal apart from the config key and the `vote_ballot` stamp, so equal state hashes, events and
prompts, and no block served (`test_the_fake_rehearsal_is_inert`). Scripted (`tests/_helpers/scripted_routes.py`,
seed 0): ON serves both readings, the opener's ADMIN to REACTOR change in one tick serves no step, and the one
ejection (the opener, at the first meeting) rests on the walk's second sighting; each ON ballot minus its block
equals its OFF twin and the tally (targets, confidences, outcome, ejected, post-meeting hash) is the same. All
four games report `outcome_verified` through `ReplayLoader` and re-render every prompt through the golden's
`walk_directory`. The seven instruments (kill-craft, the two funnels, solvability, win-condition, evidence
honesty, the watchability referee) complete on the scripted ON recording, and every ballot reader
(`_parse_suspicion_graph`, `_parse_valid_targets`, the rendered maximum, the railroad tripwire's read,
`served_own_kill_rows`) reads each ON ballot as its OFF twin.

**The bundle diff** (`uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base` with the
checkout at the merge base `83806ab0`, then the same with `--out <scratch>/bundle-head` at `5b3a7d8d`, one
checkout, exit 0 both): 109 files each, the same file set; `diff -rq` lists four files, all in the 9p2i set
(`data/9p2i/eval/summary.json`, `data/9p2i/replays.json`, `data/9p2i/replays/headless-seed-14.json`,
`data/9p2i/replays/headless-seed-19.json`), and each differs only by an added `"route_lines_version": null`
key in a served config view (five keys in all; removing them gives the base bytes). The 4p1i set and the
frontend assets are unchanged. No behaviour ships, but the public payload moves, so **the merge is the
owner's**.

**Mutation pass** (one bounded pass at `0a8ad54b`, the eight classes only, each mutant alone against its
targeted suite, restored from a copy; scratch harness, count only): 39 mutants, 39 killed, no survivor, none
named equivalent.

| id | class | site | first red test |
| --- | --- | --- | --- |
| M01 | F | `_route_spots` kind filter dropped | `test_a_vent_sighting_places_nobody` |
| M02 | T | `alibi_stay` dropped from the kinds | `test_every_route_kind_places_its_player` |
| M03 | T | `company` dropped from the kinds | `test_every_route_kind_places_its_player` |
| M04 | S | consecutive pairs swapped for every pair | `test_every_route_kind_places_its_player` (3 red) |
| M05 | N | `how is None` inverted | `test_one_door_in_one_tick_walks` |
| M06 | B | step reading branches swapped | `test_two_rooms_at_one_tick_are_no_step_and_a_walk_across_a_regroup_walks` |
| M07 | C | step `from_tick` a constant | `test_every_route_kind_places_its_player` |
| M08 | C | step `from_rooms` a constant | `test_a_compound_label_renders_both_rooms` |
| M09 | M | non-candidate refusal message a constant | `test_a_line_about_a_non_candidate_or_a_second_line_is_refused` |
| M10 | F | non-candidate refusal dropped | same |
| M11 | N | door comparison a None test | `test_the_typed_check_refuses[a wrong door count]` |
| M12 | N | walk comparison inverted | `test_two_rooms_at_one_tick_are_no_step_and_a_walk_across_a_regroup_walks` |
| M13 | C | validator's room read a constant | `test_one_door_in_one_tick_walks` |
| M14 | L | the door bound read as the literal 10 | `test_the_door_bound_follows_the_room_table` |
| M15 | C | regroup tick a constant | `test_a_change_across_the_public_regroup_names_the_regroup_tick` |
| M16 | F | parse's one-line-per-candidate check dropped | `test_a_malformed_line_inside_the_block_raises` |
| M17 | B | parse reading branches swapped | `test_the_example_line_is_accepted_and_served_as_the_card_words_it` |
| M19 | T | field dropped from the account refusal | `test_the_profile_refuses_it_beside_an_account_profile[public_account_version]` |
| M20 | N | evidence-v2 refusal's None test inverted | `test_the_profile_refuses_it_beside_version_two_evidence` |
| M21 | M | evidence-v2 refusal message a constant | same |
| M22 | T | field dropped from `CONFIG_ONLY_PROFILE_FIELDS` | `test_the_profile_carries_it_from_the_config_alone` |
| M23 | T | field dropped from the profile's integer check | `test_the_profile_refuses_a_value_other_than_one_or_none[True]` |
| M24 | T | field dropped from the config's integer check | `test_a_value_other_than_one_or_none_is_refused[True]` |
| M25 | T | field dropped from `OMITTED_AT_DEFAULT` | `test_none_dumps_no_key_and_is_the_default` (3 red) |
| M26 | C | `FIELD_LAYER` layer a constant | `test_the_wave_fields_and_the_derived_rows_sit_in_their_layers` |
| M27 | T | arm registry entry dropped | `test_the_stamp_is_derived_and_served_only_for_a_config_carrying_it` |
| M28 | N | manager gate inverted | `test_the_manager_threads_the_lines_to_every_ballot_and_to_nothing_else` |
| M29 | C | manager regroup ticks a constant | same |
| M30 | M | manager version argument a constant | same |
| M31 | S | manager candidates swapped for every participant | same |
| M32 | N | loader refusal's None test inverted | `test_two_rooms_at_one_tick_are_no_step_and_a_walk_across_a_regroup_walks` |
| M33 | M | loader lines argument a constant | same |
| M34 | B | template reading branches swapped | `test_the_example_line_is_accepted_and_served_as_the_card_words_it` |
| M35 | F | `and route_lines` dropped from the guard | `test_the_same_change_without_a_regroup_is_no_step_and_leaves_no_line` |
| M36 | C | door noun a constant | `test_the_example_line_is_accepted_and_served_as_the_card_words_it` |
| M37 | T | field dropped from `READABLE_SETTINGS` | `test_every_instrument_reads_the_readable_settings_whole` |
| M38 | N | instrument's served comparison inverted | `test_a_served_block_other_than_its_rebuilt_lines_raises` |
| M39 | F | instrument's subject filter dropped | `test_the_committed_r2_column_recomputes_from_the_checkouts_bytes` |
| M40 | B | unreached-reason branches swapped | `test_an_unreached_case_names_its_reason` |

Which probes first came back green: none in the pass itself. Three would have, by the planning analysis done
before the pass, and got a planted case before it ran: M14 (the door bound was an import-time constant, so no
source change could reach it; it became `_max_doors()`, read when asked, with
`test_the_door_bound_follows_the_room_table`), M23 (no profile-level integer test) and M40 (r2 holds no
consecutive case, so the committed recompute could not tell the reasons apart).

**Per-line neuter table** (each line or check neutered alone, restored from a copy). Lines the mutants above
already neuter are not repeated.

| id | line neutered | red |
| --- | --- | --- |
| X01 | the census `FIELD_CLASSIFICATION` entry | `tests/eval/test_gameplay_census.py::test_the_census_declares_its_own_layers_every_one_it_classifies` |
| X02 | `ExperimentConfigView.route_lines_version` | `test_an_older_payload_without_the_wave_keys_reads_as_defaults` |
| X03 | the generator's optional listing | `tests/api/test_view_model.py::test_generated_frontend_types_are_committed` |
| X04 | loader passes the version to the template | `test_the_example_line_is_accepted_and_served_as_the_card_words_it` |
| X05 | manager passes the lines | `test_the_manager_threads_the_lines_to_every_ballot_and_to_nothing_else` |
| X06 / X07 | the r3 declared path / `"r3"` in `COLUMN_LABELS` | `test_an_r3_column_is_read_from_its_served_blocks_by_both_instruments` |
| X08 / X09 / X10 | the instrument's strip, parse-back and recorded-OFF checks | `test_an_on_render_that_moves_more_than_its_block_raises`, `test_an_on_render_whose_block_holds_other_lines_raises`, `test_a_ballot_recorded_off_but_rendered_with_lines_raises` |
| X11 / X12 | the parity source and per-record checks | `test_a_column_the_route_check_replay_pins_to_other_bytes_raises`, `test_a_parity_mismatch_raises` |
| X13 / X14 | one render per participant; one line per player | `test_a_meeting_needs_one_ballot_per_participant_and_one_line_per_player` |
| X15-X21 | `RouteLine` subject, non-empty and tick-order checks; `RouteStep` disjoint, sorted, canonical and whole-number checks | `test_the_typed_check_refuses[...]`, one case each |
| X22-X26, X30, X31 | parse's header order, door noun, one block, closed block, blank line, non-empty block, line form | `test_a_malformed_line_inside_the_block_raises`, `test_a_template_copy_that_rewords_a_line_fails_the_round_trip` |
| X27 / X28 | the builder's input refusals | `test_the_builder_refuses_invalid_input` |
| X29 | a candidate with no step still given a line | `test_one_door_in_one_tick_walks` |
| X33 | the template's line prefix | `test_the_example_line_is_accepted_and_served_as_the_card_words_it` |
| X34 / X35 | the config and profile field declarations | collection of `tests/meetings/test_route_lines_arm.py` fails |
| X36 | `VotePromptRenderer`'s two keywords | strict mypy: `meetings/manager.py:2374: Unexpected keyword argument "route_lines_version"` |
| X37 | the lab's explicit re-export | strict mypy: `tests/experiments/test_route_check_replay.py:1997: ... does not explicitly export attribute "reconcilable"` |
| X32 | `or doors is None` in `_route_step` | equivalent: `reconcilable` returns `None` whenever the doors are `None`; the clause narrows the type for mypy |

Before the neuter pass, reading each check against its case showed three cases that also failed another check
(the lone off-map room had no doors; the boolean and negative tick cases broke the reading rule) and one check
no input could reach alone (forward ticks: a step whose ticks run back satisfies neither reading), so the cases
were sharpened and the check deleted. The pass then left one check green, X18 (the disjoint-rooms check, whose
overlap case also miscounted its doors); its case was sharpened and X18 re-ran red. Both are in `be712049`.

**Validation** (every command in a shell with no `AILIBI_*` export, at `be712049` unless noted; exit codes
captured directly):

| command | exit | result |
| --- | --- | --- |
| `uv sync --frozen` | 0 | 46 packages |
| the card's targeted pytest list, `-n 6` | 0 | 1,507 passed |
| `uv run lint-imports` | 0 | 4 contracts kept, 0 broken |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced (42.6 s) |
| `uv run python -m experiments.lab.route_lines_replay --check` | 0 | reproduced (43.6 s) |
| `bash scripts/verify_samples.sh` for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir replays/<set> --check`, the same five sets | 0 each | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py` then `--check` | 0 | consistent; `git diff --stat` 2 files, 2 insertions: the one classification row in `docs/gameplay-census.md` and `.json` |
| `uv run python scripts/gen_frontend_types.py --check` | 0 | `frontend/src/types/api.ts` gains one optional key |
| `npm --prefix frontend run tsc:check` | 0 | |
| `uv run python scripts/check_doc_facts.py` | 0 | doc facts, front door, ML program and budgets verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks, 390 prompts, 101 work cards |
| `uv run python scripts/generate_prompts.py --check` | 0 | |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | 63 checks: 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest -m campaign` | 0 | 337 passed |
| the default tier, `uv run pytest -n auto --dist loadfile`, on the tree committed as `6014c883` and `93e8cfb8` less the door-bound change and four later tests | 0 | 10,421 passed, 20 skipped, 3 xfailed |
| the field's default planted at 1 (scratch, restored) | red as planted | the read-off test, the view mirror test and the golden on all three walked sets go red; the byte test stays green, since the omission keys on the default and the bytes still round-trip |

`bash scripts/check.sh`, the full gate, ran once at `0bac2050` (the head carrying this Results section; the
commit recording this line changes this card only), in a shell with no `AILIBI_*` export, its exit code
captured directly: **exit 0**. Ruff check and format clean (559 files), import-linter 4 contracts kept,
`validate_task_docs` and `generate_prompts --check` clean, strict mypy clean over 530 source files, the default
tier 10,433 passed, 20 skipped and 3 xfailed, and the frontend lint, typecheck, 695 unit tests in 26 files and
build all passed.

**Limitations that stay.** Reaching is showing a line, not changing a vote; fake games prove mechanics, not
reasoning. A lie stated at the table yields a line as plain as the truth. Vent-sighting pairs stay unreached by
design (9 of r2's 40). The consecutive rule gives up one r1 case the every-pair leg reaches. The token
projection is a share of recorded prompt characters, not a tokenizer count. A model could quote a line's door
count in its rationale; the ballot's rationale rule already forbids bookkeeping figures, and the census card
counts what the block serves.

**Deviations, each named.**
- `tests/experiments/test_route_check_replay.py`, where the card allowed imports only: the hop-bound test now
  patches `meetings.route_lines.CANONICAL_ROOMS` (the rule's new home) and the unknown-label examples use `r4`
  (`r3` is now a known label), one import added; no assertion weakened.
- Five renderer test doubles gained the two defaulted keywords (`tests/agents/test_beliefs.py`,
  `tests/meetings/_manager_helpers.py`, `tests/meetings/test_corroboration.py`,
  `tests/orchestrator/test_meeting_integration.py`, `tests/orchestrator/test_replay_meetings.py`), the card's
  permitted follow-through.
- The lab re-exports the lifted public names (`Placement as Placement`, and so on), which strict mypy needs for
  the lab's tests; it defines none of them.
- The golden's forced-ON pin is a count and a sha256 per set rather than a literal tuple (751 ballots), so a
  failure prints no prompt; the test also recomputes the set from the bytes.
- The card's Status line and the `tasks/README.md` inventory sentence are left to the orchestrator (memo 8.5).
- The Playwright journey was not run: no viewer component changes (the card's Validation note); `check.sh`
  ran the frontend lint, typecheck, unit tests and build.
- `eval/vote_correctness.py:45` still says round 2's config carries two ballot arms: it describes that recorded
  config, which is true.
