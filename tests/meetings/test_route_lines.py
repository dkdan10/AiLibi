"""The route lines: the builder, the typed check, the planted cases and the block.

``meetings/route_lines.py`` builds, for each living candidate of a ballot, one
role-blind line listing the changes of room its places stated at this table make
that the station's doors or the public regroup allow, and the served
``qwen3_6_27b`` ballot renders those lines in one guarded ``<routes>`` block
(``tasks/work/route-lines-field.md``). Every case here scripts a meeting, builds
its lines, renders the real ballot and reads the block back; nothing prints a
rendered prompt.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import re
import shutil
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

import experiments.lab.route_check_replay as rcr
import meetings.manager as manager_module
import meetings.route_lines as route_lines
import meetings.transcript as transcript_module
from agents.strategic.prompts.loader import (
    CANONICAL_MAP_CARD,
    VOTE_BALLOT_TEMPLATE,
    build_prompt_renderers,
)
from engine.world import Map, load_canonical_map
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.corroboration import _walkable_transits
from meetings.evidence_profile import MeetingEvidenceProfile
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
)
from meetings.render_contract import PromptRenderInputs
from meetings.route_lines import (
    ROUTE_BLOCK_CLOSE,
    ROUTE_BLOCK_OPEN,
    ROUTE_PLACEMENT_KINDS,
    RouteLine,
    _require_lines_on_the_table,
    build_route_lines,
    parse_route_lines,
    route_block_span,
    without_route_block,
)
from meetings.schemas import (
    AlibiClaim,
    AlibiSegment,
    MeetingTranscript,
    MeetingTurn,
    ModelAuthoredVoteBallot,
    ObservationClaim,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    WhereaboutsClaim,
)
from meetings.transcript import (
    CANONICAL_ROOM_NEIGHBORS,
    CANONICAL_ROOMS,
    StatedPlacement,
    is_relevant_sighting,
)
from tests.meetings._manager_helpers import (
    _crewmate_report_prompt,
    _impostor_report_prompt,
    _statement_prompt,
    _turn_json,
)

_REPO: Final[Path] = Path(__file__).resolve().parents[2]
_SET: Final[str] = "qwen3_6_27b"
_CANDIDATES: Final[tuple[str, ...]] = ("p-2", "p-3", "p-4", "p-5")
_SUBJECT: Final[str] = "p-3"

Step = tuple[tuple[str, ...], int, tuple[str, ...], int, int, str, int | None]


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _saw(subject: str, room: str, tick: int) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room
    )


def _vent(subject: str, room: str, tick: int) -> SawVentObservation:
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


def _turn(
    index: int,
    speaker: str,
    *observations: ObservationClaim,
    claims: tuple[AlibiClaim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "opt_in",
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=f"turn {index} from {speaker}",
    )


def _sightings(*placed: tuple[str, str, int]) -> MeetingTranscript:
    """One turn per sighting, each by its own speaker, of (subject, room, tick)."""

    speakers = ("p-1", "p-4", "p-5", "p-2", "p-6", "p-7")
    return MeetingTranscript(
        turns=tuple(
            _turn(index, speakers[index % len(speakers)], _saw(*sighting))
            for index, sighting in enumerate(placed)
        )
    )


def _lines(
    transcript: MeetingTranscript,
    *,
    candidates: tuple[str, ...] = _CANDIDATES,
    regroup: frozenset[int] = frozenset(),
) -> tuple[RouteLine, ...]:
    return build_route_lines(
        transcript=transcript, candidate_targets=candidates, regroup_ticks=regroup
    )


def _vote(root: Path | None = None) -> Callable[..., str]:
    return (
        build_prompt_renderers(_SET, env={}).vote
        if root is None
        else build_prompt_renderers(_SET, root=root, env={}).vote
    )


def _ballot_inputs(
    *,
    voter: str = "p-1",
    candidates: tuple[str, ...] = _CANDIDATES,
    transcript: MeetingTranscript | None = None,
) -> dict[str, Any]:
    return {
        "voter_id": voter,
        "rendered_memory": "## Your role: CREWMATE",
        "transcript": transcript if transcript is not None else MeetingTranscript(),
        "contradiction_flags": (),
        "suspicion_graph": tuple(
            SuspicionEntry(player_id=player, suspicion=0.4, trust=0.5)
            for player in candidates
        ),
        "candidate_targets": candidates,
        "skip_confidence_threshold": 0.6,
        "render_inputs": PromptRenderInputs(
            impostor_count=2, map_card=CANONICAL_MAP_CARD
        ),
    }


def _render(lines: tuple[RouteLine, ...], **overrides: Any) -> str:
    """The served ballot with the route lines ON, over neutral inputs."""

    return _vote()(
        **{**_ballot_inputs(), **overrides},
        route_lines=lines,
        route_lines_version=1,
    )


def _steps(lines: Sequence[RouteLine], subject: str) -> tuple[Step, ...]:
    for line in lines:
        if line.subject == subject:
            return tuple(
                (
                    step.from_rooms,
                    step.from_tick,
                    step.to_rooms,
                    step.to_tick,
                    step.doors,
                    step.reading,
                    step.regroup_tick,
                )
                for step in line.steps
            )
    return ()


def _served_steps(
    transcript: MeetingTranscript,
    subject: str = _SUBJECT,
    *,
    regroup: frozenset[int] = frozenset(),
) -> tuple[Step, ...]:
    """The steps the rendered ballot serves about ``subject``, read back off the block."""

    lines = _lines(transcript, regroup=regroup)
    parsed = parse_route_lines(_render(lines)) if lines else ()
    assert parsed == lines
    return _steps(parsed, subject)


# ---------------------------------------------------------------------------
# The planted cases
# ---------------------------------------------------------------------------


def test_one_door_in_one_tick_walks() -> None:
    assert _served_steps(
        _sightings((_SUBJECT, "WEST_HALL", 5), (_SUBJECT, "ADMIN", 6))
    ) == ((("WEST_HALL",), 5, ("ADMIN",), 6, 1, "walking_fits", None),)


def test_two_doors_in_two_ticks_walk_where_the_one_hop_clause_links_nothing() -> None:
    transcript = _sightings((_SUBJECT, "ADMIN", 5), (_SUBJECT, "CAFETERIA", 7))
    assert _served_steps(transcript) == (
        (("ADMIN",), 5, ("CAFETERIA",), 7, 2, "walking_fits", None),
    )
    pair = (
        StatedPlacement(
            tick=5, rooms=frozenset({"ADMIN"}), speaker="p-1", event_id="a"
        ),
        StatedPlacement(
            tick=7, rooms=frozenset({"CAFETERIA"}), speaker="p-4", event_id="b"
        ),
    )
    assert _walkable_transits(pair) == ()


def test_a_change_across_the_public_regroup_names_the_regroup_tick() -> None:
    transcript = _sightings((_SUBJECT, "REACTOR", 4), (_SUBJECT, "MEDBAY", 6))
    regroup = frozenset({5})
    assert _served_steps(transcript, regroup=regroup) == (
        (("REACTOR",), 4, ("MEDBAY",), 6, 5, "regroup_between", 5),
    )
    rendered = _render(_lines(transcript, regroup=regroup))
    assert (
        "REACTOR at tick 4 to MEDBAY at tick 6, 5 doors apart, the public regroup at "
        "tick 5 falls between, walking cannot decide it." in rendered
    )


def test_the_same_change_without_a_regroup_is_no_step_and_leaves_no_line() -> None:
    transcript = _sightings((_SUBJECT, "REACTOR", 4), (_SUBJECT, "MEDBAY", 6))
    assert _lines(transcript) == ()
    assert ROUTE_BLOCK_OPEN not in _render(_lines(transcript))


def test_two_rooms_at_one_tick_are_no_step_and_a_walk_across_a_regroup_walks() -> None:
    assert _lines(_sightings((_SUBJECT, "ADMIN", 5), (_SUBJECT, "UPPER_HALL", 5))) == ()
    walked = _sightings((_SUBJECT, "WEST_HALL", 5), (_SUBJECT, "ADMIN", 7))
    assert _served_steps(walked, regroup=frozenset({6})) == (
        (("WEST_HALL",), 5, ("ADMIN",), 7, 1, "walking_fits", None),
    )


def test_a_change_neither_reading_allows_is_left_out_between_two_that_are() -> None:
    transcript = _sightings(
        (_SUBJECT, "WEST_HALL", 5),
        (_SUBJECT, "ADMIN", 6),
        (_SUBJECT, "REACTOR", 7),
        (_SUBJECT, "ENGINEERING", 8),
    )
    assert _served_steps(transcript) == (
        (("WEST_HALL",), 5, ("ADMIN",), 6, 1, "walking_fits", None),
        (("REACTOR",), 7, ("ENGINEERING",), 8, 1, "walking_fits", None),
    )


def test_a_vent_sighting_places_nobody() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(0, "p-1", _vent(_SUBJECT, "REACTOR", 4)),
            _turn(1, "p-4", _saw(_SUBJECT, "ENGINEERING", 5)),
        )
    )
    assert "saw_vent" not in ROUTE_PLACEMENT_KINDS
    assert _lines(transcript) == ()


def test_a_spawn_window_sighting_places_its_subject() -> None:
    transcript = _sightings((_SUBJECT, "CAFETERIA", 1), (_SUBJECT, "UPPER_HALL", 2))
    assert _served_steps(transcript) == (
        (("CAFETERIA",), 1, ("UPPER_HALL",), 2, 1, "walking_fits", None),
    )
    # The gate the field does not apply would drop the first sighting.
    assert not is_relevant_sighting(
        tick=1,
        rooms=frozenset({"CAFETERIA"}),
        triggering_body_rooms=frozenset(),
        regroup_ticks=frozenset(),
    )


def test_a_compound_label_renders_both_rooms() -> None:
    transcript = _sightings((_SUBJECT, "LABS/MEDBAY", 5), (_SUBJECT, "WEST_HALL", 6))
    assert _served_steps(transcript) == (
        (("LABS", "MEDBAY"), 5, ("WEST_HALL",), 6, 1, "walking_fits", None),
    )
    assert "LABS/MEDBAY at tick 5 to WEST_HALL at tick 6, 1 door apart" in _render(
        _lines(transcript)
    )


def test_the_voter_a_dead_player_and_a_one_room_candidate_have_no_line() -> None:
    transcript = _sightings(
        ("p-1", "WEST_HALL", 5),
        ("p-1", "ADMIN", 6),
        ("p-9", "WEST_HALL", 5),
        ("p-9", "ADMIN", 6),
        ("p-5", "ADMIN", 3),
        ("p-5", "ADMIN", 6),
        (_SUBJECT, "WEST_HALL", 5),
        (_SUBJECT, "ADMIN", 6),
    )
    # p-1 votes, p-9 is dead (neither is a candidate), and p-5 never changes room.
    lines = _lines(transcript)
    assert [line.subject for line in lines] == [_SUBJECT]


def test_lines_follow_the_candidate_order_and_list_steps_in_tick_order() -> None:
    transcript = _sightings(
        ("p-5", "ADMIN", 9),
        ("p-2", "STORAGE", 3),
        ("p-5", "WEST_HALL", 8),
        ("p-2", "ENGINEERING", 4),
        ("p-5", "MEDBAY", 9),
    )
    lines = _lines(transcript, candidates=("p-5", "p-2"))
    assert [line.subject for line in lines] == ["p-5", "p-2"]
    # p-5: WEST_HALL at 8, then ADMIN and MEDBAY at 9, ordered by rooms.
    assert _steps(lines, "p-5") == (
        (("WEST_HALL",), 8, ("ADMIN",), 9, 1, "walking_fits", None),
    )


def test_places_stated_twice_count_once() -> None:
    once = _sightings((_SUBJECT, "WEST_HALL", 5), (_SUBJECT, "ADMIN", 6))
    twice = _sightings(
        (_SUBJECT, "WEST_HALL", 5),
        (_SUBJECT, "WEST_HALL", 5),
        (_SUBJECT, "ADMIN", 6),
        (_SUBJECT, "ADMIN", 6),
    )
    assert _lines(twice) == _lines(once)


def test_every_route_kind_places_its_player() -> None:
    """Company, a movement's destination, a whereabouts and an alibi stay each place."""

    company = MeetingTranscript(
        turns=(
            _turn(
                0,
                "p-1",
                SawPlayerObservation(
                    type="saw_player",
                    tick=5,
                    subject="p-4",
                    room="WEST_HALL",
                    co_present=(_SUBJECT,),
                ),
            ),
            _turn(1, "p-4", _saw(_SUBJECT, "ADMIN", 6)),
        )
    )
    moved = MeetingTranscript(
        turns=(
            _turn(
                0,
                "p-1",
                SawMoveObservation(
                    type="saw_move",
                    tick=5,
                    subject=_SUBJECT,
                    from_room="MEDBAY",
                    to_room="WEST_HALL",
                ),
            ),
            _turn(1, "p-4", _saw(_SUBJECT, "ADMIN", 6)),
        )
    )
    whereabouts = MeetingTranscript(
        turns=(
            _turn(
                0,
                _SUBJECT,
                WhereaboutsClaim(type="whereabouts", tick=5, room="WEST_HALL"),
            ),
            _turn(1, "p-4", _saw(_SUBJECT, "ADMIN", 6)),
        )
    )
    alibi = MeetingTranscript(
        turns=(
            _turn(
                0,
                _SUBJECT,
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject=_SUBJECT,
                        route=(
                            AlibiSegment(room="WEST_HALL", from_tick=3, to_tick=5),
                            AlibiSegment(room="ADMIN", from_tick=6, to_tick=6),
                        ),
                    ),
                ),
            ),
        )
    )
    expected = ((("WEST_HALL",), 5, ("ADMIN",), 6, 1, "walking_fits", None),)
    for transcript in (company, moved, whereabouts, alibi):
        assert _steps(_lines(transcript), _SUBJECT) == expected


def test_the_route_kinds_are_the_reference_readings_kinds() -> None:
    assert ROUTE_PLACEMENT_KINDS == rcr.C_INPUT_KINDS


# ---------------------------------------------------------------------------
# The typed check
# ---------------------------------------------------------------------------


def _step(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "from_rooms": ("REACTOR",),
        "from_tick": 4,
        "to_rooms": ("MEDBAY",),
        "to_tick": 6,
        "doors": 5,
        "reading": "regroup_between",
        "regroup_tick": 5,
    }
    return {**base, **overrides}


#: The card's example line: its two steps are a planted case the check accepts.
_EXAMPLE_STEPS: Final[tuple[dict[str, object], ...]] = (
    _step(),
    _step(
        from_rooms=("MEDBAY",),
        from_tick=6,
        to_rooms=("WEST_HALL",),
        to_tick=7,
        doors=1,
        reading="walking_fits",
        regroup_tick=None,
    ),
)
_EXAMPLE: Final[dict[str, object]] = {"subject": _SUBJECT, "steps": _EXAMPLE_STEPS}


def test_the_example_line_is_accepted_and_served_as_the_card_words_it() -> None:
    line = RouteLine.model_validate(_EXAMPLE)
    rendered = _render((line,))
    assert (
        "- `p-3`, places stated at this table: REACTOR at tick 4 to MEDBAY at tick 6, "
        "5 doors apart, the public regroup at tick 5 falls between, walking cannot "
        "decide it; MEDBAY at tick 6 to WEST_HALL at tick 7, 1 door apart, walking "
        "fits.\n" in rendered
    )
    assert parse_route_lines(rendered) == (line,)


@pytest.mark.parametrize(
    ("label", "payload"),
    [
        ("a suspect key", {**_EXAMPLE, "suspect": True}),
        (
            "walking_fits for five doors in two ticks",
            {**_EXAMPLE, "steps": (_step(reading="walking_fits", regroup_tick=None),)},
        ),
        (
            "regroup_between with no regroup tick",
            {**_EXAMPLE, "steps": (_step(regroup_tick=None),)},
        ),
        (
            "regroup_between with the regroup tick outside",
            {**_EXAMPLE, "steps": (_step(regroup_tick=7),)},
        ),
        (
            "regroup_between with the regroup tick at the first end",
            {**_EXAMPLE, "steps": (_step(regroup_tick=4),)},
        ),
        (
            "regroup_between where a walk fits",
            {
                **_EXAMPLE,
                "steps": (
                    _step(
                        from_rooms=("WEST_HALL",),
                        from_tick=5,
                        to_rooms=("ADMIN",),
                        to_tick=6,
                        doors=1,
                        regroup_tick=6,
                    ),
                ),
            },
        ),
        ("a wrong door count", {**_EXAMPLE, "steps": (_step(doors=4),)}),
        (
            "a reading outside the two",
            {**_EXAMPLE, "steps": (_step(reading="walking_does_not_fit"),)},
        ),
        ("a room off the map", {**_EXAMPLE, "steps": (_step(to_rooms=("BRIDGE",)),)}),
        (
            "overlapping rooms",
            {**_EXAMPLE, "steps": (_step(to_rooms=("MEDBAY", "REACTOR")),)},
        ),
        (
            "unsorted rooms",
            {**_EXAMPLE, "steps": (_step(to_rooms=("MEDBAY", "LABS"), doors=5),)},
        ),
        ("no room", {**_EXAMPLE, "steps": (_step(from_rooms=()),)}),
        ("ticks running back", {**_EXAMPLE, "steps": (_step(from_tick=7),)}),
        ("a boolean tick", {**_EXAMPLE, "steps": (_step(from_tick=True),)}),
        ("a negative tick", {**_EXAMPLE, "steps": (_step(regroup_tick=-1),)}),
        ("no step", {**_EXAMPLE, "steps": ()}),
        (
            "steps out of tick order",
            {**_EXAMPLE, "steps": tuple(reversed(_EXAMPLE_STEPS))},
        ),
        ("a subject that is no id", {**_EXAMPLE, "subject": "p 3"}),
        ("an empty subject", {**_EXAMPLE, "subject": ""}),
        ("free text on a step", {**_EXAMPLE, "steps": (_step(note="was in"),)}),
    ],
)
def test_the_typed_check_refuses(label: str, payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RouteLine.model_validate(payload)


def test_the_door_bound_follows_the_room_table(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: the room table's source changes and the step's hop bound follows it."""

    assert route_lines.RouteStep.model_validate(_step()).doors == 5
    # Two rooms on the table bound every search at two doors, so the five doors
    # between REACTOR and MEDBAY are no longer found and the step is refused.
    monkeypatch.setattr(
        route_lines, "CANONICAL_ROOMS", frozenset({"REACTOR", "MEDBAY"})
    )
    with pytest.raises(ValidationError, match="door count is the map's: None"):
        route_lines.RouteStep.model_validate(_step())


def test_a_line_about_a_non_candidate_or_a_second_line_is_refused() -> None:
    line = RouteLine.model_validate(_EXAMPLE)
    assert _require_lines_on_the_table([line], candidate_targets=("p-3",)) == (line,)
    with pytest.raises(ValueError, match="only a candidate"):
        _require_lines_on_the_table([line], candidate_targets=("p-2",))
    with pytest.raises(ValueError, match="at most one route line"):
        _require_lines_on_the_table([line, line], candidate_targets=("p-3",))


def test_the_builder_refuses_invalid_input() -> None:
    transcript = _sightings((_SUBJECT, "WEST_HALL", 5), (_SUBJECT, "ADMIN", 6))
    with pytest.raises(ValueError, match="each candidate once"):
        _lines(transcript, candidates=("p-3", "p-3"))
    for bad in (frozenset({-1}), frozenset({True})):
        with pytest.raises(ValueError, match="regroup ticks"):
            _lines(transcript, regroup=bad)


def test_the_builder_takes_exactly_its_three_keywords() -> None:
    parameters = inspect.signature(build_route_lines).parameters
    assert list(parameters) == ["transcript", "candidate_targets", "regroup_ticks"]
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters.values())
    assert all(p.default is inspect.Parameter.empty for p in parameters.values())


# ---------------------------------------------------------------------------
# Imports and the one home of the placement reader and the reconcile rule
# ---------------------------------------------------------------------------

_ALLOWED_ROOTS: Final[frozenset[str]] = frozenset({"meetings", "pydantic"})


def _foreign_imports(source: str) -> list[str]:
    """Modules ``source`` imports outside ``meetings``, pydantic and the stdlib."""

    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names = [node.module]
        for name in names:
            root = name.split(".", 1)[0]
            if root not in _ALLOWED_ROOTS and root not in sys.stdlib_module_names:
                found.append(name)
    return found


def test_the_module_imports_only_meetings_pydantic_and_the_stdlib() -> None:
    source = (_REPO / "meetings" / "route_lines.py").read_text(encoding="utf-8")
    assert _foreign_imports(source) == []
    # Planted: an engine read and an agents read are both found.
    planted = source + "\nimport engine.world\nfrom agents.memory import store\n"
    assert _foreign_imports(planted) == ["engine.world", "agents.memory"]


_ONE_HOME: Final[frozenset[str]] = frozenset({"spoken_placements", "reconcilable"})


def _definers(sources: Mapping[str, str]) -> dict[str, list[str]]:
    """Which modules define a function named ``spoken_placements`` or ``reconcilable``."""

    found: dict[str, list[str]] = {name: [] for name in sorted(_ONE_HOME)}
    for path, source in sorted(sources.items()):
        for node in ast.walk(ast.parse(source)):
            if (
                isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
                and node.name in _ONE_HOME
            ):
                found[node.name].append(path)
    return found


def _tracked_sources() -> dict[str, str]:
    roots: tuple[str, ...] = (
        "agents",
        "api",
        "engine",
        "eval",
        "experiments",
        "meetings",
        "llm",
        "observation",
        "orchestrator",
        "scripts",
        "training",
        "tests",
    )
    return {
        path.relative_to(_REPO).as_posix(): path.read_text(encoding="utf-8")
        for root in roots
        for path in (_REPO / root).rglob("*.py")
        if "ml_spike" not in path.parts and "torch_probe" not in path.parts
    }


def test_only_the_route_lines_module_defines_the_reader_and_the_rule() -> None:
    sources = _tracked_sources()
    assert _definers(sources) == {
        "reconcilable": ["meetings/route_lines.py"],
        "spoken_placements": ["meetings/route_lines.py"],
    }
    # The lab reads them back from the one home and keeps no copy.
    assert rcr.spoken_placements is route_lines.spoken_placements
    assert rcr.reconcilable is route_lines.reconcilable
    assert rcr.Placement is route_lines.Placement
    # Planted: a copy of the rule in the lab is found.
    planted = dict(sources)
    planted["experiments/lab/route_check_replay.py"] += (
        "\n\ndef reconcilable(earlier, later, *, regroup_ticks):\n    return None\n"
    )
    assert _definers(planted)["reconcilable"] == [
        "experiments/lab/route_check_replay.py",
        "meetings/route_lines.py",
    ]


# ---------------------------------------------------------------------------
# The fixed wording
# ---------------------------------------------------------------------------

#: Words the block's fixed text may never carry: a role, a suspect, a verdict on
#: honesty or presence, or an impossible move.
_FORBIDDEN_WORDS: Final[tuple[str, ...]] = (
    "impostor",
    "crewmate",
    "suspect",
    "guilty",
    "innocent",
    "lying",
    "honest",
    "true",
    "confirmed",
    "was in",
    "were in",
    "impossible",
)


def _forbidden_in(text: str) -> list[str]:
    return [
        word
        for word in _FORBIDDEN_WORDS
        if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE)
    ]


def _block_source() -> str:
    source = (
        _REPO / "agents" / "strategic" / "prompts" / _SET / VOTE_BALLOT_TEMPLATE
    ).read_text(encoding="utf-8")
    start = source.index(f"\n{ROUTE_BLOCK_OPEN}\n")
    end = source.index(f"\n{ROUTE_BLOCK_CLOSE}\n", start)
    return source[start:end]


def _fixed_text(block: str) -> str:
    """The block's fixed text: its template source with every tag and expression removed."""

    return re.sub(r"\{%.*?%\}|\{\{.*?\}\}", " ", block, flags=re.DOTALL)


def test_the_fixed_text_carries_no_forbidden_word() -> None:
    fixed = _fixed_text(_block_source())
    assert "places stated at this table" in fixed
    assert _forbidden_in(fixed) == []
    served = _render((RouteLine.model_validate(_EXAMPLE),))
    start, end = route_block_span(served) or (0, 0)
    assert _forbidden_in("\n".join(served.split("\n")[start : end + 1])) == []


@pytest.mark.parametrize("word", _FORBIDDEN_WORDS)
def test_the_wording_scan_fails_on_each_planted_word(word: str) -> None:
    fixed = _fixed_text(_block_source())
    assert _forbidden_in(f"{fixed} A line here {word} there.") == [word]


def test_the_block_names_no_task_audit_or_ruling_id_and_no_heading() -> None:
    fixed = _fixed_text(_block_source())
    assert re.search(r"\b(Task|R\d+|D\d|B\d|audit|ruling|card)\b", fixed) is None
    assert "## " not in _block_source()


# ---------------------------------------------------------------------------
# The block: ON only, parses back, the OFF bytes underneath
# ---------------------------------------------------------------------------

_PLAYERS: Final[tuple[str, ...]] = ("p-1", "p-2", "p-3", "p-4", "p-5", "p-6")
_ROOMS: Final = st.sampled_from(sorted(CANONICAL_ROOMS))
_TICKS: Final = st.integers(min_value=0, max_value=20)


@st.composite
def _observation(draw: st.DrawFn) -> ObservationClaim:
    kind = draw(st.sampled_from(("saw_player", "whereabouts", "saw_move", "saw_vent")))
    tick = draw(_TICKS)
    subject = draw(st.sampled_from(_PLAYERS))
    room = draw(st.one_of(_ROOMS, st.sampled_from(("LABS/MEDBAY", "VARIOUS"))))
    if kind == "saw_player":
        company = draw(st.lists(st.sampled_from(_PLAYERS), max_size=2, unique=True))
        return SawPlayerObservation(
            type="saw_player",
            tick=tick,
            subject=subject,
            room=room,
            co_present=tuple(company),
        )
    if kind == "whereabouts":
        return WhereaboutsClaim(type="whereabouts", tick=tick, room=room)
    if kind == "saw_move":
        return SawMoveObservation(
            type="saw_move",
            tick=tick,
            subject=subject,
            from_room=draw(_ROOMS),
            to_room=room,
        )
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


@st.composite
def _alibi(draw: st.DrawFn, speaker: str) -> AlibiClaim:
    start = draw(_TICKS)
    legs: list[AlibiSegment] = []
    for _ in range(draw(st.integers(min_value=1, max_value=3))):
        end = start + draw(st.integers(min_value=0, max_value=3))
        legs.append(AlibiSegment(room=draw(_ROOMS), from_tick=start, to_tick=end))
        start = end + 1
    return AlibiClaim(type="alibi", subject=speaker, route=tuple(legs))


@st.composite
def _meetings(draw: st.DrawFn) -> tuple[MeetingTranscript, frozenset[int]]:
    turns: list[MeetingTurn] = []
    for index in range(draw(st.integers(min_value=1, max_value=6))):
        speaker = draw(st.sampled_from(_PLAYERS))
        observations = draw(st.lists(_observation(), max_size=4))
        claims = draw(st.lists(_alibi(speaker), max_size=1))
        turns.append(_turn(index, speaker, *observations, claims=tuple(claims)))
    regroup = draw(st.frozensets(_TICKS, max_size=3))
    return MeetingTranscript(turns=tuple(turns)), regroup


def _bfs(game_map: Map, origin: tuple[str, ...], destination: tuple[str, ...]) -> int:
    """Fewest doors between two room sets, by a breadth-first walk of the engine map."""

    frontier = set(origin)
    seen = set(origin)
    doors = 0
    while not frontier & set(destination):
        frontier = {
            neighbor for room in frontier for neighbor in game_map.room_neighbors(room)
        } - seen
        if not frontier:
            raise AssertionError("the engine map does not link the rooms")
        seen |= frontier
        doors += 1
    return doors


def _map_problems(
    lines: Sequence[RouteLine], game_map: Map, regroup: frozenset[int]
) -> list[str]:
    """Each step whose doors or reading disagree with the engine map and the rule."""

    problems: list[str] = []
    for line in lines:
        for step in line.steps:
            doors = _bfs(game_map, step.from_rooms, step.to_rooms)
            inside = sorted(t for t in regroup if step.from_tick < t <= step.to_tick)
            if doors <= step.to_tick - step.from_tick:
                expected: tuple[str, int | None] = ("walking_fits", None)
            elif inside:
                expected = ("regroup_between", inside[0])
            else:
                problems.append(f"{line.subject}: a step neither walks nor crosses")
                continue
            if step.doors != doors or (step.reading, step.regroup_tick) != expected:
                problems.append(f"{line.subject}: a step disagrees with the engine map")
    return problems


@given(meeting=_meetings())
@settings(deadline=None, max_examples=150)
def test_every_step_reads_the_engine_map(
    meeting: tuple[MeetingTranscript, frozenset[int]],
) -> None:
    transcript, regroup = meeting
    lines = _lines(transcript, candidates=_PLAYERS[1:], regroup=regroup)
    assert _map_problems(lines, load_canonical_map(), regroup) == []


def test_one_door_flipped_in_a_copy_of_the_table_turns_the_map_property_red(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: the neighbour table's source changes and the output follows it."""

    transcript = _sightings((_SUBJECT, "REACTOR", 4), (_SUBJECT, "MEDBAY", 6))
    assert _lines(transcript) == ()
    flipped = {
        room: set(neighbors) for room, neighbors in CANONICAL_ROOM_NEIGHBORS.items()
    }
    flipped["REACTOR"].add("MEDBAY")
    flipped["MEDBAY"].add("REACTOR")
    monkeypatch.setattr(
        transcript_module,
        "CANONICAL_ROOM_NEIGHBORS",
        MappingProxyType({room: frozenset(n) for room, n in flipped.items()}),
    )
    lines = _lines(transcript)
    assert _steps(lines, _SUBJECT) == (
        (("REACTOR",), 4, ("MEDBAY",), 6, 1, "walking_fits", None),
    )
    # On the engine's own map the five doors neither walk in two ticks nor cross.
    assert _map_problems(lines, load_canonical_map(), frozenset()) == [
        f"{_SUBJECT}: a step neither walks nor crosses"
    ]
    # A regroup inside the ticks: the engine map reads it as a crossing, so the
    # flipped table's walk disagrees with it.
    crossed = _lines(transcript, regroup=frozenset({5}))
    assert _map_problems(crossed, load_canonical_map(), frozenset({5})) == [
        f"{_SUBJECT}: a step disagrees with the engine map"
    ]


@given(meeting=_meetings())
@settings(deadline=None, max_examples=60)
def test_a_rendered_block_parses_back_to_its_lines(
    meeting: tuple[MeetingTranscript, frozenset[int]],
) -> None:
    transcript, regroup = meeting
    lines = _lines(transcript, candidates=_PLAYERS[1:], regroup=regroup)
    rendered = _render(lines, candidate_targets=_PLAYERS[1:])
    assert parse_route_lines(rendered) == lines
    assert (route_block_span(rendered) is not None) == bool(lines)


_VOTER_ROLES: Final = st.sampled_from(
    (("CREWMATE", ()), ("IMPOSTOR", ("p-4",)), ("IMPOSTOR", ()), (None, ()))
)


@given(
    meeting=_meetings(),
    voter=_VOTER_ROLES,
    arms=st.sampled_from(((None, None), (1, 1))),
)
@settings(deadline=None, max_examples=60)
def test_removing_the_block_from_an_on_ballot_gives_the_off_ballot(
    meeting: tuple[MeetingTranscript, frozenset[int]],
    voter: tuple[Literal["CREWMATE", "IMPOSTOR"] | None, tuple[str, ...]],
    arms: tuple[Literal[1] | None, Literal[1] | None],
) -> None:
    transcript, regroup = meeting
    role, fellows = voter
    kill_row, impostor_ballot = arms
    inputs = {
        **_ballot_inputs(candidates=_PLAYERS[1:], transcript=transcript),
        "voter_role": role,
        "fellow_impostor_ids": fellows,
        "ballot_kill_row_version": kill_row,
        "impostor_ballot_version": impostor_ballot,
    }
    lines = _lines(transcript, candidates=_PLAYERS[1:], regroup=regroup)
    vote = _vote()
    off = vote(**inputs)
    on = vote(**inputs, route_lines=lines, route_lines_version=1)
    assert without_route_block(on) == off
    # The version alone, with no line, renders the OFF bytes.
    assert vote(**inputs, route_lines=(), route_lines_version=1) == off


def test_the_block_sits_between_the_map_and_the_evidence_and_parses_with_its_header() -> (
    None
):
    rendered = _render((RouteLine.model_validate(_EXAMPLE),))
    span = route_block_span(rendered)
    assert span is not None
    rows = rendered.split("\n")
    assert rows[span[0] - 2] == "</map>" and rows[span[0] - 1] == ""
    assert rendered.index(ROUTE_BLOCK_CLOSE) < rendered.index(
        "## Your suspicion of each player"
    )


def test_a_malformed_line_inside_the_block_raises() -> None:
    rendered = _render((RouteLine.model_validate(_EXAMPLE),))
    for old, new in (
        ("walking fits.", "walking works."),
        ("5 doors apart", "5 door apart"),
        ("1 door apart", "1 doors apart"),
        ("at tick 6, 5 doors", "at tick 6, 4 doors"),
    ):
        broken = rendered.replace(old, new, 1)
        assert broken != rendered
        with pytest.raises(ValueError):
            parse_route_lines(broken)
    span = route_block_span(rendered)
    assert span is not None
    rows = rendered.split("\n")
    with pytest.raises(ValueError, match="header precedes"):
        parse_route_lines(
            "\n".join([*rows[: span[1]], "a stray header line", *rows[span[1] :]])
        )
    with pytest.raises(ValueError, match="at most one route line"):
        doubled = [*rows[: span[1]], rows[span[1] - 1], *rows[span[1] :]]
        parse_route_lines("\n".join(doubled))
    with pytest.raises(ValueError, match="at least one line"):
        parse_route_lines("\n".join([*rows[: span[0] + 2], *rows[span[1] :]]))
    with pytest.raises(ValueError, match="at most once"):
        parse_route_lines(rendered + "\n" + ROUTE_BLOCK_OPEN + "\n" + ROUTE_BLOCK_CLOSE)
    with pytest.raises(ValueError, match="never closed"):
        parse_route_lines(rendered.replace(ROUTE_BLOCK_CLOSE, "(closed)"))
    assert parse_route_lines("no block here") == ()
    assert without_route_block("no block here") == "no block here"


def test_a_template_copy_that_rewords_a_line_fails_the_round_trip(
    tmp_path: Path,
) -> None:
    """Planted: the served wording reworded in a template copy no longer parses back."""

    root = tmp_path / "prompts"
    shutil.copytree(_REPO / "agents" / "strategic" / "prompts" / _SET, root / _SET)
    victim = root / _SET / VOTE_BALLOT_TEMPLATE
    source = victim.read_text(encoding="utf-8")
    assert source.count("places stated at this table:") == 1
    victim.write_text(
        source.replace("places stated at this table:", "places said here:"),
        encoding="utf-8",
    )
    line = RouteLine.model_validate(_EXAMPLE)
    reworded = _vote(root)(
        **_ballot_inputs(), route_lines=(line,), route_lines_version=1
    )
    with pytest.raises(ValueError, match="not in the served form"):
        parse_route_lines(reworded)


def test_lines_handed_over_without_their_version_are_refused() -> None:
    with pytest.raises(ValueError, match="route_lines_version None"):
        _vote()(**_ballot_inputs(), route_lines=(RouteLine.model_validate(_EXAMPLE),))


def test_no_other_template_of_any_set_reads_the_route_lines() -> None:
    readers = sorted(
        path.relative_to(_REPO).as_posix()
        for path in (_REPO / "agents" / "strategic" / "prompts").rglob("*.j2")
        if "route_lines" in path.read_text(encoding="utf-8")
    )
    assert readers == ["agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2"]


# ---------------------------------------------------------------------------
# Role-blind and the same for every voter, through the real manager
# ---------------------------------------------------------------------------

_VOTER_LINE: Final[re.Pattern[str]] = re.compile(
    r'"voter" must equal "(?P<voter>p-\d+)"'
)


@dataclass
class _ScriptedTable:
    """Turns answered from a script; every ballot SKIPs. Records nothing else."""

    observations: Mapping[str, tuple[ObservationClaim, ...]]

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is ModelAuthoredVoteBallot:
            match = _VOTER_LINE.search(prompt)
            assert match is not None
            text = (
                '{"voter": "%s", "target": "SKIP", "confidence": 0.5, '
                '"primary_reason_id": null, "considered_alternatives": [], '
                '"rationale_text": "nothing settles it"}' % match["voter"]
            )
        else:
            assert agent_id is not None
            text = _turn_json(
                speaker=agent_id, observations=self.observations.get(agent_id, ())
            )
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model="scripted-table",
        )


@dataclass
class _BlockSink:
    """The real ballot renderer, keeping each voter's route block."""

    blocks: dict[str, str] = field(default_factory=dict)

    def __call__(self, **kwargs: Any) -> str:
        prompt = build_prompt_renderers(_SET, env={}).vote(**kwargs)
        span = route_block_span(prompt)
        self.blocks[kwargs["voter_id"]] = (
            "" if span is None else "\n".join(prompt.split("\n")[span[0] : span[1] + 1])
        )
        return prompt


def _blocks_at_a_table(
    observations: Mapping[str, tuple[ObservationClaim, ...]],
    *,
    impostors: frozenset[str],
    regroup: frozenset[int],
) -> dict[str, str]:
    """Each voter's route block at one scripted meeting with ``impostors`` impostors."""

    sink = _BlockSink()
    manager = MeetingManager(
        llm_client=_ScriptedTable(observations=observations),
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=sink,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
        evidence_profile=MeetingEvidenceProfile(route_lines_version=1),
    )
    participants = tuple(
        MeetingParticipant(
            agent_id=player,
            role="IMPOSTOR" if player in impostors else "CREWMATE",
            rendered_memory=f"## Your role: {'IMPOSTOR' if player in impostors else 'CREWMATE'}",
            suspicion_graph=(),
            fellow_impostor_ids=tuple(sorted(impostors - {player}))
            if player in impostors
            else (),
        )
        for player in _PLAYERS
    )
    asyncio.new_event_loop().run_until_complete(
        manager.run(
            meeting_id="m-1",
            trigger=MeetingTrigger(
                triggered_by="p-1",
                trigger_tick=21,
                description="p-1 called an emergency meeting",
                kind="emergency",
            ),
            participants=participants,
            regroup_ticks=regroup,
        )
    )
    return sink.blocks


_Table = Callable[..., dict[str, str]]


def _role_blind_problems(
    observations: Mapping[str, tuple[ObservationClaim, ...]],
    *,
    regroup: frozenset[int],
    assignments: Sequence[frozenset[str]],
    table: _Table = _blocks_at_a_table,
) -> list[str]:
    """Where a block moves with the roles, or two voters read one player differently."""

    problems: list[str] = []
    runs = [
        table(observations, impostors=impostors, regroup=regroup)
        for impostors in assignments
    ]
    if any(run != runs[0] for run in runs[1:]):
        problems.append("a block moved with the roles")
    for run in runs:
        lines: dict[str, RouteLine] = {}
        for block in run.values():
            for line in parse_route_lines(block):
                if lines.setdefault(line.subject, line) != line:
                    problems.append(f"two voters read {line.subject} differently")
    return problems


_OBSERVATIONS: Final = st.dictionaries(
    keys=st.sampled_from(_PLAYERS),
    values=st.lists(
        _observation().filter(lambda obs: not isinstance(obs, SawVentObservation)),
        max_size=3,
    ).map(tuple),
    max_size=4,
)
_ASSIGNMENTS: Final = st.lists(
    st.frozensets(st.sampled_from(_PLAYERS), min_size=1, max_size=2),
    min_size=2,
    max_size=3,
)


@given(
    observations=_OBSERVATIONS,
    regroup=st.frozensets(_TICKS, max_size=2),
    assignments=_ASSIGNMENTS,
)
@settings(deadline=None, max_examples=25)
def test_every_block_is_the_same_whoever_holds_the_roles(
    observations: dict[str, tuple[ObservationClaim, ...]],
    regroup: frozenset[int],
    assignments: list[frozenset[str]],
) -> None:
    load_canonical_map()
    assert (
        _role_blind_problems(observations, regroup=regroup, assignments=assignments)
        == []
    )


def test_a_role_read_planted_into_the_builder_breaks_the_role_blind_property(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observations = {
        "p-2": (_saw(_SUBJECT, "WEST_HALL", 5),),
        "p-4": (_saw(_SUBJECT, "ADMIN", 6),),
    }
    assignments = [frozenset({"p-5", "p-6"}), frozenset({_SUBJECT, "p-6"})]
    assert (
        _role_blind_problems(observations, regroup=frozenset(), assignments=assignments)
        == []
    )
    real = route_lines.build_route_lines
    seated: set[str] = set()

    def _role_reading(**kwargs: Any) -> tuple[RouteLine, ...]:
        # Planted: the builder drops the line of a player seated as an impostor.
        return tuple(line for line in real(**kwargs) if line.subject not in seated)

    def _seating(
        observations: Mapping[str, tuple[ObservationClaim, ...]],
        *,
        impostors: frozenset[str],
        regroup: frozenset[int],
    ) -> dict[str, str]:
        seated.clear()
        seated.update(impostors)
        return _blocks_at_a_table(observations, impostors=impostors, regroup=regroup)

    monkeypatch.setattr(manager_module, "build_route_lines", _role_reading)
    assert "a block moved with the roles" in _role_blind_problems(
        observations, regroup=frozenset(), assignments=assignments, table=_seating
    )
