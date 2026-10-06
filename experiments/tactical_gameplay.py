"""Source-bound offline tactical comparisons; no live providers or adoption.

Run ``python -m experiments.tactical_gameplay --output PATH --split development``.
Committed recordings establish historical mechanism counts. Fresh paired games
use an injected deterministic fake, so their outcomes do not measure model skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import statistics
import time
import tempfile
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

from pydantic import BaseModel, ConfigDict, TypeAdapter

from agents.tactical.experimental import FRESH_KILL_WINDOW_TICKS, IN_VENT_CAP_TICKS
from engine.actions import Action
from engine.events import (
    EngineEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.tick import _apply_action
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.balance_eval import _CURRENT_REPORT_WALK_CONFIG
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkConfig,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    walk_replay,
)
from llm.budget import GameBudget
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from orchestrator.experiment_config import (
    ConfigLayer,
    RecordedExperimentConfig,
    engine_arguments,
)
from orchestrator.action_ordering import order_actions_for_tick
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.recording_fingerprint import recording_fingerprint
from orchestrator.replay import (
    classify_action_dispositions,
    compute_cost_usd,
    read_all_entries,
    recorded_experiment_config,
    require_baseline_experiments,
)
from orchestrator.run_limits import RunDeadline
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state


class Roster(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


class GameMetrics(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    seed: int
    roster: Roster
    counts: dict[str, int]
    maximum_finished_wait_ticks: int
    completion_status: str
    winner: str | None
    reason: str | None
    replay_sha256: str
    trajectory_sha256: str
    reported_cost_usd: float
    input_tokens: int = 0
    output_tokens: int = 0
    model_calls: int = 0
    error: str | None = None


#: The lab's walk profiles read Stage-B settings in these layers besides the
#: engine's. Their consumers count recorded actions, engine events and applied
#: meeting results, each checked against the recorded hashes, and re-decide
#: nothing, so a count keeps its meaning under any value of a field in these
#: layers. Declared here, never inherited from the current-report profile.
LAB_THREADED_LAYERS: Final[frozenset[ConfigLayer]] = frozenset(
    {"orchestrator", "tactical", "meeting"}
)

#: :func:`measure_identity_effects`' walk. That consumer also refuses every
#: experimental recording before it walks (``require_baseline_experiments``).
SEAT_EFFECTS_WALK_CONFIG: Final[ReplayWalkConfig] = replace(
    _CURRENT_REPORT_WALK_CONFIG,
    profile="tactical-seat-effects",
    threaded_layers=LAB_THREADED_LAYERS,
)

#: :func:`measure_replay`'s walk.
MECHANISMS_WALK_CONFIG: Final[ReplayWalkConfig] = replace(
    _CURRENT_REPORT_WALK_CONFIG,
    profile="tactical-mechanisms",
    threaded_layers=LAB_THREADED_LAYERS,
)

#: The round-1 config's fields that act during a fake game's play. Its
#: rebuttal and ballot fields change only a meeting's turns and prompts, and a
#: fake meeting ejects nobody, so the lab leaves them out; the body handle is
#: left out with them.
STAGE_B_FULL_SETTINGS: Final[Mapping[str, object]] = MappingProxyType(
    {
        "vent_witness_rule": "physical",
        "vent_exit_policy": "look_and_wait",
        "vent_entry_policy": "own_fresh_kill",
        "meeting_reset": "hub_with_grace",
    }
)

#: Each attribution arm, named after the recorded value it drops, and the one
#: field it sets back to its default.
STAGE_B_MINUS_ONE: Final[Mapping[str, str]] = MappingProxyType(
    {
        "stage_b_full_minus_look_and_wait": "vent_exit_policy",
        "stage_b_full_minus_own_fresh_kill": "vent_entry_policy",
        "stage_b_full_minus_physical": "vent_witness_rule",
        "stage_b_full_minus_hub_with_grace": "meeting_reset",
    }
)

#: The kill-cooldown dial: each arm is the full Stage-B arm with the recorded
#: cooldown set; ``stage_b_full`` is the map's own value, 4.
STAGE_B_KILL_COOLDOWNS: Final[Mapping[str, int]] = MappingProxyType(
    {
        "stage_b_full_kill_cooldown_6": 6,
        "stage_b_full_kill_cooldown_8": 8,
    }
)

#: The idle-policy cross. Each arm is the reference arm, the full Stage-B arm
#: at kill cooldown 6, with the finished crew's idle policy set; the reference
#: itself, at the default ``hub_wait``, is the cross's third column.
STAGE_B_IDLE_REFERENCE: Final[str] = "stage_b_full_kill_cooldown_6"
STAGE_B_IDLE_POLICIES: Final[Mapping[str, str]] = MappingProxyType(
    {
        "stage_b_full_kill_cooldown_6_patrol": "patrol",
        "stage_b_full_kill_cooldown_6_accompany": "accompany",
    }
)

#: Each split's seeds, the same on both rosters. ``development_wide`` begins
#: with ``development`` and stays below the held-out seeds.
SPLIT_SEEDS: Final[Mapping[str, tuple[int, ...]]] = MappingProxyType(
    {
        "development": tuple(range(1000, 1008)),
        "held_out": tuple(range(2000, 2016)),
        "development_wide": tuple(range(1000, 1100)),
    }
)

#: The role-blind whereabouts counts :func:`fold_whereabouts` adds to a row.
WHEREABOUTS_COUNTS: Final[tuple[str, ...]] = (
    "whereabouts_subjects_at_kill_ticks",
    "whereabouts_covered_at_kill_ticks",
    "whereabouts_subjects_at_play_ticks",
    "whereabouts_covered_at_play_ticks",
)

#: The kill-witness counts :func:`fold_kill_witnesses` adds to a row.
KILL_WITNESS_COUNTS: Final[tuple[str, ...]] = (
    "crew_kill_witnesses",
    "crew_kill_witnesses_walked_in",
    "kills_with_walk_in_crew_witness",
)


def candidate_configs() -> dict[str, RecordedExperimentConfig]:
    """Predeclared comparisons; no automatic promotion of an arm.

    One-change arms, the Stage-B arm that sets every round-1 field acting
    during play, one attribution arm per such field, which drops it, and the
    Stage-B arm at each kill cooldown of the dial, and the idle-policy cross
    over the reference arm.
    """

    configs = {
        "baseline": RecordedExperimentConfig(),
        "workload": RecordedExperimentConfig(
            redistribution_policy="least_remaining_work"
        ),
        "patrol": RecordedExperimentConfig(crew_idle_policy="patrol"),
        "accompany": RecordedExperimentConfig(crew_idle_policy="accompany"),
        "vent_risk": RecordedExperimentConfig(vent_exit_policy="observed_risk"),
        "post_meeting": RecordedExperimentConfig(post_meeting_retarget=True),
        "meeting_reset": RecordedExperimentConfig(meeting_reset="hub_with_grace"),
        "self_report": RecordedExperimentConfig(self_report=True),
        "earlier_sabotage": RecordedExperimentConfig(sabotage_threshold="two_thirds"),
        "vent_physical": RecordedExperimentConfig(vent_witness_rule="physical"),
        "vent_look_and_wait": RecordedExperimentConfig(
            vent_exit_policy="look_and_wait"
        ),
        "vent_own_fresh_kill": RecordedExperimentConfig(
            vent_entry_policy="own_fresh_kill"
        ),
        "stage_b_full": RecordedExperimentConfig.model_validate(
            dict(STAGE_B_FULL_SETTINGS)
        ),
    }
    for name, field in STAGE_B_MINUS_ONE.items():
        configs[name] = RecordedExperimentConfig.model_validate(
            {
                **STAGE_B_FULL_SETTINGS,
                field: RecordedExperimentConfig.model_fields[field].default,
            }
        )
    for name, ticks in STAGE_B_KILL_COOLDOWNS.items():
        configs[name] = RecordedExperimentConfig.model_validate(
            {**STAGE_B_FULL_SETTINGS, "kill_cooldown_ticks": ticks}
        )
    for name, policy in STAGE_B_IDLE_POLICIES.items():
        configs[name] = RecordedExperimentConfig.model_validate(
            {
                **configs[STAGE_B_IDLE_REFERENCE].model_dump(),
                "crew_idle_policy": policy,
            }
        )
    return configs


def ticks_to_parity(arms: Mapping[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """Count-only: per arm and roster, how long the impostors took to reach parity.

    ``arms`` is the comparison's ``arms`` block. For each arm and roster: the
    games, the games the impostors won by parity, the minimum, median and
    maximum ``tick_rows`` of those parity games (a game's tick rows are its
    game-over tick plus one; ``None`` with no parity game), and the kills over
    every game.
    """

    summary: dict[str, dict[str, dict[str, Any]]] = {}
    for arm, entry in arms.items():
        for roster, rows in entry["sets"].items():
            parity = [
                row["counts"]["tick_rows"]
                for row in rows
                if row["reason"] == "IMPOSTOR_PARITY"
            ]
            summary.setdefault(arm, {})[roster] = {
                "games": len(rows),
                "parity_games": len(parity),
                "parity_tick_rows_minimum": min(parity) if parity else None,
                "parity_tick_rows_median": statistics.median(parity)
                if parity
                else None,
                "parity_tick_rows_maximum": max(parity) if parity else None,
                "kills": sum(row["counts"].get("event:Killed", 0) for row in rows),
            }
    return summary


def _share(counts: Mapping[str, int], scope: str) -> tuple[int, int]:
    """(covered, subjects) of one row over ``kill_ticks`` or ``play_ticks``."""

    return (
        counts[f"whereabouts_covered_at_{scope}"],
        counts[f"whereabouts_subjects_at_{scope}"],
    )


def whereabouts_coverage_summary(
    arms: Mapping[str, Any],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Count-only: per arm and roster, the role-blind whereabouts coverage.

    ``arms`` is the comparison's ``arms`` block. For each arm and roster: the
    games, the kills, the four coverage sums, the games without a kill tick, and
    the minimum, median and maximum of one game's covered share at kill ticks
    over the games with a kill tick (``None`` with none). A game has a kill tick
    exactly when it has a subject at one.
    """

    summary: dict[str, dict[str, dict[str, Any]]] = {}
    for arm, entry in arms.items():
        for roster, rows in entry["sets"].items():
            shares = [
                covered / subjects
                for covered, subjects in (
                    _share(row["counts"], "kill_ticks") for row in rows
                )
                if subjects
            ]
            summary.setdefault(arm, {})[roster] = {
                "games": len(rows),
                "kills": sum(row["counts"].get("event:Killed", 0) for row in rows),
                **{
                    key: sum(row["counts"][key] for row in rows)
                    for key in WHEREABOUTS_COUNTS
                },
                "games_without_a_kill_tick": len(rows) - len(shares),
                "kill_tick_share_minimum": min(shares) if shares else None,
                "kill_tick_share_median": statistics.median(shares) if shares else None,
                "kill_tick_share_maximum": max(shares) if shares else None,
            }
    return summary


def _compare_shares(
    arm: Mapping[str, int], reference: Mapping[str, int], scope: str
) -> int:
    """1, 0 or -1 as the arm's covered share is higher, equal or lower; exact."""

    arm_covered, arm_subjects = _share(arm, scope)
    reference_covered, reference_subjects = _share(reference, scope)
    if not arm_subjects or not reference_subjects:
        raise ValueError(f"a game without a subject at {scope} has no share")
    left = arm_covered * reference_subjects
    right = reference_covered * arm_subjects
    return (left > right) - (left < right)


def idle_policy_pairs(arms: Mapping[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """Count-only: each idle-policy arm against the reference arm, seed by seed.

    Only a cross arm whose reference ran in the same comparison is paired. Per
    roster: the seeds, the seeds where both games have a kill tick and, among
    them, where the arm's kill-tick share is higher, equal or lower; then the
    same three over play ticks for every seed. Paired games share a seed and
    diverge after their first differing decision.
    """

    pairs: dict[str, dict[str, dict[str, Any]]] = {}
    if STAGE_B_IDLE_REFERENCE not in arms:
        return pairs
    reference_sets = arms[STAGE_B_IDLE_REFERENCE]["sets"]
    for arm in STAGE_B_IDLE_POLICIES:
        if arm not in arms:
            continue
        for roster, rows in arms[arm]["sets"].items():
            mine = {row["seed"]: row["counts"] for row in rows}
            theirs = {row["seed"]: row["counts"] for row in reference_sets[roster]}
            if set(mine) != set(theirs):
                raise ValueError(f"{arm} and its reference ran different seeds")
            both = [
                seed
                for seed in sorted(mine)
                if _share(mine[seed], "kill_ticks")[1]
                and _share(theirs[seed], "kill_ticks")[1]
            ]
            kill = [
                _compare_shares(mine[seed], theirs[seed], "kill_ticks") for seed in both
            ]
            play = [
                _compare_shares(mine[seed], theirs[seed], "play_ticks")
                for seed in sorted(mine)
            ]
            pairs.setdefault(arm, {})[roster] = {
                "reference": STAGE_B_IDLE_REFERENCE,
                "seeds": len(mine),
                "seeds_with_a_kill_tick_in_both": len(both),
                "kill_tick_share_higher": kill.count(1),
                "kill_tick_share_equal": kill.count(0),
                "kill_tick_share_lower": kill.count(-1),
                "play_tick_share_higher": play.count(1),
                "play_tick_share_equal": play.count(0),
                "play_tick_share_lower": play.count(-1),
            }
    return pairs


def entry_after_own_fresh_kill(
    entry: VentEnteredEvent,
    *,
    kills: Sequence[KilledEvent],
    meeting_ticks: Sequence[int],
) -> bool:
    """Whether a vent entry follows the entering impostor's own fresh kill.

    The census's definition: a kill by the same impostor in the room it entered
    from, at most :data:`FRESH_KILL_WINDOW_TICKS` ticks before the entry, with no
    meeting opened at or after the kill and before the entry.
    """

    return any(
        kill.actor == entry.actor
        and kill.room == entry.source_room
        and entry.tick - FRESH_KILL_WINDOW_TICKS <= kill.tick < entry.tick
        and not any(kill.tick <= tick < entry.tick for tick in meeting_ticks)
        for kill in kills
    )


def living_player_in_vent(state: WorldState) -> bool:
    """Whether a living player is inside a vent; only an impostor can be."""

    return any(player.alive and player.in_vent for player in state.players.values())


def whereabouts_coverage(state: WorldState) -> tuple[int, int]:
    """(subjects, covered subjects) in one state; no role is read.

    Every living player is a subject. A subject is covered when it is not inside
    a vent and at least one other living player outside a vent stands in its
    room: the engine's kill-witness rule (``engine.rules._witnesses_in_room``)
    applied to every player, and the same-room sight every observer holds in
    every visibility mode. It counts positions, not what anyone noticed.

    It bounds one thing: on the canonical map a crewmate sees only its own
    room, so every player a crewmate sees in this state is covered. It bounds
    nothing an impostor sees, since an impostor also sees the adjacent rooms at
    base sight and still sees from inside a vent, and nothing a player holds
    from earlier ticks, from a departure it watched or from speech.
    """

    standing = Counter(
        player.room
        for player in state.players.values()
        if player.alive and not player.in_vent
    )
    subjects = sum(player.alive for player in state.players.values())
    covered = sum(count for count in standing.values() if count > 1)
    return subjects, covered


def fold_whereabouts(step: TickAdvanced, counts: Counter[str]) -> None:
    """Add one play tick's coverage, read from the state the tick leaves.

    Every play tick adds to the play-tick pair. A kill tick, a play tick with at
    least one ``Killed`` event, adds the same once to the kill-tick pair however
    many kills it holds; its killer is a living subject, so it has at least one.
    """

    subjects, covered = whereabouts_coverage(step.state)
    counts["whereabouts_subjects_at_play_ticks"] += subjects
    counts["whereabouts_covered_at_play_ticks"] += covered
    if any(isinstance(event, KilledEvent) for event in step.events):
        counts["whereabouts_subjects_at_kill_ticks"] += subjects
        counts["whereabouts_covered_at_kill_ticks"] += covered


def _arrivals(events: Sequence[EngineEvent]) -> set[tuple[str, str]]:
    """(player, room) for each move a tick made from another room into that room."""

    return {
        (event.actor, event.to_room)
        for event in events
        if isinstance(event, MovedEvent) and event.from_room != event.to_room
    }


def fold_kill_witnesses(step: TickAdvanced, counts: Counter[str]) -> None:
    """Per kill: its crew witnesses, those who walked in, and whether any did.

    A witness is one the engine recorded on the ``Killed`` event; the role is
    read as ``kills_crew_witnessed`` reads it. A witness walked in when it moved
    from another room into the kill's room on the kill tick. The engine applies
    a tick's actions in order and reads the witnesses when the kill applies, so
    such a witness arrived before the kill.
    """

    arrivals = _arrivals(step.events)
    for event in step.events:
        if not isinstance(event, KilledEvent):
            continue
        crew = [
            pid
            for pid in event.witnesses
            if step.pre_state.players[pid].role == "CREWMATE"
        ]
        walked_in = [pid for pid in crew if (pid, event.room) in arrivals]
        counts["crew_kill_witnesses"] += len(crew)
        counts["crew_kill_witnesses_walked_in"] += len(walked_in)
        counts["kills_with_walk_in_crew_witness"] += bool(walked_in)


def _remaining_work(state: WorldState, owner: str) -> int:
    return sum(
        task.required_ticks - task.progress
        for task in state.tasks.values()
        if task.owner == owner and not task.completed
    )


def permute_state_and_actions(
    state: WorldState,
    actions: Sequence[Action],
    permutation: Mapping[str, str],
) -> tuple[WorldState, tuple[Action, ...]]:
    """Relabel one genuine transition while keeping roles and intentions attached.

    Existing body handles and map task identifiers stay opaque. Composite task
    instance keys, every player reference and prior action are remapped together.
    This is an unrecorded intervention on action ordering, not a reseeded game.
    """

    roster = set(state.players)
    if set(permutation) != roster or set(permutation.values()) != roster:
        raise ValueError("identity permutation must be a bijection of the whole roster")

    def action_with_new_ids(action: Action) -> Action:
        raw = action.model_dump(mode="json")
        raw["actor"] = permutation[action.actor]
        if action.type == "kill":
            raw["payload"]["target"] = permutation[action.payload.target]
        return TypeAdapter(Action).validate_python(raw)

    players = {
        permutation[pid]: replace(
            player,
            id=permutation[pid],
            last_action=None
            if player.last_action is None
            else action_with_new_ids(player.last_action),
        )
        for pid, player in state.players.items()
    }
    bodies = {
        key: replace(
            body,
            player_id=permutation[body.player_id],
            killed_by=permutation[body.killed_by],
            discovered_by=None
            if body.discovered_by is None
            else permutation[body.discovered_by],
        )
        for key, body in state.bodies.items()
    }
    tasks = {
        f"{permutation[task.owner]}:{task.map_task_id}": replace(
            task,
            id=f"{permutation[task.owner]}:{task.map_task_id}",
            owner=permutation[task.owner],
        )
        for task in state.tasks.values()
    }
    renamed = replace(
        state,
        players=players,
        bodies=bodies,
        tasks=tasks,
        cooldowns={permutation[pid]: value for pid, value in state.cooldowns.items()},
        emergency_uses={
            permutation[pid]: value for pid, value in state.emergency_uses.items()
        },
    )
    reordered = order_actions_for_tick(
        [action_with_new_ids(action) for action in actions]
    )
    return renamed, tuple(reordered)


def measure_identity_effects(
    path: Path, *, seed: int, roster: Roster
) -> dict[str, int]:
    """Compare two fixed relabellings per recorded transition; never rescore speech."""

    entries = read_all_entries(path)
    require_baseline_experiments(
        entries, consumer="recorded baseline identity intervention"
    )
    engine = engine_arguments(recorded_experiment_config(entries))
    counts: Counter[str] = Counter()
    game_map = load_canonical_map()
    adapter: TypeAdapter[Action] = TypeAdapter(Action)
    for step in walk_replay(
        path,
        seed=seed,
        game_map=game_map,
        config=SEAT_EFFECTS_WALK_CONFIG,
        **roster.model_dump(),
    ):
        if not isinstance(step, TickAdvanced):
            continue
        actions = tuple(adapter.validate_python(raw) for raw in step.entry.actions)
        original = dict(
            zip(
                (action.actor for action in actions),
                classify_action_dispositions(actions, step.events),
                strict=True,
            )
        )
        ids = sorted(step.pre_state.players)
        for label, shifted in (
            ("rotate", ids[1:] + ids[:1]),
            ("reverse", list(reversed(ids))),
        ):
            permutation = dict(zip(ids, shifted, strict=True))
            renamed, reordered = permute_state_and_actions(
                step.pre_state, actions, permutation
            )
            after, events = advance_tick(
                renamed, reordered, game_map=game_map, **engine
            )
            actual = dict(
                zip(
                    (action.actor for action in reordered),
                    classify_action_dispositions(reordered, events),
                    strict=True,
                )
            )
            changed = False
            counts[f"{label}:transitions"] += 1
            for pid, disposition in original.items():
                new_disposition = actual[permutation[pid]]
                role = step.pre_state.players[pid].role
                counts[f"{label}:decisions:{role}"] += 1
                if new_disposition != disposition:
                    changed = True
                    counts[
                        f"{label}:changed:{role}:{disposition}_to_{new_disposition}"
                    ] += 1
            counts[f"{label}:transitions_with_disposition_changes"] += changed
            counts[f"{label}:transitions_with_phase_changes"] += (
                after.phase != step.state.phase
            )
            inverse = {
                renamed_id: original_id
                for original_id, renamed_id in permutation.items()
            }
            restored_after, _ = permute_state_and_actions(after, (), inverse)
            counts[f"{label}:transitions_with_task_state_changes"] += (
                restored_after.tasks != step.state.tasks
            )
            counts[f"{label}:transitions_with_survival_changes"] += any(
                after.players[permutation[pid]].alive != player.alive
                for pid, player in step.state.players.items()
            )
    return dict(sorted(counts.items()))


def _transfers(
    before: WorldState, after: WorldState, victim: str, counts: Counter[str]
) -> None:
    surviving = {
        key: task
        for key, task in before.tasks.items()
        if not (task.owner == victim and not task.completed)
    }
    crew = sorted(
        pid
        for pid, player in after.players.items()
        if player.alive and player.role == "CREWMATE"
    )
    for task in before.tasks.values():
        if task.owner != victim or task.completed:
            continue
        counts["death_incomplete_instances"] += 1
        eligible = [pid for pid in crew if f"{pid}:{task.map_task_id}" not in surviving]
        copies = [
            item
            for key, item in after.tasks.items()
            if key not in surviving and item.map_task_id == task.map_task_id
        ]
        if not copies:
            counts["dropped_incomplete_instances"] += 1
            counts["dropped_with_eligible_recipient"] += bool(eligible)
            continue
        if len(copies) != 1:
            raise ValueError("task transfer did not preserve a single instance")
        copied = copies[0]
        if copied.owner not in eligible or (copied.progress, copied.required_ticks) != (
            task.progress,
            task.required_ticks,
        ):
            raise ValueError(
                "task transfer changed progress or used an ineligible recipient"
            )
        work = {
            pid: sum(
                item.required_ticks - item.progress
                for item in surviving.values()
                if item.owner == pid and not item.completed
            )
            for pid in eligible
        }
        counts["redistributed_instances"] += 1
        counts[f"redistribution_recipient:{copied.owner}"] += 1
        counts["redistributed_remaining_work"] += (
            copied.required_ticks - copied.progress
        )
        counts["redistributions_to_above_minimum_work"] += work[copied.owner] > min(
            work.values()
        )
        surviving[copied.id] = copied


def measure_replay(path: Path, *, seed: int, roster: Roster) -> GameMetrics:
    """Fold verified transitions, retaining unfinished status and raw spending."""

    from orchestrator.replay import (
        AbortedMeetingReplayEntry,
        FailedCallReplayEntry,
        GameEndReplayEntry,
        MeetingReplayEntry,
        ReplayEntry,
        read_all_entries,
        recorded_completion_status,
        recorded_experiment_config,
    )

    entries = read_all_entries(path)
    trajectory = [
        {
            "kind": entry.kind,
            "tick": entry.tick,
            "actions": entry.actions,
            "state_hash": entry.state_hash,
        }
        if isinstance(entry, ReplayEntry)
        else {
            "kind": entry.kind,
            "tick": entry.tick,
            "state_hash_after": entry.state_hash_after,
        }
        if isinstance(entry, MeetingReplayEntry)
        else {
            "kind": entry.kind,
            "tick": entry.tick,
            "winner": entry.winner,
            "reason": entry.reason,
        }
        for entry in entries
        if isinstance(entry, (ReplayEntry, MeetingReplayEntry, GameEndReplayEntry))
    ]
    calls = [
        call
        for entry in entries
        if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry))
        for call in entry.llm_calls
    ]
    failures = [entry for entry in entries if isinstance(entry, FailedCallReplayEntry)]
    engine = engine_arguments(recorded_experiment_config(entries))
    game_map = load_canonical_map()
    adapter: TypeAdapter[Action] = TypeAdapter(Action)
    # The role-blind and kill-witness counts are present in every row, zero
    # included.
    counts: Counter[str] = Counter(
        dict.fromkeys(WHEREABOUTS_COUNTS + KILL_WITNESS_COUNTS, 0)
    )
    last_move: dict[str, tuple[int, str, str]] = {}
    last_wait: dict[str, tuple[int, int]] = {}
    max_wait = 0
    death_ticks: dict[str, int] = {}
    meeting_state: WorldState | None = None
    winner: str | None = None
    reason: str | None = None
    # Vent trips: each open trip's anchor tick (its entry, or the last meeting
    # opened since), the kills so far and the meeting ticks, for the census's
    # ticks-inside and own-fresh-kill definitions. A trip a meeting ends without
    # an exit leaves its anchor behind until that impostor's next entry replaces
    # it; only an exit reads an anchor.
    vent_anchor: dict[str, int] = {}
    kills: list[KilledEvent] = []
    meeting_ticks: list[int] = []
    for step in walk_replay(
        path,
        seed=seed,
        game_map=game_map,
        config=MECHANISMS_WALK_CONFIG,
        **roster.model_dump(),
    ):
        if isinstance(step, TickOpened):
            counts["tick_rows"] += 1
            if counts["tick_rows"] == 1:
                workloads = [
                    _remaining_work(step.state, pid)
                    for pid, player in step.state.players.items()
                    if player.role == "CREWMATE" and player.alive
                ]
                counts["initial_crew_work_minimum"] = min(workloads)
                counts["initial_crew_work_maximum"] = max(workloads)
                counts["initial_crew_work_total"] = sum(workloads)
            completed = sum(task.completed for task in step.state.tasks.values())
            total = len(step.state.tasks)
            for raw in step.entry.actions:
                actor = raw["actor"]
                role = step.state.players[actor].role
                counts[f"decisions:{role}"] += 1
                counts[f"submitted:{role}:{raw['type']}"] += 1
                if role == "IMPOSTOR" and 0 < total and completed < total:
                    counts["impostor_decisions_at_six_sevenths"] += (
                        completed * 7 >= total * 6
                    )
                    counts["impostor_decisions_at_two_thirds"] += (
                        completed * 3 >= total * 2
                    )
                if role == "CREWMATE" and _remaining_work(step.state, actor) == 0:
                    counts["finished_crew_decision_slots"] += 1
        elif isinstance(step, TickAdvanced):
            fold_whereabouts(step, counts)
            fold_kill_witnesses(step, counts)
            actions = tuple(adapter.validate_python(raw) for raw in step.entry.actions)
            dispositions = classify_action_dispositions(actions, step.events)
            working = step.pre_state
            for action, disposition in zip(actions, dispositions, strict=True):
                role = step.pre_state.players[action.actor].role
                counts[f"{disposition}:{role}:{action.type}"] += 1
                if disposition != "applied":
                    continue
                after, event = _apply_action(working, game_map, action, **engine)
                if isinstance(event, KilledEvent):
                    _transfers(working, after, event.target, counts)
                working = after
                # Only an impostor is ever inside a vent.
                if (
                    action.type == "wait"
                    and step.pre_state.players[action.actor].in_vent
                ):
                    counts["impostor_in_vent_waits"] += 1
                if (
                    role == "CREWMATE"
                    and action.type == "wait"
                    and _remaining_work(step.pre_state, action.actor) == 0
                ):
                    counts["finished_crew_applied_waits"] += 1
                    old_tick, length = last_wait.get(action.actor, (-2, 0))
                    length = length + 1 if old_tick == step.entry.tick - 1 else 1
                    last_wait[action.actor] = (step.entry.tick, length)
                    max_wait = max(max_wait, length)
                    if (
                        step.pre_state.players[action.actor].room
                        == game_map.meeting.room
                    ):
                        counts["finished_crew_applied_waits_at_hub"] += 1
            moves_this_tick: set[str] = set()
            for event in step.events:
                counts[f"event:{event.type}"] += 1
                if isinstance(event, MovedEvent):
                    role = step.pre_state.players[event.actor].role
                    moves_this_tick.add(event.actor)
                    previous = last_move.get(event.actor)
                    if previous == (
                        step.entry.tick - 1,
                        event.to_room,
                        event.from_room,
                    ):
                        counts[f"move_reversals:{role}"] += 1
                    last_move[event.actor] = (
                        step.entry.tick,
                        event.from_room,
                        event.to_room,
                    )
                elif isinstance(event, KilledEvent):
                    death_ticks[event.target] = event.tick
                    kills.append(event)
                    counts["kills_crew_witnessed"] += any(
                        step.pre_state.players[pid].role == "CREWMATE"
                        for pid in event.witnesses
                    )
                elif isinstance(event, MeetingTriggeredEvent):
                    counts[f"meeting_triggers:{event.trigger}"] += 1
                    if event.body_id is not None:
                        victim = step.state.bodies[event.body_id].player_id
                        age = event.tick - death_ticks[victim]
                        counts[f"reported_body_age:{age}"] += 1
                elif isinstance(event, VentExitedEvent):
                    crew = {
                        pid
                        for pid, player in step.pre_state.players.items()
                        if player.role == "CREWMATE"
                    }
                    source = bool(crew & set(event.source_witnesses))
                    destination = bool(crew & set(event.destination_witnesses))
                    counts["vent_exits_crew_witnessed"] += source or destination
                    counts["vent_exits_crew_destination_witnessed"] += destination
                    counts["vent_exits_crew_source_only_witnessed"] += (
                        source and not destination
                    )
                    inside = event.tick - vent_anchor.pop(event.actor)
                    counts[f"vent_trip_ticks_inside:{inside}"] += 1
                    counts["vent_trips_reaching_cap"] += inside >= IN_VENT_CAP_TICKS
                    counts["vent_exits_in_place"] += (
                        event.source_room == event.destination_room
                    )
                elif isinstance(event, VentEnteredEvent):
                    vent_anchor[event.actor] = event.tick
                    counts[
                        "vent_entries_not_after_own_fresh_kill"
                    ] += not entry_after_own_fresh_kill(
                        event, kills=kills, meeting_ticks=meeting_ticks
                    )
            last_move = {
                pid: value for pid, value in last_move.items() if pid in moves_this_tick
            }
        elif isinstance(step, MeetingOpened):
            meeting_state = step.state
            counts["meetings"] += 1
            meeting_ticks.append(step.entry.tick)
            for actor in vent_anchor:
                vent_anchor[actor] = step.entry.tick
            counts["meetings_opening_with_impostor_in_vent"] += living_player_in_vent(
                step.state
            )
            counts[
                f"meeting_caller:{step.state.players[step.entry.triggered_by].role}"
            ] += 1
        elif isinstance(step, MeetingApplied):
            assert meeting_state is not None
            ejected = step.result.ejected_player_id
            if ejected is not None:
                counts[f"ejections:{meeting_state.players[ejected].role}"] += 1
                _transfers(meeting_state, step.state, ejected, counts)
            if step.state.phase != "GAME_OVER":
                counts["nonterminal_meetings"] += 1
                for pid, player in step.state.players.items():
                    if not player.alive:
                        continue
                    before_player = meeting_state.players[pid]
                    counts["survivors_after_nonterminal_meetings"] += 1
                    counts["survivors_with_preserved_spatial_state"] += (
                        player.room,
                        player.position,
                        player.in_vent,
                    ) == (
                        before_player.room,
                        before_player.position,
                        before_player.in_vent,
                    )
                    counts["survivors_vented_after_nonterminal_meetings"] += (
                        player.in_vent
                    )
            counts["unreported_bodies_after_meetings"] += sum(
                body.discovered_by is None for body in step.state.bodies.values()
            )
            last_move.clear()
            last_wait.clear()
        elif isinstance(step, WalkComplete):
            if step.game_end is not None:
                winner, reason = step.game_end.winner, step.game_end.reason
            counts["terminal_tasks_total"] = len(step.state.tasks)
            counts["terminal_tasks_completed"] = sum(
                task.completed for task in step.state.tasks.values()
            )
    return GameMetrics(
        seed=seed,
        roster=roster,
        counts=dict(sorted(counts.items())),
        maximum_finished_wait_ticks=max_wait,
        completion_status=recorded_completion_status(entries),
        winner=winner,
        reason=reason,
        replay_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        trajectory_sha256=hashlib.sha256(
            json.dumps(trajectory, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
        reported_cost_usd=compute_cost_usd(path),
        input_tokens=sum(call.input_tokens for call in calls + failures),
        output_tokens=sum(call.output_tokens for call in calls + failures),
        model_calls=len(calls) + sum(row.model != "default" for row in failures),
    )


class BoundedFakeProvider(FakeProvider):
    def __init__(self, *, max_calls: int = 256) -> None:
        self.calls = 0
        self.max_calls = max_calls
        self.preflight_cost_per_input_token_usd = 0.0
        self.preflight_cost_per_output_token_usd = 0.0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if self.calls >= self.max_calls:
            raise RuntimeError("offline model-call limit reached")
        self.calls += 1
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


def run_candidate(
    *,
    seed: int,
    roster: Roster,
    config: RecordedExperimentConfig,
    replay_path: Path,
    max_ticks: int = 96,
    max_calls: int = 256,
) -> GameMetrics:
    """Run and reconstruct one candidate with explicit offline spending limits."""

    provider = BoundedFakeProvider(max_calls=max_calls)
    budget = GameBudget(
        max_cost_usd=0, max_input_tokens=1_000_000, max_output_tokens=100_000
    )
    deadline = RunDeadline(seconds=30)
    runner = build_default_meeting_runner(
        llm_client=provider,
        budget=budget,
        deadline=deadline,
        env={"AILIBI_PROMPT_SET": "qwen3_6_27b"},
    )
    game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=replay_path,
        audit_log_path=Path(os.devnull),
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=runner,
        experiment_config=config,
        deadline=deadline,
        **roster.model_dump(),
    )
    error: str | None = None
    try:
        game.run()
    except (RuntimeError, TimeoutError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    metrics = measure_replay(replay_path, seed=seed, roster=roster)
    snapshot = budget.snapshot()
    if (
        abs(metrics.reported_cost_usd - snapshot.cost_usd) > 1e-9
        or metrics.input_tokens != snapshot.input_tokens
        or metrics.output_tokens != snapshot.output_tokens
    ):
        raise ValueError("recorded spending differs from the enforced game budget")
    return metrics.model_copy(
        update={
            "input_tokens": snapshot.input_tokens,
            "output_tokens": snapshot.output_tokens,
            "model_calls": provider.calls,
            "error": error,
        }
    )


def runtime_fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for package in (
        "engine",
        "observation",
        "agents",
        "meetings",
        "llm",
        "orchestrator",
        "eval",
    ):
        for path in sorted(
            path
            for path in (root / package).rglob("*")
            if path.suffix in {".py", ".j2", ".yaml", ".json"}
        ):
            digest.update(
                path.relative_to(root).as_posix().encode()
                + b"\0"
                + path.read_bytes()
                + b"\0"
            )
    for path in (root / "pyproject.toml", root / "uv.lock", Path(__file__)):
        digest.update(
            path.relative_to(root).as_posix().encode()
            + b"\0"
            + path.read_bytes()
            + b"\0"
        )
    return digest.hexdigest()


def measure_world_copy_control(*, iterations: int = 5_000) -> dict[str, Any]:
    """Characterize current immutable copies without changing engine behavior.

    Median of five warmed in-process loops; no CI timing threshold. The mapping
    loop is a separate operation measurement, not a causal percentage of total
    replacement time. Reusing an arbitrary MappingProxyType fails the aliasing
    control because its backing dict may still be externally mutable.
    """

    if iterations < 1:
        raise ValueError("copy measurement needs a positive iteration count")
    state = seed_initial_state(
        seed=1000,
        game_map=load_canonical_map(),
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    names = ("players", "bodies", "tasks", "cooldowns", "emergency_uses")
    updated = replace(state, tick=state.tick + 1)
    external_players = dict(state.players)
    wrapped = replace(state, players=MappingProxyType(external_players))
    external_players.clear()
    protected = len(wrapped.players) == len(state.players)
    if not protected:
        raise ValueError("immutable world accepted an externally mutable mapping alias")
    replace(state, tick=1)
    replacements = []
    copies = []
    mappings = tuple(getattr(state, name) for name in names)
    for _ in range(5):
        started = time.perf_counter_ns()
        for _ in range(iterations):
            replace(state, tick=1)
        replacements.append((time.perf_counter_ns() - started) / iterations)
        started = time.perf_counter_ns()
        for _ in range(iterations):
            tuple(MappingProxyType(dict(mapping)) for mapping in mappings)
        copies.append((time.perf_counter_ns() - started) / iterations)
    return {
        "scope": "five warmed single-process loops; nanoseconds per operation",
        "iterations_per_loop": iterations,
        "replace_world_median_ns": statistics.median(replacements),
        "copy_five_mappings_median_ns": statistics.median(copies),
        "new_mapping_objects": sum(
            getattr(state, name) is not getattr(updated, name) for name in names
        ),
        "mapping_values_preserved": all(
            getattr(state, name) == getattr(updated, name) for name in names
        ),
        "rng_bytes_preserved": updated.rng_state is state.rng_state,
        "external_mapping_proxy_cannot_mutate_state": protected,
        "disposition": "retain safe copies; RNG reconstruction already bypasses initialization",
    }


def build_comparison(
    *,
    split: str,
    arms: tuple[str, ...] | None = None,
    include_samples: bool = False,
) -> dict[str, Any]:
    if split not in SPLIT_SEEDS:
        raise ValueError(f"unknown split {split!r}; declared: {sorted(SPLIT_SEEDS)}")
    root = Path(__file__).resolve().parents[1]
    before = runtime_fingerprint(root)
    configs = candidate_configs()
    selected = tuple(configs) if arms is None else arms
    if (
        not selected
        or len(set(selected)) != len(selected)
        or any(name not in configs for name in selected)
    ):
        raise ValueError("select distinct, declared experiment arms")
    seeds = SPLIT_SEEDS[split]
    set_names = ("4p1i", "9p2i")
    source_fingerprints = {
        name: recording_fingerprint(root / "replays/samples" / name)
        for name in set_names
    }
    roster_bytes = {
        name: (root / "replays/samples" / name / "roster.json").read_bytes()
        for name in set_names
    }
    rosters = {
        name: Roster.model_validate_json(raw) for name, raw in roster_bytes.items()
    }
    if any(
        recording_fingerprint(root / "replays/samples" / name) != fingerprint
        for name, fingerprint in source_fingerprints.items()
    ) or any(
        (root / "replays/samples" / name / "roster.json").read_bytes() != raw
        for name, raw in roster_bytes.items()
    ):
        raise RuntimeError("recording inputs changed while capturing the run setup")
    output: dict[str, Any] = {
        "format_version": 1,
        "kind": "offline tactical mechanisms; fake outcomes are not model-quality evidence",
        "split": split,
        "seeds": seeds,
        "source_sha256": before,
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "machine": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "measured_utc": datetime.now(timezone.utc).isoformat(),
        "input_fingerprints": source_fingerprints,
        "consumed_roster_sha256": {
            name: hashlib.sha256(raw).hexdigest() for name, raw in roster_bytes.items()
        },
        "limits": {
            "ticks": 96,
            "calls": 256,
            "input_tokens": 1_000_000,
            "output_tokens": 100_000,
            "cost_usd": 0,
            "wall_seconds_per_game": 30,
        },
        "arms": {},
        "historical_samples": {},
        "identity_permutations": {},
        "world_copy_control": measure_world_copy_control(),
    }
    for name, roster in rosters.items():
        if include_samples:
            output["historical_samples"][name] = [
                measure_replay(
                    root / "replays/samples" / name / f"replay-seed-{seed}.jsonl",
                    seed=seed,
                    roster=roster,
                ).model_dump(mode="json")
                for seed in range(50)
            ]
            identity: Counter[str] = Counter()
            for seed in range(50):
                identity.update(
                    measure_identity_effects(
                        root / "replays/samples" / name / f"replay-seed-{seed}.jsonl",
                        seed=seed,
                        roster=roster,
                    )
                )
            output["identity_permutations"][name] = dict(sorted(identity.items()))
        for arm in selected:
            rows = []
            for seed in seeds:
                with tempfile.TemporaryDirectory(
                    prefix="ailibi-tactical-"
                ) as directory:
                    metrics = run_candidate(
                        seed=seed,
                        roster=roster,
                        config=configs[arm],
                        replay_path=Path(directory) / f"replay-seed-{seed}.jsonl",
                    )
                rows.append(metrics.model_dump(mode="json"))
            output["arms"].setdefault(
                arm, {"config": configs[arm].model_dump(mode="json"), "sets": {}}
            )["sets"][name] = rows
    output["ticks_to_parity"] = ticks_to_parity(output["arms"])
    output["whereabouts_coverage"] = whereabouts_coverage_summary(output["arms"])
    output["idle_policy_pairs"] = idle_policy_pairs(output["arms"])
    if runtime_fingerprint(root) != before:
        raise RuntimeError(
            "runtime source changed during the comparison; rerun on frozen inputs"
        )
    if any(
        recording_fingerprint(root / "replays/samples" / name) != fingerprint
        for name, fingerprint in source_fingerprints.items()
    ):
        raise RuntimeError("committed input recordings changed during measurement")
    if any(
        (root / "replays/samples" / name / "roster.json").read_bytes() != raw
        for name, raw in roster_bytes.items()
    ):
        raise RuntimeError("consumed roster bytes differ from the recording inputs")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--split", required=True, choices=tuple(SPLIT_SEEDS))
    parser.add_argument("--arms", nargs="+")
    parser.add_argument("--include-samples", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    result = build_comparison(
        split=args.split,
        arms=None if args.arms is None else tuple(args.arms),
        include_samples=args.include_samples,
    )
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
