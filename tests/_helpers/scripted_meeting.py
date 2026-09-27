"""Record real games offline, with a scripted client where a turn must say something.

The fake provider (:class:`llm.fake_provider.FakeProvider`) answers every turn
with no claim, so a fake game never accuses anyone and the one-reply rebuttal
(``bounded_rebuttal_version``) never fires in it. :class:`ScriptedMeetingClient`
answers exactly as the fake provider does, except on the turns a script names:
there it returns an accusation against the speaker of an earlier turn of the
same meeting, and on the ballots of a meeting an :class:`Ejection` names, where
every voter but the named player votes to eject that player. Only the responses
are scripted; the manager decides who speaks, in what order, whether the
rebuttal is due and what the tally ejects, as it does in a recorded game.

:func:`record_game` records one ``HeadlessGame`` into a directory from a declared
experiment config, with the meeting runner built from that config
(``build_default_meeting_runner(profile=...)``) and no environment export, on
the prompt set the committed recordings use, and writes the ``roster.json`` the
readers resolve the roster from and the ``MANIFEST.md`` row the recorder's own
manifest writer (``scripts/_manifest_writer.py``) derives from the replay.

The ballot cases (:class:`ScriptedBallot`) script one named voter's ballot in one
meeting: its target, its confidence and what it cites. A citation is read off the
ballot prompt the voter was actually served, never invented: ``"own_row"`` cites
the first first-hand row the prompt's evidence block holds about the target, and
``"accusing_turn"`` the first row saying someone spoke against the target at
this table. A scripted citation the prompt does not hold raises, so a script can
never record an id the voter did not hold. :data:`BALLOT_ARMS_SEED` and
:data:`BALLOT_ARMS_SCRIPT` are the ballot card's scripted game, recorded on the
round-1 config (:data:`ROUND_ONE_CONFIG`).
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel

from engine.world import load_canonical_map
from llm.client import CallKind, LLMClient, LLMResponse
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import profile_from_config
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot
from orchestrator.experiment_config import RecordedExperimentConfig, meeting_values
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _manifest_writer import update_manifest  # noqa: E402

#: The prompt set every committed recording and the candidate record use.
PROMPT_SET: Final[str] = "qwen3_6_27b"


@dataclass(frozen=True)
class Accusation:
    """Turn ``turn`` of scripted meeting ``meeting`` accuses turn ``against_turn``'s speaker.

    Meetings and turns count from 0 in recording order; turn 0 is the opening.
    ``reason`` is the charge the accused reads back in a rebuttal prompt.
    """

    meeting: int
    turn: int
    against_turn: int
    reason: str

    def __post_init__(self) -> None:
        if not 0 <= self.against_turn < self.turn:
            raise ValueError("a scripted accusation names a turn spoken before it")


@dataclass(frozen=True)
class Ejection:
    """Every voter of scripted meeting ``meeting`` but one ejects turn ``target_turn``'s speaker.

    The named player's own ballot stays the fake provider's; every other voter
    names them at a confidence the tally's ejection floor accepts.
    """

    meeting: int
    target_turn: int
    confidence: float = 0.9


#: Turn 1 of the first meeting accuses the opener, who has already spoken, so
#: the opener holds the one unanswered new charge and takes the rebuttal.
ACCUSE_THE_OPENER: Final[tuple[Accusation, ...]] = (
    Accusation(
        meeting=0,
        turn=1,
        against_turn=0,
        reason="you stood over the body before anyone else arrived",
    ),
)

#: Turn 2 of the first meeting accuses turn 1's speaker and turn 3 accuses the
#: opener. The earliest unanswered new charge is the one against turn 1's
#: speaker, who is not the opener, so that player takes the rebuttal and the
#: opener takes none.
ACCUSE_A_NON_OPENER: Final[tuple[Accusation, ...]] = (
    Accusation(
        meeting=0,
        turn=2,
        against_turn=1,
        reason="you walked away from the reactor right after the lights failed",
    ),
    Accusation(
        meeting=0,
        turn=3,
        against_turn=0,
        reason="you reported a body you never explained finding",
    ),
)


BallotCitation = Literal["own_row", "own_kill_row", "accusing_turn"]


@dataclass(frozen=True)
class ScriptedBallot:
    """Voter ``voter``'s ballot in scripted meeting ``meeting``.

    ``target`` is a player id or ``"SKIP"``. ``cite`` names what the ballot
    cites, read off the prompt the voter was served: ``None`` cites nothing,
    ``"own_row"`` the first first-hand evidence row about ``target`` and
    ``"own_kill_row"`` the first one saying the voter watched ``target`` kill
    (either observation id goes in ``primary_reason_observation_id``), and
    ``"accusing_turn"`` the first evidence row saying someone spoke against
    ``target`` (its turn id goes in ``primary_reason_id``).
    """

    meeting: int
    voter: str
    target: str
    confidence: float = 0.9
    cite: BallotCitation | None = None


#: One served evidence row: subject, description, provenance clause, citation.
_EVIDENCE_ROW = re.compile(
    r"^- `(?P<subject>p-\d+)` \S+ (?P<description>.+?) "
    r"\((?P<provenance>[^;\n]+); cite `(?P<citation>[^`\n]+)`\)$",
    re.MULTILINE,
)


def served_citation(prompt: str, *, target: str, cite: BallotCitation) -> str:
    """The id the ballot prompt's evidence block offers for ``cite`` about ``target``.

    Raises when the prompt holds no such row, so a script cannot cite what the
    voter was not served.
    """

    block = prompt.split("<evidence>", 1)[-1].split("</evidence>", 1)[0]
    for match in _EVIDENCE_ROW.finditer(block):
        if match["subject"] != target:
            continue
        first_hand = match["provenance"].startswith("first-hand")
        if cite == "own_row" and first_hand:
            return match["citation"]
        if (
            cite == "own_kill_row"
            and first_hand
            and match["description"].startswith("you watched them KILL in ")
        ):
            return match["citation"]
        if cite == "accusing_turn" and " spoke against them in turn " in (
            f" {match['description']}"
        ):
            return match["citation"]
    raise ValueError(f"the ballot prompt serves no {cite} row about {target}")


@dataclass
class ScriptedMeetingClient:
    """The fake provider, except on the turns :attr:`script` names.

    A meeting's turns are counted from its opening; a turn call after a ballot
    call opens the next meeting. The manager accepts every scripted turn on the
    first attempt, so the count never double-counts a retry.
    """

    script: Sequence[Accusation]
    ejections: Sequence[Ejection] = ()
    ballots: Sequence[ScriptedBallot] = ()
    fake: FakeProvider = field(default_factory=FakeProvider)
    meeting: int = -1
    speakers: list[str] = field(default_factory=list)
    in_ballots: bool = True
    scripted_turns: int = 0

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
            for ballot in self.ballots:
                if (ballot.meeting, ballot.voter) != (self.meeting, agent_id):
                    continue
                cited = (
                    served_citation(prompt, target=ballot.target, cite=ballot.cite)
                    if ballot.cite is not None
                    else None
                )
                text = json.dumps(
                    {
                        "voter": agent_id,
                        "target": ballot.target,
                        "confidence": ballot.confidence,
                        "primary_reason_id": (
                            cited if ballot.cite == "accusing_turn" else None
                        ),
                        "primary_reason_observation_id": (
                            cited
                            if ballot.cite in ("own_row", "own_kill_row")
                            else None
                        ),
                        "considered_alternatives": [],
                        "decision_basis": "cited" if cited is not None else None,
                        "rationale_text": f"I vote {ballot.target}.",
                    }
                )
                ModelAuthoredVoteBallot.model_validate_json(text)
                return response.model_copy(update={"text": text})
            for ejection in self.ejections:
                if ejection.meeting != self.meeting:
                    continue
                target = self.speakers[ejection.target_turn]
                if agent_id is None or agent_id == target:
                    return response
                text = json.dumps(
                    {
                        "voter": agent_id,
                        "target": target,
                        "confidence": ejection.confidence,
                        "primary_reason_id": None,
                        "considered_alternatives": [],
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
        turn = len(self.speakers)
        self.speakers.append(agent_id)
        for accusation in self.script:
            if (accusation.meeting, accusation.turn) != (self.meeting, turn):
                continue
            self.scripted_turns += 1
            target = self.speakers[accusation.against_turn]
            text = json.dumps(
                {
                    "turn_id": "scripted",
                    "turn_index": turn,
                    "speaker": agent_id,
                    "turn_kind": "opt_in",
                    "reply_to": None,
                    "claims": [
                        {
                            "type": "accusation",
                            "against": target,
                            "confidence": 0.7,
                            "reason": accusation.reason,
                        }
                    ],
                    "observations": [],
                    "free_text": f"I think {target} did it.",
                }
            )
            MeetingTurn.model_validate_json(text)
            return response.model_copy(update={"text": text})
        return response


def record_game(
    directory: Path,
    *,
    seed: int,
    config: RecordedExperimentConfig | None,
    client: LLMClient | None = None,
    num_players: int = 9,
    num_impostors: int = 2,
    tasks_per_crewmate: int = 2,
) -> Path:
    """Record one fake game into ``directory`` from a declared config; return its path.

    The meeting runner is built from ``config``'s meeting layer, never from the
    environment, and ``client`` (the fake provider when omitted) answers every
    call. The directory's ``roster.json`` states the roster the game ran with,
    and its ``MANIFEST.md`` carries the game's row.
    """

    directory.mkdir(parents=True, exist_ok=True)
    runner = build_default_meeting_runner(
        llm_client=client if client is not None else FakeProvider(),
        env={"AILIBI_PROMPT_SET": PROMPT_SET},
        profile=(
            profile_from_config(meeting_values(config)) if config is not None else None
        ),
    )
    path = directory / f"replay-seed-{seed}.jsonl"
    HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=path,
        audit_log_path=Path(os.devnull),
        meeting_runner=runner,
        experiment_config=config,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    ).run()
    (directory / "roster.json").write_text(
        json.dumps(
            {
                "num_players": num_players,
                "num_impostors": num_impostors,
                "tasks_per_crewmate": tasks_per_crewmate,
            }
        ),
        encoding="utf-8",
    )
    update_manifest(
        directory / "MANIFEST.md",
        directory,
        [seed],
        git_sha="scripted",
        refreshed_at="2026-09-26",
    )
    return path


#: The round-1 config the Stage-B decision memo declares (section 1, "Arms"),
#: as the literal the record card's config file holds.
ROUND_ONE_CONFIG: Final[dict[str, object]] = {
    "format_version": 1,
    "meeting_reset": "hub_with_grace",
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "vent_witness_rule": "physical",
    "bounded_rebuttal_version": 1,
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}

#: The ballot card's scripted game: a 9p2i fake game whose impostors are p-2
#: and p-3 and whose crewmate p-1 watches p-3 kill before the first meeting,
#: so p-1 holds a kill row at all three meetings.
BALLOT_ARMS_SEED: Final[int] = 26

#: Two accusations the impostors' ballots cite: p-4 accuses the opener at the
#: first meeting, and p-3 (an impostor) accuses the opener at the second.
BALLOT_ARMS_ACCUSATIONS: Final[tuple[Accusation, ...]] = (
    Accusation(meeting=0, turn=3, against_turn=0, reason="you were alone by the body"),
    Accusation(meeting=1, turn=2, against_turn=0, reason="you keep finding the bodies"),
)

#: The scripted ballots, every other ballot the fake provider's. Meeting 0: p-1
#: ejects the killer it watched, citing its kill row; p-2 names p-1, citing p-4's
#: accusation; p-3 names its teammate p-2, which the meeting layer records as
#: SKIP. Meeting 1: p-2 names p-4, citing only its own sighting; p-3 names p-1,
#: citing its own accusation. Meeting 2: both impostors name p-7 (p-2 citing its
#: own sighting, p-3 nothing) and crewmate p-9 names p-7 below the tally's
#: confidence floor, so the impostors' ballots alone carry p-7's ejection.
BALLOT_ARMS_BALLOTS: Final[tuple[ScriptedBallot, ...]] = (
    ScriptedBallot(meeting=0, voter="p-2", target="p-1", cite="accusing_turn"),
    ScriptedBallot(meeting=0, voter="p-3", target="p-2"),
    ScriptedBallot(meeting=0, voter="p-1", target="p-3", cite="own_kill_row"),
    ScriptedBallot(meeting=1, voter="p-2", target="p-4", cite="own_row"),
    ScriptedBallot(meeting=1, voter="p-3", target="p-1", cite="accusing_turn"),
    ScriptedBallot(meeting=2, voter="p-2", target="p-7", cite="own_row"),
    ScriptedBallot(meeting=2, voter="p-3", target="p-7"),
    ScriptedBallot(meeting=2, voter="p-9", target="p-7", confidence=0.2),
    ScriptedBallot(meeting=2, voter="p-1", target="p-9", confidence=0.3),
)


def record_ballot_arms_game(
    directory: Path, *, config: RecordedExperimentConfig | None = None
) -> Path:
    """Record the ballot card's scripted game into ``directory``; return its path.

    ``config`` defaults to :data:`ROUND_ONE_CONFIG`; a caller passes another to
    record the same script under other arms.
    """

    return record_game(
        directory,
        seed=BALLOT_ARMS_SEED,
        config=(
            config
            if config is not None
            else RecordedExperimentConfig.model_validate(ROUND_ONE_CONFIG)
        ),
        client=ScriptedMeetingClient(
            script=BALLOT_ARMS_ACCUSATIONS, ballots=BALLOT_ARMS_BALLOTS
        ),
    )


__all__ = [
    "ACCUSE_A_NON_OPENER",
    "ACCUSE_THE_OPENER",
    "BALLOT_ARMS_ACCUSATIONS",
    "BALLOT_ARMS_BALLOTS",
    "BALLOT_ARMS_SEED",
    "PROMPT_SET",
    "ROUND_ONE_CONFIG",
    "Accusation",
    "BallotCitation",
    "Ejection",
    "ScriptedBallot",
    "ScriptedMeetingClient",
    "record_ballot_arms_game",
    "record_game",
    "served_citation",
]
