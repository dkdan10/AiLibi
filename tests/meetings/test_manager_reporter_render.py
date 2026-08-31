"""Reporter-exculpation vote-surface render threading (Task 15.5; graduated to
unconditional at Task 15.7).

The render half of the ``reporter_exculpation`` lever
(tasks/post-phase-14-clean-up.md H5): the manager threads the body-report
meeting's reporter (``MeetingTrigger.triggered_by`` -- the meeting-scope
identity, never re-derived from the transcript) into the vote-ballot renderer's
DEFAULTED ``reporter_id`` input for a body report, and the v6 ``vote_ballot``
template renders the self-report base-rate annotation only when it is supplied.
The lever graduated to unconditional-ON at the Task-15.7 baseline-3 record, so a
body-report ballot ALWAYS carries the annotation and it is env-independent; an
emergency call (no body-reporter) threads ``None`` and omits it. The
``reporter_id=None`` template path (an emergency ballot, or any tooling caller)
stays byte-identical to the un-annotated render -- the widen-the-contract-inert
guarantee, pinned by ``TestReporterAnnotationTemplateBytes`` below.

These tests drive the real ``_collect_one_ballot`` seam with the real qwen3_32b
vote-ballot renderer, capturing both the threaded ``reporter_id`` and the
rendered prompt.

The SPEECH half -- the default-OFF ``reporter_reasoning`` lever -- lives here too,
because it is the same finding on a second surface: the base rate the ballot has
carried since 15.5 reaches the turn prompts, the reporter's own opening is asked
for the discovery account, and a speaker whose own record places them at the body
is told so. Those cases drive the real ``_render_turn_prompt`` seam with the real
``qwen3_6_27b`` turn templates (the served set, the only one that renders the
blocks), and the base-rate sentence is asserted against the BALLOT render rather
than a re-typed literal, so the two surfaces cannot drift apart silently.
"""

from __future__ import annotations

import asyncio
from functools import partial

import pytest

from agents.memory.episodic import EpisodicEvent
from agents.perception import EVENT_OWN_KILL, PROVENANCE_OBSERVED, ingest_packet
from agents.strategic.prompts.loader import (
    build_environment,
    build_prompt_renderers,
    vote_ballot_prompt,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.world import load_canonical_map
from llm.fake_provider import FakeProvider
from meetings.manager import (
    EMERGENCY_TRIGGER_PHRASE,
    ENV_REPORTER_REASONING,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    Role,
    derive_belief_evidence,
    reporter_reasoning_enabled,
)
from meetings.render_contract import BodyDiscoveryRecord, SuspicionEntry
from meetings.schemas import MeetingTranscript, PlayerId
from observation.packet import BodyView, GlobalView, ObservationPacket, SelfView
from orchestrator.game import (
    TacticalAgent,
    _build_participants,  # noqa: PLC2701
)
from orchestrator.seeder import seed_initial_state

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
    *,
    trigger: MeetingTrigger,
    voter: str = "p-3",
) -> tuple[list[PlayerId | None], str]:
    """Drive ``_collect_one_ballot`` and capture (threaded reporter_ids, prompt).

    The capturing renderer records the ``reporter_id`` the manager threads and
    delegates to the real qwen3_32b vote-ballot template, so the returned prompt
    is the exact bytes a recording would log. The reporter_exculpation lever is
    unconditional (Task 15.7), so the helper sets no env -- a body report always
    threads the reporter and renders the annotation.
    """

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
    def test_body_report_names_the_trigger_reporter(self) -> None:
        reporter_ids, prompt = _run_ballot(trigger=_BODY_REPORT)
        # The threaded id is the trigger's reporter, NOT re-derived from the
        # (empty) transcript.
        assert reporter_ids == [_REPORTER]
        assert _ANNOTATION_HEADER in prompt
        assert f"`{_REPORTER}` reported the body" in prompt
        assert "self-report is weakly exculpatory" in prompt

    def test_body_report_annotation_is_env_independent(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Graduated to unconditional at Task 15.7: the annotation renders on a
        # body report whatever AILIBI_REPORTER_EXCULPATION says (unset, "0", or
        # "1") -- no env flips it off.
        for value in (None, "0", "1"):
            if value is None:
                monkeypatch.delenv(_ENV_LEVER, raising=False)
            else:
                monkeypatch.setenv(_ENV_LEVER, value)
            reporter_ids, prompt = _run_ballot(trigger=_BODY_REPORT)
            assert reporter_ids == [_REPORTER]
            assert _ANNOTATION_HEADER in prompt

    def test_body_report_prompt_is_the_reporter_supplied_render(self) -> None:
        # The manager threads exactly reporter_id=_REPORTER; the resulting prompt
        # equals the reporter-supplied template render and differs from the
        # reporter_id=None render by exactly the additive annotation.
        _, body_prompt = _run_ballot(trigger=_BODY_REPORT)
        env = build_environment("qwen3_32b")
        annotated = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory="(memory)",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            # The graduated (Task 18.12) roll-call round + unconditional absence
            # prior shift the manager-threaded graph: the absent `p-4` gains a
            # +0.08 testimony-spread lift to suspicion 0.58 (from a 0.5 base),
            # so the pinned expected graph carries that second entry.
            suspicion_graph=(
                SuspicionEntry(player_id=_REPORTER, suspicion=0.5, trust=0.5),
                SuspicionEntry(player_id="p-4", suspicion=0.58, trust=0.5),
            ),
            candidate_targets=("p-1", "p-4"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            reporter_id=_REPORTER,
            environment=env,
        )
        none_render = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory="(memory)",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            # Same graduated (Task 18.12) absence-prior graph as the annotated
            # render above -- the two differ only by the additive reporter block.
            suspicion_graph=(
                SuspicionEntry(player_id=_REPORTER, suspicion=0.5, trust=0.5),
                SuspicionEntry(player_id="p-4", suspicion=0.58, trust=0.5),
            ),
            candidate_targets=("p-1", "p-4"),
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=(),
            reporter_id=None,
            environment=env,
        )
        assert body_prompt == annotated
        assert body_prompt != none_render
        assert _ANNOTATION_HEADER not in none_render

    def test_emergency_meeting_never_annotates(self) -> None:
        # An emergency call has no body-reporter; the exculpation must not assert
        # a false "reporter at body" prior even under the unconditional lever.
        reporter_ids, prompt = _run_ballot(trigger=_EMERGENCY)
        assert reporter_ids == [None]
        assert _ANNOTATION_HEADER not in prompt

    def test_annotates_even_when_the_voter_is_the_reporter(self) -> None:
        # The base-rate line is surfaced uniformly; a reporter voting on the
        # meeting they opened still sees it (names themselves).
        reporter_ids, prompt = _run_ballot(trigger=_BODY_REPORT, voter=_REPORTER)
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


# --------------------------------------------------------------------------- #
# The SPEECH half: the default-OFF reporter_reasoning lever                    #
# --------------------------------------------------------------------------- #

_SERVED_SET = "qwen3_6_27b"
_LEVER_ON = {ENV_REPORTER_REASONING: "1"}
_CO_DISCOVERY_LINE = "Your own record places you at the body when it was reported."
_DISCOVERY_ACCOUNT_OPENER = "You reported the body that opened this meeting"
# The distinctive words of the BALLOT's exculpatory framing. Rule (c)'s line must
# carry none of them: half the players holding a co-discovery row at the report
# tick are impostors, so exculpatory wording there would defend one.
_EXCULPATORY_WORDS = ("exculpatory", "evidence of guilt", "merely for having")


def _who_reported_block(prompt: str) -> str:
    """The rendered reporter block, or "" when the prompt carries none."""

    if "<who_reported>" not in prompt:
        return ""
    return prompt.split("<who_reported>", 1)[1].split("</who_reported>", 1)[0].strip()


def _paragraph_sentences(text: str, *, opener: str) -> list[str]:
    """Sentences of the line that starts with ``opener``, in order.

    Lets the accusation-round block be compared against the BALLOT RENDER rather
    than a re-typed string, so an edit to either surface fails loudly instead of
    letting the two drift.
    """

    for line in text.splitlines():
        if line.startswith(opener):
            return [part.strip() + "." for part in line.rstrip(".").split(". ")]
    raise AssertionError(f"no paragraph starting {opener!r} in:\n{text}")


def _ballot_base_rate_sentences() -> list[str]:
    """The served ballot's own reporter paragraph, split into sentences."""

    prompt = vote_ballot_prompt(
        voter_id="p-3",
        rendered_memory="mem",
        transcript=MeetingTranscript(turns=()),
        contradiction_flags=(),
        suspicion_graph=(SuspicionEntry(player_id="p-2", suspicion=0.5, trust=0.5),),
        candidate_targets=("p-1", "p-2"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=(),
        reporter_id=_REPORTER,
        environment=build_environment(_SERVED_SET),
    )
    return _paragraph_sentences(prompt, opener=f"`{_REPORTER}` reported the body")


def _turn_prompts(
    *,
    trigger: MeetingTrigger,
    env: dict[str, str],
    discoveries: dict[PlayerId, tuple[BodyDiscoveryRecord, ...]] | None = None,
    roles: dict[PlayerId, Role] | None = None,
) -> dict[tuple[PlayerId, str], str]:
    """Every participant's opening AND reply prompt, keyed by (speaker, kind).

    Drives the real ``_render_turn_prompt`` with the real served-set renderers,
    so each string is the exact bytes a recording would log. The lever is read
    through the explicit ``env`` mapping, never ``os.environ``.
    """

    renderers = build_prompt_renderers(_SERVED_SET)
    manager = MeetingManager(
        llm_client=FakeProvider(),
        crewmate_report_prompt=renderers.crewmate_report,
        impostor_report_prompt=renderers.impostor_report,
        statement_prompt=renderers.statement,
        vote_prompt=renderers.vote,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
    )
    ids: tuple[PlayerId, ...] = ("p-1", "p-3", "p-4")
    participants = [
        MeetingParticipant(
            agent_id=pid,
            role=(roles or {}).get(pid, "CREWMATE"),
            rendered_memory="(memory)",
            body_discovery_records=(discoveries or {}).get(pid, ()),
        )
        for pid in ids
    ]
    is_body_report = EMERGENCY_TRIGGER_PHRASE not in trigger.description
    reporter_id = (
        trigger.triggered_by
        if reporter_reasoning_enabled(env) and is_body_report
        else None
    )
    out: dict[tuple[PlayerId, str], str] = {}
    for participant in participants:
        for turn_kind in ("opening", "reply"):
            out[(participant.agent_id, turn_kind)] = manager._render_turn_prompt(  # noqa: PLC2701
                participant=participant,
                turn_kind=turn_kind,
                trigger=trigger,
                transcript_so_far=MeetingTranscript(turns=()),
                contradictions=(),
                prior_turn=None,
                living_ids=frozenset(ids),
                render_reporter_id=reporter_id,
            )
    return out


class TestReporterReasoningResolver:
    def test_default_off_and_reads_its_env_var(self) -> None:
        for value in ("", "0", "no", "nope", " "):
            assert (
                reporter_reasoning_enabled({ENV_REPORTER_REASONING: value}) is False
            ), value
        assert reporter_reasoning_enabled({}) is False
        for value in ("1", "true", "TRUE", "yes", "on", " On "):
            assert (
                reporter_reasoning_enabled({ENV_REPORTER_REASONING: value}) is True
            ), value

    def test_an_explicit_mapping_wins_over_the_process_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(ENV_REPORTER_REASONING, "1")
        # What lets every case below toggle the lever without mutating os.environ.
        assert reporter_reasoning_enabled({}) is False
        assert reporter_reasoning_enabled() is True


class TestReporterReasoningOffPath:
    def test_lever_off_renders_the_pre_lever_bytes(self) -> None:
        off = _turn_prompts(trigger=_BODY_REPORT, env={})
        for key, prompt in off.items():
            assert "<who_reported>" not in prompt, key
            assert _DISCOVERY_ACCOUNT_OPENER not in prompt, key
            assert _CO_DISCOVERY_LINE not in prompt, key
        # The perturbation half: the same seam DOES move with the lever ON, so
        # the OFF assertion above states something about the lever rather than
        # about a render that never carried the block under any setting.
        on = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)
        assert on[("p-3", "reply")] != off[("p-3", "reply")]
        assert on[("p-1", "opening")] != off[("p-1", "opening")]

    def test_a_caller_threading_no_reporter_context_gets_todays_prompt(self) -> None:
        # Inert twice over: a direct-construction caller that threads nothing
        # renders exactly the bytes a caller that omits the kwargs renders.
        renderers = build_prompt_renderers(_SERVED_SET)
        threaded = renderers.statement(
            agent_id="p-3",
            rendered_memory="(memory)",
            transcript=MeetingTranscript(turns=()),
            contradictions=(),
            prior_turn=None,
            turn_kind="reply",
            reporter_context=None,
            at_body=False,
        )
        omitted = renderers.statement(
            agent_id="p-3",
            rendered_memory="(memory)",
            transcript=MeetingTranscript(turns=()),
            contradictions=(),
            prior_turn=None,
            turn_kind="reply",
        )
        assert threaded == omitted


class TestReporterReasoningListenerBlock:
    """Rule (a): the exculpation reaches the accusation round."""

    def test_every_non_reporter_turn_names_the_reporter(self) -> None:
        prompts = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)
        for speaker in ("p-3", "p-4"):
            block = _who_reported_block(prompts[(speaker, "reply")])
            assert f"`{_REPORTER}` reported the body" in block, speaker

    def test_the_base_rate_sentence_is_byte_identical_to_the_ballots(self) -> None:
        prompts = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)
        spoken = _paragraph_sentences(
            _who_reported_block(prompts[("p-3", "reply")]),
            opener=f"`{_REPORTER}` reported the body",
        )
        ballot = _ballot_base_rate_sentences()
        # Who reported, and the base rate: the ballot's own bytes, compared
        # against the BALLOT RENDER rather than a re-typed literal.
        assert spoken[:2] == ballot[:2]
        assert "weakly exculpatory" in ballot[1]

    def test_the_block_lands_before_the_transcript(self) -> None:
        # Placement is load-bearing: the prior has to be in front of the reader
        # before they form a target, not after the meeting so far.
        prompt = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)[("p-3", "reply")]
        assert prompt.index("<who_reported>") < prompt.index("<transcript>")
        # And it carries no markdown header, so the recorded-call slot
        # classifier still reads the turn header first.
        assert prompt.index("## Your turn") < prompt.index("<who_reported>")
        assert "##" not in _who_reported_block(prompt)

    def test_the_reporter_is_not_addressed_with_their_own_defence(self) -> None:
        prompts = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)
        assert _who_reported_block(prompts[(_REPORTER, "opening")]) == ""
        assert _who_reported_block(prompts[(_REPORTER, "reply")]) == ""

    def test_an_emergency_meeting_arms_nothing(self) -> None:
        prompts = _turn_prompts(trigger=_EMERGENCY, env=_LEVER_ON)
        for key, prompt in prompts.items():
            assert _who_reported_block(prompt) == "", key
            assert _DISCOVERY_ACCOUNT_OPENER not in prompt, key
            assert _CO_DISCOVERY_LINE not in prompt, key


class TestReporterReasoningDiscoveryAccount:
    """Rule (b): the discovery account becomes speakable."""

    _ROWS: dict[PlayerId, tuple[BodyDiscoveryRecord, ...]] = {
        _REPORTER: (BodyDiscoveryRecord(victim_id="p-2", room="MEDBAY", tick=5),)
    }

    def test_the_reporters_opening_gains_the_account_line(self) -> None:
        prompts = _turn_prompts(
            trigger=_BODY_REPORT, env=_LEVER_ON, discoveries=self._ROWS
        )
        opening = prompts[(_REPORTER, "opening")]
        assert _DISCOVERY_ACCOUNT_OPENER in opening
        # The reader's OWN row is what makes the line concrete.
        assert "p-2's, in MEDBAY" in opening

    def test_a_reporter_holding_no_row_still_gets_the_generic_ask(self) -> None:
        opening = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON)[
            (_REPORTER, "opening")
        ]
        line = next(
            row
            for row in opening.splitlines()
            if row.startswith(_DISCOVERY_ACCOUNT_OPENER)
        )
        # No row to read back, so no concrete clause is invented for it.
        assert "MEDBAY" not in line
        assert "p-2" not in line

    def test_the_perturbation_a_non_reporter_gets_no_account_line(self) -> None:
        # Same participant, same rows, but someone else opened the meeting: the
        # line must move with the reporter, not with the discovery row.
        other = MeetingTrigger(
            triggered_by="p-4",
            trigger_tick=5,
            description="p-4 reported p-2's body in MedBay at tick 5",
        )
        prompts = _turn_prompts(trigger=other, env=_LEVER_ON, discoveries=self._ROWS)
        assert _DISCOVERY_ACCOUNT_OPENER not in prompts[(_REPORTER, "opening")]
        assert _DISCOVERY_ACCOUNT_OPENER in prompts[("p-4", "opening")]

    def test_an_emergency_opening_never_asks_for_a_discovery_account(self) -> None:
        prompts = _turn_prompts(
            trigger=_EMERGENCY, env=_LEVER_ON, discoveries=self._ROWS
        )
        assert _DISCOVERY_ACCOUNT_OPENER not in prompts[(_REPORTER, "opening")]


class TestReporterReasoningCoDiscovery:
    """Rule (c): neutral, self-addressed, and never a roster."""

    _ROWS: dict[PlayerId, tuple[BodyDiscoveryRecord, ...]] = {
        "p-3": (BodyDiscoveryRecord(victim_id="p-2", room="MEDBAY", tick=5),),
        "p-4": (BodyDiscoveryRecord(victim_id="p-2", room="MEDBAY", tick=4),),
    }

    def test_a_co_discoverers_own_turn_carries_the_neutral_line(self) -> None:
        prompts = _turn_prompts(
            trigger=_BODY_REPORT, env=_LEVER_ON, discoveries=self._ROWS
        )
        assert _CO_DISCOVERY_LINE in _who_reported_block(prompts[("p-3", "reply")])
        # Tick - 1 is inside the window: perception stamps the row on the
        # packet's tick, one early for a player who saw it on the approach.
        assert _CO_DISCOVERY_LINE in _who_reported_block(prompts[("p-4", "reply")])

    def test_an_impostor_co_discoverer_gets_the_same_neutral_line(self) -> None:
        # The over-damping canary. Exculpatory framing on this surface would
        # print a defence of an impostor in over half the meetings it fires in,
        # so the reader's own line carries NONE of the ballot's framing words --
        # and an impostor's block is byte-identical to a crewmate's.
        crew = _turn_prompts(
            trigger=_BODY_REPORT, env=_LEVER_ON, discoveries=self._ROWS
        )
        impostor = _turn_prompts(
            trigger=_BODY_REPORT,
            env=_LEVER_ON,
            discoveries=self._ROWS,
            roles={"p-3": "IMPOSTOR"},
        )
        crew_block = _who_reported_block(crew[("p-3", "reply")])
        impostor_block = _who_reported_block(impostor[("p-3", "reply")])
        assert impostor_block == crew_block
        own_line = impostor_block.splitlines()[-1]
        assert own_line == _CO_DISCOVERY_LINE
        for word in _EXCULPATORY_WORDS:
            assert word not in own_line, word

    def test_the_absence_check_bites_on_planted_exculpatory_wording(self) -> None:
        # The perturbation for the assertion above: a line that DID carry the
        # ballot's framing must be caught by the same words.
        planted = (
            "Your own record places you at the body; being first to the scene is "
            "not by itself evidence of guilt."
        )
        assert [word for word in _EXCULPATORY_WORDS if word in planted]

    def test_no_prompt_names_another_player_as_a_co_discoverer(self) -> None:
        prompts = _turn_prompts(
            trigger=_BODY_REPORT, env=_LEVER_ON, discoveries=self._ROWS
        )
        for (speaker, turn_kind), prompt in prompts.items():
            block = _who_reported_block(prompt)
            if _CO_DISCOVERY_LINE not in block:
                continue
            for other in {"p-1", "p-3", "p-4"} - {speaker, _REPORTER}:
                # The reporter is named by rule (a), by design; nobody else is.
                assert other not in block, (speaker, turn_kind, other)

    def test_a_participant_holding_no_row_gets_no_line(self) -> None:
        prompts = _turn_prompts(
            trigger=_BODY_REPORT,
            env=_LEVER_ON,
            discoveries={"p-3": self._ROWS["p-3"]},
        )
        assert _CO_DISCOVERY_LINE in _who_reported_block(prompts[("p-3", "reply")])
        assert _CO_DISCOVERY_LINE not in _who_reported_block(prompts[("p-4", "reply")])

    def test_a_row_outside_the_window_is_not_a_co_discovery(self) -> None:
        stale: dict[PlayerId, tuple[BodyDiscoveryRecord, ...]] = {
            "p-3": (BodyDiscoveryRecord(victim_id="p-9", room="ADMIN", tick=1),)
        }
        prompts = _turn_prompts(trigger=_BODY_REPORT, env=_LEVER_ON, discoveries=stale)
        assert _CO_DISCOVERY_LINE not in _who_reported_block(prompts[("p-3", "reply")])


class TestReporterReasoningRegister:
    """Craft rule 4: no internal dialect on a rendered surface."""

    _FORBIDDEN = (
        "task ",
        "audits/",
        "\u00a7",
        "lever",
        "flag",
        "engine",
        "gate",
        "threshold",
        "0.",
    )

    def _rendered_blocks(self) -> list[str]:
        prompts = _turn_prompts(
            trigger=_BODY_REPORT,
            env=_LEVER_ON,
            discoveries={
                _REPORTER: (
                    BodyDiscoveryRecord(victim_id="p-2", room="MEDBAY", tick=5),
                ),
                "p-3": (BodyDiscoveryRecord(victim_id="p-2", room="MEDBAY", tick=5),),
            },
        )
        blocks: list[str] = []
        for prompt in prompts.values():
            block = _who_reported_block(prompt)
            if block:
                blocks.append(block)
            for line in prompt.splitlines():
                if line.startswith(_DISCOVERY_ACCOUNT_OPENER):
                    blocks.append(line)
        assert blocks, "no lever-rendered block to inspect"
        return blocks

    def test_the_rendered_blocks_carry_no_internal_dialect(self) -> None:
        for block in self._rendered_blocks():
            lowered = block.lower()
            for term in self._FORBIDDEN:
                assert term not in lowered, (term, block)

    def test_the_dialect_sweep_bites_on_a_planted_violation(self) -> None:
        planted = "Per task 21.18 (audits/review-2026-08-26) the 0.46 gate lifts."
        lowered = planted.lower()
        assert [term for term in self._FORBIDDEN if term in lowered]


# --------------------------------------------------------------------------- #
# The self-channel behind rule (c)                                            #
# --------------------------------------------------------------------------- #


def _body_packet(
    *,
    agent_id: str,
    tick: int,
    bodies: tuple[BodyView, ...],
    self_room: str = "MEDBAY",
) -> ObservationPacket:
    """A packet whose ``visible_bodies`` seeds first-hand discovery rows."""

    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(room=self_room, role="CREWMATE", pending_task_id=None),
        visible_players=(),
        visible_bodies=bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


class TestBodyDiscoveryRecordsAccessor:
    """``TacticalAgent.body_discovery_records_for_meeting`` -- self-channel only.

    The rows the reporter-voice lever reads to decide whether a speaker's OWN
    record places them at the body. A straight episodic filter over the agent's
    own ``saw_body`` rows, deduped on first sighting exactly as the §6.6 render
    dedupes its "You discovered ..." line, and never another player's memory.
    """

    def _crew_agent(self, agent_id: str = "p-2") -> TacticalAgent:
        return TacticalAgent(
            agent_id=agent_id,
            role="CREWMATE",
            policy=CrewmatePolicy(agent_id=agent_id),
        )

    def test_reports_only_rows_the_agent_itself_holds(self) -> None:
        seer = self._crew_agent("p-2")
        blind = self._crew_agent("p-5")
        ingest_packet(
            packet=_body_packet(
                agent_id="p-2",
                tick=7,
                bodies=(BodyView(id="body-p-9-6", room="MEDBAY", victim_id="p-9"),),
            ),
            memory=seer.memory.episodic,
        )
        # The co-present player who never perceived the body: perception ran for
        # them, the self_state row landed, and no discovery row did.
        ingest_packet(
            packet=_body_packet(agent_id="p-5", tick=7, bodies=()),
            memory=blind.memory.episodic,
        )
        assert seer.body_discovery_records_for_meeting() == (
            BodyDiscoveryRecord(
                victim_id="p-9", room="MEDBAY", tick=7, observation_id="p-2:7:1"
            ),
        )
        assert blind.body_discovery_records_for_meeting() == ()

    def test_a_second_sighting_of_the_same_body_adds_nothing(self) -> None:
        # The §6.6 render surfaces a discovery ONCE, on the body's first
        # sighting; a channel that re-minted it would tell a speaker they were
        # at the body every tick they walked past the corpse.
        agent = self._crew_agent()
        body = BodyView(id="body-p-9-6", room="MEDBAY", victim_id="p-9")
        for tick in (7, 8, 9):
            ingest_packet(
                packet=_body_packet(agent_id="p-2", tick=tick, bodies=(body,)),
                memory=agent.memory.episodic,
            )
        records = agent.body_discovery_records_for_meeting()
        assert [record.tick for record in records] == [7]

    def test_a_killers_own_victim_is_not_a_discovery(self) -> None:
        # DESIGN.md §6.2: the kill is narrated as a kill, and the render
        # suppresses the discovery line for it. Telling a killer their record
        # places them at the body they made would put its own kill back in front
        # of it under a discovery framing.
        killer = TacticalAgent(
            agent_id="p-2", role="IMPOSTOR", policy=ImpostorPolicy(agent_id="p-2")
        )
        killer.memory.episodic.append(
            EpisodicEvent(
                tick=6,
                type=EVENT_OWN_KILL,
                payload={"victim_id": "p-9", "room": "MEDBAY"},
                provenance=PROVENANCE_OBSERVED,
            )
        )
        ingest_packet(
            packet=_body_packet(
                agent_id="p-2",
                tick=7,
                bodies=(
                    BodyView(id="body-p-9-6", room="MEDBAY", victim_id="p-9"),
                    BodyView(id="body-p-8-6", room="MEDBAY", victim_id="p-8"),
                ),
            ),
            memory=killer.memory.episodic,
        )
        victims = [
            record.victim_id for record in killer.body_discovery_records_for_meeting()
        ]
        # The other corpse still records: the suppression is per-victim, not a
        # blanket silence for impostors.
        assert victims == ["p-8"]

    def test_a_fresh_agent_discovered_nothing(self) -> None:
        assert self._crew_agent().body_discovery_records_for_meeting() == ()

    def test_build_participants_threads_it_onto_the_right_seat(self) -> None:
        state = seed_initial_state(seed=7, game_map=load_canonical_map(), num_players=4)
        agents = {
            player_id: TacticalAgent(
                agent_id=player_id,
                role=player.role,
                policy=CrewmatePolicy(agent_id=player_id),
            )
            for player_id, player in state.players.items()
        }
        for player_id, agent in agents.items():
            ingest_packet(
                packet=_body_packet(
                    agent_id=player_id,
                    tick=7,
                    bodies=(
                        (BodyView(id="body-p-9-6", room="MEDBAY", victim_id="p-9"),)
                        if player_id == "p-3"
                        else ()
                    ),
                ),
                memory=agent.memory.episodic,
                beliefs=agent.memory.beliefs,
            )
        participants = _build_participants(
            state=state, agents=agents, token_budget=2048
        )
        by_id = {p.agent_id: p for p in participants}
        assert [r.victim_id for r in by_id["p-3"].body_discovery_records] == ["p-9"]
        for player_id, participant in by_id.items():
            if player_id != "p-3":
                assert participant.body_discovery_records == (), player_id
