"""Real-provider round-trip tests + fence-strip unit tests (DESIGN.md §7, §10.4).

Two kinds of test live here:

* **Fence-strip unit tests** (``TestStripJsonCodeFences``) exercise the
  pure-string :func:`llm.provider._strip_json_code_fences` helper. They
  are *not* ``@real_provider``-marked and run in CI — Claude models wrap
  structured-output JSON in markdown fences by default (DESIGN.md §7
  structured output), and these pin the adapter's defensive stripping.
* **Real-provider tests** (``TestAnthropicRoundTrip``,
  ``TestAnthropicSchemaRoundTrip``) exercise
  :class:`llm.provider.AnthropicClient` against the live Anthropic API
  through the SDK transport wired in Task 3.14. They are gated by the
  ``@real_provider`` marker (a ``skipif`` keyed on
  ``AILIBI_RUN_REAL_PROVIDER_TESTS == "1"``), so CI — which leaves that
  env var unset per ``llm/README.md`` — always reports them as skipped
  and never touches the network. Run them locally with a real
  ``ANTHROPIC_API_KEY`` set.

The real-provider tests drive the async ``complete`` call with
``asyncio.run`` rather than ``pytest-asyncio`` to avoid adding a test-only
dependency, matching the ``_run`` pattern already used in
``tests/llm/test_client.py``.
"""

from __future__ import annotations

import asyncio
import os

import pytest
from pydantic_core import ValidationError

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    crewmate_report_prompt,
    impostor_report_prompt,
    vote_ballot_prompt,
)
from llm.client import LLMResponse
from llm.provider import (
    AnthropicClient,
    AnthropicRawResponse,
    _extract_json_block,
    _strip_json_code_fences,
    extract_parse_failure,
)
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    MeetingTranscript,
    ReportDocument,
    Statement,
    VoteBallot,
)
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


# A minimal, schema-shaped JSON body reused across the strip cases. The
# helper is a pure string transform, so the body need only be
# representative; it happens to be a valid ``ReportDocument`` payload.
_INNER = '{"agent_id": "p-1", "tick": 5, "free_text": "ok"}'


class TestStripJsonCodeFences:
    """Unit coverage for the pure-string fence-strip helper.

    Not ``@real_provider``-marked: these exercise string logic only and
    run in CI. The parametrized cases map 1:1 to the Task 3.15 definition
    of done, items (a)-(f).
    """

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            (f"```json\n{_INNER}\n```", _INNER),
            (f"```\n{_INNER}\n```", _INNER),
            (f"```json {_INNER} ```", _INNER),
            (_INNER, _INNER),
            (f"{_INNER}\n\n", f"{_INNER}\n\n"),
            ('{"free_text": "see ``` for code"}', '{"free_text": "see ``` for code"}'),
        ],
        ids=[
            "a_json_tag_with_newlines",
            "b_bare_fence_with_newlines",
            "c_json_tag_no_inner_newlines",
            "d_plain_json_unchanged",
            "e_trailing_whitespace_unchanged",
            "f_inner_backticks_not_fences_unchanged",
        ],
    )
    def test_documented_cases(self, text: str, expected: str) -> None:
        assert _strip_json_code_fences(text) == expected

    def test_language_tag_is_case_insensitive(self) -> None:
        assert _strip_json_code_fences(f"```JSON\n{_INNER}\n```") == _INNER

    def test_whitespace_outside_the_fences_is_trimmed(self) -> None:
        assert _strip_json_code_fences(f"  ```json\n{_INNER}\n```  ") == _INNER

    def test_unclosed_open_fence_is_stripped(self) -> None:
        # A response truncated by max_tokens may end mid-prose without ever
        # emitting the closing fence. Strip the open fence anyway so Pydantic
        # gets a chance to fail on the incomplete JSON body rather than on a
        # leading backtick (pre-Phase-4 eval crash 2026-05-25-2138).
        text = '```json\n{"agent_id": "p-1", "incomplete":'
        expected = '{"agent_id": "p-1", "incomplete":'
        assert _strip_json_code_fences(text) == expected

    def test_unclosed_open_fence_without_language_tag(self) -> None:
        text = '```\n{"foo":'
        expected = '{"foo":'
        assert _strip_json_code_fences(text) == expected

    def test_closing_fence_only_passes_through_unchanged(self) -> None:
        # No opening fence to strip — passing through is safe (the trailing
        # fence is left for Pydantic to reject as part of the JSON body).
        text = '{"foo": "bar"}\n```'
        assert _strip_json_code_fences(text) == text

    def test_inner_backticks_preserved_when_outer_fences_stripped(self) -> None:
        # Fences are anchored at the text edges, so triple-backticks inside
        # the JSON body survive even when the surrounding fences are removed.
        inner = '{"agent_id": "p-1", "free_text": "see ``` for code"}'
        assert _strip_json_code_fences(f"```json\n{inner}\n```") == inner


class TestJsonBlockExtraction:
    """Unit coverage for the balanced-block extractor (Task 3.19 finding 1).

    Not ``@real_provider``-marked: pure string logic that runs in CI. The
    extractor handles the prose-preamble and trailing-prose shapes the
    open-anchored fence strip (``TestStripJsonCodeFences``) could not,
    while delegating the no-JSON / truncated-mid-object shapes back to it.
    """

    def test_prose_preamble_then_fenced_json_extracts_json(self) -> None:
        # The crash shape from the sixth Pre-Phase-4 eval: "thinking" prose
        # before a ```json fence. The open-anchored strip left the prose +
        # fence in place and model_validate_json died on the leading "I".
        text = f"I need to analyze my memory first.\n```json\n{_INNER}\n```"
        assert _extract_json_block(text) == _INNER

    def test_prose_preamble_then_bare_json_extracts_json(self) -> None:
        text = f"Let me think step by step about my role.\n{_INNER}"
        assert _extract_json_block(text) == _INNER

    def test_json_with_trailing_prose_extracts_json(self) -> None:
        text = f"{_INNER}\n\nThat is my report. Hope it helps!"
        assert _extract_json_block(text) == _INNER

    def test_string_embedded_braces_do_not_break_depth_tracking(self) -> None:
        # The braces live inside a string literal; without string-awareness
        # the lone "}" would close the object early and truncate the body.
        text = '{"agent_id": "p-1", "free_text": "braces } and { inside"}'
        assert _extract_json_block(text) == text

    def test_escaped_quotes_inside_strings_are_respected(self) -> None:
        # The escaped quote must not end the string early (which would make
        # the following "}" look unquoted and close the object prematurely).
        text = '{"agent_id": "p-1", "free_text": "she said \\"hi\\" today"}'
        assert _extract_json_block(text) == text

    def test_multiple_balanced_blocks_returns_only_the_first(self) -> None:
        second = '{"agent_id": "p-2", "tick": 6, "free_text": "second"}'
        assert _extract_json_block(f"{_INNER}\n{second}") == _INNER

    def test_no_json_content_falls_back_unchanged(self) -> None:
        # No "{" at all -> fall back to the fence strip, which passes
        # non-fenced prose through unchanged for Pydantic to reject loud.
        assert _extract_json_block("there is no json here") == "there is no json here"


class TestFailedCallRecording:
    """The provider attaches cost + partial-response metadata to the
    ``ValidationError`` it re-raises when a structured-output response fails
    schema validation, so the orchestrator can persist a failed-call audit
    trail before the meeting aborts (Task 3.19 finding 2).

    Pure unit test: an injected ``send`` hook returns a schema-invalid body,
    so there is no network call and no ``@real_provider`` gate. Verifies the
    surfacing contract works even without a real provider call.
    """

    def test_validation_error_carries_failed_call_metadata(self) -> None:
        async def _send_invalid_body(**_kwargs: object) -> AnthropicRawResponse:
            # Valid JSON, but missing ReportDocument's required ``tick`` and
            # ``free_text`` fields -> model_validate_json raises.
            return AnthropicRawResponse(
                text='{"agent_id": "p-1"}',
                model="claude-sonnet-4-6",
                input_tokens=123,
                output_tokens=45,
            )

        client = AnthropicClient(api_key="test-key", send=_send_invalid_body)
        prompt = "x" * 40

        with pytest.raises(ValidationError) as exc_info:
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=ReportDocument,
                    max_tokens=512,
                    temperature=0.0,
                )
            )

        failure = extract_parse_failure(exc_info.value)
        assert failure is not None, "expected an LLMCallFailure on the exception"
        assert failure.model == "claude-sonnet-4-6"
        assert failure.input_tokens == 123
        assert failure.output_tokens == 45
        assert failure.prompt_length == len(prompt)
        # Sonnet list pricing makes a non-zero cost for 123 in + 45 out.
        assert failure.cost_usd > 0.0
        assert failure.error_type == "ValidationError"
        assert failure.raw_response == '{"agent_id": "p-1"}'

    def test_extract_parse_failure_returns_none_for_plain_exception(self) -> None:
        # An exception that never went through the provider carries no
        # metadata -> the recording layer records no failed-call row for it.
        assert extract_parse_failure(ValueError("unrelated")) is None


class TestAnthropicSchemaRoundTrip:
    @real_provider
    def test_report_document_schema_validates_against_live_provider(self) -> None:
        """A live structured-output call must parse as the requested schema.

        Reproduces the meeting-report path that crashed the
        2026-05-25-1539 eval: the live model fences its JSON output, and
        the adapter must strip the fence before ``model_validate_json``.
        This test would have caught that crash before any tournament spend.
        The prompt asks for clean JSON, but the test does not rely on
        instruction-following to avoid fences — the fence-strip is the
        defense; this verifies the adapter parses correctly even when the
        model fences (which it usually does).
        """
        api_key = os.environ["ANTHROPIC_API_KEY"]
        client = AnthropicClient(api_key=api_key)
        prompt = (
            "You are agent p-1 in a social-deduction game. Output ONLY a "
            "single JSON object (no prose) with EXACTLY these fields: "
            '"agent_id" (the string "p-1"), "tick" (the integer 5), '
            '"observations" (an empty array), "claims" (an empty array), '
            'and "free_text" (a one-sentence status string). Include no '
            "other fields."
        )

        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=512,
                temperature=0.0,
            )
        )

        # The adapter has already fence-stripped and validated; these
        # assertions pin the observable contract: a costed completion whose
        # recorded text is the post-strip, schema-valid JSON.
        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        doc = ReportDocument.model_validate_json(response.text)
        assert doc.agent_id == "p-1"


# A minimal-but-realistic rendered-memory view, shaped like
# agents.memory.store.render_for_prompt output (DESIGN.md §6.6). Reused
# across the production-template round-trip tests so each renders against
# the same plausible meeting context the live model would see.
_REAL_CREWMATE_MEMORY = (
    "## Your role: CREWMATE\n"
    "## Tasks completed (global): 4 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 410] You discovered p-2's body in MEDBAY.\n"
    "- [tick 402] You completed task calibrate-distributor in ELECTRICAL.\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n\n"
    "## Your current beliefs:\n"
    "- p-5: suspicion 0.70 (default 0.50)\n"
    "- p-1: suspicion 0.40 (default 0.50)\n"
)

_REAL_IMPOSTOR_MEMORY = (
    "## Your role: IMPOSTOR\n"
    "## Tasks completed (global): 4 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 402] You completed task calibrate-distributor in ELECTRICAL.\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n\n"
    "## Your current beliefs:\n"
    "- p-5: suspicion 0.30 (default 0.50)\n"
)


def _real_transcript() -> MeetingTranscript:
    """One Phase-1 report + one Phase-2 statement, enough to exercise the
    accusation-round and vote-ballot templates' transcript-rendering loops."""

    return MeetingTranscript(
        reports=(
            ReportDocument(
                agent_id="p-1",
                tick=410,
                observations=(),
                claims=(),
                free_text="I was in MEDBAY when the body was found at tick 410.",
            ),
        ),
        statements=(
            Statement(
                statement_id="m-1:r0:p-1",
                speaker="p-1",
                tick=412,
                round_index=0,
                target=None,
                claims=(),
                free_text="I have an alibi for the whole window; ask p-5.",
            ),
        ),
    )


class TestProductionTemplateSchemaRoundTrips:
    """Each production ``.j2`` template, rendered through the Jinja loader
    and sent to the live provider, must round-trip into its Pydantic schema.

    Unlike :class:`TestAnthropicSchemaRoundTrip` (which hand-writes a prompt
    asking for specific field names), these load the *actual production
    template* via :mod:`agents.strategic.prompts.loader`. That is the only
    way a prompt-template <-> schema field-name drift is exercised
    end-to-end: the FakeProvider builds schema objects from fixtures rather
    than round-tripping JSON shaped by the template, so the fake-provider
    smoke tests cannot catch the class of defect these guard against
    (DESIGN.md §5.3, §5.5, §7; audit 2026-05-25-2038).
    """

    @real_provider
    def test_crewmate_report_template_produces_valid_report_document(self) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = crewmate_report_prompt(
            agent_id="p-1",
            current_tick=410,
            meeting_trigger="p-1 reported p-2's body in MEDBAY at tick 410",
            rendered_memory=_REAL_CREWMATE_MEMORY,
            public_transcript="",
        )

        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=1024,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        doc = ReportDocument.model_validate_json(response.text)
        # The crewmate template instructs agent_id == the passed id.
        assert doc.agent_id == "p-1"

    @real_provider
    def test_impostor_report_template_produces_valid_report_document(self) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=410,
            meeting_trigger="p-1 reported p-2's body in MEDBAY at tick 410",
            rendered_memory=_REAL_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=1024,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        # The impostor template tells the model to emit any non-empty
        # agent_id (the manager overrides it), so assert parse + non-empty
        # rather than an exact id.
        doc = ReportDocument.model_validate_json(response.text)
        assert doc.agent_id

    @real_provider
    def test_accusation_round_template_produces_valid_statement(self) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = accusation_round_prompt(
            rendered_memory=_REAL_CREWMATE_MEMORY,
            transcript=_real_transcript(),
            contradictions=(),
        )

        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=Statement,
                max_tokens=1024,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        stmt = Statement.model_validate_json(response.text)
        assert stmt.free_text

    @real_provider
    def test_vote_ballot_template_produces_valid_vote_ballot(self) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_REAL_CREWMATE_MEMORY,
            transcript=_real_transcript(),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.4, trust=0.5),
                SuspicionEntry(player_id="p-5", suspicion=0.7, trust=0.3),
            ),
            candidate_targets=("p-1", "p-5"),
            skip_confidence_threshold=0.6,
        )

        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=VoteBallot,
                max_tokens=1024,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        ballot = VoteBallot.model_validate_json(response.text)
        # The vote template instructs voter == the passed voter_id.
        assert ballot.voter == "p-3"


class TestAnthropicTruncationFailureMode:
    """A meeting-protocol response (report, statement, or vote) truncated by
    ``max_tokens`` must fail with a Pydantic ``ValidationError`` on the
    incomplete JSON, NOT with an ``Invalid JSON … line 1 column 1`` error
    caused by a leading backtick from an unclosed markdown fence (pre-Phase-4
    eval crash 2026-05-25-2138,
    ``audits/audit-2026-05-25-2138-pre-phase-4-real-provider-eval.md``). The
    statement case is the seed-22 production crash characterized in
    ``audits/audit-2026-05-25-2320-seed-23-deep-debug.md``.

    Driven with ``asyncio.run`` rather than ``pytest-asyncio`` to match the
    module convention (see module docstring); ``@real_provider`` keeps it
    skipped in CI. Per-invocation cost ~$0.001 — the ``max_tokens=50`` cap
    makes the call deliberately tiny.
    """

    @real_provider
    def test_truncated_report_fails_with_validation_error_not_backtick(
        self,
    ) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = (
            "You are agent p-1 in a social-deduction game. Output a "
            "ReportDocument as a single JSON object with realistic, detailed "
            "observations, claims, and free-text prose."
        )

        with pytest.raises(ValidationError) as exc:
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=ReportDocument,
                    max_tokens=50,  # tight cap forces truncation mid-output
                    temperature=0.0,
                )
            )

        # The leading-backtick failure mode is what the 2138 eval saw;
        # confirm the fence strip means we no longer hit it.
        assert "line 1 column 1" not in str(exc.value)

    @real_provider
    def test_truncated_statement_fails_with_validation_error_not_backtick(
        self,
    ) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = (
            "You are agent p-1 in a social-deduction game meeting. Output a "
            "Statement as a single JSON object with a detailed accusation, "
            "structured claims, and free-text prose."
        )

        with pytest.raises(ValidationError) as exc:
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=Statement,
                    max_tokens=50,  # tight cap forces truncation mid-output
                    temperature=0.0,
                )
            )

        # The leading-backtick failure mode is what the 2138 eval saw;
        # confirm the fence strip means we no longer hit it.
        assert "line 1 column 1" not in str(exc.value)

    @real_provider
    def test_truncated_vote_fails_with_validation_error_not_backtick(
        self,
    ) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = (
            "You are agent p-1 in a social-deduction game meeting. Output a "
            "VoteBallot as a single JSON object with a target, a confidence, "
            "and a detailed free-text rationale."
        )

        with pytest.raises(ValidationError) as exc:
            asyncio.run(
                client.complete(
                    prompt=prompt,
                    schema=VoteBallot,
                    max_tokens=50,  # tight cap forces truncation mid-output
                    temperature=0.0,
                )
            )

        # The leading-backtick failure mode is what the 2138 eval saw;
        # confirm the fence strip means we no longer hit it.
        assert "line 1 column 1" not in str(exc.value)


class TestAnthropicProsePreamble:
    """A live response that emits "thinking" prose before its fenced JSON
    must still parse (Task 3.19 finding 1).

    The sixth Pre-Phase-4 eval
    (``audits/audit-2026-05-25-2018-pre-phase-4-real-provider-eval.md``)
    crashed at game 28 when Sonnet 4.6 emitted a prose preamble before its
    ```json fence: the open-anchored ``_strip_json_code_fences`` did not
    match, leaving the prose in place, and ``model_validate_json`` died on
    the leading "I". The balanced-block extractor ignores the preamble and
    pulls the JSON object out.

    Driven with ``asyncio.run`` rather than ``pytest-asyncio`` to match the
    module convention; ``@real_provider`` keeps it skipped in CI.
    Per-invocation cost ~$0.01.
    """

    @real_provider
    def test_prose_preamble_report_parses_without_raising(self) -> None:
        client = AnthropicClient(api_key=os.environ["ANTHROPIC_API_KEY"])
        prompt = (
            "Think step by step about your role in this meeting, narrating "
            "your reasoning in a sentence or two of prose FIRST. THEN, after "
            "that prose, emit a single ReportDocument JSON object with "
            'EXACTLY these fields: "agent_id" (the string "p-1"), "tick" '
            '(the integer 5), "observations" (an empty array), "claims" (an '
            'empty array), and "free_text" (a one-sentence status string).'
        )

        # The contract under test is simply that complete() returns without
        # raising: the extractor must strip the prose preamble before
        # validation. A pre-3.19 adapter raised ValidationError here.
        response = asyncio.run(
            client.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=2048,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd > 0.0
        # The recorded text is the post-extraction JSON object, so it
        # re-parses cleanly as the requested schema.
        doc = ReportDocument.model_validate_json(response.text)
        assert doc.agent_id
