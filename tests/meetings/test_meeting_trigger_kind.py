"""The meeting layer reads the trigger's typed kind, never its wording.

``MeetingTrigger.kind`` is the engine's ``MeetingTriggeredEvent.trigger``, copied
by ``orchestrator.game._build_meeting_trigger`` and read by every trigger
decision in ``meetings.manager`` through ``_trigger_is_emergency``. The prompt
templates still branch on the emergency phrase inside the description they
receive, so the lockstep pin here holds the two answers equal on every trigger
the builder constructs. Each gate below runs beside a planted or perturbed input
that has to make it fire.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import re
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal, TypeGuard, get_args

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

import eval.reasoning_evidence as reasoning_evidence
import meetings.manager as manager_module
from engine.entities import BodyState
from engine.events import EngineEvent, MeetingTriggeredEvent
from engine.world import WorldState, load_canonical_map
from eval.replay_walk import MeetingOpened
from meetings.manager import (
    EMERGENCY_TRIGGER_PHRASE,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingTrigger,
    ReporterContext,
    _trigger_is_emergency,  # noqa: PLC2701
)
from meetings.schemas import (
    ContradictionRef,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MoveWitnessRecord,
    PlayerId,
    SightingRecord,
    VentWitnessRecord,
)
from meetings.transcript import MeetingTriggerKind
from observation.body_ids import public_body_id
from orchestrator.game import _build_meeting_trigger  # noqa: PLC2701
from orchestrator.seeder import seed_initial_state
from tests._helpers.committed import meeting_trigger_kind
from tests.meetings._manager_helpers import (
    _crew_participants,
    _crewmate_report_prompt,
    _extract_marker,
    _impostor_report_prompt,
    _ScriptedLLMClient,
    _statement_prompt,
    _turn_json,
    _vote_json,
    _vote_prompt,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MANAGER_SOURCE = _REPO_ROOT / "meetings" / "manager.py"
_PROMPTS_DIR = _REPO_ROOT / "agents" / "strategic" / "prompts"
_SERVED_SET = "qwen3_6_27b"
_SERVED_BRANCH_TEMPLATES = (
    "crewmate_report.j2",
    "impostor_report.j2",
    "impostor_report_roll_call.j2",
)
_KINDS: tuple[MeetingTriggerKind, ...] = get_args(MeetingTriggerKind)


def _templates_answer(trigger: MeetingTrigger) -> MeetingTriggerKind:
    """What the opening templates decide: the emergency phrase in the description."""

    return "emergency" if EMERGENCY_TRIGGER_PHRASE in trigger.description else "report"


# --------------------------------------------------------------------------- #
# The kind is typed and required.                                              #
# --------------------------------------------------------------------------- #


def test_omitting_the_kind_raises_type_error() -> None:
    # Perturbed in Results: giving ``kind`` a default of "report" turns this red.
    with pytest.raises(TypeError, match="kind"):
        MeetingTrigger(  # type: ignore[call-arg]
            triggered_by="p-1",
            trigger_tick=8,
            description="p-1 called an emergency meeting at tick 8",
        )


def test_a_miscased_kind_raises_value_error() -> None:
    with pytest.raises(ValueError, match="'Emergency'"):
        MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=8,
            description="p-1 called an emergency meeting at tick 8",
            kind="Emergency",  # type: ignore[arg-type]
        )


@given(
    value=st.one_of(
        st.text().filter(lambda text: text not in _KINDS),
        st.none(),
        st.integers(),
        st.booleans(),
    )
)
def test_every_undeclared_kind_raises_value_error(value: object) -> None:
    with pytest.raises(ValueError, match="MeetingTrigger.kind must be one of"):
        MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=8,
            description="p-1 reported a body at tick 8",
            kind=value,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("kind", _KINDS)
def test_each_declared_kind_constructs_and_decides(kind: MeetingTriggerKind) -> None:
    trigger = MeetingTrigger(
        triggered_by="p-1", trigger_tick=8, description="anything", kind=kind
    )
    assert trigger.kind == kind
    assert _trigger_is_emergency(trigger) is (kind == "emergency")


# --------------------------------------------------------------------------- #
# The builder carries the engine's kind, and the lockstep pin.                 #
# --------------------------------------------------------------------------- #

_BodyMode = Literal["present", "consumed", "none"]


def _meeting_state(*, victim: PlayerId, body_id: str, present: bool) -> WorldState:
    state = seed_initial_state(
        seed=0, game_map=load_canonical_map(), num_players=9, num_impostors=2
    )
    bodies = (
        {
            body_id: BodyState(
                id=body_id,
                player_id=victim,
                room="MEDBAY",
                position=(0.0, 0.0),
                killed_by="p-9",
                discovered_by=None,
            )
        }
        if present
        else {}
    )
    return replace(state, phase="MEETING", bodies=bodies)


def _built(
    *,
    kind: MeetingTriggerKind,
    actor: PlayerId,
    tick: int,
    victim: PlayerId,
    body_mode: _BodyMode,
    temporal_observations: bool,
) -> tuple[MeetingTrigger, MeetingTriggerKind, MeetingTriggeredEvent]:
    body_id = f"body-{victim}-{max(0, tick - 3)}"
    event = MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=tick,
        actor=actor,
        trigger=kind,
        body_id=body_id if kind == "report" and body_mode != "none" else None,
    )
    state = _meeting_state(
        victim=victim, body_id=body_id, present=body_mode == "present"
    )
    trigger, _body_id, engine_kind = _build_meeting_trigger(
        state=state, events=(event,), temporal_observations=temporal_observations
    )
    return trigger, engine_kind, event


@pytest.mark.parametrize("kind", _KINDS)
def test_the_builder_copies_the_engine_kind(kind: MeetingTriggerKind) -> None:
    # Perturbed in Results: a builder that hard-codes kind="report" fails the
    # emergency case.
    trigger, engine_kind, event = _built(
        kind=kind,
        actor="p-3",
        tick=41,
        victim="p-2",
        body_mode="present",
        temporal_observations=False,
    )
    assert trigger.kind == event.trigger == kind
    assert engine_kind == trigger.kind


@pytest.mark.parametrize(
    ("kind", "body_mode", "temporal", "expected_description"),
    [
        ("emergency", "none", False, "p-3 called an emergency meeting at tick 41"),
        ("report", "present", False, "p-3 reported body body-p-2-38 at tick 41"),
        ("report", "consumed", True, "p-3 reported a body at tick 41"),
        ("report", "none", False, "p-3 reported a body at tick 41"),
        (
            "report",
            "present",
            True,
            f"p-3 reported body {public_body_id('p-2')} at tick 41",
        ),
    ],
)
def test_the_lockstep_pin_on_every_trigger_shape_the_builder_constructs(
    kind: MeetingTriggerKind,
    body_mode: _BodyMode,
    temporal: bool,
    expected_description: str,
) -> None:
    """The typed kind equals the templates' own substring test, shape by shape.

    Emergency; a report naming a present body; a report whose body was already
    consumed ("a body"); a report with no body id; a temporal report naming the
    public handle. The description is pinned too, so a shape the builder stops
    producing cannot pass by producing another.
    """

    trigger, _engine_kind, _event = _built(
        kind=kind,
        actor="p-3",
        tick=41,
        victim="p-2",
        body_mode=body_mode,
        temporal_observations=temporal,
    )
    assert trigger.description == expected_description
    assert trigger.kind == _templates_answer(trigger) == kind


@given(
    kind=st.sampled_from(_KINDS),
    actor=st.integers(min_value=1, max_value=15).map(lambda n: f"p-{n}"),
    victim=st.integers(min_value=1, max_value=15).map(lambda n: f"p-{n}"),
    tick=st.integers(min_value=0, max_value=5_000),
    body_mode=st.sampled_from(("present", "consumed", "none")),
    temporal=st.booleans(),
)
# Every example parses the map and seeds a world, so its wall time grows with
# machine load; the per-example deadline is off, as on the other costly properties.
@settings(deadline=None)
def test_the_lockstep_pin_holds_over_every_generated_engine_trigger(
    kind: MeetingTriggerKind,
    actor: PlayerId,
    victim: PlayerId,
    tick: int,
    body_mode: _BodyMode,
    temporal: bool,
) -> None:
    """A property over the engine's id shapes: seeded ``p-N`` players, any tick.

    Perturbed in Results: a builder whose report description carries the
    emergency phrase fails here.
    """

    trigger, engine_kind, event = _built(
        kind=kind,
        actor=actor,
        tick=tick,
        victim=victim,
        body_mode=body_mode,
        temporal_observations=temporal,
    )
    assert trigger.kind == event.trigger == engine_kind
    assert trigger.kind == _templates_answer(trigger)


def test_the_lockstep_check_itself_catches_a_disagreeing_trigger() -> None:
    # Planted: a report whose wording carries the emergency phrase. The
    # templates would render the emergency frame for it; the check must see that.
    planted = MeetingTrigger(
        triggered_by="p-1",
        trigger_tick=8,
        description=f"p-1 reported a body at tick 8 after p-4 {EMERGENCY_TRIGGER_PHRASE}",
        kind="report",
    )
    assert planted.kind != _templates_answer(planted)


# The templates' own branch: ``"<literal>" in meeting_trigger`` or ``not in``,
# single- or double-quoted, wherever it appears in a template.
_TEMPLATE_BRANCH = re.compile(
    r"""(?P<quote>["'])(?P<literal>.*?)(?P=quote)\s+(?:not\s+)?in\s+meeting_trigger\b"""
)


def _branch_literals(texts: dict[str, str]) -> list[tuple[str, str]]:
    return [
        (name, match.group("literal"))
        for name, text in sorted(texts.items())
        for match in _TEMPLATE_BRANCH.finditer(text)
    ]


def _template_problems(texts: dict[str, str]) -> list[str]:
    return [
        f"{name}: branches on {literal!r}, not the builder's emergency phrase"
        for name, literal in _branch_literals(texts)
        if literal != EMERGENCY_TRIGGER_PHRASE
    ]


def _committed_templates() -> dict[str, str]:
    return {
        str(path.relative_to(_REPO_ROOT)): path.read_text(encoding="utf-8")
        for path in sorted(_PROMPTS_DIR.rglob("*.j2"))
    }


def test_every_template_branch_literal_is_the_builders_phrase() -> None:
    templates = _committed_templates()
    literals = _branch_literals(templates)
    # Vacuity guard: each served opening template carries exactly one branch.
    served = [
        name for name, _literal in literals if Path(name).parent.name == _SERVED_SET
    ]
    assert sorted(Path(name).name for name in served) == sorted(
        _SERVED_BRANCH_TEMPLATES
    )
    assert _template_problems(templates) == []


def test_a_template_copy_with_an_edited_literal_is_caught() -> None:
    # Planted: the served crewmate opening with its branch literal edited.
    name = f"agents/strategic/prompts/{_SERVED_SET}/crewmate_report.j2"
    original = _committed_templates()[name]
    edited = original.replace(
        f'"{EMERGENCY_TRIGGER_PHRASE}" in meeting_trigger',
        '"called an emergency huddle" in meeting_trigger',
    )
    assert edited != original
    assert _template_problems({name: edited}) == [
        f"{name}: branches on 'called an emergency huddle', not the builder's "
        "emergency phrase"
    ]


# --------------------------------------------------------------------------- #
# The planted case: the wording no longer decides, seen through run().         #
# --------------------------------------------------------------------------- #

# A report whose description happens to contain the emergency wording.
_REPORT_WITH_THE_PHRASE = MeetingTrigger(
    triggered_by="p-1",
    trigger_tick=410,
    description=f"p-1 reported a body at tick 410 after p-4 {EMERGENCY_TRIGGER_PHRASE}",
    kind="report",
)
# Its mirror: an emergency call whose description never says so.
_EMERGENCY_WITHOUT_THE_PHRASE = MeetingTrigger(
    triggered_by="p-1",
    trigger_tick=410,
    description="p-1 pressed the meeting button at tick 410",
    kind="emergency",
)
_STALE_BODY = FoundBodyObservation(
    type="found_body", tick=406, body_of="p-9", room="STORAGE"
)


@dataclass
class _Seen:
    """What the manager handed each seam, in call order."""

    detector_kinds: list[MeetingTriggerKind | None] = field(default_factory=list)
    opener_reporter_contexts: list[ReporterContext | None] = field(default_factory=list)
    reply_is_body_report: list[bool] = field(default_factory=list)
    ballot_reporter_ids: list[PlayerId | None] = field(default_factory=list)


class _WatchedManager(MeetingManager):
    """The real manager, recording the trigger kind its detector receives."""

    def __init__(self, *, seen: _Seen, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._seen = seen

    def _detect_contradictions(
        self,
        transcript: MeetingTranscript,
        *,
        roster: frozenset[PlayerId],
        vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]],
        move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
        sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
        evidence_reasoning_version: Literal[1, 2] | None,
        trigger_kind: MeetingTriggerKind | None = None,
    ) -> tuple[ContradictionRef, ...]:
        self._seen.detector_kinds.append(trigger_kind)
        return super()._detect_contradictions(
            transcript,
            roster=roster,
            vent_witness_records=vent_witness_records,
            move_witness_records=move_witness_records,
            sighting_records=sighting_records,
            evidence_reasoning_version=evidence_reasoning_version,
            trigger_kind=trigger_kind,
        )


def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
    """The opener re-narrates a stale body and accuses p-2; everyone SKIPs."""

    if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
        speaker = _extract_marker(prompt, "agent_id=")
        if "PHASE=OPENING" in prompt and speaker == "p-1":
            return _turn_json(
                speaker=speaker, accuses="p-2", observations=(_STALE_BODY,)
            )
        return _turn_json(speaker=speaker)
    if "PHASE=VOTE" in prompt:
        return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
    raise AssertionError("unrecognised prompt")


def _run_watched(trigger: MeetingTrigger) -> tuple[MeetingResult, _Seen]:
    seen = _Seen()

    def _opening(**kwargs: Any) -> str:
        if kwargs["agent_id"] == trigger.triggered_by:
            seen.opener_reporter_contexts.append(kwargs.get("reporter_context"))
        return _crewmate_report_prompt(**kwargs)

    def _statement(**kwargs: Any) -> str:
        seen.reply_is_body_report.append(kwargs["is_body_report"])
        return _statement_prompt(**kwargs)

    def _vote(**kwargs: Any) -> str:
        seen.ballot_reporter_ids.append(kwargs.get("reporter_id"))
        return _vote_prompt(**kwargs)

    manager = _WatchedManager(
        seen=seen,
        llm_client=_ScriptedLLMClient(responder=_responder),
        crewmate_report_prompt=_opening,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement,
        vote_prompt=_vote,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
        reporter_reasoning=True,
        corroboration_discipline=False,
    )
    result = asyncio.run(
        manager.run(
            meeting_id="m-1", trigger=trigger, participants=_crew_participants()
        )
    )
    return result, seen


def test_a_report_whose_wording_says_emergency_runs_as_a_report() -> None:
    """The planted case: all five trigger decisions follow ``kind="report"``.

    On the base the substring decided, and every assertion below reads the
    other way (Results quotes that red run).
    """

    result, seen = _run_watched(_REPORT_WITH_THE_PHRASE)
    reporter = _REPORT_WITH_THE_PHRASE.triggered_by

    # The ballot render names the reporter (``_collect_one_ballot``).
    assert seen.ballot_reporter_ids
    assert set(seen.ballot_reporter_ids) == {reporter}
    # The pre-vote detection runs with the report kind.
    assert seen.detector_kinds[-1] == "report"
    # The reporter-voice render id reaches the opener's own opening.
    assert seen.opener_reporter_contexts
    assert all(
        context is not None and context.reporter_id == reporter
        for context in seen.opener_reporter_contexts
    )
    # Every reply is told this is a body report.
    assert seen.reply_is_body_report
    assert set(seen.reply_is_body_report) == {True}
    # The emergency-opening body strip does not touch a report's opening.
    assert _STALE_BODY in result.transcript.turns[0].observations


def test_an_emergency_whose_wording_never_says_so_runs_as_an_emergency() -> None:
    """The mirror: ``kind="emergency"`` without the phrase is an emergency."""

    result, seen = _run_watched(_EMERGENCY_WITHOUT_THE_PHRASE)

    assert seen.ballot_reporter_ids
    assert set(seen.ballot_reporter_ids) == {None}
    assert seen.detector_kinds[-1] == "emergency"
    assert seen.opener_reporter_contexts
    assert set(seen.opener_reporter_contexts) == {None}
    assert seen.reply_is_body_report
    assert set(seen.reply_is_body_report) == {False}
    assert not any(
        isinstance(observation, FoundBodyObservation)
        for observation in result.transcript.turns[0].observations
    )


# --------------------------------------------------------------------------- #
# The manager never reads the wording; other production builders agree.       #
# --------------------------------------------------------------------------- #


def _is_trigger_description(node: ast.AST) -> TypeGuard[ast.Attribute]:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "description"
        and isinstance(node.value, ast.Name)
        and node.value.id == "trigger"
    )


def _wording_reads(source: str) -> list[str]:
    """Where manager source decides from the wording instead of handing it on.

    Two shapes count: a load of the emergency phrase constant anywhere, and a
    read of ``trigger.description`` other than as the renderer's
    ``meeting_trigger=`` argument.
    """

    tree = ast.parse(source)
    handed_on = {
        id(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.keyword)
        and node.arg == "meeting_trigger"
        and _is_trigger_description(node.value)
    }
    problems = [
        f"line {node.lineno}: loads EMERGENCY_TRIGGER_PHRASE"
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "EMERGENCY_TRIGGER_PHRASE"
        and isinstance(node.ctx, ast.Load)
    ]
    problems.extend(
        f"line {node.lineno}: reads trigger.description"
        for node in ast.walk(tree)
        if _is_trigger_description(node) and id(node) not in handed_on
    )
    return sorted(problems)


def test_the_manager_hands_the_wording_on_and_decides_nothing_from_it() -> None:
    assert _wording_reads(_MANAGER_SOURCE.read_text(encoding="utf-8")) == []


def test_a_planted_substring_decision_is_caught() -> None:
    planted = (
        "def _render(trigger):\n"
        "    return renderer(\n"
        "        meeting_trigger=trigger.description,\n"
        "        is_body_report=(EMERGENCY_TRIGGER_PHRASE not in trigger.description),\n"
        "    )\n"
    )
    assert _wording_reads(planted) == [
        "line 4: loads EMERGENCY_TRIGGER_PHRASE",
        "line 4: reads trigger.description",
    ]


def test_the_reasoning_evidence_scenario_opens_a_typed_emergency(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The one other production construction agrees with its own wording."""

    seen: list[MeetingTrigger] = []
    real_run = MeetingManager.run

    async def _watched_run(
        self: MeetingManager, *, trigger: MeetingTrigger, **kwargs: Any
    ) -> MeetingResult:
        seen.append(trigger)
        return await real_run(self, trigger=trigger, **kwargs)

    # ``eval.reasoning_evidence`` builds this very class; patching it here is
    # patching the manager that scenario runs.
    monkeypatch.setattr(MeetingManager, "run", _watched_run)
    asyncio.run(reasoning_evidence.run_reply_scenario(enabled=False, accuse=False))

    assert len(seen) == 1
    assert seen[0].kind == "emergency" == _templates_answer(seen[0])


@pytest.mark.parametrize("kind", _KINDS)
def test_the_committed_walk_helper_returns_the_engine_kind(
    kind: MeetingTriggerKind,
) -> None:
    """``tests/_helpers/committed.py`` hands detection the engine event's kind."""

    event = MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=41,
        actor="p-3",
        trigger=kind,
        body_id="body-p-2-38" if kind == "report" else None,
    )
    state = _meeting_state(victim="p-2", body_id="body-p-2-38", present=True)
    events: tuple[EngineEvent, ...] = (event,)
    walk_event = MeetingOpened(
        entry=None,  # type: ignore[arg-type]
        trigger=event,
        body_id=event.body_id,
        state=state,
        events=events,
    )
    assert meeting_trigger_kind(walk_event) == kind


# --------------------------------------------------------------------------- #
# The comments that describe the trigger tell the truth.                       #
# --------------------------------------------------------------------------- #

_RETIRED_CLAIMS = ("no structured trigger kind", "the one structured trigger fact")

# Each passage as it read at e886b663, before the kind was typed.
_BASE_PASSAGES: dict[str, str] = {
    "EMERGENCY_TRIGGER_PHRASE comment": """
        # Emergency-opening no-body backstop (Task 10.11.1; audit-2026-06-13-1816
        # B-B-1). The phrase that marks an EMERGENCY meeting's ``MeetingTrigger``
        # description -- the ONE home shared with
        # ``orchestrator.game._build_meeting_trigger`` (the producer) and, as a
        # documented JINJA-literal lockstep (a template cannot import), the
        # ``crewmate_report.j2`` emergency branch. DESIGN.md keeps no structured trigger
        # kind on the meeting layer -- the description IS the trigger surface -- so the
        # manager detects an emergency the same way the renderer does.
    """,
    "MeetingTrigger docstring": """
        Why the meeting was opened (DESIGN.md §5.1).

        The orchestrator constructs this from the engine event that
        transitioned the world into ``MEETING`` phase. ``triggered_by`` is the
        opener (turn 0); ``description`` is a short free-text summary (e.g.
        ``"p3 reported p2's body in MedBay at tick 410"``) that the opening
        prompt surfaces to the LLM.

        ``body_victim_id`` is the player whose corpse a BODY REPORT was made on --
        the one structured trigger fact the meeting layer carries, added because a
        speaker can hold discoveries of two different corpses within a tick of each
        other and a render that says "the body" must know which one it means.
        ``None`` for an emergency call and for any caller that does not thread it;
        a ``None`` here means the layer cannot tell the corpses apart and says so by
        rendering no victim rather than by guessing one. Additive and defaulted, so
        every existing construction site stays valid.
    """,
    "_trigger_is_emergency docstring": """
        True iff ``trigger`` opened an EMERGENCY meeting (Task 10.11.1).

        The meeting layer carries no structured trigger kind by design -- the
        description IS the trigger surface (``orchestrator.game._build_meeting_trigger``
        builds it from :data:`EMERGENCY_TRIGGER_PHRASE`, the same substring the
        ``crewmate_report.j2`` emergency branch keys on). Detecting it here off the
        same phrase keeps the no-body strip in lockstep with the prompt the model
        actually saw.
    """,
    "_build_meeting_trigger docstring": """
        Construct a :class:`MeetingTrigger` from the engine's transition events.

        The engine emits a :class:`MeetingTriggeredEvent` from
        :mod:`engine.tick._apply_report` / ``_apply_emergency`` whenever a
        valid ``ReportBody`` / ``EmergencyMeeting`` action drives the
        world into ``MEETING`` phase. The orchestrator pulls the most
        recent such event off the engine's emitted event list and renders
        it into the human-readable description the report prompt
        surfaces.

        The emergency description's "called an emergency meeting" phrase is
        load-bearing (Task 10.8): ``crewmate_report.j2`` v6 branches its
        emergency-opening frame on exactly that substring of the rendered
        ``meeting_trigger`` (the meeting layer threads no structured trigger
        kind to the prompt renderers, by design — the description IS the
        trigger surface). A wording change here must move in lockstep with
        the template branch; the strategic-prompt tests pin both ends.

        The second element of the returned tuple is the ``body_id`` of
        the corpse that triggered a ``report`` meeting (``None`` for an
        ``emergency`` meeting). :func:`apply_meeting_result` consumes
        that body so a hardcoded second report cannot re-trigger a meeting
        on the same corpse after gameplay resumes (defense in depth — the
        visibility layer already hides discovered bodies from default
        tactical agents, but the engine's ``resolve_report`` does not
        reject already-discovered bodies, so an adversarial / scripted
        intent could otherwise replay the trigger).

        The third element is the engine's trigger kind, consumed by the
        Task 10.8 post-meeting pacing notification (an ``emergency``
        meeting spends its caller's one emergency call per game).
    """,
}


def _normalized(passage: str) -> str:
    lines = (re.sub(r"^\s*#\s?", "", line) for line in passage.splitlines())
    return " ".join(" ".join(lines).split())


def _passage_problems(name: str, passage: str) -> list[str]:
    text = _normalized(passage).lower()
    problems = [
        f"{name}: still says {claim!r}" for claim in _RETIRED_CLAIMS if claim in text
    ]
    if re.search(r"\bkind\b", text) is None:
        problems.append(f"{name}: never names `kind`")
    return problems


def _phrase_comment_block(source: str) -> str:
    lines = source.splitlines()
    anchor = next(
        index
        for index, line in enumerate(lines)
        if line.startswith("EMERGENCY_TRIGGER_PHRASE: Final[str]")
    )
    start = anchor
    while start > 0 and lines[start - 1].startswith("#"):
        start -= 1
    block = lines[start:anchor]
    assert block, "the emergency phrase lost its comment block"
    return "\n".join(block)


def _current_passages() -> dict[str, str]:
    return {
        "EMERGENCY_TRIGGER_PHRASE comment": _phrase_comment_block(
            inspect.getsource(manager_module)
        ),
        "MeetingTrigger docstring": inspect.getdoc(MeetingTrigger) or "",
        "_trigger_is_emergency docstring": inspect.getdoc(_trigger_is_emergency) or "",
        "_build_meeting_trigger docstring": inspect.getdoc(_build_meeting_trigger)
        or "",
    }


def test_the_four_trigger_passages_describe_the_typed_kind() -> None:
    passages = _current_passages()
    assert set(passages) == set(_BASE_PASSAGES)
    assert [
        problem
        for name, passage in passages.items()
        for problem in _passage_problems(name, passage)
    ] == []


@pytest.mark.parametrize("name", sorted(_BASE_PASSAGES))
def test_each_base_wording_fails_the_passage_check(name: str) -> None:
    # Planted: the e886b663 wording of each passage, held as a fixed string.
    assert _passage_problems(name, _BASE_PASSAGES[name]) != []
