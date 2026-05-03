from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok"]
    service: str


def health() -> HealthResponse:
    return HealthResponse(status="ok", service="ailibi-api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AiLibi API",
        version="0.1.0",
        description="Spectator and control-plane API for AiLibi.",
    )
    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    return app


app = create_app()
