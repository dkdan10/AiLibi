"""The ballot's weighing channel: evidence rows and ``counter_reason_id``.

Ruling D5 of 2026-09-19 (``tasks/direction-2026-09-19-process-over-outcome.md``
§4, §7, §12). Three things are under test here and nothing else:

* the typed :class:`~meetings.render_contract.EvidenceRow` rows
  :func:`meetings.manager.build_evidence_rows` assembles -- where they come
  from, what they may cite, how they are ordered and bounded, and that they are
  built from THIS voter's channels alone;
* the served ``qwen3_6_27b`` v8 ballot body -- the evidence block above the
  suspicion number, the deleted deference sentence, the dropped trust column,
  and the ninth contract key;
* ``counter_reason_id`` end to end -- validated by the SAME two decisions as the
  primary slots, nulled with its own registered marker, and a gate over
  NOTHING: it never moves a target, a tally or a ``grounding_label``.

Every property that is stated as universal is driven over a GENERATED family
through the real :class:`~meetings.manager.MeetingManager`, not over one
example; the committed-bytes leg reads recorded transcripts count-only and
prints no rendered prompt.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, Final

import pytest
from pydantic import BaseModel

from agents.strategic.prompts.loader import build_prompt_renderers
from api.replay_loader import _BALLOT_PREFIX_MARKERS
from eval.deduction_metrics import _BALLOT_MARKER_CHAIN, _marker_pattern
from meetings.corroboration import build_testimony_ledger
from meetings.manager import (
    INVALID_COUNTER_REASON_MARKER,
    MAX_EVIDENCE_ROWS_PER_SUBJECT,
    MeetingParticipant,
    SuspicionEntry,
    _EVIDENCE_KIND_CLASS,
    build_evidence_rows,
)
from meetings.render_contract import BodyDiscoveryRecord, EvidenceRow
from meetings.schemas import (
    MARKER_QUOTED_ORIGINAL_MAX_CHARS,
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    SawPlayerObservation,
    SightingRecord,
    VentWitnessRecord,
    VoteBallot,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from tests.meetings._manager_helpers import (
    _extract_marker,
    _participant,
    _run_meeting,
    _turn_json,
)

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_SERVED_SET: Final[str] = "qwen3_6_27b"
_DEFERENCE_SENTENCE: Final[str] = (
    "Your suspicion levels above are your own accumulated evidence from the "
    "whole game — trust them over meeting rhetoric."
)


# --------------------------------------------------------------------------- #
# Fixtures: a four-player meeting whose voters hold real typed channels        #
# --------------------------------------------------------------------------- #


def _voter(
    agent_id: str,
    *,
    sightings: tuple[SightingRecord, ...] = (),
    vents: tuple[VentWitnessRecord, ...] = (),
    moves: tuple[MoveWitnessRecord, ...] = (),
    bodies: tuple[BodyDiscoveryRecord, ...] = (),
    observation_ids: tuple[str, ...] = (),
) -> MeetingParticipant:
    """One living crewmate carrying the four own-perception channels."""

    return replace(
        _participant(agent_id),
        sighting_records=sightings,
        vent_witness_records=vents,
        move_witness_records=moves,
        body_discovery_records=bodies,
        observation_ids=observation_ids,
        suspicion_graph=(SuspicionEntry(player_id="p-2", suspicion=0.7, trust=0.5),),
    )


def _channel_voters() -> tuple[MeetingParticipant, ...]:
    """Four voters; p-1 holds one row in each of its four own channels."""

    return (
        _voter(
            "p-1",
            sightings=(
                SightingRecord(
                    subject="p-2",
                    room="MEDBAY",
                    tick=11,
                    co_present=("p-3",),
                    observation_id="p-1:11:0",
                ),
            ),
            vents=(
                VentWitnessRecord(
                    subject="p-2",
                    room="ENGINEERING",
                    tick=12,
                    observation_id="p-1:12:0",
                ),
            ),
            moves=(
                MoveWitnessRecord(
                    subject="p-3",
                    from_room="ADMIN",
                    to_room="CAFETERIA",
                    tick=13,
                    observation_id="p-1:13:0",
                ),
            ),
            bodies=(
                BodyDiscoveryRecord(
                    victim_id="p-9",
                    room="REACTOR",
                    tick=14,
                    observation_id="p-1:14:0",
                ),
            ),
            observation_ids=("p-1:11:0", "p-1:12:0", "p-1:13:0", "p-1:14:0"),
        ),
        _voter("p-2"),
        _voter("p-3"),
        _voter("p-4"),
    )


def _capturing_vote_prompt() -> tuple[
    dict[str, tuple[EvidenceRow, ...]], Callable[..., str]
]:
    """A vote renderer that records the rows it was threaded, per voter."""

    captured: dict[str, tuple[EvidenceRow, ...]] = {}

    def _prompt(
        *,
        voter_id: str,
        rendered_memory: str,
        transcript: MeetingTranscript,
        contradiction_flags: Any,
        suspicion_graph: Any,
        candidate_targets: tuple[str, ...],
        skip_confidence_threshold: float,
        evidence_rows: tuple[EvidenceRow, ...] = (),
        **_: Any,
    ) -> str:
        captured[voter_id] = evidence_rows
        return (
            "PHASE=VOTE\n"
            f"voter={voter_id}\n"
            f"candidates={','.join(candidate_targets)}\n"
            f"TURNS_COUNT={len(transcript.turns)}\n"
        )

    return captured, _prompt


def _vote_responder(
    *,
    targets: Mapping[str, str] | None = None,
    counters: Mapping[str, str | None] | None = None,
    reason_ids: Mapping[str, str | None] | None = None,
    accusations: Mapping[str, str] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """Turns accuse as scripted; ballots carry the scripted counter citation."""

    resolved_targets = dict(targets or {})
    resolved_counters = dict(counters or {})
    resolved_reasons = dict(reason_ids or {})
    resolved_accusations = dict(accusations or {})

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            speaker = _extract_marker(prompt, "agent_id=")
            return _turn_json(
                speaker=speaker, accuses=resolved_accusations.get(speaker)
            )
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            return VoteBallot(
                voter=voter,
                target=resolved_targets.get(voter, "SKIP"),
                confidence=0.8,
                primary_reason_id=resolved_reasons.get(voter),
                counter_reason_id=resolved_counters.get(voter),
                considered_alternatives=(),
                rationale_text=f"stub-vote-{voter}",
            ).model_dump_json()
        raise AssertionError("unrecognised prompt")

    return _responder


# --------------------------------------------------------------------------- #
# A. What a row may cite                                                       #
# --------------------------------------------------------------------------- #


def _citation_violations(
    rows: Sequence[EvidenceRow],
    *,
    turn_ids: frozenset[str],
    observation_ids: frozenset[str],
) -> list[EvidenceRow]:
    """Rows whose ``citation_id`` is neither a turn here nor this voter's own.

    The one definition the card's invariant is stated in, used by BOTH the
    positive assertion and the planted perturbation below, so the two cannot
    disagree about what "citable" means.
    """

    return [
        row
        for row in rows
        if row.citation_id is not None
        and row.citation_id not in turn_ids
        and row.citation_id not in observation_ids
    ]


class TestEveryCitationResolves:
    def test_rows_cite_only_this_meeting_or_this_voters_own_memory(self) -> None:
        """Every ``citation_id`` resolves in one of exactly two id sets.

        Driven through the real manager, so the rows under test are the ones a
        served ballot would actually carry.
        """

        captured, prompt = _capturing_vote_prompt()
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-2"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        turn_ids = frozenset(turn.turn_id for turn in result.transcript.turns)

        assert captured["p-1"], "the channel-holding voter must have rows"
        for participant in _channel_voters():
            rows = captured[participant.agent_id]
            assert (
                _citation_violations(
                    rows,
                    turn_ids=turn_ids,
                    observation_ids=frozenset(participant.observation_ids),
                )
                == []
            )

    def test_a_row_built_from_another_participants_channel_is_caught(self) -> None:
        """PLANTED: p-1's rows assembled onto p-2 violate the invariant.

        The defect this gate exists for is an assembler that reads a channel
        belonging to somebody else -- which would hand a voter an id it cannot
        cite and, worse, evidence it never perceived. Built by calling the real
        assembler with p-1's records and then checking the rows against p-2's
        own id set: every own-channel citation is out of set, so the invariant
        reports violations rather than passing.
        """

        voters = _channel_voters()
        transcript = MeetingTranscript(turns=())
        rows = build_evidence_rows(
            voter=voters[0],
            candidate_targets=("p-2", "p-3", "p-4"),
            contradictions=(),
            transcript=transcript,
        )

        violations = _citation_violations(
            rows,
            turn_ids=frozenset(),
            observation_ids=frozenset(voters[1].observation_ids),
        )
        assert len(violations) == 4, violations
        # ...and the same rows against their REAL owner are clean, so the check
        # is not vacuously red.
        assert (
            _citation_violations(
                rows,
                turn_ids=frozenset(),
                observation_ids=frozenset(voters[0].observation_ids),
            )
            == []
        )

    def test_the_invariant_holds_over_committed_meeting_transcripts(self) -> None:
        """The same invariant over recorded bytes, count-only.

        The committed recordings predate the evidence rows, so the rows cannot
        be read off them -- they are minted at render time. What the committed
        bytes DO supply is the half that mints turn-id citations: real
        transcripts and real detector flags. Those are fed to the real
        assembler with a voter whose own channels are the recorded ballots'
        voters, and every citation must still resolve. Counts only: no rendered
        prompt and no seed prefix is printed.
        """

        path = _REPO_ROOT / "replays" / "samples" / "9p2i" / "replay-seed-0.jsonl"
        meetings = [
            entry
            for entry in read_all_entries(path)
            if isinstance(entry, MeetingReplayEntry)
        ]
        assert meetings, "the committed seed must carry at least one meeting"

        checked = 0
        rows_seen = 0
        for entry in meetings:
            turn_ids = frozenset(turn.turn_id for turn in entry.transcript.turns)
            voters = sorted({ballot.voter for ballot in entry.ballots})
            targets = tuple(voters)
            for voter_id in voters:
                participant = _voter(voter_id)
                rows = build_evidence_rows(
                    voter=participant,
                    candidate_targets=tuple(t for t in targets if t != voter_id),
                    contradictions=entry.contradictions,
                    transcript=entry.transcript,
                    testimony_ledger=build_testimony_ledger(
                        entry.transcript,
                        contradictions=entry.contradictions,
                        sighting_records={},
                        move_witness_records={},
                        opener=entry.triggered_by,
                        roster=frozenset(voters),
                        trigger_kind="report",
                    ),
                )
                assert (
                    _citation_violations(
                        rows, turn_ids=turn_ids, observation_ids=frozenset()
                    )
                    == []
                )
                checked += 1
                rows_seen += len(rows)
        assert checked > 0 and rows_seen > 0, (checked, rows_seen)


# --------------------------------------------------------------------------- #
# B. Order, bound, and provenance of the rows                                  #
# --------------------------------------------------------------------------- #


class TestRowOrderAndBound:
    def test_the_stated_order_holds_under_every_adjacent_swap(self) -> None:
        """Swapping any adjacent pair breaks the order the docstring states.

        The order is a claim about a TOTAL key, so the way to test it is to
        show no adjacent pair may be exchanged: for every consecutive (a, b),
        the key of a sorts strictly before the key of b.
        """

        captured, prompt = _capturing_vote_prompt()
        _run_meeting(
            _vote_responder(accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-2"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        rows = captured["p-1"]
        assert len(rows) >= 3, rows

        targets = ("p-2", "p-3", "p-4")
        rank = {subject: index for index, subject in enumerate(targets)}

        def _key(row: EvidenceRow) -> tuple[int, int, int]:
            return (
                rank.get(row.subject, len(targets)),
                0 if row.first_hand else 1,
                _EVIDENCE_KIND_CLASS[row.kind],
            )

        for left, right in zip(rows, rows[1:]):
            assert _key(left) <= _key(right), (left, right)

    def test_each_subject_and_class_is_bounded(self) -> None:
        """An over-budget group keeps the LATEST rows and drops the earliest.

        Bounding is a page rule, not an evidence rule, so what is pinned is the
        count per (subject, class) and WHICH rows survive -- by position, never
        by content.
        """

        many = tuple(
            SightingRecord(
                subject="p-2",
                room="MEDBAY",
                tick=tick,
                observation_id=f"p-1:{tick}:0",
            )
            for tick in range(MAX_EVIDENCE_ROWS_PER_SUBJECT + 3)
        )
        voter = replace(
            _voter("p-1", observation_ids=tuple(r.observation_id or "" for r in many)),
            sighting_records=many,
        )

        rows = build_evidence_rows(
            voter=voter,
            candidate_targets=("p-2",),
            contradictions=(),
            transcript=MeetingTranscript(turns=()),
        )

        assert len(rows) == MAX_EVIDENCE_ROWS_PER_SUBJECT
        kept_ticks = [int(row.citation_id.split(":")[1]) for row in rows]  # type: ignore[union-attr]
        assert kept_ticks == sorted(kept_ticks)
        assert kept_ticks[0] == 3, kept_ticks  # the three earliest went

    def test_the_budget_drops_by_arrival_time_not_by_render_position(self) -> None:
        """An over-budget TESTIMONY group loses its earliest voices, not its
        grounded ones.

        The render puts first-hand rows first inside a class, so a budget taken
        off the front of the RENDER order would drop the grounded voices first
        -- a bound deciding by what a row says, which is the one thing it must
        never do. Built so the two rules disagree: nine voices against p-3, and
        the LAST one to speak is the only grounded one. Under the arrival rule
        it survives and the earliest voice goes; under the render rule it would
        be the first thing dropped.
        """

        speakers = [f"p-{index}" for index in range(10, 19)]
        grounded_speaker = speakers[-1]

        def _voice(index: int, speaker: str) -> MeetingTurn:
            return MeetingTurn(
                turn_id=f"m-1:turn-{index}",
                turn_index=index,
                speaker=speaker,
                turn_kind="opening" if index == 0 else "reply",
                reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
                observations=(
                    (
                        SawPlayerObservation(
                            type="saw_player", tick=5, subject="p-3", room="MEDBAY"
                        ),
                    )
                    if speaker == grounded_speaker
                    else ()
                ),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-3",
                        confidence=0.6,
                        reason=f"{speaker} accuses p-3",
                    ),
                ),
                free_text="p-3 did it.",
            )

        transcript = MeetingTranscript(
            turns=tuple(_voice(index, speaker) for index, speaker in enumerate(speakers))
        )
        rows = build_evidence_rows(
            voter=_participant("p-1"),
            candidate_targets=("p-3",),
            contradictions=(),
            transcript=transcript,
            testimony_ledger=build_testimony_ledger(
                transcript,
                contradictions=(),
                sighting_records={
                    grounded_speaker: (
                        SightingRecord(
                            subject="p-3",
                            room="MEDBAY",
                            tick=5,
                            observation_id=f"{grounded_speaker}:5:1",
                        ),
                    )
                },
                move_witness_records={},
                opener=speakers[0],
                roster=frozenset({"p-1", "p-3", *speakers}),
                trigger_kind="report",
            ),
        )

        assert len(rows) == MAX_EVIDENCE_ROWS_PER_SUBJECT
        kept = [row.speaker for row in rows]
        # The grounded voice spoke LAST and survives, at the head of the block.
        assert kept[0] == grounded_speaker
        assert rows[0].first_hand is True
        # Exactly the earliest voice was dropped, and nothing else.
        assert set(speakers) - set(kept) == {speakers[0]}

    def test_only_this_voters_own_channels_reach_its_rows(self) -> None:
        """A voter with empty channels gets no own-perception row.

        The firewall half of the assembler, stated as an observable: p-2 holds
        nothing first-hand, so nothing about p-1's four records may appear in
        p-2's block however the meeting runs.
        """

        captured, prompt = _capturing_vote_prompt()
        _run_meeting(
            _vote_responder(accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-2"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )

        own_kinds = {"own_sighting", "own_vent", "own_transit", "own_body_discovery"}
        assert {row.kind for row in captured["p-1"]} & own_kinds
        for voter_id in ("p-2", "p-3", "p-4"):
            assert not [row for row in captured[voter_id] if row.kind in own_kinds]
            assert all(
                row.speaker != "p-1" or row.kind != "own_sighting"
                for row in captured[voter_id]
            )

    def test_every_own_channel_row_is_marked_first_hand(self) -> None:
        """All four own-perception kinds carry ``first_hand=True``.

        The bit is what the template turns into "first-hand: you saw this
        yourself" versus "stated it at this table", so a kind that quietly
        shipped ``False`` would tell the voter its own vent sighting was
        hearsay. Asserted per KIND rather than over the tuple, so flipping one
        of the four cannot hide behind the other three.
        """

        rows = build_evidence_rows(
            voter=_channel_voters()[0],
            candidate_targets=("p-2", "p-3", "p-4"),
            contradictions=(),
            transcript=MeetingTranscript(turns=()),
        )
        by_kind = {row.kind: row for row in rows}
        assert set(by_kind) == {
            "own_sighting",
            "own_vent",
            "own_transit",
            "own_body_discovery",
        }
        for kind, row in by_kind.items():
            assert row.first_hand is True, kind
            assert row.speaker == "p-1", kind

    def test_a_contradiction_row_resolves_to_the_turn_it_was_spoken_in(self) -> None:
        """The flag's event id names a turn, and that turn is what it cites.

        A flag carries claim/observation ids, not turn ids, so the row's
        citation and speaker come from resolving ``turn:{turn_id}:…`` back to
        the turn -- the id the ballot's own instruction already asks a voter to
        cite. Both halves are asserted, and the unresolvable case beside them,
        because a resolution that silently returned ``None`` would render a flag
        nobody can cite and attribute it to the subject.
        """

        turn = MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker="p-3",
            turn_kind="reply",
            reply_to="m-1:turn-0",
            observations=(),
            claims=(),
            free_text="I was in MEDBAY.",
        )
        flag = ContradictionRef(
            contradiction_id="c-1",
            kind="alibi_vs_sighting",
            event_a_id="turn:m-1:turn-1:claim:0",
            event_b_id="turn:m-1:turn-1:obs:0",
            subjects=("p-2",),
            description="p-2's account cannot be squared with a sighting.",
        )
        rows = build_evidence_rows(
            voter=_participant("p-1"),
            candidate_targets=("p-2",),
            contradictions=(flag,),
            transcript=MeetingTranscript(turns=(turn,)),
        )
        assert len(rows) == 1
        assert rows[0].kind == "contradiction"
        assert rows[0].citation_id == "m-1:turn-1"
        assert rows[0].speaker == "p-3"
        assert rows[0].first_hand is False
        assert rows[0].description == flag.description

        # An id minted from something other than a turn of THIS meeting: the row
        # still renders, with no citation and the subject as its speaker, rather
        # than citing a turn that is not there.
        foreign = flag.model_copy(
            update={"event_a_id": "turn:other:claim:0", "event_b_id": "elsewhere"}
        )
        orphan = build_evidence_rows(
            voter=_participant("p-1"),
            candidate_targets=("p-2",),
            contradictions=(foreign,),
            transcript=MeetingTranscript(turns=(turn,)),
        )
        assert orphan[0].citation_id is None
        assert orphan[0].speaker == "p-2"

    def test_one_speaker_naming_one_subject_twice_makes_one_row(self) -> None:
        """The (speaker, subject) dedupe, and which turn survives it.

        A reactive chain lets one speaker name the same player in several turns;
        without the dedupe the block would repeat that voice once per turn and
        read as several voices, which is exactly the count the corroboration
        ledger exists to state honestly. The EARLIEST turn is kept, so the row
        cites where the charge started.
        """

        def _accusing_turn(index: int) -> MeetingTurn:
            return MeetingTurn(
                turn_id=f"m-1:turn-{index}",
                turn_index=index,
                speaker="p-3",
                turn_kind="opening" if index == 0 else "reply",
                reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
                observations=(),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-2",
                        confidence=0.6,
                        reason="p-3 accuses p-2",
                    ),
                ),
                free_text="p-2 did it.",
            )

        rows = build_evidence_rows(
            voter=_participant("p-1"),
            candidate_targets=("p-2",),
            contradictions=(),
            transcript=MeetingTranscript(
                turns=(_accusing_turn(0), _accusing_turn(1), _accusing_turn(2))
            ),
        )
        assert len(rows) == 1
        assert rows[0].kind == "testimony"
        assert rows[0].speaker == "p-3"
        assert rows[0].citation_id == "m-1:turn-0"

    def test_a_body_discovery_names_the_victim_and_carries_its_id(self) -> None:
        """The one own-channel row whose subject is never an ejection target."""

        rows = build_evidence_rows(
            voter=_channel_voters()[0],
            candidate_targets=("p-2", "p-3", "p-4"),
            contradictions=(),
            transcript=MeetingTranscript(turns=()),
        )
        discoveries = [row for row in rows if row.kind == "own_body_discovery"]
        assert len(discoveries) == 1
        assert discoveries[0].subject == "p-9"
        assert discoveries[0].citation_id == "p-1:14:0"
        assert discoveries[0].first_hand is True

    def test_an_unstamped_record_renders_without_a_citation(self) -> None:
        """``observation_id=None`` yields a row, not a fabricated id."""

        voter = replace(
            _participant("p-1"),
            sighting_records=(SightingRecord(subject="p-2", room="MEDBAY", tick=11),),
        )
        rows = build_evidence_rows(
            voter=voter,
            candidate_targets=("p-2",),
            contradictions=(),
            transcript=MeetingTranscript(turns=()),
        )
        assert len(rows) == 1
        assert rows[0].citation_id is None

    def test_a_testimony_row_cites_the_accusing_turn(self) -> None:
        """One row per (speaker, subject), citing the earliest such turn."""

        captured, prompt = _capturing_vote_prompt()
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-2"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        turn_ids = frozenset(turn.turn_id for turn in result.transcript.turns)
        testimony = [row for row in captured["p-4"] if row.kind == "testimony"]
        assert testimony
        assert all(row.citation_id in turn_ids for row in testimony)
        pairs = [(row.speaker, row.subject) for row in testimony]
        assert len(pairs) == len(set(pairs))
        # Nobody here spoke a sighting their own record bears out, so no row
        # claims first-hand status. The leg below is the other half.
        assert all(row.first_hand is False for row in testimony)

    def test_a_grounded_voice_is_marked_first_hand_on_the_default_path(self) -> None:
        """The ledger that decides ``first_hand`` is built with the lever OFF.

        A testimony row's ``first_hand`` bit is the meeting layer's own
        definition -- the speaker's OWN typed record bore their account of the
        subject out -- and that is computed by
        :func:`meetings.corroboration.build_testimony_ledger`. Before ruling D5
        the manager built that ledger only while the corroboration lever was ON,
        so on the shipped default path every voice would have read "not
        first-hand" whatever its record said. This drives a real meeting with
        the lever OFF: p-2 speaks a sighting of p-3 that p-2's own
        ``SightingRecord`` bears out, and accuses p-3, so the row p-1 reads must
        say first-hand.
        """

        speaker = replace(
            _voter("p-2"),
            sighting_records=(
                SightingRecord(
                    subject="p-3",
                    room="MEDBAY",
                    tick=5,
                    observation_id="p-2:5:1",
                ),
            ),
        )
        voters = (_channel_voters()[0], speaker, _voter("p-3"), _voter("p-4"))
        spoken = SawPlayerObservation(
            type="saw_player", tick=5, subject="p-3", room="MEDBAY"
        )

        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                who = _extract_marker(prompt, "agent_id=")
                return _turn_json(
                    speaker=who,
                    accuses={"p-1": "p-2", "p-2": "p-3"}.get(who),
                    observations=(spoken,) if who == "p-2" else (),
                )
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                return VoteBallot(
                    voter=voter,
                    target="SKIP",
                    confidence=0.2,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text=f"stub-vote-{voter}",
                ).model_dump_json()
            raise AssertionError("unrecognised prompt")

        captured, prompt = _capturing_vote_prompt()
        _run_meeting(_responder, participants=voters, vote_prompt=prompt)

        grounded = [
            row
            for row in captured["p-1"]
            if row.kind == "testimony" and row.speaker == "p-2" and row.subject == "p-3"
        ]
        assert len(grounded) == 1, captured["p-1"]
        assert grounded[0].first_hand is True

    def test_a_grounded_voice_sorts_above_an_ungrounded_one(self) -> None:
        """First-hand before hearsay, inside ONE subject and ONE channel.

        The rank is only observable where two rows are alike in every earlier
        key: same subject, same provenance class, differing only in whether the
        speaker's own record bore their account out. Two voices against p-3, one
        grounded and one not, is that case -- and without the rank the order
        would fall through to the turn index, putting whichever spoke first on
        top regardless of what either holds.
        """

        def _voice(index: int, speaker: str, spoke: bool) -> MeetingTurn:
            return MeetingTurn(
                turn_id=f"m-1:turn-{index}",
                turn_index=index,
                speaker=speaker,
                turn_kind="opening" if index == 0 else "reply",
                reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
                observations=(
                    (
                        SawPlayerObservation(
                            type="saw_player", tick=5, subject="p-3", room="MEDBAY"
                        ),
                    )
                    if spoke
                    else ()
                ),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-3",
                        confidence=0.6,
                        reason=f"{speaker} accuses p-3",
                    ),
                ),
                free_text="p-3 did it.",
            )

        # p-4 speaks first and is NOT grounded; p-2 speaks second and IS.
        transcript = MeetingTranscript(
            turns=(_voice(0, "p-4", spoke=False), _voice(1, "p-2", spoke=True))
        )
        grounding = {
            "p-2": (
                SightingRecord(
                    subject="p-3", room="MEDBAY", tick=5, observation_id="p-2:5:1"
                ),
            )
        }
        rows = build_evidence_rows(
            voter=_participant("p-1"),
            candidate_targets=("p-3",),
            contradictions=(),
            transcript=transcript,
            testimony_ledger=build_testimony_ledger(
                transcript,
                contradictions=(),
                sighting_records=grounding,
                move_witness_records={},
                opener="p-4",
                roster=frozenset({"p-1", "p-2", "p-3", "p-4"}),
                trigger_kind="report",
            ),
        )
        assert [(row.speaker, row.first_hand) for row in rows] == [
            ("p-2", True),
            ("p-4", False),
        ]


# --------------------------------------------------------------------------- #
# C. The served body                                                           #
# --------------------------------------------------------------------------- #


def _served_ballot(**kwargs: Any) -> str:
    renderers = build_prompt_renderers(_SERVED_SET)
    defaults: dict[str, Any] = {
        "voter_id": "p-1",
        "rendered_memory": "## Your role: CREWMATE",
        "transcript": MeetingTranscript(turns=()),
        "contradiction_flags": (),
        "suspicion_graph": (SuspicionEntry(player_id="p-2", suspicion=0.8, trust=0.5),),
        "candidate_targets": ("p-2", "p-3"),
        "skip_confidence_threshold": 0.6,
    }
    defaults.update(kwargs)
    return renderers.vote(**defaults)


class TestTheServedBody:
    def test_evidence_renders_above_the_number(self) -> None:
        rendered = _served_ballot(
            evidence_rows=(
                EvidenceRow(
                    subject="p-2",
                    description="you saw them in MEDBAY at tick 11",
                    kind="own_sighting",
                    first_hand=True,
                    speaker="p-1",
                    citation_id="p-1:11:0",
                ),
            )
        )
        assert "<evidence>" in rendered
        assert rendered.index("<evidence>") < rendered.index(
            "## Your suspicion of each player"
        )
        assert "you saw them in MEDBAY at tick 11" in rendered
        assert "cite `p-1:11:0`" in rendered

    def test_no_rows_renders_no_block(self) -> None:
        assert "<evidence>" not in _served_ballot()

    def test_a_row_with_no_citation_says_so(self) -> None:
        rendered = _served_ballot(
            evidence_rows=(
                EvidenceRow(
                    subject="p-2",
                    description="you saw them in MEDBAY at tick 11",
                    kind="own_sighting",
                    first_hand=True,
                    speaker="p-1",
                ),
            )
        )
        assert "nothing here you could cite" in rendered

    def test_the_deference_sentence_is_gone_and_nothing_replaced_it(self) -> None:
        """The one sentence ruling D5 names, deleted with no substitute."""

        rendered = _served_ballot()
        assert _DEFERENCE_SENTENCE not in rendered
        assert "trust them over" not in rendered
        for pushing in (
            "trust them",
            "your suspicion levels above are",
            "vote the player with the highest",
            "eject the highest",
        ):
            assert pushing not in rendered.lower()

    def test_planted_the_restored_deference_sentence_is_detected(self) -> None:
        """PLANTED: the assertion above fails on a body that restores it.

        A gate that cannot fail is not a gate, so the deleted sentence is put
        back into a COPY of the rendered bytes and the same predicate is run.
        """

        restored = _served_ballot().replace(
            "ejecting anyway must rest on evidence you can cite below, "
            "never on momentum.",
            "ejecting anyway must rest on evidence you can cite below, "
            f"never on momentum. {_DEFERENCE_SENTENCE}",
        )
        assert _DEFERENCE_SENTENCE in restored
        assert "trust them over" in restored

    def test_the_decision_section_recommends_no_player(self) -> None:
        """No rendered line points the voter at a target, a SKIP or an EJECT.

        The section is scanned for a recommendation verb sitting next to a
        player id; the roster lists and the evidence rows name players without
        recommending any, which is exactly the distinction being kept.
        """

        rendered = _served_ballot()
        section = rendered.split("## How to decide", 1)[1].split("<output_format>")[0]
        recommends = re.compile(
            r"(vote|eject|choose|pick|name)\s+`?p-\d+`?", re.IGNORECASE
        )
        assert recommends.search(section) is None, recommends.search(section)

    def test_planted_a_recommended_target_is_detected(self) -> None:
        """PLANTED: the scan above fires on a body that names one."""

        section = "## How to decide\nYou should vote p-2 tonight.\n<output_format>"
        recommends = re.compile(
            r"(vote|eject|choose|pick|name)\s+`?p-\d+`?", re.IGNORECASE
        )
        assert recommends.search(section) is not None

    def test_the_trust_column_is_gone_from_the_served_row(self) -> None:
        rendered = _served_ballot()
        assert "`p-2`: suspicion 0.80" in rendered
        assert "trust" not in rendered

    def test_the_contract_has_nine_keys_including_the_counter(self) -> None:
        rendered = _served_ballot()
        assert "EXACTLY these 9 keys" in rendered
        assert '"counter_reason_id": null' in rendered
        assert "none_held" in rendered
        skeleton = [
            line for line in rendered.splitlines() if line.startswith('{"voter"')
        ]
        assert len(skeleton) == 1
        assert (
            len(
                json.loads(
                    skeleton[0]
                    .replace("<candidate id or SKIP>", "p-2")
                    .replace("<one short sentence>", "x")
                )
            )
            == 9
        )

    def test_the_frozen_sets_keep_their_trust_column(self) -> None:
        """Ruling D5 moved ONE body; the six frozen sets are untouched."""

        frozen = build_prompt_renderers("qwen3_32b").vote(
            voter_id="p-1",
            rendered_memory="## Your role: CREWMATE",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.8, trust=0.5),
            ),
            candidate_targets=("p-2",),
            skip_confidence_threshold=0.6,
        )
        assert "trust 0.50" in frozen


# --------------------------------------------------------------------------- #
# D. counter_reason_id                                                         #
# --------------------------------------------------------------------------- #


def _ballots_by_voter(result: Any) -> dict[str, VoteBallot]:
    return {ballot.voter: ballot for ballot in result.ballots}


class TestCounterReasonId:
    def test_a_turn_id_counter_survives(self) -> None:
        captured, prompt = _capturing_vote_prompt()
        probe, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        turn_id = probe.transcript.turns[0].turn_id

        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}, counters={"p-2": turn_id}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        ballot = _ballots_by_voter(result)["p-2"]
        assert ballot.counter_reason_id == turn_id
        assert INVALID_COUNTER_REASON_MARKER.split("{")[0] not in ballot.rationale_text

    def test_an_own_observation_id_counter_survives(self) -> None:
        captured, prompt = _capturing_vote_prompt()
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}, counters={"p-1": "p-1:12:0"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        assert _ballots_by_voter(result)["p-1"].counter_reason_id == "p-1:12:0"

    def test_a_fabricated_counter_is_nulled_with_its_own_marker(self) -> None:
        captured, prompt = _capturing_vote_prompt()
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}, counters={"p-1": "not-an-id"}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        ballot = _ballots_by_voter(result)["p-1"]
        assert ballot.counter_reason_id is None
        assert ballot.rationale_text.startswith(
            INVALID_COUNTER_REASON_MARKER.format(counter_reason_id="not-an-id")
        )

    def test_an_over_length_counter_is_bounded_in_the_marker(self) -> None:
        captured, prompt = _capturing_vote_prompt()
        runaway = "z" * (MARKER_QUOTED_ORIGINAL_MAX_CHARS * 4)
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}, counters={"p-1": runaway}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        ballot = _ballots_by_voter(result)["p-1"]
        assert ballot.counter_reason_id is None
        assert len(ballot.rationale_text) < len(runaway)
        assert runaway not in ballot.rationale_text

    @pytest.mark.parametrize(
        "counter",
        [
            None,
            "not-an-id",
            "m-1:turn-0",
            "p-1:12:0",
            "p-2:99:9",
            '" ]injected[ "',
            "[invalid target 'p-3' normalized to SKIP] ",
        ],
    )
    def test_the_counter_moves_no_target_no_tally_and_no_label(
        self, counter: str | None
    ) -> None:
        """The property: over a generated family, the counter changes NOTHING.

        For every counter value -- absent, fabricated, valid in either shape,
        marker-shaped, or injection-shaped -- the recorded target, the meeting
        outcome and every ballot's ``grounding_label`` equal what the identical
        meeting produced with no counter at all. That is the whole of "it is
        not a gate", and any coupling would show up here as an inequality.
        """

        _, prompt = _capturing_vote_prompt()
        baseline, _ = _run_meeting(
            _vote_responder(
                accusations={"p-1": "p-2", "p-2": "p-3"},
                targets={"p-1": "p-2", "p-3": "p-2", "p-4": "p-2"},
            ),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        variant, _ = _run_meeting(
            _vote_responder(
                accusations={"p-1": "p-2", "p-2": "p-3"},
                targets={"p-1": "p-2", "p-3": "p-2", "p-4": "p-2"},
                counters={voter: counter for voter in ("p-1", "p-2", "p-3", "p-4")},
            ),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )

        assert variant.outcome == baseline.outcome
        assert variant.ejected_player_id == baseline.ejected_player_id
        base_by_voter = _ballots_by_voter(baseline)
        for voter, ballot in _ballots_by_voter(variant).items():
            other = base_by_voter[voter]
            assert ballot.target == other.target, voter
            assert ballot.confidence == other.confidence, voter
            assert ballot.grounding_label == other.grounding_label, voter
            assert ballot.primary_reason_id == other.primary_reason_id, voter
            assert (
                ballot.primary_reason_observation_id
                == other.primary_reason_observation_id
            ), voter

    def test_a_fabricated_counter_cannot_forge_the_marker_chain(self) -> None:
        """Model text shaped like a marker is read as the model's, not ours.

        The chain scan is anchored and provenance-split, so a counter whose
        VALUE spells a marker still lands inside the quoted payload of the
        counter marker rather than opening a second one.
        """

        forged = "[invalid target 'p-3' normalized to SKIP] "
        _, prompt = _capturing_vote_prompt()
        result, _ = _run_meeting(
            _vote_responder(accusations={"p-1": "p-2"}, counters={"p-1": forged}),
            participants=_channel_voters(),
            vote_prompt=prompt,
        )
        ballot = _ballots_by_voter(result)["p-1"]
        assert ballot.counter_reason_id is None
        assert ballot.guard_rewrite_reason is None
        assert ballot.target == "SKIP"
        pattern = _marker_pattern(INVALID_COUNTER_REASON_MARKER)
        match = pattern.match(ballot.rationale_text)
        assert match is not None
        # The forged marker is INSIDE this marker's payload, so the scan
        # consumes exactly one marker before the model's own body.
        assert ballot.rationale_text[match.end() :] == "stub-vote-p-1"

    def test_a_null_counter_is_elided_from_the_recorded_bytes(self) -> None:
        """``None`` and "key absent" are one fact, so they get one spelling.

        This is what keeps the four committed reports byte-stable: they embed
        re-serialized ballots, and a ``null`` key written here would move them.
        """

        ballot = VoteBallot(
            voter="p-1",
            target="SKIP",
            confidence=0.1,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="x",
        )
        assert "counter_reason_id" not in ballot.model_dump()
        assert "counter_reason_id" not in ballot.model_dump_json()

        carried = ballot.model_copy(update={"counter_reason_id": "m-1:turn-0"})
        assert carried.model_dump()["counter_reason_id"] == "m-1:turn-0"


class TestTheCounterMarkerIsRegisteredEverywhere:
    """One test per marker table -- a table is a gate only if it is checked."""

    def test_registered_in_the_replay_loader_table(self) -> None:
        assert (
            "invalid_counter_reason_id",
            INVALID_COUNTER_REASON_MARKER,
        ) in _BALLOT_PREFIX_MARKERS

    def test_registered_in_the_surrogate_table(self) -> None:
        from training.surrogate.dataset import BALLOT_AUDIT_MARKERS

        assert (
            "invalid_counter_reason_id",
            INVALID_COUNTER_REASON_MARKER,
        ) in BALLOT_AUDIT_MARKERS

    def test_registered_in_the_deduction_marker_chain(self) -> None:
        patterns = [pattern.pattern for pattern, _, _, _ in _BALLOT_MARKER_CHAIN]
        assert _marker_pattern(INVALID_COUNTER_REASON_MARKER).pattern in patterns

    def test_it_rewrites_no_target_in_the_chain(self) -> None:
        """Registered as a NON-rewriting marker, which is what it is."""

        wanted = _marker_pattern(INVALID_COUNTER_REASON_MARKER).pattern
        for pattern, rewrites_target, redirected, parse_default in _BALLOT_MARKER_CHAIN:
            if pattern.pattern == wanted:
                assert (rewrites_target, redirected, parse_default) == (
                    False,
                    False,
                    False,
                )
                return
        raise AssertionError("the counter marker is not in the chain")
