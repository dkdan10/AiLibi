"""Shared pytest fixtures for the AiLibi test suite.

Hermetic LLM provider: force ``AILIBI_LLM_PROVIDER=fake`` for every test so
the environment-selected default client
(:func:`llm.provider.build_default_client`, reached through
:func:`orchestrator.game.build_default_meeting_runner` and the public CLI
wire-up) is always the zero-cost :class:`~llm.fake_provider.FakeProvider`,
regardless of the ambient shell.

Without this guard a suite run in a real-provider-configured environment
(``AILIBI_LLM_PROVIDER=anthropic`` plus a live ``ANTHROPIC_API_KEY`` -- the
configuration the eval/dev sandboxes export) silently routes every
default-wire-up test through the paid Anthropic API: real money is spent
and a full meeting's real cost trips the $0.30 default
:class:`~llm.budget.GameBudget` cap, so those tests fail locally while
passing in CI (which exports no provider env var).

The ``@real_provider`` tests are unaffected: they construct
:class:`~llm.provider.AnthropicClient` directly from ``ANTHROPIC_API_KEY``
and gate on ``AILIBI_RUN_REAL_PROVIDER_TESTS``, never consulting
``AILIBI_LLM_PROVIDER``. Tests that exercise the provider-selection logic
itself pass an explicit ``env=`` mapping to ``build_default_client`` and so
are likewise independent of the process environment.

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

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE

if TYPE_CHECKING:
    from eval.meeting_quality import TournamentEvalReport

_REPO_ROOT = Path(__file__).resolve().parents[1]
_COMMITTED_9P2I_DIR = _REPO_ROOT / "replays" / "samples" / "9p2i"


@pytest.fixture(autouse=True)
def _force_fake_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin the default LLM provider to the fake adapter for every test."""

    monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)


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
