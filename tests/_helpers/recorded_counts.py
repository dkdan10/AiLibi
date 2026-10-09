"""Count-only folds over a replay set's recorded rows, for pins derived at test time.

A literal transcribed from the shown set changes at every legitimate re-record and
proves no defect. A pin that holds an instrument's reading against the raw recorded
rows instead cross-checks two surfaces, and it survives a re-record. These folds
read the rows' structure only (row kinds, list lengths, ballot targets, outcome
labels, action types, flag kinds), never their text.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType


@dataclass(frozen=True)
class RecordedCounts:
    """What one set's recorded rows hold, counted straight off the files."""

    games: int
    tick_rows: int
    meetings: int
    turns: int
    ballots: int
    skip_ballots: int
    prompts: int
    outcomes: Mapping[str, int]
    actions: Mapping[str, int]
    applied_actions: Mapping[str, int]
    dispositions: Mapping[str, int]
    flag_kinds: Mapping[str, int]
    meetings_with_flag_kind: Mapping[str, int]

    @property
    def eject_ballots(self) -> int:
        """Ballots that name a player rather than SKIP."""

        return self.ballots - self.skip_ballots

    @property
    def ejections(self) -> int:
        """Meetings whose recorded outcome ejected a player."""

        return self.outcomes.get("EJECTED", 0)


def recorded_counts(set_dir: Path) -> RecordedCounts:
    """Fold every ``replay-seed-*.jsonl`` under ``set_dir`` into counts; an empty directory raises."""

    paths = sorted(set_dir.glob("replay-seed-*.jsonl"))
    if not paths:
        raise ValueError(f"{set_dir}: no replay-seed-*.jsonl recordings to count")
    tick_rows = meetings = turns = ballots = skip_ballots = prompts = 0
    outcomes: Counter[str] = Counter()
    actions: Counter[str] = Counter()
    applied_actions: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    flag_kinds: Counter[str] = Counter()
    meetings_with_flag_kind: Counter[str] = Counter()
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                kind = row.get("kind")
                if kind == "tick":
                    tick_rows += 1
                    actions.update(str(action["type"]) for action in row["actions"])
                    dispositions.update(str(d) for d in row["action_dispositions"])
                    applied_actions.update(
                        str(action["type"])
                        for action, disposition in zip(
                            row["actions"], row["action_dispositions"], strict=True
                        )
                        if disposition == "applied"
                    )
                elif kind == "meeting":
                    meetings += 1
                    turns += len(row["transcript"]["turns"])
                    ballots += len(row["ballots"])
                    skip_ballots += sum(
                        1 for ballot in row["ballots"] if ballot["target"] == "SKIP"
                    )
                    prompts += sum(1 for call in row["llm_calls"] if call.get("prompt"))
                    outcomes[str(row["outcome"])] += 1
                    kinds = [str(flag["kind"]) for flag in row["contradictions"]]
                    flag_kinds.update(kinds)
                    meetings_with_flag_kind.update(set(kinds))
    return RecordedCounts(
        games=len(paths),
        tick_rows=tick_rows,
        meetings=meetings,
        turns=turns,
        ballots=ballots,
        skip_ballots=skip_ballots,
        prompts=prompts,
        outcomes=MappingProxyType(dict(outcomes)),
        actions=MappingProxyType(dict(actions)),
        applied_actions=MappingProxyType(dict(applied_actions)),
        dispositions=MappingProxyType(dict(dispositions)),
        flag_kinds=MappingProxyType(dict(flag_kinds)),
        meetings_with_flag_kind=MappingProxyType(dict(meetings_with_flag_kind)),
    )
