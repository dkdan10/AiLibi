from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from api.routes import eval as eval_routes
from api.routes import replays as replays_routes


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


def create_app() -> FastAPI:
    app = FastAPI(
        title="AiLibi API",
        version="0.1.0",
        description="Spectator and control-plane API for AiLibi.",
    )
    app.add_api_route("/", root, methods=["GET"], response_model=ServiceInfoResponse)
    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    app.include_router(replays_routes.router, prefix="/replays", tags=["replays"])
    app.include_router(eval_routes.router, prefix="/eval", tags=["eval"])
    return app


app = create_app()
