# Observation entitlement and timing

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
removal is implemented only in temporal mode: **OFF opening descriptions still
contain the internal body ID and can expose its encoded death tick.** Keeping
those rendered bytes unchanged follows the default-OFF rule pending an adopting
decision; the packet repair alone does not establish complete model privacy.

`eval/leak_scan.py` independently checks packet visibility, body identity,
audible entitlement and source-event claims. Planted tests cover invented,
missing, duplicated and misattributed evidence; runtime/reconstruction tests
cover temporal ordering and exact memory parity. Audio carries only the active
global alarm. The duplicate vent cue and its consumers are retired; unsupported
historical cues are refused. Spectator version 3 narrows this vocabulary and
explicitly reads version-2 payloads with compatible audio, including direct tick
requests. Frozen encoder versions keep the former cue's position as a reserved
zero so their weights and dimensions remain valid.

## Explicit temporal version 2

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
continue serving version 1; version 2 derives entitlement independently.

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

Spectator contract version 4 admits the `task_activity` observation/account union
and attributed public statement fields. Compatible version-2/3 inputs retain
their historical audio and event interpretation; unsupported audio and versions
still fail. Spectator knowledge remains privileged: a public account is labeled
as a speaker's claim even if the viewer can independently inspect engine truth.
