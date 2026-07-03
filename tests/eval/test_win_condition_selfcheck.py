"""Tests for the §6.3 win-condition self-check (eval/win_condition_selfcheck.py).

Three layers:

* **Pure predicate** — :func:`win_condition_is_consistent` and the
  :class:`WinConditionSelfCheck.is_consistent` property over synthetic ticks,
  including the regression case (eliminated-but-game-ran-on) the check exists to
  catch.
* **Committed-replay reconstruction** — the check run over the frozen committed
  4p/1i set (every game consistent; the impostor-ejection games have
  ``first_zero_impostor_tick == game_over_tick``) and the frozen 9p/2i
  impostor-elimination games (multi-impostor + friendly-fire deaths exercise the
  alive-impostor count crossing zero by a path other than the lone ejection).
* **Fail-loud reconstruction** — a wrong roster diverges the per-tick
  ``state_hash`` and raises rather than yielding a misleading tick.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from eval.win_condition_selfcheck import (
    WinConditionRegressionError,
    WinConditionSelfCheck,
    assert_win_condition_consistent,
    check_replay_win_condition,
    win_condition_is_consistent,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
# Both committed sets are now per-set subdirs of replays/samples/ (Task 12.12).
_SAMPLES_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"
_SAMPLES_9P2I = _REPO_ROOT / "replays" / "samples" / "9p2i"

# ---------------------------------------------------------------------------
# Pure predicate
# ---------------------------------------------------------------------------


def test_predicate_vacuous_when_impostors_never_eliminated() -> None:
    # Impostors alive at game end (crew task win / impostor parity): vacuous pass.
    assert win_condition_is_consistent(None, 21) is True
    assert win_condition_is_consistent(None, None) is True


def test_predicate_consistent_when_elimination_equals_game_over() -> None:
    assert win_condition_is_consistent(7, 7) is True


def test_predicate_flags_game_that_ran_past_elimination() -> None:
    # The §6.3 regression: last impostor gone at tick 5, game_over recorded at 8.
    assert win_condition_is_consistent(5, 8) is False


def test_predicate_flags_elimination_with_no_game_over() -> None:
    assert win_condition_is_consistent(7, None) is False


def _check(*, first_zero: int | None, game_over: int | None) -> WinConditionSelfCheck:
    return WinConditionSelfCheck(
        game_id="headless-seed-0",
        seed=0,
        winner="CREWMATES",
        reason="CREWMATE_EJECT",
        first_zero_impostor_tick=first_zero,
        game_over_tick=game_over,
    )


def test_selfcheck_is_consistent_property() -> None:
    assert _check(first_zero=7, game_over=7).is_consistent is True
    assert _check(first_zero=None, game_over=21).is_consistent is True
    assert _check(first_zero=5, game_over=8).is_consistent is False


def test_assert_consistent_passes_and_raises() -> None:
    assert_win_condition_consistent(_check(first_zero=7, game_over=7))  # no raise
    with pytest.raises(WinConditionRegressionError, match="ran past the crew-win"):
        assert_win_condition_consistent(_check(first_zero=5, game_over=8))


def test_selfcheck_model_is_frozen() -> None:
    check = _check(first_zero=7, game_over=7)
    with pytest.raises(ValidationError):
        check.first_zero_impostor_tick = 9


# ---------------------------------------------------------------------------
# Reconstruction over committed replays
# ---------------------------------------------------------------------------


def _selfcheck_4p1i(seed: int) -> WinConditionSelfCheck:
    return check_replay_win_condition(
        _SAMPLES_4P1I / f"replay-seed-{seed}.jsonl",
        seed=seed,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
    )


def test_committed_4p1i_set_holds_the_invariant() -> None:
    """Every committed 4p/1i game satisfies first_zero == game_over (A-A-3)."""

    eliminations = 0
    for seed in range(50):
        check = _selfcheck_4p1i(seed)
        assert check.is_consistent, (
            f"seed {seed}: first_zero={check.first_zero_impostor_tick} "
            f"game_over={check.game_over_tick}"
        )
        if check.first_zero_impostor_tick is not None:
            eliminations += 1
            assert check.game_over_tick == check.first_zero_impostor_tick
    # Ground truth of the Task 14.12 canonical re-record (baseline 2, prompts
    # qwen3_32b.v4, evidence_quality_lift lever ON): on Qwen/Qwen3-32B the flat
    # 4p/1i set ejects the impostor in 12 of 50 games (CREWMATE_EJECT) — matching
    # the set's impostor_ejections=12 (ejection_accuracy 0.9231), and still a jump
    # from the 9B baseline's four. Each elimination's first_zero == game_over tick
    # is asserted above (the A-A-3 invariant, which still holds set-wide); this
    # pins the count the re-record produced, so the §6.3 elimination path runs on
    # the committed bytes, not only the hermetic apply_meeting_result eject tests.
    assert eliminations == 12


def _roster(replay_dir: Path) -> tuple[int, int, int]:
    roster = json.loads((replay_dir / "roster.json").read_text(encoding="utf-8"))
    return (
        roster["num_players"],
        roster["num_impostors"],
        roster["tasks_per_crewmate"],
    )


def _crewmate_eject_seeds(replay_dir: Path) -> list[int]:
    """Seeds whose committed replay ends CREWMATE_EJECT (impostor elimination).

    Read straight from each replay's ``game_over`` row (not the derived report),
    so it adapts to a re-record rather than pinning specific frozen seeds.
    """

    seeds: list[int] = []
    for path in sorted(replay_dir.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.removeprefix("replay-seed-"))
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("kind") == "game_over" and record.get("reason") == (
                "CREWMATE_EJECT"
            ):
                seeds.append(seed)
                break
    return seeds


def test_committed_9p2i_elimination_games_hold_the_invariant() -> None:
    """Multi-impostor 9p/2i eliminations satisfy the invariant (A-A-3).

    Exercises the two-impostor elimination path the single-impostor 4p/1i set
    cannot: when the committed set contains a CREWMATE_EJECT game, the
    alive-impostor count crosses zero before game-over and the §6.3 self-check
    must stay consistent. Skips when the set has no such game — post-7.12
    impostor coordination can leave crew unable to eject both impostors (all
    crew wins via CREWMATE_TASKS), so there is no elimination path to exercise.
    """

    num_players, num_impostors, tasks_per_crewmate = _roster(_SAMPLES_9P2I)
    elimination_seeds = _crewmate_eject_seeds(_SAMPLES_9P2I)
    if not elimination_seeds:
        pytest.skip(
            "no CREWMATE_EJECT game in the committed 9p/2i set: post-7.12 impostor "
            "coordination removed teammate-betrayal, so crew never ejects both "
            "impostors (all crew wins are CREWMATE_TASKS). The §6.3 multi-impostor "
            "elimination path is exercised only when an elimination-bearing set is "
            "recorded; the single-impostor 4p/1i reconstruction still covers §6.3."
        )

    for seed in elimination_seeds:
        check = check_replay_win_condition(
            _SAMPLES_9P2I / f"replay-seed-{seed}.jsonl",
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        assert check.first_zero_impostor_tick is not None  # impostors eliminated
        assert check.is_consistent, (
            f"seed {seed}: first_zero={check.first_zero_impostor_tick} "
            f"game_over={check.game_over_tick}"
        )


def test_wrong_roster_fails_loud_on_state_hash() -> None:
    """A roster that does not match the recording diverges the per-tick hash."""

    with pytest.raises(ValueError, match="reconstruction diverged"):
        check_replay_win_condition(
            _SAMPLES_4P1I / "replay-seed-0.jsonl",
            seed=0,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=2,  # committed 4p/1i is 1 task/crewmate
        )
