"""Planted cases and properties for the game-shape profile (rubric version 2).

Every reading of :mod:`eval.game_profile` is pinned by a planted pair that
differs in exactly the thing its definition names, built by hand on the census
carrier and scorecard row 3's inputs, so nothing here re-walks a recording
except the committed-set cases at the bottom, which read the shared cache.
The metamorphic properties hold the pre-reveal half to the role-blind
projection: permuting the seeded roles, or swapping the recorded ending, moves
no membership, facet, chip or tripwire byte. Each new gate is shown red on the
defect it claims: a role read planted into a predicate, a one-sided leak test,
a universe that drops a tripped game, a constant moved without a new version.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import itertools
import json
import subprocess
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from fractions import Fraction
from functools import cache
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, Final, get_args, get_origin

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

from engine.entities import PlayerId, Role, RoomId
from eval import game_profile as gp
from eval.gameplay_census import (
    BallotFact,
    BodyFact,
    CensusInputs,
    EraKey,
    Frame,
    GameFacts,
    KillFact,
    MeetingFact,
    OwnKillRowFact,
    TurnFact,
    game_endings,
    grounding_labels,
    tally_outcome,
)
from eval.process_scorecard import ContextCells, SetInputs, load_set_inputs
from eval.report_schema import GameCostSummary, GameReport, MeetingReport
from meetings.schemas import (
    AlibiClaim,
    AlibiSegment,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
)
from tests._helpers.committed import SAMPLES_9P2I, census_inputs, repo_root

# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------

PLAYERS: Final[tuple[PlayerId, ...]] = tuple(f"p-{index}" for index in range(9))
IMPOSTORS: Final[frozenset[PlayerId]] = frozenset({"p-7", "p-8"})
ROLES: Final[Mapping[PlayerId, Role]] = MappingProxyType(
    {player: "IMPOSTOR" if player in IMPOSTORS else "CREWMATE" for player in PLAYERS}
)
ERA: Final = EraKey(
    settings=(),
    temporal_observation_version=None,
    substrate_flags=None,
    prompt_stamps=None,
)
WINNERS: Final[Mapping[str, str]] = MappingProxyType(
    {
        "CREWMATE_EJECT": "CREWMATES",
        "CREWMATE_TASKS": "CREWMATES",
        "IMPOSTOR_PARITY": "IMPOSTORS",
    }
)
STAMP: Final = gp.ProfileStamp(
    era="planted", manifest_key="abc1234", source_fingerprint="sha256:0", seedset="9p2i"
)
Route = Mapping[int, Mapping[PlayerId, RoomId]]


def ballot(
    voter: PlayerId,
    target: str,
    label: str = "supported",
    *,
    confidence: float = 0.9,
    cited: str | None = None,
    reason: str | None = None,
) -> BallotFact:
    return BallotFact(
        voter=voter,
        target=target,
        authored_target=target,
        confidence=confidence,
        grounding_label=label,  # type: ignore[arg-type]
        cited_observation_id=cited,
        primary_reason_id=reason,
    )


def votes(*spec: tuple[str, str], start: int = 0) -> tuple[BallotFact, ...]:
    """Ballots ``(target, label)`` from voters ``p-{start}``, ``p-{start + 1}``, …"""

    return tuple(
        ballot(PLAYERS[start + offset], target, label)
        for offset, (target, label) in enumerate(spec)
    )


def turn(speaker: PlayerId, *accused: PlayerId, index: int = 0) -> TurnFact:
    return TurnFact(
        turn_id=f"t-{speaker}-{index}",
        index=index,
        speaker=speaker,
        reply_to=None,
        accusations=tuple(accused),
        observations=(),
        alibis=(),
    )


def kill(
    tick: int, victim: PlayerId, *witnesses: PlayerId, room: RoomId = "CAFETERIA"
) -> KillFact:
    return KillFact(
        tick=tick,
        killer="p-8",
        room=room,
        witnesses=frozenset(witnesses),
        victim=victim,
    )


def body_id(fact: KillFact) -> str:
    return f"body-{fact.victim}-{fact.tick}"


def meeting(
    index: int,
    *,
    tick: int,
    ballots: Sequence[BallotFact] = (),
    opener: PlayerId = "p-0",
    trigger: str = "emergency",
    body: str | None = None,
    living: frozenset[PlayerId] = frozenset(PLAYERS),
    turns: Sequence[TurnFact] = (),
    vent: Sequence[frozenset[PlayerId]] = (),
    rows: Sequence[OwnKillRowFact] = (),
    regrouped: bool = True,
    floor: float = 0.6,
    seed: int = 0,
) -> MeetingFact:
    """One meeting whose ejection is the game's own tally of ``ballots``."""

    outcome, ejected = tally_outcome(tuple(ballots), floor)
    return MeetingFact(
        meeting_id=f"g{seed}:meeting-{index}",
        tick=tick,
        trigger_kind=trigger,  # type: ignore[arg-type]
        opener=opener,
        trigger_body=body,
        bodies_at_open=(),
        in_vent_at_open=frozenset(),
        impostor_cooldowns_at_open=(),
        living=living,
        sabotage_active=False,
        outcome=outcome,
        ejected=ejected,
        vent_flag_subjects=tuple(vent),
        turns=tuple(turns),
        ballots=tuple(ballots),
        ballot_floor=floor,
        selector_pick=None,
        opener_prompt_has_kill_tick_handle=None,
        own_kill_rows=tuple(rows),
        trigger_tick_dropped_events=(),
        phase_after="PLAY",
        in_vent_after=frozenset(),
        bodies_after=frozenset(),
        regrouped=regrouped,
    )


def game(
    seed: int = 0,
    *,
    kills: Sequence[KillFact] = (),
    meetings: Sequence[MeetingFact] = (),
    terminal_tick: int = 60,
    roles: Mapping[PlayerId, Role] = ROLES,
    end_reason: str | None = "IMPOSTOR_PARITY",
    tasks: tuple[int | None, int | None] = (10, 14),
    sabotage: Sequence[int] = (),
) -> GameFacts:
    """One game; ``sabotage`` lists the frames on which a sabotage is active."""

    frames = {
        tick: Frame(rooms=MappingProxyType({}), sabotage_active=tick in sabotage)
        for tick in range(terminal_tick)
    }
    return GameFacts(
        seed=seed,
        roles=MappingProxyType(dict(roles)),
        era=ERA,
        kills=tuple(kills),
        vents=(),
        bodies=tuple(
            BodyFact(body_id=body_id(fact), kill_tick=fact.tick, victim=fact.victim)
            for fact in kills
        ),
        frames=MappingProxyType(frames),
        meetings=tuple(meetings),
        discarded=(),
        rows_without_dispositions=0,
        winner=WINNERS.get(end_reason or "")  # type: ignore[arg-type]
        if end_reason is not None
        else None,
        terminal_tick=terminal_tick,
        end_reason=end_reason,
        final_tasks_completed=tasks[0],
        final_tasks_total=tasks[1],
    )


def carrier(*games: GameFacts, cooldown: int = 6) -> CensusInputs:
    return CensusInputs(
        label="planted/9p2i",
        source="planted",
        era=ERA,
        kill_cooldown_ticks=cooldown,
        neighbours=MappingProxyType({}),
        games=tuple(games),
    )


def report_of(fact: MeetingFact) -> MeetingReport:
    """The scorecard's meeting for ``fact``, with no transcript and no flag."""

    return MeetingReport(
        meeting_id=fact.meeting_id,
        tick=fact.tick,
        triggered_by=fact.opener,
        trigger=fact.trigger_kind,
        outcome=fact.outcome,
        ejected_player_id=fact.ejected,
        transcript=MeetingTranscript(turns=()),
        ballots=(),
        contradictions=(),
        llm_calls=(),
    )


#: ``p-1`` stands in CAFETERIA at engine tick 0 and walks on, so a claim of
#: CAFETERIA from agent tick 1 is true at its first tick and row 3 classes a
#: flag against it as manufactured.
ROUTE: Final[Route] = MappingProxyType(
    {
        -1: {"p-1": "CAFETERIA"},
        0: {"p-1": "CAFETERIA"},
        1: {"p-1": "EAST_HALL"},
        2: {"p-1": "STORAGE"},
    }
)


def flagged_report(
    fact: MeetingFact, *, named: PlayerId = "p-1", kind: str = "alibi_vs_sighting"
) -> MeetingReport:
    """``fact``'s meeting with ``p-1``'s own alibi and one flag naming ``named``."""

    claim = AlibiClaim(
        type="alibi",
        subject="p-1",
        route=(AlibiSegment(room="CAFETERIA", from_tick=1, to_tick=3),),
    )
    spoken = MeetingTurn(
        turn_id=f"{fact.meeting_id}:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=(claim,),
        free_text="",
    )
    flag = ContradictionRef(
        contradiction_id=f"c-{named}",
        kind=kind,  # type: ignore[arg-type]
        event_a_id="a",
        event_b_id="b",
        subjects=(named,),
        description="",
    )
    return report_of(fact).model_copy(
        update={
            "transcript": MeetingTranscript(turns=(spoken,)),
            "contradictions": (flag,),
        }
    )


def scorecard(
    inputs: CensusInputs,
    *,
    reports: Mapping[str, MeetingReport] | None = None,
    routes: Mapping[int, Route] | None = None,
) -> SetInputs:
    """Row 3's inputs for ``inputs``: one report per game, meetings by id."""

    planted = reports or {}
    games = tuple(
        GameReport(
            game_id=f"headless-seed-{fact.seed}",
            seed=fact.seed,
            winner=fact.winner,
            reason=fact.end_reason or "planted",
            final_tick=fact.terminal_tick,
            roles=dict(fact.roles),
            replay_ref=f"replay-seed-{fact.seed}.jsonl",
            meetings=tuple(
                planted.get(item.meeting_id, report_of(item)) for item in fact.meetings
            ),
            failed_calls=(),
            prompt_versions={},
            cost=GameCostSummary(
                total_cost_usd=0.0,
                total_input_tokens=0,
                total_output_tokens=0,
                by_model={},
            ),
        )
        for fact in inputs.games
    )
    return SetInputs(
        label="planted",
        source="planted",
        games=games,
        routes={
            fact.seed: dict((routes or {}).get(fact.seed, ROUTE))
            for fact in inputs.games
        },
        rooms=("CAFETERIA", "EAST_HALL", "STORAGE"),
        context=ContextCells(
            impostor_alibis=0,
            impostor_alibis_survived=0,
            impostor_alibi_survival_rate=None,
            reporter_slots=0,
            reporter_ejections=0,
            innocent_non_reporter_slots=0,
            innocent_non_reporter_ejections=0,
        ),
    )


def blind_set(inputs: CensusInputs, sc: SetInputs | None = None) -> gp.BlindSet:
    return gp.blind_projection(inputs, sc if sc is not None else scorecard(inputs))


def blind_game(**kwargs: Any) -> gp.BlindGame:
    """One planted game's blind projection, cooldown 6."""

    return blind_set(carrier(game(**kwargs))).games[0]


def revealed(
    inputs: CensusInputs, sc: SetInputs | None = None
) -> tuple[gp.RevealGame, ...]:
    return gp.reveal_projection(inputs, blind_set(inputs, sc))


def profile_of(inputs: CensusInputs, sc: SetInputs | None = None) -> gp.GameProfile:
    return gp.build_profile(
        inputs, sc if sc is not None else scorecard(inputs), stamp=STAMP
    )


def readings_of(
    inputs: CensusInputs, sc: SetInputs | None = None
) -> Mapping[str, tuple[int, ...]]:
    return gp.read_pre_reveal(blind_set(inputs, sc)).readings[inputs.games[0].seed]


def ejecting_meeting(ballots: Sequence[BallotFact], *, floor: float = 0.6) -> GameFacts:
    return game(meetings=(meeting(0, tick=10, ballots=ballots, floor=floor),))


# ---------------------------------------------------------------------------
# 1. The pure module and its role-stripped projection
# ---------------------------------------------------------------------------

#: What the blind projection may never carry, by field name.
_ROLE_OR_ENDING_FIELDS: Final = frozenset(
    {
        "roles",
        "role",
        "winner",
        "end_reason",
        "reason",
        "tasks_done",
        "tasks_assigned",
        "final_tasks_completed",
        "final_tasks_total",
        "killer",
        "subject",
        "actor",
        "in_vent_at_open",
        "impostor_cooldowns_at_open",
        "report",
        "game_report",
    }
)

_BLIND_TYPES: Final = (
    gp.BlindGame,
    gp.BlindMeeting,
    gp.BlindBallot,
    gp.BlindKill,
    gp.BlindBody,
    gp.BlindTurn,
    gp.BlindOwnKillRow,
    gp.BlindSet,
)


def test_the_blind_projection_holds_no_role_ending_task_count_or_report() -> None:
    for kind in _BLIND_TYPES:
        names = {field.name for field in dataclasses.fields(kind)}
        assert not names & _ROLE_OR_ENDING_FIELDS, (kind.__name__, names)
    blind = {field.name for field in dataclasses.fields(gp.BlindGame)}
    assert "kill_cooldown_ticks" in blind
    meeting_fields = {field.name for field in dataclasses.fields(gp.BlindMeeting)}
    assert {"manufactured_subjects", "own_kill_rows", "vent_flag_subjects"} <= (
        meeting_fields
    )


def test_every_projection_and_reading_is_frozen() -> None:
    kinds = (
        *_BLIND_TYPES,
        gp.RevealGame,
        gp.Pointer,
        gp.Distance,
        gp.LeakRow,
        gp.CandidateClass,
        gp.PreRevealReading,
        gp.ProfileStamp,
    )
    for kind in kinds:
        assert getattr(kind, "__dataclass_params__").frozen, kind.__name__
    blind = blind_game(kills=(kill(5, "p-1"),))
    with pytest.raises(dataclasses.FrozenInstanceError):
        blind.seed = 3  # type: ignore[misc]
    for model in (gp.GameProfile, gp.Shelf, gp.GameFacets, gp.ClassTable):
        assert model.model_config.get("frozen") is True, model.__name__
        assert model.model_config.get("extra") == "forbid", model.__name__


def test_the_reveal_game_adds_the_roles_the_ending_and_the_task_count() -> None:
    inputs = carrier(game(end_reason="CREWMATE_TASKS", tasks=(14, 14)))
    (reveal,) = revealed(inputs)
    assert dict(reveal.roles) == dict(ROLES)
    assert reveal.end_reason == "CREWMATE_TASKS"
    assert (reveal.tasks_done, reveal.tasks_assigned) == (14, 14)
    reveal_fields = {field.name for field in dataclasses.fields(gp.RevealGame)}
    assert reveal_fields == {
        "blind",
        "roles",
        "end_reason",
        "tasks_done",
        "tasks_assigned",
        "sabotage_starts",
    }


_MODULE_SOURCE: Final = Path(gp.__file__)
_SLOW_BURN_ANCHOR: Final = "    if stretches:\n"
_T2_ANCHOR: Final = "    if ejected in meeting.manufactured_subjects:\n"


def _mypy(paths: Sequence[Path], cache_dir: Path) -> str:
    finished = subprocess.run(
        [sys.executable, "-m", "mypy", "--cache-dir", str(cache_dir), *map(str, paths)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return finished.stdout


def test_strict_mypy_refuses_a_role_read_in_a_pre_reveal_reading(
    tmp_path: Path,
) -> None:
    """Planted: slow burn reads ``game.roles``; T2 reads a game report's roles.

    The unplanted copy passes, so each error is the plant's.
    """

    source = _MODULE_SOURCE.read_text(encoding="utf-8")
    assert source.count(_SLOW_BURN_ANCHOR) == 1
    assert source.count(_T2_ANCHOR) == 1
    control = tmp_path / "profile_control.py"
    control.write_text(source, encoding="utf-8")
    slow_burn = tmp_path / "profile_slow_burn_reads_roles.py"
    slow_burn.write_text(
        source.replace(_SLOW_BURN_ANCHOR, "    if stretches and game.roles:\n"),
        encoding="utf-8",
    )
    t2 = tmp_path / "profile_t2_reads_a_report.py"
    t2.write_text(
        source.replace(
            _T2_ANCHOR,
            "    if ejected in meeting.manufactured_subjects and meeting.report.roles:\n",
        ),
        encoding="utf-8",
    )
    output = _mypy((control, slow_burn, t2), tmp_path / "mypy-cache")
    errors = [line for line in output.splitlines() if ": error:" in line]
    assert not [line for line in errors if line.startswith(str(control))], output
    assert any(
        line.startswith(str(slow_burn))
        and '"BlindGame" has no attribute "roles"' in line
        for line in errors
    ), output
    assert any(
        line.startswith(str(t2)) and '"BlindMeeting" has no attribute "report"' in line
        for line in errors
    ), output


def test_a_scorecard_meeting_id_differing_from_the_carriers_raises() -> None:
    """The mismatch sits on seed 4's second meeting, so no default value names it."""

    fact = game(4, meetings=(meeting(0, tick=10, seed=4), meeting(1, tick=20, seed=4)))
    inputs = carrier(fact)
    moved = report_of(fact.meetings[1]).model_copy(update={"meeting_id": "elsewhere"})
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 4, meeting index 1: the scorecard's meeting "
        r"elsewhere is not the carrier's g4:meeting-1$",
    ):
        blind_set(inputs, scorecard(inputs, reports={"g4:meeting-1": moved}))


def test_the_projection_refuses_a_mismatched_scorecard() -> None:
    """Each refusal names the set, the seed and every count it compared.

    Seed 9 and a two-meeting carrier keep each named value off every default,
    so a message argument replaced by a constant fails its match.
    """

    inputs = carrier(
        game(9, meetings=(meeting(0, tick=10, seed=9), meeting(1, tick=20, seed=9)))
    )
    sc = scorecard(inputs)
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i: the carrier holds seeds \[9\] and the scorecard "
        r"inputs \[\]$",
    ):
        blind_set(inputs, dataclasses.replace(sc, games=()))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i: the carrier holds seeds \[9\] and the scorecard "
        r"inputs \[8\]$",
    ):
        blind_set(inputs, scorecard(carrier(game(8))))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 9: the scorecard holds no route$",
    ):
        blind_set(inputs, dataclasses.replace(sc, routes={}))
    shorter = sc.games[0].model_copy(update={"meetings": sc.games[0].meetings[:1]})
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 9: the scorecard holds 1 meetings and the "
        r"carrier 2$",
    ):
        blind_set(inputs, dataclasses.replace(sc, games=(shorter,)))
    twice = dataclasses.replace(sc, games=(sc.games[0], sc.games[0]))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i: the scorecard inputs hold seed 9 twice$",
    ):
        gp.blind_projection(inputs, twice)
    doubled = dataclasses.replace(inputs, games=(inputs.games[0], inputs.games[0]))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i: the carrier holds seed 9 twice$",
    ):
        gp.blind_projection(doubled, sc)


def test_a_ballot_with_no_label_raises_naming_set_seed_meeting_and_voter() -> None:
    unlabelled = dataclasses.replace(ballot("p-4", "SKIP"), grounding_label=None)
    inputs = carrier(
        game(seed=3, meetings=(meeting(0, tick=9, seed=3, ballots=(unlabelled,)),))
    )
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"set planted/9p2i, seed 3, meeting index 0, voter p-4: the ballot "
        "carries no grounding label",
    ):
        blind_set(inputs)


def test_a_kill_or_a_body_with_no_victim_raises() -> None:
    """Each refusal names the set, the seed and the kill tick or body id."""

    nameless = dataclasses.replace(kill(5, "p-1"), victim=None)
    inputs = carrier(dataclasses.replace(game(6), kills=(nameless,)))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 6: the kill at tick 5 names no victim$",
    ):
        blind_set(inputs)
    fact = game(6, kills=(kill(5, "p-1"),))
    bodiless = dataclasses.replace(
        fact, bodies=(dataclasses.replace(fact.bodies[0], victim=None),)
    )
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 6: the body body-p-1-5 names no victim$",
    ):
        blind_set(carrier(bodiless))


def test_the_reveal_projection_refuses_an_unknown_or_missing_ending() -> None:
    """Each refusal names the set and the seed (9, off every default)."""

    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 9: the recorded ending 'IMPOSTOR_TIMEOUT' is "
        r"not one the engine or the runner records$",
    ):
        revealed(carrier(game(9, end_reason="IMPOSTOR_TIMEOUT")))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 9: no recorded ending$",
    ):
        revealed(carrier(game(9, end_reason=None)))
    for tasks in ((None, 14), (10, None)):
        with pytest.raises(
            gp.GameProfileConformanceError,
            match=r"^set planted/9p2i, seed 9: no final task count$",
        ):
            revealed(carrier(game(9, tasks=tasks)))
    inputs = carrier(game(9))
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 9: the carrier holds no game$",
    ):
        gp.reveal_projection(dataclasses.replace(inputs, games=()), blind_set(inputs))


def test_the_endings_follow_the_recorded_types(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sourced: an ending the recorded types drop is refused."""

    inputs = carrier(game(end_reason="CREWMATE_TASKS"))
    assert revealed(inputs)[0].end_reason == "CREWMATE_TASKS"
    monkeypatch.setattr(
        gp, "game_endings", lambda: ("CREWMATE_EJECT", "IMPOSTOR_PARITY")
    )
    with pytest.raises(gp.GameProfileConformanceError, match="'CREWMATE_TASKS'"):
        revealed(inputs)


def test_the_leak_facts_follow_the_recorded_endings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sourced: an ending the recorded types gain gets its own leak row.

    The leak rule's facts are read from :func:`eval.gameplay_census.game_endings`
    at call time, in its order, so a planted ending placed first leads the rows.
    """

    planted = ("PLANTED_STALEMATE", *game_endings())
    monkeypatch.setattr(gp, "game_endings", lambda: planted)
    games = (
        game(0, end_reason="IMPOSTOR_PARITY"),
        game(1, end_reason="PLANTED_STALEMATE"),
    )
    facts = gp.era_facts(revealed(carrier(*games)))
    assert facts == (
        ("PLANTED_STALEMATE", frozenset({1})),
        ("IMPOSTOR_PARITY", frozenset({0})),
        (gp.ANY_EJECTION, frozenset()),
        (gp.CREWMATE_EJECTED, frozenset()),
    )


# ---------------------------------------------------------------------------
# 2. No pre-reveal byte reads a role or the ending
# ---------------------------------------------------------------------------


def pre_reveal_bytes(reading: gp.PreRevealReading) -> str:
    """Every pre-reveal membership, facet, chip and tripwire, as bytes."""

    return json.dumps(
        {
            "readings": {
                str(seed): dict(found) for seed, found in reading.readings.items()
            },
            "candidates": {
                str(seed): {
                    name: [list(pointer.meetings), list(pointer.kill_ticks)]
                    for name, pointer in held.items()
                }
                for seed, held in reading.candidates.items()
            },
            "eyewitness": {
                str(seed): list(marked) for seed, marked in reading.eyewitness.items()
            },
            "tripped": sorted(reading.tripped),
            "saturated": list(reading.saturated),
            "facets": [facet.model_dump(mode="json") for facet in reading.facets],
        },
        sort_keys=True,
    )


def reading_bytes(inputs: CensusInputs, sc: SetInputs) -> str:
    return pre_reveal_bytes(gp.read_pre_reveal(gp.blind_projection(inputs, sc)))


def with_roles(
    inputs: CensusInputs, sc: SetInputs, roles: Mapping[int, Mapping[PlayerId, Role]]
) -> tuple[CensusInputs, SetInputs]:
    """The carrier and row 3's reports with each game's roles replaced."""

    return (
        dataclasses.replace(
            inputs,
            games=tuple(
                dataclasses.replace(
                    fact, roles=MappingProxyType(dict(roles[fact.seed]))
                )
                for fact in inputs.games
            ),
        ),
        dataclasses.replace(
            sc,
            games=tuple(
                report.model_copy(update={"roles": dict(roles[report.seed])})
                for report in sc.games
            ),
        ),
    )


def with_endings(
    inputs: CensusInputs, sc: SetInputs, endings: Mapping[int, str]
) -> tuple[CensusInputs, SetInputs]:
    """The carrier and row 3's reports with each game's ending and winner swapped."""

    return (
        dataclasses.replace(
            inputs,
            games=tuple(
                dataclasses.replace(
                    fact,
                    end_reason=endings[fact.seed],
                    winner=WINNERS[endings[fact.seed]],  # type: ignore[arg-type]
                )
                for fact in inputs.games
            ),
        ),
        dataclasses.replace(
            sc,
            games=tuple(
                report.model_copy(
                    update={
                        "reason": endings[report.seed],
                        "winner": WINNERS[endings[report.seed]],
                    }
                )
                for report in sc.games
            ),
        ),
    )


def permuted(
    roles: Mapping[PlayerId, Role], order: Sequence[PlayerId]
) -> dict[PlayerId, Role]:
    """``roles`` moved onto other seats, the role counts kept."""

    seats = sorted(roles)
    return {seat: roles[source] for seat, source in zip(seats, order, strict=True)}


_HELD_OR_LOOSE: Final = (
    "supported",
    "flag_only",
    "off_target",
    "uncited",
    "invalid_citation",
    "not_assessed",
)


@st.composite
def planted_game(draw: st.DrawFn, seed: int) -> GameFacts:
    victims = draw(st.lists(st.sampled_from(PLAYERS), unique=True, max_size=4))
    ticks = sorted(
        draw(st.lists(st.integers(1, 45), min_size=len(victims), max_size=len(victims)))
    )
    kills = tuple(
        kill(
            tick,
            victim,
            *draw(st.lists(st.sampled_from(PLAYERS), unique=True, max_size=3)),
        )
        for tick, victim in zip(ticks, victims, strict=True)
    )
    meeting_ticks = sorted(set(draw(st.lists(st.integers(2, 55), max_size=4))))
    meetings: list[MeetingFact] = []
    ejected: set[PlayerId] = set()
    reported: set[str] = set()
    for index, tick in enumerate(meeting_ticks):
        dead = {fact.victim for fact in kills if fact.tick <= tick}
        living = frozenset(PLAYERS) - {v for v in dead if v is not None} - ejected
        if len(living) < 2:
            break
        bodies = [
            body_id(fact)
            for fact in kills
            if fact.tick <= tick and body_id(fact) not in reported
        ]
        report = bool(bodies) and draw(st.booleans())
        body = draw(st.sampled_from(bodies)) if report else None
        if body is not None:
            reported.add(body)
        order = sorted(living)
        cast_ballots: list[BallotFact] = []
        for voter in draw(st.lists(st.sampled_from(order), unique=True, min_size=1)):
            target = draw(st.sampled_from([*order, "SKIP"]))
            labels = (
                (*_HELD_OR_LOOSE, "none_held") if target == "SKIP" else _HELD_OR_LOOSE
            )
            cast_ballots.append(
                ballot(
                    voter,
                    target,
                    draw(st.sampled_from(labels)),
                    confidence=draw(st.sampled_from((0.4, 0.9))),
                    cited=draw(st.sampled_from((None, "obs-1", "obs-2"))),
                    reason=draw(st.sampled_from((None, "turn-1", "turn-2"))),
                )
            )
        spoken = tuple(
            turn(
                speaker,
                *draw(st.lists(st.sampled_from(order), max_size=2)),
                index=number,
            )
            for number, speaker in enumerate(
                draw(st.lists(st.sampled_from(order), max_size=3))
            )
        )
        rows = tuple(
            OwnKillRowFact(
                holder=draw(st.sampled_from(order)),
                subject="p-8",
                room="CAFETERIA",
                tick=1,
                citation_id=draw(st.sampled_from((None, "obs-1", "obs-2"))),
            )
            for _ in range(draw(st.integers(0, 2)))
        )
        vent = tuple(
            frozenset(draw(st.lists(st.sampled_from(order), unique=True, max_size=2)))
            for _ in range(draw(st.integers(0, 1)))
        )
        fact = meeting(
            index,
            tick=tick,
            ballots=cast_ballots,
            opener=draw(st.sampled_from(order)),
            trigger="report" if report else "emergency",
            body=body,
            living=living,
            turns=spoken,
            vent=vent,
            rows=rows,
            regrouped=draw(st.booleans()),
            seed=seed,
        )
        if fact.ejected is not None:
            ejected.add(fact.ejected)
        meetings.append(fact)
    terminal = max([50, *ticks, *meeting_ticks])
    return game(
        seed,
        kills=kills,
        meetings=meetings,
        terminal_tick=terminal,
        end_reason=draw(st.sampled_from(sorted(WINNERS))),
    )


@st.composite
def planted_sets(draw: st.DrawFn) -> tuple[CensusInputs, SetInputs]:
    games = [draw(planted_game(seed)) for seed in range(draw(st.integers(1, 3)))]
    inputs = carrier(*games, cooldown=draw(st.integers(3, 8)))
    return inputs, scorecard(inputs)


_PROPERTY: Final = settings(
    max_examples=40,
    deadline=None,
    database=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@_PROPERTY
@given(planted=planted_sets(), data=st.data())
def test_permuting_the_roles_moves_no_pre_reveal_byte_on_planted_sets(
    planted: tuple[CensusInputs, SetInputs], data: st.DataObject
) -> None:
    inputs, sc = planted
    roles = {
        fact.seed: permuted(fact.roles, data.draw(st.permutations(sorted(fact.roles))))
        for fact in inputs.games
    }
    assert reading_bytes(*with_roles(inputs, sc, roles)) == reading_bytes(inputs, sc)


@_PROPERTY
@given(planted=planted_sets(), data=st.data())
def test_swapping_the_ending_moves_no_pre_reveal_byte_on_planted_sets(
    planted: tuple[CensusInputs, SetInputs], data: st.DataObject
) -> None:
    inputs, sc = planted
    endings = {
        fact.seed: data.draw(st.sampled_from(sorted(WINNERS))) for fact in inputs.games
    }
    assert reading_bytes(*with_endings(inputs, sc, endings)) == reading_bytes(
        inputs, sc
    )


@cache
def committed_scorecard() -> SetInputs:
    """Row 3's inputs for the shown set, walked once per worker."""

    return load_set_inputs(SAMPLES_9P2I)


@cache
def committed_reading() -> str:
    return reading_bytes(census_inputs(SAMPLES_9P2I), committed_scorecard())


@settings(max_examples=6, deadline=None, database=None)
@given(data=st.data())
def test_permuting_the_roles_moves_no_pre_reveal_byte_on_the_shown_set(
    data: st.DataObject,
) -> None:
    inputs = census_inputs(SAMPLES_9P2I)
    roles = {
        fact.seed: permuted(fact.roles, data.draw(st.permutations(sorted(fact.roles))))
        for fact in inputs.games
    }
    assert reading_bytes(*with_roles(inputs, committed_scorecard(), roles)) == (
        committed_reading()
    )


@settings(max_examples=6, deadline=None, database=None)
@given(data=st.data())
def test_swapping_the_ending_moves_no_pre_reveal_byte_on_the_shown_set(
    data: st.DataObject,
) -> None:
    inputs = census_inputs(SAMPLES_9P2I)
    endings = {
        fact.seed: data.draw(st.sampled_from(sorted(WINNERS))) for fact in inputs.games
    }
    assert reading_bytes(*with_endings(inputs, committed_scorecard(), endings)) == (
        committed_reading()
    )


def _closing_over(
    monkeypatch: pytest.MonkeyPatch, peek: Callable[[GameFacts], bool]
) -> Callable[[CensusInputs, SetInputs], str]:
    """A planted fold: a double kill also holds where ``peek`` reads the full carrier."""

    original = gp.candidate_pointers
    current: dict[str, CensusInputs] = {}

    def leaky(game_: gp.BlindGame, *, label: str) -> Mapping[str, gp.Pointer]:
        hits = dict(original(game_, label=label))
        facts = next(
            fact for fact in current["inputs"].games if fact.seed == game_.seed
        )
        if peek(facts):
            hits[gp.DOUBLE_KILL] = gp.Pointer()
        return MappingProxyType(hits)

    monkeypatch.setattr(gp, "candidate_pointers", leaky)

    def bytes_of(inputs: CensusInputs, sc: SetInputs) -> str:
        current["inputs"] = inputs
        return reading_bytes(inputs, sc)

    return bytes_of


def test_a_fold_reading_the_carrier_fails_both_properties(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a predicate that closes over the full carrier and reads a role
    beside the ending, so a role permutation and an ending swap each move it."""

    bytes_of = _closing_over(
        monkeypatch,
        lambda fact: (
            fact.roles[min(fact.roles)] == "IMPOSTOR"
            or fact.end_reason == "CREWMATE_TASKS"
        ),
    )
    inputs = carrier(
        game(meetings=(meeting(0, tick=10),), end_reason="IMPOSTOR_PARITY")
    )
    sc = scorecard(inputs)
    swapped = {0: permuted(ROLES, ("p-7", *PLAYERS[1:7], "p-0", "p-8"))}
    assert bytes_of(*with_roles(inputs, sc, swapped)) != bytes_of(inputs, sc)
    assert bytes_of(*with_endings(inputs, sc, {0: "CREWMATE_TASKS"})) != bytes_of(
        inputs, sc
    )

    @_PROPERTY
    @given(planted=planted_sets(), data=st.data())
    def roles_property(
        planted: tuple[CensusInputs, SetInputs], data: st.DataObject
    ) -> None:
        planted_inputs, planted_sc = planted
        roles = {
            fact.seed: permuted(
                fact.roles, data.draw(st.permutations(sorted(fact.roles)))
            )
            for fact in planted_inputs.games
        }
        assert bytes_of(*with_roles(planted_inputs, planted_sc, roles)) == bytes_of(
            planted_inputs, planted_sc
        )

    @_PROPERTY
    @given(planted=planted_sets(), data=st.data())
    def ending_property(
        planted: tuple[CensusInputs, SetInputs], data: st.DataObject
    ) -> None:
        planted_inputs, planted_sc = planted
        endings = {
            fact.seed: data.draw(st.sampled_from(sorted(WINNERS)))
            for fact in planted_inputs.games
        }
        assert bytes_of(*with_endings(planted_inputs, planted_sc, endings)) == bytes_of(
            planted_inputs, planted_sc
        )

    with pytest.raises(AssertionError):
        roles_property()
    with pytest.raises(AssertionError):
        ending_property()

    # The committed carrier: an impostor's role moved onto the first seat of
    # every game, and every ending set to a task win, each move the planted
    # reading.
    shown = census_inputs(SAMPLES_9P2I)
    shown_sc = committed_scorecard()

    def onto_first_seat(roles: Mapping[PlayerId, Role]) -> dict[PlayerId, Role]:
        first = min(roles)
        impostor = next(seat for seat in sorted(roles) if roles[seat] == "IMPOSTOR")
        moved = dict(roles)
        moved[impostor], moved[first] = roles[first], roles[impostor]
        return moved

    moved_roles = {fact.seed: onto_first_seat(fact.roles) for fact in shown.games}
    assert bytes_of(*with_roles(shown, shown_sc, moved_roles)) != bytes_of(
        shown, shown_sc
    )
    task_wins = {fact.seed: "CREWMATE_TASKS" for fact in shown.games}
    assert bytes_of(*with_endings(shown, shown_sc, task_wins)) != bytes_of(
        shown, shown_sc
    )


def test_a_fold_reading_the_ending_fails_the_ending_property(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a predicate that closes over the carrier and reads the ending."""

    bytes_of = _closing_over(
        monkeypatch, lambda fact: fact.end_reason == "CREWMATE_TASKS"
    )
    inputs = carrier(game(end_reason="IMPOSTOR_PARITY"))
    sc = scorecard(inputs)
    assert bytes_of(*with_endings(inputs, sc, {0: "CREWMATE_TASKS"})) != bytes_of(
        inputs, sc
    )


def _t2_reading_report_roles(
    monkeypatch: pytest.MonkeyPatch, sc: SetInputs
) -> dict[str, SetInputs]:
    """Planted: T2 also requires the game report's roles to name a crewmate.

    The planted reading closes over the scorecard inputs in the returned holder,
    which the test points at the inputs it projects.
    """

    original = gp._manufactured
    holder = {"sc": sc}

    def leaky(
        report: MeetingReport, route: Route
    ) -> tuple[frozenset[PlayerId], int, int]:
        subjects, flags, evaluable = original(report, route)
        roles = next(
            game_report.roles
            for game_report in holder["sc"].games
            if any(
                item.meeting_id == report.meeting_id for item in game_report.meetings
            )
        )
        return (
            frozenset(subject for subject in subjects if roles[subject] == "CREWMATE"),
            flags,
            evaluable,
        )

    monkeypatch.setattr(gp, "_manufactured", leaky)
    return holder


def _manufactured_case() -> tuple[CensusInputs, SetInputs]:
    """A meeting that ejects ``p-1`` while a manufactured flag names ``p-1``."""

    fact = meeting(0, tick=10, ballots=votes(*[("p-1", "supported")] * 5, start=2))
    inputs = carrier(game(meetings=(fact,)))
    return inputs, scorecard(inputs, reports={fact.meeting_id: flagged_report(fact)})


def test_a_t2_reading_the_report_roles_fails_the_role_property(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs, sc = _manufactured_case()
    before = readings_of(inputs, sc)
    assert before["manufactured"] == (0,)
    roles = {0: permuted(ROLES, ("p-0", "p-7", *PLAYERS[2:7], "p-1", "p-8"))}
    moved_inputs, moved_sc = with_roles(inputs, sc, roles)
    assert reading_bytes(moved_inputs, moved_sc) == reading_bytes(inputs, sc)
    holder = _t2_reading_report_roles(monkeypatch, sc)
    planted_before = reading_bytes(inputs, sc)
    holder["sc"] = moved_sc
    assert reading_bytes(moved_inputs, moved_sc) != planted_before


# ---------------------------------------------------------------------------
# 3. T1, decisive
# ---------------------------------------------------------------------------


def test_the_seed_41_shape_trips_any_but_not_decisive() -> None:
    """Four held ballots carry the ejection alone; one off-target slip rides along."""

    ballots = votes(
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "off_target"),
        ("SKIP", "supported"),
        start=0,
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["any"] == (0,)
    assert found["decisive"] == ()
    assert found["every"] == ()
    assert not gp.tripped(found)


def test_the_seed_26_shape_trips_decisive() -> None:
    """Removal leaves a tie with SKIP, so the table would have held."""

    ballots = votes(
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "off_target"),
        ("SKIP", "supported"),
        ("SKIP", "none_held"),
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["decisive"] == (0,)
    assert found["decisive_read_as_skip"] == (0,)
    assert found["any"] == (0,)
    assert found["every"] == ()
    assert gp.tripped(found)


def test_a_removal_that_hands_the_tally_to_another_player_trips_decisive() -> None:
    """Planted: without the two ungrounded ballots, the table ejects ``p-6`` instead.

    Every other planted T1 case removes down to a tie or a skip; here the tally
    after removal still ejects someone, just not the player the meeting ejected,
    so only the "someone else" half of the definition can trip it.
    """

    ballots = (
        ballot("p-0", "p-3", "supported"),
        ballot("p-1", "p-3", "supported"),
        ballot("p-2", "p-3", "off_target"),
        ballot("p-4", "p-3", "uncited"),
        ballot("p-5", "p-6", "supported"),
        ballot("p-7", "p-6", "supported"),
        ballot("p-8", "p-6", "supported"),
    )
    fact = ejecting_meeting(ballots)
    assert fact.meetings[0].ejected == "p-3"
    held = tuple(item for item in ballots if item.grounding_label == "supported")
    assert tally_outcome(held, 0.6)[1] == "p-6"
    found = readings_of(carrier(fact))
    assert found["decisive"] == (0,)
    assert found["decisive_read_as_skip"] == (0,)
    assert found["decisive_all_ungrounded_removed"] == (0,)
    assert found["any"] == (0,)
    assert found["every"] == ()
    assert gp.tripped(found)


def test_every_reads_an_ejection_resting_on_ungrounded_ballots_alone() -> None:
    ballots = votes(
        ("p-3", "uncited"), ("p-3", "invalid_citation"), ("SKIP", "supported")
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["every"] == (0,)
    assert found["decisive"] == (0,)


def test_a_not_assessed_ejecting_ballot_is_kept_as_recorded() -> None:
    ballots = votes(
        ("p-3", "not_assessed"),
        ("p-3", "not_assessed"),
        ("p-3", "off_target"),
        ("SKIP", "supported"),
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["any"] == (0,)
    assert found["decisive"] == ()
    assert found["every"] == ()


def test_the_recorded_floor_decides_the_planted_tally() -> None:
    """The held ballot is under 0.6 and over 0.4: the floor decides the trip."""

    ballots = (
        ballot("p-0", "p-3", "supported", confidence=0.5),
        ballot("p-1", "p-3", "off_target", confidence=0.9),
    )
    assert readings_of(carrier(ejecting_meeting(ballots, floor=0.6)))["decisive"] == (
        0,
    )
    assert readings_of(carrier(ejecting_meeting(ballots, floor=0.4)))["decisive"] == ()


def test_removal_governs_where_reading_as_skip_differs() -> None:
    ballots = votes(
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "off_target"),
        ("SKIP", "supported"),
        ("SKIP", "supported"),
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["decisive"] == ()
    assert found["decisive_read_as_skip"] == (0,)
    assert not gp.tripped(found)
    profile = profile_of(carrier(ejecting_meeting(ballots)))
    assert profile.pre_reveal.games[0].tripped == ()


def test_removing_every_ungrounded_ballot_is_published_beside_the_governing_reading() -> (
    None
):
    ballots = votes(
        ("p-3", "supported"),
        ("p-3", "supported"),
        ("p-3", "off_target"),
        ("SKIP", "supported"),
        ("SKIP", "off_target"),
    )
    found = readings_of(carrier(ejecting_meeting(ballots)))
    assert found["decisive"] == (0,)
    assert found["decisive_all_ungrounded_removed"] == ()


def test_an_ejecting_none_held_ballot_raises_naming_all_four() -> None:
    """The ballot sits at meeting index 1, so a constant index fails the match."""

    ballots = (
        *votes(("p-3", "supported"), ("p-3", "supported")),
        ballot("p-5", "p-3", "none_held"),
    )
    inputs = carrier(
        game(
            seed=12,
            meetings=(
                meeting(0, tick=5, seed=12),
                meeting(1, tick=10, seed=12, ballots=ballots),
            ),
        )
    )
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted/9p2i, seed 12, meeting index 1, voter p-5: an ejecting "
        r"ballot labelled 'none_held' is a case the tripwire does not classify; the "
        r"owner decides how it reads$",
    ):
        gp.read_pre_reveal(blind_set(inputs))


def test_a_none_held_skip_is_read_as_recorded() -> None:
    ballots = votes(("p-3", "supported"), ("p-3", "supported"), ("SKIP", "none_held"))
    assert readings_of(carrier(ejecting_meeting(ballots)))["any"] == ()


def test_every_ejection_is_read_whatever_the_ejected_players_role() -> None:
    for ejected in ("p-3", "p-7"):
        ballots = votes(
            (ejected, "supported"), (ejected, "off_target"), ("SKIP", "supported")
        )
        assert readings_of(carrier(ejecting_meeting(ballots)))["decisive"] == (0,), (
            ejected
        )


def test_an_eighth_grounding_label_raises_unclassified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    labels = grounding_labels()
    assert set(labels) == set(gp.LABEL_CLASSES)
    monkeypatch.setattr(gp, "grounding_labels", lambda: (*labels, "half_held"))
    with pytest.raises(
        gp.GameProfileConformanceError, match="'half_held' has no class"
    ):
        gp.label_classes()


def test_an_eighth_grounding_label_stops_the_reading_and_the_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sourced: the pre-reveal reading and the profile read the partition live.

    A label the meeting layer gains after the blind projection is built stops
    :func:`read_pre_reveal` and :func:`build_profile`, rather than either reading
    the module's own table as if the label did not exist.
    """

    inputs = carrier(
        ejecting_meeting(
            votes(("p-3", "supported"), ("p-3", "supported"), ("SKIP", "supported"))
        )
    )
    blind = blind_set(inputs)
    assert gp.read_pre_reveal(blind).tripped == frozenset()
    labels = grounding_labels()
    monkeypatch.setattr(gp, "grounding_labels", lambda: (*labels, "half_held"))
    unclassified = r"^the grounding label 'half_held' has no class in the tripwire's "
    with pytest.raises(gp.GameProfileConformanceError, match=unclassified):
        gp.read_pre_reveal(blind)
    with pytest.raises(gp.GameProfileConformanceError, match=unclassified):
        profile_of(inputs)


def test_a_label_the_meeting_layer_dropped_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    labels = tuple(label for label in grounding_labels() if label != "flag_only")
    monkeypatch.setattr(gp, "grounding_labels", lambda: labels)
    with pytest.raises(gp.GameProfileConformanceError, match="classes 'flag_only'"):
        gp.label_classes()
    readings = tuple(label for label in gp.LABEL_CLASSES if label != "none_held")
    monkeypatch.setattr(gp, "grounding_labels", lambda: readings)
    monkeypatch.setattr(
        gp,
        "LABEL_CLASSES",
        MappingProxyType({label: gp.LABEL_CLASSES[label] for label in readings}),
    )
    with pytest.raises(
        gp.GameProfileConformanceError, match="groups ballots labelled 'none_held'"
    ):
        gp.label_classes()


def test_the_label_partition_is_read_from_the_meeting_layers_type() -> None:
    from meetings.schemas import BallotGroundingLabel

    assert grounding_labels() == get_args(BallotGroundingLabel)
    assert dict(gp.label_classes()) == {
        "not_assessed": "as_recorded",
        "supported": "held",
        "off_target": "ungrounded",
        "invalid_citation": "ungrounded",
        "none_held": "unclassified",
        "flag_only": "held",
        "uncited": "ungrounded",
    }


# ---------------------------------------------------------------------------
# 4. T2, a manufactured contradiction
# ---------------------------------------------------------------------------


def test_a_manufactured_flag_naming_the_ejected_player_trips() -> None:
    inputs, sc = _manufactured_case()
    found = readings_of(inputs, sc)
    assert found["manufactured"] == (0,)
    assert found["decisive"] == ()
    profile = profile_of(inputs, sc)
    assert [label.model_dump() for label in profile.pre_reveal.games[0].tripped] == [
        {"tripwire": gp.MANUFACTURED, "meeting": 0}
    ]
    assert profile.pre_reveal.tripwires.alibi_flags == 1
    assert profile.pre_reveal.tripwires.alibi_flags_evaluable == 1


def test_a_flag_naming_another_player_or_one_row_3_cannot_answer_does_not_trip() -> (
    None
):
    fact = meeting(0, tick=10, ballots=votes(*[("p-3", "supported")] * 5, start=2))
    inputs = carrier(game(meetings=(fact,)))
    other = scorecard(inputs, reports={fact.meeting_id: flagged_report(fact)})
    assert readings_of(inputs, other)["manufactured"] == ()
    blind = blind_set(inputs, other).games[0].meetings[0]
    assert blind.manufactured_subjects == frozenset({"p-1"})
    unanswerable = scorecard(
        inputs, reports={fact.meeting_id: flagged_report(fact, named="p-3")}
    )
    projected = blind_set(inputs, unanswerable).games[0].meetings[0]
    assert projected.manufactured_subjects == frozenset()
    assert (projected.alibi_flags, projected.alibi_flags_evaluable) == (1, 0)
    assert readings_of(inputs, unanswerable)["manufactured"] == ()


def test_the_alibi_kinds_are_row_3s(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sourced: narrowed alibi kinds, and the planted trip goes."""

    from eval.process_scorecard import ALIBI_FLAG_KINDS

    assert vars(gp)["ALIBI_FLAG_KINDS"] is ALIBI_FLAG_KINDS
    inputs, sc = _manufactured_case()
    assert readings_of(inputs, sc)["manufactured"] == (0,)
    monkeypatch.setattr(gp, "ALIBI_FLAG_KINDS", frozenset({"alibi_conflict"}))
    assert readings_of(inputs, sc)["manufactured"] == ()


def test_a_vent_flag_is_not_an_alibi_class_flag() -> None:
    fact = meeting(0, tick=10, ballots=votes(*[("p-1", "supported")] * 5, start=2))
    inputs = carrier(game(meetings=(fact,)))
    vented = scorecard(
        inputs, reports={fact.meeting_id: flagged_report(fact, kind="vent_sighting")}
    )
    projected = blind_set(inputs, vented).games[0].meetings[0]
    assert projected.alibi_flags == 0
    assert readings_of(inputs, vented)["manufactured"] == ()


# ---------------------------------------------------------------------------
# 5. The pre-reveal shelves, and the chip
# ---------------------------------------------------------------------------


def shelves_of(blind: gp.BlindGame) -> Mapping[str, gp.Pointer]:
    return gp.candidate_pointers(blind, label="planted")


def test_the_reporter_saw_it_happen() -> None:
    seen = kill(5, "p-1", "p-2")
    report = meeting(0, tick=8, trigger="report", opener="p-2", body=body_id(seen))
    hit = shelves_of(blind_game(kills=(seen,), meetings=(report,)))
    assert hit[gp.REPORTER_SAW_IT] == gp.Pointer(meetings=(0,))
    outsider = meeting(0, tick=8, trigger="report", opener="p-3", body=body_id(seen))
    assert gp.REPORTER_SAW_IT not in shelves_of(
        blind_game(kills=(seen,), meetings=(outsider,))
    )


def test_only_a_report_meeting_counts_as_a_reporter_or_a_report() -> None:
    """Planted: an emergency meeting that names a body is still no report."""

    seen = kill(5, "p-1", "p-2")
    called = meeting(0, tick=8, trigger="emergency", opener="p-2", body=body_id(seen))
    blind = blind_game(kills=(seen,), meetings=(called,))
    assert gp.REPORTER_SAW_IT not in shelves_of(blind)
    (facets,) = profile_of(
        carrier(game(kills=(seen,), meetings=(called,)))
    ).pre_reveal.games
    assert facets.reports == ()
    assert facets.bodies_never_found == 1


def test_a_same_tick_double_kill_joins_each_body_by_victim() -> None:
    first = kill(5, "p-1", "p-2")
    second = kill(5, "p-3", "p-4")
    right = meeting(0, tick=8, trigger="report", opener="p-4", body=body_id(second))
    wrong = meeting(0, tick=8, trigger="report", opener="p-2", body=body_id(second))
    assert gp.REPORTER_SAW_IT in shelves_of(
        blind_game(kills=(first, second), meetings=(right,))
    )
    assert gp.REPORTER_SAW_IT not in shelves_of(
        blind_game(kills=(first, second), meetings=(wrong,))
    )


def test_a_reported_body_joining_no_kill_raises() -> None:
    report = meeting(0, tick=8, trigger="report", opener="p-2", body="body-nobody")
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^set planted, seed 0, meeting index 0: the reported body "
        r"body-nobody joins 0 corpses$",
    ):
        shelves_of(blind_game(meetings=(report,)))
    seen = kill(5, "p-1", "p-2")
    twice = dataclasses.replace(
        blind_game(kills=(seen,), meetings=(report,)),
        kills=(
            gp.BlindKill(tick=5, room="CAFETERIA", victim="p-1", witnesses=frozenset()),
            gp.BlindKill(tick=6, room="CAFETERIA", victim="p-1", witnesses=frozenset()),
        ),
    )
    joined = dataclasses.replace(
        twice,
        meetings=(dataclasses.replace(twice.meetings[0], trigger_body=body_id(seen)),),
    )
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"meeting index 0: the reported body body-p-1-5 joins 2 kills$",
    ):
        shelves_of(joined)


def test_double_kill() -> None:
    hit = shelves_of(blind_game(kills=(kill(5, "p-1"), kill(5, "p-2"), kill(9, "p-3"))))
    assert hit[gp.DOUBLE_KILL] == gp.Pointer(kill_ticks=(5,))
    assert gp.DOUBLE_KILL not in shelves_of(
        blind_game(kills=(kill(5, "p-1"), kill(6, "p-2")))
    )


@pytest.mark.parametrize(
    ("ticks", "terminal", "expected"),
    [
        ((10, 30), 40, (10, 30)),
        ((10, 29), 48, None),
        ((20,), 30, (20,)),
        ((19,), 38, None),
        ((5,), 25, (5,)),
        ((), 20, ()),
        ((), 19, None),
    ],
)
def test_slow_burn_needs_twenty_quiet_ticks(
    ticks: tuple[int, ...], terminal: int, expected: tuple[int, ...] | None
) -> None:
    victims = PLAYERS[1 : 1 + len(ticks)]
    found = shelves_of(
        blind_game(
            kills=tuple(kill(tick, victim) for tick, victim in zip(ticks, victims)),
            terminal_tick=terminal,
        )
    )
    if expected is None:
        assert gp.SLOW_BURN not in found
    else:
        assert found[gp.SLOW_BURN] == gp.Pointer(kill_ticks=expected)


def test_two_kills_after_one_regroup_and_a_kill_one_tick_past_the_wave() -> None:
    regroup = meeting(0, tick=10, regrouped=True)
    inside = blind_game(kills=(kill(17, "p-1"), kill(20, "p-2")), meetings=(regroup,))
    found = shelves_of(inside)
    assert found[gp.TWO_KILLS_AFTER_ONE_REGROUP] == gp.Pointer(
        meetings=(0,), kill_ticks=(17, 20)
    )
    assert found[gp.STRUCK_AFTER_THE_REGROUP] == gp.Pointer(kill_ticks=(17, 20))
    past = shelves_of(
        blind_game(kills=(kill(17, "p-1"), kill(21, "p-2")), meetings=(regroup,))
    )
    assert gp.TWO_KILLS_AFTER_ONE_REGROUP not in past
    assert past[gp.STRUCK_AFTER_THE_REGROUP] == gp.Pointer(kill_ticks=(17,))
    early = shelves_of(blind_game(kills=(kill(16, "p-1"),), meetings=(regroup,)))
    assert gp.STRUCK_AFTER_THE_REGROUP not in early
    unregrouped = meeting(0, tick=10, regrouped=False)
    assert gp.STRUCK_AFTER_THE_REGROUP not in shelves_of(
        blind_game(kills=(kill(17, "p-1"),), meetings=(unregrouped,))
    )


def test_two_regroups_each_with_one_wave_kill_is_not_two_after_one() -> None:
    meetings = (meeting(0, tick=10), meeting(1, tick=20))
    found = shelves_of(
        blind_game(kills=(kill(17, "p-1"), kill(27, "p-2")), meetings=meetings)
    )
    assert gp.TWO_KILLS_AFTER_ONE_REGROUP not in found
    assert found[gp.STRUCK_AFTER_THE_REGROUP] == gp.Pointer(kill_ticks=(17, 27))


def test_the_wave_follows_the_recorded_kill_cooldown() -> None:
    """Sourced: a cooldown of 5 moves a kill ten ticks past the regroup out."""

    fact = game(kills=(kill(20, "p-1"),), meetings=(meeting(0, tick=10),))
    at_six = blind_set(carrier(fact, cooldown=6)).games[0]
    at_five = blind_set(carrier(fact, cooldown=5)).games[0]
    assert (at_six.kill_cooldown_ticks, at_five.kill_cooldown_ticks) == (6, 5)
    assert gp.wave_kills(at_six) == ((10, 20),)
    assert gp.wave_kills(at_five) == ()


def test_a_close_call_is_a_margin_of_one() -> None:
    near = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-3", "supported"), ("p-3", "supported"), ("SKIP", "supported")
        ),
    )
    assert shelves_of(blind_game(meetings=(near,)))[gp.CLOSE_CALL] == gp.Pointer(
        meetings=(0,)
    )
    two = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-3", "supported"),
            ("p-3", "supported"),
            ("p-3", "supported"),
            ("SKIP", "supported"),
        ),
    )
    assert gp.CLOSE_CALL not in shelves_of(blind_game(meetings=(two,)))
    assert gp.CLOSE_CALL not in shelves_of(blind_game(meetings=(meeting(0, tick=10),)))


def test_suspicion_moved_onto_an_earlier_target() -> None:
    first = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-3", "supported"), ("SKIP", "supported"), ("SKIP", "supported")
        ),
    )
    second = meeting(
        1,
        tick=20,
        ballots=votes(
            ("p-3", "supported"), ("p-3", "supported"), ("SKIP", "supported")
        ),
    )
    assert shelves_of(blind_game(meetings=(first, second)))[
        gp.SUSPICION_MOVED
    ] == gp.Pointer(meetings=(1,))


def test_suspicion_moved_away_from_a_living_player_but_not_from_the_dead() -> None:
    first = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-5", "supported"), ("SKIP", "supported"), ("SKIP", "supported")
        ),
    )
    cleared = meeting(
        1, tick=20, ballots=votes(("SKIP", "supported"), ("SKIP", "supported"))
    )
    assert gp.SUSPICION_MOVED in shelves_of(blind_game(meetings=(first, cleared)))
    accused = meeting(
        1,
        tick=20,
        ballots=votes(("SKIP", "supported"), ("SKIP", "supported")),
        turns=(turn("p-2", "p-5"),),
    )
    assert gp.SUSPICION_MOVED not in shelves_of(blind_game(meetings=(first, accused)))
    died = meeting(
        1,
        tick=20,
        ballots=votes(("SKIP", "supported"), ("SKIP", "supported")),
        living=frozenset(PLAYERS) - {"p-5"},
    )
    assert gp.SUSPICION_MOVED not in shelves_of(
        blind_game(kills=(kill(15, "p-5"),), meetings=(first, died))
    )


def test_a_self_accusation_keeps_no_suspicion_on_a_player() -> None:
    """Planted: the player who drew ballots only accuses themselves next meeting.

    A recorded transcript can carry a self-accusation (the meeting layer's own
    accuser indexes skip one, ``meetings/corroboration.py`` and
    ``meetings/transcript.py``), so a speaker naming themselves is no charge
    against them, and suspicion still moved away.
    """

    first = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-5", "supported"), ("SKIP", "supported"), ("SKIP", "supported")
        ),
    )
    self_accused = meeting(
        1,
        tick=20,
        ballots=votes(("SKIP", "supported"), ("SKIP", "supported")),
        turns=(turn("p-5", "p-5"),),
    )
    assert shelves_of(blind_game(meetings=(first, self_accused)))[
        gp.SUSPICION_MOVED
    ] == gp.Pointer(meetings=(1,))


def test_suspicion_moved_when_the_lead_changes_while_the_old_lead_lives() -> None:
    held = (("SKIP", "supported"), ("SKIP", "supported"))
    first = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-5", "supported"), ("p-5", "supported"), ("p-6", "supported"), *held
        ),
    )
    second = meeting(
        1,
        tick=20,
        ballots=votes(
            ("p-6", "supported"), ("p-6", "supported"), ("p-5", "supported"), *held
        ),
    )
    assert first.ejected is None and second.ejected is None
    assert gp.SUSPICION_MOVED in shelves_of(blind_game(meetings=(first, second)))
    gone = dataclasses.replace(second, living=frozenset(PLAYERS) - {"p-5"})
    assert gp.SUSPICION_MOVED not in shelves_of(blind_game(meetings=(first, gone)))


def test_a_third_round_needs_three_meetings() -> None:
    three = tuple(meeting(index, tick=10 * (index + 1)) for index in range(3))
    assert shelves_of(blind_game(meetings=three))[gp.THIRD_ROUND] == gp.Pointer(
        meetings=(2,)
    )
    assert gp.THIRD_ROUND not in shelves_of(blind_game(meetings=three[:2]))


def test_caught_venting() -> None:
    vented = meeting(0, tick=10, vent=(frozenset({"p-7"}),))
    assert shelves_of(blind_game(meetings=(vented,)))[gp.CAUGHT_VENTING] == gp.Pointer(
        meetings=(0,)
    )
    assert gp.CAUGHT_VENTING not in shelves_of(
        blind_game(meetings=(meeting(0, tick=10),))
    )
    empty = meeting(0, tick=10, vent=(frozenset(),))
    assert gp.CAUGHT_VENTING not in shelves_of(blind_game(meetings=(empty,)))


def test_one_line_two_readings() -> None:
    def cited(label: str, other_target: str) -> MeetingFact:
        return meeting(
            0,
            tick=10,
            ballots=(
                ballot("p-0", "p-3", "supported", reason="turn-1"),
                ballot("p-1", other_target, label, reason="turn-1"),
            ),
        )

    assert shelves_of(blind_game(meetings=(cited("off_target", "SKIP"),)))[
        gp.ONE_LINE_TWO_READINGS
    ] == gp.Pointer(meetings=(0,))
    assert gp.ONE_LINE_TWO_READINGS not in shelves_of(
        blind_game(meetings=(cited("supported", "p-3"),))
    )
    assert gp.ONE_LINE_TWO_READINGS not in shelves_of(
        blind_game(meetings=(cited("flag_only", "SKIP"),))
    )


def test_the_eyewitness_chip_marks_a_holder_citing_its_own_kill_row() -> None:
    def chip(cited: str | None, row_id: str | None) -> tuple[int, ...]:
        row = OwnKillRowFact(
            holder="p-2", subject="p-8", room="CAFETERIA", tick=5, citation_id=row_id
        )
        fact = meeting(
            0, tick=10, ballots=(ballot("p-2", "p-8", cited=cited),), rows=(row,)
        )
        return gp.eyewitness_meetings(blind_game(meetings=(fact,)))

    assert chip("obs-9", "obs-9") == (0,)
    assert chip("obs-1", "obs-9") == ()
    assert chip(None, None) == ()


def test_the_chip_places_no_game_on_a_shelf() -> None:
    row = OwnKillRowFact(
        holder="p-2", subject="p-8", room="CAFETERIA", tick=5, citation_id="obs-9"
    )
    skips = votes(
        ("SKIP", "supported"), ("SKIP", "supported"), ("SKIP", "supported"), start=3
    )
    fact = meeting(
        0, tick=10, ballots=(ballot("p-2", "p-8", cited="obs-9"), *skips), rows=(row,)
    )
    profile = profile_of(carrier(game(meetings=(fact,))))
    assert [member.model_dump() for member in profile.pre_reveal.chips[0].members] == [
        {"seed": 0, "meetings": (0,)}
    ]
    assert all(not shelf.members for shelf in profile.pre_reveal.shelves)
    assert gp.EYEWITNESS_CHIP not in {
        table.name for table in profile.reveal.class_tables
    }


# ---------------------------------------------------------------------------
# 6. Reveal shelves and facets
# ---------------------------------------------------------------------------


def reveal_of(**kwargs: Any) -> gp.RevealGame:
    return revealed(carrier(game(**kwargs)))[0]


def test_a_one_vote_ejection() -> None:
    one = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-3", "supported"), ("p-3", "supported"), ("SKIP", "supported")
        ),
    )
    assert gp.reveal_pointers(reveal_of(meetings=(one,)))[
        gp.ONE_VOTE_EJECTION
    ] == gp.Pointer(meetings=(0,))
    two = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-3", "supported"),
            ("p-3", "supported"),
            ("p-3", "supported"),
            ("SKIP", "supported"),
        ),
    )
    assert gp.ONE_VOTE_EJECTION not in gp.reveal_pointers(reveal_of(meetings=(two,)))


def test_nobody_voted_out() -> None:
    skipped = (meeting(0, tick=10), meeting(1, tick=20))
    assert gp.reveal_pointers(reveal_of(meetings=skipped))[
        gp.NOBODY_VOTED_OUT
    ] == gp.Pointer(meetings=(0, 1))
    assert gp.NOBODY_VOTED_OUT not in gp.reveal_pointers(reveal_of())
    ejection = meeting(1, tick=20, ballots=votes(("p-3", "supported")))
    assert gp.NOBODY_VOTED_OUT not in gp.reveal_pointers(
        reveal_of(meetings=(skipped[0], ejection))
    )


@pytest.mark.parametrize(
    ("tasks", "wire", "runaway"),
    [
        ((13, 14), True, False),
        ((12, 14), False, False),
        ((7, 14), False, True),
        ((8, 14), False, False),
    ],
)
def test_an_impostor_win_counts_the_tasks_left(
    tasks: tuple[int, int], wire: bool, runaway: bool
) -> None:
    found = gp.reveal_pointers(reveal_of(end_reason="IMPOSTOR_PARITY", tasks=tasks))
    assert (gp.DOWN_TO_THE_WIRE in found, gp.RUNAWAY in found) == (wire, runaway)


def test_the_wire_needs_a_start_three_steps_away() -> None:
    found = gp.reveal_pointers(reveal_of(end_reason="IMPOSTOR_PARITY", tasks=(1, 2)))
    assert gp.DOWN_TO_THE_WIRE not in found
    assert gp.distance(
        reveal_of(end_reason="IMPOSTOR_PARITY", tasks=(2, 3))
    ) == gp.Distance(counts="tasks_left", steps=1, start=3)
    assert gp.DOWN_TO_THE_WIRE in gp.reveal_pointers(
        reveal_of(end_reason="IMPOSTOR_PARITY", tasks=(2, 3))
    )


def test_a_task_win_reads_the_symmetric_distance_from_its_living_count() -> None:
    """Two crewmates killed, an impostor ejected: five crew and one impostor live."""

    ejection = meeting(0, tick=10, ballots=votes(*[("p-7", "supported")] * 4))
    measured = gp.distance(
        reveal_of(
            end_reason="CREWMATE_TASKS",
            kills=(kill(5, "p-1"), kill(15, "p-2")),
            meetings=(ejection,),
        )
    )
    assert measured == gp.Distance(counts="kills_short_of_parity", steps=4, start=5)
    found = gp.reveal_pointers(
        reveal_of(
            end_reason="CREWMATE_TASKS",
            kills=(kill(5, "p-1"), kill(15, "p-2")),
            meetings=(ejection,),
        )
    )
    assert gp.RUNAWAY in found


def test_an_ejection_win_counts_at_the_deciding_meeting() -> None:
    deciding = meeting(
        0,
        tick=30,
        ballots=votes(*[("p-7", "supported")] * 3),
        living=frozenset({"p-0", "p-1", "p-2", "p-7"}),
    )
    measured = gp.distance(
        reveal_of(end_reason="CREWMATE_EJECT", meetings=(deciding,), terminal_tick=30)
    )
    assert measured == gp.Distance(counts="kills_short_of_parity", steps=2, start=5)
    with pytest.raises(
        gp.GameProfileConformanceError,
        match=r"^seed 9: an ejection win with no meeting$",
    ):
        gp.distance(reveal_of(seed=9, end_reason="CREWMATE_EJECT"))


def test_a_stopped_game_has_no_losing_side() -> None:
    assert gp.distance(reveal_of(end_reason="TICK_BUDGET_REACHED")) is None


def test_decided_at_a_meeting() -> None:
    last = meeting(0, tick=30)
    assert gp.reveal_pointers(reveal_of(meetings=(last,), terminal_tick=30))[
        gp.DECIDED_AT_A_MEETING
    ] == gp.Pointer(meetings=(0,))
    assert gp.DECIDED_AT_A_MEETING not in gp.reveal_pointers(
        reveal_of(meetings=(last,), terminal_tick=31)
    )


def test_decided_without_proof_splits_right_and_wrong_by_the_ejected_role() -> None:
    impostor = meeting(0, tick=10, ballots=votes(*[("p-7", "supported")] * 3))
    crewmate = meeting(1, tick=20, ballots=votes(*[("p-3", "flag_only")] * 3))
    found = gp.reveal_pointers(reveal_of(meetings=(impostor, crewmate)))
    assert found[gp.RIGHT_WITHOUT_PROOF] == gp.Pointer(meetings=(0,))
    assert found[gp.WRONG_ON_WHAT_IT_HELD] == gp.Pointer(meetings=(1,))
    vented = meeting(
        0,
        tick=10,
        ballots=votes(*[("p-7", "supported")] * 3),
        vent=(frozenset({"p-7"}),),
    )
    loose = meeting(
        0,
        tick=10,
        ballots=votes(
            ("p-7", "supported"), ("p-7", "supported"), ("p-7", "off_target")
        ),
    )
    for fact in (vented, loose):
        found = gp.reveal_pointers(reveal_of(meetings=(fact,)))
        assert gp.RIGHT_WITHOUT_PROOF not in found
    inputs, sc = _manufactured_case()
    assert gp.WRONG_ON_WHAT_IT_HELD not in gp.reveal_pointers(revealed(inputs, sc)[0])


def test_the_pair_is_always_emitted_with_an_empty_half() -> None:
    impostor = meeting(0, tick=10, ballots=votes(*[("p-7", "supported")] * 3))
    profile = profile_of(carrier(game(meetings=(impostor,))))
    pair = profile.reveal.decided_without_proof
    assert [member.seed for member in pair.right.members] == [0]
    assert pair.wrong.members == ()
    assert pair.wrong.name == gp.WRONG_ON_WHAT_IT_HELD
    dumped = json.loads(gp.serialize_profile(profile))
    assert dumped["reveal"]["decided_without_proof"]["wrong"] == {
        "name": gp.WRONG_ON_WHAT_IT_HELD,
        "members": [],
    }


def test_the_reveal_facets() -> None:
    ejections = (
        meeting(0, tick=10, ballots=votes(*[("p-7", "supported")] * 3)),
        meeting(1, tick=20, ballots=votes(*[("p-3", "supported")] * 3)),
    )
    profile = profile_of(
        carrier(
            game(
                meetings=ejections,
                sabotage=(4, 5, 9),
                end_reason="IMPOSTOR_PARITY",
                tasks=(9, 14),
            )
        )
    )
    (facets,) = profile.reveal.games
    assert facets.ending == "IMPOSTOR_PARITY"
    assert facets.sabotage_starts == (4, 9)
    assert (facets.tasks_done, facets.tasks_assigned) == (9, 14)
    assert [(item.meeting, item.right) for item in facets.ejections] == [
        (0, True),
        (1, False),
    ]
    assert facets.distance is not None
    assert (facets.distance.counts, facets.distance.steps, facets.distance.start) == (
        "tasks_left",
        5,
        14,
    )


def test_the_pre_reveal_facets() -> None:
    first = kill(5, "p-1")
    second = kill(17, "p-2")
    unfound = kill(40, "p-3")
    meetings = (
        meeting(0, tick=8, trigger="report", opener="p-4", body=body_id(first)),
        meeting(1, tick=12, regrouped=True),
    )
    (facets,) = profile_of(
        carrier(
            game(kills=(first, second, unfound), meetings=meetings, terminal_tick=44)
        )
    ).pre_reveal.games
    assert facets.ticks == 44
    assert [
        (item.index, item.tick, item.trigger, item.regrouped)
        for item in facets.meetings
    ] == [
        (0, 8, "report", True),
        (1, 12, "emergency", True),
    ]
    assert [(item.tick, item.in_wave) for item in facets.kills] == [
        (5, False),
        (17, False),
        (40, False),
    ]
    assert [(item.meeting, item.corpse_age) for item in facets.reports] == [(0, 3)]
    assert facets.bodies_never_found == 2
    assert facets.tripped == ()


# ---------------------------------------------------------------------------
# 7. The leak rule
# ---------------------------------------------------------------------------


def brute_force_p(a: int, b: int, c: int, d: int) -> Fraction:
    """The two-sided p by enumerating every way to draw the first row."""

    total = a + b + c + d
    successes = a + c
    draws = list(itertools.combinations(range(total), a + b))
    counts: dict[int, int] = {}
    for chosen in draws:
        hit = sum(1 for item in chosen if item < successes)
        counts[hit] = counts.get(hit, 0) + 1
    probability = {hit: Fraction(count, len(draws)) for hit, count in counts.items()}
    observed = probability[a]
    return sum((p for p in probability.values() if p <= observed), Fraction(0))


_TABLES: Final = st.tuples(*(st.integers(0, 4) for _ in range(4))).filter(
    lambda table: sum(table) <= 11
)


@settings(max_examples=120, deadline=None, database=None)
@given(table=_TABLES)
def test_the_fisher_p_is_the_brute_force_hypergeometric_p(
    table: tuple[int, int, int, int],
) -> None:
    assert gp.fisher_two_sided(*table) == brute_force_p(*table)


def one_sided_p(a: int, b: int, c: int, d: int) -> Fraction:
    """Planted: the upper tail alone."""

    import math

    row, column, total = a + b, a + c, a + b + c + d
    whole = math.comb(total, row)
    return sum(
        (
            Fraction(math.comb(column, x) * math.comb(total - column, row - x), whole)
            for x in range(a, min(row, column) + 1)
        ),
        Fraction(0),
    )


def test_a_one_sided_p_fails_the_brute_force_property() -> None:
    tables = [
        table for table in itertools.product(range(4), repeat=4) if sum(table) <= 10
    ]
    assert all(gp.fisher_two_sided(*table) == brute_force_p(*table) for table in tables)
    assert any(one_sided_p(*table) != brute_force_p(*table) for table in tables)


def test_the_fisher_p_reproduces_the_design_memos_tables() -> None:
    assert round(float(gp.fisher_two_sided(4, 2, 42, 2)), 4) == 0.0655
    assert round(float(gp.fisher_two_sided(2, 18, 11, 19)), 4) == 0.0498
    assert round(float(gp.fisher_two_sided(22, 18, 2, 8)), 4) == 0.0766
    with pytest.raises(
        ValueError, match=r"^a 2x2 table cannot hold a negative count: \(1, -1, 2, 3\)$"
    ):
        gp.fisher_two_sided(1, -1, 2, 3)


def _era(n: int = 50) -> frozenset[int]:
    return frozenset(range(n))


def test_a_candidate_matching_one_ending_exactly_leaks() -> None:
    members = frozenset(range(13))
    found = gp.classify_candidate(
        "planted", members, seeds=_era(), facts=(("CREWMATE_EJECT", members),)
    )
    assert found.classification == "leaks"
    assert found.rows[0].p < gp.LEAK_P_LEVEL
    spread = gp.classify_candidate(
        "planted",
        members,
        seeds=_era(),
        facts=(
            (
                "CREWMATE_EJECT",
                frozenset({0, 1, 2, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29}),
            ),
        ),
    )
    assert spread.classification == "shelf"


def test_members_outside_the_era_are_refused() -> None:
    """The refusal names the candidate and only the members the era lacks."""

    with pytest.raises(
        ValueError, match=r"^planted-shelf: members outside the era: \[60, 61\]$"
    ):
        gp.classify_candidate(
            "planted-shelf", frozenset({3, 60, 61}), seeds=_era(), facts=()
        )


def _fifty_game_era() -> CensusInputs:
    """Six games carry a double kill; two of them and two others, one tripped, end
    in a task win; the tripped game's only meeting ejects on an off-target ballot."""

    games: list[GameFacts] = []
    for seed in range(50):
        kills = (kill(5, "p-1"), kill(5, "p-2")) if seed < 6 else (kill(5, "p-1"),)
        ending = "CREWMATE_TASKS" if seed in {0, 1, 6, 7} else "IMPOSTOR_PARITY"
        meetings: tuple[MeetingFact, ...] = ()
        if seed == 7:
            meetings = (
                meeting(
                    0,
                    tick=10,
                    seed=7,
                    ballots=votes(
                        ("p-3", "supported"),
                        ("p-3", "off_target"),
                        ("SKIP", "supported"),
                    ),
                ),
            )
        games.append(
            game(
                seed,
                kills=kills,
                meetings=meetings,
                end_reason=ending,
                terminal_tick=12,
            )
        )
    return carrier(*games)


def _class_of(profile: gp.GameProfile, name: str) -> str:
    return next(
        entry.classification for entry in profile.catalogue if entry.name == name
    )


def test_the_leak_universe_counts_a_tripped_game_as_a_non_member() -> None:
    profile = profile_of(_fifty_game_era())
    assert [game.seed for game in profile.pre_reveal.games if game.tripped] == [7]
    table = next(
        table for table in profile.reveal.class_tables if table.name == gp.DOUBLE_KILL
    )
    row = next(row for row in table.rows if row.fact == "CREWMATE_TASKS")
    assert (row.a, row.b, row.c, row.d) == (2, 4, 2, 42)
    assert round(row.p, 4) == 0.0655
    assert _class_of(profile, gp.DOUBLE_KILL) == "shelf"
    assert gp.DOUBLE_KILL in {shelf.name for shelf in profile.pre_reveal.shelves}


def test_a_universe_dropping_the_tripped_game_moves_the_shelf_and_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: the fold drops the tripped game from the 2x2 tables."""

    original = gp.classify_candidate

    def dropping(
        name: str,
        members: frozenset[int],
        *,
        seeds: frozenset[int],
        facts: Sequence[tuple[str, frozenset[int]]],
    ) -> gp.CandidateClass:
        return original(
            name,
            members,
            seeds=seeds - {7},
            facts=tuple((fact, holders - {7}) for fact, holders in facts),
        )

    monkeypatch.setattr(gp, "classify_candidate", dropping)
    profile = profile_of(_fifty_game_era())
    table = next(
        table for table in profile.reveal.class_tables if table.name == gp.DOUBLE_KILL
    )
    row = next(row for row in table.rows if row.fact == "CREWMATE_TASKS")
    assert (row.a, row.b, row.c, row.d) == (2, 4, 1, 42)
    assert round(row.p, 4) == 0.0361
    assert _class_of(profile, gp.DOUBLE_KILL) == "leaks"


def test_the_leak_facts_are_each_recorded_ending_then_the_two_ejection_facts() -> None:
    ejecting = meeting(0, tick=10, ballots=votes(*[("p-3", "supported")] * 3))
    games = (
        game(0, end_reason="IMPOSTOR_PARITY", meetings=(ejecting,)),
        game(1, end_reason="CREWMATE_TASKS"),
    )
    facts = gp.era_facts(revealed(carrier(*games)))
    assert facts == (
        ("CREWMATE_TASKS", frozenset({1})),
        ("IMPOSTOR_PARITY", frozenset({0})),
        (gp.ANY_EJECTION, frozenset({0})),
        (gp.CREWMATE_EJECTED, frozenset({0})),
    )
    impostor = meeting(0, tick=10, ballots=votes(*[("p-7", "supported")] * 3))
    facts = gp.era_facts(revealed(carrier(game(0, meetings=(impostor,)))))
    assert dict(facts)[gp.CREWMATE_EJECTED] == frozenset()
    assert dict(facts)[gp.ANY_EJECTION] == frozenset({0})


# ---------------------------------------------------------------------------
# 8. The saturation rule
# ---------------------------------------------------------------------------


def test_thirty_eight_of_fifty_is_a_facet_and_thirty_seven_a_shelf() -> None:
    quiet = (("IMPOSTOR_PARITY", frozenset(range(0, 50, 2))),)
    assert (
        gp.classify_candidate(
            "planted", frozenset(range(38)), seeds=_era(), facts=quiet
        ).classification
        == "saturated"
    )
    assert (
        gp.classify_candidate(
            "planted", frozenset(range(37)), seeds=_era(), facts=quiet
        ).classification
        == "shelf"
    )
    assert gp.is_saturated(38, 50) and not gp.is_saturated(37, 50)


def test_a_tripped_member_does_not_saturate_a_candidate() -> None:
    """Planted: 37 untripped games and one tripped game carry a double kill.

    The catalogue classes the candidate over its 37 untripped members, a shelf,
    so no game may carry it as a saturated moment; counting the tripped game
    reads 38 of 50, and the two halves of the served file would disagree.
    """

    games: list[GameFacts] = []
    for seed in range(50):
        kills = (kill(5, "p-1"), kill(5, "p-2")) if seed < 38 else (kill(5, "p-1"),)
        meetings: tuple[MeetingFact, ...] = ()
        if seed == 0:
            meetings = (
                meeting(
                    0,
                    tick=10,
                    seed=0,
                    ballots=votes(
                        ("p-3", "supported"),
                        ("p-3", "off_target"),
                        ("SKIP", "supported"),
                    ),
                ),
            )
        games.append(game(seed, kills=kills, meetings=meetings, terminal_tick=12))
    inputs = carrier(*games)
    assert gp.read_pre_reveal(blind_set(inputs)).saturated == ()
    profile = profile_of(inputs)
    assert [game.seed for game in profile.pre_reveal.games if game.tripped] == [0]
    assert _class_of(profile, gp.DOUBLE_KILL) == "shelf"
    shelf = next(
        shelf for shelf in profile.pre_reveal.shelves if shelf.name == gp.DOUBLE_KILL
    )
    assert [member.seed for member in shelf.members] == list(range(1, 38))
    assert not [
        game.seed for game in profile.pre_reveal.games if gp.DOUBLE_KILL in game.moments
    ]


def test_saturation_applies_before_the_leak_rule() -> None:
    members = frozenset(range(40))
    found = gp.classify_candidate(
        "planted", members, seeds=_era(), facts=(("CREWMATE_TASKS", members),)
    )
    assert any(row.p < gp.LEAK_P_LEVEL for row in found.rows)
    assert found.classification == "saturated"


def test_a_saturated_candidate_is_served_as_a_facet() -> None:
    games = [
        game(
            seed,
            kills=(kill(17, "p-1"),) if seed < 4 else (),
            meetings=(meeting(0, tick=10, seed=seed),),
            terminal_tick=19,
        )
        for seed in range(5)
    ]
    profile = profile_of(carrier(*games))
    entry = next(
        entry
        for entry in profile.catalogue
        if entry.name == gp.STRUCK_AFTER_THE_REGROUP
    )
    assert (entry.half, entry.kind, entry.classification) == (
        "pre_reveal",
        "facet",
        "saturated",
    )
    assert gp.STRUCK_AFTER_THE_REGROUP not in {
        shelf.name for shelf in (*profile.pre_reveal.shelves, *profile.reveal.shelves)
    }
    assert [game.moments for game in profile.pre_reveal.games] == [
        (gp.STRUCK_AFTER_THE_REGROUP,)
    ] * 4 + [()]


# ---------------------------------------------------------------------------
# 9. The constants
# ---------------------------------------------------------------------------

#: The design constants each profile version froze. A changed constant needs a
#: new version and a new row.
CONSTANT_PINS: Final[Mapping[int, Mapping[str, object]]] = MappingProxyType(
    {
        2: MappingProxyType(
            {
                "SLOW_BURN_TICKS": 20,
                "WAVE_SLACK_TICKS": 4,
                "CLOSE_CALL_MARGIN": 1,
                "THIRD_ROUND_MEETINGS": 3,
                "DOWN_TO_THE_WIRE_START": 3,
                "RUNAWAY_SHARE": Fraction(1, 2),
                "LEAK_P_LEVEL": Fraction("0.05"),
                "SATURATION_SHARE": Fraction(3, 4),
            }
        )
    }
)


def pin_failures(
    module: ModuleType, pins: Mapping[int, Mapping[str, object]]
) -> list[str]:
    """Each constant that moved from its version's row, or the missing row."""

    version = module.RUBRIC_VERSION
    if version not in pins:
        return [f"no pinned row for rubric version {version}"]
    return [
        name
        for name, value in pins[version].items()
        if getattr(module, name) != value
        or type(getattr(module, name)) is not type(value)
    ]


def test_the_constants_are_pinned_to_their_version() -> None:
    assert gp.RUBRIC_VERSION == 2
    assert pin_failures(gp, CONSTANT_PINS) == []


def _load_copy(path: Path, monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, path.stem, module)
    spec.loader.exec_module(module)
    return module


def test_a_moved_constant_fails_the_pin_until_its_version_moves(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = _MODULE_SOURCE.read_text(encoding="utf-8")
    slow = "SLOW_BURN_TICKS: Final[int] = 20\n"
    version = "RUBRIC_VERSION: Final[int] = 2\n"
    assert source.count(slow) == 1 and source.count(version) == 1
    moved = tmp_path / "profile_slow_burn_19.py"
    moved.write_text(
        source.replace(slow, "SLOW_BURN_TICKS: Final[int] = 19\n"), encoding="utf-8"
    )
    assert pin_failures(_load_copy(moved, monkeypatch), CONSTANT_PINS) == [
        "SLOW_BURN_TICKS"
    ]
    bumped = tmp_path / "profile_version_3.py"
    bumped.write_text(
        source.replace(slow, "SLOW_BURN_TICKS: Final[int] = 19\n").replace(
            version, "RUBRIC_VERSION: Final[int] = 3\n"
        ),
        encoding="utf-8",
    )
    module = _load_copy(bumped, monkeypatch)
    assert pin_failures(module, CONSTANT_PINS) == ["no pinned row for rubric version 3"]
    extended = {**CONSTANT_PINS, 3: {**CONSTANT_PINS[2], "SLOW_BURN_TICKS": 19}}
    assert pin_failures(module, extended) == []


def test_the_served_constants_are_the_modules() -> None:
    constants = gp.profile_constants()
    assert constants.model_dump() == {
        "slow_burn_ticks": gp.SLOW_BURN_TICKS,
        "wave_slack_ticks": gp.WAVE_SLACK_TICKS,
        "close_call_margin": gp.CLOSE_CALL_MARGIN,
        "third_round_meetings": gp.THIRD_ROUND_MEETINGS,
        "down_to_the_wire_start": gp.DOWN_TO_THE_WIRE_START,
        "runaway_share": "1/2",
        "leak_p_level": "0.05",
        "saturation_share": "3/4",
    }
    with pytest.raises(ValueError, match=r"^1/3 has no short decimal form$"):
        gp._decimal(Fraction(1, 3))


_GLOSSARY: Final = repo_root / "docs" / "glossary.md"
_SHARE_WORDS: Final[Mapping[Fraction, str]] = MappingProxyType(
    {Fraction(3, 4): "three quarters", Fraction(1, 2): "half"}
)


def _glossary_entry(term: str) -> str:
    """The text under the glossary heading that starts with ``term``."""

    text = _GLOSSARY.read_text(encoding="utf-8")
    marker = f"\n### {term}"
    assert text.count(marker) == 1, term
    return " ".join(text.split(marker, 1)[1].split("\n### ", 1)[0].split())


def test_the_glossary_states_the_modules_leak_and_saturation_numbers() -> None:
    assert f"below {gp.profile_constants().leak_p_level}" in _glossary_entry(
        "leak rule"
    )
    assert f"more than {_SHARE_WORDS[gp.SATURATION_SHARE]}" in _glossary_entry(
        "saturation rule"
    )


# ---------------------------------------------------------------------------
# 10. The served file refuses a number to climb
# ---------------------------------------------------------------------------

_SERVED: Final = SAMPLES_9P2I / "results-game-profile.json"
BANNED_KEY_TOKENS: Final = frozenset(
    {"score", "rank", "total", "points", "weight", "best", "top"}
)


def _models_under(model: type[BaseModel]) -> Iterator[type[BaseModel]]:
    seen: set[type[BaseModel]] = set()
    stack = [model]
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        yield current
        for field in current.model_fields.values():
            pending = [field.annotation]
            while pending:
                annotation = pending.pop()
                if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                    stack.append(annotation)
                elif get_origin(annotation) is not None or get_args(annotation):
                    pending.extend(get_args(annotation))


def banned_keys(model: type[BaseModel]) -> list[str]:
    """Every field under ``model`` whose name carries a scoring word."""

    return sorted(
        f"{current.__name__}.{name}"
        for current in _models_under(model)
        for name in current.model_fields
        if set(name.split("_")) & BANNED_KEY_TOKENS
    )


def test_no_field_of_the_profile_names_a_score() -> None:
    assert banned_keys(gp.GameProfile) == []
    assert len(list(_models_under(gp.GameProfile))) == 23


def test_the_key_scan_refuses_a_planted_total() -> None:
    class Planted(gp.GameFacets):
        per_game_total: int

    class PlantedRank(BaseModel):
        games: tuple[Planted, ...]
        best_rank: int

    assert banned_keys(PlantedRank) == [
        "Planted.per_game_total",
        "PlantedRank.best_rank",
    ]


def _committed() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(_SERVED.read_text(encoding="utf-8"))
    return payload


def test_a_file_carrying_a_score_rank_or_total_is_refused_at_load() -> None:
    gp.GameProfile.model_validate(_committed())
    for planted in (
        {**_committed(), "score": 50.0},
        {**_committed(), "rank": 1},
    ):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            gp.GameProfile.model_validate(planted)
    per_game = _committed()
    per_game["pre_reveal"]["games"][0]["total"] = 3
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        gp.GameProfile.model_validate(per_game)


def test_members_out_of_seed_order_raise() -> None:
    with pytest.raises(
        ValidationError, match=r"planted-shelf: members out of seed order: \[4, 2\]"
    ):
        gp.Shelf(
            name="planted-shelf",
            members=(
                gp.ShelfMember(seed=4, meetings=(), kill_ticks=()),
                gp.ShelfMember(seed=2, meetings=(), kill_ticks=()),
            ),
        )
    with pytest.raises(
        ValidationError, match=r"planted-chip: members out of seed order: \[3, 3\]"
    ):
        gp.Chip(
            name="planted-chip",
            members=(
                gp.ChipMember(seed=3, meetings=()),
                gp.ChipMember(seed=3, meetings=()),
            ),
        )
    payload = _committed()
    payload["pre_reveal"]["games"] = list(reversed(payload["pre_reveal"]["games"]))
    with pytest.raises(ValidationError, match="all games: members out of seed order"):
        gp.GameProfile.model_validate(payload)
    payload = _committed()
    payload["reveal"]["games"] = list(reversed(payload["reveal"]["games"]))
    with pytest.raises(
        ValidationError, match="reveal facets: members out of seed order"
    ):
        gp.GameProfile.model_validate(payload)


_ENDING_TOKENS: Final = ("winner", "reason", "IMPOSTOR", "CREWMATE")


def ending_tokens(half: Mapping[str, Any]) -> list[str]:
    text = json.dumps(half)
    return [token for token in _ENDING_TOKENS if token in text]


def test_the_pre_reveal_half_names_no_winner_reason_or_role() -> None:
    assert ending_tokens(_committed()["pre_reveal"]) == []
    assert ending_tokens(_committed()["reveal"]) != []


def test_an_ending_facet_moved_before_the_reveal_fails_the_token_test() -> None:
    planted = _committed()
    planted["pre_reveal"]["games"][0]["ending"] = planted["reveal"]["games"][0][
        "ending"
    ]
    assert ending_tokens(planted["pre_reveal"]) != []


# ---------------------------------------------------------------------------
# The shown set's reading, through the committed file
# ---------------------------------------------------------------------------


def _members(shelves: Sequence[Mapping[str, Any]]) -> dict[str, list[int]]:
    return {
        shelf["name"]: [member["seed"] for member in shelf["members"]]
        for shelf in shelves
    }


def test_the_served_file_reads_the_shown_sets_numbers() -> None:
    served = _committed()
    pre = _members(served["pre_reveal"]["shelves"])
    assert {name: len(seeds) for name, seeds in pre.items()} == {
        gp.REPORTER_SAW_IT: 14,
        gp.DOUBLE_KILL: 7,
        gp.SLOW_BURN: 11,
        gp.TWO_KILLS_AFTER_ONE_REGROUP: 6,
        gp.CLOSE_CALL: 16,
        gp.SUSPICION_MOVED: 16,
        gp.THIRD_ROUND: 19,
    }
    assert list(pre) == [name for name in gp.CANDIDATES if name in pre]
    assert pre[gp.REPORTER_SAW_IT] == [
        0,
        1,
        7,
        9,
        16,
        19,
        23,
        28,
        29,
        30,
        32,
        35,
        38,
        43,
    ]
    assert pre[gp.TWO_KILLS_AFTER_ONE_REGROUP] == [0, 4, 12, 13, 16, 36]
    reveal = _members(served["reveal"]["shelves"])
    assert {name: len(seeds) for name, seeds in reveal.items()} == {
        gp.CAUGHT_VENTING: 19,
        gp.ONE_LINE_TWO_READINGS: 20,
        gp.ONE_VOTE_EJECTION: 10,
        gp.NOBODY_VOTED_OUT: 4,
        gp.DOWN_TO_THE_WIRE: 12,
        gp.RUNAWAY: 14,
        gp.DECIDED_AT_A_MEETING: 14,
    }
    pair = served["reveal"]["decided_without_proof"]
    assert (
        len(pair["right"]["members"]),
        sum(len(m["meetings"]) for m in pair["right"]["members"]),
    ) == (18, 19)
    assert (
        len(pair["wrong"]["members"]),
        sum(len(m["meetings"]) for m in pair["wrong"]["members"]),
    ) == (20, 21)
    readings = {
        reading["name"]: [
            (entry["seed"], entry["meeting"]) for entry in reading["entries"]
        ]
        for reading in served["pre_reveal"]["tripwires"]["readings"]
    }
    assert readings == {
        "decisive": [(26, 2)],
        "decisive_read_as_skip": [(26, 2)],
        "decisive_all_ungrounded_removed": [(26, 2)],
        "every": [],
        "any": [(26, 2), (41, 0)],
        "manufactured": [],
    }
    tripwires = served["pre_reveal"]["tripwires"]
    assert (tripwires["alibi_flags"], tripwires["alibi_flags_evaluable"]) == (15, 1)
    chip = served["pre_reveal"]["chips"][0]["members"]
    assert (len(chip), sum(len(member["meetings"]) for member in chip)) == (14, 15)
    assert next(member for member in chip if member["seed"] == 19)["meetings"] == [2]
    every_shelf = {**pre, **reveal, **_members((pair["right"], pair["wrong"]))}
    on = {
        seed: sorted(name for name, seeds in every_shelf.items() if seed in seeds)
        for seed in (14, 19)
    }
    assert on[19] == sorted(
        [
            gp.REPORTER_SAW_IT,
            gp.SLOW_BURN,
            gp.THIRD_ROUND,
            gp.CAUGHT_VENTING,
            gp.ONE_LINE_TWO_READINGS,
            gp.DECIDED_AT_A_MEETING,
            gp.RIGHT_WITHOUT_PROOF,
        ]
    )
    assert on[14] == sorted([gp.RUNAWAY, gp.RIGHT_WITHOUT_PROOF])
    tripped = [
        game["seed"] for game in served["pre_reveal"]["games"] if game["tripped"]
    ]
    assert tripped == [26]
    assert all(26 not in seeds for seeds in (*pre.values(), *reveal.values()))
