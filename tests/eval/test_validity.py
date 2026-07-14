"""Unit tests for eval/validity.py (Task 15.1).

Covers each of the eight gate checks with a PASS input and a synthetic VIOLATION
that flips ``passed`` to ``False`` (a gate that cannot fail is not a gate), the
reconstruction cross-check against the tested win-condition home, and the
baseline-4 reproduction of ``run_validity_gate`` over the committed sets.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Sequence
from pathlib import Path

import pytest

from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.validity import (
    ValidityCheck,
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
    resolve_roster_knobs,
    roles_by_seed,
    run_validity_gate,
    seeds_on_disk,
)
from eval.win_condition_selfcheck import (
    WinConditionSelfCheck,
    check_replay_win_condition,
)
from meetings.schemas import AccusationClaim, ContradictionRef
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord

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
) -> WinConditionSelfCheck:
    return WinConditionSelfCheck(
        game_id=f"headless-seed-{seed}",
        seed=seed,
        winner="CREWMATES",
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
    assert check.facts["resolved_meetings"] == 179


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
    assert int(check.facts["meetings_total"]) == 179  # type: ignore[arg-type]


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


def _railroaded_meeting(base: MeetingReport, crew: str) -> MeetingReport:
    prompt = (
        "## Your suspicion of each player\n"
        f"- `{crew}`: suspicion 1.0, trust 0.0\n"
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


def test_byte_identity_reports_verifier_crash_as_failure(tmp_path: Path) -> None:
    # A replay malformed so the verifier RAISES (a dropped meeting row a later
    # tick still references) is reported as a failed check, not a crash.
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
    path.write_text("\n".join(out) + "\n")
    check = check_byte_identical_reconstruction(mini)  # must not raise
    assert not check.passed
    assert check.facts["raised"] is True


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


def test_run_validity_gate_reproduces_9p2i_close() -> None:
    report = run_validity_gate(_NINE)
    assert report.passed
    assert report.games_total == 50
    assert report.failing_checks() == ()
    facts = {c.name: c.facts for c in report.checks}
    assert facts["meeting_rate_and_resolution"]["meeting_rate"] == 1.0
    assert facts["meeting_rate_and_resolution"]["resolved_meetings"] == 179


def test_run_validity_gate_reproduces_4p1i_close() -> None:
    report = run_validity_gate(_FOUR)
    assert report.passed
    facts = {c.name: c.facts for c in report.checks}
    assert facts["meeting_rate_and_resolution"]["meeting_rate"] == 0.78
    assert facts["meeting_rate_and_resolution"]["resolved_meetings"] == 39


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
