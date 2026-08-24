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

Task 18.7 (audits/audit-phase-18-planning.md §4 #7) adds the CREW TWIN of this
stack for the opt-in crew deployment surface: the same four obligations against
the shipped ``agents.tactical.learned.crew_forward.LearnedCrewScorer`` and its
``build_learned_crew_factory`` — artifact parity against the committed
``crew-owned-tasks-es`` genome, the crew edition of the Q4 bit-exact gate
(against ``training.crew.scorer.CrewOptionScorer`` over the widened owned-task
basis, driven through the training-side ``rollout_crew_candidate`` so the game is
exactly a training-candidate rollout), the factory-level determinism double-run,
and the leak-mode scan — plus the two obligations the impostor wrapper never had:
the crew stamp's ``orchestrator.replay.CrewTacticalPolicyStamp`` constructibility
and the impostor-champion conflation guard, and the wrapper's override
re-validation against the submission mask (the mask-violation fail-loud case, the
legal-override and owned-task ``do_task`` accepts) plus the emergency-uses
bookkeeping carried across meetings via the meeting-concluded hook. The crew
block lives in its own clearly-sectioned suite below; every impostor test above
is untouched.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Final

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from agents.tactical.learned.crew_forward import (
    CREW_CHAMPION_WEIGHTS_PATH,
    CREW_CHAMPION_WEIGHTS_SIDECAR_PATH,
    CREW_ENCODER_VERSION,
    CREW_GENOME_LENGTH,
    OWNED_TASK_OPTION_FEATURE_NAMES,
    LearnedCrewScorer,
    _build_action_mask,
    committed_crew_weights_sha256,
    load_crew_champion_weights,
)
from agents.tactical.learned.factory import (
    FrameCallback,
    LearnedAgentFactory,
    LearnedCrewAgentFactory,
    LearnedCrewPolicyStamp,
    LearnedPolicyStamp,
    _LearnedCrewAgent,
    build_learned_agent_factory,
    build_learned_crew_factory,
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
from engine.world import Map, load_canonical_map
from eval.leak_test import scan_factory_packets
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    MoveIntent,
    WaitIntent,
)
from observation.packet import GlobalView, ObservationPacket, SelfView
from observation.public_map import PublicMapView
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    CrewTacticalPolicyStamp,
    MeetingReplayEntry,
    ReplayEntry,
    TacticalPolicyStamp,
    read_all_entries,
)
from orchestrator.scheduler import TickScheduler
from training.bakeoff.harness import load_candidate_weights
from training.crew.options import (
    OWNED_TASK_OPTION_FEATURE_NAMES as TRAINING_OWNED_TASK_OPTION_FEATURE_NAMES,
)
from training.crew.options import (
    OwnedTaskOptionBasis,
)
from training.crew.scorer import (
    CrewOptionScorer,
    CrewTrackPolicy,
    rollout_crew_candidate,
)
from training.determinism import PolicyFrame, run_policy_determinism
from training.env import build_action_mask as training_build_action_mask

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
    factory: LearnedAgentFactory | LearnedCrewAgentFactory,
    *,
    seed: int,
    replay_path: Path,
) -> None:
    """One full production game through the learned factory (fake provider).

    Accepts either the impostor factory (:class:`LearnedAgentFactory`) or the
    Task-18.7 crew factory (:class:`LearnedCrewAgentFactory`) — both are the same
    ``(agent_id, role) -> AgentInterface`` orchestrator ``AgentFactory`` shape, so
    the crew determinism double-run reuses this helper verbatim. The parameter
    type is widened (never narrowed), so the impostor callers are unaffected.
    """

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


# =========================================================================== #
# THE CREW TWIN (Task 18.7; audits/audit-phase-18-planning.md §4 #7).          #
#                                                                              #
# The opt-in crew deployment surface's acceptance stack: the same four         #
# obligations the impostor block above pins, against the shipped               #
# ``LearnedCrewScorer`` / ``build_learned_crew_factory``, plus the two the     #
# impostor wrapper never carried (the crew stamp + conflation guard, and the   #
# override re-validation / emergency bookkeeping). Every fixture is surgical    #
# and firewall-agnostic (a test may import ``training/`` and ``engine/``); the  #
# Q4 gate and the determinism double-run drive full production games.          #
# =========================================================================== #

# The committed crew artifact digest (audits/audit-phase-18-planning.md §4 #7);
# sha256 of ``training/artifacts/crew/crew-owned-tasks-es/weights.json``.
_CREW_COMMITTED_SHA256: Final[str] = (
    "bd6fdd0a030a01cc57f2ef8c95abf66f46d8cbc5ac270e04ae74a6cab587f19c"
)
_CREW_TRAINING_ARTIFACT_DIR: Final[Path] = Path(
    "training/artifacts/crew/crew-owned-tasks-es"
)

# The crew Q4 gate's recorded-decision-stream seeds — the crew eval protocol's
# committed determinism seeds (``CrewProtocolConfig.determinism_seeds``), full
# 9p2i games so the widened owned-task menu exercises multi-option argmaxes.
_CREW_Q4_SEEDS: Final[tuple[int, ...]] = (1004, 1009)


def _crew_hex_stream(values: tuple[float, ...]) -> tuple[str, ...]:
    """Bit-exact float64 comparison alphabet: ``float.hex`` per element."""

    return tuple(float(value).hex() for value in values)


def _crew_map() -> PublicMapView:
    """The four-room star topology the crew fixture wrappers decide over."""

    return PublicMapView(
        map_id="test_map",
        room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
        room_neighbors={
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        },
        vent_graph={},
        vent_rooms={},
        task_locations={"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _saw_player_event(*, tick: int, player_id: str, room: str) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": None},
        provenance=PROVENANCE_OBSERVED,
    )


def _crew_memory(*events: EpisodicEvent) -> AgentMemory:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return AgentMemory(episodic=store)


def _crew_wrapper_packet(
    *,
    tick: int,
    room: str,
    agent_id: str = "p-1",
    role: str = "CREWMATE",
    pending_task_id: str | None = None,
    owned_task_ids: tuple[str, ...] = (),
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
            owned_task_ids=owned_task_ids,
        ),
        visible_players=(),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=14,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


def _crew_factory(*, on_frame: FrameCallback | None = None) -> LearnedCrewAgentFactory:
    """Build the opt-in crew factory around the committed crew surface.

    The ``sabotage_kinds`` / ``emergency_uses_per_player`` injections read the
    engine ``Map`` (which ``agents/`` may not import); a single
    ``load_canonical_map()`` call sources both, mirroring the CLI arm's wiring.
    ``_inner_factory`` (the impostor block's REAL ``TacticalAgent`` constructor)
    satisfies :class:`WrappableCrewTacticalAgent` — its ``note_meeting_concluded``
    is exactly the hook the crew wrapper carries.
    """

    game_map = load_canonical_map()
    return build_learned_crew_factory(
        _inner_factory,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_per_player=game_map.emergency.uses_per_player,
        on_frame=on_frame,
    )


# --------------------------------------------------------------------------- #
# 1. Crew artifact parity pins (the committed copy — pinned by test, never     #
#    imported at inference: ``agents/`` reading ``training/`` breaches the     #
#    firewall). Mirrors the impostor section-1 idiom.                          #
# --------------------------------------------------------------------------- #


def test_crew_weights_payload_is_byte_identical_to_the_training_artifact() -> None:
    agents_payload = CREW_CHAMPION_WEIGHTS_PATH.read_bytes()
    training_payload = (_CREW_TRAINING_ARTIFACT_DIR / "weights.json").read_bytes()
    assert agents_payload == training_payload


def test_crew_sha256_sidecars_agree_and_record_the_committed_digest() -> None:
    agents_digest = CREW_CHAMPION_WEIGHTS_SIDECAR_PATH.read_text().split()[0]
    training_digest = (
        (_CREW_TRAINING_ARTIFACT_DIR / "weights.json.sha256").read_text().split()[0]
    )
    assert agents_digest == training_digest == _CREW_COMMITTED_SHA256
    # The sidecar is honest: it is the digest of the payload it sits beside.
    payload_digest = hashlib.sha256(CREW_CHAMPION_WEIGHTS_PATH.read_bytes()).hexdigest()
    assert payload_digest == _CREW_COMMITTED_SHA256
    assert committed_crew_weights_sha256() == _CREW_COMMITTED_SHA256


def test_crew_loader_returns_the_training_side_genome_bit_for_bit() -> None:
    weights = load_crew_champion_weights()
    assert len(weights) == CREW_GENOME_LENGTH == 27
    training_weights = load_candidate_weights(_CREW_TRAINING_ARTIFACT_DIR)
    assert _crew_hex_stream(weights) == _crew_hex_stream(training_weights)


def test_crew_feature_basis_matches_the_training_side_definition() -> None:
    assert OWNED_TASK_OPTION_FEATURE_NAMES == TRAINING_OWNED_TASK_OPTION_FEATURE_NAMES
    assert len(OWNED_TASK_OPTION_FEATURE_NAMES) == 26
    assert CREW_ENCODER_VERSION == "crew-option-features-v2"


def test_crew_champion_weights_config_pins_the_shipped_feature_basis() -> None:
    # The committed config.json's feature_names are the training-side record of
    # the widened owned-task basis the genome was trained on; the shipped basis
    # must equal it, and the genome length / encoder tag / entrant must pin.
    config = json.loads((_CREW_TRAINING_ARTIFACT_DIR / "config.json").read_text())
    assert tuple(config["feature_names"]) == OWNED_TASK_OPTION_FEATURE_NAMES
    assert config["genome_length"] == CREW_GENOME_LENGTH
    assert config["encoder_version"] == CREW_ENCODER_VERSION
    assert config["entrant"] == "crew-owned-tasks-es"


# --------------------------------------------------------------------------- #
# 2. The crew Q4 bit-exact cross-implementation gate (decision 6, crew         #
#    edition — the DoD spine).                                                 #
# --------------------------------------------------------------------------- #


class _CrewQ4Comparator:
    """Runs the training + shipped crew passes in lockstep as a ``CrewTrackPolicy``.

    Holds BOTH the training-side reference
    (:class:`training.crew.scorer.CrewOptionScorer` over the committed weights +
    the widened :class:`~training.crew.options.OwnedTaskOptionBasis`) and the
    shipped pass (:class:`~agents.tactical.learned.crew_forward.LearnedCrewScorer`).
    Its :meth:`evaluate` runs both on the SAME
    ``(packet, public_map, memory, fsm_intent, emergency_uses_remaining)``,
    compares the float-hex feature/score streams and the chosen intents,
    accumulates mismatch strings + decision counts, and returns the TRAINING
    frame — so :func:`training.crew.scorer.rollout_crew_candidate` drives the game
    exactly as a training-candidate rollout while the shipped pass is scored in
    parallel at every decision. :meth:`choice_distribution` delegates to the
    training scorer (unused by the traceless gate rollout, present for the
    protocol).
    """

    def __init__(self, *, game_map: Map) -> None:
        weights = load_crew_champion_weights()
        self._training = CrewOptionScorer(
            weights=weights, game_map=game_map, basis=OwnedTaskOptionBasis()
        )
        self._shipped = LearnedCrewScorer(weights=weights)
        self.decisions = 0
        self.multi_option_decisions = 0
        self.mismatches: list[str] = []

    @property
    def encoder_version(self) -> str:
        return self._training.encoder_version

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> PolicyFrame:
        training_frame = self._training.evaluate(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )
        shipped_frame = self._shipped.evaluate(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )
        self.decisions += 1
        if len(shipped_frame.scores) > 1:
            self.multi_option_decisions += 1
        where = f"agent {packet.agent_id} tick {packet.tick}"
        if _crew_hex_stream(training_frame.features) != _crew_hex_stream(
            shipped_frame.features
        ):
            self.mismatches.append(f"{where}: feature bits diverged")
        if _crew_hex_stream(training_frame.logits) != _crew_hex_stream(
            shipped_frame.scores
        ):
            self.mismatches.append(f"{where}: score bits diverged")
        if training_frame.intent != shipped_frame.intent:
            self.mismatches.append(f"{where}: chosen intents diverged")
        return training_frame

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> Mapping[str, float]:
        return self._training.choice_distribution(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )


def test_crew_q4_gate_training_and_shipped_passes_are_bit_exact_over_a_stream(
    tmp_path: Path,
) -> None:
    """The task's crew spine: both crew implementations over the committed weights
    across a recorded decision stream (fixed seeds, full widened option menus) —
    bit-identical float64 features and scores and identical chosen intents, per
    crew decision. Driven through the training-side ``rollout_crew_candidate`` so
    the game is exactly a training-candidate rollout.
    """

    game_map = load_canonical_map()
    comparator = _CrewQ4Comparator(game_map=game_map)
    # The comparator satisfies the crew-track policy seam the rollout drives.
    assert isinstance(comparator, CrewTrackPolicy)
    for seed in _CREW_Q4_SEEDS:
        rollout_crew_candidate(comparator, seed, output_dir=tmp_path, game_map=game_map)

    assert not comparator.mismatches, comparator.mismatches
    # The stream is non-trivial: real crew decisions with FULL widened option
    # menus (a single-option menu cannot exercise the argmax) were compared.
    assert comparator.decisions > 0
    assert comparator.multi_option_decisions > 0
    # Both passes report the widened owned-task encoder tag.
    assert (
        comparator._training.encoder_version
        == comparator._shipped.encoder_version
        == CREW_ENCODER_VERSION
        == "crew-option-features-v2"
    )


# --------------------------------------------------------------------------- #
# 3. The factory-level determinism double-run (mirrors the impostor twin).      #
# --------------------------------------------------------------------------- #


def test_crew_factory_double_run_is_bit_identical(tmp_path: Path) -> None:
    # Two identical full games through _crew_factory() itself must record a
    # bit-identical (feature, score, intent) crew-decision stream AND drive the
    # engine down a bit-identical state-hash chain.
    streams: list[list[str]] = []
    chains: list[list[str]] = []
    for run in range(2):
        sink: list[LearnedDecisionFrame] = []
        factory = _crew_factory(on_frame=sink.append)
        replay_path = tmp_path / f"crew-run-{run}.jsonl"
        _run_factory_game(factory, seed=_DETERMINISM_SEED, replay_path=replay_path)
        ordered = sorted(sink, key=lambda frame: (frame.tick, frame.agent_id))
        streams.append([_serialize_frame(frame) for frame in ordered])
        chains.append(_state_hash_chain(replay_path))

    assert streams[0], "the crew factory recorded no crew decisions"
    assert streams[0] == streams[1]
    assert chains[0], "the replay recorded no state hashes"
    assert chains[0] == chains[1]


# --------------------------------------------------------------------------- #
# 4. The leak-test factory mode through the crew factory.                       #
# --------------------------------------------------------------------------- #


def test_crew_factory_passes_the_leak_test_factory_mode() -> None:
    scanned = scan_factory_packets(_crew_factory())
    assert scanned > 0, "crew factory mode captured no packets"


# --------------------------------------------------------------------------- #
# 5. Crew stamp pins + the impostor-champion conflation guard.                  #
# --------------------------------------------------------------------------- #


def test_crew_stamp_fields_are_plain_strings_pinned_to_the_committed_sidecar() -> None:
    stamp = _crew_factory().stamp
    assert isinstance(stamp, LearnedCrewPolicyStamp)
    # The engine-free record lives under agents/ — never orchestrator.replay's
    # CrewTacticalPolicyStamp (that import would chain agents -> orchestrator ->
    # engine through the firewall).
    assert LearnedCrewPolicyStamp.__module__ == "agents.tactical.learned.factory"
    fields = (
        stamp.policy_id,
        stamp.method,
        stamp.encoder_version,
        stamp.weights_sha256,
        stamp.anchor_policy,
    )
    assert fields == (
        "crew-owned-tasks-es",
        "crew-utility-scorer-es",
        "crew-option-features-v2",
        _CREW_COMMITTED_SHA256,
        "fsm-default",
    )
    for value in fields:
        assert type(value) is str
    assert stamp.weights_sha256 == committed_crew_weights_sha256()
    # The CLI construction path: the REAL crew stamp object builds from the five
    # plain strings (and its shared validators accept them).
    real_stamp = CrewTacticalPolicyStamp(
        policy_id=stamp.policy_id,
        method=stamp.method,
        encoder_version=stamp.encoder_version,
        weights_sha256=stamp.weights_sha256,
        anchor_policy=stamp.anchor_policy,
    )
    assert real_stamp.weights_sha256 == _CREW_COMMITTED_SHA256


def test_crew_stamp_namespace_is_disjoint_from_the_impostor_champion() -> None:
    # The 18.7 conflation guard: a crew recording must NEVER wear the impostor
    # champion's stamp, so the two namespaces are disjoint on policy_id AND on
    # the committed weights digest.
    crew_stamp = _crew_factory().stamp
    impostor_stamp = build_learned_agent_factory(_inner_factory).stamp
    assert crew_stamp.policy_id != impostor_stamp.policy_id
    assert crew_stamp.weights_sha256 != impostor_stamp.weights_sha256
    assert committed_crew_weights_sha256() != committed_weights_sha256()


# --------------------------------------------------------------------------- #
# 6. Crew wrapper fixture pins: override re-validation + emergency bookkeeping. #
#    A stub scorer forces an OFF-vocabulary intent (the real menu is            #
#    submission-legal by construction and can never emit one), and a surgical   #
#    inner stub satisfies WrappableCrewTacticalAgent.                           #
# --------------------------------------------------------------------------- #


class _StubCrewInnerAgent:
    """A surgical inner-agent stub satisfying ``WrappableCrewTacticalAgent``.

    Carries a hand-built memory + a fixed FSM proposal for ``decide``, and
    records every forwarded ``note_meeting_concluded`` call so the wrapper's
    verbatim delegation (and its emergency-uses bookkeeping) can be pinned
    without standing up a real ``TacticalAgent``.
    """

    def __init__(self, *, memory: AgentMemory, decide_intent: ActionIntent) -> None:
        self._memory = memory
        self._decide_intent = decide_intent
        self.concluded_calls: list[
            tuple[int, tuple[PlayerId, ...], PlayerId | None]
        ] = []

    @property
    def memory(self) -> AgentMemory:
        return self._memory

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        del packet, public_map
        return self._decide_intent

    def note_meeting_concluded(
        self,
        *,
        end_tick: int,
        dead_ids: tuple[PlayerId, ...],
        emergency_caller_id: PlayerId | None,
        ejected_id: PlayerId | None = None,
        ejected_role: Role | None = None,
        votes_for_ejected: int | None = None,
        skip_votes: int | None = None,
        roster_impostor_count: int | None = None,
    ) -> None:
        # The announcement payload the WrappableCrewTacticalAgent protocol
        # carries beside the pacing facts is accepted and ignored, so the
        # recorded 3-tuple (and every existing assertion on it) stands unchanged.
        del ejected_id, ejected_role, votes_for_ejected, skip_votes
        del roster_impostor_count
        self.concluded_calls.append((end_tick, dead_ids, emergency_caller_id))


class _StubCrewScorer(LearnedCrewScorer):
    """A crew scorer whose ``evaluate`` returns a FORCED intent (drifted-menu twin).

    Subclasses the real scorer (so it type-checks as the ``LearnedCrewScorer``
    the wrapper accepts) but overrides ``evaluate`` to bypass the menu and return
    a hand-chosen intent — the only way to exercise the wrapper's override
    re-validation with an OFF-vocabulary intent the real (submission-legal-by-
    construction) menu can never emit.
    """

    def __init__(self, *, forced_intent: ActionIntent) -> None:
        super().__init__(weights=(0.0,) * CREW_GENOME_LENGTH)
        self._forced_intent = forced_intent

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> LearnedDecisionFrame:
        del public_map, memory, fsm_intent, emergency_uses_remaining
        return LearnedDecisionFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(1.0,),
            scores=(1.0,),
            intent=self._forced_intent,
        )


def test_crew_wrapper_raises_on_a_mask_violating_override() -> None:
    # ADMIN's only neighbor is CAFETERIA, so a MoveIntent to ELECTRICAL is a far
    # move the submission mask marks illegal — the drifted-menu case the wrapper
    # backstops fail-loud.
    off_vocab: ActionIntent = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "ELECTRICAL"}}
    )
    inner = _StubCrewInnerAgent(
        memory=_crew_memory(_saw_player_event(tick=5, player_id="p-2", room="ADMIN")),
        decide_intent=WaitIntent(actor="p-1", type="wait"),
    )
    frames: list[LearnedDecisionFrame] = []
    agent = _LearnedCrewAgent(
        inner,
        agent_id="p-1",
        scorer=_StubCrewScorer(forced_intent=off_vocab),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        on_frame=frames.append,
    )
    with pytest.raises(ValueError, match="non-submission-legal"):
        agent.decide(_crew_wrapper_packet(tick=5, room="ADMIN"), _crew_map())
    assert frames == []  # the raise fires BEFORE any frame is emitted


def test_crew_wrapper_accepts_a_submission_legal_override() -> None:
    # CAFETERIA is adjacent to ADMIN, so a one-hop MoveIntent is submission-legal
    # and, differing from the FSM's wait, is an accepted override.
    adjacent: ActionIntent = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "CAFETERIA"}}
    )
    inner = _StubCrewInnerAgent(
        memory=_crew_memory(_saw_player_event(tick=5, player_id="p-2", room="ADMIN")),
        decide_intent=WaitIntent(actor="p-1", type="wait"),
    )
    frames: list[LearnedDecisionFrame] = []
    agent = _LearnedCrewAgent(
        inner,
        agent_id="p-1",
        scorer=_StubCrewScorer(forced_intent=adjacent),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        on_frame=frames.append,
    )
    chosen = agent.decide(_crew_wrapper_packet(tick=5, room="ADMIN"), _crew_map())
    assert chosen == adjacent
    assert len(frames) == 1  # the accepted override emitted its frame


def test_crew_wrapper_accepts_the_owned_task_do_task_override() -> None:
    # The owned-task mirror: the mask enumerates do_task ONLY for the engine-fed
    # pending task (swipe_card, room ADMIN != ELECTRICAL, so illegal); the owned
    # wires task is invisible to the mask yet engine-legal in the actor's own
    # room, so override_is_submission_legal accepts it though the mask never
    # enumerates it.
    packet = _crew_wrapper_packet(
        tick=7,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    owned_do_task: ActionIntent = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "p-1", "payload": {"task_id": "wires_electrical"}}
    )
    # The mask itself does not admit the owned-task do_task (proving the mirror
    # is load-bearing, not redundant).
    assert not _build_action_mask(
        packet,
        _crew_map(),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_remaining=1,
    ).is_submission_legal(owned_do_task)
    inner = _StubCrewInnerAgent(
        memory=_crew_memory(
            _saw_player_event(tick=7, player_id="p-2", room="ELECTRICAL")
        ),
        decide_intent=WaitIntent(actor="p-1", type="wait"),
    )
    frames: list[LearnedDecisionFrame] = []
    agent = _LearnedCrewAgent(
        inner,
        agent_id="p-1",
        scorer=_StubCrewScorer(forced_intent=owned_do_task),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        on_frame=frames.append,
    )
    chosen = agent.decide(packet, _crew_map())
    assert chosen == owned_do_task
    assert len(frames) == 1


def test_crew_wrapper_tracks_emergency_uses_across_meetings() -> None:
    inner = _StubCrewInnerAgent(
        memory=_crew_memory(
            _saw_player_event(tick=1, player_id="p-2", room="CAFETERIA")
        ),
        decide_intent=WaitIntent(actor="p-1", type="wait"),
    )
    agent = _LearnedCrewAgent(
        inner,
        agent_id="p-1",
        scorer=_StubCrewScorer(forced_intent=WaitIntent(actor="p-1", type="wait")),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        on_frame=None,
    )
    assert agent._emergency_uses_remaining == 1
    # A meeting ANOTHER player called does not spend this agent's use.
    agent.note_meeting_concluded(
        end_tick=4, dead_ids=("p-9",), emergency_caller_id="p-2"
    )
    assert agent._emergency_uses_remaining == 1
    # This agent's OWN emergency spends its single use.
    agent.note_meeting_concluded(end_tick=8, dead_ids=(), emergency_caller_id="p-1")
    assert agent._emergency_uses_remaining == 0
    # The floor is 0: a second own call cannot underflow (max(0, ...)).
    agent.note_meeting_concluded(end_tick=12, dead_ids=(), emergency_caller_id="p-1")
    assert agent._emergency_uses_remaining == 0
    # Every conclusion forwarded VERBATIM to the inner agent.
    assert inner.concluded_calls == [
        (4, ("p-9",), "p-2"),
        (8, (), "p-1"),
        (12, (), "p-1"),
    ]


def test_crew_wrapper_delegates_impostor_decisions_without_a_frame() -> None:
    fsm_intent = WaitIntent(actor="p-1", type="wait")
    inner = _StubCrewInnerAgent(
        memory=_crew_memory(_saw_player_event(tick=3, player_id="p-2", room="ADMIN")),
        decide_intent=fsm_intent,
    )
    # A scorer that WOULD override if reached — proving the role gate short-
    # circuits before any scoring for an impostor packet.
    would_override: ActionIntent = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "CAFETERIA"}}
    )
    frames: list[LearnedDecisionFrame] = []
    agent = _LearnedCrewAgent(
        inner,
        agent_id="p-1",
        scorer=_StubCrewScorer(forced_intent=would_override),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        on_frame=frames.append,
    )
    chosen = agent.decide(
        _crew_wrapper_packet(tick=3, room="ADMIN", role="IMPOSTOR"), _crew_map()
    )
    assert chosen == fsm_intent  # the inner FSM proposal, untouched
    assert frames == []  # no crew decision, so no frame was emitted


def test_crew_build_action_mask_matches_the_training_side_mask() -> None:
    # The mask mirror is WHOLE (ported verbatim from training/env.py), so the
    # shipped agent-side mask equals the training-side mask tuple-for-tuple over
    # the same sabotage vocabulary + emergency-uses count.
    packet = _crew_wrapper_packet(
        tick=7,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    shipped = _build_action_mask(
        packet,
        _crew_map(),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_remaining=1,
    )
    training = training_build_action_mask(
        packet,
        _crew_map(),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_remaining=1,
    )
    assert shipped.engine_legal == training.engine_legal
    assert shipped.submission_only == training.submission_only
    assert shipped.illegal == training.illegal
