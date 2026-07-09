"""Definition-of-done tests for the surrogate MeetingRunner (Task 15.13).

The ballot-predictor surrogate is the ``$0`` inner-loop meeting path: it predicts
one BALLOT per living voter from the live-parity features and feeds the REAL
:func:`meetings.voting.tally_ballots` (never a re-implemented or tuned decision
head). These tests pin that contract end to end against the COMMITTED weights
artifact and the committed 9p2i corpus:

* the runner IS an :class:`orchestrator.game.MeetingRunner` (runtime-checkable);
* a full surrogate-driven :class:`~orchestrator.game.HeadlessGame` completes, and
  every recorded meeting echoes its dispatch identity, carries one ballot per
  living voter, records NO llm calls, and its outcome is exactly the real tally of
  its own ballots;
* the cross-meeting belief fold consumes the surrogate result's ballot roster;
* the surrogate path is byte-deterministic (double-run replay hash);
* the committed artifact round-trips (provenance + determinism) and reproduces the
  pinned held-out fidelity numbers and the pre-stated NO-GO verdict;
* fallback (a) is exercised regardless of the verdict (the bake-off trains today);
* the §5.6 staleness cap is enforced, cumulatively across runner instances;
* the fit/predict leakage fence holds (predict never reads labels, fit never reads
  outside the fit side, and a fit fence-violation fails loud);
* no module under ``training/`` re-implements the tally; and
* the surrogate's OWN predicted-ballot calibration channel is distinct from the
  harness's recorded-ballot calibration.
"""

from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from agents.base import AgentInterface
from agents.memory.store import DEFAULT_TOKEN_BUDGET
from engine.entities import PlayerId, Role
from engine.world import WorldState, load_canonical_map
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger, SuspicionEntry
from meetings.schemas import VentWitnessRecord
from meetings.voting import tally_ballots
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    HeadlessGame,
    MeetingArtifacts,
    MeetingRunner,
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from training.env import TacticalRolloutEnv
from training.rewards import compute_shaped_reward
from training.surrogate.ballots import (
    BallotSurrogateModel,
    PredictedBallot,
    SurrogateStalenessCap,
    ballot_features_from_row,
    fit_corpus_ballot_predictor,
    load_ballot_predictor_artifact,
    load_staleness_cap,
)
from training.surrogate.dataset import (
    MeetingTable,
    MeetingTableRow,
    build_meeting_table,
)
from training.surrogate.fidelity import (
    MeetingView,
    SurrogateFidelityReport,
    build_meeting_views,
    decide_go_no_go,
    fo6_rebaseline,
    run_surrogate_fidelity,
)
from training.surrogate.runner import (
    SurrogateMeetingRunner,
    SurrogateStalenessExceededError,
    SurrogateUseCounter,
    _meeting_index_from_id,  # noqa: PLC2701 - the id-parse fence is under test
    load_surrogate_runner_factory,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "surrogate"


# --------------------------------------------------------------------------- #
# Module-scoped fixtures — the expensive artifacts, built once and shared.     #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def corpus_table() -> MeetingTable:
    """The committed 9p2i corpus table (~5s to build; shared)."""

    return build_meeting_table(_CORPUS)


@pytest.fixture(scope="module")
def surrogate_report(corpus_table: MeetingTable) -> SurrogateFidelityReport:
    """The held-out fidelity report for the ballot surrogate (single split fold)."""

    return run_surrogate_fidelity(
        corpus_table,
        lambda: BallotSurrogateModel(corpus_table),
        model_name="ballot-surrogate.v1",
    )


@pytest.fixture(scope="module")
def fo6_report(corpus_table: MeetingTable) -> SurrogateFidelityReport:
    """The FO-6 re-baseline over the SAME table/folds (the prior baseline)."""

    return fo6_rebaseline(corpus_table)


@pytest.fixture(scope="module")
def module_model(
    corpus_table: MeetingTable,
) -> tuple[BallotSurrogateModel, list[MeetingView]]:
    """A model fit on the corpus fit side + the held-out test views.

    Fit exactly on the non-test (train ∪ val) views — the fit-side seed set the
    committed split declares — so ``predicted_ballot_calibration`` reads the same
    held-out population the harness scores.
    """

    views = build_meeting_views(corpus_table)
    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    fit_views = [view for view in views if view.seed not in test_seeds]
    test_views = [view for view in views if view.seed in test_seeds]
    model = BallotSurrogateModel(corpus_table)
    model.fit(fit_views)
    return model, test_views


# --------------------------------------------------------------------------- #
# Recording doubles — observe the surrogate path without altering it.          #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _CapturedMeeting:
    """What the recording runner saw at ``run_meeting`` time for one meeting."""

    meeting_id: str
    triggered_by: PlayerId
    trigger_tick: int
    living: frozenset[PlayerId]


class _RecordingRunner:
    """Wraps a :class:`SurrogateMeetingRunner`, capturing each dispatch.

    Records ``(meeting_id, trigger.triggered_by, trigger.trigger_tick, living set
    from state)`` before delegating verbatim to the inner surrogate runner, so the
    test can assert the runner's returned result echoes exactly what it was handed.
    """

    def __init__(self, inner: SurrogateMeetingRunner) -> None:
        self._inner = inner
        self.captured: list[_CapturedMeeting] = []

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        living = frozenset(
            player_id for player_id, player in state.players.items() if player.alive
        )
        self.captured.append(
            _CapturedMeeting(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                living=living,
            )
        )
        return await self._inner.run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )


class _RecordingAgent:
    """A delegating :class:`MeetingAwareAgent` + :class:`BeliefPersistingAgent`.

    Forwards every load-bearing accessor to a real :class:`TacticalAgent` (so the
    live beliefs the surrogate reads are genuine) and records each
    :meth:`absorb_meeting_evidence` call before delegating it. Deliberately does
    NOT implement the optional ``absorb_reported_testimony`` /
    ``note_meeting_concluded`` capabilities — the orchestrator's isinstance gates
    skip them, isolating the belief-fold path under test.
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


class _CannedMeetingAgent:
    """A minimal :class:`MeetingAwareAgent` test double (no belief store).

    Returns empty meeting inputs (an unseeded roster reads the neutral 0.5 prior in
    the runner), so the surrogate predicts a well-formed ballot per voter without a
    real agent. ``decide`` is never invoked by the surrogate runner.
    """

    def __init__(
        self,
        agent_id: PlayerId,
        suspicion_graph: tuple[SuspicionEntry, ...] = (),
    ) -> None:
        self._agent_id = agent_id
        self._suspicion_graph = suspicion_graph

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return "CREWMATE"

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        raise AssertionError("the surrogate runner never calls decide()")

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
        return ()


@dataclass(frozen=True)
class _SurrogateGameRun:
    """The outcome of one surrogate-driven recorded game (for reuse across tests)."""

    outcome: str
    captured: tuple[_CapturedMeeting, ...]
    meeting_entries: tuple[MeetingReplayEntry, ...]
    absorbed: tuple[PlayerId, ...]
    replay_path: Path


def _run_surrogate_game(seed: int, out_dir: Path) -> _SurrogateGameRun:
    """Drive a full default-roster HeadlessGame with the committed surrogate.

    Wraps the committed-artifact runner in a recording runner and every default
    agent in a recording delegating wrapper, so both the meeting dispatch and the
    post-meeting belief fold are observable. Fresh factory (fresh use-counter) per
    call, so repeated calls are independent.
    """

    out_dir.mkdir(parents=True, exist_ok=True)
    replay_path = out_dir / f"replay-seed-{seed}.jsonl"
    factory = load_surrogate_runner_factory(_ARTIFACT_DIR)
    recording_runner = _RecordingRunner(factory())
    absorbed: list[PlayerId] = []
    base_factory = build_default_agent_factory()

    def agent_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        inner = base_factory(agent_id, role)
        assert isinstance(inner, TacticalAgent)
        return _RecordingAgent(inner, absorbed)

    game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=agent_factory,
        replay_path=replay_path,
        meeting_runner=recording_runner,
    )
    result = game.run()
    meeting_entries = tuple(
        entry
        for entry in read_all_entries(replay_path)
        if isinstance(entry, MeetingReplayEntry)
    )
    return _SurrogateGameRun(
        outcome=result.outcome,
        captured=tuple(recording_runner.captured),
        meeting_entries=meeting_entries,
        absorbed=tuple(absorbed),
        replay_path=replay_path,
    )


@pytest.fixture(scope="module")
def surrogate_game(tmp_path_factory: pytest.TempPathFactory) -> _SurrogateGameRun:
    """One surrogate-driven game at seed 2 (fires a meeting on the default roster)."""

    out_dir = tmp_path_factory.mktemp("surrogate_game")
    return _run_surrogate_game(2, out_dir)


# --------------------------------------------------------------------------- #
# 1. PROTOCOL                                                                  #
# --------------------------------------------------------------------------- #


def test_runner_satisfies_meeting_runner_protocol() -> None:
    """A :class:`SurrogateMeetingRunner` IS a runtime-checkable MeetingRunner."""

    runner = load_surrogate_runner_factory(_ARTIFACT_DIR)()
    assert isinstance(runner, SurrogateMeetingRunner)
    assert isinstance(runner, MeetingRunner)


# --------------------------------------------------------------------------- #
# 2. FULL SURROGATE-DRIVEN HEADLESSGAME (the flagship)                         #
# --------------------------------------------------------------------------- #


def test_full_surrogate_driven_game_meetings_are_real_tallies(
    surrogate_game: _SurrogateGameRun,
) -> None:
    """Every recorded meeting echoes its dispatch and IS the real tally of its ballots.

    The runner is dispatched from inside the real tick loop; for every meeting the
    recorded replay entry must echo the meeting_id / reporter / trigger tick the
    runner was handed, carry exactly one ballot per living voter, record NO llm
    calls, and have an outcome/ejected that equals the test's own recompute of
    :func:`tally_ballots` on those ballots — proving the decision IS the real tally.
    """

    assert surrogate_game.outcome in ("CREWMATES", "IMPOSTORS")
    assert surrogate_game.meeting_entries, "seed 2 must fire at least one meeting"
    # Meetings are dispatched and recorded in the same order.
    assert len(surrogate_game.captured) == len(surrogate_game.meeting_entries)

    for captured, entry in zip(
        surrogate_game.captured, surrogate_game.meeting_entries, strict=True
    ):
        # The result echoes the dispatched identity (game.run would raise on a
        # mismatch, but assert it explicitly from the captured dispatch).
        assert entry.meeting_id == captured.meeting_id
        assert entry.triggered_by == captured.triggered_by
        assert entry.tick == captured.trigger_tick
        # One ballot per living voter — exactly the belief-fold roster.
        assert {ballot.voter for ballot in entry.ballots} == captured.living
        # No LLM layer: the whole point of the $0 inner loop.
        assert entry.llm_calls == ()
        assert entry.prompt_versions == {}
        # The recorded decision IS the real tally of the recorded ballots.
        outcome, ejected = tally_ballots(
            entry.ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD
        )
        assert (outcome, ejected) == (entry.outcome, entry.ejected_player_id)


# --------------------------------------------------------------------------- #
# 3. CROSS-MEETING BELIEF FOLD CONSUMES THE RESULT                            #
# --------------------------------------------------------------------------- #


def test_belief_fold_consumes_surrogate_ballot_roster(
    surrogate_game: _SurrogateGameRun,
) -> None:
    """Each meeting's post-fold ``absorb_meeting_evidence`` fans out over the survivors.

    The orchestrator folds every resolved meeting's evidence into the living
    agents' beliefs off ``result.ballots``' roster. Every survivor of a meeting
    (the ballot roster minus any ejected player) receives exactly one absorb call,
    so the total is the sum of per-meeting survivor counts — proving the fold ran
    off the surrogate result, not a stubbed roster.
    """

    expected = sum(
        len(entry.ballots) - (1 if entry.ejected_player_id is not None else 0)
        for entry in surrogate_game.meeting_entries
    )
    assert expected > 0
    assert len(surrogate_game.absorbed) == expected
    assert len(surrogate_game.absorbed) >= len(surrogate_game.meeting_entries)


# --------------------------------------------------------------------------- #
# 4. DETERMINISM DOUBLE-RUN HASH                                              #
# --------------------------------------------------------------------------- #


def test_surrogate_game_is_byte_deterministic(tmp_path: Path) -> None:
    """The SAME surrogate-driven game run twice writes byte-identical replays."""

    run_a = _run_surrogate_game(2, tmp_path / "a")
    run_b = _run_surrogate_game(2, tmp_path / "b")
    assert run_a.replay_path.read_bytes() == run_b.replay_path.read_bytes()


# --------------------------------------------------------------------------- #
# 5. ARTIFACT ROUND-TRIP + pinned fidelity + pre-stated verdict               #
# --------------------------------------------------------------------------- #


def test_committed_artifact_round_trips_and_provenance_holds(
    corpus_table: MeetingTable,
) -> None:
    """The committed artifact loads (sha verified), and a refit is ULP-equivalent.

    Serialization is byte-stable: loading the committed bytes and re-serializing
    is the identity, so the sha256 sidecar pins exactly what the bake-off
    reloads. Refit provenance is parameter-level: ``fit_corpus_ballot_predictor``
    reproduces every committed parameter to float ULP — numpy's SIMD summation
    grouping varies by CPU, so a refit is byte-identical only on the recording
    platform (CI runs on a different one). The committed bytes, never a refit,
    are the frozen ground truth; the frozen-weights evaluation test below pins
    that they reproduce the reported numbers.
    """

    predictor, sha = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    committed_json = (_ARTIFACT_DIR / "ballot-predictor.json").read_text()
    # Load -> re-serialize is the identity (byte-stable round trip).
    assert predictor.to_artifact_json() == committed_json

    cap = load_staleness_cap(_ARTIFACT_DIR)
    assert cap.weights_sha256 == sha
    assert cap.max_uses == 50_000
    assert cap.unit == "meetings"

    refit = json.loads(fit_corpus_ballot_predictor(corpus_table).to_artifact_json())
    committed = json.loads(committed_json)
    assert refit.keys() == committed.keys()
    for key, committed_value in committed.items():
        refit_value = refit[key]
        if (
            isinstance(committed_value, list)
            and committed_value
            and isinstance(committed_value[0], str)
            and "0x" in committed_value[0]
        ):
            committed_floats = [float.fromhex(item) for item in committed_value]
            refit_floats = [float.fromhex(item) for item in refit_value]
            assert refit_floats == pytest.approx(
                committed_floats, rel=1e-9, abs=1e-12
            ), key
        elif isinstance(committed_value, str) and "0x" in committed_value:
            assert float.fromhex(refit_value) == pytest.approx(
                float.fromhex(committed_value), rel=1e-9, abs=1e-12
            ), key
        else:
            # Non-float metadata (format marker, feature names, epochs) is exact.
            assert refit_value == committed_value, key


def test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers(
    corpus_table: MeetingTable,
) -> None:
    """The LOADED committed weights reproduce the reported held-out numbers.

    The DoD round-trip in its own words: the bake-off reloads exactly the
    committed artifact, and evaluating the FROZEN predictor (no refit — the
    ``predictor`` injection on :class:`BallotSurrogateModel`) over the held-out
    test views reproduces the report's ranking/decision census and the
    predicted-ballot calibration channel.
    """

    predictor, _ = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    frozen = BallotSurrogateModel(corpus_table, predictor=predictor)
    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    test_views = [
        view for view in build_meeting_views(corpus_table) if view.seed in test_seeds
    ]
    assert len(test_views) == 91

    top1_hits = 0
    predicted_ejections = 0
    predicted_skips = 0
    correct_skips = 0
    for view in test_views:
        prediction = frozen.predict(view)
        if prediction.ejected is None:
            predicted_skips += 1
            if view.ejected is None:
                correct_skips += 1
        else:
            predicted_ejections += 1
        if view.is_ejection and prediction.ranking[0] == view.ejected:
            top1_hits += 1
    assert top1_hits == 47
    assert predicted_ejections == 88
    assert predicted_skips == 3
    assert correct_skips == 0

    calibration = frozen.predicted_ballot_calibration(test_views)
    assert calibration.predicted_ballots == 529
    assert calibration.predicted_skips == 0
    # Inference from FIXED committed weights; tolerance covers libm exp variance
    # across platforms, nothing more.
    assert calibration.brier == pytest.approx(0.3574025827101143, abs=1e-9)


def test_surrogate_fidelity_reproduces_pinned_numbers(
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """The held-out surrogate report reproduces the pinned deterministic numbers."""

    report = surrogate_report
    # Integer census — exact.
    assert report.meetings_scored == 91
    assert report.ejection_meetings == 73
    assert report.skip_meetings == 18
    assert report.top1_hits == 47
    assert report.top2_hits == 60
    assert report.predicted_ejections == 88
    assert report.predicted_skips == 3
    assert report.correct_skip_decisions == 0
    assert report.correct_eject_decisions == 70
    assert report.ejection_predicted_skips == 3
    assert report.degenerates_to_skip is False
    assert report.ballot_rows == 501
    assert report.honest_ceiling.ejections_total == 73
    assert report.honest_ceiling.reachable == 50
    # Floats — deterministic, pinned to the exact literals.
    assert report.top1 == pytest.approx(0.6438356164383562, abs=1e-12)
    assert report.top2 == pytest.approx(0.821917808219178, abs=1e-12)
    assert report.skip_vs_eject_accuracy == pytest.approx(0.7692307692307693, abs=1e-12)
    assert report.always_eject_baseline == pytest.approx(0.8021978021978022, abs=1e-12)
    assert report.brier == pytest.approx(0.09837767767162488, abs=1e-12)
    assert report.ece == pytest.approx(0.07975082915365356, abs=1e-12)
    assert report.ballot_brier == pytest.approx(0.20695409181636726, abs=1e-12)
    assert report.ballot_ece == pytest.approx(0.10099800399201568, abs=1e-12)
    assert report.honest_ceiling.max_achievable_top1 == pytest.approx(
        0.684931506849315, abs=1e-12
    )


def test_go_no_go_reproduces_the_pre_stated_no_go_verdict(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """``decide_go_no_go`` on the two same-population reports pins NO-GO + fallback (a)."""

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.verdict == "NO-GO"
    assert verdict.meets_ceiling_bar is True
    assert verdict.beats_prior_baseline is True
    assert verdict.beats_always_eject is False
    assert verdict.training_time_runner == "fake-provider-meeting-manager"
    assert verdict.surrogate_role == "diagnostic-only"
    assert verdict.top1_bar == pytest.approx(0.5136986301369862, abs=1e-12)


def test_fo6_rebaseline_reproduces_pinned_numbers(
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The FO-6 prior baseline reproduces its always-SKIP collapse on the corpus."""

    report = fo6_report
    assert report.top1_hits == 13
    assert report.ejection_meetings == 73
    assert report.degenerates_to_skip is True
    assert report.predicted_ejections == 27
    assert report.predicted_skips == 64
    assert report.correct_skip_decisions == 11
    assert report.ejection_predicted_skips == 53
    assert report.top1 == pytest.approx(0.1780821917808219, abs=1e-12)
    assert report.top2 == pytest.approx(0.410958904109589, abs=1e-12)
    assert report.skip_vs_eject_accuracy == pytest.approx(
        0.34065934065934067, abs=1e-12
    )


# --------------------------------------------------------------------------- #
# 6. FALLBACK (a) EXERCISED REGARDLESS OF VERDICT                             #
# --------------------------------------------------------------------------- #


def test_fallback_a_trains_today_regardless_of_verdict() -> None:
    """The fake-provider MeetingManager path (fallback a) is scoreable at seed 2.

    A NO-GO can never block the bake-off: the DEFAULT env (no surrogate factory)
    rolls out a meeting-firing seed to completion and both sides' shaped rewards
    compute without raising. The diagnostic surrogate path stays available too.
    """

    env = TacticalRolloutEnv()
    episode = env.rollout(2)
    assert episode.complete is True
    assert episode.meetings
    assert all(meeting.outcome is not None for meeting in episode.meetings)
    # Both sides score without raising (the bake-off trains under fallback (a)).
    compute_shaped_reward(episode, "IMPOSTOR")
    compute_shaped_reward(episode, "CREWMATE")

    # The diagnostic surrogate path also completes when opted into.
    surrogate_env = TacticalRolloutEnv(
        meeting_runner_factory=load_surrogate_runner_factory(_ARTIFACT_DIR),
        no_replay=True,
    )
    surrogate_episode = surrogate_env.rollout(2)
    assert surrogate_episode.complete is True


# --------------------------------------------------------------------------- #
# 7. STALENESS CAP                                                            #
# --------------------------------------------------------------------------- #


def test_use_counter_raises_at_cap_and_rejects_foreign_sha() -> None:
    """The use-counter meters two uses then raises; a foreign sha is rejected."""

    cap = SurrogateStalenessCap(weights_sha256="a" * 64, max_uses=2, unit="meetings")
    counter = SurrogateUseCounter(cap)
    assert counter.record_use(weights_sha256="a" * 64) == 1
    assert counter.record_use(weights_sha256="a" * 64) == 2
    with pytest.raises(SurrogateStalenessExceededError):
        counter.record_use(weights_sha256="a" * 64)

    # A counter keyed on one artifact never meters a different one.
    fresh = SurrogateUseCounter(
        SurrogateStalenessCap(weights_sha256="a" * 64, max_uses=5, unit="meetings")
    )
    with pytest.raises(ValueError, match="keyed on weights sha256"):
        fresh.record_use(weights_sha256="b" * 64)


def test_factory_rejects_a_loosened_or_foreign_shared_counter() -> None:
    """A shared counter may tighten the committed cap, never loosen or re-key it.

    Codex review (PR #241): ``record_use`` only checks the sha, so the factory
    must refuse a supplied counter whose cap exceeds the committed
    ``max-uses.json`` (the staleness doctrine would otherwise be silently
    bypassable) or that is keyed on different weights.
    """

    _, committed_sha = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    committed_cap = load_staleness_cap(_ARTIFACT_DIR)

    loosened = SurrogateUseCounter(
        SurrogateStalenessCap(
            weights_sha256=committed_sha,
            max_uses=committed_cap.max_uses + 1,
            unit="meetings",
        )
    )
    with pytest.raises(ValueError, match="never.*loosen"):
        load_surrogate_runner_factory(_ARTIFACT_DIR, use_counter=loosened)

    foreign = SurrogateUseCounter(
        SurrogateStalenessCap(weights_sha256="a" * 64, max_uses=1, unit="meetings")
    )
    with pytest.raises(ValueError, match="never meters two artifacts"):
        load_surrogate_runner_factory(_ARTIFACT_DIR, use_counter=foreign)

    # A TIGHTER shared counter is accepted (the cumulative-metering test relies
    # on exactly this), and an equal one trivially so.
    equal = SurrogateUseCounter(committed_cap)
    assert callable(load_surrogate_runner_factory(_ARTIFACT_DIR, use_counter=equal))


def _canned_agents(state: WorldState) -> dict[PlayerId, AgentInterface]:
    return {player_id: _CannedMeetingAgent(player_id) for player_id in state.players}


def test_cap_is_cumulative_across_fresh_runner_instances() -> None:
    """A shared counter meters across separately-constructed runners (never resets).

    A fresh runner per game is a wiring choice; the committed §5.6 cap must span
    the whole run. With ``max_uses=2`` on the real committed sha, one meeting on
    each of two fresh runners succeeds, and a third fresh runner raises.
    """

    _, committed_sha = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    counter = SurrogateUseCounter(
        SurrogateStalenessCap(weights_sha256=committed_sha, max_uses=2, unit="meetings")
    )
    factory = load_surrogate_runner_factory(_ARTIFACT_DIR, use_counter=counter)

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=2,
    )
    agents = _canned_agents(state)
    trigger = MeetingTrigger(
        triggered_by="p-1", trigger_tick=state.tick, description="p-1 reported a body"
    )
    living = frozenset(
        player_id for player_id, player in state.players.items() if player.alive
    )

    async def _drive(runner: SurrogateMeetingRunner) -> MeetingArtifacts:
        return await runner.run_meeting(
            meeting_id="headless-seed-0:meeting-0",
            trigger=trigger,
            state=state,
            agents=agents,
        )

    artifacts = asyncio.run(_drive(factory()))
    # One ballot per living voter; echoes the trigger; no LLM metadata.
    assert {ballot.voter for ballot in artifacts.result.ballots} == living
    assert artifacts.result.meeting_id == "headless-seed-0:meeting-0"
    assert artifacts.result.triggered_by == "p-1"
    assert artifacts.result.trigger_tick == state.tick
    assert artifacts.llm_calls == ()
    assert artifacts.prompt_versions == {}

    asyncio.run(_drive(factory()))  # second use — still under the cap of 2
    with pytest.raises(SurrogateStalenessExceededError):
        asyncio.run(_drive(factory()))  # third fresh runner — cap is cumulative


def test_missing_artifact_and_malformed_meeting_id_fail_loud(tmp_path: Path) -> None:
    """An artifact-less dir raises FileNotFoundError; a bad meeting_id raises ValueError."""

    with pytest.raises(FileNotFoundError):
        load_surrogate_runner_factory(tmp_path)

    runner = load_surrogate_runner_factory(_ARTIFACT_DIR)()
    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=2,
    )
    agents = _canned_agents(state)
    trigger = MeetingTrigger(
        triggered_by="p-1", trigger_tick=state.tick, description="report"
    )
    with pytest.raises(ValueError, match="does not carry the orchestrator"):
        asyncio.run(
            runner.run_meeting(
                meeting_id="no-index", trigger=trigger, state=state, agents=agents
            )
        )
    # The bare id parser fails loud on its own too.
    with pytest.raises(ValueError, match="does not carry the orchestrator"):
        _meeting_index_from_id("no-index")


def test_impostor_ballot_never_names_a_fellow_impostor() -> None:
    """The §7.12 teammate-ballot firewall holds on the surrogate path (Codex P1).

    The real vote path coerces a ballot naming a fellow impostor to SKIP before
    the tally (``meetings.manager.coerce_teammate_ballot_to_skip``), so an
    impostor can never supply the betrayal vote that ejects a teammate. The
    Codex repro shape: a 9p/2i state where an impostor's own suspicion graph
    puts its TEAMMATE far above every other candidate — the surrogate must
    still never record a teammate-targeted ballot (the teammate is excluded
    from the choice set), and an impostor whose only other living players are
    teammates lands on SKIP (the guard chain's terminal shape).
    """

    runner = load_surrogate_runner_factory(_ARTIFACT_DIR)()
    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    impostors = sorted(
        player_id
        for player_id, player in state.players.items()
        if player.role == "IMPOSTOR"
    )
    assert len(impostors) == 2
    voter, teammate = impostors
    graph = tuple(
        SuspicionEntry(
            player_id=player_id,
            suspicion=1.0 if player_id == teammate else 0.1,
            trust=0.5,
        )
        for player_id in sorted(state.players)
        if player_id != voter
    )
    agents: dict[PlayerId, AgentInterface] = {
        player_id: _CannedMeetingAgent(player_id, graph if player_id == voter else ())
        for player_id in state.players
    }
    trigger = MeetingTrigger(
        triggered_by=voter, trigger_tick=state.tick, description="reported a body"
    )
    artifacts = asyncio.run(
        runner.run_meeting(
            meeting_id="headless-seed-0:meeting-0",
            trigger=trigger,
            state=state,
            agents=agents,
        )
    )
    by_voter = {ballot.voter: ballot for ballot in artifacts.result.ballots}
    assert set(by_voter) == set(state.players)
    # Neither impostor's ballot ever names its teammate — even with the teammate
    # as the graph's runaway argmax.
    assert by_voter[voter].target != teammate
    assert by_voter[teammate].target != voter
    assert by_voter[voter].target == "SKIP" or by_voter[voter].target in (
        set(state.players) - {voter, teammate}
    )

    # Terminal shape: an impostor duo with no living crew has an empty choice
    # set per voter, so both ballots are SKIP and the real tally skips.
    dead_crew = {
        player_id: replace(player, alive=False)
        for player_id, player in state.players.items()
        if player_id not in impostors
    }
    duo_state = replace(state, players={**state.players, **dead_crew})
    duo_agents: dict[PlayerId, AgentInterface] = {
        player_id: _CannedMeetingAgent(player_id) for player_id in impostors
    }
    duo = asyncio.run(
        runner.run_meeting(
            meeting_id="headless-seed-0:meeting-1",
            trigger=MeetingTrigger(
                triggered_by=voter,
                trigger_tick=duo_state.tick,
                description="emergency",
            ),
            state=duo_state,
            agents=duo_agents,
        )
    )
    assert {ballot.voter for ballot in duo.result.ballots} == set(impostors)
    assert all(ballot.target == "SKIP" for ballot in duo.result.ballots)
    assert duo.result.outcome == "SKIPPED"


# --------------------------------------------------------------------------- #
# 8. LEAKAGE FENCE                                                            #
# --------------------------------------------------------------------------- #


def _poison_labels(row: MeetingTableRow) -> MeetingTableRow:
    """Replace a row's LABEL columns with garbage; keep FEATURE columns intact.

    The label set covers the ballot join targets, the meeting outcome, AND the
    roles ground truth (``voter_role`` / ``voter_is_impostor`` / per-candidate
    ``role`` / ``is_impostor`` / ``is_ejected``) — a predict path that read ANY
    of them would diverge from the clean model.
    """

    return row.model_copy(
        update={
            "ballot_target": "poisoned-label",
            "ballot_confidence": 0.0,
            "ballot_primary_reason_id": None,
            "ejected_player_id": "poisoned-label",
            "outcome": "EJECTED",
            "voter_role": "IMPOSTOR",
            "voter_is_impostor": True,
            "candidates": tuple(
                cand.model_copy(
                    update={
                        "role": "IMPOSTOR",
                        "is_ejected": True,
                        "is_impostor": True,
                    }
                )
                for cand in row.candidates
            ),
        }
    )


def _poison_everything(row: MeetingTableRow) -> MeetingTableRow:
    """Replace a row's LABEL and FEATURE columns with garbage."""

    return row.model_copy(
        update={
            "ballot_target": "poisoned-label",
            "ballot_confidence": 0.0,
            "ballot_primary_reason_id": None,
            "ejected_player_id": "poisoned-label",
            "outcome": "EJECTED",
            "voter_role": "IMPOSTOR",
            "voter_is_impostor": True,
            "meeting_index": 9999,
            "candidates": tuple(
                cand.model_copy(
                    update={
                        "role": "IMPOSTOR",
                        "is_ejected": True,
                        "is_impostor": True,
                        "belief_suspicion": 999.0,
                        "belief_trust": 999.0,
                        "is_reporter": True,
                        "witnessed_vent": True,
                    }
                )
                for cand in row.candidates
            ),
        }
    )


def _poisoned_table(
    table: MeetingTable,
    poison: Callable[[MeetingTableRow], MeetingTableRow],
    test_seeds: frozenset[int],
) -> MeetingTable:
    return table.model_copy(
        update={
            "rows": tuple(
                poison(row) if row.seed in test_seeds else row for row in table.rows
            )
        }
    )


def test_predict_never_touches_test_labels(corpus_table: MeetingTable) -> None:
    """Poisoning every TEST-seed row's LABELS leaves every prediction unchanged.

    The predict-side leakage fence: with identical clean fit-side views, a model
    over a label-poisoned table and one over the clean table must produce
    byte-identical rankings / ejections / ejection probabilities on the held-out
    test views — proving ``predict`` reads FEATURE columns only.
    """

    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    views = build_meeting_views(corpus_table)
    fit_views = [view for view in views if view.seed not in test_seeds]
    test_views = [view for view in views if view.seed in test_seeds]

    poisoned = _poisoned_table(corpus_table, _poison_labels, test_seeds)
    clean_model = BallotSurrogateModel(corpus_table)
    poisoned_model = BallotSurrogateModel(poisoned)
    # Fit both on the SAME clean fit-side views (the poisoned table's fit-side rows
    # are identical to clean by construction).
    clean_model.fit(fit_views)
    poisoned_model.fit(fit_views)

    for view in test_views:
        clean_pred = clean_model.predict(view)
        poisoned_pred = poisoned_model.predict(view)
        assert clean_pred.ranking == poisoned_pred.ranking
        assert clean_pred.ejected == poisoned_pred.ejected
        assert clean_pred.ejection_prob == poisoned_pred.ejection_prob


def test_fit_never_reads_outside_the_fit_side(corpus_table: MeetingTable) -> None:
    """Poisoning EVERYTHING of every TEST-seed row leaves the fit byte-identical.

    The fit-side leakage fence: the fitted weights are a pure function of the
    fit-side rows, so garbage in the held-out rows (features AND labels) cannot
    change the serialized predictor.
    """

    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    views = build_meeting_views(corpus_table)
    fit_views = [view for view in views if view.seed not in test_seeds]

    poisoned = _poisoned_table(corpus_table, _poison_everything, test_seeds)
    clean_model = BallotSurrogateModel(corpus_table)
    poisoned_model = BallotSurrogateModel(poisoned)
    clean_model.fit(fit_views)
    poisoned_model.fit(fit_views)
    assert (
        clean_model.predictor.to_artifact_json()
        == poisoned_model.predictor.to_artifact_json()
    )


def test_fit_fence_raises_on_a_held_out_view(corpus_table: MeetingTable) -> None:
    """``fit`` refuses a view from outside the declared fit-side seed set."""

    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    views = build_meeting_views(corpus_table)
    fit_views = [view for view in views if view.seed not in test_seeds]
    test_view = next(view for view in views if view.seed in test_seeds)

    model = BallotSurrogateModel(corpus_table)
    with pytest.raises(
        ValueError, match="outside the declared fit-side seed set"
    ) as exc:
        model.fit([fit_views[0], test_view])
    assert str(test_view.seed) in str(exc.value)


# --------------------------------------------------------------------------- #
# 9. NO REIMPLEMENTED TALLY                                                   #
# --------------------------------------------------------------------------- #


def test_no_module_under_training_reimplements_the_tally() -> None:
    """No ``training/`` module defines its own ``tally*`` — the real tally is reused."""

    tally_def = re.compile(r"def\s+tally")
    offenders = [
        str(path)
        for path in (_REPO_ROOT / "training").rglob("*.py")
        if "__pycache__" not in path.parts and tally_def.search(path.read_text())
    ]
    assert offenders == []


# --------------------------------------------------------------------------- #
# 10. PREDICTED-BALLOT CALIBRATION CHANNEL                                    #
# --------------------------------------------------------------------------- #


def test_predicted_ballot_calibration_is_a_distinct_channel(
    module_model: tuple[BallotSurrogateModel, list[MeetingView]],
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """The surrogate's predicted-ballot calibration is pinned AND distinct from ballot_brier.

    ``predicted_ballot_calibration`` scores the surrogate's OWN predicted ballot
    confidences (a model-dependent channel), pinned to its deterministic values; it
    is a different measurement from the harness's recorded-ballot ``ballot_brier``
    (a property of the committed voters), so the two must not coincide.
    """

    model, test_views = module_model
    calib = model.predicted_ballot_calibration(test_views)
    assert calib.predicted_ballots == 529
    assert calib.predicted_skips == 0
    assert calib.brier == pytest.approx(0.3574025827101143, abs=1e-12)
    # Distinct channel by construction.
    assert calib.brier != surrogate_report.ballot_brier


def test_predict_reads_only_feature_columns_directly(
    module_model: tuple[BallotSurrogateModel, list[MeetingView]],
    corpus_table: MeetingTable,
) -> None:
    """A direct predict off a row's FEATURE view yields a well-formed ballot.

    Sanity that the predict entry point consumes only the fenced feature view
    (:func:`ballot_features_from_row`) and returns a schema-valid
    :class:`PredictedBallot` (target in the voter's candidate set or SKIP).
    """

    model, _ = module_model
    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    row = next(row for row in corpus_table.rows if row.seed in test_seeds)
    view = ballot_features_from_row(row)
    predicted = model.predictor.predict_ballot(view)
    assert isinstance(predicted, PredictedBallot)
    assert predicted.target == "SKIP" or predicted.target in view.candidates
    assert 0.0 <= predicted.confidence <= 1.0
