"""Execute the shared gate against recording, failure-injectable tool stubs.

Every mandatory leg must run and its failure must stop the gate. Temporary
script mutations prove that omitted checks and ignored failures are detected.
Explicit frontend opt-out and serial pytest remain supported; bare pytest
stays serial. No real check, install, or network operation runs in this harness.
"""

from __future__ import annotations

import os
import shlex
import stat
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pytest

_REPO_ROOT: Final = Path(__file__).resolve().parents[2]
_CHECK_SH: Final = _REPO_ROOT / "scripts" / "check.sh"
_PYPROJECT: Final = _REPO_ROOT / "pyproject.toml"

#: The escape hatch the script reads. No test reads it — the root conftest
#: clears the whole ``AILIBI_*`` namespace, so a test that did would be reading
#: a name that is never set.
_SERIAL_ENV: Final = "AILIBI_PYTEST_SERIAL"


@dataclass(frozen=True)
class _Invocation:
    command: str
    cwd: Path


def _stub_tool_tree(tmp_path: Path) -> tuple[Path, Path]:
    """Record both tools' invocations, failing only the selected command."""

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gate-argv.log"
    for program in ("uv", "npm"):
        stub = bin_dir / program
        stub.write_text(
            "#!/usr/bin/env bash\n"
            f'command="{program} $*"\n'
            f'printf "%q " "$(pwd -P)" {program} "$@" >> "$GATE_ARGV_LOG"\n'
            'printf "\\n" >> "$GATE_ARGV_LOG"\n'
            'if [ "$command" = "${FAIL_GATE_COMMAND:-}" ]; then exit 73; fi\n'
            "exit 0\n",
            encoding="utf-8",
        )
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return bin_dir, log


def _run_check(
    tmp_path: Path,
    *,
    serial: str | None,
    skip_frontend: str | None = "1",
    source: str | None = None,
    fail_command: str | None = None,
) -> tuple[subprocess.CompletedProcess[str], list[_Invocation]]:
    """Run a temporary gate copy in a minimal workspace with both tools stubbed."""

    bin_dir, log = _stub_tool_tree(tmp_path)
    workspace = tmp_path / "workspace"
    (workspace / "frontend").mkdir(parents=True)
    (workspace / "frontend" / "package.json").write_text("{}\n", encoding="utf-8")
    script = workspace / "check.sh"
    script.write_text(
        _CHECK_SH.read_text(encoding="utf-8") if source is None else source,
        encoding="utf-8",
    )
    env = dict(os.environ)
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["GATE_ARGV_LOG"] = str(log)
    env["FAIL_GATE_COMMAND"] = fail_command or ""
    if skip_frontend is None:
        env.pop("AILIBI_SKIP_FRONTEND", None)
    else:
        env["AILIBI_SKIP_FRONTEND"] = skip_frontend
    if serial is None:
        env.pop(_SERIAL_ENV, None)
    else:
        env[_SERIAL_ENV] = serial
    result = subprocess.run(
        ["bash", str(script)],
        cwd=workspace,
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    recorded: list[_Invocation] = []
    if log.exists():
        for line in log.read_text(encoding="utf-8").splitlines():
            directory, *argv = shlex.split(line)
            recorded.append(
                _Invocation(
                    command=shlex.join(argv),
                    cwd=Path(directory).resolve().relative_to(workspace.resolve()),
                )
            )
    return result, recorded


def _pytest_lines(recorded: list[_Invocation]) -> list[str]:
    return [
        item.command.removeprefix("uv ")
        for item in recorded
        if item.command.startswith("uv run pytest")
    ]


def _required_commands(serial: str | None) -> tuple[str, ...]:
    """The checks promised by the shared gate, in fail-fast execution order."""

    return (
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run lint-imports",
        "uv run python scripts/validate_task_docs.py",
        "uv run python scripts/generate_prompts.py --check",
        "uv run mypy .",
        "uv run pytest" if serial == "1" else "uv run pytest -n auto --dist loadfile",
        "npm run lint",
        "npm run tsc:check",
        "npm run test",
        "npm run build",
    )


def _assert_required_gate(
    result: subprocess.CompletedProcess[str],
    recorded: list[_Invocation],
    *,
    serial: str | None,
    fail_command: str | None = None,
    frontend: bool = True,
) -> None:
    """Check observed execution and failure propagation, not script spelling."""

    expected = _required_commands(serial)
    if not frontend:
        expected = tuple(command for command in expected if command.startswith("uv "))
    if fail_command is None:
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode != 0, f"gate ignored failure of {fail_command}"
        expected = expected[: expected.index(fail_command) + 1]
    expected_invocations = [
        _Invocation(command, Path("frontend" if command.startswith("npm ") else "."))
        for command in expected
    ]
    assert recorded == expected_invocations, (
        "mandatory checks were omitted, reordered, ran in the wrong directory, "
        "or continued after failure"
    )


@pytest.mark.parametrize("serial", [None, "1"])
@pytest.mark.parametrize("skip_frontend", [None, "0"])
def test_every_mandatory_leg_runs(
    tmp_path: Path, serial: str | None, skip_frontend: str | None
) -> None:
    result, recorded = _run_check(tmp_path, serial=serial, skip_frontend=skip_frontend)
    _assert_required_gate(result, recorded, serial=serial)


@pytest.mark.parametrize("serial", [None, "1"])
@pytest.mark.parametrize("command_index", range(len(_required_commands(None))))
def test_each_mandatory_failure_stops_the_gate(
    tmp_path: Path, serial: str | None, command_index: int
) -> None:
    command = _required_commands(serial)[command_index]
    result, recorded = _run_check(
        tmp_path, serial=serial, skip_frontend=None, fail_command=command
    )
    _assert_required_gate(result, recorded, serial=serial, fail_command=command)


@pytest.mark.parametrize("serial", [None, "1"])
@pytest.mark.parametrize("command_index", range(len(_required_commands(None))))
@pytest.mark.parametrize("mutation", ["remove", "ignore-failure"])
def test_gate_contract_rejects_each_omission_and_ignored_failure(
    tmp_path: Path, serial: str | None, command_index: int, mutation: str
) -> None:
    command = _required_commands(serial)[command_index]
    source = _CHECK_SH.read_text(encoding="utf-8")
    # Match a command boundary so the serial pytest line does not also replace
    # the parallel invocation. This spelling check applies only to the plant.
    suffix = (
        " &&" if command.startswith("npm ") and command != "npm run build" else "\n"
    )
    if command == "npm run build":
        suffix = ")\n"
    assert source.count(command + suffix) == 1
    replacement = ":" if mutation == "remove" else f"({command} || true)"
    source = source.replace(command + suffix, replacement + suffix, 1)
    failing = command if mutation == "ignore-failure" else None
    result, recorded = _run_check(
        tmp_path,
        serial=serial,
        skip_frontend=None,
        source=source,
        fail_command=failing,
    )

    with pytest.raises(AssertionError, match="mandatory checks|ignored failure"):
        _assert_required_gate(result, recorded, serial=serial, fail_command=failing)


def test_gate_contract_preserves_argument_boundaries(tmp_path: Path) -> None:
    source = _CHECK_SH.read_text(encoding="utf-8").replace(
        "uv run ruff check .", 'uv "run ruff check ."', 1
    )
    result, recorded = _run_check(
        tmp_path, serial=None, skip_frontend=None, source=source
    )
    with pytest.raises(AssertionError, match="mandatory checks"):
        _assert_required_gate(result, recorded, serial=None)


@pytest.mark.parametrize(
    ("original", "replacement"),
    [
        ("(cd frontend && npm run lint", "(true && npm run lint"),
        ("uv run ruff check .", "(cd frontend && uv run ruff check .)"),
    ],
    ids=["frontend-in-root", "python-in-frontend"],
)
def test_gate_contract_rejects_the_wrong_working_directory(
    tmp_path: Path, original: str, replacement: str
) -> None:
    source = _CHECK_SH.read_text(encoding="utf-8")
    assert source.count(original) == 1
    source = source.replace(original, replacement, 1)
    result, recorded = _run_check(
        tmp_path, serial=None, skip_frontend=None, source=source
    )
    with pytest.raises(AssertionError, match="wrong directory"):
        _assert_required_gate(result, recorded, serial=None)


@pytest.mark.parametrize("serial", [None, "1"])
def test_frontend_opt_out_preserves_every_python_check(
    tmp_path: Path, serial: str | None
) -> None:
    result, recorded = _run_check(tmp_path, serial=serial, skip_frontend="1")
    _assert_required_gate(result, recorded, serial=serial, frontend=False)
    assert "Skipping frontend checks (AILIBI_SKIP_FRONTEND=1)" in result.stderr


def test_an_unrecognised_frontend_opt_out_fails_before_any_check(
    tmp_path: Path,
) -> None:
    result, recorded = _run_check(tmp_path, serial=None, skip_frontend="true")
    assert result.returncode != 0
    assert "AILIBI_SKIP_FRONTEND must be 0 or 1 (got 'true')" in result.stderr
    assert recorded == []


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
