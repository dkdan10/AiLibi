"""The static half of the observation firewall: two independent gates.

``import-linter`` walks the import graph of every root package in
``.importlinter`` and proves the transitive claim — ``agents/`` reaches
``engine/`` by no route, however long. That holds only while every route stays
inside the graph, so the AST source scan below covers the two ways out: the
external packages grimp never sees (``numpy``, ``torch``, banned under
``agents/`` by the pure-Python inference doctrine) and the packages left out of
the graph on purpose (``tests``, ``experiments``, ``audits``, ``design``), where
a traversal stops dead and whatever follows is unseen.

The scan is stated as a CLOSURE, not a list of places to look. ``agents``,
``llm``, ``meetings`` and ``observation`` are the firewall's interior; no file
in any of them may import an ungraphed package, nor any configured root outside
the interior — otherwise a bridge planted one hop out
(``agents -> observation -> orchestrator._bridge -> tests._helpers -> engine``)
walks to the engine with neither layer seeing it. Naming the interior makes the
gate safe by default: a package added to ``root_packages`` later lands outside
and is banned until someone moves it in. A covering assertion pins the pair, so
a new top-level package must join one list or the other to land.

Every planted-failure leg writes into a throwaway copy of the source tree under
``tmp_path`` and runs the linter there. Nothing here writes inside the checkout:
a concurrent ``lint-imports`` can never see a synthetic violation, an
interrupted run leaves no residue, and parallel pytest workers cannot collide.
"""

from __future__ import annotations

import ast
import configparser
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import KilledEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from observation.service import ObservationService
from tests._helpers.world_state import scripted_initial_world_state

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable, Iterator

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_IMPORT_LINTER_CONFIG = _REPO_ROOT / ".importlinter"
_ENGINE_CONTRACT = "Agents must not import engine"


# --------------------------------------------------------------------------- #
# Reading the committed configuration and the tracked tree.                    #
# --------------------------------------------------------------------------- #


def _configured_root_packages() -> tuple[str, ...]:
    """The ``root_packages`` list of the committed ``.importlinter``."""

    parser = configparser.ConfigParser()
    parser.read(_IMPORT_LINTER_CONFIG, encoding="utf-8")
    return tuple(parser["importlinter"]["root_packages"].split())


def _modules_agents_may_not_import() -> frozenset[str]:
    """What the committed ``forbidden`` contracts put out of ``agents/``'s reach."""

    parser = configparser.ConfigParser()
    parser.read(_IMPORT_LINTER_CONFIG, encoding="utf-8")
    forbidden: set[str] = set()
    for section in parser.sections():
        options = parser[section]
        if options.get("type") != "forbidden":
            continue
        if "agents" not in options.get("source_modules", "").split():
            continue
        forbidden.update(options.get("forbidden_modules", "").split())
    return frozenset(forbidden)


def _tracked_python_paths() -> tuple[str, ...]:
    """Every ``.py`` file git tracks, as repo-relative POSIX paths.

    Tracked, not globbed: the point is what a contributor can commit, and a
    filesystem walk would sweep in ``.venv`` and other untracked noise.
    """

    result = subprocess.run(
        ["git", "ls-files", "-z", "*.py"],
        cwd=_REPO_ROOT,
        capture_output=True,
        check=True,
        text=True,
    )
    return tuple(path for path in result.stdout.split("\0") if path)


def _top_level_names(paths: Iterable[str]) -> set[str]:
    """The top-level importable name each path contributes.

    A file inside a directory contributes the directory (``agents/x.py`` ->
    ``agents``); a file at the repository root contributes its own module name
    (``bridge.py`` -> ``bridge``), because that is what ``import bridge`` would
    resolve to. A root-level module belongs to no linter root, so it has to be
    accounted for exactly like a package or it slips past both layers.
    """

    names: set[str] = set()
    for path in paths:
        pure = PurePosixPath(path)
        names.add(pure.parts[0] if len(pure.parts) > 1 else pure.stem)
    return names


def _uncovered_top_level_names(
    paths: Iterable[str],
    root_packages: Collection[str],
    banned: Collection[str],
) -> list[str]:
    """Top-level names neither layer of the firewall can see."""

    return sorted(_top_level_names(paths) - set(root_packages) - set(banned))


# --------------------------------------------------------------------------- #
# The throwaway source tree every plant is written into.                       #
# --------------------------------------------------------------------------- #


def _lint_imports_executable() -> Path:
    """The ``lint-imports`` console script of the interpreter running the suite.

    Resolved from ``sys.executable`` rather than through ``uv run``: the linter
    is invoked with the temp copy as its cwd, and ``uv run`` would look there
    for a project to sync and find none.
    """

    candidate = Path(sys.executable).with_name("lint-imports")
    if candidate.is_file():
        return candidate
    found = shutil.which("lint-imports")
    if found is None:
        raise RuntimeError(
            "lint-imports is not installed in this environment; the dev "
            "dependency group provides it (bash scripts/setup_env.sh)"
        )
    return Path(found)


@dataclass(frozen=True)
class FirewallTree:
    """A copy of the source tree that plants may be written into."""

    root: Path
    config: Path

    def plant(self, relative_path: str, source: str) -> Path:
        """Write ``source`` at ``relative_path`` inside the copy."""

        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
        return target

    def lint(self) -> subprocess.CompletedProcess[str]:
        """Run ``lint-imports`` over the copy, from the copy.

        ``COLUMNS`` is pinned wide because the reporter wraps its import chains
        to the console width, and a chain split across two lines is a chain the
        assertions below cannot read.
        """

        return subprocess.run(
            [
                str(_lint_imports_executable()),
                "--config",
                str(self.config),
                "--no-cache",
            ],
            cwd=self.root,
            capture_output=True,
            check=False,
            text=True,
            env={**os.environ, "COLUMNS": "200"},
        )


@pytest.fixture
def firewall_tree(tmp_path: Path) -> Iterator[FirewallTree]:
    """A copy of every configured root package, plus a derived linter config.

    The config is PARSED from the committed ``.importlinter`` and only
    ``root_packages`` is rewritten — to the packages the copy actually holds —
    so a fifth contract added there is exercised by every planted leg below
    without anyone editing this file.
    """

    root = tmp_path / "tree"
    copied: list[str] = []
    for package in _configured_root_packages():
        source_dir = _REPO_ROOT / package
        assert source_dir.is_dir(), (
            f".importlinter names {package!r} as a root package, but the "
            "checkout has no such directory"
        )
        copied.append(package)
        for path in sorted(source_dir.rglob("*.py")):
            target = root / path.relative_to(_REPO_ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
    assert copied, "no configured root package exists in the checkout"

    parser = configparser.ConfigParser()
    parser.read(_IMPORT_LINTER_CONFIG, encoding="utf-8")
    parser["importlinter"]["root_packages"] = "\n" + "\n".join(copied)
    config = root / ".importlinter"
    with config.open("w", encoding="utf-8") as handle:
        parser.write(handle)

    yield FirewallTree(root=root, config=config)

    shutil.rmtree(root, ignore_errors=True)


def _broken_contract_chain(report: str, contract_name: str) -> str:
    """The import chain ``lint-imports`` printed under one broken contract.

    The report lists each broken contract under a ``Broken contracts`` banner,
    introduced by the contract's name over a rule of dashes; the next such rule
    ends the block.
    """

    heading = f"{contract_name}\n{'-' * len(contract_name)}\n"
    _, _, tail = report.partition("Broken contracts")
    assert heading in tail, f"{contract_name!r} is not reported broken:\n{report}"
    lines: list[str] = []
    for line in tail.split(heading, 1)[1].splitlines():
        if line and set(line) == {"-"}:
            if lines:
                lines.pop()  # the next contract's name, not part of this chain
            break
        lines.append(line)
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 1. The import-linter contracts.                                              #
# --------------------------------------------------------------------------- #


def test_the_temp_copy_reproduces_the_committed_contracts(
    firewall_tree: FirewallTree,
) -> None:
    """Unplanted, the copy is green — so a planted BROKEN below is the plant."""

    result = firewall_tree.lint()
    assert result.returncode == 0, result.stdout
    assert re.search(r"Contracts: \d+ kept, 0 broken", result.stdout), result.stdout


def test_the_temp_config_is_derived_from_the_committed_one(
    firewall_tree: FirewallTree,
) -> None:
    """Only ``root_packages`` differs; every contract section is carried over."""

    committed = configparser.ConfigParser()
    committed.read(_IMPORT_LINTER_CONFIG, encoding="utf-8")
    derived = configparser.ConfigParser()
    derived.read(firewall_tree.config, encoding="utf-8")

    assert set(derived.sections()) == set(committed.sections())
    for section in committed.sections():
        if section == "importlinter":
            continue
        assert dict(derived[section]) == dict(committed[section])
    assert derived["importlinter"]["root_packages"].split() == list(
        _configured_root_packages()
    )


@dataclass(frozen=True)
class _PlantedRoute:
    """One synthetic ``agents/`` -> ``engine/`` route and the report it forces."""

    route: str
    plants: tuple[tuple[str, str], ...]
    first_hop: str


# The three back-channels are live production chains: orchestrator/game.py,
# api/main.py and eval/leak_scan.py all reach engine/. Each was invisible to
# lint-imports until its package became a root package, so these legs fail if
# root_packages is ever narrowed again.
_PLANTED_ROUTES: tuple[_PlantedRoute, ...] = (
    _PlantedRoute(
        route="direct",
        plants=(("agents/_firewall_bad_import.py", "import engine\n"),),
        first_hop="agents._firewall_bad_import -> engine",
    ),
    _PlantedRoute(
        route="via-observation",
        plants=(
            ("observation/_firewall_engine_bridge.py", "import engine\n"),
            (
                "agents/_firewall_bad_transitive_import.py",
                "import observation._firewall_engine_bridge\n",
            ),
        ),
        first_hop=(
            "agents._firewall_bad_transitive_import -> "
            "observation._firewall_engine_bridge"
        ),
    ),
    _PlantedRoute(
        route="via-orchestrator",
        plants=(
            ("agents/_firewall_probe_orchestrator.py", "import orchestrator.game\n"),
        ),
        first_hop="agents._firewall_probe_orchestrator -> orchestrator.game",
    ),
    _PlantedRoute(
        route="via-api",
        plants=(("agents/_firewall_probe_api.py", "import api.main\n"),),
        first_hop="agents._firewall_probe_api -> api.main",
    ),
    _PlantedRoute(
        route="via-eval",
        plants=(("agents/_firewall_probe_eval.py", "import eval.leak_scan\n"),),
        first_hop="agents._firewall_probe_eval -> eval.leak_scan",
    ),
)


@pytest.mark.parametrize(
    "planted", _PLANTED_ROUTES, ids=[route.route for route in _PLANTED_ROUTES]
)
def test_import_linter_reports_a_planted_agents_to_engine_route(
    planted: _PlantedRoute, firewall_tree: FirewallTree
) -> None:
    """Each route breaks the engine contract, with its full chain named."""

    for relative_path, source in planted.plants:
        firewall_tree.plant(relative_path, source)

    result = firewall_tree.lint()

    assert result.returncode != 0, result.stdout
    assert f"{_ENGINE_CONTRACT} BROKEN" in result.stdout
    chain = _broken_contract_chain(result.stdout, _ENGINE_CONTRACT)
    hops = [line.strip().lstrip("- ") for line in chain.splitlines() if "->" in line]
    assert hops, chain
    assert hops[0].startswith(planted.first_hop), chain
    assert re.search(r"-> engine(\.\w+)*\b", hops[-1]), chain


# --------------------------------------------------------------------------- #
# 2. The AST source scan over agents/ — the grimp-independent second layer.    #
# --------------------------------------------------------------------------- #

# The top-level packages that hold tracked Python and stay OUT of the import
# graph on purpose: ``tests`` and ``experiments`` import the inner packages
# freely, and ``audits`` and ``design`` hold one-off generators. grimp builds no
# nodes for them, so a chain through one is invisible to every contract —
# ``tests._helpers.world_state`` imports ``engine``, which makes
# ``agents -> observation -> tests._helpers -> engine`` a real route no linter
# can follow. This scan is what forbids it.
_UNGRAPHED_PACKAGES = frozenset({"tests", "experiments", "audits", "design"})

# The INTERIOR of the firewall: the roots ``agents/`` may import. Naming the
# interior rather than the exterior is what makes this gate safe by default — a
# package added to ``root_packages`` later lands outside it and is banned from
# every interior package by :func:`_exterior_bans` until someone deliberately
# moves it in. The reverse spelling (a list of scanned packages) would let a new
# root join the graph and skip the scan.
_FIREWALL_INTERIOR = frozenset({"agents", "llm", "meetings", "observation"})

# Production inference under ``agents/`` is pure Python: BLAS reductions are not
# bit-stable across machines and thread counts, so numpy stays confined to
# ``training/`` and the Encoder-v2 inference path is stdlib ``math`` + lists.
# Both are external packages, invisible to any contract
# (``include_external_packages`` is unset), so this scan is their only gate.
_PURE_PYTHON_INFERENCE_BAN = frozenset({"numpy", "torch"})


def _exterior_bans_for(
    root_packages: Iterable[str],
    interior: Collection[str],
    agent_forbidden: Collection[str],
    ungraphed: Collection[str],
) -> frozenset[str]:
    """Top-level names no interior package may import.

    Two kinds, and between them they make the interior CLOSED under imports —
    which is the property the transitive claim actually needs:

    * the ungraphed packages, because the traversal stops dead at one and
      whatever it reaches afterwards is unseen; and
    * the configured roots outside the interior that no whole-root contract
      already forbids ``agents/``. Importing one of those from, say,
      ``observation/`` extends the interior into a package nothing here sweeps,
      and a bridge planted there to an ungraphed package would be invisible to
      both layers.

    ``engine`` and ``training`` are deliberately absent: both ARE whole-root
    contracts, so grimp catches any chain that passes through them, and
    ``observation/`` imports ``engine`` by design.
    """

    whole_roots = {module for module in agent_forbidden if "." not in module}
    outside = set(root_packages) - set(interior) - whole_roots
    return frozenset(set(ungraphed) | outside)


def _exterior_bans() -> frozenset[str]:
    """:func:`_exterior_bans_for` over the committed configuration."""

    return _exterior_bans_for(
        _configured_root_packages(),
        _FIREWALL_INTERIOR,
        _modules_agents_may_not_import(),
        _UNGRAPHED_PACKAGES,
    )


# ``agents/`` carries the interior's ban plus its own pure-Python doctrine. The
# scan is AST rather than substring so a docstring that legitimately NAMES a
# banned import (the encoder module documents this very ban) never
# false-positives.
_FORBIDDEN_AGENT_IMPORTS = _PURE_PYTHON_INFERENCE_BAN | _exterior_bans()

# The productized learned champion is production inference, so it inherits the
# ban above and adds the two packages import-linter already forbids agents/ —
# belt and braces on the path a training artifact is most likely to drag in.
_FORBIDDEN_LEARNED_IMPORTS = _FORBIDDEN_AGENT_IMPORTS | {"engine", "training"}


def _imported_top_level_modules(source: str) -> set[str]:
    """The set of top-level module names imported by ``source`` (AST, not substring).

    ``import a.b.c`` and ``from a.b import c`` both contribute ``"a"``. Relative
    imports (``from . import x``) contribute nothing. Docstrings and comments are
    ignored — only real ``import`` statements are inspected.
    """

    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module is not None:
                roots.add(node.module.split(".", 1)[0])
    return roots


def _package_source_files(tree_root: Path, package: str) -> list[Path]:
    return sorted((tree_root / package).rglob("*.py"))


def _agent_source_files(tree_root: Path) -> list[Path]:
    return _package_source_files(tree_root, "agents")


def _learned_package_source_files(tree_root: Path) -> list[Path]:
    return sorted((tree_root / "agents" / "tactical" / "learned").rglob("*.py"))


def _banned_importers(
    paths: Iterable[Path], banned: Collection[str]
) -> list[tuple[str, list[str]]]:
    """Every file in ``paths`` that imports one of ``banned``, and which names."""

    offenders: list[tuple[str, list[str]]] = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        hits = sorted(_imported_top_level_modules(source) & set(banned))
        if hits:
            offenders.append((str(path), hits))
    return offenders


def test_agents_import_no_forbidden_top_level_module() -> None:
    offenders = _banned_importers(
        _agent_source_files(_REPO_ROOT), _FORBIDDEN_AGENT_IMPORTS
    )
    assert not offenders, (
        "agents/ must import none of "
        f"{sorted(_FORBIDDEN_AGENT_IMPORTS)}; offenders: {offenders}"
    )


@pytest.mark.parametrize("banned", sorted(_FORBIDDEN_AGENT_IMPORTS))
def test_the_agents_source_scan_rejects_every_banned_import(
    banned: str, firewall_tree: FirewallTree
) -> None:
    """A gate that cannot fail is not a gate — one planted leg per banned name."""

    planted = firewall_tree.plant(
        f"agents/_firewall_banned_{banned}.py", f"import {banned}\n"
    )
    offenders = _banned_importers(
        _agent_source_files(firewall_tree.root), _FORBIDDEN_AGENT_IMPORTS
    )
    assert (str(planted), [banned]) in offenders


def _closure_breakers(tree_root: Path) -> list[tuple[str, list[str]]]:
    """Every interior file importing something that would open the interior."""

    offenders: list[tuple[str, list[str]]] = []
    for package in sorted(_FIREWALL_INTERIOR):
        offenders.extend(
            _banned_importers(
                _package_source_files(tree_root, package), _exterior_bans()
            )
        )
    return offenders


def test_the_firewall_interior_is_configured_and_agent_legal() -> None:
    """Every interior package is a linter root that ``agents/`` may import."""

    configured = set(_configured_root_packages())
    assert _FIREWALL_INTERIOR <= configured, (
        "an interior package that is not a root_packages entry is outside the "
        f"import graph: {sorted(_FIREWALL_INTERIOR - configured)}"
    )
    whole_roots = {
        module for module in _modules_agents_may_not_import() if "." not in module
    }
    assert not (_FIREWALL_INTERIOR & whole_roots)
    # A SUBMODULE contract does not evict its root: agents/ may not import
    # meetings.manager, but it does import meetings.schemas.
    assert "meetings.manager" in _modules_agents_may_not_import()
    assert "meetings" in _FIREWALL_INTERIOR


def test_a_new_configured_root_lands_outside_the_interior() -> None:
    """Safe by default: a root added later is banned until it is moved in."""

    bans = _exterior_bans_for(
        (*_configured_root_packages(), "_firewall_new_root"),
        _FIREWALL_INTERIOR,
        _modules_agents_may_not_import(),
        _UNGRAPHED_PACKAGES,
    )
    assert "_firewall_new_root" in bans
    # Whole-root contracts stay out of the ban set: grimp walks those chains,
    # and observation/ imports engine by design.
    assert "engine" not in bans
    assert "training" not in bans


def test_the_interior_is_closed_under_imports() -> None:
    offenders = _closure_breakers(_REPO_ROOT)
    assert not offenders, (
        f"no package agents/ can reach may import {sorted(_exterior_bans())} — "
        "each one either leaves grimp's graph or extends the interior into a "
        f"package this scan does not sweep; offenders: {offenders}"
    )


@pytest.mark.parametrize("package", sorted(_FIREWALL_INTERIOR))
def test_the_closure_scan_rejects_a_bridge_in_every_interior_package(
    package: str, firewall_tree: FirewallTree
) -> None:
    """A gate that cannot fail is not a gate — one bridge per interior package."""

    planted = firewall_tree.plant(
        f"{package}/_firewall_ungraphed_bridge.py",
        "import tests._helpers.world_state\n",
    )
    assert (str(planted), ["tests"]) in _closure_breakers(firewall_tree.root)


@pytest.mark.parametrize("banned", sorted(_exterior_bans()))
def test_the_closure_scan_rejects_every_exterior_import(
    banned: str, firewall_tree: FirewallTree
) -> None:
    """...and one per banned name, planted in a non-``agents`` interior package."""

    planted = firewall_tree.plant(
        f"observation/_firewall_exterior_{banned}.py", f"import {banned}\n"
    )
    assert (str(planted), [banned]) in _closure_breakers(firewall_tree.root)


def test_a_bridge_through_an_ungraphed_package_is_the_source_scans_job(
    firewall_tree: FirewallTree,
) -> None:
    """The division of labour between the two layers, kept honest.

    ``agents -> observation._bridge -> tests._helpers -> engine`` reaches the
    engine, but ``tests`` is not a root package, so the graph traversal stops
    there and the linter reports the tree clean. The closure scan is the only
    gate that sees this route; if it were ever relaxed, this leg would still
    pass and the firewall would be open — which is why it asserts BOTH halves.
    """

    firewall_tree.plant(
        "observation/_firewall_ungraphed_bridge.py",
        "import tests._helpers.world_state\n",
    )
    firewall_tree.plant(
        "agents/_firewall_bridge_consumer.py",
        "import observation._firewall_ungraphed_bridge\n",
    )

    result = firewall_tree.lint()
    assert result.returncode == 0, result.stdout
    assert re.search(r"Contracts: \d+ kept, 0 broken", result.stdout), result.stdout

    assert [path for path, names in _closure_breakers(firewall_tree.root)] == [
        str(firewall_tree.root / "observation" / "_firewall_ungraphed_bridge.py")
    ]


def test_a_two_hop_route_out_of_the_interior_is_caught_at_the_first_hop(
    firewall_tree: FirewallTree,
) -> None:
    """``agents -> observation -> orchestrator._bridge -> tests._helpers -> engine``.

    Every hop is legal to the linter — ``orchestrator`` is graphed but the
    bridge planted in it reaches the engine only through ungraphed ``tests``, so
    the traversal stops short and the tree reports clean. Scanning ``agents/``
    alone would miss it too. The closure catches it at the
    ``observation -> orchestrator`` hop: that is the difference between an
    interior that is closed and one that is merely deep.
    """

    firewall_tree.plant(
        "orchestrator/_firewall_ungraphed_bridge.py",
        "import tests._helpers.world_state\n",
    )
    firewall_tree.plant(
        "observation/_firewall_orchestrator_hop.py",
        "import orchestrator._firewall_ungraphed_bridge\n",
    )
    firewall_tree.plant(
        "agents/_firewall_bridge_consumer.py",
        "import observation._firewall_orchestrator_hop\n",
    )

    result = firewall_tree.lint()
    assert result.returncode == 0, result.stdout
    assert re.search(r"Contracts: \d+ kept, 0 broken", result.stdout), result.stdout

    assert [path for path, names in _closure_breakers(firewall_tree.root)] == [
        str(firewall_tree.root / "observation" / "_firewall_orchestrator_hop.py")
    ]


def test_learned_package_is_swept_by_the_agents_source_scan() -> None:
    """``agents/tactical/learned/`` is explicitly inside the agents/ sweep.

    The rglob in :func:`_agent_source_files` covers every subpackage, but this
    pin makes the obligation loud: if the learned package moved out from under
    ``agents/``, escaping the doctrine above, this fails.
    """

    learned = _learned_package_source_files(_REPO_ROOT)
    assert learned, "agents/tactical/learned/ must exist and carry source files"
    assert set(learned) <= set(_agent_source_files(_REPO_ROOT))


def test_learned_package_imports_no_forbidden_top_level_module() -> None:
    offenders = _banned_importers(
        _learned_package_source_files(_REPO_ROOT), _FORBIDDEN_LEARNED_IMPORTS
    )
    assert not offenders, (
        "the productized champion must import none of "
        f"{sorted(_FORBIDDEN_LEARNED_IMPORTS)}; offenders: {offenders}"
    )


def test_the_learned_package_scan_rejects_a_planted_import(
    firewall_tree: FirewallTree,
) -> None:
    """The narrower learned-package sweep bites on its own extra bans."""

    planted = firewall_tree.plant(
        "agents/tactical/learned/_firewall_bad_import.py", "import training\n"
    )
    offenders = _banned_importers(
        _learned_package_source_files(firewall_tree.root), _FORBIDDEN_LEARNED_IMPORTS
    )
    assert (str(planted), ["training"]) in offenders


# --------------------------------------------------------------------------- #
# 3. The covering assertion that pins the two layers together.                 #
# --------------------------------------------------------------------------- #


def test_every_top_level_python_name_is_covered_by_one_layer() -> None:
    """No importable top-level name escapes both the roots and the ban set.

    A new one must join ``.importlinter``'s ``root_packages`` (so its chains are
    walked) or :data:`_FORBIDDEN_AGENT_IMPORTS` (so no interior package can
    reach it) before it can land. Joining ``root_packages`` puts it in BOTH:
    :func:`_exterior_bans` derives the ban from the configured roots, so the
    package is walked by grimp and banned from the interior at once.
    """

    uncovered = _uncovered_top_level_names(
        _tracked_python_paths(), _configured_root_packages(), _FORBIDDEN_AGENT_IMPORTS
    )
    assert not uncovered, (
        "these top-level names hold tracked Python and are covered by "
        f"neither firewall layer: {uncovered}"
    )


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("_firewall_new_package/module.py", "_firewall_new_package"),
        # A module at the repository root belongs to no linter root at all, so
        # it needs accounting for exactly like a package.
        ("_firewall_root_bridge.py", "_firewall_root_bridge"),
    ],
    ids=["package", "root-module"],
)
def test_the_covering_check_rejects_unlisted_python(path: str, expected: str) -> None:
    """A gate that cannot fail is not a gate."""

    uncovered = _uncovered_top_level_names(
        (*_tracked_python_paths(), path),
        _configured_root_packages(),
        _FORBIDDEN_AGENT_IMPORTS,
    )
    assert uncovered == [expected]


# --------------------------------------------------------------------------- #
# 4. The packet surface itself.                                                #
# --------------------------------------------------------------------------- #


def test_agent_visible_observation_schemas_have_no_engine_imports() -> None:
    schema_paths = (
        _REPO_ROOT / "observation" / "action_intent.py",
        _REPO_ROOT / "observation" / "packet.py",
        _REPO_ROOT / "observation" / "public_map.py",
    )

    for schema_path in schema_paths:
        source = schema_path.read_text(encoding="utf-8")
        assert "from engine" not in source
        assert "import engine" not in source


def test_own_kill_rides_only_the_killers_self_channel(tmp_path: Path) -> None:
    """``SelfView.own_kill`` is the killer's privileged self channel (Task 11.3,
    DESIGN.md §1.3, §6.2). The engine excludes a killer from its own kill's
    witnesses, so the kill is logged nowhere else; surfacing it here lets the
    §6.2 renderer state the act. The firewall guarantee: it is populated ONLY
    for the actor -- every other agent's packet (crewmate witnesses here) carries
    ``own_kill is None`` -- and the kill VERB ("(IMPOSTOR) killed ...") is
    produced only in the store render, never in any packet JSON.
    """

    game_map = load_canonical_map()
    # p-3 is the sole impostor (cooldown 0); all four players spawn co-present in
    # CAFETERIA, so the crewmates p-2/p-4 witness the kill of p-1 -- yet only the
    # killer's packet may carry ``own_kill``.
    state = scripted_initial_world_state(seed=11)
    kill_action = _ACTION_ADAPTER.validate_python(
        {"type": "kill", "actor": "p-3", "payload": {"target": "p-1"}}
    )
    state, events = advance_tick(state, [kill_action], game_map=game_map)
    assert any(
        isinstance(event, KilledEvent)
        and event.actor == "p-3"
        and event.target == "p-1"
        for event in events
    )

    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    try:
        killer_packet = service.build_packet(
            world_state=state, agent_id="p-3", engine_events=events
        )
        assert killer_packet.self_state.own_kill is not None
        assert killer_packet.self_state.own_kill.victim_id == "p-1"

        for player_id, player in state.players.items():
            if not player.alive:
                continue
            packet = service.build_packet(
                world_state=state, agent_id=player_id, engine_events=events
            )
            if player_id != "p-3":
                # Every crewmate (and any non-actor) packet carries no own_kill.
                assert packet.self_state.own_kill is None
            dumped = json.dumps(packet.model_dump(mode="json"))
            # The kill verb lives only in the store render, never in packet JSON.
            assert "killed" not in dumped
            assert "(IMPOSTOR) killed" not in dumped
    finally:
        service.close()
