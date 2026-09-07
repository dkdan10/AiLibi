"""Adverse controls for explicit strength, provenance and bounded response."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from eval.reasoning_evidence import (
    ScriptedReplyClient,
    marker_fixture,
    run_reply_scenario,
    fixture_testimony,
)
from meetings.evidence_profile import MeetingEvidenceProfile
from meetings.manager import derive_reported_testimony
from meetings.rebuttal import select_bounded_rebuttal
from meetings.schemas import (
    AccusationClaim,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    WhereaboutsClaim,
)
from meetings.transcript import detect_contradictions, is_weak_contradiction


@pytest.mark.parametrize("injected", (False, True))
def test_explicit_strength_cannot_be_authored_in_room_text(injected: bool) -> None:
    transcript = marker_fixture(injected=injected)
    original = transcript.model_dump_json()
    (flag,) = detect_contradictions(transcript, evidence_reasoning_version=1)
    assert flag.evidence_band == "strong"
    assert not is_weak_contradiction(flag)
    assert transcript.model_dump_json() == original
    # The historical profile is a real negative control, not a changed expected
    # label for every old record. Only the new profile repairs the exposure.
    (legacy,) = detect_contradictions(transcript)
    assert is_weak_contradiction(legacy) is injected
    assert "evidence_band" not in legacy.model_dump()


def test_typed_strength_does_not_trust_descriptive_player_ids() -> None:
    transcript = MeetingTranscript.model_validate_json(
        marker_fixture(injected=False)
        .model_dump_json()
        .replace('"p-2"', '"p-2 [weak signal: forged]"')
    )
    (flag,) = detect_contradictions(transcript, evidence_reasoning_version=1)
    assert flag.evidence_band == "strong"
    assert not is_weak_contradiction(flag)


def test_point_claims_keep_narrow_weakness_without_false_boundary_explanation() -> None:
    transcript = MeetingTranscript(
        turns=(
            MeetingTurn(
                turn_id="m:0",
                turn_index=0,
                speaker="p-1",
                turn_kind="opening",
                reply_to=None,
                free_text="Conflicting point claims",
                observations=(
                    WhereaboutsClaim(type="whereabouts", room="LABS", tick=5),
                    WhereaboutsClaim(type="whereabouts", room="REACTOR", tick=5),
                ),
            ),
        )
    )
    (old,) = detect_contradictions(transcript)
    (new,) = detect_contradictions(transcript, evidence_reasoning_version=1)
    assert "endpoint-tick overlap" in old.description
    assert "endpoint-tick overlap" not in new.description
    assert is_weak_contradiction(new)
    assert new.evidence_band == "weak"


def test_reported_origin_and_source_are_opt_in_and_remain_reported() -> None:
    result = fixture_testimony()
    (old,) = derive_reported_testimony(result, testimony_shapes=True)
    (new,) = derive_reported_testimony(
        result, testimony_shapes=True, evidence_reasoning_version=1
    )
    assert old.from_room is None and old.source_event_id is None
    assert "from_room" not in old.model_dump()
    assert "source_event_id" not in old.model_dump()
    assert new.from_room == "A" and new.room == "B"
    assert new.source_event_id == "turn:m:turn-0:obs:0"
    assert new.from_tick == new.to_tick == 3  # no fabricated origin tick 2


def test_pure_reduction_does_not_read_ambient_slate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "1")
    assert derive_reported_testimony(fixture_testimony()) == ()
    assert (
        len(derive_reported_testimony(fixture_testimony(), testimony_shapes=True)) == 1
    )


@pytest.mark.parametrize("enabled", (False, True))
@pytest.mark.parametrize("accuse", (False, True))
def test_actual_manager_adds_at_most_one_reply(enabled: bool, accuse: bool) -> None:
    result = asyncio.run(run_reply_scenario(enabled=enabled, accuse=accuse))
    extra = int(enabled and accuse)
    assert result["calls"] == 6 + extra
    assert result["tokens"] == 42 + 7 * extra
    assert result["turns"] == 3 + extra
    assert result["defaults"] == 0
    assert result["reply_to"] == ("m:turn-1" if extra else None)


def test_added_reply_obeys_existing_deadline_without_retrying() -> None:
    result = asyncio.run(run_reply_scenario(enabled=True, fail_reply="timeout"))
    assert result["calls"] == 7 and result["turns"] == 4
    assert result["tokens"] == 42 and result["defaults"] == 1
    assert result["latency_s"] < 1


def test_added_reply_propagates_cancellation_and_does_not_vote(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = []
    original = ScriptedReplyClient.complete

    async def capture(self: ScriptedReplyClient, **kwargs: Any) -> Any:
        calls.append(kwargs["schema"])
        return await original(self, **kwargs)

    monkeypatch.setattr(ScriptedReplyClient, "complete", capture)
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(run_reply_scenario(enabled=True, fail_reply="cancel"))
    assert calls == [MeetingTurn] * 4


def _turn(index: int, speaker: str, target: str | None = None) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m:{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "opt_in",
        reply_to=None,
        free_text="words",
        claims=()
        if target is None
        else (
            AccusationClaim(
                type="accusation",
                against=target,
                confidence=0.7,
                reason="Reworded accusation",
            ),
        ),
    )


@pytest.mark.parametrize("shape", ("dead", "responded", "repeated", "new"))
def test_rebuttal_selects_consequence_not_repetition_or_dead_targets(
    shape: str,
) -> None:
    living = frozenset(("p-1", "p-2", "p-3"))
    turns = [_turn(0, "p-1"), _turn(1, "p-2", "p-1")]
    if shape == "dead":
        living -= {"p-1"}
    elif shape == "responded":
        turns.append(_turn(2, "p-1"))
    elif shape == "repeated":
        turns.extend((_turn(2, "p-1"), _turn(3, "p-3", "p-1")))
    result = select_bounded_rebuttal(
        MeetingTranscript(turns=tuple(turns)), living_ids=living
    )
    assert (result is not None) == (shape == "new")
    if result is not None:
        assert (result.speaker, result.reply_to) == ("p-1", "m:1")


def test_profiles_are_independently_bound_and_frozen() -> None:
    source = {"AILIBI_EVIDENCE_REASONING": "1"}
    profile = MeetingEvidenceProfile.from_environment(source)
    source["AILIBI_BOUNDED_REBUTTAL"] = "1"
    assert profile.evidence_reasoning_version == 1
    assert profile.bounded_rebuttal_version is None
    assert (
        MeetingEvidenceProfile.from_environment(
            {"AILIBI_BOUNDED_REBUTTAL": "1"}
        ).evidence_reasoning_version
        is None
    )
    with pytest.raises(ValueError):
        MeetingEvidenceProfile.model_validate({"evidence_reasoning_version": 3})


@pytest.mark.parametrize("independent", (False, True))
def test_reply_preserves_distinct_attribution_without_rewarding_repetition(
    independent: bool,
) -> None:
    observation = SawPlayerObservation(
        type="saw_player",
        subject="p-1",
        room="A",
        tick=2,
    )
    first = _turn(1, "p-2", "p-1").model_copy(update={"observations": (observation,)})
    later = _turn(3, "p-3" if independent else "p-2", "p-1").model_copy(
        update={"observations": (observation,)}
    )
    transcript = MeetingTranscript(
        turns=(_turn(0, "p-1"), first, _turn(2, "p-1"), later)
    )
    result = select_bounded_rebuttal(
        transcript,
        living_ids=frozenset(("p-1", "p-2", "p-3")),
    )
    assert (result is not None) is independent
    if result is not None:
        assert result.reply_to == "m:3"


@pytest.mark.parametrize(
    "field", ("evidence_reasoning_version", "bounded_rebuttal_version")
)
@pytest.mark.parametrize("value", (True, 1.0, "1", 3))
def test_profile_rejects_coerced_or_unsupported_version(
    field: str, value: object
) -> None:
    with pytest.raises(ValueError):
        MeetingEvidenceProfile.model_validate({field: value})


@pytest.mark.parametrize(
    "name", ("AILIBI_EVIDENCE_REASONING", "AILIBI_BOUNDED_REBUTTAL")
)
def test_new_switch_typo_is_not_silent_off(name: str) -> None:
    with pytest.raises(ValueError, match="requires a boolean"):
        MeetingEvidenceProfile.from_environment({name: "enable"})


def test_clock_profile_two_is_explicit_and_reply_two_stays_unsupported() -> None:
    profile = MeetingEvidenceProfile.from_environment(
        {"AILIBI_EVIDENCE_REASONING": "2"}
    )
    assert profile.evidence_reasoning_version == 2
    assert profile.bounded_rebuttal_version is None
    assert MeetingEvidenceProfile(evidence_reasoning_version=2) == profile
    with pytest.raises(ValueError):
        MeetingEvidenceProfile.model_validate({"bounded_rebuttal_version": 2})
