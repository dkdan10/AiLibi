"""The grounding label, and the two guards ruling D6 of 2026-09-19 retired.

`tasks/work/grounded-skip-and-guard-labels.md`. Three things are asserted here,
and the third is the point of the card:

* every ballot the production chain records carries one
  :data:`~meetings.schemas.BallotGroundingLabel`, including a SKIP -- the class
  that carried no machine-checkable basis on 1,485 of the committed record's
  ballots;
* the label is written by the meeting layer and read by nobody who decides
  anything: :func:`meetings.voting.tally_ballots` takes no argument carrying it
  and its body never names it, so an ``uncited`` EJECT is tallied for the player
  the voter named;
* the RECORDED target is the AUTHORED target outside exactly three rewrite
  reasons, stated as a property over a generated family rather than as examples.

The planted cases are driven through :class:`meetings.manager.MeetingManager`
rather than against the labeller alone wherever the chain is what is under test,
because a label the production path never reaches is not a label the record
carries.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from dataclasses import replace
from pathlib import Path
from typing import Final

import pytest
from pydantic import BaseModel

from llm.client import LLMResponse, TokenUsage

from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_BASIS_MARKER,
    INVALID_REASON_ID_MARKER,
    OFF_TARGET_CITATION_EJECT_MARKER,
    TEAMMATE_COERCED_VOTE_RATIONALE,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    MeetingParticipant,
    label_ballot_grounding,
)
from meetings.schemas import (
    AlibiClaim,
    AlibiSegment,
    BallotGroundingLabel,
    Claim,
    ContradictionRef,
    MeetingResult,
    VoteBallot,
)
from meetings.voting import tally_ballots
from tests.meetings._manager_helpers import (
    _CallRecord,
    _default_trigger,
    _extract_marker,
    _make_manager,
    _participant,
    _run,
    _run_meeting,
    _turn_json,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: The observation the planted SKIPs cite. It is rendered into p-1's memory, so
#: the fake vote prompt carries it as a LINE -- which is the surface
#: ``cited_line_names`` reads, exactly as the shipped render does.
_OBS_ID = "p-1:4:0"
_OBS_LINE = f"[obs {_OBS_ID}] tick 4: p-3 left MEDBAY in a hurry."


def _memory_with_observation(agent_id: str) -> str:
    return f"## Your role: CREWMATE\n{agent_id} memory\n{_OBS_LINE}"


def _voter_p1(*, observation_ids: tuple[str, ...] = ()) -> MeetingParticipant:
    """p-1, carrying the rendered observation line and its typed id set."""

    return replace(
        _participant("p-1"),
        rendered_memory=_memory_with_observation("p-1"),
        observation_ids=observation_ids,
    )


def _roster(*, observation_ids: tuple[str, ...] = ()) -> tuple[MeetingParticipant, ...]:
    return (
        _voter_p1(observation_ids=observation_ids),
        _participant("p-2"),
        _participant("p-3"),
        _participant("p-4"),
    )


def _betrayal_roster() -> tuple[MeetingParticipant, ...]:
    """The same table with p-3 and p-4 on one impostor team.

    The one roster where a ballot reaches the teammate firewall, which is the
    only live guard that REPLACES a rationale rather than prefixing it.
    """

    return (
        _participant("p-1"),
        _participant("p-2"),
        _participant("p-3", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
        _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-3",)),
    )


def _ballot_payload(
    *,
    voter: str,
    target: str,
    confidence: float = 0.8,
    primary_reason_id: str | None = None,
    primary_reason_observation_id: str | None = None,
    considered_alternatives: tuple[str, ...] = (),
    decision_basis: str | None = None,
) -> str:
    """A raw vote payload, built as a dict so an INVALID basis can be planted.

    Deliberately not built through :class:`VoteBallot`: case 9 needs a
    ``decision_basis`` the schema would refuse, which is the whole point of the
    pre-pass that drops it.
    """

    payload: dict[str, object] = {
        "voter": voter,
        "target": target,
        "confidence": confidence,
        "primary_reason_id": primary_reason_id,
        "primary_reason_observation_id": primary_reason_observation_id,
        "considered_alternatives": list(considered_alternatives),
        "rationale_text": f"stub-vote-{voter}-{target}",
    }
    if decision_basis is not None:
        payload["decision_basis"] = decision_basis
    return json.dumps(payload)


def _responder(
    ballots: dict[str, dict[str, object]],
    *,
    accusations: dict[str, str | None] | None = None,
    claims_by: dict[str, tuple[Claim, ...]] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """Drive every turn to a bare opening and every vote off ``ballots``.

    A voter with no entry casts a bare SKIP, which is the shipped default shape
    and keeps each planted case to the one ballot it is about.

    ``accusations`` and ``claims_by`` are the turn-side knobs the flag cases
    need: a contradiction is DETECTED from the transcript, never injected, so
    the only way to reach ``flag_only`` through the production chain is to make
    two turns say incompatible things about one player.
    """

    accusations = accusations or {}
    claims_by = claims_by or {}

    def _respond(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            speaker = _extract_marker(prompt, "agent_id=")
            return _turn_json(
                speaker=speaker,
                accuses=accusations.get(speaker),
                claims=claims_by.get(speaker, ()),
            )
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            spec = dict(ballots.get(voter, {"target": "SKIP"}))
            spec.setdefault("target", "SKIP")
            return _ballot_payload(voter=voter, **spec)  # type: ignore[arg-type]
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _respond


#: The two turn bodies that make the transcript contradict itself about p-3:
#: one speaker puts p-3 in STORAGE across ticks 100-200, another in CAFETERIA
#: inside that window. ``detect_contradictions`` mints one ``alibi_conflict``
#: whose ``subjects`` is ``("p-3",)`` -- the flag ``flag_only`` reads.
_FLAG_ACCUSATIONS: Final[dict[str, str | None]] = {"p-1": "p-2", "p-2": None}
_FLAG_CLAIMS: Final[dict[str, tuple[Claim, ...]]] = {
    "p-1": (
        AlibiClaim(
            type="alibi",
            subject="p-3",
            route=(AlibiSegment(room="STORAGE", from_tick=100, to_tick=200),),
        ),
    ),
    "p-2": (
        AlibiClaim(
            type="alibi",
            subject="p-3",
            route=(AlibiSegment(room="CAFETERIA", from_tick=150, to_tick=180),),
        ),
    ),
}


@dataclass
class _UnvalidatingClient:
    """The scripted client, minus the schema validation.

    ``_ScriptedLLMClient`` validates every completion against the schema it was
    handed, exactly as the three shipped adapters do. That is the right default
    and the wrong harness for one thing: the pre-pass
    (``meetings.manager._prepared_ballot_payload``) exists for "a client that
    validates nothing", which is the same reason the guard-provenance strip
    beside it exists. Driving the manager with a client of that class is the
    only way to reach the pre-pass at all, so the planted case that needs it
    uses this one -- and
    ``test_a_validating_adapter_refuses_the_fabrication_first`` states, on the
    default client, what happens on the other path.
    """

    responder: Callable[[str, type[BaseModel] | None], str]
    calls: list[_CallRecord] = dataclass_field(default_factory=list)

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: str = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        text = self.responder(prompt, schema)
        self.calls.append(
            _CallRecord(
                prompt=prompt,
                schema_name=schema.__name__ if schema is not None else None,
                call_kind="meeting",
                agent_id=agent_id,
            )
        )
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "unvalidating-test",
        )


def _run_meeting_unvalidated(
    responder: Callable[[str, type[BaseModel] | None], str],
    *,
    participants: tuple[MeetingParticipant, ...],
    dead_ids: tuple[str, ...] = (),
) -> tuple[MeetingResult, _UnvalidatingClient]:
    client = _UnvalidatingClient(responder=responder)
    manager = _make_manager(llm_client=client)
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=_default_trigger(),
            participants=participants,
            dead_ids=dead_ids,
        )
    )
    return result, client


def _p1(result: MeetingResult) -> VoteBallot:
    return next(ballot for ballot in result.ballots if ballot.voter == "p-1")


class TestEveryBallotDeclaresItsBasis:
    """The nine planted cases, one per label plus the fabricated basis.

    Each runs the REAL chain: the manager parses a raw payload, the two citation
    validators run, and the labeller writes the field onto the recorded ballot.
    """

    def test_a_skip_citing_a_weighed_alternative_is_supported(self) -> None:
        # Case 1. The SKIP the card exists to make possible: it cites its own
        # observation, that observation names p-3, and p-3 is one of the two
        # players this voter wrote down as weighed.
        result, _ = _run_meeting(
            _responder(
                {
                    "p-1": {
                        "target": "SKIP",
                        "primary_reason_observation_id": _OBS_ID,
                        "considered_alternatives": ("p-3", "p-4"),
                        "decision_basis": "cited",
                    }
                }
            ),
            participants=_roster(observation_ids=(_OBS_ID,)),
        )

        ballot = _p1(result)
        assert ballot.grounding_label == "supported"
        assert ballot.decision_basis == "cited"
        assert ballot.target == "SKIP"

    def test_the_same_citation_about_nobody_weighed_is_off_target(self) -> None:
        # Case 2. One byte of the ballot moves -- the weighed list -- and the
        # label flips, which is what makes it a statement about ABOUTNESS rather
        # than about citation presence.
        result, _ = _run_meeting(
            _responder(
                {
                    "p-1": {
                        "target": "SKIP",
                        "primary_reason_observation_id": _OBS_ID,
                        "considered_alternatives": ("p-2", "p-4"),
                        "decision_basis": "cited",
                    }
                }
            ),
            participants=_roster(observation_ids=(_OBS_ID,)),
        )

        assert _p1(result).grounding_label == "off_target"

    def test_a_fabricated_turn_id_is_invalid_citation(self) -> None:
        # Case 3. The voter reached for evidence and missed: the validator nulls
        # the id with its own marker, and the label says which of the two
        # no-citation records this is.
        result, _ = _run_meeting(
            _responder(
                {
                    "p-1": {
                        "target": "SKIP",
                        "primary_reason_id": "m-1:turn-77",
                        "decision_basis": "cited",
                    }
                }
            ),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.grounding_label == "invalid_citation"
        assert ballot.primary_reason_id is None
        assert ballot.rationale_text.startswith(
            INVALID_REASON_ID_MARKER.format(reason_id="m-1:turn-77")
        )

    def test_a_declared_none_held_is_none_held(self) -> None:
        # Case 4. The voter's own word, carried onto the record.
        result, _ = _run_meeting(
            _responder({"p-1": {"target": "SKIP", "decision_basis": "none_held"}}),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.grounding_label == "none_held"
        assert ballot.decision_basis == "none_held"

    def test_a_bare_skip_is_uncited(self) -> None:
        # Case 5. And the distinction the card turns on: answering nothing is a
        # different record from saying you hold nothing.
        result, _ = _run_meeting(
            _responder({"p-1": {"target": "SKIP"}}), participants=_roster()
        )

        ballot = _p1(result)
        assert ballot.grounding_label == "uncited"
        assert ballot.decision_basis is None

    def test_a_ballot_naming_a_dead_player_is_not_assessed_and_tallies_as_skip(
        self,
    ) -> None:
        # Case 6. p-5 was ejected in an earlier meeting, so it is not a living
        # candidate. The rewrite is one a tally cannot do without, the recorded
        # target is the layer's, and the label refuses to assess a decision the
        # voter's own ballot no longer carries.
        result, _ = _run_meeting(
            _responder({"p-1": {"target": "p-5", "primary_reason_id": "m-1:turn-0"}}),
            participants=_roster(),
            dead_ids=("p-5",),
        )

        ballot = _p1(result)
        assert ballot.grounding_label == "not_assessed"
        assert ballot.target == "SKIP"
        assert ballot.guard_rewrite_reason == "invalid_target"
        assert ballot.guard_redirected_from == "p-5"
        assert tally_ballots([ballot], skip_confidence_threshold=0.6) == (
            "SKIPPED",
            None,
        )

    def test_an_uncited_eject_onto_a_flagged_target_is_flag_only_and_ejects(
        self,
    ) -> None:
        # Case 7, half of the tally ruling. `main` coerced this ballot to SKIP.
        flag = ContradictionRef(
            contradiction_id="c-1",
            kind="alibi_vs_sighting",
            subjects=("p-3",),
            event_a_id="m-1:turn-0",
            event_b_id="m-1:turn-1",
            description="their account does not match what two of us saw",
        )
        ballot = VoteBallot(
            voter="p-1",
            target="p-3",
            confidence=0.8,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="they are lying.",
        )

        labelled = label_ballot_grounding(
            ballot=ballot, contradictions=(flag,), candidate_targets=("p-2", "p-3")
        )

        assert labelled.grounding_label == "flag_only"
        assert labelled.target == "p-3"
        assert tally_ballots([labelled], skip_confidence_threshold=0.6) == (
            "EJECTED",
            "p-3",
        )

    def test_an_uncited_eject_onto_an_unflagged_target_is_uncited_and_ejects(
        self,
    ) -> None:
        # Case 8, the other half, and the one `main` coerced on 6 committed
        # ballots. Same vote, no flag, and it still counts for p-3.
        ballot = VoteBallot(
            voter="p-1",
            target="p-3",
            confidence=0.8,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="they are lying.",
        )

        labelled = label_ballot_grounding(
            ballot=ballot, contradictions=(), candidate_targets=("p-2", "p-3")
        )

        assert labelled.grounding_label == "uncited"
        assert labelled.target == "p-3"
        assert tally_ballots([labelled], skip_confidence_threshold=0.6) == (
            "EJECTED",
            "p-3",
        )

    def test_a_declared_none_held_outranks_a_flag_on_the_target(self) -> None:
        # Case 10, review round 2: the one ordering the precedence list calls
        # deliberate, and the only pair of branches whose ORDER is a ruling
        # rather than an arithmetic necessity. A voter that says it holds
        # nothing must not be upgraded by the layer reading a flag on its
        # behalf, so `none_held` sits ABOVE `flag_only` -- swap the two branches
        # and this case reads `flag_only`. Driven through the manager chain
        # because the flag has to be DETECTED from the transcript for the
        # ordering to be exercised where it ships.
        result, _ = _run_meeting(
            _responder(
                {"p-1": {"target": "p-3", "decision_basis": "none_held"}},
                accusations=_FLAG_ACCUSATIONS,
                claims_by=_FLAG_CLAIMS,
            ),
            participants=_roster(),
        )

        # The flag the layer could have upgraded this ballot with is real, was
        # minted this meeting, and names this ballot's target.
        assert [flag.subjects for flag in result.contradictions] == [("p-3",)]
        ballot = _p1(result)
        assert ballot.target == "p-3"
        assert ballot.decision_basis == "none_held"
        assert ballot.grounding_label == "none_held"

        # Non-vacuous: the SAME meeting with the SAME flag, minus the voter's
        # own word, is the `flag_only` half. Without this half the assertion
        # above would also pass on a build that never reached `flag_only`.
        flagged, _ = _run_meeting(
            _responder(
                {"p-1": {"target": "p-3"}},
                accusations=_FLAG_ACCUSATIONS,
                claims_by=_FLAG_CLAIMS,
            ),
            participants=_roster(),
        )
        assert [flag.subjects for flag in flagged.contradictions] == [("p-3",)]
        assert _p1(flagged).grounding_label == "flag_only"

    def test_an_uncited_eject_survives_the_whole_production_chain(self) -> None:
        # The same ruling at the chokepoint rather than on the pure function:
        # the recorded ballot is an EJECT and the meeting ejects off it.
        result, _ = _run_meeting(
            _responder({voter: {"target": "p-3"} for voter in ("p-1", "p-2", "p-4")}),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.target == "p-3"
        assert ballot.grounding_label == "uncited"
        assert ballot.guard_rewrite_reason is None
        assert UNCITED_ZERO_FLAG_EJECT_MARKER.split("{")[0] not in ballot.rationale_text
        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_an_out_of_set_basis_is_stripped_marked_and_never_defaults_the_vote(
        self,
    ) -> None:
        # Case 9. `extra="forbid"` would have refused the value and degraded the
        # WHOLE vote to the parse default; the pre-pass drops it so the
        # fabrication costs the voter its declared basis and nothing else.
        result, client = _run_meeting_unvalidated(
            _responder(
                {"p-1": {"target": "SKIP", "decision_basis": "absolutely certain"}}
            ),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.decision_basis is None
        assert ballot.grounding_label == "uncited"
        assert ballot.guard_rewrite_reason is None
        assert ballot.rationale_text.startswith(
            INVALID_BASIS_MARKER.format(basis="absolutely certain")
        )
        # Not defaulted: the model's own sentence is still on the record behind
        # the marker, and no parse failure was surfaced.
        assert ballot.rationale_text.endswith("stub-vote-p-1-SKIP")
        assert client.calls

    def test_a_validating_adapter_refuses_the_fabrication_first(self) -> None:
        # The limit of the case above, stated rather than left to be found. The
        # three shipped adapters validate a completion against the AUTHORED
        # schema before returning it, and `_FrozenModel` is `extra="forbid"`,
        # so on those clients an out-of-set basis never reaches the pre-pass:
        # it is a schema violation like any other and takes the existing
        # provider-level retry, then the parse default. Exactly the same limit
        # the guard-provenance strip beside it has had since it shipped.
        result, _ = _run_meeting(
            _responder(
                {"p-1": {"target": "SKIP", "decision_basis": "absolutely certain"}}
            ),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.guard_rewrite_reason == "parse_default"
        assert ballot.grounding_label == "not_assessed"

    def test_a_fabricated_basis_survives_the_teammate_redaction(self) -> None:
        # The provenance boundary, planted. `_collect_vote` reads the model's
        # body into `authored_rationale_text` BEFORE prepending
        # `INVALID_BASIS_MARKER`, and `_preserved_ballot_markers` keeps exactly
        # what precedes that body. Take the boundary one line later and the
        # marker falls on the MODEL side of the split: the teammate coercion
        # then redacts it away with the body, and the fabrication is uncounted
        # for every marker consumer -- on precisely the ballots the firewall
        # also touched. Nothing else in the suite pins that ordering.
        result, _ = _run_meeting_unvalidated(
            _responder(
                {"p-3": {"target": "p-4", "decision_basis": "absolutely certain"}}
            ),
            participants=_betrayal_roster(),
        )

        ballot = next(b for b in result.ballots if b.voter == "p-3")
        assert ballot.target == "SKIP"
        assert ballot.guard_rewrite_reason == "teammate_coerced"
        assert ballot.guard_redirected_from == "p-4"
        assert ballot.decision_basis is None
        # The marker survives as a CLASS with its payload redacted -- the model
        # chose that payload, so it is untrusted text like the body.
        assert ballot.rationale_text == (
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-4")
            + INVALID_BASIS_MARKER.format(basis="(redacted)")
            + TEAMMATE_COERCED_VOTE_RATIONALE
        )
        assert "stub-vote-p-3-p-4" not in ballot.rationale_text
        assert ballot.grounding_label == "not_assessed"

        # Non-vacuous: the same betrayal without a fabricated basis records the
        # teammate marker alone, so the assertion above is about THIS marker.
        clean, _ = _run_meeting_unvalidated(
            _responder({"p-3": {"target": "p-4"}}),
            participants=_betrayal_roster(),
        )
        assert next(b for b in clean.ballots if b.voter == "p-3").rationale_text == (
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-4")
            + TEAMMATE_COERCED_VOTE_RATIONALE
        )

    @pytest.mark.parametrize(
        "basis", [123, ["cited"], {"basis": "cited"}, "CITED", " none_held"]
    )
    def test_every_out_of_set_shape_is_dropped_rather_than_refused(
        self, basis: object
    ) -> None:
        # Case, whitespace and type are all significant, and none of them may
        # reach the schema: the closed set is exact.
        result, _ = _run_meeting_unvalidated(
            _responder({"p-1": {"target": "SKIP", "decision_basis": basis}}),
            participants=_roster(),
        )

        ballot = _p1(result)
        assert ballot.decision_basis is None
        assert ballot.guard_rewrite_reason is None
        assert ballot.rationale_text.startswith(INVALID_BASIS_MARKER.split("{")[0])


class TestEveryRecordedBallotIsLabelled:
    """The property, over a generated family rather than over examples."""

    _SPECS: tuple[dict[str, object], ...] = (
        {"target": "SKIP"},
        {"target": "SKIP", "decision_basis": "none_held"},
        {"target": "SKIP", "primary_reason_id": "m-1:turn-0"},
        {"target": "SKIP", "primary_reason_id": "m-1:turn-99"},
        {"target": "SKIP", "primary_reason_observation_id": _OBS_ID},
        {"target": "SKIP", "decision_basis": "fabricated"},
        {"target": "p-3"},
        {"target": "p-3", "primary_reason_id": "m-1:turn-0"},
        {"target": "p-3", "primary_reason_observation_id": _OBS_ID},
        {"target": "p-9"},
    )

    def _family(self) -> tuple[VoteBallot, ...]:
        recorded: list[VoteBallot] = []
        for spec in self._SPECS:
            result, _ = _run_meeting_unvalidated(
                _responder({"p-1": dict(spec)}),
                participants=_roster(observation_ids=(_OBS_ID,)),
            )
            recorded.append(_p1(result))
        return tuple(recorded)

    def test_every_ballot_in_the_family_carries_a_label(self) -> None:
        labels = {ballot.grounding_label for ballot in self._family()}

        assert None not in labels
        assert labels <= set(BallotGroundingLabel.__args__)  # type: ignore[attr-defined]

    def test_the_recorded_target_is_the_authored_one_outside_three_reasons(
        self,
    ) -> None:
        # The card's whole-chain assertion, as a PROPERTY: for every ballot in
        # the family, the recorded target equals the authored one unless the
        # layer says which of the three rewrites moved it.
        authored = {
            spec_index: str(spec["target"])
            for spec_index, spec in enumerate(self._SPECS)
        }
        moved = 0
        for index, ballot in enumerate(self._family()):
            if ballot.guard_rewrite_reason is None:
                assert ballot.target == authored[index], authored[index]
                assert ballot.guard_redirected_from is None
                continue
            moved += 1
            assert ballot.guard_rewrite_reason in {
                "invalid_target",
                "teammate_coerced",
                "parse_default",
            }
            assert ballot.guard_redirected_from == authored[index]
        # Non-vacuous on both sides: the family holds the one illegal target.
        assert moved == 1

    def test_a_label_never_moves_a_target(self) -> None:
        # The labeller in isolation, over the same family: strip the field and
        # the ballot is the one it was handed, byte for byte.
        for ballot in self._family():
            relabelled = label_ballot_grounding(
                ballot=ballot, contradictions=(), candidate_targets=("p-2", "p-3")
            )
            assert (
                relabelled.model_copy(
                    update={"grounding_label": ballot.grounding_label}
                )
                == ballot
            )


class TestTheTallyNeverReadsTheLabel:
    """Ruling D6, asserted on the tally itself rather than on its callers."""

    def _ballots(self, label: BallotGroundingLabel | None) -> tuple[VoteBallot, ...]:
        return tuple(
            VoteBallot(
                voter=voter,
                target="p-3",
                confidence=0.8,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="body",
                grounding_label=label,
            )
            for voter in ("p-1", "p-2")
        )

    @pytest.mark.parametrize(
        "label",
        [None, *BallotGroundingLabel.__args__],  # type: ignore[attr-defined]
    )
    def test_the_outcome_is_the_same_under_every_label(
        self, label: BallotGroundingLabel | None
    ) -> None:
        assert tally_ballots(self._ballots(label), skip_confidence_threshold=0.6) == (
            "EJECTED",
            "p-3",
        )

    def test_the_tally_takes_no_label_argument_and_names_no_label(self) -> None:
        # Structural, so it cannot be satisfied by a body that happens to agree
        # today: the source of `tally_ballots` mentions neither the field nor any
        # of its values.
        source = ast.parse((_REPO_ROOT / "meetings" / "voting.py").read_text())
        function = next(
            node
            for node in ast.walk(source)
            if isinstance(node, ast.FunctionDef) and node.name == "tally_ballots"
        )
        body = ast.unparse(ast.Module(body=function.body[1:], type_ignores=[]))

        assert "grounding_label" not in body
        for value in BallotGroundingLabel.__args__:  # type: ignore[attr-defined]
            assert value not in body


class TestTheRetiredGuardsMintNothing:
    """The three markers are read-only history, and the source says so."""

    #: Every package a meeting can run through. `experiments/` and `tests/` are
    #: excluded on purpose: the instrument reads recorded bytes and the tests
    #: assert about them, neither is a path a recording takes.
    _LIVE_PACKAGES = ("agents", "api", "eval", "meetings", "orchestrator", "training")

    _RETIRED = (
        "BALLOT_TARGET_REDIRECT_MARKER",
        "UNCITED_ZERO_FLAG_EJECT_MARKER",
        "OFF_TARGET_CITATION_EJECT_MARKER",
    )

    def _minting_sites(self, marker: str) -> list[str]:
        """Every ``<MARKER>.format(...)`` call under a live package.

        Minting is what ``.format()`` IS for these constants: each interpolates
        the authored target into a prefix. A module that merely NAMES the
        constant is registering it for a reader, which is the whole point of
        keeping them.
        """

        sites: list[str] = []
        for package in self._LIVE_PACKAGES:
            for path in sorted((_REPO_ROOT / package).rglob("*.py")):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    if not isinstance(func, ast.Attribute) or func.attr != "format":
                        continue
                    value = func.value
                    if isinstance(value, ast.Name) and value.id == marker:
                        sites.append(f"{path.relative_to(_REPO_ROOT)}:{node.lineno}")
        return sites

    @pytest.mark.parametrize("marker", _RETIRED)
    def test_no_live_path_mints_the_marker(self, marker: str) -> None:
        assert self._minting_sites(marker) == []

    def test_the_scan_finds_a_marker_that_is_minted(self) -> None:
        # The gate can fail: the same scan over a marker the chain DOES still
        # mint returns its call site, so an empty result above is a fact about
        # the tree and not about the scanner.
        assert self._minting_sites("INVALID_REASON_ID_MARKER") != []

    @pytest.mark.parametrize("marker", _RETIRED)
    def test_the_literals_survive_for_the_readers(self, marker: str) -> None:
        # Retired is not deleted: 83 committed ballots carry the redirect and 6
        # carry the uncited coercion, and four consumers parse those bytes.
        literal = {
            "BALLOT_TARGET_REDIRECT_MARKER": BALLOT_TARGET_REDIRECT_MARKER,
            "UNCITED_ZERO_FLAG_EJECT_MARKER": UNCITED_ZERO_FLAG_EJECT_MARKER,
            "OFF_TARGET_CITATION_EJECT_MARKER": OFF_TARGET_CITATION_EJECT_MARKER,
        }[marker]

        assert "{target!r}" in literal

    def test_the_retired_guards_are_gone_from_the_manager(self) -> None:
        import meetings.manager as manager

        assert not hasattr(manager, "guard_ballot_target_graph")
        assert not hasattr(manager, "guard_ballot_citation")


class TestTheOnlyTargetRewrites:
    """Three paths move a ballot's target, and the source names all three."""

    def test_only_three_reasons_are_reachable_from_a_live_path(self) -> None:
        # ``ballot_target_rewrite_provenance`` is the ONE writer of the typed
        # pair, so every reason a live path can record is a literal handed to
        # it. Scanning the call sites is what makes this a statement about the
        # code rather than about the three examples a test happens to build.
        reasons: set[str] = set()
        for package in ("agents", "api", "eval", "meetings", "orchestrator"):
            for path in sorted((_REPO_ROOT / package).rglob("*.py")):
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    name = getattr(func, "id", None) or getattr(func, "attr", None)
                    if name != "ballot_target_rewrite_provenance":
                        continue
                    for argument in node.args:
                        if isinstance(argument, ast.Constant) and isinstance(
                            argument.value, str
                        ):
                            reasons.add(argument.value)

        assert reasons == {"invalid_target", "teammate_coerced"}

    def test_the_parse_default_is_the_third_and_writes_the_field_directly(
        self,
    ) -> None:
        from meetings.manager import _vote_parse_default

        degraded = _vote_parse_default(voter="p-1", raw_response="{not json")

        assert degraded.guard_rewrite_reason == "parse_default"
        assert degraded.guard_redirected_from is None
        assert degraded.grounding_label == "not_assessed"
