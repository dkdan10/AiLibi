from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final, Literal

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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

# Optional comma-separated cross-origin allowlist (documented in
# docs/deployment.md and .env.example). The spectator API is an
# unauthenticated GM view: it ships with a CLOSED CORS posture. When this var
# is unset (or holds no non-empty origins) no CORS middleware is installed —
# the same-origin Vite dev proxy and same-origin static serving need none.
# When it lists explicit origins, ``CORSMiddleware`` is installed scoped to
# exactly those origins. A literal ``*`` is rejected: never serve the GM view
# with a wildcard CORS policy.
ENV_CORS_ORIGINS: Final[str] = "AILIBI_CORS_ORIGINS"


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


def _parse_cors_origins(raw: str | None) -> list[str]:
    """Parse the cross-origin allowlist from its comma-separated env value.

    Returns the explicit list of origins. An unset value, a whitespace-only
    value, or a value whose entries are all blank yields an empty list, which
    the caller treats as "no cross-origin access" — no permissive middleware is
    installed. This honors the project's no-silent-fallback discipline: an
    explicitly-set-but-empty allowlist means "allow nothing", never "allow all".

    A literal ``*`` entry raises: the spectator API is an unauthenticated GM
    view and must never be served with a wildcard CORS policy.
    """

    if raw is None:
        return []
    origins = [origin.strip() for origin in raw.split(",")]
    origins = [origin for origin in origins if origin]
    if "*" in origins:
        raise RuntimeError(
            f"{ENV_CORS_ORIGINS} must be an explicit allowlist of origins; the "
            "wildcard '*' is forbidden because the spectator API serves an "
            "unauthenticated GM view. List explicit origins or leave it unset."
        )
    return origins


def create_app() -> FastAPI:
    app = FastAPI(
        title="AiLibi API",
        version="0.1.0",
        description="Spectator and control-plane API for AiLibi.",
    )
    # Closed-by-default CORS posture (see ENV_CORS_ORIGINS above and
    # docs/deployment.md). Middleware is installed ONLY when an explicit
    # allowlist is configured; the default (unset) path adds nothing, leaving
    # the same-origin dev proxy and static serving untouched.
    cors_origins = _parse_cors_origins(os.environ.get(ENV_CORS_ORIGINS))
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=False,
            allow_methods=["GET"],
            allow_headers=["Content-Type"],
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
