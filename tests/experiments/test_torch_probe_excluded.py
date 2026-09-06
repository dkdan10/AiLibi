"""The 15.17 torch-probe pins — all torch-free (Task 15.17).

Three guarantees the task contract commits:

1. **The mypy exclusion covers the probe.** ``[tool.mypy] exclude`` in
   ``pyproject.toml`` matches every file under ``experiments/lab/torch_probe/``
   (torch is never installed for the gate, so an un-excluded probe file would
   break ``uv run mypy .``) — and does NOT swallow production paths.
2. **No production package imports the probe.** An AST scan (the
   ``tests/test_firewall.py`` mechanism — AST, not substring, so a docstring
   MENTION never false-positives) over every production root, plus the
   plant-detect-cleanup self-check so the gate is proven able to fail.
3. **The comparability plumbing works without torch.** A tiny CPU stub drives
   the probe's entrant adapter end-to-end: the adapter constructs
   ``training.env.TacticalRolloutEnv`` + ``agents.tactical.features
   .TacticalFeatureEncoder``, and the frozen candidate is accepted by the
   15.15 harness's experiment-tier (determinism-FAIL-tolerant) row path —
   the exact seam the torch champion reports through.

The probe package is imported DYNAMICALLY (``importlib`` after the ml_spike
``sys.path`` bootstrap): a static import would drag the mypy-excluded module
into the strict gate via import following, defeating the exclusion this test
pins.
"""

from __future__ import annotations

import ast
import importlib
import json
import re
import sys
import tomllib
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Any

import pytest

from agents.tactical.features import TacticalFeatureEncoder
from engine.world import load_canonical_map
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff.harness import (
    BakeoffEntrant,
    BakeoffProtocolConfig,
    BakeoffResult,
    evaluate_candidate,
)
from training.bakeoff.policy_es import head_size
from training.env import TacticalRolloutEnv

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROBE_DIR = _REPO_ROOT / "experiments" / "lab" / "torch_probe"

# Every root whose code ships (or gates shipping): the observation firewall
# roots, the training stack, the API/orchestration layer, and the check
# tooling. ``experiments/`` itself is deliberately absent — probe scripts may
# import each other.
_PRODUCTION_ROOTS: tuple[str, ...] = (
    "agents",
    "api",
    "engine",
    "eval",
    "llm",
    "meetings",
    "observation",
    "orchestrator",
    "scripts",
    "training",
)

# Any absolute import resolving into the probe: the namespace-package spelling
# the scripts use (``torch_probe.*``) or a dotted path through experiments.
_FORBIDDEN_TOP_LEVEL: frozenset[str] = frozenset({"torch_probe", "experiments"})


def _probe_module(name: str) -> ModuleType:
    """Import ``torch_probe.<name>`` via the ml_spike sys.path bootstrap."""

    lab_root = str(_REPO_ROOT / "experiments" / "lab")
    if lab_root not in sys.path:
        sys.path.insert(0, lab_root)
    return importlib.import_module(f"torch_probe.{name}")


# --------------------------------------------------------------------------- #
# 1. The mypy exclusion pin.                                                   #
# --------------------------------------------------------------------------- #


def test_mypy_exclude_covers_the_probe_directory() -> None:
    config = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text())
    exclude = config["tool"]["mypy"]["exclude"]
    assert isinstance(exclude, str)
    pattern = re.compile(exclude)
    probe_files = sorted(_PROBE_DIR.rglob("*.py"))
    assert probe_files, "the torch probe directory carries no Python files"
    for path in probe_files:
        relative = path.relative_to(_REPO_ROOT).as_posix()
        assert pattern.search(relative), (
            f"mypy exclude regex does not cover {relative!r}; "
            "`uv run mypy .` would need torch installed"
        )
    # The exclusion must not swallow production code or the committed tests.
    for kept in (
        "training/bakeoff/harness.py",
        "training/env.py",
        "agents/tactical/features.py",
        "tests/experiments/test_torch_probe_excluded.py",
    ):
        assert not pattern.search(kept), f"mypy exclude regex swallows {kept!r}"


def test_torch_is_not_a_project_dependency() -> None:
    """The probe is `uv run --with torch` ONLY — torch never enters the project."""

    config = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text())
    dependencies = [str(item) for item in config["project"]["dependencies"]]
    groups = config.get("dependency-groups", {})
    for group in groups.values():
        dependencies.extend(str(item) for item in group)
    offenders = [item for item in dependencies if item.startswith("torch")]
    assert offenders == [], f"torch leaked into project dependencies: {offenders!r}"
    lock_text = (_REPO_ROOT / "uv.lock").read_text()
    assert re.search(r'name = "torch"', lock_text) is None, (
        "torch is resolved into uv.lock; the probe is `uv run --with torch` only"
    )


# --------------------------------------------------------------------------- #
# 2. No production package imports the probe (AST scan + self-check).          #
# --------------------------------------------------------------------------- #


def _probe_imports(path: Path) -> list[tuple[str, int, str]]:
    """Every absolute import in ``path`` that resolves into the torch probe."""

    tree = ast.parse(path.read_text(), filename=str(path))
    offenders: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in _FORBIDDEN_TOP_LEVEL:
                    offenders.append((str(path), node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if (
                node.level == 0
                and module is not None
                and module.split(".", 1)[0] in _FORBIDDEN_TOP_LEVEL
            ):
                offenders.append((str(path), node.lineno, module))
    return offenders


def test_no_production_package_imports_the_probe() -> None:
    offenders: list[tuple[str, int, str]] = []
    for root in _PRODUCTION_ROOTS:
        for path in sorted((_REPO_ROOT / root).rglob("*.py")):
            offenders.extend(_probe_imports(path))
    assert offenders == [], (
        "production code must never import the experiment-tier torch probe; "
        f"offenders: {offenders!r}"
    )


def test_probe_import_scan_rejects_a_planted_import(tmp_path: Path) -> None:
    """A gate that cannot fail is not a gate (the firewall-test idiom).

    The plant goes under ``tmp_path``, never into the checkout: an in-tree plant
    is visible to any concurrent gate and survives an interrupted run.
    """

    planted = tmp_path / "_torch_probe_planted_import.py"
    planted.write_text("from torch_probe.entrant import TorchProbeEntrant\n")
    offenders = _probe_imports(planted)
    assert offenders, "the AST scan missed a planted torch_probe import"


# --------------------------------------------------------------------------- #
# 3. The torch-free wiring: stub-driven entrant -> experiment-tier row.        #
# --------------------------------------------------------------------------- #


def test_probe_entrant_module_imports_without_torch() -> None:
    module = _probe_module("entrant")
    assert "torch" not in sys.modules, (
        "importing the probe's entrant adapter must not import torch — the "
        "committed test path is torch-free by contract"
    )
    assert hasattr(module, "TorchProbeEntrant")
    assert hasattr(module, "TorchProbePolicy")


class _DriftingStubScorer:
    """A tiny CPU stand-in for the frozen GRU: head logits with a call drift.

    The drift (a call counter leaking into one logit) models torch float
    nondeterminism: the determinism harness's double-run sees two different
    frame streams and must FAIL, which is exactly what routes the row down
    the experiment-tier path this test pins.
    """

    def __init__(self, head: int) -> None:
        self._head = head
        self._calls = 0.0

    def score(
        self, agent_id: str, features: Sequence[float], *, new_episode: bool
    ) -> Sequence[float]:
        self._calls += 1.0
        logits = [0.0] * self._head
        logits[0] = self._calls * 1e-3
        return logits


class _StubLearner:
    """A deterministic torch-free ProbeLearner: first candidate, no learning."""

    def __init__(self, head: int) -> None:
        self._head = head
        self.acts = 0
        self.episodes = 0
        self.updates = 0
        self.reward_totals: list[float] = []

    def act(
        self,
        agent_id: str,
        features: Sequence[float],
        candidates: Sequence[Any],
        *,
        fsm_index: int | None,
        new_episode: bool,
    ) -> int:
        self.acts += 1
        return 0

    def episode_result(
        self, rewards_by_agent: Mapping[str, Sequence[float]], *, truncated: bool
    ) -> None:
        self.episodes += 1
        self.reward_totals.append(
            sum(sum(rewards) for rewards in rewards_by_agent.values())
        )

    def update(self) -> Mapping[str, float]:
        self.updates += 1
        return {"stub": 1.0}

    def frozen_scorer(self) -> _DriftingStubScorer:
        return _DriftingStubScorer(self._head)

    def flat_weights(self) -> tuple[float, ...]:
        return (0.0,)

    def config(self) -> Mapping[str, object]:
        return {"stub": True, "head": self._head}


def test_stub_entrant_trains_through_env_and_lands_experiment_tier(
    tmp_path: Path,
) -> None:
    entrant_module = _probe_module("entrant")
    head = head_size(public_map_from_engine_map(load_canonical_map()))
    learner = _StubLearner(head)
    entrant = entrant_module.TorchProbeEntrant(
        learner=learner,
        config=entrant_module.TorchProbeConfig(
            train_seeds=(0,), updates=1, episodes_per_update=1
        ),
    )
    candidate = entrant.train()

    # (a) The adapter constructed the REAL production env + encoder: the
    # comparability constraint is code, not prose.
    assert isinstance(entrant.rollout_env, TacticalRolloutEnv)
    assert isinstance(entrant.featurizer.encoder, TacticalFeatureEncoder)
    assert entrant.rollout_env.no_replay is True
    assert candidate.entrant == entrant.name
    # The adapter satisfies the 15.15 entrant seam (checked AFTER the
    # attribute asserts: isinstance narrows the module-typed value to the
    # protocol, which hides the adapter-only attributes from mypy).
    assert isinstance(entrant, BakeoffEntrant)
    assert candidate.policy.encoder_version == TacticalFeatureEncoder().version
    assert learner.acts > 0
    assert learner.episodes == 1
    assert learner.updates == 1
    # Every impostor decision routed one reward entry through the learner.
    assert len(learner.reward_totals) == 1

    # (b) The frozen candidate is ACCEPTED by the harness's experiment-tier
    # (determinism-FAIL-tolerant) row path: the drifting scorer fails the
    # double-run digest, the row survives with tier="experiment" and the
    # N-repeat metric spread attached. Scoring explicitly uses the historical
    # conviction diagnostic; the stub proves adapter plumbing, not a current fit.
    protocol = BakeoffProtocolConfig(
        eval_seeds=(1004,),
        determinism_seeds=(1004,),
        leak_seeds=(0,),
        repeat_n=2,
        surrogate_artifact_dir=None,
        evidence_scope="historical",
    )
    refused_dir = tmp_path / "refused-current"
    with pytest.raises(ValueError, match="historical version-one"):
        evaluate_candidate(
            candidate,
            replace(protocol, evidence_scope="current"),
            artifact_root=refused_dir,
        )
    assert not refused_dir.exists()
    result = evaluate_candidate(candidate, protocol, artifact_root=tmp_path)
    assert isinstance(result, BakeoffResult)
    assert result.tier == "experiment"
    assert result.evidence_scope == "historical"
    assert result.determinism.deterministic is False
    spread = result.repeat_spread
    assert spread is not None
    assert spread.repeats == 2
    for metric in (
        spread.inner_fitness_real,
        spread.impostor_win_rate,
        spread.anchor_cross_entropy,
    ):
        assert metric.min <= metric.mean <= metric.max
    # The row round-trips through the committed jsonl serialization.
    restored = BakeoffResult.model_validate(json.loads(result.to_json_line()))
    assert restored.tier == "experiment"
    assert restored.evidence_scope == "historical"
    assert restored.entrant == candidate.entrant
