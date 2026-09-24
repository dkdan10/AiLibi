# B0: the physical vent witness rule (R7)

**Status:** ready

## Outcome

A vent exit stops being "seen" from a room the impostor was never visible in. A new engine arm,
`vent_witness_rule: Literal["both_rooms", "physical"] = "both_rooms"` on
`RecordedExperimentConfig`, decides who witnesses a vent action. Under `"physical"`, an exit whose
destination room differs from the room left has `source_witnesses = ()` and
`witnesses = destination_witnesses`: only the living, non-vented occupants of the room surfaced
into see it. Entries and exits in place are already one-room and are identical under both values.
Under `"both_rooms"`, the default, every event is byte-identical to today's.

The rule reaches every reader that re-derives or checks a witness set, not only the engine: the
spine's engine-arguments helper (one line, so every re-simulation site takes it), temporal delivery
(`observation/temporal.py`, switched to the event's own lists), both entitlement oracles, the
factory leak scan and `scripts/scan_recording_packets.py`. A reader that forgets the arm fails a
test instead of passing every state-hash check with wrong witness sets.

The arm is default-OFF. No committed recording, derived view, fixture, gate or doc fact moves. It
is recorded ON only in the candidate round (`replays/candidates/stage-b-r1/9p2i/`, written by the
record card). It changes which crewmate perceives a vent exit; it tells no agent the rule, adds no
prompt text, and nudges no agent toward any answer.

## Evidence

Every `path:line` in this card is at `e886b663`. The implementer re-anchors each one by the
named symbol at dispatch. The design is the decision memo's section 2.2 and its card-6 dispatch
brief (section 3.4), in `stage-b-2026-09-24/decision-memo.md`. The investigation is
`vent_witness_and_exit.md`, sections 1, 2, 2.1 and 5, in the same directory.

**The owner's rulings of 2026-09-24, verbatim, that this card relies on.**
- Ruling 1: "We should implement stage B"
- Ruling 2, which R7 pairs with: "B1. Add vent logic so that imposters try to avoid being caught
  coming out of a vent."
- Items 6 to 10 and 13: "What do you think is best?" This delegated R7 to the orchestrator.
- Ruling 12: "Hold off on ML as D suggests until gameplay is finished."
- The record paragraph: "Let's not re-record all 300 seeds each time. When it's time to record,
  record the smaller group of 50 seeds, assess if the implementations have been effective and
  resulted in desired results. Also it is understood that updating the vent and body reset logic
  will probably have a substantial effect on previous limits and statistics around the baseline
  voting results, that is okay."

**The orchestrator's rulings, made under the owner's delegation of 2026-09-24.**
- R7: "The vent witness rule becomes PHYSICAL, as a new engine arm." In the dispatch brief's words,
  "a vent action is witnessed by the living non-vented occupants of the room where it physically
  happens, the entry by the room entered from and the exit by the room surfaced into".
- The memo's resolution of R7 is binding: "The witness-entitlement oracle and the leak scan must
  take the rule", because the oracle hard-fails a correctly threaded physical recording. That
  work "is required, not optional."
- Decision 0.3 item 2 (a new field is omitted from the payload at its default).
- Decision 0.3 item 6 (a recorded value's meaning is frozen).
- Decision 0.3 item 9 (`WAVE_ARMS_PENDING`; each arm card deletes its own entry).

**The rule today.**
- `resolve_vent` (`engine/rules.py:111-188`) treats an exit as leaving the current vent's room
  (`:125-138`) and surfacing in the connected vent's room. An entry's source and destination are
  the actor's own room (`:139-144`).
- `source_witnesses` and `destination_witnesses` are the living, non-vented occupants of each room
  (`_witnesses_in_room`, `:29-44`), and `witnesses` is their union (`:146-156`). So a crewmate in
  the room left "sees" an exit made from inside a vent there, where the impostor was invisible.
- The events carry all three lists (`engine/events.py:82-113`).
- `advance_tick` (`engine/tick.py:594`) threads only `redistribution_policy`, validated at
  `:615-616`, through `_apply_action` (`:560`). `_apply_vent` (`:442`) calls `resolve_vent` with no
  rule. The precedent alias is `RedistributionPolicy` (`:58`).

**What the rule costs today.** Count-only figures from `vent_witness_and_exit.md` section 1.5,
reproduced by `census_and_record.md` section 1. They are quoted, not re-derived here. Re-measure
them at dispatch with `uv run python scripts/publish_gameplay_census.py --check` once the census
card has merged (cells C3, C4, C5 and C15 of `census_and_record.md` section 4.2).

| cell | s9 | 9p2i | pooled |
|---|---|---|---|
| vent exits | 85 | 435 | 512 |
| exits seen by crew, today's rule | 62 | 271 | 313 |
| seen in the exit room (what `physical` keeps) | 53 | 226 | 251 |
| seen only from the room left (what `physical` removes) | 9 | 45 | 62 |
| vent convictions | 70 | 281 | 326 |
| convictions resting only on room-left witnesses | 8 | 37 | 50 |

Entries are one-room on 587 of 587 pooled entries (`census_and_record.md` section 1), so the rule
changes exits only. The decision memo's projection is that R7 alone removes the 9 s9 room-left
exits and about 8 of the 70 s9 vent convictions, by construction. The convictions figure is an
upper bound, because the game diverges after the first changed exit.

**Witness sets are invisible to verification.**
- The state hash covers `WorldState` only (`orchestrator/replay.py:2043-2045`). Tick rows record
  actions and a hash, not events.
- A reader that forgets the arm therefore reproduces every hash while serving the old witness
  sets.
- The investigator's scratch prototype measured this on 8 physical 9p2i games: state hashes equal
  on 221 of 221 re-simulated ticks, and exit witness lists different on 4 of 28 exits
  (`vent_witness_and_exit.md` section 6.2). `bash scripts/verify_samples.sh` cannot see the rule.

**The re-simulation sites.**
- `git grep -n "advance_tick(" -- "*.py"` finds 13 production call lines at `e886b663` (182 more
  under `tests/`).
- Three of them thread the recorded config today: the live tick (`orchestrator/game.py:2566`), the
  loader (`api/replay_loader.py:1633`) and the walk (`eval/replay_walk.py:636`).
- The lab calls `_apply_action` directly with the recorded `redistribution_policy`
  (`experiments/tactical_gameplay.py:413`).
- The rest either read no recording (training rollouts, the determinism and leak tests, type
  generation) or refuse experiment recordings. The refusals are the off-menu instrument
  (`eval/off_menu.py:359-361`), the anchor study (`training/anchor_study.py:441-445`), the
  surrogate table (`training/surrogate/dataset.py:1026`) and the lab's identity check
  (`experiments/tactical_gameplay.py:194`).
- The rubric extractor (`audits/workflows/extract_gameplay_facts.py:2235`) is made to refuse by
  the readers card.
- The spine owns the helper and its call at each threading site. This card adds the rule to the
  helper's output.

**Independent re-derivations that must take the rule.**
- `observation/temporal.py:132-135` delivers a vent to any observer in
  `(event.source_room, event.destination_room)`. That contradicts the contract's "Engine event's
  actual witness set" (`docs/observation-contract.md:12`) as soon as the engine rule changes.
- `eval/witness_entitlement.py:93-110` asserts both lists by room.
- `eval/temporal_entitlement.py:131` accepts `room in {event.source_room, event.destination_room}`.
- The factory leak scan calls the first oracle with no rule (`eval/leak_scan.py:1006`) and the
  second through `assert_event_observations_are_entitled` (`:829`).
- `scripts/scan_recording_packets.py` reaches both oracles through `_reconstruct_factory_records`
  (`:78-87`).
- The legacy readers read the event's lists and follow the engine automatically:
  `observation/service.py:652-664` and `eval/leak_scan.py:853-862`.

**One temporal population exists.** The fifth-run archive,
`audits/deduction-candidate/run-2026-09-16/`, holds 100 recordings. All 100 stamp
`temporal_observation_version` 2, with a 12-key experiment config that has no witness-rule key.
This was measured count-only on 2026-09-24 with a scratch script over the first tick row of each
file; re-measure at dispatch. The switch in `observation/temporal.py` must therefore be
byte-identical under `both_rooms`.

## Acceptance

- [ ] **The engine arm, and the exit that proves it.** `resolve_vent` takes the rule as a keyword.
  `_apply_vent`, `_apply_action` and `advance_tick` take `vent_witness_rule: VentWitnessRule =
  "both_rooms"`; the alias sits beside `RedistributionPolicy`. Mechanism: the physical branch in
  `resolve_vent`. Proof, the investigator's test 2.1-1:
  - `test_vent_can_exit_through_connected_destination_vent` (`tests/engine/test_tick.py:932-987`)
    stays the `both_rooms` pin: p-2 in ADMIN and p-4 in REACTOR both witness the ADMIN_VENT to
    REACTOR_VENT exit.
  - Its new `physical` twin asserts `witnesses == ("p-4",)`, `source_witnesses == ()` and
    `destination_witnesses == ("p-4",)`.
  - So the crewmate in the room left does NOT witness under `physical` and DOES under
    `both_rooms`. An engine that ignores the keyword fails the twin; one that applies the physical
    branch by default fails the pin.
- [ ] **Entries equal under both rules** (2.1-2). Mechanism: the physical branch is gated on an exit
  whose destination room differs from the room left.
  - A crewmate in the entry room witnesses under both values.
  - A crewmate in a connected vent's room (REACTOR, while the actor enters ADMIN_VENT) witnesses
    under neither.
  - The two values produce equal events, following the pattern at
    `tests/engine/test_tick.py:505-537`.
  - Planted proof: a variant that also empties `source_witnesses` on entries fails the
    entry-room assertion.
- [ ] **An exit in place is one-room under both rules** (2.1-3). Mechanism: the same gate. Every
  occupant of that one room witnesses under `physical`. A planted variant that gates on "is an exit"
  alone empties the list and fails.
- [ ] **The default is today's bytes, and an unknown value raises** (2.1-4). `advance_tick` raises
  `ValueError` on an unknown rule before applying any action, as it does for redistribution at
  `engine/tick.py:615-616`. A Hypothesis property over random vent scenes (entries, in-place exits,
  cross-room exits, occupants in either room, vented and dead bystanders) asserts:
  - the default call equals the explicit `"both_rooms"` call;
  - `"physical"` equals `"both_rooms"` on entries and in-place exits;
  - on cross-room exits, `"physical"` keeps `destination_witnesses` unchanged and sets
    `source_witnesses` to `()` and `witnesses` to `destination_witnesses`.
  - Planted proof: flipping the default to `"physical"` fails the first clause.
- [ ] **What a crewmate perceives** (2.1-5). Legacy observations follow the event lists unchanged
  (`observation/service.py:652-664`). Temporal delivery switches from the two-room predicate to
  membership in the event's own `source_witnesses` or `destination_witnesses`, keeping the
  `can_watch` guard and the observer's event-local room as the reported room. The tests:
  - A room-left crewmate's legacy packet carries no `vent` action under `physical` and carries one
    under `both_rooms`. The temporal v2 batch behaves the same way.
  - A Hypothesis property asserts that the temporal batch built with the new predicate equals the
    batch from a reference copy of the old room predicate, kept in the test, on every `both_rooms`
    scene. This proves byte identity for the fifth-run archive's temporal recordings.
  - Planted proof: restoring the room predicate in `observation/temporal.py` fails the `physical`
    case.
- [ ] **Both oracles take the rule** (2.1-6). `assert_event_witnesses_match_source_state` and
  `assert_temporal_batch_entitled` gain a required keyword with no default, so a caller cannot
  forget it. By `git grep` at `e886b663` that is 6 call lines for the first oracle and 7 for the
  second, `eval/leak_scan.py` included; every caller passes the rule. Each oracle stays an
  independent re-derivation from ordered state: it does not import `engine.rules`, and it never
  derives its expectation from the lists it checks. The tests:
  - The poisoned-event pattern (`tests/eval/test_witness_entitlement.py:31-62`) runs under
    `physical`. An exit event whose `source_witnesses` still names the room-left occupant is
    rejected with "vent source witness entitlement". The same event is accepted under
    `both_rooms`, and the reverse pair holds too.
  - The temporal oracle gets the same pair.
  - The refuter's hard-fail is reproduced as a planted case: a correct physical exit checked under
    `both_rooms` (the unthreaded oracle) raises. This proves the threading is necessary.
- [ ] **The leak scan and the packet census pass the recorded rule.** `_reconstruct_factory_records`
  reads the rule from the recording's own config (`recorded_experiment_config`,
  `orchestrator/replay.py:741`). A missing config means `both_rooms`. The rule is handed to both
  oracles through one reader. The tests:
  - A fake physical set passes `scan_recording_set` with at least one vent view counted.
  - The same set scanned with the rule withheld from the oracles fails with the vent entitlement
    message.
  - `tests/scripts/test_scan_recording_packets.py` carries both cases, beside its ml_corpus cases.
- [ ] **The `leak-scan-factory` walk profile declares its layers.** Mechanism: the profile
  (`eval/leak_scan.py:951`) sets the spine's `threaded_layers` to the layers the scan reads, named
  in Results; the spine names this card as its owner. Proof: it reads the spine's fake full-config
  recording (a copy of a fake recording on today's arms, its tick rows and footer rewritten to
  carry every wave field at its ON value, `vent_witness_rule="physical"` included, with the pending
  set patched empty) with every hash verified, and it refuses a planted unknown field (a stand-in
  added to the config model and `FIELD_LAYER` in a layer the profile does not declare) by name
  before its first advance. Perturbed: the profile with its layer declaration removed refuses the
  full-config copy. `scan_recording_packets.py` on the round-1 candidate walks this profile.
- [ ] **The reader gate: a reader that forgets the arm fails** (2.1-7). The fixture is one
  fake-provider physical game (`HeadlessGame` with a declared `RecordedExperimentConfig`, no env)
  recorded into `tmp_path`. The test first asserts that the game holds at least one exit with a
  crewmate in the room left and none in the destination, so it cannot pass vacuously; the seed or
  scripted fixture is named in Results. For that crewmate, three readings agree and none holds a
  vent observation of that exit:
  - the live game's own agent memory;
  - `ReplayLoader` with memory collection (`api/replay_loader.py:1435-1456`);
  - `walk_replay`: the `TickAdvanced` events list no room-left witness, and the packet built from
    them has no vent row.

  Planted proof, parametrised over the three sites (live tick, loader, walk): replacing the helper's
  result at exactly one site with the `both_rooms` arguments makes the test fail. State hashes stay
  equal throughout.
- [ ] **The config line and the pending guard** (2.1-8). The spine's engine-arguments helper
  returns `vent_witness_rule` from a recorded config, and `both_rooms` for no config. This card
  deletes `vent_witness_rule` from `WAVE_ARMS_PENDING` and nothing else there; the spine's
  pending-refusal test reads the mapping's live contents, so this card does not edit
  `tests/orchestrator/test_experiment_arms.py`. The half of 2.1-8 that re-serializes every committed
  audit row's config is the spine's committed-bytes test, which this card re-runs unchanged. The
  tests:
  - A `physical` config round-trips through `RecordedExperimentConfig` and the spine's view mirror.
  - A config holding the rule at its default serializes without the key, under the spine's
    omit-at-default pattern.
  - A physical-only config has `has_tactical_changes` False, because this is an engine arm.
  - Planted proof: a helper without this card's line fails the reader gate above.
- [ ] **The census reads 0 by construction on a physical game.** One end-to-end test in this card's
  own reader-gate test file walks the fake physical game through the census card's `--set-dir`
  fold. The census cell "exits seen only from the room left" (C5 in `census_and_record.md`, under
  whatever name the census card ships) reads 0, and its conformance guard passes. Planted proof: the
  same recording walked with the helper's rule withheld at the census walk raises the cell's
  conformance breach. C15 (convictions) is not exercised, because fake meetings eject nobody.
- [ ] **The OFF path is byte-identical** (2.1-9). Mechanism: the default value and the omitted key;
  no committed recording carries the key (0 of 300 in the four sets, `vent_witness_and_exit.md`
  section 2). Evidence, run at the branch head:
  - `bash scripts/verify_samples.sh <set>` once per set directory, for all four;
  - the four `scripts/build_sample_report.py --sample-dir <set> --check` runs;
  - the prompt-byte golden on s9 and s4, whose re-rendered prompts carry the vent sightings;
  - `scripts/publish_process_scorecard.py --check`;
  - `scripts/publish_gameplay_census.py --check`, which re-derives all 512 exit witness lists, so
    C5 still reads 62 pooled and 9 on s9;
  - the ml_corpus packet scans;
  - `uv run pytest -m campaign`.

  Planted proof: an engine patch that applies the physical branch under the default turns the
  census `--check` and the `both_rooms` pin red. Results names both failures.
- [ ] **The observation contract states the rule.** `docs/observation-contract.md`'s witnessed
  kill/vent row, or one sentence under the table, says four things:
  - a vent exit is witnessed from both rooms under the default;
  - it is witnessed only from the room surfaced into under the physical arm;
  - entries are one-room under both;
  - a recording without the key reads as the default.

  The sentence names no card, ruling or audit ID. Mechanism: a test in
  `tests/engine/test_vent_witness_rule.py` reads the contract and asserts that it names every value
  of `VentWitnessRule` (via `typing.get_args`) and the default. Planted proof: a third alias value,
  or the sentence deleted, fails it. `DESIGN.md:351` is historical and is not edited.

## Constraints

**The partial-record principle binds this card.**
- Only `replays/samples/9p2i`'s seeds 0-49 are ever re-recorded, and only into a candidate
  directory (`replays/candidates/stage-b-r1/9p2i/`) by the record card, never by this one.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted at its default.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying
  byte-identically.
- No registry prompt bump: this card changes no template and no prompt stamp.
- Role-correctness is reported and never a gate.
- Nothing pushes an agent toward the correct answer: the rule decides who perceives an exit and
  nothing else.
- The meeting layer labels and never rewrites, and this card does not touch it.

**Wave, order and ownership.**
- Wave 2, card 6 of the memo's section 3.1.
- Starts after the spine (`tasks/work/stage-b-arm-spine.md`) has merged, which itself follows the
  documentation card (`tasks/work/docs-truth-typed-trigger.md`).
- Runs in parallel with the readers card and the record-plumbing card.
- Merges in wave 2 after the census card (`tasks/work/gameplay-census.md`), whose end-to-end cell
  it calls.
- Merges before `tasks/work/vent-look-and-wait.md`, which starts only once this card has merged.
- The dated 2026-09-24 addendum to `tasks/direction-2026-09-19-process-over-outcome.md` (decision
  memo section 6) lands as a `docs:` commit before wave 1. This card cites it in its PR.

Shared files, one writer at a time, per the memo's section 3.2:
- `orchestrator/experiment_config.py` is the spine's. This card holds the declared exception: it
  adds `vent_witness_rule` to the engine-arguments helper and deletes its own name from
  `WAVE_ARMS_PENDING`, nothing else. The pending removals merge in the order B0, B1, B4, B6, and
  this card is first.
- `engine/tick.py`: the documentation card (its comment near `:399`), then this card.
- `docs/observation-contract.md`: this card, then the reset card.
- Every other file in Expected scope is this card's alone.
- It does not write `experiments/tactical_gameplay.py` (spine, then B1),
  `tests/_helpers/committed.py`, `api/`, `frontend/`, `docs/architecture.md` or `docs/glossary.md`.
- A test here that walks a committed set calls an existing `tests/_helpers/committed.py` entry
  point without editing that file. If none fits, the check stays a command in Validation.

**Decisions this card makes, recorded in Results.**
- `advance_tick` keeps a default for the rule, like `redistribution_policy`, so the 182 test call
  lines do not move. The guard against a forgotten reader is the single helper plus the reader
  gate, not a required keyword.
- The two oracles take the rule as a required keyword, because an oracle that defaults would hide
  exactly the omission the refuter found.
- The keyword is threaded into `_apply_action` as well as `advance_tick`, so the lab's direct call
  (`experiments/tactical_gameplay.py:413`) takes the helper's output with no edit to that file. If
  the spine did not route that call through the helper, stop and ask.

**What stays out.**
- No agent learns the rule. Nothing under `agents/` changes, and `.importlinter` is unchanged.
- No new env lever or `AILIBI_*` switch; the field is set only by a declared config.
- No viewer, featured-list or public-results change: the tour waits, per ruling 11, "Tour fix can
  be deferred to after gameplay is finished".
- No ML training, refit or corpus change (ruling 12).
- No scorecard cell (R13).
- No held-out band.
- Fake provider and scripted clients only: no live call, no `.env`.

**Delivery.**
- Branch `work/vent-witness-physical`, one pull request into `main`, merged or fast-forwarded,
  never squashed.
- Never amend a pushed commit. Bring `main` in by merging it, never by rebasing.
- Each commit body carries `Card: tasks/work/vent-witness-physical.md`, immediately followed by
  the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card).
- The PR body fills `.github/pull_request_template.md`'s sections Summary, Definition of done,
  Decisions and Questions, and ends with the Claude Code attribution line.
- Agents post no PR comments.
- Every merge is the owner's.
- `tasks/README.md` and this card's Status line are the orchestrator's. The worker fills Results
  and leaves Status alone, because `scripts/validate_task_docs.py` derives the inventory sentence
  from every Status.

**Stop and ask** if any of these happens:
- a committed byte, derived view or census cell moves under the default;
- the prompt-byte golden needs an edit to stay green;
- a reader outside Expected scope needs the rule to stay correct;
- the spine's helper cannot carry the rule to a threading site.

## Expected scope

- Engine:
  - `engine/rules.py`: `resolve_vent` and a one-line intent comment on the rule;
  - `engine/tick.py`: the `VentWitnessRule` alias, validation in `advance_tick`, and the keyword
    through `_apply_action` and `_apply_vent`.
- Configuration: `orchestrator/experiment_config.py`, the helper line and the pending line only.
- Observation: `observation/temporal.py`, the vent branch near `:132-135`.
- Oracles and scans:
  - `eval/witness_entitlement.py` and `eval/temporal_entitlement.py`: the required rule keyword;
  - `eval/leak_scan.py`: `_reconstruct_factory_records` reads the rule and passes it to both
    oracles, and the `leak-scan-factory` profile declares its layers;
  - `scripts/scan_recording_packets.py`: edited only if the rule cannot reach the oracles through
    `_reconstruct_factory_records`.
- Docs: `docs/observation-contract.md`.
- Tests:
  - `tests/engine/test_tick.py` (the twin);
  - a new `tests/engine/test_vent_witness_rule.py` (entries, in place, the unknown value, the
    Hypothesis property);
  - `tests/eval/test_witness_entitlement.py` and `tests/observation/test_temporal_v2.py`
    (required-keyword call sites, poisoned pairs, the temporal property);
  - `tests/scripts/test_scan_recording_packets.py` (the physical fake set);
  - a new `tests/eval/test_vent_witness_readers.py` (the reader gate, the config round-trip and the
    census end-to-end test).
- This card's Results.

Not in scope: every file the Constraints name as another card's, and `DESIGN.md`. Also not
`engine/events.py`, whose event shape is unchanged.

## Record impact

**What moves: nothing.**
- No committed recording, derived report, fixture, prompt stamp, doc fact or census cell changes.
- The default is today's rule, the key is omitted at its default, and no committed recording
  carries it.
- The field's value list and its layer classification were declared by the spine, so no Literal
  inventory moves here.
- The arm is recorded ON only by the record card, into `replays/candidates/stage-b-r1/9p2i/`.
  There, crew-seen exits are read against the exit-room column, not the all-rooms column, because
  R7 alone removes the 9 room-left exits on s9.

**Publication.**
- A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`).
- This card edits nothing under `api/` or `frontend/` and changes no shown replay. It does change
  engine and observation code, which the bundle's loader executes.
- So the PR proves the bundle unchanged: `scripts/build_demo_bundle.py --out <scratch>` at the
  merge base and at the head, then `diff -r` of the two `data/` trees, which must be empty.

**The adoption consequence, stated now.**
- A missing key means `both_rooms`, and it must keep meaning that for as long as any committed
  recording lacks the key. The four committed sets and the fifth-run archive all lack it today.
- Adopting `physical` therefore takes one of two routes:
  - every later recording writes `vent_witness_rule: "physical"` explicitly, forever;
  - or every set still in use is re-recorded on the adopted rule.
- Flipping the default while baseline-9 bytes remain would silently re-derive every
  reconstruction of a `both_rooms` game under the wrong rule, with every hash still green.
- The `both_rooms` branch is a reader of every committed recording, so graduation cannot delete it
  while such a recording remains. The key stays as a read-only recorded field (craft rule 3; the
  memo's section 1, adoption items 3 and 6).
- A pooled instrument must refuse or stratify sets recorded under different witness rules. The
  census era key does this.

**A limitation that stays.** The hash chain cannot verify which rule a recording was made under.
A tick row stamped with the wrong rule re-simulates with equal hashes. The guard is provenance, not
replay: the declared config's sha256 in the candidate README, and the validity gate's
`--expected-experiment-config` check that every tick row equals the declared config. Both are the
record-plumbing card's.

## Validation

```
uv sync --frozen
# targeted, while developing
uv run pytest tests/engine/test_tick.py tests/engine/test_vent_witness_rule.py \
  tests/eval/test_witness_entitlement.py tests/observation/test_temporal_v2.py \
  tests/scripts/test_scan_recording_packets.py tests/eval/test_vent_witness_readers.py -q
uv run lint-imports
# the OFF path, at the branch head
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
uv run pytest -m campaign                          # the c9 refit pins' campaign-tier half
# the bundle, at the merge base and at the head, into scratch directories outside the tree
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
diff -r <scratch>/bundle-base/data <scratch>/bundle-head/data
# the full gate, whole, in a clean worktree, with its real exit code quoted in Results
bash scripts/check.sh; echo "check.sh exit $?"
```

Every gate runs in a bare shell with no `AILIBI_*` export. `npm --prefix frontend test` and the
Playwright journey are not required: this card touches neither `api/` nor `frontend/`, and the
bundle diff is the publication proof. `check.sh` still runs the frontend legs.

## Results

Not started. The implementer records the following here and in the PR:
- the architecture and decision sections relied on (the spine's arm page, `docs/experiment-arms.md`,
  linked from `docs/architecture.md`, and the decision memo sections 2.2 and 3.4);
- the three decisions under Constraints;
- the reader-gate fixture seed and its room-left exit count;
- the planted failures, each named with its red output;
- every Validation command with its exit code;
- the bundle diff;
- limitations, including the provenance limit under Record impact.
