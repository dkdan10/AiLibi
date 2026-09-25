# Experiment arms

The Stage-B gameplay wave changes behaviour only through recorded experiment
arms. Each arm is a field of `RecordedExperimentConfig`
([`orchestrator/experiment_config.py`](../orchestrator/experiment_config.py)),
off by default, written on every tick row and on the game-over row of a
recording that turns it on. No `AILIBI_*` lever and no environment switch
selects a Stage-B arm. The owner's rulings and the wave's design are in
[the Stage-B decision memo](../tasks/decision-2026-09-24-stage-b-wave.md)
(sections 0.3, 1 and 3.3) and in the dated 2026-09-24 addendum to
[the process-over-outcome direction](../tasks/direction-2026-09-19-process-over-outcome.md).

## The eight fields

`FIELD_LAYER` classifies every config field by the consumer that reads it:
`format` (the recording format), `engine` (the engine tick), `orchestrator`
(the game's own wiring), `tactical` (the per-tick policies) or `meeting` (the
meeting evidence profile). The wave's fields, defaults first:

| Field | Values | Layer | Card that builds it |
| --- | --- | --- | --- |
| `vent_witness_rule` | `both_rooms`, `physical` | engine | [physical vent witness](../tasks/work/vent-witness-physical.md) |
| `vent_exit_policy` | `target_distance`, `observed_risk`, `look_and_wait` | tactical | [look and wait](../tasks/work/vent-look-and-wait.md) |
| `vent_entry_policy` | `any_body`, `own_fresh_kill` | tactical | [look and wait](../tasks/work/vent-look-and-wait.md) |
| `meeting_reset` | `preserve`, `hub_with_grace` | orchestrator | exists; [coherence](../tasks/work/meeting-reset-coherence.md) |
| `bounded_rebuttal_version` | none, `1` | meeting | exists; [readers](../tasks/work/stage-b-readers.md) |
| `report_body_handle_version` | none, `1` | orchestrator | [body handle](../tasks/work/report-body-handle.md) |
| `ballot_kill_row_version` | none, `1` | meeting | [ballot](../tasks/work/ballot-kill-row-and-impostor-strategy.md) |
| `impostor_ballot_version` | none, `1` | meeting | [ballot](../tasks/work/ballot-kill-row-and-impostor-strategy.md) |

The meeting layer is exactly `MeetingEvidenceProfile`'s fields, and the
tactical layer is exactly `TacticalExperimentOptions`' fields apart from the
derived `meeting_positions_preserved`; tests in
`tests/orchestrator/test_experiment_config.py` hold both equal.

## What a missing key means

`vent_witness_rule`, `vent_entry_policy`, `report_body_handle_version`,
`ballot_kill_row_version` and `impostor_ballot_version` are omitted from the
serialized config while they hold their default, under every
`format_version` (`OMITTED_AT_DEFAULT`, applied by the config's serializer). So
no committed payload gains a key and the wave's config serializes with
`format_version` 1. A missing key means the historical default, now and after
adoption: a recording that adopts a value writes it explicitly.
`tests/orchestrator/test_experiment_arms.py` re-serializes every committed
config payload and requires the committed bytes.

## The pending guard

`WAVE_ARMS_PENDING` lists each new ON value whose behaviour is not built yet:
`physical`, `look_and_wait`, `own_fresh_kill`, and version 1 of the body
handle and both ballot fields. Config validation refuses a listed value,
naming field and value; the `HeadlessGame` constructor checks again, so a
config built past validation is refused too; and `build_default_meeting_runner`
refuses a profile carrying a listed ballot value. Each arm card deletes its own
names when it builds the behaviour. The ballot card, merging last, deletes the
emptied guard, its call sites and its test, and the record card's preflight
confirms it is gone. Validation also refuses evidence version 1, and
`post_meeting_retarget`, beside `meeting_reset = hub_with_grace`.

## One engine-arguments helper

`engine_arguments` turns a recorded config (or none) into the keyword
arguments of `engine.tick.advance_tick`. The live tick in
`orchestrator/game.py`, the replay loader, the shared replay walk and both
sites of the tactical lab take their engine keywords from it. It raises,
naming the field, for an engine-layer field set off its default that it does
not thread, because a witness list lives only in the events and a site that
dropped such a field could still reproduce every state hash. An `ast` scan in
`tests/orchestrator/test_experiment_arms.py` fails on an `advance_tick` or
`_apply_action` call in those modules that does not take the helper's
arguments.

A replay-walk profile reads the older experiment fields when it sets
`supports_experiments`. A recording that sets a Stage-B field, or the
`look_and_wait` value, outside the engine layer is read only by a profile that
names that field's layer in `threaded_layers`; any other profile refuses it
before its first advance, naming field and profile. Every profile declares no
layer until its owner reviews what its consumer reads.

## Config-only ballot fields

The two ballot fields have no environment switch: `EXPERIMENT_ENV_NAMES` keeps
its four names and `.env.example` does not change. A declared config reaches
the meeting runner through `profile_from_config` and
`build_default_meeting_runner(profile=...)`, which refuses an environment that
also exports any of the four switches ON. `HeadlessGame` requires a default
meeting runner's two ballot fields to equal the recorded config's, both ways.

A meeting arm that re-bodies a template registers it in
`EXPERIMENT_ARM_TEMPLATES` (empty until the ballot card), and
`prompt_versions_for_set(..., experiment_config=...)` serves its stamp only for
a config that carries the arm. The stamp suffix is derived from the field,
never chosen: drop `_version` and append `_v<value>`, so the ballot stamps
read `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1` and
`vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`.

## Frozen values

Once round 1 is recorded, an arm value's meaning is frozen. A revision adds a
new value (for example `look_and_wait_2`) and never redefines a recorded one;
this holds for `hub_with_grace` too.
