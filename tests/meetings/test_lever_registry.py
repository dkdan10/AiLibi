"""No accept-and-ignore lever resolver may reappear in the substrate packages.

A lever graduates by DELETING its resolver, its parameter, the dead ``if`` and
the tests that pin them -- keeping only its key in
``orchestrator.replay._RETIRED_ALWAYS_ON_LEVERS`` and one history line
(AGENTS.md "Graduation sweeps" / craft rule 3). Before Task 20.37 the repo
instead kept seventeen functions of the shape::

    def x_enabled(env: Mapping[str, str] | None = None) -> bool:
        del env
        return True

-- 332 source lines describing a switch that no longer existed. This module is
the structural gate that stops them regenerating: it walks every module under
``agents/``, ``meetings/`` and ``orchestrator/`` with :mod:`ast` and fails on any
function whose name ends ``_enabled`` and whose body neither reads its ``env``
argument nor returns anything but a bare ``True``.

The gate ships with a planted counter-case: a fixture module written into
``tmp_path`` carrying exactly that shape, asserted to be REPORTED by the same
predicate the sweep uses. A live resolver (one that reads ``env``) is asserted
clean by the same predicate, so the gate discriminates rather than matching on
the name alone.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Final

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_SWEPT_PACKAGES: Final[tuple[str, ...]] = ("agents", "meetings", "orchestrator")


def _is_bare_true_return(node: ast.stmt) -> bool:
    """``return True`` -- the whole body of an accept-and-ignore resolver."""

    return (
        isinstance(node, ast.Return)
        and isinstance(node.value, ast.Constant)
        and node.value.value is True
    )


def _reads_env(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether the body LOADS the ``env`` name anywhere.

    ``del env`` is a Del context and a bare annotation is a Store, so neither
    counts: only an actual read of the argument makes the parameter live.
    """

    return any(
        isinstance(node, ast.Name)
        and node.id == "env"
        and isinstance(node.ctx, ast.Load)
        for node in ast.walk(func)
    )


def accept_and_ignore_resolvers(source: str) -> list[str]:
    """Names of the ``*_enabled`` functions in ``source`` that are pure ``True``.

    A resolver is reported when its name ends ``_enabled``, its body reads no
    ``env``, and every statement it executes is either a docstring, a ``del`` or
    ``return True``. That is exactly the graduated-but-undeleted shape; a
    resolver that branches, or that reads its argument, is a LIVE toggle and is
    never reported.
    """

    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.endswith("_enabled"):
            continue
        if _reads_env(node):
            continue
        body = [
            stmt
            for stmt in node.body
            if not (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            )
        ]
        if not body:
            continue
        if all(
            isinstance(stmt, ast.Delete) or _is_bare_true_return(stmt) for stmt in body
        ):
            found.append(node.name)
    return found


def test_no_accept_and_ignore_resolver_survives() -> None:
    offenders: list[str] = []
    for package in _SWEPT_PACKAGES:
        for path in sorted((_REPO_ROOT / package).rglob("*.py")):
            for name in accept_and_ignore_resolvers(path.read_text(encoding="utf-8")):
                offenders.append(f"{path.relative_to(_REPO_ROOT)}::{name}")
    assert offenders == [], (
        "graduated levers must be DELETED, not left as accept-and-ignore "
        f"resolvers (AGENTS.md craft rule 3): {offenders}"
    )


def test_the_gate_bites_on_a_planted_resolver(tmp_path: Path) -> None:
    # The perturbation: a module carrying exactly the retired shape must be
    # REPORTED, or the sweep above is prose. Written to disk and read back
    # through the same path the sweep uses.
    planted = tmp_path / "planted_lever.py"
    planted.write_text(
        "from collections.abc import Mapping\n"
        "\n"
        "\n"
        "def graduated_thing_enabled(env: Mapping[str, str] | None = None) -> bool:\n"
        '    """Whether the thing is on -- now always True."""\n'
        "\n"
        "    del env\n"
        "    return True\n",
        encoding="utf-8",
    )

    assert accept_and_ignore_resolvers(planted.read_text(encoding="utf-8")) == [
        "graduated_thing_enabled"
    ]


def test_the_gate_leaves_a_live_resolver_alone(tmp_path: Path) -> None:
    # The discrimination half: a resolver that READS its env argument is a live
    # toggle and must not be reported, so the gate cannot be satisfied by
    # deleting the one lever the project still switches.
    live = tmp_path / "live_lever.py"
    live.write_text(
        "import os\n"
        "from collections.abc import Mapping\n"
        "\n"
        "\n"
        "def live_thing_enabled(env: Mapping[str, str] | None = None) -> bool:\n"
        '    """Whether the live toggle is on."""\n'
        "\n"
        "    environment = env if env is not None else os.environ\n"
        '    return environment.get("AILIBI_LIVE_THING", "") == "1"\n',
        encoding="utf-8",
    )

    assert accept_and_ignore_resolvers(live.read_text(encoding="utf-8")) == []


def test_the_one_live_resolver_in_the_tree_is_not_reported() -> None:
    # The real discrimination case, not a fixture: the 18.10 impostor-answer arm
    # is the project's one surviving toggle and both its resolvers read env, so
    # the sweep passing above is a statement about deletion, not about the tree
    # having no ``*_enabled`` function left at all.
    loader = _REPO_ROOT / "agents" / "strategic" / "prompts" / "loader.py"
    mirror = _REPO_ROOT / "orchestrator" / "replay.py"
    source = loader.read_text(encoding="utf-8") + mirror.read_text(encoding="utf-8")
    assert "impostor_roll_call_enabled" in source
    assert accept_and_ignore_resolvers(source) == []
