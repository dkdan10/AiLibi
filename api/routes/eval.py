"""Eval routes (DESIGN.md §11.4).

Thin adapter over :class:`api.replay_loader.ReplayLoader`: the cost-summary
handler delegates the cross-replay aggregation to the loader. The endpoint
signature is frozen from Task 4.1; 4.2 only fills the body and adds the loader
dependency.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import EvalCostSummaryView

router = APIRouter()

_LoaderDep = Annotated[ReplayLoader, Depends(get_replay_loader)]


@router.get("/cost-summary", response_model=EvalCostSummaryView)
def get_cost_summary(loader: _LoaderDep) -> EvalCostSummaryView:
    return loader.cost_summary()
