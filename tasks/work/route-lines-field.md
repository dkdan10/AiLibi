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

- [ ] **The field: declared last, validated, omitted at default, format 1.** Mechanism: the model, its validator and
  serializer. `route_lines_version: Literal[1] | None = None` follows `kill_cooldown_ticks`, joins
  `_literal_versions_are_integers`, `FIELD_LAYER` (`meeting`) and `OMITTED_AT_DEFAULT`, and stays out of
  `_PRE_WAVE_VALUES`. Proof, in a new `tests/meetings/test_route_lines_arm.py`: 0, 2, `True`, `1.0` and `"1"` raise;
  1 round-trips and dumps the key; `None` dumps none and `is_default` holds; `wave_settings` names it;
  `has_tactical_changes` is False; round 2's declared file plus `"route_lines_version": 1` validates at format 1,
  and without the key it equals that file byte for byte. Perturbed: the field dropped from `OMITTED_AT_DEFAULT`
  fails `test_every_committed_recorded_payload_reserializes_byte_for_byte` at the first archive row and a new test
  that re-serializes every committed `experiment-config.json` under `replays/`.
- [ ] **The profile, config-only, and its refusals.** Mechanism: `MeetingEvidenceProfile` gains the field;
  `CONFIG_ONLY_PROFILE_FIELDS` gains it; the account refusal covers it; a new validator refuses it beside
  `evidence_reasoning_version == 2` (two walking readers with different timing rules on one page). Proof: no
  environment sets it (the existing Hypothesis case, with `AILIBI_ROUTE_LINES` and `AILIBI_ROUTE_LINES_VERSION`
  added to its names); the both-ways `HeadlessGame` check holds for it by parametrization; each refusal raises
  naming the field; the runner refuses it beside each legacy overlay and for a set whose vote body has no live
  guard. Planted: each refusal deleted turns exactly its test red.
- [ ] **The stamp, derived and served from one source.** Mechanism: `EXPERIMENT_ARM_TEMPLATES` gains
  `"route_lines_version": ("vote_ballot",)`. Proof: the suffix is `route_lines_v1`; `prompt_versions_for_set`
  serves `vote_ballot.qwen3_6_27b.v8.route_lines_v1` only for a config carrying the field; for round 3's config it
  serves the composite of three arms in declaration order, the two adopted stamps of Evidence then that one; it
  returns the default registries by identity otherwise; no arm stamp equals a default or overlay stamp
  (`tests/agents/test_bespoke_prompt_sets.py`, `_BALLOT_ARM_STAMPS` gains the cases). Perturbed: a hand-written
  suffix fails the derivation test; a pin omitting the arm while the profile renders it is refused.
- [ ] **One home for the stated places and the reconcile rule.** Mechanism: `Placement`, `PlacementKind`, its sort
  key, the alibi-stay reader, `spoken_placements`, `placements_of`, `reconcilable` and its spot protocol move from
  `experiments/lab/route_check_replay.py` into a new `meetings/route_lines.py`, bodies byte for byte, and the lab
  imports them back and keeps no copy. Proof: `python -m experiments.lab.route_check_replay --check` reproduces the
  committed JSON and report byte for byte, and `tests/experiments/test_route_check_replay.py` passes unchanged.
  Planted: an `ast` test fails if a module besides `meetings/route_lines.py` defines either of the two functions.
- [ ] **The builder is pure and role-blind.** Mechanism: `build_route_lines(*, transcript, candidate_targets,
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
- [ ] **The planted cases.** Mechanism: the builder and the rendered block, read back. Each case scripts a meeting
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
- [ ] **A typed check refuses a line that would name a suspect, assert presence or claim a false link.**
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
- [ ] **The block renders only ON, only in the ballot, and parses back.** Mechanism: one guarded block,
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
- [ ] **Every reader of a ballot reads an ON ballot as before.** Mechanism: placement before `<evidence>`, no
  `## ` heading inside the block. Proof: on scripted ON ballots `_parse_suspicion_graph`, the rendered-maximum
  parse, the railroad tripwire and `served_own_kill_rows` return exactly what they return on the same ballots OFF.
  Planted: the block moved under the suspicion header fails the suspicion parse test.
- [ ] **The manager threads it to every ballot and to nothing else.** Mechanism: the ballot path calls the builder
  only when its profile's value is not `None`, over the final transcript, the voter's candidate targets and the
  run's regroup ticks, and passes `route_lines` and `route_lines_version` to the vote renderer;
  `VotePromptRenderer` and `vote_ballot_prompt` take both with defaults `()` and `None`. Proof: a recording stub
  captures both keywords at every ballot of a scripted ON meeting and at no report or statement render.
  Perturbed: the manager passing `()` fails the scripted ON golden below.
- [ ] **Fake and scripted rehearsals, on and off.** Mechanism: `HeadlessGame` with no environment, on round 2's
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
- [ ] **The golden's planted OFF leg.** Mechanism: the OFF gate. Proof: forcing the builder ON and the version to 1
  inside `meetings.manager` fails the golden at exactly the committed sample ballots whose transcript states, for
  a candidate, a change of room that walking or the regroup reconciles, a set measured here and pinned like
  `_KILL_HOLDER_MEETINGS`, and at no other.
- [ ] **Readers thread or refuse.** Mechanism: `READABLE_SETTINGS` gains the field; the six instruments and the
  golden read an ON recording through the walk; `FIELD_CLASSIFICATION` gains one not-read entry ("adds role-blind
  route lines to a ballot; no cell is forced by it"), which the census card later replaces. Proof: each instrument
  completes on the scripted ON recording; with the field removed from `READABLE_SETTINGS` each refuses naming it;
  the pin test expects the new set; the census classification test is green and the regenerated pages differ by
  that one row.
- [ ] **The mirrors and pages state it.** Mechanism: `ExperimentConfigView` gains the field with the same type and
  default; `scripts/gen_frontend_types.py` lists it optional; `frontend/src/types/api.ts` is regenerated;
  `tests/api/test_leak.py` allows the key; `_WAVE_FIELDS` gains it; `docs/experiment-arms.md` gains its row (meeting
  layer, this card), its place in the omitted-at-default list and the config-only and stamp paragraphs;
  `docs/glossary.md` gains "route line". Live-tense sentences that count two ballot arms are fixed
  (`orchestrator/game.py:527`, `meetings/manager.py:2392`, `meetings/render_contract.py:493`, `loader.py:1112`,
  `eval/recorded_settings.py:8` and `:36`, `eval/watchability.py:1595`, the template header). Proof: the
  view-mirror test; the page check bites the row deleted; `npm --prefix frontend run tsc:check`.
- [ ] **The pre-spend measurement, against (c).** Mechanism: a new `experiments/lab/route_lines_replay.py`, count
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
- [ ] **The record card's r3 column.** Mechanism: both instruments accept the label `r3`, declaring
  `replays/candidates/stage-b-r3/experiment-config.json`; on r3 the field instrument reads the served blocks.
  Proof: on a scratch set of scripted ON games, both run at a throwaway commit and the field's served reach equals
  its re-rendered reach; the committed outputs, which hold no r3 column, reproduce byte for byte. Planted: an r3
  set recorded under another config is refused, naming the column.
- [ ] **Nothing committed moves; the bundle diff is exactly the view key.** Mechanism: the `None` default and the
  omitted key. Proof at the branch head, in a bare shell: `verify_samples.sh` and `build_sample_report.py --check`
  for `samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` and `candidates/stage-b-r1/9p2i`; the
  golden over every committed set; `publish_process_scorecard.py --check`; the census `--check` after
  regeneration; `uv run pytest -m campaign`; `verify_ml_evidence.py` offline. `build_demo_bundle.py` at the merge
  base and the head: `diff -r` shows only `"route_lines_version":null` added to each served config view.
  Planted: the field's default set to 1 turns the committed-payload test and the golden red.
- [ ] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or
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

Not started. The implementer records: the commits; the sections relied on (this card, `docs/architecture.md`
"Enforced boundaries" and "Determinism and the substrate ladder", `docs/experiment-arms.md`, decision memo 0.3, the
route-check Reading, baselines memo D2); the decisions above; the served wording; each planted failure by test id;
the instrument's per-column table and token projection; the bundle diff; the mutation and neuter tables; and every
validation command with its exit code.
