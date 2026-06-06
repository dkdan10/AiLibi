"""Per-template smoke tests for the strategic prompt loader (Task 3.9 / 8.8).

The four ``.j2`` templates at ``agents/strategic/prompts/*.j2`` are the
reactive accusation-chain prompts (DESIGN.md §5.2): the crewmate / impostor
**opening** templates, the reactive **reply / opt-in** template, and the
**vote** template. A ``{% endfor %}`` typo, a wrong kwarg name, or a
schema-incompatible output would not surface until the first live-provider
meeting; these tests close that gap by exercising each template through the
loader and asserting the rendered output (a) is non-empty, (b) contains the
template's distinctive version-marker substring (the four versions bump in
lockstep with ``orchestrator.game.DEFAULT_PROMPT_VERSIONS``), and (c) parses
cleanly through the corresponding Pydantic schema after a
:class:`~llm.fake_provider.FakeProvider` round-trip.

Task 8.8 reshaped the templates from the old parallel-reports
``ReportDocument`` / ``Statement`` pair to the single ordered ``turns``
list: the three meeting-turn templates now emit
:class:`~meetings.schemas.MeetingTurn` and the reactive-turn template gains
the ``prior_turn`` / ``turn_kind`` inputs.

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
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
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


def _opening_turn() -> MeetingTurn:
    """The opening turn (turn 0): an accusation against p-5."""

    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=(
            AccusationClaim(
                type="accusation",
                against="p-5",
                confidence=0.6,
                reason="near MEDBAY before the kill",
            ),
        ),
        free_text="stub-opening-from-p-1",
    )


def _stub_transcript() -> MeetingTranscript:
    """A minimal chain transcript: one opening turn + one reply turn."""

    return MeetingTranscript(
        turns=(
            _opening_turn(),
            MeetingTurn(
                turn_id="m-1:turn-1",
                turn_index=1,
                speaker="p-5",
                turn_kind="reply",
                reply_to="m-1:turn-0",
                observations=(),
                claims=(),
                free_text="stub-reply-from-p-5",
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
        # The crewmate opening template carries a visible version marker
        # (bumped to v2 in Task 8.8) plus the role framing the LLM plays.
        # A regression that swaps this for the impostor framing, or fails
        # to bump the marker in lockstep, must fail the test.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "crewmate_report.v2" in prompt
        assert "**crewmate**" in prompt
        assert "opening speaker" in prompt

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
        # and ship a malformed prompt to the LLM.
        with pytest.raises(UndefinedError):
            _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
                agent_id="p-3",
                current_tick=412,
                meeting_trigger="trigger",
                # rendered_memory omitted on purpose.
                public_transcript="",
            )

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
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
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        # If the schema were drifting from what the template asks for
        # (missing required field, type mismatch), the fake provider's
        # internal validation would have raised before returning.
        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


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
        # The impostor opening template carries its visible version marker
        # (bumped to v3 in Task 8.8) and the explicit role line.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "impostor_report_v3" in prompt
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

    def test_teammate_block_renders_only_when_non_empty(self) -> None:
        # The 7.12 firewall block renders only for a coordinating impostor.
        without = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )
        with_team = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-5",),
        )

        assert "fellow impostors" not in without.lower()
        assert "fellow impostors" in with_team.lower()
        assert "p-5" in with_team

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # impostor_report.j2 references ``rendered_memory`` and
        # ``public_transcript``. Render through the raw environment
        # with only one of them to exercise StrictUndefined directly.
        with pytest.raises(UndefinedError):
            _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
                # rendered_memory deliberately omitted.
                public_transcript="",
            )

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
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
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


class TestAccusationRoundTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "accusation_round.v4" in prompt
        assert "reactive accusation chain" in prompt

    def test_reply_turn_frames_the_accuser(self) -> None:
        # A reply turn names the prior turn's speaker so the model knows
        # who it is answering (the "who accused me" context, Task 8.8).
        prompt = accusation_round_prompt(
            agent_id="p-5",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "reply" in prompt
        assert "`p-1`" in prompt  # the accuser

    def test_opt_in_turn_is_terminal_and_non_chaining(self) -> None:
        # An opt-in turn frames itself as terminal (no prior_turn) and
        # explicitly does not extend the chain (DESIGN.md §5.2 PHASE 3).
        prompt = accusation_round_prompt(
            agent_id="p-7",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
        )

        assert "opt-in" in prompt.lower()
        assert "terminal turn" in prompt
        assert "does NOT extend" in prompt

    def test_renders_transcript_turns(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "stub-opening-from-p-1" in prompt
        assert "stub-reply-from-p-5" in prompt
        # The turn ids anchor a vote's primary_reason_id.
        assert "m-1:turn-0" in prompt
        assert "m-1:turn-1" in prompt

    def test_renders_contradictions_section(self) -> None:
        contradictions = (
            ContradictionRef(
                contradiction_id="c-1",
                kind="alibi_conflict",
                event_a_id="m-1:turn-0:claim-0",
                event_b_id="m-1:turn-1:claim-0",
                subjects=("p-5",),
                description="alibi conflict for p-5 around tick 405",
            ),
        )

        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=contradictions,
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "alibi_conflict" in prompt
        assert "alibi conflict for p-5 around tick 405" in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        with pytest.raises(UndefinedError):
            _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
                agent_id="p-3",
                rendered_memory=_STUB_CREWMATE_MEMORY,
                # transcript deliberately omitted; the turn loop trips.
                contradictions=(),
                prior_turn=None,
                turn_kind="reply",
            )

    def test_renders_speaker_self_alibi_example_with_own_id(self) -> None:
        # The template must anchor the self-alibi example to the speaker's
        # own player id so the model emits `"subject": "p-3"` rather than a
        # placeholder that DESIGN.md §5.4 contradiction detection cannot
        # match across speakers (Task 3.20).
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert '"subject": "p-3"' in prompt

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


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

        # vote_ballot.j2 carries an explicit visible version marker in its
        # body, bumped to v4 in Task 8.16 (the `primary_reason_id` example
        # is now sourced from the live transcript). A regression that bumps
        # the version without updating the test is the desired failure mode.
        assert "vote_ballot/v4" in prompt

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

    def test_renders_transcript_turns(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "stub-opening-from-p-1" in prompt
        assert "stub-reply-from-p-5" in prompt
        # The opening turn's accusation is surfaced for the voter.
        assert "accuses `p-5`" in prompt

    def test_primary_reason_id_example_is_sourced_from_transcript(self) -> None:
        # Task 8.16 (DESIGN.md §5.5; audit gp-3): the decision-rule example
        # for `primary_reason_id` must cite a REAL turn id from the rendered
        # transcript, never the old hardcoded `m-7:turn-4` (which the 7B
        # model copied verbatim into other meetings' ballots).
        transcript = _stub_transcript()
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=transcript,
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        # The example is the first turn's real id; the hardcoded one is gone.
        assert transcript.turns[0].turn_id == "m-1:turn-0"
        assert '`"m-1:turn-0"`' in prompt
        assert "m-7:turn-4" not in prompt

    def test_primary_reason_id_example_omitted_for_empty_transcript(self) -> None:
        # With no turns there is no real id to cite, so the example clause is
        # dropped rather than falling back to a hardcoded (dangling) id.
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "m-7:turn-4" not in prompt
        assert "primary_reason_id" in prompt

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
        # vote_ballot.j2 iterates ``transcript.turns`` near the top
        # of the body; omitting ``transcript`` must trip StrictUndefined
        # as the for-loop dereferences the missing variable.
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
