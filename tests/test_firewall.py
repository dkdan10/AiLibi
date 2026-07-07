from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import KilledEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from observation.service import ObservationService
from tests._helpers.world_state import scripted_initial_world_state

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


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


# The pure-Python inference doctrine (Task 15.10, tasks/phase-15.md locked
# decision 2): production inference under ``agents/`` is pure-Python, so no
# ``numpy`` / ``torch`` import may appear anywhere under ``agents/``. BLAS
# reductions are not bit-stable across machines / thread counts, which is exactly
# why ``numpy`` stays confined to ``training/`` (its own import-linter contract)
# and the Encoder-v2 inference path (``agents/tactical/features.py``) is stdlib
# ``math`` + lists. numpy/torch are external packages, so this is a SOURCE scan
# (the ``test_agent_visible_observation_schemas_have_no_engine_imports``
# mechanism), not an import-linter contract — but it uses AST rather than a
# substring so a docstring that legitimately NAMES ``import numpy`` (the encoder
# module documents this very ban) does not false-positive.
_FORBIDDEN_AGENT_INFERENCE_MODULES = frozenset({"numpy", "torch"})


def _agent_source_files() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    return sorted((repo_root / "agents").rglob("*.py"))


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


def test_agents_have_no_numpy_or_torch_import() -> None:
    offenders: list[tuple[str, list[str]]] = []
    for path in _agent_source_files():
        banned = (
            _imported_top_level_modules(path.read_text(encoding="utf-8"))
            & _FORBIDDEN_AGENT_INFERENCE_MODULES
        )
        if banned:
            offenders.append((str(path), sorted(banned)))
    assert not offenders, (
        "pure-Python inference doctrine: agents/ must not import numpy/torch; "
        f"offenders: {offenders}"
    )


def test_numpy_torch_source_scan_rejects_planted_import() -> None:
    """A synthetic ``import numpy`` planted under ``agents/`` trips the scan.

    Mirrors :func:`test_agents_cannot_import_engine`'s plant-detect-cleanup shape
    but via the AST source-scan mechanism (numpy/torch are external packages, so
    the ban is a source scan, not an import-linter contract). A gate that cannot
    fail is not a gate.
    """

    repo_root = Path(__file__).resolve().parents[1]
    planted = repo_root / "agents" / "_firewall_numpy_bad_import.py"
    planted.write_text("import numpy\n", encoding="utf-8")
    try:
        assert "numpy" in _imported_top_level_modules(
            planted.read_text(encoding="utf-8")
        )
        offenders = [
            path
            for path in _agent_source_files()
            if _imported_top_level_modules(path.read_text(encoding="utf-8"))
            & _FORBIDDEN_AGENT_INFERENCE_MODULES
        ]
        assert planted in offenders
    finally:
        planted.unlink(missing_ok=True)


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
