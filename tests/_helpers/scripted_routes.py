"""Record a scripted fake game whose turns state places, for the route lines.

A fake-provider turn states no place (:class:`llm.fake_provider.FakeProvider`
answers every list field empty), so a fake game serves no route line.
:class:`ScriptedRoutesClient` answers as the fake provider does except on the
turns a script names: there a turn states a sighting of an earlier speaker of the
same meeting, in a room at a tick counted from that meeting's own tick or from
the public regroup before it; and at a meeting a :class:`RouteEjection` names,
every voter but the target ejects the target, citing a turn read off the ballot
it was served. Only responses are scripted: the manager decides who speaks, what
the ballot shows and what the tally ejects.

The ticks are counted, never hard-coded: the client reads each meeting's tick
off the opening prompt it answers, and the regroup tick of a meeting is the tick
after the previous one (``orchestrator.replay.derive_regroup_ticks``), which is
why the script is recorded under a config that regroups.

:data:`ROUTES_SEED` and :data:`ROUTES_PLACEMENTS` are the route-lines card's
scripted game (``tasks/work/route-lines-field.md``), recorded on round 2's
declared config with and without ``route_lines_version``
(:func:`record_routes_game`). Its first meeting places the opener one door apart
in one tick (a walk) and then three doors apart in one tick (neither walk nor
crossing), and every other voter ejects the opener citing the walk's second
sighting. Its second meeting places one player two doors apart in two ticks and
another five doors apart across the regroup.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel

from eval.eras import STAGE_B_R2
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot
from orchestrator.experiment_config import RecordedExperimentConfig
from tests._helpers.scripted_meeting import record_game

#: The repository root, for the declared config of round 2.
_REPO: Final[Path] = Path(__file__).resolve().parents[2]

#: The opening prompt's statement of the meeting's tick.
_MEETING_TICK: Final[re.Pattern[str]] = re.compile(
    r"It is tick (?P<tick>\d+) and a meeting just started"
)

#: One transcript line of a ballot: its turn id and its index.
_TRANSCRIPT_TURN: Final[re.Pattern[str]] = re.compile(
    r"^- \[(?P<turn_id>[^\]\n]+)\] turn (?P<index>\d+) \(", re.MULTILINE
)

TickBase = Literal["meeting", "regroup"]


@dataclass(frozen=True)
class ScriptedPlacement:
    """Turn ``turn`` of meeting ``meeting`` states it saw turn ``subject_turn``'s speaker.

    The sighting is in ``room`` at ``offset`` ticks from ``base``: the meeting's
    own tick, or the public regroup tick before it (the tick after the previous
    meeting). Meetings and turns count from 0; turn 0, the opening, is never
    scripted, since the opener must accuse or say it is unsure.
    """

    meeting: int
    turn: int
    subject_turn: int
    room: str
    base: TickBase
    offset: int

    def __post_init__(self) -> None:
        if self.turn < 1 or not 0 <= self.subject_turn < self.turn:
            raise ValueError("a scripted sighting is spoken after its subject spoke")


@dataclass(frozen=True)
class RouteEjection:
    """At meeting ``meeting`` every voter but turn ``target_turn``'s speaker ejects them.

    Each ballot cites turn ``cite_turn`` by the id its own ballot prompt shows.
    """

    meeting: int
    target_turn: int
    cite_turn: int


def served_turn_id(prompt: str, *, index: int) -> str:
    """The id of the transcript turn ``index`` a ballot prompt shows; raise when absent."""

    transcript = prompt.split("<transcript>", 1)[-1].split("</transcript>", 1)[0]
    for match in _TRANSCRIPT_TURN.finditer(transcript):
        if int(match["index"]) == index:
            return match["turn_id"]
    raise ValueError(f"the ballot prompt shows no turn {index}")


@dataclass
class ScriptedRoutesClient:
    """The fake provider, except on the turns and ballots the script names."""

    placements: Sequence[ScriptedPlacement]
    ejections: Sequence[RouteEjection] = ()
    fake: FakeProvider = field(default_factory=FakeProvider)
    meeting: int = -1
    meeting_ticks: list[int] = field(default_factory=list)
    speakers: list[str] = field(default_factory=list)
    in_ballots: bool = True
    scripted_turns: int = 0

    def _tick(self, base: TickBase, offset: int) -> int:
        if base == "meeting":
            return self.meeting_ticks[self.meeting] + offset
        if self.meeting == 0:
            raise ValueError("the first meeting has no regroup before it")
        return self.meeting_ticks[self.meeting - 1] + 1 + offset

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
        response = await self.fake.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        if schema is ModelAuthoredVoteBallot:
            self.in_ballots = True
            for ejection in self.ejections:
                if ejection.meeting != self.meeting:
                    continue
                target = self.speakers[ejection.target_turn]
                if agent_id is None or agent_id == target:
                    return response
                cited = served_turn_id(prompt, index=ejection.cite_turn)
                text = json.dumps(
                    {
                        "voter": agent_id,
                        "target": target,
                        "confidence": 0.9,
                        "primary_reason_id": cited,
                        "primary_reason_observation_id": None,
                        "considered_alternatives": [],
                        "decision_basis": "cited",
                        "rationale_text": f"I vote to eject {target}.",
                    }
                )
                ModelAuthoredVoteBallot.model_validate_json(text)
                return response.model_copy(update={"text": text})
            return response
        if schema is not MeetingTurn:
            return response
        if agent_id is None:
            raise ValueError("a scripted meeting needs every turn's speaker")
        if self.in_ballots:
            self.meeting += 1
            self.speakers = []
            self.in_ballots = False
            opened = _MEETING_TICK.search(prompt)
            if opened is None:
                raise ValueError("the opening prompt states no meeting tick")
            self.meeting_ticks.append(int(opened["tick"]))
        turn = len(self.speakers)
        self.speakers.append(agent_id)
        stated = [
            placement
            for placement in self.placements
            if (placement.meeting, placement.turn) == (self.meeting, turn)
        ]
        if not stated:
            return response
        self.scripted_turns += 1
        text = json.dumps(
            {
                "turn_id": "scripted",
                "turn_index": turn,
                "speaker": agent_id,
                "turn_kind": "opt_in",
                "reply_to": None,
                "claims": [],
                "observations": [
                    {
                        "type": "saw_player",
                        "tick": self._tick(placement.base, placement.offset),
                        "subject": self.speakers[placement.subject_turn],
                        "room": placement.room,
                        "co_present": [],
                    }
                    for placement in stated
                ],
                "free_text": "Here is where I saw them.",
            }
        )
        MeetingTurn.model_validate_json(text)
        return response.model_copy(update={"text": text})


#: The scripted game's seed: a 9p2i fake game with three meetings.
ROUTES_SEED: Final[int] = 0

#: Meeting 0, about the opener (turn 0): WEST_HALL three ticks before the
#: meeting and ADMIN two before (one door in one tick: a walk), then REACTOR one
#: before (three doors in one tick, no regroup between: no step). Meeting 1:
#: turn 1's speaker in ADMIN and then CAFETERIA two ticks later (two doors in two
#: ticks: a walk), and turn 2's speaker in REACTOR the tick before the regroup
#: and MEDBAY at the regroup tick (five doors in one tick, the regroup between).
ROUTES_PLACEMENTS: Final[tuple[ScriptedPlacement, ...]] = (
    ScriptedPlacement(
        meeting=0, turn=1, subject_turn=0, room="WEST_HALL", base="meeting", offset=-3
    ),
    ScriptedPlacement(
        meeting=0, turn=2, subject_turn=0, room="ADMIN", base="meeting", offset=-2
    ),
    ScriptedPlacement(
        meeting=0, turn=3, subject_turn=0, room="REACTOR", base="meeting", offset=-1
    ),
    ScriptedPlacement(
        meeting=1, turn=3, subject_turn=1, room="ADMIN", base="regroup", offset=1
    ),
    ScriptedPlacement(
        meeting=1, turn=4, subject_turn=1, room="CAFETERIA", base="regroup", offset=3
    ),
    ScriptedPlacement(
        meeting=1, turn=3, subject_turn=2, room="REACTOR", base="regroup", offset=-1
    ),
    ScriptedPlacement(
        meeting=1, turn=4, subject_turn=2, room="MEDBAY", base="regroup", offset=0
    ),
)

#: The one ejection: at meeting 0 every other voter ejects the opener, citing
#: turn 2, whose sighting is the walk's second end.
ROUTES_EJECTIONS: Final[tuple[RouteEjection, ...]] = (
    RouteEjection(meeting=0, target_turn=0, cite_turn=2),
)


def round_two_config(*, route_lines: bool) -> RecordedExperimentConfig:
    """Round 2's declared config, with ``route_lines_version = 1`` when asked.

    Read where the era registry keeps it: round 2's candidate copy since round
    3's promotion (was ``replays/samples/9p2i/experiment-config.json``).
    """

    kept = STAGE_B_R2.declared_config
    assert kept is not None
    declared = json.loads((_REPO / kept).read_text(encoding="utf-8"))
    if route_lines:
        declared["route_lines_version"] = 1
    return RecordedExperimentConfig.model_validate(declared)


def record_routes_game(directory: Path, *, route_lines: bool) -> Path:
    """Record the scripted routes game into ``directory``; return its replay path."""

    return record_game(
        directory,
        seed=ROUTES_SEED,
        config=round_two_config(route_lines=route_lines),
        client=ScriptedRoutesClient(
            placements=ROUTES_PLACEMENTS, ejections=ROUTES_EJECTIONS
        ),
    )


__all__ = [
    "ROUTES_EJECTIONS",
    "ROUTES_PLACEMENTS",
    "ROUTES_SEED",
    "RouteEjection",
    "ScriptedPlacement",
    "ScriptedRoutesClient",
    "record_routes_game",
    "round_two_config",
    "served_turn_id",
]
