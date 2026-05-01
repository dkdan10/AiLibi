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
