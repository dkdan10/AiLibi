"""How many committed recordings the decided-trigger allowance still carries.

Walking a committed set and evaluating win conditions at every meeting open
counts the ticks a pre-21.6 engine handed to a meeting after the game was
already decided. Exactly two games in the whole record do: a third occurrence
and a stale entry both turn this red.

Task 21.15 is the expiry. When the re-record lands on the corrected engine this
census reads zero, and ``engine.tick.superseded_meeting_tick`` plus its seven call
sites (eval/replay_walk.py, api/replay_loader.py, training/surrogate/dataset.py,
eval/off_menu.py, training/rollout.py, training/anchor_study.py and
tests/meetings/test_prompt_byte_golden.py) are deleted.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import NoReturn

import pytest

from api.replay_loader import ReplayLoader
from engine.win_conditions import evaluate_win_conditions
from engine.world import Map, load_canonical_map
from eval import validity
from eval.replay_walk import MeetingOpened, ReplayWalkConfig, WalkViolation, walk_replay
from training.anchor_study import walk_corpus_game
from training.rollout import reconstruct_episode

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"
_CORPUS_4P1I = _REPO_ROOT / "replays" / "ml_corpus" / "4p1i"
_ALL_SETS = (
    _SAMPLES_4P1I,
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _CORPUS_4P1I,
    _REPO_ROOT / "replays" / "ml_corpus" / "9p2i",
)


def _raise(violation: WalkViolation) -> NoReturn:
    raise AssertionError(f"census walk violated: {violation}")


_CENSUS_PROFILE = ReplayWalkConfig(
    profile="win-ordering-census",
    on_violation=_raise,
    verify_tick_hashes=True,
)


class _Census:
    """Games, meetings, decided triggers and the crew-minus-impostor margins."""

    def __init__(self) -> None:
        self.games = 0
        self.meetings = 0
        self.decided: list[tuple[str, int, int, str, str]] = []
        self.margins: Counter[int] = Counter()


def _walk_set(set_dir: Path, game_map: Map, census: _Census) -> None:
    num_players, num_impostors, tasks_per_crewmate = validity.resolve_roster_knobs(
        set_dir
    )
    for seed in validity.seeds_on_disk(set_dir):
        census.games += 1
        for walk_event in walk_replay(
            set_dir / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=_CENSUS_PROFILE,
        ):
            if not isinstance(walk_event, MeetingOpened):
                continue
            census.meetings += 1
            alive = [p for p in walk_event.state.players.values() if p.alive]
            impostors = sum(1 for p in alive if p.role == "IMPOSTOR")
            census.margins[len(alive) - 2 * impostors] += 1
            result = evaluate_win_conditions(walk_event.state)
            if result is not None:
                census.decided.append(
                    (
                        set_dir.name,
                        seed,
                        walk_event.entry.tick,
                        result.winner,
                        result.reason,
                    )
                )


@pytest.fixture(scope="module")
def game_map() -> Map:
    return load_canonical_map()


def test_exactly_two_committed_4p1i_games_need_the_allowance(game_map: Map) -> None:
    census = _Census()
    _walk_set(_SAMPLES_4P1I, game_map, census)
    samples_decided = list(census.decided)
    _walk_set(_CORPUS_4P1I, game_map, census)

    assert samples_decided == [("4p1i", 3, 10, "CREWMATES", "CREWMATE_TASKS")]
    assert census.decided == [
        ("4p1i", 3, 10, "CREWMATES", "CREWMATE_TASKS"),
        ("4p1i", 1009, 7, "CREWMATES", "CREWMATE_TASKS"),
    ]
    assert (census.games, census.meetings) == (100, 84)
    assert dict(census.margins) == {1: 84}


#: The two superseded games, as ``(set_dir, seed)``.
_SUPERSEDED = ((_SAMPLES_4P1I, 3), (_CORPUS_4P1I, 1009))


def test_every_reconstruction_home_still_reads_the_superseded_games(
    game_map: Map,
) -> None:
    """Each home that re-derives a tick hash carries the allowance.

    A home that compares a re-derived hash to the recorded one BEFORE its
    GAME_OVER break raises on these two games without the restore, which is how
    ``training.rollout`` and ``training.anchor_study`` were found missing.
    """

    for set_dir, seed in _SUPERSEDED:
        path = set_dir / f"replay-seed-{seed}.jsonl"

        episode = reconstruct_episode(
            path,
            game_map=game_map,
            seed=seed,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
        )
        assert (episode.winner, len(episode.meetings)) == ("CREWMATES", 1)

        facts, _decisions = walk_corpus_game(
            path, num_players=4, num_impostors=1, tasks_per_crewmate=1
        )
        assert (facts.winner, facts.meetings) == ("CREWMATES", 1)

        replay = ReplayLoader(replay_dir=set_dir).load_replay(f"headless-seed-{seed}")
        assert len(replay.meetings) == 1
        assert replay.finale is not None
        assert replay.finale.winner_reason == "CREWMATE_TASKS"


@pytest.mark.campaign
def test_the_four_committed_sets_carry_two_decided_triggers(game_map: Map) -> None:
    census = _Census()
    for set_dir in _ALL_SETS:
        _walk_set(set_dir, game_map, census)

    assert (census.games, census.meetings) == (300, 668)
    assert len(census.decided) == 2
    assert dict(sorted(census.margins.items())) == {
        1: 148,
        2: 116,
        3: 257,
        4: 140,
        5: 7,
    }
