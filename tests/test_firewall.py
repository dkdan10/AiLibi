from __future__ import annotations

import subprocess
from pathlib import Path


def test_agents_cannot_import_engine() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bad_import = repo_root / "agents" / "_firewall_bad_import.py"
    bad_import.write_text("import engine\n", encoding="utf-8")

    try:
        result = subprocess.run(
            ["uv", "run", "lint-imports", "--no-cache"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
        assert result.returncode != 0
        assert "agents._firewall_bad_import" in result.stdout
        assert "engine" in result.stdout
    finally:
        bad_import.unlink(missing_ok=True)


def test_agents_cannot_reach_engine_through_observation() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    bridge = repo_root / "observation" / "_firewall_engine_bridge.py"
    bad_import = repo_root / "agents" / "_firewall_bad_transitive_import.py"
    bridge.write_text("import engine\n", encoding="utf-8")
    bad_import.write_text(
        "import observation._firewall_engine_bridge\n", encoding="utf-8"
    )

    try:
        result = subprocess.run(
            ["uv", "run", "lint-imports", "--no-cache"],
            cwd=repo_root,
            capture_output=True,
            check=False,
            text=True,
        )
        assert result.returncode != 0
        assert "agents._firewall_bad_transitive_import" in result.stdout
        assert "engine" in result.stdout
    finally:
        bad_import.unlink(missing_ok=True)
        bridge.unlink(missing_ok=True)


def test_agent_visible_observation_schemas_have_no_engine_imports() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    schema_paths = (
        repo_root / "observation" / "action_intent.py",
        repo_root / "observation" / "packet.py",
        repo_root / "observation" / "public_map.py",
    )

    for schema_path in schema_paths:
        source = schema_path.read_text(encoding="utf-8")
        assert "from engine" not in source
        assert "import engine" not in source
