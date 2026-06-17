"""Replay spectator routes (DESIGN.md §7, §11.4).

Thin adapters over :class:`api.replay_loader.ReplayLoader`: each handler
resolves the injected loader, delegates engine-playback to it, and maps loader
exceptions to HTTP status codes. The endpoint signatures (paths, path params,
response models) are frozen from Task 4.1; 4.2 only fills the bodies and adds
the loader dependency. ``ReplayStateMismatchError`` is intentionally NOT caught
here — it is mapped to a ``500`` with the offending tick by the app-level
handler registered in :mod:`api.main`.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from api.replay_loader import ReplayLoader, get_replay_loader
from api.schemas import (
    AgentMemoryView,
    BeliefFrameView,
    MeetingView,
    ReplayMetadataView,
    ReplayView,
    TickView,
)

router = APIRouter()

_LoaderDep = Annotated[ReplayLoader, Depends(get_replay_loader)]


@router.get("", response_model=list[ReplayMetadataView])
def list_replays(
    loader: _LoaderDep,
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ReplayMetadataView]:
    # Optional pagination (Audit G-G-3): absent params return every replay,
    # preserving the original behavior; the loader slices its (seed-sorted) path
    # list before building any metadata view so the work is bounded by the page.
    return loader.list_replays(limit=limit, offset=offset)


@router.get("/{game_id}", response_model=ReplayView)
def get_replay(game_id: str, loader: _LoaderDep) -> ReplayView:
    try:
        return loader.load_replay(game_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"replay not found: {game_id}")


@router.get("/{game_id}/ticks/{tick}", response_model=TickView)
def get_tick(game_id: str, tick: int, loader: _LoaderDep) -> TickView:
    try:
        replay = loader.load_replay(game_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"replay not found: {game_id}")
    for tick_view in replay.ticks:
        if tick_view.tick == tick:
            return tick_view
    raise HTTPException(
        status_code=404, detail=f"tick out of range for {game_id}: {tick}"
    )


@router.get("/{game_id}/beliefs", response_model=list[BeliefFrameView])
def get_belief_frames(game_id: str, loader: _LoaderDep) -> list[BeliefFrameView]:
    # Per-MEETING belief × truth snapshots (DESIGN.md §3.3, §7). Reuses the
    # cached meeting-memory re-walk; an empty list is a valid response for a
    # zero-meeting game (the frontend renders a first-class empty state).
    try:
        return list(loader.belief_frames(game_id))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"replay not found: {game_id}")


@router.get("/{game_id}/meetings/{meeting_id}", response_model=MeetingView)
def get_meeting(game_id: str, meeting_id: str, loader: _LoaderDep) -> MeetingView:
    try:
        replay = loader.load_replay(game_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"replay not found: {game_id}")
    for meeting in replay.meetings:
        if meeting.meeting_id == meeting_id:
            return meeting
    raise HTTPException(status_code=404, detail=f"meeting not found: {meeting_id}")


@router.get(
    "/{game_id}/meetings/{meeting_id}/memory/{agent_id}",
    response_model=AgentMemoryView,
)
def get_meeting_memory(
    game_id: str, meeting_id: str, agent_id: str, loader: _LoaderDep
) -> AgentMemoryView:
    try:
        return loader.get_meeting_memory(game_id, meeting_id, agent_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"replay not found: {game_id}")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=exc.args[0])
