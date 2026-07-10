"""The 15.10 acceptance stack through ``build_learned_agent_factory`` (15.20).

The 15.15 lesson: acceptance through one's OWN factory is what makes the
result transferable — so every run here goes through the real
:func:`agents.tactical.learned.factory.build_learned_agent_factory` (or, for
the 15.10 harness whose seam is a :class:`training.determinism.FramePolicy`,
through the real shipped scorer behind a frame-type adapter — the scorer
computes everything; the adapter only re-wraps the engine-free frame record
into the training-side ``PolicyFrame``):

1. The 15.10 determinism harness — double-run hash equality over the
   ``(feature, score, intent)`` stream plus frozen-policy full-game
   state-hash equality.
2. A literal factory-level double-run: two identical full games through
   ``build_learned_agent_factory()`` itself, asserting the recorded frame
   stream and the replay state-hash chain are bit-identical.
3. The leak-test factory mode (``eval.leak_test.scan_factory_packets``)
   through the learned factory.
4. The five plain-string stamp fields, pinned to the committed sidecar digest
   and constructible into the real ``orchestrator.replay.TacticalPolicyStamp``
   (the 15.21 path).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from agents.memory.store import AgentMemory
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from agents.tactical.learned.factory import (
    LearnedAgentFactory,
    LearnedPolicyStamp,
    build_learned_agent_factory,
)
from agents.tactical.learned.forward import (
    ENCODER_VERSION,
    LearnedDecisionFrame,
    LearnedImpostorScorer,
)
from agents.tactical.learned.weights import (
    committed_weights_sha256,
    load_champion_weights,
)
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from eval.leak_test import scan_factory_packets
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    TacticalPolicyStamp,
    read_all_entries,
)
from orchestrator.scheduler import TickScheduler
from training.determinism import PolicyFrame, run_policy_determinism

# The committed champion digest (audits/audit-phase-15-pause.md decision 1).
_COMMITTED_SHA256: Final[str] = (
    "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"
)

# The canonical 9p2i bake-off roster the champion was trained and evaluated on.
_NUM_PLAYERS: Final[int] = 9
_NUM_IMPOSTORS: Final[int] = 2
_TASKS_PER_CREWMATE: Final[int] = 2

# One committed determinism seed (the 15.15 protocol's CI budget) — the 15.10
# harness and the factory-level double-run each replay it twice.
_DETERMINISM_SEED: Final[int] = 1004


def _inner_factory(agent_id: PlayerId, role: Role) -> TacticalAgent:
    """The injected inner-agent constructor: the REAL production agent.

    Exactly the per-player construction ``build_default_agent_factory`` /
    ``build_candidate_factory`` perform — the orchestrator-owned
    :class:`TacticalAgent` around the role-appropriate scripted FSM. Injected
    because ``agents/tactical/learned/`` may not import the orchestrator; this
    is the same one-liner 15.21's CLI passes.
    """

    policy: CrewmatePolicy | ImpostorPolicy
    if role == "IMPOSTOR":
        policy = ImpostorPolicy(agent_id=agent_id)
    else:
        policy = CrewmatePolicy(agent_id=agent_id)
    return TacticalAgent(agent_id=agent_id, policy=policy, role=role)


class _ShippedScorerFramePolicy:
    """The shipped scorer behind the 15.10 ``FramePolicy`` seam.

    Not a test double: the real :class:`LearnedImpostorScorer` computes every
    feature, score, and intent; this adapter only re-wraps its engine-free
    :class:`LearnedDecisionFrame` into the training-side :class:`PolicyFrame`
    the harness hashes (``agents/`` may not import ``training/``, so the
    shipped frame record cannot BE a ``PolicyFrame``).
    """

    def __init__(self, scorer: LearnedImpostorScorer) -> None:
        self._scorer = scorer

    @property
    def encoder_version(self) -> str:
        return self._scorer.encoder_version

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        frame = self._scorer.evaluate(packet, public_map, memory, fsm_intent=fsm_intent)
        return PolicyFrame(
            agent_id=frame.agent_id,
            tick=frame.tick,
            features=frame.features,
            logits=frame.scores,
            intent=frame.intent,
        )


def _run_factory_game(
    factory: LearnedAgentFactory, *, seed: int, replay_path: Path
) -> None:
    """One full production game through the learned factory (fake provider)."""

    game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=factory,
        replay_path=replay_path,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS_PER_CREWMATE,
        scheduler=TickScheduler(max_ticks=DEFAULT_MAX_TICKS),
        meeting_runner=build_default_meeting_runner(
            llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
        ),
        force=True,
    )
    game.run()


def _serialize_frame(frame: LearnedDecisionFrame) -> str:
    """Bit-exact frame serialization (the 15.10 float-hex idiom)."""

    return json.dumps(
        {
            "tick": frame.tick,
            "agent_id": frame.agent_id,
            "features": [value.hex() for value in frame.features],
            "scores": [value.hex() for value in frame.scores],
            "intent": frame.intent.model_dump(mode="json"),
        },
        sort_keys=True,
    )


def _state_hash_chain(replay_path: Path) -> list[str]:
    """The COMPLETE recorded state-hash chain: tick rows + meeting before/after."""

    chain: list[str] = []
    for entry in read_all_entries(replay_path):
        if isinstance(entry, ReplayEntry):
            chain.append(f"tick:{entry.tick}:{entry.state_hash}")
        elif isinstance(entry, MeetingReplayEntry):
            chain.append(f"meeting_before:{entry.tick}:{entry.state_hash_before}")
            chain.append(f"meeting_after:{entry.tick}:{entry.state_hash_after}")
    return chain


def test_learned_scorer_passes_the_15_10_determinism_harness() -> None:
    policy = _ShippedScorerFramePolicy(
        LearnedImpostorScorer(weights=load_champion_weights())
    )
    report = run_policy_determinism(
        policy,
        seeds=(_DETERMINISM_SEED,),
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS_PER_CREWMATE,
    )
    assert report.deterministic is True
    assert report.encoder_version == ENCODER_VERSION
    assert report.num_frames > 0
    assert report.num_state_hashes > 0


def test_learned_factory_double_run_is_bit_identical(tmp_path: Path) -> None:
    # The literal through-the-real-factory determinism check: two identical
    # full games through build_learned_agent_factory() itself must record a
    # bit-identical (feature, score, intent) stream AND drive the engine down
    # a bit-identical state-hash chain.
    streams: list[list[str]] = []
    chains: list[list[str]] = []
    for run in range(2):
        sink: list[LearnedDecisionFrame] = []
        factory = build_learned_agent_factory(_inner_factory, on_frame=sink.append)
        replay_path = tmp_path / f"run-{run}.jsonl"
        _run_factory_game(factory, seed=_DETERMINISM_SEED, replay_path=replay_path)
        ordered = sorted(sink, key=lambda frame: (frame.tick, frame.agent_id))
        streams.append([_serialize_frame(frame) for frame in ordered])
        chains.append(_state_hash_chain(replay_path))

    assert streams[0], "the learned factory recorded no impostor decisions"
    assert streams[0] == streams[1]
    assert chains[0], "the replay recorded no state hashes"
    assert chains[0] == chains[1]


def test_learned_factory_passes_the_leak_test_factory_mode() -> None:
    factory = build_learned_agent_factory(_inner_factory)
    scanned = scan_factory_packets(factory)
    assert scanned > 0, "learned factory mode captured no packets"


def test_stamp_fields_are_plain_strings_pinned_to_the_committed_sidecar() -> None:
    factory = build_learned_agent_factory(_inner_factory)
    stamp = factory.stamp
    assert isinstance(stamp, LearnedPolicyStamp)
    # The engine-free record lives under agents/ — never orchestrator.replay's
    # TacticalPolicyStamp (that import would chain agents -> orchestrator ->
    # engine through the firewall).
    assert LearnedPolicyStamp.__module__ == "agents.tactical.learned.factory"
    fields = (
        stamp.policy_id,
        stamp.method,
        stamp.encoder_version,
        stamp.weights_sha256,
        stamp.anchor_policy,
    )
    assert fields == (
        "utility-es",
        "utility-scorer-es",
        "impostor-option-features-v1",
        _COMMITTED_SHA256,
        "fsm-default",
    )
    for value in fields:
        assert type(value) is str
    assert stamp.weights_sha256 == committed_weights_sha256()
    # The 15.21 construction path: the real stamp object builds from the five
    # plain strings (and its validators accept them).
    real_stamp = TacticalPolicyStamp(
        policy_id=stamp.policy_id,
        method=stamp.method,
        encoder_version=stamp.encoder_version,
        weights_sha256=stamp.weights_sha256,
        anchor_policy=stamp.anchor_policy,
    )
    assert real_stamp.weights_sha256 == _COMMITTED_SHA256


def test_factory_wraps_the_real_tactical_agent_and_forwards_its_protocol() -> None:
    factory = build_learned_agent_factory(_inner_factory)
    # The scorer accessor carries the committed champion genome verbatim.
    assert factory.scorer.weights == load_champion_weights()
    agent = factory("p-1", "IMPOSTOR")
    # The meeting protocol + belief-fold hooks resolve to the wrapped inner
    # TacticalAgent via __getattr__ (the 15.8/15.10/15.15 wrapper idiom).
    assert isinstance(getattr(agent, "memory"), AgentMemory)
    assert callable(getattr(agent, "render_memory_for_meeting"))
    assert callable(getattr(agent, "suspicion_graph_for_meeting"))
    assert callable(getattr(agent, "vent_witness_records_for_meeting"))
