"""The ML champion leak gate's contract, pinned where it can be read.

``eval.leak_scan.scan_factory_packets`` is not only a test: ``training/crew/
scorer.py`` and ``training/bakeoff/harness.py`` call it OUTSIDE pytest to decide
whether a learned agent may become champion, and they turn its ``AssertionError``
into a recorded ``leak_test_passed=False`` row rather than letting it end the run.
Three things have to stay true for that to mean anything, and none of them is
visible from either side alone: both call sites must bind the same scanner this
module ships, the scan must actually run the entitlement check (not a shape-only
subset), and an entitlement break must arrive as an ``AssertionError`` the
handlers record.

The end-to-end evaluators are campaign-tier (minutes per row), so the recording
half is pinned structurally — the call site's own ``try``/``except`` — while the
raising half is exercised live against a planted filter break.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Mapping
from types import ModuleType

import pytest

import eval.leak_scan
import training.bakeoff.harness
import training.crew.scorer
from engine import visibility as engine_visibility
from engine.entities import BodyId, BodyState, RoomId
from eval.leak_scan import scan_factory_packets
from orchestrator.game import build_default_agent_factory

_GATE_MODULES = (training.crew.scorer, training.bakeoff.harness)


def test_both_champion_gates_bind_the_shipped_scanner() -> None:
    """A local copy or a shim would make every pin below vacuous."""

    for module in _GATE_MODULES:
        assert module.scan_factory_packets is eval.leak_scan.scan_factory_packets


def test_the_gate_scan_returns_a_positive_packet_count() -> None:
    """The gate's own return value: packets scanned, with entitlement on.

    ``scan_factory_packets`` asserts its own coverage (the games must reach a
    body), so a positive count here means full production games were walked and
    every packet passed the entitlement oracle, not that the walk was empty.
    """

    assert scan_factory_packets(build_default_agent_factory()) > 0


def test_an_entitlement_break_raises_the_assertion_the_gate_catches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The failure signal is an ``AssertionError``, which is what the handlers catch."""

    def _bodies_everywhere(
        *,
        bodies: Mapping[BodyId, BodyState],
        visible_rooms: tuple[RoomId, ...],
    ) -> tuple[BodyId, ...]:
        return tuple(
            sorted(
                body_id
                for body_id, body in bodies.items()
                if body.discovered_by is None
            )
        )

    monkeypatch.setattr(engine_visibility, "_visible_body_ids", _bodies_everywhere)
    with pytest.raises(AssertionError, match="visible_bodies"):
        scan_factory_packets(build_default_agent_factory())


def _gate_try_block(module: ModuleType) -> ast.Try:
    """The ``try`` that wraps this module's ``scan_factory_packets`` call."""

    tree = ast.parse(inspect.getsource(module))
    blocks = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Try)
        and any(
            isinstance(call.func, ast.Name) and call.func.id == "scan_factory_packets"
            for statement in node.body
            for call in ast.walk(statement)
            if isinstance(call, ast.Call)
        )
    ]
    assert len(blocks) == 1, (
        f"expected exactly one guarded scan_factory_packets call, found {len(blocks)}"
    )
    return blocks[0]


@pytest.mark.parametrize(
    "module", _GATE_MODULES, ids=("crew-scorer", "bakeoff-harness")
)
def test_the_gate_records_a_leak_failure_instead_of_ending_the_run(
    module: ModuleType,
) -> None:
    """The scan is guarded, the guard catches ``AssertionError``, and the handler
    records the verdict rather than re-raising — so a leaking candidate is
    rejected with a reason instead of aborting a tournament."""

    block = _gate_try_block(module)
    handlers = block.handlers
    assert len(handlers) == 1
    handler = handlers[0]
    assert isinstance(handler.type, ast.Name)
    assert handler.type.id == "AssertionError"
    assert not [node for node in ast.walk(handler) if isinstance(node, ast.Raise)], (
        "the champion gate must record a leak failure, never re-raise it"
    )
    assigned = {
        target.id
        for statement in handler.body
        if isinstance(statement, ast.Assign)
        for target in statement.targets
        if isinstance(target, ast.Name)
    }
    assert {"leak_passed", "leak_failure"} <= assigned
