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
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    VoteBallot,
    WhereaboutsClaim,
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


# --------------------------------------------------------------------------- #
# The testimony-shapes lever: three more spoken shapes reach a listener        #
# --------------------------------------------------------------------------- #

_SHAPES_ON: dict[str, str] = {"AILIBI_TESTIMONY_SHAPES": "1"}

_THREE_SHAPE_TURNS: tuple[MeetingTurn, ...] = (
    _turn(
        turn_index=0,
        speaker="p-1",
        observations=(
            WhereaboutsClaim(type="whereabouts", tick=11, room="MEDBAY"),
            SawMoveObservation(
                type="saw_move",
                tick=12,
                subject="p-4",
                from_room="ADMIN",
                to_room="LABS",
            ),
            SawKillObservation(type="saw_kill", tick=13, subject="p-2", room="REACTOR"),
        ),
    ),
)


class TestTestimonyShapesLever:
    """OFF is the pre-lever tuple; ON adds one statement per new shape."""

    def test_off_drops_all_three_new_shapes(self) -> None:
        result = _result_with(turns=_THREE_SHAPE_TURNS)

        # The OFF tuple is produced by exactly the code that produced it before
        # the lever existed: the three shapes fall through both loops, and the
        # meeting reduces to nothing at all.
        assert derive_reported_testimony(result, testimony_shapes=False) == ()
        # Omission is the explicit baseline profile, independent of ambient state.
        assert derive_reported_testimony(result) == ()

    def test_on_emits_one_statement_per_new_shape(self) -> None:
        statements = derive_reported_testimony(
            _result_with(turns=_THREE_SHAPE_TURNS), testimony_shapes=True
        )

        by_kind = {statement.kind: statement for statement in statements}
        assert set(by_kind) == {"whereabouts", "saw_move", "saw_kill"}
        # A whereabouts is a SELF-placement: the shape carries no subject, so the
        # subject is the speaker and the window is the single spoken tick.
        assert by_kind["whereabouts"] == ReportedStatement(
            speaker="p-1",
            kind="whereabouts",
            subject="p-1",
            from_tick=11,
            to_tick=11,
            room="MEDBAY",
        )
        # A witnessed kill names the KILLER and carries no victim.
        assert by_kind["saw_kill"] == ReportedStatement(
            speaker="p-1",
            kind="saw_kill",
            subject="p-2",
            from_tick=13,
            to_tick=13,
            room="REACTOR",
        )

    def test_a_transition_contributes_the_destination_only(self) -> None:
        # The rule the detector applies to the same shape, copied: ONE placement,
        # the arrival. Carrying the origin at ``tick - 1`` would re-open the
        # off-by-one class the shape closes.
        statements = derive_reported_testimony(
            _result_with(turns=_THREE_SHAPE_TURNS), testimony_shapes=True
        )

        moves = [s for s in statements if s.kind == "saw_move"]
        assert moves == [
            ReportedStatement(
                speaker="p-1",
                kind="saw_move",
                subject="p-4",
                from_tick=12,
                to_tick=12,
                room="LABS",
            )
        ]
        assert all(statement.room != "ADMIN" for statement in statements)

    def test_the_lever_only_adds(self) -> None:
        # Every OFF statement survives ON unchanged, so the lever is additive and
        # a listener never LOSES content by turning it on.
        result = _result_with(
            turns=(
                *_THREE_SHAPE_TURNS,
                _turn(
                    turn_index=1,
                    speaker="p-3",
                    observations=(
                        SawPlayerObservation(
                            type="saw_player", tick=9, subject="p-2", room="ADMIN"
                        ),
                    ),
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-2",
                            confidence=0.6,
                            reason="near the body",
                        ),
                    ),
                ),
            )
        )

        off = derive_reported_testimony(result, testimony_shapes=False)
        on = derive_reported_testimony(result, testimony_shapes=True)
        assert set(off) < set(on)
        assert len(on) - len(off) == 3

    def test_the_reduction_stays_deterministic_under_both_states(self) -> None:
        # The module's own promise: the same recorded meeting reduces to the same
        # tuple every time, with the lever as its only other input.
        result = _result_with(turns=_THREE_SHAPE_TURNS)
        for enabled in (False, True):
            first = derive_reported_testimony(result, testimony_shapes=enabled)
            assert first == derive_reported_testimony(result, testimony_shapes=enabled)

    def test_the_sort_key_totally_orders_a_mixed_statement_set(self) -> None:
        # A mixed set of every kind, spoken out of order, still reduces to one
        # deterministic sequence -- and the ORDER is the sort key's, not the
        # transcript's, which is what makes the reduction replay-deterministic
        # whatever order the turns arrived in.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(
                    SawKillObservation(
                        type="saw_kill", tick=13, subject="p-2", room="REACTOR"
                    ),
                    WhereaboutsClaim(type="whereabouts", tick=11, room="MEDBAY"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-1",
                observations=(
                    SawMoveObservation(
                        type="saw_move",
                        tick=12,
                        subject="p-4",
                        from_room="ADMIN",
                        to_room="LABS",
                    ),
                    SawPlayerObservation(
                        type="saw_player", tick=9, subject="p-2", room="ADMIN"
                    ),
                ),
                claims=(
                    CorroborationClaim(
                        type="corroboration", supports="p-2", on_tick=8, reason="ok"
                    ),
                ),
            ),
        )
        statements = derive_reported_testimony(
            _result_with(turns=turns), testimony_shapes=True
        )

        assert [(s.speaker, s.kind) for s in statements] == [
            ("p-1", "corroboration"),
            ("p-1", "saw_move"),
            ("p-1", "saw_player"),
            ("p-3", "saw_kill"),
            ("p-3", "whereabouts"),
        ]
        # Total order: no two statements tie on the whole key.
        keys = [
            (s.speaker, s.kind, s.subject, s.from_tick, s.to_tick, s.room)
            for s in statements
        ]
        assert len(set(keys)) == len(keys)

    def test_a_non_roster_speaker_is_still_dropped_under_the_lever(self) -> None:
        # The lever widens WHAT is carried, never WHO may speak: the roster gate
        # is unchanged.
        result = _result_with(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-9",
                    observations=(
                        WhereaboutsClaim(type="whereabouts", tick=11, room="MEDBAY"),
                    ),
                ),
            ),
            voters=("p-1", "p-2", "p-3"),
        )

        assert derive_reported_testimony(result, testimony_shapes=True) == ()
