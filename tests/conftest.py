"""Shared pytest fixtures for the AiLibi test suite.

Hermetic process environment: every test runs under the environment CI
exports, which is none of it. The guard below clears the whole ``AILIBI_*``
namespace plus the two provider keys and re-pins ``AILIBI_LLM_PROVIDER=fake``,
so an ambient value on a developer box can neither red a test that CI passes
nor -- the silent and worse direction -- make a test pass that would otherwise
fail. It is applied twice over: once when this file is imported, which is
before pytest imports any test module and therefore before collection-time
reads, and again in :func:`_hermetic_ailibi_env`, which holds it for the run
and restores the ambient environment at session end. Subprocess families that
hand ``dict(os.environ)`` to a child inherit the cleaned parent for free.

The provider pin is the load-bearing member of that set. Without it a suite
run in a real-provider-configured environment (``AILIBI_LLM_PROVIDER=anthropic``
plus a live ``ANTHROPIC_API_KEY`` -- the configuration the eval/dev sandboxes
export) silently routes every default-wire-up test
(:func:`llm.provider.build_default_client`, reached through
:func:`orchestrator.game.build_default_meeting_runner` and the public CLI
wire-up) through the paid Anthropic API: real money is spent, and a full
meeting's real cost trips the $0.30 default
:class:`~llm.budget.GameBudget` cap. Clearing the keys is the second half of
the same guarantee -- with the opt-in gates off, no test can reach a paid
path from ambient state at all.

The opt-in real-provider, Ollama and benchmark families are unaffected: their
gates survive the clear (the fixture's allow-list says why), and they build
their clients directly rather than consulting ``AILIBI_LLM_PROVIDER``. Tests
that exercise the provider-selection logic itself pass an explicit ``env=``
mapping to ``build_default_client`` and so are likewise independent of the
process environment.

Tiering (Task 19.27): ``bash scripts/check.sh`` — whose ``uv run pytest`` is
henceforth the DEFAULT gate — runs everything not marked ``campaign``
(pyproject's ``addopts``). The campaign tier runs weekly in CI
(``-m campaign``), and the phase close runs BOTH tiers — the 19.28
phase-close contract pins that.

The session-scoped committed-replay fixture below exists because the
committed ``replays/samples/9p2i`` set was independently re-walked by every
pin that needed the assembled report — six ``build_report`` calls per suite
run at the Task-19.27 baseline, each a state-hash-verified engine walk of
all 50 recordings. One session-scoped walk serves them all; the walk itself
is pure and deterministic over the committed bytes, so sharing the result
cannot couple tests.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE

if TYPE_CHECKING:
    from eval.meeting_quality import TournamentEvalReport

_REPO_ROOT = Path(__file__).resolve().parents[1]
_COMMITTED_9P2I_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"

#: The namespace the hermetic guard owns. Every name under it is cleared unless the
#: allow-list below keeps it.
ENV_PREFIX: Final = "AILIBI_"

#: The operator's opt-in switches, preserved whatever their value. Each is read by a
#: module-level ``skipif`` and re-read at call time by a meta-test asserting the two
#: agree; clearing one would leave both reads consistent and silently skip the whole
#: family the operator asked to run, which is the one direction this guard must not
#: take.
OPT_IN_GATES: Final[tuple[str, ...]] = (
    "AILIBI_RUN_REAL_PROVIDER_TESTS",
    "AILIBI_RUN_OLLAMA_TESTS",
    "AILIBI_RUN_PERF_BENCHMARK",
)

#: Credentials and endpoints each gated family reads at CALL time, preserved only
#: while that gate reads ``"1"``. With the gate off nothing reads them, so clearing
#: them is the safety direction: no test can reach a paid or networked path from
#: ambient state.
GATE_CARRIED_ENV: Final[Mapping[str, tuple[str, ...]]] = {
    "AILIBI_RUN_REAL_PROVIDER_TESTS": (
        "ANTHROPIC_API_KEY",
        "FEATHERLESS_API_KEY",
        "AILIBI_LLM_MEETING_MODEL",
    ),
    "AILIBI_RUN_OLLAMA_TESTS": ("AILIBI_OLLAMA_HOST",),
}

#: Provider keys outside the prefix that the clear covers too.
PROVIDER_KEYS: Final[tuple[str, ...]] = ("ANTHROPIC_API_KEY", "FEATHERLESS_API_KEY")


def env_names_to_clear(environ: Mapping[str, str]) -> frozenset[str]:
    """The names the hermetic guard removes from ``environ``.

    Derived BY PREFIX from what is actually exported, never from a list of known
    names -- a list goes stale the moment a knob is added, which is the failure this
    guard exists to end. Pure, so a test can plant a dirty environment and check the
    policy directly.
    """

    preserved = set(OPT_IN_GATES)
    for gate, carried in GATE_CARRIED_ENV.items():
        if environ.get(gate) == "1":
            preserved.update(carried)
    doomed = {name for name in environ if name.startswith(ENV_PREFIX)}
    doomed.update(name for name in PROVIDER_KEYS if name in environ)
    return frozenset(doomed - preserved)


def _apply_hermetic_env(patch: pytest.MonkeyPatch) -> None:
    """Clear the ambient namespace and pin the fake provider, through ``patch``."""

    for name in sorted(env_names_to_clear(os.environ)):
        patch.delenv(name, raising=False)
    patch.setenv(ENV_PROVIDER, PROVIDER_FAKE)


# Applied at conftest import — before pytest imports any test module, and therefore
# before the module-level code that reads the environment during collection: the three
# opt-in `skipif` gates directly, and tests/api/test_replay_loader.py through
# `substrate_flag_snapshot()`. A fixture runs after collection and is too late for
# those. The fixture below undoes this at session end.
_COLLECTION_TIME_ENV: Final = pytest.MonkeyPatch()
_apply_hermetic_env(_COLLECTION_TIME_ENV)


@pytest.fixture(autouse=True, scope="session")
def _hermetic_ailibi_env() -> Iterator[None]:
    """Clear the ambient ``AILIBI_*`` surface and pin the fake provider.

    Four kinds of name survive the clear, each for a stated reason:

    * ``AILIBI_LLM_PROVIDER`` -- cleared, then re-pinned to ``fake`` so the
      environment-selected default client is always the zero-cost adapter.
    * the three opt-in gates in :data:`OPT_IN_GATES` -- kept whatever their value,
      because they are how an operator asks for the real-provider, Ollama and
      benchmark families; clearing one would silently skip everything it selects.
    * ``ANTHROPIC_API_KEY``, ``FEATHERLESS_API_KEY`` and
      ``AILIBI_LLM_MEETING_MODEL`` -- kept only while
      ``AILIBI_RUN_REAL_PROVIDER_TESTS`` reads ``1``, since only the live
      round-trips read them, and only then.
    * ``AILIBI_OLLAMA_HOST`` -- kept only while ``AILIBI_RUN_OLLAMA_TESTS`` reads
      ``1``, for the same reason.

    Session-scoped: the process environment is one object, so one clear covers the
    run. Per-test overrides are unaffected -- ``monkeypatch`` restores to the
    cleaned value rather than to the ambient one.
    """

    with pytest.MonkeyPatch.context() as patch:
        _apply_hermetic_env(patch)
        yield
    _COLLECTION_TIME_ENV.undo()


@pytest.fixture(scope="session")
def committed_9p2i_report() -> "TournamentEvalReport":
    """The committed 9p2i set's eval report, rebuilt ONCE per suite run.

    ``build_report`` re-derives roles from the seeds, folds the 50 recorded
    replays through the one operator assembly
    (``scripts/build_sample_report.py``), and runs the state-hash-verified
    kill-craft walk over the whole directory — the expensive part. The result
    is a frozen-input pure function of the committed bytes, so a single
    session-scoped instance serves every consumer without coupling them.

    Imports lazily: ``build_sample_report`` pulls in the api/engine/eval
    stack, which does not belong in conftest import time for the tests that
    never use this fixture.
    """

    scripts_dir = _REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from build_sample_report import build_report

    return build_report(_COMMITTED_9P2I_DIR)


# The Task-14.10 evidence-quality lift lever is UNCONDITIONAL since the Task-14.12
# close (the 14.9 move, applied after baseline 2 adopted it), so there is no env
# gate to clear for hermeticity — the belief fold always applies the bounds and
# the committed baseline-2 pins are recorded under that (only) substrate.
