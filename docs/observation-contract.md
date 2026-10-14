# Game rules and what each player may know

The first part states the rules that shape every game, each with the code that
enforces it; the second, what the observation firewall lets each player know,
and when.

## The rules that shape every game

Six rules shape every game the default configuration plays, which is every
game of the baseline-9 era: the 4-player set and the ML corpus. Each section
names the code that enforces its rule. An experiment can change one of them only
through a recorded experiment field, and no default has moved. The shown
9-player set is a later era (`eval/eras.py`), recorded under one declared config
(`replays/samples/9p2i/experiment-config.json`) that changes two of these rules,
as the sections below say; the other four hold there too.

### Venting is visible

Only impostors vent. `engine.rules.resolve_vent` lists the witnesses of each
vent by the rule below, and the observation layer shows each witness the vent as
that player's action. At a meeting, a spoken vent claim that matches the
speaker's own witness record becomes a public `vent_sighting`
[flag](glossary.md#flag-minting-stamping-a-contradiction-into-the-transcript)
(`meetings.transcript.detect_contradictions`). A vent claim with no matching
record raises no flag.

Who witnesses a vent is set by the recording's `vent_witness_rule`. Under the
default, `both_rooms`, a vent exit is witnessed from the room the impostor left
and from the room it surfaced into. Under `physical`, an exit into another room
is witnessed only from the room surfaced into, because the impostor was unseen
inside the vent it left. An entry, and an exit in place, happen in one room and
are witnessed from that room under both rules. A recording without the key
reads as `both_rooms`.

The shown 9-player set's declared config sets `physical`. Its impostors also
vent only away from their own fresh kill (`vent_entry_policy`) and look before
leaving a vent (`vent_exit_policy`).

### Impostors never report

The default impostor policy, `agents.tactical.impostor_policy.ImpostorPolicy`,
never asks to report a body or to call an emergency meeting. When a body lies in
its room it walks away, or vents away when the room has a vent and nobody but a
teammate is there to see. Impostor self-report exists only as an experiment
(`self_report`), off by default.

### Actions resolve in player-id order

`orchestrator.action_ordering.order_actions_for_tick` sorts each tick's actions
by player id, and `engine.tick.advance_tick` applies them in that order. When an
action opens a meeting, `advance_tick` returns at once: the actions of players
later in the order are dropped for that tick, and the end-of-tick updates (kill
cooldowns, sabotage timers and task progress) do not run.

### Every move takes one tick

A player crosses one room edge, or one vent, per tick: `engine.world.Edge` and
`engine.world.Vent` reject any other `traversal_ticks`, because the engine has
no in-transit state and public pathing and meeting geometry count adjacency
hops. A custom map loads through `engine.world.load_map`, so unsupported timing
and invalid topology fail before a simulation begins. Task, sabotage and
cooldown durations stay configurable. Longer moves would need a coordinated
engine, observation, pathing, reasoning and spectator change, with explicit
recording compatibility.

### Meetings pause the world

Under the default (`meeting_reset = preserve`), a meeting changes the map in two
ways only: it removes the reported body and, on an ejection, the ejected player.
`orchestrator.game.apply_meeting_result` removes only the body that was
reported, so every other corpse stays where it fell, and players resume where
they stood.
Kill cooldowns do not count down across a meeting: `engine.tick._decrement_cooldowns`
runs only among the end-of-tick updates of a play tick, which neither the tick
that opened the meeting nor the meeting itself runs.

The shown 9-player set records a regroup instead (`meeting_reset =
hub_with_grace`): [the regroup reset](#the-regroup-reset) below says what it
moves, clears and restarts.

### Crewmates see one room

At the map's base visibility, `engine.visibility._resolve_observer_visibility_mode`
limits a crewmate to its own room, while an impostor also sees the adjacent
rooms. An active lights sabotage limits everyone to their own room. The map
file's comment that visibility is uniform across the map describes its base
setting, not what each role sees.

## What each player may know

The observation firewall projects engine truth into typed values. An agent may
retain only the listed evidence; knowing that a player died is distinct from
knowing when or where the kill occurred.

| Channel | Source and entitled recipient | Permitted fields | Event time | Delivery | Memory citation |
| --- | --- | --- | --- | --- | --- |
| Self and team | Recipient's own current state; teammate identities only for impostors | Own role, room, tasks, cooldown, teammate IDs | Snapshot tick | Before a tactical decision | Observed self-state ID; role/team stay private |
| Visible players and tasks | Current visibility and public task activity | Player, room, visible action; own task progression | Snapshot tick | Before decision | Observed player/task IDs |
| Body discovery | Visible, undiscovered corpse | Public `body-{victim_id}` handle, victim, room; no death time or killer | Discovery snapshot tick | Before decision | Observed body ID records discovery time |
| Witnessed kill/vent | Engine event's actual witness set | Actor, entitled event room, kill/vent action | Source event tick in temporal mode | Legacy: next ordinary snapshot; temporal: after advance, before meeting | Observed player/action ID |
| Own kill | Resolved kill actor alone | Victim and kill room | Source event tick in temporal mode | Same schedule as witnessed events | Observed own-kill ID |
| Movement | Legacy: departure room visible from post-tick observer state. Temporal: actor visible immediately before that move resolves in sequential action order | Actor, source room, destination room | Source event tick in temporal mode | Legacy: next snapshot; temporal: before meeting | Observed movement ID |
| Global status and alarm | Public aggregates; alarm available to every scheduled recipient | Task totals, sabotage status; exactly one roomless alarm while active | Snapshot tick | Before decision; dead players are not scheduled | Global aggregate inferred; alarm observed |
| Dead roster and ejection | Public meeting announcement | Public dead/ejected identities and meeting result; no hidden kill time or role | Announcement tick | Meeting opening/conclusion | Meeting outcome memory; not a private kill observation |

`EventObservationBatch` separates source-time evidence from current-state
snapshots. In temporal mode the next snapshot does not repeat kill, vent, own
kill or movement actions. A witness killed later in the action batch still
receives its earlier entitled events; it receives no later tactical decision.
Per-source identity prevents repeated event delivery from adding citations or
applying belief updates twice. Custom agents opting into this mode must expose
`observe_events`; unsupported agents fail explicitly.

The temporal version is default OFF and has no adopting record. An optional
tick-row version identifies a partial recording before any terminal stamp;
missing means legacy timing. Current readers select the recorded version,
reject mixed/conflicting versions, and share live projection and ingestion.
Frozen instruments without an adapter reject ON sources explicitly.

Public packet body handles are an unconditional boundary repair, translated
back to unchanged internal engine IDs for reporting. Historical recorded
report actions, state hashes and raw prompt bodies remain readable. An explicit
legacy packet projection supports historical analysis. Full model-facing
removal is implemented in temporal mode. Without it, the recorded body-handle
setting `report_body_handle_version = 1` changes the report opening alone: it
names the corpse by the public `body-{victim_id}` handle, which carries no death
tick, and a corpse missing from the state reads "a body". **With neither, opening
descriptions still contain the internal body ID and can expose its encoded death
tick.** Keeping those rendered bytes unchanged follows the default-OFF rule
pending an adopting decision; the packet repair alone does not establish
complete model privacy.

`eval/leak_scan.py` independently checks packet visibility, body identity,
audible entitlement and source-event claims. Planted tests cover invented,
missing, duplicated and misattributed evidence; runtime/reconstruction tests
cover temporal ordering and exact memory parity. Audio carries only the active
global alarm. The duplicate vent cue and its consumers are retired; unsupported
historical cues are refused. Spectator version 3 narrows this vocabulary and
explicitly reads version-2 payloads with compatible audio, including direct tick
requests. Frozen encoder versions keep the former cue's position as a reserved
zero so their weights and dimensions remain valid.

### Explicit temporal version 2

Temporal OFF and recorded version 1 retain their original projection, identifiers
and rendering. `AILIBI_TEMPORAL_OBSERVATIONS=2` selects the new ordered contract;
historical `true`/`1` selects version 1. Unknown or coerced version numbers fail.
A boolean can describe enabled status but does not replace an explicit version.
Evidence reasoning version 2 requires temporal version 2. Both remain experiments
without an adopting record.

A snapshot at tick T describes the state **before** that tick's actions. Version
2 snapshots carry their version and contain no action evidence. After the engine
resolves actions, `observation/temporal.py` folds the actual pre-state and ordered
events to project each recipient's entitled observations. Its inputs include the
actual submitted actions, so a resolved task attempt can be distinguished from
a discarded action or passive task continuation. Existing engine witness lists
continue serving version 1. Version 2 derives movement, kill and task
entitlement independently, and delivers a vent to exactly the engine event's
own witnesses, so it follows the recorded vent witness rule.

`EventObservationBatch.ordered_events` is authoritative in version 2. Each row
contains `observation_order`, `observer_before_event` (room and vent occupancy),
and a discriminated event payload. Order is dense **within one recipient and
source tick**; it reveals neither a hidden global event count nor another
recipient's ordering. It is not a simultaneous whole-tick view. The envelope
supports witnessed action, witnessed movement, own transition, own kill and own
task-attempt payloads. Own transitions locate the observer before a later action
in the same tick. An actor taking a visible departure through a public connecting
door entitles the atomic movement endpoint; only an observed movement supports
movement testimony. Vent evidence exposes the witnessed endpoint only. Event
witnesses must be alive and outside vents when the action occurs; death later in
the batch does not erase earlier observations or grant later ones.

An own task-attempt receipt includes map task ID, room and one of `progressed`,
`completed` or `rejected`. A rejection has no progress or completion. This is an
actor-private channel. Other observers receive only source-time task activity,
without task identity, ownership, rejection reason or a completion certificate.
A public `task_activity` account remains attributed speech even when the same
words happen to describe an actual receipt. Public assertions never rewrite the
listener's observed memory or become private task progress.

Version 2 episodic rows preserve explicit `source_tick`, `observation_phase`,
recipient-local `observation_order`, observer position and an opaque
`source_event_id`. Citation lookup matches retained observation IDs; it does not
parse an ID to infer timing. The recorded viewer separately identifies the scene
where delivery became available. Source time, delivery scene and public testimony
time serve different purposes.

Version 2 rendering states the snapshot/event distinction, preserves own event
transitions and renders separated sightings individually. It does not infer
watched arrivals, departures, companions or task completions from successive
snapshots. Death evidence separates last-alive observations, public dead-by
announcements and body discovery. Public death bounds exclude later co-presence
from murder-opportunity suspicion for that victim. Walking checks retain earlier
change intervals and explicitly condition public-placement comparisons on the
claim being accurate. A feasible route is neither proof of presence nor proof of
innocence; tick-only claims retain conservative phase uncertainty.

When the configured rules publicly regroup survivors, `public_regroup` records
the actual resume tick, public destination and living participants. It is public
knowledge, not a first-hand movement observation. The memory's meeting history
retains this boundary; walking checks do not accuse a player based on crossing
that relocation, and subsequent intervals start from the public destination.
Ordinary meetings do not suppress cross-meeting travel checks.

`eval/temporal_entitlement.py` independently compares every ordered channel,
position and local order with an event-local reconstruction. The snapshot gate
binds source tick, version and own position, and rejects action evidence on v2
snapshots. Separate legacy witness checks validate actual movement witness lists
without changing their producer. Planted missing/extra movement, forged endpoint,
wrong order/observer/tick, invented task activity and removed version controls
exercise these gates. Packet census format 2 includes checked event batches,
source-time kill/vent/movement views and actor task receipts, so temporal channels
are counted rather than disappearing from the census.

Spectator contract version 5 serves a spoken alibi as a route, over version 4's
`task_activity` observation/account union and attributed public statement
fields. The served route keeps the legs the speaker stated, and so do the
transcript and the listener render of the turn: the meeting layer labels an
account and never rewrites what was said. The contradiction detectors, the
scored metrics and the reported-testimony reduction read the same account as
MAXIMAL STAYS instead — contiguous legs naming one room merge into the stay
they restate — because where a speaker cuts one continuous stay is free, so no
flag, band, identifier, count or belief a listener holds may depend on it. A
merged stay is labelled with the smallest of the labels merged into it, so the
cut cannot choose the spelling a description quotes either. The reduction files
one reported statement per stay, so a listener's rendered memory is identical
for every narration of one account. Rendered alibi rows are capped per speaker
so no voice's volume evicts another's placement, and the belief block is not
budgeted, so a second cap bounds it: a subject's OWN rows and the rows other
players stated about that subject are selected in SEPARATE pools, three and
four, so the per-subject bound is seven and nothing an accused says — stays,
ticks, spelling, restatements — can change which of the other voices' rows a
listener sees, nor anything the others say change which of the accused's own
rows it sees. Selection never reads a room label above a total tie-break, so a
wording cannot move it either. The others pool is filled round-robin by recency
across speakers — every voice's newest row first, then every voice's
second-newest — so a voice is dropped only when more others than the pool have
named one subject, and then the stalest voices go first; below that, a voice
with several rows can lose its older rows to another voice's rows. Both numbers are
judgments about how much of a render reported testimony may take from the
elastic memory below it, not the largest values that still fit the budget. A
boundary that survives the merge is a declared room change or a gap, which is a
claim a listener can check. Compatible version-2/3/4 inputs retain their historical audio and event
interpretation; unsupported audio and versions still fail. Spectator knowledge remains privileged: a public account is labeled
as a speaker's claim even if the viewer can independently inspect engine truth.

## The regroup reset

The recorded `meeting_reset = hub_with_grace` regroups the survivors when a
meeting that did not end the game closes: every living player is placed in the
meeting room, every corpse is cleared, the vents are emptied and each living
impostor's kill cooldown restarts at its full value, six ticks in the shown set
(`kill_cooldown_ticks`) ([glossary](glossary.md#regroup-the-full-meeting-reset)).
Two rules keep what an agent perceives true to that relocation.

**The resume rule.** The first packets after a meeting are built from the
state play resumes in and from the trigger tick's events. After a regroup the
resume packet carries only the trigger tick's kills and vent entries and vent
exits: their witnesses were fixed where the event happened, so the relocation
cannot change who saw them. A trigger-tick walk or task step is dropped, because
its view is gated on the observer's current position, which the regroup has
moved to the meeting room. One helper composes the resume events for the live
loop and for every reader of a recording
(`orchestrator.replay.compose_resume_events`), and it reports the walks and task
steps it dropped. Without a regroup the resume packet carries the trigger tick's
events followed by the meeting's own, as it always has.

**The announced regroup.** The `public_regroup` row is written into every living
memory on the default evidence path as well as under evidence version 2, and
never under evidence version 1. Wherever the row exists the memory states the
regroup beside the meeting record and as its own step in the agent's route. On
the default evidence path it can also fold the sightings the regroup produced
(every other living player, in the meeting room) into one line, and does so only
when none of those sightings carries a movement note. A sighting carries one
when it is that player's latest sighting in the memory and the agent saw the
player in another room before it. So a player the agent saw elsewhere before
the meeting and not again after the regroup leaves every regroup sighting on its
own row, the note on that player's. Like any sighting row, the fold line can be
shed by the render's token budget. Evidence version 2 folds no sightings, so
each of those keeps its own row, as the sightings at the start of the game do.

A sighting on a regroup's tick or the tick after it is not evidence about
anyone's whereabouts. On every meeting profile but attributed testimony the
meeting layer neither corroborates nor prosecutes an alibi with it, and a
voter's own sighting there makes no ballot evidence row; it stays in the voter's
memory. That includes public accounts (`public_account_version`) without
attributed testimony, whose meetings keep the ordinary contradiction step
(`meetings.transcript.detect_contradictions`) and its window. Under attributed
testimony (`attributed_testimony_version`, alone or beside public accounts) the
contradiction step is the account detector
(`meetings.public_accounts.detect_public_account_conflicts`), which compares
spoken placements and reads no window, so it would flag a player the regroup
moved as an impossible walk. This is a stated limitation: the recorded settings
accept the reset beside either account profile and refuse neither. No committed
recording combines them, and the Stage-B record's settings include neither
account profile.
