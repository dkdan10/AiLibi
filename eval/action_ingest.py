"""Per-tick action-by-role ingest (Task 10.16; audit 2026-06-13-1816 D-D-1).

The ONE new data path the Wave-2 indistinguishability metric needs. The
meeting-only eval model (:class:`eval.report_schema.TournamentReport`) carries
no per-tick action stream, so the "never-tasks" fingerprint
(:func:`eval.meeting_quality.compute_indistinguishability`) cannot be folded
from it. This module walks the committed per-tick replay rows
(:func:`orchestrator.replay.read_replay_entries` — the SAME tick records the
determinism gate reconstructs) and tallies every recorded action by the
ACTOR'S SEEDED ROLE.

**The seam (documented per the Task 10.16 contract).** Roles come from
:attr:`eval.report_schema.GameReport.roles`, which the loader fills from the
seeded game setup (:func:`orchestrator.seeder.seed_initial_state`), NEVER from
behaviour — the metric measures whether behaviour BETRAYS the seeded role, so
deriving the role from behaviour would be circular. The ``actor`` / ``type``
fields are read straight off the recorded action dicts; no engine re-run is
needed (the lighter option the contract names — the replay loader already
exposes the tick actions), and an action whose actor is absent from the game's
roles is a corrupt replay and fails loud (AGENTS.md "no silent fallbacks").

A tick row's ``actions`` is the SUBMITTED batch, which is not the same as what
the engine did: a meeting convened mid-batch ends the tick, and every
later-ordered action is recorded but never executed. The fingerprint measures
BEHAVIOUR, so a recording that says which those were
(``ReplayEntry.action_dispositions``) has them excluded and counted; a
recording that does not carry the field is tallied exactly as before, since an
absent field is not a claim that everything applied.

The replay file for a game is ``sample_dir / game.replay_ref`` (the bare
``replay-seed-{seed}.jsonl`` name the loader records), so the ingest is keyed
to the SAME games the report was built from.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from eval.meeting_quality import ActionRoleTally
from eval.report_schema import GameReport
from orchestrator.replay import read_replay_entries


@dataclass(frozen=True)
class ActionIngest:
    """One ingest pass: the role tally plus what it refused to count.

    ``discarded_excluded`` is the number of recorded actions the recording
    itself marks ``discarded_by_meeting`` and this pass therefore left out of
    ``tally``. It rides here rather than on
    :class:`eval.meeting_quality.ActionRoleTally` so the published tally model
    keeps its shape; 0 over every recording that carries no dispositions.
    """

    tally: ActionRoleTally
    discarded_excluded: int


def ingest_actions_by_role(
    sample_dir: Path, games: Sequence[GameReport]
) -> ActionIngest:
    """Tally executed per-tick actions by seeded role, reporting the exclusions.

    Reads each game's committed ``replay-seed-{seed}.jsonl`` under
    ``sample_dir`` and folds its tick rows into an
    :class:`~eval.meeting_quality.ActionRoleTally`, skipping every action the
    row marks ``discarded_by_meeting``. The only I/O in the Wave-2 metric path;
    deterministic over a fixed sample dir. See the module docstring for the
    role-from-seeder seam and the submitted-vs-executed one.
    """

    crewmate_counts: dict[str, int] = {}
    impostor_counts: dict[str, int] = {}
    per_game_player_wait_counts: list[tuple[int, ...]] = []
    discarded_excluded = 0

    for game in games:
        replay_path = sample_dir / game.replay_ref
        waits: dict[str, int] = {}
        for entry in read_replay_entries(replay_path):
            dispositions = entry.action_dispositions
            for index, action in enumerate(entry.actions):
                if dispositions is not None and (
                    dispositions[index] == "discarded_by_meeting"
                ):
                    discarded_excluded += 1
                    continue
                actor = action["actor"]
                if actor not in game.roles:
                    raise ValueError(
                        f"action actor {actor!r} in {replay_path} is absent from "
                        f"game {game.game_id!r} seeded roles; the action-by-role "
                        "tally cannot classify it, so this fails loud rather than "
                        "silently dropping or mis-attributing it."
                    )
                action_type = action["type"]
                counts = (
                    impostor_counts
                    if game.roles[actor] == "IMPOSTOR"
                    else crewmate_counts
                )
                counts[action_type] = counts.get(action_type, 0) + 1
                if action_type == "wait":
                    waits[actor] = waits.get(actor, 0) + 1
        per_game_player_wait_counts.append(tuple(waits.values()))

    return ActionIngest(
        tally=ActionRoleTally(
            crewmate_action_counts=crewmate_counts,
            impostor_action_counts=impostor_counts,
            per_game_player_wait_counts=tuple(per_game_player_wait_counts),
        ),
        discarded_excluded=discarded_excluded,
    )


def tally_actions_by_role(
    sample_dir: Path, games: Sequence[GameReport]
) -> ActionRoleTally:
    """The role tally alone, for callers that do not need the exclusion count.

    Delegates to :func:`ingest_actions_by_role`; identical folding.
    """

    return ingest_actions_by_role(sample_dir, games).tally
