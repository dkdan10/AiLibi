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

- [x] Review correction (round 2): the cell's bound is stated at the strength the code holds, in the README
  bullet and the `whereabouts_coverage` docstring. Every player a crewmate sees in the state a tick leaves is
  covered. The cell bounds nothing an impostor sees (the rooms next to its own at base sight, and sight from
  inside a vent), and nothing a player holds from earlier ticks, from speech or from a departure it watched.
  Mechanism: `test_every_player_a_crewmate_sees_is_covered`, a Hypothesis property over generated states with no
  sabotage and with each of the map's sabotages active. It reads the cell one player at a time, and
  `test_the_per_player_read_counts_exactly_the_covered_players` checks that read. Planted, both red:
  `test_a_cell_missing_a_player_a_crewmate_sees_fails_the_bound` (a cell that needs two companions) and
  `test_crewmate_sight_beyond_its_own_room_breaks_the_bound` (an engine change that gives crewmates the adjacent
  rooms). The limits are pinned by `test_the_cell_does_not_bound_what_an_impostor_sees` (`next-door`,
  `inside-a-vent`) and `test_the_cell_does_not_bound_a_departure_a_crewmate_watched`. The docstring is in the
  hashed harness, so the capture is retaken at `34205618`. All 800 rows equal round 1's capture over 69,884 leaf
  fields, with 0 differing, and `runtime_fingerprint` equals its `source_sha256`. The `audits/` row is
  re-derived: `test_every_counted_registry_row_matches_the_index` was red before and green after.
- [x] Review correction: the three source-byte pins' base digests are restated as measured. At the branch
  point `derivation_fingerprint` reads `5f63f37c`, the version-two `fit_corpus_fingerprint` `109da039` and
  `bakeoff_substrate_sha` `53a87623`; at the head they read `70c95948`, `7f109b57` and `14524d8b`. Mechanism: the
  inline command under Results, "Review corrections, round 1", run on a tree of the branch point, on the head
  with only `training/rewards.py` at the branch point's bytes, and on the head; `git grep` for the six prefixes
  finds only this card.
- [x] Review correction: the README reads the kill-tick cell as company when the tick ends, not as onlookers at
  the kill, and names the kill-moment rows. Mechanism:
  `test_kill_tick_coverage_is_company_as_the_tick_ends_not_the_kills_witnesses` (a walk-in after the kill covers
  the killer with no witness; a witness who walks out after the kill leaves the killer uncovered), red under the
  pre-tick-state mutant; the count-only probe under Results on the capture's 800 games. The `audits/` row is
  re-derived: `test_every_counted_registry_row_matches_the_index` red before, green after.
- [x] Review correction: the README section itself now names the cell as the role-blind replacement for the
  measurement step of the `patrol_coverage` term, and Results says where each document names it. Mechanism: the
  section's definition of the cell (`grep -c patrol_coverage` over the section prints 1), Outcome item 2 and the
  section 7 paragraph ("the measured candidate for coverage").
- [x] **The cross arms.** Mechanism: a read-only `STAGE_B_IDLE_POLICIES` mapping (`MappingProxyType`) names
  `stage_b_full_kill_cooldown_6_patrol` and `stage_b_full_kill_cooldown_6_accompany`. `candidate_configs` builds each
  from the cooldown-6 arm's validated payload plus `crew_idle_policy`, so the cooldown is derived, never copied. A
  test holds each arm's `model_dump()` equal to the cooldown-6 arm's plus exactly that one field. Planted, red on its
  defect: an arm built from `stage_b_full` (the cooldown dropped); an arm setting `hub_wait`; and the source-change
  case, `STAGE_B_KILL_COOLDOWNS` monkeypatched to 7, under which the cross arms follow. Both arms join
  `test_genuine_candidate_reconstructs_in_api_and_repeats`: each reconstructs with `outcome_verified` and repeats
  byte for byte. The arm-count literal becomes 21.
- [x] **The wider development split.** Mechanism: a read-only `SPLIT_SEEDS` mapping replaces the conditional at
  `:929`: `development` 1000-1007, `held_out` 2000-2015, `development_wide` 1000-1099. The CLI choices derive from its
  keys, and an unknown split raises `ValueError` before any game. Planted: `held-out` (hyphen) raises; a
  `development_wide` that reaches seed 2000 fails the disjointness test. Its first eight rows equal a `--split
  development` run's rows for the same arms, field for field.
- [x] **The coverage cell, exact.** Mechanism: a pure helper over one `WorldState` returns (subjects, covered) by the
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
- [x] **Role-blind by property.** Mechanism: a Hypothesis property over states seeded on the canonical map, with
  random rooms, `alive` and `in_vent` flags and a random role assignment, under `settings(deadline=None)`. The helper's
  result is unchanged under every permutation of roles among players. Perturbed: a variant counting only crewmate
  observers, held in the test, fails the property.
- [x] **The rule it restates, pinned at its source.** Mechanism: the helper implements the rule itself, and a
  Hypothesis property (same generator, `settings(deadline=None)`) holds it to the engine. A living, non-vented subject
  is covered exactly when `engine.rules._witnesses_in_room(state, room=<its room>, exclude={<it>})` is non-empty.
  Planted source-change case: a monkeypatched `_witnesses_in_room` that also admits vented players fails the pin. An
  engine change to the witness rule therefore cannot silently change what the cell means.
- [x] **The walk-in witness rows.** Mechanism: `measure_replay` adds `crew_kill_witnesses`,
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
- [x] **No existing count moves.** Mechanism: a run at the head, written outside the tree, of the ten round-1 arms
  on `--split development`, and a count-only comparison quoted in Results, as the kill-cooldown card ran its own. The
  rows equal `stage-b-r1-frozen-head.json` on every top-level row field. `counts` is compared on the frozen file's
  own keys, and the new count keys are exactly the seven declared here. At authoring that is 2,240 fields with 0
  differing. Perturbed: a scratch copy of the head run with one `kills_crew_witnessed` raised by 1 makes the
  comparison name that row. The capture holds no
  `"experiment_config"` key, so `tests/orchestrator/test_experiment_arms.py`'s committed-payload census (956 rows in
  101 files) is unchanged.
- [x] **The capture is committed, reproducible and read.** Mechanism: one run of the Validation command writes
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
- [x] **Registered.** Mechanism: `docs/artifacts.md`'s `audits/` row states the measured tracked bytes and file count
  at the PR head. `test_every_counted_registry_row_matches_the_index` and offline `verify_ml_evidence` enforce it.
  Planted: the run before the row is updated is red, and Results quotes it.
- [x] **The re-pricing, written.** Mechanism: section 7 gains one paragraph after the four checks, worded as below
  (only the ruling's citation filled in), and the `rewards.py` comment gains the clause below, as `#` lines. A new
  `tests/scripts/test_reopening_repricing_note.py` reads file bytes, never imports. It requires exactly one
  paragraph in section 7 beginning `**Dated 2026-10-06`, naming `correct_reports`, `patrol_coverage`,
  `FITNESS_OBJECTIVE_ID`, `role-blind`, `before any search`, `2026-07-09` and
  `training/artifacts/conviction/verdict.json`. It also requires the contiguous comment block directly above
  `correct_reports = sum(` to name `role-blind`, `FITNESS_OBJECTIVE_ID`, `before any search`, `conviction` and
  `2026-07-09`. Planted, as fixed strings in the test: the paragraph removed; moved into section 8; missing
  `patrol_coverage`; doubled; and the comment without the clause. Each is rejected.
- [x] **Comment-only, proved the way `d1ea113a` proved it.** Mechanism: the strings-kept AST comparison in
  Validation finds `training/rewards.py` equal at base and head. Every changed line of `git diff <base> --
  training/rewards.py` matches `^[+-]\s*#`, and `training/README.md` is the only other file under `training/` that
  changes. Planted, both red:
  - in a byte copy, `"patrol_coverage": patrol_coverage` becomes `patrol_coverage * 0.5`; the AST comparison exits 1;
  - applied in place, the seed-0 pin fails on `patrol_coverage`.
  The file is restored from the byte copy, never from git, and its `shasum` is equal before and after.
- [x] **Nothing frozen moves.** Mechanism: `git diff --stat <base> HEAD` over `replays training/artifacts
  training/reports agents/tactical/learned tests/training api frontend` prints nothing. The seed-0 test passes
  unchanged. Offline `scripts/verify_ml_evidence.py` reports FAIL 0, never `--complete`. `uv run pytest -m campaign`
  passes. `uv run pytest tests/scripts/test_build_demo_bundle.py` passes, with the bundle's inputs untouched.
- [x] **One bounded mutation pass.** Mechanism: a single pass over every production line this card adds or changes,
  using only these classes: F filter, S swap, N comparison, C constant (a role, kind, room or tick read), M message,
  T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the touched suites and
  is restored from a byte copy. A survivor is killed by a new test or named equivalent with its reason. Results
  carries the per-line neuter table: each production line, and the test that goes red when it is neutered.
- [x] **The full gate.** `bash scripts/check.sh` passes in a clean worktree at the head that states the numbers.

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

### Delivery, 2026-10-06

Branch `work/crew-idle-policy-lab` from `2275bdba`; `main` moved to `83806ab0` (docs and card text only) and was
merged at `d6070be6`. Commits: `3f3dec11` (the lab code and its tests), `39e8fea7` (the re-pricing note and its
gate), `e5b1dd80` (the capture, its README section and the registry row), `d6070be6` (the merge), then this card's
Results. Status and the `tasks/README.md` inventory sentence are left to the orchestrator, as Constraints say.

**Acceptance state.** Every box is checked but one. **The summaries** stays open on one field, explained under
Deviations: the card asks the coverage summary for a kill-tick total, which none of the seven declared counts
carries, and the card also fixes the new count keys at exactly seven. The summary publishes `kills` and the games
without a kill tick instead. The orchestrator picks between the two readings; nothing else waits on it.

**Sections this card rests on.**
- `docs/architecture.md`: "Layering" (`experiments/` writes its own artifacts and nothing reads them back),
  "Enforced boundaries" (no `agents/` or `engine/` file changes; import-linter passes in `check.sh`), and
  "Determinism and the substrate ladder" (fake games repeat byte for byte; nothing recorded moves).
- `docs/experiment-arms.md`: "The fields" (the cross sets the existing `crew_idle_policy`, so there is no new field)
  and "One engine-arguments helper" (the lab's two engine calls are unchanged; the new folds read events and states
  only, and the tests advance through `engine_arguments`).
- `tasks/decision-2026-09-24-stage-b-wave.md`: section 0 (ruling 12, the ML hold), section 7 (the seven adopted
  arms), 8.1 (the owner's ruling of 2026-10-06, the committed home the section 7 paragraph cites), 8.2 item 4 (the
  orchestrator's reading 4, which this card carries) and 8.5 (the one-writer map and the merge before F).
- `tasks/diagnosis-2026-10-02/README.md` Part 3: card 6 (the cross) and card 3 (the witness rows).

**Decisions.**
- Orchestrator ruling 1. The lab ran with the fake provider on development seeds only, trained nothing and moved no
  artifact. Its reading says whether a hand-written idle policy closes the slack a learned crew policy would need.
  It decides nothing about ML.
- Orchestrator ruling 2. The whereabouts cell was defined before the run, role-blind, from engine positions, the
  same way for every role (`whereabouts_coverage`). Outcome item 2 names it as the role-blind replacement for
  `patrol_coverage`'s measurement step, and from round 1 so does the README section's definition of the cell; the
  section 7 paragraph calls it the measured candidate for coverage (corrected in round 1: this line first said the
  README section named it, which it did not). No crewmate-observer variant was built; the only one in
  the tree is the perturbed helper inside a test, which the role-blind property rejects.
- Orchestrator ruling 3. The re-pricing is comment-only, of `d1ea113a`'s class; the pins that read source bytes are
  named below with their state at the head. The seed-0 pin stays. The note names the two crew terms only, as the
  rule is written. The grade question (memo D10-R3) stays the owner's open point. The conviction GO's
  re-registration at a reopening is folded into the note.
- Orchestrator ruling 4. Diagnosis card 3's two rows (crew-witnessed kills and walk-ins) are included on the
  existing cooldown arms. They cost one fold and one more arm in the same run, well under an hour.
- Orchestrator ruling 5. `main` moved under this branch (`83806ab0`, docs only). It was merged, and the capture's
  fingerprint still equals the merged tree's (`runtime_fingerprint` exit 0 at `d6070be6`), so there was no
  re-capture. If `route-lines-field` or `census-held-data-cells` lands before this card merges, the branch merges
  `main` again and re-captures, comparing rows on the frozen file keys.
- Orchestrator ruling 6. Nothing ships. The demo bundle was built twice in this worktree, at `83806ab0` and at
  `d6070be6` (`scripts/build_demo_bundle.py --out <scratch>`). `diff -r` prints nothing over 109 files. The
  orchestrator merges.
- The observer's role is dropped from the cell. A crewmate-observer variant would read a role, so it could not
  re-price a role-reading term.
- The cell reads `TickAdvanced.state`, the state the tick leaves, so a move that joins two players counts on that
  tick.
- Sight is same-room only. It is the sight every observer holds in every visibility mode, and the engine's
  kill-witness rule uses it. An impostor's wider base sight is deliberately not used.
- `development_wide` has 100 seeds (1000-1099). It begins with `development` and stays below the held-out band, and
  each paired column holds 100 seeds per roster.
- The summaries' shape. `whereabouts_coverage[arm][roster]` and `idle_policy_pairs[arm][roster]` mirror
  `ticks_to_parity`'s shape, so a reader indexes all three the same way. Shares are compared exactly, by cross
  multiplication, never as floats. A pair is published only when its reference ran in the same comparison.
  Mismatched seeds, or a game with no subject, raise.
- The doc gate lives in `tests/scripts/test_reopening_repricing_note.py`. It reads bytes and imports nothing from
  `training/`. It also refuses a second dated paragraph anywhere in the README and a clause detached from its anchor.

**The capture.** `audits/tactical-gameplay/stage-b-idle-policy-development.json`, written once by the Validation
command at the clean committed head `39e8fea7`. `source_sha256` is
`31814833632ed9cca17a7a3a43afe91082b9a23459925ad5989af73e0fe5a51d`. Four arms ran on 100 seeds per roster: 800
games, all `completed`, every `error` null, none at a limit (the most any game used was 71 ticks, 52 calls, 220,212
input and 2,990 output tokens). There were 14,190 fake calls, 52,639,727 input and 815,925 output tokens, $0, and
77.35 s of wall (`/usr/bin/time -p`). Round 2 retook the capture at `34205618`, with every row unchanged; its
stamp is under "Review corrections, round 2". The README's compact check, run on the JSON, reprints all 20 table rows, and
they equal the README's rows in order (`rows printed 20 rows in the tables 20; identical, in order: True`).

The 9p2i tables, quoted from the README (4p1i is there beside them):

| Arm | Task wins | Parity wins | Tasks done | Kills | Crew-witnessed kills | Walked in | Kills with a walk-in | Meetings | Hub waits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stage_b_full` | 4 | 96 | 1020/1399 | 497 | 17 | 20/20 | 17 | 228 | 2714 |
| `stage_b_full_kill_cooldown_6` | 27 | 72 | 1253/1400 | 457 | 32 | 45/45 | 32 | 254 | 4840 |
| `stage_b_full_kill_cooldown_6_patrol` | 31 | 69 | 1256/1399 | 445 | 45 | 54/54 | 45 | 262 | 0 |
| `stage_b_full_kill_cooldown_6_accompany` | 34 | 66 | 1277/1399 | 444 | 47 | 53/53 | 47 | 260 | 0 |

| Arm | Coverage at kill ticks | Coverage at play ticks | Games without a kill tick | Covered share per game, min / median / max |
| --- | ---: | ---: | ---: | ---: |
| `stage_b_full` | 1479/2862 (51.7%) | 14143/22414 (63.1%) | 0 | 0.083 / 0.533 / 0.846 |
| `stage_b_full_kill_cooldown_6` | 1650/2713 (60.8%) | 20361/30401 (67.0%) | 0 | 0.200 / 0.600 / 0.900 |
| `stage_b_full_kill_cooldown_6_patrol` | 1353/2624 (51.6%) | 17095/28247 (60.5%) | 0 | 0.227 / 0.511 / 0.767 |
| `stage_b_full_kill_cooldown_6_accompany` | 1397/2613 (53.5%) | 17467/28474 (61.3%) | 0 | 0.200 / 0.533 / 0.818 |

The two predeclared readings, quoted from the README:

> **What the cross shows.** On the 9-player roster neither hand-written alternative raises whereabouts coverage.
> Waiting at the hub keeps more players in company than walking about does, at kill ticks and over the whole game.
> On the 4-player roster both raise it at kill ticks, from 10.5% to 16.5% and 16.3%, but 48 of the 66 paired seeds
> read equal. [...] **This reading decides nothing about ML**; the hold on ML stands whatever it reads.

> **The best arm's uncovered remainder.** On 9p2i the best of the three at kill ticks is hub wait itself: 1,063 of
> its 2,713 subjects (39.2%) are uncovered. On 4p1i it is patrol: 213 of 255 (83.5%). That remainder is an upper
> bound on what any idle policy, hand-written or learned, could still cover in this cell under these rules.

> **The two cooldown rows, as mechanics.** [...] fake meeting ejects nobody, so the rise in the recorded hosted
> games, from 4 of 227 kills a crewmate saw in the first Stage-B candidate round to 14 of 195 in the shown 9-player
> set, is neither confirmed nor explained here.

The paired seeds on 9p2i: patrol's kill-tick share is below hub wait's on 77 of 100 seeds (17 above, 6 equal), and
accompany's on 70 (22 above, 8 equal). Over play ticks they are below on 93 and 90.

**Validation, at `d6070be6` unless named (exit codes captured directly).**

```
env | grep -c '^AILIBI_'                                  0
pytest <the card's eight files> -n 6 --dist loadfile       405 passed in 25.27s
the capture (Validation command, at 39e8fea7)              exit 0, 77.35 s, 800 games
runtime_fingerprint == capture source_sha256               exit 0 (at 39e8fea7 and d6070be6)
  perturbed: one fingerprint character changed in a scratch copy      exit 1
ten round-1 arms, --split development, into scratch        exit 0
  keyed count-only comparison against stage-b-r1-frozen-head.json:
    rows 160; fields compared 2240; differing 0; rows whose new count keys are not exactly the seven 0
    top-level keys only in the head run: idle_policy_pairs, ticks_to_parity, whereabouts_coverage
  perturbed: one kills_crew_witnessed raised by 1 in a scratch copy:
    differing 1: stage_b_full/9p2i/1003: counts ['kills_crew_witnessed']   exit 1
the four capture arms, --split development, into scratch   exit 0
  the capture's first eight seeds, --prefix (counts in full): rows 64; fields compared 896; differing 0
committed-payload census: grep -c '"experiment_config"' on the capture   0
  pytest tests/orchestrator/test_experiment_arms.py -k committed           2 passed (956 rows, 101 files)
AST comparison, strings kept, base copy from 2275bdba      exit 0
  planted: "patrol_coverage": patrol_coverage * 0.5 in a byte copy        exit 1
git diff 2275bdba -- training/rewards.py | ... | grep -vcE '^[+-]\s*#'    0
git diff --stat 2275bdba HEAD -- training/ | tail -1      2 files changed, 19 insertions(+), 1 deletion(-)
git diff --stat 2275bdba HEAD -- replays training/artifacts training/reports agents/tactical/learned tests/training api frontend
                                                          (prints nothing)
seed-0 pin, planted in place (byte copy of the planted file over training/rewards.py):
  1 failed: {'patrol_coverage': 0.3431372549019608} != {'patrol_coverage': 0.6862745098039216}
  restored from the byte copy: shasum 1cde7fe27b1b... before and after; git status clean; 1 passed
uv run python scripts/verify_ml_evidence.py   checks: 63 | OK 51 | FAIL 0 | ABSENT 7 | INFO 5; exit 0 (never --complete)
uv run pytest -m campaign -q -n auto          337 passed, exit 0
uv run pytest tests/scripts/test_build_demo_bundle.py -q   31 passed
scripts/validate_task_docs.py                 passed: 390 phase tasks, 390 prompts, 101 work cards; exit 0
scripts/check_doc_facts.py                    exit 0
verify_samples.sh: samples/9p2i 50, samples/4p1i 50, ml_corpus/9p2i 150, ml_corpus/4p1i 50,
                   candidates/stage-b-r1/9p2i 50, each "verified clean"
build_sample_report.py --sample-dir <each of the five sets> --check   "... is consistent with its replays." x5
publish_process_scorecard.py --check, publish_gameplay_census.py --check   consistent, exit 0
the demo bundle, built at 83806ab0 and at d6070be6 in one checkout: diff -r prints nothing (109 files)
```

`npm --prefix frontend test` and the e2e were not run: no frontend file changes. `generate_prompts --check` runs
inside `check.sh`; no template changes.

**Planted and perturbed cases, by name** (each red on its defect, green on the shipped code):
- The cross: `test_a_cross_arm_without_the_cooldown_or_at_hub_wait_fails` (built from `stage_b_full`; at
  `hub_wait`) and `test_the_cross_arms_follow_the_cooldown_dial` (`STAGE_B_KILL_COOLDOWNS` patched to 7).
- The splits: `test_a_wide_split_reaching_the_held_out_seeds_fails` (reaching 2000; not beginning with
  `development`), `test_an_unknown_split_is_refused_before_any_game` (`held-out`, `Development`, `''`,
  `development `), and `test_the_command_line_offers_exactly_the_declared_splits` (`--split held-out` exits 2).
- The cell: the five exact hand-built cases. `test_a_cell_counting_only_crewmate_observers_fails_the_property` (the
  property, run on the perturbed helper, raises). `test_a_witness_rule_that_admits_vented_players_breaks_the_pin`
  (`engine.rules._witnesses_in_room` patched; the pin raises).
- The walk-ins: the six parametrized cases, `test_walk_ins_count_per_witness_and_once_per_kill` and
  `test_a_walk_in_is_read_against_the_kills_own_room`.
- The summaries: `test_a_summary_over_another_arms_rows_or_a_pair_against_stage_b_full_fails`,
  `test_pairs_refuse_arms_that_ran_different_seeds` and `test_a_game_without_a_subject_has_no_share`.
- The note: `test_reopening_repricing_note.py`'s six fixed planted texts (removed, moved into section 8, missing
  `patrol_coverage`, doubled, copied after section 8, the comment without the clause, detached from the anchor).
  The gate's functions run on the branch point's own bytes report "section 7 holds 0 paragraphs" and five missing
  comment terms.
- The registry: with the capture staged and the row unchanged, `test_every_counted_registry_row_matches_the_index`
  failed: "audits/: docs/artifacts.md promises 333 files, the index tracks 334" and "promises 28,136,878 tracked
  bytes, the tracked files contain 31,430,328 bytes". With the row updated, 1 passed.

**The pins that read source bytes** (ruling 3; the class `d1ea113a` established).
- Value pins compare computed values, which no comment moves. The seed-0 pin passes unchanged and fails on a value
  change (above).
- `training.provenance.derivation_fingerprint` hashes the 110-file `derivation_files` closure, which includes
  `training/rewards.py`. It reads `5f63f37c` at the branch point and `70c95948` at the head. The version-two
  `fit_corpus_fingerprint` moves from `109da039` to `7f109b57`, and `bakeoff_substrate_sha` from `53a87623` to
  `14524d8b`. `git grep` finds none of the six prefixes outside this card, so no committed stamp binds them; the
  committed fits carry version-one identities over corpus bytes alone (`test_current_loader_refuses_historical_fit`
  is in the 405 above). Corrected in round 1, with the command inline there: the base prefixes first printed here
  did not reproduce.
- `scripts/_tournament_progress.py::configuration_fingerprint` hashes every `training/*.py`, so it moves too. It binds
  only a live tournament's `--resume`, and no progress record is committed. No tournament `--resume` may span this
  edit. It also hashes provider settings from the environment, so it was not computed here.
- Offline `verify_ml_evidence`: FAIL 0, above. The corpus FROZEN line and every artifact are untouched (the empty
  `git diff --stat` above).

**The mutation pass, and the per-line neuter table.** One pass over `experiments/tactical_gameplay.py`, the only
production module touched (the `training/rewards.py` change is comment-only, proved above). There were 40 per-line
neuters (A: each added row, line or argument deleted) and 39 mutants of the eight classes (B). Each ran alone with
`pytest -x` over `tests/experiments/test_tactical_gameplay.py`, `tests/orchestrator/test_experiment_config.py` and
the kill-cooldown readers' parity test. The file was restored from a byte copy after each run, and its sha256
(`c185cdcd...`) was re-checked after each run and at the end. Result: 78 killed, 1 equivalent. Two cases were
planted after reading the diff, before the first probe ran: `test_a_walk_in_is_read_against_the_kills_own_room`
(every other walk-in case kills in ADMIN, so a constant room read would survive) and the `@example` game in
`test_on_lab_games_walk_ins_stay_within_crew_witnessed_kills`, with its bound `kills_crew_witnessed <=
crew_kill_witnesses` (without the forced game, a dropped `fold_kill_witnesses` call could survive on random seeds).
No probe first came back green except B10.

| id | class | what was neutered or mutated | result | first red test |
| --- | --- | --- | --- | --- |
| A1 | neuter | patrol row of STAGE_B_IDLE_POLICIES | killed | `test_genuine_candidate_reconstructs_in_api_and_repeats[stage_b_full_kill_cooldown_6_patrol]` |
| A2 | neuter | accompany row of STAGE_B_IDLE_POLICIES | killed | `test_genuine_candidate_reconstructs_in_api_and_repeats[stage_b_full_kill_cooldown_6_accompany]` |
| A3 | neuter | development row of SPLIT_SEEDS | killed | `test_source_identity_binds_the_exact_consumed_roster_before_running` |
| A4 | neuter | held_out row of SPLIT_SEEDS | killed | `test_the_split_table_keeps_development_apart_from_held_out` |
| A5 | neuter | development_wide row of SPLIT_SEEDS | killed | `test_the_split_table_keeps_development_apart_from_held_out` |
| A6 | neuter | crew_idle_policy argument of the cross arm | killed | `test_the_cross_arms_are_the_reference_arm_plus_one_idle_policy` |
| A7 | neuter | reference payload spread of the cross arm | killed | `test_the_cross_arms_are_the_reference_arm_plus_one_idle_policy` |
| A8 | neuter | fold_whereabouts call in measure_replay | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| A9 | neuter | fold_kill_witnesses call in measure_replay | killed | `test_on_lab_games_walk_ins_stay_within_crew_witnessed_kills` |
| A10 | neuter | zero-initialised counts | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| A11 | neuter | split refusal | killed | `test_an_unknown_split_is_refused_before_any_game[held-out]` |
| A12 | neuter | whereabouts_coverage output key | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A13 | neuter | idle_policy_pairs output key | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A14 | neuter | play-tick subjects increment | killed | `test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair` |
| A15 | neuter | play-tick covered increment | killed | `test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair` |
| A16 | neuter | kill-tick subjects increment | killed | `test_a_tick_with_two_kills_counts_its_players_once` |
| A17 | neuter | kill-tick covered increment | killed | `test_a_tick_with_two_kills_counts_its_players_once` |
| A18 | neuter | crew_kill_witnesses increment | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[already-in-the-room]` |
| A19 | neuter | walked-in increment | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[walks-in-before-the-kill]` |
| A20 | neuter | kills-with-walk-in increment | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[walks-in-before-the-kill]` |
| A21 | neuter | summary games row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A22 | neuter | summary kills row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A23 | neuter | summary four sums | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A24 | neuter | summary games without a kill tick | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A25 | neuter | summary share minimum | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A26 | neuter | summary share median | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A27 | neuter | summary share maximum | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A28 | neuter | pairs reference row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A29 | neuter | pairs seeds row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A30 | neuter | pairs seeds-with-kill-ticks row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A31 | neuter | pairs kill higher row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A32 | neuter | pairs kill equal row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A33 | neuter | pairs kill lower row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A34 | neuter | pairs play higher row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A35 | neuter | pairs play equal row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A36 | neuter | pairs play lower row | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| A37 | neuter | no-share refusal | killed | `test_a_game_without_a_subject_has_no_share` |
| A38 | neuter | reference-absent return | killed | `test_pairs_need_the_reference_in_the_same_comparison` |
| A39 | neuter | cross-arm-absent skip | killed | `test_pairs_need_the_reference_in_the_same_comparison` |
| A40 | neuter | different-seeds refusal | killed | `test_pairs_refuse_arms_that_ran_different_seeds` |
| B1 | F filter | drop alive from the standing filter | killed | `test_a_dead_player_covers_nothing_and_is_not_a_subject` |
| B2 | F filter | drop in_vent from the standing filter | killed | `test_a_vented_player_covers_nothing_and_is_not_covered` |
| B3 | F filter | subjects count every player | killed | `test_a_dead_player_covers_nothing_and_is_not_a_subject` |
| B4 | F filter | drop the other-room condition | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[moves-to-its-own-room]` |
| B5 | F filter | drop the crew role filter | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[an-impostor-walks-in]` |
| B6 | F filter | drop the kill-tick share filter | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B7 | F filter | pair kill seeds without the reference's kill tick | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B8 | S swap | pre-tick state for coverage | killed | `test_the_state_the_tick_leaves_is_read` |
| B9 | S swap | every player instead of the witness list | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[already-in-the-room]` |
| B10 | S swap | post-tick state for the role read | survived | none (equivalent, below) |
| B11 | S swap | summary reads the reference arm's rows | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B12 | S swap | play pairs over the kill seeds | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B13 | S swap | walk-ins over every witness | killed | `test_a_kill_witness_walked_in_only_from_another_room_before_the_kill[an-impostor-walks-in]` |
| B14 | N comparison | a subject as its own observer | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` |
| B15 | N comparison | kill-tick test inverted | killed | `test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair` |
| B16 | N comparison | no-share test as a None test | killed | `test_a_game_without_a_subject_has_no_share` |
| B17 | N comparison | seed-set test inverted | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B18 | N comparison | reference-absent test inverted | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B19 | N comparison | split test as a None test | killed | `test_an_unknown_split_is_refused_before_any_game[held-out]` |
| B20 | C constant | kill room read as ADMIN | killed | `test_a_walk_in_is_read_against_the_kills_own_room` |
| B21 | C constant | kill-tick kind read as always true | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B22 | C constant | arrival kind read as always true | killed | `test_genuine_candidate_reconstructs_in_api_and_repeats[baseline]` |
| B23 | C constant | share scope read as kill ticks | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B24 | M message | split refusal message | killed | `test_an_unknown_split_is_refused_before_any_game[held-out]` |
| B25 | M message | different-seeds message | killed | `test_pairs_refuse_arms_that_ran_different_seeds` |
| B26 | M message | no-share message | killed | `test_a_game_without_a_subject_has_no_share` |
| B27 | T tuple | drop subjects-at-kill-ticks key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B28 | T tuple | drop covered-at-kill-ticks key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B29 | T tuple | drop subjects-at-play-ticks key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B30 | T tuple | drop covered-at-play-ticks key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B31 | T tuple | drop crew_kill_witnesses key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B32 | T tuple | drop walked-in key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B33 | T tuple | drop kills-with-walk-in key | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` |
| B34 | B branch swap | higher and lower swapped | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B35 | B branch swap | share minimum and maximum swapped | killed | `test_the_comparison_publishes_coverage_and_pairs_over_its_own_arms` |
| B36 | L literal | cross arm from a literal cooldown 6 | killed | `test_the_cross_arms_follow_the_cooldown_dial` |
| B37 | L literal | seeds as the development literal | killed | `test_the_wide_split_runs_its_hundred_seeds` |
| B38 | L literal | command-line choices as the old literal | killed | `test_the_command_line_offers_exactly_the_declared_splits` |
| B39 | L literal | pairs' reference read as its literal | killed | `test_a_summary_over_another_arms_rows_or_a_pair_against_stage_b_full_fails` |

B10 is equivalent. The role read takes `step.state` in place of `step.pre_state`, and no engine action changes a
role within a tick, so the two reads are identical for every witness.

**Deviations.**
- The summaries' kill-tick total (acceptance **The summaries**, left open). A kill tick can hold two kills on 9p2i,
  so `event:Killed` does not count kill ticks, and none of the seven declared counts does. The card also fixes the
  new count keys at exactly seven (**No existing count moves**, Record impact). `whereabouts_coverage` publishes
  `kills` and `games_without_a_kill_tick` in its place. A game has a kill tick exactly when it has a subject at
  one, because its killer is alive. Option (a): accept this shape. Option (b): add an eighth count, `kill_ticks`,
  which changes the declared seven, the comparison script and Record impact.
- `tests/eval/test_kill_cooldown_readers.py`: its comparison stub gains the four coverage keys, because the summary
  reads them strictly. Constraints name this follow-through. No assertion changed.
- `build_comparison(split=...)` is typed `str`, and `SPLIT_SEEDS` is the one source of truth that refuses. A
  `Literal` would make the refusal test a type error.
- `tasks/work/kill-cooldown-arm.md:307` still says the test counts 19 arms. It is a done card's record of its own
  head, so it is not edited.

**Limitations.**
- Fake meetings eject nobody, so the race, kills and coverage are play-layer mechanics. They are not model play and
  not balance.
- The cell counts positions, not what an agent rendered, remembered or said. It bounds only what crewmates see in
  the state a tick leaves. It bounds nothing an impostor sees, nor anything a player holds from earlier ticks, from
  speech or from a departure it watched. (Corrected in round 2: this line first called the cell an upper bound on
  held whereabouts.)
- Paired games share a seed and diverge after the first differing decision.
- 100 development seeds per roster, with no held-out confirmation.
- The diagnosis's scratch figures (1,813 idle crew-ticks; 14 of 14 walk-ins) are not reproduced here. Those are
  hosted games, and the lab reads fake ones. In the lab every crewmate witness on both rosters and all four arms
  walked in on the kill tick, which matches their direction but is a different measurement.

**Open for the owner** (Constraints): which grade of "reads roles" a future objective forbids (the two crew terms
only, as the note says, or also `meetings_survived` and the teammate witness discount; memo D10-R3), and whether a
crewmate-observer variant of the cell is ever wanted (it would read a role and could not be the re-pricing).

**The full gate.** `bash scripts/check.sh` runs once at the head that states these numbers; its exit code is
recorded in the next subsection.

### The full gate, 2026-10-06

`bash scripts/check.sh > <scratch>/check.log 2>&1; echo "check.sh exit $?"` was run once, in this clean worktree,
at `0656f099`, the head whose Results state the numbers above (`main` still at `83806ab0`). It printed
`check.sh exit 0`. Ruff passed, with 554 files already formatted. The four import-linter contracts were kept, 0
broken. Task docs validation passed, and all 390 prompts were in sync. Strict mypy found no issues in 525 source
files. Pytest gave 10,333 passed, 20 skipped and 3 xfailed in 397.97 s. The frontend gave 26 test files and 695
tests passed, and the build completed. This commit changes only this card.

### Review corrections, round 1 (2026-10-06)

Independent verification of `9da3f696` found three blocking problems, all in evidence claims and documentation. This
round changes no production line. `experiments/tactical_gameplay.py`, everything under `training/` and every other
hashed source are byte-identical to `9da3f696`, so the capture stands as committed. `runtime_fingerprint` still
equals its `source_sha256` (exit 0 at this head). `main` is still at `83806ab0`, so there was no merge and no
re-capture. This round changes four files:
- `audits/tactical-gameplay/README.md`: two bullets of the idle-policy section;
- `docs/artifacts.md`: the `audits/` row;
- `tests/experiments/test_tactical_gameplay.py`: one planted test;
- this card.

**Finding 1: the base digests did not reproduce.** The pins paragraph above first printed `354d9de9`, `92fa327f` and
`a77eb4fb` for the branch point's `derivation_fingerprint`, version-two `fit_corpus_fingerprint` and
`bakeoff_substrate_sha`. Those values do not reproduce. The scratch script that printed them is gone, so the cause
is not known. The digests were recomputed at this head by two methods, with 110 files in the derivation closure
each time:

| Tree | `derivation_fingerprint` | `fit_corpus_fingerprint` (v2) | `bakeoff_substrate_sha` |
| --- | --- | --- | --- |
| the branch point `2275bdba` | `5f63f37c` | `109da039` | `53a87623` |
| this head, with only `training/rewards.py` at `2275bdba`'s bytes | `5f63f37c` | `109da039` | `53a87623` |
| this head | `70c95948` | `7f109b57` | `14524d8b` |

At this head the production `training.bakeoff.map_elites.bakeoff_substrate_sha()` also prints `14524d8b`. The
first two base prefixes equal the Evidence section's values at `76270d6c`, because nothing in the closure changed
between those commits. The pins paragraph above now carries the measured values. The commands follow; `SCRATCH` is a
directory outside the worktree. The second method runs the same command on a `git archive HEAD` tree after
`git show 2275bdba:training/rewards.py` has overwritten its `training/rewards.py`.

```
git archive --output="$SCRATCH/base.tar" 2275bdba
mkdir "$SCRATCH/base" && tar -xf "$SCRATCH/base.tar" -C "$SCRATCH/base"
uv run python -c "import hashlib, sys; from pathlib import Path; \
  from training.provenance import derivation_fingerprint as d, fit_corpus_fingerprint as f; \
  c = Path('replays/ml_corpus/9p2i'); [print(d(r)[:8], f(c, source_root=r)[:8], \
  hashlib.sha256(('cell-substrate-v2:' + f(c, source_root=r)).encode()).hexdigest()[:8]) \
  for r in (Path(sys.argv[1]), Path('.').resolve())]" "$SCRATCH/base"
#   5f63f37c 109da039 53a87623
#   70c95948 7f109b57 14524d8b                                        exit 0
git grep -l -e 5f63f37c -e 109da039 -e 53a87623 -e 70c95948 -e 7f109b57 -e 14524d8b
#   tasks/work/crew-idle-policy-lab.md                                (nothing else)
```

The pins that read source bytes are still green at this head, and a value change still trips the value pin. The
checks below ran on this head:
- Offline `verify_ml_evidence` reads checks 63, OK 51, FAIL 0, ABSENT 7, INFO 5 (exit 0, never `--complete`).
- The seed-0 pin and `test_current_loader_refuses_historical_fit` are in the 407 passed below.
- Planted in a byte copy, `"patrol_coverage": patrol_coverage * 0.5` makes the AST comparison exit 1.
- Applied in place, the same change fails the seed-0 pin:
  `{'patrol_coverage': 0.3431372549019608} != {'patrol_coverage': 0.6862745098039216}`.
- Restored from the byte copy, `training/rewards.py` has the same `shasum` before and after (`308a1fbc99eb...`), and
  the pin passes again.

**Finding 2: the kill-tick cell reads company when the tick ends, not onlookers at the kill.** The README said "A
killer alone with the body is uncovered, so this figure also says whether a kill had any onlooker." Outcome item 2
says the same of the kill-tick cell. **Review correction for that Outcome sentence.** The cell reads the state the
tick leaves, so for a killer it reads company when the tick ends, not an onlooker at the kill. The engine applies a
tick's actions in order and records a kill's witnesses when the kill applies, which gives two cases:
- a player who walks into the room after the kill on the same tick covers the killer without witnessing the kill;
- a witness who walks out after the kill can leave the killer uncovered.

The kill-moment reading is the witness rows (`kills_crew_witnessed`, `crew_kill_witnesses` and the walk-ins), which
read the engine's witness list. The Outcome stays as the contract was written, and this correction governs how that
sentence is read. The README bullet now reads:

> **At kill ticks** sums the same over the play ticks with at least one kill, each tick counted once however many
> kills it holds. Each killer is one of those subjects, covered when anyone stood with it as the tick ended. That is
> company at the end of the tick, not an onlooker at the kill. The engine applies a tick's actions in order, so a
> player who walks in after the kill on the same tick covers the killer without having seen the kill, and a witness
> who walks out after the kill can leave the killer uncovered. Crew-witnessed kills and the two walk-in counts below
> read the moment of the kill, from the witnesses the engine recorded.

`test_kill_tick_coverage_is_company_as_the_tick_ends_not_the_kills_witnesses` plants both cases through
`advance_tick` under the cooldown-6 arm's engine arguments:
- `walks-in-after-the-kill`: the `Killed` event lists no witness, and the killer is covered (4 of 4 at the kill tick);
- `walks-out-after-the-kill`: the witness is listed, and the killer is uncovered (2 of 4).

Under the pre-tick-state mutant (M4 below) it is red. How often each case happens, count-only, on the capture's 800
games re-run at this head through `run_candidate` (every arm's kills equal the capture's):

| Roster | Arm | Kills | Killer covered, no witness | of which every companion walked in | A witness, killer uncovered |
| --- | --- | ---: | ---: | ---: | ---: |
| 4p1i | `stage_b_full` | 162 | 2 | 2 | 0 |
| 4p1i | `stage_b_full_kill_cooldown_6` | 105 | 0 | 0 | 0 |
| 4p1i | `stage_b_full_kill_cooldown_6_patrol` | 93 | 8 | 8 | 0 |
| 4p1i | `stage_b_full_kill_cooldown_6_accompany` | 94 | 8 | 8 | 0 |
| 9p2i | `stage_b_full` | 497 | 34 | 34 | 0 |
| 9p2i | `stage_b_full_kill_cooldown_6` | 457 | 46 | 46 | 0 |
| 9p2i | `stage_b_full_kill_cooldown_6_patrol` | 445 | 51 | 51 | 1 |
| 9p2i | `stage_b_full_kill_cooldown_6_accompany` | 444 | 61 | 61 | 1 |

The columns mean the following:
- "Killer covered, no witness": the killer is covered in the state the tick leaves, and the `Killed` event lists no
  witness of any role.
- "Of which every companion walked in": every player covering the killer moved into the kill's room from another
  room on that tick. None of them is on the witness list, so each one arrived after the kill.

These are lab counts of fake games, not cells of the committed capture. The README therefore states the mechanism
without them. The probe (about 100 s; it prints counts only):

```
uv run python - <<'EOF'
import tempfile
from collections import Counter
from pathlib import Path

import experiments.tactical_gameplay as lab
from engine.events import KilledEvent, MovedEvent

fold, tally, key = lab.fold_kill_witnesses, Counter(), []


def probe(step, counts):
    fold(step, counts)
    moved = {(e.actor, e.to_room) for e in step.events if isinstance(e, MovedEvent) and e.from_room != e.to_room}
    for e in step.events:
        if isinstance(e, KilledEvent):
            room = step.state.players[e.actor].room
            company = [i for i, p in step.state.players.items() if i != e.actor and p.alive and not p.in_vent and p.room == room]
            tally[key[-1], "kills"] += 1
            tally[key[-1], "killer covered, no witness"] += bool(company) and not e.witnesses
            tally[key[-1], "of which every companion walked in"] += bool(company) and not e.witnesses and all((i, room) in moved for i in company)
            tally[key[-1], "witness, killer uncovered"] += bool(e.witnesses) and not company


lab.fold_kill_witnesses = probe
configs = lab.candidate_configs()
with tempfile.TemporaryDirectory() as tmp:
    for arm in ("stage_b_full", "stage_b_full_kill_cooldown_6", "stage_b_full_kill_cooldown_6_patrol", "stage_b_full_kill_cooldown_6_accompany"):
        for name in ("4p1i", "9p2i"):
            roster = lab.Roster.model_validate_json(Path(f"replays/samples/{name}/roster.json").read_bytes())
            key.append(f"{name} {arm}")
            for seed in lab.SPLIT_SEEDS["development_wide"]:
                lab.run_candidate(seed=seed, roster=roster, config=configs[arm], replay_path=Path(tmp) / f"{arm}-{name}-{seed}.jsonl")
for (row, column), value in sorted(tally.items()):
    print(row, column, value)
EOF
```

The `audits/` row follows the README's new bytes. Before the row moved, `test_every_counted_registry_row_matches_the_index`
failed with "audits/: docs/artifacts.md promises 31,430,328 tracked bytes, the tracked files contain 31,431,207
bytes". With the row at 31,431,207 tracked bytes / 334 files, it passes. The README's tables did not change, and its
compact check still reprints all 20 rows identically and in order. A `git grep` for the old sentence over `*.md` and
`*.py` finds it only in this card's Outcome, which this correction covers.

**Finding 3: where the cell is named as the re-pricing.** The Decisions line for ruling 2 said that the README
section named the cell as the re-pricing of `patrol_coverage`'s measurement step. It did not: none of
`patrol_coverage`, `re-pric` or `measurement step` appeared in the section. The README's definition of the cell now
ends with this sentence:

> It is the role-blind replacement for the step where the one committed training objective measures crew coverage.
> That objective's `patrol_coverage` term pays a crewmate for sharing a room with a player who is an impostor, which
> reads a role. `training/README.md` section 7 records that any reopening of the training work redefines that term
> without reading roles before any search; this cell is the measured candidate, and nothing here adopts it.

Outcome item 2 names the cell as the role-blind replacement for `patrol_coverage`'s measurement step. The section 7
paragraph calls it "the measured candidate for coverage". That paragraph is not edited: the doc gate and the
comment-only proof pin its bytes. The Decisions line above is corrected in place. Command:
`sed -n '/^### Development: the crew idle-policy cross/,/^### Held-out: 4p1i/p' audits/tactical-gameplay/README.md |
grep -c patrol_coverage` prints 1.

**The mutation pass, bounded to the spans the findings name.** The spans are `whereabouts_coverage` and
`fold_whereabouts`, the kill-tick cell; no production line changed this round. There were ten mutants, of the listed
classes only. Each ran alone against `tests/experiments/test_tactical_gameplay.py` (`-x -n 4`), and the new test
also ran alone. The file was restored from a byte copy after each mutant, with its sha256 (`c185cdcd0120...`)
re-checked. All ten mutants were killed, and none survived. The new test alone came back green on M2, M7, M9 and M10;
an earlier test kills each of those, as the table names.

| id | class | mutant | result | first red test | new test alone |
| --- | --- | --- | --- | --- | --- |
| M1 | F filter | drop `alive` from the standing filter | killed | `test_a_dead_player_covers_nothing_and_is_not_a_subject` | red |
| M2 | F filter | drop `in_vent` from the standing filter | killed | `test_a_vented_player_covers_nothing_and_is_not_covered` | green |
| M3 | F filter | covered counts every room (company filter dropped) | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red |
| M4 | S swap | pre-tick state for the cell | killed | `test_the_state_the_tick_leaves_is_read` | red |
| M5 | N comparison | company test inverted | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red |
| M6 | N comparison | kill-tick test inverted | killed | `test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair` | red |
| M7 | C constant | kill-tick kind read as always true | killed | `test_a_tick_without_a_kill_adds_only_to_the_play_tick_pair` | green |
| M8 | C constant | room read as `ADMIN` | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red |
| M9 | S swap | subjects over the standing players only | killed | `test_a_vented_player_covers_nothing_and_is_not_covered` | green |
| M10 | T tuple | drop the covered-at-kill-ticks key from the declared counts | killed | `test_every_row_carries_the_seven_counts_even_without_a_kill` | green |

This round adds no production line, so there is no per-line neuter row to add. The one new line set is the planted
test, and its red-on-defect evidence is the "new test alone" column.

**Validation at this head** (exit codes captured directly):

```
env | grep -c '^AILIBI_'                                  0
pytest <the card's eight files> -n 6 --dist loadfile       407 passed (405 before, plus the two new cases)
runtime_fingerprint == capture source_sha256              exit 0
AST comparison, strings kept, base copy from 2275bdba     exit 0; planted copy exit 1
git diff 2275bdba -- training/rewards.py | ... | grep -vcE '^[+-]\s*#'   0
git diff --stat 2275bdba -- training/ | tail -1           2 files changed, 19 insertions(+), 1 deletion(-)
git diff --stat 2275bdba -- replays training/artifacts training/reports agents/tactical/learned tests/training api frontend
                                                          (prints nothing)
uv run python scripts/verify_ml_evidence.py               checks: 63 | OK 51 | FAIL 0 | ABSENT 7 | INFO 5; exit 0
uv run pytest -m campaign -q -n auto                      337 passed
uv run pytest tests/scripts/test_build_demo_bundle.py -q  31 passed
verify_samples.sh: samples/9p2i 50, samples/4p1i 50, ml_corpus/9p2i 150, ml_corpus/4p1i 50,
                   candidates/stage-b-r1/9p2i 50, each "All N samples verified clean."
build_sample_report.py --sample-dir <each of the five sets> --check   "... is consistent with its replays." x5
publish_process_scorecard.py --check, publish_gameplay_census.py --check   "... consistent with the committed recordings."
ruff check, ruff format --check, mypy on the test file    clean
```

The capture command and the ten-arm frozen-head comparison were not re-run. No file under `runtime_fingerprint`
moved, which the fingerprint check proves, so both would reproduce the rows already committed and quoted. The task-doc
validator, the doc-facts check, the bundle diff and the full gate are recorded below for the head that carries this
subsection.

**Deviations, round 1.**
- **The summaries** box stays open. It waits on the orchestrator's pick between the two readings under Deviations
  above, and no finding of this round touches it. Checking it here would make that pick.
- The Outcome sentence is corrected by the Review correction above, not edited, because the Outcome is the card's
  contract.
- One `git grep` for the old sentence first ran over the whole tree without a path filter. It printed part of one
  committed audit JSONL line that holds transcript text into this session's tool output. Nothing was written,
  committed or quoted from it, and the later searches were limited to `*.md` and `*.py`.

**Task docs, the bundle and the full gate.** The following ran at `52bb8f0c`:
- `scripts/validate_task_docs.py` exited 0 ("390 historical phase tasks and 390 prompts; 101 work cards").
- `scripts/check_doc_facts.py` exited 0.
- The demo bundle was built in this one worktree at `83806ab0` (the base, `main`) and at `52bb8f0c`
  (`scripts/build_demo_bundle.py --out <scratch>`). `diff -r` prints nothing over 109 files, so nothing ships.

`bash scripts/check.sh` runs once at the head that carries this paragraph. Its exit code is recorded in the next
commit.

**The full gate, round 1.** `bash scripts/check.sh > <scratch>/check.log 2>&1` ran once in this clean worktree at
`6fa72bac`, with `main` still at `83806ab0`. The background runner captured its exit code directly: 0. The results
were as follows:
- Ruff passed, with 554 files already formatted.
- Import-linter kept all four contracts, with 0 broken.
- Task docs validation passed, and all 390 prompts were in sync.
- Strict mypy found no issues in 525 source files.
- Pytest gave 10,335 passed, 20 skipped and 3 xfailed in 446.47 s. That is the 10,333 before this round plus the two
  new cases.
- The frontend passed 26 test files and 695 tests, and its build completed.

This commit changes only this card.

### Review corrections, round 2 (2026-10-06)

Independent verification of `4a6d4880` found one blocking problem, in a documented claim. This round changes five
files:
- `experiments/tactical_gameplay.py`: the `whereabouts_coverage` docstring only, with no code line changed;
- `tests/experiments/test_tactical_gameplay.py`: five new tests, seven cases;
- `audits/tactical-gameplay/README.md`: the coverage bullet, and the capture's stamp and wall time;
- `audits/tactical-gameplay/stage-b-idle-policy-development.json`: the capture, retaken by the harness;
- `docs/artifacts.md`: the `audits/` row.

This card also changes. `main` is still at `83806ab0`, so there was no merge.

**The finding: the cell was called an upper bound on the whereabouts any player held.** The README bullet said the
cell "counts positions, not what anyone noticed, remembered or said, so it is an upper bound on the whereabouts any
player held". The docstring said it "bounds from above the whereabouts any agent held". The code does not deliver
that. `engine.visibility.compute_visibility_for_player`, which `observation/service.py` turns into packets, gives an
impostor the adjacent rooms at base sight (`_resolve_observer_visibility_mode`). It also gives sight to an observer
inside a vent, because it never reads the observer's `in_vent`. So an impostor can see a player the cell leaves
uncovered. A crewmate's packet also carries the departures it watched (`_moved_players_for_agent`): a player that
left the crewmate's room, and the room it went to. And the cell reads no memory and no speech.

What the code does deliver is one bound. On the canonical map a crewmate sees only its own room, whatever the
sabotage: at base sight `_resolve_observer_visibility_mode` gives it `same_room_only`, `lights` gives everyone
`same_room_only`, and `reactor` leaves the base mode. Only an impostor can enter a vent (`engine.rules.resolve_vent`).
So every player a crewmate sees in the state a tick leaves stands in that crewmate's room beside a living crewmate
outside a vent, and the cell counts it covered. The README bullet now reads:

> It counts positions, not what anyone noticed, remembered or said. It bounds one thing: what crewmates see as the
> tick ends. On this map a crewmate sees only its own room, whatever the sabotage, so every player a crewmate sees
> in the state the tick leaves is covered, and an uncovered subject is one no crewmate sees then. It does not bound
> what impostors see. An impostor also sees the rooms next to its own unless the lights are sabotaged, and it still
> sees from inside a vent, so it can see a player the cell leaves uncovered. Nor does it bound what anyone holds. A
> player keeps what it saw on earlier ticks and hears what others say, and a crewmate that sees a player leave its
> room is told which room that player went to, even when the player stands there alone.

The docstring says the same in the module's terms: the cell bounds the players a crewmate sees in the state, and
nothing an impostor sees or a player holds from earlier ticks, from a departure it watched or from speech.

**Review correction for Outcome item 2.** Its sentence "The cell counts positions, not memories or speech: it is an
upper bound on what any agent held" is read as follows. The cell counts positions, not memories or speech. It bounds
only what crewmates see in the state the tick leaves, and nothing an impostor sees or any player holds. The Outcome
stays as the contract was written, and this correction governs how that sentence is read.

**Review correction for the Limitations line.** Validation's "Limitations to state" carries the same claim: "it is
an upper bound on held whereabouts". It is corrected the same way, and it stays as written because it is the
contract. The matching line under Results, "Limitations", is Results text, so it is corrected in place and marked.

**The tests.** Five new tests, seven cases, in `tests/experiments/test_tactical_gameplay.py`:
- `test_every_player_a_crewmate_sees_is_covered`. A Hypothesis property under `settings(deadline=None)` over the
  existing seeded canonical-map states (random rooms, `alive`, `in_vent` and roles), with no sabotage or with
  `lights` or `reactor` active. For every living crewmate outside a vent, every player
  `compute_visibility_for_player` lists is covered by `lab.whereabouts_coverage`. The cell returns counts, so the
  test reads one player at a time: a player is covered when removing it lowers the covered count.
- `test_the_per_player_read_counts_exactly_the_covered_players`. The same generator: summed over all players, that
  one-player read equals the cell's covered count, so the instrument is exact.
- `test_a_cell_missing_a_player_a_crewmate_sees_fails_the_bound`. Planted: a cell that needs two companions fails
  the property.
- `test_crewmate_sight_beyond_its_own_room_breaks_the_bound`. Planted source change:
  `engine.visibility._resolve_observer_visibility_mode` is patched so that a crewmate keeps the map's adjacent
  sight, and the property fails. An engine change to crewmate sight therefore cannot leave the README's bound silently
  stale.
- `test_the_cell_does_not_bound_what_an_impostor_sees`, with `next-door` (an impostor in `WEST_HALL`, a lone crewmate
  in `ADMIN`) and `inside-a-vent` (the impostor in `ADMIN`'s vent). In both the cell returns (3, 0), no crewmate sees
  anyone, and the impostor sees the crewmate.
- `test_the_cell_does_not_bound_a_departure_a_crewmate_watched`. One `advance_tick` moves a player from a crewmate's
  room to `WEST_HALL`. The cell returns (3, 0), and the crewmate's packet from `ObservationService.build_packet` lists
  `MovedPlayerView(id="p-2", from_room="ADMIN", to_room="WEST_HALL")`.

All seven cases were green on the shipped code, and both planted cases raise. The eight Validation files ran 414
passed (407 before this round, plus the seven).

**How often each side of the bound occurs.** This is count-only, from the capture's 800 games re-run at `34205618`
through `run_candidate`. Every arm's subjects and covered counts equal the capture's. "Seen by a crewmate" and "seen
by an impostor" use `compute_visibility_for_player` in the state the tick leaves. "A crewmate saw it leave" counts an
uncovered subject that moved this tick out of a room where a living crewmate stands when the tick ends: by the
packet's departure rule, that crewmate is told where it went.

| Roster | Arm | Uncovered at kill ticks | seen by a crewmate | seen by an impostor | a crewmate saw it leave | Uncovered at play ticks | seen by a crewmate | seen by an impostor | a crewmate saw it leave |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4p1i | `stage_b_full` | 390 | 0 | 36 | 4 | 3,476 | 0 | 741 | 228 |
| 4p1i | `stage_b_full_kill_cooldown_6` | 256 | 0 | 28 | 4 | 3,342 | 0 | 769 | 129 |
| 4p1i | `stage_b_full_kill_cooldown_6_patrol` | 213 | 0 | 28 | 8 | 3,238 | 0 | 809 | 276 |
| 4p1i | `stage_b_full_kill_cooldown_6_accompany` | 215 | 0 | 28 | 8 | 3,238 | 0 | 813 | 288 |
| 9p2i | `stage_b_full` | 1,383 | 0 | 399 | 100 | 8,271 | 0 | 3,140 | 1,019 |
| 9p2i | `stage_b_full_kill_cooldown_6` | 1,063 | 0 | 364 | 80 | 10,040 | 0 | 4,140 | 1,138 |
| 9p2i | `stage_b_full_kill_cooldown_6_patrol` | 1,271 | 0 | 464 | 156 | 11,152 | 0 | 4,504 | 1,558 |
| 9p2i | `stage_b_full_kill_cooldown_6_accompany` | 1,216 | 0 | 442 | 134 | 11,007 | 0 | 4,517 | 1,590 |

The hub-wait figures equal the verifier's (364 of 1,063 and 4,140 of 10,040 on 9p2i; 28 of 256 and 769 of 3,342 on
4p1i). These are lab counts of fake games, not cells of the committed capture, so the README states the mechanism
without them, as round 1 did. The probe takes about 100 s and prints counts only:

```
PYTHONPATH=. uv run python - stage_b_full stage_b_full_kill_cooldown_6 stage_b_full_kill_cooldown_6_patrol \
  stage_b_full_kill_cooldown_6_accompany <<'EOF'
import sys, tempfile
from collections import Counter
from pathlib import Path
import experiments.tactical_gameplay as lab
from engine.events import KilledEvent, MovedEvent
from engine.visibility import compute_visibility_for_player
from engine.world import load_canonical_map

game_map, fold, tally, key = load_canonical_map(), lab.fold_whereabouts, Counter(), []


def probe(step, counts):
    fold(step, counts)
    players = step.state.players
    standing = Counter(p.room for p in players.values() if p.alive and not p.in_vent)
    uncovered = [i for i, p in players.items() if p.alive and (p.in_vent or standing[p.room] < 2)]
    seen = {"CREWMATE": set(), "IMPOSTOR": set()}
    for i, p in players.items():
        if p.alive:
            seen[p.role].update(compute_visibility_for_player(
                observer_id=i, world_state=step.state, game_map=game_map).visible_player_ids)
    crew_rooms = {p.room for p in players.values() if p.alive and p.role == "CREWMATE"}
    left = {e.actor for e in step.events
            if isinstance(e, MovedEvent) and e.from_room != e.to_room and e.from_room in crew_rooms}
    kill = any(isinstance(e, KilledEvent) for e in step.events)
    for scope in ("play", "kill") if kill else ("play",):
        tally[key[-1], scope, "uncovered"] += len(uncovered)
        tally[key[-1], scope, "seen by a crewmate"] += sum(u in seen["CREWMATE"] for u in uncovered)
        tally[key[-1], scope, "seen by an impostor"] += sum(u in seen["IMPOSTOR"] for u in uncovered)
        tally[key[-1], scope, "a crewmate saw it leave"] += sum(u in left for u in uncovered)


lab.fold_whereabouts = probe
configs = lab.candidate_configs()
with tempfile.TemporaryDirectory() as tmp:
    for arm in sys.argv[1:]:
        for name in ("4p1i", "9p2i"):
            roster = lab.Roster.model_validate_json(Path(f"replays/samples/{name}/roster.json").read_bytes())
            key.append(f"{name} {arm}")
            for seed in lab.SPLIT_SEEDS["development_wide"]:
                lab.run_candidate(seed=seed, roster=roster, config=configs[arm],
                                  replay_path=Path(tmp) / f"{arm}-{name}-{seed}.jsonl")
for (row, scope, column), value in sorted(tally.items()):
    print(row, scope, column, value)
EOF
```

**The capture is retaken, because the docstring is in the hashed harness.** `runtime_fingerprint` hashes
`experiments/tactical_gameplay.py`'s own bytes. The capture must equal the fingerprint at the PR head (acceptance
**The capture is committed, reproducible and read**), so a docstring edit moves the fingerprint and requires a new
capture. The old file was removed. The Validation command then wrote the new one through the harness at the clean
committed head `342056181b9551de457a18c4d56917f3e676c175`. It took 109.81 s of wall (`/usr/bin/time -p`). All 800
games are `completed`, and every `error` is null.

A count-only comparison checked the new capture against round 1's, key by key. It skipped only the stamp keys
(`source_sha256`, `git_head`, `measured_utc`, `machine`, `world_copy_control`):
- top-level keys equal;
- 800 rows, 69,884 leaf fields compared, 0 differing;
- the stamp keys that moved: `git_head`, `measured_utc`, `source_sha256` and `world_copy_control` (the copy timings);
- exit 0.

Perturbed: in a scratch copy of the new capture, one `whereabouts_covered_at_kill_ticks` (cooldown-6, 9p2i, the
fourth seed) was raised by 1. The comparison then printed "differing 1" and exited 1. The script stays in scratch.
It flattens every key outside the stamp set to leaves and compares them path by path.

The new stamps are as follows:
- `source_sha256` is `d901fcb0f2c67316a4f6bd77a331daf0c2a41e62d8d7dadbc417c9f295d2909e`, and the Validation
  fingerprint command exits 0 at this head;
- `git_head` is `342056181b9551de457a18c4d56917f3e676c175`;
- the README's inputs paragraph carries both, and its wall time is now 110 seconds.

The README's compact check, run on the new JSON, reprints all 20 rows: "rows printed 20 rows in the tables 20;
identical, in order: True". The totals are unchanged: 14,190 calls, 52,639,727 input and 815,925 output tokens, $0,
and at most 71 ticks, 52 calls and 220,212 input tokens in one game.

Record impact says the capture is "written once and never regenerated in place". This round reads that as never
edited by hand, and never re-taken unless the fingerprint moved. The capture's acceptance already re-takes it when
the fingerprint moves. Every row is shown unchanged, so no reading of the capture changes.

**The registry.** With the new capture and README staged and the row unchanged,
`test_every_counted_registry_row_matches_the_index` failed: "audits/: docs/artifacts.md promises 31,431,207 tracked
bytes, the tracked files contain 31,431,870 bytes". With the row at 31,431,870 tracked bytes / 334 files, it passes.
`git ls-files -z audits | xargs -0 cat | wc -c` prints 31431870, and `git ls-files audits | wc -l` prints 334.

**The grep for the old wording.** Two searches ran at this head. The first was `git grep -n -i -e "upper bound"
-e "bounds from above"` over `audits/tactical-gameplay/README.md`, `experiments`, `tests/experiments`, `training`,
`docs`, this card, the decision memo and `tasks/diagnosis-2026-10-02`. The second searched `*.md` and `*.py` for
"bounds from above", "upper bound on held", "upper bound on what any agent", "any player held" and "any agent held".
Before this round they found the README bullet, the docstring and three lines of this card: Outcome item 2, the
Validation limitation and the Results limitation. Now the claim is left only in the two contract lines this
correction governs. Every other hit is a different claim:
- The README's "best arm's uncovered remainder" sentence, and the card lines that predeclare it, say that the share
  the best arm leaves uncovered bounds what any idle policy could still add in this cell. No share exceeds 1, so
  that holds, and it is left as written.
- The other hits are unrelated bounds in older lab reports and training code.

The decision memo's 8.2 item 4 and the section 7 paragraph call the cell role-blind and the measured candidate,
which stays true. The diagnosis's `ml-tactical.md` proposes a different, crewmate-observer cell, which this card
did not build.

**The pins that read source bytes.** Nothing under `training/` changed this round (`git diff --stat 4a6d4880 --
training/` prints nothing), so the round-1 digests stand. Offline `verify_ml_evidence` reads checks 63, OK 51, FAIL 0,
ABSENT 7, INFO 5 (exit 0, never `--complete`). The AST comparison against `2275bdba` still exits 0.

**The mutation pass, bounded to the span the finding names.** That span is the code of `whereabouts_coverage`; the
only production change this round is its docstring. There were nine mutants, of the listed classes only. Each ran
alone against `tests/experiments/test_tactical_gameplay.py` (`-x -n 4`), and the new tests also ran alone (`-k`
over the seven cases). The file was restored from a byte copy after each run, with its sha256 (`4a4c349ef1b7...`)
re-checked. All nine were killed, and none survived.

| id | class | mutant | result | first red test | new tests alone |
| --- | --- | --- | --- | --- | --- |
| R1 | F filter | drop `alive` from the standing filter | killed | `test_a_tick_with_two_kills_counts_its_players_once` | green |
| R2 | F filter | drop `in_vent` from the standing filter | killed | `test_a_vented_player_covers_nothing_and_is_not_covered` | red (`inside-a-vent`) |
| R3 | F filter | drop the whole standing filter | killed | `test_a_tick_with_two_kills_counts_its_players_once` | red (`inside-a-vent`) |
| R4 | F filter | drop the company filter on covered | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red (the source-change case) |
| R5 | N comparison | company test inverted (`count <= 1`) | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red (the property) |
| R6 | N comparison | `in_vent` test inverted | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red (the property) |
| R7 | C constant | standing room read as `"ADMIN"` | killed | `test_two_players_in_one_room_cover_each_other_and_a_lone_player_is_uncovered` | red (the source-change case) |
| R8 | S swap | subjects over the standing players only | killed | `test_a_vented_player_covers_nothing_and_is_not_covered` | red (`inside-a-vent`) |
| R9 | S swap | subjects over every player, the dead included | killed | `test_a_tick_with_two_kills_counts_its_players_once` | green |

The new tests alone came back green on R1 and R9. Those mutants change what a dead player counts for, which the
bound does not speak to, and an earlier test kills both. On R4 and R7 the property passes, because a cell that
over-counts cannot break an upper bound. The planted source-change case then goes red instead: it can no longer
make the property fail. An earlier exact case kills both, as the table names. This round adds no production code line,
so there is no per-line neuter row to add. The docstring's claims are enforced by the seven cases above.

**Validation at this head** (exit codes captured directly; `34205618` plus the capture, the README stamp, the
`audits/` row and this card):

```
env | grep -c '^AILIBI_'                                  0
pytest <the card's eight files> -n 6 --dist loadfile       414 passed (407 before, plus the seven new cases)
the capture, retaken at 34205618 (Validation command)      exit 0, 109.81 s, 800 games, all completed
runtime_fingerprint == capture source_sha256              exit 0
capture comparison against round 1, count-only            800 rows, 69,884 fields, 0 differing; exit 0
  perturbed: one covered count raised by 1                 differing 1; exit 1
README compact check                                      20 rows printed, identical, in order
AST comparison, strings kept, base copy from 2275bdba     exit 0
git diff 2275bdba -- training/rewards.py | ... | grep -vcE '^[+-]\s*#'   0
git diff --stat 2275bdba -- training/ | tail -1           2 files changed, 19 insertions(+), 1 deletion(-)
git diff --stat 2275bdba -- replays training/artifacts training/reports agents/tactical/learned tests/training api frontend
                                                          (prints nothing)
uv run python scripts/verify_ml_evidence.py               checks: 63 | OK 51 | FAIL 0 | ABSENT 7 | INFO 5; exit 0
uv run pytest -m campaign -q -n auto                      337 passed
uv run pytest tests/scripts/test_build_demo_bundle.py -q  31 passed
verify_samples.sh: samples/9p2i 50, samples/4p1i 50, ml_corpus/9p2i 150, ml_corpus/4p1i 50,
                   candidates/stage-b-r1/9p2i 50, each "All N samples verified clean."
build_sample_report.py --sample-dir <each of the five sets> --check   "... is consistent with its replays." x5
publish_process_scorecard.py --check, publish_gameplay_census.py --check   "... consistent with the committed recordings."
ruff check, ruff format --check, mypy on the two changed Python files   clean
```

The task-doc validator, the doc-facts check, the bundle diff and the full gate are recorded below for the head that
carries this subsection.

**Decisions, round 2.**
- The bound is stated at exactly the strength the code holds, as the crewmates' sight in the state the tick
  leaves. A stronger bound that names an observer (a crewmate first-hand) would read a role, which the cell was
  defined not to do (ruling 2), so it is stated as a property of the engine's sight, not as a second cell.
- The departure limit goes beyond what the finding named. Reading `observation/service.py` for the finding showed
  that a crewmate is told the room a watched player walked into, on the same tick. That limit is as real as the two
  the finding named, so it is stated and pinned too.
- The capture is retaken rather than left with a stale fingerprint, for the reason above.

**Deviations, round 2.**
- **The summaries** box stays open. It waits on the orchestrator's pick between the two readings under Deviations
  above, as in round 1. This round's dispatch asked that no box be left unchecked. Checking this one would make the
  pick, so it stays open, and the orchestrator is told so.
- The card's **Status** line reads `ready`. It belongs to the orchestrator on `main` (Constraints), so it is not
  changed here.

**Task docs, the bundle and the full gate, round 2.** The following ran at `87f256f6`:
- `scripts/validate_task_docs.py` exited 0 ("390 historical phase tasks and 390 prompts; 101 work cards").
- `scripts/check_doc_facts.py` exited 0.
- The demo bundle was built in this one worktree at `83806ab0` (the base, `main`) and at `87f256f6`
  (`scripts/build_demo_bundle.py --out <scratch>`). `diff -r` prints nothing over 109 files, so nothing ships.

`bash scripts/check.sh` runs once at the head that carries this paragraph. Its exit code is recorded in the next
commit.

**The full gate, round 2.** `bash scripts/check.sh > <scratch>/check.log 2>&1` ran once in this clean worktree at
`833bc71b`, with `main` still at `83806ab0`. The background runner captured its exit code directly: 0. The results
were as follows:
- Ruff passed, with 554 files already formatted.
- Import-linter kept all four contracts, with 0 broken.
- Task docs validation passed, and all 390 prompts were in sync.
- Strict mypy found no issues in 525 source files.
- Pytest gave 10,342 passed, 20 skipped and 3 xfailed in 828.09 s. That is the 10,335 of round 1 plus the seven
  new cases.
- The frontend passed 26 test files and 695 tests, and its build completed.

This commit changes only this card.
