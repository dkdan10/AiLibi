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
Phase 19 changed labels and instrumentation only (locked decision 1 —
``meetings/`` and the prompt templates were untouched), so every assertion over
the served DTOs holds unchanged.

A second block at the bottom reads the same four exhibits under the Phase-20
grounded-prosecution rules (which bind only when a caller supplies the sighting
records, so the served bytes above are still the record-free reading) and
records each fixture's new outcome as an asserted value.
An exhibit whose mechanism moves at that lever's adopting record then says so
here rather than quietly ceasing to demonstrate anything.
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
#
# The baseline-7 record FLIPPED all four. Each test below asserts the flip on
# the committed bytes, and each anchor carries the baseline-6 reading it
# replaced (audits/audit-phase-20-baseline-7.md §4).


def test_every_mechanism_records_its_verdict() -> None:
    """Each exhibit says what the record did to it, and what it read before.

    Not every status is FLIPPED any more. On baseline 8 the content-vs-own-memory
    exhibit is PARTLY FLIPPED: its evidence half held (the fatal STRONG flag is
    still gone) while its outcome half regressed (the meeting ejects a crewmate
    again). The allowed set is enumerated so a status nobody defined fails here,
    rather than widened to "any string".
    """

    allowed = {"FLIPPED", "PARTLY FLIPPED"}
    for mechanism in EVIDENCE_MECHANISMS:
        assert mechanism.status in allowed, mechanism.key
        for anchor in mechanism.anchors:
            assert anchor.baseline6.strip(), f"{mechanism.key}: no baseline-6 line"
            # Every one of them was a CREWMATE ejection: that is what "flipped"
            # is measured against, and an exhibit whose frozen line no longer
            # says so would be flipping away from nothing.
            assert "(CREWMATE)" in anchor.baseline6, mechanism.key


def test_provenance_impossible_sighting_no_longer_mints_its_flag() -> None:
    """Seed 23 M1: the impostor-authored sighting flag is gone, and so is the ejection.

    The mechanism was a flag whose sighting side nobody could have made. On the
    recorded bytes the meeting carries no contradiction at all and the table
    skips, so there is no unchecked sighting left to convict on.
    """

    (anchor,) = PROVENANCE_IMPOSSIBLE_SIGHTING.anchors
    meeting = _meeting(_load(anchor), anchor)

    # DEMOTED rather than absent on baseline 8: two flags survive, both
    # weak-banded, and neither can convict alone. The mechanism this exhibit is
    # about — a STRONG unchecked sighting carrying a crewmate out — still does
    # not happen, and the table still skips.
    assert [flag.category for flag in meeting.contradictions] == [
        "weak_signal",
        "weak_signal",
    ]
    assert all(flag.weak for flag in meeting.contradictions)
    assert meeting.outcome == "SKIPPED"
    assert meeting.ejected_player_id is None


def test_content_vs_own_memory_miss_defangs_the_flag_but_still_ejects() -> None:
    """Seed 12 M0: the evidence half held, the outcome half did NOT.

    The fatal STRONG flag built from two innocents' statements is still gone —
    both survivors are weak-banded, so nothing here can convict alone. But on
    baseline 8 this meeting EJECTS the crewmate p-5, where the previous recording
    skipped. The exhibit's original claim ("no longer ejects an innocent") is
    therefore false on these bytes, and this test pins the regression rather than
    the claim: same family as the sole-flag class re-opening
    (audits/audit-phase-21-rerecord.md §5.1.1), and the Wave-2 record rules on it.
    """

    (anchor,) = CONTENT_VS_OWN_MEMORY_MISS.anchors
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}

    # The evidence half: unchanged, and still defanged.
    assert [flag.category for flag in meeting.contradictions] == [
        "weak_signal",
        "weak_signal",
    ]
    assert all(flag.weak for flag in meeting.contradictions)

    # The outcome half: a crewmate is ejected on weak evidence alone.
    assert meeting.outcome == "EJECTED"
    assert meeting.ejected_player_id == "p-5"
    assert roles["p-5"] == "CREWMATE"


def test_one_tick_interval_artifact_now_convicts_the_impostor() -> None:
    """Seeds 49 + 41: the interval flags are gone; role proof decides both.

    Both meetings used to eject a crewmate on a one-tick window. Each now
    carries exactly one flag -- an engine-certified ``vent_sighting`` -- and
    each ejects the impostor it names.
    """

    seed_49, seed_41 = ONE_TICK_INTERVAL_ARTIFACT.anchors
    assert (seed_49.seed, seed_41.seed) == (49, 41)

    for anchor in (seed_49, seed_41):
        replay = _load(anchor)
        meeting = _meeting(replay, anchor)
        roles = {player.agent_id: player.role for player in replay.players}
        assert [flag.category for flag in meeting.contradictions] == ["role_proof"]
        (proof,) = meeting.contradictions
        assert meeting.outcome == "EJECTED"
        assert meeting.ejected_player_id in proof.subjects
        assert roles[str(meeting.ejected_player_id)] == "IMPOSTOR"


def test_equal_weight_conflict_has_nothing_left_to_weigh() -> None:
    """Seed 41 M0: the meeting carries one kind of evidence, not two.

    The mechanism was a role proof and a cross-statement flag entering the
    graph at the same lift. On the recorded bytes the cross-statement flag is
    gone entirely, so the two can no longer compete -- and the ejection goes to
    the player the proof names.
    """

    (anchor,) = EQUAL_WEIGHT_CONFLICT.anchors
    replay = _load(anchor)
    meeting = _meeting(replay, anchor)
    roles = {player.agent_id: player.role for player in replay.players}

    assert [flag.category for flag in meeting.contradictions] == ["role_proof"]
    (proof,) = meeting.contradictions
    assert [roles[s] for s in proof.subjects] == ["IMPOSTOR"]
    assert meeting.ejected_player_id in proof.subjects


#: Committed meetings that DO convict on a STRONG statement-pair flag naming the
#: ejected player -- the shape the four exhibits were, and the shape this search
#: hunts. Frozen by NAME so the property survives as a tripwire on GROWTH: a
#: meeting outside this set fails, and so does one that leaves it.
#:
#: This class held at ZERO on baseline 7 and RE-OPENED at one meeting carrying
#: two such flags on baseline 8, where it convicts the CREWMATE p-9. It is the
#: same family as the sole-flag wrongful-conviction class re-opening 0 -> 4
#: (audits/audit-phase-21-rerecord.md §5.1.1), and the Wave-2 record rules on it.
#: Pinning it here neither excuses it nor deletes the property.
_STATEMENT_PAIR_CONVICTIONS: Final[frozenset[str]] = frozenset(
    {"headless-seed-41:meeting-2"}
)


def test_the_flip_search_finds_exactly_the_named_meetings() -> None:
    """The perturbation: a meeting that convicts an innocent is detectable.

    The exhibits above assert absences -- no flag, no innocent ejection -- so the
    predicate behind them must be shown to fire. Walk the whole 9p2i set for a
    STRONG statement-pair flag naming the ejected player, and hold the result to
    the named set above rather than to zero, which is what these bytes carry.
    The planted case proves the predicate still fires on a shape nothing recorded.

    ``alibi_vs_physical`` is deliberately outside the search: it is grounded on
    an engine-certified body or vent, not on two accounts of the same tick, and
    one committed meeting still convicts on it.
    """

    statement_pair = {"alibi_vs_sighting", "alibi_conflict"}

    def convicting(meeting: MeetingView) -> list[str]:
        return [
            flag.kind
            for flag in meeting.contradictions
            if flag.category == "cross_statement"
            and flag.kind in statement_pair
            and not flag.weak
            and meeting.ejected_player_id in flag.subjects
        ]

    loader = ReplayLoader(_SAMPLES / "9p2i")
    found: dict[str, list[str]] = {}
    ejected_roles: dict[str, str | None] = {}
    for seed in range(50):
        replay = loader.load_replay(f"headless-seed-{seed}")
        roles = {player.agent_id: player.role for player in replay.players}
        for meeting in replay.meetings:
            hits = convicting(meeting)
            if hits:
                found[meeting.meeting_id] = hits
                ejected_roles[meeting.meeting_id] = roles.get(
                    meeting.ejected_player_id or ""
                )

    # Exactly the named set: a NEW meeting convicting this way fails here, and so
    # does one dropping out (which would mean the class closed and this pin, not
    # the bytes, is what needs revisiting).
    assert set(found) == _STATEMENT_PAIR_CONVICTIONS

    # And the loss is stated, not merely tolerated: the one meeting convicts a
    # CREWMATE on two STRONG alibi-versus-sighting flags.
    assert found["headless-seed-41:meeting-2"] == [
        "alibi_vs_sighting",
        "alibi_vs_sighting",
    ]
    assert ejected_roles["headless-seed-41:meeting-2"] == "CREWMATE"

    planted = MeetingView.model_validate(
        {
            **_meeting(
                _load(CONTENT_VS_OWN_MEMORY_MISS.anchors[0]),
                CONTENT_VS_OWN_MEMORY_MISS.anchors[0],
            ).model_dump(),
            "ejected_player_id": "p-5",
            "outcome": "EJECTED",
            "contradictions": [
                {
                    **_meeting(
                        _load(CONTENT_VS_OWN_MEMORY_MISS.anchors[0]),
                        CONTENT_VS_OWN_MEMORY_MISS.anchors[0],
                    )
                    .contradictions[1]
                    .model_dump(),
                    "category": "cross_statement",
                    "weak": False,
                }
            ],
        }
    )
    assert convicting(planted) == ["alibi_vs_sighting"]
