"""A provider double that BILLS for a call and then refuses its own payload.

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

from typing import Final

from pydantic import BaseModel, ValidationError

import experiments.fresh_deduction_instrument as instrument
from experiments.fresh_deduction_instrument import DryRunProvider
from llm.client import CallKind, LLMResponse
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
    schema: type[BaseModel], *, prompt: str, input_tokens: int, output_tokens: int
) -> ValidationError:
    """The exception a real provider raises after billing for a refused payload.

    The adapter validates, then re-raises with the burned call's usage attached.
    `_attach_parse_failure` is used rather than a copy of the attribute name it
    sets, so this double cannot drift from the seam
    `llm.provider.extract_parse_failure` reads.
    """

    try:
        schema.model_validate_json(BURNED_RESPONSE)
    except ValidationError as exc:
        _attach_parse_failure(
            exc,
            LLMCallFailure(
                model=instrument.DRY_RUN_MODEL,
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


class BurnedCallProvider(DryRunProvider):
    """A dry-run provider that bills for one ballot and then refuses it.

    A vote is the sharpest seam for it: the ballot path has no retry, so one
    raise is one burned call and one defaulted SKIP, and the unit still resolves.
    `then_transport_failure` follows the burned call with an ordinary transport
    failure, which is a stop — the case that shows whether the burned call
    reached the partial accounting a stop reports.
    """

    def __init__(
        self,
        *,
        input_tokens: int = BURNED_INPUT_TOKENS,
        output_tokens: int = BURNED_OUTPUT_TOKENS,
        then_transport_failure: bool = False,
    ) -> None:
        super().__init__()
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.burned = 0
        self._then_transport_failure = then_transport_failure

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
        if schema is ModelAuthoredVoteBallot and self.burned == 0:
            self.burned += 1
            raise charged_parse_failure(
                schema,
                prompt=prompt,
                input_tokens=self.input_tokens,
                output_tokens=self.output_tokens,
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
