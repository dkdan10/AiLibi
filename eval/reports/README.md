# Generated reports

The pages in this folder are written by scripts from the committed recordings,
with no model calls. Each one is regenerated, never edited by hand: change the
code or the recordings, run the script, and commit what it writes.

| Page | What it shows | Written by |
| --- | --- | --- |
| [process-scorecard.md](process-scorecard.md) | Nine measures of whether each vote rested on what the voter actually knew, per set and per [era](../../docs/glossary.md#era-recordings-that-share-one-recorded-identity) | `uv run python scripts/publish_process_scorecard.py` |
| [gameplay-census.md](gameplay-census.md) and [its JSON twin](gameplay-census.json) | Counts of what happened in the games themselves: sightings, vent trips, bodies, ballots and endings | `uv run python scripts/publish_gameplay_census.py` |
| [game-profile.md](game-profile.md) | The shape of each game in the shown 9-player set, sorted onto shelves | `uv run python scripts/publish_game_profile.py` |

Each script's `--check` flag recomputes its page and fails when the committed
copy has drifted; `scripts/check.sh` runs all three checks through the tests.
[process-scorecard-before.json](process-scorecard-before.json) is not generated:
it keeps the scorecard rows of recordings that were later replaced, copied once
and never recomputed.
