"""Shared pytest fixtures for the AiLibi test suite.

Hermetic process environment: every test runs under the environment CI
exports, which is none of it. The guard below clears the whole ``AILIBI_*``
namespace plus the two provider keys and re-pins ``AILIBI_LLM_PROVIDER=fake``,
so an ambient value on a developer box can neither red a test that CI passes
nor -- the silent and worse direction -- make a test pass that would otherwise
fail. It is applied twice over: in :func:`pytest_configure`, which runs before
pytest imports any test module and so covers the reads that happen during
collection, and again in :func:`_hermetic_ailibi_env` for the run itself. The
ambient environment is given back in :func:`pytest_unconfigure`. Subprocess
families that hand ``dict(os.environ)`` to a child inherit the cleaned parent
for free.

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

Committed-replay walks: every walk over a committed sample set — the assembled
9p2i report below included — is computed once per worker by
``tests/_helpers/committed.py`` and shared from there. The walks are
state-hash-verified engine replays of whole directories, the suite's most
expensive fixtures, and pure functions of frozen bytes, so sharing a result
cannot couple the tests that read it.

Parallelism: ``scripts/check.sh`` runs this tier across ``pytest-xdist``
workers. Session scope is therefore per worker, which is what the shared cache
above is scoped to as well.
"""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping
from typing import TYPE_CHECKING, Final

import pytest

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE

if TYPE_CHECKING:
    from eval.meeting_quality import TournamentEvalReport

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


#: Where the collection-time application parks its undo, on the Config that owns it.
_COLLECTION_TIME_ENV: Final = pytest.StashKey[pytest.MonkeyPatch]()


def pytest_configure(config: pytest.Config) -> None:
    """Apply the guard before pytest imports any test module.

    Registering this conftest runs ``pytest_configure`` immediately, which is ahead
    of collecting the directory it governs -- and collection is where the too-late
    reads live: the three opt-in ``skipif`` gates read the environment directly, and
    tests/api/test_replay_loader.py reads it through ``substrate_flag_snapshot()`` at
    module level. A fixture runs after all of that.
    """

    patch = pytest.MonkeyPatch()
    _apply_hermetic_env(patch)
    config.stash[_COLLECTION_TIME_ENV] = patch


def pytest_unconfigure(config: pytest.Config) -> None:
    """Give the ambient environment back, including after a collection error."""

    patch = config.stash.get(_COLLECTION_TIME_ENV, None)
    if patch is not None:
        patch.undo()


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


@pytest.fixture(scope="session")
def committed_9p2i_report() -> "TournamentEvalReport":
    """The committed 9p2i set's eval report — fixture-shaped access to the walk.

    The walk itself, and the cache that pays for it once per worker, live in
    :func:`tests._helpers.committed.report_9p2i`; consumers that cannot request a
    fixture call it directly.
    """

    from tests._helpers.committed import report_9p2i

    return report_9p2i()


# The Task-14.10 evidence-quality lift lever is UNCONDITIONAL since the Task-14.12
# close (the 14.9 move, applied after baseline 2 adopted it), so there is no env
# gate to clear for hermeticity — the belief fold always applies the bounds and
# the committed baseline-2 pins are recorded under that (only) substrate.
