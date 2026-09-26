# B0: the physical vent witness rule (R7)

**Status:** done

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

- [x] **The engine arm, and the exit that proves it.** `resolve_vent` takes the rule as a keyword.
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
- [x] **Entries equal under both rules** (2.1-2). Mechanism: the physical branch is gated on an exit
  whose destination room differs from the room left.
  - A crewmate in the entry room witnesses under both values.
  - A crewmate in a connected vent's room (REACTOR, while the actor enters ADMIN_VENT) witnesses
    under neither.
  - The two values produce equal events, following the pattern at
    `tests/engine/test_tick.py:505-537`.
  - Planted proof: a variant that also empties `source_witnesses` on entries fails the
    entry-room assertion.
- [x] **An exit in place is one-room under both rules** (2.1-3). Mechanism: the same gate. Every
  occupant of that one room witnesses under `physical`. A planted variant that gates on "is an exit"
  alone empties the list and fails.
- [x] **The default is today's bytes, and an unknown value raises** (2.1-4). `advance_tick` raises
  `ValueError` on an unknown rule before applying any action, as it does for redistribution at
  `engine/tick.py:615-616`. A Hypothesis property over random vent scenes (entries, in-place exits,
  cross-room exits, occupants in either room, vented and dead bystanders) asserts:
  - the default call equals the explicit `"both_rooms"` call;
  - `"physical"` equals `"both_rooms"` on entries and in-place exits;
  - on cross-room exits, `"physical"` keeps `destination_witnesses` unchanged and sets
    `source_witnesses` to `()` and `witnesses` to `destination_witnesses`.
  - Planted proof: flipping the default to `"physical"` fails the first clause.
- [x] **What a crewmate perceives** (2.1-5). Legacy observations follow the event lists unchanged
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
- [x] **Both oracles take the rule** (2.1-6). `assert_event_witnesses_match_source_state` and
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
- [x] **The leak scan and the packet census pass the recorded rule.** `_reconstruct_factory_records`
  reads the rule from the recording's own config (`recorded_experiment_config`,
  `orchestrator/replay.py:741`). A missing config means `both_rooms`. The rule is handed to both
  oracles through one reader. The tests:
  - A fake physical set passes `scan_recording_set` with at least one vent view counted.
  - The same set scanned with the rule withheld from the oracles fails with the vent entitlement
    message.
  - `tests/scripts/test_scan_recording_packets.py` carries both cases, beside its ml_corpus cases.
- [x] **The `leak-scan-factory` walk profile declares its layers.** Mechanism: the profile
  (`eval/leak_scan.py:951`) sets the spine's `threaded_layers` to the layers the scan reads, named
  in Results; the spine names this card as its owner. Proof: it reads the spine's fake full-config
  recording (a copy of a fake recording on today's arms, its tick rows and footer rewritten to
  carry every wave field at its ON value, `vent_witness_rule="physical"` included, with the pending
  set patched empty) with every hash verified, and it refuses a planted unknown field (a stand-in
  added to the config model and `FIELD_LAYER` in a layer the profile does not declare) by name
  before its first advance. Perturbed: the profile with its layer declaration removed refuses the
  full-config copy. `scan_recording_packets.py` on the round-1 candidate walks this profile.
- [x] **The reader gate: a reader that forgets the arm fails** (2.1-7). The fixture is one
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
- [x] **The config line and the pending guard** (2.1-8). The spine's engine-arguments helper
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
- [x] **The census reads 0 by construction on a physical game.** One end-to-end test in this card's
  own reader-gate test file walks the fake physical game through the census card's `--set-dir`
  fold. The census cell "exits seen only from the room left" (C5 in `census_and_record.md`, under
  whatever name the census card ships) reads 0, and its conformance guard passes. Planted proof: the
  same recording walked with the helper's rule withheld at the census walk raises the cell's
  conformance breach. C15 (convictions) is not exercised, because fake meetings eject nobody.
- [x] **The OFF path is byte-identical** (2.1-9). Mechanism: the default value and the omitted key;
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
- [x] **The observation contract states the rule.** `docs/observation-contract.md`'s witnessed
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
  the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs).
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

Implemented on `work/vent-witness-physical` from `bdfa5b19`: `8a9c93d0` (the engine arm, the
helper line, the pending removal, the contract paragraph) and `c99a8dd9` (temporal delivery, both
oracles, the leak scan and its profile, the reader gate and the census end to end). Every command
below ran at `c99a8dd9` in a bare shell with no `AILIBI_*` export, unless it names another commit.

**Sections relied on.** The spine's arm page, `docs/experiment-arms.md` (linked from
`docs/architecture.md`, "Explicit cleanup experiments"): the engine layer, omit-at-default, the
pending guard, the one engine-arguments helper and walk-profile layers. `docs/observation-contract.md`
(the witnessed kill/vent row). The decision memo `tasks/decision-2026-09-24-stage-b-wave.md`:
0.2 (R7), 0.3 items 2, 6 and 9, section 1 (adoption items 3 and 6), 2.2, 3.2 and the card-6 brief
in 3.4. The investigation `tasks/investigations-2026-09-24/vent_witness_and_exit.md` sections 1,
2, 2.1, 5 and 6.2. The dated 2026-09-24 addendum to
`tasks/direction-2026-09-19-process-over-outcome.md`, which lists `vent_witness_rule` among the
wave's recorded fields.

**What was built.**
- `engine/rules.py::resolve_vent` takes a required `vent_witness_rule` keyword. Under `physical`
  an exit whose destination room differs from the room left sets `source_witnesses = ()`, so
  `witnesses` is `destination_witnesses`. Entries and exits in place never change rooms, so the
  gate leaves them alone.
- `engine/tick.py`: `VentWitnessRule` sits beside `RedistributionPolicy`. `advance_tick`,
  `_apply_action` and `_apply_vent` take the rule with a `both_rooms` default, and `advance_tick`
  raises `ValueError("unknown vent witness rule: ...")` before any action applies.
- `orchestrator/experiment_config.py`: one line in `EngineArguments` (so `engine_arguments`
  returns the recorded rule, and `both_rooms` for no config), and `vent_witness_rule` deleted from
  `WAVE_ARMS_PENDING`. Nothing else in that file changed.
- `observation/temporal.py`: a vent reaches a watching observer the event lists among its source
  or destination witnesses, in the observer's event-local room.
- `eval/witness_entitlement.py`, `eval/temporal_entitlement.py`: a required `vent_witness_rule`
  keyword with no default. Each oracle states the two rule names itself (`VENT_WITNESS_RULES`),
  imports neither `engine.rules`, `engine.tick` nor `observation.temporal`, and re-derives the
  lists from ordered state. `git grep` finds 6 and 7 call lines at `bdfa5b19`, as the card
  counted, and 7 and 11 at `c99a8dd9` with this card's new tests; every one passes the rule, and
  strict mypy refuses a call without it.
- `eval/leak_scan.py`: `_recorded_vent_witness_rule` reads the rule once from the recording's
  config through `engine_arguments` (a missing config reads `both_rooms`) and hands it to the
  witness oracle directly and to the temporal oracle through a new `PacketContext.vent_witness_rule`
  field (default `both_rooms`). `scripts/scan_recording_packets.py` needed no edit: it reaches both
  oracles through `_reconstruct_factory_records`.
- The `leak-scan-factory` profile declares `threaded_layers = {orchestrator, tactical, meeting}`.
  The scan rebuilds packets and event batches from the recorded actions and the engine events
  alone, never re-decides a policy (`reconstruct_v3_policies` stays off), never renders a meeting
  prompt and never reads a ballot, so no setting in those layers changes what it checks. Engine
  settings reach it through the helper.
- `docs/observation-contract.md` gains the rule paragraph under the table (default, physical,
  entries and exits in place, a missing key), naming no card, ruling or audit, and its version-2
  sentence now says a vent is delivered to the event's own witnesses.

**Decisions.**
1. `advance_tick` keeps a `both_rooms` default, like `redistribution_policy`, so the test call
   lines do not move; the guard against a forgotten reader is the single helper plus the reader
   gate.
2. The two oracles take the rule as a required keyword: an oracle that defaulted would hide the
   omission the refuter found.
3. The rule is threaded into `_apply_action` as well as `advance_tick`; the lab's direct call
   (`experiments/tactical_gameplay.py`, `_apply_action(..., **engine)`) already takes the helper's
   output, so that file is unedited.
4. The temporal oracle's rule reaches it through `PacketContext` rather than a new required keyword
   on `assert_event_observations_are_entitled`, whose other callers
   (`tests/observation/test_temporal_observations.py`, `eval/leak_test.py`) never see a physical
   recording. The field's `both_rooms` default is pinned by a test, and the factory reconstruction
   always sets it.
5. The watch guard in `observation/temporal.py` is kept, as the card asks. The engine never lists
   a vented or dead player, so on engine events it changes nothing; a forged-metadata test pins it.

**The reader-gate fixture.** `tests/eval/test_vent_witness_readers.py` records seed 0 with the
fake provider at 9 players, 2 impostors, 2 tasks each, `RecordedExperimentConfig(vent_witness_rule="physical")`,
the runner built from the config's meeting values and no environment. It holds 3 exits with a
crewmate in the room left and none in the room surfaced into (ticks 45, 45 and 53, all from
MEDBAY), each crewmate alive at the next packet, so the gate checks 3 (exit, crewmate) pairs. The
three readings (live agent memory, `ReplayLoader._walk(collect_memory=True)`, `walk_replay` with
every tick and meeting hash verified) agree on every vent observation of every agent and hold none
of those exits.

**Planted and perturbed failures.** Each row is one edit to a copy-restored production file, then
the targeted suites (`tests/engine/test_vent_witness_rule.py tests/engine/test_tick.py
tests/eval/test_witness_entitlement.py tests/observation/test_temporal_v2.py
tests/scripts/test_scan_recording_packets.py tests/eval/test_vent_witness_readers.py
tests/orchestrator/test_experiment_arms.py tests/eval/test_replay_walk.py`, 272 tests, run with
`pytest -n 6 --dist loadfile`). The card's named proofs:
- Twin and pin: without the physical branch (N01) the twin
  `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` fails; with the branch
  applied under `both_rooms` too (N03) the pin `test_vent_can_exit_through_connected_destination_vent`
  fails.
- Entries: the gate without the room test (N02) fails
  `test_an_entry_is_witnessed_from_its_one_room_under_both_rules`.
- Exit in place: the gate on "is an exit" alone (N04) fails
  `test_an_exit_in_place_is_witnessed_by_every_occupant_under_both_rules`.
- The default flipped to `physical` (N09) fails the property
  `test_the_rule_changes_only_a_cross_room_exits_room_left` at its first clause, and the pin.
- The room predicate restored in `observation/temporal.py` (N14) fails
  `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[physical]`; the committed test
  `test_the_room_predicate_would_hand_the_physical_exit_to_the_room_left` shows the same through the
  in-test reference copy.
- The refuter's hard fail: `test_a_correct_physical_exit_fails_an_oracle_left_at_both_rooms`
  (witness oracle) and `test_the_temporal_oracle_takes_the_rule_the_events_were_made_under` (its
  temporal pair) are committed planted cases.
- The scan: `test_a_physical_set_fails_the_scan_with_the_rule_withheld` raises "vent source witness
  entitlement"; `test_a_temporal_physical_set_fails_with_the_rule_withheld_from_the_v2_oracle`
  raises "v2 missing, extra or incorrectly ordered/positioned evidence".
- The profile: `test_the_factory_profile_without_its_layers_refuses_the_full_config_copy` and
  `test_the_factory_profile_refuses_a_stand_in_in_a_layer_it_does_not_declare[engine|format]`
  (every declarable layer is declared, so the undeclared layers are the engine and format ones);
  both refuse by name with no walk event yielded.
- The reader gate: `test_a_site_that_forgets_the_rule_fails_the_gate_with_every_hash_equal[live|loader|walk]`,
  each naming its own site's problems for all 3 pairs; `test_a_helper_without_the_rule_refuses_the_physical_game`.
- The census: `test_the_census_walk_without_the_rule_raises_the_cells_breach` (exit 1,
  "conformance breach: ... vent_witness_rule = physical ... seed 0").
- The contract: `test_the_contract_check_bites_a_new_value_and_a_deleted_sentence`.
- The OFF path: the physical branch applied under `both_rooms` (N03, by hand at `c99a8dd9`, then
  restored from a copy) turned `uv run python scripts/publish_gameplay_census.py --check` red (exit 1,
  "docs/gameplay-census.md, docs/gameplay-census.json is STALE") and the pin red
  (`FAILED tests/engine/test_tick.py::test_vent_can_exit_through_connected_destination_vent`).

**Neuter pass.** Every production line, argument and row this card adds or changes, neutered one
at a time. All 27 went red; none first came back green.

| neuter | targeted result | first failing test |
|---|---|---|
| N01 rules: physical branch removed | 18 failed, 254 passed | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| N02 rules: room-difference gate dropped | 8 failed, 264 passed | `test_an_entry_is_witnessed_from_its_one_room_under_both_rules` |
| N03 rules: rule test dropped | 19 failed, 253 passed | `test_vent_can_exit_through_connected_destination_vent` |
| N04 rules: gate on is-an-exit alone | 3 failed, 269 passed | `test_an_exit_in_place_is_witnessed_by_every_occupant_under_both_rules` |
| N05 tick: unknown-rule validation removed | 4 failed, 268 passed | `test_an_unknown_rule_raises_before_any_action_applies[PHYSICAL]` |
| N06 tick: `_apply_vent` passes `both_rooms` | 18 failed, 254 passed | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| N07 tick: `_apply_action` drops the rule | 18 failed, 254 passed | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| N08 tick: `advance_tick` drops the rule | 17 failed, 255 passed | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| N09 tick: `advance_tick` default flipped | 5 failed, 267 passed | `test_vent_can_exit_through_connected_destination_vent` |
| N10 tick: `_apply_action` default flipped | 1 failed, 271 passed | `test_the_per_action_entry_points_default_to_both_rooms` |
| N11 tick: `_apply_vent` default flipped | 1 failed, 271 passed | `test_the_per_action_entry_points_default_to_both_rooms` |
| N12 config: helper line removed | 14 failed, 244 passed, 14 errors | `test_an_engine_setting_the_helper_does_not_thread_is_refused_by_any_profile` |
| N13 config: pending name restored | 2 failed, 246 passed, 12 errors | `test_an_engine_setting_the_helper_does_not_thread_is_refused_by_any_profile` |
| N14 temporal: room predicate restored | 6 failed, 266 passed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[physical]` |
| N15 witness oracle: validation removed | 3 failed, 269 passed | `test_an_unknown_rule_raises[PHYSICAL]` |
| N16 witness oracle: physical branch removed | 8 failed, 264 passed | `test_a_correct_physical_exit_fails_an_oracle_left_at_both_rooms` |
| N17 witness oracle: room gate dropped | 5 failed, 267 passed | `test_an_entry_and_an_exit_in_place_keep_their_one_room_witnesses[physical]` |
| N18 witness oracle: rule test dropped | 8 failed, 264 passed | `test_leak_scan_profile_tolerates_doubled_meeting_row` |
| N19 temporal oracle: validation removed | 3 failed, 269 passed | `test_the_temporal_oracle_raises_on_an_unknown_rule[PHYSICAL]` |
| N20 temporal oracle: physical set removed | 4 failed, 268 passed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[physical]` |
| N21 leak scan: layer declaration removed | 1 failed, 271 passed | `test_the_factory_profile_scans_a_full_config_copy_with_every_hash_verified` |
| N22 leak scan: reader returns the default | 3 failed, 269 passed | `test_a_physical_set_passes_the_scan_with_vent_views` |
| N23 leak scan: witness oracle call drops the rule | 3 failed, 269 passed | `test_a_physical_set_passes_the_scan_with_vent_views` |
| N24 leak scan: context built without the rule | 1 failed, 271 passed | `test_a_temporal_physical_set_passes_the_scan_with_event_batches` |
| N25 leak scan: wrapper passes a constant rule | 2 failed, 270 passed | `test_the_scan_context_hands_its_rule_to_the_temporal_oracle` |
| N26 leak scan: context default flipped | 1 failed, 271 passed | `test_the_scan_context_hands_its_rule_to_the_temporal_oracle` |
| N27 leak scan: temporal version read dropped | 2 failed, 270 passed | `test_a_temporal_physical_set_fails_with_the_rule_withheld_from_the_v2_oracle` |

Before the pass, a line-by-line read of the diff found no test for the `_apply_action` and
`_apply_vent` defaults (N10, N11), the `PacketContext` default (N26) or the wrapper's argument
(N25); `test_the_per_action_entry_points_default_to_both_rooms` and
`test_the_scan_context_hands_its_rule_to_the_temporal_oracle` were added for them first. In the pass
itself no neuter came back green.

**Mutation pass.** One bounded pass over the lines this card added or changed and the vent branches
they sit in (`engine/rules.py`, `engine/tick.py`, `observation/temporal.py`, both oracles,
`eval/leak_scan.py`), with exactly the eight operator classes, each mutant run against the same
targeted suites. 37 mutants: 34 killed, 3 equivalent.

| mutant [class] | targeted result | first failing test |
|---|---|---|
| M01 [1] temporal: watch guard dropped | 1 failed | `test_a_vent_listing_a_vented_or_dead_observer_still_reaches_neither` |
| M02 [1] leak scan: helper dropped from the reader | 272 passed | equivalent (below) |
| M03 [2] rules: destination list emptied instead | 22 failed | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| M04 [2] temporal: source list read as the destination list | 5 failed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[both_rooms]` |
| M05 [2] temporal: the two lists read as the combined list | 272 passed | equivalent (below) |
| M06 [2] temporal oracle: physical room set reads the room left | 4 failed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[physical]` |
| M07 [2] witness oracle: arrival read for the room left | 6 failed | `test_leak_scan_profile_tolerates_doubled_meeting_row` |
| M08 [3] rules: rule test becomes is-not-None | 19 failed | `test_vent_can_exit_through_connected_destination_vent` |
| M09 [3] rules: room test becomes is-not-None | 8 failed | `test_an_entry_is_witnessed_from_its_one_room_under_both_rules` |
| M10 [3] tick: validation becomes is-None | 4 failed | `test_an_unknown_rule_raises_before_any_action_applies[PHYSICAL]` |
| M11 [3] witness oracle: rule test becomes is-None | 8 failed | `test_a_correct_physical_exit_fails_an_oracle_left_at_both_rooms` |
| M12 [3] witness oracle: room test becomes is-not-None | 5 failed | `test_an_entry_and_an_exit_in_place_keep_their_one_room_witnesses[physical]` |
| M13 [3] temporal oracle: rule test becomes is-None | 4 failed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[physical]` |
| M14 [3] temporal oracle: validation becomes is-None | 3 failed | `test_the_temporal_oracle_raises_on_an_unknown_rule[PHYSICAL]` |
| M15 [4] rules: room left read as ADMIN | 7 failed | `test_the_rule_changes_only_a_cross_room_exits_room_left` |
| M16 [4] rules: destination room read as REACTOR | 7 failed | `test_an_entry_is_witnessed_from_its_one_room_under_both_rules` |
| M17 [4] witness oracle: actor room read as ADMIN | 4 failed | `test_a_physical_set_passes_the_scan_with_vent_views` |
| M18 [4] temporal: reported room read as the destination | 3 failed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[both_rooms]` |
| M19 [4] temporal oracle: destination room read as REACTOR | 1 failed | `test_a_temporal_physical_set_passes_the_scan_with_event_batches` |
| M20 [5] tick: unknown-rule message constant | 4 failed | `test_an_unknown_rule_raises_before_any_action_applies[PHYSICAL]` |
| M21 [5] witness oracle: unknown-rule message constant | 3 failed | `test_an_unknown_rule_raises[PHYSICAL]` |
| M22 [5] temporal oracle: unknown-rule message constant | 3 failed | `test_the_temporal_oracle_raises_on_an_unknown_rule[PHYSICAL]` |
| M23 [6] leak scan: orchestrator layer dropped | 1 failed | `test_the_factory_profile_scans_a_full_config_copy_with_every_hash_verified` |
| M24 [6] leak scan: tactical layer dropped | 1 failed | same |
| M25 [6] leak scan: meeting layer dropped | 1 failed | same |
| M26 [6] witness oracle: `physical` dropped from its rules | 12 failed | `test_a_correct_physical_exit_fails_an_oracle_left_at_both_rooms` |
| M27 [6] temporal oracle: `physical` dropped from its rules | 5 failed | `test_each_oracle_states_the_rule_for_itself[eval.temporal_entitlement]` |
| M28 [6] tick: `physical` dropped from the alias | 21 failed, 14 errors | `test_physical_vent_exit_is_witnessed_only_from_the_room_surfaced_into` |
| M29 [7] witness oracle: branches swapped | 16 failed | `test_leak_scan_profile_tolerates_doubled_meeting_row` |
| M30 [7] temporal oracle: branches swapped | 6 failed | `test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms[both_rooms]` |
| M31 [8] tick: `get_args(VentWitnessRule)` replaced by its literal | 272 passed | equivalent (below) |
| M32 [8] rules: map vent room replaced by the canonical room | 2 failed | `test_a_physical_exit_follows_the_maps_vent_room` |
| M33 [8] witness oracle: map vent room replaced by the canonical room | 1 failed | `test_the_physical_expectation_follows_the_maps_vent_room` |
| M34 [8] leak scan: recorded config replaced by the default | 4 failed | `test_a_physical_set_passes_the_scan_with_vent_views` |
| M35 [6] temporal: exit kind dropped from the vent branch | 1 failed, 6 errors | `test_a_temporal_physical_set_passes_the_scan_with_event_batches` |
| M36 [6] witness oracle: exit kind dropped from the vent branch | 19 failed | `test_leak_scan_profile_tolerates_doubled_meeting_row` |
| M37 [6] temporal oracle: entry kind dropped from the vent branch | 2 failed | `test_a_temporal_physical_set_fails_with_the_rule_withheld_from_the_v2_oracle` |

First-round survivors, and what killed them: M32 and M33 survived the first round, because the
planted relocated-vent map only exercised a cross-room exit; an exit in place through the moved vent
was added to both planted-map tests. M01, M04 and M05 first came back as collection errors, because
the in-test reference copy was located by the production predicate's own text; the reference now
locates the vent clause by the branch around it, and M01 and M04 then failed on semantic tests.

Equivalent mutants:
- M02: the reader's value is the recorded field either way, and an engine field the helper does not
  thread is still refused by name before the first advance, by the walk's own `engine_arguments`
  call.
- M05: the engine builds `witnesses` as exactly the sorted union of the two lists.
- M31: the literal equals `get_args(VentWitnessRule)`, which
  `test_the_default_rule_is_both_rooms_at_every_layer` pins.

**Changed test expectations (no test weakened, skipped or deleted).**
- `tests/orchestrator/test_experiment_arms.py`: `test_no_config_threads_todays_engine_arguments` and
  `test_a_stand_in_engine_field_raises_where_hand_threading_runs_the_default` now expect
  `"vent_witness_rule": "both_rooms"` in the helper's output.
  `test_an_engine_field_the_helper_does_not_thread_is_refused` was parametrised over the engine
  fields the helper does not thread, which this card empties (pytest would report it as skipped);
  it now takes every engine field and plants the field out of the threaded set, so it still runs
  (2 cases).
- `tests/eval/test_replay_walk.py::test_an_engine_setting_the_helper_does_not_thread_is_refused_by_any_profile`
  used `vent_witness_rule="physical"` as its unthreaded field. It now walks that copy with every hash
  verified and plants the unthreaded case by patching the helper's threaded fields.
- The 11 existing oracle call lines in `tests/eval/test_witness_entitlement.py` and
  `tests/observation/test_temporal_v2.py` pass `vent_witness_rule="both_rooms"`.

**Measured at `c99a8dd9`, through the production path, count-only.** From
`uv run python scripts/publish_gameplay_census.py --check` (exit 0), which recomputes
`docs/gameplay-census.md` from the recordings, the card's table stands: vent exits 512 pooled,
435 on the two nine-player sets, 85 on s9; seen by crew 313, 271, 62; seen from the exit room 251,
226, 53; seen only from the room left 62, 45, 9; vent-band impostor ejections 326, 281, 70, of which
resting only on the room left 50, 37, 8. The fifth-run archive, re-measured count-only over the
first tick row of each file: 100 recordings, all `temporal_observation_version` 2, all with a
12-key experiment config, 0 carrying `vent_witness_rule`. The four committed sets: 300 recordings,
0 carrying the key (`grep -l vent_witness_rule` per set).

**Validation, at `c99a8dd9`** (each exit code captured directly):

| command | exit | result |
|---|---|---|
| `uv run lint-imports` | 0 | 4 contracts kept |
| `bash scripts/verify_samples.sh replays/samples/9p2i` | 0 | 50 verified clean |
| `bash scripts/verify_samples.sh replays/samples/4p1i` | 0 | 50 verified clean |
| `bash scripts/verify_samples.sh replays/ml_corpus/9p2i` | 0 | 150 verified clean |
| `bash scripts/verify_samples.sh replays/ml_corpus/4p1i` | 0 | 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, four sets | 0 each | consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `uv run python scripts/check_doc_facts.py` | 0 | passed |
| `uv run python scripts/validate_task_docs.py` | 0 | 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0 | every check passed, 7 evidence-branch-absent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 0 | 25 passed |
| `uv run python scripts/scan_recording_packets.py replays/ml_corpus/9p2i` and `.../4p1i` | 0, 0 | 150 games, 24615 packets, 376 vent views; 50 games, 1895 packets, 31 vent views; both JSON outputs byte-identical to the same command at `bdfa5b19` |
| the card's targeted pytest line | 0 | 146 passed |
| `uv run pytest -m campaign -q` | 0 | 336 passed |
| `8a9c93d0` alone: engine, orchestrator config, walk, oracle, observation, scan and census suites | 0 | 828 passed |

**The bundle.** `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head` at
`c99a8dd9` and the same command in a `git archive` of `bdfa5b19`, whose replay files were given the
worktree's modification times first (the loader serves each file's mtime as `created_at`, which
otherwise differs between a checkout and an archive). Both wrote 156 baked JSON files;
`diff -r <scratch>/bundle-base/data <scratch>/bundle-head/data` printed nothing and exited 0.

**The adoption consequence.** A missing key means `both_rooms`, and must keep meaning it while any
committed recording lacks the key: the four committed sets and the fifth-run archive all lack it
today. Adopting `physical` therefore takes one of two routes: every later recording writes
`vent_witness_rule: "physical"` explicitly, for as long as the key exists, or every set still in
use is re-recorded on the adopted rule. Flipping the default while baseline-9 bytes remain would
re-derive every reconstruction of a `both_rooms` game under the wrong rule with every hash still
green. The `both_rooms` branch reads every committed recording, so graduation cannot delete it
while one remains; the key stays a read-only recorded field. A pooled instrument must refuse or
stratify sets recorded under different rules; the census era key does.

**Limitations.**
- The hash chain cannot verify which rule a recording was made under: a tick row stamped with the
  wrong rule re-simulates with equal hashes. The guard is provenance (the candidate README's config
  sha256 and the validity gate's `--expected-experiment-config`), both the record-plumbing card's.
- The reader gate covers the three re-simulation sites the card names. The lab's per-action apply
  takes the helper's output through the spine's `ast` scan, not through this gate.
- The fake-provider game establishes mechanics only; fake meetings eject nobody, so the census's
  convictions cell (C15) is not exercised end to end.
- `docs/game-shape.md` ("Venting is visible") still describes the default rule, which it states
  is the default configuration's; it names no experiment and is not this card's file.
  `DESIGN.md:351` is historical and unedited.
- Closing greps at `c99a8dd9`: `git grep -n -i -E 'room (it|the impostor) (leaves|left)|source.destination room|witness metadata|entitlement independently'`
  outside `tasks/`, `audits/`, `agent_prompts/`, `replays/`, `training/reports/` and the census
  pages finds `DESIGN.md:351` (historical), `api/replay_loader.py:2188` and `api/schemas.py:429`
  (a vent transition's two endpoints, not its witnesses), `docs/game-shape.md:13` (the default, as
  above) and this card's own new sentences; `git grep -n -i physical` filtered for pending,
  unbuilt, refused or unthreaded finds only the new test's name.

**Deviations from Expected scope, all direct follow-through.** `tests/orchestrator/test_experiment_arms.py`
(which the card said this card would not edit) and `tests/eval/test_replay_walk.py`, for the three
expectations above; `docs/experiment-arms.md`, whose pending-guard sentence listed `physical`; the
card's Status line and the `tasks/README.md` inventory sentence, which the dispatch asked this card
to flip and re-derive.

**The full gate.** `bash scripts/check.sh` runs at the commit that records these Results; its
exit code and counts are recorded in the commit after it.
