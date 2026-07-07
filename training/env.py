"""The tactical rollout environment + legal-action mask (Task 15.8).

``TacticalRolloutEnv`` is the seam every trainer in Phase 15 rides. It drives the
REAL production loop — :class:`orchestrator.game.HeadlessGame` with an injected
:data:`~orchestrator.game.AgentFactory` — never a bespoke "training game." The
ONLY interposition is at the factory: :class:`_InterposedAgent` wraps the real
:class:`~orchestrator.game.TacticalAgent`, optionally overrides the chosen intent
via a policy-supplied :data:`IntentSelector`, and delegates the FULL
``MeetingAwareAgent`` protocol (both properties, both render methods, and the
belief-fold hooks) to the inner agent via ``__getattr__``. This is the ml_spike
interposition pattern (``experiments/lab/ml_spike/core.py:148-200``) ported into
strict-typed code — the spike itself is mypy-excluded and is NOT imported.

Three capabilities land here and in the sibling modules:

* the **legal-action mask** (:class:`ActionMask` / :func:`build_action_mask`),
  derived from the pure legality predicates in ``engine/rules.py`` /
  ``engine/tick.py`` (audit §5.1) — mirrored AGENT-SIDE from the observation
  packet + two policy-side trackers (the two documented caveats: emergency
  uses-remaining and the map's sabotage kinds are NOT on the observation
  surface, so the mask carries small trackers rather than widening the packet,
  the ``EmergencyPacingTracker`` precedent). The mask SPLITS engine-legal
  resolved actions from observation-meaningful submissions, keeping the
  impostor's engine-rejected pretend ``do_task`` (rendered as ``action="task"``
  camouflage to witnesses) in the impostor SUBMISSION set;
* the **potential-based reward channel** (:mod:`training.rewards`);
* the **per-episode rollout records** (:mod:`training.rollout`).

A meeting runner is ALWAYS installed (default: ``build_default_meeting_runner``
on the fake provider), so ``meeting_runner=None`` truncation
(``MEETING_PHASE_REACHED``) is structurally unreachable from the env. The
explicit ``episode_boundary="first_meeting"`` opt-in is the one deliberate
boundary mode (the 15.13 fallback-(b) seam); its episodes are MARKED truncated in
the rollout record and the reward channel refuses to score them as full games.

numpy is training-confined by a new import-linter contract (``agents`` must not
import ``training``); the production inference path (15.10, Wave 2) stays
pure-Python precisely because BLAS reductions are not bit-stable across
machines/thread counts.

Throughput (Task 15.8 definition of done): measured on the check host at
``9p2i`` full fake-provider games through the injected factory, the env sustains
~5.9 games/s (above the ≥5 games/s floor). The figure is a full-game rollout
INCLUDING the typed state-hash-verified reconstruction pass (the live game plus a
cheap bare-engine walk); it is a floor, not a benchmark, and varies with host.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from agents.base import AgentInterface
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    KillIntent,
    MoveIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_TASKS_PER_CREWMATE,
    AgentFactory,
    HeadlessGame,
    MeetingRunner,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from training.rollout import (
    EpisodeBoundary,
    EpisodeRollout,
    _validate_episode_boundary,
    reconstruct_episode,
)


@dataclass(frozen=True)
class ActionMask:
    """A legal-action mask over the option/intent space at one tick (Task 15.8).

    The mask SPLITS two vocabularies (audit §5.1 caveat 2):

    * ``engine_legal`` — concrete :class:`~observation.action_intent.ActionIntent`
      candidates that RESOLVE without an ``ActionRejected`` from the engine.
    * ``submission_only`` — observation-meaningful submissions the engine REJECTS
      but that still carry signal: the impostor's pretend ``do_task`` (it owns no
      instance, so it is engine-rejected, yet it renders as ``action="task"``
      camouflage to witnesses — 396 such submissions in the committed baseline-2
      9p2i stream). A strict engine-legal-only vocabulary would delete this lever
      and regress the impostor's task-traffic mimicry.
    * ``illegal`` — enumerated candidates that are neither engine-legal nor
      observation-meaningful (a far move, a wrong-room ``do_task`` for a crew, an
      out-of-range kill, …). Kept so the property test can assert every unmasked
      candidate is engine-rejected.

    ``submission_legal`` is the full set a policy may emit: ``engine_legal`` plus
    ``submission_only``.
    """

    engine_legal: tuple[ActionIntent, ...]
    submission_only: tuple[ActionIntent, ...]
    illegal: tuple[ActionIntent, ...]

    @property
    def submission_legal(self) -> tuple[ActionIntent, ...]:
        """Every intent a policy may submit (engine-legal + observation-meaningful)."""

        return self.engine_legal + self.submission_only

    def is_engine_legal(self, intent: ActionIntent) -> bool:
        return intent in self.engine_legal

    def is_submission_legal(self, intent: ActionIntent) -> bool:
        return intent in self.engine_legal or intent in self.submission_only


def _vent_in_room(public_map: PublicMapView, room: str) -> str | None:
    """The (deterministic, alphabetically-first) vent id sitting in ``room``."""

    vents = sorted(
        vent_id
        for vent_id, vent_room in public_map.vent_rooms.items()
        if vent_room == room
    )
    return vents[0] if vents else None


def build_action_mask(
    packet: ObservationPacket,
    public_map: PublicMapView,
    *,
    sabotage_kinds: Sequence[str],
    emergency_uses_remaining: int,
) -> ActionMask:
    """Mirror the engine legality predicates agent-side into an :class:`ActionMask`.

    Every predicate is a pure boolean of ``(state, map, actor)`` with zero RNG
    (audit §5.1), so the mask mirrors them from the observation packet +
    ``PublicMapView`` + the two policy-side trackers (``sabotage_kinds`` — the
    map's sabotage vocabulary, absent from the packet — and
    ``emergency_uses_remaining`` — the actor's spent-use count, absent from the
    packet). It never imports ``engine/``: ``training/`` reaches engine truth only
    through the orchestrator loop, so the mask is a faithful mirror the property
    test pins against the real engine.
    """

    self_state = packet.self_state
    actor = packet.agent_id
    role = self_state.role
    own_room = self_state.room
    in_vent = self_state.in_vent
    fellows = set(self_state.fellow_impostor_ids)
    cooldown = packet.cooldown
    pending = self_state.pending_task_id
    global_state = packet.global_state
    sabotage_active = global_state.sabotage_active
    sabotage_kind = global_state.sabotage_kind
    repair_rooms = set(global_state.sabotage_repair_rooms)
    neighbors = set(public_map.room_neighbors.get(own_room, ()))

    engine_legal: list[ActionIntent] = []
    submission_only: list[ActionIntent] = []
    illegal: list[ActionIntent] = []

    def add(intent: ActionIntent, *, legal: bool) -> None:
        (engine_legal if legal else illegal).append(intent)

    # WAIT — always legal for a live actor (tick.py:530-536).
    engine_legal.append(WaitIntent(actor=actor, type="wait"))

    # MOVE — not in vent; destination is current room or an adjacent room.
    for room in public_map.room_ids:
        add(
            MoveIntent.model_validate(
                {"type": "move", "actor": actor, "payload": {"to_room": room}}
            ),
            legal=(not in_vent) and (room == own_room or room in neighbors),
        )

    # DO_TASK — the crew's real pending task vs the impostor's pretend camouflage.
    if pending is not None:
        do_task = DoTaskIntent.model_validate(
            {"type": "do_task", "actor": actor, "payload": {"task_id": pending}}
        )
        if role == "IMPOSTOR":
            # Pretend do_task: engine-rejected (owns no instance) but the
            # ``action="task"`` camouflage submission — observation-meaningful.
            submission_only.append(do_task)
        else:
            task_room = public_map.task_locations.get(pending)
            add(
                do_task,
                legal=(
                    (not in_vent)
                    and not (sabotage_active and global_state.sabotage_is_gating)
                    and task_room == own_room
                ),
            )

    # KILL — impostor only; co-located non-teammate crew; cooldown 0.
    if role == "IMPOSTOR":
        for view in packet.visible_players:
            add(
                KillIntent.model_validate(
                    {"type": "kill", "actor": actor, "payload": {"target": view.id}}
                ),
                legal=(
                    cooldown == 0 and view.room == own_room and view.id not in fellows
                ),
            )

    # VENT — impostor only; enter = vent in current room; exit = connected vent.
    if role == "IMPOSTOR":
        current_vent = _vent_in_room(public_map, own_room) if in_vent else None
        connected = (
            set(public_map.vent_graph.get(current_vent, ()))
            if current_vent is not None
            else set()
        )
        for vent_id in sorted(public_map.vent_rooms):
            if in_vent:
                legal = current_vent is not None and (
                    vent_id == current_vent or vent_id in connected
                )
            else:
                legal = public_map.vent_rooms[vent_id] == own_room
            add(
                VentIntent.model_validate(
                    {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
                ),
                legal=legal,
            )

    # REPORT — a visible body in the actor's own room.
    for body in packet.visible_bodies:
        add(
            ReportBodyIntent.model_validate(
                {"type": "report", "actor": actor, "payload": {"body_id": body.id}}
            ),
            legal=body.room == own_room,
        )

    # EMERGENCY — not in vent; uses remaining; in the emergency-button room.
    add(
        EmergencyMeetingIntent(actor=actor, type="emergency"),
        legal=(
            (not in_vent)
            and emergency_uses_remaining > 0
            and own_room == public_map.emergency_button_room
        ),
    )

    # SABOTAGE — impostor only; no sabotage already active; kind exists (no
    # location or in-vent requirement).
    if role == "IMPOSTOR":
        for kind in sabotage_kinds:
            add(
                SabotageIntent.model_validate(
                    {"type": "sabotage", "actor": actor, "payload": {"kind": kind}}
                ),
                legal=not sabotage_active,
            )

    # REPAIR_SABOTAGE — role-blind; not in vent; an active sabotage of the SAME
    # kind; in that kind's repair room.
    for kind in sabotage_kinds:
        add(
            RepairSabotageIntent.model_validate(
                {
                    "type": "repair_sabotage",
                    "actor": actor,
                    "payload": {"kind": kind},
                }
            ),
            legal=(
                (not in_vent)
                and sabotage_active
                and sabotage_kind == kind
                and own_room in repair_rooms
            ),
        )

    return ActionMask(
        engine_legal=tuple(engine_legal),
        submission_only=tuple(submission_only),
        illegal=tuple(illegal),
    )


@dataclass(frozen=True)
class MaskedDecision:
    """The inputs handed to an :data:`IntentSelector` at one decision (Task 15.8).

    Carries the observation the policy legally sees, the public map, the FSM's own
    choice (a ready-made behavior-cloning label / anchor, audit §5.2), and the
    legal-action mask. A learned policy (15.10+) rides this seam; a returned
    intent that is not ``submission_legal`` is rejected by the wrapper.
    """

    packet: ObservationPacket
    public_map: PublicMapView
    fsm_intent: ActionIntent
    mask: ActionMask


# A policy that selects the tick's intent given the FSM proposal + the mask. The
# learned tactical policy of 15.10+ is exactly this shape; ``None`` (the default)
# is pure FSM delegation, so a rollout with no selector is the scripted anchor.
IntentSelector: TypeAlias = Callable[[MaskedDecision], ActionIntent]


class _InterposedAgent:
    """AgentInterface proxy around a real :class:`TacticalAgent` (Task 15.8).

    Ports the ml_spike ``SpikeAgent`` interposition into strict-typed code (the
    spike is mypy-excluded and NOT imported). :meth:`decide` always drives the
    inner FSM (so its perception, memory, and emergency-pacing bookkeeping stay
    exact), then — only when an :data:`IntentSelector` is supplied — computes the
    :class:`ActionMask` and lets the selector override the intent, validating the
    choice against the mask's submission vocabulary. Everything else — the whole
    ``MeetingAwareAgent`` protocol (both properties, both render methods) and the
    belief-fold hooks — delegates to the inner agent via ``__getattr__``, so the
    wrapper satisfies the isinstance-checked protocol for free.
    """

    def __init__(
        self,
        inner: TacticalAgent,
        *,
        sabotage_kinds: Sequence[str],
        emergency_uses_per_player: int,
        intent_selector: IntentSelector | None = None,
    ) -> None:
        self._inner = inner
        self._agent_id = inner.agent_id
        self._sabotage_kinds = tuple(sabotage_kinds)
        self._intent_selector = intent_selector
        # Policy-side emergency-uses tracker (the EmergencyPacingTracker
        # precedent, audit §5.1 caveat 1): the actor's spent-use count is not on
        # the observation surface, so the mask carries it rather than widening the
        # packet. Decremented when THIS agent's own emergency opens a meeting
        # (engine truth via note_meeting_concluded), mirroring the engine's
        # per-player ``emergency_uses`` counter.
        self._emergency_uses_remaining = emergency_uses_per_player

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        fsm_intent = self._inner.decide(packet, public_map)
        selector = self._intent_selector
        if selector is None:
            return fsm_intent
        mask = build_action_mask(
            packet,
            public_map,
            sabotage_kinds=self._sabotage_kinds,
            emergency_uses_remaining=self._emergency_uses_remaining,
        )
        chosen = selector(
            MaskedDecision(
                packet=packet,
                public_map=public_map,
                fsm_intent=fsm_intent,
                mask=mask,
            )
        )
        if not mask.is_submission_legal(chosen):
            raise ValueError(
                f"intent selector for {self._agent_id!r} returned a non-submission-"
                f"legal intent {chosen!r}; the mask forbids illegal actions"
            )
        return chosen

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
    ) -> None:
        """Track this agent's own spent emergency use, then delegate (Task 15.8).

        Explicitly overridden (rather than delegated via ``__getattr__``) so the
        mask's ``emergency_uses_remaining`` tracker stays in lockstep with the
        engine's per-player counter. The inner agent's own bookkeeping (its
        ``EmergencyPacingTracker`` + memory) still runs — this forwards verbatim.
        """

        if emergency_caller_id == self._agent_id:
            self._emergency_uses_remaining = max(0, self._emergency_uses_remaining - 1)
        self._inner.note_meeting_concluded(
            end_tick=end_tick,
            dead_ids=dead_ids,
            emergency_caller_id=emergency_caller_id,
        )

    def __getattr__(self, name: str) -> object:
        # Delegate the meeting protocol + properties + belief-fold hooks to the
        # inner agent. ``__getattr__`` only fires for names not defined on the
        # wrapper, so ``decide`` / ``note_meeting_concluded`` above win and
        # everything else (agent_id, role, render_memory_for_meeting,
        # suspicion_graph_for_meeting, vent_witness_records_for_meeting,
        # absorb_*) comes straight from the inner TacticalAgent.
        return getattr(self._inner, name)


def build_interposition_factory(
    *,
    game_map: Map,
    intent_selector: IntentSelector | None = None,
) -> AgentFactory:
    """Build the injected :data:`AgentFactory` (the ONLY interposition seam).

    Each constructed agent wraps a real role-appropriate
    :class:`TacticalAgent` in an :class:`_InterposedAgent`. With
    ``intent_selector=None`` (the default) the wrapper is a transparent FSM
    delegate — the scripted anchor — so a rollout is byte-identical to the
    production loop; a learned policy (15.10+) slots in as the selector.
    """

    sabotage_kinds = tuple(sorted(game_map.sabotages))
    emergency_uses = game_map.emergency.uses_per_player

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        inner = TacticalAgent(agent_id=agent_id, policy=policy, role=role)
        return _InterposedAgent(
            inner,
            sabotage_kinds=sabotage_kinds,
            emergency_uses_per_player=emergency_uses,
            intent_selector=intent_selector,
        )

    return factory


class TacticalRolloutEnv:
    """Roll out full production games through an injected factory (Task 15.8).

    The env drives :class:`orchestrator.game.HeadlessGame` — the real engine, the
    real observation firewall, the real meeting manager — with the injected
    interposition factory as the ONLY seam. A meeting runner is ALWAYS installed,
    so ``MEETING_PHASE_REACHED`` truncation is structurally unreachable. Each
    :meth:`rollout` writes a replay, then reconstructs it into a typed
    :class:`~training.rollout.EpisodeRollout` (:mod:`training.rollout`).

    Signature is stable per the task contract: it is the seam every trainer in
    this phase rides.
    """

    def __init__(
        self,
        *,
        game_map: Map | None = None,
        num_players: int = DEFAULT_NUM_PLAYERS,
        num_impostors: int = DEFAULT_NUM_IMPOSTORS,
        tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
        episode_boundary: EpisodeBoundary = "full_game",
        intent_selector: IntentSelector | None = None,
        meeting_runner_factory: Callable[[], MeetingRunner] | None = None,
        max_ticks: int = DEFAULT_MAX_TICKS,
        output_dir: Path | None = None,
    ) -> None:
        # Fail loud at construction on a bad boundary from config/CLI, rather
        # than silently scoring a truncated-intent episode as a full game later.
        _validate_episode_boundary(episode_boundary)
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._episode_boundary: EpisodeBoundary = episode_boundary
        self._intent_selector = intent_selector
        self._meeting_runner_factory = meeting_runner_factory
        self._max_ticks = max_ticks
        self._output_dir = output_dir
        self._public_map = public_map_from_engine_map(self._game_map)

    @property
    def game_map(self) -> Map:
        return self._game_map

    @property
    def public_map(self) -> PublicMapView:
        return self._public_map

    @property
    def episode_boundary(self) -> EpisodeBoundary:
        return self._episode_boundary

    @property
    def sabotage_kinds(self) -> tuple[str, ...]:
        return tuple(sorted(self._game_map.sabotages))

    def _build_meeting_runner(self) -> MeetingRunner:
        # ALWAYS installed (Task 15.8): the default runner, or the surrogate
        # factory once 15.13 lands. A fresh runner per game — runners carry
        # per-game recording/budget state.
        if self._meeting_runner_factory is not None:
            return self._meeting_runner_factory()
        # Force the deterministic FAKE provider (ignore the ambient
        # ``AILIBI_LLM_PROVIDER``): Phase-15 self-play must stay $0 / offline /
        # byte-deterministic. In an eval/dev shell that exports a real provider,
        # the env-selected default client would otherwise send every training
        # meeting to Anthropic/Featherless. A caller who genuinely wants a real
        # (or surrogate) meeting layer opts in via ``meeting_runner_factory``.
        return build_default_meeting_runner(
            llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
        )

    def rollout(self, seed: int) -> EpisodeRollout:
        """Run one full production game and return its typed episode record.

        Writes the replay to ``output_dir`` (or a throwaway temp dir), then
        reconstructs it — state-hash-verified — into an
        :class:`~training.rollout.EpisodeRollout`.
        """

        if self._output_dir is not None:
            self._output_dir.mkdir(parents=True, exist_ok=True)
            return self._rollout_into(self._output_dir, seed)
        with tempfile.TemporaryDirectory(prefix="ailibi-rollout-") as tmp:
            return self._rollout_into(Path(tmp), seed)

    def rollouts(self, seeds: Sequence[int]) -> Iterator[EpisodeRollout]:
        """Yield one :class:`EpisodeRollout` per seed (a convenience iterator)."""

        for seed in seeds:
            yield self.rollout(seed)

    def _rollout_into(self, directory: Path, seed: int) -> EpisodeRollout:
        replay_path = directory / f"replay-seed-{seed}.jsonl"
        factory = build_interposition_factory(
            game_map=self._game_map, intent_selector=self._intent_selector
        )
        game = HeadlessGame(
            seed=seed,
            game_map=self._game_map,
            agent_factory=factory,
            replay_path=replay_path,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=self._max_ticks),
            meeting_runner=self._build_meeting_runner(),
            force=True,
        )
        result = game.run()
        if result.outcome == "MEETING_PHASE_REACHED":
            # Structurally unreachable: a runner is ALWAYS installed. Fail loud if
            # the invariant is ever violated rather than silently truncate.
            raise RuntimeError(
                "TacticalRolloutEnv reached MEETING_PHASE_REACHED with a meeting "
                "runner installed; the always-installed-runner invariant is broken"
            )
        return reconstruct_episode(
            replay_path,
            game_map=self._game_map,
            seed=seed,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
            episode_boundary=self._episode_boundary,
        )


__all__ = [
    "ActionMask",
    "IntentSelector",
    "MaskedDecision",
    "TacticalRolloutEnv",
    "build_action_mask",
    "build_interposition_factory",
]
