"""Eval routes (DESIGN.md §11.4).

Task 4.1 registers the endpoint signature with its response DTO and a ``501``
placeholder body. Task 4.2 fills the body via the replay loader without
changing the signature. Thin adapter: route declarations only.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import EvalCostSummaryView

router = APIRouter()

_NOT_IMPLEMENTED_DETAIL = "Not implemented in 4.1; lands in 4.2"


@router.get("/cost-summary", response_model=EvalCostSummaryView)
def get_cost_summary() -> EvalCostSummaryView:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)
