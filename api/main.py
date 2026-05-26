from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from api.replay_loader import ReplayLoader, ReplayStateMismatchError
from api.routes import eval as eval_routes
from api.routes import replays as replays_routes

# Env var (documented in .env.example) configuring where replay JSONL files are
# scanned from. Falls back to ``./replays/`` relative to the process cwd.
ENV_REPLAY_DIR: str = "AILIBI_REPLAY_DIR"
DEFAULT_REPLAY_DIR: str = "./replays"


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


def _replay_dir_from_env() -> Path:
    return Path(os.environ.get(ENV_REPLAY_DIR, DEFAULT_REPLAY_DIR))


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
    app.state.replay_loader = ReplayLoader(replay_dir=_replay_dir_from_env())
    app.add_exception_handler(ReplayStateMismatchError, _handle_state_mismatch)
    app.add_api_route("/", root, methods=["GET"], response_model=ServiceInfoResponse)
    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    app.include_router(replays_routes.router, prefix="/replays", tags=["replays"])
    app.include_router(eval_routes.router, prefix="/eval", tags=["eval"])
    return app


app = create_app()
