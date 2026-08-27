"""The vote ballot and the accusation round render the SAME turn the same way.

Two templates render ``transcript.turns`` for the same audience minutes apart:
the accusation round shows a speaker's observations, alibi rooms and tick
windows, and the reasons behind each accusation and corroboration; the vote
ballot is where those turns are actually weighed. Nothing keeps the two bodies
in step except this gate, and without it the ballot render silently narrowed to
a single ``free_text`` line.

The invariant is one-directional: every turn field the statement render exposes
must reach the vote render. The two templates legitimately differ elsewhere —
their empty-transcript lines, their surrounding prose, their evidence blocks —
so parity is asserted over the TURN BODY only, field by field and line by line,
never by whole-prompt equality.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from agents.strategic.prompts.loader import _PROMPTS_ROOT, build_prompt_renderers
from meetings.manager import PromptRenderInputs, SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    CompletedTaskObservation,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    WhereaboutsClaim,
)

_LOCKED_SET = "qwen3_6_27b"
_CORPUS = Path("replays/ml_corpus/9p2i")

# One turn carrying EVERY observation type and EVERY claim type. The shared
# fixture in ``test_bespoke_prompt_sets`` carries only ``found_body`` /
# ``saw_player`` / accusations; a gate blind to ``whereabouts``, ``saw_move``,
# ``completed_task``, alibis and corroborations would not have caught the
# defect this file exists to stop.
_RICH_TURN = MeetingTurn(
    turn_id="m-1:turn-0",
    turn_index=0,
    speaker="p-2",
    turn_kind="opening",
    reply_to=None,
    observations=(
        FoundBodyObservation(
            type="found_body", tick=410, body_of="p-7", room="ELECTRICAL"
        ),
        SawPlayerObservation(
            type="saw_player",
            tick=405,
            subject="p-3",
            room="ELECTRICAL",
            co_present=("p-5",),
        ),
        SawMoveObservation(
            type="saw_move",
            tick=406,
            subject="p-3",
            from_room="ELECTRICAL",
            to_room="EAST_HALL",
        ),
        CompletedTaskObservation(
            type="completed_task", tick=402, task_id="empty_trash", room="CAFETERIA"
        ),
        SawVentObservation(type="saw_vent", tick=407, subject="p-3", room="MEDBAY"),
        WhereaboutsClaim(type="whereabouts", tick=409, room="CAFETERIA"),
    ),
    claims=(
        AlibiClaim(
            type="alibi", subject="p-2", from_tick=400, to_tick=409, room="CAFETERIA"
        ),
        AccusationClaim(
            type="accusation",
            against="p-3",
            confidence=0.7,
            reason="walked out of the room the body was in",
        ),
        CorroborationClaim(
            type="corroboration",
            supports="p-5",
            on_tick=405,
            reason="I stood beside them the whole window",
        ),
    ),
    free_text="Found p-7 in ELECTRICAL; p-3 walked out just before.",
)
_PLAIN_TURN = MeetingTurn(
    turn_id="m-1:turn-1",
    turn_index=1,
    speaker="p-3",
    turn_kind="reply",
    reply_to="m-1:turn-0",
    observations=(),
    claims=(),
    free_text="I was nowhere near that room.",
)
_TRANSCRIPT = MeetingTranscript(turns=(_RICH_TURN, _PLAIN_TURN))

_MEMORY = "[obs p-2:410:0] you found the body of p-7 in ELECTRICAL"
_SUSP = (
    SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5),
    SuspicionEntry(player_id="p-5", suspicion=0.3, trust=0.5),
)


def _renders(
    transcript: MeetingTranscript, *, root: Path | None = None
) -> tuple[str, str]:
    """(statement render, vote render) of the same transcript, one set."""

    renderers = (
        build_prompt_renderers(_LOCKED_SET)
        if root is None
        else build_prompt_renderers(_LOCKED_SET, root=root)
    )
    inputs = PromptRenderInputs(impostor_count=2)
    statement = renderers.statement(
        agent_id="p-5",
        rendered_memory=_MEMORY,
        transcript=transcript,
        contradictions=(),
        prior_turn=transcript.turns[-1] if transcript.turns else None,
        turn_kind="reply" if transcript.turns else "opening",
        fellow_impostor_ids=(),
        living_ids=("p-2", "p-3", "p-5"),
        dead_ids=("p-7",),
        is_impostor=False,
        is_body_report=True,
        render_inputs=inputs,
    )
    vote = renderers.vote(
        voter_id="p-5",
        rendered_memory=_MEMORY,
        transcript=transcript,
        contradiction_flags=(),
        suspicion_graph=_SUSP,
        candidate_targets=("p-2", "p-3"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=(),
        suspicion_provenance=(),
        render_inputs=inputs,
    )
    return statement, vote


def _transcript_section(rendered: str) -> str:
    """The bytes between ``<transcript>`` and ``</transcript>``, exclusive."""

    head = rendered.index("<transcript>") + len("<transcript>")
    return rendered[head : rendered.index("</transcript>", head)]


def _body_lines(section: str) -> list[str]:
    """The section's rendered lines, blank lines dropped."""

    return [line for line in section.splitlines() if line.strip()]


def _turn_fields(turn: MeetingTurn) -> list[str]:
    """Every value a full turn render must put on the page for this turn.

    Derived from the fixture rather than from either template, so a template
    that stops rendering a field fails here instead of quietly agreeing with
    the assertion built from its own output.
    """

    fields: list[str] = [turn.turn_id, turn.speaker, turn.free_text]
    for obs in turn.observations:
        fields.append(str(obs.tick))
        if obs.type == "saw_player":
            fields += [obs.subject, obs.room, *obs.co_present]
        elif obs.type == "saw_move":
            fields += [obs.subject, obs.from_room, obs.to_room]
        elif obs.type == "completed_task":
            fields += [obs.task_id, obs.room]
        elif obs.type == "found_body":
            fields += [obs.body_of, obs.room]
        elif obs.type == "saw_vent":
            fields += [obs.subject, obs.room]
        else:
            fields.append(obs.room)
    for claim in turn.claims:
        if claim.type == "alibi":
            fields += [
                claim.subject,
                claim.room,
                str(claim.from_tick),
                str(claim.to_tick),
            ]
        elif claim.type == "accusation":
            fields += [claim.against, claim.reason]
        else:
            fields += [claim.supports, str(claim.on_tick), claim.reason]
    return fields


class TestTheVoteRenderMatchesTheStatementRender:
    """The ballot shows the voter everything the table was shown."""

    def test_every_turn_field_the_statement_exposes_reaches_the_vote(self) -> None:
        statement, vote = _renders(_TRANSCRIPT)
        spoken = _transcript_section(statement)
        voted = _transcript_section(vote)

        for field in _turn_fields(_RICH_TURN):
            assert field in spoken, field
            assert field in voted, field

    def test_the_two_turn_bodies_render_line_for_line(self) -> None:
        # Stronger than the field sweep and the real anti-drift property: a
        # voter reads ONE register across both prompts, so the turn body is
        # the same bytes in both.
        statement, vote = _renders(_TRANSCRIPT)

        assert _body_lines(_transcript_section(statement)) == _body_lines(
            _transcript_section(vote)
        )

    def test_no_blank_line_the_statement_body_did_not_have(self) -> None:
        # Jinja whitespace control is the easy half to get wrong: a block tag
        # moved onto a content line changes the rendered bytes without
        # changing a word.
        statement, vote = _renders(_TRANSCRIPT)

        assert _transcript_section(statement) == _transcript_section(vote)

    def test_the_turn_line_still_opens_with_the_copyable_turn_id(self) -> None:
        # ``primary_reason_id`` is copied VERBATIM off this line, and the
        # output-format skeleton interpolates the last turn's id.
        _statement, vote = _renders(_TRANSCRIPT)
        section = _transcript_section(vote)

        assert "- [m-1:turn-0] turn 0 (opening) — p-2" in section
        assert "- [m-1:turn-1] turn 1 (reply) — p-3" in section

    def test_the_inline_accusation_on_the_header_line_is_gone(self) -> None:
        # The header's ``accuses X (0.70)`` said less than the claims row that
        # supersedes it, and no consumer parses it.
        _statement, vote = _renders(_TRANSCRIPT)
        header = _transcript_section(vote).splitlines()[1]

        assert header == "- [m-1:turn-0] turn 0 (opening) — p-2"
        assert "accuses p-3 (0.70): walked out of the room the body was in" in (
            _transcript_section(vote)
        )

    def test_a_turn_with_no_observations_renders_no_saw_block(self) -> None:
        # The contrast IS the surface: every other turn has a ``saw:`` block.
        _statement, vote = _renders(_TRANSCRIPT)
        section = _transcript_section(vote)
        _rich, plain = section.split("- [m-1:turn-1]")

        assert "saw:" in _rich
        assert "saw:" not in plain
        assert "claims:" not in plain

    def test_the_empty_transcript_keeps_the_vote_template_own_line(self) -> None:
        # Parity is over the turn body, not the empty state — a voter is never
        # the first to speak, and the two templates word this differently.
        _statement, vote = _renders(MeetingTranscript(turns=()))

        assert _transcript_section(vote).strip() == "(no turns recorded)"

    def test_the_parity_gate_bites(self, tmp_path: Path) -> None:
        # Restore the flat one-line turn render in a scratch copy of the set:
        # the same assertion must FAIL, or it is proving nothing.
        root = tmp_path / "prompts"
        shutil.copytree(_PROMPTS_ROOT / _LOCKED_SET, root / _LOCKED_SET)
        victim = root / _LOCKED_SET / "vote_ballot.j2"
        body = victim.read_text(encoding="utf-8")
        opener = "{% for turn in transcript.turns %}\n"
        closer = "{% endfor %}\n{% else %}\n(no turns recorded)"
        start = body.index(opener) + len(opener)
        victim.write_text(
            body[:start]
            + "- [{{ turn.turn_id }}] turn {{ turn.turn_index }} "
            + "({{ turn.turn_kind }}) — {{ turn.speaker }}: {{ turn.free_text }}\n"
            + body[body.index(closer) :],
            encoding="utf-8",
        )

        statement, _live_vote = _renders(_TRANSCRIPT)
        _crippled_statement, crippled = _renders(_TRANSCRIPT, root=root)
        section = _transcript_section(crippled)
        missing = [field for field in _turn_fields(_RICH_TURN) if field not in section]

        # Every assertion this file makes fails on the crippled render.
        assert "walked out of the room the body was in" in missing
        assert "empty_trash" in missing
        assert "I stood beside them the whole window" in missing
        assert _body_lines(_transcript_section(statement)) != _body_lines(section)
        assert _transcript_section(statement) != section


def _committed_meeting_transcripts() -> list[tuple[str, MeetingTranscript]]:
    """Every recorded meeting transcript in one committed corpus replay.

    A hand-built fixture cannot prove the render survives the shapes the corpus
    actually contains, and the register's own side-by-side came from this seed.
    """

    path = _CORPUS / "replay-seed-1128.jsonl"
    out: list[tuple[str, MeetingTranscript]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("kind") != "meeting":
                continue
            out.append(
                (
                    record["meeting_id"],
                    MeetingTranscript.model_validate(record["transcript"]),
                )
            )
    return out


class TestParityOverTheCommittedCorpus:
    """The same parity, over turns a model actually produced."""

    def test_the_corpus_supplies_turns_to_check(self) -> None:
        meetings = _committed_meeting_transcripts()

        assert meetings, f"no meeting rows in {_CORPUS}/replay-seed-1128.jsonl"
        assert any(
            turn.observations or turn.claims
            for _id, transcript in meetings
            for turn in transcript.turns
        )

    @pytest.mark.parametrize(
        ("meeting_id", "transcript"),
        _committed_meeting_transcripts(),
        ids=lambda value: value if isinstance(value, str) else "",
    )
    def test_recorded_turns_reach_the_ballot_whole(
        self, meeting_id: str, transcript: MeetingTranscript
    ) -> None:
        statement, vote = _renders(transcript)
        spoken = _transcript_section(statement)
        voted = _transcript_section(vote)

        assert _body_lines(spoken) == _body_lines(voted), meeting_id
        for turn in transcript.turns:
            for field in _turn_fields(turn):
                assert field in voted, (meeting_id, turn.turn_id, field)
