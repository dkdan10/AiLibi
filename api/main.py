from __future__ import annotations

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, Final, Literal, Protocol, cast

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from api.replay_loader import (
    ReplayPolicyMismatchError,
    ReplayStateMismatchError,
    ReplaySubstrateMismatchError,
    SetLoaderRegistry,
)
from api.routes import eval as eval_routes
from api.routes import replays as replays_routes
from api.routes import sets as sets_routes

# The repo anchor (Task 19.24). The fallback replay directories are resolved
# against the directory this file lives in — ``api/main.py`` -> repo root — and
# NEVER against the process working directory. The old ``Path("./replays")``
# fallbacks made app construction a function of where the interpreter happened to
# be started: importing ``api.main`` from anywhere but the repo root raised at
# import time (this module builds ``app`` at module scope for
# ``uvicorn api.main:app``), and a run started from a subdirectory silently found
# a different — or no — corpus. An anchored path answers the same question the
# same way from every CWD.
_REPO_ROOT: Final[Path] = Path(__file__).resolve().parent.parent

# Env var (documented in .env.example) configuring the PARENT directory of the
# per-set replay subdirs (Task 12.12; ``replays/samples/`` -> ``4p1i/``, ``9p2i/``,
# + future). When unset, falls through to ``<repo>/replays/`` then
# ``<repo>/replays/samples/`` — see ``_resolve_replay_dir`` below. The per-set
# loader resolves ``<parent>/<set>/`` (``api.replay_loader.SetLoaderRegistry``).
ENV_REPLAY_DIR: Final[str] = "AILIBI_REPLAY_DIR"
# Fallback slots RELATIVE TO THE ANCHOR (joined in ``_resolve_replay_dir``), in
# priority order.
_FALLBACK_RELATIVE_PATHS: Final[tuple[str, ...]] = ("replays", "replays/samples")

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


def _announce(parent: Path, sets: list[str]) -> None:
    listing = ", ".join(sets) if sets else "none"
    print(
        f"Serving replay sets from {parent} ({len(sets)} set(s): {listing}).",
        file=sys.stderr,
    )


def _has_set_subdir(parent: Path) -> bool:
    """True iff ``parent`` holds >=1 per-set subdir the registry would SERVE.

    Delegates to :meth:`SetLoaderRegistry.available_sets` so the fallback resolver
    uses the EXACT same definition of "a set" the registry serves — a subdir with a
    valid set name AND >=1 ``replay-seed-*.jsonl``. Without this, an invalid-name
    scratch dir (e.g. ``.tmp/replay-seed-0.jsonl``, which the registry skips) could
    make ``_resolve_replay_dir`` stop at a parent whose ``/sets`` is then empty,
    instead of falling through to a parent that actually has serveable sets (Task
    12.12). The restructure made ``replays/samples/`` a PARENT of per-set subdirs,
    so a valid parent no longer carries ``replay-seed-*.jsonl`` directly.
    """

    return bool(SetLoaderRegistry(parent).available_sets())


def _anchored(path: Path, anchor: Path) -> Path:
    """Return ``path`` as given if absolute, else resolved against ``anchor``.

    A CONFIGURED path may be relative — the two setters that ship in this repo
    both are (``scripts/run_spectator.sh`` exports ``replays/samples``,
    ``frontend/playwright.config.ts`` passes the same). Both run the server from
    the repo root, so anchoring resolves them to exactly the directory they mean
    today; what it removes is the case where they DON'T, which is the whole point
    of Task 19.24: a relative configured path read against the process CWD is the
    same "which corpus is this?" ambiguity the fallbacks had.

    An absolute path is never rewritten, so an operator pointing at a corpus
    outside the repo is unaffected — and that is the escape hatch for anyone who
    genuinely wants a directory the anchor cannot name.
    """

    return path if path.is_absolute() else anchor / path


def _resolve_replay_dir(
    *, replay_dir: Path | None = None, anchor: Path = _REPO_ROOT
) -> Path:
    """Resolve the PARENT replay directory (a parent of per-set subdirs).

    Priority: the INJECTED ``replay_dir``, then the explicit env var, then
    ``<anchor>/replays/``, then ``<anchor>/replays/samples/``. A fallback slot
    wins when it is a directory holding at least one per-set subdir (Task 12.12).
    The injected and env-var slots are honored as named — populated or not — so a
    caller that named a root deliberately gets a clear registry-level error if the
    path is wrong, rather than silent fallthrough; a RELATIVE one is resolved
    against the anchor (:func:`_anchored`) rather than the working directory.

    ``anchor`` defaults to the repo root and is a parameter only so tests can
    exercise the ladder hermetically; nothing resolves against the process
    working directory (Task 19.24), so where the server was started from cannot
    change which corpus it serves.
    """

    if replay_dir is not None:
        return _anchored(replay_dir, anchor)

    explicit = os.environ.get(ENV_REPLAY_DIR, "").strip()
    if explicit:
        return _anchored(Path(explicit), anchor)

    candidates = tuple(anchor / relative for relative in _FALLBACK_RELATIVE_PATHS)
    for candidate in candidates:
        if _has_set_subdir(candidate):
            return candidate

    raise RuntimeError(
        f"No replay sets found. Tried: ${ENV_REPLAY_DIR}, "
        f"{candidates[0]}, {candidates[1]}. Each must be a parent of "
        "per-set subdirs (e.g. replays/samples/4p1i/). "
        "Run `bash scripts/run_spectator.sh` or record into a NAMED set subdir "
        "with `uv run python scripts/run_game.py --seed 0 "
        "--replay-path replays/local/replay-seed-0.jsonl` (a flat "
        "replays/replay-seed-0.jsonl no longer resolves — the resolver needs a "
        "set subdir)."
    )


class _NamesItsGame(Protocol):
    """What every replay-provenance refusal has in common: it names its game."""

    game_id: str


#: The replay-provenance refusals the app surfaces, each with the extra body
#: fields its own comparison already computed — the divergence is named by the
#: loader, never re-derived at the edge. Every one of these errors promises a 500
#: carrying the offending game id, and each promise needs a registration to be
#: true. Ordered specific-first: ``ReplayDispositionMismatchError`` subclasses the
#: state error and is covered by that entry, which carries the tick both need.
_REPLAY_MISMATCH_HANDLERS: Final[
    tuple[tuple[type[Exception], Callable[[Any], dict[str, object]]], ...]
] = (
    (ReplayStateMismatchError, lambda exc: {"tick": exc.tick}),
    (
        ReplaySubstrateMismatchError,
        lambda exc: {"differing_levers": exc.differing, "unknown_levers": exc.unknown},
    ),
    (ReplayPolicyMismatchError, lambda exc: {"differing_fields": exc.differing}),
)


async def _handle_replay_mismatch(request: Request, exc: Exception) -> JSONResponse:
    """Surface a replay-provenance refusal as a 500 naming what diverged."""

    for error_type, extra_fields in _REPLAY_MISMATCH_HANDLERS:
        if isinstance(exc, error_type):
            return JSONResponse(
                status_code=500,
                content={
                    "detail": str(exc),
                    "game_id": cast(_NamesItsGame, exc).game_id,
                    **extra_fields(exc),
                },
            )
    raise exc  # pragma: no cover — only the registered classes reach here


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


def create_app(*, replay_dir: Path | None = None) -> FastAPI:
    """Build the spectator app, serving replays from a CWD-INDEPENDENT root.

    ``replay_dir`` is the injection seam: pass a parent-of-per-set-subdirs and it
    wins outright. Otherwise the root comes from ``AILIBI_REPLAY_DIR`` or, failing
    that, from the repo anchor (see :func:`_resolve_replay_dir`) — never from the
    working directory, including when the injected or configured path is itself
    relative, so ``import api.main`` and every request it then serves behave
    identically wherever the process was started.
    """

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
    # The per-set registry is constructed once at startup and injected via the
    # ``get_replay_loader`` / ``get_loader_registry`` dependencies (which read it
    # back off app.state). It serves ALL recorded sets in one run; per-set loaders
    # are built lazily on first request and cached (Task 12.12).
    parent_dir = _resolve_replay_dir(replay_dir=replay_dir)
    registry = SetLoaderRegistry(parent_dir)
    _announce(parent_dir, registry.available_sets())
    app.state.loader_registry = registry
    for error_type, _extra_fields in _REPLAY_MISMATCH_HANDLERS:
        app.add_exception_handler(error_type, _handle_replay_mismatch)
    app.add_api_route("/", root, methods=["GET"], response_model=ServiceInfoResponse)
    app.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse)
    app.include_router(replays_routes.router, prefix="/replays", tags=["replays"])
    app.include_router(eval_routes.router, prefix="/eval", tags=["eval"])
    app.include_router(sets_routes.router, prefix="/sets", tags=["sets"])
    return app


app = create_app()
