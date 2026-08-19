"""How ``scripts/check.sh`` invokes pytest, pinned against silent regression.

Two properties matter and neither is visible from a passing suite:

* the gate runs the default tier ACROSS WORKERS — dropping the ``-n`` flags
  would still be green, just four times slower, and nobody would notice;
* ``AILIBI_PYTEST_SERIAL`` still buys a single-process run, and an unrecognised
  value fails loudly instead of being read as "parallel anyway" — a typo'd
  ``AILIBI_PYTEST_SERIAL=true`` that silently parallelised is exactly the
  situation the operator reached for the variable to escape.

The parallel flags deliberately live here and not in pyproject's ``addopts``,
so a bare ``uv run pytest <node-id>`` stays single-process and debuggable; that
separation is pinned too.

The checks read the script's bytes and run it as a subprocess with a stub
``uv`` on ``PATH`` — no leg of the real gate runs, so the pins cost milliseconds
and cannot recurse into the suite that is asserting them.
"""

from __future__ import annotations

import os
import shlex
import stat
import subprocess
import tomllib
from pathlib import Path
from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[2]
_CHECK_SH: Final = _REPO_ROOT / "scripts" / "check.sh"
_PYPROJECT: Final = _REPO_ROOT / "pyproject.toml"

#: The escape hatch the script reads. No test reads it — the root conftest
#: clears the whole ``AILIBI_*`` namespace, so a test that did would be reading
#: a name that is never set.
_SERIAL_ENV: Final = "AILIBI_PYTEST_SERIAL"


def _stub_uv_tree(tmp_path: Path) -> tuple[Path, Path]:
    """A ``PATH`` holding a ``uv`` that records its argv instead of running it."""

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "uv-argv.log"
    stub = bin_dir / "uv"
    stub.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$UV_ARGV_LOG"\nexit 0\n',
        encoding="utf-8",
    )
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return bin_dir, log


def _run_check(
    tmp_path: Path, *, serial: str | None
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    """Run check.sh against the stub ``uv``; return the result and its argv log."""

    bin_dir, log = _stub_uv_tree(tmp_path)
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["UV_ARGV_LOG"] = str(log)
    # The frontend leg shells out to npm, which the stub does not cover.
    env["AILIBI_SKIP_FRONTEND"] = "1"
    if serial is None:
        env.pop(_SERIAL_ENV, None)
    else:
        env[_SERIAL_ENV] = serial
    result = subprocess.run(
        ["bash", str(_CHECK_SH)],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    recorded = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    return result, recorded


def _pytest_lines(recorded: list[str]) -> list[str]:
    return [line for line in recorded if line.startswith("run pytest")]


def test_the_default_gate_runs_pytest_across_workers(tmp_path: Path) -> None:
    result, recorded = _run_check(tmp_path, serial=None)

    assert result.returncode == 0, result.stderr
    assert _pytest_lines(recorded) == ["run pytest -n auto --dist loadfile"]


def test_the_serial_hatch_runs_one_process(tmp_path: Path) -> None:
    result, recorded = _run_check(tmp_path, serial="1")

    assert result.returncode == 0, result.stderr
    assert _pytest_lines(recorded) == ["run pytest"]
    assert "AILIBI_PYTEST_SERIAL=1" in result.stderr


def test_an_unrecognised_serial_value_fails_loudly(tmp_path: Path) -> None:
    result, recorded = _run_check(tmp_path, serial="true")

    assert result.returncode != 0
    assert "AILIBI_PYTEST_SERIAL must be 0 or 1 (got 'true')" in result.stderr
    # It fails BEFORE any leg runs, so a typo costs a second, not ten minutes.
    assert recorded == []


def test_zero_is_the_parallel_default_not_a_third_state(tmp_path: Path) -> None:
    _, explicit_zero = _run_check(tmp_path, serial="0")

    assert _pytest_lines(explicit_zero) == ["run pytest -n auto --dist loadfile"]


def test_addopts_does_not_parallelise_a_bare_pytest() -> None:
    """A single-node-id debug run must stay in one process."""

    options = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))["tool"]["pytest"][
        "ini_options"
    ]
    addopts = options["addopts"]
    assert isinstance(addopts, str)
    parallel = [
        token
        for token in shlex.split(addopts)
        if token.startswith(("-n", "--dist", "--numprocesses"))
    ]
    assert parallel == [], (
        "addopts carries a pytest-xdist flag, so `uv run pytest <node-id>` would "
        f"fan out across workers instead of staying debuggable: {parallel}"
    )


def test_pytest_xdist_is_declared_in_the_dev_group() -> None:
    """The gate's parallelism is a pinned dependency, not an ambient one."""

    project = tomllib.loads(_PYPROJECT.read_text(encoding="utf-8"))
    dev = project["dependency-groups"]["dev"]
    assert any(str(entry).startswith("pytest-xdist==") for entry in dev), dev
