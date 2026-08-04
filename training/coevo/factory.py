"""FROZEN (Phase 19 tier map, training/README.md): concluded campaign machinery.
Bug fixes and evidence readers only; no new search.

The dual-role co-evolution factory (Task 18.19).

Where ``training.bakeoff.harness.build_candidate_factory`` interposes IMPOSTOR
decisions only (crew frozen to the scripted FSM) and
``training.crew.scorer.build_crew_candidate_factory`` interposes CREW decisions
only (impostors frozen to the scripted FSM), :func:`build_coevo_factory`
composes both into ONE game: a ROLE BRANCH over the two EXISTING wrappers, not
a new agent class (the task hint — the wrappers are imported/mirrored, never
rewired). An impostor agent is wrapped in the harness's private
``_CandidateAgent`` (harness.py:548-626, which overrides IMPOSTOR decisions
against ``impostor_policy`` and delegates every other role to the FSM); a crew
agent is wrapped in the scorer's private ``_CrewCandidateAgent``
(scorer.py:712-845, which overrides CREW decisions against ``crew_policy``,
carries the per-agent emergency-uses tracker, and delegates every other role to
the FSM). Because each wrapper already role-gates internally and only ever
overrides its own role, wrapping impostors with the impostor wrapper and crew
with the crew wrapper yields exactly the dual behavior with byte-identical
single-side parity: with one side's policy ``None`` its wrapper is a
transparent FSM delegate, so the game reduces to the corresponding single-side
factory's trajectory (the DoD "every single-side path byte-identical").

The one runtime discriminator between the two structurally near-identical
``BakeoffPolicy`` / ``CrewTrackPolicy`` ``runtime_checkable`` Protocols is the
encoder-version NAMESPACE: every crew encoder tag starts with
:data:`CREW_ENCODER_NAMESPACE_PREFIX` (``crew-option-features-v1``,
``crew-option-features-v2``, ``crew-fsm-delegate-v1``) and no impostor tag does
(``impostor-option-features-v1``, ``v2``). The conflation guard keys on that
prefix and fails loud at factory-build time — BEFORE any game runs — so a crew
policy handed to the impostor slot (or vice versa) raises rather than silently
scoring the wrong side (AGENTS.md: no silent fallbacks).
"""

from __future__ import annotations

from typing import Final

from agents.base import AgentInterface
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import Map
from orchestrator.game import AgentFactory, TacticalAgent
from training.bakeoff.harness import BakeoffPolicy, DecisionTrace, _CandidateAgent
from training.crew.scorer import (
    CrewDecisionTrace,
    CrewTrackPolicy,
    _CrewCandidateAgent,
)

# The crew encoder-version namespace: every committed crew featurizer tag begins
# with this prefix (``crew-option-features-v1`` / ``crew-option-features-v2`` /
# ``crew-fsm-delegate-v1``) and no impostor tag does (``impostor-option-features-v1``,
# the masked-MLP family's ``v2``). It is the ONLY runtime identity distinguishing
# the two policy families — ``BakeoffPolicy`` and ``CrewTrackPolicy`` are
# structurally near-identical Protocols — so the conflation guard keys on it.
CREW_ENCODER_NAMESPACE_PREFIX: Final[str] = "crew-"


def build_coevo_factory(
    impostor_policy: BakeoffPolicy | None,
    crew_policy: CrewTrackPolicy | None,
    *,
    game_map: Map,
    impostor_trace: DecisionTrace | None = None,
    crew_trace: CrewDecisionTrace | None = None,
) -> AgentFactory:
    """The dual-role co-evo factory (Task 18.19).

    Builds every agent as the exact production role-appropriate
    :class:`~orchestrator.game.TacticalAgent` both single-side factories build —
    IMPOSTOR gets an :class:`~agents.tactical.impostor_policy.ImpostorPolicy`
    inner, else a :class:`~agents.tactical.crewmate_policy.CrewmatePolicy` inner
    — then ROLE-BRANCHES the interposition: an impostor is wrapped in
    ``_CandidateAgent`` (harness.py:629-662's ``build_candidate_factory``
    construction) so ``impostor_policy`` overrides its IMPOSTOR decisions and
    feeds ``impostor_trace``; a crew agent is wrapped in ``_CrewCandidateAgent``
    (scorer.py:848-888's ``build_crew_candidate_factory`` construction) so
    ``crew_policy`` overrides its CREW decisions, feeds ``crew_trace``, and runs
    the per-agent emergency-uses tracker off
    ``game_map.emergency.uses_per_player``. ``sabotage_kinds`` is
    ``tuple(sorted(game_map.sabotages))`` (both wrappers take it); the closure
    records the engine-truth roster into ``roles`` per construction (the
    ``build_crew_candidate_factory`` idiom), which reaches only the crew
    wrapper's Q6 diagnostic — kept ``None`` here — never a policy input.

    ``None``/``None`` is legal: with both policies absent every wrapper is a
    transparent FSM delegate and the game is the fully scripted FSM on both
    sides — the absolute-anchor benchmark shape Task 18.21 consumes.

    CONFLATION GUARD (fail loud, ``ValueError``, at build time — BEFORE any game
    runs): ``BakeoffPolicy`` and ``CrewTrackPolicy`` are structurally
    near-identical ``runtime_checkable`` Protocols, so the encoder-version
    namespace is the ONLY runtime identity that tells the two families apart. A
    crew policy (``encoder_version`` starting :data:`CREW_ENCODER_NAMESPACE_PREFIX`)
    in the impostor slot, or a non-crew policy in the crew slot, raises here
    rather than silently scoring the wrong side — the prefix convention is pinned
    by the three committed crew tags + two impostor tags.
    """

    if impostor_policy is not None and impostor_policy.encoder_version.startswith(
        CREW_ENCODER_NAMESPACE_PREFIX
    ):
        raise ValueError(
            "conflation guard (Task 18.19): a crew policy "
            f"(encoder_version={impostor_policy.encoder_version!r}) in the "
            "impostor slot of build_coevo_factory — the impostor slot takes a "
            "BakeoffPolicy whose encoder tag never starts with "
            f"{CREW_ENCODER_NAMESPACE_PREFIX!r}. Pass it as crew_policy instead."
        )
    if crew_policy is not None and not crew_policy.encoder_version.startswith(
        CREW_ENCODER_NAMESPACE_PREFIX
    ):
        raise ValueError(
            "conflation guard (Task 18.19): a non-crew policy "
            f"(encoder_version={crew_policy.encoder_version!r}) in the crew slot "
            "of build_coevo_factory — every crew encoder tag starts with "
            f"{CREW_ENCODER_NAMESPACE_PREFIX!r} (the committed "
            "crew-option-features-v1 / crew-option-features-v2 / "
            "crew-fsm-delegate-v1 tags); a BakeoffPolicy (impostor-option-features-v1, "
            "the masked-MLP family's v2) belongs in the impostor slot."
        )

    sabotage_kinds = tuple(sorted(game_map.sabotages))
    emergency_uses = game_map.emergency.uses_per_player
    roles: dict[PlayerId, Role] = {}

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        roles[agent_id] = role
        policy_impl: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy_impl = ImpostorPolicy(agent_id=agent_id)
        else:
            policy_impl = CrewmatePolicy(agent_id=agent_id)
        inner = TacticalAgent(agent_id=agent_id, policy=policy_impl, role=role)
        if role == "IMPOSTOR":
            return _CandidateAgent(
                inner,
                policy=impostor_policy,
                sabotage_kinds=sabotage_kinds,
                trace=impostor_trace,
                on_decision=None,
            )
        return _CrewCandidateAgent(
            inner,
            policy=crew_policy,
            sabotage_kinds=sabotage_kinds,
            emergency_uses_per_player=emergency_uses,
            trace=crew_trace,
            diagnostic=None,
            roles=roles,
        )

    return factory
