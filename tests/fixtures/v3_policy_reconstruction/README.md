# Frozen format-3 recording for the cross-tree policy check

`replay-seed-1.jsonl` exists so the version-3 policy reconstruction is exercised
against bytes a *different* process at a *different* commit produced. Every
other version-3 walk in the suite records and re-decides inside one process at
one commit, which can only attest self-consistency: the recorder and the checker
share the policy under test, so a policy regression moves both sides together
and the check stays green. These bytes do not move, so a later tree that decides
differently disagrees with them and
`tests/eval/test_v3_cross_tree_reconstruction.py` fails.

| Property | Value |
| --- | --- |
| Recorded from | `origin/main` at `201849fc`, before this card edited any source |
| Recorder | `orchestrator.game.HeadlessGame`, fake provider, no meeting runner |
| Seed / roster | seed 1, 7 players, 1 impostor, 1 task per crewmate |
| Budget | `TickScheduler(max_ticks=14)`; the run stops itself at tick 8 |
| Experiment | `format_version=3`, `evidence_reasoning_version=2`, `investigation_version=1` |
| Clock | `temporal_observation_version=2` |
| Content | 9 tick rows and one `game_stopped` row: 28 moves, 27 task attempts, 1 kill, 2 vents, 1 body report |
| sha256 | `543bf9cde342af39bb762c05e772f57054c1190b8b087c887679355c42fa3205` |

The recording is an interrupted prefix: no meeting runner was wired, so the game
stops when tick 8 enters `MEETING` and no meeting row follows. The walk profile
therefore truncates there, which is the recorded timeline, not a failure.

Regenerating it is a deliberate decision, not maintenance. A tactical-policy or
observation change that makes the check fail means exactly what the check is
for — the current tree no longer reproduces these decisions — so record the
divergence and decide, rather than re-recording the fixture to match.
