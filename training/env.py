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

Two DEFAULT-OFF training knobs (Task 15.8.1): ``no_replay`` drives each rollout
through :meth:`orchestrator.game.HeadlessGame.run_unrecorded`, writing NOTHING to
disk and assembling the episode from the live trajectory instead of a replay file
(so it skips the record-side + reconstruct-side state serialization entirely); and
``rng_hash_policy`` selects the per-tick rng-state serialization, whose opt-in
:attr:`~engine.rng.RngStateHashPolicy.TRAINING_FAST` skips the ~43%-of-engine-cost
``json.dumps`` snapshot (~1.3-1.4x engine-core speedup). The fast path serializes
``rng_state`` with a non-committed codec, so it is REFUSED unless ``no_replay`` is
set — trajectories are identical under either mode, so training on the fast path
transfers to the recording path exactly.

Task 18.23 adds the scenario-staging integration on the same no-replay path:
:meth:`TacticalRolloutEnv.rollout_injected` runs one episode from an injected
mid-game ``WorldState`` (the ``HeadlessGame`` ``initial_state`` seam, bypassing
``seed_initial_state``) and assembles it live — the skill-scenario library in
:mod:`training.scenarios` builds those states and scores the episodes from
tactical facts only.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from agents.base import AgentInterface
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.actions import DoTaskAction
from engine.entities import PlayerId, Role
from engine.events import EngineEvent, GameOverEvent, KilledEvent, MeetingTriggeredEvent
from engine.rng import RngStateHashPolicy
from engine.world import Map, WorldState, load_canonical_map
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
    UnrecordedGameResult,
    build_default_meeting_runner,
)
from orchestrator.replay import WinnerSide, _state_hash
from orchestrator.scheduler import TickScheduler
from training.rollout import (
    EpisodeBoundary,
    EpisodeFrame,
    EpisodeOutcome,
    EpisodeRollout,
    MeetingRecord,
    RolloutReconstructionError,
    _build_descriptors,
    _frame,
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

    Membership is exact frozen-model equality with ONE canonicalization (Task
    15.16): emergency intents compare with their free-form ``reason`` payload
    dropped — see :func:`_canonical_mask_intent`.
    """

    engine_legal: tuple[ActionIntent, ...]
    submission_only: tuple[ActionIntent, ...]
    illegal: tuple[ActionIntent, ...]

    @property
    def submission_legal(self) -> tuple[ActionIntent, ...]:
        """Every intent a policy may submit (engine-legal + observation-meaningful)."""

        return self.engine_legal + self.submission_only

    def is_engine_legal(self, intent: ActionIntent) -> bool:
        return _canonical_mask_intent(intent) in self.engine_legal

    def is_submission_legal(self, intent: ActionIntent) -> bool:
        canonical = _canonical_mask_intent(intent)
        return canonical in self.engine_legal or canonical in self.submission_only


def _canonical_mask_intent(intent: ActionIntent) -> ActionIntent:
    """Canonicalize one intent for mask membership (Task 15.16).

    The emergency-intent canonicalization that closes the documented 15.8
    exact-equality gap (``eval/leak_test.py`` ``_IdleExploreAgent`` docstring):
    the mask's emergency entry carries the DEFAULT payload (``reason=None``,
    :func:`build_action_mask`'s EMERGENCY region), while the crew FSM stamps a
    producer tag on the same action (``reason='suspicion_accumulation'`` /
    ``'kill_witnessed'`` — ``agents/tactical/crewmate_policy.py``). The engine's
    emergency legality is reason-blind (the tag is agent-side provenance for
    replay/eval tooling, never an engine input), but frozen-pydantic equality is
    field-exact, so without canonicalization a selector delegating the FSM's own
    emergency would fail :meth:`ActionMask.is_submission_legal` and raise out of
    the interposition wrapper. Emergency intents therefore compare with the
    payload dropped; every other intent type compares exact — their payloads
    (rooms, targets, kinds) ARE engine inputs.
    """

    if isinstance(intent, EmergencyMeetingIntent):
        return EmergencyMeetingIntent(actor=intent.actor, type="emergency")
    return intent


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
        task_room = public_map.task_locations.get(pending)
        if role == "IMPOSTOR":
            # Pretend do_task: engine-rejected (owns no instance). It is the
            # ``action="task"`` camouflage submission ONLY when the impostor
            # actually stands in the pretend task's room and is not vented —
            # matching the FSM blend (``impostor_policy._idle``) and the
            # believable-camouflage semantics (crew task only in task rooms, so a
            # ``do_task`` elsewhere is a tell, not camouflage; a vented actor is
            # unseen, so nothing renders). Elsewhere it is a plain illegal
            # submission, so a selector cannot spam a stationary fake task to
            # farm the camouflage/cadence channel.
            if (not in_vent) and task_room == own_room:
                submission_only.append(do_task)
            else:
                illegal.append(do_task)
        else:
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
        ejected_id: PlayerId | None = None,
    ) -> None:
        """Track this agent's own spent emergency use, then delegate (Task 15.8).

        Explicitly overridden (rather than delegated via ``__getattr__``) so the
        mask's ``emergency_uses_remaining`` tracker stays in lockstep with the
        engine's per-player counter. The inner agent's own bookkeeping (its
        ``EmergencyPacingTracker`` + memory) still runs — this forwards verbatim,
        including the Task 18.22 ``ejected_id`` payload that feeds the inner
        agent's meeting-history memory channel (the v3 encoder's input).
        """

        if emergency_caller_id == self._agent_id:
            self._emergency_uses_remaining = max(0, self._emergency_uses_remaining - 1)
        self._inner.note_meeting_concluded(
            end_tick=end_tick,
            dead_ids=dead_ids,
            emergency_caller_id=emergency_caller_id,
            ejected_id=ejected_id,
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
    emergency_uses_spent: Mapping[PlayerId, int] | None = None,
) -> AgentFactory:
    """Build the injected :data:`AgentFactory` (the ONLY interposition seam).

    Each constructed agent wraps a real role-appropriate
    :class:`TacticalAgent` in an :class:`_InterposedAgent`. With
    ``intent_selector=None`` (the default) the wrapper is a transparent FSM
    delegate — the scripted anchor — so a rollout is byte-identical to the
    production loop; a learned policy (15.10+) slots in as the selector.

    ``emergency_uses_spent`` seeds each wrapper's mask-side emergency tracker
    with already-spent button uses (Task 18.23): an injected mid-game state can
    carry nonzero ``WorldState.emergency_uses``, and a tracker seeded to the
    map-wide full allowance would advertise an engine-rejected emergency as
    engine-legal, corrupting the mask contract. Default ``None`` (no spent
    uses) is the seeded-game default, byte-identical to before.
    """

    sabotage_kinds = tuple(sorted(game_map.sabotages))
    emergency_uses = game_map.emergency.uses_per_player
    spent = dict(emergency_uses_spent) if emergency_uses_spent is not None else {}

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
            emergency_uses_per_player=max(0, emergency_uses - spent.get(agent_id, 0)),
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
        no_replay: bool = False,
        rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
    ) -> None:
        # Fail loud at construction on a bad boundary from config/CLI, rather
        # than silently scoring a truncated-intent episode as a full game later.
        _validate_episode_boundary(episode_boundary)
        # Task 15.8.1 knobs, both DEFAULT-OFF so the env is byte-identical to the
        # 15.8 baseline unless a caller opts in:
        #   * ``no_replay`` drives each rollout through the no-replay training
        #     mode (:meth:`HeadlessGame.run_unrecorded`), writing NOTHING to disk
        #     and reconstructing the episode from the live trajectory instead of a
        #     replay file;
        #   * ``rng_hash_policy`` selects the per-tick rng-state serialization; its
        #     opt-in :attr:`RngStateHashPolicy.TRAINING_FAST` skips the ~43%-of-
        #     engine-cost json.dumps snapshot. The fast path serializes rng_state
        #     with a non-committed codec, so — mirroring the HeadlessGame guard —
        #     it is REFUSED unless ``no_replay`` is set, fail-loud rather than
        #     silently recording un-verifiable bytes (AGENTS.md no silent
        #     fallbacks).
        if rng_hash_policy is not RngStateHashPolicy.FULL and not no_replay:
            raise ValueError(
                "the training-only RNG hash fast path "
                f"({rng_hash_policy!r}) requires no_replay=True: the fast codec is "
                "not the committed rng_state encoding, so a recorded rollout must "
                "keep RngStateHashPolicy.FULL. Set no_replay=True to opt in."
            )
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._tasks_per_crewmate = tasks_per_crewmate
        self._episode_boundary: EpisodeBoundary = episode_boundary
        self._intent_selector = intent_selector
        self._meeting_runner_factory = meeting_runner_factory
        self._max_ticks = max_ticks
        self._output_dir = output_dir
        self._no_replay = no_replay
        self._rng_hash_policy = rng_hash_policy
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
    def no_replay(self) -> bool:
        """Whether rollouts run the no-replay training mode (Task 15.8.1)."""

        return self._no_replay

    @property
    def rng_hash_policy(self) -> RngStateHashPolicy:
        """The per-tick rng-state serialization policy for rollouts (Task 15.8.1)."""

        return self._rng_hash_policy

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

        In the DEFAULT (recording) mode, writes the replay to ``output_dir`` (or a
        throwaway temp dir), then reconstructs it — state-hash-verified — into an
        :class:`~training.rollout.EpisodeRollout`.

        With ``no_replay=True`` (Task 15.8.1) the game runs through
        :meth:`HeadlessGame.run_unrecorded`, writing NOTHING to disk, and the
        episode is assembled from the live trajectory instead of a replay file —
        the path that carries the opt-in
        :attr:`~engine.rng.RngStateHashPolicy.TRAINING_FAST` rng fast path.
        """

        if self._no_replay:
            return self._rollout_no_replay(seed)
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

    def _rollout_no_replay(self, seed: int) -> EpisodeRollout:
        """Run one no-replay training game and assemble it live (Task 15.8.1).

        Drives :meth:`HeadlessGame.run_unrecorded` — the real production loop with
        NO replay written — and turns the live-captured trajectory into an
        :class:`~training.rollout.EpisodeRollout` WITHOUT a reconstruction re-walk.
        Carries the opt-in fast rng policy; nothing touches disk.
        """

        factory = build_interposition_factory(
            game_map=self._game_map, intent_selector=self._intent_selector
        )
        game = HeadlessGame(
            seed=seed,
            game_map=self._game_map,
            agent_factory=factory,
            replay_path=None,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=self._max_ticks),
            meeting_runner=self._build_meeting_runner(),
            rng_hash_policy=self._rng_hash_policy,
        )
        result = game.run_unrecorded()
        if result.outcome == "MEETING_PHASE_REACHED":
            # Structurally unreachable: a runner is ALWAYS installed. Fail loud if
            # the invariant is ever violated rather than silently truncate.
            raise RuntimeError(
                "TacticalRolloutEnv reached MEETING_PHASE_REACHED with a meeting "
                "runner installed; the always-installed-runner invariant is broken"
            )
        return self._episode_from_unrecorded(
            result,
            seed,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
        )

    def rollout_injected(
        self,
        initial_state: WorldState,
        *,
        agent_factory: AgentFactory | None = None,
    ) -> EpisodeRollout:
        """Run one no-replay episode from an injected mid-game state (Task 18.23).

        The env half of the scenario-staging seam: drives
        :meth:`HeadlessGame.run_unrecorded` with ``initial_state`` injected
        (bypassing ``seed_initial_state``) and assembles the live trajectory into
        a typed :class:`~training.rollout.EpisodeRollout` exactly like
        :meth:`rollout` in no-replay mode. Requires ``no_replay=True`` at
        construction — an injected episode has no recorded state-hash chain, so
        the recording path is structurally wrong for it and the mismatch fails
        loud here rather than deep in reconstruction (AGENTS.md "no silent
        fallbacks").

        ``agent_factory`` (default ``None`` = the env's interposition factory
        with the constructor's ``intent_selector``) lets a scenario episode run
        the campaign's OWN memory-aware agents — e.g. the factory
        ``training.coevo.factory.build_coevo_factory`` builds over the sides'
        learned policies, whose wrappers read the inner agent's live
        ``AgentMemory`` (the v3 meeting-history / last-seen channels an
        :data:`IntentSelector` never sees). Mutually exclusive with a
        constructor ``intent_selector`` (fail loud rather than silently ignore
        one seam), and a supplied factory owns its OWN mid-game trackers: the
        interposition factory's mask-side emergency seeding applies only to
        the default path.

        The roster (``num_players`` / ``num_impostors``) is derived from the
        injected state itself, so the episode record is consistent with the
        state by construction; the env's constructor roster knobs describe the
        SEEDED path and are deliberately not consulted. ``tasks_per_crewmate``
        has no seeder provenance for a mid-game state, so the record carries the
        max per-living-crewmate instance count (0 when no living crewmate owns
        one). The game seed is ``initial_state.seed`` — the scenario library
        stamps it alongside the canonical ``EngineRng.from_seed(seed)`` rng
        snapshot, so determinism is inherited from ``advance_tick`` purity.

        Scenario episodes are truncated by construction (the injected tick plus
        a short horizon), so they surface ``outcome="TICK_BUDGET"`` /
        ``truncated=True`` records that the reward channel's terminal gate
        refuses; an episode that does reach ``GAME_OVER`` inside its horizon
        keeps its truthful terminal shape, and scenario fitness reads dense
        tactical facts either way (:mod:`training.scenarios`), never
        ``compute_shaped_reward``.
        """

        if not self._no_replay:
            raise ValueError(
                "rollout_injected() rides the no-replay live-assembly path "
                "(Task 18.23): an injected episode has no recorded hash chain "
                "to reconstruct, so the env must be constructed with "
                "no_replay=True."
            )
        if agent_factory is not None and self._intent_selector is not None:
            raise ValueError(
                "rollout_injected() received an explicit agent_factory but the "
                "env was constructed with an intent_selector; the two are "
                "competing agent seams, so pass exactly one (drop the selector "
                "to drive the episode through the supplied factory)."
            )
        if initial_state.tick >= self._max_ticks:
            raise ValueError(
                f"injected initial_state starts at tick {initial_state.tick} "
                f"but the env's tick budget is max_ticks={self._max_ticks}; the "
                "episode could not advance a single tick. Raise max_ticks above "
                "the staged tick plus the scenario horizon."
            )
        # The mask-side emergency trackers are seeded by SUBTRACTING the staged
        # spent-use counts from the map allowance below, and the engine itself
        # counts presses up from 0 — so an out-of-range counter (a negative
        # value minting extra presses, or a roster-foreign key) is a state no
        # game can produce and must fail loud here, not corrupt the mask.
        uses_cap = self._game_map.emergency.uses_per_player
        for player_id, used in initial_state.emergency_uses.items():
            if player_id not in initial_state.players:
                raise ValueError(
                    f"injected initial_state carries an emergency_uses entry for "
                    f"{player_id!r}, which is not on its roster"
                )
            if not 0 <= used <= uses_cap:
                raise ValueError(
                    f"injected initial_state has emergency_uses={used} for "
                    f"{player_id!r}, outside [0, {uses_cap}]; the engine counts "
                    "presses up from 0 to the map cap, so any other value has "
                    "no game provenance"
                )
        num_players = len(initial_state.players)
        num_impostors = sum(
            1 for player in initial_state.players.values() if player.role == "IMPOSTOR"
        )
        instances_per_crewmate = [
            sum(1 for task in initial_state.tasks.values() if task.owner == pid)
            for pid, player in initial_state.players.items()
            if player.alive and player.role == "CREWMATE"
        ]
        tasks_per_crewmate = max(instances_per_crewmate, default=0)
        # Default path: the interposition factory, its mask-side emergency
        # trackers seeded with the staged state's spent uses so the mask keeps
        # mirroring engine legality mid-game. A supplied factory replaces the
        # whole agent seam (the campaign's memory-aware wrappers) and owns its
        # own trackers.
        factory = (
            agent_factory
            if agent_factory is not None
            else build_interposition_factory(
                game_map=self._game_map,
                intent_selector=self._intent_selector,
                emergency_uses_spent=initial_state.emergency_uses,
            )
        )
        game = HeadlessGame(
            seed=initial_state.seed,
            game_map=self._game_map,
            agent_factory=factory,
            replay_path=None,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=self._tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=self._max_ticks),
            meeting_runner=self._build_meeting_runner(),
            rng_hash_policy=self._rng_hash_policy,
            initial_state=initial_state,
        )
        # ``tasks_per_crewmate`` above only feeds ``seed_initial_state``, which
        # the injected path bypasses; the episode record below carries the
        # state-derived count instead.
        result = game.run_unrecorded()
        if result.outcome == "MEETING_PHASE_REACHED":
            # Structurally unreachable: a runner is ALWAYS installed. Fail loud if
            # the invariant is ever violated rather than silently truncate.
            raise RuntimeError(
                "TacticalRolloutEnv reached MEETING_PHASE_REACHED with a meeting "
                "runner installed; the always-installed-runner invariant is broken"
            )
        return self._episode_from_unrecorded(
            result,
            initial_state.seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )

    def _episode_from_unrecorded(
        self,
        result: UnrecordedGameResult,
        seed: int,
        *,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
    ) -> EpisodeRollout:
        """Assemble a typed :class:`EpisodeRollout` from a no-replay live trace.

        The no-replay path (Task 15.8.1) writes no replay, so there is nothing for
        :func:`training.rollout.reconstruct_episode` to walk. This mirrors that
        walk's ASSEMBLY — the ``initial`` / ``tick`` / ``meeting`` frame chain, the
        typed event log, the meeting records, the behavioral descriptors, and the
        terminal-shape logic — but reads the already-captured live trajectory
        instead of re-running ``advance_tick`` and verifying recorded hashes: the
        captured states ARE the engine truth.

        The per-frame ``state_hash`` is SKIPPED on the fast path: the fast rng
        rollout never verifies these hashes (there is no replay to verify
        against), so stable-JSON-serializing the full ``WorldState`` per frame
        would re-pay exactly the per-tick serialization cost the fast path exists
        to avoid, and the reward channel / descriptors read frame SCALARS + events
        rather than the hash. Fast-path frames therefore carry an empty
        ``state_hash`` placeholder. The FULL no-replay path keeps a real hash, so
        it stays byte-identical to :func:`reconstruct_episode` (including the
        state-hash chain).
        """

        episode_boundary = self._episode_boundary
        # Skip the full-WorldState serialization on the fast training path (see
        # docstring); FULL no-replay keeps real, reconstruct-comparable hashes.
        skip_state_hash = self._rng_hash_policy is RngStateHashPolicy.TRAINING_FAST

        def _frame_hash(state: WorldState) -> str:
            return "" if skip_state_hash else _state_hash(state)

        initial_state = result.initial_state
        roles: dict[PlayerId, Role] = {
            pid: player.role for pid, player in initial_state.players.items()
        }
        meeting_by_trigger = {step.trigger_tick: step for step in result.meeting_steps}

        events: list[EngineEvent] = []
        meetings: list[MeetingRecord] = []
        cumulative_kills = 0
        do_task_emissions = 0
        winner: WinnerSide | None = None
        win_reason: str | None = None
        truncated = False
        outcome: EpisodeOutcome
        # The staged tick for an injected episode (Task 18.23); 0 on the seeded
        # default path, so a zero-step episode still reports a truthful final
        # tick.
        final_tick = initial_state.tick

        # The seeded pre-action state opens the frame chain (kind="initial"),
        # exactly like reconstruct_episode, so the potential series telescopes
        # over the real episode start.
        frames: list[EpisodeFrame] = [
            _frame(
                initial_state,
                tick=initial_state.tick,
                kind="initial",
                state_hash=_frame_hash(initial_state),
                roles=roles,
                cumulative_kills=cumulative_kills,
            )
        ]

        for step in result.tick_steps:
            do_task_emissions += sum(
                1 for action in step.actions if isinstance(action, DoTaskAction)
            )
            for event in step.events:
                events.append(event)
                if isinstance(event, KilledEvent):
                    cumulative_kills += 1
                elif isinstance(event, GameOverEvent):
                    winner = event.winner
                    win_reason = event.reason
            final_tick = step.state.tick
            frames.append(
                _frame(
                    step.state,
                    tick=step.input_tick,
                    kind="tick",
                    state_hash=_frame_hash(step.state),
                    roles=roles,
                    cumulative_kills=cumulative_kills,
                )
            )

            if step.state.phase == "GAME_OVER":
                break
            if step.state.phase != "MEETING":
                continue

            trigger_event = next(
                (e for e in step.events if isinstance(e, MeetingTriggeredEvent)),
                None,
            )
            if trigger_event is None:
                raise RolloutReconstructionError(
                    f"seed {seed}: tick {step.input_tick} entered MEETING with no "
                    "MeetingTriggeredEvent in the captured events"
                )

            if episode_boundary == "first_meeting":
                # The deliberate 15.13 fallback-(b) boundary: stop at the first
                # meeting trigger, MARK truncated, do NOT record the (already
                # applied) outcome — a pre-meeting training record must not leak a
                # post-boundary ejection.
                boundary_step = meeting_by_trigger.get(step.input_tick)
                meetings.append(
                    MeetingRecord(
                        tick=step.input_tick,
                        meeting_id=boundary_step.result.meeting_id
                        if boundary_step is not None
                        else f"seed-{seed}:meeting-{step.input_tick}",
                        trigger=trigger_event.trigger,
                        triggered_by=trigger_event.actor,
                        outcome=None,
                        ejected_player_id=None,
                    )
                )
                truncated = True
                break

            meeting_step = meeting_by_trigger.get(step.input_tick)
            if meeting_step is None:
                raise RolloutReconstructionError(
                    f"seed {seed}: tick {step.input_tick} entered MEETING but the "
                    "captured trace carries no meeting step for that tick"
                )
            for event in meeting_step.post_events:
                events.append(event)
                if isinstance(event, GameOverEvent):
                    winner = event.winner
                    win_reason = event.reason
            meetings.append(
                MeetingRecord(
                    tick=step.input_tick,
                    meeting_id=meeting_step.result.meeting_id,
                    trigger=trigger_event.trigger,
                    triggered_by=meeting_step.result.triggered_by,
                    outcome=meeting_step.result.outcome,
                    ejected_player_id=meeting_step.result.ejected_player_id,
                )
            )
            final_tick = meeting_step.state.tick
            frames.append(
                _frame(
                    meeting_step.state,
                    # apply_meeting_result resumes at trigger_tick + 1, so the
                    # post-meeting frame is stamped with the RESUMED tick.
                    tick=meeting_step.state.tick,
                    kind="meeting",
                    state_hash=_frame_hash(meeting_step.state),
                    roles=roles,
                    cumulative_kills=cumulative_kills,
                )
            )
            if meeting_step.state.phase == "GAME_OVER":
                break

        if truncated:
            outcome = "FIRST_MEETING"
        elif winner is not None:
            outcome = winner
        else:
            # No GameOverEvent and no first-meeting cut: the scheduler capped it.
            outcome = "TICK_BUDGET"
            truncated = True

        # Cross-check the reconstructed winner against the game's own terminal
        # outcome (both derive from the SAME GameOverEvent, so a mismatch is a
        # capture bug, not a drift — there is no recorded row to compare against).
        if (
            not truncated
            and winner is not None
            and result.outcome in ("CREWMATES", "IMPOSTORS")
            and result.outcome != winner
        ):
            raise RolloutReconstructionError(
                f"seed {seed}: captured winner {winner!r} != game outcome "
                f"{result.outcome!r}"
            )

        # Rate descriptors (meeting_trigger_rate, do_task_cadence) normalize
        # over the CAPTURED horizon: an injected episode's clock starts at the
        # staged tick, so the absolute final_tick would dilute its rates by
        # ticks the episode never saw (Task 18.23). On the seeded default path
        # the staged tick is 0, so this is the pre-18.23 value exactly;
        # ``EpisodeRollout.final_tick`` below stays absolute.
        descriptors = _build_descriptors(
            events=events,
            meetings=meetings,
            do_task_emissions=do_task_emissions,
            final_tick=final_tick - initial_state.tick,
            roles=roles,
            outcome=outcome,
            winner=winner,
            win_reason=win_reason,
        )

        return EpisodeRollout(
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            episode_boundary=episode_boundary,
            truncated=truncated,
            outcome=outcome,
            winner=None if truncated else winner,
            win_reason=None if truncated else win_reason,
            final_tick=final_tick,
            roles=roles,
            frames=tuple(frames),
            events=tuple(events),
            meetings=tuple(meetings),
            descriptors=descriptors,
        )


__all__ = [
    "ActionMask",
    "IntentSelector",
    "MaskedDecision",
    "TacticalRolloutEnv",
    "build_action_mask",
    "build_interposition_factory",
]
