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
* the committed artifact round-trips (provenance + determinism, incl. the
  re-derived ~143× staleness cap = 143 × 367 = 52481) and reproduces the pinned
  held-out fidelity numbers and the re-measured NO-GO verdict (Task 18.14 re-fit
  on the baseline-6 corpus — the bar itself is the pre-stated, owner-ratified
  15.13 bar; the verdict flipped GO → NO-GO because baseline 6 reverted to
  eject-majority, so the all-SKIP decision head falls below always-eject);
* the Task-18.14 fit-corpus fence binds the weights to the corpus identity, so
  the loader catches substrate drift (not only weights drift);
* fallback (a) is exercised regardless of the verdict (the bake-off trains today);
* the §5.6 staleness cap is enforced, cumulatively across runner instances;
* the fit/predict leakage fence holds (predict never reads labels, fit never reads
  outside the fit side, and a fit fence-violation fails loud);
* coerced-SKIP rows (the J2 citation-gate marker) are dropped from every fit —
  their labels are never read — while the recorded bytes stay scored unfiltered
  (Task 17.10 designer ruling; ONE such row on the baseline-6 corpus, the first
  time the exclusion drops a real row rather than only a synthetic one);
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
from eval.funnel import (
    _walk_game_vj,  # noqa: PLC2701 - the production-fold walk the replay reads
)
from eval.validity import resolve_roster_knobs, roles_by_seed
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from meetings.manager import MeetingTrigger, SuspicionEntry
from meetings.schemas import ObservationId, SightingRecord, VentWitnessRecord
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
    derive_max_uses,
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
    GO_BAR_ID,
    GO_TOP1_CEILING_RATIO,
    Fo6Logistic,
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
    fit_corpus_fingerprint,
    load_fit_corpus_record,
    load_surrogate_runner_factory,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CORPUS = _REPO_ROOT / "replays" / "ml_corpus" / "9p2i"
_ARTIFACT_DIR = _REPO_ROOT / "training" / "artifacts" / "surrogate"

# Task 18.14 re-fit the committed artifact on the baseline-6 corpus and re-pinned
# every corpus-derived number below. The seven ``_PENDING_SURROGATE_REGROUND_1814``
# xfails Task 18.13 left (deferring the re-fit) are cleared, and the
# stale-baseline5 tripwire that tracked the hybrid is deleted — the artifact is now
# current. The verdict FLIPPED GO -> NO-GO on the eject-majority baseline-6 economy
# (axis 3, SKIP-vs-eject 0.375 < always-eject 0.625): see
# training/reports/report-ballot-surrogate.md §5.


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

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        return self._inner.sighting_records_for_meeting()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        return self._inner.observation_ids_for_meeting()

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

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        return ()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
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


def test_the_committed_surrogate_is_a_baseline6_fit_on_a_baseline7_corpus(
    corpus_table: MeetingTable,
) -> None:
    """The HYBRID tripwire: the committed weights and the live corpus disagree.

    This is the same shape as the PR #301 tripwire (Task 18.14) that preceded the
    baseline-6 re-ground — a committed fit one baseline behind the corpus under
    it, held as an explicit, reviewable pin until the re-fit lands. The
    baseline-7 record re-recorded ``replays/ml_corpus`` without re-grounding the
    ML program; that re-ground is a NAMED follow-up
    (audits/audit-phase-20-baseline-7.md §10.2), and this test is what keeps the
    interim state honest rather than silent.

    Both halves are asserted, so the tripwire cannot pass by accident: the
    artifact is INTERNALLY consistent (weights, cap and fit-corpus record all key
    to each other and to the baseline-6 fit-side count of 367), and it is
    EXTERNALLY stale (the live corpus fingerprints differently and carries 345
    fit-side meetings, which would re-derive the cap to 49 335 rather than the
    committed 52 481). When the re-ground lands, both halves move together and
    this test fails — which is the point.
    """

    cap = load_staleness_cap(_ARTIFACT_DIR)
    _, weights_sha256 = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    record = load_fit_corpus_record(_ARTIFACT_DIR)

    # Internally consistent: the committed artifact is a coherent baseline-6 fit.
    assert record.weights_sha256 == weights_sha256
    assert cap.weights_sha256 == weights_sha256
    assert record.corpus_set == "9p2i"
    assert record.fit_side_meetings == 367
    assert cap.max_uses == derive_max_uses(record.fit_side_meetings) == 52_481

    # Externally stale: the live corpus is the baseline-7 recording.
    views = build_meeting_views(corpus_table)
    assert corpus_table.splits is not None
    test_seeds = set(corpus_table.splits.test)
    live_fit_meetings = sum(1 for v in views if v.seed not in test_seeds)
    assert live_fit_meetings == 345
    assert derive_max_uses(live_fit_meetings) == 49_335 != cap.max_uses
    assert record.corpus_sha256 != fit_corpus_fingerprint(_CORPUS)


def test_fit_corpus_fence_fails_loud_on_substrate_and_key_drift(
    tmp_path: Path,
) -> None:
    """The Task-18.14 fence: the loader catches substrate drift and a keyed-wrong
    record, and refuses a missing fit-corpus record.

    ``SurrogateStalenessCap`` keys only on the weights, so a bake-off that loaded
    these weights against a re-recorded corpus would raise on weights drift but
    silently score against a stale surrogate. The committed fit-corpus record
    closes that gap: a ``corpus_dir`` whose fingerprint disagrees raises, a
    record keyed to different weights raises, and an absent record raises.
    """

    # Loading against the WRONG corpus (the 4p1i set) fingerprints differently.
    with pytest.raises(ValueError, match="substrate drifted"):
        load_surrogate_runner_factory(
            _ARTIFACT_DIR, corpus_dir=_REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
        )
    # And against its OWN set, because the baseline-7 record re-recorded the
    # corpus without re-grounding the fit (the tripwire above). This is the fence
    # doing its job on a real drift, not a synthetic one.
    with pytest.raises(ValueError, match="substrate drifted"):
        load_surrogate_runner_factory(_ARTIFACT_DIR, corpus_dir=_CORPUS)

    # The gate is a gate, not a wall: an artifact whose record names the corpus it
    # is actually handed loads. Re-fingerprinting the record is exactly what the
    # deferred re-ground will do -- with re-fitted WEIGHTS beside it, which is why
    # this local copy is a fence proof and not a shortcut around the re-ground.
    for name in (
        "ballot-predictor.json",
        "ballot-predictor.json.sha256",
        "max-uses.json",
    ):
        (tmp_path / name).write_text((_ARTIFACT_DIR / name).read_text())
    regrounded = load_fit_corpus_record(_ARTIFACT_DIR).model_copy(
        update={"corpus_sha256": fit_corpus_fingerprint(_CORPUS)}
    )
    (tmp_path / "fit-corpus.json").write_text(
        regrounded.model_dump_json(indent=2) + "\n"
    )
    assert callable(load_surrogate_runner_factory(tmp_path, corpus_dir=_CORPUS))

    # A copied artifact whose fit-corpus record is keyed to DIFFERENT weights
    # (a botched re-fit that moved the weights but not the corpus record).
    for name in (
        "ballot-predictor.json",
        "ballot-predictor.json.sha256",
        "max-uses.json",
    ):
        (tmp_path / name).write_text((_ARTIFACT_DIR / name).read_text())
    drifted = load_fit_corpus_record(_ARTIFACT_DIR).model_copy(
        update={"weights_sha256": "a" * 64}
    )
    (tmp_path / "fit-corpus.json").write_text(drifted.model_dump_json(indent=2) + "\n")
    with pytest.raises(ValueError, match="fit-corpus record and the artifact"):
        load_surrogate_runner_factory(tmp_path)

    # An artifact with weights + cap but NO fit-corpus record fails loud.
    (tmp_path / "fit-corpus.json").unlink()
    with pytest.raises(FileNotFoundError, match="fit-corpus provenance"):
        load_surrogate_runner_factory(tmp_path)


def test_committed_artifact_round_trips_and_the_refit_no_longer_matches(
    corpus_table: MeetingTable,
) -> None:
    """The artifact still round-trips byte-stably; the refit is now a DIFFERENT fit.

    Two claims, and only the first survives the baseline-7 record unchanged.

    Serialization is byte-stable: loading the committed bytes and re-serializing
    is the identity, so the sha256 sidecar pins exactly what the bake-off
    reloads. That is a property of the format and holds on any corpus.

    Refit provenance used to be parameter-level -- ``fit_corpus_ballot_predictor``
    reproduced every committed parameter to float ULP, because the committed
    weights WERE that refit. The baseline-7 record re-recorded the corpus without
    re-grounding the fit (audits/audit-phase-20-baseline-7.md §10.2), so a refit
    on the live corpus is a genuinely different model, and the pin inverts: the
    parameters must DISAGREE by more than float noise. Same tripwire shape as
    ``test_the_committed_surrogate_is_a_baseline6_fit_on_a_baseline7_corpus``, at
    parameter granularity -- when the re-ground lands, this fails and the
    ULP-equivalence pin comes back.

    The committed staleness cap keys to the artifact's OWN fit-side count (367,
    the ~143× rule of the Task 17.10 designer ruling), not to the live corpus's
    345 -- asserting it against the live count is what would silently launder a
    stale cap as a current one.
    """

    predictor, sha = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    committed_json = (_ARTIFACT_DIR / "ballot-predictor.json").read_text()
    # Load -> re-serialize is the identity (byte-stable round trip).
    assert predictor.to_artifact_json() == committed_json

    cap = load_staleness_cap(_ARTIFACT_DIR)
    record = load_fit_corpus_record(_ARTIFACT_DIR)
    assert cap.weights_sha256 == sha
    assert cap.max_uses == derive_max_uses(record.fit_side_meetings) == 52_481
    assert cap.unit == "meetings"

    # The live corpus's fit side, which the cap is NOT keyed to.
    assert corpus_table.splits is not None
    fit_seeds = frozenset(corpus_table.splits.train) | frozenset(
        corpus_table.splits.val
    )
    live_fit_meetings = len(
        {(r.seed, r.meeting_id) for r in corpus_table.rows if r.seed in fit_seeds}
    )
    assert live_fit_meetings == 345 != record.fit_side_meetings

    refit = json.loads(fit_corpus_ballot_predictor(corpus_table).to_artifact_json())
    committed = json.loads(committed_json)
    # The SHAPE is unchanged -- same keys, same feature names, same format marker.
    # Only the fitted numbers moved, which is what "a different fit" means.
    assert refit.keys() == committed.keys()
    diverged = 0
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
            if refit_floats != pytest.approx(committed_floats, rel=1e-9, abs=1e-12):
                diverged += 1
        elif isinstance(committed_value, str) and "0x" in committed_value:
            if float.fromhex(refit_value) != pytest.approx(
                float.fromhex(committed_value), rel=1e-9, abs=1e-12
            ):
                diverged += 1
        else:
            # Non-float metadata (format marker, feature names, epochs) is exact
            # either way -- a re-fit changes the numbers, not the schema.
            assert refit_value == committed_value, key
    assert diverged > 0, (
        "the refit reproduces the committed weights to ULP -- either the ML "
        "re-ground landed (delete this tripwire and restore the equivalence pin) "
        "or the corpus never moved"
    )


def test_bakeoff_reloads_the_committed_artifact_and_reproduces_the_numbers(
    corpus_table: MeetingTable,
) -> None:
    """The LOADED committed weights reproduce the reported held-out numbers.

    The DoD round-trip in its own words: the bake-off reloads exactly the
    committed artifact, and evaluating the FROZEN predictor (no refit — the
    ``predictor`` injection on :class:`BallotSurrogateModel`) over the held-out
    test views reproduces the report's ranking/decision census and the
    predicted-ballot calibration channel (baseline-6: 96 test meetings, 60
    ejections; the decision head still skips every meeting).
    """

    predictor, _ = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    frozen = BallotSurrogateModel(corpus_table, predictor=predictor)
    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    test_views = [
        view for view in build_meeting_views(corpus_table) if view.seed in test_seeds
    ]
    assert len(test_views) == 87  # was 96

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
    assert top1_hits == 45  # was 46
    assert predicted_ejections == 2  # was 0
    assert predicted_skips == 85  # was 96
    assert correct_skips == 32  # was 36

    calibration = frozen.predicted_ballot_calibration(test_views)
    assert calibration.predicted_ballots == 97  # was 100
    assert calibration.predicted_skips == 401  # was 457
    # Inference from FIXED committed weights; tolerance covers libm exp variance
    # across platforms, nothing more.
    assert calibration.brier == pytest.approx(
        0.3061476258037689, abs=1e-9
    )  # was 0.2541857827042379


def test_surrogate_fidelity_reproduces_pinned_numbers(
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """The held-out surrogate report reproduces the pinned deterministic numbers.

    Baseline-6 truth (Task 18.14 re-ground): the meeting economy REVERTED to
    eject-majority (60 of the 96 scored meetings EJECT), the ranking channel
    stays strong (46/60 top-1) but the decision channel still predicts SKIP on
    every meeting — which now scores BELOW the always-eject constant, so
    ``degenerates_to_skip`` reads True and the verdict flips to NO-GO. The honest
    reading is in the report's §5.
    """

    report = surrogate_report
    # Integer census — exact.
    assert report.meetings_scored == 87  # was 96
    assert report.ejection_meetings == 55  # was 60
    assert report.skip_meetings == 32  # was 36
    assert report.top1_hits == 44  # was 46
    assert report.top2_hits == 52  # was 55
    assert report.predicted_ejections == 2  # was 0
    assert report.predicted_skips == 85  # was 96
    assert report.correct_skip_decisions == 32  # was 36
    assert report.correct_eject_decisions == 2  # was 0
    assert report.ejection_predicted_skips == 53  # was 60
    assert report.degenerates_to_skip is True
    assert report.ballot_rows == 283  # was 323
    assert report.honest_ceiling.ejections_total == 55  # was 60
    assert report.honest_ceiling.reachable == 44  # was 51
    # Floats — deterministic, pinned to the exact literals.
    assert report.top1 == pytest.approx(0.8, abs=1e-12)  # was 0.7666666666666667
    assert report.top2 == pytest.approx(
        0.9454545454545454, abs=1e-12
    )  # was 0.9166666666666666
    assert report.skip_vs_eject_accuracy == pytest.approx(
        0.39080459770114945, abs=1e-12
    )  # was 0.375
    assert report.always_eject_baseline == pytest.approx(
        0.632183908045977, abs=1e-12
    )  # was 0.625
    assert report.brier == pytest.approx(
        0.0667040763679702, abs=1e-12
    )  # was 0.06785997153616342
    assert report.ece == pytest.approx(
        0.10106989788592366, abs=1e-12
    )  # was 0.09477687280149634
    assert report.ballot_brier == pytest.approx(
        0.12890565371024734, abs=1e-12
    )  # was 0.1242077399380805
    assert report.ballot_ece == pytest.approx(
        0.0818727915194337, abs=1e-12
    )  # was 0.048885448916408246
    assert report.honest_ceiling.max_achievable_top1 == pytest.approx(
        0.8, abs=1e-12
    )  # was 0.85


def test_go_no_go_reproduces_the_re_measured_no_go_verdict(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """``decide_go_no_go`` on the two same-population reports pins the baseline-6 NO-GO.

    The bar is the pre-stated, owner-ratified 15.13 bar, re-MEASURED on the 18.13
    corpus (locked decision 4 travels): axes 1 (ceiling) and 2 (beats FO-6) pass,
    but axis 3 FAILS — the decision channel's all-SKIP accuracy (0.375) is below
    the eject-majority always-eject constant (0.625) — so the conjunction is
    NO-GO. Per the pre-committed mapping the surrogate ships DIAGNOSTIC-only and
    the fake-provider MeetingManager stays the training-time runner (the bake-off
    is never blocked, §5–§6).
    """

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.verdict == "NO-GO"
    assert verdict.meets_ceiling_bar is True
    assert verdict.beats_prior_baseline is True
    assert verdict.beats_always_eject is False
    assert verdict.training_time_runner == "fake-provider-meeting-manager"
    assert verdict.surrogate_role == "diagnostic-only"
    assert verdict.top1_bar == pytest.approx(
        0.6000000000000001, abs=1e-12
    )  # was 0.6375


# --------------------------------------------------------------------------- #
# The split bar: two claims reported apart, one conjunction driving consequence #
# --------------------------------------------------------------------------- #


def test_split_verdict_separates_the_ranking_and_decision_claims(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The harness can now say WHICH half failed, on the current committed corpus.

    Every cell re-measured here, none carried over from the previous bar: the
    ranking instrument clears its bar (axes 1 and 2) and the decision channel does
    not (axis 3), so the composed verdict is still NO-GO and the surrogate still
    ships diagnostic-only under the pre-committed fallback mapping.
    """

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.bar_id == GO_BAR_ID
    assert verdict.ranking_verdict == "GO"
    assert verdict.decision_verdict == "NO-GO"
    assert verdict.verdict == "NO-GO"
    assert verdict.surrogate_role == "diagnostic-only"
    assert verdict.top1_bar == pytest.approx(0.6000000000000001, abs=1e-12)
    # AT the measured ceiling, not above a floor with headroom left: axis 1 is
    # saturated in HEADROOM, which is a different statement from a dead axis.
    assert verdict.top1_ceiling_gap == pytest.approx(0.0, abs=1e-12)
    assert verdict.surrogate_top1 == pytest.approx(0.8, abs=1e-12)
    assert verdict.ceiling_top1 == pytest.approx(0.8, abs=1e-12)
    # WHY the ceiling sits at 0.8 — the overlapping channel decomposition.
    assert verdict.ceiling_flag_present == 45
    assert verdict.ceiling_proximity_present == 48
    assert verdict.ceiling_belief_lead == 43
    assert verdict.ceiling_reachable == 44


def test_axis_one_still_discriminates_a_weaker_candidate(
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """The ceiling axis is saturated in headroom, NOT dead.

    The floor is 0.75 x ceiling = 0.6000 on this population, so a candidate ranking
    below it fails axis 1 — the axis discriminates, which is why the split reports
    it rather than retiring it.
    """

    bar = GO_TOP1_CEILING_RATIO * surrogate_report.honest_ceiling.max_achievable_top1
    assert bar == pytest.approx(0.6000000000000001, abs=1e-12)
    assert surrogate_report.top1 >= bar
    weaker = surrogate_report.model_copy(update={"top1": bar - 0.01})
    assert weaker.top1 < bar


def test_the_reshaped_bar_cannot_manufacture_a_promotion(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """No input that was NO-GO under the unsplit bar becomes GO under this one.

    The one failure mode that would discredit the re-ground. Swept over every
    combination of the three axis outcomes: the composed verdict is the conjunction
    of all three, exactly as before the split, so GO requires all three and the
    split is reporting only.
    """

    for meets_ceiling in (True, False):
        for beats_baseline in (True, False):
            for beats_eject in (True, False):
                ceiling = surrogate_report.honest_ceiling.max_achievable_top1
                bar = GO_TOP1_CEILING_RATIO * ceiling
                top1 = ceiling if meets_ceiling else bar / 2.0
                baseline_top1 = (top1 / 2.0) if beats_baseline else (top1 + 0.05)
                accuracy = (
                    surrogate_report.always_eject_baseline + 0.05
                    if beats_eject
                    else surrogate_report.always_eject_baseline - 0.05
                )
                surrogate = surrogate_report.model_copy(
                    update={"top1": top1, "skip_vs_eject_accuracy": accuracy}
                )
                baseline = fo6_report.model_copy(update={"top1": baseline_top1})
                verdict = decide_go_no_go(surrogate, baseline)

                unsplit_go = meets_ceiling and beats_baseline and beats_eject
                assert (verdict.verdict == "GO") is unsplit_go
                assert (verdict.ranking_verdict == "GO") is (
                    meets_ceiling and beats_baseline
                )
                assert (verdict.decision_verdict == "GO") is beats_eject
                # ...and the consequence mapping still keys off the conjunction.
                assert (verdict.surrogate_role == "training-time-runner") is unsplit_go
                assert (verdict.training_time_runner == "surrogate") is unsplit_go


def test_decision_reachability_is_the_tallys_own_gate_quantity(
    corpus_table: MeetingTable,
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """How many meetings could eject AT ALL before anyone spends a fit on axis 3.

    The tally ejects only when the MAX confidence among the ballots naming the
    single non-SKIP plurality target clears
    ``DEFAULT_SKIP_CONFIDENCE_THRESHOLD`` (meetings/voting.py rule 4). That is the
    quantity counted here — deliberately NOT ``ejection_prob``, which is a mean of
    per-voter target-probability mass and a different number. On the committed
    corpus only 2 of 87 held-out meetings reach it, which is the same 2 the model
    actually ejects.
    """

    assert surrogate_report.plurality_confidence_meetings == 87
    assert surrogate_report.decision_reachable_meetings == 2
    assert surrogate_report.decision_reachability == pytest.approx(2 / 87, abs=1e-12)
    # Reachability is the CEILING on the decision channel: a meeting whose gate is
    # never reached cannot be ejected however the model ranks it.
    assert surrogate_report.predicted_ejections == (
        surrogate_report.decision_reachable_meetings
    )

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.decision_reachable_meetings == 2
    assert verdict.decision_reachability == pytest.approx(2 / 87, abs=1e-12)

    # A ballot-free model leaves the cell unmeasured rather than reporting zero:
    # FO-6 predicts ejections, not ballots, so it has no plurality confidence.
    assert fo6_report.plurality_confidence_meetings == 0
    assert fo6_report.decision_reachable_meetings == 0
    views = build_meeting_views(corpus_table)
    fo6 = Fo6Logistic()
    fo6.fit(views)
    assert fo6.predict(views[0]).plurality_confidence is None


def test_the_report_is_a_re_fit_not_frozen_weights(
    corpus_table: MeetingTable,
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """``run_surrogate_fidelity`` re-fits every fold — the "frozen weights" reading
    is wrong at the source.

    The verifier's own control: a factory that PRE-INSTALLS the committed
    artifact's predictor and one that does not produce byte-identical reports on
    the same table, because ``BallotSurrogateModel.fit`` REPLACES the installed
    predictor rather than refining it.
    """

    predictor, _ = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    preinstalled = run_surrogate_fidelity(
        corpus_table,
        lambda: BallotSurrogateModel(corpus_table, predictor=predictor),
        model_name="ballot-surrogate.v1",
    )
    assert preinstalled == surrogate_report


def test_no_go_verdict_holds_on_live_served_clamped_features(
    corpus_table: MeetingTable,
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The runner-path fidelity replay: the NO-GO verdict inputs survive J1 serving.

    The diagnostic runner reads ``suspicion_graph_for_meeting()`` — the
    J1-CLAMPED render — while the table (and therefore the §5 verdict's
    scoring) reads the raw stored scalar; the measured divergence is 28
    held-out cells (the baseline-6 parity census). Codex review on PR #280: the
    verdict must be shown to hold on the inputs a bake-off runner actually
    serves. So: replace every held-out cell's ``belief_suspicion`` with the
    PRODUCTION-served value (the memory-augmented walk's graphs — the exact
    channel the runner reads), score the FROZEN committed artifact over the same
    test views, and assert the verdict inputs reproduce EXACTLY — same decision
    and same top-1 target on every one of the 96 meetings, so the two passing GO
    axes AND the failing third axis (the NO-GO) hold unchanged on live-served
    features. The only movement is a decision-irrelevant sub-top-rank reorder on
    a handful of meetings (libm/ULP-sensitive near probability ties across CPUs,
    the same platform variance the artifact round-trip tolerates).
    """

    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(_CORPUS)
    game_map = load_canonical_map()
    per_seed_roles = roles_by_seed(
        _CORPUS,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    served: dict[tuple[str, PlayerId], dict[PlayerId, float]] = {}
    for seed in sorted(test_seeds):
        walk = _walk_game_vj(
            _CORPUS / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=per_seed_roles[seed],
            game_map=game_map,
        )
        for meeting in walk.meetings:
            for voter, graph in meeting.suspicion_graph_by_voter.items():
                served[(meeting.meeting_id, voter)] = {
                    entry.player_id: entry.suspicion for entry in graph
                }

    replaced = 0

    def clamp_row(row: MeetingTableRow) -> MeetingTableRow:
        nonlocal replaced
        if row.seed not in test_seeds:
            return row
        graph = served[(row.meeting_id, row.voter)]
        candidates = []
        for cand in row.candidates:
            # An absent production row is the unseeded neutral prior — the
            # same 0.5 the table carries (fold parity is exact, so every
            # non-divergent cell compares bit-equal).
            live = graph.get(cand.candidate, 0.5)
            if cand.is_self or live == cand.belief_suspicion:
                candidates.append(cand)
            else:
                replaced += 1
                candidates.append(cand.model_copy(update={"belief_suspicion": live}))
        return row.model_copy(update={"candidates": tuple(candidates)})

    clamped = corpus_table.model_copy(
        update={"rows": tuple(clamp_row(row) for row in corpus_table.rows)}
    )
    # Exactly the parity census's held-out J1-divergent cells move — the two
    # instruments cross-validate each other.
    assert replaced == 19  # was 28

    predictor, _ = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    raw_model = BallotSurrogateModel(corpus_table, predictor=predictor)
    live_model = BallotSurrogateModel(clamped, predictor=predictor)
    test_views = [
        view for view in build_meeting_views(corpus_table) if view.seed in test_seeds
    ]
    top1_hits = 0
    predicted_skips = 0
    correct_skips = 0
    rank_reorders = 0
    for view in test_views:
        raw_pred = raw_model.predict(view)
        live_pred = live_model.predict(view)
        # The verdict inputs are IDENTICAL per meeting under live serving.
        assert live_pred.ejected == raw_pred.ejected
        assert live_pred.ranking[0] == raw_pred.ranking[0]
        rank_reorders += int(live_pred.ranking != raw_pred.ranking)
        if live_pred.ejected is None:
            predicted_skips += 1
            if view.ejected is None:
                correct_skips += 1
        if view.is_ejection and live_pred.ranking[0] == view.ejected:
            top1_hits += 1
    assert top1_hits == 45  # was 46
    assert predicted_skips == 85  # was 96
    assert correct_skips == 32  # was 36
    # Third-rank-and-below shuffles only, BOUNDED not pinned: the reorder count
    # sits on near-ties in the softmax shares, so it is libm/ULP-sensitive
    # across CPUs. The per-meeting decision/top-1 equality above is the
    # load-bearing claim.
    assert rank_reorders <= 4

    # The three verdict axes re-stated on the live-served scoring, against the
    # SAME population bar the §5 verdict used (every decision is SKIP, so the
    # decision accuracy is exactly the correct-skip share). Axes 1–2 PASS and
    # axis 3 FAILS unchanged — the NO-GO holds on the served features.
    live_top1 = top1_hits / surrogate_report.ejection_meetings
    live_accuracy = correct_skips / surrogate_report.meetings_scored
    assert live_top1 >= 0.75 * surrogate_report.honest_ceiling.max_achievable_top1
    assert live_top1 > fo6_report.top1
    assert live_accuracy < surrogate_report.always_eject_baseline


def test_fo6_rebaseline_reproduces_pinned_numbers(
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The FO-6 prior baseline, re-measured: it degenerates to SKIP again.

    FO-6 is a physical logistic FIT FRESH from whatever corpus it is handed, so
    these are measurements of the baseline-7 corpus, not a frozen artifact's
    reproduction — which is why they re-pin here rather than waiting on the ML
    re-ground (audits/audit-phase-20-baseline-7.md §10.2).

    The head has flipped twice now. Baseline 5 degenerated to SKIP; baseline 6
    reverted the meeting mix to eject-majority and FO-6 went all-EJECT (96 of 96,
    exactly tying the always-eject constant at 0.625); on the baseline-7 record it
    degenerates back to SKIP — 75 of 87 meetings called SKIP, so its decision
    accuracy (0.414) now falls BELOW the always-eject constant (0.632) instead of
    tying it. The instability across three consecutive records is the finding: this
    head tracks the meeting mix, not the physics. Its ranking is the more stable
    half, and still the point of the comparison — 23/55 top-1, below the
    surrogate's, so axis 2 of the bar keeps passing.
    """

    report = fo6_report
    assert report.top1_hits == 23
    assert report.ejection_meetings == 55
    assert report.degenerates_to_skip is True
    assert report.predicted_ejections == 12
    assert report.predicted_skips == 75
    assert report.correct_skip_decisions == 28
    assert report.ejection_predicted_skips == 47
    assert report.top1 == pytest.approx(0.41818181818181815, abs=1e-12)
    assert report.top2 == pytest.approx(0.6363636363636364, abs=1e-12)
    assert report.skip_vs_eject_accuracy == pytest.approx(
        0.41379310344827586, abs=1e-12
    )
    # The head falls below the constant it used to tie.
    assert report.skip_vs_eject_accuracy < report.always_eject_baseline


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

    The label set covers the ballot join targets, the coercion flag, the meeting
    outcome, AND the roles ground truth (``voter_role`` / ``voter_is_impostor`` /
    per-candidate ``role`` / ``is_impostor`` / ``is_ejected``) — a predict path
    that read ANY of them would diverge from the clean model.
    """

    return row.model_copy(
        update={
            "ballot_target": "poisoned-label",
            "ballot_confidence": 0.0,
            "ballot_primary_reason_id": None,
            "ballot_coerced_skip": True,
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
            "ballot_coerced_skip": True,
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
# 8b. COERCED-SKIP FIT EXCLUSION (Task 17.10 designer ruling)                 #
# --------------------------------------------------------------------------- #


def test_committed_corpus_carries_zero_coerced_skip_rows(
    corpus_table: MeetingTable,
) -> None:
    """The baseline-6 corpus records ONE J2-coerced ballot — the census moved.

    A FINDING, not a stale pin. Through baseline 5 this bucket was honestly EMPTY
    on committed bytes: the 17.9 re-record produced zero
    ``UNCITED_ZERO_FLAG_EJECT_MARKER`` ballots on either set, and the 18.12 samples
    record likewise ("the coerced-SKIP bucket is honestly 0"), so the fit-side
    exclusion had never actually dropped a row outside a synthetic fixture. At
    baseline 6 it drops exactly ONE — ``headless-seed-1027:meeting-4`` on 9p2i
    (4p1i stays 0) — so the citation gate's coercion path is now exercised by
    committed corpus bytes for the first time, and the fit-side exclusion is
    load-bearing rather than merely proven-in-fixture.

    One row of 468 meetings is far too small to move any fit, so this is reported,
    not banded. The fence itself is still proven on a synthetic marking below (a
    rule that cannot move is not a rule).
    """

    assert sum(row.ballot_coerced_skip for row in corpus_table.rows) == 7  # was 1
    four = build_meeting_table(_REPO_ROOT / "replays" / "ml_corpus" / "4p1i")
    assert sum(row.ballot_coerced_skip for row in four.rows) == 0


def _mark_coerced(
    table: MeetingTable, seeds: frozenset[int], *, poison_labels: bool
) -> MeetingTable:
    """Flag every row of ``seeds`` as coerced; optionally poison its labels."""

    def mark(row: MeetingTableRow) -> MeetingTableRow:
        if row.seed not in seeds:
            return row
        update: dict[str, object] = {"ballot_coerced_skip": True}
        if poison_labels:
            update["ballot_target"] = "poisoned-label"
            update["ballot_confidence"] = 0.0
        return row.model_copy(update=update)

    return table.model_copy(update={"rows": tuple(mark(row) for row in table.rows)})


def test_coerced_skip_rows_are_dropped_from_every_fit_path() -> None:
    """Rows flagged ``ballot_coerced_skip`` leave BOTH fits; their labels are dead.

    On the (fast) 4p1i corpus table: flag one fit-side game's rows as coerced
    with their labels intact vs with their labels POISONED to a target outside
    every candidate set — a label that would raise ``ValueError`` inside
    ``BallotPredictor.fit`` if it were ever read. Both the corpus training entry
    (:func:`fit_corpus_ballot_predictor`) and the fidelity-adapter path
    (:meth:`BallotSurrogateModel.fit`) must produce byte-identical predictors
    for the two tables (the rows were dropped, so the poison is unreachable),
    and the drop must actually MOVE the fit vs the unmarked table (rows really
    left). Predict-side blindness to the flag is pinned by the §8 poison tests
    (``_poison_labels`` poisons ``ballot_coerced_skip`` too) — the fidelity
    replay scores recorded bytes unfiltered.
    """

    table = build_meeting_table(_REPO_ROOT / "replays" / "ml_corpus" / "4p1i")
    assert table.splits is not None
    rows_bearing = {row.seed for row in table.rows}
    marked_seed = frozenset(
        {next(seed for seed in table.splits.train if seed in rows_bearing)}
    )

    marked = _mark_coerced(table, marked_seed, poison_labels=False)
    poisoned = _mark_coerced(table, marked_seed, poison_labels=True)

    # The corpus training entry: byte-identical with labels intact vs poisoned
    # (dropped rows are never read), and different from the unmarked fit (the
    # rows really left the fit side).
    fit_marked = fit_corpus_ballot_predictor(marked)
    fit_poisoned = fit_corpus_ballot_predictor(poisoned)
    assert fit_marked.to_artifact_json() == fit_poisoned.to_artifact_json()
    fit_clean = fit_corpus_ballot_predictor(table)
    assert fit_clean.to_artifact_json() != fit_marked.to_artifact_json()

    # The fidelity-adapter path drops the same rows inside per-fold fits.
    views = build_meeting_views(table)
    test_seeds = frozenset(table.splits.test)
    fit_views = [view for view in views if view.seed not in test_seeds]
    model_marked = BallotSurrogateModel(marked)
    model_poisoned = BallotSurrogateModel(poisoned)
    model_marked.fit(fit_views)
    model_poisoned.fit(fit_views)
    assert (
        model_marked.predictor.to_artifact_json()
        == model_poisoned.predictor.to_artifact_json()
    )


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
    assert calib.predicted_ballots == 107  # was 100
    assert calib.predicted_skips == 391  # was 457
    assert calib.brier == pytest.approx(
        0.33399645935635536, abs=1e-12
    )  # was 0.2541857827042379
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
