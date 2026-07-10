"""Tests for the productized learned champion's forward pass (Task 15.20).

Three obligations from the task contract:

1. **Artifact parity pins.** The agents-side ``weights.json`` is byte-identical
   to the frozen training-side champion artifact
   (``training/artifacts/impostor/utility-es/weights.json``) and both sha256
   sidecars record the committed digest ``6d327dcb…`` — the copy is pinned by
   test, never read across the package boundary.
2. **Forward-pass unit tests.** The shipped ``math.fsum`` linear scorer, the
   crew delegation path, the lexical intent-key tie-break, and the fail-loud
   loader/menu error paths.
3. **The Q4 bit-exact gate** (audits/audit-phase-15-pause.md decision 6): over
   the committed float-hex weights and a fixed recorded decision stream (fixed
   seeds, full option menus), the training-side scorer
   (``training/bakeoff/utility_es.py`` — itself pure-Python ``math.fsum``; the
   ruling's "numpy-trained" is shorthand for training-side) and the shipped
   pure-Python pass produce bit-identical float64 scores and identical chosen
   intents.
"""

from __future__ import annotations

import hashlib
import json
import math
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Final, Literal

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_SAW_PLAYER,
    PROVENANCE_OBSERVED,
)
from agents.tactical.learned.forward import (
    ENCODER_VERSION,
    GENOME_LENGTH,
    OPTION_FEATURE_NAMES,
    OPTION_KINDS,
    ImpostorOption,
    LearnedImpostorScorer,
    enumerate_options,
    intent_key,
)
from agents.tactical.learned.weights import (
    CHAMPION_WEIGHTS_PATH,
    CHAMPION_WEIGHTS_SIDECAR_PATH,
    _verified_payload,
    committed_weights_sha256,
    load_champion_weights,
)
from engine.world import load_canonical_map
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
from observation.packet import (
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView, RoomId
from training.bakeoff.harness import intent_key as training_intent_key
from training.bakeoff.harness import load_candidate_weights, rollout_candidate
from training.bakeoff.utility_es import (
    OPTION_FEATURE_NAMES as TRAINING_OPTION_FEATURE_NAMES,
)
from training.bakeoff.utility_es import (
    OPTION_KINDS as TRAINING_OPTION_KINDS,
)
from training.bakeoff.utility_es import (
    UtilityScorerPolicy,
)
from training.bakeoff.utility_es import (
    enumerate_options as training_enumerate_options,
)

# The committed champion digest (audits/audit-phase-15-pause.md decision 1).
_COMMITTED_SHA256: Final[str] = (
    "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"
)
_TRAINING_ARTIFACT_DIR: Final[Path] = Path("training/artifacts/impostor/utility-es")

# The Q4 gate's fixed recorded-decision-stream seeds: the 15.15 protocol's
# committed determinism seeds (corpus test-split members, full 9p2i games).
_Q4_SEEDS: Final[tuple[int, ...]] = (1004, 1009)


def _hex_stream(values: tuple[float, ...]) -> tuple[str, ...]:
    """Bit-exact float64 comparison alphabet: ``float.hex`` per element."""

    return tuple(float(value).hex() for value in values)


# --------------------------------------------------------------------------- #
# Fixture states (the test_bakeoff_methods four-room topology, mirrored).      #
# --------------------------------------------------------------------------- #


def _public_map() -> PublicMapView:
    return PublicMapView(
        map_id="test_map",
        room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
        room_neighbors={
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        },
        vent_graph={
            "ADMIN_VENT": ("ELECTRICAL_VENT", "MEDBAY_VENT"),
            "ELECTRICAL_VENT": ("ADMIN_VENT", "MEDBAY_VENT"),
            "MEDBAY_VENT": ("ADMIN_VENT", "ELECTRICAL_VENT"),
        },
        vent_rooms={
            "ADMIN_VENT": "ADMIN",
            "ELECTRICAL_VENT": "ELECTRICAL",
            "MEDBAY_VENT": "MEDBAY",
        },
        task_locations={"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _cooldown_event(*, tick: int, cooldown: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_COOLDOWN_STATUS,
        payload={"cooldown": cooldown},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_player_event(*, tick: int, player_id: str, room: RoomId) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": None},
        provenance=PROVENANCE_OBSERVED,
    )


def _memory(*events: EpisodicEvent) -> AgentMemory:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return AgentMemory(episodic=store)


def _packet(
    *,
    tick: int,
    room: RoomId,
    agent_id: str = "imp",
    role: Literal["CREWMATE", "IMPOSTOR"] = "IMPOSTOR",
    pending_task_id: str | None = None,
    fellow_impostor_ids: tuple[str, ...] = (),
    in_vent: bool = False,
    cooldown: int | None = 0,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    tasks_completed: int = 0,
    tasks_total: int = 1,
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
) -> ObservationPacket:
    completion = tasks_completed / tasks_total if tasks_total else 0.0
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,
            pending_task_id=pending_task_id,
            fellow_impostor_ids=fellow_impostor_ids,
            in_vent=in_vent,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=completion,
            sabotage_active=sabotage_active,
            sabotage_kind=sabotage_kind,
        ),
        cooldown=cooldown,
    )


def _kill_menu_state() -> tuple[ObservationPacket, AgentMemory]:
    """Cooldown 0, one co-located crewmate, a pending fake task elsewhere."""

    packet = _packet(
        tick=5,
        room="ADMIN",
        pending_task_id="wires_electrical",
        cooldown=0,
        visible_players=(PlayerView(id="crew-1", room="ADMIN", action=None),),
    )
    memory = _memory(
        _saw_player_event(tick=5, player_id="crew-1", room="ADMIN"),
        _cooldown_event(tick=5, cooldown=0),
    )
    return packet, memory


# --------------------------------------------------------------------------- #
# 1. Artifact parity pins (the committed copy, pinned by test — never imported).#
# --------------------------------------------------------------------------- #


def test_weights_payload_is_byte_identical_to_the_training_artifact() -> None:
    agents_payload = CHAMPION_WEIGHTS_PATH.read_bytes()
    training_payload = (_TRAINING_ARTIFACT_DIR / "weights.json").read_bytes()
    assert agents_payload == training_payload


def test_sha256_sidecars_agree_and_record_the_committed_digest() -> None:
    agents_digest = CHAMPION_WEIGHTS_SIDECAR_PATH.read_text().split()[0]
    training_digest = (
        (_TRAINING_ARTIFACT_DIR / "weights.json.sha256").read_text().split()[0]
    )
    assert agents_digest == training_digest == _COMMITTED_SHA256
    # The sidecar is honest: it is the digest of the payload it sits beside.
    payload_digest = hashlib.sha256(CHAMPION_WEIGHTS_PATH.read_bytes()).hexdigest()
    assert payload_digest == _COMMITTED_SHA256
    assert committed_weights_sha256() == _COMMITTED_SHA256


def test_loader_returns_the_training_side_genome_bit_for_bit() -> None:
    weights = load_champion_weights()
    assert len(weights) == GENOME_LENGTH == 19
    training_weights = load_candidate_weights(_TRAINING_ARTIFACT_DIR)
    assert _hex_stream(weights) == _hex_stream(training_weights)


def test_loader_fails_loud_on_sidecar_drift(tmp_path: Path) -> None:
    weights_path = tmp_path / "weights.json"
    sidecar_path = tmp_path / "weights.json.sha256"
    weights_path.write_text(CHAMPION_WEIGHTS_PATH.read_text())
    sidecar_path.write_text(f"{'0' * 64}  weights.json\n")
    with pytest.raises(ValueError, match="sidecar records"):
        _verified_payload(weights_path, sidecar_path)


def test_feature_basis_matches_the_training_side_definition() -> None:
    assert OPTION_FEATURE_NAMES == TRAINING_OPTION_FEATURE_NAMES
    assert OPTION_KINDS == TRAINING_OPTION_KINDS
    assert len(OPTION_FEATURE_NAMES) == 18
    assert ENCODER_VERSION == "impostor-option-features-v1"


# --------------------------------------------------------------------------- #
# 2. Forward-pass unit tests.                                                  #
# --------------------------------------------------------------------------- #


def test_scorer_rejects_a_wrong_length_genome() -> None:
    with pytest.raises(ValueError, match="weights length"):
        LearnedImpostorScorer(weights=(0.0,) * (GENOME_LENGTH - 1))


def test_score_is_the_fsum_dot_product_plus_bias() -> None:
    weights = tuple(float(index + 1) / 7.0 for index in range(GENOME_LENGTH))
    scorer = LearnedImpostorScorer(weights=weights)
    option = ImpostorOption(
        kind="wait",
        intent=WaitIntent.model_validate(
            {"type": "wait", "actor": "imp", "payload": {}}
        ),
        target_id=None,
        features=tuple(
            float(index) / 3.0 for index in range(len(OPTION_FEATURE_NAMES))
        ),
    )
    expected = (
        math.fsum(
            weight * feature
            for weight, feature in zip(weights[:-1], option.features, strict=True)
        )
        + weights[-1]
    )
    assert scorer.score(option).hex() == expected.hex()


def test_score_accumulation_is_correctly_rounded_not_a_naive_sum() -> None:
    # The task's named hazard: swapping ``math.fsum`` for a naive ``sum()``
    # loop diverges in the last ULP. This crafted cancellation makes the
    # difference a full 1.0 — a naive left-to-right sum absorbs the middle
    # term into 1e16 and returns 0.0 — so the pin fails loudly on its own,
    # independent of whichever menus the Q4 stream happens to record. (On the
    # recorded Q4 stream itself the substitution is also loud: measured, 77 of
    # 513 option scores differ in the last ULP.)
    weights = (1e16, 1.0, -1e16) + (0.0,) * (GENOME_LENGTH - 3)
    scorer = LearnedImpostorScorer(weights=weights)
    option = ImpostorOption(
        kind="wait",
        intent=WaitIntent.model_validate(
            {"type": "wait", "actor": "imp", "payload": {}}
        ),
        target_id=None,
        features=(1.0, 1.0, 1.0) + (0.0,) * (len(OPTION_FEATURE_NAMES) - 3),
    )
    assert scorer.score(option) == 1.0
    naive = (
        sum(
            weight * feature
            for weight, feature in zip(weights[:-1], option.features, strict=True)
        )
        + weights[-1]
    )
    assert naive == 0.0  # what the forbidden naive accumulation would return


def test_evaluate_delegates_crew_decisions_to_the_fsm() -> None:
    scorer = LearnedImpostorScorer(weights=load_champion_weights())
    fsm_intent: ActionIntent = WaitIntent.model_validate(
        {"type": "wait", "actor": "crew-9", "payload": {}}
    )
    packet = _packet(tick=1, room="ADMIN", agent_id="crew-9", role="CREWMATE")
    frame = scorer.evaluate(packet, _public_map(), _memory(), fsm_intent=fsm_intent)
    assert frame.intent == fsm_intent
    assert frame.features == ()
    assert frame.scores == ()


def test_all_equal_scores_tie_break_on_the_canonical_intent_key() -> None:
    # Zero weights + zero bias score every option identically, so the argmax
    # falls through to the lexical intent-key tie-break: the ADMIN fake-task
    # menu is {do_task:swipe_card, wait} and "do_task:…" sorts first.
    scorer = LearnedImpostorScorer(weights=(0.0,) * GENOME_LENGTH)
    packet = _packet(tick=3, room="ADMIN", pending_task_id="swipe_card", cooldown=4)
    memory = _memory(_cooldown_event(tick=3, cooldown=4))
    fsm_intent: ActionIntent = WaitIntent.model_validate(
        {"type": "wait", "actor": "imp", "payload": {}}
    )
    menu = enumerate_options(packet, _public_map(), memory)
    assert sorted(intent_key(option.intent) for option in menu) == [
        "do_task:swipe_card",
        "wait",
    ]
    frame = scorer.evaluate(packet, _public_map(), memory, fsm_intent=fsm_intent)
    assert intent_key(frame.intent) == "do_task:swipe_card"
    assert frame.scores == (0.0, 0.0)


def test_menu_fails_loud_on_empty_memory_and_missing_cooldown() -> None:
    packet = _packet(tick=1, room="ADMIN")
    with pytest.raises(ValueError, match="at least one episodic event"):
        enumerate_options(packet, _public_map(), _memory())
    no_cooldown = _packet(tick=1, room="ADMIN", cooldown=None)
    memory = _memory(_cooldown_event(tick=1, cooldown=0))
    with pytest.raises(ValueError, match="integer cooldown"):
        enumerate_options(no_cooldown, _public_map(), memory)


def test_fixture_menu_and_scores_match_the_training_side_bit_for_bit() -> None:
    # The fixture-state micro-Q4: same state, both implementations, identical
    # menus (kind / target / canonical key / feature bits) and identical score
    # bits under the committed champion weights.
    weights = load_champion_weights()
    packet, memory = _kill_menu_state()
    shipped_menu = enumerate_options(packet, _public_map(), memory)
    training_menu = training_enumerate_options(packet, _public_map(), memory)
    assert [
        (option.kind, option.target_id, intent_key(option.intent))
        for option in shipped_menu
    ] == [
        (option.kind, option.target_id, training_intent_key(option.intent))
        for option in training_menu
    ]
    assert [_hex_stream(option.features) for option in shipped_menu] == [
        _hex_stream(option.features) for option in training_menu
    ]
    assert {option.kind for option in shipped_menu} == {
        "kill_now",
        "reposition",
        "wait",
    }
    scorer = LearnedImpostorScorer(weights=weights)
    training_policy = UtilityScorerPolicy(
        weights=weights, game_map=load_canonical_map()
    )
    assert [scorer.score(option).hex() for option in shipped_menu] == [
        training_policy._score(option).hex() for option in training_menu
    ]


def test_intent_key_matches_the_training_side_canonicalization() -> None:
    packet, memory = _kill_menu_state()
    for option in training_enumerate_options(packet, _public_map(), memory):
        assert intent_key(option.intent) == training_intent_key(option.intent)
    # Every canonicalization branch — not just the ones a fixture menu happens
    # to emit — is value-pinned against the training-side reference, so the
    # reimplementation cannot drift on a rarely-menued intent kind.
    all_kinds: tuple[ActionIntent, ...] = (
        MoveIntent.model_validate(
            {"type": "move", "actor": "imp", "payload": {"to_room": "STORAGE"}}
        ),
        KillIntent.model_validate(
            {"type": "kill", "actor": "imp", "payload": {"target": "p-3"}}
        ),
        VentIntent.model_validate(
            {"type": "vent", "actor": "imp", "payload": {"vent_id": "v-1"}}
        ),
        DoTaskIntent.model_validate(
            {"type": "do_task", "actor": "imp", "payload": {"task_id": "t-5"}}
        ),
        ReportBodyIntent.model_validate(
            {"type": "report", "actor": "imp", "payload": {"body_id": "b-1"}}
        ),
        SabotageIntent.model_validate(
            {"type": "sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
        ),
        RepairSabotageIntent.model_validate(
            {"type": "repair_sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
        ),
        WaitIntent(actor="imp", type="wait"),
        EmergencyMeetingIntent(actor="imp", type="emergency"),
    )
    assert [intent_key(intent) for intent in all_kinds] == [
        training_intent_key(intent) for intent in all_kinds
    ]
    assert [intent_key(intent) for intent in all_kinds] == [
        "move:STORAGE",
        "kill:p-3",
        "vent:v-1",
        "do_task:t-5",
        "report:b-1",
        "sabotage:reactor",
        "repair:reactor",
        "wait",
        "emergency",
    ]


# --------------------------------------------------------------------------- #
# 3. The Q4 bit-exact cross-implementation gate (decision 6).                  #
# --------------------------------------------------------------------------- #


def test_q4_gate_training_and_shipped_passes_are_bit_exact_over_a_stream() -> None:
    """The task's spine: both implementations over the committed weights across
    a recorded decision stream (fixed seeds, full option menus) — bit-identical
    float64 scores (and features) and identical chosen intents, per decision.
    """

    weights = load_champion_weights()
    game_map = load_canonical_map()
    training_policy = UtilityScorerPolicy(weights=weights, game_map=game_map)
    shipped_scorer = LearnedImpostorScorer(weights=weights)

    decisions = 0
    multi_option_decisions = 0
    mismatches: list[str] = []

    def compare(
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        fsm_intent: ActionIntent,
        chosen: ActionIntent,
    ) -> None:
        nonlocal decisions, multi_option_decisions
        decisions += 1
        training_frame = training_policy.evaluate(
            packet, public_map, memory, fsm_intent=fsm_intent
        )
        shipped_frame = shipped_scorer.evaluate(
            packet, public_map, memory, fsm_intent=fsm_intent
        )
        if len(shipped_frame.scores) > 1:
            multi_option_decisions += 1
        where = f"agent {packet.agent_id} tick {packet.tick}"
        if _hex_stream(training_frame.logits) != _hex_stream(shipped_frame.scores):
            mismatches.append(f"{where}: score bits diverged")
        if _hex_stream(training_frame.features) != _hex_stream(shipped_frame.features):
            mismatches.append(f"{where}: feature bits diverged")
        if training_frame.intent != shipped_frame.intent:
            mismatches.append(f"{where}: chosen intents diverged")
        if shipped_frame.intent != chosen:
            mismatches.append(f"{where}: shipped intent != the intent that drove")

    with tempfile.TemporaryDirectory(prefix="ailibi-q4-gate-") as tmp:
        for seed in _Q4_SEEDS:
            rollout_candidate(
                training_policy,
                seed,
                output_dir=Path(tmp),
                game_map=game_map,
                on_decision=compare,
            )

    assert not mismatches, mismatches
    # The stream is non-trivial: real impostor decisions with FULL option menus
    # (a single-option menu cannot exercise the argmax) were compared.
    assert decisions > 0
    assert multi_option_decisions > 0


def test_champion_weights_config_pins_the_shipped_feature_basis() -> None:
    # The committed config.json's feature_names are the training-side record of
    # the basis the genome was trained on; the shipped basis must equal it.
    config: Mapping[str, Any] = json.loads(
        (_TRAINING_ARTIFACT_DIR / "config.json").read_text()
    )
    assert tuple(config["feature_names"]) == OPTION_FEATURE_NAMES
    assert config["genome_length"] == GENOME_LENGTH
    assert config["encoder_version"] == ENCODER_VERSION
    assert config["entrant"] == "utility-es"
