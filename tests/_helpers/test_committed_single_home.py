"""Pin ``tests/_helpers/committed.py`` as the only home for committed-set walks.

A second copy of one of the five instrument walks is invisible: it passes, it
asserts the same numbers, and it silently doubles the most expensive fixture in
the suite. This module reads every test file, finds each call to a walk whose set
argument is a committed directory, and fails on any that does not go through the
shared cache — except the sites in :data:`UNCACHED_BY_DESIGN`, where a second
independent computation IS the assertion and delegating would make the pin
tautological.

The scanner is a pure function of source text so it can be aimed at planted
modules: the tests below prove it flags a committed walk (as a bare name, via
``self``, through a module alias, and through a path factored across two
constants) and that it leaves a ``tmp_path`` walk alone. A corrupted copy of a
committed set proves the second property — the cache is keyed by directory and
cannot answer for bytes it never walked — and a walk of the five report graphs
proves the third: sharing one instance cannot couple its readers, because every
report is frozen and every collection on it is typed ``Mapping``/``Sequence``,
which ``mypy --strict`` will not let a caller mutate.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, get_args, get_origin

import pytest
from pydantic import BaseModel, ConfigDict

from tests._helpers.committed import SAMPLES_4P1I, kill_craft_report, repo_root

#: The instrument entry points whose cost the shared cache exists to pay once.
WALKERS: Final[frozenset[str]] = frozenset(
    {
        "build_report",
        "compute_deception_instruments",
        "compute_information_funnel",
        "compute_kill_craft_report",
        "compute_solvability_report",
    }
)

#: Call sites that must keep their own uncached walk, keyed by module path and
#: enclosing ``def``, each with the reason the cache would break it.
UNCACHED_BY_DESIGN: Final[Mapping[str, Mapping[str, str]]] = {
    "tests/eval/test_kill_craft.py": {
        "test_report_is_deterministic": (
            "a second INDEPENDENT computation is the assertion; served from the "
            "cache it would compare one object with itself"
        ),
    },
    "tests/eval/test_deception_instruments.py": {
        "test_determinism_and_json_round_trip": (
            "same shape: the pin is that two independent folds agree, so the "
            "second fold has to actually run"
        ),
    },
    "tests/scripts/test_build_sample_report.py": {
        "test_rebuild_matches_committed_flat_4p1i": (
            "it tests build_report itself — the subject under test cannot be "
            "replaced by a cached result of the subject under test"
        ),
    },
}

#: Keyword names the five walkers accept for the set directory.
_SET_KEYWORDS: Final[frozenset[str]] = frozenset({"sample_dir", "replay_dir"})

#: Importing a set constant from here is the other way a module names committed
#: bytes without the word ``replays`` appearing in its own source.
_HELPER_MODULE: Final = "tests._helpers.committed"


@dataclass(frozen=True)
class WalkCall:
    """One call that walks a committed replay set."""

    walker: str
    enclosing_def: str
    line: int


def _referenced_names(node: ast.expr) -> frozenset[str]:
    """Every plain name and attribute name appearing anywhere under ``node``."""

    names: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            names.add(child.id)
        elif isinstance(child, ast.Attribute):
            names.add(child.attr)
    return frozenset(names)


def _constant_assignments(
    node: ast.AST,
) -> Iterator[tuple[tuple[ast.expr, ...], ast.expr]]:
    """Every module-level or class-level assignment under ``node``.

    Function bodies are skipped deliberately. Set directories in this repo are
    module constants or class attributes; a local inside a helper that copies
    committed bytes into ``tmp_path`` is NOT a committed set, and taint that
    escaped the function would flag exactly the fail-loud pins that build the
    corrupted copy.
    """

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
            continue
        if isinstance(child, ast.Assign):
            yield tuple(child.targets), child.value
        elif isinstance(child, ast.AnnAssign) and child.value is not None:
            yield (child.target,), child.value
        yield from _constant_assignments(child)


def _names_bound_to_committed_bytes(tree: ast.Module) -> frozenset[str]:
    """Constants that end up holding a path under ``replays/``.

    Covers module constants (``_SAMPLES_9P2I = ...``) and class attributes
    (``_SET_DIR = ...``) alike; both are ``ast.Name`` assignment targets. The
    search runs to a fixed point so a path factored in steps —
    ``_BASE = repo_root / "replays" / "samples"`` then ``_SET = _BASE / "9p2i"``
    — taints every name along the chain, not only the one that spells
    ``replays``.
    """

    assignments = list(_constant_assignments(tree))
    bound: set[str] = set()
    growing = True
    while growing:
        growing = False
        for targets, value in assignments:
            if "replays" not in ast.unparse(value) and not (
                _referenced_names(value) & bound
            ):
                continue
            for target in targets:
                if isinstance(target, ast.Name) and target.id not in bound:
                    bound.add(target.id)
                    growing = True
    return frozenset(bound)


def _set_constants_imported_from_the_helper(tree: ast.Module) -> frozenset[str]:
    """Set-directory constants ``tree`` imports from the shared helper."""

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == _HELPER_MODULE:
            imported.update(
                alias.asname or alias.name
                for alias in node.names
                if alias.name.isupper()
            )
    return frozenset(imported)


def _calls_by_enclosing_def(
    node: ast.AST, enclosing: str
) -> Iterator[tuple[str, ast.Call]]:
    """Every ``ast.Call`` under ``node``, tagged with the ``def`` it sits in."""

    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
            yield from _calls_by_enclosing_def(child, child.name)
            continue
        if isinstance(child, ast.Call):
            yield enclosing, child
        yield from _calls_by_enclosing_def(child, enclosing)


def _walker_name(call: ast.Call) -> str | None:
    """The walker this call invokes, whether bare or through a module alias."""

    func = call.func
    if isinstance(func, ast.Name):
        return func.id if func.id in WALKERS else None
    if isinstance(func, ast.Attribute):
        return func.attr if func.attr in WALKERS else None
    return None


def _set_argument(call: ast.Call) -> ast.expr | None:
    """The set-directory argument of ``call``, positional or keyword."""

    if call.args:
        return call.args[0]
    for keyword in call.keywords:
        if keyword.arg in _SET_KEYWORDS:
            return keyword.value
    return None


def _is_committed(argument: ast.expr, committed_names: frozenset[str]) -> bool:
    """Whether ``argument`` names a committed set rather than a built temp dir."""

    if "replays" in ast.unparse(argument):
        return True
    return bool(_referenced_names(argument) & committed_names)


#: Container types whose contents a reader can rebind in place. A cached report
#: that exposed one would make the shared instance a channel between tests.
_MUTABLE_CONTAINERS: Final[tuple[type, ...]] = (dict, list, set)


def _annotation_parts(annotation: Any) -> Iterator[Any]:
    """``annotation`` and every type argument nested inside it."""

    yield annotation
    for argument in get_args(annotation):
        yield from _annotation_parts(argument)


def _shared_value_offenders(
    model: type[BaseModel], seen: set[type[BaseModel]]
) -> list[str]:
    """Reasons ``model`` is unsafe to share: not frozen, or mutably typed."""

    if model in seen:
        return []
    seen.add(model)
    offenders: list[str] = []
    if not model.model_config.get("frozen", False):
        offenders.append(f"{model.__name__} is not frozen")
    for name, field in model.model_fields.items():
        for part in _annotation_parts(field.annotation):
            if (get_origin(part) or part) in _MUTABLE_CONTAINERS:
                offenders.append(f"{model.__name__}.{name}: {part}")
            if isinstance(part, type) and issubclass(part, BaseModel):
                offenders.extend(_shared_value_offenders(part, seen))
    return offenders


def committed_walk_calls(source: str) -> tuple[WalkCall, ...]:
    """Every call in ``source`` that walks a COMMITTED replay set.

    Walks of a directory the test builds itself (``tmp_path`` and friends) are
    not committed walks and are not returned — those are the fail-loud pins, and
    caching them would be wrong.
    """

    tree = ast.parse(source)
    bound = _names_bound_to_committed_bytes(tree)
    imported = _set_constants_imported_from_the_helper(tree)
    committed_names = bound | imported

    found: list[WalkCall] = []
    for enclosing, call in _calls_by_enclosing_def(tree, "<module>"):
        walker = _walker_name(call)
        if walker is None:
            continue
        argument = _set_argument(call)
        if argument is None or not _is_committed(argument, committed_names):
            continue
        found.append(WalkCall(walker, enclosing, call.lineno))
    return tuple(found)


def test_every_committed_walk_goes_through_the_shared_cache() -> None:
    offenders: list[str] = []
    for path in sorted((repo_root / "tests").rglob("*.py")):
        relative = path.relative_to(repo_root).as_posix()
        if relative.startswith("tests/_helpers/"):
            continue
        allowed = UNCACHED_BY_DESIGN.get(relative, {})
        for call in committed_walk_calls(path.read_text(encoding="utf-8")):
            if call.enclosing_def in allowed:
                continue
            offenders.append(
                f"{relative}:{call.line} {call.walker}() in {call.enclosing_def}"
            )
    assert not offenders, (
        "These call sites walk a committed replay set outside "
        "tests/_helpers/committed.py, so the walk runs again per worker. Delegate "
        "to the shared accessor, or add the site to UNCACHED_BY_DESIGN with the "
        "reason a second independent walk is the assertion:\n  "
        + "\n  ".join(offenders)
    )


def test_the_allow_list_names_only_live_call_sites() -> None:
    """An allow-listed site that stopped walking is a stale exemption."""

    for relative, entries in UNCACHED_BY_DESIGN.items():
        source = (repo_root / relative).read_text(encoding="utf-8")
        walking = {call.enclosing_def for call in committed_walk_calls(source)}
        assert set(entries) <= walking, (
            f"{relative}: allow-listed but no longer walks a committed set: "
            f"{sorted(set(entries) - walking)}"
        )
        assert all(reason.strip() for reason in entries.values()), relative


def test_the_cache_is_keyed_by_directory_not_shared_across_bytes(
    tmp_path: Path,
) -> None:
    """One key per directory: a perturbed copy is re-walked, and fails loudly.

    A cache that answered for a different directory would turn every
    reconstruction pin downstream into prose — the corrupted copy below would
    pass by being served the committed set's result.
    """

    from eval.kill_craft import KillCraftReconstructionError

    assert kill_craft_report(SAMPLES_4P1I) is kill_craft_report(SAMPLES_4P1I)

    corrupted = tmp_path / "4p1i"
    corrupted.mkdir()
    for source in sorted(SAMPLES_4P1I.iterdir()):
        if source.is_file():
            (corrupted / source.name).write_bytes(source.read_bytes())

    replay = sorted(corrupted.glob("replay-seed-*.jsonl"))[0]
    lines = replay.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    assert first["kind"] == "tick"
    first["state_hash"] = "0" * len(first["state_hash"])
    lines[0] = json.dumps(first)
    replay.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(KillCraftReconstructionError):
        kill_craft_report(corrupted)


def test_the_scanner_flags_a_planted_committed_walk() -> None:
    planted = (
        "from pathlib import Path\n"
        "_SET = Path(__file__).resolve().parents[2] / 'replays' / 'samples' / '9p2i'\n"
        "def test_planted() -> None:\n"
        "    compute_kill_craft_report(_SET)\n"
    )
    assert committed_walk_calls(planted) == (
        WalkCall("compute_kill_craft_report", "test_planted", 4),
    )


def test_the_scanner_flags_a_class_attribute_and_a_module_alias() -> None:
    planted = (
        "from pathlib import Path\n"
        "class TestX:\n"
        "    _SET_DIR = Path('x') / 'replays' / 'samples' / '9p2i'\n"
        "    def test_funnel(self) -> None:\n"
        "        compute_information_funnel(self._SET_DIR)\n"
        "def test_alias() -> None:\n"
        "    bsr.build_report(sample_dir=TestX._SET_DIR)\n"
    )
    assert committed_walk_calls(planted) == (
        WalkCall("compute_information_funnel", "test_funnel", 5),
        WalkCall("build_report", "test_alias", 7),
    )


def test_the_scanner_follows_a_path_factored_in_steps() -> None:
    """Only the first assignment spells ``replays``; both names are committed."""

    planted = (
        "from pathlib import Path\n"
        "_BASE = Path(__file__).resolve().parents[2] / 'replays' / 'samples'\n"
        "_SET = _BASE / '9p2i'\n"
        "def test_planted() -> None:\n"
        "    compute_information_funnel(_SET)\n"
    )
    assert committed_walk_calls(planted) == (
        WalkCall("compute_information_funnel", "test_planted", 5),
    )


def test_the_scanner_flags_a_set_constant_imported_from_the_helper() -> None:
    planted = (
        "from tests._helpers.committed import SAMPLES_9P2I, kill_craft_report\n"
        "def test_planted() -> None:\n"
        "    compute_solvability_report(SAMPLES_9P2I)\n"
    )
    assert committed_walk_calls(planted) == (
        WalkCall("compute_solvability_report", "test_planted", 3),
    )


def test_the_scanner_does_not_taint_across_a_function_boundary() -> None:
    """A helper that copies committed bytes into ``tmp_path`` builds a TEMP set.

    Its locals must not make the caller's ``tmp_path`` argument read as
    committed — that would flag every fail-loud pin in the suite.
    """

    planted = (
        "from pathlib import Path\n"
        "_SET = Path('x') / 'replays' / 'samples' / '4p1i'\n"
        "def _corrupted(tmp_path):\n"
        "    lines = (_SET / 'replay-seed-0.jsonl').read_text().splitlines()\n"
        "    (tmp_path / 'replay-seed-0.jsonl').write_text(lines[0])\n"
        "    return tmp_path\n"
        "def test_fail_loud(tmp_path) -> None:\n"
        "    compute_solvability_report(_corrupted(tmp_path))\n"
    )
    assert committed_walk_calls(planted) == ()


def test_the_scanner_leaves_temp_directory_walks_alone() -> None:
    planted = (
        "from pathlib import Path\n"
        "_SET = Path('x') / 'replays' / 'samples' / '9p2i'\n"
        "def test_fail_loud(tmp_path: Path) -> None:\n"
        "    compute_solvability_report(tmp_path)\n"
        "    compute_deception_instruments(tmp_path / 'built')\n"
    )
    assert committed_walk_calls(planted) == ()


def test_the_scanner_ignores_a_call_that_is_not_a_walker() -> None:
    planted = (
        "_SET = 'replays/samples/9p2i'\n"
        "def test_other() -> None:\n"
        "    check_report(_SET)\n"
    )
    assert committed_walk_calls(planted) == ()


def test_the_cached_reports_carry_no_mutable_collection() -> None:
    """Sharing ONE instance is safe only while no reader can mutate it.

    ``frozen=True`` stops attribute rebinding; it does not stop
    ``report.histogram[key] = value``. What stops that is the annotation: every
    collection on these reports is a ``Mapping``/``Sequence``, which has no
    ``__setitem__``, so ``uv run mypy .`` — a leg of ``scripts/check.sh``, run
    over ``tests/`` too — rejects the mutation where it is written. This walks
    the five report graphs and fails the moment a field is re-declared as a bare
    ``dict``/``list``/``set``, which is what would turn the process-wide cache
    into a channel between tests.
    """

    from eval.deception_instruments import DeceptionInstrumentsReport
    from eval.funnel import InformationFunnelReport
    from eval.kill_craft import KillCraftReport
    from eval.meeting_quality import TournamentEvalReport
    from eval.solvability import SolvabilityReport

    offenders: list[str] = []
    for model in (
        DeceptionInstrumentsReport,
        InformationFunnelReport,
        KillCraftReport,
        SolvabilityReport,
        TournamentEvalReport,
    ):
        offenders.extend(_shared_value_offenders(model, set()))
    assert offenders == [], (
        "These cached-report fields can be mutated in place, so one test could "
        "poison every later reader on the same worker:\n  " + "\n  ".join(offenders)
    )


def test_the_immutability_gate_bites_on_a_planted_mutable_field() -> None:
    class Planted(BaseModel):
        model_config = ConfigDict(frozen=True)

        histogram: dict[int, int]

    assert _shared_value_offenders(Planted, set()) == [
        "Planted.histogram: dict[int, int]"
    ]


def test_the_immutability_gate_bites_on_a_planted_unfrozen_model() -> None:
    class Thawed(BaseModel):
        count: int

    assert _shared_value_offenders(Thawed, set()) == ["Thawed is not frozen"]
