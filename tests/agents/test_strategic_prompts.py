"""Per-template smoke tests for the strategic prompt loader (Task 3.9 / 8.8).

The four ``.j2`` templates at ``agents/strategic/prompts/*.j2`` are the
reactive accusation-chain prompts (DESIGN.md §5.2): the crewmate / impostor
**opening** templates, the reactive **reply / opt-in** template, and the
**vote** template. A ``{% endfor %}`` typo, a wrong kwarg name, or a
schema-incompatible output would not surface until the first live-provider
meeting; these tests close that gap by exercising each template through the
loader and asserting the rendered output (a) is non-empty, (b) contains the
template's distinctive version-marker substring (the four versions bump in
lockstep with ``orchestrator.game.DEFAULT_PROMPT_VERSIONS``), and (c) parses
cleanly through the corresponding Pydantic schema after a
:class:`~llm.fake_provider.FakeProvider` round-trip.

Task 8.8 reshaped the templates from the old parallel-reports
``ReportDocument`` / ``Statement`` pair to the single ordered ``turns``
list: the three meeting-turn templates now emit
:class:`~meetings.schemas.MeetingTurn` and the reactive-turn template gains
the ``prior_turn`` / ``turn_kind`` inputs.

The loader's :class:`jinja2.StrictUndefined` configuration is also
pinned: missing kwargs raise :class:`jinja2.UndefinedError` instead of
silently rendering an empty string.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from typing import TypeVar

import pytest
from jinja2 import UndefinedError

from agents.strategic.prompts import (
    accusation_round_prompt,
    crewmate_report_prompt,
    impostor_report_prompt,
    vote_ballot_prompt,
)
from agents.strategic.prompts.loader import (
    ACCUSATION_ROUND_TEMPLATE,
    CREWMATE_REPORT_TEMPLATE,
    IMPOSTOR_REPORT_TEMPLATE,
    VOTE_BALLOT_TEMPLATE,
    _ENV,  # noqa: PLC2701
)
from llm.fake_provider import FakeProvider
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    VoteBallot,
)

_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


_STUB_CREWMATE_MEMORY = (
    "## Your role: CREWMATE\n"
    "## Tasks completed (global): 3 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 410] You discovered p-2's body in MEDBAY.\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n\n"
    "## Your current beliefs:\n"
    "- p-5: suspicion 0.70\n"
)

_STUB_IMPOSTOR_MEMORY = (
    "## Your role: IMPOSTOR\n"
    "## Tasks completed (global): 3 / 12\n\n"
    "## Recent observations (most salient first):\n"
    "- [tick 395] You saw p-5 in ELECTRICAL.\n"
)


def _opening_turn() -> MeetingTurn:
    """The opening turn (turn 0): an accusation against p-5."""

    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=(
            AccusationClaim(
                type="accusation",
                against="p-5",
                confidence=0.6,
                reason="near MEDBAY before the kill",
            ),
        ),
        free_text="stub-opening-from-p-1",
    )


def _stub_transcript() -> MeetingTranscript:
    """A minimal chain transcript: one opening turn + one reply turn."""

    return MeetingTranscript(
        turns=(
            _opening_turn(),
            MeetingTurn(
                turn_id="m-1:turn-1",
                turn_index=1,
                speaker="p-5",
                turn_kind="reply",
                reply_to="m-1:turn-0",
                observations=(),
                claims=(),
                free_text="stub-reply-from-p-5",
            ),
        ),
    )


class TestLoaderEnvironment:
    def test_loader_uses_strict_undefined(self) -> None:
        # StrictUndefined makes a missing kwarg raise at render time
        # instead of producing an empty string. A regression that
        # silently relaxes this (e.g. switching to ChainableUndefined)
        # must fail this test.
        from jinja2 import StrictUndefined

        assert _ENV.undefined is StrictUndefined

    def test_loader_settings_are_pinned(self) -> None:
        assert _ENV.autoescape is False
        assert _ENV.trim_blocks is True
        assert _ENV.lstrip_blocks is True


class TestCrewmateReportTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="p-3 reported a body at tick 410",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        # The crewmate opening template carries a visible version marker
        # (bumped to v7 in Task 10.11: the emergency-opening branch must not
        # present a fabricated found_body) plus the role framing the LLM
        # plays. A regression that swaps this for the impostor framing, or
        # fails to bump the marker in lockstep, must fail the test.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "crewmate_report.v7" in prompt
        assert "**crewmate**" in prompt
        assert "opening speaker" in prompt

    def test_renders_agent_kwargs_into_prompt(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="p-3 reported a body at tick 410",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "p-3" in prompt
        assert "412" in prompt
        assert "p-3 reported a body at tick 410" in prompt
        assert _STUB_CREWMATE_MEMORY.strip() in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # A template that references a kwarg the loader's strict-undefined
        # environment was not handed must raise UndefinedError; the
        # default Undefined policy would silently render an empty string
        # and ship a malformed prompt to the LLM.
        with pytest.raises(UndefinedError):
            _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
                agent_id="p-3",
                current_tick=412,
                meeting_trigger="trigger",
                # rendered_memory omitted on purpose.
                public_transcript="",
            )

    def test_living_roster_renders_and_constrains_accusations(self) -> None:
        # Task 9.9 (audit gp-3): the living-roster accusation list (living
        # players minus this speaker, threaded like the vote ballot's
        # candidate_targets) renders into the opening prompt with the
        # only-accuse-the-living instruction.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
            living_ids=("p-1", "p-5"),
        )

        assert "You may ONLY accuse a player on the LIVING list below" in prompt
        assert "`p-1`, `p-5`" in prompt

    def test_free_text_length_discipline_is_present(self) -> None:
        # Task 9.9 (audit gp-3): with think:false the 9B relocates its
        # deliberation into free_text and overruns the frozen 2048 turn cap,
        # so the template must carry the length discipline.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "at most 2-3 sentences stating your single conclusion" in prompt
        assert "Do NOT narrate or second-guess your reasoning" in prompt

    def test_render_without_living_ids_validates_under_strict_undefined(
        self,
    ) -> None:
        # The roster block is guarded with `is defined` (the optional-kwarg
        # pattern, like fellow_impostor_ids), so a raw render that omits
        # living_ids entirely still validates under StrictUndefined and
        # simply omits the block.
        prompt = _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "LIVING list" not in prompt

    def test_accuse_or_declare_unsure_hard_rule_is_present(self) -> None:
        # Task 10.3 (audit gp-9 H-H-1): the §5.2 PHASE 1 choice is a hard
        # requirement -- accuse one player or write "unsure" in free_text --
        # backing the manager-side opening validation. 5 of 76 audited
        # meetings opened narration-only and every one killed the chain.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "must EITHER include one `accusation` claim OR say" in prompt
        assert '"unsure" in `free_text`' in prompt

    def test_anti_repetition_line_is_present(self) -> None:
        # Task 10.3 (audit gp-9 H-H-2): the remaining 2048-cap defaults were
        # structured-array repetition loops (one sighting repeated ~5x).
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )

        assert "List each sighting once" in prompt

    def test_dead_roster_renders_as_do_not_accuse_line(self) -> None:
        # Task 10.3 (audit gp-9 H-H-3/D-D-8): 17/18 invalid accusation
        # targets named a real-but-DEAD player; the living list alone never
        # said who is dead. The DEAD line renders under the living roster.
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2", "p-8"),
        )

        assert "`p-1`, `p-5`" in prompt
        assert "DEAD or EJECTED -- do NOT accuse: `p-2`, `p-8`." in prompt

    def test_render_without_dead_ids_validates_under_strict_undefined(
        self,
    ) -> None:
        # dead_ids follows the same optional-kwarg pattern as living_ids: a
        # raw render that omits it entirely still validates and omits the
        # DEAD line (the living roster renders alone).
        prompt = _ENV.get_template(CREWMATE_REPORT_TEMPLATE).render(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
            living_ids=("p-1", "p-5"),
        )

        assert "`p-1`, `p-5`" in prompt
        assert "DEAD or EJECTED" not in prompt

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
        prompt = crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        # If the schema were drifting from what the template asks for
        # (missing required field, type mismatch), the fake provider's
        # internal validation would have raised before returning.
        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


# ---------------------------------------------------------------------------
# Task 10.8 — the crewmate_report v6 emergency-opening branch (DESIGN.md §3.2,
# §5.2; audit gp-3 B-B-4). Golden pins for BOTH branches of the template.
# ---------------------------------------------------------------------------

# The orchestrator's emergency trigger-description phrase the template
# branches on. ``orchestrator.game._build_meeting_trigger`` documents the
# phrase as load-bearing and renders it for every engine EMERGENCY trigger;
# the template selects the emergency-opening frame on exactly this substring
# of ``meeting_trigger`` (the meeting layer threads no structured trigger
# kind to the renderers). Pinned on both ends: here against the template,
# and in tests/orchestrator/test_meeting_integration.py against the
# orchestrator's rendered description.
_EMERGENCY_TRIGGER_PHRASE = "called an emergency meeting"

# Fixed render inputs for the golden pins. The body / emergency renders below
# differ ONLY in ``meeting_trigger``, so any further byte difference between
# the two branches is template drift.
_GOLDEN_BODY_TRIGGER = "p-3 reported body body-p-2-1 at tick 410"
_GOLDEN_EMERGENCY_TRIGGER = "p-3 called an emergency meeting at tick 320"
_GOLDEN_LIVING_IDS = ("p-1", "p-5")
_GOLDEN_DEAD_IDS = ("p-2",)

# The v5 body-report render captured byte-for-byte at the Task 10.8 branch
# point (crewmate_report.v5 as merged in Wave 0 and recorded by 10.5),
# rendered with the inputs above. The v6 body branch must reproduce it
# exactly, apart from the visible version-marker line — that is the
# "body-report branch is byte-unchanged" contract the golden enforces.
_CREWMATE_V5_BODY_GOLDEN = """You are an AI agent playing a social-deduction simulation. You are a
**crewmate**. A meeting has been called and you are the **opening speaker**
(turn 0): you reported the body or called the emergency, so you speak first.
State what you saw and name the single player your evidence most points to. Your
job is to catch the impostor; a non-answer hands them a free round and another
kill. Only withhold an accusation if you genuinely recorded nothing pointing at
anyone -- and if so, you MUST write the word "unsure" in your `free_text`.

Hard rule: your opening must EITHER include one `accusation` claim OR say
"unsure" in `free_text`. An opening with neither is rejected and re-requested.

Prompt: crewmate_report.v5 (DESIGN.md §5.2 PHASE 1)

Your job in this opening turn: surface your observations AND commit to your single
best suspect. You are the crew's first mover — a decisive, grounded accusation
drives the meeting toward the impostor; a non-answer ends it. You will almost
always have something — a player you saw near the body, someone whose movements
do not add up, a contradiction in someone's account. That is enough to name them.

## Meeting context
- You are: `p-3`
- Current tick: 412
- Meeting trigger: p-3 reported body body-p-2-1 at tick 410

## Living players (the only valid accusation targets)
You may ONLY accuse a player on the LIVING list below. Players found dead or
previously ejected are out of the game and naming one wastes your turn; your
own id is not listed because you cannot accuse yourself.

`p-1`, `p-5`
DEAD or EJECTED -- do NOT accuse: `p-2`. They are out of the game.


## Your memory (rendered view)
## Your role: CREWMATE
## Tasks completed (global): 3 / 12

## Recent observations (most salient first):
- [tick 410] You discovered p-2's body in MEDBAY.
- [tick 395] You saw p-5 in ELECTRICAL.

## Your current beliefs:
- p-5: suspicion 0.70

## What to produce
Emit exactly one JSON object that validates against the `MeetingTurn`
schema. The meeting manager is authoritative for the identity fields and
overrides whatever you emit for them, so emit a placeholder for each and put
your real turn in the content fields.

Identity fields (emit a placeholder; the manager overrides each):
- `turn_id`: any non-empty string (e.g. `"t"`).
- `turn_index`: any integer (e.g. `0`).
- `speaker`: any non-empty string (your own player id is fine).
- `turn_kind`: the string `"opening"`.
- `reply_to`: `null` (the opening turn answers no prior turn).

Content fields (your actual turn):
- `observations`: an ordered list of first-hand observations *you* made. Each
  entry is one of the discriminated union variants below; use the `type`
  string exactly as shown.
    - `{"type": "saw_player", "tick": <int>, "subject": "<player_id>", "room": "<room_id>", "co_present": ["<player_id>", ...]}`
    - `{"type": "completed_task", "tick": <int>, "task_id": "<task_id>", "room": "<room_id>"}`
    - `{"type": "found_body", "tick": <int>, "body_of": "<player_id>", "room": "<room_id>"}`
  Only include observations whose `tick` matches an event that appears in
  the rendered memory above. If you discovered the body, lead with the
  `found_body` observation. Fabricated or unsupported ticks will be rejected
  by validation. List each sighting once -- never repeat an observation
  entry.
- `claims`: an ordered list of higher-level claims. Each entry is one of:
    - `{"type": "alibi", "subject": "p-3", "from_tick": <int>, "to_tick": <int>, "room": "<room_id>", "evidence": ["<short evidence ref>", ...]}`
      (use chronological ticks: `from_tick <= to_tick`).
    - `{"type": "accusation", "against": "<player_id>", "confidence": <0.0..1.0>, "reason": "<short reason>"}`
    - `{"type": "corroboration", "supports": "<player_id>", "on_tick": <int>, "reason": "<short reason>"}`
  To accuse, add exactly one `accusation` claim naming your single best
  suspect. To stay unsure, add no `accusation` claim and write the word
  "unsure" in `free_text` (a self-alibi is fine).
- `free_text`: at most 2-3 sentences stating your single conclusion -- what
  you would say aloud to the table. Do NOT narrate or second-guess your reasoning:
  no step-by-step deliberation, no weighing of alternatives; state your
  conclusion and the single strongest signal behind it. Do not duplicate the
  entire `observations` list here.

## Reasoning guidelines
- **Name one suspect.** Pick the single player your evidence most points to —
  the one you saw near the body, in a suspicious place at a suspicious time, or
  whose account conflicts with what you observed. The chain passes the floor to
  the player you accuse. Do not stack several accusations into one opening.
- **Ground every accusation in a REAL observation.** Your accusation must rest on
  something you actually recorded — a sighting, a co-presence near the body, a
  contradiction. Never name a player you have no recorded reason to suspect; a
  baseless accusation is as harmful as silence. (This is the one hard limit on
  being decisive.)
- **Set confidence to your honest read** — circumstantial leads (proximity,
  timing) around 0.6-0.7, hard signals (a witnessed kill or vent, a directly
  contradicted alibi) above 0.8. Do not round your confidence down to avoid
  committing; a real circumstantial lead is worth naming at its true confidence.
- **Cite ticks from memory.** Every observation refers to a tick that appears in
  the rendered memory view. Never invent ticks, rooms, or co-present players.
- **Lead with the strongest signal.** If you discovered a body, report it first;
  if you witnessed a kill or a vent, report that. If you saw ANY player near the
  body, in a suspicious spot, or contradicting another's account, name them. An
  alibi-only turn is acceptable only if you genuinely witnessed nothing relevant.
- **Reason only from what you know.** Use only the rendered memory and the
  public transcript. Do not assume facts about other players' roles, kill
  attribution, or hidden vent moves you did not personally witness.
- **Stay in role.** You are a crewmate. Do not claim to be the impostor and
  do not invent hidden information you "would have" if you were."""

# The two paragraphs the v6 emergency branch swaps in. The emergency render
# must equal the body render with EXACTLY these two paragraph substitutions
# (plus the echoed ``meeting_trigger`` input) — pinning the branch as
# additive: no shared line moved.
_BODY_INTRO_PARAGRAPH = (
    "You are an AI agent playing a social-deduction simulation. You are a\n"
    "**crewmate**. A meeting has been called and you are the **opening speaker**\n"
    "(turn 0): you reported the body or called the emergency, so you speak first.\n"
    "State what you saw and name the single player your evidence most points to. Your\n"
    "job is to catch the impostor; a non-answer hands them a free round and another\n"
    "kill. Only withhold an accusation if you genuinely recorded nothing pointing at\n"
    'anyone -- and if so, you MUST write the word "unsure" in your `free_text`.'
)

_EMERGENCY_INTRO_PARAGRAPH = (
    "You are an AI agent playing a social-deduction simulation. You are a\n"
    "**crewmate**. YOU called this emergency meeting and you are the **opening\n"
    "speaker** (turn 0): no body was reported -- you pressed the button because your\n"
    "own observations point at someone. State who you suspect and the first-hand\n"
    "basis for it. Your job is to catch the impostor; a meeting called on suspicion\n"
    "with no named suspect hands them a free round and another kill. Only withhold\n"
    "an accusation if you genuinely cannot back one -- and if so, you MUST write the\n"
    'word "unsure" in your `free_text`.'
)

_BODY_JOB_PARAGRAPH = (
    "Your job in this opening turn: surface your observations AND commit to your single\n"
    "best suspect. You are the crew's first mover — a decisive, grounded accusation\n"
    "drives the meeting toward the impostor; a non-answer ends it. You will almost\n"
    "always have something — a player you saw near the body, someone whose movements\n"
    "do not add up, a contradiction in someone's account. That is enough to name them."
)

_EMERGENCY_JOB_PARAGRAPH = (
    "Your job in this opening turn: state why you called the meeting and commit to\n"
    "your single best suspect. You spent the crew's one emergency call on this -- a\n"
    "decisive, grounded accusation makes it count; a non-answer wastes it. Lead with\n"
    "the suspicion that crossed the line: the first-hand observations that drove you\n"
    "to the button -- a player whose movements do not add up, a suspicious\n"
    "co-presence, a contradiction in someone's account. That is enough to name them.\n"
    "No body was found in this meeting -- do NOT emit a `found_body` observation. Your\n"
    "`observations` are the sightings, co-presences, and contradictions behind your\n"
    "suspicion, never a body discovery."
)


class TestCrewmateReportEmergencyBranch:
    """Task 10.8/10.11 golden pins: emergency branch + body-branch stability.

    Task 10.11 (audit-2026-06-13-1816 B-B-1) bumped v6 -> v7 with a single
    emergency-branch change -- the emergency job paragraph now leads with the
    suspicion that crossed the line and FORBIDS a found_body observation. The
    body-report branch stays byte-identical to v5/v6 apart from the version
    marker, and the emergency render is still exactly the two-paragraph swap
    (intro + job) off the body render.
    """

    @staticmethod
    def _render(meeting_trigger: str) -> str:
        return crewmate_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger=meeting_trigger,
            rendered_memory=_STUB_CREWMATE_MEMORY,
            public_transcript="",
            living_ids=_GOLDEN_LIVING_IDS,
            dead_ids=_GOLDEN_DEAD_IDS,
        )

    def test_body_branch_renders_byte_identically_to_v5_modulo_marker(self) -> None:
        # The golden pin behind the "body-report branch is byte-unchanged"
        # contract: a body-meeting render under v6 equals the captured v5
        # render byte-for-byte once the version-marker line is accounted
        # for. The marker must move with DEFAULT_PROMPT_VERSIONS (replay
        # provenance), so it is the one permitted difference.
        prompt = self._render(_GOLDEN_BODY_TRIGGER)

        expected = _CREWMATE_V5_BODY_GOLDEN.replace(
            "Prompt: crewmate_report.v5 (DESIGN.md §5.2 PHASE 1)",
            "Prompt: crewmate_report.v7 (DESIGN.md §5.2 PHASE 1)",
        )
        assert prompt == expected

    def test_emergency_branch_is_exactly_the_two_paragraph_swap(self) -> None:
        # The emergency-branch golden, constructed rather than duplicated:
        # swapping the two branched paragraphs (and the echoed trigger
        # input) into the body render must reproduce the emergency render
        # byte-for-byte. Anything else — a shared line edited, a third
        # branch — breaks the equality.
        body = self._render(_GOLDEN_BODY_TRIGGER)
        emergency = self._render(_GOLDEN_EMERGENCY_TRIGGER)

        assert _BODY_INTRO_PARAGRAPH in body
        assert _BODY_JOB_PARAGRAPH in body
        expected = (
            body.replace(_BODY_INTRO_PARAGRAPH, _EMERGENCY_INTRO_PARAGRAPH)
            .replace(_BODY_JOB_PARAGRAPH, _EMERGENCY_JOB_PARAGRAPH)
            .replace(_GOLDEN_BODY_TRIGGER, _GOLDEN_EMERGENCY_TRIGGER)
        )
        assert emergency == expected

    def test_emergency_opening_renders_called_on_suspicion_frame(self) -> None:
        # The frame the task contract specifies: the opener is the caller,
        # the meeting is body-less and called on suspicion, and the model
        # must state who it suspects and the first-hand basis — or unsure.
        prompt = self._render(_GOLDEN_EMERGENCY_TRIGGER)

        assert "YOU called this emergency meeting" in prompt
        assert "no body was reported" in prompt
        assert "State who you suspect and the first-hand" in prompt
        assert '"unsure" in `free_text`' in prompt
        # Task 10.11: the emergency opening must NOT present a found_body --
        # lead with the suspicion that crossed the line.
        assert "Lead with\nthe suspicion that crossed the line" in prompt
        assert "do NOT emit a `found_body` observation" in prompt
        assert "never a body discovery" in prompt
        # The accuse-or-unsure hard rule and roster constraints stay shared.
        assert "must EITHER include one `accusation` claim OR say" in prompt
        assert "You may ONLY accuse a player on the LIVING list below" in prompt

    def test_body_branch_never_carries_the_no_found_body_directive(self) -> None:
        # The found_body suppression is emergency-only: a body-report opening
        # leads WITH the found_body, so the directive must never leak into the
        # body branch (the byte-stable contract, asserted positively).
        prompt = self._render(_GOLDEN_BODY_TRIGGER)

        assert "do NOT emit a `found_body` observation" not in prompt
        assert "If you discovered the body, lead with the" in prompt

    def test_body_trigger_never_selects_emergency_frame(self) -> None:
        # A report-shaped description — and any ad-hoc trigger string that
        # does not contain the orchestrator's emergency phrase — renders
        # the body-report branch.
        for trigger in (_GOLDEN_BODY_TRIGGER, "trigger"):
            prompt = self._render(trigger)
            assert "YOU called this emergency meeting" not in prompt
            assert "you reported the body or called the emergency" in prompt

    def test_branch_keys_on_the_orchestrator_phrase(self) -> None:
        # The template's branch condition is the documented orchestrator
        # phrase, verbatim. If either end rewords, this fails here or in
        # the orchestrator-side description pin.
        assert _EMERGENCY_TRIGGER_PHRASE in _GOLDEN_EMERGENCY_TRIGGER
        prompt = self._render(f"p-9 {_EMERGENCY_TRIGGER_PHRASE} at tick 7")
        assert "YOU called this emergency meeting" in prompt


class TestImpostorReportTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        # The impostor opening template carries its visible version marker
        # (bumped to v5 in Task 10.14: the anticipatory-cover branch; v4 added
        # the accuse-or-declare-unsure hard rule, the anti-repetition line, and
        # the gated living/DEAD roster block) and the explicit role line.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "impostor_report_v5" in prompt
        assert "Your role for this match is IMPOSTOR" in prompt

    def test_renders_memory_into_prompt(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert _STUB_IMPOSTOR_MEMORY.strip() in prompt

    def test_teammate_block_renders_only_when_non_empty(self) -> None:
        # The 7.12 firewall block renders only for a coordinating impostor.
        without = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )
        with_team = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-5",),
        )

        assert "fellow impostors" not in without.lower()
        assert "fellow impostors" in with_team.lower()
        assert "p-5" in with_team

    def test_accuse_or_declare_unsure_hard_rule_is_present(self) -> None:
        # Task 10.3 (audit gp-9 H-H-1): the same §5.2 PHASE 1 hard rule as
        # the crewmate opening -- the manager validates impostor openings
        # identically, so the impostor prompt must carry the instruction.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "must EITHER include one `accusation` claim OR say" in prompt
        assert '"unsure" in `free_text`' in prompt

    def test_anti_repetition_line_is_present(self) -> None:
        # Task 10.3 (audit gp-9 H-H-2): the structured-array repetition loop
        # nudge, carried by all three turn templates.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "List each sighting once" in prompt

    def test_living_roster_renders_and_constrains_accusations(self) -> None:
        # New in impostor_report_v4 (Task 10.3): the living-roster block was
        # crewmate-only, and 12 of the 18 dead-id accusation drops were
        # impostor-spoken (audit gp-9 D-D-8) -- the impostor opening now
        # renders the same roster constraint as the crewmate one.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
            living_ids=("p-1", "p-5"),
        )

        assert "You may ONLY accuse a player on the LIVING list below" in prompt
        assert "`p-1`, `p-5`" in prompt

    def test_dead_roster_renders_as_do_not_accuse_line(self) -> None:
        # Task 10.3 (audit gp-9 H-H-3/D-D-8): the explicit DEAD negative
        # list under the living roster.
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-8",),
        )

        assert "DEAD or EJECTED -- do NOT accuse: `p-8`." in prompt

    def test_render_without_rosters_validates_under_strict_undefined(self) -> None:
        # Both roster inputs follow the optional-kwarg pattern: a raw render
        # omitting living_ids and dead_ids entirely still validates and
        # omits both blocks.
        prompt = _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )

        assert "LIVING list" not in prompt
        assert "DEAD or EJECTED" not in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # impostor_report.j2 references ``rendered_memory`` and
        # ``public_transcript``. Render through the raw environment
        # with only one of them to exercise StrictUndefined directly.
        with pytest.raises(UndefinedError):
            _ENV.get_template(IMPOSTOR_REPORT_TEMPLATE).render(
                # rendered_memory deliberately omitted.
                public_transcript="",
            )

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
        prompt = impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger="trigger",
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


# ---------------------------------------------------------------------------
# Task 10.14 -- the impostor_report v5 anticipatory-cover branch (DESIGN.md
# §3.4, §4.5, §5.3; audit-2026-06-13-1816 D-D-1/D-D-7;
# experiments/lab/report-deception-battery-2.md P1/P3). Golden pins for the
# cover frame and the body-vs-emergency branch structure.
# ---------------------------------------------------------------------------

# The exact anticipatory-cover block the v5 body-report opening inserts. It is
# the ONLY difference between the body and emergency branches (the trigger string
# itself is not rendered into the impostor opening), so removing it from a body
# render must reproduce the emergency render byte-for-byte. Pinned here against
# the template and re-derivable from orchestrator.game._build_meeting_trigger's
# "called an emergency meeting" branch substring.
_IMPOSTOR_V5_COVER_BLOCK = (
    "## Prepare your cover (a body was found)\n"
    "A body has been reported, so the table will try to pin down where everyone was\n"
    "when it happened. Before you compose your turn, DECIDE on the account your\n"
    "`alibi` will give: ONE room and tick-window AWAY from the body's room and the\n"
    "tick it happened, and commit to it. Where the rendered memory already puts you\n"
    "somewhere sheltered -- a room you saw another player in, well clear of the body\n"
    "-- lean on that; otherwise give a plausible quiet spot. State the SAME room and\n"
    "window every time you are asked this meeting; an account that drifts to a\n"
    "different room or tick is what exposes an impostor. Never place yourself in the\n"
    "body's room or around its tick, and do not volunteer having seen the victim\n"
    "there.\n\n"
)

_IMPOSTOR_COVER_BODY_TRIGGER = "p-3 reported body body-p-2-7 at tick 410"
_IMPOSTOR_COVER_EMERGENCY_TRIGGER = "p-3 called an emergency meeting at tick 320"


class TestImpostorReportV5AnticipatoryCover:
    """The v5 anticipatory-cover branch (Task 10.14). On a body-report opening
    the impostor opening renders the perform-from-a-goal cover directive
    (battery-2 P3) and PINS the cover room/window (battery-2 P1); the emergency
    branch -- impostors gain no button this wave -- keeps the v4 frame.
    """

    @staticmethod
    def _render(meeting_trigger: str) -> str:
        return impostor_report_prompt(
            agent_id="p-3",
            current_tick=412,
            meeting_trigger=meeting_trigger,
            rendered_memory=_STUB_IMPOSTOR_MEMORY,
            public_transcript="",
            fellow_impostor_ids=("p-7",),
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2",),
        )

    def test_body_report_opening_renders_the_cover_frame(self) -> None:
        # Given a recent kill (a body report is on the table), the opening frames
        # "prepare an account that does NOT place you at the kill room/tick" --
        # the lab's perform-from-a-goal directive, not a verbatim script.
        prompt = self._render(_IMPOSTOR_COVER_BODY_TRIGGER)

        assert "## Prepare your cover (a body was found)" in prompt
        # Perform-from-a-goal (battery-2 P3): decide on an account away from the
        # scene -- leaning on memory where it helps, otherwise inventing a quiet
        # spot (the renderer does not expose the impostor's own room history).
        assert "DECIDE on the account your" in prompt
        assert "ONE room and tick-window AWAY from the body's room" in prompt
        assert "otherwise give a plausible quiet spot." in prompt
        assert "do not volunteer having seen the victim" in prompt
        # PINNED cover (battery-2 P1): commit to ONE room/window, do not drift.
        assert "commit to it." in prompt
        assert "every time you are asked this meeting" in prompt
        assert "different room or tick is what exposes an impostor" in prompt
        # The v4 invariants stay intact under the new branch.
        assert "impostor_report_v5" in prompt
        assert "must EITHER include one `accusation` claim OR say" in prompt

    def test_emergency_opening_skips_the_cover_frame(self) -> None:
        # An emergency trigger (no body) renders no body-cover directive -- the
        # impostor opening keeps the v4 frame. Impostors gain no button this wave,
        # so this branch is defensive, but the firewall/roster invariants hold.
        prompt = self._render(_IMPOSTOR_COVER_EMERGENCY_TRIGGER)

        assert "Prepare your cover" not in prompt
        assert "AWAY from the body's room" not in prompt
        assert "impostor_report_v5" in prompt
        assert "must EITHER include one `accusation` claim OR say" in prompt

    def test_cover_block_is_the_only_branch_difference(self) -> None:
        # The structural golden: the cover block is the ENTIRE difference between
        # the two branches (the trigger string is not rendered into the impostor
        # opening). Removing it from the body render reproduces the emergency
        # render byte-for-byte -- any other drift breaks the equality.
        body = self._render(_IMPOSTOR_COVER_BODY_TRIGGER)
        emergency = self._render(_IMPOSTOR_COVER_EMERGENCY_TRIGGER)

        assert _IMPOSTOR_V5_COVER_BLOCK in body
        assert _IMPOSTOR_V5_COVER_BLOCK not in emergency
        assert body.replace(_IMPOSTOR_V5_COVER_BLOCK, "", 1) == emergency

    def test_cover_frame_never_names_a_teammate(self) -> None:
        # Firewall (DESIGN.md §4.7; battery-2 P5): the cover directive is generic
        # -- it never instructs naming or implicating a teammate, and the 7.12
        # teammate block stays the deterministic backstop.
        prompt = self._render(_IMPOSTOR_COVER_BODY_TRIGGER)

        # The teammate id appears ONLY inside the dedicated "never betray them"
        # block, never inside the cover frame (the exact block, pinned above).
        assert "p-7" not in _IMPOSTOR_V5_COVER_BLOCK
        assert _IMPOSTOR_V5_COVER_BLOCK in prompt
        assert "never accuse" in prompt.lower()


class TestAccusationRoundTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "accusation_round.v8" in prompt
        assert "reactive accusation chain" in prompt

    def test_reply_turn_frames_the_accuser(self) -> None:
        # A reply turn names the prior turn's speaker so the model knows
        # who it is answering (the "who accused me" context, Task 8.8).
        prompt = accusation_round_prompt(
            agent_id="p-5",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "reply" in prompt
        assert "`p-1`" in prompt  # the accuser

    def test_opt_in_turn_is_terminal_and_non_chaining(self) -> None:
        # An opt-in turn frames itself as terminal (no prior_turn) and
        # explicitly does not extend the chain (DESIGN.md §5.2 PHASE 3).
        prompt = accusation_round_prompt(
            agent_id="p-7",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
        )

        assert "opt-in" in prompt.lower()
        assert "terminal turn" in prompt
        assert "does NOT extend" in prompt

    def test_renders_transcript_turns(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "stub-opening-from-p-1" in prompt
        assert "stub-reply-from-p-5" in prompt
        # The turn ids anchor a vote's primary_reason_id.
        assert "m-1:turn-0" in prompt
        assert "m-1:turn-1" in prompt

    def test_renders_contradictions_section(self) -> None:
        contradictions = (
            ContradictionRef(
                contradiction_id="c-1",
                kind="alibi_conflict",
                event_a_id="m-1:turn-0:claim-0",
                event_b_id="m-1:turn-1:claim-0",
                subjects=("p-5",),
                description="alibi conflict for p-5 around tick 405",
            ),
        )

        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=contradictions,
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "alibi_conflict" in prompt
        assert "alibi conflict for p-5 around tick 405" in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        with pytest.raises(UndefinedError):
            _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
                agent_id="p-3",
                rendered_memory=_STUB_CREWMATE_MEMORY,
                # transcript deliberately omitted; the turn loop trips.
                contradictions=(),
                prior_turn=None,
                turn_kind="reply",
            )

    def test_living_roster_renders_and_constrains_accusations(self) -> None:
        # Task 9.9 (audit gp-3): the living-roster accusation list (living
        # players minus this speaker, threaded like the vote ballot's
        # candidate_targets) renders into reply / opt-in prompts with the
        # only-accuse-the-living instruction.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            living_ids=("p-1", "p-5"),
        )

        assert "You may ONLY accuse a player on the LIVING list below" in prompt
        assert "`p-1`, `p-5`" in prompt

    def test_free_text_length_discipline_is_present(self) -> None:
        # Task 9.9 (audit gp-3): with think:false the 9B relocates its
        # deliberation into free_text and overruns the frozen 2048 turn cap,
        # so the template must carry the length discipline.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "at most 2-3 sentences stating your single conclusion" in prompt
        assert "Do NOT narrate or second-guess your reasoning" in prompt

    def test_render_without_living_ids_validates_under_strict_undefined(
        self,
    ) -> None:
        # The roster block is guarded with `is defined` (the optional-kwarg
        # pattern, like fellow_impostor_ids), so a raw render that omits
        # living_ids entirely still validates under StrictUndefined and
        # simply omits the block.
        prompt = _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "LIVING list" not in prompt

    def test_anti_repetition_line_is_present(self) -> None:
        # Task 10.3 (audit gp-9 H-H-2): the structured-array repetition loop
        # nudge, carried by all three turn templates.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "List each sighting once" in prompt

    def test_dead_roster_renders_as_do_not_accuse_line(self) -> None:
        # Task 10.3 (audit gp-9 H-H-3/D-D-8): the explicit DEAD negative
        # list under the living roster, on reply / opt-in turns too.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            living_ids=("p-1", "p-5"),
            dead_ids=("p-2", "p-9"),
        )

        assert "`p-1`, `p-5`" in prompt
        assert "DEAD or EJECTED -- do NOT accuse: `p-2`, `p-9`." in prompt

    def test_render_without_dead_ids_validates_under_strict_undefined(
        self,
    ) -> None:
        # dead_ids follows the same optional-kwarg pattern as living_ids: a
        # raw render that omits it entirely still validates and omits the
        # DEAD line (the living roster renders alone).
        prompt = _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            living_ids=("p-1", "p-5"),
        )

        assert "`p-1`, `p-5`" in prompt
        assert "DEAD or EJECTED" not in prompt

    def test_renders_speaker_self_alibi_example_with_own_id(self) -> None:
        # The template must anchor the self-alibi example to the speaker's
        # own player id so the model emits `"subject": "p-3"` rather than a
        # placeholder that DESIGN.md §5.4 contradiction detection cannot
        # match across speakers (Task 3.20).
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert '"subject": "p-3"' in prompt

    def test_fake_provider_response_parses_into_meeting_turn(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=MeetingTurn,
                max_tokens=512,
                temperature=0.0,
            )
        )

        parsed = MeetingTurn.model_validate_json(response.text)
        assert isinstance(parsed, MeetingTurn)


# The exact cover-consistency directive the v8 reply branch inserts for an
# impostor. It is ported verbatim from impostor_report.j2's v5 cover frame so the
# opening and reply paths stay one wording (Task 11.2); reused as the structural
# pin here. Mirrors _IMPOSTOR_V5_COVER_BLOCK above, by design.
_ACCUSATION_V8_COVER_BLOCK = (
    "## Prepare your cover (a body was found)\n"
    "A body has been reported, so the table will try to pin down where everyone was\n"
    "when it happened. Before you compose your turn, DECIDE on the account your\n"
    "`alibi` will give: ONE room and tick-window AWAY from the body's room and the\n"
    "tick it happened, and commit to it. Where the rendered memory already puts you\n"
    "somewhere sheltered -- a room you saw another player in, well clear of the body\n"
    "-- lean on that; otherwise give a plausible quiet spot. State the SAME room and\n"
    "window every time you are asked this meeting; an account that drifts to a\n"
    "different room or tick is what exposes an impostor. Never place yourself in the\n"
    "body's room or around its tick, and do not volunteer having seen the victim\n"
    "there.\n"
)


class TestAccusationRoundCoverDirective:
    """The v8 cover-consistency directive (Task 11.2; DESIGN.md §5.2;
    experiments/lab/report-vent-escape-lab.md). On the REPLY turn -- the only
    turn an impostor ever speaks -- an impostor reply renders the
    cover-consistency directive ported verbatim from impostor_report's body-report
    opening; crewmate replies and every opt-in turn render it nowhere.
    """

    def test_impostor_reply_renders_the_cover_block(self) -> None:
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            is_impostor=True,
        )

        # The directive is present verbatim and pins the single sheltered
        # room/window reused every turn (the residual self-pair drift fix).
        assert _ACCUSATION_V8_COVER_BLOCK in prompt
        assert "## Prepare your cover (a body was found)" in prompt
        assert "ONE room and tick-window AWAY from the body's room" in prompt
        assert "every time you are asked this meeting" in prompt
        assert "different room or tick is what exposes an impostor" in prompt
        # It never names a teammate -- the directive is generic (firewall).
        assert "p-7" not in _ACCUSATION_V8_COVER_BLOCK

    def test_cover_block_text_matches_impostor_report_wording(self) -> None:
        # The two paths must stay one wording: the v8 reply directive is the v5
        # impostor-opening cover frame verbatim (modulo the trailing blank line
        # the opening template adds before the next block).
        assert (
            _ACCUSATION_V8_COVER_BLOCK == _IMPOSTOR_V5_COVER_BLOCK.rstrip("\n") + "\n"
        )

    def test_crewmate_reply_omits_the_cover_block(self) -> None:
        # Default is_impostor=False (the crewmate reply path) renders no cover
        # directive -- byte-unchanged from the pre-v8 reply body.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "Prepare your cover" not in prompt
        assert _ACCUSATION_V8_COVER_BLOCK not in prompt

    def test_impostor_opt_in_omits_the_cover_block(self) -> None:
        # The block is scoped to the reply branch only: the opt-in turn is
        # terminal (the lab residual is opening<->reply drift), so even an
        # impostor opt-in renders no cover directive.
        prompt = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=None,
            turn_kind="opt_in",
            is_impostor=True,
        )

        assert "Prepare your cover" not in prompt
        assert _ACCUSATION_V8_COVER_BLOCK not in prompt

    def test_cover_block_is_the_only_impostor_reply_difference(self) -> None:
        # The structural golden: the cover block is the ENTIRE difference between
        # an impostor reply and a crewmate reply. Removing it from the impostor
        # render reproduces the crewmate render byte-for-byte.
        impostor = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            is_impostor=True,
        )
        crewmate = accusation_round_prompt(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
            is_impostor=False,
        )

        assert _ACCUSATION_V8_COVER_BLOCK in impostor
        assert _ACCUSATION_V8_COVER_BLOCK not in crewmate
        # The block renders with a leading blank line (its markdown separator);
        # removing both reproduces the crewmate reply byte-for-byte.
        assert impostor.replace("\n" + _ACCUSATION_V8_COVER_BLOCK, "", 1) == crewmate

    def test_render_without_is_impostor_validates_under_strict_undefined(
        self,
    ) -> None:
        # is_impostor follows the optional-kwarg `is defined and` pattern (like
        # fellow_impostor_ids), so a raw render that omits it entirely still
        # validates under StrictUndefined and simply omits the cover block.
        prompt = _ENV.get_template(ACCUSATION_ROUND_TEMPLATE).render(
            agent_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradictions=(),
            prior_turn=_opening_turn(),
            turn_kind="reply",
        )

        assert "Prepare your cover" not in prompt


class TestVoteBallotTemplate:
    def test_rendered_output_is_non_empty(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert prompt
        assert len(prompt) > 100

    def test_rendered_output_contains_version_marker(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        # vote_ballot.j2 carries an explicit visible version marker in its
        # body, bumped to v4 in Task 8.16 (the `primary_reason_id` example
        # is now sourced from the live transcript). A regression that bumps
        # the version without updating the test is the desired failure mode.
        assert "vote_ballot/v5" in prompt

    def test_renders_voter_and_candidates(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "`p-3`" in prompt
        assert "`p-1`" in prompt
        assert "`p-2`" in prompt

    def test_renders_transcript_turns(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "stub-opening-from-p-1" in prompt
        assert "stub-reply-from-p-5" in prompt
        # The opening turn's accusation is surfaced for the voter.
        assert "accuses `p-5`" in prompt

    def test_primary_reason_id_example_is_sourced_from_transcript(self) -> None:
        # Task 8.16 (DESIGN.md §5.5; audit gp-3): the decision-rule example
        # for `primary_reason_id` must cite a REAL turn id from the rendered
        # transcript, never the old hardcoded `m-7:turn-4` (which the 7B
        # model copied verbatim into other meetings' ballots).
        transcript = _stub_transcript()
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=transcript,
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        # The example is the first turn's real id; the hardcoded one is gone.
        assert transcript.turns[0].turn_id == "m-1:turn-0"
        assert '`"m-1:turn-0"`' in prompt
        assert "m-7:turn-4" not in prompt

    def test_primary_reason_id_example_omitted_for_empty_transcript(self) -> None:
        # With no turns there is no real id to cite, so the example clause is
        # dropped rather than falling back to a hardcoded (dangling) id.
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "m-7:turn-4" not in prompt
        assert "primary_reason_id" in prompt

    def test_renders_suspicion_graph_entries(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.4, trust=0.5),
                SuspicionEntry(player_id="p-2", suspicion=0.7, trust=0.3),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "suspicion 0.40" in prompt
        assert "suspicion 0.70" in prompt
        assert "trust 0.50" in prompt
        assert "trust 0.30" in prompt

    def test_gate_max_ignores_high_suspicion_non_candidate(self) -> None:
        """A dead/ejected player's belief row must not trip the §4.6 eject gate.

        ``suspicion_graph_for_meeting`` snapshots every ``known_players()`` row,
        including players who are no longer living ejection targets. The v5 gate
        computes its max over ``candidate_targets`` (the living set) so a
        high-suspicion DEAD player cannot force a "MUST eject" verdict when no
        LIVING candidate crosses the threshold — that would otherwise coerce a
        ballot onto an unrelated living player.
        """

        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.40, trust=0.5),
                SuspicionEntry(player_id="p-2", suspicion=0.45, trust=0.5),
                # p-9 is dead/ejected — still in the belief snapshot, NOT a
                # candidate target — and carries the only above-threshold score.
                SuspicionEntry(player_id="p-9", suspicion=0.95, trust=0.5),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert 'you MUST set `target` to `"SKIP"`' in prompt
        assert "you MUST vote to eject" not in prompt

    def test_gate_max_fires_on_above_threshold_candidate(self) -> None:
        """Sibling of the dead-player case: a LIVING candidate at/above the
        threshold still yields a "MUST eject" verdict (conversion preserved)."""

        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.40, trust=0.5),
                SuspicionEntry(player_id="p-2", suspicion=0.72, trust=0.5),
            ),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )

        assert "you MUST vote to eject" in prompt
        assert 'you MUST set `target` to `"SKIP"`' not in prompt

    def test_missing_kwarg_raises_under_strict_undefined(self) -> None:
        # vote_ballot.j2 iterates ``transcript.turns`` near the top
        # of the body; omitting ``transcript`` must trip StrictUndefined
        # as the for-loop dereferences the missing variable.
        with pytest.raises(UndefinedError):
            _ENV.get_template(VOTE_BALLOT_TEMPLATE).render(
                voter_id="p-3",
                rendered_memory=_STUB_CREWMATE_MEMORY,
                # transcript deliberately omitted.
                contradiction_flags=(),
                suspicion_graph=(),
                candidate_targets=("p-1", "p-2"),
                skip_confidence_threshold=0.6,
            )

    def test_fake_provider_response_parses_into_schema(self) -> None:
        prompt = vote_ballot_prompt(
            voter_id="p-3",
            rendered_memory=_STUB_CREWMATE_MEMORY,
            transcript=_stub_transcript(),
            contradiction_flags=(),
            suspicion_graph=(),
            candidate_targets=("p-1", "p-2"),
            skip_confidence_threshold=0.6,
        )
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt=prompt,
                schema=VoteBallot,
                max_tokens=256,
                temperature=0.0,
            )
        )

        parsed = VoteBallot.model_validate_json(response.text)
        assert isinstance(parsed, VoteBallot)
