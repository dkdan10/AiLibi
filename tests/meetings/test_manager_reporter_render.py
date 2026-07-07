"""Reporter-exculpation vote-surface render threading (Task 15.5).

The render half of the default-OFF ``reporter_exculpation`` lever
(tasks/post-phase-14-clean-up.md H5): the manager threads the body-report
meeting's reporter (``MeetingTrigger.triggered_by`` -- the meeting-scope
identity, never re-derived from the transcript) into the vote-ballot renderer's
DEFAULTED ``reporter_id`` input ONLY when the lever is ON and the meeting is a
body report, and the v6 ``vote_ballot`` template renders the self-report
base-rate annotation only when it is supplied. Lever-OFF (the default) threads
``None`` and the prompt is byte-identical.

These tests drive the real ``_collect_one_ballot`` seam with the real qwen3_32b
vote-ballot renderer, capturing both the threaded ``reporter_id`` and the
rendered prompt.
"""

from __future__ import annotations

import asyncio
from functools import partial

import pytest

from agents.strategic.prompts.loader import build_environment, vote_ballot_prompt
from llm.fake_provider import FakeProvider
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    derive_belief_evidence,
)
from meetings.render_contract import SuspicionEntry
from meetings.schemas import MeetingTranscript, PlayerId

_ENV_LEVER = "AILIBI_REPORTER_EXCULPATION"
_ANNOTATION_HEADER = "## Who reported the body"
_REPORTER = "p-1"
_BODY_REPORT = MeetingTrigger(
    triggered_by=_REPORTER,
    trigger_tick=5,
    description="p-1 reported p-2's body in MedBay at tick 5",
)
_EMERGENCY = MeetingTrigger(
    triggered_by=_REPORTER,
    trigger_tick=5,
    description="p-1 called an emergency meeting",
)


def _unused_prompt(*args: object, **kwargs: object) -> str:
    raise AssertionError("only the ballot path should render")


def _run_ballot(
    monkeypatch: pytest.MonkeyPatch,
    *,
    trigger: MeetingTrigger,
    lever_on: bool,
    voter: str = "p-3",
) -> tuple[list[PlayerId | None], str]:
    """Drive ``_collect_one_ballot`` and capture (threaded reporter_ids, prompt).

    The capturing renderer records the ``reporter_id`` the manager threads and
    delegates to the real qwen3_32b vote-ballot template, so the returned prompt
    is the exact bytes a recording would log.
    """

    if lever_on:
        monkeypatch.setenv(_ENV_LEVER, "1")
    else:
        monkeypatch.delenv(_ENV_LEVER, raising=False)

    env = build_environment("qwen3_32b")
    real_vote = partial(vote_ballot_prompt, environment=env)
    captured_reporter_ids: list[PlayerId | None] = []
    captured_prompt = ""

    def capture(*, reporter_id: PlayerId | None = None, **kwargs: object) -> str:
        nonlocal captured_prompt
        captured_reporter_ids.append(reporter_id)
        captured_prompt = real_vote(reporter_id=reporter_id, **kwargs)  # type: ignore[arg-type]
        return captured_prompt

    manager = MeetingManager(
        llm_client=FakeProvider(),
        crewmate_report_prompt=_unused_prompt,
        impostor_report_prompt=_unused_prompt,
        statement_prompt=_unused_prompt,
        vote_prompt=capture,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
    )
    participants = [
        MeetingParticipant(
            agent_id=pid,
            role="CREWMATE",
            rendered_memory="(memory)",
            suspicion_graph=(
                SuspicionEntry(player_id=_REPORTER, suspicion=0.5, trust=0.5),
            ),
        )
        for pid in ("p-1", "p-3", "p-4")
    ]
    voter_participant = next(p for p in participants if p.agent_id == voter)
    transcript = MeetingTranscript(turns=())
    evidence = derive_belief_evidence(
        transcript,
        contradictions=(),
        roster=frozenset(p.agent_id for p in participants),
    )
    asyncio.run(
        manager._collect_one_ballot(  # noqa: PLC2701
            trigger=trigger,
            participant=voter_participant,
            participants=participants,
            transcript=transcript,
            contradictions=(),
            evidence=evidence,
        )
    )
    return captured_reporter_ids, captured_prompt


class TestReporterAnnotationThreading:
    def test_lever_on_body_report_names_the_trigger_reporter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        reporter_ids, prompt = _run_ballot(
            monkeypatch, trigger=_BODY_REPORT, lever_on=True
        )
        # The threaded id is the trigger's reporter, NOT re-derived from the
        # (empty) transcript.
        assert reporter_ids == [_REPORTER]
        assert _ANNOTATION_HEADER in prompt
        assert f"`{_REPORTER}` reported the body" in prompt
        assert "self-report is weakly exculpatory" in prompt

    def test_lever_off_threads_none_and_omits_the_annotation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        reporter_ids, prompt = _run_ballot(
            monkeypatch, trigger=_BODY_REPORT, lever_on=False
        )
        assert reporter_ids == [None]
        assert _ANNOTATION_HEADER not in prompt

    def test_lever_on_off_prompts_differ_only_by_the_annotation(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # OFF must be byte-identical to the prompt the lever never touched.
        _, off_prompt = _run_ballot(monkeypatch, trigger=_BODY_REPORT, lever_on=False)
        _, on_prompt = _run_ballot(monkeypatch, trigger=_BODY_REPORT, lever_on=True)
        assert off_prompt != on_prompt
        # Rendering the same inputs with reporter_id=None reproduces the OFF
        # bytes exactly (the widen-the-contract-inert guarantee).
        env = build_environment("qwen3_32b")
        reference = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory="(memory)",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id=_REPORTER, suspicion=0.5, trust=0.5),
            ),
            candidate_targets=("p-1", "p-4"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            reporter_id=None,
            environment=env,
        )
        assert off_prompt == reference

    def test_lever_on_emergency_meeting_never_annotates(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # An emergency call has no body-reporter; the exculpation must not assert
        # a false "reporter at body" prior even with the lever ON.
        reporter_ids, prompt = _run_ballot(
            monkeypatch, trigger=_EMERGENCY, lever_on=True
        )
        assert reporter_ids == [None]
        assert _ANNOTATION_HEADER not in prompt

    def test_lever_on_annotates_even_when_the_voter_is_the_reporter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The base-rate line is surfaced uniformly; a reporter voting on the
        # meeting they opened still sees it (names themselves).
        reporter_ids, prompt = _run_ballot(
            monkeypatch, trigger=_BODY_REPORT, lever_on=True, voter=_REPORTER
        )
        assert reporter_ids == [_REPORTER]
        assert _ANNOTATION_HEADER in prompt


class TestReporterAnnotationTemplateBytes:
    """Template-level byte-identity of the OFF path, independent of the manager."""

    def _render(self, reporter_id: PlayerId | None) -> str:
        env = build_environment("qwen3_32b")
        return vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory="mem",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.5, trust=0.5),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            reporter_id=reporter_id,
            environment=env,
        )

    def test_none_and_omitted_render_identically(self) -> None:
        env = build_environment("qwen3_32b")
        omitted = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory="mem",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.5, trust=0.5),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            environment=env,
        )
        assert self._render(None) == omitted
        assert _ANNOTATION_HEADER not in omitted

    def test_supplied_reporter_adds_the_annotation_without_dropping_content(
        self,
    ) -> None:
        on = self._render("p-1")
        off = self._render(None)
        assert _ANNOTATION_HEADER in on
        assert "`p-1` reported the body" in on
        # The annotation is purely additive: every non-annotation section the OFF
        # render carries (the decision + output sections) is still present in ON.
        assert "## How to decide" in on
        assert "## Output" in on
        assert len(on) > len(off)
