"""Tests for ``meetings/manager.py::derive_reported_testimony`` (Task 13.5.2).

The content twin of ``extract_belief_evidence`` (pinned in
``tests/meetings/test_manager.py``): where that reduction collapses a meeting
to scalar suspicion subject-sets, this one preserves the WHAT of public speech
as ``ReportedStatement`` rows (the 2026-06-25 memory diagnosis, workflow
``wg54kfoxy``: "social info is a scalar, not content"). These tests pin the
derivation contract: a pure, replay-deterministic function of the recorded
``MeetingResult`` -- free-text excluded, roster-only, structured kinds only.
"""

from __future__ import annotations

from meetings.manager import derive_reported_testimony
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    ReportedStatement,
    SawPlayerObservation,
    VoteBallot,
)

_ROSTER = ("p-1", "p-2", "p-3", "p-4", "p-5")


def _result_with(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    voters: tuple[str, ...] = _ROSTER,
) -> MeetingResult:
    return MeetingResult(
        meeting_id="m-1",
        triggered_by="p-1",
        trigger_tick=400,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            )
            for voter in voters
        ),
        transcript=MeetingTranscript(turns=turns),
    )


def _turn(
    *,
    turn_index: int,
    speaker: str,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
    free_text: str = "narration",
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "reply",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=free_text,
    )


class TestDeriveReportedTestimony:
    def test_collects_all_four_structured_kinds(self) -> None:
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    observations=(
                        SawPlayerObservation(
                            type="saw_player", tick=12, subject="p-5", room="ELECTRICAL"
                        ),
                    ),
                    claims=(
                        AlibiClaim(
                            type="alibi",
                            subject="p-2",
                            from_tick=10,
                            to_tick=14,
                            room="MEDBAY",
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-3",
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-5",
                            confidence=0.7,
                            reason="suspicious",
                        ),
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-2",
                            on_tick=11,
                            reason="vouch",
                        ),
                    ),
                ),
            )
        )

        statements = derive_reported_testimony(result)

        assert statements == (
            ReportedStatement(
                speaker="p-1",
                kind="alibi",
                subject="p-2",
                from_tick=10,
                to_tick=14,
                room="MEDBAY",
            ),
            ReportedStatement(
                speaker="p-1",
                kind="saw_player",
                subject="p-5",
                from_tick=12,
                to_tick=12,
                room="ELECTRICAL",
            ),
            ReportedStatement(
                speaker="p-3",
                kind="accusation",
                subject="p-5",
            ),
            ReportedStatement(
                speaker="p-3",
                kind="corroboration",
                subject="p-2",
                from_tick=11,
                to_tick=11,
            ),
        )

    def test_is_pure_and_deterministic_across_repeats(self) -> None:
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    observations=(
                        SawPlayerObservation(
                            type="saw_player", tick=5, subject="p-2", room="CAFETERIA"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-2",
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-1",
                            confidence=0.9,
                            reason="x",
                        ),
                    ),
                ),
            )
        )

        first = derive_reported_testimony(result)
        second = derive_reported_testimony(result)

        assert first == second
        # Sorted output is independent of transcript turn order: the sort key is
        # total over concrete fields.
        assert [s.speaker for s in first] == ["p-1", "p-2"]

    def test_free_text_is_excluded(self) -> None:
        # A turn that carries ONLY free-text (no structured claim/observation)
        # produces no statement -- free-text never becomes content.
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    free_text="I think p-5 is the impostor, I saw them vent",
                ),
            )
        )

        assert derive_reported_testimony(result) == ()

    def test_non_structured_observations_are_dropped(self) -> None:
        # completed_task / found_body are out of scope (owner decision): only
        # the four structured kinds carry as content.
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    observations=(
                        CompletedTaskObservation(
                            type="completed_task",
                            tick=3,
                            task_id="t-1",
                            room="STORAGE",
                        ),
                        FoundBodyObservation(
                            type="found_body", tick=4, body_of="p-2", room="STORAGE"
                        ),
                    ),
                ),
            )
        )

        assert derive_reported_testimony(result) == ()

    def test_observation_about_dead_subject_is_preserved(self) -> None:
        # Codex P2 (Task 13.5.2): a saw_player about a player DEAD before this
        # meeting (the body victim p-5, absent from the ballots) is real public
        # testimony the prompts explicitly elicit -- derive must NOT drop it on the
        # living-voter roster. Subject validity for observations is enforced
        # per-agent at INGEST against the agent's known roster (which covers
        # dead-but-seen players via co-spawn); see the ingest suite's
        # test_roster_only_drops_unknown_ids for the garbage backstop.
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    observations=(
                        SawPlayerObservation(
                            type="saw_player", tick=7, subject="p-5", room="ELECTRICAL"
                        ),
                        SawPlayerObservation(
                            type="saw_player", tick=8, subject="p-3", room="ELECTRICAL"
                        ),
                    ),
                ),
            ),
            voters=("p-1", "p-2", "p-3"),  # p-5 is dead -- not a voter
        )

        statements = derive_reported_testimony(result)

        # Both sightings survive derive; the dead victim p-5 is preserved (the gate
        # moved to ingest). Sorted by (speaker, kind, subject): p-3 then p-5.
        assert [s.subject for s in statements] == ["p-3", "p-5"]

    def test_speaker_outside_roster_is_dropped(self) -> None:
        # A turn whose speaker is not among the living voters contributes nothing.
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-9",
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-2",
                            confidence=0.5,
                            reason="x",
                        ),
                    ),
                ),
            ),
            voters=("p-1", "p-2", "p-3"),
        )

        assert derive_reported_testimony(result) == ()

    def test_empty_meeting_derives_nothing(self) -> None:
        assert derive_reported_testimony(_result_with()) == ()
