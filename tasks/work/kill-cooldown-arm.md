# The kill cooldown becomes a recorded dial

**Status:** ready

## Outcome

Candidate round 1 read every conformance cell at zero and its impostors won 34 of 50 games, above
the pre-registered 0.60. The owner adopted the seven non-balance arms and ordered a balance round.
The orchestrator's application of that ruling (the decision memo's section 7) keeps the vent exit
`look_and_wait` and sets exactly one dial, the kill cooldown. Today the dial does not exist: the
kill cooldown is the map's constant, 4 ticks, and no recorded setting can change it.

This card adds one engine-layer field to `RecordedExperimentConfig`:
`kill_cooldown_ticks: int | None = None`, where `None` means the map's value. A recorded value sets
the cooldown at all three places the engine writes it: round start, after each kill, and at each
regroup. Every reader that re-simulates or measures a recording follows the recorded value: the
live game, the replay loader, the shared replay walk, the prompt-byte golden, the instruments that
name the settings they read, and the gameplay census. The census reads its grace window from the
recording, and a new census conformance cell checks the three writes against the recorded value.
The tactical lab gains arms at 6 and 8, so the record card can cite a mechanical projection beside
today's 4.

The field is default-OFF and omitted from every payload at its default. No committed recording,
report, fixture, prompt stamp or count cell moves. It is recorded ON only by the record card
(`tasks/work/stage-b-record-r2.md`), at 6, into `replays/candidates/stage-b-r2/9p2i`. It changes
how long an impostor waits between kills; it adds no prompt text and tells no agent anything it
does not already see, since an impostor already reads its own cooldown count.

## Evidence

Every `path:line` below is at `6acdac92`, the head of `main` and this card's base. That commit is
the adoption `docs:` commit; it touched only the decision memo, the direction memo and
`docs/experiment-arms.md`, so every code and test line is `cd1a8454`'s. Each is re-anchored by its
named symbol at dispatch. Every count is reproducible from the tree, the round-1 audit or the
decision memo, by the command or citation beside it, and is re-measured at dispatch.

**The ruling.** The owner ruled on 2026-10-01, verbatim: "Merge.  Adopt all 7 non-balance arms.
And run a balance round". Section 7 of the decision memo (`tasks/decision-2026-09-24-stage-b-wave.md`,
landed in `6acdac92`) is the source for what follows. It adopts the seven arms in the sense the
direction addendum defines, verbatim: "(declared ON in every later round; defaults untouched; the
shown set moves by the era-keyed promotion once a round sits inside the envelope)". The direction
addendum of 2026-10-01 (`tasks/direction-2026-09-19-process-over-outcome.md`, section 12, at
`6acdac92`) adds that "the project's documents describe them as the current game", and
`docs/experiment-arms.md` ("Adopted arms", same commit) does so. A missing key keeps its historical
meaning, so the baseline-9 sets keep verifying.

The rest is the orchestrator's application in memo 7, not the owner's words. `look_and_wait` stays.
Round 2 has exactly one dial, "a recorded kill-cooldown override field on the engine layer, first
value 6 ticks against the map's 4", and a pre-registered round-3 rule. Memo 7 states the rule's
first two branches ("win share above 0.60 at 6 names 8; below 0.20 names 5"). Both round-2 cards
carry the whole rule as this one sentence, verbatim:

> **The round-3 rule.** On round 2's point share of impostor wins: above 0.60 at 6 it names round 3
> at `kill_cooldown_ticks = 8`; below 0.20 it names round 3 at `kill_cooldown_ticks = 5`;
> otherwise, with no envelope flag and every Conf. cell at 0, it names the era-keyed promotion of
> round 2 for the owner to decide, else no step.

The third branch reads memo 7's adoption meaning: the promotion comes once a round sits inside the
envelope, and the envelope also flags reporter ejections above 0.104 per report meeting (memo
section 4; round 1's audit, 1.6). No ruling confirms that branch yet, so the record card asks the
owner to confirm the rule before its first seed. The rule names a step. It gates no acceptance item
of either card, and the step is the owner's.

Two cards carry round 2: this one and `stage-b-record-r2`. The memo's decision 0.3 item 2 (omit a
new field at its default) and item 6 (a recorded value's meaning is frozen) bind this field as they
bound round 1's.

**Round 1.** `audits/audit-2026-09-27-stage-b-r1.md`, section 6.3 (`:1101`): impostor win share
11/50 before, 34/50 = 0.68 (Wilson 0.54-0.79) after, flagged above 0.60. The arms landed together,
so the share is not attributable to one arm (`:1108-1113`).

**The rule today.** The map sets `kill_cooldown_ticks: 4` (`engine/maps/canonical_1.yaml:34`), and
`Map` refuses a value below 1 (`engine/world.py:284-285`). A kill needs cooldown 0
(`engine/rules.py:86-87`). Three writes set an impostor's cooldown from the map:
- round start: `seed_initial_state` (`orchestrator/seeder.py:111-113`);
- after a kill: `_apply_kill` (`engine/tick.py:413`); the killer is skipped by that tick's
  decrement (`cooldown_skip_players`, `:647`, `:662`), so it holds the full value after the tick;
- at a regroup: `regroup_after_meeting` (`engine/meeting_reset.py:36-40`), called only by
  `apply_meeting_result` under `meeting_reset = hub_with_grace` (`orchestrator/game.py:2208-2209`).

**Who re-simulates.** The live game, the loader, the walk and the golden each seed, advance and
apply meetings themselves:

| site | seed | advance | meeting applied |
|---|---|---|---|
| `orchestrator/game.py` (`run`, `run_unrecorded`, the shared loop) | `:2692`, `:2768` | `:2860` | `:3025` |
| `api/replay_loader.py` (`_walk`) | `:1514` | `:1639` | `:1807` |
| `eval/replay_walk.py` (`_walk_replay`) | `:639` | `:711` | `:822` |
| `tests/meetings/test_prompt_byte_golden.py` (`walk_replay_meetings`) | `:773` | `:795` | `:841` |

In the golden, `engine = engine_arguments(recorded)` runs at `:781`, after the seed at `:773`, so
passing the helper's value to the seed moves that line above it. The golden has a second walker,
`_first_meeting_state` (seed `:1503`, advance `:1519`), which seeds without the value. It reads only
`_SAMPLE_SETS[0]` (`:1945`), `replays/samples/9p2i`, whose recordings carry no config, and it stops
at the first meeting, so it applies no meeting. This card names it exempt (Constraints).

Every advance there already takes `**engine` from `engine_arguments`
(`orchestrator/experiment_config.py:313`), and an `ast` scan pins that for the first three modules
and the lab (`tests/orchestrator/test_experiment_arms.py:396-512`). The helper refuses an
engine-layer field it does not thread (`:313-344`). The other 16 production `seed_initial_state`
call lines either recover roles only (for example `eval/validity.py:358`) or read no experiment
recording; `audits/workflows/extract_gameplay_facts.py` refuses every experiment recording
(`refuse_experiment_settings`, `:184`). Count with `git grep -n "seed_initial_state(" -- '*.py'`.

**Cooldowns are hashed.** `WorldState.cooldowns` (`engine/world.py:66`) is inside the state hash
(`_state_hash`, `orchestrator/replay.py:2255-2257`). Unlike the physical witness rule, a reader that
re-simulates a cooldown-6 recording at 4 fails the hash of tick 0's row, because the seeded values
differ. What the hash chain cannot see is a writer and a reader that share the same mistake, for
example an engine that ignores the override: both then agree at 4. The census cell below is the
check for that case.

**The cooldown reaches model-facing text.** An impostor's memory renders "Your kill cooldown is N
ticks." (`agents/memory/store.py:2160-2169`). Count-only, 50 of 50 s9 recordings and 50 of 50
round-1 recordings carry that line (`grep -l` over each set's replay files, no text printed). So the
golden, which re-renders every recorded prompt from re-simulated state, is a reader of the field.

**The census reads the map.** `load_census_inputs` loads the canonical map
(`eval/gameplay_census.py:2756`) and publishes its cooldown as the set's grace window (`:2793`,
`_constants` `:3120-3124`). The grace-window cell counts kills with
`kill.tick - meeting.tick <= inputs.kill_cooldown_ticks` (`:1929`), and `census_from_inputs` refuses
to fold sets with different cooldowns (`:3141-3143`). A set whose games carry different settings
already raises `GameplayCensusEraError` (`resolve_era`, `:498-520`). `FIELD_CLASSIFICATION`
(`:369-409`) must name every config field, and its names are held equal to the model's both ways
(`tests/eval/test_gameplay_census.py:725`). Each entry is a `FieldUse` (`:346-359`), which accepts
exactly one of two kinds: read by named setting predicates, or not read, for a reason
(`__post_init__`, `:357-359`). A cell guarded `always` has no predicate, so neither kind states
truthfully that the census reads this field's value for the grace window and the cooldown cell;
the second would publish it as not read.

**Surfaces that list every config field.** `ExperimentConfigView` (`api/schemas.py:1432-1458`) with
the generated `frontend/src/types/api.ts:63-83` and the optional-key list in
`scripts/gen_frontend_types.py:312-318`; the view-mirror test
(`tests/orchestrator/test_experiment_arms.py:897-906`); the API key allowlist
(`tests/api/test_leak.py:495-515`); `READABLE_SETTINGS` (`eval/recorded_settings.py:37-49`), which
five instruments read whole (evidence honesty, funnel, kill-craft, solvability, win-condition) and
the golden reads too; the arm page `docs/experiment-arms.md` and its check (`_WAVE_FIELDS`,
`tests/orchestrator/test_experiment_arms.py:84-93`, `:933-1000`).
`test_the_readable_settings_are_the_wave_fields_and_redistribution`
(`tests/eval/test_recorded_arm_readers.py:309-321`) pins `READABLE_SETTINGS` to the eight wave fields
plus `redistribution_policy`, so it turns red when the field joins. The five instruments' "Recorded
settings" docstrings (`eval/evidence_honesty.py`, `eval/funnel.py`, `eval/kill_craft.py`,
`eval/solvability.py`, `eval/win_condition_selfcheck.py`), and those of `eval/recorded_settings.py`,
`eval/replay_walk.py` and `eval/gameplay_census.py`, say the engine settings reach the walk's
advances through the engine-arguments helper; after this card they also reach seeding and meeting
application.

**Nothing committed carries the key.** 0 of the 350 committed recordings under `replays/` contain
`kill_cooldown_ticks` (`grep -l` over `replays/*/*/replay-seed-*.jsonl` and
`replays/candidates/*/*/replay-seed-*.jsonl`). The spine's committed-payload test re-serializes
956 config rows in 101 files byte for byte (`tests/orchestrator/test_experiment_arms.py:189-193`).
Defaults on the engine entry points keep the test call lines still: 212 `advance_tick(`, 128
`seed_initial_state(`, 30 `apply_meeting_result(` and 2 `regroup_after_meeting(` lines under
`tests/` (`git grep -n -F` per name, definitions excluded).

**The lab today.** `experiments/tactical_gameplay.py` runs fresh fake games per arm
(`candidate_configs`, `:152`; `STAGE_B_FULL_SETTINGS`, `:131`, the four round-1 fields that act
during play). In `audits/tactical-gameplay/stage-b-r1-frozen-head.json` (audit 2.5, measured at
`f937dfaa`), `stage_b_full` reached impostor parity in 8 of 8 nine-player games, at 26 to 58 tick
rows (median 35.5), and in 7 of 8 four-player games, at 14 to 19 (median 17); read `counts.tick_rows`
of the rows whose `reason` is `IMPOSTOR_PARITY`. Tick rows are numbered from 0 with no gap, a
meeting's tick included, so a game's `tick_rows` is its game-over tick plus one (count-only on round
1's seeds 0-4: 43, 24, 24, 62 and 24 rows against game-over ticks 42, 23, 23, 61 and 23).

**The design: thread one value, do not substitute the map.** Two ways exist to make every read
follow the recording:
- Substitute the map once per recording (a copy of `Map` with the cooldown replaced). It needs no
  engine signature change, but `engine_arguments` would have to exempt one engine field from its
  refusal, and two maps with the canonical id would circulate (`WorldState.map` stores only the id),
  with nothing recorded to tell them apart. Each site's edit is no smaller: the loader reads
  `self._game_map` at its seed, advance and meeting calls.
- Thread the value (this card). `EngineArguments` gains the field, so every advance takes it with
  no edit, and nine call lines pass the same helper value to seeding and meeting application (the
  table above: three in the live game, two each in the loader, the walk and the golden). One
  resolver in the engine turns `None` into the map's value, so the rule is stated once.

The threaded design leaves the helper's refusal without exceptions, keeps one map per id, and costs
nine explicit lines against the substitution's comparable count. The committed-bytes test and the
four-set verification prove it moves no byte (Acceptance, last item).

## Acceptance

Each item names its enforcing mechanism and a planted or perturbed proof. Each new test is written
first and fails at the base for the stated reason; Results quotes that failing run.

- [ ] **The field, validated and omitted at its default.** `kill_cooldown_ticks: int | None = None`
  is declared after `impostor_ballot_version`, accepts only a true integer of at least 1 (checked
  before coercion, as `_literal_versions_are_integers` does), is assigned `engine` in `FIELD_LAYER`,
  sits in `OMITTED_AT_DEFAULT`, and stays out of `_PRE_WAVE_VALUES`, so a set value is a wave
  setting. Mechanism: the model's validator and serializer. Proof, in
  `tests/engine/test_kill_cooldown_override.py`:
  - 0, -1, `True`, `6.0` and `"6"` each raise a validation error;
  - a config at 6 round-trips and dumps the key; at `None` it dumps no key and `is_default` holds;
  - a cooldown-only config has `has_tactical_changes` False;
  - the round-2 declaration (round 1's eight non-default fields plus `kill_cooldown_ticks: 6`)
    validates with `format_version` 1.
  - Perturbed: the field removed from `OMITTED_AT_DEFAULT` fails
    `test_every_committed_recorded_payload_reserializes_byte_for_byte` at the first archive row.
- [ ] **One resolver, three engine writes.** One engine function (named in Results; for example
  `engine.world.resolve_kill_cooldown(game_map, kill_cooldown_ticks)`) returns the map's value for
  `None` and the integer otherwise, and raises `ValueError` for a non-integer or a value below 1.
  `advance_tick`, `_apply_action` and `_apply_kill`, `seed_initial_state`, `regroup_after_meeting`
  and `apply_meeting_result` each take `kill_cooldown_ticks: int | None = None` and resolve it
  through that function before changing any state; `advance_tick` raises before applying any
  action, as it does for an unknown witness rule. Proof:
  - at 6, every seeded impostor holds 6, a killer holds 6 on its kill tick's resulting state, and
    every living impostor holds 6 after a regroup;
  - at `None`, the same three reads give 4, the map's value;
  - 0 raises at each entry point, and the input state is unchanged.
  - Planted: each of the three writes restored to `game_map.kill_cooldown_ticks` fails its own case
    and only that case (three plants).
- [ ] **The helper threads it to every re-simulation site.** `EngineArguments` gains
  `kill_cooldown_ticks: int | None`, and `engine_arguments` returns the recorded value, or `None` for
  no config. The nine call lines in Evidence pass the helper's value to seeding and to meeting
  application; the advances already take `**engine`. Proof:
  - `test_no_config_threads_todays_engine_arguments` expects `"kill_cooldown_ticks": None`;
  - planted: `test_an_engine_field_the_helper_does_not_thread_is_refused`, parametrised over every
    engine field, takes 6 for this integer field; with the field left out of the threaded set the
    helper refuses, naming `kill_cooldown_ticks=6`;
  - the `ast` scan over the re-simulation modules stays green unchanged.
- [ ] **The reader gate: a site that forgets the value fails.** Mechanism: the hash chain at every
  reader, and direct value checks on the writer. The fixture, in
  `tests/eval/test_kill_cooldown_readers.py`, is one fake-provider game recorded into `tmp_path` by
  `HeadlessGame` with `RecordedExperimentConfig(kill_cooldown_ticks=6, meeting_reset="hub_with_grace")`
  and no environment. The test first asserts the game is not vacuous: at least one kill whose killer
  is alive on the next row, at least one regroup that resumes play with a living impostor, and a
  default re-simulation that fails a hash at a named tick. The seed and roster are named in Results.
  - The walk, with every tick and meeting hash verified, reads 6 at round start, after each kill
    and after each regroup.
  - `ReplayLoader` reconstructs it with `outcome_verified`.
  - The golden's directory walk reproduces every recorded prompt, and at least one recorded
    impostor prompt of the fixture, or of a second named seed, carries the cooldown line with a
    value above 4 (a regex count; no text printed).
  - Planted, parametrised over the thirteen calls in Evidence's table (nine seeding and meeting
    lines, four advances): the helper's value replaced by `None` at exactly one site makes the
    test fail, naming that site.
- [ ] **Every reader that names its settings reads the field, or refuses it.** `READABLE_SETTINGS`
  gains `kill_cooldown_ticks`, so the five instruments that read it whole, and the golden, read a
  cooldown recording through the walk. Any reader that does not name the field refuses it by name
  before its first advance (`refuse_unread_settings`).
  `test_the_readable_settings_are_the_wave_fields_and_redistribution`
  (`tests/eval/test_recorded_arm_readers.py:309-321`) expects the eight wave fields,
  `redistribution_policy` and `kill_cooldown_ticks`. The docstrings named in Evidence say the engine
  settings reach seeding and meeting application as well as every advance. Proof: each of the five
  instruments' walks completes on the reader-gate fixture with every hash its profile checks;
  perturbed, with the field removed from `READABLE_SETTINGS`, each refuses with a message naming
  `kill_cooldown_ticks`.
- [ ] **The census grace window follows the recording.** `load_census_inputs` resolves the set's
  era first and reads the window from it through the same resolver; `CensusInputs`, `_constants`,
  the grace-window cell's definition and the docstrings say "the recorded kill cooldown, else the
  map's". `FieldUse` gains a third kind, read as a value: a member naming what reads the field's
  value, with `__post_init__` requiring exactly one of the three kinds. `FIELD_CLASSIFICATION`
  classifies `kill_cooldown_ticks` with it, as read for the grace window's length and by the
  cooldown cell below, and the census pages render that row as read, not as not read. Proof:
  - a `FieldUse` with no kind, or with two, raises `ValueError`;
  - on the reader-gate fixture, the census built from the set publishes `grace_window_ticks` 6 and
    the grace-window cell reads 0 by construction;
  - planted, on a census carrier: a kill at T+5 after a regroup at meeting tick T in a cooldown-6
    era raises the cell's conformance breach naming seed and tick; the same carrier in the default
    era raises nothing;
  - perturbed: the window read from the map again fails the T+5 case;
  - a scratch set of one `None` game and one cooldown-6 game raises `GameplayCensusEraError`.
- [ ] **A census cell checks the three writes against the recorded value.** A new conformance cell,
  key `kill_cooldowns_differing_from_recorded`, title "Kill cooldowns that differ from the recorded
  value", is guarded `always`. It compares every impostor's cooldown at round start, on the state
  after each of its kills, and after each regroup, with the resolved value: the recorded override,
  else the map's. Its denominator is every write it checks. A new table,
  `kill_cooldown_writes_by_writer`, splits that denominator by writer, with rows `round_start`,
  `after_kill` and `regroup`, so each writer's count is visible. A breach raises naming set, seed,
  writer and tick. The record card's readings command reads both keys by these names. Proof:
  - on the reader-gate fixture it reads 0 of a non-empty count at each of the three writers;
  - on the four committed sets and round 1 it reads 0 against 4, a measured count, with the
    regroup row empty where no regroup ran;
  - planted, three cases: the engine's write left at the map's value at exactly one writer (the
    live game and the walk then agree and every hash passes) raises the breach naming that writer.
- [ ] **The validity gate covers it by homogeneity, unchanged.** `experiment_config_violations`
  (`eval/validity.py:424-443`) compares each game's normalized config with the declared one, so a
  game recorded at another cooldown fails `cost_and_provenance_exact`. Nothing in `eval/validity.py`
  changes. Proof: on a scratch set of two fake games, one at 6 and one at `None`,
  `scripts/validity_gate.py` with `--expected-experiment-config` at 6 fails
  `cost_and_provenance_exact`, naming the `None` game; with no expected config it fails that check
  naming the cooldown-6 game; on a set of two cooldown-6 games that check passes.
- [ ] **The lab has the dial and reports ticks to parity.** `candidate_configs` gains
  `stage_b_full_kill_cooldown_6` and `stage_b_full_kill_cooldown_8` (`STAGE_B_FULL_SETTINGS` plus the
  cooldown); `stage_b_full` is the 4 column. The output gains one top-level key, count-only: per arm
  and roster, the games, the parity games, and the minimum, median and maximum `tick_rows` of the
  parity games, with kills. No existing row changes shape. Proof:
  - `test_genuine_candidate_reconstructs_in_api_and_repeats` takes both arms: each reconstructs with
    `outcome_verified` and repeats byte for byte;
  - on a named seed whose `stage_b_full` game kills before tick 6, the 6 arm's first kill is at
    tick 6 or later and the 8 arm's at tick 8 or later, read from the replay's `Killed` events;
  - perturbed: the 6 arm run with the field withheld kills before tick 6 and fails that assertion;
  - the ten round-1 arms' rows equal `audits/tactical-gameplay/stage-b-r1-frozen-head.json` field for
    field, so no default path moved; `tests/orchestrator/test_experiment_config.py` counts 19 arms.
  - Results quote the count-only parity table for 4, 6 and 8 on development seeds 1000-1007, both
    rosters, from a run written outside the tree; this card commits no lab output.
- [ ] **The mirrors and the pages state the field.** `ExperimentConfigView` gains the field with
  the same type and default; `frontend/src/types/api.ts` is regenerated with it optional (one entry
  in `scripts/gen_frontend_types.py`); `tests/api/test_leak.py` allows the name. `_WAVE_FIELDS`
  gains it, and the page check accepts an integer field when its row spells `none` and "an integer
  of at least 1". `docs/experiment-arms.md` gains the field's row (engine layer), its place in the
  omitted-at-default list and one sentence on the helper and the two non-advance writes.
  `docs/glossary.md` gains "kill cooldown" (the ticks an impostor waits at round start, after a
  kill and after a regroup; the map's value unless a recording sets another), and its regroup entry
  says the cooldown restarts at that value. The census terms "grace window" and "regroup" say the
  same. No copy names a card, ruling or audit. Proof: the view-mirror test; the page check bites the
  row deleted; `npm run tsc:check`.
- [ ] **Nothing committed moves, and the bundle is byte-identical.** Mechanism: the `None` default
  and the omitted key. Evidence at the branch head:
  - the committed-payload test still counts 956 rows in 101 files;
  - `bash scripts/verify_samples.sh <set>` once per directory: the four sets and round 1;
  - the four `build_sample_report.py --check` runs, the candidate test and the golden;
  - `publish_process_scorecard.py --check`; `uv run pytest -m campaign`;
  - `publish_gameplay_census.py --check` after regenerating: every existing count, table and
    constant equals the base for the four sets, and the diff of `docs/gameplay-census.json` is only
    the new cell and table, the field's classification row, the grace-window cell's definition and
    the two terms;
  - `scripts/build_demo_bundle.py` at the merge base and the head; `diff -r` of the whole trees is
    empty.
  - Planted: a resolver that returns 6 for `None` turns the census `--check` and
    `verify_samples.sh replays/samples/4p1i` red; Results names both failures.

## Constraints

**The partial-record principle binds this card.**
- The field is default-OFF and omitted at its default; a missing key means the map's value, now and
  after adoption. A recording that adopts a value writes it explicitly.
- `engine/maps/canonical_1.yaml` is never edited for balance: every committed game would then
  re-simulate at a new cooldown and fail its hash chain.
- No `AILIBI_*` lever and no environment switch: the field is set only by a declared config.
- No prompt template, stamp or registry change. The cooldown line's value follows the game, as
  every rendered memory line does.
- Once round 2 records, `kill_cooldown_ticks = 6` means 6 ticks at round start, after each kill and
  at each regroup; a different meaning is a new field, never a redefinition.
- Role-correctness is reported, never a gate. Nothing pushes an agent toward an answer.

**Wave, order and ownership.**
- Alone, before the record card. Base: `main` at `6acdac92`, the adoption `docs:` commit, or later.
  The record card starts after this card merges.
- This card owns the code, the census, every test for the field, the field's row on
  `docs/experiment-arms.md`, the glossary entries and the regenerated census pages.
- The record card owns `replays/candidates/stage-b-r2/**`, its audit, the `docs/artifacts.md` and
  `audits/README.md` rows it moves, its sentence on `docs/experiment-arms.md` (after this card's
  edit), its golden pin and its own card. This card writes none of them.
- `tasks/README.md` and this card's Status line are the orchestrator's; the worker fills Results.

**Decisions this card makes, recorded in Results.**
- The value is threaded through `engine_arguments`, not substituted into the map (Evidence).
- The engine entry points keep a `None` default, so the test call lines do not move. The guard
  against a forgotten site is the hash chain plus the reader gate; against a shared mistake in
  writer and reader, the census cell.
- The census cell is guarded `always`, so the committed sets carry a measured 0 against 4: the
  record card's before column.
- `FieldUse` gains a third kind, read as a value, because an `always` cell has no setting predicate
  and the not-read kind would publish the field as unread (Evidence).
- The golden's `engine_arguments` line in `walk_replay_meetings` moves above its seed, so the seed
  can take the helper's value. `_first_meeting_state` is exempt: it reads only
  `replays/samples/9p2i`, whose recordings carry no config, and applies no meeting. Results names
  both.

**What stays out.**
- Nothing under `agents/`, `meetings/` or `observation/`. The tactical constants that mention the
  cooldown stay as they are: the pretend-task dwell (`observation/service.py:77-83`), the learned
  features' normalizer (`agents/tactical/features.py:138`) and the vote-correctness tick window
  (`eval/vote_correctness.py:215`). Results notes each as unchanged.
- No viewer code: `frontend/src/components/` is untouched. `PublicResults.tsx` names each recorded
  experiment and has no words for this field, so a shown group set apart only by its cooldown would
  read as having no enabled experiment. The label waits for the promotion that first shows such a
  round; the record card's decision menu lists it, so the promoting card owns it.
- No change to the recorder, `scripts/refresh_samples.sh`, `scripts/run_tournament.py`,
  `eval/validity.py`, the training scenarios or the `HeadlessGame` injected-state seam, which runs
  only unrecorded training games.
- No ML training, refit or corpus change; no scorecard cell; no held-out band.
- Fake provider and scripted clients only: no live call, no `.env`.

**Delivery.**
- Branch `work/kill-cooldown-arm`, one pull request into `main`, merged or fast-forwarded, never
  squashed. Never amend a pushed commit; bring `main` in by merging.
- Each commit body carries `Card: tasks/work/kill-cooldown-arm.md`, immediately followed by the
  exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- The PR fills `.github/pull_request_template.md` and ends with the Claude Code attribution line.
  Agents post no PR comments. Every merge is the owner's.

**Stop and ask** if:
- a committed recording, report, prompt stamp, existing census cell or the bundle moves;
- the golden needs an edit beyond its two call lines in `walk_replay_meetings` and moving that
  walker's `engine_arguments` line above its seed;
- a reader outside Expected scope needs the value;
- a re-simulation site cannot take the helper's value;
- the census diff reaches beyond the lines named in the last Acceptance item.

## Expected scope

- Engine:
  - `engine/world.py`: the one resolver, beside the map's own bound;
  - `engine/tick.py`: the keyword through `advance_tick`, `_apply_action` and `_apply_kill`, and its
    validation before any action applies;
  - `engine/meeting_reset.py`: the keyword on `regroup_after_meeting`.
- Orchestrator:
  - `orchestrator/experiment_config.py`: the field, its validator, `FIELD_LAYER`,
    `OMITTED_AT_DEFAULT`, `EngineArguments`;
  - `orchestrator/seeder.py`: the keyword and its docstring;
  - `orchestrator/game.py`: the keyword on `apply_meeting_result` and its docstring, and the
    helper's value at the two seeds and the live meeting application.
- Readers:
  - `api/replay_loader.py` and `eval/replay_walk.py`: the helper's value at seeding and meeting
    application, and the walk's docstring;
  - `eval/recorded_settings.py`: `READABLE_SETTINGS` and its docstring;
  - `eval/evidence_honesty.py`, `eval/funnel.py`, `eval/kill_craft.py`, `eval/solvability.py` and
    `eval/win_condition_selfcheck.py`: their "Recorded settings" docstrings only;
  - `eval/gameplay_census.py`: the third `FieldUse` kind, the classification, the window and the
    grace-window cell's definition, the new cell and table, the two terms, the docstrings;
  - `api/schemas.py`, `scripts/gen_frontend_types.py`, `frontend/src/types/api.ts` (generated).
- Lab: `experiments/tactical_gameplay.py`, the two arms and the parity summary.
- Docs: `docs/experiment-arms.md`, `docs/glossary.md`, `docs/gameplay-census.md` and
  `docs/gameplay-census.json` (regenerated).
- Tests:
  - new `tests/engine/test_kill_cooldown_override.py` (the field, the resolver, the three writes);
  - new `tests/eval/test_kill_cooldown_readers.py` (the reader gate, the readers, the census cell
    and window, the validity gate, the lab first-kill check);
  - `tests/meetings/test_prompt_byte_golden.py` (its two call lines in `walk_replay_meetings`, and
    that walker's `engine_arguments` line moved above its seed);
  - `tests/eval/test_recorded_arm_readers.py`
    (`test_the_readable_settings_are_the_wave_fields_and_redistribution`, `:309-321`);
  - `tests/orchestrator/test_experiment_arms.py`, `tests/orchestrator/test_experiment_config.py`,
    `tests/experiments/test_tactical_gameplay.py`, `tests/eval/test_gameplay_census.py` and
    `tests/api/test_leak.py`: the follow-through named in Acceptance.
- This card's Results.

Not in scope: `engine/maps/canonical_1.yaml`, `engine/rules.py`, `agents/`, `meetings/`,
`observation/`, `frontend/src/components/`, `eval/validity.py`, `replays/`, `audits/`,
`docs/artifacts.md`, `scripts/verify_ml_evidence.py`, `DESIGN.md` and `tasks/README.md`.

## Record impact

**What moves: nothing recorded.**
- No committed recording, fixture, report, prompt stamp or doc fact changes; 0 of 350 recordings
  carry the key, and the default reproduces today's three writes.
- Derived pages are regenerated for wording and one new measured cell: the census pages gain the
  cooldown cell and its table (0 against 4 on every committed set), the field's classification row,
  the grace-window cell's reworded definition and the reworded grace-window and regroup terms. No
  existing count moves.
- The API view and the generated types gain one optional field. No shown payload carries it, and
  no viewer code changes, so the bundle is byte-identical.
- The field is recorded ON first by the record card, at 6, in `replays/candidates/stage-b-r2/9p2i`.
  Its readings there use the census window and cell this card builds.

**Publication.** A push to `main` rebuilds the demo bundle (`.github/workflows/pages.yml`). This card
changes engine and reader code the bundle's loader runs, so the PR proves the whole bundle tree
byte-identical at the merge base and the head.

**The adoption consequence, stated now.** A missing key means the map's value for as long as any
committed recording lacks the key, which today is all 350. Adopting a cooldown therefore means every
later recording writes it explicitly, or every set in use is re-recorded. Changing the map instead
would silently re-derive every committed game at the new value, and the hash chain would refuse
them all.

**Limitations that stay.** The lab's fake games establish mechanics, not model play. The round-2
outcome cannot separate the cooldown from hosted generation's own variation; the record card states
that. The tactical constants named under Constraints were tuned at 4 and are not re-derived.

## Validation

```
uv sync --frozen
# targeted, while developing
uv run pytest tests/engine/test_kill_cooldown_override.py tests/eval/test_kill_cooldown_readers.py \
  tests/orchestrator/test_experiment_arms.py tests/orchestrator/test_experiment_config.py \
  tests/experiments/test_tactical_gameplay.py tests/eval/test_gameplay_census.py \
  tests/meetings/test_prompt_byte_golden.py tests/api/test_leak.py -q
uv run lint-imports
# nothing committed moves, at the branch head
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
bash scripts/verify_samples.sh replays/candidates/stage-b-r1/9p2i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py                 # regenerate, then:
uv run python scripts/publish_gameplay_census.py --check
git diff --stat -- docs/gameplay-census.md docs/gameplay-census.json
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout > <scratch>/r1-census.json
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/gen_frontend_types.py --check
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
uv run pytest -m campaign
# the lab, into scratch outside the tree; quoted count-only in Results
uv run python -m experiments.tactical_gameplay --split development --output <scratch>/lab.json \
  --arms baseline vent_risk vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full \
    stage_b_full_minus_look_and_wait stage_b_full_minus_own_fresh_kill \
    stage_b_full_minus_physical stage_b_full_minus_hub_with_grace \
    stage_b_full_kill_cooldown_6 stage_b_full_kill_cooldown_8
# the bundle, at the merge base and at the head
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
diff -r <scratch>/bundle-base <scratch>/bundle-head
# the full gate, whole, in a clean worktree, with its real exit code quoted in Results
bash scripts/check.sh; echo "check.sh exit $?"
```

Every gate runs in a bare shell with no `AILIBI_*` export. If `gen_frontend_types.py` has no
`--check` flag at dispatch, the generated file is compared by regenerating it and running
`git diff --exit-code -- frontend/src/types/api.ts`. The Playwright journey is not required: no
viewer code changes and the bundle diff is the publication proof; `check.sh` runs the frontend legs.

## Results

Not started. The implementer records here: the commits, the sections relied on (this card, the
decision memo's sections 0.3 and 7, the direction addendum of 2026-10-01, `docs/experiment-arms.md`
and `docs/architecture.md` "Determinism and the substrate ladder"), the decisions above, the
resolver's name, the reader-gate seed, each planted failure with its test id, the lab's parity
table, the census diff and every validation command with its exit code.
