"""Cost-dashboard metric over the typed tournament report (DESIGN.md §10.4, §11.3).

A pure analyzer that folds an :class:`eval.report_schema.TournamentReport` into
the cost-dashboard data DESIGN.md §10.4 frames around the ~$0.20/game target:
total tournament spend, mean cost-per-game, a per-model roll-up, and a
cost-per-prompt-version breakdown so a prompt-template change's cost impact is
legible alongside its quality impact (the §11.3 behavioral metrics, Tasks
5.2-5.4). This is the cost half of the Phase 5 close loop — a prompt-template
change should show both a metric delta *and* a cost delta here.

The metric works over the already-aggregated report, never raw JSONL: it does
not re-read replay files (:func:`orchestrator.replay.compute_cost_usd` is the
file-level reducer that the Task 5.6 loader uses to populate the per-game
:class:`~eval.report_schema.GameCostSummary`; this module trusts that result).

Four semantic decisions are pinned here; each is load-bearing and tested:

* **No double-count.** :attr:`GameCostSummary.total_cost_usd` is the
  authoritative complete per-game spend. It ALREADY includes meeting-aborting
  failed-call cost, because the canonical reducer
  :func:`orchestrator.replay.compute_cost_usd` sums meeting ``llm_calls`` cost
  PLUS every ``failed_call`` cost. So this metric reads ``total_cost_usd`` and
  never adds ``sum(fc.cost_usd for fc in game.failed_calls)`` on top — doing so
  would charge the crashed-meeting spend twice.

* **Per-version totals OVERLAP — they are not a partition.** A game runs
  several prompt templates at once (e.g. a meeting template and a trigger
  template). The full game cost is attributed once under EACH
  ``(template_name, version)`` present in ``GameReport.prompt_versions`` — it is
  NOT split across templates. Consequently the per-version ``total_cost_usd``
  values overlap: summing them across versions does NOT recover the tournament
  total and must not be presented as if it does.

* **Single-run collapse → the comparison is cross-report.** Within one
  tournament run ``prompt_versions`` is constant across all games (one template
  set is loaded per run), so every ``(template, version)`` key appears in every
  game and each per-version total equals the tournament total. The breakdown's
  comparative value (version A vs version B) is therefore a CROSS-report
  comparison of two runs — consumed by Task 5.8's regression loop — not a
  within-report delta. :class:`CostDashboard` is a frozen value object with a
  deterministically ordered, ``(template_name, version)``-keyed breakdown, so
  two dashboards are cleanly comparable; Task 5.8 computes the cross-run delta
  by matching keys across two dashboards.

* **Empty inputs are well-defined.** A zero-game tournament, a game with zero
  cost / zero meetings, or an empty ``prompt_versions`` all produce finite,
  non-NaN numbers: ``mean_cost_per_game`` is ``0.0`` when there are no games
  (guarded against division by zero), and a game with empty ``prompt_versions``
  contributes to no breakdown key while its cost still counts toward the total.

This task ships the metric module and its unit tests only. It does NOT wire the
dashboard into tournament JSON output (Task 5.6) and does NOT build the frontend
(Task 5.7) — it produces the typed data those consume.
"""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict

from eval.report_schema import TournamentReport


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base shared by every result model.

    Mirrors the convention in :mod:`eval.report_schema`: the dashboard outputs
    are immutable value objects (so a downstream consumer cannot mutate a metric
    result in place) and an unexpected field is a bug, not something to silently
    absorb (AGENTS.md "no silent fallbacks").
    """

    model_config = ConfigDict(frozen=True, extra="forbid")


class PromptVersionCost(_FrozenModel):
    """Total spend attributed to one ``(template_name, version)`` pair.

    ``total_cost_usd`` is the sum of ``GameCostSummary.total_cost_usd`` over the
    ``game_count`` games whose :attr:`~eval.report_schema.GameReport.prompt_versions`
    mapped ``template_name`` to ``version``. The full game cost is counted once
    here for EACH template the game ran (not split across templates), so these
    totals OVERLAP across the sibling :class:`PromptVersionCost` rows of a
    :class:`CostDashboard` and do not sum to the tournament total — see the
    module docstring.
    """

    template_name: str
    version: str
    total_cost_usd: float
    game_count: int


class CostDashboard(_FrozenModel):
    """Cost-dashboard roll-up for one tournament report (DESIGN.md §10.4, §11.3).

    ``total_cost_usd`` is the sum of every game's authoritative
    ``GameCostSummary.total_cost_usd`` (which already folds in failed-call spend
    — no double-counting). ``mean_cost_per_game`` is ``total_cost_usd /
    game_count``, defined as ``0.0`` for a zero-game report. ``by_model`` is the
    per-model spend rolled up across every game's
    :attr:`~eval.report_schema.GameCostSummary.by_model`, so a mixed-tier
    tournament is auditable per model. ``per_prompt_version`` is the overlapping
    (non-partition) per-``(template_name, version)`` breakdown, ordered
    deterministically by ``(template_name, version)`` so two dashboards from two
    runs compare cleanly (Task 5.8's cross-run delta).
    """

    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    game_count: int
    mean_cost_per_game: float
    by_model: Mapping[str, float]
    per_prompt_version: tuple[PromptVersionCost, ...]


def compute_cost_dashboard(report: TournamentReport) -> CostDashboard:
    """Reduce a :class:`TournamentReport` to its :class:`CostDashboard`.

    Pure and total: no I/O, no engine/LLM calls, never raises on a partial or
    empty report. Reads each game's pre-aggregated
    :class:`~eval.report_schema.GameCostSummary` as the authoritative per-game
    spend; ``GameReport.failed_calls`` is intentionally NOT read here because its
    cost is already inside ``total_cost_usd`` (see the module docstring's
    no-double-count decision).
    """

    total_cost_usd = 0.0
    total_input_tokens = 0
    total_output_tokens = 0
    by_model: dict[str, float] = {}
    version_totals: dict[tuple[str, str], float] = {}
    version_counts: dict[tuple[str, str], int] = {}

    for game in report.games:
        cost = game.cost
        # total_cost_usd is authoritative and already includes failed-call spend
        # (orchestrator.replay.compute_cost_usd folds failed calls in); never add
        # game.failed_calls cost on top (the no-double-count invariant).
        total_cost_usd += cost.total_cost_usd
        total_input_tokens += cost.total_input_tokens
        total_output_tokens += cost.total_output_tokens

        for model_id, model_cost in cost.by_model.items():
            by_model[model_id] = by_model.get(model_id, 0.0) + model_cost

        # Attribute the FULL game cost once under EACH (template, version) the
        # game ran; the per-version totals therefore overlap and are not a
        # partition (a game with empty prompt_versions contributes to no key).
        for template_name, version in game.prompt_versions.items():
            key = (template_name, version)
            version_totals[key] = version_totals.get(key, 0.0) + cost.total_cost_usd
            version_counts[key] = version_counts.get(key, 0) + 1

    game_count = len(report.games)
    # Guard the zero-game case: 0 cost over 0 games is 0.0 by convention, never a
    # ZeroDivisionError or NaN (partial-replay robustness).
    mean_cost_per_game = total_cost_usd / game_count if game_count else 0.0

    per_prompt_version = tuple(
        PromptVersionCost(
            template_name=template_name,
            version=version,
            total_cost_usd=version_totals[(template_name, version)],
            game_count=version_counts[(template_name, version)],
        )
        for template_name, version in sorted(version_totals)
    )

    return CostDashboard(
        total_cost_usd=total_cost_usd,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        game_count=game_count,
        mean_cost_per_game=mean_cost_per_game,
        by_model={model_id: by_model[model_id] for model_id in sorted(by_model)},
        per_prompt_version=per_prompt_version,
    )


__all__ = [
    "CostDashboard",
    "PromptVersionCost",
    "compute_cost_dashboard",
]
