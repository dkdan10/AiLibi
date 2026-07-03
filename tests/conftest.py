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
"""

from __future__ import annotations

import pytest

from agents.memory.beliefs import ENV_EVIDENCE_QUALITY_LIFT
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE


@pytest.fixture(autouse=True)
def _force_fake_llm_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin the default LLM provider to the fake adapter for every test."""

    monkeypatch.setenv(ENV_PROVIDER, PROVIDER_FAKE)


@pytest.fixture(autouse=True)
def _clear_evidence_quality_lift_lever(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pin the Task-14.10 belief-fold lever to its default OFF for every test.

    The same hermeticity guard as ``_force_fake_llm_provider``: the suite's
    committed-bytes pins and fold-arithmetic expectations are recorded under
    the default-OFF substrate, so a shell that exports
    ``AILIBI_EVIDENCE_QUALITY_LIFT=1`` (the Task-14.12 recording
    configuration) must not silently flip the fold under them. Tests that
    exercise the lever ON set the variable explicitly (``monkeypatch.setenv``
    after this fixture, or an explicit ``env=`` mapping into the resolver),
    so they are unaffected.
    """

    monkeypatch.delenv(ENV_EVIDENCE_QUALITY_LIFT, raising=False)
