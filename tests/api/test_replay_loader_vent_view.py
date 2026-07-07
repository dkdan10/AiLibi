"""Task 15.4.1 — the spectator mirror for vent observations serves end-to-end.

Task 15.4 made witnessed impostor vents structurally speakable in the meeting
layer: a :class:`meetings.schemas.SawVentObservation` rides a turn, and a
grounded sighting mints a role-proving ``vent_sighting``
:class:`meetings.schemas.ContradictionRef` the manager persists at close. The
privileged spectator path was deliberately exhaustive-with-raise
(``api.replay_loader._observation_claim_view`` /
``_contradiction_view`` raised ``TypeError`` on the unknown fourth kind — the
"no silent fallbacks" doctrine), so the FIRST replay carrying a structured vent
turn would crash the replay API.

This module pins the fix: a real replay whose recorded meeting carries BOTH a
``SawVentObservation`` turn and a ``vent_sighting`` contradiction loads and
serves through :class:`api.replay_loader.ReplayLoader` without error, and the
served DTOs expose the sighting (subject / room / tick) plus the strong
role-proving flag. The fixture is built through the production
:class:`orchestrator.replay.ReplayLog` writer (state-hash-verified on load), so
it matches exactly what a baseline-3 recording produces.
"""

from __future__ import annotations

from pathlib import Path

from engine.actions import Action, KillAction, ReportBodyAction, WaitAction
from engine.tick import advance_tick
from engine.world import load_canonical_map
from meetings.schemas import (
    ContradictionRef,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    SawVentObservation,
    VoteBallot,
)
from orchestrator.game import apply_meeting_result
from orchestrator.replay import ReplayLog, _state_hash
from orchestrator.seeder import seed_initial_state

from api.replay_loader import ReplayLoader
from api.schemas import ContradictionView, SawVentObservationView

_NUM_PLAYERS = 4
_NUM_IMPOSTORS = 1


def _wait(actor: str) -> WaitAction:
    return WaitAction.model_validate({"actor": actor, "type": "wait", "payload": {}})


def _write_vent_meeting_replay(path: Path, *, seed: int = 0) -> dict[str, str | int]:
    """Write a body-report meeting whose transcript carries a witnessed vent.

    Mirrors ``tests/api/fixtures/sample_replay.write_meeting_replay`` (seed 0:
    ``p-3`` is the impostor; everyone spawns in ``CAFETERIA``) but the recorded
    :class:`MeetingResult` carries a structured :class:`SawVentObservation`
    (the reporter also witnessed the vent) plus the ``vent_sighting``
    contradiction a grounded sighting mints. The outcome is ``SKIPPED`` so the
    engine-state application stays trivial — the serving path this test pins is
    independent of the vote outcome.
    """

    game_map = load_canonical_map()
    game_id = f"headless-seed-{seed}"
    log = ReplayLog(path=path, game_id=game_id)
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
    )

    impostor = next(p for p, s in state.players.items() if s.role == "IMPOSTOR")
    crewmates = sorted(p for p, s in state.players.items() if s.role == "CREWMATE")
    victim = crewmates[0]
    reporter = crewmates[1]
    living = tuple(sorted(p for p in state.players if p != victim))

    # Round-start kill cooldown (DESIGN.md §3.4): no-op until it clears.
    for _ in range(game_map.kill_cooldown_ticks):
        input_tick = state.tick
        waits: list[Action] = [_wait(pid) for pid in sorted(state.players)]
        state, _events = advance_tick(state, waits, game_map=game_map)
        log.record_tick(input_tick, waits, state)

    kill_tick = state.tick
    tick_kill: list[Action] = [
        _wait(pid) for pid in sorted(state.players) if pid != impostor
    ]
    tick_kill.append(
        KillAction.model_validate(
            {"actor": impostor, "type": "kill", "payload": {"target": victim}}
        )
    )
    input_tick = state.tick
    state, _events = advance_tick(state, tick_kill, game_map=game_map)
    log.record_tick(input_tick, tick_kill, state)
    body_id = f"body-{victim}-{kill_tick}"

    report = ReportBodyAction.model_validate(
        {"actor": reporter, "type": "report", "payload": {"body_id": body_id}}
    )
    meeting_tick = state.tick
    input_tick = state.tick
    state, _events = advance_tick(state, [report], game_map=game_map)
    log.record_tick(input_tick, [report], state)

    meeting_id = f"{game_id}:meeting-0"
    turn_id = f"{meeting_id}:turn-0"
    opening = MeetingTurn(
        turn_id=turn_id,
        turn_index=0,
        speaker=reporter,
        turn_kind="opening",
        reply_to=None,
        observations=(
            FoundBodyObservation(
                type="found_body",
                tick=meeting_tick,
                body_of=victim,
                room="CAFETERIA",
            ),
            SawVentObservation(
                type="saw_vent",
                tick=kill_tick,
                subject=impostor,
                room="CAFETERIA",
            ),
        ),
        claims=(),
        free_text=f"{reporter}: found {victim} in CAFETERIA; I saw {impostor} vent.",
    )
    ballots = tuple(
        VoteBallot(
            voter=agent_id,
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="not enough evidence",
        )
        for agent_id in living
    )
    # A grounded vent is always STRONG (no weak marker in the description): both
    # event ids reference the single public spoken observation (the turn), per
    # ``meetings.schemas.ContradictionRef``.
    contradictions = (
        ContradictionRef(
            contradiction_id=f"{meeting_id}:v0",
            kind="vent_sighting",
            event_a_id=turn_id,
            event_b_id=turn_id,
            subjects=(impostor,),
            description=f"{impostor} vented in CAFETERIA at tick {kill_tick}.",
        ),
    )
    result = MeetingResult(
        meeting_id=meeting_id,
        triggered_by=reporter,
        trigger_tick=meeting_tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=ballots,
        contradictions=contradictions,
        transcript=MeetingTranscript(turns=(opening,)),
    )

    state_hash_before = _state_hash(state)
    state, _post = apply_meeting_result(
        state, result, game_map=game_map, triggering_body_id=body_id
    )
    state_hash_after = _state_hash(state)
    log.record_meeting(
        meeting_id=meeting_id,
        result=result,
        llm_calls=(),
        prompt_versions={},
        state_hash_before=state_hash_before,
        state_hash_after=state_hash_after,
    )

    quiet_tick = state.tick
    input_tick = state.tick
    state, _events = advance_tick(state, [], game_map=game_map)
    log.record_tick(input_tick, [], state)
    log.record_game_end(
        winner="CREWMATES", reason="all_tasks_complete", tick=quiet_tick
    )

    return {
        "game_id": game_id,
        "meeting_id": meeting_id,
        "impostor": impostor,
        "kill_tick": kill_tick,
    }


def test_vent_turn_serves_through_replay_api(tmp_path: Path) -> None:
    """The pre-fix TypeError input now loads and serves without error.

    Regression pin: before Task 15.4.1, ``_observation_claim_view`` (and
    ``_contradiction_view``) raised ``TypeError`` on the vent kind, so this very
    fixture crashed the loader. The load below is the assertion — it must not
    raise — and the DTO checks confirm the sighting is surfaced faithfully.
    """

    expected = _write_vent_meeting_replay(tmp_path / "replay-seed-0.jsonl")

    replay = ReplayLoader(replay_dir=tmp_path).load_replay(str(expected["game_id"]))

    assert len(replay.meetings) == 1
    meeting = replay.meetings[0]

    # The vent sighting rides the opening turn's observations, mirrored to the
    # spectator DTO with subject / room / tick intact.
    vent_views = [
        obs
        for turn in meeting.turns
        for obs in turn.observations
        if isinstance(obs, SawVentObservationView)
    ]
    assert len(vent_views) == 1
    vent = vent_views[0]
    assert vent.type == "saw_vent"
    assert vent.subject == expected["impostor"]
    assert vent.room == "CAFETERIA"
    assert vent.tick == expected["kill_tick"]

    # The role-proving flag mirrors through as a STRONG contradiction.
    vent_flags = [c for c in meeting.contradictions if c.kind == "vent_sighting"]
    assert len(vent_flags) == 1
    flag = vent_flags[0]
    assert isinstance(flag, ContradictionView)
    assert flag.subjects == (expected["impostor"],)
    assert flag.weak is False
    assert flag.severity == "strong"


def test_existing_observation_variants_unchanged(tmp_path: Path) -> None:
    """The three pre-15.4 observation variants still serve byte-identically.

    Loads the shared meeting fixture (a ``found_body`` opening + an
    ``alibi_conflict`` contradiction) and confirms adding the fourth variant
    did not perturb the existing view mapping.
    """

    from tests.api.fixtures.sample_replay import write_meeting_replay

    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl")

    replay = ReplayLoader(replay_dir=tmp_path).load_replay(expected.game_id)

    meeting = replay.meetings[0]
    opening = meeting.turns[0]
    assert [obs.type for obs in opening.observations] == ["found_body"]
    assert [c.kind for c in meeting.contradictions] == ["alibi_conflict"]
    # No vent view leaked into the classic fixture.
    assert not any(
        isinstance(obs, SawVentObservationView)
        for turn in meeting.turns
        for obs in turn.observations
    )
