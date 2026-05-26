"""Per-template smoke tests for the strategic prompt loader (Task 3.9 C-4).

The four ``.j2`` templates at ``agents/strategic/prompts/*.j2`` had
zero CI coverage prior to Task 3.9; a ``{% endfor %}`` typo, a wrong
kwarg name, or a schema-incompatible output would not have surfaced
until the first live-provider meeting. These tests close that gap by
exercising each template through the loader, asserting the rendered
output (a) is non-empty, (b) contains the template's distinctive
version-marker substring, and (c) parses cleanly through the
corresponding Pydantic schema after a :class:`~llm.fake_provider.FakeProvider`
round-trip.

The loader's :class:`jinja2.StrictUndefined` configuration is also
pinned: missing kwargs raise :class:`jinja2.UndefinedError` instead of
silently rendering an empty string.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

import pytest
from jinja2 import UndefinedError

from agents.strategic.prompts import (
    accusation_round_prompt,
    crewmate_report_prompt,
    impostor_report_prompt,
    vote_ballot_prompt,
)
from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_TEMPLATE,
    CREWMATE_REPORT_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    VOTE_BALLOT_TEMPLATE,
    _ENV,  # noqa: PLC2701
)
from llm.fake_provider import FakeProvider
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    ReportDocument,
    Statement,
    VoteBallot,
)

_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


_STUB_CREWMATE_MEMORY = (
    "## Your role: CREWMATE\n"
    "## Tasks completed (global): 3 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 410] You discovered p-2's body in MEDBAY.\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n\n"
    "## Your current beliefs:\n"
    "- p-5: suspicion 0.70\n"
)

_STUB_IMPOSTOR_MEMORY = (
    "## Your role: IMPOSTOR\n"
    "## Tasks completed (global): 3 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n"
)


def _stub_transcript() -> MeetingTranscript:
    """Build a minimal transcript with one report + one statement."""

    return MeetingTranscript(
        reports=(
            ReportDocument(
                agent_id="p-1",
                tick=410,
                observations=(),
                claims=(),
                free_text="stub-free-text-from-p-1",
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
                free_text="stub-statement-from-p-1",
            ),
        ),
    )


class TestLoaderEnvironment:
    def test_loader_uses_strict_undefined(self) -> None:
        # StrictUndefined makes a missing kwarg raise at render time
        # instead of producing an empty string. A regression that
        # silently relaxes this (e.g. switching to ChainableUndefined)
        # must fail this test.
        from jinja2 import StrictUndefined

        assert _ENV.undefined is StrictUndefined

    def test_loader_settings_are_pinned(self) -> None:
        assert _ENV.autoescape is False
        assert _ENV.trim_blocks is True
        assert _ENV.lstrip_blocks is True


class TestCrewmateReportTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="p-3 reported a body at tick 410",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        # The crewmate template body opens with the role tag the LLM
        # is supposed to play. A regression that swaps this for the
        # impostor framing would fail the test.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "**crewmate**" in prompt
        assert "report intake" in prompt

    def test_renders_agent_kwargs_into_prompt(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="p-3 reported a body at tick 410",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "p-3" in prompt
        assert "412" in prompt
        assert "p-3 reported a body at tick 410" in prompt
        assert _STUB_CREWMATE_MEMORY.strip() in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # A template that references a kwarg the loader's strict-undefined
        # environment was not handed must raise UndefinedError; the
        # default Undefined policy would silently render an empty string
        # and ship a malformed prompt to the LLM. Probing through the
        # raw environment proves StrictUndefined is the active policy
        # (the wrappers force-pass every kwarg by signature, so a typo
        # at the wrapper level would surface as TypeError instead -- a
        # weaker signal that does not exercise StrictUndefined).
        with pytest.raises(UndefinedError):
            _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
                agent_id="p-3",
                current_tick=412,
                meeting_trigger="trigger",
                # rendered_memory omitted on purpose.
                public_transcript="",
            )

    def test_fake_provider_response_parses_into_schema(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=256,
                temperature=0.0,
            )
        )

        # If the schema were drifting from what the template asks for
        # (missing required field, type mismatch), the fake provider's
        # internal validation would have raised before returning.
        parsed = ReportDocument.model_validate_json(response.text)
        assert isinstance(parsed, ReportDocument)


class TestImpostorReportTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        # The impostor template body opens with an explicit role line
        # that identifies the template; a regression swapping this for
        # the crewmate framing would fail.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "Your role for this match is IMPOSTOR" in prompt

    def test_renders_memory_into_prompt(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert _STUB_IMPOSTOR_MEMORY.strip() in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # impostor_report.j2 references ``rendered_memory`` and
        # ``public_transcript``. Render through the raw environment
        # with only one of them to exercise StrictUndefined directly.
        with pytest.raises(UndefinedError):
            _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
                # rendered_memory deliberately omitted.
                public_transcript="",
            )

    def test_fake_provider_response_parses_into_schema(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=ReportDocument,
                max_tokens=256,
                temperature=0.0,
            )
        )

        parsed = ReportDocument.model_validate_json(response.text)
        assert isinstance(parsed, ReportDocument)


class TestAccusationRoundTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
        )

        assert "accusation round" in prompt

    def test_renders_transcript_reports_and_statements(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
        )

        assert "stub-free-text-from-p-1" in prompt
        assert "stub-statement-from-p-1" in prompt

    def test_renders_contradictions_section(self) -> None:
        contradictions = (
            ContradictionRef(
                contradiction_id="c-1",
                kind="alibi_conflict",
                event_a_id="stmt-1",
                event_b_id="stmt-2",
                subjects=("p-5",),
                description="alibi conflict for p-5 around tick 405",
            ),
        )

        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=contradictions,
        )

        assert "alibi_conflict" in prompt
        assert "alibi conflict for p-5 around tick 405" in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        with pytest.raises(UndefinedError):
            _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
                agent_id="p-3",
                rendered_memory=_STUB_CREWMATE_MEMORY,
                # transcript deliberately omitted.
                contradictions=(),
            )

    def test_renders_speaker_self_alibi_example_with_own_id(self) -> None:
        # Task 3.20: the template must anchor the self-alibi example to
        # the speaker's own player id so the model emits
        # `"subject": "p-3"` rather than a placeholder (e.g. "p-0" /
        # "p-self") that DESIGN.md §5.4 contradiction detection cannot
        # match across speakers.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
        )

        assert '"subject": "p-3"' in prompt

    def test_fake_provider_response_parses_into_schema(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=Statement,
                max_tokens=256,
                temperature=0.0,
            )
        )

        parsed = Statement.model_validate_json(response.text)
        assert isinstance(parsed, Statement)


class TestVoteBallotTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        # vote_ballot.j2 carries an explicit visible version marker in
        # its body. A regression that bumps the version without
        # updating the test is the desired failure mode.
        assert "vote_ballot/v1" in prompt

    def test_renders_voter_and_candidates(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "`p-3`" in prompt
        assert "`p-1`" in prompt
        assert "`p-2`" in prompt

    def test_renders_suspicion_graph_entries(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.4, trust=0.5),
                SuspicionEntry(player_id="p-2", suspicion=0.7, trust=0.3),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "suspicion 0.40" in prompt
        assert "suspicion 0.70" in prompt
        assert "trust 0.50" in prompt
        assert "trust 0.30" in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # vote_ballot.j2 iterates ``transcript.reports`` near the top
        # of the body; omitting ``transcript`` must trip
        # StrictUndefined as the for-loop dereferences the missing
        # variable.
        with pytest.raises(UndefinedError):
            _ENV.get_template(VOTE_BALLOT_TEMPLATE).render(
                voter_id="p-3",
                rendered_memory=_STUB_CREWMATE_MEMORY,
                # transcript deliberately omitted.
                contradiction_flags=(),
                suspicion_graph=(),
                candidate_targets=("p-1", "p-2"),
                skip_confidence_threshold=0.6,
            )

    def test_fake_provider_response_parses_into_schema(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=VoteBallot,
                max_tokens=256,
                temperature=0.0,
            )
        )

        parsed = VoteBallot.model_validate_json(response.text)
        assert isinstance(parsed, VoteBallot)
