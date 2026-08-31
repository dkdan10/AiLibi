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
  (Task 17.10 designer ruling; FIVE such fit-side rows on the baseline-8 corpus,
  so the exclusion drops real rows rather than only synthetic ones);
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
    BALLOT_FEATURE_NAMES,
    MASKED_IS_REPORTER,
    BallotSurrogateModel,
    PredictedBallot,
    SurrogateStalenessCap,
    _target_was_rewritten,
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
    SURROGATE_VERDICT_FILENAME,
    SurrogateMeetingRunner,
    SurrogateStalenessExceededError,
    SurrogateUseCounter,
    _meeting_index_from_id,  # noqa: PLC2701 - the id-parse fence is under test
    fit_corpus_fingerprint,
    load_fit_corpus_record,
    load_surrogate_runner_factory,
    load_surrogate_verdict,
    write_surrogate_verdict_artifact,
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


def test_the_committed_surrogate_is_a_baseline8_fit_on_the_baseline8_corpus(
    corpus_table: MeetingTable,
) -> None:
    """The EQUIVALENCE pin: the committed weights and the live corpus AGREE.

    The inverse of the hybrid tripwire it replaces. That tripwire asserted a fit
    two baselines behind the corpus under it and was written to fail the day the
    re-ground landed; this asserts what the re-ground produced. One assertion per
    seam the re-fit had to move together, so a PARTIAL re-ground — new weights
    with a stale cap, a record re-keyed against unmoved weights — fails here
    rather than at some consumer's load.

    Both halves are asserted, so the pin cannot pass by accident: the artifact is
    INTERNALLY consistent (weights, cap and fit-corpus record all key to each
    other and to the fit-side count), and it is EXTERNALLY current (the live
    corpus fingerprints to exactly the digest the record names, and re-deriving
    the cap from the live fit side reproduces the committed one).
    """

    cap = load_staleness_cap(_ARTIFACT_DIR)
    _, weights_sha256 = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    record = load_fit_corpus_record(_ARTIFACT_DIR)

    # Internally consistent: the artifact is a coherent fit.
    assert record.weights_sha256 == weights_sha256
    assert cap.weights_sha256 == weights_sha256
    assert record.corpus_set == "9p2i"
    assert record.fit_side_meetings == 348  # was 367 on the baseline-6 fit
    assert cap.max_uses == derive_max_uses(record.fit_side_meetings) == 49_764

    # Externally current: the live corpus IS the corpus the fit was made on.
    views = build_meeting_views(corpus_table)
    assert corpus_table.splits is not None
    test_seeds = set(corpus_table.splits.test)
    live_fit_meetings = sum(1 for v in views if v.seed not in test_seeds)
    assert live_fit_meetings == record.fit_side_meetings
    assert derive_max_uses(live_fit_meetings) == cap.max_uses
    assert record.corpus_sha256 == fit_corpus_fingerprint(_CORPUS)


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

    The re-ground makes the committed artifact's own set the POSITIVE leg, so
    the refusal is proved on a synthetic drifted record instead — a gate whose
    only negative case was the repo's own staleness would stop biting the moment
    that staleness was paid off.
    """

    # Loading against the WRONG corpus (the 4p1i set) fingerprints differently.
    with pytest.raises(ValueError, match="substrate drifted"):
        load_surrogate_runner_factory(
            _ARTIFACT_DIR, corpus_dir=_REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
        )
    # The gate is a gate, not a wall: the committed artifact against the corpus it
    # was actually fitted on loads clean, fingerprint check and all.
    assert callable(load_surrogate_runner_factory(_ARTIFACT_DIR, corpus_dir=_CORPUS))

    # The planted refusal: a copied artifact whose record names a corpus digest
    # nothing on disk produces. One flipped nibble is enough — the fence compares
    # the whole digest, so this is the smallest drift it must still catch.
    for name in (
        "ballot-predictor.json",
        "ballot-predictor.json.sha256",
        "max-uses.json",
    ):
        (tmp_path / name).write_text((_ARTIFACT_DIR / name).read_text())
    committed_record = load_fit_corpus_record(_ARTIFACT_DIR)
    live_fingerprint = fit_corpus_fingerprint(_CORPUS)
    assert committed_record.corpus_sha256 == live_fingerprint
    perturbed = committed_record.model_copy(
        update={"corpus_sha256": ("b" if live_fingerprint[0] != "b" else "c")
        + live_fingerprint[1:]}
    )
    (tmp_path / "fit-corpus.json").write_text(perturbed.model_dump_json(indent=2) + "\n")
    with pytest.raises(ValueError, match="substrate drifted"):
        load_surrogate_runner_factory(tmp_path, corpus_dir=_CORPUS)

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


# --------------------------------------------------------------------------- #
# 6b. THE COMMITTED VERDICT + THE TRAINING-TIME INSTALL GATE                   #
# --------------------------------------------------------------------------- #


def test_the_committed_verdict_is_keyed_on_the_weights_and_reproduces(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The verdict artifact is the machine-readable NO-GO, keyed to the weights.

    Mirrors the conviction verdict byte for byte: sorted keys, one trailing
    newline, and a ``weights_sha256`` naming the artifact it sits beside — so a
    reader never has to take the consequence mapping out of the report's prose.
    Field for field it is what ``decide_go_no_go`` returns for the two
    same-population reports this module already measures, so it is a recorded
    output rather than a hand-written one.
    """

    _, weights_sha256 = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    verdict = load_surrogate_verdict(_ARTIFACT_DIR)
    assert verdict.weights_sha256 == weights_sha256
    assert verdict.bar_id == GO_BAR_ID
    assert verdict.verdict == "NO-GO"
    assert (verdict.ranking_verdict, verdict.decision_verdict) == ("GO", "NO-GO")
    assert verdict.surrogate_role == "diagnostic-only"
    assert verdict.training_time_runner == "fake-provider-meeting-manager"

    committed = (_ARTIFACT_DIR / SURROGATE_VERDICT_FILENAME).read_text()
    assert committed.endswith("}\n")
    assert json.loads(committed) == verdict.model_dump()

    rederived = decide_go_no_go(
        surrogate_report, fo6_report, weights_sha256=weights_sha256
    )
    # The artifact stores the corpus path REPO-RELATIVE; this run built its
    # table from an absolute one, so that one field is resolved.
    assert Path(rederived.replay_set_dir).resolve() == _CORPUS.resolve()

    # The re-derivation EQUALS the committed artifact, field for field. During
    # the interim between the baseline-7 record and the Task-21.17 re-ground this
    # assertion was relaxed to "differs on the measured cells, agrees on the
    # consequence mapping", because the corpus had moved under a frozen fit;
    # the re-ground restores the strong form, which is the only one that proves
    # the committed verdict is a recorded output rather than a hand-written one.
    committed_fields = verdict.model_dump()
    rederived_fields = rederived.model_dump()
    assert rederived.verdict == verdict.verdict == "NO-GO"
    differing = {
        key
        for key in committed_fields
        if key != "replay_set_dir" and committed_fields[key] != rederived_fields[key]
    }
    assert not differing


def test_writing_a_verdict_that_names_no_weights_is_refused(tmp_path: Path) -> None:
    """An unkeyed verdict cannot say which artifact it judged, so it is refused."""

    unkeyed = load_surrogate_verdict(_ARTIFACT_DIR).model_copy(
        update={"weights_sha256": None}
    )
    with pytest.raises(ValueError, match="must name the weights it authorizes"):
        write_surrogate_verdict_artifact(unkeyed, tmp_path)


def test_the_install_gate_refuses_the_committed_no_go_as_a_training_runner(
    tmp_path: Path,
) -> None:
    """Both directions of the gate, on committed bytes rather than a fixture.

    The committed verdict is NO-GO, so asking for the training-time role refuses
    — the pre-committed fallback mapping enforced by the load path rather than by
    convention. The diagnostic role, which is what every production call site
    holds, still loads the same artifact: a NO-GO surrogate remains a legal
    fidelity and probe runner, and a gate that blocked it would have retired a
    live capability instead of guarding one.

    The planted GO case proves the refusal is keyed on the COMPOSED ``verdict``
    field: the same artifact with a GO composed field installs, and — with the
    reporting halves left NO-GO to make the point — the gate neither reads them
    nor re-conjoins them. A GO verdict keyed to OTHER weights is refused before
    the verdict is even consulted, so a stale or copied verdict cannot authorize
    an artifact nobody judged.
    """

    with pytest.raises(ValueError, match="DIAGNOSTIC-ONLY"):
        load_surrogate_runner_factory(
            _ARTIFACT_DIR, install_role="training-time-runner"
        )
    assert callable(load_surrogate_runner_factory(_ARTIFACT_DIR))
    assert callable(
        load_surrogate_runner_factory(_ARTIFACT_DIR, install_role="diagnostic")
    )

    for name in (
        "ballot-predictor.json",
        "ballot-predictor.json.sha256",
        "max-uses.json",
        "fit-corpus.json",
    ):
        (tmp_path / name).write_text((_ARTIFACT_DIR / name).read_text())
    promoted = load_surrogate_verdict(_ARTIFACT_DIR).model_copy(
        update={"verdict": "GO", "surrogate_role": "training-time-runner"}
    )
    assert (promoted.ranking_verdict, promoted.decision_verdict) == ("GO", "NO-GO")
    write_surrogate_verdict_artifact(promoted, tmp_path)
    assert callable(
        load_surrogate_runner_factory(tmp_path, install_role="training-time-runner")
    )

    # A GO verdict that judged OTHER weights authorizes nothing here — checked
    # BEFORE the verdict value, so a stale copied GO cannot seat new weights.
    write_surrogate_verdict_artifact(
        promoted.model_copy(update={"weights_sha256": "a" * 64}), tmp_path
    )
    with pytest.raises(ValueError, match="a verdict that judged other weights"):
        load_surrogate_runner_factory(tmp_path, install_role="training-time-runner")
    assert callable(load_surrogate_runner_factory(tmp_path))

    # And an artifact with no verdict at all cannot be installed as the runner,
    # while it still loads for the diagnostic paths.
    (tmp_path / SURROGATE_VERDICT_FILENAME).unlink()
    with pytest.raises(FileNotFoundError, match="no committed surrogate verdict"):
        load_surrogate_runner_factory(tmp_path, install_role="training-time-runner")
    assert callable(load_surrogate_runner_factory(tmp_path))


def test_committed_artifact_round_trips_and_the_refit_no_longer_matches(
    corpus_table: MeetingTable,
) -> None:
    """The artifact round-trips byte-stably, and the refit reproduces it to ULP.

    Two claims, both restored by the Task-21.17 re-ground.

    Serialization is byte-stable: loading the committed bytes and re-serializing
    is the identity, so the sha256 sidecar pins exactly what the bake-off
    reloads. That is a property of the format and holds on any corpus.

    Refit provenance is parameter-level again: ``fit_corpus_ballot_predictor``
    over the live corpus reproduces every committed parameter, because the
    committed weights ARE that refit. Comparison is by ULP tolerance, not by
    bytes — the fit is numpy full-batch gradient descent, byte-identical on the
    recording platform and ULP-equivalent elsewhere — so this pin travels across
    CPUs while still refusing a genuinely different model. During the interim
    between the baseline-7 record and the re-ground this assertion was INVERTED,
    pinning that the refit disagreed; restoring it is what the re-ground earns.

    The committed staleness cap keys to the artifact's own fit-side count, and
    the live corpus now produces that same count — the two agreeing is the
    statement that the cap is current rather than carried.
    """

    predictor, sha = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    committed_json = (_ARTIFACT_DIR / "ballot-predictor.json").read_text()
    # Load -> re-serialize is the identity (byte-stable round trip).
    assert predictor.to_artifact_json() == committed_json

    cap = load_staleness_cap(_ARTIFACT_DIR)
    record = load_fit_corpus_record(_ARTIFACT_DIR)
    assert cap.weights_sha256 == sha
    assert cap.max_uses == derive_max_uses(record.fit_side_meetings) == 49_764
    assert cap.unit == "meetings"

    # The live corpus's fit side, which the cap IS keyed to.
    assert corpus_table.splits is not None
    fit_seeds = frozenset(corpus_table.splits.train) | frozenset(
        corpus_table.splits.val
    )
    live_fit_meetings = len(
        {(r.seed, r.meeting_id) for r in corpus_table.rows if r.seed in fit_seeds}
    )
    assert live_fit_meetings == record.fit_side_meetings == 348

    refit = json.loads(fit_corpus_ballot_predictor(corpus_table).to_artifact_json())
    committed = json.loads(committed_json)
    # Same keys, same feature names, same format marker, same numbers to ULP.
    assert refit.keys() == committed.keys()
    for key, committed_value in committed.items():
        refit_value = refit[key]
        if (
            isinstance(committed_value, list)
            and committed_value
            and isinstance(committed_value[0], str)
            and "0x" in committed_value[0]
        ):
            assert [float.fromhex(item) for item in refit_value] == pytest.approx(
                [float.fromhex(item) for item in committed_value],
                rel=1e-9,
                abs=1e-12,
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
    predicted-ballot calibration channel (baseline-8: 91 test meetings, 57
    ejections; the decision head still skips all but two meetings). Since the
    Task-21.17 re-ground these ARE the weights the report's numbers were
    produced by, so the reproduction is exact rather than approximate.
    """

    predictor, _ = load_ballot_predictor_artifact(_ARTIFACT_DIR)
    frozen = BallotSurrogateModel(corpus_table, predictor=predictor)
    assert corpus_table.splits is not None
    test_seeds = frozenset(corpus_table.splits.test)
    test_views = [
        view for view in build_meeting_views(corpus_table) if view.seed in test_seeds
    ]
    assert len(test_views) == 91  # was 87

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
    # The census the re-ground's own weights score on their own held-out split.
    assert top1_hits == 47  # was 46 on the baseline-6 fit
    assert predicted_ejections == 2
    assert predicted_skips == 89
    assert correct_skips == 34

    calibration = frozen.predicted_ballot_calibration(test_views)
    assert calibration.predicted_ballots == 110  # was 114
    assert calibration.predicted_skips == 406  # was 402
    # Inference from FIXED committed weights; tolerance covers libm exp variance
    # across platforms, nothing more.
    assert calibration.brier == pytest.approx(
        0.3277976536219233, abs=1e-9
    )  # was 0.3379753557131337


def test_surrogate_fidelity_reproduces_pinned_numbers(
    surrogate_report: SurrogateFidelityReport,
) -> None:
    """The held-out surrogate report reproduces the pinned deterministic numbers.

    Baseline-8 truth (Task 21.15 re-record, still scoring the baseline-6 fit):
    the meeting economy stays eject-majority (57 of the 91 scored meetings
    EJECT), the ranking channel stays strong (47/57 top-1) but the decision
    channel predicts SKIP on all but two meetings — which scores BELOW the
    always-eject constant, so ``degenerates_to_skip`` reads True and the verdict
    is NO-GO. The honest reading is in the report's §5.
    """

    report = surrogate_report
    # Integer census — exact.
    assert report.meetings_scored == 91  # was 87
    assert report.ejection_meetings == 57  # was 55
    assert report.skip_meetings == 34  # was 32
    assert report.top1_hits == 47  # was 42
    assert report.top2_hits == 54  # was 52
    assert report.predicted_ejections == 2  # was 2
    assert report.predicted_skips == 89  # was 85
    assert report.correct_skip_decisions == 34  # was 32
    assert report.correct_eject_decisions == 2  # was 2
    assert report.ejection_predicted_skips == 55  # was 53
    assert report.degenerates_to_skip is True
    assert report.ballot_rows == 289  # was 283
    assert report.honest_ceiling.ejections_total == 57  # was 55
    assert report.honest_ceiling.reachable == 47  # was 44
    # Floats — deterministic, pinned to the exact literals.
    assert report.top1 == pytest.approx(
        0.8245614035087719, abs=1e-12
    )  # was 0.7636363636363637
    assert report.top2 == pytest.approx(
        0.9473684210526315, abs=1e-12
    )  # was 0.9454545454545454
    assert report.skip_vs_eject_accuracy == pytest.approx(
        0.3956043956043956, abs=1e-12
    )  # was 0.39080459770114945
    assert report.always_eject_baseline == pytest.approx(
        0.6263736263736264, abs=1e-12
    )  # was 0.632183908045977
    assert report.brier == pytest.approx(
        0.06461725908112205, abs=1e-12
    )  # was 0.0668811387729836
    assert report.ece == pytest.approx(
        0.10778077379929225, abs=1e-12
    )  # was 0.10356921746389862
    assert report.ballot_brier == pytest.approx(
        0.12249411764705884, abs=1e-12
    )  # was 0.12890565371024734
    assert report.ballot_ece == pytest.approx(
        0.11958477508650664, abs=1e-12
    )  # was 0.0818727915194337
    assert report.honest_ceiling.max_achievable_top1 == pytest.approx(
        0.8245614035087719, abs=1e-12
    )  # was 0.8


def test_go_no_go_reproduces_the_re_measured_no_go_verdict(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """``decide_go_no_go`` on the two same-population reports pins the baseline-6 NO-GO.

    The bar is the pre-stated, owner-ratified 15.13 bar, re-MEASURED on the
    baseline-8 corpus (locked decision 4 travels): axes 1 (ceiling) and 2 (beats
    FO-6) pass, but axis 3 FAILS — the decision channel's near-all-SKIP accuracy
    (0.396) is below the eject-majority always-eject constant (0.626) — so the
    conjunction is NO-GO. Per the pre-committed mapping the surrogate ships
    DIAGNOSTIC-only and the fake-provider MeetingManager stays the training-time
    runner (the bake-off is never blocked, §5–§6).
    """

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.verdict == "NO-GO"
    assert verdict.meets_ceiling_bar is True
    assert verdict.beats_prior_baseline is True
    assert verdict.beats_always_eject is False
    assert verdict.training_time_runner == "fake-provider-meeting-manager"
    assert verdict.surrogate_role == "diagnostic-only"
    assert verdict.top1_bar == pytest.approx(
        0.618421052631579, abs=1e-12
    )  # was 0.6000000000000001


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
    assert verdict.top1_bar == pytest.approx(
        0.618421052631579, abs=1e-12
    )  # was 0.6000000000000001
    # Saturated again on the baseline-8 population: the ranking channel reaches
    # the honest ceiling exactly, so the gap closes back to zero.
    assert verdict.top1_ceiling_gap == pytest.approx(
        0.0, abs=1e-12
    )  # was 0.036363636363636376
    assert verdict.surrogate_top1 == pytest.approx(
        0.8245614035087719, abs=1e-12
    )  # was 0.7636363636363637
    assert verdict.ceiling_top1 == pytest.approx(
        0.8245614035087719, abs=1e-12
    )  # was 0.8
    # WHY the ceiling sits at 0.8246 — the overlapping channel decomposition.
    assert verdict.ceiling_flag_present == 49  # was 45
    assert verdict.ceiling_proximity_present == 52  # was 48
    assert verdict.ceiling_belief_lead == 46  # was 43
    assert verdict.ceiling_reachable == 47  # was 44


def test_axis_one_still_discriminates_a_weaker_candidate(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """The ceiling axis is saturated in headroom, NOT dead.

    The floor is 0.75 x ceiling = 0.6184 on this population. A candidate ranking
    just below it is run through the REAL ``decide_go_no_go`` and fails axis 1, so
    the axis still discriminates — which is why the split reports it rather than
    retiring it.
    """

    bar = GO_TOP1_CEILING_RATIO * surrogate_report.honest_ceiling.max_achievable_top1
    assert bar == pytest.approx(0.618421052631579, abs=1e-12)  # was 0.6000000000000001
    assert decide_go_no_go(surrogate_report, fo6_report).meets_ceiling_bar is True

    weaker = surrogate_report.model_copy(update={"top1": bar - 0.01})
    verdict = decide_go_no_go(weaker, fo6_report)
    assert verdict.meets_ceiling_bar is False
    assert verdict.ranking_verdict == "NO-GO"
    assert verdict.top1_ceiling_gap == pytest.approx(
        0.01 + (0.8245614035087719 - bar), abs=1e-12
    )  # was 0.01 + (0.8 - bar)


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
    corpus only 2 of 91 held-out meetings reach it, which is the same 2 the model
    actually ejects.
    """

    assert surrogate_report.plurality_confidence_meetings == 91  # was 87
    assert surrogate_report.decision_reachable_meetings == 2
    assert surrogate_report.decision_reachability == pytest.approx(
        2 / 91, abs=1e-12
    )  # was 2 / 87
    # Reachability is the CEILING on the decision channel: a meeting whose gate is
    # never reached cannot be ejected however the model ranks it.
    assert surrogate_report.predicted_ejections == (
        surrogate_report.decision_reachable_meetings
    )

    verdict = decide_go_no_go(surrogate_report, fo6_report)
    assert verdict.decision_reachable_meetings == 2
    assert verdict.decision_reachability == pytest.approx(
        2 / 91, abs=1e-12
    )  # was 2 / 87
    assert verdict.plurality_confidence_meetings == 91  # was 87
    assert verdict.decision_reachability_measured is True

    # A ballot-free model leaves the cell unmeasured rather than reporting zero:
    # FO-6 predicts ejections, not ballots, so it has no plurality confidence.
    assert fo6_report.plurality_confidence_meetings == 0
    assert fo6_report.decision_reachable_meetings == 0
    views = build_meeting_views(corpus_table)
    fo6 = Fo6Logistic()
    fo6.fit(views)
    assert fo6.predict(views[0]).plurality_confidence is None


def test_an_unmeasured_reachability_never_reads_as_a_measured_zero(
    surrogate_report: SurrogateFidelityReport,
    fo6_report: SurrogateFidelityReport,
) -> None:
    """0.0 reachability with zero coverage is UNMEASURED, not "gate never cleared".

    A ballot-free model reports both cells at zero. Without the coverage cell the
    verdict would publish the same 0.0 a genuinely unreachable ballot model
    produces, and a reader could not tell "the decision channel is shut" from "no
    one measured it". ``decision_reachability_measured`` is the distinction, and it
    requires COMPLETE coverage — a partial measurement would silently divide by the
    wrong denominator.
    """

    # A ballot model that published no confidences at all: same 0.0, but unmeasured.
    unmeasured = surrogate_report.model_copy(
        update={
            "decision_reachable_meetings": 0,
            "decision_reachability": 0.0,
            "plurality_confidence_meetings": 0,
        }
    )
    verdict = decide_go_no_go(unmeasured, fo6_report)
    assert verdict.decision_reachability == 0.0
    assert verdict.decision_reachability_measured is False

    # ...and a genuinely unreachable channel, fully measured, reads apart from it.
    measured_zero = surrogate_report.model_copy(
        update={"decision_reachable_meetings": 0, "decision_reachability": 0.0}
    )
    genuine = decide_go_no_go(measured_zero, fo6_report)
    assert genuine.decision_reachability == 0.0
    assert genuine.decision_reachability_measured is True

    # Partial coverage is not coverage.
    partial = surrogate_report.model_copy(
        update={"plurality_confidence_meetings": surrogate_report.meetings_scored - 1}
    )
    assert decide_go_no_go(partial, fo6_report).decision_reachability_measured is False


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
    scoring) reads the raw stored scalar; the measured divergence is 25
    held-out cells (the baseline-8 parity census). Codex review on PR #280: the
    verdict must be shown to hold on the inputs a bake-off runner actually
    serves. So: replace every held-out cell's ``belief_suspicion`` with the
    PRODUCTION-served value (the memory-augmented walk's graphs — the exact
    channel the runner reads), score the FROZEN committed artifact over the same
    test views, and assert the verdict inputs reproduce EXACTLY — same decision
    and same top-1 target on every one of the 91 meetings, so the two passing GO
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
    assert replaced == 25  # was 19

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
    assert top1_hits == 47  # was 46 on the baseline-6 fit
    assert predicted_skips == 89
    assert correct_skips == 34
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
    these are measurements of the baseline-8 corpus, not a frozen artifact's
    reproduction — which is why they re-pin here rather than waiting on the ML
    re-ground (audits/audit-phase-20-baseline-7.md §10.2).

    The head has flipped repeatedly. Baseline 5 degenerated to SKIP; baseline 6
    reverted the meeting mix to eject-majority and FO-6 went all-EJECT (96 of 96,
    exactly tying the always-eject constant at 0.625); on the baseline-7 record it
    degenerated back to SKIP on 75 of 87; on the baseline-8 record the collapse is
    TOTAL — 91 of 91 meetings called SKIP, so its decision accuracy (0.374) sits
    below the always-eject constant (0.626). The instability across four
    consecutive records is the finding: this
    head tracks the meeting mix, not the physics. Its ranking is the more stable
    half, and still the point of the comparison — 14/57 top-1, below the
    surrogate's, so axis 2 of the bar keeps passing.
    """

    report = fo6_report
    assert report.top1_hits == 14  # was 23
    assert report.ejection_meetings == 57  # was 55
    assert report.degenerates_to_skip is True
    assert report.predicted_ejections == 0  # was 12
    assert report.predicted_skips == 91  # was 75
    assert report.correct_skip_decisions == 34  # was 28
    assert report.ejection_predicted_skips == 57  # was 47
    assert report.top1 == pytest.approx(
        0.24561403508771928, abs=1e-12
    )  # was 0.41818181818181815
    assert report.top2 == pytest.approx(
        0.45614035087719296, abs=1e-12
    )  # was 0.6363636363636364
    assert report.skip_vs_eject_accuracy == pytest.approx(
        0.37362637362637363, abs=1e-12
    )  # was 0.41379310344827586
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

    The label set covers the ballot join targets, the fit-side exclusion columns
    (``ballot_coerced_skip`` / ``ballot_rewrite_labels``), the meeting outcome,
    AND the roles ground truth (``voter_role`` / ``voter_is_impostor`` /
    per-candidate ``role`` / ``is_impostor`` / ``is_ejected``) — a predict path
    that read ANY of them would diverge from the clean model. That is the
    assertion that the fidelity replay scores the recorded bytes UNFILTERED:
    the widened drop rule is fit-side only.
    """

    return row.model_copy(
        update={
            "ballot_target": "poisoned-label",
            "ballot_confidence": 0.0,
            "ballot_primary_reason_id": None,
            "ballot_coerced_skip": True,
            "ballot_rewrite_labels": ("under_gate_redirect",),
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
            "ballot_rewrite_labels": ("under_gate_redirect",),
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


def test_the_corpus_rows_the_fit_drops_are_the_whole_rewrite_class(
    corpus_table: MeetingTable,
) -> None:
    """What the fit excludes on committed bytes, counted per rule and per side.

    Two different numbers, pinned apart because they answer two different
    questions and only one of them is the fit's:

    * the whole-table CENSUS — how many recorded rows carry a rewritten target
      at all: 70 on 9p2i and 2 on 4p1i, against the 6 and 0 the narrow J2
      coercion column reads (that column stays reported, unmoved);
    * the FIT-SIDE exclusion — how many rows actually leave a fit, which reads
      the committed ``train ∪ val`` seeds only: **5 → 59** on 9p2i and 0 → 2 on
      4p1i. The 11-row difference on 9p2i is held-out test rows, which no fit
      path ever consumed, so counting them as newly excluded would overstate
      what changed.

    All four are pinned together so none can move alone, and the census test in
    ``tests/training/test_surrogate_dataset.py`` holds the per-kind split behind
    them.
    """

    four = build_meeting_table(_REPO_ROOT / "replays" / "ml_corpus" / "4p1i")

    # The whole-table census.
    assert sum(row.ballot_coerced_skip for row in corpus_table.rows) == 6  # was 7
    assert sum(_target_was_rewritten(row) for row in corpus_table.rows) == 70  # was 102
    assert sum(row.ballot_coerced_skip for row in four.rows) == 0
    assert sum(_target_was_rewritten(row) for row in four.rows) == 2

    # The fit-side exclusion: what the two fit paths actually drop.
    for table, coerced, rewritten in ((corpus_table, 5, 59), (four, 0, 2)):  # was 7, 82
        assert table.splits is not None
        fit_seeds = frozenset(table.splits.train) | frozenset(table.splits.val)
        fit_rows = [row for row in table.rows if row.seed in fit_seeds]
        assert sum(row.ballot_coerced_skip for row in fit_rows) == coerced
        assert sum(_target_was_rewritten(row) for row in fit_rows) == rewritten
    # Non-vacuous: the two readings genuinely differ on the bigger corpus.
    assert sum(_target_was_rewritten(row) for row in corpus_table.rows) > 59  # was 82


def _mark_coerced(
    table: MeetingTable, seeds: frozenset[int], *, poison_labels: bool
) -> MeetingTable:
    """Flag every row of ``seeds`` as target-rewritten; optionally poison labels."""

    def mark(row: MeetingTableRow) -> MeetingTableRow:
        if row.seed not in seeds:
            return row
        update: dict[str, object] = {
            "ballot_coerced_skip": True,
            "ballot_rewrite_labels": ("uncited_coerced",),
        }
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
    assert calib.predicted_ballots == 110  # was 105
    assert calib.predicted_skips == 406  # was 393
    assert calib.brier == pytest.approx(
        0.3277976536219233, abs=1e-12
    )  # was 0.3315434258019645
    # Distinct channel by construction.
    assert calib.brier != surrogate_report.ballot_brier


def test_every_live_feature_build_writes_the_same_masked_reporter_value() -> None:
    """Fit and serve write ONE named constant into the ``is_reporter`` slot.

    The mask is only meaningful if it is the same everywhere: a frozen weight
    vector fitted against a masked column and served an unmasked one is a
    silent mis-multiply. The three sites that build a
    :data:`~training.surrogate.ballots.BALLOT_FEATURE_NAMES` vector are pinned
    to name the shared constant, so a hard-coded literal at any of them fails
    here rather than at the next re-fit.

    ``training/surrogate/fidelity.py``'s ``FO6_FEATURE_NAMES`` is a DIFFERENT
    head — the FO-6 physical baseline — and is deliberately not in this list.
    """

    sites = (
        _REPO_ROOT / "training" / "surrogate" / "ballots.py",
        _REPO_ROOT / "training" / "surrogate" / "runner.py",
        _REPO_ROOT / "training" / "composed_runner.py",
    )
    for path in sites:
        written = re.findall(r'"is_reporter":\s*([^,\n]+)', path.read_text())
        assert written, f"{path} builds no is_reporter feature slot"
        assert set(written) == {"MASKED_IS_REPORTER"}, (str(path), written)
    assert MASKED_IS_REPORTER == 0.0
    # The layout is NOT shortened: the committed artifact serializes and
    # validates it, so the mask has to live inside a six-wide tuple.
    assert "is_reporter" in BALLOT_FEATURE_NAMES
    assert len(BALLOT_FEATURE_NAMES) == 6


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
