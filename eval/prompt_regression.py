"""Prompt regression suite (DESIGN.md §11.3).

DESIGN.md §11.3 closes Phase 5 on a demonstrable loop: *for each prompt
version, run a fixed seed set and compare metric deltas; block merge if a
metric regresses by > X%.* This module is that loop, run **deterministically
and without a model**.

The enabling insight: the Phase 5 metrics are pure analyzers over a
:class:`~eval.report_schema.TournamentReport`, which is assembled from replay
records — and real recorded meetings already exist as replay JSONL. So the
regression suite needs no live model and no engine re-run. It:

1. discovers the recorded ``replay-seed-{seed}.jsonl`` files in a frozen fixture
   directory (one directory == one prompt-template version set);
2. derives the per-seed role ground truth deterministically from the seed via
   :func:`orchestrator.seeder.seed_initial_state` (``roles`` is the one input
   not in the replay JSONL — the leak firewall keeps it out — so it is
   recomputed, never stored in the fixture);
3. folds the recorded replays into a :class:`TournamentReport` via the public
   :func:`eval.balance_eval.load_tournament_report` (the same per-seed assembly
   the live tournament path uses — no duplicated record->report mapping);
4. runs the four §11.3 analyzers via
   :func:`eval.meeting_quality.build_tournament_eval_report`; and
5. packs the metric scalars plus the per-``(template_name, version)``
   provenance into a :class:`PromptRegressionSummary`.

Because the fixtures are recorded real outputs and the analyzers are pure, the
summary is byte-stable: a committed baseline of expected scalars can be matched
**exactly**, and any drift is a real regression in a metric, the loader, or the
report schema. ``FakeProvider`` is deliberately NOT used: it emits empty/stub
meetings, so a fake run yields trivial metric values and a meaningless signal.
No provider is invoked at all, so ``AILIBI_LLM_PROVIDER`` is irrelevant.

Regression-signal policy
------------------------
* **CI uses exact match.** The frozen fixtures + pure analyzers + derived roles
  give exact scalars, so :mod:`tests.eval.test_prompt_regression` asserts the
  computed summary equals the committed baseline exactly. A mismatch is a real
  metric / loader / schema regression and fails the build.
* **The ``> X%`` tolerance is the manual real-provider re-record policy**, not a
  CI knob. When a prompt template actually changes, a maintainer re-records the
  samples with a live provider (out of CI; see below) and compares the new
  scalars to the old: a metric moving by more than ``X = 10%`` is treated as a
  regression worth blocking. That comparison is judgment over noisy live
  outputs; CI's exact match is over frozen ones.

Regenerating fixtures from a real provider (manual, out of CI)
-------------------------------------------------------------
The committed fixtures are frozen, owned copies of canonical-set replays (NOT
the live ``replays/samples/9p2i/``, which ``scripts/refresh_samples.sh``
rewrites). They are recorded at the canonical 9p/2i roster (DESIGN.md §3.5:
9 players / 2 impostors / 2 tasks per crewmate), so the role derivation must be
run at that roster. To refresh them after a genuine prompt-template change:

1. change the prompt template and bump its version marker;
2. ``bash scripts/refresh_samples.sh --meetings`` at the 9p/2i env
   (``AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2``
   ``AILIBI_SAMPLE_DIR=replays/samples/9p2i`` + its manifest) to re-record the
   meeting-bearing seeds with a live provider;
3. copy the new ``replays/samples/9p2i/replay-seed-{seed}.jsonl`` for the
   fixture seeds into ``tests/fixtures/prompt_regression/<version>/``;
4. regenerate ``baseline.json`` (run each fixture through
   :func:`run_prompt_regression` at the 9p/2i roster and dump the summaries)
   and review the metric deltas against the ``> X%`` policy before committing.

The committed ``v_b`` fixture is a *hand-authored* minimal variant of ``v_a``
(same seeds) used to demonstrate the loop deterministically: its
``impostor_report`` template version is bumped one step and one recorded
meeting gains an ``alibi_conflict`` contradiction naming the impostor, which
flips that impostor's fabricated alibi from *survived* to *caught* — moving the
alibi-fabrication survival rate while leaving the other metrics fixed. That is
the prompt-change -> metric-diff loop, attributable to the one changed template.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict

from engine.entities import PlayerId, Role
from engine.world import Map, load_canonical_map
from eval.balance_eval import load_tournament_report
from eval.meeting_quality import build_tournament_eval_report
from orchestrator.game import DEFAULT_NUM_IMPOSTORS, DEFAULT_NUM_PLAYERS
from orchestrator.seeder import seed_initial_state

# Documented tolerance for the MANUAL real-provider re-record comparison (a
# metric moving more than this between two live re-records is treated as a
# regression). CI does NOT use it: CI matches the frozen baseline exactly.
REAL_PROVIDER_REGRESSION_TOLERANCE: Final[float] = 0.10

_REPLAY_FILENAME_RE: Final[re.Pattern[str]] = re.compile(r"^replay-seed-(\d+)\.jsonl$")


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base, matching the report-schema convention."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class PromptVersionProvenance(_FrozenModel):
    """Spend attributed to one ``(template_name, version)`` pair in the run.

    Mirrors :class:`eval.cost_dashboard.PromptVersionCost` (the source of these
    numbers) but is owned by the regression summary so the baseline JSON has a
    stable, self-contained shape. The per-version rows are what make a metric
    delta *traceable*: two summaries from two fixtures differ here exactly in the
    template whose version changed.
    """

    template_name: str
    version: str
    total_cost_usd: float
    game_count: int


class PromptRegressionMetrics(_FrozenModel):
    """The §11.3 metric scalars pulled from a :class:`TournamentEvalReport`.

    One flat, comparable record per fixture: the regression loop compares these
    across prompt versions. Each field is produced by its owning metric module
    (never re-derived here):

    * ``vote_correctness_rate`` —
      :attr:`eval.vote_correctness.VoteCorrectnessReport.vote_correctness_rate`
      (``None`` when there were no impostor ejections). Kept as a
      **diagnostic only**: it reads the evidence-backed share of impostor
      ejections, which a zero-flag conviction legally lowers (see
      :mod:`eval.vote_correctness`), so a baseline delta on it is not a
      prompt-quality move — the Wave-1 leads are the two conversion fields
      below.
    * ``ejection_accuracy`` / ``impostor_accused_conversion_rate`` /
      ``missed_skip_ballots`` — the Task 9.6 Wave-1 conversion leads
      (precision and recall) plus the missed-SKIP sentinel count from
      :class:`eval.meeting_quality.ConversionReport` (the rates are ``None``
      when their denominators are empty). These are the scalars a Wave-1
      prompt A/B is gated on, so the committed baseline pins them per prompt
      version.
    * ``alibi_survival_rate`` / ``total_impostor_alibis`` —
      :class:`eval.alibi_fabrication.AlibiFabricationReport`.
      ``alibi_survival_rate`` is ``None`` when the fixture set recorded no
      impostor alibis (the None-iff-undefined convention, Task 19.5: the rate
      is undefined, and the retired ``0.0`` would have read as "alibis were
      filed and none survived").
    * ``accusation_claim_ece`` / ``vote_ballot_ece`` — the two expected
      calibration errors from
      :class:`eval.accusation_calibration.AccusationCalibrationReport` (each
      ``None`` when that channel had no samples).
    * ``total_cost_usd`` — :attr:`eval.cost_dashboard.CostDashboard.total_cost_usd`.
    * ``meeting_rate`` / ``meetings_total`` / ``body_report_meetings`` /
      ``emergency_meetings`` — the Phase 7 W0.3 Stage-A close-gate scalars from
      :class:`eval.meeting_quality.MeetingRateReport` (``meeting_rate`` is
      ``None`` when the fixture set holds no games). They make the
      ``meeting_rate ≥ 0.60`` gate a byte-stable, committed-baseline scalar like
      the other §11.3 metrics.
    """

    vote_correctness_rate: float | None
    ejection_accuracy: float | None
    impostor_accused_conversion_rate: float | None
    missed_skip_ballots: int
    alibi_survival_rate: float | None
    total_impostor_alibis: int
    accusation_claim_ece: float | None
    vote_ballot_ece: float | None
    total_cost_usd: float
    meeting_rate: float | None
    meetings_total: int
    body_report_meetings: int
    emergency_meetings: int


class PromptRegressionSummary(_FrozenModel):
    """Deterministic metric summary for one prompt-version fixture set.

    Frozen and ``extra="forbid"`` (report-schema convention). Round-trips
    through ``model_dump(mode="json")`` / ``model_validate`` so a committed
    ``baseline.json`` can be matched exactly. ``prompt_versions`` carries the
    per-``(template_name, version)`` provenance ordered deterministically, so a
    metric delta between two summaries is attributable to whichever template's
    version changed.
    """

    seeds: tuple[int, ...]
    game_count: int
    prompt_versions: tuple[PromptVersionProvenance, ...]
    metrics: PromptRegressionMetrics


def run_prompt_regression(
    fixture_dir: Path,
    *,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    tasks_per_crewmate: int = 1,
    game_map: Map | None = None,
) -> PromptRegressionSummary:
    """Run the §11.3 metrics over a frozen fixture directory of replay JSONL.

    Discovers ``replay-seed-{seed}.jsonl`` in ``fixture_dir``, derives each
    seed's role ground truth via :func:`orchestrator.seeder.seed_initial_state`
    (deterministic; never read from the replay), assembles a
    :class:`TournamentReport` with
    :func:`eval.balance_eval.load_tournament_report`, runs
    :func:`eval.meeting_quality.build_tournament_eval_report`, and packs the
    metric scalars plus per-version provenance into a
    :class:`PromptRegressionSummary`.

    ``num_players`` / ``num_impostors`` / ``tasks_per_crewmate`` / ``game_map``
    MUST match the setup the fixtures were recorded under. They default to the
    descriptor-less flat-baseline configuration (4p/1i at one task per
    crewmate — what a default ``scripts/refresh_samples.sh`` records), so a
    caller reading fixtures from another roster — e.g. the committed 9p/2i
    canonical-set fixtures — passes the roster explicitly. They feed only the
    deterministic role derivation; no game is run.

    No network, no live or fake model call: the metric signal comes entirely
    from the recorded outputs in the fixtures. Raises ``ValueError`` if the
    directory holds no ``replay-seed-*.jsonl`` files (a misconfigured fixture
    path, fail-loud).
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    seeds = _discover_fixture_seeds(fixture_dir)
    roles_by_seed: dict[int, Mapping[PlayerId, Role]] = {
        seed: _seeded_roles(
            seed=seed,
            game_map=resolved_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        for seed in seeds
    }

    # The regression metrics read only the meeting analyzers (vote correctness,
    # alibi, calibration, cost, meeting rate), never the Task 8.17 kill-gift
    # fields, so skip the kill-gift reconstruction walk: it would re-seed the
    # frozen fixtures under the current seeder, which the Task 8.14 round-start
    # cooldown changed (the fixtures are re-recorded in Task 8.18). This keeps
    # run_prompt_regression a pure no-engine-re-run analyzer over the fixtures.
    report = load_tournament_report(
        fixture_dir,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=resolved_map,
        derive_kill_gift=False,
    )
    evaluated = build_tournament_eval_report(report)

    metrics = PromptRegressionMetrics(
        vote_correctness_rate=evaluated.vote_correctness.vote_correctness_rate,
        ejection_accuracy=evaluated.conversion.ejection_accuracy,
        impostor_accused_conversion_rate=(
            evaluated.conversion.impostor_accused_conversion_rate
        ),
        missed_skip_ballots=evaluated.conversion.missed_skip_ballots,
        alibi_survival_rate=evaluated.alibi_fabrication.survival_rate,
        total_impostor_alibis=evaluated.alibi_fabrication.total_impostor_alibis,
        accusation_claim_ece=evaluated.accusation_calibration.accusation_claim_ece,
        vote_ballot_ece=evaluated.accusation_calibration.vote_ballot_ece,
        total_cost_usd=evaluated.cost_dashboard.total_cost_usd,
        meeting_rate=evaluated.meeting_rate.meeting_rate,
        meetings_total=evaluated.meeting_rate.meetings_total,
        body_report_meetings=evaluated.meeting_rate.body_report_meetings,
        emergency_meetings=evaluated.meeting_rate.emergency_meetings,
    )
    prompt_versions = tuple(
        PromptVersionProvenance(
            template_name=pv.template_name,
            version=pv.version,
            total_cost_usd=pv.total_cost_usd,
            game_count=pv.game_count,
        )
        for pv in evaluated.cost_dashboard.per_prompt_version
    )
    return PromptRegressionSummary(
        seeds=seeds,
        game_count=len(report.games),
        prompt_versions=prompt_versions,
        metrics=metrics,
    )


def _discover_fixture_seeds(fixture_dir: Path) -> tuple[int, ...]:
    """Sorted seeds of the ``replay-seed-{seed}.jsonl`` files in ``fixture_dir``.

    The fixture directory is self-describing: its replay filenames ARE the seed
    set. Fail-loud if the path is not a directory or holds no matching files, so
    a typo'd fixture path cannot silently produce an empty (vacuously passing)
    regression run.
    """

    if not fixture_dir.is_dir():
        raise ValueError(f"fixture_dir is not a directory: {fixture_dir}")
    seeds = sorted(
        int(match.group(1))
        for entry in fixture_dir.iterdir()
        if (match := _REPLAY_FILENAME_RE.match(entry.name))
    )
    if not seeds:
        raise ValueError(
            f"no replay-seed-*.jsonl fixtures found in {fixture_dir}: the "
            "regression suite reads recorded replays only, so an empty fixture "
            "directory is a misconfiguration, not a zero-metric run."
        )
    return tuple(seeds)


def _seeded_roles(
    *,
    seed: int,
    game_map: Map,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> dict[PlayerId, Role]:
    """Derive a fixture seed's role ground truth from the deterministic seeding.

    ``roles`` is the one input not in the replay JSONL (the leak firewall keeps
    it out), so it is recomputed from the seeded game setup rather than stored in
    the fixture — the same deterministic source the live loader's role recovery
    uses. The full roster (including ``tasks_per_crewmate``) is threaded so the
    derivation runs under exactly the recorded setup. No LLM, no network, fully
    reproducible.
    """

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    return {player_id: player.role for player_id, player in state.players.items()}


__all__ = [
    "REAL_PROVIDER_REGRESSION_TOLERANCE",
    "PromptRegressionMetrics",
    "PromptRegressionSummary",
    "PromptVersionProvenance",
    "run_prompt_regression",
]
