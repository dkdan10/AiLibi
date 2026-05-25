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

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    crewmate_report_prompt,
    impostor_report_prompt,
    vote_ballot_prompt,
)
from llm.client import LLMResponse
from llm.provider import AnthropicClient, _strip_json_code_fences
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

    def test_open_fence_without_close_passes_through_unchanged(self) -> None:
        # Conservative: an unmatched open fence is left intact so Pydantic
        # fails loud rather than the helper guessing at a boundary.
        text = f"```json\n{_INNER}"
        assert _strip_json_code_fences(text) == text

    def test_inner_backticks_preserved_when_outer_fences_stripped(self) -> None:
        # Fences are anchored at the text edges, so triple-backticks inside
        # the JSON body survive even when the surrounding fences are removed.
        inner = '{"agent_id": "p-1", "free_text": "see ``` for code"}'
        assert _strip_json_code_fences(f"```json\n{inner}\n```") == inner


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
