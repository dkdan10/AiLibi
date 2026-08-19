"""The static half of the observation firewall: two independent gates.

``import-linter`` walks the import graph of every root package in
``.importlinter`` and proves the transitive claim — ``agents/`` reaches
``engine/`` by no route, however long. The AST source scan below is the second
layer: it bans, at the source level, the top-level names that must not appear
under ``agents/`` at all, including the packages no import graph covers
(``tests/``, ``experiments/``) and the external ones grimp never sees
(``numpy``, ``torch``). A covering assertion pins the pair, so a new top-level
package must join one list or the other to land.

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


def _top_level_packages(paths: Iterable[str]) -> set[str]:
    """The first path segment of every path that lives inside a directory."""

    parts = (PurePosixPath(path).parts for path in paths)
    return {part[0] for part in parts if len(part) > 1}


def _uncovered_top_level_packages(
    paths: Iterable[str],
    root_packages: Collection[str],
    banned: Collection[str],
) -> list[str]:
    """Top-level packages neither layer of the firewall can see."""

    return sorted(_top_level_packages(paths) - set(root_packages) - set(banned))


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

# Top-level names that must not be imported anywhere under ``agents/``.
#
# numpy/torch: production inference under ``agents/`` is pure Python, because
# BLAS reductions are not bit-stable across machines and thread counts — numpy
# stays confined to ``training/`` and the Encoder-v2 inference path is stdlib
# ``math`` + lists. They are external packages, so no import-linter contract can
# see them (``include_external_packages`` is unset); this scan is their only gate.
#
# The packages: ``orchestrator``, ``api``, ``eval``, ``scripts``,
# ``experiments``, ``audits`` and ``tests`` all import ``engine`` directly, so
# any one of them is a route around the firewall; ``design`` holds one-off
# artifact generators that production code has no reason to reach for. The first
# four are import-linter roots, so their chains are caught there too — the other
# four are outside the graph by design and this scan is their only gate. It is
# an AST scan rather than a substring one so a docstring that legitimately NAMES
# a banned import (the encoder module documents this very ban) never
# false-positives.
_FORBIDDEN_AGENT_IMPORTS = frozenset(
    {
        "numpy",
        "torch",
        "orchestrator",
        "api",
        "eval",
        "scripts",
        "experiments",
        "audits",
        "design",
        "tests",
    }
)

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


def _agent_source_files(tree_root: Path) -> list[Path]:
    return sorted((tree_root / "agents").rglob("*.py"))


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


def test_every_top_level_python_package_is_covered_by_one_layer() -> None:
    """No top-level package escapes both the linter roots and the ban set.

    A new one must join ``.importlinter``'s ``root_packages`` (so its chains are
    walked) or :data:`_FORBIDDEN_AGENT_IMPORTS` (so ``agents/`` cannot reach it)
    before it can land.
    """

    uncovered = _uncovered_top_level_packages(
        _tracked_python_paths(), _configured_root_packages(), _FORBIDDEN_AGENT_IMPORTS
    )
    assert not uncovered, (
        "these top-level packages hold tracked Python and are covered by "
        f"neither firewall layer: {uncovered}"
    )


def test_the_covering_check_rejects_an_unlisted_new_package() -> None:
    """A gate that cannot fail is not a gate."""

    uncovered = _uncovered_top_level_packages(
        (*_tracked_python_paths(), "_firewall_new_package/module.py"),
        _configured_root_packages(),
        _FORBIDDEN_AGENT_IMPORTS,
    )
    assert uncovered == ["_firewall_new_package"]


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
