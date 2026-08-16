"""The four evidence-honesty mechanisms stay executable exhibits (Task 19.11).

audits/audit-phase-19-triage.md §7 item 12 + item 20 asks Phase 19 to PRESERVE
separate fixtures for the provenance-impossible sighting, the
content-vs-own-memory mismatch, the one-tick interval artifact, and the
equal-weight conflict — because the owner decision the triage reserves ("whether
the evidence-honesty substrate fixes become the first post-19 gameplay phase")
has to be made on evidence, and a fixture nobody runs is not evidence.

Each exhibit in ``tests/api/fixtures/evidence_mechanisms.py`` is verified here
against the SERVED spectator DTOs — the real ``ReplayLoader`` over the committed
bytes, not a hand-authored replica. The exhibits are checked SEPARATELY (one
parametrized case per mechanism, plus per-anchor cases) so a change that moves
one mechanism names that mechanism in the failure.

These tests assert what the frozen pipeline DOES; they are not a bug report.
Phase 19 changes labels and instrumentation only (locked decision 1 —
``meetings/`` and the prompt templates are untouched), so every assertion here
should hold unchanged across this phase.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Final

import pytest

from api.replay_loader import ReplayLoader
from api.schemas import MeetingView, ReplayView
from tests.api.fixtures.evidence_mechanisms import (
    CONTENT_VS_OWN_MEMORY_MISS,
    EQUAL_WEIGHT_CONFLICT,
    EVIDENCE_MECHANISMS,
    ONE_TICK_INTERVAL_ARTIFACT,
    PROVENANCE_IMPOSSIBLE_SIGHTING,
    EvidenceMechanism,
    MechanismAnchor,
)

_SAMPLES: Final[Path] = Path(__file__).resolve().parents[2] / "replays" / "samples"

# The turn an event id references (mirrors ``meetings/transcript.py``'s
# ``turn:<turn_id>:<segment>:<index>`` ids; greedy ``.+`` captures the whole turn
# id before the final suffix). ``whereabouts`` is the Task-16.7 roll-call segment.
_EVENT_TURN: Final[re.Pattern[str]] = re.compile(
    r"^turn:(.+):(?:claim|obs|whereabouts):\d+$"
)


def _load(anchor: MechanismAnchor) -> ReplayView:
    return ReplayLoader(_SAMPLES / anchor.seedset).load_replay(anchor.game_id)


def _meeting(replay: ReplayView, anchor: MechanismAnchor) -> MeetingView:
    assert len(replay.meetings) > anchor.meeting_index, (
        f"{anchor.game_id} no longer has a meeting at index "
        f"{anchor.meeting_index}; the exhibit's anchor is stale."
    )
    return replay.meetings[anchor.meeting_index]


def _speaker(meeting: MeetingView, event_id: str) -> str:
    match = _EVENT_TURN.match(event_id)
    assert match is not None, f"unrecognised event id shape: {event_id!r}"
    turn_id = match.group(1)
    speakers = {turn.turn_id: turn.speaker for turn in meeting.turns}
    assert turn_id in speakers, f"{event_id!r} references an absent turn"
    return speakers[turn_id]


def _anchors() -> list[tuple[str, MechanismAnchor]]:
    return [
        (f"{m.key}[{a.seedset}-seed-{a.seed}-M{a.meeting_index}]", a)
        for m in EVIDENCE_MECHANISMS
        for a in m.anchors
    ]


# ---------------------------------------------------------------------------
# The fixture set itself: four SEPARATE mechanisms, each documented
# ---------------------------------------------------------------------------


def test_the_four_mechanisms_are_separate_and_documented() -> None:
    """Item 20 asks for FOUR separate fixtures, each saying what it shows."""

    assert EVIDENCE_MECHANISMS == (
        PROVENANCE_IMPOSSIBLE_SIGHTING,
        CONTENT_VS_OWN_MEMORY_MISS,
        ONE_TICK_INTERVAL_ARTIFACT,
        EQUAL_WEIGHT_CONFLICT,
    )
    keys = [m.key for m in EVIDENCE_MECHANISMS]
    assert len(set(keys)) == len(keys) == 4, (
        "the four mechanisms must stay four separate fixtures — merging them "
        "loses the distinction the post-19 owner decision turns on"
    )
    for mechanism in EVIDENCE_MECHANISMS:
        assert mechanism.demonstrates.strip(), f"{mechanism.key}: no one-liner"
        assert mechanism.missing_check.strip(), f"{mechanism.key}: no missing check"
        assert mechanism.audit_ref.startswith("audits/"), (
            f"{mechanism.key}: the exhibit must cite its audit source"
        )
        assert mechanism.anchors, f"{mechanism.key}: no committed anchor"


@pytest.mark.parametrize(
    "mechanism",
    EVIDENCE_MECHANISMS,
    ids=[m.key for m in EVIDENCE_MECHANISMS],
)
def test_mechanism_anchors_point_at_committed_bytes(
    mechanism: EvidenceMechanism,
) -> None:
    """Every anchor names a replay that is actually committed."""

    for anchor in mechanism.anchors:
        path = _SAMPLES / anchor.seedset / f"replay-seed-{anchor.seed}.jsonl"
        assert path.is_file(), (
            f"{mechanism.key}: {path} is not committed — the exhibit lost its evidence"
        )


# ---------------------------------------------------------------------------
# Each anchored meeting, verified through the SERVED DTOs
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "anchor",
    [a for _, a in _anchors()],
    ids=[name for name, _ in _anchors()],
)
def test_anchored_meeting_matches_the_exhibit(anchor: MechanismAnchor) -> None:
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}

    assert meeting.tick == anchor.tick
    assert meeting.outcome == anchor.outcome
    assert meeting.ejected_player_id == anchor.ejected_player_id
    assert (
        None if anchor.ejected_player_id is None else roles[anchor.ejected_player_id]
    ) == anchor.ejected_role
    assert (
        tuple(sorted(a for a, role in roles.items() if role == "IMPOSTOR"))
        == anchor.impostors
    )

    served = meeting.contradictions
    assert len(served) == len(anchor.flags), (
        f"{anchor.game_id} M{anchor.meeting_index} now carries "
        f"{len(served)} flag(s); the exhibit pins {len(anchor.flags)}"
    )
    for flag, expected in zip(served, anchor.flags, strict=True):
        assert flag.kind == expected.kind
        assert flag.category == expected.category
        assert flag.subjects == expected.subjects
        assert flag.weak == expected.weak
        assert (flag.event_a_id == flag.event_b_id) == expected.self_linked
        assert _speaker(meeting, flag.event_a_id) == expected.speaker_a
        assert _speaker(meeting, flag.event_b_id) == expected.speaker_b
        assert expected.description_contains in flag.description


# ---------------------------------------------------------------------------
# The mechanism-specific claims (what each exhibit is FOR)
# ---------------------------------------------------------------------------


def test_provenance_impossible_sighting_convicts_on_an_unchecked_sighting() -> None:
    """Seed 23 M1: the sighting half of the fatal flag is spoken by an impostor.

    The flag juxtaposes the ejected crewmate's own placement with a sighting
    from a player whose ability to make it is never examined — the missing
    provenance gate, stated as data rather than prose.
    """

    (anchor,) = PROVENANCE_IMPOSSIBLE_SIGHTING.anchors
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}
    (flag,) = meeting.contradictions

    assert flag.category == "cross_statement"
    assert roles[_speaker(meeting, flag.event_a_id)] == "CREWMATE"
    assert roles[_speaker(meeting, flag.event_b_id)] == "IMPOSTOR"
    assert meeting.ejected_player_id in flag.subjects
    assert roles[str(meeting.ejected_player_id)] == "CREWMATE"


def test_content_vs_own_memory_miss_has_no_impostor_authored_statement() -> None:
    """Seed 12 M0: BOTH sides of the fatal flag are authored by innocents.

    Nothing in the pipeline compares a restated observation against the
    speaker's own episodic record, so two honest, slightly-wrong accounts are
    enough to eject a truthful crewmate.
    """

    (anchor,) = CONTENT_VS_OWN_MEMORY_MISS.anchors
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}

    fatal = [
        flag
        for flag in meeting.contradictions
        if meeting.ejected_player_id in flag.subjects
    ]
    assert len(fatal) == 1, "the exhibit turns on exactly one flag naming the ejectee"
    (flag,) = fatal
    assert flag.category == "cross_statement"
    for event_id in (flag.event_a_id, flag.event_b_id):
        assert roles[_speaker(meeting, event_id)] == "CREWMATE"
    assert roles[str(meeting.ejected_player_id)] == "CREWMATE"


def test_one_tick_interval_artifact_rests_on_single_tick_windows() -> None:
    """Seeds 49 + 41: every directional flag names a one-tick window.

    Seed 49's two flags are both weak-stamped and obeyed anyway; seed 41's is
    NOT stamped, because a degenerate single-tick roll-call placement takes the
    Task-18.9 whereabouts-interior exemption and mints a STRONG flag. Same
    one-tick material, opposite weighting — which is why the mechanism is about
    interval extraction, not about the weak marker alone.
    """

    seed_49, seed_41 = ONE_TICK_INTERVAL_ARTIFACT.anchors
    assert (seed_49.seed, seed_41.seed) == (49, 41)

    meeting_49 = _meeting(_load(seed_49), seed_49)
    assert [flag.category for flag in meeting_49.contradictions] == [
        "weak_signal",
        "weak_signal",
    ]
    assert meeting_49.outcome == "EJECTED"

    meeting_41 = _meeting(_load(seed_41), seed_41)
    artifact = next(
        flag for flag in meeting_41.contradictions if flag.category == "cross_statement"
    )
    assert not artifact.weak
    assert "(ticks 3-3)" in artifact.description
    assert "at tick 3." in artifact.description


def test_equal_weight_conflict_ejects_past_the_role_proof() -> None:
    """Seed 41 M0: proof names the impostor, the table ejects the crewmate.

    The meeting carries BOTH categories at once — a grounded ``vent_sighting``
    naming the real impostor and a cross-statement flag naming a crewmate — and
    the ejection goes to the crewmate. The taxonomy this task adds is what lets
    a reader see the two flags are not the same kind of evidence; nothing here
    changes how they are scored.
    """

    (anchor,) = EQUAL_WEIGHT_CONFLICT.anchors
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}

    proof = next(f for f in meeting.contradictions if f.category == "role_proof")
    conflict = next(
        f for f in meeting.contradictions if f.category == "cross_statement"
    )

    assert [roles[s] for s in proof.subjects] == ["IMPOSTOR"]
    assert [roles[s] for s in conflict.subjects] == ["CREWMATE"]
    assert meeting.ejected_player_id in conflict.subjects
    assert meeting.ejected_player_id not in proof.subjects
