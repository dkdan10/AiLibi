"""Task 16.7 — the typed first-hand-sighting self-channel accessor.

Pins ``TacticalAgent.sighting_records_for_meeting`` (``orchestrator/game.py``),
the vent accessor's polarity-inverted sibling. Where
:meth:`TacticalAgent.vent_witness_records_for_meeting` (Task 15.4) reports only
``saw_player`` episodic rows carrying the witness-gated ``"vent"`` action stamp,
this accessor reports EVERY first-hand (``provenance == "observed"``)
``saw_player`` row -- vent-witnessed rows included -- plus the ``co_present``
projection (the other subjects the observer saw in the same room on the same
tick). Those rows feed the meeting layer's grounded-vouch corroboration channel,
never a contradiction flag and never the dead trust field.

What is pinned here, and why:

1. DETERMINISM + SELF-ONLY + TICK ORDER -- ingesting first-hand packets across
   several ticks yields the exact expected tuple in tick order off the agent's
   OWN episodic log, and the accessor is a pure read (two calls are equal and
   mutate nothing). A silent reorder or an accidental mutation would desync the
   grounded-vouch feed from the rendered prose the model speaks.
2. THE DROPPED VENT FILTER (the inverted 15.4 assertion) -- a ``saw_player`` row
   with ``action == "vent"`` DOES mint a sighting record, unlike the vent
   accessor test where an ``action=None`` row minted nothing. Both accessors are
   asserted side by side so the sibling relationship (same rows, sighting keeps
   both, vent keeps only the stamped one) cannot regress unnoticed.
3. CO_PRESENT PROJECTION -- several subjects sharing one (tick, room) each name
   the others (sorted); a subject seen alone carries ``()``; a subject in a
   different room on the same tick never co-mentions. This is the Task 13.9
   grouping the §6.6 renderer's "(with ...)" suffix reads, so the typed channel
   and the rendered prose cannot drift.
4. REPORTED TESTIMONY NEVER ENTERS (self-only leak posture) -- another speaker's
   public ``saw_player`` statement lands in episodic memory as
   ``provenance == "reported"`` content (Task 13.5.2); the grounding channel
   reads only first-hand observed rows, so someone ELSE's speech can never become
   this agent's own record. The reported row is genuinely appended (roster gate
   passes), so it is the accessor's own filter -- not a silent skip -- that
   excludes it.
5. A FRESH AGENT reports nothing.
6. ``_build_participants`` THREADS IT -- the meeting-open snapshot lands on the
   right participant and only that one, exactly like the vent channel.
7. THE PROTOCOL GATE -- the runtime-checkable :class:`MeetingAwareAgent` now
   REQUIRES the sighting accessor, so a meeting double carrying only the
   pre-16.7 surface (including the vent accessor) no longer satisfies the
   protocol and can never cross ``_build_participants`` without the grounding
   channel.
8. MALFORMED PAYLOAD DEFENSIVENESS -- a hand-appended ``saw_player`` row with a
   non-string ``player_id`` or ``room`` contributes nothing (the defensive
   ``.get`` + ``isinstance`` convention), while a well-formed row beside it still
   does.

Mirrors ``TestVentWitnessRecordsAccessor`` (same module's Task 15.4 suite)
one-for-one, polarity-adjusted.
"""

from __future__ import annotations

from collections.abc import Mapping

from agents.memory.episodic import EpisodicEvent
from agents.perception import EVENT_SAW_PLAYER, PROVENANCE_OBSERVED, ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from meetings.manager import SuspicionEntry
from meetings.schemas import ReportedStatement, SightingRecord, VentWitnessRecord
from observation.packet import GlobalView, ObservationPacket, PlayerView, SelfView
from orchestrator.game import (
    MeetingAwareAgent,
    TacticalAgent,
    _build_participants,  # noqa: PLC2701
)
from orchestrator.seeder import seed_initial_state


def _view(subject: str, room: str, action: str | None = None) -> PlayerView:
    """One first-hand sighting stamp (default: an ordinary, non-vent sighting)."""

    return PlayerView(id=subject, room=room, action=action)


def _sighting_packet(
    *,
    agent_id: str,
    tick: int,
    players: tuple[PlayerView, ...],
    self_room: str = "CAFETERIA",
) -> ObservationPacket:
    """A packet whose ``visible_players`` carries first-hand sighting stamps.

    The polarity-adjusted twin of the vent accessor's ``_witness_packet``
    (``tests/orchestrator/test_meeting_integration.py``): identical
    ``ObservationPacket`` scaffolding, but ``visible_players`` is parameterised
    as a tuple so a single packet can seed the co-present projection (several
    subjects in one room on one tick) and the empty-perception baseline
    (``players=()`` runs perception -- it still appends the ``self_state`` row --
    without minting any sighting record). The accessor never reads ``self_room``,
    so the observer's own room is an inert scaffold field here.
    """

    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(room=self_room, role="CREWMATE", pending_task_id=None),
        visible_players=players,
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


class TestSightingRecordsAccessor:
    """Task 16.7: ``TacticalAgent.sighting_records_for_meeting`` reports the
    agent's OWN first-hand sightings from episodic memory -- every observed
    ``saw_player`` row (the vent-action filter dropped) with the ``co_present``
    projection attached -- and the protocol member is load-bearing at the
    ``_build_participants`` isinstance gate."""

    def _crew_agent(self, agent_id: str = "p-2") -> TacticalAgent:
        return TacticalAgent(
            agent_id=agent_id,
            role="CREWMATE",
            policy=CrewmatePolicy(agent_id=agent_id),
        )

    def test_deterministic_self_only_and_tick_ordered(self) -> None:
        agent = self._crew_agent()
        # Three ordinary first-hand sightings across ascending ticks, each
        # subject alone in its (tick, room).
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2", tick=3, players=(_view("p-3", "WEST_HALL"),)
            ),
            memory=agent.memory.episodic,
        )
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2", tick=5, players=(_view("p-5", "MEDBAY"),)
            ),
            memory=agent.memory.episodic,
        )
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2", tick=7, players=(_view("p-4", "REACTOR"),)
            ),
            memory=agent.memory.episodic,
        )

        expected = (
            SightingRecord(subject="p-3", room="WEST_HALL", tick=3),
            SightingRecord(subject="p-5", room="MEDBAY", tick=5),
            SightingRecord(subject="p-4", room="REACTOR", tick=7),
        )
        assert agent.sighting_records_for_meeting() == expected

        # Pure read: two calls agree and neither mutates the episodic log.
        before = len(agent.memory.episodic)
        first = agent.sighting_records_for_meeting()
        second = agent.sighting_records_for_meeting()
        assert first == second == expected
        assert len(agent.memory.episodic) == before

    def test_incriminating_action_rows_are_excluded(self) -> None:
        # The grounded-vouch channel is EXCULPATION ("not role-proving"), so a
        # witnessed kill or vent -- which names its subject an impostor -- must
        # NOT become a SightingRecord (grounding a sighting against it would
        # lower a witnessed killer's/venter's suspicion via the -0.05). An
        # ordinary sighting beside them still records; the vent accessor still
        # keeps the vent (each channel owns its own action).
        agent = self._crew_agent()
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2", tick=5, players=(_view("p-5", "MEDBAY"),)
            ),
            memory=agent.memory.episodic,
        )
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2",
                tick=9,
                players=(_view("p-6", "REACTOR", action="vent"),),
            ),
            memory=agent.memory.episodic,
        )
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2",
                tick=11,
                players=(_view("p-7", "ADMIN", action="kill"),),
            ),
            memory=agent.memory.episodic,
        )

        # Only the ordinary sighting survives into the grounding channel.
        assert agent.sighting_records_for_meeting() == (
            SightingRecord(subject="p-5", room="MEDBAY", tick=5),
        )
        # The vent accessor still keeps the vent (its own channel is unchanged).
        assert agent.vent_witness_records_for_meeting() == (
            VentWitnessRecord(subject="p-6", room="REACTOR", tick=9),
        )

    def test_co_present_projects_the_same_room_same_tick_companions(self) -> None:
        # One packet: three subjects share MEDBAY at tick 5 and one sits alone in
        # REACTOR at the same tick. Each MEDBAY record names the OTHER two
        # (sorted, though packet order is p-6, p-5, p-3); the REACTOR subject is
        # alone (``()``); and the different-room subject never cross-mentions.
        agent = self._crew_agent()
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2",
                tick=5,
                players=(
                    _view("p-6", "MEDBAY"),
                    _view("p-5", "MEDBAY"),
                    _view("p-3", "MEDBAY"),
                    _view("p-7", "REACTOR"),
                ),
            ),
            memory=agent.memory.episodic,
        )

        assert agent.sighting_records_for_meeting() == (
            SightingRecord(
                subject="p-6", room="MEDBAY", tick=5, co_present=("p-3", "p-5")
            ),
            SightingRecord(
                subject="p-5", room="MEDBAY", tick=5, co_present=("p-3", "p-6")
            ),
            SightingRecord(
                subject="p-3", room="MEDBAY", tick=5, co_present=("p-5", "p-6")
            ),
            SightingRecord(subject="p-7", room="REACTOR", tick=5, co_present=()),
        )

    def test_reported_testimony_never_enters_the_channel(self) -> None:
        # Another speaker's public saw_player statement lands in episodic memory
        # as provenance="reported" content (Task 13.5.2); the typed grounding
        # channel reads only first-hand observed rows, so someone ELSE's speech
        # can never become this agent's own record. The reported row is really
        # appended (both speaker and subject are known roster ids), so it is the
        # accessor's own provenance/type filter -- not the roster skip -- that
        # excludes it.
        agent = self._crew_agent()
        ingest_packet(
            packet=_sighting_packet(
                agent_id="p-2",
                tick=4,
                players=(_view("p-3", "MEDBAY"), _view("p-5", "MEDBAY")),
            ),
            memory=agent.memory.episodic,
        )
        baseline = agent.sighting_records_for_meeting()
        assert baseline == (
            SightingRecord(subject="p-3", room="MEDBAY", tick=4, co_present=("p-5",)),
            SightingRecord(subject="p-5", room="MEDBAY", tick=4, co_present=("p-3",)),
        )

        before_len = len(agent.memory.episodic)
        agent.absorb_reported_testimony(
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind="saw_player",
                    subject="p-5",
                    from_tick=6,
                    to_tick=6,
                    room="REACTOR",
                ),
            )
        )
        # The reported row was appended (proving the roster gate passed) yet the
        # first-hand accessor output is byte-identical.
        assert len(agent.memory.episodic) > before_len
        assert agent.sighting_records_for_meeting() == baseline

    def test_fresh_agent_reports_nothing(self) -> None:
        assert self._crew_agent().sighting_records_for_meeting() == ()

    def test_build_participants_threads_the_accessor(self) -> None:
        state = seed_initial_state(seed=1, game_map=load_canonical_map(), num_players=4)
        agents: dict[PlayerId, object] = {}
        for pid, player in state.players.items():
            policy = CrewmatePolicy(agent_id=pid)
            agent = TacticalAgent(agent_id=pid, role=player.role, policy=policy)
            # Perception must run once per agent before the participant render
            # (store contract); an EMPTY-players packet appends the self_state
            # row without minting any sighting record -- the polarity-adjusted
            # analog of the vent test's stamp-free packet, which for the
            # sighting channel means no visible players at all.
            ingest_packet(
                packet=_sighting_packet(agent_id=pid, tick=4, players=()),
                memory=agent.memory.episodic,
            )
            agents[pid] = agent
        witness_id = sorted(state.players)[0]
        witness = agents[witness_id]
        assert isinstance(witness, TacticalAgent)
        ingest_packet(
            packet=_sighting_packet(
                agent_id=witness.agent_id,
                tick=5,
                players=(_view("p-5", "MEDBAY"),),
            ),
            memory=witness.memory.episodic,
        )

        participants = _build_participants(
            state=state,
            agents=agents,  # type: ignore[arg-type]
            token_budget=1500,
        )

        by_id = {participant.agent_id: participant for participant in participants}
        assert by_id[witness_id].sighting_records == (
            SightingRecord(subject="p-5", room="MEDBAY", tick=5),
        )
        for pid, participant in by_id.items():
            if pid != witness_id:
                assert participant.sighting_records == ()

    def test_isinstance_gate_requires_the_sighting_accessor(self) -> None:
        # The protocol member is load-bearing: a meeting double carrying the
        # FULL pre-16.7 surface -- including the Task 15.4 vent accessor -- but
        # missing sighting_records_for_meeting no longer satisfies
        # MeetingAwareAgent, so it can never cross _build_participants and
        # silently run a meeting without the grounded-vouch channel.
        class _PreSightingDouble:
            @property
            def agent_id(self) -> PlayerId:
                return "p-1"

            @property
            def role(self) -> Role:
                return "CREWMATE"

            def render_memory_for_meeting(
                self,
                *,
                token_budget: int = 1500,
                suspicion_override: Mapping[PlayerId, float] | None = None,
            ) -> str:
                return "## Your role: CREWMATE\nmemory"

            def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
                return ()

            def vent_witness_records_for_meeting(
                self,
            ) -> tuple[VentWitnessRecord, ...]:
                return ()

        assert not isinstance(_PreSightingDouble(), MeetingAwareAgent)
        assert isinstance(self._crew_agent(), MeetingAwareAgent)

    def test_malformed_payload_contributes_nothing(self) -> None:
        # The defensive ``.get`` + ``isinstance`` convention: a saw_player row
        # whose ``player_id`` or ``room`` is not a string is dropped, while a
        # well-formed row appended beside it still mints its record (and the
        # dropped rows never contaminate the co_present projection either).
        agent = self._crew_agent()
        episodic = agent.memory.episodic
        episodic.append(
            EpisodicEvent(
                tick=5,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": "p-5", "room": "MEDBAY", "action": None},
                provenance=PROVENANCE_OBSERVED,
            )
        )
        episodic.append(
            EpisodicEvent(
                tick=6,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": 123, "room": "MEDBAY", "action": None},
                provenance=PROVENANCE_OBSERVED,
            )
        )
        episodic.append(
            EpisodicEvent(
                tick=7,
                type=EVENT_SAW_PLAYER,
                payload={"player_id": "p-7", "room": None, "action": None},
                provenance=PROVENANCE_OBSERVED,
            )
        )

        assert agent.sighting_records_for_meeting() == (
            SightingRecord(subject="p-5", room="MEDBAY", tick=5),
        )
