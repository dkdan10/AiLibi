"""Provider doubles shaped like the real endpoint's own failures.

Two families live here. :class:`BurnedCallProvider` BILLS for a call and then
refuses its own payload; :class:`NoCompletionProvider` answers with nothing at
all — the class the run of 2026-09-13 stopped on. Both exist for the same
reason: the failure they plant is produced by the provider adapter, before any
client downstream can log it, so neither was reachable offline until a double
wore the adapter's own shape.

Every other double in `tests/experiments/test_fresh_deduction_instrument.py`
RETURNS an invalid payload. That is the manager-side case: the recording client
logged the call before the manager parsed it, so the spend is in the meeting
row's `llm_calls` already. A real provider validates the completion itself and
re-raises the `ValidationError` with the burned call's usage attached
(`llm/featherless_client.py`, and the Anthropic and Ollama adapters with it), so
the tokens ride the exception and no client downstream ever logs the call. That
class was unreachable offline until this double existed, which is why the
accounting defect it plants survived to the live run of 2026-09-10.

It lives beside the test module rather than inside it because the test module
may not import `llm.provider` at all: a gate there
(`TestLiveGate::test_this_test_module_neither_names_the_flag_nor_builds_a_client`)
keeps the file free of any route to a real client, and reads THIS file to hold
the same line — the two names below are the parse-failure seam and nothing else.
"""

from __future__ import annotations

import asyncio
from typing import Final, Literal

from pydantic import BaseModel, ValidationError

import experiments.fresh_deduction_instrument as instrument
from experiments.fresh_deduction_instrument import DryRunProvider
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.provider import LLMCallFailure, _attach_parse_failure
from meetings.schemas import ModelAuthoredVoteBallot

#: The payload this double sends and the schema refuses.
BURNED_RESPONSE: Final[str] = '{"not_a_ballot": true}'

#: The spend the run of 2026-09-10 lost: one paid call whose payload failed
#: schema validation, 2,228 input and 861 output tokens the budget charged and
#: `MeetingReplayEntry.llm_calls` could not carry.
BURNED_INPUT_TOKENS: Final[int] = 2_228
BURNED_OUTPUT_TOKENS: Final[int] = 861


def charged_parse_failure(
    schema: type[BaseModel],
    *,
    prompt: str,
    input_tokens: int,
    output_tokens: int,
    model: str = instrument.DRY_RUN_MODEL,
) -> ValidationError:
    """The exception a real provider raises after billing for a refused payload.

    The adapter validates, then re-raises with the burned call's usage attached.
    `_attach_parse_failure` is used rather than a copy of the attribute name it
    sets, so this double cannot drift from the seam
    `llm.provider.extract_parse_failure` reads.

    `model` is what the endpoint says it served. It is settable because that is
    the one fact the metadata carries which a hosted endpoint can get wrong on
    its own: a checkpoint swap shows up here just as it shows up on a response.
    """

    try:
        schema.model_validate_json(BURNED_RESPONSE)
    except ValidationError as exc:
        _attach_parse_failure(
            exc,
            LLMCallFailure(
                model=model,
                prompt_length=len(prompt),
                raw_response=BURNED_RESPONSE,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=0.0,
                error_type=type(exc).__name__,
                error_message=str(exc)[:200],
            ),
        )
        return exc
    raise RuntimeError("the planted payload has to fail this schema")


def charged_no_completion(
    message: str,
    *,
    input_tokens: int = BURNED_INPUT_TOKENS,
    output_tokens: int = BURNED_OUTPUT_TOKENS,
    model: str = instrument.DRY_RUN_MODEL,
) -> RuntimeError:
    """A failure the adapter BILLED for, wearing an empty body's wording.

    The awkward case for a classifier that reads messages: an adapter that
    charged for a call and then refused it can word the refusal any way it
    likes, including the way it words a body with nothing in it. The spend is
    real either way, so this one is a sample and not a retry — which is a
    decision about the CLASS of the failure, taken before any wording is read.
    """

    exc = RuntimeError(message)
    _attach_parse_failure(
        exc,
        LLMCallFailure(
            model=model,
            prompt_length=0,
            raw_response="",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=0.0,
            error_type=type(exc).__name__,
            error_message=message[:200],
        ),
    )
    return exc


class BurnedCallProvider(DryRunProvider):
    """A dry-run provider that bills for one ballot and then refuses it.

    A vote is the sharpest seam for it: the ballot path has no retry, so one
    raise is one burned call and one defaulted SKIP, and the unit still resolves.
    `then_transport_failure` follows the burned call with an ordinary transport
    failure, which is a stop — the case that shows whether the burned call
    reached the partial accounting a stop reports.

    `burn_on_ballot` chooses WHICH ballot burns, 1-based. The unit's last ballot
    (`instrument.AUTHORIZED_LIVING_VOTERS`) is the position that matters for a
    budget overrun: an overrun charged on any earlier call is found by the next
    call's pre-flight, and on the last one the unit budget is discarded with the
    overrun still on it, so only the post-unit read-back can find it.
    `served_model` is what the endpoint claims to have served, for the checkpoint
    swap a refused payload carries in its metadata like any other.
    """

    def __init__(
        self,
        *,
        input_tokens: int = BURNED_INPUT_TOKENS,
        output_tokens: int = BURNED_OUTPUT_TOKENS,
        then_transport_failure: bool = False,
        burn_on_ballot: int = 1,
        served_model: str = instrument.DRY_RUN_MODEL,
    ) -> None:
        super().__init__()
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.burned = 0
        self.ballots = 0
        self._then_transport_failure = then_transport_failure
        self._burn_on_ballot = burn_on_ballot
        self._served_model = served_model

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is ModelAuthoredVoteBallot:
            self.ballots += 1
            if self.ballots == self._burn_on_ballot:
                self.burned += 1
                raise charged_parse_failure(
                    schema,
                    prompt=prompt,
                    input_tokens=self.input_tokens,
                    output_tokens=self.output_tokens,
                    model=self._served_model,
                )
        if self._then_transport_failure and self.burned == 1:
            self._then_transport_failure = False
            raise RuntimeError("transport failure: connection reset by peer")
        return await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


#: The message `llm/featherless_client.py::_raw_from_response_body` raises on a
#: 2xx body with no `choices` — the response that stopped the run of 2026-09-13.
#: Copied in shape rather than paraphrased: the instrument classifies this
#: failure off the adapter's own wording, so a double that invented a message of
#: its own would prove the classifier against itself. A test holds the fragment
#: the classifier keys on to that module's source.
EMPTY_BODY_ERROR: Final[str] = (
    "Featherless response carried no choices (model='Qwen/Qwen3.6-27B'); "
    "refusing to record an empty completion."
)

#: What the same module raises once its own sends are exhausted on a dropped or
#: half-read connection (`_send_with_retry`).
TRANSPORT_ERROR: Final[str] = (
    "Featherless chat-completions POST failed after 6 attempt(s) on a "
    "transport/parse error (model='Qwen/Qwen3.6-27B'): "
    "RemoteProtocolError: incomplete chunked read"
)

#: What it raises when the body carried a choice whose assistant content was
#: empty — the second of the four shapes, and the one no double planted before
#: the realism card enumerated them.
EMPTY_CONTENT_ERROR: Final[str] = (
    "Featherless returned empty assistant content (model='Qwen/Qwen3.6-27B')."
)

#: What the same module raises when the body carried a completion but no usage
#: block it would read token counts out of, and when the block was there without
#: the two counts. Both are refusals of the whole response: what the adapter read
#: it did not pass on, so nothing rides the exception and the instrument's
#: wrapper has no usage to charge for either.
NO_USAGE_BODY_ERROR: Final[str] = (
    "Featherless response carried no usage block (model='Qwen/Qwen3.6-27B'); "
    "refusing to record 0 tokens, which would under-count the per-game token "
    "budget (the only backstop under $0 provider-keyed cost)."
)

PARTIAL_USAGE_BODY_ERROR: Final[str] = (
    "Featherless usage block omitted prompt_tokens / completion_tokens "
    "(model='Qwen/Qwen3.6-27B'); refusing to record 0 tokens, which would "
    "under-count the per-game token budget."
)

#: And what it raises on a retryable status it could not get past
#: (`_format_send_error`).
RETRYABLE_STATUS_ERROR: Final[str] = (
    "Featherless chat-completions POST failed: HTTP 503 "
    "(model='Qwen/Qwen3.6-27B'): model is busy"
)

#: What one of these doubles does to the calls it spoils. The first three return
#: no completion and are the wrapper's retry classes; `stall` holds the
#: connection open past the per-attempt wall, which is the fourth; `truncation`
#: and `invalid_schema` DO produce a completion and are the control cases — a
#: sample the run may not re-draw.
NoCompletionMode = Literal[
    "empty_body",
    "empty_content",
    "no_usage_body",
    "partial_usage_body",
    "transport_error",
    "retryable_status",
    "stall",
    "truncation",
    "invalid_schema",
]

#: The message each no-completion mode raises, so a test can plant one per
#: wording the adapter actually uses rather than per mode name.
NO_COMPLETION_MESSAGES: Final[dict[str, str]] = {
    "empty_body": EMPTY_BODY_ERROR,
    "empty_content": EMPTY_CONTENT_ERROR,
    "no_usage_body": NO_USAGE_BODY_ERROR,
    "partial_usage_body": PARTIAL_USAGE_BODY_ERROR,
    "transport_error": TRANSPORT_ERROR,
    "retryable_status": RETRYABLE_STATUS_ERROR,
}


class NoCompletionProvider(DryRunProvider):
    """A dry-run provider whose first `failures` calls come back with nothing.

    `failures` is how many consecutive attempts are spoiled, counted in
    ATTEMPTS rather than in calls, so `failures=1` is a call the wrapper's retry
    recovers and `failures=4` is one it cannot. `attempts` counts every send
    this double received, which is what a test asserting "not retried" reads.

    `stall` sleeps for `stall_seconds` instead of answering, so a wrapper given
    a short per-attempt wall cuts it off exactly the way a stalled endpoint is
    cut off. `truncation` and `invalid_schema` return a completion — the first
    at its output cap, the second a body no schema accepts — and are here to
    prove the wrapper leaves a sample alone.
    """

    def __init__(
        self,
        *,
        mode: NoCompletionMode = "empty_body",
        failures: int = 1,
        stall_seconds: float = 5.0,
    ) -> None:
        super().__init__()
        self.mode: NoCompletionMode = mode
        self.failures = failures
        self.stall_seconds = stall_seconds
        self.attempts = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        self.attempts += 1
        if self.attempts <= self.failures:
            planted = NO_COMPLETION_MESSAGES.get(self.mode)
            if planted is not None:
                raise RuntimeError(planted)
            if self.mode == "stall":
                await asyncio.sleep(self.stall_seconds)
            if self.mode == "invalid_schema" and schema is not None:
                # The adapter validated and re-raised WITHOUT usage: nothing
                # rides this exception, so nothing is charged — and it is still
                # a payload the endpoint produced, which is why it is not a
                # retry class.
                schema.model_validate_json('{"not_a_payload": true}')
        response = await super().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        if self.mode == "truncation" and self.attempts <= self.failures:
            return LLMResponse(
                text=response.text,
                usage=TokenUsage(
                    input_tokens=response.usage.input_tokens, output_tokens=max_tokens
                ),
                cost_usd=response.cost_usd,
                model=response.model,
            )
        return response
