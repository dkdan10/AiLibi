"""The policy determinism harness (Task 15.10).

Every bake-off candidate (Task 15.15) must clear this before its fitness number
is trusted. It answers one question with a bit-exact artifact: *does this frozen
policy produce the same decisions twice?* Two failure modes are checked, both by
double-running a frozen policy over a fixed seed set:

1. **Feature / logit / intent determinism.** The full stream of
   ``(feature-vector, logits, chosen-intent)`` the policy emits across the seed
   set is hashed (SHA-256). Two runs must produce the SAME digest. This catches a
   determinism violation AT THE ARTIFACT — a belief-float residue that flips an
   argmax, a dict-insertion-ordered iteration — rather than downstream in a
   replay, where it would surface as a hard-to-attribute reconstruction failure.
2. **Frozen-genome full-game state-hash equality.** The per-tick engine
   ``state_hash`` chain each run RECORDS must be identical across the two runs. A
   frozen genome that drives the engine down two different trajectories is not
   deterministic even if its per-decision logits happen to match.

The harness is a LIBRARY: :func:`run_policy_determinism` takes any
:class:`FramePolicy` and returns a :class:`PolicyDeterminismReport` whose
``to_json`` is the artifact Task 15.15 quotes. A reference frozen policy
(:func:`build_reference_policy`) composes the production encoder
(``agents.tactical.features``) with a small pure-Python MLP head so the harness
has a concrete, memory-carrying policy to exercise and pin.

The frozen policy runs through the REAL production loop
(``orchestrator.game.HeadlessGame`` on the deterministic fake provider), wrapped
by an interposition agent that — unlike ``training.env``'s ``IntentSelector``
seam, which sees only the packet — reaches the inner agent's OWN
:class:`~agents.memory.store.AgentMemory` so the memory-carrying encoder gets the
belief / working / episodic state it needs. The wrapper drives the inner FSM
first (so perception + memory are populated for this tick), then evaluates the
policy off the inner agent's live memory.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.features import (
    ENCODER_VERSION,
    TacticalFeatureEncoder,
    mlp_forward,
    mlp_genome_length,
    weights_from_hex_json,
    weights_to_hex_json,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from observation.action_intent import ActionIntent, MoveIntent, WaitIntent
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
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import MeetingReplayEntry, ReplayEntry, read_all_entries
from orchestrator.scheduler import TickScheduler


@dataclass(frozen=True)
class PolicyFrame:
    """One frozen-policy decision: the encoder vector, its logits, and the intent.

    Emitted by :meth:`FramePolicy.evaluate` for every tick the policy decides. The
    harness hashes the ordered stream of these frames — so a policy that is
    non-deterministic in ANY of the three fields is caught at the digest.
    """

    agent_id: PlayerId
    tick: int
    features: tuple[float, ...]
    logits: tuple[float, ...]
    intent: ActionIntent


@runtime_checkable
class FramePolicy(Protocol):
    """The frozen-policy interface the determinism harness (and 15.15) rides.

    A policy maps one decision — the packet the agent legally sees, the static
    map, the agent's OWN memory, and the FSM's proposal (anchor / fallback) — to a
    :class:`PolicyFrame`. Implementations must be pure functions of these inputs
    (no RNG, no global state) so the double-run digests agree.
    """

    @property
    def encoder_version(self) -> str: ...

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame: ...


class ReferenceFrozenPolicy:
    """A concrete memory-carrying frozen policy for the harness (Task 15.10).

    Composes the production :class:`~agents.tactical.features.TacticalFeatureEncoder`
    with a small pure-Python MLP head over the map's rooms. The genome is loaded
    from float-hex JSON (exercising the Wave-1 weight format). Its intent choice
    mirrors the ml-spike lever — override an impostor's ``Move`` / ``Wait`` with
    the argmax over legal (stay + adjacent) rooms, lexical tie-break, delegate
    everything else to the FSM — so a rollout stays legal and the games terminate,
    while the encoder + logits are exercised on BOTH roles (crew frames are
    recorded even though the crew intent is the FSM's).

    Frozen: the genome is fixed, features are integer-quantized inside the
    encoder, and the room argmax breaks ties lexically, so :meth:`evaluate` is a
    pure function and the double-run digests agree.
    """

    def __init__(
        self,
        *,
        encoder: TacticalFeatureEncoder,
        public_map: PublicMapView,
        genome: Sequence[float],
        hidden: int,
    ) -> None:
        self._encoder = encoder
        self._rooms = tuple(sorted(public_map.room_ids))
        self._room_index = {room: i for i, room in enumerate(self._rooms)}
        self._input_dim = encoder.feature_dimension(public_map)
        self._hidden = hidden
        self._output = len(self._rooms)
        expected = mlp_genome_length(
            input_dim=self._input_dim, hidden=hidden, output=self._output
        )
        if len(genome) != expected:
            raise ValueError(
                f"genome length {len(genome)} != expected {expected} for this map"
            )
        self._genome = tuple(genome)

    @property
    def encoder_version(self) -> str:
        return self._encoder.version

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        features = self._encoder.encode(packet, public_map, memory)
        logits = mlp_forward(
            self._genome,
            features,
            input_dim=self._input_dim,
            hidden=self._hidden,
            output=self._output,
        )
        intent = self._select_intent(packet, public_map, fsm_intent, logits)
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            logits=logits,
            intent=intent,
        )

    def _select_intent(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        fsm_intent: ActionIntent,
        logits: tuple[float, ...],
    ) -> ActionIntent:
        # Only override an impostor's Move/Wait; everything else (crew, kills,
        # vents, cover, do_task, reports) delegates to the FSM. Overriding just
        # the impostor move keeps games short and legal (the ml-spike lever).
        if packet.self_state.role != "IMPOSTOR" or not isinstance(
            fsm_intent, (MoveIntent, WaitIntent)
        ):
            return fsm_intent
        own_room = packet.self_state.room
        # Candidate rooms = stay + adjacent (always-legal moves), sorted for the
        # lexical tie-break; skip a room absent from the logit head.
        neighbors = public_map.room_neighbors.get(own_room, ())
        candidates = sorted({own_room, *neighbors} & set(self._room_index))
        if not candidates:
            return fsm_intent
        best_room = candidates[0]
        best_score = logits[self._room_index[best_room]]
        for room in candidates[1:]:
            score = logits[self._room_index[room]]
            if score > best_score:  # strict → smallest room id wins a tie
                best_score = score
                best_room = room
        actor = packet.agent_id
        if best_room == own_room:
            return WaitIntent(actor=actor, type="wait")
        return MoveIntent.model_validate(
            {"type": "move", "actor": actor, "payload": {"to_room": best_room}}
        )


def build_reference_policy(
    *,
    game_map: Map | None = None,
    hidden: int = 8,
    genome_seed: int = 0,
) -> ReferenceFrozenPolicy:
    """Build the reference frozen policy the harness pins (Task 15.10).

    The genome is generated deterministically from ``genome_seed`` (a stdlib
    ``random.Random`` draw — the ONLY randomness, confined to genome creation,
    never inference), then round-tripped through the Wave-1 float-hex JSON weight
    format so the harness exercises :func:`~agents.tactical.features.weights_to_hex_json`
    / :func:`~agents.tactical.features.weights_from_hex_json` end to end.
    """

    import random

    resolved_map = game_map if game_map is not None else load_canonical_map()
    public_map = public_map_from_engine_map(resolved_map)
    encoder = TacticalFeatureEncoder()
    input_dim = encoder.feature_dimension(public_map)
    output = len(public_map.room_ids)
    length = mlp_genome_length(input_dim=input_dim, hidden=hidden, output=output)
    rng = random.Random(genome_seed)
    genome = [rng.gauss(0.0, 0.5) for _ in range(length)]
    # Round-trip the genome through the committed weight format (bit-exact).
    genome = list(weights_from_hex_json(weights_to_hex_json(genome)))
    return ReferenceFrozenPolicy(
        encoder=encoder, public_map=public_map, genome=genome, hidden=hidden
    )


class _FrameRecordingAgent:
    """Interposition wrapper that records a :class:`FramePolicy`'s frames (15.10).

    Wraps a real :class:`TacticalAgent`. On :meth:`decide` it drives the inner FSM
    first (populating the inner agent's memory via perception), then evaluates the
    frozen policy off the inner agent's OWN live ``AgentMemory`` — the memory the
    memory-carrying encoder needs and that ``training.env``'s packet-only selector
    seam cannot reach. The emitted intent drives the game; the frame is appended
    to the shared per-game sink. The full ``MeetingAwareAgent`` protocol delegates
    to the inner agent via ``__getattr__``.
    """

    def __init__(
        self,
        inner: TacticalAgent,
        *,
        policy: FramePolicy,
        public_map: PublicMapView,
        sink: list[PolicyFrame],
    ) -> None:
        self._inner = inner
        self._policy = policy
        self._public_map = public_map
        self._sink = sink

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        fsm_intent = self._inner.decide(packet, public_map)
        frame = self._policy.evaluate(
            packet, public_map, self._inner.memory, fsm_intent=fsm_intent
        )
        self._sink.append(frame)
        return frame.intent

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)


def _build_recording_factory(
    *,
    policy: FramePolicy,
    public_map: PublicMapView,
    sink: list[PolicyFrame],
) -> AgentFactory:
    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy_impl: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy_impl = ImpostorPolicy(agent_id=agent_id)
        else:
            policy_impl = CrewmatePolicy(agent_id=agent_id)
        inner = TacticalAgent(agent_id=agent_id, policy=policy_impl, role=role)
        return _FrameRecordingAgent(
            inner, policy=policy, public_map=public_map, sink=sink
        )

    return factory


def _hex(value: float) -> str:
    return float(value).hex()


def _serialize_frame(seed: int, frame: PolicyFrame) -> str:
    """Canonical, bit-exact string for one frame (floats via ``float.hex``)."""

    return json.dumps(
        {
            "seed": seed,
            "tick": frame.tick,
            "agent_id": frame.agent_id,
            "features": [_hex(value) for value in frame.features],
            "logits": [_hex(value) for value in frame.logits],
            "intent": frame.intent.model_dump(mode="json"),
        },
        sort_keys=True,
    )


@dataclass(frozen=True)
class _RunArtifacts:
    frame_digest: str
    state_hash_digest: str
    num_frames: int
    num_state_hashes: int


@dataclass(frozen=True)
class PolicyDeterminismReport:
    """The determinism verdict + digests for a frozen policy (Task 15.10 public type).

    ``frame_stream_sha256`` hashes the ordered ``(features, logits, intent)``
    stream; ``state_hash_sha256`` hashes the recorded per-tick engine state-hash
    chain. ``deterministic`` is ``True`` iff BOTH digests matched across the two
    runs. :meth:`to_json` is the machine-readable artifact Task 15.15 quotes.
    """

    encoder_version: str
    seeds: tuple[int, ...]
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    num_frames: int
    num_state_hashes: int
    frame_stream_sha256: str
    state_hash_sha256: str
    deterministic: bool

    def to_json(self) -> str:
        return json.dumps(
            {
                "encoder_version": self.encoder_version,
                "seeds": list(self.seeds),
                "num_players": self.num_players,
                "num_impostors": self.num_impostors,
                "tasks_per_crewmate": self.tasks_per_crewmate,
                "num_frames": self.num_frames,
                "num_state_hashes": self.num_state_hashes,
                "frame_stream_sha256": self.frame_stream_sha256,
                "state_hash_sha256": self.state_hash_sha256,
                "deterministic": self.deterministic,
            },
            sort_keys=True,
        )


def _run_once(
    policy: FramePolicy,
    *,
    seeds: Sequence[int],
    game_map: Map,
    public_map: PublicMapView,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    max_ticks: int,
) -> _RunArtifacts:
    frame_hasher = hashlib.sha256()
    state_hasher = hashlib.sha256()
    num_frames = 0
    num_state_hashes = 0
    with tempfile.TemporaryDirectory(prefix="ailibi-determinism-") as tmp:
        directory = Path(tmp)
        for seed in seeds:
            sink: list[PolicyFrame] = []
            factory = _build_recording_factory(
                policy=policy, public_map=public_map, sink=sink
            )
            replay_path = directory / f"replay-seed-{seed}.jsonl"
            game = HeadlessGame(
                seed=seed,
                game_map=game_map,
                agent_factory=factory,
                replay_path=replay_path,
                num_players=num_players,
                num_impostors=num_impostors,
                tasks_per_crewmate=tasks_per_crewmate,
                scheduler=TickScheduler(max_ticks=max_ticks),
                meeting_runner=build_default_meeting_runner(
                    llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
                ),
                force=True,
            )
            game.run()

            # Frames sorted deterministically so the digest is independent of the
            # orchestrator's decide() call order within a tick.
            for frame in sorted(sink, key=lambda item: (item.tick, item.agent_id)):
                frame_hasher.update(_serialize_frame(seed, frame).encode("utf-8"))
                num_frames += 1

            # Hash the COMPLETE recorded state-hash chain in entry order: per-tick
            # rows AND the meeting rows' before/after hashes. For a game that ENDS
            # on a meeting ejection (or a post-meeting game-over), the final engine
            # mutation's only hash is the ``MeetingReplayEntry.state_hash_after`` —
            # no later tick row exists — so hashing tick rows alone would report
            # full-game equality while ignoring the final meeting-applied state.
            for entry in read_all_entries(replay_path):
                if isinstance(entry, ReplayEntry):
                    state_hasher.update(
                        f"{seed}:tick:{entry.tick}:{entry.state_hash}".encode()
                    )
                    num_state_hashes += 1
                elif isinstance(entry, MeetingReplayEntry):
                    state_hasher.update(
                        f"{seed}:meeting_before:{entry.tick}:"
                        f"{entry.state_hash_before}".encode()
                    )
                    state_hasher.update(
                        f"{seed}:meeting_after:{entry.tick}:"
                        f"{entry.state_hash_after}".encode()
                    )
                    num_state_hashes += 2
    return _RunArtifacts(
        frame_digest=frame_hasher.hexdigest(),
        state_hash_digest=state_hasher.hexdigest(),
        num_frames=num_frames,
        num_state_hashes=num_state_hashes,
    )


def run_policy_determinism(
    policy: FramePolicy,
    *,
    seeds: Sequence[int],
    game_map: Map | None = None,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    tasks_per_crewmate: int = DEFAULT_TASKS_PER_CREWMATE,
    max_ticks: int = DEFAULT_MAX_TICKS,
) -> PolicyDeterminismReport:
    """Double-run ``policy`` over ``seeds`` and report the determinism verdict.

    Runs the frozen policy through the real production loop TWICE over the same
    seed set, hashing the ``(features, logits, intent)`` stream and the recorded
    per-tick state-hash chain each time. ``deterministic`` is ``True`` iff both
    digests match across the two runs.
    """

    if not seeds:
        raise ValueError("run_policy_determinism requires at least one seed")
    resolved_map = game_map if game_map is not None else load_canonical_map()
    public_map = public_map_from_engine_map(resolved_map)

    first = _run_once(
        policy,
        seeds=seeds,
        game_map=resolved_map,
        public_map=public_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        max_ticks=max_ticks,
    )
    second = _run_once(
        policy,
        seeds=seeds,
        game_map=resolved_map,
        public_map=public_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        max_ticks=max_ticks,
    )

    deterministic = (
        first.frame_digest == second.frame_digest
        and first.state_hash_digest == second.state_hash_digest
    )
    return PolicyDeterminismReport(
        encoder_version=policy.encoder_version,
        seeds=tuple(seeds),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        num_frames=first.num_frames,
        num_state_hashes=first.num_state_hashes,
        frame_stream_sha256=first.frame_digest,
        state_hash_sha256=first.state_hash_digest,
        deterministic=deterministic,
    )


def reference_determinism_report(
    *,
    seeds: Sequence[int],
    genome_seed: int = 0,
) -> PolicyDeterminismReport:
    """Convenience: the determinism report for the reference frozen policy."""

    policy = build_reference_policy(genome_seed=genome_seed)
    return run_policy_determinism(policy, seeds=seeds)


__all__ = [
    "ENCODER_VERSION",
    "FramePolicy",
    "PolicyDeterminismReport",
    "PolicyFrame",
    "ReferenceFrozenPolicy",
    "build_reference_policy",
    "reference_determinism_report",
    "run_policy_determinism",
]
