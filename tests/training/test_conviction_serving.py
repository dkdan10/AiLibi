"""Tests for the live conviction serving path (Task 18.30).

Four sections, mirroring ``tests/training/test_conviction_model.py`` idioms
(module ``_REPO_ROOT`` paths, module-scoped corpus fixture):

* **The parity pin** — the contract's heart. A test-local, hash-verified live
  walker re-drives the committed corpus TEST split through real
  :class:`~orchestrator.game.TacticalAgent` instances and asserts the
  live-assembled feature vector equals the offline table's row
  feature-for-feature (exact ``==``, every ``CONVICTION_FEATURE_NAMES`` entry,
  every meeting; the count is pinned so silent under-coverage fails). The walker
  carries its own re-drive because ``eval.funnel._walk_game_vj`` does not expose
  the live agents at meeting-open; it is hash-verified per tick and meeting, so
  any drift fails loud.
* **The accessors** — synthetic deterministic scenarios for the 18.30 kill/body
  ``*_for_meeting`` pair, driven through real ``ingest_packet`` writes (the §4.7
  fellow-set path exercised through a ``self_state`` row exactly as production
  writes it): the crew-witness kill row surfaces, an impostor's teammate-kill is
  excluded, malformed rows contribute nothing, and the body Rule-1 join honours
  first-sighting-only, the window boundaries, the victim exclusion, the teammate
  exclusion, and the kill/vent-stamped co-presence feed.
* **The assembler** — the key set AND order match ``CONVICTION_FEATURE_NAMES``,
  an absent graph row reads the neutral 0.5 prior, and a malformed meeting_id /
  missing living agent / non-conforming agent each fail loud.
* **The serving runner** — one predict + record per meeting, ``on_features``
  receives the assembled mapping, the inner artifacts return unchanged, and a
  predict-side error propagates (never swallowed, and the inner runner is never
  reached).
"""

from __future__ import annotations

import asyncio
import tempfile
from collections.abc import Mapping
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from agents.base import AgentInterface
from agents.memory.episodic import EpisodicEvent
from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED, ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import EngineEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from meetings.manager import (
    MeetingTrigger,
    derive_reported_testimony,
    extract_belief_evidence,
)
from meetings.schemas import MeetingResult, MeetingTranscript
from observation.action_intent import ActionIntent
from observation.packet import (
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.game import (
    BodyProximityRecord,
    KillWitnessRecord,
    MeetingArtifacts,
    TacticalAgent,
    apply_meeting_result,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state
from training.conviction.dataset import (
    CONVICTION_FEATURE_NAMES,
    ConvictionTable,
    build_conviction_table,
)
from training.conviction.model import ConvictionPrediction
from training.conviction.serving import (
    ConvictionServingMeetingRunner,
    LiveConvictionFeatureError,
    assemble_live_conviction_features,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"

# The committed corpus test split's meeting count (``report-conviction-model.md``
# §5: 150 games / 463 meetings, test split = 96 meetings). Pinned so a silent
# under-coverage of the parity walk fails loud.
_EXPECTED_TEST_MEETINGS = 96

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

_GLOBAL_STATE = GlobalView(
    tasks_completed=0,
    tasks_total=10,
    task_completion_percent=0.0,
    sabotage_active=False,
    sabotage_kind=None,
)


def _tactical_agent(agent_id: PlayerId, role: Role) -> TacticalAgent:
    """A real :class:`TacticalAgent` with the role-appropriate policy.

    Mirrors ``orchestrator.game.build_default_agent_factory`` so the constructed
    agent is byte-identical to what the recorded games ran, while being typed
    concretely (the kill/body accessors live on ``TacticalAgent``, not on the
    ``AgentInterface`` protocol).
    """

    policy: CrewmatePolicy | ImpostorPolicy
    if role == "IMPOSTOR":
        policy = ImpostorPolicy(agent_id=agent_id)
    else:
        policy = CrewmatePolicy(agent_id=agent_id)
    return TacticalAgent(agent_id=agent_id, policy=policy, role=role)


# ---------------------------------------------------------------------------
# The parity pin — the contract's heart
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def corpus_conviction() -> ConvictionTable:
    """The committed 150-game corpus conviction table (~9s; shared)."""

    return build_conviction_table(_CORPUS)


def _walk_game_live(
    replay_path: Path,
    *,
    seed: int,
    knobs: tuple[int, int, int],
    game_map: Map,
) -> list[tuple[str, dict[str, float]]]:
    """Re-drive one recorded game through real agents, assembling live features.

    Adapted from the SPIKE-VALIDATED walker (mirrors
    ``eval.funnel._walk_game_vj``): re-seed the game, feed every living player a
    per-tick observation packet through ``ingest_packet`` exactly as
    ``TacticalAgent.decide`` does, advance the engine with the recorded actions,
    and HASH-VERIFY every tick and meeting against the replay — so any semantics
    drift fails loud rather than silently comparing garbage. At each meeting-open
    it calls the production :func:`assemble_live_conviction_features` on the live
    agents, then applies the recorded meeting result and folds the evidence back
    into every living agent (the orchestrator's post-meeting belief update).
    Returns ``(meeting_id, live_features)`` per meeting in replay order.
    """

    num_players, num_impostors, tasks_per_crewmate = knobs
    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    roles = {player_id: player.role for player_id, player in state.players.items()}
    agents: dict[PlayerId, TacticalAgent] = {
        player_id: _tactical_agent(player_id, roles[player_id])
        for player_id in sorted(state.players)
    }

    results: list[tuple[str, dict[str, float]]] = []
    with tempfile.TemporaryDirectory(prefix="ailibi-parity-") as tmp:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(tmp) / "audit.jsonl"
        )
        last_events: tuple[EngineEvent, ...] = ()
        for entry in tick_entries:
            for player_id in sorted(state.players):
                if not state.players[player_id].alive:
                    continue
                packet = service.build_packet(
                    world_state=state,
                    agent_id=player_id,
                    engine_events=last_events,
                )
                ingest_packet(
                    packet=packet,
                    memory=agents[player_id].memory.episodic,
                    beliefs=agents[player_id].memory.beliefs,
                )
            actions = [_ACTION_ADAPTER.validate_python(a) for a in entry.actions]
            state, events = advance_tick(state, actions, game_map=game_map)
            assert _state_hash(state) == entry.state_hash, (
                f"state-hash drift at tick {entry.tick} of seed {seed}"
            )
            if state.phase == "GAME_OVER":
                break
            if state.phase != "MEETING":
                last_events = tuple(events)
                continue

            meeting_entry = meeting_by_tick[entry.tick]
            trigger_event: MeetingTriggeredEvent | None = None
            for event in events:
                if isinstance(event, MeetingTriggeredEvent):
                    trigger_event = event
            assert trigger_event is not None
            body_id = (
                trigger_event.body_id if trigger_event.trigger == "report" else None
            )

            live = assemble_live_conviction_features(
                meeting_id=meeting_entry.meeting_id, state=state, agents=agents
            )
            results.append((meeting_entry.meeting_id, live))

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
            pre_meeting_events = tuple(events)
            state, post_events = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            assert _state_hash(state) == meeting_entry.state_hash_after, (
                f"meeting state-hash drift at tick {entry.tick} of seed {seed}"
            )
            evidence = extract_belief_evidence(
                result, trigger_kind=trigger_event.trigger
            )
            statements = derive_reported_testimony(result)
            for player_id in sorted(state.players):
                if not state.players[player_id].alive:
                    continue
                agents[player_id].absorb_meeting_evidence(
                    accused=evidence.accused,
                    corroborated=evidence.corroborated,
                    contradicted=evidence.contradicted,
                )
                agents[player_id].absorb_reported_testimony(statements=statements)
            last_events = pre_meeting_events + tuple(post_events)
            if state.phase == "GAME_OVER":
                break
    return results


def test_live_assembly_matches_offline_table_over_test_split(
    corpus_conviction: ConvictionTable,
) -> None:
    """The parity pin: live-assembled == offline table, feature-for-feature.

    Over the committed corpus TEST split, every ``CONVICTION_FEATURE_NAMES``
    entry of every meeting's live-assembled vector equals the offline table's
    row EXACTLY (not approx — the live/offline semantics gap closes by
    measurement). Also pins the 1:1 join on ``(seed, meeting_id)`` and the 96
    meeting count, so neither a silent under-coverage nor an unmatched offline
    row can pass.
    """

    splits = corpus_conviction.splits
    assert splits is not None, "the committed corpus must ship splits.json"
    test_seeds = sorted(splits.test)
    test_seed_set = frozenset(test_seeds)
    offline = {
        (row.seed, row.meeting_id): dict(row.features)
        for row in corpus_conviction.rows
        if row.seed in test_seed_set
    }
    assert len(offline) == _EXPECTED_TEST_MEETINGS, (
        f"offline test split carries {len(offline)} meetings, expected "
        f"{_EXPECTED_TEST_MEETINGS}"
    )

    game_map = load_canonical_map()
    knobs = (
        corpus_conviction.num_players,
        corpus_conviction.num_impostors,
        corpus_conviction.tasks_per_crewmate,
    )
    meetings_checked = 0
    for seed in test_seeds:
        live_rows = _walk_game_live(
            _CORPUS / f"replay-seed-{seed}.jsonl",
            seed=seed,
            knobs=knobs,
            game_map=game_map,
        )
        for meeting_id, live in live_rows:
            meetings_checked += 1
            key = (seed, meeting_id)
            assert key in offline, (
                f"live meeting {key} has no offline row — the 1:1 join failed"
            )
            expected = offline.pop(key)
            for name in CONVICTION_FEATURE_NAMES:
                assert live[name] == expected[name], (
                    f"seed={seed} {meeting_id} feature {name}: live={live[name]!r} "
                    f"!= offline={expected[name]!r}"
                )

    assert meetings_checked == _EXPECTED_TEST_MEETINGS, (
        f"walked {meetings_checked} test-split meetings, expected "
        f"{_EXPECTED_TEST_MEETINGS} — silent under-coverage"
    )
    assert not offline, (
        f"offline rows left unmatched (1:1 join failed): {sorted(offline)}"
    )


# ---------------------------------------------------------------------------
# The accessors — synthetic deterministic scenarios
# ---------------------------------------------------------------------------


def _ingest(
    agent: TacticalAgent,
    *,
    tick: int,
    role: Role = "CREWMATE",
    self_room: str = "cafeteria",
    fellows: tuple[str, ...] = (),
    players: tuple[PlayerView, ...] = (),
    bodies: tuple[BodyView, ...] = (),
) -> None:
    """Ingest one hand-built packet into an agent through the real write path.

    Exercises ``agents.perception.ingest_packet``, so the ``self_state`` row —
    including ``fellow_impostor_ids`` — is written exactly as production writes
    it (the §4.7 fellow-set path the kill/body accessors read).
    """

    packet = ObservationPacket(
        tick=tick,
        agent_id=agent.agent_id,
        self_state=SelfView(
            room=self_room,
            role=role,
            pending_task_id=None,
            fellow_impostor_ids=fellows,
        ),
        visible_players=players,
        visible_bodies=bodies,
        audible_events=(),
        global_state=_GLOBAL_STATE,
        cooldown=None,
    )
    ingest_packet(packet=packet, memory=agent.memory.episodic)


def test_kill_witness_record_surfaces_for_a_crew_witness() -> None:
    """A crew witness's ``saw_player`` action-``kill`` row surfaces one record."""

    agent = _tactical_agent("OBS", "CREWMATE")
    _ingest(
        agent,
        tick=5,
        players=(PlayerView(id="K", room="cafeteria", action="kill"),),
    )
    assert agent.kill_witness_records_for_meeting() == (
        KillWitnessRecord(subject="K", room="cafeteria", tick=5),
    )


def test_kill_witness_record_excludes_a_fellow_impostors_kill() -> None:
    """§4.7: an impostor's witnessed TEAMMATE kill never pins; others still do.

    The killer named in the impostor observer's own ``self_state``
    ``fellow_impostor_ids`` is dropped (the crew-witnesses-only offline
    restriction, equivalently the belief rule's teammate guard), while a
    non-teammate killer the same impostor witnesses still surfaces a record.
    """

    agent = _tactical_agent("OBS", "IMPOSTOR")
    _ingest(
        agent,
        tick=5,
        role="IMPOSTOR",
        fellows=("K",),
        players=(PlayerView(id="K", room="electrical", action="kill"),),
    )
    assert agent.kill_witness_records_for_meeting() == ()

    _ingest(
        agent,
        tick=6,
        role="IMPOSTOR",
        fellows=("K",),
        players=(PlayerView(id="C", room="electrical", action="kill"),),
    )
    assert agent.kill_witness_records_for_meeting() == (
        KillWitnessRecord(subject="C", room="electrical", tick=6),
    )


def test_kill_witness_records_ignore_malformed_rows_and_are_tick_sorted() -> None:
    """A malformed kill row contributes nothing; output follows append order."""

    agent = _tactical_agent("OBS", "CREWMATE")
    _ingest(
        agent,
        tick=3,
        players=(PlayerView(id="K1", room="cafeteria", action="kill"),),
    )
    _ingest(
        agent,
        tick=7,
        players=(PlayerView(id="K2", room="medbay", action="kill"),),
    )
    # A malformed first-hand kill row (non-str subject) is defensively skipped.
    agent.memory.episodic.append(
        EpisodicEvent(
            tick=8,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": 123, "room": "storage", "action": "kill"},
            provenance=PROVENANCE_OBSERVED,
        )
    )
    assert agent.kill_witness_records_for_meeting() == (
        KillWitnessRecord(subject="K1", room="cafeteria", tick=3),
        KillWitnessRecord(subject="K2", room="medbay", tick=7),
    )


def test_body_proximity_window_victim_and_action_stamps() -> None:
    """The Rule-1 join: window boundaries, victim, and kill/vent co-presence.

    A body discovered at tick 10 in ``electrical`` pins every player the
    observer saw in that room within ``[discovery-3, discovery-1]``: the
    ``discovery-3`` sighting is IN, ``discovery-4`` is OUT, a same-tick sighting
    is OUT (strictly-before window), a sighting in another room is OUT, the
    victim is OUT, and kill/vent-stamped sightings DO feed co-presence.
    """

    obs = _tactical_agent("OBS", "CREWMATE")
    room = "electrical"
    _ingest(obs, tick=6, players=(PlayerView(id="A", room=room, action=None),))
    _ingest(obs, tick=7, players=(PlayerView(id="B", room=room, action=None),))
    _ingest(
        obs,
        tick=8,
        players=(
            PlayerView(id="C", room=room, action="kill"),
            PlayerView(id="Z", room="cafeteria", action=None),
        ),
    )
    _ingest(
        obs,
        tick=9,
        players=(
            PlayerView(id="V", room=room, action=None),
            PlayerView(id="D", room=room, action="vent"),
        ),
    )
    _ingest(
        obs,
        tick=10,
        players=(PlayerView(id="E", room=room, action=None),),
        bodies=(BodyView(id="b1", room=room, victim_id="V"),),
    )
    assert obs.body_proximity_records_for_meeting() == (
        BodyProximityRecord(subject="B", room=room, tick=10),
        BodyProximityRecord(subject="C", room=room, tick=10),
        BodyProximityRecord(subject="D", room=room, tick=10),
    )


def test_body_proximity_fires_on_first_sighting_only() -> None:
    """A re-sighting of the same body pins nothing (Rule 1 fires on the first)."""

    obs = _tactical_agent("OBS", "CREWMATE")
    room = "storage"
    _ingest(obs, tick=5, players=(PlayerView(id="A", room=room, action=None),))
    _ingest(obs, tick=6, bodies=(BodyView(id="b1", room=room, victim_id="V"),))
    _ingest(obs, tick=7, players=(PlayerView(id="B", room=room, action=None),))
    _ingest(obs, tick=8, bodies=(BodyView(id="b1", room=room, victim_id="V"),))
    assert obs.body_proximity_records_for_meeting() == (
        BodyProximityRecord(subject="A", room=room, tick=6),
    )


def test_body_proximity_excludes_a_fellow_impostor_for_an_impostor_observer() -> None:
    """§4.7: an impostor observer's teammate is dropped from the pin set."""

    obs = _tactical_agent("OBS", "IMPOSTOR")
    room = "reactor"
    _ingest(
        obs,
        tick=5,
        role="IMPOSTOR",
        fellows=("T",),
        players=(
            PlayerView(id="T", room=room, action=None),
            PlayerView(id="X", room=room, action=None),
        ),
    )
    _ingest(
        obs,
        tick=6,
        role="IMPOSTOR",
        fellows=("T",),
        bodies=(BodyView(id="b1", room=room, victim_id="V"),),
    )
    assert obs.body_proximity_records_for_meeting() == (
        BodyProximityRecord(subject="X", room=room, tick=6),
    )


# ---------------------------------------------------------------------------
# The assembler — unit pins
# ---------------------------------------------------------------------------


class _NonConvictionAgent:
    """An :class:`AgentInterface` double lacking the conviction accessors.

    Satisfies the minimal ``AgentInterface`` protocol (only ``decide``) so it is
    a valid mapping value, but exposes none of the four ``*_for_meeting``
    accessors, so ``isinstance(agent, LiveConvictionAgent)`` is ``False`` and the
    assembler fails loud.
    """

    def __init__(self, agent_id: PlayerId) -> None:
        self._agent_id = agent_id

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        raise AssertionError("the assembler never calls decide()")


def _seeded_state() -> WorldState:
    """A fresh 4p1i world state (all four players alive)."""

    return seed_initial_state(
        seed=0,
        game_map=load_canonical_map(),
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=2,
    )


def _empty_agents(state: WorldState) -> dict[PlayerId, TacticalAgent]:
    """One unseeded real agent per player (every belief cell reads 0.5)."""

    return {
        player_id: _tactical_agent(player_id, player.role)
        for player_id, player in state.players.items()
    }


def test_assembler_key_set_and_order_match_feature_names_and_default_to_prior() -> None:
    """The vector's key set AND order are ``CONVICTION_FEATURE_NAMES``; an
    unseeded roster reads the neutral 0.5 prior on every non-self cell."""

    state = _seeded_state()
    features = assemble_live_conviction_features(
        meeting_id="headless-seed-0:meeting-0",
        state=state,
        agents=_empty_agents(state),
    )
    assert tuple(features) == CONVICTION_FEATURE_NAMES
    assert features["alive_count"] == 4.0
    assert features["meeting_index"] == 0.0
    assert features["max_suspicion"] == 0.5
    assert features["mean_suspicion"] == 0.5
    assert features["suspicion_margin"] == 0.0
    assert features["cells_at_gate"] == 0.0
    assert features["vent_witness_pairs"] == 0.0
    assert features["vent_witnessed_candidates"] == 0.0
    assert features["kill_pin_pairs"] == 0.0
    assert features["kill_pinned_candidates"] == 0.0
    assert features["body_proximity_pairs"] == 0.0
    assert features["body_proximity_candidates"] == 0.0


def test_assembler_raises_on_malformed_meeting_id() -> None:
    """A meeting_id without the orchestrator's format fails loud."""

    state = _seeded_state()
    with pytest.raises(
        LiveConvictionFeatureError, match="does not carry the orchestrator"
    ):
        assemble_live_conviction_features(
            meeting_id="no-index", state=state, agents=_empty_agents(state)
        )


def test_assembler_raises_on_missing_living_agent() -> None:
    """A living voter with no constructed agent fails loud."""

    state = _seeded_state()
    agents = _empty_agents(state)
    living = sorted(pid for pid, player in state.players.items() if player.alive)
    del agents[living[0]]
    with pytest.raises(LiveConvictionFeatureError, match="no agent for living player"):
        assemble_live_conviction_features(
            meeting_id="headless-seed-0:meeting-0", state=state, agents=agents
        )


def test_assembler_raises_on_non_conforming_agent() -> None:
    """A voter agent missing the conviction accessors fails loud."""

    state = _seeded_state()
    agents: dict[PlayerId, AgentInterface] = dict(_empty_agents(state))
    living = sorted(pid for pid, player in state.players.items() if player.alive)
    agents[living[0]] = _NonConvictionAgent(living[0])
    with pytest.raises(
        LiveConvictionFeatureError, match="does not expose the conviction serving"
    ):
        assemble_live_conviction_features(
            meeting_id="headless-seed-0:meeting-0", state=state, agents=agents
        )


# ---------------------------------------------------------------------------
# The serving runner — recording wrapper pins
# ---------------------------------------------------------------------------


class _RecordingInner:
    """A canned inner :class:`~orchestrator.game.MeetingRunner`.

    Records every ``meeting_id`` it is delegated and returns a fixed
    :class:`MeetingArtifacts`, so the wrapper's delegate-and-return-unchanged
    behaviour is observable.
    """

    def __init__(self, artifacts: MeetingArtifacts) -> None:
        self._artifacts = artifacts
        self.calls: list[str] = []

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        self.calls.append(meeting_id)
        return self._artifacts


def _canned_artifacts() -> MeetingArtifacts:
    result = MeetingResult(
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-1",
        trigger_tick=0,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        contradictions=(),
        transcript=MeetingTranscript(),
    )
    return MeetingArtifacts(result=result, llm_calls=(), prompt_versions={})


def test_serving_runner_predicts_records_and_delegates_unchanged() -> None:
    """One predict + record per meeting; on_features gets the assembled mapping;
    the inner artifacts return unchanged."""

    state = _seeded_state()
    agents = _empty_agents(state)
    artifacts = _canned_artifacts()
    inner = _RecordingInner(artifacts)

    predict_calls: list[Mapping[str, float]] = []
    recorded: list[ConvictionPrediction] = []
    feature_maps: list[Mapping[str, float]] = []

    def _predict(features: Mapping[str, float]) -> ConvictionPrediction:
        predict_calls.append(features)
        return ConvictionPrediction(expected_flags=1.5, conversion_prob=0.25)

    def _record(prediction: ConvictionPrediction) -> None:
        recorded.append(prediction)

    def _on_features(features: Mapping[str, float]) -> None:
        feature_maps.append(features)

    runner = ConvictionServingMeetingRunner(
        inner=inner, predict=_predict, record=_record, on_features=_on_features
    )
    trigger = MeetingTrigger(
        triggered_by="p-1", trigger_tick=state.tick, description="reported a body"
    )
    returned = asyncio.run(
        runner.run_meeting(
            meeting_id="headless-seed-0:meeting-0",
            trigger=trigger,
            state=state,
            agents=agents,
        )
    )

    assert returned is artifacts
    assert inner.calls == ["headless-seed-0:meeting-0"]
    assert len(predict_calls) == 1
    assert recorded == [ConvictionPrediction(expected_flags=1.5, conversion_prob=0.25)]
    assert len(feature_maps) == 1
    assert tuple(feature_maps[0]) == CONVICTION_FEATURE_NAMES
    assert feature_maps[0] == assemble_live_conviction_features(
        meeting_id="headless-seed-0:meeting-0", state=state, agents=agents
    )


def test_serving_runner_propagates_a_predict_side_error() -> None:
    """A predict-side raise propagates; record and the inner runner never run."""

    state = _seeded_state()
    agents = _empty_agents(state)
    inner = _RecordingInner(_canned_artifacts())

    def _predict(features: Mapping[str, float]) -> ConvictionPrediction:
        raise RuntimeError("staleness cap spent")

    def _record(prediction: ConvictionPrediction) -> None:
        raise AssertionError("record must not run when predict raises")

    runner = ConvictionServingMeetingRunner(
        inner=inner, predict=_predict, record=_record
    )
    trigger = MeetingTrigger(
        triggered_by="p-1", trigger_tick=state.tick, description="emergency"
    )
    with pytest.raises(RuntimeError, match="staleness cap spent"):
        asyncio.run(
            runner.run_meeting(
                meeting_id="headless-seed-0:meeting-0",
                trigger=trigger,
                state=state,
                agents=agents,
            )
        )
    assert inner.calls == []
