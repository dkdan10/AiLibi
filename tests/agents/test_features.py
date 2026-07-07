"""Tests for the Encoder v2 memory-carrying feature encoder (Task 15.10)."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from agents.memory.beliefs import BeliefState
from agents.memory.store import AgentMemory, EpisodicEvent, MemoryStore
from agents.memory.working import WorkingMemory
from agents.perception import ingest_packet
from agents.tactical.features import (
    BELIEF_QUANT_LEVELS,
    DEFAULT_ROSTER_SLOTS,
    ENCODER_VERSION,
    FeatureSegment,
    TacticalFeatureEncoder,
    mlp_forward,
    mlp_genome_length,
    quantize_unit_interval,
    weights_from_hex_json,
    weights_to_hex_json,
)
from engine.actions import Action
from engine.events import MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from meetings.schemas import MeetingResult
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state
from observation.service import ObservationService

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)
_SAMPLES_DIR = Path("replays/samples")
_SAMPLE_SETS = ("9p2i", "4p1i")

# Golden pins (Task 15.10). Any change here means the feature layout moved — which
# is legal ONLY via an ``ENCODER_VERSION`` bump. Canonical_1 has 10 rooms; the
# default encoder carries 9 roster slots.
_GOLDEN_DIMENSION = 111
_GOLDEN_LAYOUT: tuple[tuple[str, int], ...] = (
    ("self_room_onehot", 10),
    ("visible_players_by_room", 10),
    ("visible_bodies_by_room", 10),
    ("lastseen_occupancy_by_room", 10),
    ("scalars", 17),
    ("belief_slots", 36),
    ("lastseen_slots", 18),
)
# sha256 over the golden fixture's encoded vector (float-hex serialized). Pins the
# VALUES, not just the shape — a change in any feature computation trips this.
_GOLDEN_VECTOR_SHA256 = (
    "4e91130e43efef34d2304691cbf19f7ef9e5de52fbd07d05db2a3ce81f4129e3"
)


def _canonical_public_map() -> PublicMapView:
    return public_map_from_engine_map(load_canonical_map())


def _golden_fixture(
    public_map: PublicMapView,
) -> tuple[ObservationPacket, AgentMemory]:
    """A deterministic, feature-rich packet + memory covering every code path.

    Rooms are drawn from the map's own sorted room set so the fixture stays valid
    regardless of the exact room names. It exercises: cooldown, visible players +
    bodies, a witnessed move, both audible-event kinds, beliefs above and below
    the gate (with a float-residue value), last-seen ages, and episodic events.
    """

    rooms = sorted(public_map.room_ids)
    r0, r1, r2 = rooms[0], rooms[1], rooms[2]

    packet = ObservationPacket(
        tick=12,
        agent_id="p-1",
        self_state=SelfView(
            room=r0,
            role="IMPOSTOR",
            pending_task_id=None,
            fellow_impostor_ids=("p-9",),
            in_vent=False,
        ),
        visible_players=(
            PlayerView(id="p-2", room=r0, action=None),
            PlayerView(id="p-3", room=r1, action="task"),
        ),
        visible_bodies=(BodyView(id="body-p-4-8", room=r1, victim_id="p-4"),),
        audible_events=(
            AudibleEvent(kind="vent_use_heard", room=r2),
            AudibleEvent(kind="sabotage_alarm", room=None),
        ),
        global_state=GlobalView(
            tasks_completed=3,
            tasks_total=14,
            task_completion_percent=0.2142857,
            sabotage_active=True,
            sabotage_kind="reactor",
            sabotage_repair_rooms=(r2,),
            sabotage_is_gating=True,
        ),
        cooldown=2,
        moved_players=(MovedPlayerView(id="p-3", from_room=r0, to_room=r1),),
    )

    beliefs = BeliefState()
    # A residue-laced over-gate value (0.5 + 0.05 + 0.05 IEEE case), an under-gate
    # value, and a trusted player — covering the belief-slot + aggregate paths.
    beliefs.seed_player("p-2", suspicion=0.5 + 0.05 + 0.05, trust=0.4)
    beliefs.seed_player("p-3", suspicion=0.55, trust=0.5)
    beliefs.seed_player("p-5", suspicion=0.1, trust=0.9)
    working = WorkingMemory()
    working.record_sighting(player_id="p-2", room=r1, tick=10)
    working.record_sighting(player_id="p-3", room=r0, tick=4)
    episodic = MemoryStore()
    for tick in (8, 10, 12):
        episodic.append(
            EpisodicEvent(
                tick=tick,
                type="saw_player",
                payload={"player_id": "p-2", "room": r0},
                provenance="observed",
            )
        )
    # p-6 is a NEUTRAL player: seen (episodic) but never suspected, so it has no
    # belief row. It must still occupy a roster slot with its last-seen — the
    # encoder keys last-seen on all SEEN players, not just belief-known ones.
    episodic.append(
        EpisodicEvent(
            tick=12,
            type="saw_player_move",
            payload={"player_id": "p-6", "from_room": r0, "to_room": r2},
            provenance="observed",
        )
    )
    memory = AgentMemory(episodic=episodic, working=working, beliefs=beliefs)
    return packet, memory


def _vector_sha256(vector: tuple[float, ...]) -> str:
    payload = json.dumps([float(value).hex() for value in vector])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------- #
# Version + golden layout
# ---------------------------------------------------------------------------- #


def test_encoder_version_is_stable_and_exposed() -> None:
    assert ENCODER_VERSION == "v2"
    assert TacticalFeatureEncoder().version == ENCODER_VERSION


def test_golden_layout_and_dimension() -> None:
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    layout = encoder.feature_layout(public_map)
    assert layout == tuple(FeatureSegment(name, size) for name, size in _GOLDEN_LAYOUT)
    assert encoder.feature_dimension(public_map) == _GOLDEN_DIMENSION
    assert sum(size for _, size in _GOLDEN_LAYOUT) == _GOLDEN_DIMENSION


def test_golden_vector_pins_values() -> None:
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, memory = _golden_fixture(public_map)
    vector = encoder.encode(packet, public_map, memory)
    assert len(vector) == _GOLDEN_DIMENSION
    assert all(0.0 <= value <= 1.0 for value in vector)
    assert _vector_sha256(vector) == _GOLDEN_VECTOR_SHA256


def test_default_roster_slots_and_layout_sizes() -> None:
    # The roster-slot blocks scale with DEFAULT_ROSTER_SLOTS; the golden layout is
    # pinned to that default so a slot-count change forces an ENCODER_VERSION bump.
    assert DEFAULT_ROSTER_SLOTS == 9


# ---------------------------------------------------------------------------- #
# Quantization / determinism (the §6.3 residue-flips-argmax hazard)
# ---------------------------------------------------------------------------- #


def test_quantize_unit_interval_clamps_and_rounds() -> None:
    assert quantize_unit_interval(-5.0) == 0
    assert quantize_unit_interval(0.0) == 0
    assert quantize_unit_interval(1.0) == BELIEF_QUANT_LEVELS
    assert quantize_unit_interval(5.0) == BELIEF_QUANT_LEVELS
    assert quantize_unit_interval(0.6) == 600
    assert quantize_unit_interval(0.1234) == 123


def test_quantization_kills_belief_float_residue() -> None:
    # Two suspicions that differ only by IEEE residue must produce an IDENTICAL
    # encoded vector: the encoder quantizes before use, so sub-grid residue can
    # never flip a feature (or, downstream, an argmax).
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, _ = _golden_fixture(public_map)

    def _memory_with(suspicion: float) -> AgentMemory:
        beliefs = BeliefState()
        beliefs.seed_player("p-2", suspicion=suspicion, trust=0.5)
        return AgentMemory(beliefs=beliefs)

    clean = 0.6
    residue = 0.6 + 1e-15  # a value a raw >= 0.60 compare would still pass, but
    residue_low = 0.6 - 1e-15  # this one a raw compare would FAIL — quantize fixes it
    v_clean = encoder.encode(packet, public_map, _memory_with(clean))
    v_hi = encoder.encode(packet, public_map, _memory_with(residue))
    v_lo = encoder.encode(packet, public_map, _memory_with(residue_low))
    assert v_clean == v_hi == v_lo


def test_over_gate_feature_uses_quantized_grid() -> None:
    # 0.5999999 quantizes to 600 == the gate quantum, so it reads over-gate (the
    # render-agreement behavior); 0.599 quantizes to 599, under the gate.
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, _ = _golden_fixture(public_map)

    def _first_belief_slot_over_gate(suspicion: float) -> float:
        beliefs = BeliefState()
        beliefs.seed_player("p-2", suspicion=suspicion, trust=0.5)
        vector = encoder.encode(packet, public_map, AgentMemory(beliefs=beliefs))
        # belief_slots start after 4*R rooms + scalars; slot 0's over_gate is the
        # third belief feature. Rather than index by hand, assert via the max-
        # suspicion aggregate scalar and count-over-gate scalar being consistent.
        return vector[_over_gate_scalar_index(public_map)]

    assert _first_belief_slot_over_gate(0.5999999) > 0.0
    assert _first_belief_slot_over_gate(0.599) == 0.0


def _over_gate_scalar_index(public_map: PublicMapView) -> int:
    # count_over_gate_norm is the 15th scalar (0-based 14) inside the scalar block,
    # which starts after 4 room-blocks.
    rooms = len(public_map.room_ids)
    scalar_start = 4 * rooms
    return scalar_start + 14  # count_over_gate_norm


def test_encode_is_deterministic_on_repeat() -> None:
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, memory = _golden_fixture(public_map)
    assert encoder.encode(packet, public_map, memory) == encoder.encode(
        packet, public_map, memory
    )


def test_neutral_seen_player_is_encoded_from_episodic() -> None:
    # A player the agent merely SAW (episodic saw_player) but never suspected —
    # perception mints no belief row for a plain sighting — must still occupy a
    # roster slot with its last-seen, rather than being dropped because it has no
    # belief entry (the memory-carrying vector would otherwise be blind to
    # routine movement history).
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    rooms = sorted(public_map.room_ids)
    packet = ObservationPacket(
        tick=5,
        agent_id="p-1",
        self_state=SelfView(room=rooms[0], role="CREWMATE", pending_task_id=None),
        visible_players=(),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )
    # A neutral player seen at tick 4 in rooms[1], NO belief row anywhere.
    episodic = MemoryStore()
    episodic.append(
        EpisodicEvent(
            tick=4,
            type="saw_player",
            payload={"player_id": "p-7", "room": rooms[1]},
            provenance="observed",
        )
    )
    memory = AgentMemory(episodic=episodic)
    assert memory.beliefs.known_players() == ()  # no belief row for p-7

    empty = encoder.encode(packet, public_map, AgentMemory())
    with_neutral = encoder.encode(packet, public_map, memory)
    # The neutral seen player changed the vector (a slot filled + last-seen set +
    # the known-players / last-seen-occupancy aggregates moved).
    assert empty != with_neutral


def test_memory_carrying_changes_features() -> None:
    # The whole point of Encoder v2: memory changes the vector. An empty memory
    # and a memory carrying an over-gate belief must differ.
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    packet, _ = _golden_fixture(public_map)
    empty = encoder.encode(packet, public_map, AgentMemory())
    beliefs = BeliefState()
    beliefs.seed_player("p-2", suspicion=0.95, trust=0.1)
    carried = encoder.encode(packet, public_map, AgentMemory(beliefs=beliefs))
    assert empty != carried


# ---------------------------------------------------------------------------- #
# Totality (the "moved_players is optional" + committed-corpora sweep)
# ---------------------------------------------------------------------------- #


def test_moved_players_optional_is_total() -> None:
    encoder = TacticalFeatureEncoder()
    public_map = _canonical_public_map()
    rooms = sorted(public_map.room_ids)
    packet = ObservationPacket(
        tick=0,
        agent_id="p-1",
        self_state=SelfView(room=rooms[0], role="CREWMATE", pending_task_id=None),
        visible_players=(),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )
    # moved_players omitted from the JSON when empty (packet default ()).
    assert "moved_players" not in packet.model_dump(mode="json")
    vector = encoder.encode(packet, public_map, AgentMemory())
    assert len(vector) == encoder.feature_dimension(public_map)
    assert all(value == 0.0 or 0.0 <= value <= 1.0 for value in vector)


def _iter_committed_packets(
    set_name: str,
) -> Iterator[tuple[ObservationPacket, PublicMapView, AgentMemory]]:
    """Reconstruct one committed set and yield (packet, memory) per living agent.

    Mirrors the ``training.rollout.reconstruct_episode`` walk (re-seed, advance
    over recorded actions, apply meetings) but ALSO builds each living agent's
    packet + perception memory at every PLAY tick, so the encoder sees the exact
    packet distribution the committed bytes produced. Belief state is
    perception-only (the meeting belief-fold enrichment is not replayed here) —
    totality over that memory shape is exactly what we test.
    """

    set_dir = _SAMPLES_DIR / set_name
    roster = json.loads((set_dir / "roster.json").read_text(encoding="utf-8"))
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    for replay_path in sorted(set_dir.glob("replay-seed-*.jsonl")):
        entries = read_all_entries(replay_path)
        meeting_by_tick = {
            entry.tick: entry
            for entry in entries
            if isinstance(entry, MeetingReplayEntry)
        }
        state = seed_initial_state(
            seed=int(replay_path.stem.rsplit("-", 1)[1]),
            game_map=game_map,
            num_players=roster["num_players"],
            num_impostors=roster["num_impostors"],
            tasks_per_crewmate=roster["tasks_per_crewmate"],
        )
        memories: dict[str, AgentMemory] = {pid: AgentMemory() for pid in state.players}
        audit_path = replay_path.parent / f"_sweep_audit_{replay_path.stem}.jsonl"
        service = ObservationService(game_map=game_map, audit_log_path=audit_path)
        try:
            for entry in entries:
                if not isinstance(entry, ReplayEntry):
                    continue
                actions = [
                    _ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions
                ]
                state, events = advance_tick(state, actions, game_map=game_map)
                for pid, player in state.players.items():
                    if not player.alive:
                        continue
                    packet = service.build_packet(
                        world_state=state, agent_id=pid, engine_events=events
                    )
                    ingest_packet(
                        packet=packet,
                        memory=memories[pid].episodic,
                        beliefs=memories[pid].beliefs,
                    )
                    yield packet, public_map, memories[pid]
                if state.phase == "GAME_OVER":
                    break
                if state.phase != "MEETING":
                    continue
                trigger = next(
                    e for e in events if isinstance(e, MeetingTriggeredEvent)
                )
                meeting_entry = meeting_by_tick[entry.tick]
                result = MeetingResult(
                    meeting_id=meeting_entry.meeting_id,
                    triggered_by=meeting_entry.triggered_by,
                    trigger_tick=meeting_entry.tick,
                    outcome=meeting_entry.outcome,
                    ejected_player_id=meeting_entry.ejected_player_id,
                    ballots=meeting_entry.ballots,
                    contradictions=meeting_entry.contradictions,
                    transcript=meeting_entry.transcript,
                )
                state, _ = apply_meeting_result(
                    state,
                    result,
                    game_map=game_map,
                    triggering_body_id=trigger.body_id,
                )
                if state.phase == "GAME_OVER":
                    break
        finally:
            service.close()
            audit_path.unlink(missing_ok=True)


@pytest.mark.parametrize("set_name", _SAMPLE_SETS)
def test_encode_is_total_over_committed_corpora(set_name: str) -> None:
    encoder = TacticalFeatureEncoder()
    count = 0
    for packet, public_map, memory in _iter_committed_packets(set_name):
        vector = encoder.encode(packet, public_map, memory)
        assert len(vector) == encoder.feature_dimension(public_map)
        for value in vector:
            assert 0.0 <= value <= 1.0, f"feature out of [0,1]: {value}"
            assert math.isfinite(value)
        count += 1
    assert count > 0, f"no packets swept for {set_name}"


# ---------------------------------------------------------------------------- #
# Wave-1 float64-hex weight serialization + the pure-Python MLP head
# ---------------------------------------------------------------------------- #


def test_weights_hex_json_exact_roundtrip() -> None:
    import random

    rng = random.Random(2024)
    genome = [rng.gauss(0.0, 1.0) for _ in range(256)]
    # Plus float64 edge cases the format must survive exactly.
    genome.extend(
        [0.0, -0.0, 1e-308, 1e308, -1e-308, math.pi, -math.pi, 0.1, 1.0 / 3.0]
    )
    restored = weights_from_hex_json(weights_to_hex_json(genome))
    assert restored == tuple(genome)
    # -0.0 vs 0.0 preserved bit-exactly (a lossy format would coalesce them).
    assert math.copysign(1.0, restored[len(genome) - 8]) == -1.0


def test_weights_from_hex_json_rejects_non_list() -> None:
    with pytest.raises(ValueError, match="list of float-hex strings"):
        weights_from_hex_json(json.dumps({"not": "a list"}))


def test_mlp_forward_deterministic_and_shaped() -> None:
    import random

    input_dim, hidden, output = 8, 5, 4
    length = mlp_genome_length(input_dim=input_dim, hidden=hidden, output=output)
    rng = random.Random(11)
    genome = [rng.gauss(0.0, 0.5) for _ in range(length)]
    features = [rng.gauss(0.0, 1.0) for _ in range(input_dim)]
    logits_a = mlp_forward(
        genome, features, input_dim=input_dim, hidden=hidden, output=output
    )
    logits_b = mlp_forward(
        genome, features, input_dim=input_dim, hidden=hidden, output=output
    )
    assert logits_a == logits_b
    assert len(logits_a) == output


def test_mlp_forward_rejects_bad_shapes() -> None:
    with pytest.raises(ValueError, match="feature vector length"):
        mlp_forward([0.0] * 100, [1.0], input_dim=8, hidden=5, output=4)
    with pytest.raises(ValueError, match="genome length"):
        mlp_forward([0.0] * 3, [0.0] * 8, input_dim=8, hidden=5, output=4)
