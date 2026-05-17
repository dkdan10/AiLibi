"""Tests for :func:`meetings.transcript.detect_contradictions` (Task 3.11).

The contract exercised here mirrors DESIGN.md §5.4 + §6.4:

* The detector flags pairs of events that cannot both be true:
  ``alibi_conflict`` for two alibis that place the same agent in
  different rooms over overlapping ticks, and ``alibi_vs_sighting``
  for an alibi contradicted by a ``saw_player`` observation that
  places the subject elsewhere within the alibi range.
* Flags are *information*, not verdicts -- the detector only reports
  what cannot both be true, never absence of evidence (e.g. two
  agents in the same room with no third corroborator is not flagged).
* The detector is deterministic: re-running on the same transcript
  produces byte-identical flags, including a canonical
  ``contradiction_id`` independent of iteration order, so the flags
  can land in a replay-stable rendered memory view (DESIGN.md §6.6).
* Flags are emitted as :class:`meetings.schemas.ContradictionRef`
  objects -- the shared schema downstream consumers (memory view,
  statement / vote prompts, replay) already understand.
"""

from __future__ import annotations

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    ReportDocument,
    SawPlayerObservation,
    Statement,
)
from meetings.transcript import detect_contradictions


# --- Builders --------------------------------------------------------------


def _alibi(
    *,
    subject: str,
    from_tick: int,
    to_tick: int,
    room: str,
) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        from_tick=from_tick,
        to_tick=to_tick,
        room=room,
    )


def _saw(
    *, tick: int, subject: str, room: str, co_present: tuple[str, ...] = ()
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player",
        tick=tick,
        subject=subject,
        room=room,
        co_present=co_present,
    )


def _report(
    *,
    agent_id: str,
    tick: int = 400,
    observations: tuple[SawPlayerObservation, ...] = (),
    claims: tuple[AlibiClaim | AccusationClaim | CorroborationClaim, ...] = (),
) -> ReportDocument:
    return ReportDocument(
        agent_id=agent_id,
        tick=tick,
        observations=observations,
        claims=claims,
        free_text=f"report from {agent_id}",
    )


def _statement(
    *,
    statement_id: str,
    speaker: str,
    round_index: int = 0,
    claims: tuple[AlibiClaim | AccusationClaim | CorroborationClaim, ...] = (),
    target: str | None = None,
) -> Statement:
    return Statement(
        statement_id=statement_id,
        speaker=speaker,
        tick=400,
        round_index=round_index,
        target=target,
        claims=claims,
        free_text=f"statement {statement_id}",
    )


# --- Empty / non-contradictory transcripts ---------------------------------


class TestNoContradictions:
    def test_empty_transcript_returns_empty_tuple(self) -> None:
        assert detect_contradictions(MeetingTranscript()) == ()

    def test_single_alibi_cannot_self_conflict(self) -> None:
        report = _report(
            agent_id="p-1",
            claims=(_alibi(subject="p-1", from_tick=100, to_tick=200, room="STORAGE"),),
        )
        assert detect_contradictions(MeetingTranscript(reports=(report,))) == ()

    def test_same_room_alibis_do_not_conflict(self) -> None:
        # Two agents corroborating that p-3 was in Storage at the same
        # time is *consistent* evidence, not a contradiction. DESIGN.md
        # §5.4 frames contradictions as "facts that cannot both be true",
        # which excludes mutually supportive testimony.
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="STORAGE"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_non_overlapping_ranges_do_not_conflict(self) -> None:
        # Same agent, different rooms -- but the alibis cover disjoint
        # tick windows, so they describe sequential locations, not
        # contemporaneous ones.
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-1", from_tick=100, to_tick=150, room="STORAGE"),
                    _alibi(subject="p-1", from_tick=160, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_alibis_about_different_subjects_do_not_conflict(self) -> None:
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-4", from_tick=100, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_sighting_outside_alibi_range_is_not_flagged(self) -> None:
        # Alibi covers ticks 100-200; sighting at tick 250 falls
        # outside the window, so the two can both be true (the agent
        # left STORAGE before being seen in CAFETERIA).
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=250, subject="p-3", room="CAFETERIA"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_sighting_matching_alibi_is_corroboration_not_conflict(self) -> None:
        # In-range sighting that places the subject in the alibi's
        # room is corroborating evidence. The detector deliberately
        # ignores it -- it would otherwise pollute the rendered memory
        # view with "contradictions" that are actually agreements.
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_non_alibi_claims_are_ignored(self) -> None:
        # Accusations and corroborations don't carry location data so
        # the detector must skip them. Pairing them with a saw_player
        # observation must not raise or emit a flag.
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-5",
                        confidence=0.7,
                        reason="suspicious behaviour near MedBay",
                    ),
                    CorroborationClaim(
                        type="corroboration",
                        supports="p-3",
                        on_tick=150,
                        reason="saw them in Storage",
                    ),
                ),
                observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(reports=reports)) == ()

    def test_non_sighting_observations_are_ignored(self) -> None:
        # Only ``saw_player`` is cross-referenced against alibis.
        # ``completed_task`` / ``found_body`` carry the reporter's
        # location, not the alibi subject's, and must not be wired
        # into the cross-reference loop.
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=150,
                        subject="p-5",
                        room="STORAGE",
                    ),
                ),
            ),
            _report(
                agent_id="p-1",
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=150,
                        subject="p-7",
                        room="ADMIN",
                    ),
                ),
            ),
        )
        # Mix in the discriminated-union siblings to verify the
        # iterator never treats them as sightings.
        report_with_other_obs = ReportDocument(
            agent_id="p-2",
            tick=400,
            observations=(
                CompletedTaskObservation(
                    type="completed_task",
                    tick=150,
                    task_id="wiring",
                    room="ELECTRICAL",
                ),
                FoundBodyObservation(
                    type="found_body",
                    tick=200,
                    body_of="p-4",
                    room="MEDBAY",
                ),
            ),
            claims=(),
            free_text="",
        )
        transcript = MeetingTranscript(reports=(*reports, report_with_other_obs))
        assert detect_contradictions(transcript) == ()


# --- alibi_conflict --------------------------------------------------------


class TestAlibiConflict:
    def test_two_alibis_same_subject_different_rooms_overlapping_ticks(
        self,
    ) -> None:
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))

        assert len(flags) == 1
        flag = flags[0]
        assert isinstance(flag, ContradictionRef)
        assert flag.kind == "alibi_conflict"
        assert flag.subjects == ("p-3",)
        # The two source ids must reference the contributing reports
        # in canonical (sorted) order; the detector emits stable ids
        # regardless of iteration order so replays remain byte-stable.
        assert flag.event_a_id <= flag.event_b_id
        assert flag.event_a_id == "report:p-1@400:claim:0"
        assert flag.event_b_id == "report:p-2@400:claim:0"
        # Description names both rooms; consumers may render it
        # verbatim in the §6.6 memory view.
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_self_contradicting_report_is_flagged(self) -> None:
        # A single reporter listing two overlapping alibis with
        # different rooms is a self-contradiction and the detector
        # must catch it -- without this, an impostor could plant a
        # contradictory alibi in their own report and the meeting
        # would never see it.
        report = _report(
            agent_id="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                _alibi(subject="p-3", from_tick=180, to_tick=220, room="ADMIN"),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=(report,)))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert flags[0].subjects == ("p-3",)
        assert flags[0].event_a_id == "report:p-3@400:claim:0"
        assert flags[0].event_b_id == "report:p-3@400:claim:1"

    def test_boundary_overlap_is_a_conflict(self) -> None:
        # AlibiClaim ranges are inclusive (DESIGN.md schema docstring),
        # so an alibi ending at tick T and another starting at tick T
        # share the boundary tick and are mutually exclusive.
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=150, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"

    def test_alibi_in_statement_conflicts_with_alibi_in_report(self) -> None:
        # Alibis can be raised in Phase-2 statements as well as
        # Phase-1 reports (DESIGN.md §5.2 + §5.3). The detector must
        # see both surfaces.
        transcript = MeetingTranscript(
            reports=(
                _report(
                    agent_id="p-1",
                    claims=(
                        _alibi(
                            subject="p-3",
                            from_tick=100,
                            to_tick=200,
                            room="STORAGE",
                        ),
                    ),
                ),
            ),
            statements=(
                _statement(
                    statement_id="m1:r0:p-2",
                    speaker="p-2",
                    claims=(
                        _alibi(
                            subject="p-3",
                            from_tick=150,
                            to_tick=180,
                            room="ADMIN",
                        ),
                    ),
                ),
            ),
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert {flags[0].event_a_id, flags[0].event_b_id} == {
            "report:p-1@400:claim:0",
            "stmt:m1:r0:p-2:claim:0",
        }


# --- alibi_vs_sighting -----------------------------------------------------


class TestAlibiVsSighting:
    def test_sighting_inside_alibi_range_different_room_is_flagged(self) -> None:
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_vs_sighting"
        assert flag.subjects == ("p-3",)
        assert flag.event_a_id <= flag.event_b_id
        assert {flag.event_a_id, flag.event_b_id} == {
            "report:p-3@400:claim:0",
            "report:p-5@400:obs:0",
        }
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_sighting_at_alibi_boundary_is_flagged(self) -> None:
        # Alibi ranges are inclusive; a sighting at the exact range
        # endpoint falls inside the window and conflicts.
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=200, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_vs_sighting"

    def test_multiple_sightings_each_emit_a_flag(self) -> None:
        # Each conflicting sighting is its own flag; consumers can
        # weigh them (e.g. via co_present witnesses) but the detector
        # never aggregates -- aggregation would hide evidence.
        reports = (
            _report(
                agent_id="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=120, subject="p-3", room="CAFETERIA"),),
            ),
            _report(
                agent_id="p-7",
                observations=(_saw(tick=180, subject="p-3", room="ADMIN"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))
        assert len(flags) == 2
        assert all(flag.kind == "alibi_vs_sighting" for flag in flags)


# --- Mixed cases / determinism / surface contract --------------------------


class TestMixedAndDeterministic:
    def test_alibi_conflict_and_alibi_vs_sighting_coexist(self) -> None:
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))

        kinds = sorted(flag.kind for flag in flags)
        # One alibi_conflict between the two alibis; one
        # alibi_vs_sighting per alibi whose room differs from ADMIN
        # (both differ), so we expect three flags total.
        assert kinds == [
            "alibi_conflict",
            "alibi_vs_sighting",
            "alibi_vs_sighting",
        ]

    def test_result_is_sorted_by_contradiction_id(self) -> None:
        # Determinism contract: flags must come back in a stable
        # order (sorted by contradiction_id) so the rendered memory
        # view that consumes them is replay-stable.
        reports = (
            _report(
                agent_id="p-9",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))
        ids = [flag.contradiction_id for flag in flags]
        assert ids == sorted(ids)

    def test_pure_function_is_idempotent(self) -> None:
        # Re-running on the same input yields byte-identical output
        # (no hidden state, no nondeterministic id allocation).
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
            _report(
                agent_id="p-5",
                observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
            ),
        )
        transcript = MeetingTranscript(reports=reports)
        first = detect_contradictions(transcript)
        second = detect_contradictions(transcript)
        assert first == second

    def test_iteration_order_does_not_affect_contradiction_id(self) -> None:
        # The same logical contradiction must produce the same
        # ``contradiction_id`` regardless of which report comes first.
        # Without the canonical-pair sort in the detector, swapping
        # report order would produce two different ids for the same
        # underlying conflict and the §6.6 memory view would
        # double-count after a re-render.
        alibi_left = _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE")
        alibi_right = _alibi(
            subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"
        )
        report_a = _report(agent_id="p-1", claims=(alibi_left,))
        report_b = _report(agent_id="p-2", claims=(alibi_right,))

        forward = detect_contradictions(MeetingTranscript(reports=(report_a, report_b)))
        backward = detect_contradictions(
            MeetingTranscript(reports=(report_b, report_a))
        )
        assert len(forward) == 1
        assert len(backward) == 1
        assert forward[0].contradiction_id == backward[0].contradiction_id
        assert forward[0].event_a_id == backward[0].event_a_id
        assert forward[0].event_b_id == backward[0].event_b_id

    def test_flags_are_shared_schema_objects(self) -> None:
        # Definition-of-done item: "Detected contradictions are
        # represented in shared schemas and can be surfaced to
        # rendered memory." The shared schema is
        # :class:`meetings.schemas.ContradictionRef`; the detector
        # returns that exact type so downstream consumers
        # (statement / vote prompts, rendered memory view) accept
        # the output without conversion.
        reports = (
            _report(
                agent_id="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _report(
                agent_id="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(reports=reports))

        assert isinstance(flags, tuple)
        for flag in flags:
            assert isinstance(flag, ContradictionRef)
            # Round-trip via the shared schema's JSON representation
            # to confirm the emitted objects are valid Pydantic
            # instances ready for transport (replay / API / prompt).
            dumped = flag.model_dump(mode="json")
            assert ContradictionRef.model_validate(dumped) == flag
