# Frozen baseline-8 exhibits

These files keep the tests named below reading real recorded meetings after
the baseline-9 re-record (`tasks/work/process-rerecord.md`) replaced every
committed recording. Each test asserts on a shape that the baseline-8 bytes
carried and the new bytes do not: the route claim and the labelling guards
removed the shape itself. Re-pointing these tests at a different committed meeting was
not possible, because no committed meeting has the shape. Deleting or relaxing
the assertions would have lost the property. So each exhibit is the baseline-8
recording, frozen here.

Every file comes from the committed `replays/samples/` sets at `main` commit
`39a568c6`, the last commit that held baseline 8. They are history, not the
current record. The live record stays in `replays/`, and nothing under this
directory is loaded, served or measured as a sample set.

| file | source at `39a568c6` | transform | read by | bytes | sha256 |
|---|---|---|---|---|---|
| `seed-41-meeting-2.jsonl` | `replays/samples/9p2i/replay-seed-41.jsonl`, the `headless-seed-41:meeting-2` line | none, the line verbatim | `tests/meetings/test_contradictions.py` (`TestTheAlibiIsARoute` and the honest-route sibling); `tests/api/test_evidence_mechanisms.py` (the flip search's loss statement) | 179,589 | `df2adfc848d1c535acd7ef20d866bf094323594eb993d44fb40eb209dd398e6a` |
| `alibi-conflict-meetings.jsonl` | the 17 `replays/samples/9p2i` meetings carrying a recorded `alibi_conflict` (21 flags), in seed order | `llm_calls` emptied | `tests/meetings/test_transcript.py` (the two-author conflict tripwire) | 162,390 | `8ce59029eb5e088b3ef14b07b8d820f8ace3e0dd0d91567c7f951c5f08458c52` |
| `legacy-one-room-alibi-meetings.jsonl` | all 190 meetings of `replays/samples/9p2i` then `replays/samples/4p1i`, in seed order, whose 292 alibi claims are all one-room claims | `llm_calls` emptied | `tests/meetings/test_reported_testimony_derive.py` (`TestRoutesOverTheCommittedRecord`) | 1,272,004 | `1e9b6e1356fd6d1c7a1189ca68e665cf073e3b5683d52b6eef1fe0fc4a737f62` |
| `rewritten-ballot-9p2i/replay-seed-11.jsonl` | `replays/samples/9p2i/replay-seed-11.jsonl` | none, the whole file | `tests/api/test_view_model.py` (the finale recap's rewritten-ballot case) | 346,358 | `75c859d09abb00e2035e218ed99a434e2ef1c51ef89172a5106b7a4d371a78ea` |
| `rewritten-ballot-9p2i/roster.json` | `replays/samples/9p2i/roster.json` | none | the same loader, which needs the 9p2i roster | 64 | `01ba485b9aed3cc7517a813afe919581861ccc1439c7249db0cbb06a84644340` |

Why each shape is gone on baseline 9:

- **Seed 41, meeting 2.** An honest crewmate stated a four-room walk as one room,
  and the envelope minted five flags against them. On baseline 9 the meeting
  has no recorded flag, and a search of all 676 committed meetings found no
  other meeting like it.
- **Two-author `alibi_conflict`.** The new `samples/9p2i` set carries no
  `alibi_conflict` flag at all.
- **One-room alibis.** All 1,021 baseline-9 alibi claims are routes
  (`claim_format` 2), so nothing committed exercises the legacy claim that
  the backward-compatibility tests read.
- **A rewritten ballot naming a player on a game's last meeting.** All 21
  baseline-9 target rewrites (8 `invalid_target`, 13 `teammate_coerced`)
  tally SKIP.

"`llm_calls` emptied" means the line was parsed, its `llm_calls` array was set
to `[]`, and the line was written back with the recorder's own serializer
(`orchestrator.replay._stable_json`). The tests read the transcript, the
ballots and the recorded flags, and none of them reads a model call. Each slim
line validates as a `MeetingReplayEntry` and serializes back to itself.

To rebuild all five files from git, byte for byte, run this from the repo root
with `PYTHONPATH=. uv run python`. It writes to the directory named on the
command line:

```python
import json, subprocess, sys
from pathlib import Path
from orchestrator.replay import _stable_json

BASE = "39a568c6"
out = Path(sys.argv[1])
(out / "rewritten-ballot-9p2i").mkdir(parents=True, exist_ok=True)


def blob(path: str) -> bytes:
    return subprocess.run(["git", "show", f"{BASE}:{path}"], check=True, capture_output=True).stdout


def meetings(set_name: str, seed: int) -> list[str]:
    text = blob(f"replays/samples/{set_name}/replay-seed-{seed}.jsonl").decode()
    return [line for line in text.splitlines() if json.loads(line)["kind"] == "meeting"]


def slim(line: str) -> str:
    return _stable_json({**json.loads(line), "llm_calls": []})


seed41 = [m for m in meetings("9p2i", 41) if json.loads(m)["meeting_id"].endswith(":meeting-2")]
(out / "seed-41-meeting-2.jsonl").write_text(seed41[0] + "\n", encoding="utf-8")
conflicts = [slim(m) for s in range(50) for m in meetings("9p2i", s)
             if any(f["kind"] == "alibi_conflict" for f in json.loads(m)["contradictions"])]
(out / "alibi-conflict-meetings.jsonl").write_text("\n".join(conflicts) + "\n", encoding="utf-8")
legacy = [slim(m) for n in ("9p2i", "4p1i") for s in range(50) for m in meetings(n, s)]
(out / "legacy-one-room-alibi-meetings.jsonl").write_text("\n".join(legacy) + "\n", encoding="utf-8")
for name in ("replay-seed-11.jsonl", "roster.json"):
    (out / "rewritten-ballot-9p2i" / name).write_bytes(blob(f"replays/samples/9p2i/{name}"))
```

Rebuilding these files from a later recording would defeat their purpose,
because a later recording no longer carries the shapes. If a detector or schema
change makes a test that reads them fail, the change is what needs a decision.
Record the failure and rule on it. Do not rebuild the exhibit to match.
