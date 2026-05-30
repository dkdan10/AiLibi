"""Deployment-surface configuration tests for the spectator API (Task 6.1).

The spectator API is an unauthenticated GM view (roles, kill attribution, vent
state, rendered prompts), safe only on loopback or behind auth + network
isolation. These tests pin the safe-by-default posture that hardens that
surface (audit C-C-1, C-C-2):

* the default app (no ``AILIBI_CORS_ORIGINS``) installs no CORS middleware —
  the same-origin Vite dev proxy and same-origin static serving need none;
* an explicit allowlist installs ``CORSMiddleware`` scoped to exactly those
  origins, never a wildcard;
* an explicitly-set-but-empty/blank allowlist installs nothing (no silent
  "allow all"), honoring the project's no-silent-fallback discipline;
* a literal ``*`` is rejected outright;
* docker-compose publishes the API port on the host loopback only.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.main import (
    ENV_CORS_ORIGINS,
    ENV_REPLAY_DIR,
    _parse_cors_origins,
    create_app,
)


def _cors_allow_origins(app: FastAPI) -> list[str] | None:
    """Return the configured ``allow_origins`` of the app's ``CORSMiddleware``.

    Returns ``None`` when no ``CORSMiddleware`` is installed, distinguishing the
    closed-default posture (no middleware) from a configured allowlist.
    """

    for middleware in app.user_middleware:
        # ``Middleware.cls`` is typed as a factory protocol, so widen to object
        # before the identity check (a direct ``is`` against the concrete class
        # is a non-overlapping comparison under mypy --strict).
        middleware_cls: object = middleware.cls
        if middleware_cls is CORSMiddleware:
            origins: Any = middleware.kwargs["allow_origins"]
            assert isinstance(origins, list)
            return origins
    return None


@pytest.fixture(autouse=True)
def _isolate_app_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Make ``create_app()`` hermetic and independent of the ambient shell.

    Scrubs any inherited ``AILIBI_CORS_ORIGINS`` so each test owns the posture,
    and points replay resolution at a throwaway dir so app construction never
    depends on the repo's ``replays/`` layout (``ReplayLoader.__init__`` does no
    eager file I/O, so an empty dir is fine).
    """

    monkeypatch.delenv(ENV_CORS_ORIGINS, raising=False)
    monkeypatch.setenv(ENV_REPLAY_DIR, str(tmp_path))


# -- _parse_cors_origins -------------------------------------------------------


def test_parse_origins_unset_is_empty() -> None:
    assert _parse_cors_origins(None) == []


def test_parse_origins_blank_is_empty() -> None:
    # Whitespace-only and all-blank-entry values resolve to "no origins" rather
    # than being mistaken for a permissive posture.
    assert _parse_cors_origins("") == []
    assert _parse_cors_origins("   ") == []
    assert _parse_cors_origins("  ,  , ") == []


def test_parse_origins_splits_and_strips() -> None:
    assert _parse_cors_origins("https://a.example, https://b.example") == [
        "https://a.example",
        "https://b.example",
    ]


def test_parse_origins_rejects_wildcard() -> None:
    with pytest.raises(RuntimeError) as excinfo:
        _parse_cors_origins("*")
    message = str(excinfo.value)
    assert "*" in message
    assert ENV_CORS_ORIGINS in message


def test_parse_origins_rejects_wildcard_among_explicit_origins() -> None:
    with pytest.raises(RuntimeError):
        _parse_cors_origins("https://a.example, *")


# -- create_app CORS posture ---------------------------------------------------


def test_default_app_installs_no_cors_middleware() -> None:
    # No allowlist configured (scrubbed by the autouse fixture).
    app = create_app()
    assert _cors_allow_origins(app) is None


def test_empty_allowlist_installs_no_cors_middleware(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(ENV_CORS_ORIGINS, "  ,  ")
    app = create_app()
    assert _cors_allow_origins(app) is None


def test_allowlist_installs_closed_cors_middleware(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        ENV_CORS_ORIGINS, "https://spectator.example, https://ops.example"
    )
    app = create_app()

    origins = _cors_allow_origins(app)
    assert origins == ["https://spectator.example", "https://ops.example"]
    # Closed allowlist: no wildcard ever reaches the served policy.
    assert "*" not in (origins or [])


def test_wildcard_allowlist_rejected_at_app_build(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(ENV_CORS_ORIGINS, "*")
    with pytest.raises(RuntimeError):
        create_app()


# -- docker-compose loopback publish -------------------------------------------


def test_docker_compose_publishes_on_loopback_only() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    # The host publish is scoped to 127.0.0.1 so `docker compose up` does not
    # expose the unauthenticated GM view to the LAN (audit C-C-1).
    assert "127.0.0.1:${AILIBI_API_PORT:-8000}:8000" in compose


def test_docker_compose_forwards_cors_allowlist_into_container() -> None:
    compose = Path("docker-compose.yml").read_text(encoding="utf-8")
    # Compose does not pass host/.env vars into the container automatically, so
    # the allowlist must be declared in the service environment or it is a
    # silent no-op on the compose path. The empty default keeps the closed
    # posture (an empty value installs no CORS middleware).
    assert 'AILIBI_CORS_ORIGINS: "${AILIBI_CORS_ORIGINS:-}"' in compose
