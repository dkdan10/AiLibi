"""Unit + opt-in integration tests for the local Ollama adapter
(DESIGN.md §5, §7; Phase 7 Ollama plan; Task 7.5).

Two kinds of test live here:

* **Unit tests** drive :class:`llm.ollama_client.OllamaClient` with an
  injected ``send`` hook in place of the real transport, so they make no
  network call and need no Ollama server. They pin the request shape
  (``format`` = ``schema.model_json_schema()``, the ``seed`` /
  ``temperature`` options), the token mapping, ``cost_usd == 0.0``, the
  malformed-body → FailedCall path, ``build_default_client`` wiring, and
  the budget USD-dimension behavior.
* **Server-gated integration tests** (``TestOllamaServerRoundTrip``)
  exercise the real ``ollama`` SDK transport against a live local server.
  They are gated by the ``@ollama_server`` marker (a ``skipif`` keyed on
  ``AILIBI_RUN_OLLAMA_TESTS == "1"``), mirroring the ``real_provider``
  gate in :mod:`tests.llm.test_client`. CI leaves that env var unset, so
  they always report as skipped and never touch the network.

Async ``complete`` calls are driven with ``asyncio.run`` rather than
``pytest-asyncio`` to avoid a test-only dependency, matching the
convention in :mod:`tests.llm.test_real_provider`.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field

import pytest
from pydantic import BaseModel, ConfigDict
from pydantic_core import ValidationError

from llm.budget import BudgetExceededError, GameBudget
from llm.budgeted_client import (
    _DEFAULT_COST_PER_INPUT_TOKEN_USD,
    _DEFAULT_COST_PER_OUTPUT_TOKEN_USD,
    BudgetedLLMClient,
    _default_cost_rates,
)
from llm.client import LLMClient, LLMResponse
from llm.fake_provider import FakeProvider
from llm.ollama_client import (
    DEFAULT_OLLAMA_HOST,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_SEED,
    OllamaClient,
    OllamaRawResponse,
)
from llm.provider import (
    AnthropicClient,
    build_default_client,
    extract_parse_failure,
)


class _SampleReport(BaseModel):
    """Minimal schema standing in for a meeting report (Task 7.5 unit tests).

    Kept local so the request-shape / token / cost assertions don't couple
    to the meeting-schema internals; a valid body is
    ``{"agent_id": ..., "tick": ..., "free_text": ...}``.
    """

    model_config = ConfigDict(extra="forbid")

    agent_id: str
    tick: int
    free_text: str


_VALID_BODY = '{"agent_id": "p-1", "tick": 5, "free_text": "ok"}'
# Valid JSON but schema-invalid (missing ``tick`` and ``free_text``): the
# shape a weak local model can emit, which must surface as a FailedCall.
_MALFORMED_BODY = '{"agent_id": "p-1"}'


@dataclass
class _RecordingSend:
    """Injectable ``send`` hook that records its kwargs and returns ``raw``.

    Stands in for the real ``ollama`` transport so the unit tests assert
    exactly what :meth:`OllamaClient.complete` would POST, with no network.
    """

    raw: OllamaRawResponse
    calls: list[dict[str, object]] = field(default_factory=list)

    async def __call__(
        self,
        *,
        host: str,
        model: str,
        prompt: str,
        format_schema: dict[str, object] | None,
        options: dict[str, object],
    ) -> OllamaRawResponse:
        self.calls.append(
            {
                "host": host,
                "model": model,
                "prompt": prompt,
                "format_schema": format_schema,
                "options": options,
            }
        )
        return self.raw


def _send_returning(
    *,
    text: str = _VALID_BODY,
    model: str = DEFAULT_OLLAMA_MODEL,
    prompt_eval_count: int = 11,
    eval_count: int = 7,
) -> _RecordingSend:
    return _RecordingSend(
        raw=OllamaRawResponse(
            text=text,
            model=model,
            prompt_eval_count=prompt_eval_count,
            eval_count=eval_count,
        )
    )


class TestProtocolConformance:
    def test_ollama_client_is_an_llm_client(self) -> None:
        client = OllamaClient(host="localhost:11434", seed=7)
        assert isinstance(client, LLMClient)


class TestRequestShape:
    """The POST carries ``format = schema.model_json_schema()`` for
    constrained decoding and an ``options`` block with the per-game
    ``seed`` + ``temperature`` (Task 7.5 DoD item 1)."""

    def test_schema_is_passed_as_format_for_constrained_decoding(self) -> None:
        send = _send_returning()
        client = OllamaClient(host="localhost:11434", seed=42, send=send)

        asyncio.run(
            client.complete(
                prompt="report please",
                schema=_SampleReport,
                max_tokens=128,
                temperature=0.3,
            )
        )

        assert len(send.calls) == 1
        call = send.calls[0]
        assert call["format_schema"] == _SampleReport.model_json_schema()

    def test_options_carry_temperature_seed_and_num_predict(self) -> None:
        send = _send_returning()
        client = OllamaClient(host="localhost:11434", seed=42, send=send)

        asyncio.run(
            client.complete(
                prompt="report please",
                schema=_SampleReport,
                max_tokens=128,
                temperature=0.3,
            )
        )

        options = send.calls[0]["options"]
        assert options == {"temperature": 0.3, "seed": 42, "num_predict": 128}

    def test_host_and_meeting_model_default_are_forwarded(self) -> None:
        send = _send_returning()
        client = OllamaClient(host="remote-box:9999", seed=1, send=send)

        asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
                call_kind="meeting",
            )
        )

        call = send.calls[0]
        assert call["host"] == "remote-box:9999"
        assert call["model"] == DEFAULT_OLLAMA_MODEL

    def test_trigger_call_kind_routes_to_trigger_model(self) -> None:
        send = _send_returning()
        client = OllamaClient(
            host="h",
            seed=1,
            meeting_model="meeting-model",
            trigger_model="trigger-model",
            send=send,
        )

        asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
                call_kind="trigger",
            )
        )

        assert send.calls[0]["model"] == "trigger-model"

    def test_explicit_model_override_wins_over_call_kind(self) -> None:
        send = _send_returning(model="llama3.1:8b")
        client = OllamaClient(host="h", seed=1, send=send)

        asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
                model="llama3.1:8b",
            )
        )

        assert send.calls[0]["model"] == "llama3.1:8b"

    def test_free_text_call_passes_no_format_and_returns_raw_text(self) -> None:
        # schema=None means free text: no constrained decoding (format is
        # None) and the raw response text is returned verbatim (no JSON
        # extraction).
        send = _send_returning(text="just some prose, not JSON")
        client = OllamaClient(host="h", seed=1, send=send)

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert send.calls[0]["format_schema"] is None
        assert response.text == "just some prose, not JSON"


class TestTokenMappingAndCost:
    """Ollama's ``prompt_eval_count`` / ``eval_count`` map onto
    :class:`TokenUsage`, and ``cost_usd == 0.0`` for every Ollama response
    regardless of model (Task 7.5 DoD item 2)."""

    def test_token_counters_map_onto_usage(self) -> None:
        send = _send_returning(prompt_eval_count=123, eval_count=45)
        client = OllamaClient(host="h", seed=1, send=send)

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert response.usage.input_tokens == 123
        assert response.usage.output_tokens == 45

    def test_cost_is_zero_for_default_model(self) -> None:
        send = _send_returning(model=DEFAULT_OLLAMA_MODEL)
        client = OllamaClient(host="h", seed=1, send=send)

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert response.cost_usd == 0.0
        assert response.model == DEFAULT_OLLAMA_MODEL

    @pytest.mark.parametrize("model", ["qwen2.5:7b-instruct", "llama3.1:8b", "phi3"])
    def test_cost_is_zero_regardless_of_model(self, model: str) -> None:
        # The $0 rate is keyed by PROVIDER, not model name: an A/B swap
        # (qwen2.5:7b -> llama3.1:8b) must NOT silently fall back to a
        # non-zero frontier rate.
        send = _send_returning(model=model, prompt_eval_count=999, eval_count=999)
        client = OllamaClient(host="h", seed=1, send=send)

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert response.cost_usd == 0.0


class TestMalformedBodyBecomesFailedCall:
    """A malformed local output is a recoverable FailedCall (cost + partial
    response on the propagating ValidationError), NOT a hard crash — the
    same carrier the Anthropic path uses, so the orchestrator records a
    failed-call audit row (Task 7.5 DoD item 3)."""

    def test_schema_invalid_body_surfaces_as_failed_call(self) -> None:
        send = _send_returning(text=_MALFORMED_BODY, prompt_eval_count=30, eval_count=4)
        client = OllamaClient(host="h", seed=1, send=send)
        prompt = "x" * 40

        with pytest.raises(ValidationError) as exc_info:
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )

        failure = extract_parse_failure(exc_info.value)
        assert failure is not None, "expected an LLMCallFailure on the exception"
        assert failure.model == DEFAULT_OLLAMA_MODEL
        assert failure.input_tokens == 30
        assert failure.output_tokens == 4
        assert failure.prompt_length == len(prompt)
        # A local model is free even when it produces a broken body.
        assert failure.cost_usd == 0.0
        assert failure.error_type == "ValidationError"
        assert failure.raw_response == _MALFORMED_BODY

    def test_json_with_prose_preamble_still_parses_via_shared_extractor(self) -> None:
        # Reuse of llm.provider._extract_json_block means a prose preamble
        # before the JSON object is stripped before validation, exactly as
        # for the Anthropic client (so 7.6's normalization will cover Ollama
        # through the same shared path).
        send = _send_returning(text=f"Here is my report.\n{_VALID_BODY}")
        client = OllamaClient(host="h", seed=1, send=send)

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
            )
        )

        # The recorded text is the post-extraction JSON object.
        assert response.text == _VALID_BODY
        _SampleReport.model_validate_json(response.text)


class TestSeedDerivation:
    """``options.seed`` is derived from the per-game seed: fixed across
    calls within one client (reproducible-ish), varies by client (distinct
    games don't collide), and is neither a single baked-in constant nor a
    per-call hash (Task 7.5 DoD item 1)."""

    def test_seed_is_constant_across_calls_not_per_call_hash(self) -> None:
        send = _send_returning()
        client = OllamaClient(host="h", seed=314, send=send)

        for prompt in ("first prompt", "a completely different prompt"):
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=None,
                    max_tokens=32,
                    temperature=0.0,
                )
            )

        seeds = [call["options"]["seed"] for call in send.calls]  # type: ignore[index]
        assert seeds == [314, 314]

    def test_seed_varies_by_client_so_games_do_not_collide(self) -> None:
        send_a = _send_returning()
        send_b = _send_returning()
        client_a = OllamaClient(host="h", seed=7, send=send_a)
        client_b = OllamaClient(host="h", seed=8, send=send_b)

        for client in (client_a, client_b):
            asyncio.run(
                client.complete(
                    prompt="same prompt",
                    schema=None,
                    max_tokens=32,
                    temperature=0.0,
                )
            )

        assert send_a.calls[0]["options"]["seed"] == 7  # type: ignore[index]
        assert send_b.calls[0]["options"]["seed"] == 8  # type: ignore[index]


class TestBuildDefaultClientOllama:
    """``build_default_client`` gains an ``ollama`` branch reusing the model
    knobs; the ``fake`` and ``anthropic`` branches are unchanged (Task 7.5
    DoD item 4)."""

    def test_ollama_provider_routes_to_ollama_client(self) -> None:
        client = build_default_client(env={"AILIBI_LLM_PROVIDER": "ollama"})
        assert isinstance(client, OllamaClient)

    def test_defaults_host_and_model(self) -> None:
        client = build_default_client(env={"AILIBI_LLM_PROVIDER": "ollama"})
        assert isinstance(client, OllamaClient)
        assert client._host == DEFAULT_OLLAMA_HOST
        assert client._meeting_model == DEFAULT_OLLAMA_MODEL
        assert client._trigger_model == DEFAULT_OLLAMA_MODEL

    def test_host_and_model_knobs_are_read_from_env(self) -> None:
        client = build_default_client(
            env={
                "AILIBI_LLM_PROVIDER": "ollama",
                "AILIBI_OLLAMA_HOST": "gpu-box:11434",
                "AILIBI_LLM_MEETING_MODEL": "qwen2.5:14b-instruct",
                "AILIBI_LLM_TRIGGER_MODEL": "qwen2.5:3b-instruct",
            }
        )
        assert isinstance(client, OllamaClient)
        assert client._host == "gpu-box:11434"
        assert client._meeting_model == "qwen2.5:14b-instruct"
        assert client._trigger_model == "qwen2.5:3b-instruct"

    def test_explicit_seed_arg_is_threaded_into_the_client(self) -> None:
        client = build_default_client(env={"AILIBI_LLM_PROVIDER": "ollama"}, seed=2024)
        assert isinstance(client, OllamaClient)
        assert client._seed == 2024

    def test_seed_is_read_from_env_when_no_arg(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "ollama", "AILIBI_OLLAMA_SEED": "0123"}
        )
        assert isinstance(client, OllamaClient)
        # Base-10 parse, leading zeros tolerated.
        assert client._seed == 123

    def test_seed_defaults_when_unset(self) -> None:
        client = build_default_client(env={"AILIBI_LLM_PROVIDER": "ollama"})
        assert isinstance(client, OllamaClient)
        assert client._seed == DEFAULT_OLLAMA_SEED

    def test_explicit_seed_arg_wins_over_env(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "ollama", "AILIBI_OLLAMA_SEED": "999"},
            seed=42,
        )
        assert isinstance(client, OllamaClient)
        assert client._seed == 42

    def test_non_integer_seed_env_is_fail_loud(self) -> None:
        with pytest.raises(ValueError, match="AILIBI_OLLAMA_SEED"):
            build_default_client(
                env={"AILIBI_LLM_PROVIDER": "ollama", "AILIBI_OLLAMA_SEED": "abc"}
            )

    def test_fake_branch_is_unchanged(self) -> None:
        assert isinstance(build_default_client(env={}), FakeProvider)

    def test_anthropic_branch_is_unchanged(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k"}
        )
        assert isinstance(client, AnthropicClient)

    def test_unknown_provider_error_mentions_ollama(self) -> None:
        with pytest.raises(ValueError, match="ollama"):
            build_default_client(env={"AILIBI_LLM_PROVIDER": "bogus"})


class TestBudgetUsdDimensionDisabledForOllama:
    """The USD budget dimension is disabled for Ollama (pre-flight rates →
    0 via the client's hint) while the token caps stay intact; the
    Anthropic / fake budget behavior is unchanged (Task 7.5 DoD item 5)."""

    def test_ollama_resolves_to_zero_preflight_rates(self) -> None:
        client = OllamaClient(host="h", seed=1)
        assert _default_cost_rates(client) == (0.0, 0.0)

    def test_hintless_client_keeps_frontier_default_rates(self) -> None:
        # The fake (and Anthropic) expose no hint, so the budget layer keeps
        # the frontier-calibrated defaults — the Anthropic path is unchanged.
        assert _default_cost_rates(FakeProvider()) == (
            _DEFAULT_COST_PER_INPUT_TOKEN_USD,
            _DEFAULT_COST_PER_OUTPUT_TOKEN_USD,
        )

    def test_explicit_rates_override_the_inner_hint(self) -> None:
        client = OllamaClient(host="h", seed=1)
        budgeted = BudgetedLLMClient(
            inner=client,
            budget=GameBudget(max_cost_usd=1.0),
            cost_per_input_token_usd=5.0,
            cost_per_output_token_usd=7.0,
        )
        usage, cost = budgeted.estimate(prompt="abcd", max_tokens=10)
        # 1 input token (ceil(4/4)) * 5 + 10 output * 7 = 75.0.
        assert cost == pytest.approx(75.0)
        assert usage.output_tokens == 10

    def test_ollama_preflight_does_not_trip_zero_usd_ceiling(self) -> None:
        # A $0 USD cap would reject any frontier call in pre-flight; for
        # Ollama the USD estimate is 0 so a free run sails through.
        send = _send_returning()
        client = OllamaClient(host="h", seed=1, send=send)
        budget = GameBudget(
            max_cost_usd=0.0, max_input_tokens=10_000, max_output_tokens=10_000
        )
        budgeted = BudgetedLLMClient(inner=client, budget=budget)

        response = asyncio.run(
            budgeted.complete(
                prompt="report please",
                schema=_SampleReport,
                max_tokens=512,
                temperature=0.0,
            )
        )

        assert response.cost_usd == 0.0
        assert budget.snapshot().cost_usd == 0.0

    def test_ollama_token_caps_still_enforced(self) -> None:
        # Zeroing the USD dimension must NOT disable the token ceiling — a
        # local model can ramble, so the token cap is the real backstop.
        send = _send_returning()
        client = OllamaClient(host="h", seed=1, send=send)
        budget = GameBudget(max_cost_usd=0.0, max_input_tokens=5, max_output_tokens=5)
        budgeted = BudgetedLLMClient(inner=client, budget=budget)

        with pytest.raises(BudgetExceededError) as exc_info:
            asyncio.run(
                budgeted.complete(
                    prompt="report please",
                    schema=_SampleReport,
                    max_tokens=512,
                    temperature=0.0,
                )
            )
        assert exc_info.value.dimension in {"input_tokens", "output_tokens"}

    def test_hintless_client_still_trips_usd_ceiling_in_preflight(self) -> None:
        # Pin that the frontier USD estimate is still applied to a hint-less
        # client (Anthropic budget behavior unchanged): a tiny USD cap trips
        # pre-flight before the inner client is ever called.
        budget = GameBudget(
            max_cost_usd=1e-9, max_input_tokens=10_000, max_output_tokens=10_000
        )
        budgeted = BudgetedLLMClient(inner=FakeProvider(), budget=budget)

        with pytest.raises(BudgetExceededError) as exc_info:
            asyncio.run(
                budgeted.complete(
                    prompt="report please",
                    schema=None,
                    max_tokens=512,
                    temperature=0.0,
                )
            )
        assert exc_info.value.dimension == "cost_usd"


# Server-gated integration tests opt in via an environment flag, mirroring
# the `real_provider` gate in tests/llm/test_client.py. CI does not set
# AILIBI_RUN_OLLAMA_TESTS, so anything decorated with `ollama_server` is
# skipped by default and never reaches a network/server.
ollama_server = pytest.mark.skipif(
    os.environ.get("AILIBI_RUN_OLLAMA_TESTS") != "1",
    reason=(
        "ollama-server tests skipped by default; set "
        "AILIBI_RUN_OLLAMA_TESTS=1 (and run a reachable Ollama server) to enable"
    ),
)


def _ollama_server_reachable(host: str) -> bool:
    """Best-effort reachability probe for the opt-in integration tests.

    Imported lazily so CI (which skips these tests) never imports the
    ``ollama`` SDK here nor touches the network.
    """

    try:
        import ollama

        ollama.Client(host=host).list()
    except Exception:
        return False
    return True


class TestOllamaServerCISkip:
    """Pin that the server-gated tests are CI-skippable (mirrors
    :class:`tests.llm.test_client.TestRealProviderIsCISkipped`)."""

    @ollama_server
    def test_marked_ollama_server_test_is_visible_to_pytest(self) -> None:
        assert True

    def test_ollama_server_marker_is_skipif_in_ci(self) -> None:
        assert ollama_server.mark.name == "skipif"
        expected_condition = os.environ.get("AILIBI_RUN_OLLAMA_TESTS") != "1"
        assert ollama_server.mark.args[0] is expected_condition


class TestOllamaServerRoundTrip:
    """Live round-trip against a real local Ollama server. Opt-in only."""

    @ollama_server
    def test_real_ollama_round_trip(self) -> None:
        host = os.environ.get("AILIBI_OLLAMA_HOST", DEFAULT_OLLAMA_HOST)
        if not _ollama_server_reachable(host):
            pytest.skip(f"no reachable Ollama server at {host!r}")

        client = OllamaClient(host=host, seed=7)
        response = asyncio.run(
            client.complete(
                prompt="Respond with the single token: OK",
                schema=None,
                max_tokens=16,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.text, "expected non-empty text from the live server"
        assert response.usage.input_tokens > 0
        # A local model is free.
        assert response.cost_usd == 0.0

    @ollama_server
    def test_real_ollama_schema_constrained_round_trip(self) -> None:
        host = os.environ.get("AILIBI_OLLAMA_HOST", DEFAULT_OLLAMA_HOST)
        if not _ollama_server_reachable(host):
            pytest.skip(f"no reachable Ollama server at {host!r}")

        client = OllamaClient(host=host, seed=7)
        prompt = (
            "Output a single JSON object with fields agent_id (string), "
            "tick (integer), and free_text (string)."
        )
        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=_SampleReport,
                max_tokens=256,
                temperature=0.0,
            )
        )

        assert response.cost_usd == 0.0
        _SampleReport.model_validate_json(response.text)
