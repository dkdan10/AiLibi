"""Eval routes (DESIGN.md §11.3, §11.4).

Thin adapter over :class:`api.replay_loader.ReplayLoader`: each handler
delegates the cross-replay aggregation / report load to the loader. The
cost-summary endpoint signature is frozen from Task 4.1; 4.2 only filled the
body and added the loader dependency.

``GET /tournament-report`` (Task 5.7, DESIGN.md §11.3) mirrors the
``/cost-summary`` thin-adapter pattern: it serves the latest
``tournament-eval-report.json`` from the configured eval dir. It returns the
deep :class:`eval.meeting_quality.TournamentEvalReport` directly as its
``response_model`` rather than re-modeling a parallel DTO — the structure is
deep and the spectator API is a privileged surface (DESIGN.md §1.3), so it
intentionally exposes the report's ``roles`` ground truth for the dashboard,
consistent with the replay viewer already exposing role.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import EvalCostSummaryView
from eval.meeting_quality import TournamentEvalReport

router = APIRouter()

_LoaderDep = Annotated[ReplayLoader, Depends(get_replay_loader)]


@router.get("/cost-summary", response_model=EvalCostSummaryView)
def get_cost_summary(loader: _LoaderDep) -> EvalCostSummaryView:
    return loader.cost_summary()


@router.get("/tournament-report", response_model=TournamentEvalReport)
def get_tournament_report(loader: _LoaderDep) -> TournamentEvalReport:
    try:
        return loader.tournament_report()
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="no tournament-eval-report.json in the configured eval dir",
        )
