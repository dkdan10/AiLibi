"""Guard-rationale redaction: the coerced ballot stops narrating omniscience.

Task 19.15; audits/audit-phase-19-triage.md §7 item 16. The teammate firewall
guard (:func:`meetings.manager.coerce_teammate_ballot_to_skip`, Task 7.12)
rewrites a betrayal ballot's ``target`` to SKIP and prepends
:data:`meetings.manager.TEAMMATE_VOTE_TARGET_MARKER`. Until this task it also
PRESERVED ``rationale_text`` -- text the model wrote to justify voting a fellow
impostor, so it can state the impostor's private knowledge outright ("p-3 is my
partner", "I did the kill"). That text rides the coerced ballot onto the
spectator surface, where the marker is stripped to a chip and the remainder
renders as the voter's stated reason: omniscience leaking through the guard's
own output.

What this module pins:

* the model-authored body is REPLACED by
  :data:`meetings.manager.TEAMMATE_COERCED_VOTE_RATIONALE` -- nothing of the
  original text survives, and the replacement is byte-identical regardless of
  what the model wrote (no leakage through length or shape);
* EVERY audit marker survives the redaction, not just this guard's
  (auditability is never laundered). The recorded ballot still names the
  original teammate target, AND the markers the upstream ballot chain already
  prepended -- a nulled ``primary_reason_id`` / ``primary_reason_observation_id``
  -- are preserved in place, so the coerced ballot still reports its nulled
  citations to every downstream marker consumer;
* the replacement body is BRACKETED, the repo's "system text, not model voice"
  shape, so ``eval.vj_instruments._strip_leading_markers`` drops it before a
  ballot body reaches the §2.5 voice fold. The guard's prose is never measured
  as the model's;
* the redacted body carries zero teammate / self-kill / role phrasing. The
  scan runs on the BODY, not the whole string: the marker legitimately
  contains the word "teammate" (it is the audit channel), and gating its
  DISPLAY is Task 19.11's, never this task's;
* the redaction is scoped to the coercion -- an untouched ballot (no
  teammates, or a non-teammate target) keeps its rationale verbatim.

Distinct from model-originated fourth-wall statements, which Task 19.14
measures and Task 19.8 discloses; this is the guard-originated TEXT class only.
The path is dormant for committed bytes -- the recorded corpus is frozen and no
replay is rewritten -- so what is pinned here is what a FUTURE recording
carries.

The manager harness reuses ``tests.meetings.test_manager``'s shared scripted
client helpers, mirroring ``tests.meetings.test_citation_gate``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Final

import pytest
from pydantic import BaseModel

from api.replay_loader import _parse_rewrite_reasons  # noqa: PLC2701
from eval.vj_instruments import _strip_leading_markers  # noqa: PLC2701
from meetings.manager import (
    INVALID_OBSERVATION_ID_MARKER,
    INVALID_REASON_ID_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    MeetingParticipant,
    _normalize_ballot_observation_id,  # noqa: PLC2701
    _normalize_ballot_reason_id,  # noqa: PLC2701
    coerce_teammate_ballot_to_skip,
)
from meetings.schemas import VoteBallot
from tests.meetings.test_manager import (
    _extract_marker,  # noqa: PLC2701
    _participant,  # noqa: PLC2701
    _run_meeting,  # noqa: PLC2701
    _turn_json,  # noqa: PLC2701
)

# The leak class, verbatim from the audit's description: a rationale written to
# justify the betrayal target, stating private impostor knowledge.
_OMNISCIENT_RATIONALE: Final[str] = (
    "p-5 is my partner and they botched the cafeteria kill I set up, "
    "so I am cutting them loose before the crew connects us."
)

# Substrings that must not appear in the recorded BODY. Role/team words plus
# the self-kill vocabulary the leak class uses. Matched case-insensitively.
_OMNISCIENCE_TOKENS: Final[tuple[str, ...]] = (
    "partner",
    "teammate",
    "ally",
    "impostor",
    "fellow",
    "kill",
    "vent",
    "sabotage",
    "my team",
    "we are",
)


def _ballot(
    *,
    voter: str = "p-4",
    target: str = "p-5",
    confidence: float = 0.9,
    primary_reason_id: str | None = "m-1:turn-0",
    rationale_text: str = _OMNISCIENT_RATIONALE,
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=primary_reason_id,
        considered_alternatives=(),
        rationale_text=rationale_text,
    )


def _marker_for(target: str) -> str:
    return TEAMMATE_VOTE_TARGET_MARKER.format(target=target)


def _body_of(rationale_text: str, *, target: str) -> str:
    """The model-attributed remainder, i.e. the rationale minus the audit marker."""

    marker = _marker_for(target)
    assert rationale_text.startswith(marker), rationale_text
    return rationale_text[len(marker) :]


# --- The pure guard ---------------------------------------------------------


class TestCoercedRationaleIsRedacted:
    def test_recorded_rationale_is_the_marker_plus_the_neutral_note(self) -> None:
        # The whole fixture, pinned exactly: audit marker (unchanged) followed
        # by the substitution note -- never the model's text.
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(), fellow_impostor_ids=("p-5",)
        )

        assert coerced.target == "SKIP"
        assert coerced.rationale_text == (
            "[teammate target 'p-5' coerced to SKIP] "
            "[rationale redacted by the vote guard; "
            "recorded reason: no confident read this round]"
        )
        assert coerced.rationale_text == (
            _marker_for("p-5") + TEAMMATE_COERCED_VOTE_RATIONALE
        )

    def test_no_fragment_of_the_original_rationale_survives(self) -> None:
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(), fellow_impostor_ids=("p-5",)
        )

        assert _OMNISCIENT_RATIONALE not in coerced.rationale_text
        # Word-level, not just the whole string: no salvaged clause either.
        for word in ("partner", "botched", "cafeteria", "loose", "crew"):
            assert word not in coerced.rationale_text.lower()

    @pytest.mark.parametrize(
        "rationale",
        [
            _OMNISCIENT_RATIONALE,
            "p-5 is the other impostor.",
            "I did the kill in electrical, p-5 covered for me.",
            "",
            "x" * 512,
        ],
    )
    def test_redaction_is_byte_identical_whatever_the_model_wrote(
        self, rationale: str
    ) -> None:
        # Nothing about the original leaks -- not its content, not its length,
        # not its shape. The recorded string is a function of the TARGET only.
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(rationale_text=rationale), fellow_impostor_ids=("p-5",)
        )

        assert coerced.rationale_text == (
            _marker_for("p-5") + TEAMMATE_COERCED_VOTE_RATIONALE
        )

    def test_redacted_body_carries_no_teammate_or_self_kill_phrasing(self) -> None:
        # Scanned on the BODY: the marker is the audit channel and legitimately
        # says "teammate target ..."; gating its DISPLAY is Task 19.11's.
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(), fellow_impostor_ids=("p-5",)
        )
        body = _body_of(coerced.rationale_text, target="p-5").lower()

        assert body
        for token in _OMNISCIENCE_TOKENS:
            assert token not in body, token
        # No player id either -- the redacted body names nobody.
        assert "p-" not in body

    def test_marker_survives_so_the_rewrite_stays_auditable(self) -> None:
        # Auditability is never laundered: the ORIGINAL teammate target is
        # still recoverable from the recorded ballot after the redaction, and
        # the stale reason id is still nulled (DESIGN.md §5.5; audit gp-3).
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(target="p-7"), fellow_impostor_ids=("p-7",)
        )

        assert coerced.rationale_text.startswith(_marker_for("p-7"))
        assert "'p-7'" in coerced.rationale_text
        assert coerced.primary_reason_id is None

    def test_spectator_surface_still_parses_the_chip_off_the_redacted_ballot(
        self,
    ) -> None:
        # The api projection strips markers front-to-back into chip labels
        # (``api.replay_loader._parse_rewrite_reasons``). The redaction sits
        # BEHIND the marker, so the chip still registers and the clean body a
        # spectator reads is the substitution note.
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(), fellow_impostor_ids=("p-5",)
        )

        reasons, clean = _parse_rewrite_reasons(coerced.rationale_text)

        assert reasons == ("teammate_coerced",)
        assert clean == TEAMMATE_COERCED_VOTE_RATIONALE


class TestUpstreamMarkersSurviveTheRedaction:
    """The redaction removes the model's body -- never another guard's marker.

    The ballot chain prepends the roster normalization and both citation-id
    validators BEFORE the teammate coercion, so a betrayal ballot that also
    carried a hallucinated reason / observation id arrives with their markers
    on the front. Replacing the whole rationale would drop them, silently
    un-counting nulled citations for every consumer that reads markers off the
    recorded string -- laundering one guard's audit trail through another's.
    """

    def _doubly_marked_ballot(self) -> VoteBallot:
        # Exactly the upstream chain, run for real rather than hand-spliced.
        ballot = _ballot(primary_reason_id="m-9:turn-99")
        ballot = ballot.model_copy(update={"primary_reason_observation_id": "p-4:1:1"})
        ballot = _normalize_ballot_reason_id(
            ballot=ballot,
            valid_reason_ids=frozenset({"m-1:turn-0"}),
            reason_id_by_ordinal={},
        )
        return _normalize_ballot_observation_id(
            ballot=ballot, valid_observation_ids=frozenset()
        )

    def test_nulled_citation_markers_are_preserved_in_place(self) -> None:
        marked = self._doubly_marked_ballot()
        assert INVALID_REASON_ID_MARKER.format(reason_id="m-9:turn-99") in (
            marked.rationale_text
        )

        coerced = coerce_teammate_ballot_to_skip(
            ballot=marked, fellow_impostor_ids=("p-5",)
        )

        # Same stack order the un-redacted guard produced: the teammate marker
        # in front, then the upstream markers, then the body.
        assert coerced.rationale_text == (
            _marker_for("p-5")
            + INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-4:1:1")
            + INVALID_REASON_ID_MARKER.format(reason_id="m-9:turn-99")
            + TEAMMATE_COERCED_VOTE_RATIONALE
        )
        assert _OMNISCIENT_RATIONALE not in coerced.rationale_text

    def test_every_chip_still_registers_on_the_spectator_surface(self) -> None:
        coerced = coerce_teammate_ballot_to_skip(
            ballot=self._doubly_marked_ballot(), fellow_impostor_ids=("p-5",)
        )

        reasons, clean = _parse_rewrite_reasons(coerced.rationale_text)

        assert reasons == (
            "teammate_coerced",
            "invalid_observation_id",
            "invalid_reason_id",
        )
        assert clean == TEAMMATE_COERCED_VOTE_RATIONALE

    def test_substring_marker_counts_still_see_the_nulled_citations(self) -> None:
        # ``eval.vj_instruments`` counts nulled citations by substring against
        # the recorded ``rationale_text``; the prefix (marker minus its
        # interpolated payload) is what ``eval.meeting_quality`` greps.
        coerced = coerce_teammate_ballot_to_skip(
            ballot=self._doubly_marked_ballot(), fellow_impostor_ids=("p-5",)
        )

        for marker in (INVALID_REASON_ID_MARKER, INVALID_OBSERVATION_ID_MARKER):
            prefix = marker.partition("{")[0]
            assert prefix in coerced.rationale_text, prefix

    def test_a_model_emitted_lookalike_marker_is_redacted_not_preserved(self) -> None:
        # The peel is gated on the field actually being nulled, so a model that
        # writes marker-shaped text of its own cannot smuggle a body past the
        # redaction: here ``primary_reason_id`` is still populated, so the
        # lookalike prefix is model output and goes with the rest of it.
        spoofed = _ballot(
            primary_reason_id="m-1:turn-0",
            rationale_text=(
                INVALID_REASON_ID_MARKER.format(reason_id="p-5 is my partner")
                + "and I did the kill."
            ),
        )

        coerced = coerce_teammate_ballot_to_skip(
            ballot=spoofed, fellow_impostor_ids=("p-5",)
        )

        assert coerced.rationale_text == (
            _marker_for("p-5") + TEAMMATE_COERCED_VOTE_RATIONALE
        )
        assert "partner" not in coerced.rationale_text.lower()


class TestRedactedBodyStaysOutOfTheVoiceFold:
    """The guard's prose is system text and must never be measured as a voice.

    ``eval.vj_instruments._normalize_voice`` strips leading ``[...]`` markers
    and folds whatever remains into the §2.5 echo / skeleton / distinct-n
    metrics. A parenthesized note (the ``DEFAULT_VOTE_RATIONALE`` shape) would
    survive that strip and feed the SAME guard-authored sentence into the
    model-voice diversity figures on every coerced ballot. The bracketed form
    is dropped with the markers.
    """

    def test_the_note_is_bracketed_system_text(self) -> None:
        assert TEAMMATE_COERCED_VOTE_RATIONALE.startswith("[")
        assert TEAMMATE_COERCED_VOTE_RATIONALE.endswith("]")
        # A bracketed marker's payload must not contain a nested "]", or the
        # evaluator's strip stops early and leaks a fragment into the fold.
        assert "]" not in TEAMMATE_COERCED_VOTE_RATIONALE[1:-1]

    def test_a_coerced_ballot_contributes_no_voice_tokens(self) -> None:
        coerced = coerce_teammate_ballot_to_skip(
            ballot=_ballot(), fellow_impostor_ids=("p-5",)
        )

        assert _strip_leading_markers(coerced.rationale_text) == ""

    def test_it_carries_no_marker_payload_so_registers_no_chip(self) -> None:
        # Bracketed but NOT a marker: no ``{...!r}`` payload, so the display
        # parse leaves it as the ballot's clean body rather than a chip.
        reasons, clean = _parse_rewrite_reasons(TEAMMATE_COERCED_VOTE_RATIONALE)

        assert reasons == ()
        assert clean == TEAMMATE_COERCED_VOTE_RATIONALE


class TestUncoercedBallotsKeepTheirRationale:
    def test_non_teammate_target_passes_through_untouched(self) -> None:
        ballot = _ballot(target="p-9", rationale_text="p-9 skipped the reactor task.")

        assert (
            coerce_teammate_ballot_to_skip(ballot=ballot, fellow_impostor_ids=("p-5",))
            is ballot
        )

    def test_sole_impostor_and_crewmate_pass_through_untouched(self) -> None:
        ballot = _ballot(rationale_text="p-5 skipped the reactor task.")

        assert (
            coerce_teammate_ballot_to_skip(ballot=ballot, fellow_impostor_ids=())
            is ballot
        )

    def test_skip_ballot_passes_through_untouched(self) -> None:
        ballot = _ballot(target="SKIP", rationale_text="nothing solid yet.")

        assert (
            coerce_teammate_ballot_to_skip(ballot=ballot, fellow_impostor_ids=("p-5",))
            is ballot
        )


# --- The production path ----------------------------------------------------


def _omniscient_responder(
    *, vote_targets: dict[str, str]
) -> Callable[[str, type[BaseModel] | None], str]:
    """Every voter emits the omniscient rationale, so only the guard can clean it."""

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            return VoteBallot(
                voter=voter,
                target=vote_targets.get(voter, "SKIP"),
                confidence=0.9,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text=_OMNISCIENT_RATIONALE,
            ).model_dump_json()
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder


class TestRedactionOnProductionPath:
    def _impostor_team(self) -> tuple[MeetingParticipant, ...]:
        # p-4 and p-5 are impostors and each other's teammate.
        return (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-5",)),
            _participant("p-5", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
        )

    def test_betrayal_ballot_records_the_marker_and_the_neutral_note(self) -> None:
        result, _ = _run_meeting(
            _omniscient_responder(vote_targets={"p-4": "p-5"}),
            participants=self._impostor_team(),
        )

        p4 = next(b for b in result.ballots if b.voter == "p-4")
        assert p4.target == "SKIP"
        assert p4.rationale_text == (
            _marker_for("p-5") + TEAMMATE_COERCED_VOTE_RATIONALE
        )
        assert _OMNISCIENT_RATIONALE not in p4.rationale_text

    def test_uncoerced_voters_keep_their_text_end_to_end(self) -> None:
        # The guard is surgical: only the coerced ballot is redacted. Every
        # other voter's rationale reaches the record verbatim -- this task
        # rewrites the guard's own output, never the model's elsewhere.
        result, _ = _run_meeting(
            _omniscient_responder(vote_targets={"p-4": "p-5"}),
            participants=self._impostor_team(),
        )

        for ballot in result.ballots:
            if ballot.voter == "p-4":
                continue
            assert ballot.rationale_text == _OMNISCIENT_RATIONALE
