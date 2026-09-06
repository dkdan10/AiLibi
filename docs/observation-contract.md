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
