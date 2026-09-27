"""The two ballot arms: the witnessed-kill row and the strategic impostor ballot.

``ballot_kill_row_version`` and ``impostor_ballot_version`` are default-OFF
recorded experiment fields, set only by a declared config. The first gives a
voter one first-hand ``own_kill`` evidence row per kill it watched a
non-teammate make; the second serves an impostor voter a ballot framed as a move
for its side, bounded by an instructed citation rule the tally never enforces.
Both re-body ``vote_ballot`` with guarded blocks under the v8 marker and serve
derived arm stamps. With both OFF nothing moves.

The contract is ``tasks/work/ballot-kill-row-and-impostor-strategy.md``. The
end-to-end cases walk one scripted fake game
(:func:`tests._helpers.scripted_meeting.record_ballot_arms_game`), recorded on
the round-1 config into ``tmp_path``; nothing here prints a rendered prompt.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

import meetings.manager as manager_module
import orchestrator.game as game_module
from agents.memory.episodic import EpisodicEvent
from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED, ingest_packet
from agents.strategic.prompts.loader import (
    VOTE_BALLOT_TEMPLATE,
    build_prompt_renderers,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from eval.evidence_honesty import compute_evidence_honesty
from eval.gameplay_census import (
    OWN_KILL_ROW_TEXT,
    GameplayCensusConformanceError,
    served_own_kill_rows,
)
from eval.meeting_quality import _parse_suspicion_graph
from eval.validity import (
    _rendered_suspicions,
    assemble_tournament_report,
    check_no_betrayal,
    check_no_railroaded_crew_ejections,
)
from meetings.corroboration import MeetingTestimonyLedger
from meetings.evidence_profile import MeetingEvidenceProfile, profile_from_config
from meetings.manager import (
    TEAMMATE_VOTE_TARGET_MARKER,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
    build_evidence_rows,
    extract_belief_evidence,
)
from meetings.render_contract import EvidenceRow, EvidenceRowKind, PromptRenderInputs
from meetings.schemas import (
    ContradictionRef,
    KillWitnessRecord,
    MeetingResult,
    MeetingTranscript,
    ReportedStatement,
    SightingRecord,
    VoteBallot,
)
from observation.packet import GlobalView, ObservationPacket, PlayerView, SelfView
from orchestrator.experiment_config import RecordedExperimentConfig, meeting_values
from orchestrator.game import (
    PROMPT_VERSION_SETS,
    HeadlessGame,
    TacticalAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from meetings.voting import tally_ballots
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from tests._helpers.scripted_meeting import (
    BALLOT_ARMS_SEED,
    PROMPT_SET,
    ROUND_ONE_CONFIG,
    record_ballot_arms_game,
    record_game,
)
from tests.meetings import test_prompt_byte_golden as golden
from tests.meetings._manager_helpers import (
    _crewmate_report_prompt,
    _extract_marker,
    _impostor_report_prompt,
    _participant,
    _run,
    _ScriptedLLMClient,
    _statement_prompt,
    _turn_json,
)

_REPO: Final[Path] = Path(__file__).resolve().parents[2]
_SCRIPTS: Final[Path] = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import publish_gameplay_census as census_publisher  # noqa: E402

_SET: Final[str] = PROMPT_SET
_ARMS: Final[tuple[str, ...]] = ("ballot_kill_row_version", "impostor_ballot_version")

#: R10's tightened sentence, verbatim (the decision memo, section 2.5 item 3).
_TIGHTENED: Final[str] = (
    "Name a crewmate only when you can cite a line you hold that points toward "
    "them: a turn in which someone accused them at this table, or a conflict that "
    "names them."
)
#: The suspicion header's partial-summary sentence, OFF and under the kill-row arm.
_SENTENCE_OFF: Final[str] = (
    "a kill you watched happen, or someone you saw near a body just before you "
    "found it, moves these numbers with no line of its own up there — your memory "
    "block above still carries those."
)
_SENTENCE_ON: Final[str] = (
    "someone you saw near a body just before you found it moves these numbers "
    "with no line of its own up there — your memory block above still carries that."
)
_PARTIAL_SUMMARY_CLAIM: Final[str] = "only a PARTIAL summary of the lines above"
#: The persona's belief clause, which the impostor arm replaces.
_BELIEF_CLAUSE: Final[str] = "name the one player you believe is"
_STRATEGY_CLAUSE: Final[str] = "It is a move for your side"

_KILL: Final[KillWitnessRecord] = KillWitnessRecord(
    subject="p-3", room="EAST_HALL", tick=6, observation_id="p-1:6:2"
)


# --------------------------------------------------------------------------- #
# Shared builders                                                              #
# --------------------------------------------------------------------------- #


def _voter(
    agent_id: str = "p-1",
    *,
    role: str = "CREWMATE",
    fellows: tuple[str, ...] = (),
    kills: tuple[KillWitnessRecord, ...] = (_KILL,),
    sightings: tuple[SightingRecord, ...] = (),
) -> MeetingParticipant:
    return replace(
        _participant(agent_id, role=role, fellow_impostor_ids=fellows),
        kill_witness_records=kills,
        sighting_records=sightings,
    )


def _rows(
    voter: MeetingParticipant,
    *,
    arm: Literal[1] | None,
    targets: tuple[str, ...] = ("p-2", "p-3", "p-4"),
) -> tuple[EvidenceRow, ...]:
    return build_evidence_rows(
        voter=voter,
        candidate_targets=targets,
        contradictions=(),
        transcript=MeetingTranscript(turns=()),
        ballot_kill_row_version=arm,
    )


def _kill_row(record: KillWitnessRecord, *, voter: str = "p-1") -> EvidenceRow:
    """The one row a record makes, worded as the census's pattern constant."""

    return EvidenceRow(
        subject=record.subject,
        description=OWN_KILL_ROW_TEXT.format(room=record.room, tick=record.tick),
        kind="own_kill",
        first_hand=True,
        speaker=voter,
        citation_id=record.observation_id,
    )


def _render(**kwargs: Any) -> str:
    """The served ballot body, with every required input defaulted."""

    defaults: dict[str, Any] = {
        "voter_id": "p-1",
        "rendered_memory": "## Your role: CREWMATE",
        "transcript": MeetingTranscript(turns=()),
        "contradiction_flags": (),
        "suspicion_graph": (
            SuspicionEntry(player_id="p-2", suspicion=0.4, trust=0.5),
            SuspicionEntry(player_id="p-3", suspicion=0.8, trust=0.5),
        ),
        "candidate_targets": ("p-2", "p-3"),
        "skip_confidence_threshold": 0.6,
    }
    defaults.update(kwargs)
    return build_prompt_renderers(_SET).vote(**defaults)


@pytest.fixture(scope="module")
def scripted_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The ballot card's scripted game on the round-1 config, recorded once."""

    directory = tmp_path_factory.mktemp("ballot-arms") / "9p2i"
    record_ballot_arms_game(directory)
    return directory


def _meetings(directory: Path) -> list[MeetingReplayEntry]:
    path = directory / f"replay-seed-{BALLOT_ARMS_SEED}.jsonl"
    return [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    ]


def _ballot(entry: MeetingReplayEntry, voter: str) -> VoteBallot:
    return next(ballot for ballot in entry.ballots if ballot.voter == voter)


# --------------------------------------------------------------------------- #
# A. The kill record moves and carries its id                                  #
# --------------------------------------------------------------------------- #


def test_the_kill_record_lives_beside_the_vent_record_and_is_re_exported() -> None:
    assert game_module.KillWitnessRecord is KillWitnessRecord
    record = KillWitnessRecord(subject="p-3", room="EAST_HALL", tick=6)
    assert record.observation_id is None
    with pytest.raises(ValidationError):
        setattr(record, "subject", "p-4")
    with pytest.raises(ValidationError):
        KillWitnessRecord.model_validate(
            {"subject": "p-3", "room": "EAST_HALL", "tick": 6, "victim": "p-9"}
        )


# --------------------------------------------------------------------------- #
# B. A witness gets exactly one row                                            #
# --------------------------------------------------------------------------- #


def test_a_witness_gets_exactly_one_kill_row() -> None:
    rows = _rows(_voter(), arm=1)
    kills = [row for row in rows if row.kind == "own_kill"]
    assert kills == [_kill_row(_KILL)]
    # The row names the killer as its subject and nobody else: no victim.
    assert not re.search(r"p-\d", kills[0].description)


def test_the_kill_kind_is_named_and_sorts_with_the_first_hand_rows() -> None:
    from typing import get_args

    from meetings.render_contract import EvidenceRowKind as Kind

    kinds = set(get_args(Kind))
    assert "own_kill" in kinds
    assert set(manager_module._EVIDENCE_KIND_CLASS) == kinds  # noqa: PLC2701
    assert manager_module._EVIDENCE_KIND_CLASS["own_kill"] == 0  # noqa: PLC2701


def test_the_arm_off_builds_no_kill_row_and_the_tuple_of_today() -> None:
    voter = _voter(
        sightings=(
            SightingRecord(
                subject="p-3", room="ADMIN", tick=3, observation_id="p-1:3:0"
            ),
        )
    )
    off = _rows(voter, arm=None)
    assert off == _rows(replace(voter, kill_witness_records=()), arm=None)
    assert [row.kind for row in off] == ["own_sighting"]
    # Planted: the same participant with the arm ON gets the row.
    assert "own_kill" in [row.kind for row in _rows(voter, arm=1)]


def test_a_row_worded_otherwise_is_not_the_census_row() -> None:
    """The row text is pinned to the census constant through the served page.

    The census finds a served row only in the exact wording of
    ``OWN_KILL_ROW_TEXT``; the built row renders to exactly one found row, and
    the same row reworded (planted) renders to none.
    """

    row = _kill_row(_KILL)
    assert [row] == [r for r in _rows(_voter(), arm=1) if r.kind == "own_kill"]
    served = served_own_kill_rows(_render(evidence_rows=(row,)), holder="p-1")
    assert [
        (fact.subject, fact.room, fact.tick, fact.citation_id) for fact in served
    ] == [("p-3", "EAST_HALL", 6, "p-1:6:2")]
    reworded = replace(row, description="you saw them KILL in EAST_HALL at tick 6")
    assert reworded.description != row.description
    assert served_own_kill_rows(_render(evidence_rows=(reworded,)), holder="p-1") == ()


def test_a_kill_row_sorts_by_tick_among_the_killers_first_hand_rows() -> None:
    voter = _voter(
        sightings=tuple(
            SightingRecord(
                subject="p-3", room="ADMIN", tick=tick, observation_id=f"p-1:{tick}:0"
            )
            for tick in (3, 9)
        )
    )
    about_the_killer = [row for row in _rows(voter, arm=1) if row.subject == "p-3"]
    assert [(row.kind, row.citation_id) for row in about_the_killer] == [
        ("own_sighting", "p-1:3:0"),
        ("own_kill", "p-1:6:2"),
        ("own_sighting", "p-1:9:0"),
    ]


@pytest.mark.parametrize(("kill_tick", "kept"), [(2, False), (20, True)])
def test_a_kill_row_obeys_the_per_subject_budget(kill_tick: int, kept: bool) -> None:
    """Class 0 under the same budget: the earliest row of the group goes."""

    budget = manager_module.MAX_EVIDENCE_ROWS_PER_SUBJECT
    voter = _voter(
        kills=(
            _KILL.model_copy(
                update=dict(tick=kill_tick, observation_id=f"p-1:{kill_tick}:2")
            ),
        ),
        sightings=tuple(
            SightingRecord(
                subject="p-3", room="ADMIN", tick=tick, observation_id=f"p-1:{tick}:0"
            )
            for tick in range(10, 10 + budget)
        ),
    )
    first_hand = [row for row in _rows(voter, arm=1) if row.subject == "p-3"]
    assert len(first_hand) == budget
    assert ("own_kill" in [row.kind for row in first_hand]) is kept


_SUBJECTS: Final[tuple[str, ...]] = ("p-2", "p-3", "p-4", "p-5")


@st.composite
def _kill_records(draw: st.DrawFn) -> tuple[KillWitnessRecord, ...]:
    ticks = draw(st.lists(st.integers(1, 60), unique=True, max_size=5))
    return tuple(
        KillWitnessRecord(
            subject=draw(st.sampled_from(_SUBJECTS)),
            room=draw(st.sampled_from(("ADMIN", "EAST_HALL", "MEDBAY"))),
            tick=tick,
            observation_id=draw(st.one_of(st.none(), st.just(f"p-1:{tick}:1"))),
        )
        for tick in sorted(ticks)
    )


@given(
    kills=_kill_records(),
    fellows=st.sampled_from(((), ("p-3",))),
    voter=st.sampled_from(("p-1", "p-6")),
)
@settings(deadline=None, max_examples=80)
def test_every_non_teammate_record_makes_exactly_its_own_row(
    kills: tuple[KillWitnessRecord, ...], fellows: tuple[str, ...], voter: str
) -> None:
    """A property over generated records, both arms, both roles.

    With the arm ON the kill rows are exactly one row per record that names no
    fellow impostor, each the record's own row; with it OFF there are none and
    the tuple is the one built without the records.
    """

    role = "IMPOSTOR" if fellows else "CREWMATE"
    holder = voter
    voter_participant = _voter(holder, role=role, fellows=fellows, kills=kills)
    targets = _SUBJECTS
    on = [
        row
        for row in _rows(voter_participant, arm=1, targets=targets)
        if row.kind == "own_kill"
    ]
    expected = sorted(
        (
            _kill_row(record, voter=holder)
            for record in kills
            if record.subject not in fellows
        ),
        key=lambda row: (targets.index(row.subject), row.description),
    )
    assert sorted(
        on, key=lambda row: (targets.index(row.subject), row.description)
    ) == (expected)
    assert _rows(voter_participant, arm=None, targets=targets) == _rows(
        replace(voter_participant, kill_witness_records=()), arm=None, targets=targets
    )


def _eval_imports(source: str) -> list[str]:
    """The modules under ``eval`` a Python source imports."""

    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found += [
                alias.name
                for alias in node.names
                if alias.name == "eval" or alias.name.startswith("eval.")
            ]
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.module == "eval" or node.module.startswith("eval."):
                found.append(node.module)
    return found


def test_the_meeting_layer_imports_nothing_from_eval() -> None:
    """The row text lives in the meeting layer; only this test reads the constant."""

    sources = sorted((_REPO / "meetings").rglob("*.py"))
    assert sources
    for path in sources:
        assert _eval_imports(path.read_text(encoding="utf-8")) == [], path
    # Planted: the scan finds the import it forbids.
    assert _eval_imports(
        "from eval.gameplay_census import OWN_KILL_ROW_TEXT\nimport eval.validity\n"
    ) == ["eval.gameplay_census", "eval.validity"]


# --------------------------------------------------------------------------- #
# C. A voter who was only told gets nothing                                    #
# --------------------------------------------------------------------------- #

_GLOBAL: Final[GlobalView] = GlobalView(
    tasks_completed=0,
    tasks_total=10,
    task_completion_percent=0.0,
    sabotage_active=False,
    sabotage_kind=None,
)


def _agent(agent_id: str, role: str) -> TacticalAgent:
    policy: CrewmatePolicy | ImpostorPolicy = (
        ImpostorPolicy(agent_id=agent_id)
        if role == "IMPOSTOR"
        else CrewmatePolicy(agent_id=agent_id)
    )
    return TacticalAgent(agent_id=agent_id, policy=policy, role=role)  # type: ignore[arg-type]


def _witness(
    agent: TacticalAgent,
    *,
    killer: str | None,
    room: str,
    tick: int,
    bystanders: tuple[str, ...] = (),
) -> None:
    """Perceive one tick through the real perception path, watching ``killer`` kill.

    ``killer=None`` watches no kill; ``bystanders`` are seen in the room doing
    nothing, which is how a player enters the agent's known roster.
    """

    ingest_packet(
        packet=ObservationPacket(
            tick=tick,
            agent_id=agent.agent_id,
            self_state=SelfView(
                room=room,
                role=agent.role,
                pending_task_id=None,
                fellow_impostor_ids=(),
            ),
            visible_players=(
                *(
                    (PlayerView(id=killer, room=room, action="kill"),)
                    if killer is not None
                    else ()
                ),
                *(
                    PlayerView(id=player, room=room, action=None)
                    for player in bystanders
                ),
            ),
            visible_bodies=(),
            audible_events=(),
            global_state=_GLOBAL,
            cooldown=None,
        ),
        memory=agent.memory.episodic,
    )


def _participant_from(agent: TacticalAgent) -> MeetingParticipant:
    return replace(
        _participant(agent.agent_id, role=agent.role),
        kill_witness_records=agent.kill_witness_records_for_meeting(),
    )


class _MeetingAgent:
    """The meeting protocol's required channels, all empty."""

    def __init__(self, agent_id: str, role: str) -> None:
        self.agent_id = agent_id
        self.role = role

    def render_memory_for_meeting(
        self, *, token_budget: int, suspicion_override: Any = None
    ) -> str:
        return ""

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return ()

    def vent_witness_records_for_meeting(self) -> tuple[Any, ...]:
        return ()

    def sighting_records_for_meeting(self) -> tuple[Any, ...]:
        return ()

    def observation_ids_for_meeting(self) -> tuple[str, ...]:
        return ()


class _KillWitness(_MeetingAgent):
    """The same agent with the optional kill channel, and no movement channel."""

    def kill_witness_records_for_meeting(self) -> tuple[KillWitnessRecord, ...]:
        return (_KILL,)


def test_the_participants_carry_the_kill_channel_of_an_agent_that_has_it() -> None:
    from orchestrator.game import _build_participants
    from orchestrator.seeder import seed_initial_state

    state = seed_initial_state(seed=1, game_map=load_canonical_map(), num_players=4)
    agents: dict[str, Any] = {
        pid: (
            _KillWitness(pid, player.role)
            if pid == "p-1"
            else _MeetingAgent(pid, player.role)
        )
        for pid, player in state.players.items()
    }
    participants = {
        participant.agent_id: participant
        for participant in _build_participants(
            state=state, agents=agents, token_budget=1000
        )
    }
    assert participants["p-1"].kill_witness_records == (_KILL,)
    assert participants["p-1"].move_witness_records == ()
    assert all(
        participants[pid].kill_witness_records == () for pid in ("p-2", "p-3", "p-4")
    )


def test_a_voter_told_of_a_kill_holds_no_kill_row() -> None:
    told = _agent("p-1", "CREWMATE")
    _witness(told, killer=None, room="ADMIN", tick=5, bystanders=("p-3", "p-4"))
    told.absorb_reported_testimony(
        statements=(
            ReportedStatement(
                speaker="p-4",
                kind="saw_kill",
                subject="p-3",
                from_tick=6,
                to_tick=6,
                room="EAST_HALL",
            ),
        )
    )
    assert any(
        event.provenance == "reported"
        for event in told.memory.episodic.recent(since_tick=0)
    ), "the statement was absorbed"
    assert told.kill_witness_records_for_meeting() == ()
    assert not [
        row for row in _rows(_participant_from(told), arm=1) if row.kind == "own_kill"
    ]
    # Planted: the same kill written as a first-hand sighting makes the row.
    watched = _agent("p-1", "CREWMATE")
    _witness(watched, killer="p-3", room="EAST_HALL", tick=6)
    records = watched.kill_witness_records_for_meeting()
    assert [(r.subject, r.room, r.tick) for r in records] == [("p-3", "EAST_HALL", 6)]
    assert records[0].observation_id is not None
    kills = [
        row
        for row in _rows(_participant_from(watched), arm=1)
        if row.kind == "own_kill"
    ]
    assert kills == [_kill_row(records[0])]


def test_the_accessor_reads_first_hand_rows_only() -> None:
    """The observed-provenance filter, on one row written both ways."""

    agent = _agent("p-1", "CREWMATE")
    payload = {"player_id": "p-3", "room": "EAST_HALL", "action": "kill"}
    agent.memory.episodic.append(
        EpisodicEvent(
            tick=6, type=EVENT_SAW_PLAYER, payload=payload, provenance="reported"
        )
    )
    assert agent.kill_witness_records_for_meeting() == ()
    agent.memory.episodic.append(
        EpisodicEvent(
            tick=7,
            type=EVENT_SAW_PLAYER,
            payload=payload,
            provenance=PROVENANCE_OBSERVED,
        )
    )
    assert [r.tick for r in agent.kill_witness_records_for_meeting()] == [7]


def test_the_teammate_guard_reads_first_hand_self_state_only() -> None:
    """A fellow list the agent did not perceive itself guards nothing.

    The accessor's fellow set is the latest first-hand ``self_state`` row's list;
    a row in any other provenance naming p-3 leaves p-3's kill a record, and the
    same list first-hand drops it.
    """

    kill = EpisodicEvent(
        tick=6,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": "p-3", "room": "EAST_HALL", "action": "kill"},
        provenance=PROVENANCE_OBSERVED,
        observation_id="p-2:6:1",
    )
    for provenance, held in (("reported", 1), (PROVENANCE_OBSERVED, 0)):
        agent = _agent("p-2", "IMPOSTOR")
        agent.memory.episodic.append(
            EpisodicEvent(
                tick=5,
                type="self_state",
                payload={"agent_id": "p-2", "fellow_impostor_ids": ["p-3"]},
                provenance=provenance,
            )
        )
        agent.memory.episodic.append(kill)
        assert len(agent.kill_witness_records_for_meeting()) == held, provenance


# --------------------------------------------------------------------------- #
# D. The teammate firewall holds at assembly                                   #
# --------------------------------------------------------------------------- #


def test_an_impostors_record_naming_its_teammate_makes_no_row() -> None:
    """Records passed directly, so the assembly guard is what is proven."""

    kills = (
        _KILL,
        _KILL.model_copy(update=dict(subject="p-4", tick=8, observation_id="p-1:8:2")),
    )
    impostor = _voter(role="IMPOSTOR", fellows=("p-3",), kills=kills)
    rows = [row for row in _rows(impostor, arm=1) if row.kind == "own_kill"]
    assert [row.subject for row in rows] == ["p-4"]
    assert all("p-3" not in (row.subject, row.description) for row in rows)
    # The identical records on a crewmate keep both rows.
    crew = replace(impostor, role="CREWMATE", fellow_impostor_ids=())
    assert sorted(
        row.subject for row in _rows(crew, arm=1) if row.kind == "own_kill"
    ) == ["p-3", "p-4"]


# --------------------------------------------------------------------------- #
# The manager: role and arm values reach the render; nothing else moves        #
# --------------------------------------------------------------------------- #


class _CapturingVote:
    """The served vote body, fronted by the markers the scripted client reads."""

    def __init__(self, *, drop: tuple[str, ...] = ()) -> None:
        self.rendered: dict[str, str] = {}
        self.kwargs: dict[str, dict[str, Any]] = {}
        self._drop = drop
        self._inner = build_prompt_renderers(_SET).vote

    def __call__(self, **kwargs: Any) -> str:
        voter = kwargs["voter_id"]
        self.kwargs[voter] = dict(kwargs)
        served = {key: value for key, value in kwargs.items() if key not in self._drop}
        body = self._inner(**served)
        self.rendered[voter] = body
        return f"PHASE=VOTE\nvoter={voter}\n{body}"


def _responder(
    *,
    accusations: Mapping[str, str] | None = None,
    ballots: Mapping[str, Mapping[str, Any]] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    scripted_accusations = dict(accusations or {})
    scripted_ballots = {voter: dict(spec) for voter, spec in (ballots or {}).items()}

    def _respond(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            speaker = _extract_marker(prompt, "agent_id=")
            return _turn_json(
                speaker=speaker, accuses=scripted_accusations.get(speaker)
            )
        voter = _extract_marker(prompt, "voter=")
        spec = {"target": "SKIP", "confidence": 0.8, **scripted_ballots.get(voter, {})}
        return json.dumps(
            {
                "voter": voter,
                "target": spec["target"],
                "confidence": spec["confidence"],
                "primary_reason_id": spec.get("primary_reason_id"),
                "primary_reason_observation_id": spec.get(
                    "primary_reason_observation_id"
                ),
                "considered_alternatives": [],
                "decision_basis": spec.get("decision_basis"),
                "rationale_text": f"stub-vote-{voter}",
            }
        )

    return _respond


def _manager(
    client: _ScriptedLLMClient,
    vote: Callable[..., str],
    *,
    profile: MeetingEvidenceProfile,
    corroboration_discipline: bool | None = None,
) -> MeetingManager:
    return MeetingManager(
        llm_client=client,
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=vote,
        config=MeetingConfig(deadlines=MeetingDeadlines()),
        evidence_profile=profile,
        corroboration_discipline=corroboration_discipline,
    )


def _meeting(
    participants: tuple[MeetingParticipant, ...],
    *,
    profile: MeetingEvidenceProfile,
    vote: _CapturingVote | None = None,
    accusations: Mapping[str, str] | None = None,
    ballots: Mapping[str, Mapping[str, Any]] | None = None,
    corroboration_discipline: bool | None = None,
) -> tuple[MeetingResult, _CapturingVote]:
    capture = vote if vote is not None else _CapturingVote()
    client = _ScriptedLLMClient(
        responder=_responder(accusations=accusations, ballots=ballots)
    )
    manager = _manager(
        client,
        capture,
        profile=profile,
        corroboration_discipline=corroboration_discipline,
    )
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=MeetingTrigger(
                triggered_by=participants[0].agent_id,
                trigger_tick=12,
                description=f"{participants[0].agent_id} reported a body at tick 12",
                kind="report",
            ),
            participants=participants,
            impostor_count=sum(1 for p in participants if p.role == "IMPOSTOR"),
        )
    )
    return result, capture


_KILL_ROW_ON: Final[MeetingEvidenceProfile] = MeetingEvidenceProfile(
    ballot_kill_row_version=1
)
_IMPOSTOR_ON: Final[MeetingEvidenceProfile] = MeetingEvidenceProfile(
    impostor_ballot_version=1
)
_BOTH_ON: Final[MeetingEvidenceProfile] = MeetingEvidenceProfile(
    ballot_kill_row_version=1, impostor_ballot_version=1
)


def _four(*, sole_impostor: bool = False) -> tuple[MeetingParticipant, ...]:
    """p-1 opens and watched p-3 kill; p-3 is an impostor, alone or with p-4."""

    fellows: tuple[str, ...] = () if sole_impostor else ("p-4",)
    return (
        _voter("p-1"),
        _voter("p-2", kills=()),
        _voter("p-3", role="IMPOSTOR", fellows=fellows, kills=()),
        _voter(
            "p-4",
            role="CREWMATE" if sole_impostor else "IMPOSTOR",
            fellows=() if sole_impostor else ("p-3",),
            kills=(),
        ),
    )


def test_the_manager_threads_the_role_and_both_arm_values_to_every_ballot() -> None:
    _, capture = _meeting(_four(), profile=_BOTH_ON)
    for participant in _four():
        kwargs = capture.kwargs[participant.agent_id]
        assert kwargs["voter_role"] == participant.role
        assert kwargs["ballot_kill_row_version"] == 1
        assert kwargs["impostor_ballot_version"] == 1
    _, off = _meeting(_four(), profile=MeetingEvidenceProfile())
    assert {kwargs["ballot_kill_row_version"] for kwargs in off.kwargs.values()} == {
        None
    }
    assert {kwargs["impostor_ballot_version"] for kwargs in off.kwargs.values()} == {
        None
    }


def test_the_witness_reads_its_kill_row_through_the_real_meeting() -> None:
    _, on = _meeting(_four(), profile=_KILL_ROW_ON)
    row = OWN_KILL_ROW_TEXT.format(room="EAST_HALL", tick=6)
    assert row in on.rendered["p-1"]
    assert not any(row in on.rendered[voter] for voter in ("p-2", "p-3", "p-4"))
    _, off = _meeting(_four(), profile=MeetingEvidenceProfile())
    assert row not in off.rendered["p-1"]
    # Each arm reaches its own block and no other: the kill-row arm rewords the
    # header on every ballot and serves no impostor wording, and the impostor arm
    # serves its wording and leaves the header alone.
    assert all(_SENTENCE_ON in body for body in on.rendered.values())
    assert _STRATEGY_CLAUSE not in on.rendered["p-3"]
    _, impostor = _meeting(_four(), profile=_IMPOSTOR_ON)
    assert all(_SENTENCE_OFF in body for body in impostor.rendered.values())
    assert _STRATEGY_CLAUSE in impostor.rendered["p-3"]
    assert row not in impostor.rendered["p-1"]


def test_the_role_reaches_a_sole_impostor() -> None:
    """The 4p1i shape: an impostor with no teammate list reads the strategy text."""

    participants = _four(sole_impostor=True)
    _, served = _meeting(participants, profile=_IMPOSTOR_ON)
    assert _STRATEGY_CLAUSE in served.rendered["p-3"]
    assert _TIGHTENED in served.rendered["p-3"]
    assert _BELIEF_CLAUSE not in served.rendered["p-3"]
    for crew in ("p-1", "p-2", "p-4"):
        assert _BELIEF_CLAUSE in served.rendered[crew]
    # Planted: with the role withheld the same voter reads the crew text.
    _, withheld = _meeting(
        participants, profile=_IMPOSTOR_ON, vote=_CapturingVote(drop=("voter_role",))
    )
    assert _STRATEGY_CLAUSE not in withheld.rendered["p-3"]
    assert _BELIEF_CLAUSE in withheld.rendered["p-3"]


def test_the_kill_arm_mints_no_flag_no_ledger_row_and_no_belief_input() -> None:
    """With kill records present, the arm moves the ballot rows and nothing else."""

    accusations = {"p-1": "p-3", "p-3": "p-2"}
    results: dict[str, MeetingResult] = {}
    ledgers: dict[str, dict[str, MeetingTestimonyLedger | None]] = {}
    suspicions: dict[str, dict[str, Any]] = {}
    for label, profile in (("off", MeetingEvidenceProfile()), ("on", _KILL_ROW_ON)):
        result, capture = _meeting(
            _four(),
            profile=profile,
            accusations=accusations,
            corroboration_discipline=True,
        )
        results[label] = result
        ledgers[label] = {
            voter: kwargs["testimony_ledger"]
            for voter, kwargs in capture.kwargs.items()
        }
        suspicions[label] = {
            voter: kwargs["suspicion_graph"] for voter, kwargs in capture.kwargs.items()
        }
    assert results["on"].contradictions == results["off"].contradictions
    assert results["on"].transcript == results["off"].transcript
    assert ledgers["on"] == ledgers["off"]
    assert any(ledger is not None for ledger in ledgers["on"].values())
    assert suspicions["on"] == suspicions["off"]
    assert extract_belief_evidence(results["on"]) == extract_belief_evidence(
        results["off"]
    )


# --------------------------------------------------------------------------- #
# The served bytes: crew ballots, the impostor wording                         #
# --------------------------------------------------------------------------- #

_ROW_KINDS: Final[tuple[EvidenceRowKind, ...]] = (
    "own_sighting",
    "own_vent",
    "own_transit",
    "contradiction",
    "testimony",
)


@st.composite
def _crew_render_inputs(draw: st.DrawFn) -> dict[str, Any]:
    players = ["p-2", "p-3", "p-4", "p-5"]
    targets = tuple(
        draw(st.lists(st.sampled_from(players), min_size=1, max_size=4, unique=True))
    )
    rows = tuple(
        EvidenceRow(
            subject=draw(st.sampled_from(targets)),
            description=f"you saw them in ADMIN at tick {index}",
            kind=draw(st.sampled_from(_ROW_KINDS)),
            first_hand=draw(st.booleans()),
            speaker=draw(st.sampled_from(("p-1", "p-2"))),
            citation_id=draw(st.one_of(st.none(), st.just(f"p-1:{index}:0"))),
        )
        for index in range(draw(st.integers(0, 3)))
    )
    return {
        "voter_id": "p-1",
        "rendered_memory": "## Your role: CREWMATE",
        "transcript": MeetingTranscript(turns=()),
        "contradiction_flags": (),
        "suspicion_graph": tuple(
            SuspicionEntry(
                player_id=player,
                suspicion=draw(st.floats(0.0, 1.0, allow_nan=False)),
                trust=0.5,
            )
            for player in players
        ),
        "candidate_targets": targets,
        "skip_confidence_threshold": 0.6,
        "reporter_id": draw(st.one_of(st.none(), st.sampled_from(players))),
        "persona": draw(st.sampled_from(("", "dry and brief"))),
        "render_inputs": PromptRenderInputs(
            impostor_count=draw(st.integers(1, 3)), map_card=""
        ),
        "evidence_rows": rows,
        "voter_role": draw(st.sampled_from(("CREWMATE", None))),
    }


def _crew_byte_problems(
    render: Callable[..., str], inputs: Mapping[str, Any]
) -> list[str]:
    """How a crew ballot's arm renders differ from OFF beyond the one sentence."""

    off = render(**inputs)
    problems: list[str] = []
    if render(**inputs, impostor_ballot_version=1) != off:
        problems.append("the impostor arm moved a crew ballot")
    kill_on = render(**inputs, ballot_kill_row_version=1)
    if _SENTENCE_OFF not in off or kill_on != off.replace(_SENTENCE_OFF, _SENTENCE_ON):
        problems.append("the kill-row arm moved more than the header sentence")
    if _PARTIAL_SUMMARY_CLAIM not in kill_on:
        problems.append("the kill-row arm dropped the partial-summary claim")
    both = render(**inputs, ballot_kill_row_version=1, impostor_ballot_version=1)
    if both != kill_on:
        problems.append("both arms moved a crew ballot beyond the kill-row sentence")
    return problems


@given(inputs=_crew_render_inputs())
@settings(deadline=None, max_examples=60)
def test_a_crew_ballot_moves_only_in_the_header_sentence(
    inputs: dict[str, Any],
) -> None:
    assert _crew_byte_problems(build_prompt_renderers(_SET).vote, inputs) == []


def _perturbed_vote(tmp_path: Path, old: str, new: str) -> Callable[..., str]:
    """The served ballot renderer over a template copy with one edit."""

    root = tmp_path / "prompts"
    shutil.copytree(_REPO / "agents" / "strategic" / "prompts" / _SET, root / _SET)
    victim = root / _SET / VOTE_BALLOT_TEMPLATE
    source = victim.read_text(encoding="utf-8")
    assert source.count(old) >= 1, old
    victim.write_text(source.replace(old, new), encoding="utf-8")
    return build_prompt_renderers(_SET, root=root).vote


_ROLE_TEST: Final[str] = ' and voter_role == "IMPOSTOR"'


def test_an_impostor_guard_without_the_role_test_moves_a_crew_ballot(
    tmp_path: Path,
) -> None:
    """Planted: the impostor blocks' guards with their role test deleted."""

    inputs: dict[str, Any] = {
        "voter_id": "p-1",
        "rendered_memory": "## Your role: CREWMATE",
        "transcript": MeetingTranscript(turns=()),
        "contradiction_flags": (),
        "suspicion_graph": (SuspicionEntry(player_id="p-2", suspicion=0.4, trust=0.5),),
        "candidate_targets": ("p-2",),
        "skip_confidence_threshold": 0.6,
        "voter_role": "CREWMATE",
    }
    assert _crew_byte_problems(build_prompt_renderers(_SET).vote, inputs) == []
    planted = _perturbed_vote(tmp_path, _ROLE_TEST, "")
    assert "the impostor arm moved a crew ballot" in _crew_byte_problems(
        planted, inputs
    )


def _impostor_render(
    *, fellows: tuple[str, ...], arm: Literal[1] | None, impostors: int = 2
) -> str:
    return _render(
        voter_id="p-3",
        rendered_memory="## Your role: IMPOSTOR",
        fellow_impostor_ids=fellows,
        voter_role="IMPOSTOR",
        impostor_ballot_version=arm,
        render_inputs=PromptRenderInputs(impostor_count=impostors, map_card=""),
    )


def _new_text(*, fellows: tuple[str, ...], impostors: int = 2) -> tuple[str, str]:
    """The strategic persona clause and the team block, as served under the arm."""

    rendered = _impostor_render(fellows=fellows, arm=1, impostors=impostors)
    persona = rendered.split("<persona>\n", 1)[1].split("\n</persona>", 1)[0]
    clause = persona.split(" by surviving until they equal or outnumber the crew. ", 1)[
        1
    ]
    team = rendered.split("## Your team\n", 1)[1].split("\n\n", 1)[0]
    return clause, team


#: What the impostor's new text may never carry.
_DISALLOWED: Final[tuple[tuple[str, re.Pattern[str]], ...]] = (
    ("names a player", re.compile(r"`?p-\d+`?")),
    ("carries a digit", re.compile(r"\d")),
    ("carries a confidence clause", re.compile(r"confiden", re.IGNORECASE)),
    (
        "recommends a target",
        re.compile(r"(vote|eject|choose|pick|name)\s+`?p-\d+`?", re.IGNORECASE),
    ),
    (
        "ranks a player",
        re.compile(r"\b(highest|lowest|most suspicious|rank|best target)\b", re.I),
    ),
    (
        "carries a task, audit or ruling id",
        re.compile(r"\b(Task|R\d+|D\d|B\d|audit|ruling)\b"),
    ),
    ("invites an invented line", re.compile(r"invent|make up|fabricat", re.I)),
)


def _wording_problems(text: str) -> list[str]:
    return [label for label, pattern in _DISALLOWED if pattern.search(text)]


@pytest.mark.parametrize("fellows", [("p-4",), ()], ids=["with-teammate", "sole"])
def test_the_impostor_wording_is_neutral_and_carries_the_tightened_sentence(
    fellows: tuple[str, ...],
) -> None:
    clause, team = _new_text(fellows=fellows, impostors=len(fellows) + 1)
    assert _STRATEGY_CLAUSE in clause and _BELIEF_CLAUSE not in clause
    assert _wording_problems(clause) == []
    paragraph = team.split("\n")[-1]
    assert paragraph.startswith(_TIGHTENED)
    assert _wording_problems(paragraph) == []
    assert "Copy that line's id exactly." in paragraph
    assert "When nothing you hold points toward any crewmate, write SKIP." in paragraph
    # The team block names only the teammate list.
    assert set(re.findall(r"p-\d+", team)) == set(fellows)
    if fellows:
        assert team.startswith(f"Secret: {fellows[0]} is your fellow saboteur.")
        assert "if your suspicion lands on one" not in team
    else:
        assert team.startswith('Your own name never goes in "target"')


@pytest.mark.parametrize(
    ("planted", "problem"),
    [
        ("A sighting may be invented if it helps.", "invites an invented line"),
        ("Set your confidence high.", "carries a confidence clause"),
        ("Accuse at most 2 players.", "carries a digit"),
        ("You should eject p-4 now.", "recommends a target"),
    ],
)
def test_the_wording_scan_bites_a_planted_line(planted: str, problem: str) -> None:
    clause, _ = _new_text(fellows=("p-4",))
    assert problem in _wording_problems(f"{clause} {planted}")


def test_the_impostor_arm_leaves_the_confidence_sentences_and_contract_alone() -> None:
    off = _impostor_render(fellows=("p-4",), arm=None)
    on = _impostor_render(fellows=("p-4",), arm=1)
    for kept in (
        'Set "confidence" to your honest probability that the call is right',
        "EXACTLY these 9 keys",
        '"decision_basis" is null in the skeleton because it is yours to state',
    ):
        assert kept in off and kept in on
    assert on.split("## How to decide", 1)[1] == off.split("## How to decide", 1)[1]


# --------------------------------------------------------------------------- #
# The firewall, and the layer that labels and never rewrites                   #
# --------------------------------------------------------------------------- #


def test_a_teammate_ballot_under_the_arm_is_coerced_and_betrayal_stays_zero(
    scripted_game: Path,
) -> None:
    first = _meetings(scripted_game)[0]
    coerced = _ballot(first, "p-3")
    assert coerced.target == "SKIP"
    assert coerced.guard_rewrite_reason == "teammate_coerced"
    assert coerced.guard_redirected_from == "p-2"
    assert coerced.rationale_text.startswith(
        TEAMMATE_VOTE_TARGET_MARKER.format(target="p-2")
    )
    assert coerced.grounding_label == "not_assessed"
    check = check_no_betrayal(assemble_tournament_report(scripted_game))
    assert check.passed and int(check.facts["multi_impostor_ballots"]) > 0  # type: ignore[arg-type]


def test_without_the_coercion_the_betrayal_check_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the coercion monkeypatched to identity."""

    monkeypatch.setattr(
        manager_module,
        "coerce_teammate_ballot_to_skip",
        lambda *, ballot, fellow_impostor_ids, model_rationale_text=None: ballot,
    )
    directory = tmp_path / "uncoerced" / "9p2i"
    record_ballot_arms_game(directory)
    assert _ballot(_meetings(directory)[0], "p-3").target == "p-2"
    assert not check_no_betrayal(assemble_tournament_report(directory)).passed


def test_the_layer_labels_what_the_impostor_cites_and_records_it_as_cast(
    scripted_game: Path,
) -> None:
    first, second, third = _meetings(scripted_game)
    # Citing an accusation turn against its target: supported.
    accusing = _ballot(first, "p-2")
    assert (accusing.target, accusing.grounding_label) == ("p-1", "supported")
    assert accusing.primary_reason_id == f"{first.meeting_id}:turn-3"
    # Citing only its own sighting: recorded as cast, never rewritten.
    neutral = _ballot(second, "p-2")
    assert neutral.target == "p-4" and neutral.guard_rewrite_reason is None
    assert neutral.primary_reason_id is None
    assert neutral.primary_reason_observation_id is not None
    # Both impostors' confident ballots carry the third meeting's ejection.
    assert (third.outcome, third.ejected_player_id) == ("EJECTED", "p-7")


def test_an_impostor_skip_that_holds_nothing_labels_none_held() -> None:
    result, _ = _meeting(
        _four(),
        profile=_IMPOSTOR_ON,
        ballots={"p-3": {"target": "SKIP", "decision_basis": "none_held"}},
    )
    ballot = next(b for b in result.ballots if b.voter == "p-3")
    assert (ballot.target, ballot.grounding_label) == ("SKIP", "none_held")


def _tally_meeting() -> MeetingResult:
    """An ungrounded impostor EJECT decides the tally.

    p-3 (impostor) names p-2 citing only its own sighting, at a confidence the
    floor accepts; crewmate p-1 names p-2 below the floor; p-4 names p-1; p-2
    skips. p-2 holds a strict plurality with one confident ballot, the
    impostor's, so p-2 is ejected.
    """

    participants = (
        replace(_voter("p-1", kills=()), observation_ids=("p-1:3:0",)),
        _voter("p-2", kills=()),
        replace(
            _voter("p-3", role="IMPOSTOR", kills=()),
            observation_ids=("p-3:4:0",),
        ),
        _voter("p-4", kills=()),
    )
    result, _ = _meeting(
        participants,
        profile=_IMPOSTOR_ON,
        ballots={
            "p-3": {
                "target": "p-2",
                "confidence": 0.9,
                "primary_reason_observation_id": "p-3:4:0",
                "decision_basis": "cited",
            },
            "p-1": {"target": "p-2", "confidence": 0.3},
            "p-4": {"target": "p-1", "confidence": 0.3},
        },
    )
    return result


def test_an_ungrounded_impostor_eject_is_tallied_like_any_other() -> None:
    result = _tally_meeting()
    ballot = next(b for b in result.ballots if b.voter == "p-3")
    assert ballot.target == "p-2" and ballot.primary_reason_id is None
    assert (result.outcome, result.ejected_player_id) == ("EJECTED", "p-2")


def test_a_tally_that_dropped_the_ungrounded_eject_would_change_the_outcome(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a tally that skips an EJECT citing no turn."""

    real = tally_ballots

    def _dropping(ballots: Any, **kwargs: Any) -> Any:
        kept = [
            b for b in ballots if b.target == "SKIP" or b.primary_reason_id is not None
        ]
        return real(kept, **kwargs)

    monkeypatch.setattr(manager_module, "tally_ballots", _dropping)
    result = _tally_meeting()
    assert (result.outcome, result.ejected_player_id) != ("EJECTED", "p-2")


# --------------------------------------------------------------------------- #
# Refusals                                                                     #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("arm", _ARMS)
@pytest.mark.parametrize(
    "account", ["public_account_version", "attributed_testimony_version"]
)
def test_the_profile_refuses_a_ballot_arm_beside_an_account_profile(
    arm: str, account: str
) -> None:
    with pytest.raises(ValidationError, match="cannot run with the account profile"):
        MeetingEvidenceProfile.model_validate({arm: 1, account: 1})
    assert MeetingEvidenceProfile.model_validate({arm: 1})
    assert MeetingEvidenceProfile.model_validate({account: 1})


_OVERLAYS: Final[dict[str, str]] = {
    "impostor_roll_call": "AILIBI_IMPOSTOR_ROLL_CALL",
    "reporter_reasoning": "AILIBI_REPORTER_REASONING",
    "corroboration_discipline": "AILIBI_CORROBORATION_DISCIPLINE",
    "testimony_shapes": "AILIBI_TESTIMONY_SHAPES",
}


@pytest.mark.parametrize("arm", _ARMS)
@pytest.mark.parametrize("overlay", sorted(_OVERLAYS))
def test_the_runner_refuses_a_ballot_arm_beside_a_legacy_overlay(
    arm: str, overlay: str
) -> None:
    env = {"AILIBI_PROMPT_SET": _SET, _OVERLAYS[overlay]: "1"}
    with pytest.raises(
        ValueError,
        match=(
            f"the ballot experiment \\['{arm}'\\] cannot run while the "
            f"legacy meeting overlays \\['{overlay}'\\]"
        ),
    ):
        build_default_meeting_runner(
            llm_client=_fake(),
            env=env,
            profile=MeetingEvidenceProfile.model_validate({arm: 1}),
        )
    # The overlay alone still builds.
    assert build_default_meeting_runner(llm_client=_fake(), env=env)


def _fake() -> Any:
    from llm.fake_provider import FakeProvider

    return FakeProvider()


@pytest.mark.parametrize(
    "values",
    [
        {"ballot_kill_row_version": 1},
        {"impostor_ballot_version": 1},
        {"ballot_kill_row_version": 1, "impostor_ballot_version": 1},
        {
            "ballot_kill_row_version": 1,
            "impostor_ballot_version": 1,
            "bounded_rebuttal_version": 1,
            "meeting_reset": "hub_with_grace",
        },
    ],
    ids=["kill-row", "impostor", "both", "both-with-rebuttal-and-reset"],
)
def test_each_arm_alone_and_both_with_the_rebuttal_and_reset_construct(
    values: dict[str, object],
) -> None:
    config = RecordedExperimentConfig.model_validate(values)
    runner = build_default_meeting_runner(
        llm_client=_fake(),
        env={"AILIBI_PROMPT_SET": _SET},
        profile=profile_from_config(meeting_values(config)),
    )
    game = HeadlessGame(
        seed=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=None,
        meeting_runner=runner,
        experiment_config=config,
    )
    assert game._experiment_config == config  # noqa: PLC2701


def test_a_pin_claiming_an_arm_on_another_set_fails_the_one_source_check() -> None:
    """The check reads the ACTIVE set's stamps, not the served set's."""

    pinned = {
        **PROMPT_VERSION_SETS["qwen3_32b"],
        "vote_ballot": "vote_ballot.qwen3_32b.v6.impostor_ballot_v1",
    }
    with pytest.raises(
        ValueError,
        match=(
            "the vote_ballot stamp 'vote_ballot.qwen3_32b.v6.impostor_ballot_v1' "
            "credits impostor_ballot_version at \\[1\\], but the served profile "
            "renders it at None"
        ),
    ):
        build_default_meeting_runner(
            llm_client=_fake(),
            env={"AILIBI_PROMPT_SET": "qwen3_32b"},
            prompt_versions=pinned,
            profile=MeetingEvidenceProfile(),
        )


@pytest.mark.parametrize("arm", _ARMS)
def test_the_runner_refuses_an_arm_for_a_set_whose_ballot_has_no_block(
    arm: str,
) -> None:
    with pytest.raises(ValueError, match=f"carries no live '{arm}' guard"):
        build_default_meeting_runner(
            llm_client=_fake(),
            env={"AILIBI_PROMPT_SET": "qwen3_32b"},
            profile=MeetingEvidenceProfile.model_validate({arm: 1}),
        )


def test_the_body_check_reads_the_template_the_arm_registers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: an arm registered on a body that carries no block for it."""

    monkeypatch.setattr(
        game_module,
        "EXPERIMENT_ARM_TEMPLATES",
        MappingProxyType({"ballot_kill_row_version": ("accusation_round",)}),
    )
    with pytest.raises(ValueError, match="template 'accusation_round.j2' carries no"):
        build_default_meeting_runner(
            llm_client=_fake(),
            env={"AILIBI_PROMPT_SET": _SET},
            profile=MeetingEvidenceProfile(ballot_kill_row_version=1),
        )


@pytest.mark.parametrize("arm", _ARMS)
def test_a_dead_guard_is_no_block(arm: str, tmp_path: Path) -> None:
    """Planted: the arm's guards folded to a constant in a template copy."""

    root = tmp_path / "prompts"
    shutil.copytree(_REPO / "agents" / "strategic" / "prompts" / _SET, root / _SET)
    victim = root / _SET / VOTE_BALLOT_TEMPLATE
    source = victim.read_text(encoding="utf-8")
    victim.write_text(
        source.replace(f"{arm} is defined and {arm}", f"false and {arm}"),
        encoding="utf-8",
    )
    from agents.strategic.prompts.loader import require_guarded_bodies

    with pytest.raises(ValueError, match=f"carries no live '{arm}' guard"):
        require_guarded_bodies(
            _SET, guard=arm, templates=(VOTE_BALLOT_TEMPLATE,), root=root
        )
    require_guarded_bodies(_SET, guard=arm, templates=(VOTE_BALLOT_TEMPLATE,))


# --------------------------------------------------------------------------- #
# The railroad tripwire cannot go vacuous                                      #
# --------------------------------------------------------------------------- #


def _graph_render(
    render: Callable[..., str], **arms: Any
) -> tuple[str, dict[str, float]]:
    graph = tuple(
        SuspicionEntry(player_id=player, suspicion=value, trust=0.5)
        for player, value in (("p-2", 0.25), ("p-3", 1.0), ("p-4", 0.5))
    )
    rendered = render(
        voter_id="p-1",
        rendered_memory="## Your role: CREWMATE",
        transcript=MeetingTranscript(turns=()),
        contradiction_flags=(),
        suspicion_graph=graph,
        candidate_targets=("p-2", "p-3", "p-4"),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=("p-4",),
        voter_role="IMPOSTOR",
        **arms,
    )
    return rendered, {entry.player_id: entry.suspicion for entry in graph}


def _parsed_rows(prompt: str) -> tuple[dict[str, float], dict[str, list[float]]]:
    meeting = _SuspicionMeeting(prompt)
    return _parse_suspicion_graph(prompt), {
        player: _rendered_suspicions(meeting, player)  # type: ignore[arg-type]
        for player in ("p-2", "p-3", "p-4")
    }


class _SuspicionMeeting:
    """The one attribute ``eval.validity._rendered_suspicions`` reads."""

    def __init__(self, prompt: str) -> None:
        self.llm_calls = (type("Call", (), {"prompt": prompt})(),)


_ARM_SETTINGS: Final[dict[str, dict[str, int]]] = {
    "kill-row": {"ballot_kill_row_version": 1},
    "impostor": {"impostor_ballot_version": 1},
    "both": {"ballot_kill_row_version": 1, "impostor_ballot_version": 1},
}


@pytest.mark.parametrize("arms", sorted(_ARM_SETTINGS))
def test_an_arm_on_ballot_parses_to_exactly_its_suspicion_rows(arms: str) -> None:
    rendered, graph = _graph_render(
        build_prompt_renderers(_SET).vote, **_ARM_SETTINGS[arms]
    )
    parsed, per_player = _parsed_rows(rendered)
    assert parsed == graph
    assert per_player == {player: [value] for player, value in graph.items()}


@pytest.mark.parametrize(
    ("old", "new"),
    [
        (
            "And it is only a PARTIAL summary of the lines above: {% if",
            "\n## Scratch\nAnd it is only a PARTIAL summary of the lines above: {% if",
        ),
        ("## Your suspicion of each player", "## Your suspicions"),
    ],
    ids=["a header between", "the header edited"],
)
def test_a_template_copy_that_moves_the_header_parses_to_nothing(
    old: str, new: str, tmp_path: Path
) -> None:
    rendered, _ = _graph_render(
        _perturbed_vote(tmp_path, old, new), ballot_kill_row_version=1
    )
    parsed, per_player = _parsed_rows(rendered)
    assert parsed == {} and all(values == [] for values in per_player.values())


def test_the_tripwire_reads_crew_rows_on_the_scripted_arm_on_game(
    scripted_game: Path,
) -> None:
    check = check_no_railroaded_crew_ejections(
        assemble_tournament_report(scripted_game)
    )
    assert check.passed
    assert int(check.facts["rendered_crew_rows"]) > 0  # type: ignore[arg-type]


def test_a_railroaded_crew_row_on_an_arm_on_prompt_fails_the_tripwire(
    scripted_game: Path,
) -> None:
    """Planted: a crew row at 1.00 and two same-meeting flags naming that crewmate."""

    report = assemble_tournament_report(scripted_game)
    game = report.games[0]
    meeting = game.meetings[0]
    rendered, _ = _graph_render(
        build_prompt_renderers(_SET).vote,
        ballot_kill_row_version=1,
        impostor_ballot_version=1,
    )
    call = meeting.llm_calls[0].model_copy(update={"prompt": rendered})
    flags = tuple(
        ContradictionRef(
            contradiction_id=f"c-planted-{index}",
            kind="alibi_vs_sighting",
            event_a_id=f"planted:a:{index}",
            event_b_id=f"planted:b:{index}",
            subjects=("p-3",),
            description="planted",
        )
        for index in range(2)
    )
    planted_meeting = meeting.model_copy(
        update={"llm_calls": (call,), "contradictions": flags}
    )
    planted = report.model_copy(
        update={
            "games": (
                game.model_copy(
                    update={
                        "roles": {**game.roles, "p-3": "CREWMATE"},
                        "meetings": (planted_meeting, *game.meetings[1:]),
                    }
                ),
                *report.games[1:],
            )
        }
    )
    check = check_no_railroaded_crew_ejections(planted)
    assert not check.passed
    assert check.facts["railroaded_crew_rows"] == 1


# --------------------------------------------------------------------------- #
# The golden covers the ON body                                                #
# --------------------------------------------------------------------------- #


def test_the_golden_re_renders_every_ballot_of_the_arm_on_game(
    scripted_game: Path,
) -> None:
    stamps = {
        entry.prompt_versions["vote_ballot"] for entry in _meetings(scripted_game)
    }
    assert stamps == {
        "vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1"
        "+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1"
    }
    walk = golden.walk_directory(scripted_game)
    ballots = [p for p in walk.prompts if p.kind == "vote_ballot"]
    assert ballots and all(prompt.reproduced for prompt in walk.prompts)
    assert walk.miscounted_meetings == ()


@pytest.mark.parametrize("dropped", _ARMS)
def test_the_golden_fails_when_a_bound_arm_value_is_dropped(
    scripted_game: Path, monkeypatch: pytest.MonkeyPatch, dropped: str
) -> None:
    real = profile_from_config

    def _without(values: Mapping[str, object]) -> MeetingEvidenceProfile:
        return real({**values, dropped: None})

    monkeypatch.setattr(golden, "profile_from_config", _without)
    walk = golden.walk_directory(scripted_game)
    assert not all(prompt.reproduced for prompt in walk.prompts)


_ON_BLOCK_BYTE: Final[tuple[str, str]] = (
    "It is a move for your side, not a statement",
    "It is a move for your side,  not a statement",
)


def _walk_with_renderers(
    directory: Path, renderers: Mapping[str, Any]
) -> Iterator[golden.RerenderedPrompt]:
    game_map = load_canonical_map()
    for path in sorted(directory.glob("replay-seed-*.jsonl")):
        for meeting in golden.walk_replay_meetings(
            path, game_map=game_map, renderers_for_set=renderers
        ):
            yield from golden.rerendered_prompts(meeting)


def test_a_byte_inside_an_on_block_fails_only_the_arm_on_recording(
    scripted_game: Path, tmp_path: Path
) -> None:
    """Planted: one byte inside the impostor block.

    The committed sets never render the block, so the golden stays green on
    samples/9p2i and samples/4p1i; the scripted game renders it, so it fails.
    """

    root = tmp_path / "prompts"
    for name in PROMPT_VERSION_SETS:
        shutil.copytree(_REPO / "agents" / "strategic" / "prompts" / name, root / name)
    victim = root / _SET / VOTE_BALLOT_TEMPLATE
    source = victim.read_text(encoding="utf-8")
    old, new = _ON_BLOCK_BYTE
    assert source.count(old) == 1
    victim.write_text(source.replace(old, new), encoding="utf-8")
    renderers = {
        name: build_prompt_renderers(name, root=root) for name in PROMPT_VERSION_SETS
    }
    for committed in golden._SAMPLE_SETS:  # noqa: PLC2701
        prompts = list(_walk_with_renderers(committed, renderers))
        assert prompts and all(prompt.reproduced for prompt in prompts), committed.name
    scripted = list(_walk_with_renderers(scripted_game, renderers))
    assert scripted and not all(prompt.reproduced for prompt in scripted)


# --------------------------------------------------------------------------- #
# The census and the honesty cells on the scripted game                        #
# --------------------------------------------------------------------------- #


def _census_cells(directory: Path) -> dict[str, dict[str, Any]]:
    section = json.loads(census_publisher.set_dir_json(directory))
    cells: dict[str, dict[str, Any]] = section["cells"]
    return cells


def test_the_census_reads_zero_breaching_rows_and_zero_teammate_targets(
    scripted_game: Path,
) -> None:
    cells = _census_cells(scripted_game)
    breaching = cells["own_kill_rows_breaching"]
    assert breaching["numerator"] == 0 and breaching["denominator"] > 0
    teammate = cells["recorded_teammate_ballot_targets"]
    assert teammate["numerator"] == 0 and teammate["denominator"] > 0


def test_a_teammate_kill_row_in_an_impostor_prompt_raises_the_census(
    scripted_game: Path, tmp_path: Path
) -> None:
    """Planted: p-2's first ballot prompt carries a row saying it watched p-3 kill."""

    copy = tmp_path / "planted" / "9p2i"
    shutil.copytree(scripted_game, copy)
    path = copy / f"replay-seed-{BALLOT_ARMS_SEED}.jsonl"
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    planted_row = (
        "- `p-3` — "
        + OWN_KILL_ROW_TEXT.format(room="EAST_HALL", tick=6)
        + " (first-hand: you saw this yourself; cite `p-2:6:1`)"
    )
    for row in rows:
        if row["kind"] != "meeting":
            continue
        for call in row["llm_calls"]:
            if call.get("agent_id") == "p-2" and "<evidence>" in call["prompt"]:
                call["prompt"] = call["prompt"].replace(
                    "<evidence>\n", "<evidence>\n" + planted_row + "\n", 1
                )
                break
        break
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(GameplayCensusConformanceError, match="meeting"):
        census_publisher.set_dir_json(copy)


def test_the_honesty_cells_count_the_scripted_ballots(scripted_game: Path) -> None:
    cells = compute_evidence_honesty(scripted_game).ballot_conduct
    assert (cells.impostor_ballots, cells.impostor_ejects, cells.impostor_skips) == (
        6,
        5,
        1,
    )
    assert (cells.ejects_pointing_toward, cells.ejects_pointing_toward_own_turn) == (
        2,
        1,
    )
    assert cells.ejects_other_turn == 0
    assert (
        cells.ejects_citing_only_neutral.numerator,
        cells.ejects_citing_only_neutral.denominator,
    ) == (2, 5)
    assert cells.ejects_without_citation == 1
    assert (
        cells.ejections_carried_by_impostors_alone.numerator,
        cells.ejections_carried_by_impostors_alone.denominator,
    ) == (1, 1)
    assert cells.kill_holders == 3
    assert (
        cells.kill_holders_citing_the_kill.numerator,
        cells.kill_holders_citing_the_kill.denominator,
    ) == (1, 3)
    assert (
        cells.recorded_teammate_targets.numerator,
        cells.recorded_teammate_targets.denominator,
    ) == (0, 6)
    # Cell 4 equals the census's own reading of the same game.
    census = _census_cells(scripted_game)["ejections_carried_only_by_impostor_ballots"]
    assert (census["numerator"], census["denominator"]) == (1, 1)


# --------------------------------------------------------------------------- #
# The pending guard is gone: the round-1 config plays in a bare environment    #
# --------------------------------------------------------------------------- #


def test_the_round_one_config_validates_plays_and_verifies_in_a_bare_shell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in list(os.environ):
        if name.startswith("AILIBI_"):
            monkeypatch.delenv(name)
    config = RecordedExperimentConfig.model_validate(ROUND_ONE_CONFIG)
    assert {
        key: value
        for key, value in config.model_dump(mode="json").items()
        if key in ROUND_ONE_CONFIG
    } == ROUND_ONE_CONFIG
    directory = tmp_path / "round-one" / "9p2i"
    record_game(directory, seed=BALLOT_ARMS_SEED, config=config)
    replay = ReplayLoader(directory).load_replay(f"headless-seed-{BALLOT_ARMS_SEED}")
    assert replay.metadata.outcome_verified


# --------------------------------------------------------------------------- #
# The ballot-conduct fold: one carrier per cell moves it by exactly one        #
# --------------------------------------------------------------------------- #

#: The seed's roles: p-2 and p-3 are the impostors.
_ROLES: Final[dict[str, str]] = {
    f"p-{index}": ("IMPOSTOR" if index in (2, 3) else "CREWMATE")
    for index in range(1, 10)
}
_CONDUCT_FIELDS: Final[tuple[str, ...]] = (
    "impostor_ballots",
    "impostor_ejects",
    "impostor_skips",
    "ejects_pointing_toward",
    "ejects_pointing_toward_own_turn",
    "ejects_other_turn",
    "ejects_citing_only_neutral",
    "ejects_without_citation",
    "ejections",
    "ejections_carried_by_impostors_alone",
    "kill_holders",
    "kill_holders_citing_the_kill",
    "recorded_teammate_targets",
)


def _stores(kill_holders: Mapping[str, str] | None = None) -> dict[str, Any]:
    """One memory per player; each named holder holds one first-hand kill row."""

    from agents.memory.episodic import MemoryStore

    stores: dict[str, MemoryStore] = {pid: MemoryStore() for pid in _ROLES}
    for holder, killer in (kill_holders or {}).items():
        stores[holder].append(
            EpisodicEvent(
                tick=6,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": killer, "room": "EAST_HALL", "action": "kill"},
                provenance=PROVENANCE_OBSERVED,
                observation_id=f"{holder}:6:2",
            )
        )
    return stores


def _conduct(
    entry: MeetingReplayEntry,
    *,
    roles: Mapping[str, str] = _ROLES,
    stores: Mapping[str, Any] | None = None,
    prefix: Mapping[str, int] | None = None,
) -> dict[str, int]:
    """Fold one meeting; ``prefix`` defaults to every store's full length."""

    from eval.evidence_honesty import _fold_ballot_conduct, _MeetingFacts, _Tallies

    memories = stores if stores is not None else _stores()
    tallies = _Tallies()
    _fold_ballot_conduct(
        facts=_MeetingFacts(
            entry=entry,
            living=frozenset(ballot.voter for ballot in entry.ballots),
            venting=frozenset(),
            body_triggered=True,
            memory_prefix=(
                prefix
                if prefix is not None
                else {pid: len(store) for pid, store in memories.items()}
            ),
        ),
        roles=roles,  # type: ignore[arg-type]
        memories=memories,
        tallies=tallies,
    )
    return {name: getattr(tallies, name) for name in _CONDUCT_FIELDS}


def _with_ballot(
    entry: MeetingReplayEntry, voter: str, **update: Any
) -> MeetingReplayEntry:
    return entry.model_copy(
        update={
            "ballots": tuple(
                ballot.model_copy(update=update) if ballot.voter == voter else ballot
                for ballot in entry.ballots
            )
        }
    )


def _moved(before: dict[str, int], after: dict[str, int]) -> dict[str, int]:
    return {
        name: after[name] - before[name]
        for name in _CONDUCT_FIELDS
        if after[name] != before[name]
    }


def test_each_carrier_moves_its_cell_by_exactly_one(scripted_game: Path) -> None:
    first, second, third = _meetings(scripted_game)
    base = _conduct(third)
    assert base == {
        "impostor_ballots": 2,
        "impostor_ejects": 2,
        "impostor_skips": 0,
        "ejects_pointing_toward": 0,
        "ejects_pointing_toward_own_turn": 0,
        "ejects_other_turn": 0,
        "ejects_citing_only_neutral": 1,
        "ejects_without_citation": 1,
        "ejections": 1,
        "ejections_carried_by_impostors_alone": 1,
        "kill_holders": 0,
        "kill_holders_citing_the_kill": 0,
        "recorded_teammate_targets": 0,
    }
    third_turns = {turn.speaker: turn.turn_id for turn in third.transcript.turns}
    # An impostor SKIP.
    assert _moved(base, _conduct(_with_ballot(third, "p-3", target="SKIP"))) == {
        "impostor_ejects": -1,
        "impostor_skips": 1,
        "ejects_without_citation": -1,
    }
    # A cited turn that points nowhere: another turn.
    other = _with_ballot(third, "p-3", primary_reason_id=third_turns["p-7"])
    assert _moved(base, _conduct(other)) == {
        "ejects_other_turn": 1,
        "ejects_without_citation": -1,
    }
    # The same turn, now the source of a conflict naming the target: pointing.
    flagged = other.model_copy(
        update={
            "contradictions": (
                ContradictionRef(
                    contradiction_id="c-planted",
                    kind="alibi_vs_sighting",
                    event_a_id=f"turn:{third_turns['p-7']}:claim:0",
                    event_b_id="planted:elsewhere",
                    subjects=("p-7",),
                    description="planted",
                ),
            )
        }
    )
    assert _moved(base, _conduct(flagged)) == {
        "ejects_pointing_toward": 1,
        "ejects_without_citation": -1,
    }
    # A turn the voter itself spoke against the target: pointing, own turn.
    from meetings.schemas import AccusationClaim

    accusing = third.model_copy(
        update={
            "transcript": MeetingTranscript(
                turns=tuple(
                    turn.model_copy(
                        update={
                            "claims": (
                                AccusationClaim(
                                    type="accusation",
                                    against="p-7",
                                    confidence=0.7,
                                    reason="planted",
                                ),
                            )
                        }
                    )
                    if turn.speaker == "p-2"
                    else turn
                    for turn in third.transcript.turns
                )
            )
        }
    )
    own = _with_ballot(
        accusing,
        "p-2",
        primary_reason_id=third_turns["p-2"],
        primary_reason_observation_id=None,
    )
    assert _moved(base, _conduct(own)) == {
        "ejects_pointing_toward": 1,
        "ejects_pointing_toward_own_turn": 1,
        "ejects_citing_only_neutral": -1,
    }
    # Only a neutral row, and then nothing at all.
    assert _moved(
        base,
        _conduct(_with_ballot(third, "p-3", primary_reason_observation_id="p-3:1:0")),
    ) == {"ejects_citing_only_neutral": 1, "ejects_without_citation": -1}
    assert _moved(
        base,
        _conduct(_with_ballot(third, "p-2", primary_reason_observation_id=None)),
    ) == {"ejects_citing_only_neutral": -1, "ejects_without_citation": 1}
    # A conflict minted from the cited turn that names somebody else: another
    # turn still; and one that names the target on its second event id: pointing.
    for subjects, event_a, event_b, moved in (
        (
            ("p-9",),
            f"turn:{third_turns['p-7']}:claim:0",
            "planted:elsewhere",
            {"ejects_other_turn": 1, "ejects_without_citation": -1},
        ),
        (
            ("p-7",),
            "planted:elsewhere",
            f"turn:{third_turns['p-7']}:obs:0",
            {"ejects_pointing_toward": 1, "ejects_without_citation": -1},
        ),
    ):
        elsewhere = other.model_copy(
            update={
                "contradictions": (
                    ContradictionRef(
                        contradiction_id="c-planted",
                        kind="alibi_vs_sighting",
                        event_a_id=event_a,
                        event_b_id=event_b,
                        subjects=subjects,
                        description="planted",
                    ),
                )
            }
        )
        assert _moved(base, _conduct(elsewhere)) == moved, subjects
    # A cited turn whose only claim is another kind points nowhere: other turn.
    from meetings.schemas import CorroborationClaim

    vouching = other.model_copy(
        update={
            "transcript": MeetingTranscript(
                turns=tuple(
                    turn.model_copy(
                        update={
                            "claims": (
                                CorroborationClaim(
                                    type="corroboration",
                                    supports="p-7",
                                    on_tick=30,
                                    reason="planted",
                                ),
                            )
                        }
                    )
                    if turn.speaker == "p-7"
                    else turn
                    for turn in third.transcript.turns
                )
            )
        }
    )
    assert _moved(base, _conduct(vouching)) == {
        "ejects_other_turn": 1,
        "ejects_without_citation": -1,
    }
    # A turn id that names no turn of this meeting is no citation.
    assert (
        _moved(
            base,
            _conduct(_with_ballot(third, "p-3", primary_reason_id="m-x:turn-99")),
        )
        == {}
    )
    # A recorded teammate target; a vote for oneself is not one.
    assert _moved(base, _conduct(_with_ballot(third, "p-2", target="p-3"))) == {
        "recorded_teammate_targets": 1
    }
    assert _moved(base, _conduct(_with_ballot(third, "p-2", target="p-2"))) == {}
    # A kill holder, and one whose ballot cites the kill.
    assert _moved(base, _conduct(third, stores=_stores({"p-9": "p-2"}))) == {
        "kill_holders": 1
    }
    assert _moved(
        base,
        _conduct(
            _with_ballot(third, "p-1", primary_reason_observation_id="p-1:6:2"),
            stores=_stores({"p-1": "p-3"}),
        ),
    ) == {"kill_holders": 1, "kill_holders_citing_the_kill": 1}
    # A kill row that arrived after the meeting opened is not held at it.
    late = _stores()
    prefix = {pid: len(store) for pid, store in late.items()}
    late["p-9"].append(
        EpisodicEvent(
            tick=50,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-2", "room": "EAST_HALL", "action": "kill"},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-9:50:2",
        )
    )
    assert _moved(base, _conduct(third, stores=late, prefix=prefix)) == {}
    # A holder whose kill row carries no id, voting with no citation, cites nothing.
    unstamped = _stores()
    unstamped["p-1"].append(
        EpisodicEvent(
            tick=6,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "p-3", "room": "EAST_HALL", "action": "kill"},
            provenance=PROVENANCE_OBSERVED,
        )
    )
    assert _moved(base, _conduct(third, stores=unstamped)) == {"kill_holders": 1}
    # A teammate's kill makes no holder: the accessor's own predicate.
    impostor_store = _stores({"p-2": "p-3"})
    impostor_store["p-2"].append(
        EpisodicEvent(
            tick=6,
            type="self_state",
            payload={"fellow_impostor_ids": ["p-3"]},
            provenance=PROVENANCE_OBSERVED,
            observation_id="p-2:6:0",
        )
    )
    assert _moved(base, _conduct(third, stores=impostor_store)) == {}
    # The meeting where no impostor carries the ejection alone.
    skipped = _conduct(first)
    assert skipped["ejections"] == 0
    assert second.outcome == "SKIPPED"


def test_a_ballot_by_a_player_with_no_rebuilt_memory_raises(
    scripted_game: Path,
) -> None:
    from eval.evidence_honesty import EvidenceHonestyReconstructionError

    stores = _stores()
    del stores["p-9"]
    with pytest.raises(EvidenceHonestyReconstructionError, match="p-9"):
        _conduct(_meetings(scripted_game)[2], stores=stores)


@pytest.mark.parametrize(
    ("threshold", "carried"), [(None, 1), (0.2, 0), (0.9, 1), (0.95, 0)]
)
def test_the_confidence_floor_is_read_from_the_recording(
    scripted_game: Path, threshold: float | None, carried: int
) -> None:
    """Planted: the recorded floor moved; the cell follows the recorded value.

    At the recorded floor only the impostors' ballots for p-7 meet it; at 0.2
    crewmate p-9's ballot meets it too; at 0.9, the impostors' own confidence, the
    inclusive floor still admits them; at 0.95 no ballot does.
    """

    third = _meetings(scripted_game)[2]
    entry = third.model_copy(update={"skip_confidence_threshold": threshold})
    cells = _conduct(entry if threshold is not None else third)
    assert cells["ejections_carried_by_impostors_alone"] == carried


def test_the_roles_are_read_from_the_seed(scripted_game: Path) -> None:
    """Planted: p-9 read as an impostor adds its ballot to the impostor cells."""

    third = _meetings(scripted_game)[2]
    base = _conduct(third)
    moved = _moved(base, _conduct(third, roles={**_ROLES, "p-9": "IMPOSTOR"}))
    assert moved == {
        "impostor_ballots": 1,
        "impostor_ejects": 1,
        "ejects_without_citation": 1,
    }
