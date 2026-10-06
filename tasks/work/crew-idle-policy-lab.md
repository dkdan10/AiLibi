# The crew idle-policy cross and the objective's re-pricing, written down

**Status:** ready

## Outcome

Round 2 is the shown 9-player set (`replays/samples/9p2i`, recorded under its `experiment-config.json`: the seven
adopted arms, `vent_exit_policy = look_and_wait`, `kill_cooldown_ticks = 6`). Under those rules a finished crewmate
still stands at the meeting hub, the default `crew_idle_policy = hub_wait`. The two hand-written alternatives the lab
already defines, `patrol` and `accompany`, have only been measured on the pre-wave rules. No instrument counts, the
same way for every role, how many players someone could have seen at the moment of a kill. The one committed ML
objective still prices crew coverage by engine truth (`patrol_coverage` pays a crewmate for sharing a room with a
player who IS an impostor). Nothing in `training/README.md` section 7 or in the code comment says that a reopening
must re-price that term and `correct_reports` before any search. Nothing there says that the conviction model's GO
verdict, which ships a role-derived fitness term, is re-registered at that point.

When this card is done:

1. **The cross is measured.** The tactical lab (`experiments/tactical_gameplay.py`) gains two arms. Each is
   `stage_b_full_kill_cooldown_6` with `crew_idle_policy` set to `patrol` or to `accompany`, and the existing
   cooldown-6 arm is the `hub_wait` column. The lab also gains a wider development split and the counts below. One
   committed capture under `audits/tactical-gameplay/` holds the run. A dated section of that directory's README
   reads it, and `docs/artifacts.md` registers it. The run is at $0 on the deterministic fake provider, with no ML
   trained.
2. **One new role-blind cell, defined here before the run, so its first reading is accurate.** It is whereabouts
   coverage. After every play tick the walk advances (`TickAdvanced.state`, the state the tick leaves), each player
   alive in that state is a subject. A subject is covered when it is not inside a vent and at least one other
   player, alive and not inside a vent, stands in the same room. That is the engine's own kill-witness rule, which
   reads no role, applied to every player after every tick. The rule reads `alive`, `room` and `in_vent` only: no
   role, no seat, no sight radius. Same-room sight is also the sight every observer holds in every visibility mode,
   so the rule is the same for every role. An impostor's wider base sight is deliberately not used. Four counts per
   game: subjects and covered subjects over kill ticks (play ticks with at least one `Killed` event, each counted
   once however many kills it holds), and the same two over every play tick. A killer alone with the body is
   uncovered, so the kill-tick cell also says whether a kill had any onlooker, whoever that was. The cell counts
   positions, not memories or speech: it is an upper bound on what any agent held. It is the role-blind
   replacement for `patrol_coverage`'s measurement step.
3. **The kill-witness rows, the optional lab half.** For each kill, the crew witnesses the engine recorded, and
   those who walked in: they made a `Moved` event from another room into the kill's room on the kill tick. The
   engine applies a tick's actions in order and reads a kill's witnesses at that moment, so such a witness arrived
   before the kill. Both rows read on the existing cooldown arms (`stage_b_full`, the map's 4 ticks, against
   `stage_b_full_kill_cooldown_6`). They are descriptive mechanism rows. They read the witness's role exactly as
   `kills_crew_witnessed` already does, and they are not part of the re-pricing.
4. **The re-pricing, written down.** One dated paragraph lands in `training/README.md` section 7 and one clause in
   the comment at `training/rewards.py` above `correct_reports`. Both say that any reopening re-prices
   `correct_reports` and `patrol_coverage` role-blind before any search, under a new `FITNESS_OBJECTIVE_ID`. This
   supersedes in writing the 2026-07-09 ratification of the engine-truth proxy. Both also say that the conviction
   GO verdict is re-registered at that reopening as an override of its GO. Both edits are text only, of the class
   merged in `d1ea113a`: `#` lines in `rewards.py` and one README paragraph, so no value, weight, signature, pin,
   fit or artifact moves. A new doc gate keeps both from being silently deleted.
5. **The seed-0 value pin stays**
   (`tests/training/test_rewards.py::test_shaped_reward_values_on_seed_zero_are_byte_identical`).

**The reading is what it is.** It reports whether a hand-written idle policy already moves whereabouts coverage
under the Stage-B rules, and by how much, beside the task race, kills, crew-witnessed kills, walk-in witnesses and
meetings. The best hand-written arm's uncovered remainder is reported as an upper bound on the room any idle
policy, written or learned, could still take in this cell. Whether a learner could take it is not measured. The
reading decides nothing about ML, and the hold stands whatever it reads.

## Evidence

Every `path:line` is cited at `76270d6c` and labelled by its symbol. The implementer re-anchors each one by symbol
at dispatch. Every count is re-measured at dispatch through the command named, never copied from here.

**The owner's ruling of 2026-10-06, verbatim:** "1. Rekey 2. What is your recommendation? I slightly lean to spend
with narrow field, but would go with your recommendation 3. Rebase the rubric. Maybe spend time thinking if it needs
to be completely redone with the context from this conversation. 4. README should be current and can be a focus in
the last steps, once the project is stable. 5. Sounds good 6. Sounds good 7. Sounds good 8. Merge when ready". The
orchestrator's reading (4) binds this card. The ML hold stands. The free idle-policy lab runs with a role-blind
whereabouts-coverage cell. The role-blind re-pricing of `correct_reports` and `patrol_coverage` is written into
`training/README.md` section 7 and the `rewards.py` comment as a comment-only edit (precedent `d1ea113a`). The
seed-0 pin stays until a reopening. The conviction GO's override folds into the re-pricing note. The rubric and the
README are not this card's (reading 5). The advisory baselines memo is off-tree
(`~/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`). Its D10 (options
R1 (a), R2 keep, R4 fold) and its Part 3.4 item 11 frame the work. Every number this card takes from it is re-cited
here to the tree.

**The lab today.**
- `candidate_configs` (`experiments/tactical_gameplay.py:161-203`) defines `patrol` and `accompany` against the
  default rules (`:174-175`). It also defines `stage_b_full` (`STAGE_B_FULL_SETTINGS`, `:131-138`) and the cooldown
  dial (`STAGE_B_KILL_COOLDOWNS`, `:150-157`). The policies are `ExperimentalCrewmatePolicy` (the patrol goal at
  `agents/tactical/experimental.py:185-198`, accompaniment at `:232-248`). They need no agent change.
- Splits are fixed at `build_comparison` (`:929`): `range(1000, 1008) if split == "development" else
  range(2000, 2016)`. Any other string falls through to the held-out seeds.
- `measure_replay` (`:476`) already counts `event:Killed`, `kills_crew_witnessed` (`:629-632`), finished-crew waits
  at the hub, terminal tasks and the ending reason. It counts nothing role-blind about positions.
- `runtime_fingerprint` (`:825-854`) hashes `engine`, `observation`, `agents`, `meetings`, `llm`, `orchestrator`,
  `eval`, `pyproject.toml`, `uv.lock` and the harness itself, not `training/`.
- The committed idle rows exist only on the pre-wave rules: `audits/tactical-gameplay/development.json`, arms
  `patrol` and `accompany`, and the development tables at `audits/tactical-gameplay/README.md:77-104`.
  `stage-b-development.json` and `stage-b-r1-frozen-head.json` carry no idle arm (their `arms` keys).
- `tests/orchestrator/test_experiment_config.py:425-427` holds `len(candidate_configs()) == 19`.
- Authoring re-measure at `76270d6c`, written outside the tree. The ten round-1 arms plus
  `stage_b_full_kill_cooldown_6` were run on `--split development`. The ten arms' rows equal
  `stage-b-r1-frozen-head.json` over 2,240 top-level row fields, 0 differing. The cooldown-6 arm reads 39 kills,
  4 crew-witnessed and 7 parity endings in eight 9p2i games, and 8 kills, 0 and 1 in eight 4p1i games. Its kills and
  parity endings match the kill-cooldown card's Results (`tasks/work/kill-cooldown-arm.md:709-714`). The capture's
  `source_sha256` begins `eb2c048f`. The whole run, 176 games, took 18.8 s of wall.

**What the diagnosis says, and how far.** `tasks/diagnosis-2026-10-02/README.md` Part 1.5 and Part 3 card 6 propose
the cross and card 3 the witness rows. Part 2.3 gives 1,813 idle crew-ticks, all at the hub, 19.9% of crew decisions
in round 2, from an uncommitted scratch census, not re-run here. It also gives crew-witnessed kills of 3/175, 4/227
and 14/195 in the three hosted columns. Part 2.4 says witnesses walk in on the kill tick in 14 of 14, also from
scratch. `ml-tactical.md` section 5 sketches the coverage cell with a crewmate observer, and its section 11
limitations say the cell was proposed, not computed. This card drops the observer's role too, so that the cell reads
no role at all.

**The rule the cell restates.** A kill's witnesses are `_witnesses_in_room` (`engine/rules.py:33-48`): every other
player alive, not in a vent and in the kill's room, read from the state when the kill applies, with no role read.
For sight, `visible_rooms_for_player` (`engine/visibility.py:37-61`) always includes the observer's own room, and
`_visible_player_ids` (`:64-80`) never lists a player inside a vent or a dead one. `_resolve_observer_visibility_mode`
(`:98-127`) gives a crewmate only its own room at base sight and gives an impostor the adjacent rooms too.

**The objective.**
- `_crew_terms` (`training/rewards.py:294-343`) prices `correct_reports` by the ejectee's roster role (`:308-317`).
  It prices `patrol_coverage` by `crew_shadowing_impostor` frames (`:319-335`; `training/rollout.py:339`). The
  comment `:301-306` labels both role-correct and says they are unchanged while ML is held.
- `FITNESS_OBJECTIVE_ID` is `bounded-terms-win-dominant.v1` (`:429`).
- The seed-0 pin compares exact doubles, `patrol_coverage == 0.6862745098039216` and crew total
  `1.6862745098039214` (`tests/training/test_rewards.py:518-565`).
- The 2026-07-09 ratification of the engine-truth co-location proxy is `tasks/phase-15.md:57-62`.
- The conviction verdict reads `verdict: GO`, `fitness_term: ships`, `model_role: training-signal`
  (`training/artifacts/conviction/verdict.json`). The harness adds it at `DEFAULT_CONVICTION_WEIGHT = 0.5`
  (`training/bakeoff/harness.py:281`, `inner_episode_fitness :1006`).
- Section 7 is `training/README.md:312-364`: the fork, the four mandatory checks, then "Decide-at-proposal". It names
  neither term, nor the ratification, nor the verdict.

**The precedent and the pins that read source bytes.**
- `d1ea113a` (PR #482) changed `training/rewards.py` by `#` lines only (today's `:301-306`) and `training/README.md`
  by a section-2 label. Its card proved it with an AST comparison that keeps strings (equal trees). Offline
  `verify_ml_evidence` read 61 checks, FAIL 0, and the campaign tier passed 336
  (`tasks/work/docs-truth-typed-trigger.md:600-625`).
- It stayed green for these reasons. The value pins compare computed values, which no comment moves. The two
  digests that do hash `rewards.py` bytes are bound by no committed stamp:
  - `training.provenance.derivation_fingerprint` (`training/provenance.py:108`) hashes the `derivation_files`
    closure, 110 files at `76270d6c` with `training/rewards.py` among them. It feeds the version-two
    `fit_corpus_fingerprint` and `bakeoff_substrate_sha` (`training/bakeoff/map_elites.py:724`). `git grep` for
    their current prefixes, `5f63f37c` and `109da039`, finds nothing committed. The committed surrogate and
    conviction fits carry `corpus_sha256 6536c68c...`, which equals `historical_fit_corpus_fingerprint` over
    corpus bytes alone, and the current loaders refuse them as version-one
    (`tests/training/test_model_evidence_provenance.py::test_current_loader_refuses_historical_fit`).
  - The tournament resume fingerprint `configuration_fingerprint` (`scripts/_tournament_progress.py:39`) hashes
    every `training/*.py` in its source loop. It binds only a live tournament's `--resume`, and no progress record
    is committed.
- Neither the lab's `runtime_fingerprint`, nor the held-out `GENERATOR_SOURCES`
  (`experiments/held_out_prefixes.py:173-196`), nor any `verify_ml_evidence` inventory covers `training/rewards.py`
  or `training/README.md`. No gate parses section 7 (`git grep` over `*.py`).
- Offline `verify_ml_evidence` at `76270d6c`: checks 63, OK 51, FAIL 0, ABSENT 7, INFO 5.

**The registry.** `docs/artifacts.md:113` states the `audits/` row exactly: 28,136,878 tracked bytes / 333 files,
which match `git ls-files audits` at `76270d6c`. `tests/scripts/test_verify_ml_evidence.py:2166`
(`test_every_counted_registry_row_matches_the_index`) runs in `bash scripts/check.sh` and fails when a row's count
or exact bytes drift. Sub-directories of `audits/` are indexed as units (`check_audits_index`), so a new file in
`tactical-gameplay/` needs no index row.

## Acceptance

Every item names its enforcing mechanism and the planted or perturbed case that must turn its test red.

- [ ] **The cross arms.** Mechanism: a read-only `STAGE_B_IDLE_POLICIES` mapping (`MappingProxyType`) names
  `stage_b_full_kill_cooldown_6_patrol` and `stage_b_full_kill_cooldown_6_accompany`. `candidate_configs` builds each
  from the cooldown-6 arm's validated payload plus `crew_idle_policy`, so the cooldown is derived, never copied. A
  test holds each arm's `model_dump()` equal to the cooldown-6 arm's plus exactly that one field. Planted, red on its
  defect: an arm built from `stage_b_full` (the cooldown dropped); an arm setting `hub_wait`; and the source-change
  case, `STAGE_B_KILL_COOLDOWNS` monkeypatched to 7, under which the cross arms follow. Both arms join
  `test_genuine_candidate_reconstructs_in_api_and_repeats`: each reconstructs with `outcome_verified` and repeats
  byte for byte. The arm-count literal becomes 21.
- [ ] **The wider development split.** Mechanism: a read-only `SPLIT_SEEDS` mapping replaces the conditional at
  `:929`: `development` 1000-1007, `held_out` 2000-2015, `development_wide` 1000-1099. The CLI choices derive from its
  keys, and an unknown split raises `ValueError` before any game. Planted: `held-out` (hyphen) raises; a
  `development_wide` that reaches seed 2000 fails the disjointness test. Its first eight rows equal a `--split
  development` run's rows for the same arms, field for field.
- [ ] **The coverage cell, exact.** Mechanism: a pure helper over one `WorldState` returns (subjects, covered) by the
  Outcome's rule, and `measure_replay` adds the four counts `whereabouts_subjects_at_kill_ticks`,
  `whereabouts_covered_at_kill_ticks`, `whereabouts_subjects_at_play_ticks` and `whereabouts_covered_at_play_ticks`.
  Hand-built states give exact counts and turn red on each defect:
  - two players in one room are both covered, and a player alone is not (planted: counting the subject as its own
    observer);
  - a vented player beside a walker covers nothing and is not covered (planted: the `in_vent` filter dropped);
  - a dead player in the room covers nothing (planted: the `alive` filter dropped);
  - a tick without a `Killed` event adds nothing to the kill-tick pair, and a tick with two kills counts its players
    once (planted: per-kill counting);
  - the post-tick state is read, not the pre-tick state (planted: `pre_state` swapped in, on a tick where a move
    joins two players).
- [ ] **Role-blind by property.** Mechanism: a Hypothesis property over states seeded on the canonical map, with
  random rooms, `alive` and `in_vent` flags and a random role assignment, under `settings(deadline=None)`. The helper's
  result is unchanged under every permutation of roles among players. Perturbed: a variant counting only crewmate
  observers, held in the test, fails the property.
- [ ] **The rule it restates, pinned at its source.** Mechanism: the helper implements the rule itself, and a
  Hypothesis property (same generator, `settings(deadline=None)`) holds it to the engine. A living, non-vented subject
  is covered exactly when `engine.rules._witnesses_in_room(state, room=<its room>, exclude={<it>})` is non-empty.
  Planted source-change case: a monkeypatched `_witnesses_in_room` that also admits vented players fails the pin. An
  engine change to the witness rule therefore cannot silently change what the cell means.
- [ ] **The walk-in witness rows.** Mechanism: `measure_replay` adds `crew_kill_witnesses`,
  `crew_kill_witnesses_walked_in` and `kills_with_walk_in_crew_witness`, by the Outcome's definition. A planted
  `advance_tick` sequence, run through the helper's engine arguments, gives exact counts and is red on each defect:
  - a crewmate already in the room is a witness and not a walk-in;
  - a crewmate who moves in after the kill in action order is neither (planted: the witness-list condition dropped);
  - a crewmate who leaves the kill room before the kill is neither;
  - a crewmate whose move names its own room is a witness and not a walk-in (planted: the other-room condition
    dropped);
  - an impostor who walks in is not counted (planted: the role read dropped).
  A property holds `kills_with_walk_in_crew_witness <= kills_crew_witnessed` and walked-in witnesses at most all
  crew witnesses.
- [ ] **The summaries.** Mechanism: pure functions over the `arms` block publish two top-level keys, beside
  `ticks_to_parity`.
  - `whereabouts_coverage`, per arm and roster: games, kill ticks, the four sums, games with no kill tick, and the
    per-game kill-tick share's minimum, median and maximum over games with one.
  - `idle_policy_pairs`, for each cross arm whose reference `stage_b_full_kill_cooldown_6` ran in the same comparison,
    per roster: seeds where both games have a kill tick, and among them seeds where the arm's kill-tick share is
    higher, equal or lower; then the same three over play ticks for every seed.
  Stubbed rows (as `test_the_comparison_publishes_ticks_to_parity_over_its_own_arms` does) give exact values.
  Planted: a summary over the wrong arm's rows, and a pair read against `stage_b_full`, each fail.
- [ ] **No existing count moves.** Mechanism: a run at the head, written outside the tree, of the ten round-1 arms
  on `--split development`, and a count-only comparison quoted in Results, as the kill-cooldown card ran its own. The
  rows equal `stage-b-r1-frozen-head.json` on every top-level row field. `counts` is compared on the frozen file's
  own keys, and the new count keys are exactly the seven declared here. At authoring that is 2,240 fields with 0
  differing. Perturbed: a scratch copy of the head run with one `kills_crew_witnessed` raised by 1 makes the
  comparison name that row. The capture holds no
  `"experiment_config"` key, so `tests/orchestrator/test_experiment_arms.py`'s committed-payload census (956 rows in
  101 files) is unchanged.
- [ ] **The capture is committed, reproducible and read.** Mechanism: one run of the Validation command writes
  `audits/tactical-gameplay/stage-b-idle-policy-development.json`. It runs 4 arms on 100 seeds per roster, 800 games,
  at the lab's limits: 96 ticks, 256 calls, 1,000,000 input and 100,000 output tokens, 30 s and $0 per game. Any game
  that aborts or hits a limit keeps its row and is named in Results; nothing is re-run to remove it. A command
  recomputes `runtime_fingerprint` at the PR head and compares it with the capture's `source_sha256`. If a merge of
  `main` moves the fingerprint, the capture is taken again at the new head. Perturbed: a scratch copy with one
  fingerprint character changed fails the comparison. A dated README section defines every new count in plain words,
  with no task or audit IDs. It tabulates the race, kills, crew-witnessed kills, walk-in witnesses, meetings, hub
  waits and coverage per arm and roster. It reads the cross in the Outcome's predeclared form: three coverage
  figures, the paired counts, the best arm's uncovered remainder as an upper bound, and "decides nothing about ML". It
  reads the two cooldown arms as mechanics only: fake meetings eject nobody, so the hosted rise from 4/227 to 14/195
  is neither confirmed nor explained. A compact check command at the end of the section reproduces every table cell
  from the JSON.
- [ ] **Registered.** Mechanism: `docs/artifacts.md`'s `audits/` row states the measured tracked bytes and file count
  at the PR head. `test_every_counted_registry_row_matches_the_index` and offline `verify_ml_evidence` enforce it.
  Planted: the run before the row is updated is red, and Results quotes it.
- [ ] **The re-pricing, written.** Mechanism: section 7 gains one paragraph after the four checks, worded as below
  (only the ruling's citation filled in), and the `rewards.py` comment gains the clause below, as `#` lines. A new
  `tests/scripts/test_reopening_repricing_note.py` reads file bytes, never imports. It requires exactly one
  paragraph in section 7 beginning `**Dated 2026-10-06`, naming `correct_reports`, `patrol_coverage`,
  `FITNESS_OBJECTIVE_ID`, `role-blind`, `before any search`, `2026-07-09` and
  `training/artifacts/conviction/verdict.json`. It also requires the contiguous comment block directly above
  `correct_reports = sum(` to name `role-blind`, `FITNESS_OBJECTIVE_ID`, `before any search`, `conviction` and
  `2026-07-09`. Planted, as fixed strings in the test: the paragraph removed; moved into section 8; missing
  `patrol_coverage`; doubled; and the comment without the clause. Each is rejected.
- [ ] **Comment-only, proved the way `d1ea113a` proved it.** Mechanism: the strings-kept AST comparison in
  Validation finds `training/rewards.py` equal at base and head. Every changed line of `git diff <base> --
  training/rewards.py` matches `^[+-]\s*#`, and `training/README.md` is the only other file under `training/` that
  changes. Planted, both red:
  - in a byte copy, `"patrol_coverage": patrol_coverage` becomes `patrol_coverage * 0.5`; the AST comparison exits 1;
  - applied in place, the seed-0 pin fails on `patrol_coverage`.
  The file is restored from the byte copy, never from git, and its `shasum` is equal before and after.
- [ ] **Nothing frozen moves.** Mechanism: `git diff --stat <base> HEAD` over `replays training/artifacts
  training/reports agents/tactical/learned tests/training api frontend` prints nothing. The seed-0 test passes
  unchanged. Offline `scripts/verify_ml_evidence.py` reports FAIL 0, never `--complete`. `uv run pytest -m campaign`
  passes. `uv run pytest tests/scripts/test_build_demo_bundle.py` passes, with the bundle's inputs untouched.
- [ ] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or changes,
  using only these classes: F filter, S swap, N comparison, C constant (a role, kind, room or tick read), M message,
  T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the touched suites and
  is restored from a byte copy. A survivor is killed by a new test or named equivalent with its reason. Results
  carries the per-line neuter table: each production line, and the test that goes red when it is neutered.
- [ ] **The full gate.** `bash scripts/check.sh` passes in a clean worktree at the head that states the numbers.

**The paragraph for section 7.** Its citation names the committed home of the owner's 2026-10-06 ruling at dispatch:
the decision memo's section 8.1 (`tasks/decision-2026-09-24-stage-b-wave.md`), which the orchestrator's doctrine
commit lands before this card dispatches (should it not have landed, this card).

> **Dated 2026-10-06: the objective is re-priced before any search.** Any reopening re-prices the crew terms
> `correct_reports` and `patrol_coverage` (`training/rewards.py`, `_crew_terms`) role-blind before any search, under
> a new `FITNESS_OBJECTIVE_ID`. A re-open proposal shows this done beside the four checks. The tactical lab's
> role-blind whereabouts cell (`audits/tactical-gameplay/README.md`, the idle-policy section) is the measured
> candidate for coverage. This supersedes in writing the 2026-07-09 ratification of the engine-truth co-location proxy
> (`tasks/phase-15.md:57-62`). The conviction model's GO verdict (`training/artifacts/conviction/verdict.json`,
> `fitness_term: ships`) is re-registered at that reopening, before any search, as a dated override of its GO, so a
> re-priced objective ships without the conviction supply term. No value, weight, pin or artifact moves with this
> paragraph (owner ruling of 2026-10-06, `<its committed home>`).

**The clause for the comment**, continuing `:305-306` (the first line is today's):

```
    # crew-conduct term. Their values and weights are unchanged while ML work is
    # held (owner ruling of 2026-09-24). Any reopening re-prices both role-blind
    # before any search, under a new ``FITNESS_OBJECTIVE_ID``, and re-registers
    # the conviction GO verdict with them (``training/README.md`` section 7,
    # which supersedes the 2026-07-09 ratification of this engine-truth proxy).
```

## Constraints

- **House rules.**
  - The engine is a pure deterministic tick function, and replays from a seed stay byte-identical within their
    recorded scope. LLMs run only at meetings, and tactical decisions stay rule-based.
  - Agents reason from typed event memory. `agents/` never imports `engine/` (import-linter; the observation
    firewall).
  - No module-level mutable state: the new tables are `Final` read-only mappings or tuples. Invalid input raises,
    with no silent fallback.
  - Each new invariant gate carries its planted case. Each claim names its mechanism, and each number comes with
    its command. One writer per file.
  - Properties carry `settings(deadline=None)` where a map loads. No test is weakened, and the arm-count literal
    moves only by the two arms added.
- **No switch.** No new `AILIBI_*` lever, no environment switch, and no new `RecordedExperimentConfig` field:
  `crew_idle_policy` exists, with all three values built. No prompt registry bump and no prompt, detector or
  rendered byte change. No recorded byte is edited and no history is re-scored. The earlier lab captures and their
  README sections stay as written.
- **The ML hold (ruling 12, `tasks/decision-2026-09-24-stage-b-wave.md:41`).** No ML is trained, fitted, searched or
  re-evaluated. The lab imports nothing from `training/`. `training/` bytes change only in `#` comment lines of
  `rewards.py` and in one README paragraph. No reward value, weight, signature, pin, fit, digest or artifact moves.
  The corpus FROZEN line and every ML artifact are untouched, checked by offline `verify_ml_evidence`. The seed-0
  value pin stays until a reopening.
- **What the lab may say.** Fake games establish mechanics, not model play. Role-correctness is reported, never a
  gate. Nothing pushes an agent toward the correct answer, and the idle policies are the existing hand-written ones.
  The coverage cell is reported, never a bar, a gate or a fitness, and no envelope line reads it. High coverage by
  clumping cuts kills and meetings, so the README reads meetings and kills beside it as floors read, never rewarded.
  The reading decides nothing about ML.
- **Inputs.** Development seeds only (`development_wide` contains `development`). The held-out split 2000-2015 is not
  run. Fake provider through the lab's own client and limits. No live provider call, no `.env` read, and no
  rendered prompt, transcript text or seed-band prefix printed. The round-3 ceilings do not apply because nothing here
  is recorded live.
- **Prerequisites and order.** None blocks the code. The orchestrator's doctrine commit lands before this card
  dispatches, so the section 7 paragraph cites the decision memo's section 8.1 as the committed home of the
  2026-10-06 ruling (should it not have landed, this card). This card is in round 3's first wave, dispatched
  beside `route-lines-field` and `census-held-data-cells`, and it **merges before F**, the frozen head of
  `stage-b-record-r3` (F is `main` after all three wave-1 cards merge). It must: the record's nothing-moves gate
  is an empty `git diff F..HEAD` over `training` and `experiments`, and this card writes
  `experiments/tactical_gameplay.py`, `training/README.md`, `training/rewards.py`, `audits/tactical-gameplay/` and
  the `audits/` row of `docs/artifacts.md`. It never merges while the round records. The capture binds `agents`, `meetings`, `orchestrator` and `eval` through
  `runtime_fingerprint`, so if `route-lines-field` or `census-held-data-cells` merged first, this branch merges
  `main` and re-captures; either way the capture states the head it measured. This card touches no path in the
  record's code-freeze pathspec (`engine agents meetings observation orchestrator eval api scripts llm`); the paths
  it writes are in the record's nothing-moves diff, which is why it lands before F. The `training/`
  edit moves `configuration_fingerprint`, so no tournament `--resume` may span it. A recording checkout detached at
  its own commit is unaffected.
- **One writer per file**, as the orchestrator's one-writer map assigns it.
  - Alone in this wave, merged before F: `experiments/tactical_gameplay.py`,
    `tests/experiments/test_tactical_gameplay.py`, `training/README.md`, `training/rewards.py`,
    `tests/scripts/test_reopening_repricing_note.py`, `audits/tactical-gameplay/README.md` and `audits/tactical-gameplay/stage-b-idle-policy-development.json`; the
    record card never edits `audits/tactical-gameplay/`. `tests/eval/test_kill_cooldown_readers.py` is follow-through
    only if its stub needs the new keys (the held `rubric-extractor-era` shares it and stays undispatched).
  - `tests/orchestrator/test_experiment_config.py`: this card moves the candidate count from 19 to 21 (`:427`);
    `route-lines-field` moves `len(OMITTED_AT_DEFAULT)` from 6 to 7 (`:316`) and adds a `_VERSION_PLAN` row.
    Distinct lines: either may merge first, and the second merges `main`.
  - `docs/artifacts.md`: this card's `audits/` row only, re-derived after merging `main`; the writers are serial in
    merge order (the field card's `experiments/lab/` row, the census card's census row, the record card's
    `replays/candidates/` and `audits/` rows last, after F).
  - `tasks/README.md` (the inventory sentence) and this card's Status line are the orchestrator's, on `main`; the
    worker fills Results only. The doctrine documents are not edited here.
- **Open for the owner, not decided here.**
  - Which grade of "reads roles" a future objective forbids: the two crew terms only, or also `meetings_survived`
    and the teammate witness discount. The paragraph names only the two crew terms, as ruled.
  - Whether a crewmate-observer variant of the cell is ever wanted. It would read a role and could not be the
    re-pricing.
- **Delivery.** Branch `work/crew-idle-policy-lab` from `main`, one PR into `main`, merge commit or fast-forward,
  never squash. Each commit body ends `Card: tasks/work/crew-idle-policy-lab.md`, immediately followed by
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR populates every section of
  `.github/pull_request_template.md`.
- **Publication.** Nothing ships: no viewer, shown replay, featured list, public payload or README change, and the
  demo bundle's inputs are untouched. The orchestrator merges.

## Expected scope

- `experiments/tactical_gameplay.py`: the following, and nothing else.
  - `STAGE_B_IDLE_POLICIES` and the two arms in `candidate_configs`.
  - `SPLIT_SEEDS`, the split refusal and the CLI choices.
  - The coverage helper and the walk-in fold, with their seven counts in `measure_replay`.
  - The two summary functions and their keys in `build_comparison`.
- `tests/experiments/test_tactical_gameplay.py`: the arms in the reconstruction parametrize, and the split,
  coverage, property, witness-rule pin, walk-in and summary cases.
- `tests/orchestrator/test_experiment_config.py`: the arm count, 19 to 21, only.
- `tests/scripts/test_reopening_repricing_note.py` (new): the doc gate and its planted strings.
- `audits/tactical-gameplay/stage-b-idle-policy-development.json` (new): the capture, written by the harness.
- `audits/tactical-gameplay/README.md`: one new dated section after the Stage-B vent section. No earlier section
  changes.
- `docs/artifacts.md`: the `audits/` row's tracked bytes and file count, and nothing else.
- `training/README.md`: one paragraph in section 7.
- `training/rewards.py`: the comment clause, as `#` lines only.
- `tasks/work/crew-idle-policy-lab.md`: this card's Results only.

Follow-through outside this list needs a line in Results naming the file and why. A file another round-3 card owns
is not touched; the conflict goes to the orchestrator. `agents/`, `engine/`, `eval/`, `meetings/`, `orchestrator/`,
`docs/gameplay-census.*`, `docs/process-scorecard.*`, `docs/glossary.md`, `audits/README.md`, `tasks/README.md` and
this card's Status line (the orchestrator's) are not edited. New terms are defined where they are used.

## Record impact

- **Recorded bytes.** None. Nothing under `replays/` moves, and no MANIFEST, stamp, prompt or detector byte changes.
  The capture is a lab artifact of fake games, written once and never regenerated in place.
- **Future behaviour.** None for any game. The new arms and split run only when the lab names them. The defaults
  and every existing arm's play are unchanged, as the frozen-head comparison proves.
- **Compatibility.** Lab rows gain seven count keys and the output gains two top-level keys, additively. Existing
  captures stay valid as written. `--split` refuses a name it does not know, where an unknown name used to fall
  through to the held-out seeds silently.
- **Evaluation.** The lab gains a role-blind cell and its first reading. No census cell, scorecard row, envelope
  line, bar or verdict changes.
- **ML.** `training/` changes in comment and README text only. The derivation and configuration fingerprints move
  with those bytes. The version-two fit identity and substrate stamp move too, but no committed stamp holds either.
  The version-one fits, the seed-0 pin, every digest and the corpus FROZEN line are unchanged.
- **Adoption.** Not applicable. No arm is adopted, and the cross arms stay lab arms.

Measurement: the capture at the PR head, read by the README's compact check, plus the no-existing-count-moves
comparison and the offline evidence check, each with its command in Results.

## Validation

```
# B is the branch point on main; SCRATCH is a directory outside the worktree
env | grep -c '^AILIBI_'                                       # 0
uv run pytest tests/experiments/test_tactical_gameplay.py tests/orchestrator/test_experiment_config.py \
  tests/orchestrator/test_experiment_arms.py tests/eval/test_kill_cooldown_readers.py \
  tests/experiments/test_vent_look_and_wait_game.py tests/scripts/test_reopening_repricing_note.py \
  tests/training/test_rewards.py tests/training/test_model_evidence_provenance.py -n 6 --dist loadfile
# the capture, at a clean committed head; the harness refuses an existing path
uv run python -m experiments.tactical_gameplay --split development_wide --arms stage_b_full \
  stage_b_full_kill_cooldown_6 stage_b_full_kill_cooldown_6_patrol stage_b_full_kill_cooldown_6_accompany \
  --output audits/tactical-gameplay/stage-b-idle-policy-development.json
uv run python -c "import json; from pathlib import Path; \
  from experiments.tactical_gameplay import runtime_fingerprint as f; \
  d = json.load(open('audits/tactical-gameplay/stage-b-idle-policy-development.json')); \
  raise SystemExit(0 if d['source_sha256'] == f(Path('.').resolve()) else 1)"
# no existing count moves: the ten round-1 arms into scratch, then the keyed count-only comparison against
# audits/tactical-gameplay/stage-b-r1-frozen-head.json (its script stays in scratch; Results quotes it)
uv run python -m experiments.tactical_gameplay --split development --arms baseline vent_risk vent_physical \
  vent_look_and_wait vent_own_fresh_kill stage_b_full stage_b_full_minus_look_and_wait \
  stage_b_full_minus_own_fresh_kill stage_b_full_minus_physical stage_b_full_minus_hub_with_grace \
  --output "$SCRATCH/r1-head.json"
# comment-only guard: strings kept; base copy from the branch point B
git show "$B":training/rewards.py > "$SCRATCH/rewards-base.py"
uv run python -c "import ast, sys; a, b = (ast.dump(ast.parse(open(p).read())) for p in sys.argv[1:]); \
  raise SystemExit(0 if a == b else 1)" "$SCRATCH/rewards-base.py" training/rewards.py
git diff "$B" -- training/rewards.py | grep -E '^[+-][^+-]' | grep -vcE '^[+-]\s*#'   # 0
git diff --stat "$B" HEAD -- training/ | tail -1                                      # 2 files
git diff --stat "$B" HEAD -- replays training/artifacts training/reports agents/tactical/learned tests/training \
  api frontend                                                                        # empty
uv run python scripts/verify_ml_evidence.py                    # offline; FAIL 0; never --complete
uv run pytest -m campaign -q
uv run pytest tests/scripts/test_build_demo_bundle.py -q
uv run python scripts/validate_task_docs.py && uv run python scripts/check_doc_facts.py
bash scripts/check.sh; echo "check.sh exit $?"                 # clean worktree, the head that states the numbers
```

Results records the following:
- each command's exit code and what it printed, with the planted cases red before and green after, by name;
- the per-line neuter table and the mutation pass;
- the capture's head, fingerprint, game count, limits hit (if any) and wall;
- the README's tables and the two predeclared readings, quoted;
- the sections this card rests on: `docs/architecture.md` "Layering" (`experiments/` writes separate artifacts),
  "Enforced boundaries" and "Determinism and the substrate ladder"; `docs/experiment-arms.md` (the fields and the one
  engine-arguments helper); the decision memo sections 0 and 7 (ruling 12, the adopted arms); the diagnosis Part 3
  cards 3 and 6; the owner's ruling of 2026-10-06 and the orchestrator's reading (4);
- the material decisions: the observer's role dropped from the cell; the post-tick state; same-room sight;
  `development_wide` at 100 seeds; the summaries' shape; the doc gate's home;
- the open points under Constraints.

Limitations to state:
- Fake meetings eject nobody, so the race, kills and coverage are play-layer mechanics. They are not model play and
  not balance.
- The cell counts positions, not what an agent rendered, remembered or said: it is an upper bound on held
  whereabouts.
- Paired games share a seed and diverge after the first differing decision.
- 100 development seeds per roster, with no held-out confirmation.
- The diagnosis's scratch figures (1,813 idle crew-ticks; 14 of 14 walk-ins) are not reproduced here. Those are
  hosted games, and the lab reads fake ones.

## Results

Not started.
