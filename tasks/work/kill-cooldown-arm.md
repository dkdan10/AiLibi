# The kill cooldown becomes a recorded dial

**Status:** done

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

- [x] **The field, validated and omitted at its default.** `kill_cooldown_ticks: int | None = None`
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
- [x] **One resolver, three engine writes.** One engine function (named in Results; for example
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
- [x] **The helper threads it to every re-simulation site.** `EngineArguments` gains
  `kill_cooldown_ticks: int | None`, and `engine_arguments` returns the recorded value, or `None` for
  no config. The nine call lines in Evidence pass the helper's value to seeding and to meeting
  application; the advances already take `**engine`. Proof:
  - `test_no_config_threads_todays_engine_arguments` expects `"kill_cooldown_ticks": None`;
  - planted: `test_an_engine_field_the_helper_does_not_thread_is_refused`, parametrised over every
    engine field, takes 6 for this integer field; with the field left out of the threaded set the
    helper refuses, naming `kill_cooldown_ticks=6`;
  - the `ast` scan over the re-simulation modules stays green unchanged.
- [x] **The reader gate: a site that forgets the value fails.** Mechanism: the hash chain at every
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
- [x] **Every reader that names its settings reads the field, or refuses it.** `READABLE_SETTINGS`
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
- [x] **The census grace window follows the recording.** `load_census_inputs` resolves the set's
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
- [x] **A census cell checks the three writes against the recorded value.** A new conformance cell,
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
- [x] **The validity gate covers it by homogeneity, unchanged.** `experiment_config_violations`
  (`eval/validity.py:424-443`) compares each game's normalized config with the declared one, so a
  game recorded at another cooldown fails `cost_and_provenance_exact`. Nothing in `eval/validity.py`
  changes. Proof: on a scratch set of two fake games, one at 6 and one at `None`,
  `scripts/validity_gate.py` with `--expected-experiment-config` at 6 fails
  `cost_and_provenance_exact`, naming the `None` game; with no expected config it fails that check
  naming the cooldown-6 game; on a set of two cooldown-6 games that check passes.
- [x] **The lab has the dial and reports ticks to parity.** `candidate_configs` gains
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
- [x] **The mirrors and the pages state the field.** `ExperimentConfigView` gains the field with
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
- [x] **Nothing committed moves, and the bundle is byte-identical.** Mechanism: the `None` default
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

Implemented at `e164f57d` (`feat: the kill cooldown becomes a recorded dial`) on
`work/kill-cooldown-arm`, branched from `main` at `107956bf`; this Results commit follows it.
Sources relied on: this card; the decision memo's sections 0.3 (items 2 and 6) and 7; the
direction addendum of 2026-10-01; `docs/experiment-arms.md` ("Adopted arms", "One
engine-arguments helper"); `docs/architecture.md`, "Determinism and the substrate ladder" and
"Explicit cleanup experiments". No live call, no `.env`, no held-out band, no prompt text printed.

### What was built

- **The field.** `kill_cooldown_ticks: int | None = None` follows `impostor_ballot_version`. A
  before-mode validator refuses anything but a true integer of at least 1. `FIELD_LAYER` assigns
  it `engine`, it sits in `OMITTED_AT_DEFAULT`, and it is not in `_PRE_WAVE_VALUES`.
- **The resolver** is `engine.world.resolve_kill_cooldown(game_map, kill_cooldown_ticks)`, beside
  `Map`'s own bound. `None` returns the map's value; a non-integer (`bool` included) or a value
  below 1 raises `ValueError` naming the value. `seed_initial_state`, `advance_tick`,
  `_apply_action`, `_apply_kill`, `regroup_after_meeting` and `apply_meeting_result` each take the
  keyword with a `None` default and resolve it before changing any state.
- **The threading.** `EngineArguments` gains the field, so every advance takes it through
  `**engine`. Nine call lines pass the helper's value outside the tick: the live game's two seeds
  and its meeting application, and the seeding and meeting application of the loader, the walk and
  the golden's `walk_replay_meetings`. In the golden, the `engine_arguments` line moved above the
  seed. `_first_meeting_state` is exempt: it reads only `replays/samples/9p2i` and applies no
  meeting. The golden's docstrings are unchanged; they stay true.
- **The readers.** `READABLE_SETTINGS` gains the field. The five instruments that read it whole
  and the golden therefore read a cooldown recording. The "Recorded settings" docstrings of the
  five instruments, `eval/recorded_settings.py`, `eval/replay_walk.py` and
  `eval/gameplay_census.py` now say the engine settings reach the seeding, every advance and
  every applied meeting.
- **The census.**
  - `FieldUse` gains a third kind, `value_read_by`, and `__post_init__` requires exactly one
    kind. The field's row reads "read as a value by: the length of the grace window, and the
    value the kill cooldown cell checks every cooldown write against".
  - `load_census_inputs` resolves the set's era first and reads the window through
    `recorded_kill_cooldown(era, map)`, which calls the engine resolver.
  - The loader keeps every impostor's cooldown after each write as a `CooldownWrite` on
    `GameFacts.cooldown_writes`. The field defaults to empty, so a hand-built carrier checks none.
  - The cell `kill_cooldowns_differing_from_recorded` ("Kill cooldowns that differ from the
    recorded value") is guarded `always`. Its denominator is every write. The table
    `kill_cooldown_writes_by_writer` has the rows `round_start`, `after_kill` and `regroup`. Both
    sit under a new heading, "The kill cooldown".
  - A breach reads, for example, `set S, seed N, the after_kill write of p-3's cooldown at tick 12
    (4 against 6) breaches it`.
  - The grace-window cell's definition and the "regroup" and "grace window" terms say "the
    recorded kill cooldown, else the map's".
- **The lab.** `stage_b_full_kill_cooldown_6` and `stage_b_full_kill_cooldown_8`
  (`STAGE_B_KILL_COOLDOWNS`) bring the arm count to 19. The output gains the top-level key
  `ticks_to_parity`. No existing row changes shape.
- **The mirrors and pages.**
  - `ExperimentConfigView` gains the field, and `frontend/src/types/api.ts` is regenerated with it
    optional. `tests/api/test_leak.py` allows the name.
  - `_WAVE_FIELDS` gains the field, and the page check requires "an integer of at least 1" for an
    integer field.
  - `docs/experiment-arms.md` gains the row, the omitted-at-default name and the helper sentence.
    Its heading "The eight fields" became "The fields", and two sentences that counted eight
    fields were reworded.
  - `docs/glossary.md` gains "kill cooldown", and the regroup entry says the cooldown restarts at
    its full value, the map's unless the recording sets another.

### Decisions

- The value is threaded through `engine_arguments`, not substituted into the map (Evidence). The
  engine entry points keep a `None` default, so no test call line of the engine functions moved.
- The guard against a forgotten site is the hash chain plus the reader gate. The guard against a
  writer and reader sharing one mistake is the census cell. The cell is guarded `always`, so the
  committed sets carry a measured 0 against 4.
- `FieldUse` gains a third kind, because an `always` cell has no predicate and the not-read kind
  would publish the field as unread.
- The reader gate's own reading of the recording calls the engine entry points this test module
  imports. A plant at any of the four sites therefore never reaches it, and a mismatch there can
  only mean that the recording itself was made at another cooldown (problem prefix `live`).
- `test_genuine_candidate_reconstructs_in_api_and_repeats` runs the 6 arm on seed 1001. The 6
  arm's seed-1000 game on that 4-player roster holds no meeting and so makes no model call, which
  the test requires. Every other arm keeps seed 1000.
- `test_the_view_mirrors_every_config_field_value_and_default` now also compares annotations. The
  Literal comparison alone reads `int | None` and `str | None` as equal.
- **Deviation (outside Expected scope, directly necessary).** Seeder test doubles in
  `tests/orchestrator/test_game.py`, `tests/orchestrator/test_meeting_integration.py`,
  `tests/orchestrator/test_replay_meetings.py` and `tests/eval/test_balance_eval_meeting_runner.py`
  had fixed signatures, so the live game's new keyword raised `TypeError` in 32 tests. Each double
  now accepts `kill_cooldown_ticks: int | None = None`, and the one recording spy forwards it. No
  assertion changed.
- The orchestrator's dispatch asked the worker to flip Status and re-derive the inventory sentence
  in `tasks/README.md` (now "2 ready, 88 done").
- Unchanged, as the card requires: the pretend-task dwell (`observation/service.py:77-83`), the
  features' cooldown normalizer (`agents/tactical/features.py:138`) and the vote-correctness tick
  window (`eval/vote_correctness.py:215`).

### Failing first, at the base

Both new test files, run against an export of `107956bf` (`git archive`), fail at collection:

```
E   ImportError: cannot import name 'resolve_kill_cooldown' from 'engine.world'
E   ImportError: cannot import name 'CooldownWrite' from 'eval.gameplay_census'
```

### The reader gate

The fixture is `record_game` with the fake provider, seed 0, the 9p2i sample roster (9 players, 2
impostors, 2 tasks per crewmate), prompt set `qwen3_6_27b`, and
`RecordedExperimentConfig(kill_cooldown_ticks=6, meeting_reset="hub_with_grace")`. The meeting
runner is built from the config, with no process environment. Every tick row and the footer carry
that config.

Non-vacuity is asserted, count-only: kills with a later row, regroups that resume play with a
living impostor, and the default re-simulation failing at `seeding hash at tick 0`.

The walk, with every tick and meeting hash verified, reads 6 at every write. `ReplayLoader` serves
it `outcome_verified`. The golden re-renders every recorded prompt. At least one recorded impostor
prompt carries the cooldown line above 4 (a regex count; no text printed).

### Planted and perturbed proofs (every one passes at the head)

| Test id (abridged) | Plant | Result |
|---|---|---|
| `tests/engine/test_kill_cooldown_override.py::test_restoring_one_write_to_the_map_fails_that_case_and_only_it[round_start\|after_kill\|regroup]` | each module's `resolve_kill_cooldown` binding replaced by the map's value | exactly that writer's case fails |
| `...::test_without_the_omission_rule_the_first_archive_row_fails` | the field left out of `OMITTED_AT_DEFAULT` | the first archive row mismatches |
| `...::test_an_invalid_value_raises_at_every_entry_point_before_any_change`, `...::test_advance_tick_refuses_before_applying_any_action` | 0, -3, `True`, 6.0 at the seven entry points | each raises; input unchanged; no action applied |
| `tests/orchestrator/test_experiment_arms.py::test_an_engine_field_the_helper_does_not_thread_is_refused[kill_cooldown_ticks]` | the field left out of the threaded set | the helper refuses `kill_cooldown_ticks=6` |
| `tests/eval/test_kill_cooldown_readers.py::test_a_site_that_forgets_the_value_fails_the_gate_naming_it[<13 sites>]` | the helper's value replaced by `None` at one of: `live`, `live unrecorded`, `loader`, `walk`, `golden` x seeding / advance / meeting (live unrecorded: seeding only) | the gate names that reader and phase |
| `...::test_without_the_cooldown_in_the_readable_settings_each_instrument_refuses[6 walks]` | the field removed from the readable settings | each refuses naming `kill_cooldown_ticks=6` |
| `...::test_a_write_left_at_the_maps_value_breaches_the_cell_naming_its_writer[round_start\|after_kill\|regroup]` | one engine write left at the map's value, live and walk alike | `--set-dir` exits 1 naming set, seed, writer, impostor and tick |
| `...::test_a_kill_at_meeting_plus_five_breaches_the_grace_window_at_six` / `...::test_the_same_kill_in_the_default_cooldown_era_raises_nothing` / `...::test_the_window_read_from_the_map_again_misses_the_plus_five_kill` | a kill at T+5 after a regroup | raises at 6; nothing at the default; perturbed window misses it |
| `...::test_the_census_refuses_a_set_mixing_cooldowns` | a 4p1i set of one `None` game and one cooldown-6 game | `GameplayCensusEraError` |
| `...::test_the_validity_gate_fails_a_set_mixing_cooldowns_naming_the_odd_game` | the same mixed set through `scripts/validity_gate.py --json` | declared 6: fails `cost_and_provenance_exact` naming `headless-seed-1` (`None`); undeclared: names `headless-seed-0` (`kill_cooldown_ticks=6`); two cooldown-6 games pass |
| `...::test_the_six_arm_with_the_field_withheld_kills_before_six` | every `engine_arguments` binding drops the field | the 6 arm kills before tick 6 |
| `tests/orchestrator/test_experiment_arms.py::test_the_page_check_bites_the_cooldown_row_and_its_integer_values` | the row deleted; "an integer of at least 1" or `none` removed | each named |
| manual, at the working tree of `e164f57d` | the resolver returns 6 for `None` | `publish_gameplay_census.py --check` exit 1 (`ReplayIntegrityError`: `headless-seed-1000` at tick 0, `tick_hash_mismatch`); `verify_samples.sh replays/samples/4p1i` exit 1 ("50/50 samples drifted"); restored from a copy and `cmp` equal |

### Neuter table and the bounded mutation pass

The script lives in scratch and is not committed. It applied 87 mutants, one at a time, to the
lines this diff adds or changes. Each mutant ran its targeted tests (`pytest -x -n 6`) and was
then restored from a byte copy, never from git; `git diff` hashed the same before and after.

| group | mutants | operator classes | killed | survived |
|---|---|---|---|---|
| resolver, `engine/world.py` | 6 | neuter; literal; inverse None test; message constant | 6 | 0 |
| tick, regroup, seeder | 11 | neuter (each line, argument and write) | 11 | 0 |
| config field, validator, layer and omission rows, `EngineArguments` | 9 | neuter; message constant; dict row; tuple member | 9 | 0 |
| live game: validation, regroup argument, three call arguments | 5 | neuter | 5 | 0 |
| loader, walk, golden call arguments | 6 | neuter | 6 | 0 |
| `READABLE_SETTINGS` row | 1 | tuple member | 1 | 0 |
| census (`FieldUse`, classification, fold, loader writes, filter, window, view branch, rows, terms, heading) | 38 | neuter; None test and inverse; tick, kind and role constant; message constant; swap collection; drop filter; literal; swap adjacent branches; tuple member | 37 | 1 |
| API view and generated-type entry | 3 | neuter; swap type; tuple member | 3 | 0 |
| lab (rows, loop, summary filter, kind, collection, output key, cooldown literal) | 7 | tuple member; neuter; drop filter; kind constant; swap collection; literal | 7 | 0 |
| arm-page row | 1 | neuter | 1 | 0 |

- **The one survivor, X15, is equivalent.** It replaced the round-start write's tick read
  (`event.state.tick`) with 0. The first state any walk opens is the seeded state, whose tick is
  always 0.
- **Planted before the pass.** These cases were added after reading the diff, before the first
  probe ran:
  - the resolver and validator messages;
  - the property's second impostor;
  - the exact breach text;
  - the living-impostor filter;
  - the census refusal of a non-integer window;
  - the census refusal of mixed windows;
  - the comparison's wiring.
- **The one first-run correction.** X9 initially failed by a `SyntaxError` in the mutant itself.
  With valid quoting it was killed by the writer-breach case.

### The lab, development seeds 1000-1007 (count-only, run outside the tree)

The run's `source_sha256` equals `runtime_fingerprint` of the tree at `e164f57d` (`3da4e260...`).
The ten round-1 arms' rows equal `audits/tactical-gameplay/stage-b-r1-frozen-head.json` field for
field: 2,240 fields compared, 0 differing. The output's only new top-level key is
`ticks_to_parity`.

| arm | roster | games | parity games | parity tick rows min / median / max | kills |
|---|---|---|---|---|---|
| `stage_b_full` (4) | 9p2i | 8 | 8 | 26 / 35.5 / 58 | 40 |
| `stage_b_full` (4) | 4p1i | 8 | 7 | 14 / 17 / 19 | 15 |
| `stage_b_full_kill_cooldown_6` | 9p2i | 8 | 7 | 30 / 44 / 68 | 39 |
| `stage_b_full_kill_cooldown_6` | 4p1i | 8 | 1 | 18 / 18 / 18 | 8 |
| `stage_b_full_kill_cooldown_8` | 9p2i | 8 | 3 | 49 / 52 / 58 | 30 |
| `stage_b_full_kill_cooldown_8` | 4p1i | 8 | 0 | n/a | 2 |

The first-kill check uses seed 1000 on the 4p1i roster: `stage_b_full` kills first at tick 4, the
6 arm at tick 6 and the 8 arm at tick 11.

### Census

- **Committed sets.** `docs/gameplay-census.json` was regenerated. A structural diff against
  `107956bf` finds the following, and nothing else:
  - the new cell and table in all six sections;
  - `field_classification.kill_cooldown_ticks`;
  - the grace-window cell's `definition` in all six sections;
  - `terms["grace window"]` and `terms["regroup"]`.

  The cell reads 0 by construction everywhere: 0/275 on s9 (100 round start, 175 after a kill),
  0/850 on c9, 0/116 on s4, 0/108 on c4, 0/1349 pooled. The regroup row is empty on all four.
  `grace_window_ticks` stays 4.
- **Round 1.** `--set-dir replays/candidates/stage-b-r1/9p2i` at the head, against the base export,
  differs only in the new cell, the new table and the grace-window definition. The cell reads
  0/487 (100 round start, 227 after a kill, 160 at a regroup). The grace cell still reads 0/139.

### Validation (exit codes captured directly, at the working tree committed as `e164f57d`)

| command | result |
|---|---|
| `uv run lint-imports` | 0; 4 contracts kept |
| `bash scripts/verify_samples.sh` on `replays/samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i` | 0 each; 50, 50, 150, 50 and 50 verified clean |
| `build_sample_report.py --check` on the four sets and round 1 | 0 each |
| `publish_process_scorecard.py --check` | 0 |
| `publish_gameplay_census.py` then `--check` | 0 |
| `check_doc_facts.py`; `validate_task_docs.py`; `gen_frontend_types.py --check`; `verify_ml_evidence.py` (offline) | 0 each |
| `uv run pytest -m campaign` | 0; 336 passed |
| targeted suites (the two new files, arms, config, lab, census, golden, leak) | pass; the two new files 117 tests |
| committed-payload test | 956 rows in 101 files, byte for byte |
| `build_demo_bundle.py` at `107956bf` (export) and at the head; `diff -r` | 0; 194 files each. The sample replays' mtimes were pinned equal in both trees, since `created_at` is the file mtime; the first, unpinned build differed only there |
| `bash scripts/check.sh` | run once at the head that carries this subsection, exit code captured directly; the PR body quotes its counts |

### Limitations

- The lab's fake games establish mechanics, not model play.
- The tactical constants named above were tuned at 4 and are not re-derived. The learned
  features' normalizer reads a cooldown of 6 above 1.0.
- `training/scenarios.py` still bounds a staged cooldown by the map's value. It runs only
  unrecorded training drills and is out of scope.
- `PublicResults.tsx` has no words for this field (Constraints). The promoting card owns the
  label.
- The round-2 outcome cannot separate the cooldown from hosted generation's own variation. The
  record card states that.
