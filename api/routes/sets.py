"""Recorded-set listing route (Task 12.12; design/phase-12/stage-1-design.md
§2.1, §7).

``GET /sets`` lists the per-set subdirs the spectator can serve in one run — the
available sets the frontend set selector populates from. It AUTO-GROWS: a
newly-recorded ``replays/samples/<set>/`` appears with no code change, and stray
non-set entries (a top-level README, a loose file, a replay-less subdir) are
skipped (:meth:`api.replay_loader.SetLoaderRegistry.available_sets`). ``default``
is the set served when a request carries no ``set`` query param
(:data:`api.replay_loader.DEFAULT_SET`), so the frontend can pick a sane initial
selection that matches the backend's no-``set`` behaviour.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from api.replay_loader import DEFAULT_SET, SetLoaderRegistry, get_loader_registry

router = APIRouter()

_RegistryDep = Annotated[SetLoaderRegistry, Depends(get_loader_registry)]


class SetsView(BaseModel):
    """The available recorded sets + the default-served one."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sets: tuple[str, ...]
    default: str


@router.get("", response_model=SetsView)
def list_sets(registry: _RegistryDep) -> SetsView:
    sets = registry.available_sets()
    # Prefer the configured default when present; otherwise the first available
    # set, so the advertised default always resolves (falling back to the
    # constant only for an empty parent, where every set request 404s anyway).
    if DEFAULT_SET in sets:
        default = DEFAULT_SET
    elif sets:
        default = sets[0]
    else:
        default = DEFAULT_SET
    return SetsView(sets=tuple(sets), default=default)
