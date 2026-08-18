"""The private-hard-evidence ballot citation channel (Task 16.5, C8/C3).

Pins the ``primary_reason_observation_id`` plumbing this task introduces
(audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8, DESIGN.md
§5.5 / §6.6) end to end, ENFORCEMENT-FREE:

* the additive schema field on :class:`meetings.schemas.VoteBallot` -- a
  payload without the key parses to ``None`` (the backward-compat contract
  every committed replay depends on), and the committed corpus still round-trips;
* the manager's mark-and-null validation
  (:func:`meetings.manager._normalize_ballot_observation_id`): a cited id in
  the voter's OWN typed valid-id set passes through untouched, an id outside it
  is nulled with :data:`meetings.manager.INVALID_OBSERVATION_ID_MARKER` and the
  ballot is NEVER rejected;
* the typed threading of the voter's valid-id universe onto
  :class:`meetings.manager.MeetingParticipant` via
  :meth:`orchestrator.game.TacticalAgent.observation_ids_for_meeting` at
  :func:`orchestrator.game._build_participants`;
* and the enforcement-free invariant: no gate, guard, or tally consults the
  field (Task 16.6 enforces), so a valid citation and a null citation produce
  the identical outcome.

The manager harness mirrors ``tests.meetings.test_manager`` (the turn-id
mark-and-null tests, ``TestBallotReasonIdIntegrity``); the committed
backward-compat pin mirrors ``tests.meetings.test_schemas_pooling``.
"""

from __future__ import annotations

from pathlib import Path


from agents.perception import EVENT_SAW_PLAYER, ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from engine.world import load_canonical_map
from meetings.manager import (
    INVALID_OBSERVATION_ID_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    _default_vote,  # noqa: PLC2701
)
from meetings.schemas import ObservationId, VoteBallot
from observation.packet import GlobalView, ObservationPacket, PlayerView, SelfView
from orchestrator.game import (
    MeetingAwareAgent,
    TacticalAgent,
    _build_participants,  # noqa: PLC2701
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from tests.meetings._manager_helpers import (
    _obs_vote_responder,
    _participants,
    _run_meeting,
)

# The committed 9p/2i meeting-heavy set (Tasks 7.8, 8.12): seed 0 carries
# resolved meetings recorded under the current substrate but BEFORE the Task
# 16.5 ``primary_reason_observation_id`` field existed -- the faithful
# pre-citation committed rows for the additive-schema pin below.
_COMMITTED_9P2I_SEED_0 = (
    Path(__file__).resolve().parents[2]
    / "replays"
    / "samples"
    / "9p2i"
    / "replay-seed-0.jsonl"
)


def _kill_packet(
    *,
    agent_id: str,
    tick: int,
    players: tuple[PlayerView, ...],
    self_room: str = "CAFETERIA",
) -> ObservationPacket:
    """A packet whose ``visible_players`` may carry a witnessed-kill stamp.

    ``PlayerView(action="kill")`` is the ``OBSERVED_KILL_ACTION`` stamp the
    engine's witness-gated observation layer sets; ingested, it becomes a
    ``saw_player`` row that :meth:`TacticalAgent.observation_ids_for_meeting`
    id-stamps like any first-hand observation. ``players=()`` still appends the
    ``self_state`` row (so every agent has at least one id-stamped row), the
    citation-universe baseline.
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


def _kill_witness_agent(agent_id: str = "p-2") -> TacticalAgent:
    """A REAL crew :class:`TacticalAgent` holding a witnessed kill NOBODY spoke.

    The packet stamps a private ``saw_player action="kill"`` row into the
    agent's own episodic memory; no meeting turn ever names it, so it is
    first-hand evidence that never entered the transcript -- exactly the
    ``primary_reason_observation_id`` use case (cite what the public chain
    lacks).
    """

    agent = TacticalAgent(
        agent_id=agent_id, role="CREWMATE", policy=CrewmatePolicy(agent_id=agent_id)
    )
    ingest_packet(
        packet=_kill_packet(
            agent_id=agent_id,
            tick=6,
            players=(PlayerView(id="p-7", room="ELECTRICAL", action="kill"),),
        ),
        memory=agent.memory.episodic,
    )
    return agent


def _witnessed_kill_id(agent: TacticalAgent) -> ObservationId:
    """The observation id of the agent's private witnessed-kill row."""

    return next(
        event.observation_id
        for event in agent.memory.episodic.recent(since_tick=0)
        if event.type == EVENT_SAW_PLAYER
        and event.payload.get("action") == "kill"
        and event.observation_id is not None
    )


class TestBallotObservationIdSchema:
    def test_round_trips_with_the_field(self) -> None:
        ballot = VoteBallot(
            voter="p-2",
            target="p-3",
            confidence=0.8,
            primary_reason_id=None,
            primary_reason_observation_id="p-2:410:1",
            considered_alternatives=(),
            rationale_text="I saw it.",
        )

        parsed = VoteBallot.model_validate_json(ballot.model_dump_json())

        assert parsed == ballot
        assert parsed.primary_reason_observation_id == "p-2:410:1"

    def test_payload_without_the_key_parses_to_none(self) -> None:
        # The additive contract: a payload recorded BEFORE the field existed
        # (no key) parses to None, never a validation error.
        parsed = VoteBallot.model_validate(
            {
                "voter": "p-2",
                "target": "SKIP",
                "confidence": 0.5,
                "primary_reason_id": None,
                "considered_alternatives": [],
                "rationale_text": "unsure",
            }
        )

        assert parsed.primary_reason_observation_id is None


class TestCommittedBallotsBackwardCompatible:
    def test_committed_9p2i_seed_0_ballots_parse_with_null_field(self) -> None:
        # The additive-field pin (verbatim shape of test_schemas_pooling's committed
        # pin): every committed ballot parses, carries a well-typed citation
        # (ObservationId or None), and the whole entry round-trips byte-for-byte
        # through the extended schema. The baseline-5 re-record (citation_gate ON,
        # 16.15 citation asks) now POPULATES the field where the voter cited an
        # observation and leaves it None otherwise, so the committed corpus exercises
        # the additive field on real bytes (a stronger round-trip than the
        # pre-citation all-None shape it superseded). The "no key -> None"
        # backward-compat contract itself is pinned synthetically by
        # ``TestBallotObservationIdSchema.test_payload_without_the_key_parses_to_none``.
        meetings = [
            entry
            for entry in read_all_entries(_COMMITTED_9P2I_SEED_0)
            if isinstance(entry, MeetingReplayEntry)
        ]

        assert meetings, "committed 9p2i seed 0 carries no meeting entry"
        cited = 0
        for entry in meetings:
            assert entry.ballots, "committed meeting entry carries no ballot"
            for ballot in entry.ballots:
                citation = ballot.primary_reason_observation_id
                assert citation is None or isinstance(citation, str)
                if citation is not None:
                    cited += 1
            assert (
                MeetingReplayEntry.model_validate_json(entry.model_dump_json()) == entry
            )
        # The field is exercised on the committed set: at least one recorded ballot
        # carries a real observation citation (e.g. p-5:8:1, p-3:22:1 in seed 0).
        assert cited


class TestBallotObservationIdValidation:
    def test_fabricated_id_is_nulled_with_marker(self) -> None:
        # Mark-and-null through a REAL manager run: p-2's participant carries a
        # DIFFERENT valid-id set than the fabricated citation, so the field is
        # nulled with the audit marker prefixed to rationale_text -- and the
        # ballot is NEVER rejected (p-2 still casts its SKIP).
        result, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={"p-2": "p-2:999:9"}),
            participants=_participants({"p-2": ("p-2:410:0",)}),
        )

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_observation_id is None
        assert p2.rationale_text.startswith(
            INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-2:999:9")
        )
        assert p2.target == "SKIP"

    def test_valid_citation_passes_through_untouched(self) -> None:
        # A citation that IS in the voter's own valid-id set survives unchanged,
        # no marker.
        result, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={"p-2": "p-2:410:0"}),
            participants=_participants({"p-2": ("p-2:410:0",)}),
        )

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_observation_id == "p-2:410:0"
        assert "[invalid primary_reason_observation_id" not in p2.rationale_text

    def test_null_citation_never_trips_the_validator(self) -> None:
        # None is the pre-16.5 shape and the default: it passes through untouched
        # regardless of the participant's valid-id set.
        result, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={}),
            participants=_participants({"p-2": ("p-2:410:0",)}),
        )

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_observation_id is None
        assert "[invalid primary_reason_observation_id" not in p2.rationale_text


class TestPrivateWitnessedKillCitation:
    """The DoD fixture: a voter cites a witnessed kill NOBODY spoke about."""

    def test_private_kill_id_validates_and_fabricated_id_nulls(self) -> None:
        agent = _kill_witness_agent()
        observation_ids = agent.observation_ids_for_meeting()
        kill_id = _witnessed_kill_id(agent)
        assert kill_id in observation_ids

        # The private id is in the voter's OWN valid-id set -> survives untouched
        # even though no meeting turn ever spoke it.
        valid, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={"p-2": kill_id}),
            participants=_participants({"p-2": observation_ids}),
        )
        p2_valid = next(b for b in valid.ballots if b.voter == "p-2")
        assert p2_valid.primary_reason_observation_id == kill_id
        assert "[invalid primary_reason_observation_id" not in p2_valid.rationale_text

        # A fabricated id the agent never observed nulls with the marker.
        fabricated, _ = _run_meeting(
            _obs_vote_responder(observation_ids_by_voter={"p-2": "p-2:999:9"}),
            participants=_participants({"p-2": observation_ids}),
        )
        p2_fab = next(b for b in fabricated.ballots if b.voter == "p-2")
        assert p2_fab.primary_reason_observation_id is None
        assert p2_fab.rationale_text.startswith(
            INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-2:999:9")
        )


class TestBallotObservationIdSatisfiesTheGraduatedGate:
    def test_valid_citation_keeps_the_eject_where_null_coerces(self) -> None:
        # The 16.5-era "enforcement-free" invariant (no gate consults the
        # field) was the PRE-graduation contract; Task 16.17 graduated the
        # 16.6 citation gate to unconditional, so the enforcement has
        # arrived and the two runs now DIVERGE exactly at the citation: an
        # observation-cited zero-flag EJECT stands (the C3 honest-witness
        # path), while the identical uncited ballot is coerced to SKIP with
        # the audit marker.
        targets = {voter: "p-3" for voter in ("p-1", "p-2", "p-3", "p-4")}

        def _run(observation_ids_by_voter: dict[str, ObservationId | None]):  # type: ignore[no-untyped-def]
            result, _ = _run_meeting(
                _obs_vote_responder(
                    observation_ids_by_voter=observation_ids_by_voter, targets=targets
                ),
                participants=_participants({"p-2": ("p-2:410:0",)}),
            )
            return result

        cited = _run({"p-2": "p-2:410:0"})
        uncited = _run({})

        p2_cited = next(b for b in cited.ballots if b.voter == "p-2")
        p2_uncited = next(b for b in uncited.ballots if b.voter == "p-2")
        gate_prefix = UNCITED_ZERO_FLAG_EJECT_MARKER.split("{", 1)[0]
        assert p2_cited.target == "p-3"
        assert p2_cited.primary_reason_observation_id == "p-2:410:0"
        assert gate_prefix not in p2_cited.rationale_text
        assert p2_uncited.target == "SKIP"
        assert p2_uncited.rationale_text.startswith(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
        )

    def test_default_vote_carries_a_null_citation(self) -> None:
        # The manager's fail-soft default ballot cites nothing.
        assert _default_vote(voter="p-1").primary_reason_observation_id is None


class TestObservationIdThreadingIsTyped:
    """The typed end-to-end threading through ``_build_participants`` (the
    test_sighting_accessor.py precedent), including the pre-16.5 double failing
    the runtime protocol check."""

    def test_build_participants_threads_the_accessor(self) -> None:
        state = seed_initial_state(seed=1, game_map=load_canonical_map(), num_players=4)
        agents: dict[str, object] = {}
        for pid, player in state.players.items():
            agent = TacticalAgent(
                agent_id=pid, role=player.role, policy=CrewmatePolicy(agent_id=pid)
            )
            # Perception must run once per agent before the participant render
            # (store contract); an empty-players packet still appends the
            # id-stamped self_state row, so every voter's citation universe is
            # non-empty.
            ingest_packet(
                packet=_kill_packet(agent_id=pid, tick=4, players=()),
                memory=agent.memory.episodic,
            )
            agents[pid] = agent
        witness_id = sorted(state.players)[0]
        witness = agents[witness_id]
        assert isinstance(witness, TacticalAgent)
        ingest_packet(
            packet=_kill_packet(
                agent_id=witness.agent_id,
                tick=5,
                players=(PlayerView(id="p-7", room="ELECTRICAL", action="kill"),),
            ),
            memory=witness.memory.episodic,
        )
        kill_id = _witnessed_kill_id(witness)

        participants = _build_participants(
            state=state,
            agents=agents,  # type: ignore[arg-type]
            token_budget=1500,
        )

        by_id = {participant.agent_id: participant for participant in participants}
        assert kill_id in by_id[witness_id].observation_ids
        for participant in participants:
            bound_agent = agents[participant.agent_id]
            assert isinstance(bound_agent, TacticalAgent)
            # Populated VERBATIM from the accessor, and non-empty for every
            # living participant (the self_state row is always stamped).
            assert (
                participant.observation_ids == bound_agent.observation_ids_for_meeting()
            )
            assert participant.observation_ids

    def test_isinstance_gate_requires_the_observation_accessor(self) -> None:
        # The protocol member is load-bearing: a double carrying the FULL
        # pre-16.5 surface -- render, suspicion, the 15.4 vent accessor, and the
        # 16.7 sighting accessor -- but missing observation_ids_for_meeting no
        # longer satisfies MeetingAwareAgent, so it can never cross
        # _build_participants and silently run a meeting without the citation set.
        from collections.abc import Mapping

        from engine.entities import PlayerId, Role
        from meetings.manager import SuspicionEntry
        from meetings.schemas import SightingRecord, VentWitnessRecord

        class _PreObservationDouble:
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

            def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
                return ()

        assert not isinstance(_PreObservationDouble(), MeetingAwareAgent)
