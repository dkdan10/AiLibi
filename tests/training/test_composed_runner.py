"""Definition-of-done tests for the composed meeting-outcome runner (Task 18.29).

The composed runner asks the committed conviction model WHETHER a meeting
convicts and the committed ballot surrogate's ranking channel WHO, then
synthesizes ballots coherently with that outcome through the REAL
:func:`meetings.voting.tally_ballots` — no learned parameter of its own. These
tests pin that contract end to end against the committed artifacts and the
committed 9p2i corpus:

* the runner IS a runtime-checkable :class:`~orchestrator.game.MeetingRunner`;
* the SKIP branch passes the surrogate's ballots through unchanged (field-for-
  field except the audit rationale), and the outcome IS the real tally;
* the CONVICT branch re-anchors onto the ranked target so the real tally ejects
  it, the re-anchored ballots carry the audit marker, and an anchor ballot
  reaches the 0.6 gate;
* the §7.12 teammate firewall survives — an impostor's ballot never names a
  fellow impostor, including after re-anchoring onto an impostor target;
* both component use-counters meter every composed meeting (surrogate at entry,
  conviction on delivery), cumulatively across runners from one factory, and a
  spent cap on either component fails loud;
* both artifacts are sha-verified on load and fail loud before any use, and a
  NO-GO conviction verdict makes the runner structurally unbuildable;
* a full composed-driven :class:`~orchestrator.game.HeadlessGame` completes with
  every recorded meeting an honest tally of its own ballots, byte-deterministic
  across runs, and the belief fold consuming the ballot roster;
* ``decide_composed_go`` applies the pre-registered bar (strict on decision,
  inclusive on top-1, exact-outcome never gating);
* the held-out fidelity scores exactly the committed test split (96/60) with the
  standing top-1 recipe; and
* the composed-path Goodhart leg runs 18.18's machinery over the composed runner
  with the component consumption metered on the shared sha-keyed counters.

Two committed-artifact PIN tests at the end load ``training/artifacts/composed/``
directly (the reproduce identity). They FAIL until the orchestrator commits the
composed artifacts in a later phase — that is expected in this phase.
"""

from __future__ import annotations

import asyncio
import re
from collections.abc import Mapping
from pathlib import Path

import numpy as np
import pytest

from agents.base import AgentInterface
from agents.memory.store import DEFAULT_TOKEN_BUDGET
from engine.entities import PlayerId, Role
from engine.world import WorldState, load_canonical_map
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger, SuspicionEntry
from meetings.schemas import ObservationId, SightingRecord, VentWitnessRecord
from meetings.voting import tally_ballots
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    BodyProximityRecord,
    HeadlessGame,
    KillWitnessRecord,
    MeetingArtifacts,
    MeetingRunner,
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import ConvictionPathProbeReport
from training.composed_runner import (
    COMPOSED_MANIFEST_FILENAME,
    COMPOSED_VERDICT_FILENAME,
    ComposedFidelityReport,
    ComposedGoVerdict,
    ComposedGoodhartLeg,
    ComposedMeetingRunner,
    _COMPOSED_RATIONALE,  # noqa: PLC2701 - the audit-marker fence is under test
    _REANCHOR_RATIONALE,  # noqa: PLC2701 - the audit-marker fence is under test
    build_composed_manifest,
    decide_composed_go,
    load_composed_components,
    load_composed_manifest,
    load_composed_runner_factory,
    load_composed_verdict,
    run_composed_fidelity,
    run_composed_goodhart_leg,
    write_composed_manifest_artifact,
    write_composed_verdict_artifact,
)
from training.conviction.fidelity import (
    CONVICTION_CONVERSION_DECISION_THRESHOLD,
    load_conviction_verdict,
)
from training.conviction.model import (
    ConvictionStalenessCap,
    ConvictionStalenessExceededError,
    ConvictionUseCounter,
    load_conviction_model_artifact,
)
from training.conviction.serving import assemble_live_conviction_features
from training.surrogate.ballots import (
    BallotPredictor,
    SurrogateStalenessCap,
    VoterBallotView,
    load_ballot_predictor_artifact,
)
from training.surrogate.runner import (
    SurrogateMeetingRunner,
    SurrogateStalenessExceededError,
    SurrogateUseCounter,
    load_surrogate_runner_factory,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_CONVICTION_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "conviction"
_SURROGATE_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "surrogate"
_COMPOSED_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "composed"


def _composed_factory() -> object:
    """A committed-artifact composed-runner factory (fresh use-counters)."""

    return load_composed_runner_factory(
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
    )


# --------------------------------------------------------------------------- #
# Test doubles                                                                 #
# --------------------------------------------------------------------------- #


class _CannedConvictionAgent:
    """A minimal agent satisfying BOTH meeting protocols the composed runner reads.

    Implements :class:`~orchestrator.game.MeetingAwareAgent` (the surrogate leg's
    inputs) AND :class:`training.conviction.serving.LiveConvictionAgent` (the four
    conviction-serving accessors, incl. the 18.30 kill/body pins) so the composed
    runner's WHETHER assembler accepts it. Every channel is parameterizable; an
    empty one reads the neutral prior.
    """

    def __init__(
        self,
        agent_id: PlayerId,
        *,
        suspicion_graph: tuple[SuspicionEntry, ...] = (),
        vent_records: tuple[VentWitnessRecord, ...] = (),
        kill_records: tuple[KillWitnessRecord, ...] = (),
        body_records: tuple[BodyProximityRecord, ...] = (),
    ) -> None:
        self._agent_id = agent_id
        self._suspicion_graph = suspicion_graph
        self._vent_records = vent_records
        self._kill_records = kill_records
        self._body_records = body_records

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return "CREWMATE"

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        raise AssertionError("the composed runner never calls decide()")

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        return ""

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return self._suspicion_graph

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        return self._vent_records

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        return ()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        return ()

    def kill_witness_records_for_meeting(self) -> tuple[KillWitnessRecord, ...]:
        return self._kill_records

    def body_proximity_records_for_meeting(self) -> tuple[BodyProximityRecord, ...]:
        return self._body_records


class _RecordingConvictionAgent:
    """A delegating agent that records the belief-fold ``absorb_meeting_evidence``.

    Forwards every meeting accessor the composed runner reads (incl. the 18.30
    kill/body pins) to a real :class:`~orchestrator.game.TacticalAgent`, so the
    live beliefs are genuine, and records each absorb call for the fold-survival
    pin.
    """

    def __init__(self, inner: TacticalAgent, absorbed: list[PlayerId]) -> None:
        self._inner = inner
        self._absorbed = absorbed

    @property
    def agent_id(self) -> PlayerId:
        return self._inner.agent_id

    @property
    def role(self) -> Role:
        return self._inner.role

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return self._inner.decide(packet, public_map)

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        return self._inner.render_memory_for_meeting(
            token_budget=token_budget, suspicion_override=suspicion_override
        )

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return self._inner.suspicion_graph_for_meeting()

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        return self._inner.vent_witness_records_for_meeting()

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        return self._inner.sighting_records_for_meeting()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        return self._inner.observation_ids_for_meeting()

    def kill_witness_records_for_meeting(self) -> tuple[KillWitnessRecord, ...]:
        return self._inner.kill_witness_records_for_meeting()

    def body_proximity_records_for_meeting(self) -> tuple[BodyProximityRecord, ...]:
        return self._inner.body_proximity_records_for_meeting()

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None:
        self._absorbed.append(self._inner.agent_id)
        self._inner.absorb_meeting_evidence(
            accused=accused, corroborated=corroborated, contradicted=contradicted
        )


def _seed_state(*, num_players: int, num_impostors: int) -> WorldState:
    return seed_initial_state(
        seed=0,
        game_map=load_canonical_map(),
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=2,
    )


def _canned_agents(
    state: WorldState,
    *,
    graphs: Mapping[PlayerId, tuple[SuspicionEntry, ...]] | None = None,
    vent: tuple[VentWitnessRecord, ...] = (),
    kill: tuple[KillWitnessRecord, ...] = (),
    body: tuple[BodyProximityRecord, ...] = (),
) -> dict[PlayerId, AgentInterface]:
    graphs = graphs or {}
    return {
        pid: _CannedConvictionAgent(
            pid,
            suspicion_graph=graphs.get(pid, ()),
            vent_records=vent,
            kill_records=kill,
            body_records=body,
        )
        for pid in state.players
    }


def _drive(
    runner: object,
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    *,
    meeting_id: str,
    triggered_by: PlayerId,
) -> MeetingArtifacts:
    trigger = MeetingTrigger(
        triggered_by=triggered_by,
        trigger_tick=state.tick,
        description="reported a body",
    )
    assert isinstance(runner, ComposedMeetingRunner | SurrogateMeetingRunner)
    return asyncio.run(
        runner.run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )
    )


def _independent_ranking(
    state: WorldState,
    agents: Mapping[PlayerId, AgentInterface],
    *,
    triggered_by: PlayerId,
    predictor: BallotPredictor,
    meeting_index: float,
) -> tuple[PlayerId, ...]:
    """Recompute the surrogate Form-B ranking off predict_ballot, independently."""

    living = tuple(sorted(p for p, pl in state.players.items() if pl.alive))
    impostors = frozenset(p for p, pl in state.players.items() if pl.role == "IMPOSTOR")
    alive_count = float(len(living))
    by_voter: dict[PlayerId, Mapping[PlayerId, float]] = {}
    for voter in living:
        agent = agents[voter]
        assert isinstance(agent, _CannedConvictionAgent)
        graph = {e.player_id: e for e in agent.suspicion_graph_for_meeting()}
        vent = frozenset(r.subject for r in agent.vent_witness_records_for_meeting())
        teammates = impostors - {voter} if voter in impostors else frozenset()
        candidates = tuple(c for c in living if c != voter and c not in teammates)
        features = {
            cand: {
                "belief_suspicion": (
                    float(graph[cand].suspicion) if cand in graph else 0.5
                ),
                "belief_trust": float(graph[cand].trust) if cand in graph else 0.5,
                "is_reporter": float(cand == triggered_by),
                "witnessed_vent": float(cand in vent),
                "meeting_index": meeting_index,
                "alive_count": alive_count,
            }
            for cand in candidates
        }
        predicted = predictor.predict_ballot(
            VoterBallotView(voter=voter, candidates=candidates, features=features)
        )
        by_voter[voter] = predicted.target_probs
    sorted_voters = sorted(by_voter)
    shares: dict[PlayerId, float] = {}
    for cand in living:
        masses = [by_voter[v].get(cand, 0.0) for v in sorted_voters if v != cand]
        shares[cand] = float(np.mean(masses)) if masses else 0.0
    return tuple(sorted(living, key=lambda cand: (-shares[cand], cand)))


# --------------------------------------------------------------------------- #
# Module-scoped fixtures — the expensive corpus tables, built once.            #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def composed_fidelity() -> ComposedFidelityReport:
    """Held-out composed fidelity over the committed 9p2i corpus (~15s; shared)."""

    return run_composed_fidelity(
        _CORPUS,
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
    )


@pytest.fixture(scope="module")
def committed_shas() -> tuple[str, str]:
    """The committed (conviction, surrogate) weights shas."""

    _, conviction_sha = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)
    _, surrogate_sha = load_ballot_predictor_artifact(_SURROGATE_ARTIFACT_DIR)
    return conviction_sha, surrogate_sha


# --------------------------------------------------------------------------- #
# 1. PROTOCOL                                                                  #
# --------------------------------------------------------------------------- #


def test_runner_satisfies_meeting_runner_protocol() -> None:
    """A :class:`ComposedMeetingRunner` IS a runtime-checkable MeetingRunner."""

    runner = _composed_factory()()  # type: ignore[operator]
    assert isinstance(runner, ComposedMeetingRunner)
    assert isinstance(runner, MeetingRunner)


# --------------------------------------------------------------------------- #
# 2. SKIP BRANCH — pass-through equals the surrogate leg                       #
# --------------------------------------------------------------------------- #


def test_skip_branch_passes_the_surrogate_ballots_through(
    committed_shas: tuple[str, str],
) -> None:
    """Neutral evidence: the gate does not convict → ballots pass through unchanged.

    The gate's answer is never hardcoded — it is asserted by independently
    assembling the live features and predicting through the committed model. The
    composed pass-through ballots then equal the pure surrogate leg's predictions
    field-for-field (except the audit rationale), the outcome IS the real tally,
    and the artifacts echo the dispatch with no LLM metadata.
    """

    conviction_sha, _ = committed_shas
    state = _seed_state(num_players=4, num_impostors=1)
    agents = _canned_agents(state)  # empty graphs → neutral prior everywhere
    living = frozenset(p for p, pl in state.players.items() if pl.alive)

    # The gate genuinely does not convict on neutral features (asserted, not
    # hardcoded — the composed decision must equal this independent read).
    conviction_model, _ = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)
    features = assemble_live_conviction_features(
        meeting_id="headless-seed-0:meeting-0", state=state, agents=agents
    )
    assert (
        conviction_model.predict(features).conversion_prob
        < CONVICTION_CONVERSION_DECISION_THRESHOLD
    )

    composed = _drive(
        _composed_factory()(),  # type: ignore[operator]
        state,
        agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-1",
    )
    surrogate = _drive(
        load_surrogate_runner_factory(_SURROGATE_ARTIFACT_DIR)(),
        state,
        agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-1",
    )

    composed_ballots = {b.voter: b for b in composed.result.ballots}
    surrogate_ballots = {b.voter: b for b in surrogate.result.ballots}
    assert set(composed_ballots) == living
    for voter, cb in composed_ballots.items():
        sb = surrogate_ballots[voter]
        assert cb.target == sb.target
        assert cb.confidence == sb.confidence
        assert cb.primary_reason_id == sb.primary_reason_id
        assert cb.considered_alternatives == sb.considered_alternatives
        assert cb.rationale_text == _COMPOSED_RATIONALE  # the only difference

    # The outcome IS the real tally of the (pass-through) ballots.
    outcome, ejected = tally_ballots(
        composed.result.ballots,
        skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD,
    )
    assert (outcome, ejected) == (
        composed.result.outcome,
        composed.result.ejected_player_id,
    )
    # Dispatch echo + no LLM metadata + one ballot per living voter.
    assert composed.result.meeting_id == "headless-seed-0:meeting-0"
    assert composed.result.triggered_by == "p-1"
    assert composed.result.trigger_tick == state.tick
    assert composed.llm_calls == ()
    assert composed.prompt_versions == {}


# --------------------------------------------------------------------------- #
# 3. CONVICT BRANCH — re-anchor onto the ranked target through the real tally  #
# --------------------------------------------------------------------------- #


def _heavy_evidence_state(
    target: PlayerId,
) -> tuple[WorldState, dict[PlayerId, AgentInterface]]:
    """A 9p2i state whose raw provenance convicts on ``target`` (surrogate stays SKIP).

    ``entry.suspicion`` stays moderate (the surrogate reads it, and its SKIP-heavy
    decision head does not eject) while the eight raw provenance channels + the
    kill/vent/body pins are heavy (the conviction assembler recovers the RAW
    scalar, so the gate converts) — decoupled exactly as the two instruments read
    the belief cell.
    """

    state = _seed_state(num_players=9, num_impostors=2)

    def graph_for(voter: PlayerId) -> tuple[SuspicionEntry, ...]:
        entries: list[SuspicionEntry] = []
        for other in sorted(state.players):
            if other == voter:
                continue
            if other == target:
                entries.append(
                    SuspicionEntry(
                        player_id=other,
                        suspicion=0.5,
                        trust=0.45,
                        flag_lift=0.4,
                        kill_or_vent_pin=0.3,
                        body_proximity=0.2,
                    )
                )
            else:
                entries.append(
                    SuspicionEntry(player_id=other, suspicion=0.1, trust=0.6)
                )
        return tuple(entries)

    agents = _canned_agents(
        state,
        graphs={pid: graph_for(pid) for pid in state.players},
        vent=(VentWitnessRecord(subject=target, room="cafeteria", tick=1),),
        kill=(KillWitnessRecord(subject=target, room="cafeteria", tick=1),),
        body=(BodyProximityRecord(subject=target, room="cafeteria", tick=1),),
    )
    return state, agents


def test_convict_branch_reanchors_onto_the_ranked_target(
    committed_shas: tuple[str, str],
) -> None:
    """Heavy raw evidence convicts → the composition ejects the ranked target.

    The gate convicts (asserted via the public predict). The outcome IS the real
    tally, equals ``("EJECTED", ranking[0])`` for the independently-recomputed
    ranking, at least one target ballot reaches the 0.6 gate, the re-anchored
    ballots carry the audit marker, and every untouched ballot still equals the
    surrogate leg's own prediction.
    """

    _, surrogate_sha = committed_shas
    target: PlayerId = "p-1"
    state, agents = _heavy_evidence_state(target)

    conviction_model, _ = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)
    features = assemble_live_conviction_features(
        meeting_id="headless-seed-0:meeting-0", state=state, agents=agents
    )
    assert (
        conviction_model.predict(features).conversion_prob
        >= CONVICTION_CONVERSION_DECISION_THRESHOLD
    )

    predictor, _ = load_ballot_predictor_artifact(_SURROGATE_ARTIFACT_DIR)
    ranking = _independent_ranking(
        state, agents, triggered_by="p-2", predictor=predictor, meeting_index=0.0
    )
    assert ranking[0] == target  # the crafted evidence points the ranking here

    composed = _drive(
        _composed_factory()(),  # type: ignore[operator]
        state,
        agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-2",
    )
    result = composed.result
    assert (result.outcome, result.ejected_player_id) == ("EJECTED", ranking[0])
    # The decision IS the real tally of the synthesized ballots.
    assert tally_ballots(
        result.ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
    ) == (result.outcome, result.ejected_player_id)
    # At least one target ballot reaches the gate (the confidence anchor).
    target_confidences = [
        b.confidence for b in result.ballots if b.target == result.ejected_player_id
    ]
    assert max(target_confidences) >= DEFAULT_SKIP_CONFIDENCE_THRESHOLD

    # Re-anchoring genuinely fired (the surrogate is SKIP-degenerate here), the
    # re-anchored ballots carry the audit marker, and untouched ballots still
    # equal the surrogate leg's own predictions.
    reanchored = [b for b in result.ballots if b.rationale_text == _REANCHOR_RATIONALE]
    assert reanchored, "the SKIP-degenerate surrogate must force real re-anchoring"
    surrogate = _drive(
        load_surrogate_runner_factory(_SURROGATE_ARTIFACT_DIR)(),
        state,
        agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-2",
    )
    surrogate_ballots = {b.voter: b for b in surrogate.result.ballots}
    for ballot in result.ballots:
        if ballot.rationale_text == _COMPOSED_RATIONALE:
            sb = surrogate_ballots[ballot.voter]
            assert ballot.target == sb.target
            assert ballot.confidence == sb.confidence


# --------------------------------------------------------------------------- #
# 4. TEAMMATE FIREWALL — never name a fellow impostor, incl. after re-anchoring #
# --------------------------------------------------------------------------- #


def test_firewall_holds_when_the_ranked_target_is_an_impostor() -> None:
    """An impostor's ballot never names its teammate — both branches, after re-anchor.

    On a 9p2i state with two living impostors: (a) heavy raw evidence on an
    impostor target convicts and re-anchors, ejecting the impostor while its
    fellow impostor's ballot never names it; (b) a high-suspicion / no-provenance
    graph makes the surrogate rank the same impostor first WITHOUT convicting, so
    the ballots pass through and the fellow impostor still never names it.
    """

    state = _seed_state(num_players=9, num_impostors=2)
    impostors = sorted(p for p, pl in state.players.items() if pl.role == "IMPOSTOR")
    assert len(impostors) == 2
    target, teammate = impostors

    # (a) CONVICT branch — re-anchor onto the impostor target.
    _, convict_agents = _heavy_evidence_state(target)
    convict = _drive(
        _composed_factory()(),  # type: ignore[operator]
        state,
        convict_agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-1",
    )
    convict_ballots = {b.voter: b for b in convict.result.ballots}
    assert convict.result.outcome == "EJECTED"
    assert convict.result.ejected_player_id == target
    assert convict_ballots[teammate].target != target  # never the betrayal vote
    assert convict_ballots[target].target != target

    # (b) SKIP branch — surrogate ranks the impostor first, gate does not convict.
    def high_suspicion(voter: PlayerId) -> tuple[SuspicionEntry, ...]:
        return tuple(
            SuspicionEntry(
                player_id=other,
                suspicion=0.95 if other == target else 0.1,
                trust=0.5,
            )
            for other in sorted(state.players)
            if other != voter
        )

    skip_agents = _canned_agents(
        state, graphs={pid: high_suspicion(pid) for pid in state.players}
    )
    conviction_model, _ = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)
    skip_features = assemble_live_conviction_features(
        meeting_id="headless-seed-0:meeting-1", state=state, agents=skip_agents
    )
    assert (
        conviction_model.predict(skip_features).conversion_prob
        < CONVICTION_CONVERSION_DECISION_THRESHOLD
    )
    skip = _drive(
        _composed_factory()(),  # type: ignore[operator]
        state,
        skip_agents,
        meeting_id="headless-seed-0:meeting-1",
        triggered_by="p-1",
    )
    skip_ballots = {b.voter: b for b in skip.result.ballots}
    assert all(b.rationale_text == _COMPOSED_RATIONALE for b in skip.result.ballots)
    assert skip_ballots[teammate].target != target
    assert skip_ballots[target].target != target


# --------------------------------------------------------------------------- #
# 5. METERING — both counters, cumulative, fail loud, entry order              #
# --------------------------------------------------------------------------- #


def _committed_counters(
    *, conviction_max: int, surrogate_max: int
) -> tuple[ConvictionUseCounter, SurrogateUseCounter]:
    _, conviction_sha = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)
    _, surrogate_sha = load_ballot_predictor_artifact(_SURROGATE_ARTIFACT_DIR)
    conviction = ConvictionUseCounter(
        ConvictionStalenessCap(
            weights_sha256=conviction_sha, max_uses=conviction_max, unit="meetings"
        )
    )
    surrogate = SurrogateUseCounter(
        SurrogateStalenessCap(
            weights_sha256=surrogate_sha, max_uses=surrogate_max, unit="meetings"
        )
    )
    return conviction, surrogate


def test_one_meeting_meters_both_counters_cumulatively() -> None:
    """One run_meeting == +1 on BOTH counters; runners from one factory share them."""

    conviction, surrogate = _committed_counters(conviction_max=10, surrogate_max=10)
    factory = load_composed_runner_factory(
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
        conviction_use_counter=conviction,
        surrogate_use_counter=surrogate,
    )
    state = _seed_state(num_players=4, num_impostors=1)
    agents = _canned_agents(state)

    _drive(
        factory(),
        state,
        agents,
        meeting_id="headless-seed-0:meeting-0",
        triggered_by="p-1",
    )
    assert conviction.uses == 1
    assert surrogate.uses == 1
    # A second, freshly-constructed runner shares the SAME counters (cumulative).
    _drive(
        factory(),
        state,
        agents,
        meeting_id="headless-seed-0:meeting-1",
        triggered_by="p-1",
    )
    assert conviction.uses == 2
    assert surrogate.uses == 2


def test_spent_surrogate_cap_fails_loud_from_the_composed_path() -> None:
    """A spent surrogate cap raises at meeting entry (before any conviction read)."""

    conviction, surrogate = _committed_counters(conviction_max=10, surrogate_max=1)
    surrogate.record_use(weights_sha256=surrogate.cap.weights_sha256)  # spend it
    factory = load_composed_runner_factory(
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
        conviction_use_counter=conviction,
        surrogate_use_counter=surrogate,
    )
    state = _seed_state(num_players=4, num_impostors=1)
    agents = _canned_agents(state)
    with pytest.raises(SurrogateStalenessExceededError):
        _drive(
            factory(),
            state,
            agents,
            meeting_id="headless-seed-0:meeting-0",
            triggered_by="p-1",
        )
    # Metered at entry, before conviction: the conviction counter is untouched.
    assert conviction.uses == 0


def test_spent_conviction_cap_fails_loud_after_the_entry_metering() -> None:
    """A spent conviction cap raises on delivery; the surrogate is metered at entry.

    The documented order: the surrogate counter meters at meeting ENTRY, the
    conviction counter on DELIVERY (after the assemble/predict). So a spent
    conviction cap raises ConvictionStalenessExceededError, and the surrogate
    counter has already recorded the entry use — the honest order, asserted.
    """

    conviction, surrogate = _committed_counters(conviction_max=1, surrogate_max=10)
    conviction.record_use(weights_sha256=conviction.cap.weights_sha256)  # spend it
    factory = load_composed_runner_factory(
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
        conviction_use_counter=conviction,
        surrogate_use_counter=surrogate,
    )
    state = _seed_state(num_players=4, num_impostors=1)
    agents = _canned_agents(state)
    with pytest.raises(ConvictionStalenessExceededError):
        _drive(
            factory(),
            state,
            agents,
            meeting_id="headless-seed-0:meeting-0",
            triggered_by="p-1",
        )
    assert surrogate.uses == 1  # metered at entry, before the conviction raise


def test_loader_refuses_a_foreign_keyed_counter() -> None:
    """A use-counter keyed on a foreign sha is refused by the loader (both sides)."""

    _, surrogate_sha = load_ballot_predictor_artifact(_SURROGATE_ARTIFACT_DIR)
    _, conviction_sha = load_conviction_model_artifact(_CONVICTION_ARTIFACT_DIR)

    foreign_conviction = ConvictionUseCounter(
        ConvictionStalenessCap(weights_sha256="a" * 64, max_uses=5, unit="meetings")
    )
    with pytest.raises(ValueError, match="never meters two artifacts"):
        load_composed_components(
            conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
            surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
            conviction_use_counter=foreign_conviction,
        )

    foreign_surrogate = SurrogateUseCounter(
        SurrogateStalenessCap(weights_sha256="b" * 64, max_uses=5, unit="meetings")
    )
    with pytest.raises(ValueError, match="never meters two artifacts"):
        load_composed_components(
            conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
            surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
            surrogate_use_counter=foreign_surrogate,
        )


# --------------------------------------------------------------------------- #
# 6. FAIL-LOUD LOADING                                                         #
# --------------------------------------------------------------------------- #


def _copy_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    conviction_dir = tmp_path / "conviction"
    surrogate_dir = tmp_path / "surrogate"
    conviction_dir.mkdir()
    surrogate_dir.mkdir()
    for name in _CONVICTION_ARTIFACT_DIR.iterdir():
        (conviction_dir / name.name).write_bytes(name.read_bytes())
    for name in _SURROGATE_ARTIFACT_DIR.iterdir():
        (surrogate_dir / name.name).write_bytes(name.read_bytes())
    return conviction_dir, surrogate_dir


def test_corrupt_conviction_weights_fail_loud(tmp_path: Path) -> None:
    """One corrupted byte of conviction-model.json fails the sha before any use."""

    conviction_dir, surrogate_dir = _copy_artifacts(tmp_path)
    weights = conviction_dir / "conviction-model.json"
    text = weights.read_text()
    weights.write_text(text.replace('"epochs": ', '"epochs":  ', 1))  # whitespace byte
    with pytest.raises(ValueError, match="sha256 sidecar mismatch"):
        load_composed_components(
            conviction_artifact_dir=conviction_dir,
            surrogate_artifact_dir=surrogate_dir,
        )


def test_corrupt_surrogate_weights_fail_loud(tmp_path: Path) -> None:
    """One corrupted byte of ballot-predictor.json fails the sha before any use."""

    conviction_dir, surrogate_dir = _copy_artifacts(tmp_path)
    weights = surrogate_dir / "ballot-predictor.json"
    text = weights.read_text()
    weights.write_text(text.replace('"epochs": ', '"epochs":  ', 1))
    with pytest.raises(ValueError, match="sha256 sidecar mismatch"):
        load_composed_components(
            conviction_artifact_dir=conviction_dir,
            surrogate_artifact_dir=surrogate_dir,
        )


def test_no_go_conviction_verdict_makes_the_runner_unbuildable(
    tmp_path: Path,
) -> None:
    """A conviction verdict tampered to NO-GO is refused (structurally unbuildable)."""

    conviction_dir, surrogate_dir = _copy_artifacts(tmp_path)
    verdict = load_conviction_verdict(conviction_dir)
    tampered = verdict.model_copy(
        update={"verdict": "NO-GO", "model_role": "diagnostic-only"}
    )
    (conviction_dir / "verdict.json").write_text(tampered.model_dump_json(indent=2))
    with pytest.raises(ValueError, match="structurally unbuildable"):
        load_composed_components(
            conviction_artifact_dir=conviction_dir,
            surrogate_artifact_dir=surrogate_dir,
        )


# --------------------------------------------------------------------------- #
# 7. FULL COMPOSED-DRIVEN HEADLESSGAME — coherence, determinism, fold survival #
# --------------------------------------------------------------------------- #


def _run_composed_game(
    seed: int, out_dir: Path
) -> tuple[tuple[MeetingReplayEntry, ...], tuple[PlayerId, ...], Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    replay_path = out_dir / f"replay-seed-{seed}.jsonl"
    factory = load_composed_runner_factory(
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
    )
    absorbed: list[PlayerId] = []
    base_factory = build_default_agent_factory()

    def agent_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        inner = base_factory(agent_id, role)
        assert isinstance(inner, TacticalAgent)
        return _RecordingConvictionAgent(inner, absorbed)

    game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=agent_factory,
        replay_path=replay_path,
        meeting_runner=factory(),
    )
    game.run()
    entries = tuple(
        entry
        for entry in read_all_entries(replay_path)
        if isinstance(entry, MeetingReplayEntry)
    )
    return entries, tuple(absorbed), replay_path


@pytest.fixture(scope="module")
def composed_game(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[tuple[MeetingReplayEntry, ...], tuple[PlayerId, ...], Path]:
    return _run_composed_game(2, tmp_path_factory.mktemp("composed_game"))


def test_full_composed_game_meetings_are_real_tallies(
    composed_game: tuple[tuple[MeetingReplayEntry, ...], tuple[PlayerId, ...], Path],
) -> None:
    """Every recorded composed meeting IS the real tally of its own ballots."""

    entries, absorbed, _ = composed_game
    assert entries, "seed 2 must fire at least one meeting"
    for entry in entries:
        assert entry.llm_calls == ()
        assert entry.prompt_versions == {}
        outcome, ejected = tally_ballots(
            entry.ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        assert (outcome, ejected) == (entry.outcome, entry.ejected_player_id)
    # The belief fold consumed the meetings (absorb calls fanned out).
    assert len(absorbed) > 0


def test_full_composed_game_is_byte_deterministic(tmp_path: Path) -> None:
    """The same composed-driven game run twice writes byte-identical replays."""

    _, _, path_a = _run_composed_game(2, tmp_path / "a")
    _, _, path_b = _run_composed_game(2, tmp_path / "b")
    assert path_a.read_bytes() == path_b.read_bytes()


# --------------------------------------------------------------------------- #
# 8. decide_composed_go — the pre-registered bar                              #
# --------------------------------------------------------------------------- #


def _synthetic_report(
    *,
    decision_accuracy: float,
    convicting_top1: float,
    committed_shas: tuple[str, str],
    exact_outcome_match: float = 0.0,
) -> ComposedFidelityReport:
    conviction_sha, surrogate_sha = committed_shas
    return ComposedFidelityReport(
        replay_set_dir="replays/ml_corpus/9p2i",
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
        test_meetings=96,
        test_ejections=60,
        always_eject_baseline=60 / 96,
        decision_accuracy=decision_accuracy,
        convicting_top1=convicting_top1,
        top1_ceiling=0.85,
        exact_outcome_match=exact_outcome_match,
        predicted_convictions=0,
        gate_true_positives=0,
        gate_false_positives=0,
        gate_false_negatives=0,
        gate_true_negatives=0,
        surrogate_tally_ejections=0,
        surrogate_tally_skips=96,
        convicting_top1_gated=0.0,
    )


def test_decide_composed_go_applies_the_bar_strictly(
    committed_shas: tuple[str, str],
) -> None:
    """Strict > on the decision bar, inclusive >= on top-1, exact never gates."""

    conviction_sha, surrogate_sha = committed_shas
    # Exactly the always-eject baseline must be NO-GO (strict >).
    at_baseline = _synthetic_report(
        decision_accuracy=60 / 96,
        convicting_top1=0.9,
        committed_shas=committed_shas,
    )
    at_baseline_verdict = decide_composed_go(
        at_baseline,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    assert at_baseline_verdict.meets_decision_bar is False
    assert at_baseline_verdict.verdict == "NO-GO"
    assert at_baseline_verdict.composed_role == "diagnostic-only"

    # Exactly the top-1 bar (0.75 * 0.85 = 0.6375) must PASS (inclusive >=), and
    # a decision above baseline makes it GO.
    at_top1_bar = _synthetic_report(
        decision_accuracy=0.8,
        convicting_top1=0.6375,
        committed_shas=committed_shas,
        exact_outcome_match=0.0,  # exact match never lifts a verdict
    )
    go = decide_composed_go(
        at_top1_bar,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    assert go.top1_bar == pytest.approx(0.6375, abs=1e-12)
    assert go.meets_top1_bar is True
    assert go.meets_decision_bar is True
    assert go.verdict == "GO"
    assert go.composed_role == "optional-campaign-configuration"

    # Just under the top-1 bar is NO-GO even with a strong decision channel.
    under_top1 = _synthetic_report(
        decision_accuracy=0.9,
        convicting_top1=0.6374,
        committed_shas=committed_shas,
    )
    assert (
        decide_composed_go(
            under_top1,
            conviction_weights_sha256=conviction_sha,
            surrogate_weights_sha256=surrogate_sha,
        ).verdict
        == "NO-GO"
    )


def test_decide_composed_go_cross_checks_shas_and_round_trips(
    committed_shas: tuple[str, str],
) -> None:
    """A sha drift fails loud; the verdict JSON round-trips byte-stably."""

    conviction_sha, surrogate_sha = committed_shas
    report = _synthetic_report(
        decision_accuracy=0.8, convicting_top1=0.7, committed_shas=committed_shas
    )
    with pytest.raises(ValueError, match="must key to the artifact"):
        decide_composed_go(
            report,
            conviction_weights_sha256="a" * 64,
            surrogate_weights_sha256=surrogate_sha,
        )

    verdict = decide_composed_go(
        report,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    reloaded = ComposedGoVerdict.model_validate_json(verdict.model_dump_json())
    assert reloaded == verdict


# --------------------------------------------------------------------------- #
# 9. FIDELITY DISCIPLINE                                                       #
# --------------------------------------------------------------------------- #


def test_composed_fidelity_scores_the_committed_test_split(
    composed_fidelity: ComposedFidelityReport,
) -> None:
    """Exactly 96 test meetings / 60 ejections; the standing top-1 recipe holds."""

    report = composed_fidelity
    assert report.test_meetings == 96
    assert report.test_ejections == 60
    assert report.always_eject_baseline == pytest.approx(60 / 96, abs=1e-12)
    # The convicting top-1 is the SAME recipe the surrogate reports: 46/60.
    assert report.convicting_top1 == pytest.approx(46 / 60, abs=1e-12)
    assert report.top1_ceiling == pytest.approx(0.85, abs=1e-12)
    # The surrogate tally's all-SKIP degeneracy is the NO-GO fact composed around.
    assert report.surrogate_tally_ejections == 0
    assert report.surrogate_tally_skips == 96
    # Gate confusion partitions the 96 test meetings.
    total = (
        report.gate_true_positives
        + report.gate_false_positives
        + report.gate_false_negatives
        + report.gate_true_negatives
    )
    assert total == 96
    assert 0.0 <= report.decision_accuracy <= 1.0


def test_composed_fidelity_top1_matches_an_independent_recompute(
    composed_fidelity: ComposedFidelityReport,
) -> None:
    """The convicting top-1 equals a direct recompute off the frozen surrogate model.

    Recompute ranking hits directly from the committed BallotSurrogateModel over
    the held-out ejection meetings (the standing surrogate recipe), independent
    of the composed fidelity's own accounting.
    """

    from training.surrogate.dataset import build_meeting_table
    from training.surrogate.ballots import BallotSurrogateModel
    from training.surrogate.fidelity import build_meeting_views

    table = build_meeting_table(_CORPUS)
    assert table.splits is not None
    test_seeds = frozenset(table.splits.test)
    predictor, _ = load_ballot_predictor_artifact(_SURROGATE_ARTIFACT_DIR)
    model = BallotSurrogateModel(table, predictor=predictor)
    test_views = [v for v in build_meeting_views(table) if v.seed in test_seeds]
    hits = 0
    ejections = 0
    for view in test_views:
        if view.ejected is None:
            continue
        ejections += 1
        if model.predict(view).ranking[0] == view.ejected:
            hits += 1
    assert ejections == 60
    assert composed_fidelity.convicting_top1 == pytest.approx(hits / 60, abs=1e-12)


# --------------------------------------------------------------------------- #
# 10. THE COMPOSED-PATH GOODHART LEG (tiny budget)                            #
# --------------------------------------------------------------------------- #

# The committed tiny-budget idiom (test_goodhart_probe.py): 1 generation × 2
# offspring over 2 seeds on the short 4p1i roster.
_TINY = ESConfig(generations=1, population=2, sigma=0.4, seed=0, fitness_seeds=(0, 1))


@pytest.fixture(scope="module")
def goodhart_leg() -> ComposedGoodhartLeg:
    return run_composed_goodhart_leg(
        config=_TINY,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        surrogate_artifact_dir=_SURROGATE_ARTIFACT_DIR,
    )


def test_composed_goodhart_leg_runs_and_meters_both_counters(
    goodhart_leg: ComposedGoodhartLeg,
) -> None:
    """The leg drives 18.18's probe over the composed runner with metered consumption.

    The embedded report is a :class:`ConvictionPathProbeReport`; the composed path
    actually ran meetings (surrogate uses > 0); the probe's own conviction reads
    are exactly 2× the recorded meetings; the composed runner's own gate reads
    equal the composed meeting count; totals stay under the committed caps; and
    the blockers/verdict mirror the probe.
    """

    leg = goodhart_leg
    assert isinstance(leg.probe, ConvictionPathProbeReport)
    assert leg.roster_key == "4p1i"

    # The composed path actually ran meetings, metered on the surrogate counter.
    assert leg.surrogate_uses == leg.composed_meetings
    assert leg.composed_meetings > 0

    # The probe invariant: each recorded meeting predicted twice (fitness-term +
    # composed-gate pre-screen), on the SAME shared conviction counter.
    probe_recorded = sum(read.meetings for read in leg.probe.reads)
    assert leg.conviction_uses_probe == 2 * probe_recorded
    # The composed runner's own per-meeting gate reads == the composed meetings.
    assert leg.conviction_uses_runner == leg.composed_meetings
    # The two shares reconstruct the probe's total shared-counter spend.
    assert (
        leg.conviction_uses_runner + leg.conviction_uses_probe
        == leg.probe.conviction_uses
    )

    # Consumption stays inside the committed caps.
    assert leg.conviction_uses_total <= leg.conviction_max_uses
    assert leg.surrogate_uses_total <= leg.surrogate_max_uses
    assert leg.conviction_uses_total == leg.probe.conviction_uses

    # Blockers and verdict mirror the probe; the substrate note owns the framing.
    assert leg.blockers == leg.probe.blockers
    assert leg.verdict == leg.probe.verdict
    assert "COMPOSED meeting path" in leg.substrate_note
    assert "recorded-bytes pairing" in leg.substrate_note
    assert str(leg.conviction_uses_total) in leg.consumption_note
    assert str(leg.conviction_max_uses) in leg.consumption_note

    # The whole leg round-trips as JSON (the report idiom).
    reloaded = ComposedGoodhartLeg.model_validate_json(leg.to_json())
    assert reloaded == leg


# --------------------------------------------------------------------------- #
# 11. NO LEARNED PARAMETERS (the composition doctrine)                        #
# --------------------------------------------------------------------------- #


def test_module_holds_no_learned_parameters(
    committed_shas: tuple[str, str],
) -> None:
    """The module defines no ``fit`` and the manifest pins both committed shas."""

    source = (_REPO_ROOT / "training" / "composed_runner.py").read_text()
    assert re.search(r"def\s+fit", source) is None

    conviction_sha, surrogate_sha = committed_shas
    conviction_verdict = load_conviction_verdict(_CONVICTION_ARTIFACT_DIR)
    verdict = _synthetic_report(
        decision_accuracy=0.8, convicting_top1=0.7, committed_shas=committed_shas
    )
    go = decide_composed_go(
        verdict,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    manifest = build_composed_manifest(go, conviction_verdict=conviction_verdict)
    assert manifest.conviction_weights_sha256 == conviction_sha
    assert manifest.surrogate_weights_sha256 == surrogate_sha
    assert manifest.conviction_verdict == "GO"
    assert manifest.corpus_set == "9p2i"
    assert manifest.decision_threshold == CONVICTION_CONVERSION_DECISION_THRESHOLD
    assert manifest.skip_confidence_threshold == DEFAULT_SKIP_CONFIDENCE_THRESHOLD


def test_manifest_and_verdict_artifacts_round_trip(
    tmp_path: Path, committed_shas: tuple[str, str]
) -> None:
    """The verdict + manifest writers/loaders round-trip byte-stably; missing → loud."""

    conviction_sha, surrogate_sha = committed_shas
    report = _synthetic_report(
        decision_accuracy=0.8, convicting_top1=0.7, committed_shas=committed_shas
    )
    verdict = decide_composed_go(
        report,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    manifest = build_composed_manifest(
        verdict, conviction_verdict=load_conviction_verdict(_CONVICTION_ARTIFACT_DIR)
    )

    write_composed_verdict_artifact(verdict, tmp_path)
    write_composed_manifest_artifact(manifest, tmp_path)
    assert (tmp_path / COMPOSED_VERDICT_FILENAME).is_file()
    assert (tmp_path / COMPOSED_MANIFEST_FILENAME).is_file()
    assert load_composed_verdict(tmp_path) == verdict
    assert load_composed_manifest(tmp_path) == manifest

    with pytest.raises(FileNotFoundError, match="no committed composed verdict"):
        load_composed_verdict(tmp_path / "empty")
    with pytest.raises(FileNotFoundError, match="no committed composed manifest"):
        load_composed_manifest(tmp_path / "empty")


# --------------------------------------------------------------------------- #
# COMMITTED-ARTIFACT PINS — the committed manifest + verdict under              #
# training/artifacts/composed/ (the first held-out evaluation's bytes).         #
# --------------------------------------------------------------------------- #


def test_committed_composed_verdict_round_trips_and_pins_the_shas(
    committed_shas: tuple[str, str],
) -> None:
    """The committed composed verdict + manifest round-trip and key BOTH shas.

    Loads ``training/artifacts/composed/`` directly — the composed artifact is
    a manifest pinning both component shas plus the bar verdict, never weights.
    """

    conviction_sha, surrogate_sha = committed_shas
    verdict = load_composed_verdict(_COMPOSED_ARTIFACT_DIR)
    manifest = load_composed_manifest(_COMPOSED_ARTIFACT_DIR)
    assert verdict.conviction_weights_sha256 == conviction_sha
    assert verdict.surrogate_weights_sha256 == surrogate_sha
    assert manifest.conviction_weights_sha256 == conviction_sha
    assert manifest.surrogate_weights_sha256 == surrogate_sha
    assert manifest.composed_verdict == verdict.verdict


def test_committed_composed_verdict_is_rederivable(
    composed_fidelity: ComposedFidelityReport, committed_shas: tuple[str, str]
) -> None:
    """Re-deciding the held-out fidelity reproduces the committed verdict.

    The strongest pin — ``decide_composed_go(run_composed_fidelity(corpus), ...)``
    equals the committed ``verdict.json`` field-for-field. The committed artifact
    stores the REPO-RELATIVE corpus path (portable across checkouts); this run
    built the tables from an absolute path, so the identity field is normalized
    and every measured field compares raw (the
    ``test_committed_verdict_reproduces_from_the_frozen_weights`` idiom).
    """

    conviction_sha, surrogate_sha = committed_shas
    rederived = decide_composed_go(
        composed_fidelity,
        conviction_weights_sha256=conviction_sha,
        surrogate_weights_sha256=surrogate_sha,
    )
    committed = load_composed_verdict(_COMPOSED_ARTIFACT_DIR)
    assert committed.replay_set_dir == "replays/ml_corpus/9p2i"
    assert Path(rederived.replay_set_dir).resolve() == _CORPUS.resolve()
    assert committed.model_dump() == {
        **rederived.model_dump(),
        "replay_set_dir": committed.replay_set_dir,
    }

    # The first-evaluation numbers (baseline-6 corpus, committed split).
    assert committed.verdict == "GO"
    assert committed.composed_role == "optional-campaign-configuration"
    assert committed.test_meetings == 96
    assert committed.test_ejections == 60
    assert committed.decision_accuracy == pytest.approx(83 / 96)
    assert committed.decision_accuracy_bar == pytest.approx(0.625)
    assert committed.meets_decision_bar
    assert committed.convicting_top1 == pytest.approx(46 / 60)
    assert committed.top1_bar == pytest.approx(0.6375)
    assert committed.top1_ceiling == pytest.approx(0.85)
    assert committed.meets_top1_bar
    assert committed.exact_outcome_match == pytest.approx(76 / 96)
