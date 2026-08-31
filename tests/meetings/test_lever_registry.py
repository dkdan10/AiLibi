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
predicate the sweep uses. Every LIVE resolver (one that reads ``env``) is
asserted clean by the same predicate, so the gate discriminates rather than
matching on the name alone. The live set is read out of
``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`` -- the registry AGENTS.md
names as the source of truth for which levers still switch -- rather than
listed here, so a lever registered later is covered without an edit.

The second half of the same rule lives here too:
:func:`orchestrator.replay.retired_levers_stamped_off`, the refusal a re-deriver
owes a LEGACY recording. Once a lever's OFF derivation is deleted, a stamp
naming it OFF describes a substrate this build cannot reproduce, so scoring
those bytes with the current detector would report facts about a game that never
happened. Pinned here with a planted legacy stamp beside the clean cases.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import Final

from orchestrator.replay import (  # noqa: PLC2701
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    _RETIRED_ALWAYS_ON_LEVERS,
    _TOGGLEABLE_LEVER_RESOLVERS,
    retired_levers_stamped_off,
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_SWEPT_PACKAGES: Final[tuple[str, ...]] = ("agents", "meetings", "orchestrator")

# The eight keys the baseline-7 record appended -- absent from any baseline-6-era
# stamp, which is what makes such a stamp a legacy substrate this build cannot
# reproduce rather than a merely older spelling of the same one.
_PHASE20_ADOPTED: Final[tuple[str, ...]] = (
    "task_completion_from_events",
    "self_location_trail",
    "movement_claim_shape",
    "grounded_prosecution",
    "map_aware_arbitration",
    "structured_turn_markers",
    "meeting_outcome_memory",
    "coalesced_memory_render",
)


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
    """Names of the ``*_enabled`` functions in ``source`` that always read ``True``.

    A resolver is reported when its name ends ``_enabled``, its body never LOADS
    ``env``, and EVERY ``return`` reachable inside it -- at any nesting depth --
    returns a bare ``True``. That is the graduated-but-undeleted shape whatever
    its spelling: the straight-line ``del env; return True``, and equally
    ``if cond: return True`` followed by ``return True``, which is env-independent
    and can never resolve OFF however many branches it grows. A resolver that
    reads its argument, or that can return anything but ``True``, is a LIVE
    toggle and is never reported.

    Descendant returns are read rather than the top-level statement list,
    precisely so wrapping the constant in control flow cannot slip a retired
    lever back in. A resolver with NO return at all is not reported -- it does
    not resolve to a constant ``True`` and is somebody else's bug.
    """

    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.endswith("_enabled"):
            continue
        if _reads_env(node):
            continue
        returns = [
            stmt
            for stmt in ast.walk(node)
            if isinstance(stmt, ast.Return)
            # A return inside a NESTED def belongs to that function, not this one.
            and _owning_function(node, stmt) is node
        ]
        if returns and all(_is_bare_true_return(stmt) for stmt in returns):
            found.append(node.name)
    return found


def _owning_function(
    root: ast.FunctionDef | ast.AsyncFunctionDef, target: ast.Return
) -> ast.AST | None:
    """The innermost function definition ``target`` returns from, within ``root``."""

    owner: ast.AST | None = None

    def _descend(node: ast.AST, current: ast.AST) -> None:
        nonlocal owner
        for child in ast.iter_child_nodes(node):
            if child is target:
                owner = current
                return
            nested = (
                child
                if isinstance(
                    child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
                )
                else current
            )
            _descend(child, nested)
            if owner is not None:
                return

    _descend(root, root)
    return owner


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


def test_the_gate_bites_on_a_branched_always_true_resolver(tmp_path: Path) -> None:
    # The evasion the straight-line shape invites: wrap the constant in control
    # flow and a statement-list check stops seeing it, while the resolver is
    # still env-independent and still cannot resolve OFF. The gate reads every
    # descendant return instead, so both spellings are reported.
    branched = tmp_path / "branched_lever.py"
    branched.write_text(
        "from collections.abc import Mapping\n"
        "\n"
        "\n"
        "def branched_thing_enabled(env: Mapping[str, str] | None = None) -> bool:\n"
        '    """Whether the thing is on -- now always True."""\n'
        "\n"
        "    del env\n"
        "    if True:\n"
        "        return True\n"
        "    return True\n",
        encoding="utf-8",
    )

    assert accept_and_ignore_resolvers(branched.read_text(encoding="utf-8")) == [
        "branched_thing_enabled"
    ]


def test_the_gate_leaves_a_branched_env_free_resolver_that_can_be_false(
    tmp_path: Path,
) -> None:
    # The discrimination half of the branched case: a resolver that can return
    # False is a real decision, not a retired lever, even though it reads no
    # ``env``. Reporting it would make the gate a ban on ``*_enabled`` names.
    real = tmp_path / "real_predicate.py"
    real.write_text(
        "def roster_thing_enabled(size: int) -> bool:\n"
        '    """A real predicate that happens to end _enabled."""\n'
        "\n"
        "    if size > 3:\n"
        "        return True\n"
        "    return False\n",
        encoding="utf-8",
    )

    assert accept_and_ignore_resolvers(real.read_text(encoding="utf-8")) == []


def test_the_gate_leaves_a_live_resolver_alone(tmp_path: Path) -> None:
    # The discrimination half: a resolver that READS its env argument is a live
    # toggle and must not be reported, so the gate cannot be satisfied by
    # deleting a lever the project still switches.
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


def test_a_legacy_stamp_naming_a_retired_lever_off_is_refused() -> None:
    # The other half of "retire means delete": once the OFF derivation is gone,
    # a recording that STAMPED it OFF describes a substrate this build cannot
    # reproduce, so the $0 re-extraction spine must refuse it rather than score
    # legacy bytes with the current detector. Planted counter-case first, so the
    # clean cases below are a discrimination rather than a vacuous pass.
    legacy = dict.fromkeys(_RETIRED_ALWAYS_ON_LEVERS, True)
    legacy["citation_gate"] = False
    legacy["absence_prior"] = False
    assert retired_levers_stamped_off(legacy) == ["citation_gate", "absence_prior"]

    # A baseline-7 stamp passes; so does EVERY live toggle at either polarity,
    # because those are the levers whose OFF derivation still exists. Derived
    # from the registry, so a lever registered later is covered without an edit.
    current = dict.fromkeys(SUBSTRATE_FLAG_KEYS, True)
    assert retired_levers_stamped_off(current) == []
    for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS:
        current[key] = False
        assert retired_levers_stamped_off(current) == [], key

    # An UNSTAMPED recording is unknown, not OFF: never checked, exactly as the
    # API replay loader skips an unstamped replay.
    assert retired_levers_stamped_off(None) == []

    # But within a stamp that IS present, a MISSING key reads OFF -- the same
    # ``bool(recorded.get(key))`` the loader applies. A baseline-6-era stamp
    # (the eight Phase-20 keys absent) therefore names all eight, because that
    # recording genuinely ran without them.
    baseline6 = {
        key: True for key in _RETIRED_ALWAYS_ON_LEVERS if key not in _PHASE20_ADOPTED
    }
    assert retired_levers_stamped_off(baseline6) == list(_PHASE20_ADOPTED)
    # A one-key stamp names every OTHER retired lever, never nothing.
    assert len(retired_levers_stamped_off({"testimony_as_content": True})) == (
        len(_RETIRED_ALWAYS_ON_LEVERS) - 1
    )


def test_every_live_resolver_in_the_tree_is_not_reported() -> None:
    # The real discrimination case, not a fixture: every surviving toggle's
    # resolver reads ``env``, so the sweep passing above is a statement about
    # deletion, not about the tree having no ``*_enabled`` function left at all.
    # Derived from the registry rather than listed, so a lever registered later
    # is covered here without an edit -- and the source files are named from the
    # resolvers themselves, so a resolver that MOVED cannot be swept by reading
    # a stale path.
    sources = {
        Path(inspect.getsourcefile(resolver) or "")
        for _key, resolver in _TOGGLEABLE_LEVER_RESOLVERS
    }
    sources.add(_REPO_ROOT / "agents" / "strategic" / "prompts" / "loader.py")
    combined = "".join(sorted(path.read_text(encoding="utf-8") for path in sources))
    for key, resolver in _TOGGLEABLE_LEVER_RESOLVERS:
        assert resolver.__name__.lstrip("_") == f"{key}_enabled", key
        assert f"{key}_enabled" in combined, key
    assert accept_and_ignore_resolvers(combined) == []


def test_the_live_toggle_registry_is_the_key_order() -> None:
    # The registry is the source of truth for which levers are still live
    # (AGENTS.md "Graduation sweeps"), so the two derived tuples must agree with
    # it in order and content -- a lever added to one and not the other would
    # give a recording a stamp key no resolver fills, or the reverse.
    keys = tuple(key for key, _ in _TOGGLEABLE_LEVER_RESOLVERS)
    assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS == keys
    assert SUBSTRATE_FLAG_KEYS[-len(keys) :] == keys
    assert set(keys) & set(_RETIRED_ALWAYS_ON_LEVERS) == set()
