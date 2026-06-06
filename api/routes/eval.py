"""Eval routes (DESIGN.md §11.3, §11.4).

Thin adapter over :class:`api.replay_loader.ReplayLoader`: each handler
delegates the cross-replay aggregation / report load to the loader. The
cost-summary endpoint signature is frozen from Task 4.1; 4.2 only filled the
body and added the loader dependency.

``GET /tournament-report`` (Task 5.7, DESIGN.md §11.3) mirrors the
``/cost-summary`` thin-adapter pattern: it serves the latest
``tournament-eval-report.json`` from the configured eval dir. It deliberately
exposes the report's ``roles`` ground truth for the dashboard — the spectator
API is a privileged GM surface (DESIGN.md §1.3), consistent with the replay
viewer already exposing role.

Failed-call redaction (Task 6.5, audit B-B-1 = D-D-1; DESIGN.md §11.2, §11.3).
The report transitively embeds :class:`orchestrator.replay.FailedCallReplayEntry`,
whose ``raw_response`` blob, ``prompt_length``, and untruncated ``error_message``
the Phase 4 replay surface already redacts via :class:`api.schemas.FailedCallView`.
Serving the eval report verbatim re-exposed those raw fields over HTTP — a
contract asymmetry between two surfaces that must agree (both are unauthenticated
GM views, so this is not a role/engine-state leak, but the surfaces are
reconciled here). The route therefore maps each game's failed calls through the
sanitized :class:`api.schemas.FailedCallEvalView` and serves the thin
``_TournamentEvalReportView`` chain below.

That chain re-models ONLY the failed-call leaf: it reuses the five metric
reports, the meeting report, the cost roll-up, and the role/winner leaf types
verbatim by import, and re-declares solely the three report-wrapper shapes
(game / tournament / eval-wrapper) so the sole structural change is the failed
call leaf. Every other field — roles included — is served exactly as the source
report carries it. The underlying replay record is never mutated.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Any, Final

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict

from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import EvalCostSummaryView, FailedCallEvalView
from engine.entities import Role
from eval.accusation_calibration import AccusationCalibrationReport
from eval.alibi_fabrication import AlibiFabricationReport
from eval.cost_dashboard import CostDashboard
from eval.meeting_quality import MeetingRateReport, TournamentEvalReport
from eval.report_schema import GameCostSummary, MeetingReport
from eval.vote_correctness import VoteCorrectnessReport
from meetings.schemas import PlayerId
from orchestrator.replay import WinnerSide

router = APIRouter()

_LoaderDep = Annotated[ReplayLoader, Depends(get_replay_loader)]

# Fields of ``FailedCallReplayEntry`` carried over verbatim onto
# ``FailedCallEvalView``; ``error_message`` is handled separately (truncated).
# Everything else on the source entry (``raw_response``, ``prompt_length``,
# ``input_tokens``, ``output_tokens``, ``kind``, ``game_id``) is dropped to
# mirror :class:`api.schemas.FailedCallView` (audit B-B-1 / D-D-1).
_FAILED_CALL_EVAL_KEYS: Final[tuple[str, ...]] = (
    "meeting_id",
    "tick",
    "model",
    "cost_usd",
    "error_type",
)
_ERROR_MESSAGE_MAX_CHARS: Final[int] = 200


class _GameReportEvalView(BaseModel):
    """``eval.report_schema.GameReport`` with the failed-call leaf sanitized.

    Every field mirrors ``GameReport`` one-for-one and reuses its leaf types by
    import (``MeetingReport``, ``GameCostSummary``, ``Role``, ``PlayerId``,
    ``WinnerSide``); only ``failed_calls`` is re-typed to the redacted
    :class:`~api.schemas.FailedCallEvalView`. ``extra="forbid"`` means a future
    field added to ``GameReport`` trips the redaction re-validation loudly
    instead of silently passing through unredacted (paired with the leak-firewall
    snapshot in ``tests/api/test_leak.py``).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    game_id: str
    seed: int
    winner: WinnerSide | None
    reason: str
    final_tick: int | None
    roles: Mapping[PlayerId, Role]
    replay_ref: str
    meetings: tuple[MeetingReport, ...]
    failed_calls: tuple[FailedCallEvalView, ...]
    prompt_versions: Mapping[str, str]
    cost: GameCostSummary
    # Task 8.17 kill-gift facts (DESIGN.md §3.5; audit gp-4). Pure derived
    # counts/flags, mirrored one-for-one from ``GameReport`` so the redaction
    # re-validation accepts them (and the leak snapshot stays the firewall).
    kill_gifted: bool = False
    instances_dropped: int = 0
    instances_complete_at_win: int = 0


class _TournamentReportEvalView(BaseModel):
    """``eval.report_schema.TournamentReport`` whose games carry the sanitized leaf."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    format_version: int
    games: tuple[_GameReportEvalView, ...]
    seeds_used: tuple[int, ...]
    # Task 8.17 kill-gift aggregates (DESIGN.md §3.5; audit gp-4), mirrored from
    # ``TournamentReport``.
    kill_gifted_wins: int = 0
    instances_dropped_total: int = 0
    mean_instances_complete_at_win: float | None = None


class _TournamentEvalReportView(BaseModel):
    """The served eval report: the source wrapper with redacted failed calls.

    Mirrors :class:`eval.meeting_quality.TournamentEvalReport` and reuses its
    metric reports verbatim by import; only the embedded ``report`` is the
    redacted view. Because this view forbids extras, a new field on
    ``TournamentEvalReport`` (here ``meeting_rate``) MUST be mirrored here or
    :func:`_redact_failed_calls`'s ``model_validate`` round-trip raises.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: _TournamentReportEvalView
    vote_correctness: VoteCorrectnessReport
    accusation_calibration: AccusationCalibrationReport
    alibi_fabrication: AlibiFabricationReport
    cost_dashboard: CostDashboard
    meeting_rate: MeetingRateReport


def _sanitized_failed_call(call: Mapping[str, Any]) -> dict[str, Any]:
    """Project one dumped ``FailedCallReplayEntry`` onto the eval DTO field set."""

    redacted: dict[str, Any] = {key: call[key] for key in _FAILED_CALL_EVAL_KEYS}
    redacted["error_message"] = call["error_message"][:_ERROR_MESSAGE_MAX_CHARS]
    return redacted


def _redact_failed_calls(report: TournamentEvalReport) -> _TournamentEvalReportView:
    """Re-serve ``report`` with each game's failed calls run through the eval DTO.

    Dumps the validated report to a JSON-able dict, rewrites every game's
    ``failed_calls`` to the :class:`~api.schemas.FailedCallEvalView` field set
    (dropping ``raw_response`` / ``prompt_length`` / per-call tokens, truncating
    ``error_message``), and re-validates into the thin view. Re-validation routes
    each entry through ``FailedCallEvalView`` and — because that model forbids
    extra fields — fails loud if a raw field were ever left in, so the redaction
    cannot silently regress.
    """

    payload: dict[str, Any] = report.model_dump(mode="json")
    for game in payload["report"]["games"]:
        game["failed_calls"] = [
            _sanitized_failed_call(call) for call in game["failed_calls"]
        ]
    return _TournamentEvalReportView.model_validate(payload)


@router.get("/cost-summary", response_model=EvalCostSummaryView)
def get_cost_summary(loader: _LoaderDep) -> EvalCostSummaryView:
    return loader.cost_summary()


@router.get("/tournament-report", response_model=_TournamentEvalReportView)
def get_tournament_report(loader: _LoaderDep) -> _TournamentEvalReportView:
    try:
        report = loader.tournament_report()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="no tournament-eval-report.json in the configured eval dir",
        )
    return _redact_failed_calls(report)
