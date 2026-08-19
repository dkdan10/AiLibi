"""The process environment the suite runs in.

The root conftest's hermetic guard — applied when that file is imported and held by
``_hermetic_ailibi_env`` — promises one thing: a test sees the environment CI
exports, none of the ``AILIBI_*`` knobs and neither provider key, whatever the
developer's shell exports. Checking that promise only from inside the suite would
pass vacuously on a bare shell, which is every shell until the day it is not, so the
checks come in four layers: the in-process surface, the clear policy under planted
dirty environments, the allow-list against the suite's own import-time reads, and one
child ``pytest`` launched with the ambient values the guard exists to remove.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Final

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE
from tests.conftest import (
    ENV_PREFIX,
    GATE_CARRIED_ENV,
    OPT_IN_GATES,
    PROVIDER_KEYS,
    env_names_to_clear,
)

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]

#: A gate value that is exported but is not the opt-in ``"1"``.
_GATE_OFF: Final = "0"


def _allowed_prefixed_names(environ: Mapping[str, str]) -> set[str]:
    """Every ``AILIBI_*`` name the guard may leave behind in ``environ``."""

    allowed = {ENV_PROVIDER, *OPT_IN_GATES}
    for gate, carried in GATE_CARRIED_ENV.items():
        if environ.get(gate) == "1":
            allowed.update(name for name in carried if name.startswith(ENV_PREFIX))
    return allowed


# --------------------------------------------------------------------------- #
# 1. the in-process surface                                                    #
# --------------------------------------------------------------------------- #


def test_the_ailibi_surface_is_exactly_what_the_fixture_allows() -> None:
    """No ambient knob reaches a test, and the provider is the fake adapter."""

    present = {name for name in os.environ if name.startswith(ENV_PREFIX)}
    leaked = sorted(present - _allowed_prefixed_names(os.environ))
    assert leaked == [], (
        f"ambient {ENV_PREFIX}* names reached the suite: {leaked}; "
        "tests/conftest.py's hermetic guard should have cleared them"
    )
    assert os.environ[ENV_PROVIDER] == PROVIDER_FAKE


def test_provider_keys_survive_only_behind_the_real_provider_gate() -> None:
    """A stray API key with the gate off is cleared — nothing can go paid."""

    if os.environ.get("AILIBI_RUN_REAL_PROVIDER_TESTS") == "1":
        return
    for key in PROVIDER_KEYS:
        assert key not in os.environ, (
            f"{key} is visible to the suite with the real-provider gate off"
        )


# --------------------------------------------------------------------------- #
# 2. the clear policy, under planted dirty environments                        #
# --------------------------------------------------------------------------- #


def test_a_dirty_environment_is_cleared_whole() -> None:
    dirty = {
        "AILIBI_MAX_COST_USD": "0.001",
        "AILIBI_SAMPLES_ROOT": "/somewhere/else",
        "AILIBI_LLM_PROVIDER": "anthropic",
        "ANTHROPIC_API_KEY": "planted",
        "FEATHERLESS_API_KEY": "planted",
        "PATH": "/usr/bin",
        "HOME": "/home/nobody",
    }
    assert env_names_to_clear(dirty) == frozenset(dirty) - {"PATH", "HOME"}


def test_an_opt_in_gate_carries_its_credentials_and_endpoints() -> None:
    """With every gate opted in, only the non-gate knobs are cleared."""

    dirty = {
        "AILIBI_RUN_REAL_PROVIDER_TESTS": "1",
        "AILIBI_RUN_OLLAMA_TESTS": "1",
        "AILIBI_RUN_PERF_BENCHMARK": "1",
        "ANTHROPIC_API_KEY": "planted",
        "FEATHERLESS_API_KEY": "planted",
        "AILIBI_LLM_MEETING_MODEL": "Qwen/Qwen3.6-27B",
        "AILIBI_OLLAMA_HOST": "http://localhost:11434",
        "AILIBI_MAX_COST_USD": "0.001",
    }
    assert env_names_to_clear(dirty) == frozenset({"AILIBI_MAX_COST_USD"})


def test_a_gate_that_is_not_opted_in_carries_nothing() -> None:
    """The gate itself survives (a skipif already read it); its payload does not."""

    dirty = {
        "AILIBI_RUN_REAL_PROVIDER_TESTS": _GATE_OFF,
        "AILIBI_RUN_OLLAMA_TESTS": "true",
        "ANTHROPIC_API_KEY": "planted",
        "FEATHERLESS_API_KEY": "planted",
        "AILIBI_LLM_MEETING_MODEL": "Qwen/Qwen3.6-27B",
        "AILIBI_OLLAMA_HOST": "http://localhost:11434",
    }
    assert env_names_to_clear(dirty) == frozenset(
        {
            "ANTHROPIC_API_KEY",
            "FEATHERLESS_API_KEY",
            "AILIBI_LLM_MEETING_MODEL",
            "AILIBI_OLLAMA_HOST",
        }
    )


def test_names_outside_the_namespace_are_never_touched() -> None:
    """The clear is a prefix rule plus two named keys, not a guess at intent."""

    dirty = {
        "PATH": "/usr/bin",
        "CI": "1",
        "AILIBILOOKALIKE": "no underscore, no match",
        "ailibi_max_cost_usd": "lowercase is a different name",
        "PREFIXED_AILIBI_NUM_PLAYERS": "9",
    }
    assert env_names_to_clear(dirty) == frozenset()


def test_the_clear_is_derived_from_the_environment_not_from_a_known_list() -> None:
    """A knob invented after this fixture was written is still cleared."""

    assert env_names_to_clear({"AILIBI_A_KNOB_NOBODY_HAS_WRITTEN_YET": "x"}) == (
        frozenset({"AILIBI_A_KNOB_NOBODY_HAS_WRITTEN_YET"})
    )


# --------------------------------------------------------------------------- #
# 3. the allow-list against the suite's own import-time reads                  #
# --------------------------------------------------------------------------- #


def _executed_at_import(source: str) -> Iterator[ast.AST]:
    """Nodes reachable without entering a function body or a lambda.

    Class bodies stay in: they run at import too. ``ast.walk`` cannot express this
    because it has no way to prune a subtree.
    """

    stack: list[ast.AST] = list(ast.parse(source).body)
    while stack:
        node = stack.pop()
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            continue
        yield node
        stack.extend(ast.iter_child_nodes(node))


def _import_time_env_reads(source: str) -> set[str]:
    """``AILIBI_*`` names ``source`` reads at MODULE level, i.e. during collection.

    A read at module level binds a value for the whole run and cannot be overridden
    per test, so each one is a standing decision about the environment surface — the
    kind that should be listed rather than discovered.
    """

    found: set[str] = set()
    for node in _executed_at_import(source):
        key: ast.expr | None = None
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
            and _is_os_environ(node.func.value)
        ):
            key = node.args[0]
        elif isinstance(node, ast.Subscript) and _is_os_environ(node.value):
            key = node.slice
        if (
            isinstance(key, ast.Constant)
            and isinstance(key.value, str)
            and key.value.startswith(ENV_PREFIX)
        ):
            found.add(key.value)
    return found


def _is_os_environ(node: ast.expr) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "environ"
        and isinstance(node.value, ast.Name)
        and node.value.id == "os"
    )


def _tracked_test_modules() -> list[Path]:
    listing = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files", "--", "tests"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return [_REPO_ROOT / rel for rel in listing if rel.endswith(".py")]


def test_every_import_time_env_read_is_an_allow_listed_gate() -> None:
    """The names bound at collection time are exactly the ones deliberately kept.

    A module-level read sees the already-cleared environment, so a name read there
    and *not* preserved silently resolves to its default for the whole run. Add a
    fourth import-time read and this reds until the allow-list names it, or until the
    read moves inside a function where a test can override it.
    """

    modules = _tracked_test_modules()
    assert modules, "no tracked test modules found"
    read_at_import: set[str] = set()
    for path in modules:
        read_at_import |= _import_time_env_reads(path.read_text())
    assert read_at_import == set(OPT_IN_GATES)


def test_the_import_time_reader_sees_a_planted_gate_and_ignores_a_call_time_one() -> (
    None
):
    """The extractor above bites: module level counts, function body does not."""

    planted = (
        "import os\n"
        "import pytest\n"
        'gate = pytest.mark.skipif(os.environ.get("AILIBI_PLANTED_GATE") != "1", "")\n'
        'other = os.environ["AILIBI_PLANTED_SUBSCRIPT"]\n'
        "def test_x() -> None:\n"
        '    assert os.environ.get("AILIBI_READ_AT_CALL_TIME") is None\n'
    )
    assert _import_time_env_reads(planted) == {
        "AILIBI_PLANTED_GATE",
        "AILIBI_PLANTED_SUBSCRIPT",
    }


# --------------------------------------------------------------------------- #
# 4. the fixture itself, perturbed from outside the process                    #
# --------------------------------------------------------------------------- #


def test_the_fixture_bites_on_a_planted_ambient_environment() -> None:
    """Export the values the guard exists to remove, then re-run the surface check.

    A child ``pytest`` is the only vantage point that can tell "the guard cleared
    them" apart from "this shell never exported them": the control below proves the
    planted values do reach a child of this process, so the green run that follows is
    attributable to the guard.
    """

    planted = {
        "AILIBI_MAX_COST_USD": "0.001",
        "AILIBI_NUM_PLAYERS": "9",
        "ANTHROPIC_API_KEY": "planted-not-a-real-key",
        "FEATHERLESS_API_KEY": "planted-not-a-real-key",
    }
    child_env = {**os.environ, **planted}

    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import json, os; print(json.dumps(sorted(os.environ)))",
        ],
        env=child_env,
        check=True,
        capture_output=True,
        text=True,
    )
    assert set(planted) <= set(json.loads(probe.stdout)), (
        "the planted values did not reach a child process; the run below would be "
        "green for the wrong reason"
    )

    node_id = (
        f"{Path(__file__).resolve().relative_to(_REPO_ROOT).as_posix()}"
        f"::{test_the_ailibi_surface_is_exactly_what_the_fixture_allows.__name__}"
    )
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", node_id],
        cwd=_REPO_ROOT,
        env=child_env,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
