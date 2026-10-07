# Experiment arms

The Stage-B gameplay wave changes behaviour only through recorded experiment
arms. Each arm is a field of `RecordedExperimentConfig`
([`orchestrator/experiment_config.py`](../orchestrator/experiment_config.py)),
off by default, written on every tick row and on the game-over row of a
recording that turns it on. The wave adds no `AILIBI_*` lever and no
environment switch. The one older switch among the wave's fields,
`AILIBI_BOUNDED_REBUTTAL`, still selects `bounded_rebuttal_version` for a
meeting runner built from the environment, and a game using that runner
records the value; `build_default_meeting_runner` refuses the switch exported
ON beside a declared profile. The owner's rulings and the wave's design are in
[the Stage-B decision memo](../tasks/decision-2026-09-24-stage-b-wave.md)
(sections 0.3, 1 and 3.3) and in the dated 2026-09-24 addendum to
[the process-over-outcome direction](../tasks/direction-2026-09-19-process-over-outcome.md).

## The fields

`FIELD_LAYER` classifies every config field by the consumer that reads it:
`format` (the recording format), `engine` (the engine tick), `orchestrator`
(the game's own wiring), `tactical` (the per-tick policies) or `meeting` (the
meeting evidence profile). The wave's eight fields, the kill cooldown the
balance round added and the route lines round 3 adds, defaults first:

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
| `kill_cooldown_ticks` | none (the map's value), an integer of at least 1 | engine | [kill cooldown](../tasks/work/kill-cooldown-arm.md) |
| `route_lines_version` | none, `1` | meeting | [route lines](../tasks/work/route-lines-field.md) |

The meeting layer is exactly `MeetingEvidenceProfile`'s fields, and the
tactical layer is exactly `TacticalExperimentOptions`' fields apart from the
derived `meeting_positions_preserved`; tests in
`tests/orchestrator/test_experiment_config.py` hold both equal.

## What a missing key means

`vent_witness_rule`, `vent_entry_policy`, `report_body_handle_version`,
`ballot_kill_row_version`, `impostor_ballot_version`, `kill_cooldown_ticks` and
`route_lines_version` are omitted from the serialized config while they hold
their default, under every
`format_version` (`OMITTED_AT_DEFAULT`, applied by the config's serializer). So
no committed payload gains a key and the wave's config serializes with
`format_version` 1. A missing key means the historical default, now and after
adoption: a recording that adopts a value writes it explicitly.
`tests/orchestrator/test_experiment_arms.py` re-serializes every committed
config payload and requires the committed bytes.

## Every value is built

Every value of the wave's fields has its behaviour built, so config validation
accepts each of them and the declared round-1 config validates. The guard that
refused a value while its behaviour was unbuilt was deleted, with its call sites
and its tests, by the ballot card, the last arm card to merge. Validation still
refuses evidence version 1, and `post_meeting_retarget`, beside
`meeting_reset = hub_with_grace`.

## One engine-arguments helper

`engine_arguments` turns a recorded config (or none) into the keyword
arguments of `engine.tick.advance_tick`. The live tick in
`orchestrator/game.py`, the replay loader, the shared replay walk and both
sites of the tactical lab take their engine keywords from it. It raises,
naming the field, for an engine-layer field set off its default that it does
not thread, because a witness list lives only in the events and a site that
dropped such a field could still reproduce every state hash. The kill cooldown
is also written outside the tick, at the seeding and at each regroup, so the
live game, the loader, the walk and the prompt-byte golden pass the same
helper result's `kill_cooldown_ticks` to `seed_initial_state` and to every
`apply_meeting_result`. An `ast` scan in
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

The three ballot fields have no environment switch: `EXPERIMENT_ENV_NAMES`
keeps its four names and `.env.example` does not change. A declared config
reaches the meeting runner through `profile_from_config` and
`build_default_meeting_runner(profile=...)`, which refuses an environment that
also exports any of the four switches ON. `HeadlessGame` requires a default
meeting runner's three ballot fields to equal the recorded config's, both ways.

A meeting arm that re-bodies a template registers it in
`EXPERIMENT_ARM_TEMPLATES`, and
`prompt_versions_for_set(..., experiment_config=...)` serves its stamp only for
a config that carries the arm. The stamp suffix is derived from the field,
never chosen: drop `_version` and append `_v<value>`. The three ballot fields
re-body `vote_ballot` alone, with guarded blocks in the same `vote_ballot.j2`
whose header marker stays `vote_ballot.qwen3_6_27b.v8`, so their stamps read
`vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1`,
`vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1` and
`vote_ballot.qwen3_6_27b.v8.route_lines_v1`, joined by `+` in that order when
more than one is ON.

`ballot_kill_row_version` gives a voter one first-hand `own_kill` evidence row
for each kill it watched a non-teammate make, and never a public flag, a ledger
row or a belief input. `impostor_ballot_version` serves an impostor voter a
ballot framed as a move for its side, bounded by an instructed citation rule the
tally does not enforce. `route_lines_version` adds one `<routes>` block
between the map card and the evidence block: for each living candidate whose
places stated at the table change room in a way the doors or the public regroup
allow, one role-blind line lists each such change with its door count and
either "walking fits" or the regroup tick that falls between
([`meetings/route_lines.py`](../meetings/route_lines.py)). A change of room that
neither allows is left out, a candidate with none has no line, and the line
names, ranks and recommends no one. A runner refuses any of the three arms
beside any of the four legacy meeting overlays, for a prompt set whose vote body
carries no block for it, and under an explicit version pin that does not credit
exactly the arms its profile renders; the meeting profile refuses any of them
beside an account profile, and the route lines beside
`evidence_reasoning_version = 2`.

## Frozen values

Once round 1 is recorded, an arm value's meaning is frozen. A revision adds a
new value (for example `look_and_wait_2`) and never redefines a recorded one;
this holds for `hub_with_grace` too.

## Adopted arms

On 2026-10-01 the owner adopted seven of the Stage-B fields after candidate round 1
(`audits/audit-2026-09-27-stage-b-r1.md`): `vent_witness_rule = physical`,
`vent_entry_policy = own_fresh_kill`, `meeting_reset = hub_with_grace`,
`bounded_rebuttal_version = 1`, `report_body_handle_version = 1`,
`ballot_kill_row_version = 1` and `impostor_ballot_version = 1`. Adopted means every
candidate round from round 2 on declares them ON, and the documents describe the
game they produce as the current one. It does not move any default: a missing key
keeps its historical meaning, which is what lets the baseline-9 sets keep verifying
byte-identically. `vent_exit_policy = look_and_wait` is kept in every round as well;
its balance effect is the subject of round 2, which adds one dial and nothing else.

## Candidate round 1

The ladder tip stands at baseline 9.
[`replays/candidates/stage-b-r1/9p2i`](../replays/candidates/stage-b-r1/README.md)
is candidate round 1, recorded with the experimental switches its README
names; it adopts nothing and is not a canonical sample set.

## Candidate round 2, the shown set

Candidate round 2 was recorded with the adopted switches, the kept vent exit
and a six-tick kill cooldown, under one declared config. On 2026-10-02 the owner
promoted it: it is now [`replays/samples/9p2i`](../replays/samples/9p2i/MANIFEST.md),
the shown 9-player set, in its own era (`eval/eras.py`), with that config beside
its replays as `experiment-config.json`, and its candidate copy is deleted
([the record](../audits/audit-2026-10-01-stage-b-r2.md), section 9). Promotion
moves no default. The set carries one flag its record states: reporters ejected
per report meeting read 17/114, above the pre-registered 0.104, so the round's
own rule named no promotion step; the owner's ruling promotes it regardless. The
ladder tip stands at baseline 9.
