from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final, Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from api.replay_loader import ReplayLoader, ReplayStateMismatchError
from api.routes import eval as eval_routes
from api.routes import replays as replays_routes

# Env var (documented in .env.example) configuring where replay JSONL files are
# scanned from. When unset, falls through to ``./replays/`` then
# ``./replays/samples/`` — see ``_resolve_replay_dir`` below.
ENV_REPLAY_DIR: Final[str] = "AILIBI_REPLAY_DIR"
_FALLBACK_PATHS: Final[tuple[Path, ...]] = (
    Path("./replays"),
    Path("./replays/samples"),
)
_REPLAY_GLOB: Final[str] = "replay-seed-*.jsonl"


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok"]
    service: str


class ServiceInfoResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    service: str


def health() -> HealthResponse:
    return HealthResponse(status="ok", service="ailibi-api")


def root() -> ServiceInfoResponse:
    return ServiceInfoResponse(service="ailibi-api")


def _announce(path: Path) -> Path:
    count = sum(1 for _ in path.glob(_REPLAY_GLOB))
    print(
        f"Serving replays from {path} ({count} {_REPLAY_GLOB} found).",
        file=sys.stderr,
    )
    return path


def _resolve_replay_dir() -> Path:
    """Resolve the replay directory by falling through three sources.

    Priority: explicit env var, then ``./replays/``, then ``./replays/samples/``.
    The first slot that exists and contains at least one ``replay-seed-*.jsonl``
    wins. The env-var slot is honored as-is — populated or not — so callers
    setting it deliberately get a clear loader-level error if the path is wrong,
    rather than silent fallthrough.
    """

    explicit = os.environ.get(ENV_REPLAY_DIR, "").strip()
    if explicit:
        return _announce(Path(explicit))

    for candidate in _FALLBACK_PATHS:
        if candidate.is_dir() and any(candidate.glob(_REPLAY_GLOB)):
            return _announce(candidate)

    raise RuntimeError(
        f"No replays found. Tried: ${ENV_REPLAY_DIR}, "
        f"{_FALLBACK_PATHS[0]}, {_FALLBACK_PATHS[1]}. "
        "Run `bash scripts/run_spectator.sh` or "
        "`uv run python scripts/run_game.py --seed 0 "
        "--replay-path replays/replay-seed-0.jsonl`."
    )


async def _handle_state_mismatch(request: Request, exc: Exception) -> JSONResponse:
    """Surface a replay-determinism break as a 500 with the offending tick."""

    if not isinstance(exc, ReplayStateMismatchError):  # pragma: no cover
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "tick": exc.tick, "game_id": exc.game_id},
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="AiLibi API",
        version="0.1.0",
        description="Spectator and control-plane API for AiLibi.",
    )
    # The loader is constructed once at startup and injected via the
    # ``get_replay_loader`` dependency (which reads it back off app.state).
    app.state.replay_loader = ReplayLoader(replay_dir=_resolve_replay_dir())
    app.add_exception_handler(ReplayStateMismatchError, _handle_state_mismatch)
    app.add_api_route("/", root, methods=["GET"], response_model=ServiceInfoResponse)
    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    app.include_router(replays_routes.router, prefix="/replays", tags=["replays"])
    app.include_router(eval_routes.router, prefix="/eval", tags=["eval"])
    return app


app = create_app()
