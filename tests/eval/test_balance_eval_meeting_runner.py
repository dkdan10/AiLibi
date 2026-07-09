"""Additive ``meeting_runner_factory`` keyword tests for ``run_tournament_eval``.

Task 15.13 added an additive-optional ``meeting_runner_factory`` keyword to
:func:`eval.balance_eval.run_tournament_eval` (mirroring the default path's
fresh-runner-per-game construction). These tests pin four contracts:

1. the factory is invoked exactly once per seed and the produced runner is the
   one that actually drives that seed's meeting (a fresh runner per game);
2. the default path (keyword omitted vs. explicitly ``None``) is byte-identical,
   so the seam is purely additive;
3. the surrogate diagnostic tournament end-to-end
   (:func:`training.surrogate.runner.load_surrogate_runner_factory`) produces a
   standard :class:`~eval.report_schema.TournamentReport` at $0 cost, with the
   SHARED :class:`~training.surrogate.runner.SurrogateUseCounter` metering every
   simulated meeting cumulatively; and
4. the keyword is keyword-only and defaults to ``None``.

The scripted-reporter / pre-corpse-state / canned-runner helpers are copied
locally from ``tests/orchestrator/test_meeting_integration.py`` (test modules do
not import each other's fixtures).
"""

from __future__ import annotations

import inspect
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from agents.base import AgentInterface
from engine.entities import BodyState, PlayerId, Role
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import run_tournament_eval
from eval.report_schema import TournamentReport
from llm.budget import GameBudget
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import MeetingArtifacts, build_default_meeting_runner
from orchestrator.seeder import seed_initial_state
from training.surrogate.ballots import load_staleness_cap
from training.surrogate.runner import (
    SurrogateUseCounter,
    load_surrogate_runner_factory,
)

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)

# The committed frozen weights artifact (fit from replays/ml_corpus/9p2i).
_SURROGATE_ARTIFACT_DIR: Path = Path("training/artifacts/surrogate")


def _intent(data: object) -> ActionIntent:
    return _INTENT_ADAPTER.validate_python(data)


class _ScriptedAgent:
    """Test-only agent that replays a fixed intent sequence, then waits."""

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        intents: Iterable[ActionIntent] = (),
    ) -> None:
        self._agent_id = agent_id
        self._intents = list(intents)
        self._default = _intent({"type": "wait", "actor": agent_id, "payload": {}})
        self._cursor = 0

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if self._cursor < len(self._intents):
            intent = self._intents[self._cursor]
            self._cursor += 1
            return intent
        return self._default


class _WaitAgent:
    """Test-only agent that always emits a ``wait`` intent."""

    def __init__(self, *, agent_id: PlayerId) -> None:
        self._agent_id = agent_id

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return _intent({"type": "wait", "actor": self._agent_id, "payload": {}})


def _wait_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
    return _WaitAgent(agent_id=agent_id)


@dataclass
class _CannedSkipRunner:
    """Test :class:`~orchestrator.game.MeetingRunner` that always SKIPs.

    Records every dispatch it sees on ``received`` so a test can assert the
    produced runner is the one that actually drove that game's meeting, and
    carries empty LLM metadata (``llm_calls=()``).
    """

    received: list[tuple[str, MeetingTrigger]] = field(default_factory=list)

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        self.received.append((meeting_id, trigger))
        result = _skip_result(meeting_id, trigger)
        return MeetingArtifacts(result=result, llm_calls=(), prompt_versions={})


def _skip_result(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
    return MeetingResult(
        meeting_id=meeting_id,
        triggered_by=trigger.triggered_by,
        trigger_tick=trigger.trigger_tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        contradictions=(),
        transcript=MeetingTranscript(),
    )


def _report_body_factory(
    body_id: str,
) -> Callable[[PlayerId, Role], _ScriptedAgent]:
    """Agent factory where ``p-1`` reports ``body_id`` on tick 1; others wait."""

    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-1":
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "report",
                            "actor": "p-1",
                            "payload": {"body_id": body_id},
                        }
                    )
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    return factory


def _seed_meeting_setup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    game_map: Map,
    seed: int = 2026,
) -> str:
    """Pre-seed a world state with a corpse so the report action validates.

    Patches ``seed_initial_state`` on BOTH modules the tournament path reads it
    through: ``orchestrator.game`` (the live game) and ``eval.balance_eval`` (the
    Task 8.17 kill-gift accounting walk, which re-seeds and verifies every
    reconstructed ``state_hash`` against the recording). Patching only the game
    would make the walk re-seed a corpse-free state and diverge fail-loud, so
    both bindings must resolve to the same pre-corpse state.
    """

    initial = seed_initial_state(seed=seed, game_map=game_map, num_players=4)
    body_id = "body-p-2-1"
    body = BodyState(
        id=body_id,
        player_id="p-2",
        room=game_map.spawn.room,
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state_with_body = replace(
        initial,
        bodies={body_id: body},
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
        },
    )

    def _stub(
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
    ) -> WorldState:
        return state_with_body

    monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub)
    monkeypatch.setattr("eval.balance_eval.seed_initial_state", _stub)
    return body_id


def _total_meetings(report: TournamentReport) -> int:
    return sum(len(game.meetings) for game in report.games)


# ---------------------------------------------------------------------------
# 1. Factory invoked once per seed; produced runner installed.
# ---------------------------------------------------------------------------


def test_meeting_runner_factory_invoked_once_and_produced_runner_installed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One seed → factory called once; its runner drives the game's one meeting."""

    game_map = load_canonical_map()
    body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)

    runners: list[_CannedSkipRunner] = []

    def factory() -> _CannedSkipRunner:
        runner = _CannedSkipRunner()
        runners.append(runner)
        return runner

    report = run_tournament_eval(
        seeds=(2026,),
        output_dir=tmp_path,
        agent_factory=_report_body_factory(body_id),
        max_ticks=8,
        meeting_runner_factory=factory,
    )

    # Factory invoked exactly once per seed.
    assert len(runners) == 1
    # The one constructed runner received exactly the meetings the report shows.
    assert _total_meetings(report) == 1
    assert len(runners[0].received) == _total_meetings(report) == 1
    # The report's meeting outcome is the canned SKIPPED result.
    (game,) = report.games
    (meeting,) = game.meetings
    assert meeting.outcome == "SKIPPED"


def test_meeting_runner_factory_fresh_runner_per_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Two seeds → factory called twice, each game gets a FRESH runner instance."""

    game_map = load_canonical_map()
    body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)

    runners: list[_CannedSkipRunner] = []

    def factory() -> _CannedSkipRunner:
        runner = _CannedSkipRunner()
        runners.append(runner)
        return runner

    report = run_tournament_eval(
        seeds=(2026, 2027),
        output_dir=tmp_path,
        agent_factory=_report_body_factory(body_id),
        max_ticks=8,
        meeting_runner_factory=factory,
    )

    # Called exactly twice (once per seed) and each is a distinct instance,
    # mirroring the fresh-runner-per-game default.
    assert len(runners) == 2
    assert len({id(runner) for runner in runners}) == 2
    # Each fresh runner drove exactly its own game's single meeting.
    assert _total_meetings(report) == 2
    for runner in runners:
        assert len(runner.received) == 1


# ---------------------------------------------------------------------------
# 2. Default path unchanged: the default runner is still built per seed, and
#    a supplied factory bypasses that construction entirely.
# ---------------------------------------------------------------------------


def test_default_path_still_builds_default_runner_per_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keyword omitted ⇒ ``build_default_meeting_runner`` runs once per seed.

    Spies on the default construction inside ``eval.balance_eval``: with the
    keyword omitted the default branch must build one fresh default runner per
    seed with the resolved per-game budget (the pre-15.13 behavior); with a
    factory supplied the default construction must never run — the factory
    bypasses it. (Omitted-vs-``None`` is the same Python invocation, so the
    additive guarantee is that this ELSE branch is byte-identical to the old
    inline construction — which the untouched pre-existing balance-eval tests
    keep pinned end-to-end.)
    """

    budgets: list[GameBudget | None] = []

    def spy(*, budget: GameBudget | None = None) -> object:
        budgets.append(budget)
        return build_default_meeting_runner(budget=budget)

    monkeypatch.setattr("eval.balance_eval.build_default_meeting_runner", spy)

    run_tournament_eval(
        seeds=(0, 1),
        output_dir=tmp_path / "default",
        agent_factory=_wait_factory,
        max_ticks=3,
    )
    # One fresh default runner per seed, each with a real per-game budget.
    assert len(budgets) == 2
    assert all(budget is not None for budget in budgets)

    budgets.clear()
    run_tournament_eval(
        seeds=(0, 1),
        output_dir=tmp_path / "factory",
        agent_factory=_wait_factory,
        max_ticks=3,
        meeting_runner_factory=_CannedSkipRunner,
    )
    # The supplied factory bypasses the default construction entirely.
    assert budgets == []


# ---------------------------------------------------------------------------
# 3. Surrogate diagnostic tournament end-to-end (the 15.13 seam).
# ---------------------------------------------------------------------------


def test_surrogate_runner_factory_drives_zero_cost_diagnostic_tournament(
    tmp_path: Path,
) -> None:
    """The committed surrogate factory produces a standard $0 TournamentReport.

    Default agent factory + default roster (4p/1i); seeds 2 and 5 each fire one
    meeting organically and end CREWMATES. Every simulated meeting is metered
    against the SHARED counter cumulatively (a fresh runner per game never
    resets it), and every meeting carries empty LLM metadata at $0.
    """

    counter = SurrogateUseCounter(load_staleness_cap(_SURROGATE_ARTIFACT_DIR))
    factory = load_surrogate_runner_factory(
        _SURROGATE_ARTIFACT_DIR, use_counter=counter
    )

    report = run_tournament_eval(
        seeds=(2, 5),
        output_dir=tmp_path,
        meeting_runner_factory=factory,
    )

    assert isinstance(report, TournamentReport)
    assert len(report.games) == 2
    for game in report.games:
        assert len(game.meetings) >= 1
        assert game.winner is not None
        assert game.cost.total_cost_usd == 0.0
        for meeting in game.meetings:
            assert meeting.llm_calls == ()

    # The shared counter metered exactly one use per simulated meeting,
    # cumulative across the per-game runner constructions.
    assert counter.uses == _total_meetings(report)


# ---------------------------------------------------------------------------
# 4. Keyword is keyword-only and optional (default None).
# ---------------------------------------------------------------------------


def test_meeting_runner_factory_is_keyword_only(tmp_path: Path) -> None:
    """Passing the factory positionally is a ``TypeError`` (all params kw-only)."""

    run_positionally: Callable[..., object] = run_tournament_eval
    with pytest.raises(TypeError):
        run_positionally((2,), tmp_path)


def test_meeting_runner_factory_signature_default_is_none() -> None:
    """The signature default is ``None`` and the parameter is KEYWORD_ONLY."""

    param = inspect.signature(run_tournament_eval).parameters["meeting_runner_factory"]
    assert param.default is None
    assert param.kind is inspect.Parameter.KEYWORD_ONLY
