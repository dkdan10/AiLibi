from __future__ import annotations

import importlib


_PUBLIC_PACKAGES = (
    "agents",
    "agents.memory",
    "agents.strategic",
    "agents.strategic.prompts",
    "agents.tactical",
    "api",
    "engine",
    "eval",
    "llm",
    "meetings",
    "observation",
    "orchestrator",
)


def test_smoke() -> None:
    assert True


def test_public_packages_import() -> None:
    for module_name in _PUBLIC_PACKAGES:
        importlib.import_module(module_name)
