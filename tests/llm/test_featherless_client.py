"""Unit tests for the Featherless AI adapter (DESIGN.md §7, §10.4; Task 14.1).

These drive :class:`llm.featherless_client.FeatherlessClient` with an injected
``send`` hook in place of the real ``httpx`` transport, so they make no network
call and need no API key on the wire. They pin:

* the request shape — the ``response_format_mode`` translation of ``schema``
  (default ``json_object``; ``json_schema`` / ``none`` selectable), the model
  routing per ``call_kind``, and the request-time thinking toggle;
* the transport retry/error mapping (bounded retry on transient 5xx, fail-loud
  on a permanent 4xx) via the pure ``_send_with_retry`` / ``_build_chat_payload``
  helpers;
* the token mapping + ``cost_usd == 0.0`` for every model (provider-keyed);
* the response-side thinking policy (``fail_loud`` raises on reasoning —
  INCLUDING inline ``reasoning\\n{JSON}`` content — and ``strip`` discards it);
* the malformed-body → FailedCall carrier (the shared parse seam);
* ``_raw_from_response_body`` fail-loud on missing ``usage`` / empty
  ``choices`` / empty content;
* the ``build_default_client`` wiring + the budget USD-dimension behavior;
* the model + base-URL constant pins.

Async ``complete`` calls are driven with ``asyncio.run`` rather than
``pytest-asyncio`` to avoid a test-only dependency, matching the convention in
:mod:`tests.llm.test_ollama_client`.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

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
from llm.client import LLMClient
from llm.fake_provider import FakeProvider
from llm.featherless_client import (
    DEFAULT_FEATHERLESS_BASE_URL,
    DEFAULT_FEATHERLESS_MODEL,
    FeatherlessClient,
    FeatherlessRawResponse,
    _build_chat_payload,
    _raw_from_response_body,
    _send_with_retry,
    _supports_thinking_kwarg,
)
from llm.provider import (
    AnthropicClient,
    build_default_client,
    extract_parse_failure,
)


class _SampleReport(BaseModel):
    """Minimal schema standing in for a meeting report (Task 14.1 unit tests).

    Kept local so the request-shape / token / cost assertions don't couple to
    the meeting-schema internals; a valid body is
    ``{"agent_id": ..., "tick": ..., "free_text": ...}``.
    """

    model_config = ConfigDict(extra="forbid")

    agent_id: str
    tick: int
    free_text: str


_VALID_BODY = '{"agent_id": "p-1", "tick": 5, "free_text": "ok"}'
# Valid JSON but schema-invalid (missing ``tick`` and ``free_text``): the shape
# a model can emit even under strict response_format, which must surface as a
# FailedCall.
_MALFORMED_BODY = '{"agent_id": "p-1"}'


@dataclass
class _RecordingSend:
    """Injectable ``send`` hook that records its kwargs and returns ``raw``.

    Stands in for the real ``httpx`` transport so the unit tests assert exactly
    what :meth:`FeatherlessClient.complete` would POST, with no network.
    """

    raw: FeatherlessRawResponse
    calls: list[dict[str, Any]] = field(default_factory=list)

    async def __call__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        prompt: str,
        response_format: dict[str, Any] | None,
        max_tokens: int,
        temperature: float,
        request_thinking: bool,
    ) -> FeatherlessRawResponse:
        self.calls.append(
            {
                "base_url": base_url,
                "api_key": api_key,
                "model": model,
                "prompt": prompt,
                "response_format": response_format,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "request_thinking": request_thinking,
            }
        )
        return self.raw


def _send_returning(
    *,
    text: str = _VALID_BODY,
    model: str = DEFAULT_FEATHERLESS_MODEL,
    prompt_tokens: int = 11,
    completion_tokens: int = 7,
    reasoning_content: str = "",
) -> _RecordingSend:
    return _RecordingSend(
        raw=FeatherlessRawResponse(
            text=text,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_content=reasoning_content,
        )
    )


def _client(send: _RecordingSend, **kwargs: Any) -> FeatherlessClient:
    return FeatherlessClient(api_key="test-key", send=send, **kwargs)


class TestProtocolConformance:
    def test_featherless_client_is_an_llm_client(self) -> None:
        client = FeatherlessClient(api_key="k")
        assert isinstance(client, LLMClient)


class TestConstantPins:
    """The Featherless defaults are pinned so a change is a deliberate edit.

    The model default leads the Phase-14 slate (non-binding until 14.6); the
    base URL is the hosted OpenAI-compatible endpoint.
    """

    def test_default_model_is_qwen3_32b(self) -> None:
        assert DEFAULT_FEATHERLESS_MODEL == "Qwen/Qwen3-32B"

    def test_default_base_url_is_hosted_featherless(self) -> None:
        assert DEFAULT_FEATHERLESS_BASE_URL == "https://api.featherless.ai/v1"


class TestConstructorValidation:
    def test_empty_api_key_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="api_key"):
            FeatherlessClient(api_key="")

    def test_empty_base_url_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="base_url"):
            FeatherlessClient(api_key="k", base_url="")

    def test_unknown_thinking_policy_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="thinking_policy"):
            FeatherlessClient(api_key="k", thinking_policy="loud")  # type: ignore[arg-type]

    def test_unknown_response_format_mode_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="response_format_mode"):
            FeatherlessClient(api_key="k", response_format_mode="grammar")  # type: ignore[arg-type]


class TestResponseFormatMode:
    """A structured call translates ``schema`` into the wire ``response_format``
    per the configured mode. Default is ``json_object`` (the Featherless-
    supported mode; strict ``json_schema`` is REJECTED by the slate — owner-
    ratified deviation 2026-06-27). ``json_schema`` stays selectable for a
    future endpoint/model; ``none`` sends nothing; there is no silent fallback
    (Task 14.1 DoD item 1)."""

    def test_default_mode_is_json_object(self) -> None:
        send = _send_returning()
        client = _client(send)

        asyncio.run(
            client.complete(
                prompt="report please",
                schema=_SampleReport,
                max_tokens=128,
                temperature=0.3,
            )
        )

        assert send.calls[0]["response_format"] == {"type": "json_object"}

    def test_json_schema_mode_builds_strict_json_schema(self) -> None:
        send = _send_returning()
        client = _client(send, response_format_mode="json_schema")

        asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=8, temperature=0.0
            )
        )

        assert send.calls[0]["response_format"] == {
            "type": "json_schema",
            "json_schema": {
                "name": "_SampleReport",
                "schema": _SampleReport.model_json_schema(),
                "strict": True,
            },
        }

    def test_none_mode_sends_no_response_format_even_with_schema(self) -> None:
        # The pure Anthropic shape: no response_format; the shared seam carries
        # correctness. Distinct from a free-text call (which is None because
        # schema is None, not because of the mode).
        send = _send_returning()
        client = _client(send, response_format_mode="none")

        asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=8, temperature=0.0
            )
        )

        assert send.calls[0]["response_format"] is None

    def test_free_text_call_has_no_response_format_in_any_mode(self) -> None:
        for mode in ("json_object", "json_schema", "none"):
            send = _send_returning(text="prose")
            client = _client(send, response_format_mode=mode)
            asyncio.run(
                client.complete(prompt="p", schema=None, max_tokens=8, temperature=0.0)
            )
            assert send.calls[0]["response_format"] is None, mode

    def test_max_tokens_and_temperature_are_forwarded(self) -> None:
        send = _send_returning()
        client = _client(send)

        asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=128, temperature=0.3
            )
        )

        call = send.calls[0]
        assert call["max_tokens"] == 128
        assert call["temperature"] == 0.3

    def test_api_key_and_base_url_are_forwarded(self) -> None:
        send = _send_returning()
        client = FeatherlessClient(
            api_key="secret", base_url="https://proxy.example/v1", send=send
        )

        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=8, temperature=0.0)
        )

        call = send.calls[0]
        assert call["api_key"] == "secret"
        assert call["base_url"] == "https://proxy.example/v1"

    def test_trailing_slash_in_base_url_is_normalized(self) -> None:
        send = _send_returning()
        client = FeatherlessClient(
            api_key="k", base_url="https://proxy.example/v1/", send=send
        )

        asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=8, temperature=0.0)
        )

        assert send.calls[0]["base_url"] == "https://proxy.example/v1"

    def test_request_thinking_defaults_off(self) -> None:
        # Mirrors Ollama's think=False default: the production client does not
        # ask the model to reason.
        send = _send_returning()
        client = _client(send)

        asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=8, temperature=0.0
            )
        )

        assert send.calls[0]["request_thinking"] is False

    def test_request_thinking_on_is_forwarded(self) -> None:
        # The request-time thinking toggle is distinct from the response-side
        # policy: 14.4's non-thinking/thinking sweep axis drives this knob.
        send = _send_returning()
        client = _client(send, request_thinking=True, thinking_policy="strip")

        asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=8, temperature=0.0
            )
        )

        assert send.calls[0]["request_thinking"] is True

    def test_free_text_call_passes_no_response_format_and_returns_raw_text(
        self,
    ) -> None:
        send = _send_returning(text="just some prose, not JSON")
        client = _client(send)

        response = asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=64, temperature=0.0)
        )

        assert send.calls[0]["response_format"] is None
        assert response.text == "just some prose, not JSON"

    def test_meeting_call_kind_routes_to_meeting_model(self) -> None:
        send = _send_returning(model="meeting-model")
        client = _client(
            send, meeting_model="meeting-model", trigger_model="trigger-model"
        )

        asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
                call_kind="meeting",
            )
        )

        assert send.calls[0]["model"] == "meeting-model"

    def test_trigger_call_kind_routes_to_trigger_model(self) -> None:
        send = _send_returning(model="trigger-model")
        client = _client(
            send, meeting_model="meeting-model", trigger_model="trigger-model"
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
        send = _send_returning(model="GLM-4-32B")
        client = _client(send)

        asyncio.run(
            client.complete(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
                model="GLM-4-32B",
            )
        )

        assert send.calls[0]["model"] == "GLM-4-32B"

    def test_default_meeting_model_is_forwarded(self) -> None:
        send = _send_returning()
        client = _client(send)

        asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
                call_kind="meeting",
            )
        )

        assert send.calls[0]["model"] == DEFAULT_FEATHERLESS_MODEL


class TestTokenMappingAndCost:
    """OpenAI ``prompt_tokens`` / ``completion_tokens`` map onto
    :class:`TokenUsage`, and ``cost_usd == 0.0`` for every Featherless response
    regardless of model (Task 14.1 DoD item 2)."""

    def test_token_counters_map_onto_usage(self) -> None:
        send = _send_returning(prompt_tokens=123, completion_tokens=45)
        client = _client(send)

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.usage.input_tokens == 123
        assert response.usage.output_tokens == 45

    def test_cost_is_zero_for_default_model(self) -> None:
        send = _send_returning(model=DEFAULT_FEATHERLESS_MODEL)
        client = _client(send)

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.cost_usd == 0.0
        assert response.model == DEFAULT_FEATHERLESS_MODEL

    @pytest.mark.parametrize(
        "model",
        [
            "Qwen/Qwen3-32B",
            "Qwen/Qwen3-30B-A3B",
            "zai-org/GLM-4-32B",
            "some-rp-finetune",
        ],
    )
    def test_cost_is_zero_regardless_of_model(self, model: str) -> None:
        # The $0 rate is keyed by PROVIDER, not model name: an A/B swap across
        # the slate must NOT silently fall back to a non-zero frontier rate.
        send = _send_returning(model=model, prompt_tokens=999, completion_tokens=999)
        client = _client(send)

        response = asyncio.run(
            client.complete(prompt="p", schema=None, max_tokens=64, temperature=0.0)
        )

        assert response.cost_usd == 0.0

    def test_preflight_rates_are_zero(self) -> None:
        client = FeatherlessClient(api_key="k")
        assert client.preflight_cost_per_input_token_usd == 0.0
        assert client.preflight_cost_per_output_token_usd == 0.0


class TestResponseBodyMapping:
    """``_raw_from_response_body`` (split out of ``_default_send``) maps an
    OpenAI-shaped body and fails loud on the anomalous shapes a completed
    response never produces — no silent fallback on the usage counters that are
    the only backstop under $0 provider-keyed cost (Task 14.1 DoD item 5)."""

    def _body(self, **overrides: Any) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": "server-model",
            "choices": [{"message": {"content": _VALID_BODY, "reasoning_content": ""}}],
            "usage": {"prompt_tokens": 11, "completion_tokens": 7},
        }
        body.update(overrides)
        return body

    def test_happy_path_maps_model_text_and_counters(self) -> None:
        raw = _raw_from_response_body(self._body(), model="requested-model")
        assert raw.model == "server-model"
        assert raw.text == _VALID_BODY
        assert raw.prompt_tokens == 11
        assert raw.completion_tokens == 7
        assert raw.reasoning_content == ""

    def test_reasoning_content_is_surfaced_for_the_guard(self) -> None:
        body = self._body(
            choices=[{"message": {"content": _VALID_BODY, "reasoning_content": "hmm"}}]
        )
        raw = _raw_from_response_body(body, model="m")
        assert raw.reasoning_content == "hmm"

    def test_absent_reasoning_content_maps_to_empty_string(self) -> None:
        body = self._body(choices=[{"message": {"content": _VALID_BODY}}])
        raw = _raw_from_response_body(body, model="m")
        assert raw.reasoning_content == ""

    def test_model_falls_back_to_requested_when_absent(self) -> None:
        body = self._body()
        del body["model"]
        raw = _raw_from_response_body(body, model="requested-model")
        assert raw.model == "requested-model"

    def test_empty_choices_fails_loud(self) -> None:
        with pytest.raises(RuntimeError, match="no choices"):
            _raw_from_response_body(self._body(choices=[]), model="m")

    def test_missing_choices_fails_loud(self) -> None:
        body = self._body()
        del body["choices"]
        with pytest.raises(RuntimeError, match="no choices"):
            _raw_from_response_body(body, model="m")

    def test_empty_content_fails_loud(self) -> None:
        body = self._body(choices=[{"message": {"content": ""}}])
        with pytest.raises(RuntimeError, match="empty assistant content"):
            _raw_from_response_body(body, model="m")

    def test_missing_usage_fails_loud(self) -> None:
        body = self._body()
        del body["usage"]
        with pytest.raises(RuntimeError, match="no usage block"):
            _raw_from_response_body(body, model="m")

    def test_missing_completion_tokens_fails_loud(self) -> None:
        body = self._body(usage={"prompt_tokens": 11})
        with pytest.raises(RuntimeError, match="prompt_tokens / completion_tokens"):
            _raw_from_response_body(body, model="m")

    def test_zero_completion_tokens_is_kept_not_rejected(self) -> None:
        # A genuine empty completion (0 output tokens) is distinct from a
        # MISSING counter: 0 is a real, recordable value.
        body = self._body(usage={"prompt_tokens": 5, "completion_tokens": 0})
        raw = _raw_from_response_body(body, model="m")
        assert raw.completion_tokens == 0


class TestMalformedBodyBecomesFailedCall:
    """A malformed output is a recoverable FailedCall (cost + partial response
    on the propagating ValidationError), NOT a hard crash — the same carrier
    the Anthropic / Ollama paths use (Task 14.1 DoD item 1)."""

    def test_schema_invalid_body_surfaces_as_failed_call(self) -> None:
        send = _send_returning(
            text=_MALFORMED_BODY, prompt_tokens=30, completion_tokens=4
        )
        client = _client(send)
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
        assert failure.model == DEFAULT_FEATHERLESS_MODEL
        assert failure.input_tokens == 30
        assert failure.output_tokens == 4
        assert failure.prompt_length == len(prompt)
        # A flat-rate hosted model is free even when it produces a broken body.
        assert failure.cost_usd == 0.0
        assert failure.error_type == "ValidationError"
        assert failure.raw_response == _MALFORMED_BODY

    def test_json_with_prose_preamble_parses_via_shared_extractor_under_strip(
        self,
    ) -> None:
        # Reuse of llm.provider._extract_json_block means a prose preamble
        # before the JSON object is stripped before validation. Under the strip
        # policy this is the discard mechanism for reasoning models (so 7.6's
        # normalization covers Featherless through the same shared path).
        send = _send_returning(text=f"Here is my report.\n{_VALID_BODY}")
        client = _client(send, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.text == _VALID_BODY
        _SampleReport.model_validate_json(response.text)


class TestThinkingFailLoud:
    """``fail_loud`` (default) raises on a populated reasoning channel —
    INCLUDING inline reasoning in ``content`` — via a raw-content guard that
    runs BEFORE ``_extract_json_block`` (Task 14.1 DoD item 3)."""

    def test_reasoning_content_channel_raises(self) -> None:
        send = _send_returning(reasoning_content="Let me reason step by step...")
        client = _client(send)

        with pytest.raises(RuntimeError, match="reasoning") as exc_info:
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )

        message = str(exc_info.value)
        assert "fail_loud" in message
        assert DEFAULT_FEATHERLESS_MODEL in message

    def test_inline_reasoning_then_json_raises_before_extraction(self) -> None:
        # The crux: ``_extract_json_block`` would strip the prose preamble and
        # silently accept the JSON, so fail_loud must catch the leading prose
        # BEFORE extraction. The JSON body itself is perfectly valid.
        send = _send_returning(text=f"I think p-1 is suspicious.\n{_VALID_BODY}")
        client = _client(send)

        with pytest.raises(RuntimeError, match="leading prose preamble"):
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )

    def test_think_marker_in_content_raises(self) -> None:
        send = _send_returning(text=f"<think>reasoning</think>\n{_VALID_BODY}")
        client = _client(send)

        with pytest.raises(RuntimeError, match="reasoning markers"):
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )

    def test_clean_json_first_content_does_not_raise(self) -> None:
        # The happy path: clean JSON, empty reasoning channel — no raise.
        send = _send_returning(text=_VALID_BODY)
        client = _client(send)

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )
        assert response.text == _VALID_BODY

    def test_fenced_json_does_not_trip_the_prose_guard(self) -> None:
        # A leading ```json fence is not reasoning prose; the guard must not
        # treat it as such (the shared extractor strips the fence).
        send = _send_returning(text=f"```json\n{_VALID_BODY}\n```")
        client = _client(send)

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )
        assert response.text == _VALID_BODY

    def test_whitespace_only_reasoning_channel_does_not_raise(self) -> None:
        send = _send_returning(reasoning_content="  \n\t ")
        client = _client(send)

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )
        assert response.text == _VALID_BODY

    def test_fenced_reasoning_preamble_raises(self) -> None:
        # Reasoning buried INSIDE a code fence (```json\nI think...\n{JSON}\n```)
        # must still trip fail_loud: the fence-opener is stripped before the
        # prose check so the leading rationale is not silently accepted (Codex
        # review P2). Without the fix the ``startswith("```")`` skip would let
        # it through and the extractor would record only the JSON.
        send = _send_returning(text=f"```json\nI think p-1 did it.\n{_VALID_BODY}\n```")
        client = _client(send)

        with pytest.raises(RuntimeError, match="leading prose preamble"):
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )


class TestThinkingStrip:
    """``strip`` discards reasoning EXPLICITLY (logged, never silent) so the
    14.4 sweep can evaluate reasoning models. The ``reasoning\\n{JSON}`` case
    returns the JSON rather than raising (Task 14.1 DoD item 3)."""

    def test_inline_reasoning_then_json_returns_the_json(self) -> None:
        send = _send_returning(text=f"I think p-1 is suspicious.\n{_VALID_BODY}")
        client = _client(send, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.text == _VALID_BODY
        _SampleReport.model_validate_json(response.text)

    def test_think_block_with_embedded_json_returns_final_answer(self) -> None:
        # The reasoning block carries its OWN (wrong) JSON object before the
        # final answer. The shared extractor returns the FIRST valid object, so
        # without excising the <think>...</think> block first it would record
        # the scratch JSON, not the answer (Codex review P2). Strip mode must
        # remove the block and return the real MeetingTurn/answer.
        embedded = '{"agent_id": "wrong", "tick": 0, "free_text": "scratch"}'
        send = _send_returning(
            text=f"<think>let me draft {embedded} first</think>\n{_VALID_BODY}"
        )
        client = _client(send, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.text == _VALID_BODY
        assert "wrong" not in response.text

    def test_uppercase_think_close_tag_is_stripped(self) -> None:
        # detect/strip must stay in lock-step on case: a model emitting
        # </THINK> is DETECTED as reasoning (case-insensitive), so the strip
        # must also be case-insensitive — otherwise the block (with its scratch
        # JSON) survives into the extractor and the wrong object is recorded
        # (Codex review, minor). The closing tag here is uppercase.
        embedded = '{"agent_id": "wrong", "tick": 0, "free_text": "scratch"}'
        send = _send_returning(text=f"<THINK>draft {embedded}</THINK>\n{_VALID_BODY}")
        client = _client(send, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.text == _VALID_BODY
        assert "wrong" not in response.text

    def test_reasoning_content_channel_is_discarded_not_recorded(self) -> None:
        # The dedicated channel never enters ``text``; under strip it is simply
        # discarded (and logged) rather than aborting the call.
        send = _send_returning(
            text=_VALID_BODY, reasoning_content="hidden chain of thought"
        )
        client = _client(send, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p", schema=_SampleReport, max_tokens=64, temperature=0.0
            )
        )

        assert response.text == _VALID_BODY
        assert "hidden chain of thought" not in response.text

    def test_strip_logs_the_discard(self, caplog: pytest.LogCaptureFixture) -> None:
        send = _send_returning(
            text=_VALID_BODY, reasoning_content="some chain of thought"
        )
        client = _client(send, thinking_policy="strip")

        with caplog.at_level("WARNING", logger="llm.featherless_client"):
            asyncio.run(
                client.complete(
                    prompt="p",
                    schema=_SampleReport,
                    max_tokens=64,
                    temperature=0.0,
                )
            )

        assert any(
            "discarding reasoning" in record.getMessage() for record in caplog.records
        ), "strip policy must LOG the discard (never silent)"


class TestBuildDefaultClientFeatherless:
    """``build_default_client`` gains a ``featherless`` branch; the fake /
    anthropic / ollama branches are unchanged (Task 14.1 DoD item 4)."""

    def test_featherless_provider_routes_to_featherless_client(self) -> None:
        client = build_default_client(
            env={
                "AILIBI_LLM_PROVIDER": "featherless",
                "FEATHERLESS_API_KEY": "k",
            }
        )
        assert isinstance(client, FeatherlessClient)

    def test_missing_api_key_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="FEATHERLESS_API_KEY"):
            build_default_client(env={"AILIBI_LLM_PROVIDER": "featherless"})

    def test_defaults_base_url_and_model(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "featherless", "FEATHERLESS_API_KEY": "k"}
        )
        assert isinstance(client, FeatherlessClient)
        assert client._base_url == DEFAULT_FEATHERLESS_BASE_URL.rstrip("/")
        assert client._meeting_model == DEFAULT_FEATHERLESS_MODEL
        assert client._trigger_model == DEFAULT_FEATHERLESS_MODEL

    def test_base_url_and_model_knobs_are_read_from_env(self) -> None:
        client = build_default_client(
            env={
                "AILIBI_LLM_PROVIDER": "featherless",
                "FEATHERLESS_API_KEY": "k",
                "AILIBI_FEATHERLESS_BASE_URL": "https://proxy.example/v1",
                "AILIBI_LLM_MEETING_MODEL": "zai-org/GLM-4-32B",
                "AILIBI_LLM_TRIGGER_MODEL": "Qwen/Qwen3-30B-A3B",
            }
        )
        assert isinstance(client, FeatherlessClient)
        assert client._base_url == "https://proxy.example/v1"
        assert client._meeting_model == "zai-org/GLM-4-32B"
        assert client._trigger_model == "Qwen/Qwen3-30B-A3B"

    def test_default_thinking_knobs_are_fail_loud_non_thinking(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "featherless", "FEATHERLESS_API_KEY": "k"}
        )
        assert isinstance(client, FeatherlessClient)
        assert client._request_thinking is False
        assert client._thinking_policy == "fail_loud"

    def test_default_response_format_mode_is_json_object(self) -> None:
        # The Featherless-supported default; strict json_schema is rejected by
        # the slate (owner-ratified deviation 2026-06-27).
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "featherless", "FEATHERLESS_API_KEY": "k"}
        )
        assert isinstance(client, FeatherlessClient)
        assert client._response_format_mode == "json_object"

    def test_fake_branch_is_unchanged(self) -> None:
        assert isinstance(build_default_client(env={}), FakeProvider)

    def test_anthropic_branch_is_unchanged(self) -> None:
        client = build_default_client(
            env={"AILIBI_LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "k"}
        )
        assert isinstance(client, AnthropicClient)

    def test_unknown_provider_error_mentions_featherless(self) -> None:
        with pytest.raises(ValueError, match="featherless"):
            build_default_client(env={"AILIBI_LLM_PROVIDER": "bogus"})


class TestBudgetUsdDimensionDisabledForFeatherless:
    """The USD budget dimension is disabled for Featherless (pre-flight rates →
    0 via the client's hint) while the token caps stay intact; the Anthropic /
    fake budget behavior is unchanged (Task 14.1 DoD item 2 / 5)."""

    def test_featherless_resolves_to_zero_preflight_rates(self) -> None:
        client = FeatherlessClient(api_key="k")
        assert _default_cost_rates(client) == (0.0, 0.0)

    def test_hintless_client_keeps_frontier_default_rates(self) -> None:
        assert _default_cost_rates(FakeProvider()) == (
            _DEFAULT_COST_PER_INPUT_TOKEN_USD,
            _DEFAULT_COST_PER_OUTPUT_TOKEN_USD,
        )

    def test_featherless_preflight_does_not_trip_zero_usd_ceiling(self) -> None:
        send = _send_returning()
        client = _client(send)
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

    def test_featherless_token_caps_still_enforced(self) -> None:
        # Zeroing the USD dimension must NOT disable the token ceiling — a
        # hosted model can ramble, so the token cap is the real backstop.
        send = _send_returning()
        client = _client(send)
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


@dataclass
class _FakeResponse:
    """Minimal stand-in for an ``httpx.Response`` (status + body), so the
    transport retry/error mapping is unit-testable without the network."""

    status_code: int
    _json: Any = None
    text: str = ""

    def json(self) -> Any:
        return self._json


class _FakePoster:
    """Returns a scripted sequence of :class:`_FakeResponse`, recording calls.

    Stands in for the live ``client.post`` coroutine so :func:`_send_with_retry`
    can be driven deterministically — the last response repeats once the script
    is exhausted (so a single-element script models a stable endpoint)."""

    def __init__(self, responses: list[_FakeResponse]) -> None:
        self._responses = responses
        self.calls = 0

    async def __call__(self) -> _FakeResponse:
        index = min(self.calls, len(self._responses) - 1)
        self.calls += 1
        return self._responses[index]


async def _noop_sleep(_seconds: float) -> None:
    return None


class TestBuildChatPayload:
    """The pure payload builder pins the OpenAI-compatible wire shape (Task 14.1
    DoD item 1 / item 5)."""

    def test_includes_messages_caps_and_thinking_toggle(self) -> None:
        payload = _build_chat_payload(
            model="Qwen/Qwen3-32B",
            prompt="hello",
            response_format={"type": "json_object"},
            max_tokens=128,
            temperature=0.3,
            request_thinking=False,
        )
        assert payload["model"] == "Qwen/Qwen3-32B"
        assert payload["messages"] == [{"role": "user", "content": "hello"}]
        assert payload["max_tokens"] == 128
        assert payload["temperature"] == 0.3
        assert payload["chat_template_kwargs"] == {"enable_thinking": False}
        assert payload["response_format"] == {"type": "json_object"}

    def test_omits_response_format_when_none(self) -> None:
        # A recognized (Qwen3) id so the thinking kwarg is sent — the point of
        # this test is the response_format omission, not the 14.4.1 conditional
        # (an unrecognized id now fails loud; see TestThinkingKwargConditional).
        payload = _build_chat_payload(
            model="Qwen/Qwen3-32B",
            prompt="p",
            response_format=None,
            max_tokens=8,
            temperature=0.0,
            request_thinking=True,
        )
        assert "response_format" not in payload
        assert payload["chat_template_kwargs"] == {"enable_thinking": True}


class TestSupportsThinkingKwarg:
    """The EXPLICIT per-family thinking-capability signal (Task 14.4.1).

    Qwen3 honors the ``chat_template_kwargs.enable_thinking`` chat-template
    kwarg; the non-Qwen slate (GLM, Cydonia) does not — the 14.4 sweep found the
    mandatory field collapses GLM to ``{}`` and 400/504s Cydonia. An unrecognized
    id fails loud (no silent fallback; the capability is decided up front by id,
    not by swallowing a wire 400)."""

    @pytest.mark.parametrize(
        "model",
        ["Qwen/Qwen3-32B", "Qwen/Qwen3-30B-A3B-Instruct-2507", "Qwen/Qwen3-8B"],
    )
    def test_qwen3_family_supports_kwarg(self, model: str) -> None:
        assert _supports_thinking_kwarg(model) is True

    @pytest.mark.parametrize(
        "model",
        ["zai-org/GLM-4-32B", "zai-org/GLM-4-32B-0414", "TheDrummer/Cydonia-24B-v2"],
    )
    def test_non_qwen_families_do_not_support_kwarg(self, model: str) -> None:
        assert _supports_thinking_kwarg(model) is False

    def test_unrecognized_id_fails_loud(self) -> None:
        # No silent fallback (AGENTS.md): an unclassified id raises rather than
        # guessing whether to send the Qwen-only field.
        with pytest.raises(ValueError, match="no known family"):
            _supports_thinking_kwarg("mystery-org/mystery-model-1")


class TestThinkingKwargConditional:
    """``_build_chat_payload`` gates ``chat_template_kwargs.enable_thinking`` on
    the per-family signal (Task 14.4.1). A Qwen3 request INCLUDES it (both True
    and False — byte-unchanged from 14.1); a GLM / Cydonia request OMITS the
    whole ``chat_template_kwargs`` object (an empty ``{}`` is what broke GLM);
    ``request_thinking=True`` on a non-supporting model is an explicit no-op, not
    an exception; an unrecognized id fails loud."""

    @pytest.mark.parametrize("request_thinking", [True, False])
    def test_qwen3_request_includes_enable_thinking(
        self, request_thinking: bool
    ) -> None:
        payload = _build_chat_payload(
            model="Qwen/Qwen3-32B",
            prompt="p",
            response_format={"type": "json_object"},
            max_tokens=64,
            temperature=0.0,
            request_thinking=request_thinking,
        )
        assert payload["chat_template_kwargs"] == {"enable_thinking": request_thinking}

    @pytest.mark.parametrize(
        "model",
        ["zai-org/GLM-4-32B-0414", "TheDrummer/Cydonia-24B-v2"],
    )
    @pytest.mark.parametrize("request_thinking", [True, False])
    def test_non_qwen_request_omits_chat_template_kwargs(
        self, model: str, request_thinking: bool
    ) -> None:
        # request_thinking=True must NOT raise here (the parametrize over True
        # exercises the explicit no-op) — the field is simply dropped.
        payload = _build_chat_payload(
            model=model,
            prompt="p",
            response_format={"type": "json_object"},
            max_tokens=64,
            temperature=0.0,
            request_thinking=request_thinking,
        )
        # Omitted ENTIRELY — not present as an empty ``{}`` (which collapsed GLM).
        assert "chat_template_kwargs" not in payload
        # The rest of the wire shape is the normal request, so the production
        # client can call GLM / Cydonia where 14.4 needed the bare-send workaround.
        assert payload["model"] == model
        assert payload["messages"] == [{"role": "user", "content": "p"}]
        assert payload["response_format"] == {"type": "json_object"}

    def test_unrecognized_model_id_fails_loud(self) -> None:
        with pytest.raises(ValueError, match="enable_thinking"):
            _build_chat_payload(
                model="some-rp-finetune",
                prompt="p",
                response_format=None,
                max_tokens=8,
                temperature=0.0,
                request_thinking=False,
            )


class TestNonQwenModelRoutesThroughCompleteSeam:
    """A GLM / Cydonia request flows through ``complete()`` and the SHARED
    extract->validate seam (Task 14.4.1) — the production client can call them
    where 14.4 needed the bare-send workaround. The injected send proves the
    call path with no network; the wire-shape omission is pinned in
    ``TestThinkingKwargConditional`` (the builder is downstream of the send hook
    the test replaces)."""

    @pytest.mark.parametrize(
        "model",
        ["zai-org/GLM-4-32B-0414", "TheDrummer/Cydonia-24B-v2"],
    )
    def test_non_qwen_model_parses_via_shared_seam(self, model: str) -> None:
        send = _send_returning(model=model)
        # request_thinking=True on a non-supporting model is an explicit no-op,
        # not an exception — complete() must not raise.
        client = _client(send, request_thinking=True, thinking_policy="strip")

        response = asyncio.run(
            client.complete(
                prompt="p",
                schema=_SampleReport,
                max_tokens=64,
                temperature=0.0,
                model=model,
            )
        )

        assert response.model == model
        _SampleReport.model_validate_json(response.text)


class TestSendWithRetry:
    """Bounded retry on transient 5xx / rate-limit, fail-loud on a permanent
    4xx, no silent fallback (Task 14.1 transport robustness)."""

    def test_2xx_returns_parsed_json_without_retry(self) -> None:
        poster = _FakePoster([_FakeResponse(200, _json={"ok": True})])
        body = asyncio.run(_send_with_retry(poster, model="m", sleep=_noop_sleep))
        assert body == {"ok": True}
        assert poster.calls == 1

    def test_retries_transient_500_then_succeeds(self) -> None:
        # Featherless surfaces a busy upstream as a 500; a bounded retry should
        # recover rather than abort the call.
        poster = _FakePoster(
            [
                _FakeResponse(500, text="This model is busy"),
                _FakeResponse(500, text="This model is busy"),
                _FakeResponse(200, _json={"ok": 1}),
            ]
        )
        body = asyncio.run(_send_with_retry(poster, model="m", sleep=_noop_sleep))
        assert body == {"ok": 1}
        assert poster.calls == 3

    def test_permanent_400_fails_loud_without_retry(self) -> None:
        # A permanent 400 (e.g. an unsupported json_schema request) must NOT be
        # retried and must surface a descriptive error — never a silent
        # fallback to another mode.
        poster = _FakePoster([_FakeResponse(400, text="request rejected as invalid")])
        with pytest.raises(RuntimeError, match="HTTP 400") as exc_info:
            asyncio.run(
                _send_with_retry(poster, model="Qwen/Qwen3-32B", sleep=_noop_sleep)
            )
        assert poster.calls == 1
        message = str(exc_info.value)
        assert "Qwen/Qwen3-32B" in message
        assert "rejected as invalid" in message

    def test_exhausted_retries_raise_with_last_status(self) -> None:
        poster = _FakePoster([_FakeResponse(503, text="unavailable")])
        with pytest.raises(RuntimeError, match="HTTP 503"):
            asyncio.run(
                _send_with_retry(poster, model="m", sleep=_noop_sleep, max_attempts=3)
            )
        # All attempts consumed (no early success).
        assert poster.calls == 3
