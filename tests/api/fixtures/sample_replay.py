"""Real replay-log fixtures for the spectator API tests.

Every fixture writes a genuine JSONL replay through the production
:class:`orchestrator.replay.ReplayLog` API, seeding the engine via
:func:`orchestrator.seeder.seed_initial_state` and advancing it with
:func:`engine.tick.advance_tick`. Using the real writer (rather than a
hand-authored mock) guarantees the fixtures match exactly what a headless game
produces, so the loader is exercised against ground truth and cannot drift from
the replay schema.

Seed 0 assigns ``p-3`` the impostor role with every player spawning in the
canonical map's ``CAFETERIA`` (see ``orchestrator/seeder.py``), which is what
makes the kill -> report -> meeting fixture deterministic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
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
    VoteBallot,
)
from orchestrator.game import apply_meeting_result
from orchestrator.replay import LLMCallRecord, ReplayLog, _state_hash
from orchestrator.seeder import seed_initial_state

_NUM_PLAYERS = 4
_NUM_IMPOSTORS = 1
_BAD_HASH = "0" * 64


def _wait(actor: str) -> WaitAction:
    return WaitAction.model_validate({"actor": actor, "type": "wait", "payload": {}})


def _opening_kill_tick(
    player_ids: list[str], *, impostor: str, victim: str
) -> list[Action]:
    """Tick-0 actions: every non-impostor waits, then the impostor kills.

    Naming every player (as a real headless game does — one action per alive
    agent per tick) lets the loader recover ``num_players`` from the stream. The
    kill is ordered last so each waiter is still alive when its WaitAction is
    applied (no rejections).
    """

    actions: list[Action] = [
        _wait(pid) for pid in sorted(player_ids) if pid != impostor
    ]
    actions.append(
        KillAction.model_validate(
            {"actor": impostor, "type": "kill", "payload": {"target": victim}}
        )
    )
    return actions


@dataclass(frozen=True)
class MeetingReplayExpectations:
    """Ground-truth values a meeting fixture wrote, for tests to assert on."""

    game_id: str
    meeting_id: str
    meeting_tick: int
    reporter: str
    victim: str
    impostor: str
    living_agents: tuple[str, ...]
    total_cost_usd: float
    total_ticks: int
    winner: str


def write_sample_replay(path: Path, *, seed: int = 0, ticks: int = 3) -> None:
    """Write a minimal no-op game that ends with a CREWMATES win record."""

    game_map = load_canonical_map()
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
    )
    for _ in range(ticks):
        input_tick = state.tick
        state, _events = advance_tick(state, [], game_map=game_map)
        log.record_tick(input_tick, [], state)
    log.record_game_end(winner="CREWMATES", reason="all_tasks_complete", tick=ticks - 1)


def write_partial_replay(path: Path, *, seed: int = 0, ticks: int = 3) -> None:
    """Write a no-op game with NO game-end record (a crashed/partial replay)."""

    game_map = load_canonical_map()
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
    )
    for _ in range(ticks):
        input_tick = state.tick
        state, _events = advance_tick(state, [], game_map=game_map)
        log.record_tick(input_tick, [], state)
    # Intentionally no ``record_game_end`` — winner must surface as None.


def write_meeting_replay(
    path: Path,
    *,
    seed: int = 0,
    llm_calls: tuple[LLMCallRecord, ...] | None = None,
) -> MeetingReplayExpectations:
    """Write a 3-tick game with one body-report meeting; return expectations.

    Tick 0: the impostor (``p-3``) kills ``p-1`` in CAFETERIA. Tick 1: ``p-2``
    reports the body, opening a meeting that resolves SKIPPED. Tick 2: a no-op
    tick after the meeting resumes play. Returns a dict of the values tests
    assert against (meeting id, reporter, costs, ...).

    ``llm_calls`` overrides the synthetic LLM-call records written into the
    meeting entry; callers use it to pin specific ``agent_id`` values for
    per-call attribution tests. Defaults to :func:`_build_llm_calls`.
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

    # Roles are seed-dependent; derive the impostor, victim, and reporter from
    # the seeded roster so the fixture works for any seed (everyone spawns in
    # CAFETERIA, so the kill and report are always legal at tick 0/1).
    impostor = next(p for p, s in state.players.items() if s.role == "IMPOSTOR")
    crewmates = sorted(p for p, s in state.players.items() if s.role == "CREWMATE")
    victim = crewmates[0]
    reporter = crewmates[1]
    living = tuple(sorted(p for p in state.players if p != victim))

    # Round-start kill cooldown (DESIGN.md §3.4): the impostor spawns on
    # cooldown, so every player no-ops until it clears (naming every player each
    # tick keeps num_players recoverable from the stream). Only then is the
    # opening kill legal — a tick-0 spawn kill is impossible by design (gp-1).
    for _ in range(game_map.kill_cooldown_ticks):
        input_tick = state.tick
        waits: list[Action] = [_wait(pid) for pid in sorted(state.players)]
        state, _events = advance_tick(state, waits, game_map=game_map)
        log.record_tick(input_tick, waits, state)

    # Kill tick — the cooldown has cleared; the impostor kills a co-located crewmate.
    kill_tick = state.tick  # == game_map.kill_cooldown_ticks
    tick_kill = _opening_kill_tick(
        list(state.players), impostor=impostor, victim=victim
    )
    input_tick = state.tick
    state, _events = advance_tick(state, tick_kill, game_map=game_map)
    log.record_tick(input_tick, tick_kill, state)
    body_id = f"body-{victim}-{kill_tick}"

    # Report tick — a living crewmate reports the body, opening the meeting.
    report = ReportBodyAction.model_validate(
        {"actor": reporter, "type": "report", "payload": {"body_id": body_id}}
    )
    meeting_tick = state.tick
    input_tick = state.tick
    state, _events = advance_tick(state, [report], game_map=game_map)
    log.record_tick(input_tick, [report], state)

    meeting_id = f"{game_id}:meeting-0"
    result = _build_meeting_result(
        meeting_id=meeting_id,
        reporter=reporter,
        victim=victim,
        living=living,
        trigger_tick=meeting_tick,
    )
    llm_calls = _build_llm_calls() if llm_calls is None else llm_calls
    prompt_versions = {"crewmate_report": "crewmate_report.v1"}

    state_hash_before = _state_hash(state)
    state, _post = apply_meeting_result(
        state, result, game_map=game_map, triggering_body_id=body_id
    )
    state_hash_after = _state_hash(state)
    log.record_meeting(
        meeting_id=meeting_id,
        result=result,
        llm_calls=llm_calls,
        prompt_versions=prompt_versions,
        state_hash_before=state_hash_before,
        state_hash_after=state_hash_after,
    )

    # Quiet tick after the meeting resumes play.
    quiet_tick = state.tick
    input_tick = state.tick
    state, _events = advance_tick(state, [], game_map=game_map)
    log.record_tick(input_tick, [], state)
    log.record_game_end(
        winner="CREWMATES", reason="all_tasks_complete", tick=quiet_tick
    )

    return MeetingReplayExpectations(
        game_id=game_id,
        meeting_id=meeting_id,
        meeting_tick=meeting_tick,
        reporter=reporter,
        victim=victim,
        impostor=impostor,
        living_agents=living,
        total_cost_usd=sum(call.cost_usd for call in llm_calls),
        # Recorded ticks are 0..quiet_tick inclusive: the cooldown waits, the
        # kill, the meeting/report tick, then this quiet tick.
        total_ticks=quiet_tick + 1,
        winner="CREWMATES",
    )


def write_roster_replay(
    path: Path, *, seed: int = 0, num_players: int = 6, ticks: int = 2
) -> None:
    """Write a game seeded with a non-default roster size.

    Every player submits a WaitAction each tick, so the recorded action stream
    names every ``p-1 .. p-{num_players}`` — letting the loader recover
    ``num_players`` even though the replay format doesn't persist it.
    """

    game_map = load_canonical_map()
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=_NUM_IMPOSTORS,
    )
    for _ in range(ticks):
        actions: list[Action] = [_wait(pid) for pid in sorted(state.players)]
        input_tick = state.tick
        state, _events = advance_tick(state, actions, game_map=game_map)
        log.record_tick(input_tick, actions, state)
    log.record_game_end(winner="CREWMATES", reason="all_tasks_complete", tick=ticks - 1)


def write_unresolved_meeting_replay(path: Path, *, seed: int = 0) -> str:
    """Write a game that opens a meeting but crashes before it resolves.

    Tick 0 kills a crewmate; tick 1 reports the body (engine enters MEETING);
    then the run "crashes" — no ``MeetingReplayEntry`` and no game-end record are
    written. Returns the synthetic ``meeting_id`` the loader assigns to the
    unresolved meeting (the id surfaced by the tick timeline's
    ``meeting_triggered`` event).
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

    # Round-start kill cooldown (DESIGN.md §3.4): no-op until the cooldown clears
    # before the opening kill (a tick-0 spawn kill is impossible by design).
    for _ in range(game_map.kill_cooldown_ticks):
        input_tick = state.tick
        waits: list[Action] = [_wait(pid) for pid in sorted(state.players)]
        state, _events = advance_tick(state, waits, game_map=game_map)
        log.record_tick(input_tick, waits, state)

    kill_tick = state.tick  # == game_map.kill_cooldown_ticks
    tick_kill = _opening_kill_tick(
        list(state.players), impostor=impostor, victim=victim
    )
    input_tick = state.tick
    state, _events = advance_tick(state, tick_kill, game_map=game_map)
    log.record_tick(input_tick, tick_kill, state)

    report = ReportBodyAction.model_validate(
        {
            "actor": reporter,
            "type": "report",
            "payload": {"body_id": f"body-{victim}-{kill_tick}"},
        }
    )
    input_tick = state.tick
    state, _events = advance_tick(state, [report], game_map=game_map)
    log.record_tick(input_tick, [report], state)
    # Crash: no record_meeting, no record_game_end.
    return f"{game_id}:meeting-0"


def corrupt_tick_hash(path: Path, *, tick: int) -> None:
    """Overwrite the recorded ``state_hash`` of one tick record with a bad value."""

    lines = path.read_text(encoding="utf-8").splitlines()
    rewritten: list[str] = []
    for raw in lines:
        if not raw:
            continue
        record = json.loads(raw)
        if record.get("kind", "tick") == "tick" and record.get("tick") == tick:
            record["state_hash"] = _BAD_HASH
        rewritten.append(json.dumps(record, sort_keys=True))
    path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")


def strip_llm_call_agent_ids(path: Path) -> None:
    """Remove the ``agent_id`` key from every recorded LLM call in-place.

    Simulates a replay written before Task 4.7 added ``LLMCallRecord.agent_id``,
    so the loader's backward-compatible default (``agent_id=None``) is exercised
    against on-disk JSONL that predates the field.
    """

    lines = path.read_text(encoding="utf-8").splitlines()
    rewritten: list[str] = []
    for raw in lines:
        if not raw:
            continue
        record = json.loads(raw)
        if record.get("kind") == "meeting":
            for call in record.get("llm_calls", []):
                call.pop("agent_id", None)
        rewritten.append(json.dumps(record, sort_keys=True))
    path.write_text("\n".join(rewritten) + "\n", encoding="utf-8")


def _build_meeting_result(
    *,
    meeting_id: str,
    reporter: str,
    victim: str,
    living: tuple[str, ...],
    trigger_tick: int,
) -> MeetingResult:
    # The reactive chain's opening turn (DESIGN.md §5.2 PHASE 1): the reporter
    # states findings (the body discovery) and is unsure (no accusation), so the
    # chain terminates immediately and the meeting resolves SKIPPED.
    opening = MeetingTurn(
        turn_id=f"{meeting_id}:turn-0",
        turn_index=0,
        speaker=reporter,
        turn_kind="opening",
        reply_to=None,
        observations=(
            FoundBodyObservation(
                type="found_body",
                tick=trigger_tick,
                body_of=victim,
                room="CAFETERIA",
            ),
        ),
        claims=(),
        free_text=f"{reporter} reporting: found {victim}'s body in CAFETERIA.",
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
    contradictions = (
        ContradictionRef(
            contradiction_id=f"{meeting_id}:c0",
            kind="alibi_conflict",
            event_a_id="a",
            event_b_id="b",
            subjects=(reporter,),
            description=f"{reporter} alibi conflict at tick {trigger_tick}.",
        ),
    )
    return MeetingResult(
        meeting_id=meeting_id,
        triggered_by=reporter,
        trigger_tick=trigger_tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=ballots,
        contradictions=contradictions,
        transcript=MeetingTranscript(turns=(opening,)),
    )


def _build_llm_calls() -> tuple[LLMCallRecord, ...]:
    # Prompt bodies carry the stable markers ``_classify_template_id`` keys on
    # after the Task 8.7/8.8 chain reshape: the crewmate opening addresses the
    # "opening speaker"; the impostor opening is framed "Your role for this match
    # is IMPOSTOR". Both now emit a ``MeetingTurn`` (turn_kind = "opening").
    crewmate_prompt = (
        "You are a **crewmate** and the **opening speaker** (turn 0).\n"
        "## Your role: CREWMATE\nEmit one MeetingTurn."
    )
    impostor_prompt = (
        "Your role for this match is IMPOSTOR.\n"
        "## Your role: IMPOSTOR\nEmit one MeetingTurn."
    )
    return (
        LLMCallRecord(
            call_kind="meeting",
            model="fake-model",
            prompt=crewmate_prompt,
            response_text='{"ok": true}',
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.01,
            agent_id="p-1",
        ),
        LLMCallRecord(
            call_kind="meeting",
            model="fake-model",
            prompt=impostor_prompt,
            response_text='{"ok": true}',
            input_tokens=12,
            output_tokens=6,
            cost_usd=0.02,
            agent_id="p-3",
        ),
    )
