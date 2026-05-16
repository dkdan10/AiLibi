from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import TypeAlias

import pytest

from pydantic import TypeAdapter

from agents.base import AgentInterface
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from eval.balance_eval import BalanceReport, run_balance_eval
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import build_default_agent_factory

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)

# Role-bearing substrings that must never appear in an observation packet
# *value*; the equivalent scanner in ``eval/leak_test.py`` runs against
# scripted fixtures, this duplicate guards live tournament games. Keep the
# two lists in lockstep when a role label changes.
_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")
_ALLOWED_VALUE_PATHS = frozenset({("self_state", "role")})
_FORBIDDEN_RECURSIVE_FIELD_NAMES = frozenset(
    {"killed_by", "kill_attribution", "player_id"}
)
_ALLOWED_RECURSIVE_FIELD_PATHS = frozenset({("self_state", "role")})

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonPathPart: TypeAlias = str | int
JsonPath: TypeAlias = tuple[JsonPathPart, ...]


class _WaitAgent:
    """Test-only agent that always emits a `wait` intent.

    Lets the test drive the orchestrator without invoking the real
    tactical policies, so unit tests stay fast and deterministic.
    """

    def __init__(self, *, agent_id: PlayerId) -> None:
        self._agent_id = agent_id

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return _INTENT_ADAPTER.validate_python(
            {"type": "wait", "actor": self._agent_id, "payload": {}}
        )


def _wait_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
    return _WaitAgent(agent_id=agent_id)


def _walk_json(
    value: JsonValue, path: JsonPath = ()
) -> Iterator[tuple[JsonPath, JsonValue]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_json(child, (*path, key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk_json(child, (*path, index))


def _format_json_path(path: JsonPath) -> str:
    formatted = "$"
    for part in path:
        formatted = (
            f"{formatted}[{part}]" if isinstance(part, int) else f"{formatted}.{part}"
        )
    return formatted


def _assert_packet_has_no_leaks(packet_dump: JsonValue) -> None:
    """Walk one audit-log packet dump and flag any role-bearing leak.

    Mirrors the scanners in ``eval/leak_test.py``: field-name leaks
    (``role`` outside ``self_state.role``, ``killed_by``,
    ``kill_attribution``, ``player_id``) and value leaks (any string
    containing ``impostor``, ``crewmate`` or ``crew`` outside the
    allowed ``self_state.role`` slot).
    """

    for path, value in _walk_json(packet_dump):
        if path:
            field_name = path[-1]
            if isinstance(field_name, str):
                if field_name == "role" and path not in _ALLOWED_RECURSIVE_FIELD_PATHS:
                    raise AssertionError(
                        f"hidden field 'role' leaked at {_format_json_path(path)}"
                    )
                if field_name in _FORBIDDEN_RECURSIVE_FIELD_NAMES:
                    raise AssertionError(
                        f"hidden field {field_name!r} leaked at "
                        f"{_format_json_path(path)}"
                    )
        if isinstance(value, str) and path not in _ALLOWED_VALUE_PATHS:
            lowered = value.lower()
            for forbidden in _FORBIDDEN_VALUE_SUBSTRINGS:
                if forbidden in lowered:
                    raise AssertionError(
                        f"role-bearing value {value!r} leaked at "
                        f"{_format_json_path(path)}"
                    )


def _audit_log_paths(output_dir: Path, seeds: Iterable[int]) -> list[Path]:
    return [output_dir / f"replay-seed-{seed}.audit.jsonl" for seed in seeds]


def test_run_balance_eval_returns_report_with_seeds_used(tmp_path: Path) -> None:
    seeds = (0, 1, 2)
    report = run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        max_ticks=3,
    )

    assert isinstance(report, BalanceReport)
    assert report.games == 3
    assert report.seeds_used == seeds


def test_run_balance_eval_bucket_totals_match_games(tmp_path: Path) -> None:
    seeds = tuple(range(5))
    report = run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        max_ticks=3,
    )

    bucket_total = (
        report.crew_wins
        + report.impostor_wins
        + report.tick_budget_reached
        + report.meeting_phase_reached
    )
    assert bucket_total == report.games == len(seeds)


def test_run_balance_eval_classifies_tick_budget_reached(tmp_path: Path) -> None:
    """A tiny tick budget + wait-only agents → every game is TICK_BUDGET_REACHED.

    Pins the contract that non-decisive outcomes are routed to their own
    bucket and never coerced into the CREWMATES or IMPOSTORS totals.
    """

    seeds = (0, 1)
    report = run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        max_ticks=1,
    )

    assert report.tick_budget_reached == 2
    assert report.crew_wins == 0
    assert report.impostor_wins == 0
    assert report.meeting_phase_reached == 0


def test_run_balance_eval_writes_one_replay_per_seed(tmp_path: Path) -> None:
    seeds = (7, 13, 21)
    run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        max_ticks=2,
    )

    for seed in seeds:
        assert (tmp_path / f"replay-seed-{seed}.jsonl").exists()
        assert (tmp_path / f"replay-seed-{seed}.audit.jsonl").exists()


def test_run_balance_eval_rejects_empty_seeds(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="non-empty"):
        run_balance_eval(seeds=(), output_dir=tmp_path)


def test_run_balance_eval_rejects_duplicate_seeds(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unique"):
        run_balance_eval(seeds=(1, 2, 1), output_dir=tmp_path)


def test_balance_report_rejects_inconsistent_bucket_sum() -> None:
    with pytest.raises(ValueError, match="must sum to games"):
        BalanceReport(
            games=10,
            crew_wins=3,
            impostor_wins=3,
            tick_budget_reached=3,
            meeting_phase_reached=0,
            seeds_used=tuple(range(10)),
        )


def test_balance_report_rejects_seeds_length_mismatch() -> None:
    with pytest.raises(ValueError, match="len\\(seeds_used\\)"):
        BalanceReport(
            games=3,
            crew_wins=1,
            impostor_wins=1,
            tick_budget_reached=1,
            meeting_phase_reached=0,
            seeds_used=(0, 1),
        )


def test_tournament_audit_logs_have_no_role_leaks(tmp_path: Path) -> None:
    """Every observation packet emitted by the tournament must pass leak scans.

    This is the "leak test still passes across all tournament games"
    requirement: a small tournament under the real tactical agents writes
    audit logs and the test walks each packet asserting no role-bearing
    substrings appear outside ``self_state.role``.
    """

    seeds = (0, 1, 2)
    report = run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=build_default_agent_factory(),
        num_players=5,
        num_impostors=2,
        max_ticks=80,
    )
    assert report.games == len(seeds)

    audit_paths = _audit_log_paths(tmp_path, seeds)
    total_packets = 0
    for audit_path in audit_paths:
        assert audit_path.exists()
        for raw_line in audit_path.read_text(encoding="utf-8").splitlines():
            if not raw_line:
                continue
            packet_dump: JsonValue = json.loads(raw_line)
            _assert_packet_has_no_leaks(packet_dump)
            total_packets += 1
    assert total_packets > 0


def test_leak_scanner_trips_on_planted_visible_player_id() -> None:
    planted: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "visible_players": [
            {"id": "impostor-1", "room": "STORAGE", "action": None},
        ],
    }

    with pytest.raises(AssertionError, match=r"\$\.visible_players\[0\]\.id"):
        _assert_packet_has_no_leaks(planted)


def test_leak_scanner_allows_self_state_role() -> None:
    legitimate: JsonValue = {
        "self_state": {"role": "CREWMATE"},
        "visible_players": [
            {"id": "p-1", "room": "STORAGE", "action": None},
        ],
    }

    _assert_packet_has_no_leaks(legitimate)


def test_canonical_balance_keeps_both_sides_alive(tmp_path: Path) -> None:
    """Fast canary for Task 2.10.5 Phase 2 tournament balance (DESIGN.md §3.5).

    A 10-game tournament against the canonical config with the default
    agents must produce at least one ``CREWMATES`` and at least one
    ``IMPOSTORS`` decisive outcome. This is a small-N regression test
    on the canonical ``kill_cooldown_ticks`` tuning, not the full
    100-game merge gate — the merge gate lives in
    ``tasks/phase-2.md`` Merge Criteria and is exercised by
    ``scripts/run_tournament.py``.
    """

    seeds = tuple(range(10))
    report = run_balance_eval(
        seeds=seeds,
        output_dir=tmp_path,
        max_ticks=1000,
    )

    assert report.crew_wins > 0
    assert report.impostor_wins > 0


def test_run_balance_eval_reuses_headless_game_outcomes(tmp_path: Path) -> None:
    """Sanity check: the tournament harness produces the same outcome a
    direct :class:`HeadlessGame` would for the same seed and config.

    Pins the "reuse :class:`HeadlessGame` — do NOT reinvent the single-
    game loop" requirement at runtime.
    """

    from orchestrator.game import HeadlessGame
    from orchestrator.scheduler import TickScheduler

    seed = 4
    direct_path = tmp_path / "direct.jsonl"
    direct_game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=direct_path,
        num_players=4,
        num_impostors=1,
        scheduler=TickScheduler(max_ticks=10),
    )
    direct_result = direct_game.run()

    tournament_dir = tmp_path / "tournament"
    report = run_balance_eval(
        seeds=(seed,),
        output_dir=tournament_dir,
        max_ticks=10,
    )

    expected_counts = {
        "CREWMATES": report.crew_wins,
        "IMPOSTORS": report.impostor_wins,
        "TICK_BUDGET_REACHED": report.tick_budget_reached,
        "MEETING_PHASE_REACHED": report.meeting_phase_reached,
    }
    assert expected_counts[direct_result.outcome] == 1
