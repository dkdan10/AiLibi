"""Unit tests for eval/validity.py (Task 15.1).

Covers each of the ten gate checks with a PASS input and a synthetic VIOLATION
that flips ``passed`` to ``False`` (a gate that cannot fail is not a gate), the
reconstruction cross-check against the tested win-condition home, the
truncated-replay rejection (a recorded ``game_over`` row the walk never earns),
and the baseline-9 reproduction of ``run_validity_gate`` over the committed sets.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, Final, Literal, NoReturn

import pytest

from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval import balance_eval, replay_walk, validity
from eval.balance_eval import run_tournament_eval
from eval.replay_walk import ReplayWalkConfig, WalkViolation
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.validity import (
    TRUNCATED_REPLAY_REASON,
    VALIDITY_THREADED_LAYERS,
    SetInventory,
    ValidityCheck,
    ValidityGateReport,
    _GameReconstruction,
    _KillFact,
    _reconstruct_game,
    assemble_tournament_report,
    check_all_games_reach_game_over,
    check_byte_identical_reconstruction,
    check_cost_and_provenance,
    check_meeting_rate_and_resolution,
    check_no_betrayal,
    check_no_dangling_primary_reason_id,
    check_no_duplicate_meeting_rows,
    check_no_friendly_fire_kills,
    check_no_railroaded_crew_ejections,
    check_no_tick_1_kills,
    experiment_config_violations,
    read_set_inventory,
    recording_sha_violations,
    resolve_roster_knobs,
    roles_by_seed,
    run_validity_gate,
    seed_set_violations,
    seeds_on_disk,
)
from eval.win_condition_selfcheck import (
    WinConditionSelfCheck,
    check_replay_win_condition,
)
from meetings.schemas import AccusationClaim, ContradictionRef
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    ConfigLayer,
    RecordedExperimentConfig,
    wave_settings,
)
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord
from orchestrator.replay_integrity import ReplayIntegrityError

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


@pytest.fixture(scope="module")
def nine_report() -> TournamentReport:
    """The committed 9p2i tournament report (folded once, no reconstruction)."""

    return assemble_tournament_report(_NINE)


# --------------------------------------------------------------------------- #
# Fixture builders                                                             #
# --------------------------------------------------------------------------- #


def _win_check(
    seed: int,
    *,
    first_zero: int | None = None,
    game_over_tick: int | None = 7,
    winner: str | None = "CREWMATES",
) -> WinConditionSelfCheck:
    return WinConditionSelfCheck(
        game_id=f"headless-seed-{seed}",
        seed=seed,
        winner=winner,  # type: ignore[arg-type]
        reason="CREWMATE_EJECT",
        first_zero_impostor_tick=first_zero,
        game_over_tick=game_over_tick,
    )


def _recon(
    seed: int,
    *,
    win_check: WinConditionSelfCheck | None = None,
    kills: Sequence[_KillFact] = (),
    reconstructed_winner: str | None = "__match__",
    reconstructed_reason: str | None = "__match__",
    game_over_is_last_record: bool = True,
) -> _GameReconstruction:
    check = win_check if win_check is not None else _win_check(seed)
    # Default the reconstructed outcome to MATCH the recorded one so a plain
    # _recon is a clean game; pass explicit values to forge a mismatch.
    rw = check.winner if reconstructed_winner == "__match__" else reconstructed_winner
    rr = check.reason if reconstructed_reason == "__match__" else reconstructed_reason
    return _GameReconstruction(
        seed=seed,
        win_check=check,
        kills=tuple(kills),
        reconstructed_winner=rw,  # type: ignore[arg-type]
        reconstructed_reason=rr,
        game_over_is_last_record=game_over_is_last_record,
    )


def _kill(seed: int, tick: int, victim_role: str) -> _KillFact:
    return _KillFact(
        seed=seed,
        tick=tick,
        killer="p-1",
        killer_role="IMPOSTOR",
        victim="p-2",
        victim_role=victim_role,  # type: ignore[arg-type]
    )


def _mini_set(tmp_path: Path, *, seeds: Sequence[int] = (0, 1, 2)) -> Path:
    """A minimal valid replay set (roster + a few 9p2i seeds) under ``tmp_path``."""

    shutil.copy(_NINE / "roster.json", tmp_path / "roster.json")
    for seed in seeds:
        shutil.copy(
            _NINE / f"replay-seed-{seed}.jsonl", tmp_path / f"replay-seed-{seed}.jsonl"
        )
    return tmp_path


def _truncate_tick_stream(replay_path: Path) -> None:
    """Drop the replay's LAST tick row, keeping its ``game_over`` row.

    The corruption shape the gate must reject: the recorded terminal survives
    while the reconstruction stops a tick short. The state-hash chain still
    verifies (a shorter walk breaks no link), so only the game-over check can
    catch it.
    """

    lines = replay_path.read_text(encoding="utf-8").splitlines()
    for index in range(len(lines) - 1, -1, -1):
        if json.loads(lines[index]).get("kind") == "tick":
            del lines[index]
            break
    else:  # pragma: no cover - the committed fixture always has tick rows
        raise AssertionError(f"{replay_path} carries no tick row to drop")
    replay_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _replace_first_game(report: TournamentReport, game: GameReport) -> TournamentReport:
    return report.model_copy(update={"games": (game, *report.games[1:])})


def _first_game_with_meeting(report: TournamentReport) -> GameReport:
    for game in report.games:
        if game.meetings:
            return game
    raise AssertionError("fixture set has no game with a meeting")


# --------------------------------------------------------------------------- #
# 1. all_games_reach_game_over                                                 #
# --------------------------------------------------------------------------- #


def test_all_games_reach_game_over_passes() -> None:
    check = check_all_games_reach_game_over([_recon(0), _recon(1)])
    assert check.passed
    assert check.violations == ()


def test_all_games_reach_game_over_fails_without_game_over() -> None:
    check = check_all_games_reach_game_over(
        [_recon(0), _recon(1, win_check=_win_check(1, game_over_tick=None))]
    )
    assert not check.passed
    assert any("no game_over" in v for v in check.violations)


def test_all_games_reach_game_over_fails_when_the_walk_stops_short() -> None:
    # A game_over row is RECORDED but the reconstruction stopped short: trailing
    # tick rows were dropped, which shortens the walk without breaking the chain.
    check = check_all_games_reach_game_over(
        [_recon(0), _recon(4, reconstructed_winner=None, reconstructed_reason=None)]
    )
    assert not check.passed
    assert any(
        TRUNCATED_REPLAY_REASON in v
        and "seed 4" in v
        and "never reached GAME_OVER" in v
        for v in check.violations
    )


def test_all_games_reach_game_over_fails_on_a_winnerless_game_over_row() -> None:
    check = check_all_games_reach_game_over(
        [_recon(5, win_check=_win_check(5, winner=None))]
    )
    assert not check.passed
    assert any(
        TRUNCATED_REPLAY_REASON in v and "seed 5" in v and "names no winner" in v
        for v in check.violations
    )


def test_all_games_reach_game_over_fails_on_rows_after_the_game_over_row() -> None:
    # Any record kind written after the terminal row rides into the corpus
    # unreplayed, whatever tick number it claims.
    check = check_all_games_reach_game_over([_recon(6, game_over_is_last_record=False)])
    assert not check.passed
    assert any(
        "seed 6" in v and "after the game_over row" in v for v in check.violations
    )


def test_all_games_reach_game_over_counts_only_reconstructed_terminals() -> None:
    # The truncated game must never be summarised as one that reached game_over.
    check = check_all_games_reach_game_over(
        [_recon(0), _recon(1, reconstructed_winner=None, reconstructed_reason=None)]
    )
    assert check.facts["games_total"] == 2
    assert check.facts["games_reached_game_over"] == 1
    assert check.summary.startswith("1/2 games reached a reconstructed game_over")


def test_all_games_reach_game_over_fails_on_win_condition_regression() -> None:
    # Last impostor eliminated at tick 3 but game_over recorded at tick 7.
    regressed = _win_check(2, first_zero=3, game_over_tick=7)
    check = check_all_games_reach_game_over([_recon(2, win_check=regressed)])
    assert not check.passed
    assert any("§6.3" in v for v in check.violations)


def test_all_games_reach_game_over_fails_on_forged_outcome() -> None:
    # Recorded winner CREWMATES but engine reconstructed IMPOSTORS/IMPOSTOR_PARITY.
    forged = _recon(
        3, reconstructed_winner="IMPOSTORS", reconstructed_reason="IMPOSTOR_PARITY"
    )
    check = check_all_games_reach_game_over([forged])
    assert not check.passed
    assert any("forged game_over label" in v for v in check.violations)


# --------------------------------------------------------------------------- #
# 2. meeting_rate_and_resolution                                              #
# --------------------------------------------------------------------------- #


def test_meeting_rate_passes_on_committed(nine_report: TournamentReport) -> None:
    check = check_meeting_rate_and_resolution(nine_report)
    assert check.passed
    assert check.facts["meeting_rate"] == 1.0
    assert check.facts["resolved_meetings"] == 145  # was 151


def test_meeting_rate_fails_below_floor(nine_report: TournamentReport) -> None:
    stripped = nine_report.model_copy(
        update={
            "games": tuple(
                game.model_copy(update={"meetings": ()}) for game in nine_report.games
            )
        }
    )
    check = check_meeting_rate_and_resolution(stripped)
    assert not check.passed
    assert any("floor" in v for v in check.violations)


def test_meeting_resolution_fails_on_unresolved_meeting(
    nine_report: TournamentReport,
) -> None:
    game = _first_game_with_meeting(nine_report)
    ghost = FailedCallReplayEntry(
        game_id=game.game_id,
        meeting_id=f"{game.game_id}:ghost-meeting",
        tick=99,
        model="m",
        prompt_length=0,
        raw_response="",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        error_type="ValidationError",
        error_message="crashed before resolving",
    )
    bad_game = game.model_copy(update={"failed_calls": (ghost,)})
    check = check_meeting_rate_and_resolution(
        _replace_first_game(nine_report, bad_game)
    )
    assert not check.passed
    assert any("unresolved" in v or "aborted" in v for v in check.violations)


def test_no_duplicate_meeting_rows_passes(nine_report: TournamentReport) -> None:
    check = check_no_duplicate_meeting_rows(nine_report)
    assert check.passed
    assert int(check.facts["meetings_total"]) == 145  # type: ignore[arg-type]  # was 151


def test_no_duplicate_meeting_rows_fails(nine_report: TournamentReport) -> None:
    game = _first_game_with_meeting(nine_report)
    dup = game.meetings[0]
    bad_game = game.model_copy(update={"meetings": (dup, *game.meetings)})
    check = check_no_duplicate_meeting_rows(_replace_first_game(nine_report, bad_game))
    assert not check.passed
    assert any("duplicate meeting row" in v for v in check.violations)


# --------------------------------------------------------------------------- #
# 3. no_tick_1_kills / 4. no_friendly_fire_kills                              #
# --------------------------------------------------------------------------- #


def test_no_tick_1_kills_passes() -> None:
    check = check_no_tick_1_kills([_kill(0, tick=5, victim_role="CREWMATE")])
    assert check.passed


@pytest.mark.parametrize("tick", [0, 1])
def test_no_tick_1_kills_fails(tick: int) -> None:
    check = check_no_tick_1_kills([_kill(0, tick=tick, victim_role="CREWMATE")])
    assert not check.passed
    assert check.facts["tick_1_kills"] == 1


def test_no_friendly_fire_passes() -> None:
    check = check_no_friendly_fire_kills([_kill(0, tick=5, victim_role="CREWMATE")])
    assert check.passed


def test_no_friendly_fire_fails_on_impostor_victim() -> None:
    check = check_no_friendly_fire_kills([_kill(0, tick=5, victim_role="IMPOSTOR")])
    assert not check.passed
    assert check.facts["friendly_fire_kills"] == 1


# --------------------------------------------------------------------------- #
# no_betrayal_ballots_or_accusations (§7.12 firewall; audit §1 hard row)       #
# --------------------------------------------------------------------------- #


def _first_multi_impostor_game(report: TournamentReport) -> GameReport:
    for game in report.games:
        impostors = {p for p, r in game.roles.items() if r == "IMPOSTOR"}
        if len(impostors) >= 2 and game.meetings:
            return game
    raise AssertionError("fixture set has no multi-impostor game with a meeting")


def test_betrayal_passes_on_committed(nine_report: TournamentReport) -> None:
    check = check_no_betrayal(nine_report)
    assert check.passed
    # Non-vacuous: 9p2i is multi-impostor, so ballots were actually inspected.
    assert int(check.facts["multi_impostor_ballots"]) > 0  # type: ignore[arg-type]


def test_betrayal_fails_on_impostor_voting_teammate(
    nine_report: TournamentReport,
) -> None:
    game = _first_multi_impostor_game(nine_report)
    impostors = sorted(pid for pid, role in game.roles.items() if role == "IMPOSTOR")
    meeting = next(m for m in game.meetings if m.ballots)
    bad_ballot = meeting.ballots[0].model_copy(
        update={"voter": impostors[0], "target": impostors[1]}
    )
    bad_meeting = meeting.model_copy(
        update={"ballots": (bad_ballot, *meeting.ballots[1:])}
    )
    bad_game = game.model_copy(
        update={
            "meetings": tuple(
                bad_meeting if m.meeting_id == meeting.meeting_id else m
                for m in game.meetings
            )
        }
    )
    bad_report = nine_report.model_copy(
        update={
            "games": tuple(
                bad_game if g.game_id == game.game_id else g for g in nine_report.games
            )
        }
    )
    check = check_no_betrayal(bad_report)
    assert not check.passed
    assert any("voted against teammate" in v for v in check.violations)


def test_betrayal_fails_on_impostor_accusing_teammate(
    nine_report: TournamentReport,
) -> None:
    game = _first_multi_impostor_game(nine_report)
    impostors = sorted(pid for pid, role in game.roles.items() if role == "IMPOSTOR")
    meeting = next(m for m in game.meetings if m.transcript.turns)
    turn = meeting.transcript.turns[0]
    betrayal = AccusationClaim(
        type="accusation",
        against=impostors[1],
        confidence=0.9,
        reason="synthetic betrayal",
    )
    bad_turn = turn.model_copy(update={"speaker": impostors[0], "claims": (betrayal,)})
    bad_transcript = meeting.transcript.model_copy(
        update={"turns": (bad_turn, *meeting.transcript.turns[1:])}
    )
    bad_meeting = meeting.model_copy(update={"transcript": bad_transcript})
    bad_game = game.model_copy(
        update={
            "meetings": tuple(
                bad_meeting if m.meeting_id == meeting.meeting_id else m
                for m in game.meetings
            )
        }
    )
    bad_report = nine_report.model_copy(
        update={
            "games": tuple(
                bad_game if g.game_id == game.game_id else g for g in nine_report.games
            )
        }
    )
    check = check_no_betrayal(bad_report)
    assert not check.passed
    assert any("accused teammate" in v for v in check.violations)


def test_betrayal_ignores_impostor_self_accusation_and_self_vote(
    nine_report: TournamentReport,
) -> None:
    # Task 15.7: an impostor accusing/voting ITSELF (against==speaker / target==voter)
    # betrays no FELLOW impostor, so the §7.12 firewall — which drops only OTHER
    # impostors (``meetings.manager`` fellow_impostor_ids excludes self, manager.py:496)
    # — leaves it clean. baseline-3's v5 prompts produced a few such self-accusations
    # (a Phase-16 dialogue finding); they must NOT trip this gate. Cross-teammate
    # betrayal (the tests above) still fails, so the refinement narrows, not weakens.
    game = _first_multi_impostor_game(nine_report)
    impostors = sorted(pid for pid, role in game.roles.items() if role == "IMPOSTOR")
    self_id = impostors[0]
    meeting = next(m for m in game.meetings if m.ballots and m.transcript.turns)
    self_ballot = meeting.ballots[0].model_copy(
        update={"voter": self_id, "target": self_id}
    )
    self_accusation = AccusationClaim(
        type="accusation",
        against=self_id,
        confidence=0.6,
        reason="synthetic self-accusation",
    )
    self_turn = meeting.transcript.turns[0].model_copy(
        update={"speaker": self_id, "claims": (self_accusation,)}
    )
    bad_meeting = meeting.model_copy(
        update={
            "ballots": (self_ballot, *meeting.ballots[1:]),
            "transcript": meeting.transcript.model_copy(
                update={"turns": (self_turn, *meeting.transcript.turns[1:])}
            ),
        }
    )
    bad_game = game.model_copy(
        update={
            "meetings": tuple(
                bad_meeting if m.meeting_id == meeting.meeting_id else m
                for m in game.meetings
            )
        }
    )
    report = nine_report.model_copy(
        update={
            "games": tuple(
                bad_game if g.game_id == game.game_id else g for g in nine_report.games
            )
        }
    )
    check = check_no_betrayal(report)
    assert check.passed
    assert not check.violations


def test_betrayal_vacuous_on_single_impostor(nine_report: TournamentReport) -> None:
    # 4p1i is single-impostor: no teammate exists, so the check is vacuously clean.
    four_report = assemble_tournament_report(_FOUR)
    check = check_no_betrayal(four_report)
    assert check.passed
    assert check.facts["multi_impostor_ballots"] == 0


# --------------------------------------------------------------------------- #
# 5. no_railroaded_crew_ejections                                            #
# --------------------------------------------------------------------------- #


def test_railroad_passes_on_committed(nine_report: TournamentReport) -> None:
    check = check_no_railroaded_crew_ejections(nine_report)
    assert check.passed
    # Non-vacuous: it actually read rendered crew suspicion rows.
    assert int(check.facts["rendered_crew_rows"]) > 0  # type: ignore[arg-type]


def _railroaded_meeting(
    base: MeetingReport, crew: str, *, trust_suffix: str = ", trust 0.0"
) -> MeetingReport:
    """A meeting whose vote prompt railroads ``crew`` at a clamped 1.0.

    ``trust_suffix`` selects the RENDERED ROW SHAPE: ``", trust 0.0"`` is every
    committed recording, ``""`` is what ``vote_ballot.qwen3_6_27b.v8`` writes
    after ruling D5 of 2026-09-19 dropped the dead trust column. The gate must
    catch the same railroad under both.
    """

    prompt = (
        "## Your suspicion of each player\n"
        f"- `{crew}`: suspicion 1.0{trust_suffix}\n"
        "## Next section\n"
    )
    call = LLMCallRecord(
        call_kind="meeting",
        model="Qwen/Qwen3.6-27B",
        prompt=prompt,
        response_text="{}",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
    )
    flags = tuple(
        ContradictionRef(
            contradiction_id=f"c-{i}",
            kind="alibi_conflict",
            event_a_id="a",
            event_b_id="b",
            subjects=(crew,),
            description="synthetic same-meeting flag",
        )
        for i in range(2)
    )
    return base.model_copy(update={"llm_calls": (call,), "contradictions": flags})


def test_railroad_fails_on_clamped_crew_row(nine_report: TournamentReport) -> None:
    game = _first_game_with_meeting(nine_report)
    crew = next(pid for pid, role in game.roles.items() if role == "CREWMATE")
    bad_meeting = _railroaded_meeting(game.meetings[0], crew)
    bad_game = game.model_copy(update={"meetings": (bad_meeting, *game.meetings[1:])})
    check = check_no_railroaded_crew_ejections(
        _replace_first_game(nine_report, bad_game)
    )
    assert not check.passed
    assert any(crew in v for v in check.violations)


@pytest.mark.parametrize("trust_suffix", [", trust 0.0", ""])
def test_railroad_reads_both_rendered_row_shapes(
    nine_report: TournamentReport, trust_suffix: str
) -> None:
    """The Task-14.12 tripwire fires on the pre-card AND the post-card row.

    ``_SUSPICION_GRAPH_ROW_RE`` is how this gate sees a rendered suspicion at
    all, and a pattern that still REQUIRED the ``, trust <N>`` suffix does not
    fail loudly on a v8 prompt -- it matches nothing, so ``_rendered_suspicions``
    returns ``[]``, no row clears :data:`CERTAIN_GUILT_SUSPICION`, and the check
    reports ``passed=True`` over a railroaded crew row. That is a gate going
    VACUOUS, which is worse than a gate going red, so both shapes are pinned
    here and the ``rendered_crew_rows`` fact is asserted non-zero for each: the
    first leg keeps the committed bytes honest, the second is what the
    re-record will write.
    """

    game = _first_game_with_meeting(nine_report)
    crew = next(pid for pid, role in game.roles.items() if role == "CREWMATE")
    bad_meeting = _railroaded_meeting(game.meetings[0], crew, trust_suffix=trust_suffix)
    bad_game = game.model_copy(update={"meetings": (bad_meeting, *game.meetings[1:])})
    check = check_no_railroaded_crew_ejections(
        _replace_first_game(nine_report, bad_game)
    )

    assert not check.passed
    assert any(crew in violation for violation in check.violations)
    assert int(check.facts["rendered_crew_rows"]) > 0  # type: ignore[arg-type]


def test_railroad_ignores_single_flag_certain_guilt(
    nine_report: TournamentReport,
) -> None:
    # A clamped 1.0 with only ONE same-meeting flag is the legitimate
    # across-meeting accumulator — NOT railroaded.
    game = _first_game_with_meeting(nine_report)
    crew = next(pid for pid, role in game.roles.items() if role == "CREWMATE")
    base = game.meetings[0]
    prompt = (
        "## Your suspicion of each player\n"
        f"- `{crew}`: suspicion 1.0, trust 0.0\n## Next\n"
    )
    call = LLMCallRecord(
        call_kind="meeting",
        model="m",
        prompt=prompt,
        response_text="{}",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
    )
    one_flag = (
        ContradictionRef(
            contradiction_id="c-0",
            kind="alibi_conflict",
            event_a_id="a",
            event_b_id="b",
            subjects=(crew,),
            description="single flag",
        ),
    )
    single = base.model_copy(update={"llm_calls": (call,), "contradictions": one_flag})
    bad_game = game.model_copy(update={"meetings": (single, *game.meetings[1:])})
    check = check_no_railroaded_crew_ejections(
        _replace_first_game(nine_report, bad_game)
    )
    assert check.passed


# --------------------------------------------------------------------------- #
# 6. no_dangling_primary_reason_id                                           #
# --------------------------------------------------------------------------- #


def test_dangling_passes_on_committed(nine_report: TournamentReport) -> None:
    check = check_no_dangling_primary_reason_id(nine_report)
    assert check.passed
    assert int(check.facts["ballots_total"]) > 0  # type: ignore[arg-type]


def test_dangling_fails_on_ghost_turn(nine_report: TournamentReport) -> None:
    game = _first_game_with_meeting(nine_report)
    meeting = game.meetings[0]
    ballot = meeting.ballots[0]
    bad_ballot = ballot.model_copy(update={"primary_reason_id": "ghost-turn-id"})
    bad_meeting = meeting.model_copy(
        update={"ballots": (bad_ballot, *meeting.ballots[1:])}
    )
    bad_game = game.model_copy(update={"meetings": (bad_meeting, *game.meetings[1:])})
    check = check_no_dangling_primary_reason_id(
        _replace_first_game(nine_report, bad_game)
    )
    assert not check.passed
    assert any("ghost-turn-id" in v for v in check.violations)


# --------------------------------------------------------------------------- #
# 7. cost_and_provenance_exact                                               #
# --------------------------------------------------------------------------- #


def _substrate_by_seed(sample_dir: Path) -> dict[int, dict[str, bool] | None]:
    from orchestrator.replay import read_substrate_flags

    return {
        seed: read_substrate_flags(sample_dir / f"replay-seed-{seed}.jsonl")
        for seed in seeds_on_disk(sample_dir)
    }


def test_provenance_passes_on_committed(nine_report: TournamentReport) -> None:
    check = check_cost_and_provenance(nine_report, _substrate_by_seed(_NINE))
    assert check.passed
    assert check.facts["model"] == "Qwen/Qwen3.6-27B"


def test_provenance_fails_on_wrong_substrate(nine_report: TournamentReport) -> None:
    stamps: dict[int, dict[str, bool] | None] = {
        seed: {"not_a_real_lever": True} for seed in seeds_on_disk(_NINE)
    }
    check = check_cost_and_provenance(nine_report, stamps)
    assert not check.passed
    assert any("substrate" in v for v in check.violations)


def test_provenance_fails_on_missing_stamp(nine_report: TournamentReport) -> None:
    stamps: dict[int, dict[str, bool] | None] = dict.fromkeys(
        seeds_on_disk(_NINE), None
    )
    check = check_cost_and_provenance(nine_report, stamps)
    assert not check.passed
    assert any("no substrate_flags" in v for v in check.violations)


def test_provenance_fails_on_multiple_models(nine_report: TournamentReport) -> None:
    game = nine_report.games[0]
    other = game.cost.model_copy(update={"by_model": {"SomeOtherModel": 0.0}})
    bad_game = game.model_copy(update={"cost": other})
    check = check_cost_and_provenance(
        _replace_first_game(nine_report, bad_game), _substrate_by_seed(_NINE)
    )
    assert not check.passed
    assert any("inconsistent model sets" in v for v in check.violations)


def test_provenance_fails_on_negative_per_call_tokens(
    nine_report: TournamentReport,
) -> None:
    # A corrupt per-call row can hide inside a still-positive game aggregate.
    game = _first_game_with_meeting(nine_report)
    meeting = game.meetings[0]
    bad_call = meeting.llm_calls[0].model_copy(update={"input_tokens": -1})
    bad_meeting = meeting.model_copy(
        update={"llm_calls": (bad_call, *meeting.llm_calls[1:])}
    )
    bad_game = game.model_copy(update={"meetings": (bad_meeting, *game.meetings[1:])})
    check = check_cost_and_provenance(
        _replace_first_game(nine_report, bad_game), _substrate_by_seed(_NINE)
    )
    assert not check.passed
    assert any("llm_call cost row" in v for v in check.violations)


def test_provenance_exact_model_pins(nine_report: TournamentReport) -> None:
    subs = _substrate_by_seed(_NINE)
    assert check_cost_and_provenance(
        nine_report, subs, expected_model="Qwen/Qwen3.6-27B"
    ).passed
    wrong = check_cost_and_provenance(nine_report, subs, expected_model="WrongModel")
    assert not wrong.passed
    assert any("expected" in v for v in wrong.violations)


def test_provenance_exact_prompt_versions_pin(nine_report: TournamentReport) -> None:
    subs = _substrate_by_seed(_NINE)
    game = _first_game_with_meeting(nine_report)
    real_versions = dict(game.prompt_versions)
    assert check_cost_and_provenance(
        nine_report, subs, expected_prompt_versions=real_versions
    ).passed
    wrong = check_cost_and_provenance(
        nine_report, subs, expected_prompt_versions={"accusation_round": "v0.wrong"}
    )
    assert not wrong.passed
    assert any("prompt-version provenance" in v for v in wrong.violations)


def test_provenance_fails_on_stripped_prompt_versions(
    nine_report: TournamentReport,
) -> None:
    # A game that called the model but carries NO prompt stamp is stripped
    # provenance — and an expected-pin over it must not vacuously pass.
    stripped = nine_report.model_copy(
        update={
            "games": tuple(
                g.model_copy(update={"prompt_versions": {}}) for g in nine_report.games
            )
        }
    )
    subs = _substrate_by_seed(_NINE)
    plain = check_cost_and_provenance(stripped, subs)
    assert not plain.passed
    assert any("stripped prompt provenance" in v for v in plain.violations)
    pinned = check_cost_and_provenance(
        stripped, subs, expected_prompt_versions={"accusation_round": "x"}
    )
    assert not pinned.passed
    assert any("records none" in v for v in pinned.violations)


def test_provenance_require_zero_cost(nine_report: TournamentReport) -> None:
    subs = _substrate_by_seed(_NINE)
    # The committed Featherless baseline is $0, so the pin passes.
    assert check_cost_and_provenance(nine_report, subs, require_zero_cost=True).passed
    # A game with positive spend fails the pin.
    game = nine_report.games[0]
    paid = game.cost.model_copy(update={"total_cost_usd": 1.5})
    bad_game = game.model_copy(update={"cost": paid})
    check = check_cost_and_provenance(
        _replace_first_game(nine_report, bad_game), subs, require_zero_cost=True
    )
    assert not check.passed
    assert any("--require-zero-cost" in v for v in check.violations)


# --------------------------------------------------------------------------- #
# 8. byte_identical_reconstruction                                           #
# --------------------------------------------------------------------------- #


def test_byte_identity_passes_on_committed() -> None:
    assert check_byte_identical_reconstruction(_NINE).passed


def test_byte_identity_fails_on_corrupted_hash(tmp_path: Path) -> None:
    mini = _mini_set(tmp_path, seeds=(0,))
    path = mini / "replay-seed-0.jsonl"
    lines = path.read_text().splitlines()
    out: list[str] = []
    flipped = False
    for line in lines:
        obj = json.loads(line)
        if (
            not flipped
            and obj.get("kind", "tick") == "tick"
            and obj.get("tick", -1) >= 1
        ):
            digest = obj["state_hash"]
            obj["state_hash"] = ("1" if digest[0] != "1" else "0") + digest[1:]
            flipped = True
            line = json.dumps(obj, sort_keys=True, separators=(",", ":"))
        out.append(line)
    path.write_text("\n".join(out) + "\n")
    check = check_byte_identical_reconstruction(mini)
    assert not check.passed
    assert check.facts["drifted_samples"] == 1


def test_byte_identity_reports_dropped_meeting_as_drift(tmp_path: Path) -> None:
    # A dropped meeting leaves later ticks that cannot be reconstructed. The
    # strict sample verifier reports that integrity failure without crashing.
    mini = _mini_set(tmp_path, seeds=(0,))
    path = mini / "replay-seed-0.jsonl"
    lines = path.read_text().splitlines()
    out: list[str] = []
    dropped = False
    for line in lines:
        obj = json.loads(line)
        if not dropped and obj.get("kind") == "meeting":
            dropped = True
            continue
        out.append(line)
    assert dropped
    path.write_text("\n".join(out) + "\n")
    check = check_byte_identical_reconstruction(mini)  # must not raise
    assert not check.passed
    assert check.facts == {"drifted_samples": 1}
    assert any("row_order" in violation for violation in check.violations)


def test_byte_identity_reports_verifier_crash_as_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def crash(sample_dir: Path) -> None:
        assert sample_dir == tmp_path
        raise RuntimeError("injected verifier crash")

    monkeypatch.setattr("eval.validity.verify_samples", crash)
    check = check_byte_identical_reconstruction(tmp_path)
    assert not check.passed
    assert check.facts == {"drifted_samples": -1, "raised": True}
    assert check.violations == ("RuntimeError: injected verifier crash",)


# --------------------------------------------------------------------------- #
# Reconstruction cross-check + loaders + full-gate reproduction               #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("seed", [0, 22])
def test_reconstruction_matches_win_condition_home(seed: int) -> None:
    # The one-walk reconstruction must agree with the tested win-condition home.
    num_players, num_impostors, tasks_per_crewmate = resolve_roster_knobs(_NINE)
    per_seed = roles_by_seed(
        _NINE,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    from engine.world import load_canonical_map

    game_map = load_canonical_map()
    recon = _reconstruct_game(
        _NINE / f"replay-seed-{seed}.jsonl",
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        roles=per_seed[seed],
        game_map=game_map,
    )
    home = check_replay_win_condition(
        _NINE / f"replay-seed-{seed}.jsonl",
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    assert recon.win_check == home


def test_resolve_roster_knobs() -> None:
    assert resolve_roster_knobs(_NINE) == (9, 2, 2)
    assert resolve_roster_knobs(_FOUR) == (4, 1, 1)


def test_seeds_on_disk() -> None:
    assert len(seeds_on_disk(_NINE)) == 50
    assert len(seeds_on_disk(_FOUR)) == 50


def test_seeds_on_disk_skips_an_audit_sidecar(tmp_path: Path) -> None:
    """The planted case: a ``<n>.audit`` stem is skipped, not parsed.

    A wrapper writes ``replay-seed-<n>.audit.jsonl`` beside the replay, and the
    glob matches it. Parsing that stem raised an uncaught ``ValueError`` and
    aborted the gate with a traceback instead of a report, so the guard is the
    difference between a report and a crash — not a tidier list.
    """

    (tmp_path / "replay-seed-7.jsonl").write_text("")
    (tmp_path / "replay-seed-11.jsonl").write_text("")

    assert seeds_on_disk(tmp_path) == [7, 11]

    (tmp_path / "replay-seed-7.audit.jsonl").write_text("")

    assert seeds_on_disk(tmp_path) == [7, 11]


def test_seeds_on_disk_still_raises_on_a_mistyped_replay(tmp_path: Path) -> None:
    """The OTHER half: the skip is one recognised shape, not any odd name.

    A mistyped ``replay-seed-7x.jsonl`` must not be quietly excluded — dropping
    it would let the gate report on the remaining games and call the set clean,
    which is worse than the crash the sidecar guard removed. Only the exact
    ``replay-seed-<n>.audit`` stem is skipped.
    """

    (tmp_path / "replay-seed-7.jsonl").write_text("")
    (tmp_path / "replay-seed-7x.jsonl").write_text("")

    with pytest.raises(ValueError, match="replay-seed-7x.jsonl"):
        seeds_on_disk(tmp_path)

    # And a near-miss on the sidecar shape is refused too.
    (tmp_path / "replay-seed-7x.jsonl").unlink()
    (tmp_path / "replay-seed-x.audit.jsonl").write_text("")

    with pytest.raises(ValueError, match="replay-seed-x.audit.jsonl"):
        seeds_on_disk(tmp_path)


def test_run_validity_gate_reproduces_9p2i_close() -> None:
    report = run_validity_gate(_NINE)
    assert report.passed
    assert report.games_total == 50
    assert report.failing_checks() == ()
    facts = {c.name: c.facts for c in report.checks}
    assert facts["meeting_rate_and_resolution"]["meeting_rate"] == 1.0
    assert facts["meeting_rate_and_resolution"]["resolved_meetings"] == 145  # was 151


def test_run_validity_gate_reproduces_4p1i_close() -> None:
    report = run_validity_gate(_FOUR)
    assert report.passed
    facts = {c.name: c.facts for c in report.checks}
    assert facts["meeting_rate_and_resolution"]["meeting_rate"] == 0.78  # was 0.8
    assert facts["meeting_rate_and_resolution"]["resolved_meetings"] == 39  # was 40


def test_run_validity_gate_rejects_a_truncated_replay(tmp_path: Path) -> None:
    # seed 12 ends `tick, tick, tick, game_over`, so dropping its last tick row
    # fails both the reconstructed-terminal check and the strict sample
    # verifier. The remaining validity checks stay green.
    mini = _mini_set(tmp_path, seeds=(12,))
    _truncate_tick_stream(mini / "replay-seed-12.jsonl")
    report = run_validity_gate(mini)
    assert not report.passed
    assert report.failing_checks() == (
        "all_games_reach_game_over",
        "byte_identical_reconstruction",
    )
    check = next(c for c in report.checks if c.name == "all_games_reach_game_over")
    assert any(TRUNCATED_REPLAY_REASON in v for v in check.violations)
    assert check.facts["games_reached_game_over"] == 0


def test_run_validity_gate_rejects_rows_after_the_terminal(tmp_path: Path) -> None:
    # The mirror corruption: the walk STOPS at GAME_OVER, so a row appended
    # after the terminal is never hash-verified and would ride along inside
    # "verified" bytes. The gate fails closed on it.
    mini = _mini_set(tmp_path, seeds=(12,))
    path = mini / "replay-seed-12.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    last_tick = json.loads(
        next(line for line in reversed(lines) if json.loads(line)["kind"] == "tick")
    )
    last_tick["tick"] += 1
    lines.append(json.dumps(last_tick, sort_keys=True, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = run_validity_gate(mini)
    assert not report.passed
    assert "all_games_reach_game_over" in report.failing_checks()
    check = next(c for c in report.checks if c.name == "all_games_reach_game_over")
    assert any("after the terminal GAME_OVER" in v for v in check.violations)


def test_run_validity_gate_rejects_a_record_after_the_game_over_row(
    tmp_path: Path,
) -> None:
    # A failed_call row appended after game_over: it names an already-resolved
    # meeting, carries zero cost, and claims a tick the walk never reaches, so
    # content checks read it as inert. Both the terminal-order check and the
    # strict sample verifier reject its physical placement.
    mini = _mini_set(tmp_path, seeds=(12,))
    path = mini / "replay-seed-12.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    meeting = next(
        json.loads(line) for line in lines if json.loads(line)["kind"] == "meeting"
    )
    appended = FailedCallReplayEntry(
        game_id=meeting["game_id"],
        meeting_id=meeting["meeting_id"],
        tick=999,
        model="Qwen/Qwen3.6-27B",
        prompt_length=0,
        raw_response="",
        error_type="ValidationError",
        error_message="planted",
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
    )
    lines.append(appended.model_dump_json())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report = run_validity_gate(mini)
    assert not report.passed
    assert report.failing_checks() == (
        "all_games_reach_game_over",
        "byte_identical_reconstruction",
    )
    check = next(c for c in report.checks if c.name == "all_games_reach_game_over")
    assert any("after the game_over row" in v for v in check.violations)


def test_run_validity_gate_passes_the_untruncated_fixture(tmp_path: Path) -> None:
    # The same one-game set, unedited: the truncation rejection above is not the
    # fixture merely being unacceptable to the gate.
    assert run_validity_gate(_mini_set(tmp_path, seeds=(12,))).passed


def test_run_validity_gate_never_crashes_on_corrupt_input(tmp_path: Path) -> None:
    # A doubled game_over row makes read_all_entries raise CorruptedFileError; the
    # gate must emit a failed report, not a traceback.
    mini = _mini_set(tmp_path, seeds=(0,))
    path = mini / "replay-seed-0.jsonl"
    go = next(
        line
        for line in path.read_text().splitlines()
        if json.loads(line).get("kind") == "game_over"
    )
    path.write_text(path.read_text() + go + "\n")
    report = run_validity_gate(mini)  # must not raise
    assert not report.passed
    assert "byte_identical_reconstruction" in report.failing_checks()
    # The report-based checks that could not read the corrupt file fail closed.
    unavailable = {
        c.name for c in report.checks if c.facts.get("input_available") is False
    }
    assert "meeting_rate_and_resolution" in unavailable


def test_gate_report_json_round_trips() -> None:
    report = run_validity_gate(_FOUR)
    text = report.model_dump_json()
    from eval.validity import ValidityGateReport

    back = ValidityGateReport.model_validate_json(text)
    assert back == report


def test_every_check_is_individually_reported() -> None:
    report = run_validity_gate(_FOUR)
    names = [check.name for check in report.checks]
    assert names == [
        "all_games_reach_game_over",
        "meeting_rate_and_resolution",
        "no_duplicate_meeting_rows",
        "no_tick_1_kills",
        "no_friendly_fire_kills",
        "no_betrayal_ballots_or_accusations",
        "no_railroaded_crew_ejections",
        "no_dangling_primary_reason_id",
        "cost_and_provenance_exact",
        "byte_identical_reconstruction",
    ]
    assert all(isinstance(check, ValidityCheck) for check in report.checks)


# --------------------------------------------------------------------------- #
# Experiment-stamped sets: the gate's and the report's walk profiles, and     #
# check 9's declarations                                                       #
# --------------------------------------------------------------------------- #

#: The declared test config: three arms that exist today, since the pending
#: guard refuses the wave's new values.
_TEST_CONFIG_JSON: Final[str] = (
    '{"format_version": 1, "meeting_reset": "hub_with_grace", '
    '"vent_exit_policy": "observed_risk", "bounded_rebuttal_version": 1}\n'
)
_TEST_CONFIG: Final[RecordedExperimentConfig] = (
    RecordedExperimentConfig.model_validate_json(_TEST_CONFIG_JSON)
)
#: Every other wave setting outside the engine layer at its ON value: the
#: round-one config of the decision memo, less the physical witness rule, which
#: joins once its card threads it through the engine-arguments helper.
_FULL_CONFIG_SETTINGS: Final[dict[str, object]] = {
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}
_FAKE_SEEDS: Final[tuple[int, ...]] = (0, 1, 2)
#: Seed 1 of the fake 4p/1i roster holds a meeting, so a regroup moves players.
_MEETING_SEED: Final[int] = 1
_FAKE_SHA: Final[str] = "abc1234"


def _scripts_on_path() -> None:
    scripts = _REPO_ROOT / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))


def _record_fake_set(
    directory: Path,
    *,
    seeds: Sequence[int],
    config: RecordedExperimentConfig | None,
) -> Path:
    """Fake-provider 4p/1i games recorded into ``directory`` as the recorder does.

    The replays, a roster descriptor and a MANIFEST whose rows all name
    :data:`_FAKE_SHA`; the observation sidecars are dropped, as the recorder's
    stage drops them.
    """

    _scripts_on_path()
    import _manifest_writer

    run_tournament_eval(
        seeds=seeds,
        output_dir=directory,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        experiment_config=config,
    )
    for audit in directory.glob("*.audit.jsonl"):
        audit.unlink()
    _manifest_writer.ensure_roster_descriptor(
        directory, num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    _manifest_writer.update_manifest(
        directory / "MANIFEST.md",
        directory,
        seeds,
        git_sha=_FAKE_SHA,
        refreshed_at="2026-09-26",
        model_override="fake-meeting",
    )
    return directory


@pytest.fixture(scope="module")
def arms_on_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Three fake games recorded on the test config, with roster and MANIFEST."""

    return _record_fake_set(
        tmp_path_factory.mktemp("arms-on") / "set",
        seeds=_FAKE_SEEDS,
        config=_TEST_CONFIG,
    )


def _copied(source: Path, tmp_path: Path) -> Path:
    return Path(shutil.copytree(source, tmp_path / "set"))


def _rewrite_configs(path: Path, update: Callable[[dict[str, object]], object]) -> None:
    """Apply ``update`` to the config on every tick row and on the footer."""

    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    stamped = 0
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            update(row["experiment_config"])
            stamped += 1
    assert stamped > 1
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _provenance(report: ValidityGateReport) -> ValidityCheck:
    return next(c for c in report.checks if c.name == "cost_and_provenance_exact")


def test_a_declared_arms_on_set_passes_the_whole_gate(arms_on_set: Path) -> None:
    """The profile reads every game with its hashes verified; check 9 agrees."""

    report = run_validity_gate(
        arms_on_set,
        expected_experiment_config=_TEST_CONFIG,
        expected_seeds=frozenset(_FAKE_SEEDS),
        require_one_recording_sha=True,
    )
    assert report.passed, report.failing_checks()
    games = assemble_tournament_report(arms_on_set).games
    assert {game.experiment_config for game in games} == {_TEST_CONFIG}


def test_an_arms_on_set_gated_with_no_declaration_fails_naming_its_config(
    arms_on_set: Path,
) -> None:
    report = run_validity_gate(arms_on_set)
    assert report.failing_checks() == ("cost_and_provenance_exact",)
    violations = _provenance(report).violations
    assert len(violations) == len(_FAKE_SEEDS)
    assert all(
        "meeting_reset='hub_with_grace'" in line
        and "bounded_rebuttal_version=1" in line
        and "(none: historical defaults)" in line
        for line in violations
    )


def test_a_set_mixing_two_configs_fails_naming_the_odd_game(
    arms_on_set: Path, tmp_path: Path
) -> None:
    mixed = _copied(arms_on_set, tmp_path)
    _rewrite_configs(
        mixed / "replay-seed-2.jsonl",
        lambda config: config.update(bounded_rebuttal_version=None),
    )
    report = run_validity_gate(mixed, expected_experiment_config=_TEST_CONFIG)
    assert report.failing_checks() == ("cost_and_provenance_exact",)
    (line,) = _provenance(report).violations
    recorded, declared = line.split(" differs from the declared config ")
    assert recorded.startswith("headless-seed-2: recorded experiment config")
    assert "bounded_rebuttal_version" not in recorded
    assert "bounded_rebuttal_version=1" in declared


def test_a_set_whose_seed_one_was_recorded_without_the_arm_fails(
    arms_on_set: Path, tmp_path: Path
) -> None:
    mixed = _copied(arms_on_set, tmp_path)
    bare = _record_fake_set(tmp_path / "bare", seeds=(1,), config=None)
    shutil.copy(bare / "replay-seed-1.jsonl", mixed / "replay-seed-1.jsonl")
    _scripts_on_path()
    import _manifest_writer

    _manifest_writer.update_manifest(
        mixed / "MANIFEST.md",
        mixed,
        (1,),
        git_sha=_FAKE_SHA,
        refreshed_at="2026-09-26",
        model_override="fake-meeting",
    )
    report = run_validity_gate(
        mixed,
        expected_experiment_config=_TEST_CONFIG,
        expected_seeds=frozenset(_FAKE_SEEDS),
        require_one_recording_sha=True,
    )
    assert "cost_and_provenance_exact" in report.failing_checks()
    (line,) = _provenance(report).violations
    assert line.startswith(
        "headless-seed-1: recorded experiment config (none: historical defaults)"
    )


def test_one_foreign_recording_sha_fails_only_under_the_sha_flag(
    arms_on_set: Path, tmp_path: Path
) -> None:
    foreign = _copied(arms_on_set, tmp_path)
    manifest = foreign / "MANIFEST.md"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    edited = [
        line.replace(f"| {_FAKE_SHA} |", "| def5678 |")
        if line.startswith("| 2 |")
        else line
        for line in lines
    ]
    assert edited != lines
    manifest.write_text("\n".join(edited) + "\n", encoding="utf-8")

    flagged = run_validity_gate(
        foreign,
        expected_experiment_config=_TEST_CONFIG,
        require_one_recording_sha=True,
    )
    assert flagged.failing_checks() == ("cost_and_provenance_exact",)
    assert _provenance(flagged).violations == (
        f"MANIFEST.md names 2 recording shas ({_FAKE_SHA}, def5678); one is required",
    )
    assert run_validity_gate(foreign, expected_experiment_config=_TEST_CONFIG).passed


def test_a_removed_seed_fails_only_under_the_seed_flag(
    arms_on_set: Path, tmp_path: Path
) -> None:
    short = _copied(arms_on_set, tmp_path)
    (short / "replay-seed-2.jsonl").unlink()
    _scripts_on_path()
    import _manifest_writer

    assert _manifest_writer.prune_manifest(short / "MANIFEST.md", short) == 1

    flagged = run_validity_gate(
        short,
        expected_experiment_config=_TEST_CONFIG,
        expected_seeds=frozenset(_FAKE_SEEDS),
    )
    assert "cost_and_provenance_exact" in flagged.failing_checks()
    assert _provenance(flagged).violations == (
        "the replay files do not hold exactly the declared seeds: missing [2], "
        "unexpected []",
        "the MANIFEST.md rows do not hold exactly the declared seeds: missing [2], "
        "unexpected []",
    )
    unflagged = run_validity_gate(short, expected_experiment_config=_TEST_CONFIG)
    assert _provenance(unflagged).passed


def test_the_seed_and_sha_declarations_read_each_inventory_part() -> None:
    """Planted inventories: no MANIFEST, a row without a sha, a stray replay."""

    none = SetInventory(
        replay_seeds=frozenset({0, 1}), manifest_seeds=None, manifest_shas=()
    )
    assert seed_set_violations(none, frozenset({0, 1})) == [
        "the declared seeds are checked against MANIFEST.md rows, but the "
        "directory has no MANIFEST.md"
    ]
    assert recording_sha_violations(none) == [
        "one recording sha is required, but the directory has no MANIFEST.md"
    ]
    unnamed = SetInventory(
        replay_seeds=frozenset({0, 1}),
        manifest_seeds=frozenset({0, 1}),
        manifest_shas=((0, _FAKE_SHA),),
    )
    assert recording_sha_violations(unnamed) == [
        "MANIFEST.md rows for seeds [1] name no recording sha"
    ]
    stray = SetInventory(
        replay_seeds=frozenset({0, 1, 7}),
        manifest_seeds=frozenset({0, 1}),
        manifest_shas=((0, _FAKE_SHA), (1, _FAKE_SHA)),
    )
    assert seed_set_violations(stray, frozenset({0, 1})) == [
        "the replay files do not hold exactly the declared seeds: missing [], "
        "unexpected [7]"
    ]
    assert recording_sha_violations(stray) == []
    with pytest.raises(ValueError, match="at least one seed"):
        seed_set_violations(stray, frozenset())


def test_the_inventory_reads_the_replay_files_and_the_manifest(
    arms_on_set: Path,
) -> None:
    assert read_set_inventory(arms_on_set) == SetInventory(
        replay_seeds=frozenset(_FAKE_SEEDS),
        manifest_seeds=frozenset(_FAKE_SEEDS),
        manifest_shas=tuple((seed, _FAKE_SHA) for seed in _FAKE_SEEDS),
    )


def test_the_opt_in_declarations_need_the_inventory(
    nine_report: TournamentReport,
) -> None:
    with pytest.raises(ValueError, match="inventory"):
        check_cost_and_provenance(
            nine_report, _substrate_by_seed(_NINE), expected_seeds=frozenset({0})
        )
    with pytest.raises(ValueError, match="inventory"):
        check_cost_and_provenance(
            nine_report, _substrate_by_seed(_NINE), require_one_recording_sha=True
        )


def test_the_committed_sample_sets_satisfy_every_declaration_with_no_config(
    nine_report: TournamentReport,
) -> None:
    """The historical default holds on every committed sample game."""

    for sample_dir in (_NINE, _FOUR):
        inventory = read_set_inventory(sample_dir)
        assert recording_sha_violations(inventory) == []
        assert seed_set_violations(inventory, frozenset(range(50))) == []
    assert experiment_config_violations(nine_report.games, None) == []


def _gate_cli() -> ModuleType:
    _scripts_on_path()
    import validity_gate

    return validity_gate


def test_an_unknown_field_in_the_declared_file_is_a_usage_error(
    arms_on_set: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    declared = tmp_path / "config.json"
    declared.write_text('{"format_version": 1, "hidden_travel": "on"}\n')
    with pytest.raises(SystemExit) as exited:
        _gate_cli().main(
            [str(arms_on_set), "--expected-experiment-config", str(declared)]
        )
    assert exited.value.code == 2
    assert "hidden_travel" in capsys.readouterr().err
    good = tmp_path / "good.json"
    good.write_text(_TEST_CONFIG_JSON)
    arguments = [
        str(arms_on_set),
        "--expected-experiment-config",
        str(good),
        "--expected-seeds",
        "0-2",
        "--require-one-recording-sha",
    ]
    assert _gate_cli().main(arguments) == 0
    assert _gate_cli().main([*arguments[:-3], "--expected-seeds", "0-3"]) == 1


@pytest.mark.parametrize(
    ("raw", "seeds"),
    [
        ("0-49", frozenset(range(50))),
        ("3", frozenset({3})),
        ("0, 2,5", frozenset({0, 2, 5})),
    ],
)
def test_the_seed_flag_reads_a_range_or_a_list(raw: str, seeds: frozenset[int]) -> None:
    assert _gate_cli()._parse_seed_set(raw) == seeds


@pytest.mark.parametrize("raw", ["5-2", "a-b", "1,,2", "-1", "1-", ""])
def test_the_seed_flag_refuses_a_malformed_value(raw: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        _gate_cli()._parse_seed_set(raw)


#: The three profiles, each run below through the entry point its consumers call.
_PROFILES: Final[dict[str, tuple[ModuleType, str]]] = {
    "validity-gate": (validity, "_WALK_CONFIG"),
    "kill-gift": (balance_eval, "_KILL_GIFT_WALK_CONFIG"),
    "current-report": (balance_eval, "_CURRENT_REPORT_WALK_CONFIG"),
}


def _walk_with(profile: str, path: Path, seed: int) -> object:
    """``path`` read by ``profile``'s consumer, as that consumer calls the walk."""

    game_map = load_canonical_map()
    roles = roles_by_seed(
        path.parent,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=game_map,
    )[seed]
    if profile == "validity-gate":
        return _reconstruct_game(
            path,
            seed=seed,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            roles=roles,
            game_map=game_map,
        )
    if profile == "kill-gift":
        return balance_eval._kill_gift_accounting(
            path, seed=seed, roles=roles, tasks_per_crewmate=1, game_map=game_map
        )
    return balance_eval._current_replay_facts(
        path, seed=seed, roles=roles, tasks_per_crewmate=1, game_map=game_map
    )


def _one_game(source: Path, tmp_path: Path, name: str) -> Path:
    directory = tmp_path / name
    directory.mkdir()
    return Path(shutil.copy(source / f"replay-seed-{_MEETING_SEED}.jsonl", directory))


def _counted_advances(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    """Count the walk's engine advances, to see a refusal land before the first."""

    calls: list[int] = []
    real = advance_tick

    def counting(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(replay_walk, "advance_tick", counting)
    return calls


def _open_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))


def test_the_full_config_copy_sets_a_later_value_in_every_declarable_layer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_pending(monkeypatch)
    full = RecordedExperimentConfig.model_validate(
        {**_TEST_CONFIG.model_dump(), **_FULL_CONFIG_SETTINGS}
    )
    layers = {FIELD_LAYER[field] for field, _value in wave_settings(full)}
    assert layers == {"orchestrator", "tactical", "meeting"}


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_each_profile_declares_every_layer_after_its_review(profile: str) -> None:
    module, name = _PROFILES[profile]
    config = getattr(module, name)
    assert config.profile == profile
    assert config.supports_experiments
    declared = {
        "validity-gate": VALIDITY_THREADED_LAYERS,
        "kill-gift": balance_eval.KILL_GIFT_THREADED_LAYERS,
        "current-report": balance_eval.CURRENT_REPORT_THREADED_LAYERS,
    }[profile]
    assert config.threaded_layers == declared == {"orchestrator", "tactical", "meeting"}


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_each_profile_reads_the_full_config_copy_with_every_hash_verified(
    profile: str,
    arms_on_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_pending(monkeypatch)
    plain = _one_game(arms_on_set, tmp_path, "plain")
    full = _one_game(arms_on_set, tmp_path, "full")
    _rewrite_configs(full, lambda config: config.update(_FULL_CONFIG_SETTINGS))
    advances = _counted_advances(monkeypatch)
    assert _walk_with(profile, full, _MEETING_SEED) == _walk_with(
        profile, plain, _MEETING_SEED
    )
    assert advances


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_without_its_declaration_a_profile_refuses_the_full_config_copy(
    profile: str,
    arms_on_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_pending(monkeypatch)
    full = _one_game(arms_on_set, tmp_path, "full")
    _rewrite_configs(full, lambda config: config.update(_FULL_CONFIG_SETTINGS))
    module, name = _PROFILES[profile]
    monkeypatch.setattr(
        module, name, replace(getattr(module, name), threaded_layers=frozenset())
    )
    advances = _counted_advances(monkeypatch)
    with pytest.raises(ValueError, match=f"replay profile '{profile}' does not read"):
        _walk_with(profile, full, _MEETING_SEED)
    assert advances == []


class _StandIn(RecordedExperimentConfig):
    """The config model with one field no reader has reviewed."""

    stand_in_rule: Literal["old", "new"] = "old"


@pytest.mark.parametrize("profile", sorted(_PROFILES))
@pytest.mark.parametrize("layer", ["engine", "orchestrator", "tactical", "meeting"])
def test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing(
    profile: str,
    layer: ConfigLayer,
    arms_on_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a field added to the config model and to the layer table.

    An engine-layer stand-in is refused by the engine-arguments helper, which no
    profile can declare past. A stand-in in a declarable layer is read by the
    profile as declared, and refused by the same profile with that one layer
    removed, so the refusal comes from the declaration.
    """

    path = _one_game(arms_on_set, tmp_path, "game")
    stand_in = _StandIn.model_validate(
        {**_TEST_CONFIG.model_dump(), "stand_in_rule": "new"}
    )
    layers = MappingProxyType({**FIELD_LAYER, "stand_in_rule": layer})
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", layers)
    monkeypatch.setattr(replay_walk, "FIELD_LAYER", layers)
    monkeypatch.setattr(
        replay_walk, "recorded_experiment_config", lambda _entries: stand_in
    )
    module, name = _PROFILES[profile]
    declared = getattr(module, name)
    advances = _counted_advances(monkeypatch)
    if layer != "engine":
        _walk_with(profile, path, _MEETING_SEED)
        assert advances
        advances.clear()
        monkeypatch.setattr(
            module,
            name,
            replace(declared, threaded_layers=declared.threaded_layers - {layer}),
        )
    with pytest.raises(ValueError, match="stand_in_rule='new'"):
        _walk_with(profile, path, _MEETING_SEED)
    assert advances == []


@pytest.mark.parametrize("profile", sorted(_PROFILES))
def test_each_profile_resimulates_the_recorded_meeting_reset(
    profile: str,
    arms_on_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the reset stripped from every row fails the meeting post-hash.

    The stripped copy reads as ``preserve``, while its hashes were recorded
    under the regroup, so a profile that takes the reset from the recording
    reads the unedited game and fails the edited one at its meeting.
    """

    stripped = _one_game(arms_on_set, tmp_path, "stripped")
    _rewrite_configs(stripped, lambda config: config.pop("meeting_reset"))
    meeting_tick = next(
        json.loads(line)["tick"]
        for line in stripped.read_text(encoding="utf-8").splitlines()
        if json.loads(line)["kind"] == "meeting"
    )
    seen: list[tuple[str, int | None]] = []
    real = replay_walk._violate

    def spy(config: ReplayWalkConfig, violation: WalkViolation) -> NoReturn:
        seen.append((violation.kind, violation.tick))
        real(config, violation)

    monkeypatch.setattr(replay_walk, "_violate", spy)
    with pytest.raises((ValueError, ReplayIntegrityError)):
        _walk_with(profile, stripped, _MEETING_SEED)
    assert seen == [("meeting_post_hash_mismatch", meeting_tick)]
    seen.clear()
    _walk_with(profile, _one_game(arms_on_set, tmp_path, "kept"), _MEETING_SEED)
    assert seen == []


@pytest.mark.parametrize("profile", ["validity-gate", "kill-gift"])
def test_validity_and_kill_gift_still_refuse_temporal_observations(
    profile: str,
    arms_on_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = _one_game(arms_on_set, tmp_path, "game")
    monkeypatch.setattr(
        replay_walk, "recorded_temporal_observation_version", lambda _entries: 2
    )
    with pytest.raises(ValueError, match="does not support temporal observations"):
        _walk_with(profile, path, _MEETING_SEED)
    # The report profile reads them, so the plant is what the two refuse.
    _walk_with("current-report", path, _MEETING_SEED)
