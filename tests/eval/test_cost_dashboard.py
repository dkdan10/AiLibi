"""Unit tests for the Phase 5 cost-dashboard metric (DESIGN.md §10.4, §11.3).

Fixtures are built by instantiating the ``eval.report_schema`` models directly
rather than by running a tournament: this metric is a pure fold over the
already-aggregated :class:`~eval.report_schema.GameCostSummary`, so the tests
pin the cost arithmetic, the per-``(template, version)`` keying, the
no-double-count invariant for failed calls, the per-model roll-up, and
partial-replay robustness without any orchestrator or LLM dependency.

The metric reads the pre-aggregated per-game ``cost`` summary, NOT the meetings'
``llm_calls``, so the cost fixtures leave ``meetings`` empty and set ``cost``
directly: that is the level of abstraction this metric consumes (the Task 5.6
loader is what populates ``cost`` from the raw calls via
``orchestrator.replay.compute_cost_usd``).

Derived float values (sums, means, deltas) are compared with ``pytest.approx``
because IEEE addition is not exact (``0.1 + 0.2 != 0.3``); pass-through values a
single game contributes unchanged are compared exactly.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.cost_dashboard import (
    CostDashboard,
    PromptVersionCost,
    compute_cost_dashboard,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    TournamentReport,
)
from meetings.schemas import PlayerId
from orchestrator.replay import FailedCallReplayEntry

# A minimal 2-player roster; the cost metric never reads roles, but GameReport
# requires the post-game ground-truth map, so supply a coherent one.
_ROLES: Mapping[PlayerId, Role] = {"p-0": "CREWMATE", "p-1": "IMPOSTOR"}


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _cost(
    *,
    total_cost_usd: float,
    by_model: Mapping[str, float],
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> GameCostSummary:
    return GameCostSummary(
        total_cost_usd=total_cost_usd,
        total_input_tokens=input_tokens,
        total_output_tokens=output_tokens,
        by_model=by_model,
    )


def _failed_call(*, cost: float) -> FailedCallReplayEntry:
    return FailedCallReplayEntry(
        game_id="g",
        meeting_id="m",
        tick=70,
        model="claude-sonnet",
        prompt_length=4096,
        raw_response='{"target": "p-9"',  # truncated / invalid JSON
        input_tokens=1500,
        output_tokens=40,
        cost_usd=cost,
        error_type="ValidationError",
        error_message="target references unknown player",
    )


def _game(
    *,
    game_id: str,
    seed: int,
    cost: GameCostSummary,
    prompt_versions: Mapping[str, str],
    failed_calls: tuple[FailedCallReplayEntry, ...] = (),
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner="CREWMATES",
        reason="impostor ejected",
        final_tick=50,
        roles=_ROLES,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=(),
        failed_calls=failed_calls,
        prompt_versions=prompt_versions,
        cost=cost,
    )


def _tournament(*games: GameReport) -> TournamentReport:
    return TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=games,
        seeds_used=tuple(g.seed for g in games),
    )


# ---------------------------------------------------------------------------
# Per-prompt-version keying + summation (constructibility fixture)
# ---------------------------------------------------------------------------


def test_two_prompt_versions_keying_summation_and_overlap() -> None:
    """Constructibility fixture: two versions of one template across games.

    NOTE: a *real* single tournament run carries ONE prompt-version set across
    every game (templates load once per run), so two versions in one report only
    arises when constructed by hand — that is exactly what this test does to pin
    the per-``(template, version)`` keying and summation. It also pins the
    overlap property: because every game's full cost is attributed under EACH
    template it ran, the per-version totals do NOT partition the tournament
    total.

    * game A (cost 0.10): meeting_v=vA, trigger_v=t1
    * game B (cost 0.20): meeting_v=vB, trigger_v=t1

    => (meeting_v, vA): 0.10 / 1 game; (meeting_v, vB): 0.20 / 1 game;
       (trigger_v, t1): 0.30 / 2 games  (both games ran trigger_v=t1).
    """

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.10, by_model={"claude-sonnet": 0.10}),
            prompt_versions={"meeting_v": "vA", "trigger_v": "t1"},
        ),
        _game(
            game_id="game-b",
            seed=2,
            cost=_cost(total_cost_usd=0.20, by_model={"claude-sonnet": 0.20}),
            prompt_versions={"meeting_v": "vB", "trigger_v": "t1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.total_cost_usd == pytest.approx(0.30)

    # Deterministic ordering: sorted by (template_name, version).
    assert tuple(
        (pv.template_name, pv.version) for pv in dashboard.per_prompt_version
    ) == (
        ("meeting_v", "vA"),
        ("meeting_v", "vB"),
        ("trigger_v", "t1"),
    )

    by_key = {(pv.template_name, pv.version): pv for pv in dashboard.per_prompt_version}
    assert by_key[("meeting_v", "vA")].total_cost_usd == 0.10
    assert by_key[("meeting_v", "vA")].game_count == 1
    assert by_key[("meeting_v", "vB")].total_cost_usd == 0.20
    assert by_key[("meeting_v", "vB")].game_count == 1
    # trigger_v=t1 ran in BOTH games, so it accumulates the full cost of each.
    assert by_key[("trigger_v", "t1")].total_cost_usd == pytest.approx(0.30)
    assert by_key[("trigger_v", "t1")].game_count == 2

    # Overlap, not a partition: summing per-version totals over-counts the
    # tournament total (0.10 + 0.20 + 0.30 == 0.60 != 0.30). Documented invariant.
    summed = sum(pv.total_cost_usd for pv in dashboard.per_prompt_version)
    assert summed == pytest.approx(0.60)
    assert summed != dashboard.total_cost_usd


# ---------------------------------------------------------------------------
# Single-version report collapses to one key == total cost
# ---------------------------------------------------------------------------


def test_single_version_collapses_to_one_key_equal_to_total() -> None:
    """The realistic single-run shape: one template/version across all games.

    With a single template held constant, the breakdown collapses to one key
    whose total equals the whole tournament cost and whose game_count is every
    game — the within-report breakdown carries no comparative signal, which is
    why version-vs-version is a cross-report comparison (Task 5.8).
    """

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.10, by_model={"claude-sonnet": 0.10}),
            prompt_versions={"meeting_v": "v1"},
        ),
        _game(
            game_id="game-b",
            seed=2,
            cost=_cost(total_cost_usd=0.15, by_model={"claude-sonnet": 0.15}),
            prompt_versions={"meeting_v": "v1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.total_cost_usd == pytest.approx(0.25)
    assert len(dashboard.per_prompt_version) == 1
    only = dashboard.per_prompt_version[0]
    assert (only.template_name, only.version) == ("meeting_v", "v1")
    # The lone key accumulates identically to the total, so it matches exactly.
    assert only.total_cost_usd == dashboard.total_cost_usd
    assert only.game_count == 2


# ---------------------------------------------------------------------------
# Failed-call spend is NOT double-counted
# ---------------------------------------------------------------------------


def test_failed_calls_are_not_double_counted() -> None:
    """``total_cost_usd`` already includes failed-call spend; do not re-add it.

    The game's authoritative ``total_cost_usd`` (0.05) already folds in the
    0.02 the aborted meeting burned (that is what
    ``orchestrator.replay.compute_cost_usd`` does loader-side). The dashboard
    must read 0.05 and never 0.07.
    """

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.05, by_model={"claude-sonnet": 0.05}),
            prompt_versions={"meeting_v": "v1"},
            failed_calls=(_failed_call(cost=0.02),),
        ),
    )

    dashboard = compute_cost_dashboard(report)

    # Reads total_cost_usd as-is; the 0.02 failed-call cost is NOT added on top.
    assert dashboard.total_cost_usd == 0.05
    assert dashboard.total_cost_usd != 0.07
    # The single game's per-version total is likewise the authoritative total.
    assert dashboard.per_prompt_version[0].total_cost_usd == 0.05


# ---------------------------------------------------------------------------
# Per-model roll-up across games (mixed-tier tournament)
# ---------------------------------------------------------------------------


def test_per_model_rollup_aggregates_by_model_across_games() -> None:
    """``by_model`` sums each model's spend across every game, sorted by model id."""

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(
                total_cost_usd=0.030,
                by_model={"claude-sonnet": 0.024, "claude-haiku": 0.006},
            ),
            prompt_versions={"meeting_v": "v1"},
        ),
        _game(
            game_id="game-b",
            seed=2,
            cost=_cost(
                total_cost_usd=0.014,
                by_model={"claude-haiku": 0.004, "claude-opus": 0.010},
            ),
            prompt_versions={"meeting_v": "v1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.by_model == pytest.approx(
        {
            "claude-haiku": 0.010,  # 0.006 + 0.004, summed across both games
            "claude-opus": 0.010,
            "claude-sonnet": 0.024,
        }
    )
    # Deterministic key ordering (sorted model ids).
    assert list(dashboard.by_model) == [
        "claude-haiku",
        "claude-opus",
        "claude-sonnet",
    ]
    # Per-model roll-up is auditable against the tournament total.
    assert dashboard.total_cost_usd == pytest.approx(0.044)
    assert sum(dashboard.by_model.values()) == pytest.approx(0.044)


# ---------------------------------------------------------------------------
# Mean cost-per-game + token totals
# ---------------------------------------------------------------------------


def test_mean_cost_per_game_and_token_totals() -> None:
    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(
                total_cost_usd=0.10,
                by_model={"claude-sonnet": 0.10},
                input_tokens=1000,
                output_tokens=200,
            ),
            prompt_versions={"meeting_v": "v1"},
        ),
        _game(
            game_id="game-b",
            seed=2,
            cost=_cost(
                total_cost_usd=0.30,
                by_model={"claude-sonnet": 0.30},
                input_tokens=3000,
                output_tokens=400,
            ),
            prompt_versions={"meeting_v": "v1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.game_count == 2
    assert dashboard.total_cost_usd == pytest.approx(0.40)
    assert dashboard.mean_cost_per_game == pytest.approx(0.20)
    assert dashboard.total_input_tokens == 4000
    assert dashboard.total_output_tokens == 600


# ---------------------------------------------------------------------------
# Partial-replay robustness
# ---------------------------------------------------------------------------


def test_empty_tournament_is_well_defined() -> None:
    """A zero-game report: no division-by-zero, no NaN, empty breakdowns."""

    dashboard = compute_cost_dashboard(
        TournamentReport(format_version=CURRENT_FORMAT_VERSION, games=(), seeds_used=())
    )

    assert dashboard.game_count == 0
    assert dashboard.total_cost_usd == 0.0
    assert dashboard.mean_cost_per_game == 0.0  # not a ZeroDivisionError / NaN
    assert dashboard.total_input_tokens == 0
    assert dashboard.total_output_tokens == 0
    assert dashboard.by_model == {}
    assert dashboard.per_prompt_version == ()


def test_zero_cost_zero_meeting_game_is_well_defined() -> None:
    """A game that never reached a meeting: zero cost, empty by_model."""

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.0, by_model={}),
            prompt_versions={"meeting_v": "v1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.game_count == 1
    assert dashboard.total_cost_usd == 0.0
    assert dashboard.mean_cost_per_game == 0.0
    assert dashboard.by_model == {}
    # The prompt version is still recorded, with a zero total.
    assert len(dashboard.per_prompt_version) == 1
    assert dashboard.per_prompt_version[0].total_cost_usd == 0.0
    assert dashboard.per_prompt_version[0].game_count == 1


def test_empty_prompt_versions_contributes_no_breakdown_key() -> None:
    """An empty ``prompt_versions`` yields no breakdown key, but cost still counts."""

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.08, by_model={"claude-sonnet": 0.08}),
            prompt_versions={},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    # The cost is in the total and the per-model roll-up, but there is no
    # (template, version) to attribute it to, so the breakdown is empty.
    assert dashboard.total_cost_usd == 0.08
    assert dashboard.by_model == {"claude-sonnet": 0.08}
    assert dashboard.per_prompt_version == ()


def test_single_game_tournament_mean_equals_that_game() -> None:
    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.17, by_model={"claude-sonnet": 0.17}),
            prompt_versions={"meeting_v": "v1"},
        ),
    )

    dashboard = compute_cost_dashboard(report)

    assert dashboard.game_count == 1
    assert dashboard.total_cost_usd == 0.17
    assert dashboard.mean_cost_per_game == 0.17


# ---------------------------------------------------------------------------
# Result model is a frozen, JSON-round-trippable value object
# ---------------------------------------------------------------------------


def test_dashboard_round_trips_through_json() -> None:
    """The dashboard is consumed by Task 5.6 JSON output / Task 5.7 frontend."""

    report = _tournament(
        _game(
            game_id="game-a",
            seed=1,
            cost=_cost(total_cost_usd=0.10, by_model={"claude-sonnet": 0.10}),
            prompt_versions={"meeting_v": "vA", "trigger_v": "t1"},
        ),
        _game(
            game_id="game-b",
            seed=2,
            cost=_cost(total_cost_usd=0.20, by_model={"claude-haiku": 0.20}),
            prompt_versions={"meeting_v": "vB", "trigger_v": "t1"},
        ),
    )
    dashboard = compute_cost_dashboard(report)

    dumped = dashboard.model_dump(mode="json")
    restored = CostDashboard.model_validate(dumped)

    assert restored == dashboard
    assert restored.model_dump(mode="json") == dumped


def test_dashboard_is_frozen() -> None:
    dashboard = compute_cost_dashboard(
        _tournament(
            _game(
                game_id="game-a",
                seed=1,
                cost=_cost(total_cost_usd=0.10, by_model={"claude-sonnet": 0.10}),
                prompt_versions={"meeting_v": "v1"},
            ),
        )
    )

    with pytest.raises(ValidationError):
        dashboard.total_cost_usd = 0.0


def test_two_dashboards_compare_cleanly_by_prompt_version_key() -> None:
    """Backs the cross-report comparison contract (Task 5.8 computes the delta).

    Two runs of the SAME template at different versions each collapse to one key
    equal to that run's total; a consumer matches the two dashboards by
    ``(template_name, version)`` and reads the cost delta. This test demonstrates
    the model is cleanly comparable; it does not implement the delta (Task 5.8).
    """

    run_a = compute_cost_dashboard(
        _tournament(
            _game(
                game_id="a0",
                seed=1,
                cost=_cost(total_cost_usd=0.20, by_model={"claude-sonnet": 0.20}),
                prompt_versions={"meeting_v": "v1"},
            ),
        )
    )
    run_b = compute_cost_dashboard(
        _tournament(
            _game(
                game_id="b0",
                seed=1,
                cost=_cost(total_cost_usd=0.26, by_model={"claude-sonnet": 0.26}),
                prompt_versions={"meeting_v": "v2"},
            ),
        )
    )

    a_by_key = {(pv.template_name, pv.version): pv for pv in run_a.per_prompt_version}
    b_by_key = {(pv.template_name, pv.version): pv for pv in run_b.per_prompt_version}

    assert a_by_key[("meeting_v", "v1")].total_cost_usd == 0.20
    assert b_by_key[("meeting_v", "v2")].total_cost_usd == 0.26
    # The cross-run cost delta a consumer (Task 5.8) would compute.
    assert run_b.total_cost_usd - run_a.total_cost_usd == pytest.approx(0.06)


def test_per_prompt_version_entries_are_frozen() -> None:
    dashboard = compute_cost_dashboard(
        _tournament(
            _game(
                game_id="game-a",
                seed=1,
                cost=_cost(total_cost_usd=0.10, by_model={"claude-sonnet": 0.10}),
                prompt_versions={"meeting_v": "v1"},
            ),
        )
    )
    entry: PromptVersionCost = dashboard.per_prompt_version[0]

    with pytest.raises(ValidationError):
        entry.total_cost_usd = 0.0
