"""Task 16.7.1 — the pooling/citation spectator surface serves end-to-end.

Task 16.7 made roll-call self-placement structurally speakable in the meeting
layer: a :class:`meetings.schemas.WhereaboutsClaim` ("I was in ``room`` at
``tick``") rides a turn as the FIFTH :class:`meetings.schemas.ObservationClaim`
variant. Task 16.5 added the private hard-evidence citation channel:
``meetings.schemas.VoteBallot.primary_reason_observation_id``, a stable episodic
observation id (``{agent_id}:{tick}:{seq}``) drawn from the VOTER'S OWN memory,
which the manager validates but no gate consults.

The privileged spectator path (``api.replay_loader._observation_claim_view``)
was deliberately exhaustive-with-raise (it raised ``TypeError`` on any unknown
observation variant — the "no silent fallbacks" doctrine), so the FIRST replay
carrying a structured whereabouts turn would crash the replay API; and the
citation field had no mirror on ``api.schemas.BallotView`` at all.

This module pins the fix: a real replay whose recorded meeting carries BOTH a
``WhereaboutsClaim`` turn and a cited :class:`VoteBallot` loads and serves
through :class:`api.replay_loader.ReplayLoader` without error, the whereabouts
sighting surfaces (room / tick, no subject — the speaker IS the subject), and
the citation round-trips display-only onto ``BallotView``. The fixture is built
through the production :class:`orchestrator.replay.ReplayLog` writer
(state-hash-verified on load), so it matches exactly what a recording produces.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from engine.actions import Action, KillAction, ReportBodyAction, WaitAction
from engine.tick import advance_tick
from engine.world import load_canonical_map
from meetings.schemas import (
    AlibiClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    VoteBallot,
    WhereaboutsClaim,
)
from orchestrator.game import apply_meeting_result
from orchestrator.replay import ReplayLog, _state_hash
from orchestrator.seeder import seed_initial_state

from api.replay_loader import ReplayLoader, _observation_claim_view
from api.schemas import WhereaboutsClaimView

_NUM_PLAYERS = 4
_NUM_IMPOSTORS = 1


def _wait(actor: str) -> WaitAction:
    return WaitAction.model_validate({"actor": actor, "type": "wait", "payload": {}})


def _write_pooling_meeting_replay(path: Path, *, seed: int = 0) -> dict[str, str | int]:
    """Write a body-report meeting whose transcript carries a whereabouts claim.

    Mirrors ``tests/api/fixtures/sample_replay.write_meeting_replay`` (seed 0:
    ``p-3`` is the impostor; everyone spawns in ``CAFETERIA``) but the recorded
    :class:`MeetingResult` carries a structured :class:`WhereaboutsClaim` (the
    reporter self-places on the public record) beside the ``found_body``
    observation, and exactly ONE :class:`VoteBallot` cites a private episodic
    observation (``primary_reason_observation_id``) while the rest cite none.
    The outcome is ``SKIPPED`` so the engine-state application stays trivial —
    the serving path this test pins is independent of the vote outcome.
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
            # Task 16.7: the reporter self-places on the public record. No
            # subject field — the subject IS the speaker (``turn.speaker``).
            WhereaboutsClaim(
                type="whereabouts",
                tick=meeting_tick,
                room="CAFETERIA",
            ),
        ),
        claims=(),
        free_text=f"{reporter}: found {victim} in CAFETERIA; I was in CAFETERIA.",
    )
    # Exactly one voter cites a private episodic observation from its OWN memory
    # (the ``{agent_id}:{tick}:{seq}`` scheme, Task 16.5); the rest cite none.
    cited_voter = living[0]
    citation_id = f"{cited_voter}:{kill_tick}:0"
    ballots = tuple(
        VoteBallot(
            voter=agent_id,
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            primary_reason_observation_id=(
                citation_id if agent_id == cited_voter else None
            ),
            considered_alternatives=(),
            rationale_text="not enough evidence",
        )
        for agent_id in living
    )
    result = MeetingResult(
        meeting_id=meeting_id,
        triggered_by=reporter,
        trigger_tick=meeting_tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=ballots,
        contradictions=(),
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
        "reporter": reporter,
        "meeting_tick": meeting_tick,
        "cited_voter": cited_voter,
        "citation_id": citation_id,
    }


def test_pooling_surface_serves_through_replay_api(tmp_path: Path) -> None:
    """The pre-fix TypeError input now loads and serves without error.

    Regression pin: before Task 16.7.1, ``_observation_claim_view`` raised
    ``TypeError`` on the whereabouts kind, so this very fixture crashed the
    loader. The load below is the assertion — it must not raise — and the DTO
    checks confirm the self-placement and the citation are surfaced faithfully.
    """

    expected = _write_pooling_meeting_replay(tmp_path / "replay-seed-0.jsonl")

    replay = ReplayLoader(replay_dir=tmp_path).load_replay(str(expected["game_id"]))

    assert len(replay.meetings) == 1
    meeting = replay.meetings[0]

    # The whereabouts claim rides the opening turn's observations, mirrored to
    # the spectator DTO with room / tick intact — and NO subject (the speaker is
    # the subject, so the view carries no such field).
    where_views = [
        obs
        for turn in meeting.turns
        for obs in turn.observations
        if isinstance(obs, WhereaboutsClaimView)
    ]
    assert len(where_views) == 1
    where = where_views[0]
    assert where.type == "whereabouts"
    assert where.room == "CAFETERIA"
    assert where.tick == expected["meeting_tick"]

    # The citation round-trips display-only onto the cited ballot; every other
    # ballot surfaces ``None`` (it cited no private observation).
    ballots = {b.voter: b for b in meeting.ballots}
    cited = ballots[str(expected["cited_voter"])]
    assert cited.primary_reason_observation_id == expected["citation_id"]
    uncited = [b for v, b in ballots.items() if v != expected["cited_voter"]]
    assert uncited  # the fixture has more than one voter
    assert all(b.primary_reason_observation_id is None for b in uncited)


def test_unknown_observation_claim_raises() -> None:
    """The exhaustive-with-raise doctrine survives the fifth variant.

    ``_observation_claim_view`` mirrors the five known observation kinds and
    raises ``TypeError`` on anything else (no silent fallback). An
    :class:`meetings.schemas.AlibiClaim` is a statement claim, NOT a member of
    the observation union, so it exercises the terminal ``raise``. The ``cast``
    is deliberate: mypy correctly rejects the off-union argument, and this test
    asserts the runtime guard behind that static wall.
    """

    stray = AlibiClaim(
        type="alibi",
        subject="p-0",
        from_tick=1,
        to_tick=2,
        room="CAFETERIA",
    )
    with pytest.raises(TypeError, match="unsupported observation claim"):
        _observation_claim_view(cast(ObservationClaim, stray))


def test_existing_observation_variants_unchanged(tmp_path: Path) -> None:
    """The pre-16.7 observation variants and ballots still serve unchanged.

    Loads the shared meeting fixture (a ``found_body`` opening + an
    ``alibi_conflict`` contradiction) and confirms adding the fifth variant and
    the citation field did not perturb the existing mapping: no whereabouts view
    leaks, the classic observation/contradiction kinds are intact, and every
    ballot surfaces ``primary_reason_observation_id is None`` (recorded before
    the field existed, so the additive ``None`` default holds).
    """

    from tests.api.fixtures.sample_replay import write_meeting_replay

    expected = write_meeting_replay(tmp_path / "replay-seed-0.jsonl")

    replay = ReplayLoader(replay_dir=tmp_path).load_replay(expected.game_id)

    meeting = replay.meetings[0]
    opening = meeting.turns[0]
    assert [obs.type for obs in opening.observations] == ["found_body"]
    assert [c.kind for c in meeting.contradictions] == ["alibi_conflict"]
    # No whereabouts view leaked into the classic fixture.
    assert not any(
        isinstance(obs, WhereaboutsClaimView)
        for turn in meeting.turns
        for obs in turn.observations
    )
    # Ballots predate the citation field: every one surfaces the None default.
    assert meeting.ballots
    assert all(b.primary_reason_observation_id is None for b in meeting.ballots)
