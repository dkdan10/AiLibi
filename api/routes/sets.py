"""Recorded-set listing route (Task 12.12; design/phase-12/stage-1-design.md
§2.1, §7).

``GET /sets`` lists the per-set subdirs the spectator can serve in one run — the
available sets the frontend set selector populates from. It AUTO-GROWS: a
newly-recorded ``replays/samples/<set>/`` appears with no code change, and stray
non-set entries (a top-level README, a loose file, a replay-less subdir) are
skipped (:meth:`api.replay_loader.SetLoaderRegistry.available_sets`). ``default``
is the set served when a request carries no ``set`` query param — resolved by
:meth:`api.replay_loader.SetLoaderRegistry.default_set`, the SAME resolver
``get_replay_loader`` uses for an omitted ``set``, so the advertised default and
the routes' no-``set`` behaviour can never disagree.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from api.replay_loader import SetLoaderRegistry, get_loader_registry

router = APIRouter()

_RegistryDep = Annotated[SetLoaderRegistry, Depends(get_loader_registry)]


class SetsView(BaseModel):
    """The available recorded sets + the default-served one."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sets: tuple[str, ...]
    default: str


@router.get("", response_model=SetsView)
def list_sets(registry: _RegistryDep) -> SetsView:
    # The advertised default is the SAME resolver routes use for an omitted ?set=
    # (SetLoaderRegistry.default_set), so the two can never disagree.
    return SetsView(
        sets=tuple(registry.available_sets()), default=registry.default_set()
    )
