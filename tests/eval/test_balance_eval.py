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
from eval.balance_eval import (
    _DEFAULT_MAX_COST_USD,
    BalanceReport,
    _max_cost_usd_from_env,
    _resolve_game_budget,
    _seeded_roles,
    run_balance_eval,
    run_tournament_eval,
)
from llm.budget import GameBudget
from orchestrator.seeder import seed_initial_state
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler

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

    bucket_total = report.crew_wins + report.impostor_wins + report.tick_budget_reached
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
            seeds_used=tuple(range(10)),
        )


def test_balance_report_rejects_seeds_length_mismatch() -> None:
    with pytest.raises(ValueError, match="len\\(seeds_used\\)"):
        BalanceReport(
            games=3,
            crew_wins=1,
            impostor_wins=1,
            tick_budget_reached=1,
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
            {"id": "crew_role_leak_fixture", "room": "STORAGE", "action": None},
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


def test_run_tournament_eval_threads_roster_and_task_config(tmp_path: Path) -> None:
    """run_tournament_eval seeds the exact roster + task config it is given.

    For 7p/2i + tasks_per_crewmate=2 the harness must seed that config: each
    game's role ground truth has 7 players with exactly 2 impostors, matching an
    independent ``seed_initial_state`` call for the same seed — which also
    confirms the task count is 5 crew x 2 = 10 distinct tasks. This pins that the
    harness seeds the same config the game ran with.
    """

    seeds = (0, 1)
    report = run_tournament_eval(
        seeds=seeds,
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        num_players=7,
        num_impostors=2,
        tasks_per_crewmate=2,
        max_ticks=3,
    )

    game_map = load_canonical_map()
    assert report.seeds_used == seeds
    for game in report.games:
        assert len(game.roles) == 7
        assert sum(1 for role in game.roles.values() if role == "IMPOSTOR") == 2
        seeded = seed_initial_state(
            seed=game.seed,
            game_map=game_map,
            num_players=7,
            num_impostors=2,
            tasks_per_crewmate=2,
        )
        assert dict(game.roles) == {
            pid: player.role for pid, player in seeded.players.items()
        }
        # 5 crewmates x 2 tasks each = 10 distinct tasks for this config.
        assert len(seeded.tasks) == 5 * 2


def test_seeded_roles_threads_tasks_per_crewmate(tmp_path: Path) -> None:
    """The meeting-abort re-seed path recovers roles for the exact run config.

    ``_seeded_roles`` reconstructs the role ground truth on the abort path; it
    must accept and thread ``tasks_per_crewmate`` so the recovered roles come
    from the identical seeded setup the game ran (roles are independent of the
    task count, but the call must mirror the game's own seeding rather than rely
    on a default that could drift).
    """

    game_map = load_canonical_map()
    roles = _seeded_roles(
        seed=0,
        game_map=game_map,
        num_players=7,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    seeded = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=7,
        num_impostors=2,
        tasks_per_crewmate=2,
    )

    assert roles == {pid: player.role for pid, player in seeded.players.items()}
    assert sum(1 for role in roles.values() if role == "IMPOSTOR") == 2


def test_run_balance_eval_reuses_headless_game_outcomes(tmp_path: Path) -> None:
    """Sanity check: the tournament harness produces the same outcome a
    direct :class:`HeadlessGame` would for the same seed and config.

    Pins the "reuse :class:`HeadlessGame` — do NOT reinvent the single-
    game loop" requirement at runtime.
    """

    seed = 4
    direct_path = tmp_path / "direct.jsonl"
    # Mirror run_balance_eval's per-game wiring exactly: a fresh
    # FakeProvider-backed runner + per-game GameBudget. Without this the
    # direct game would lack a meeting runner and could diverge from the
    # tournament outcome on any seed that fires a meeting.
    direct_game = HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=direct_path,
        num_players=4,
        num_impostors=1,
        scheduler=TickScheduler(max_ticks=10),
        meeting_runner=build_default_meeting_runner(budget=GameBudget()),
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
    }
    assert expected_counts[direct_result.outcome] == 1


# R-11 CI floor: documented post-2.10 decisive-outcome guard. The 100-game
# tournament gate stays a local-only check (see ``tasks/phase-2.md`` Merge
# Criteria); this test enforces that *at least one* of a small, fixed seed
# set produces a decisive ``CREWMATES`` / ``IMPOSTORS`` outcome under the
# default agents. Probed at current HEAD with max_ticks=200:
#   seed 0  -> CREWMATES (tick 11)
#   seed 1  -> CREWMATES (tick  9)
#   seed 2  -> CREWMATES (tick  7)
#   seed 7  -> CREWMATES (tick  7)
#   seed 42 -> CREWMATES (tick  8)
# See ``audits/audit-2026-05-15-0225-reconciled.md`` §R-11 / Task 2.10's R-2
# sweep.
_R11_CI_GUARD_SEEDS = (0, 1, 2, 7, 42)
_R11_CI_GUARD_MAX_TICKS = 200


def test_default_agent_sweep_reaches_at_least_one_decisive_outcome(
    tmp_path: Path,
) -> None:
    """R-11 CI floor: after Task 2.10 the small seed sweep must yield at
    least one decisive outcome. If this test fails, the Phase 2 tactical
    fixes (R-1 / R-2 / R-3) have regressed; investigate before reverting.
    """

    game_map = load_canonical_map()
    factory = build_default_agent_factory()
    decisive = 0
    for seed in _R11_CI_GUARD_SEEDS:
        result = HeadlessGame(
            seed=seed,
            game_map=game_map,
            agent_factory=factory,
            replay_path=tmp_path / f"r-{seed}.jsonl",
            scheduler=TickScheduler(max_ticks=_R11_CI_GUARD_MAX_TICKS),
        ).run()
        if result.outcome in {"CREWMATES", "IMPOSTORS"}:
            decisive += 1
    assert decisive >= 1, (
        "R-11 regression: zero decisive outcomes across the CI guard "
        "seeds; see audits/audit-2026-05-15-0225-reconciled.md §R-11."
    )


# -- parametrized per-game budget (Task 7.7) ----------------------------------


def test_resolve_game_budget_4p_reproduces_frozen_baseline_caps() -> None:
    """The 4p preset with the knob unset == the historical fixed caps exactly.

    The frozen baseline was recorded against ``GameBudget(max_cost_usd=1.00)``
    (its token caps are the ``GameBudget`` defaults). With ``AILIBI_MAX_COST_USD``
    unset, the roster-scaled budget for 4 players must reproduce those caps
    byte-for-byte, so re-recording the baseline is unchanged.
    """

    legacy = GameBudget(max_cost_usd=1.00).snapshot()
    resolved = _resolve_game_budget(num_players=4, env={}).snapshot()

    assert resolved.max_cost_usd == legacy.max_cost_usd == 1.00
    assert resolved.max_input_tokens == legacy.max_input_tokens
    assert resolved.max_output_tokens == legacy.max_output_tokens


def test_resolve_game_budget_scales_token_caps_with_roster() -> None:
    """A 7-player meeting gets a strictly larger token ceiling than a 4-player one."""

    four = _resolve_game_budget(num_players=4, env={}).snapshot()
    seven = _resolve_game_budget(num_players=7, env={}).snapshot()

    assert seven.max_input_tokens > four.max_input_tokens
    assert seven.max_output_tokens > four.max_output_tokens
    # Linear form BASE + PER_PLAYER * num_players, with the named constants:
    #   input : 400_000 + 150_000 * 7 = 1_450_000
    #   output:  80_000 +  30_000 * 7 =   290_000
    assert seven.max_input_tokens == 1_450_000
    assert seven.max_output_tokens == 290_000


def test_max_cost_usd_unset_defaults_to_one_dollar() -> None:
    assert _max_cost_usd_from_env(env={}) == _DEFAULT_MAX_COST_USD == 1.00


def test_max_cost_usd_env_overrides_per_game_cap() -> None:
    """``AILIBI_MAX_COST_USD`` overrides only the USD cap; tokens stay roster-scaled."""

    assert _max_cost_usd_from_env(env={"AILIBI_MAX_COST_USD": "2.5"}) == 2.5

    budget = _resolve_game_budget(
        num_players=4, env={"AILIBI_MAX_COST_USD": "2.5"}
    ).snapshot()
    assert budget.max_cost_usd == 2.5
    # The override leaves the roster-scaled token caps untouched (still the 4p
    # baseline caps), proving it changes only the USD dimension.
    assert budget.max_input_tokens == 1_000_000
    assert budget.max_output_tokens == 200_000


def test_max_cost_usd_reads_process_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The unset default path reads the real process environment (``env=None``)."""

    monkeypatch.setenv("AILIBI_MAX_COST_USD", "3.0")
    assert _max_cost_usd_from_env() == 3.0
    monkeypatch.delenv("AILIBI_MAX_COST_USD", raising=False)
    assert _max_cost_usd_from_env() == _DEFAULT_MAX_COST_USD


def test_max_cost_usd_invalid_value_fails_loud() -> None:
    # A non-numeric knob is fail-loud, not silently the default (AGENTS.md).
    with pytest.raises(ValueError, match="AILIBI_MAX_COST_USD must be a number"):
        _max_cost_usd_from_env(env={"AILIBI_MAX_COST_USD": "not-a-number"})


def test_resolve_game_budget_rejects_negative_cap() -> None:
    # Range / finiteness validation is delegated to GameBudget, which rejects a
    # negative cap fail-loud.
    with pytest.raises(ValueError, match="non-negative"):
        _resolve_game_budget(num_players=4, env={"AILIBI_MAX_COST_USD": "-1"})
