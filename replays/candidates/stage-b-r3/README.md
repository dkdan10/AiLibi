# Candidate round 3: the route lines

This round records the first 50 seeds of the 9-player sample roster (9 players,
2 impostors, 2 tasks per crewmate) once more, on the rules of the shown set,
with one more switch: each voter's ballot carries a plain line about the places
stated at the table. In the shown set, players were sometimes voted out on a
charge that they could not have been in two rooms, when the station's doors or
the public regroup allowed that change of room. This round asks what changes
when every voter is told which stated changes of room are possible, with
nothing else moved. The games were played by the same model, prompt set and
substrate as the sample sets: `Qwen/Qwen3.6-27B` on featherless, the
`qwen3_6_27b` prompts and every live substrate toggle off.

It adopts nothing and is not a canonical sample set. The committed sample sets
and the first round keep their bytes, the spectator and the static demo never
read this directory, and nothing here is published. The reading of the round,
and the next step it names, are in its record, listed in
[the audits index](../../../audits/README.md) under the Stage-B gameplay wave.

## The declaration

```candidate-declaration
a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d  experiment-config.json
9p2i seeds 0-49
```

## The one change

[`experiment-config.json`](experiment-config.json) sets ten fields off their
default: the nine of the shown set, and one more.

| field | value | in plain words |
| --- | --- | --- |
| `route_lines_version` | `1` | Each ballot carries one line for each player whose places stated at the table change room in a way the station's doors allow in the ticks between, or with the public regroup between them; the line lists each such change and how many doors it crosses. It is the same for every role, and it names, ranks and recommends no one. |

## The switches it keeps

These carry over from the shown set unchanged: the seven switches the owner
adopted, the kept vent exit and the longer kill cooldown.
[The experiment arms page](../../../docs/experiment-arms.md) lists every field
and its values.

| field | value | in plain words |
| --- | --- | --- |
| `vent_witness_rule` | `physical` | A vent exit into another room is seen only by the players in the room the impostor comes out in, not by those in the room it left. |
| `vent_exit_policy` | `look_and_wait` | An impostor inside a vent comes out only when it can see no one but its teammates in its vent room and the neighbouring rooms it can see, and otherwise waits, until the in-vent limit makes it come out. |
| `vent_entry_policy` | `own_fresh_kill` | An impostor enters a vent only beside a body that is its own recent victim, with no meeting since the kill. |
| `meeting_reset` | `hub_with_grace` | When a meeting ends, the living players gather in the meeting room, the bodies are cleared, the vents are emptied, and each impostor has to wait out the full kill cooldown again. |
| `bounded_rebuttal_version` | `1` | The player named by the earliest new accusation in a meeting gets one reply, whoever that player is. |
| `report_body_handle_version` | `1` | A body report names the body by the victim alone, without the moment of the kill. |
| `ballot_kill_row_version` | `1` | A player who watched a kill sees it on its ballot as its own evidence, and nobody else learns of it that way. |
| `impostor_ballot_version` | `1` | An impostor's ballot is framed as a move for its side: it may name a crewmate it can point to with a line it holds, never a teammate, and otherwise skips. |
| `kill_cooldown_ticks` | `6` | After a kill, at the start of play and after every meeting, an impostor waits six ticks before it may kill again, where the map's own wait is four. |

Everything else keeps its default: an impostor never opens a meeting, and the
reasoning and account experiments stay off.

## Files

- `experiment-config.json`: the declared config, one line.
- `9p2i/`: the 50 recordings, `MANIFEST.md` (one row per seed, all naming the
  one commit they were recorded at), `roster.json` and the eval report
  `tournament-eval-report.json.gz`, rebuilt from the recordings and never
  edited by hand.
