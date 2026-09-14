"""What the candidate accounts arm does with the answer its prompt asks for.

The measurement the accounts/turn-schema alignment card owes, taken offline on
the fake provider against a planted payload of the archived refusal's shape
(``tasks/diagnosis-2026-09-13-live-run-stops.md``): two candidate-arm turns
across two live runs were billed and refused on ``claims[].type`` with the tag
``whereabouts``, and the meeting replaced each with a placeholder. The two
tests below run the real account renderers through a real
:class:`~meetings.manager.MeetingManager` and count
:attr:`~meetings.manager.MeetingManager.defaulted_calls` per turn call:
answering where the prompt now files the shape refuses nothing, and the
archived misfiling still defaults every turn it is sent on, which is why the
prompt had to name the list. The live output-length half of that diagnosis
cannot be measured here at all -- a scripted payload has no length of its own
-- and waits on the owner's calibration decision.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from agents.strategic.prompts import build_prompt_renderers
from engine.world import load_map
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.evidence_profile import MeetingEvidenceProfile
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
)
from meetings.schemas import MeetingResult, MeetingTurn, VoteBallot
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map

_SPEAKERS: tuple[str, ...] = ("p-1", "p-2", "p-3")
_PLACEMENT: dict[str, Any] = {"type": "whereabouts", "tick": 4, "room": "CAFETERIA"}


def _public_map() -> PublicMapView:
    return public_map_from_engine_map(load_map(Path("engine/maps/canonical_1.yaml")))


def _accusation(speaker: str) -> dict[str, Any]:
    target = _SPEAKERS[(_SPEAKERS.index(speaker) + 1) % len(_SPEAKERS)]
    return {
        "type": "accusation",
        "against": target,
        "confidence": 0.6,
        "reason": "They were never where they said they were.",
    }


def _answer(speaker: str, *, place_in: str) -> str:
    """One turn payload, with the self-placement filed in ``place_in``.

    ``observations`` is where the accounts menu now files a ``whereabouts``
    item; ``claims`` is where the two archived live turns put it.
    """

    payload: dict[str, Any] = {
        "turn_id": "ignored",
        "turn_index": 0,
        "speaker": speaker,
        "turn_kind": "opening",
        "reply_to": None,
        "observations": [],
        "claims": [_accusation(speaker)],
        "free_text": "I was in the cafeteria at tick 4.",
    }
    payload[place_in] = [_PLACEMENT, *payload[place_in]]
    return json.dumps(payload)


class _PlantedAnswerClient:
    """A fake provider that answers every turn with one planted payload."""

    def __init__(self, *, place_in: str) -> None:
        self.place_in = place_in
        self.turn_calls = 0
        self.turn_prompts: list[str] = []

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
        assert agent_id is not None
        if schema is MeetingTurn:
            self.turn_calls += 1
            self.turn_prompts.append(prompt)
            text = _answer(agent_id, place_in=self.place_in)
        else:
            text = VoteBallot(
                voter=agent_id,
                target="SKIP",
                confidence=0.2,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="The public accounts are insufficient.",
            ).model_dump_json()
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=4, output_tokens=3),
            cost_usd=0.0,
            model="planted-accounts-answer",
        )


async def _candidate_meeting(
    *, place_in: str
) -> tuple[MeetingResult, MeetingManager, _PlantedAnswerClient]:
    """One meeting on the candidate arm: both account levers on."""

    client = _PlantedAnswerClient(place_in=place_in)
    renderers = build_prompt_renderers(
        "qwen3_6_27b",
        env={},
        public_account_version=1,
        attributed_testimony_version=1,
    )
    manager = MeetingManager(
        llm_client=client,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
        crewmate_report_prompt=renderers.crewmate_report,
        impostor_report_prompt=renderers.impostor_report,
        statement_prompt=renderers.statement,
        vote_prompt=renderers.vote,
        reporter_reasoning=False,
        corroboration_discipline=False,
        evidence_profile=MeetingEvidenceProfile(
            public_account_version=1, attributed_testimony_version=1
        ),
        public_map=_public_map(),
    )
    participants = tuple(
        MeetingParticipant(
            agent_id=speaker,
            role="IMPOSTOR" if speaker == "p-3" else "CREWMATE",
            rendered_memory="You were in CAFETERIA at tick 4.",
        )
        for speaker in _SPEAKERS
    )
    result = await manager.run(
        meeting_id="m",
        trigger=MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=10,
            description="p-1 called an emergency meeting",
        ),
        participants=participants,
    )
    return result, manager, client


def test_the_answer_the_accounts_prompt_asks_for_is_never_refused() -> None:
    # The measurement: with the self-placement filed where the menu files it,
    # no turn on the candidate arm is refused, and every turn reaches the
    # record carrying the placement it was asked for.
    result, manager, client = asyncio.run(_candidate_meeting(place_in="observations"))
    assert client.turn_calls > 0
    assert manager.defaulted_calls == ()
    assert len(result.transcript.turns) == client.turn_calls
    for turn in result.transcript.turns:
        assert [entry.type for entry in turn.observations] == ["whereabouts"]
        assert turn.free_text == "I was in the cafeteria at tick 4."
    # The prompt those turns answered is the one that files it there.
    for prompt in client.turn_prompts:
        assert 'Each item of "observations" is one of these shapes:' in prompt
        assert '- {"type":"whereabouts","tick":<int>,"room":"<room id>"}' in prompt


def test_the_archived_shape_defaults_every_turn_it_is_sent_on() -> None:
    # The control, and the reason the prompt had to name the list: the same
    # sentence filed under "claims" -- the shape the two archived live turns
    # carried -- is refused on every attempt, so each turn is replaced by a
    # placeholder. The schema is unchanged by this card: what moved is which
    # list the model is asked to put the item in.
    result, manager, client = asyncio.run(_candidate_meeting(place_in="claims"))
    assert client.turn_calls > 0
    defaults = manager.defaulted_calls
    assert len(defaults) == len(result.transcript.turns)
    assert {default.trigger for default in defaults} == {"validation"}
    for turn in result.transcript.turns:
        assert turn.observations == ()
        assert turn.free_text != "I was in the cafeteria at tick 4."
