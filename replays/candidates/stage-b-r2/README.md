# Candidate round 2: the shown set's rules before the route lines

This round recorded the first 50 seeds of the 9-player sample roster (9 players,
2 impostors, 2 tasks per crewmate) once, with the seven switches the owner
adopted after round 1, the kept vent exit and a longer kill cooldown. The games
were played by the same model, prompt set and substrate as the sample sets:
`Qwen/Qwen3.6-27B` on featherless, the `qwen3_6_27b` prompts and every live
substrate toggle off.

These bytes were the shown 9-player set, `replays/samples/9p2i`, from
2026-10-02 until candidate round 3 replaced them. Round 3 recorded the same
seeds on the same rules with one more switch, the route lines, so this copy is
the comparison record that isolates that one change. Every file here is the
shown set's file as it was, moved without a byte changed.

It adopts nothing and is not a canonical sample set. The spectator and the
static demo never read this directory, and nothing here is published. The
round's reading is in its record, and the promotion that replaced it is in
round 3's record; both are listed in [the audits index](../../../audits/README.md)
under the Stage-B gameplay wave.

## The declaration

```candidate-declaration
0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b  experiment-config.json
9p2i seeds 0-49
```

## The switches it turns on

[`experiment-config.json`](experiment-config.json) sets nine fields off their
default. [The experiment arms page](../../../docs/experiment-arms.md) lists every
field and its values.

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

Everything else keeps its default: an impostor never opens a meeting, the
ballots carry no route lines, and the reasoning and account experiments stay
off.

## Files

- `experiment-config.json`: the declared config, one line.
- `9p2i/`: the 50 recordings, `MANIFEST.md` (one row per seed, all naming the
  one commit they were recorded at), `roster.json` and the eval report
  `tournament-eval-report.json.gz`, rebuilt from the recordings and never
  edited by hand.
