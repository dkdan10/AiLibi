"""Replay spectator routes (DESIGN.md §7, §11.4).

Task 4.1 registers the endpoint signatures with their response DTOs and a
``501`` placeholder body. Task 4.2 fills the bodies via the replay loader
without changing any signature. These modules are thin adapters: route
declarations only, no business logic, no engine/observation/orchestrator
imports.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from api.schemas import (
    AgentMemoryView,
    MeetingView,
    ReplayMetadataView,
    ReplayView,
    TickView,
)

router = APIRouter()

_NOT_IMPLEMENTED_DETAIL = "Not implemented in 4.1; lands in 4.2"


@router.get("", response_model=list[ReplayMetadataView])
def list_replays() -> list[ReplayMetadataView]:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)


@router.get("/{game_id}", response_model=ReplayView)
def get_replay(game_id: str) -> ReplayView:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)


@router.get("/{game_id}/ticks/{tick}", response_model=TickView)
def get_tick(game_id: str, tick: int) -> TickView:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)


@router.get("/{game_id}/meetings/{meeting_id}", response_model=MeetingView)
def get_meeting(game_id: str, meeting_id: str) -> MeetingView:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)


@router.get(
    "/{game_id}/meetings/{meeting_id}/memory/{agent_id}",
    response_model=AgentMemoryView,
)
def get_meeting_memory(game_id: str, meeting_id: str, agent_id: str) -> AgentMemoryView:
    raise HTTPException(status_code=501, detail=_NOT_IMPLEMENTED_DETAIL)
