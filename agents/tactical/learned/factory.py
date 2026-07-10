"""The opt-in learned agent factory beside the scripted default (Task 15.20).

:func:`build_learned_agent_factory` productizes the bake-off's
``build_candidate_factory`` wrapper pattern
(``training/bakeoff/harness.py``): every agent is a real role-appropriate
production ``TacticalAgent``, impostors wrapped so the champion's learned
utility scorer arbitrates the FSM's own option menu on every impostor
decision, crew delegate to the scripted FSM unchanged, and the meeting
protocol (plus the belief-fold hooks) forwards to the wrapped inner agent via
``__getattr__`` — the 15.8/15.10/15.15 wrapper idiom, not a new agent class.

Firewall shape: the production ``TacticalAgent`` lives in
``orchestrator/game.py``, which ``agents/`` may not import (the chain
``agents → orchestrator → engine`` would breach the observation firewall), so
the factory takes the inner-agent construction as an INJECTED callable
(:data:`InnerAgentFactory`) satisfying the structural
:class:`WrappableTacticalAgent` protocol. Callers that may import the
orchestrator (15.21's CLI in ``scripts/``, the acceptance tests) pass a
one-liner building the real ``TacticalAgent`` per player; this module stays
engine-free and imports on a bare tree.

Provenance: the factory exposes the five stamp fields as PLAIN STRINGS on the
engine-free :class:`LearnedPolicyStamp` record. Importing
``orchestrator.replay.TacticalPolicyStamp`` here would break the firewall
contract, so the real stamp object is constructed by 15.21's CLI in
``scripts/`` from these fields; ``weights_sha256`` is always the verified
digest of the committed artifact actually loaded (never a hard-coded
constant), so the recording surfaces cannot mis-stamp.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final, Protocol, TypeAlias, runtime_checkable

from pydantic import BaseModel, ConfigDict

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.tactical.learned.forward import (
    ENCODER_VERSION,
    LearnedDecisionFrame,
    LearnedImpostorScorer,
)
from agents.tactical.learned.weights import (
    committed_weights_sha256,
    load_champion_weights,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket, PlayerId, Role
from observation.public_map import PublicMapView

# The champion's five stamp-field values (audits/audit-phase-15-pause.md
# decision 1). ``policy_id`` is the bake-off entrant name the audit locked;
# ``method`` is the single-line training-method token for "learned utility
# scorer over FSM-proposed options + (1+λ)-ES"; the anchor is the frozen
# scripted FSM — ``orchestrator.replay.FSM_DEFAULT_POLICY_ID``'s value,
# restated here as a literal because that module is behind the firewall.
CHAMPION_POLICY_ID: Final[str] = "utility-es"
CHAMPION_METHOD: Final[str] = "utility-scorer-es"
CHAMPION_ANCHOR_POLICY: Final[str] = "fsm-default"


class LearnedPolicyStamp(BaseModel):
    """The five tactical-policy stamp fields, as plain strings (Task 15.20).

    An engine-free local record mirroring the field names of
    ``orchestrator.replay.TacticalPolicyStamp`` WITHOUT importing it (the
    ``agents → orchestrator → engine`` chain is firewall-forbidden). 15.21's
    CLI in ``scripts/`` — which may import the orchestrator freely —
    constructs the real stamp object from these fields; ``weights_sha256`` is
    the committed sidecar digest of the artifact the factory actually loaded.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str
    method: str
    encoder_version: str
    weights_sha256: str
    anchor_policy: str


@runtime_checkable
class WrappableTacticalAgent(Protocol):
    """The inner-agent surface the learned wrapper needs (structural).

    The production ``orchestrator.game.TacticalAgent`` satisfies this: the
    wrapper drives ``decide`` first (so perception populates the agent's OWN
    :class:`~agents.memory.store.AgentMemory` exactly as in production and the
    FSM's proposal is available), then reads ``memory`` for the option menu.
    Everything else (the meeting protocol, the belief-fold hooks) forwards via
    ``__getattr__`` untyped, exactly as the bake-off's ``_CandidateAgent``
    forwards it.
    """

    @property
    def memory(self) -> AgentMemory: ...

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent: ...


# The injected inner-agent constructor: ``(agent_id, role) -> TacticalAgent``.
# Injection (not an orchestrator import) is what keeps this module engine-free.
InnerAgentFactory: TypeAlias = Callable[[PlayerId, Role], WrappableTacticalAgent]

# Per-decision observer over the learned scorer's engine-free frames — the
# seam the acceptance tests hash the (feature, score, intent) stream through.
FrameCallback: TypeAlias = Callable[[LearnedDecisionFrame], None]


class _LearnedAgent:
    """Interposition wrapper driving the champion through the production loop.

    Mirrors the bake-off's ``_CandidateAgent``: drives the inner FSM agent
    first (so perception + the agent's OWN memory populate exactly as in
    production), then — for IMPOSTOR decisions only; the crew side stays the
    frozen scripted FSM — evaluates the learned scorer off the inner agent's
    live memory and lets its intent drive the game. The menu is structurally
    unable to emit an off-vocabulary intent (every option is one the FSM
    itself would generate in the same state), so no mask re-validation is
    needed here — the bake-off wrapper's mask check was harness plumbing
    (``training.env``), which ``agents/`` may not import.
    """

    def __init__(
        self,
        inner: WrappableTacticalAgent,
        *,
        scorer: LearnedImpostorScorer,
        on_frame: FrameCallback | None,
    ) -> None:
        self._inner = inner
        self._scorer = scorer
        self._on_frame = on_frame

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        fsm_intent = self._inner.decide(packet, public_map)
        if packet.self_state.role != "IMPOSTOR":
            return fsm_intent
        frame = self._scorer.evaluate(
            packet, public_map, self._inner.memory, fsm_intent=fsm_intent
        )
        if self._on_frame is not None:
            self._on_frame(frame)
        return frame.intent

    def __getattr__(self, name: str) -> object:
        # Delegate the MeetingAwareAgent protocol + belief-fold hooks to the
        # inner TacticalAgent (the 15.8/15.10/15.15 wrapper idiom).
        return getattr(self._inner, name)


class LearnedAgentFactory:
    """The champion's agent factory: a callable ``(agent_id, role) -> agent``.

    Structurally an ``orchestrator.game.AgentFactory`` (same ``(PlayerId,
    Role) -> AgentInterface`` shape over the engine-free aliases), plus the
    :attr:`stamp` accessor 15.21's CLI reads its five provenance strings from.
    Construct via :func:`build_learned_agent_factory`.
    """

    def __init__(
        self,
        inner_factory: InnerAgentFactory,
        *,
        scorer: LearnedImpostorScorer,
        stamp: LearnedPolicyStamp,
        on_frame: FrameCallback | None,
    ) -> None:
        self._inner_factory = inner_factory
        self._scorer = scorer
        self._stamp = stamp
        self._on_frame = on_frame

    @property
    def stamp(self) -> LearnedPolicyStamp:
        """The five plain-string stamp fields for the loaded champion."""

        return self._stamp

    @property
    def scorer(self) -> LearnedImpostorScorer:
        """The frozen scorer every agent this factory builds shares."""

        return self._scorer

    def __call__(self, agent_id: PlayerId, role: Role) -> AgentInterface:
        inner = self._inner_factory(agent_id, role)
        return _LearnedAgent(inner, scorer=self._scorer, on_frame=self._on_frame)


def build_learned_agent_factory(
    inner_factory: InnerAgentFactory,
    *,
    on_frame: FrameCallback | None = None,
) -> LearnedAgentFactory:
    """Build the opt-in learned factory around the committed champion (15.20).

    Loads the committed ``utility-es`` weights (sha-verified on load, fail
    loud) and returns a :class:`LearnedAgentFactory` that wraps every agent
    ``inner_factory`` constructs: impostors run the learned scorer over the
    FSM's own option menu, crew delegate to the FSM, the meeting protocol
    forwards to the wrapped inner agent. The scripted FSM default
    (``orchestrator.game.build_default_agent_factory``) stays untouched beside
    this — the anchor, the BC oracle, and the fallback (decision 2, branch A).

    ``inner_factory`` builds the real production inner agent per player —
    e.g. ``lambda agent_id, role: TacticalAgent(agent_id=agent_id,
    policy=<role FSM policy>, role=role)`` — and is injected because this
    module may not import the orchestrator. ``on_frame`` observes every
    impostor decision's engine-free :class:`LearnedDecisionFrame` (the
    determinism-stream seam); pass ``None`` in production.
    """

    scorer = LearnedImpostorScorer(weights=load_champion_weights())
    stamp = LearnedPolicyStamp(
        policy_id=CHAMPION_POLICY_ID,
        method=CHAMPION_METHOD,
        encoder_version=ENCODER_VERSION,
        weights_sha256=committed_weights_sha256(),
        anchor_policy=CHAMPION_ANCHOR_POLICY,
    )
    return LearnedAgentFactory(
        inner_factory, scorer=scorer, stamp=stamp, on_frame=on_frame
    )


__all__ = [
    "CHAMPION_ANCHOR_POLICY",
    "CHAMPION_METHOD",
    "CHAMPION_POLICY_ID",
    "FrameCallback",
    "InnerAgentFactory",
    "LearnedAgentFactory",
    "LearnedPolicyStamp",
    "WrappableTacticalAgent",
    "build_learned_agent_factory",
]
