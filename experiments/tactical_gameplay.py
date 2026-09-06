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
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, TypeAdapter

from engine.actions import Action
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    VentExitedEvent,
)
from engine.tick import _apply_action
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.balance_eval import _CURRENT_REPORT_WALK_CONFIG
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    walk_replay,
)
from llm.budget import GameBudget
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from orchestrator.experiment_config import RecordedExperimentConfig
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


def candidate_configs() -> dict[str, RecordedExperimentConfig]:
    """Predeclared one-change comparisons; no automatic promotion of an arm."""

    return {
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
    }


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

    require_baseline_experiments(
        read_all_entries(path), consumer="recorded baseline identity intervention"
    )
    counts: Counter[str] = Counter()
    game_map = load_canonical_map()
    config = replace(_CURRENT_REPORT_WALK_CONFIG, profile="tactical-seat-effects")
    adapter: TypeAdapter[Action] = TypeAdapter(Action)
    for step in walk_replay(
        path, seed=seed, game_map=game_map, config=config, **roster.model_dump()
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
            after, events = advance_tick(renamed, reordered, game_map=game_map)
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
    experiments = recorded_experiment_config(entries) or RecordedExperimentConfig()
    config = replace(_CURRENT_REPORT_WALK_CONFIG, profile="tactical-mechanisms")
    game_map = load_canonical_map()
    adapter: TypeAdapter[Action] = TypeAdapter(Action)
    counts: Counter[str] = Counter()
    last_move: dict[str, tuple[int, str, str]] = {}
    last_wait: dict[str, tuple[int, int]] = {}
    max_wait = 0
    death_ticks: dict[str, int] = {}
    meeting_state: WorldState | None = None
    winner: str | None = None
    reason: str | None = None
    for step in walk_replay(
        path, seed=seed, game_map=game_map, config=config, **roster.model_dump()
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
            actions = tuple(adapter.validate_python(raw) for raw in step.entry.actions)
            dispositions = classify_action_dispositions(actions, step.events)
            working = step.pre_state
            for action, disposition in zip(actions, dispositions, strict=True):
                role = step.pre_state.players[action.actor].role
                counts[f"{disposition}:{role}:{action.type}"] += 1
                if disposition != "applied":
                    continue
                after, event = _apply_action(
                    working,
                    game_map,
                    action,
                    redistribution_policy=experiments.redistribution_policy,
                )
                if isinstance(event, KilledEvent):
                    _transfers(working, after, event.target, counts)
                working = after
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
            last_move = {
                pid: value for pid, value in last_move.items() if pid in moves_this_tick
            }
        elif isinstance(step, MeetingOpened):
            meeting_state = step.state
            counts["meetings"] += 1
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
    split: Literal["development", "held_out"],
    arms: tuple[str, ...] | None = None,
    include_samples: bool = False,
) -> dict[str, Any]:
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
    seeds = tuple(range(1000, 1008) if split == "development" else range(2000, 2016))
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
    parser.add_argument("--split", required=True, choices=("development", "held_out"))
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
