"""Real-provider round-trip test (DESIGN.md §7, §10.4).

Exercises :class:`llm.provider.AnthropicClient` against the live Anthropic
API through the SDK transport wired in Task 3.14. The test is gated by the
``@real_provider`` marker (a ``skipif`` keyed on
``AILIBI_RUN_REAL_PROVIDER_TESTS == "1"``), so CI — which leaves that env
var unset per ``llm/README.md`` — always reports this test as skipped and
never touches the network. Run it locally with a real ``ANTHROPIC_API_KEY``
set to validate that the adapter round-trips against the real provider.

The test drives the async ``complete`` call with ``asyncio.run`` rather
than ``pytest-asyncio`` to avoid adding a test-only dependency, matching
the ``_run`` pattern already used in ``tests/llm/test_client.py``.
"""

from __future__ import annotations

import asyncio
import os

from llm.client import LLMResponse
from llm.provider import AnthropicClient
from tests.llm.test_client import real_provider


class TestAnthropicRoundTrip:
    @real_provider
    def test_real_provider_round_trip(self) -> None:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        client = AnthropicClient(api_key=api_key)

        response = asyncio.run(
            client.complete(
                prompt="Respond with the single token: OK",
                schema=None,
                max_tokens=8,
                temperature=0.0,
            )
        )

        # Exact text is not asserted — live LLM output varies. We assert the
        # round-trip produced a real, costed completion from a named model.
        assert isinstance(response, LLMResponse)
        assert response.text, "expected a non-empty response from the live provider"
        assert response.usage.input_tokens > 0
        assert response.usage.output_tokens > 0
        assert response.cost_usd > 0.0
        assert response.model, "expected a non-empty model id from the live provider"
