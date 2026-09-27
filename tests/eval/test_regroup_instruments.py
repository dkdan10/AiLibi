"""The instruments that read a regroup recording, and the ones that still refuse.

Under ``meeting_reset = "hub_with_grace"`` the frame play resumes from is the
regrouped one, so every instrument that tables engine rooms by tick must read a
meeting tick's rooms off the applied meeting (``MeetingApplied.state``), which
keeps every room without a regroup:

* the process scorecard's route table (row 3's claim truth);
* evidence honesty's ``room_at`` table and its clock alignment, which lifts the
  refusal the readers card left pending for this card.

The funnel's memory walk reads each meeting's public regroup ticks for its belief
fold and its pooling folds. The sample report's inform band
(``eval.meeting_quality``) and the V&J pre-vote graphs (``eval.vj_instruments``)
read the same window. The scorecard's walk profile declares the layers it
reads and refuses every other one before its first advance. The offline lever
counterfactual keeps refusing every recorded setting, and the frozen deception
instruments and the phase-21 counterfactual refuse the reset by name before their
walk.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal

import pytest

import eval.evidence_honesty as honesty_module
import eval.meeting_quality as meeting_quality
import eval.process_scorecard as scorecard
import eval.replay_walk as walk_module
from agents.memory.beliefs import ABSENCE_SUSPICION_DELTA, ACCUSATION_SUSPICION_DELTA
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval import funnel
from eval.evidence_honesty import (
    HONESTY_READS,
    EvidenceHonestyReconstructionError,
    compute_evidence_honesty,
)
from eval.meeting_quality import (
    CHANNEL_BODY_PROXIMITY,
    CHANNEL_SINGLE_WITNESS_INFORM,
    compute_multi_signal_conversion,
    decompose_ejection_channels,
)
from eval.recorded_settings import READABLE_SETTINGS
from eval.replay_walk import MeetingApplied, TickAdvanced, walk_replay
from eval.report_schema import GameReport
from eval.validity import assemble_tournament_report
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    ConfigLayer,
    RecordedExperimentConfig,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from tests._helpers.scripted_meeting import record_game
from tests.orchestrator.test_meeting_reset_coherence import (
    RESET,
    SEED,
    _Live,
    _record_live,
)

_ROSTER: Final[dict[str, int]] = {
    "num_players": 9,
    "num_impostors": 2,
    "tasks_per_crewmate": 2,
}


@pytest.fixture(scope="module")
def reset_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("reset") / "9p2i"
    record_game(directory, seed=SEED, config=RESET)
    return directory


@pytest.fixture(scope="module")
def preserve_set(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("preserve") / "9p2i"
    record_game(directory, seed=SEED, config=None)
    return directory


def _path(directory: Path) -> Path:
    return directory / f"replay-seed-{SEED}.jsonl"


def _meetings(directory: Path) -> list[MeetingReplayEntry]:
    return [
        row
        for row in read_all_entries(_path(directory))
        if isinstance(row, MeetingReplayEntry)
    ]


def _frames(
    directory: Path,
) -> tuple[dict[int, dict[str, str]], dict[int, dict[str, str]]]:
    """Each tick's post-advance rooms, and each meeting's applied rooms."""

    advanced: dict[int, dict[str, str]] = {}
    applied: dict[int, dict[str, str]] = {}
    for event in walk_replay(
        _path(directory),
        seed=SEED,
        game_map=load_canonical_map(),
        config=honesty_module._WALK_CONFIG,
        **_ROSTER,
    ):
        if isinstance(event, TickAdvanced):
            advanced[event.entry.tick] = {
                pid: p.room for pid, p in event.state.players.items()
            }
        elif isinstance(event, MeetingApplied):
            applied[event.entry.tick] = {
                pid: p.room for pid, p in event.state.players.items()
            }
    return advanced, applied


# --------------------------------------------------------------------------- #
# The scorecard's route table                                                 #
# --------------------------------------------------------------------------- #


def _routes(directory: Path) -> Any:
    return scorecard.walk_routes(directory, game_map=load_canonical_map(), **_ROSTER)[
        SEED
    ]


def _moved_by_the_regroup(directory: Path) -> tuple[int, str]:
    """The first meeting's tick and a survivor the regroup moved."""

    tick = _meetings(directory)[0].tick
    advanced, applied = _frames(directory)
    room = load_canonical_map().meeting.room
    mover = next(
        pid
        for pid, before in sorted(advanced[tick].items())
        if before != room and applied[tick][pid] == room
    )
    return tick, mover


def _resume_claim(subject: str, tick: int) -> AlibiClaim:
    room = load_canonical_map().meeting.room
    return AlibiClaim(
        type="alibi",
        subject=subject,
        route=(AlibiSegment(room=room, from_tick=tick + 1, to_tick=tick + 1),),
    )


def test_a_resume_tick_self_claim_naming_the_meeting_room_scores_true(
    reset_set: Path,
) -> None:
    tick, mover = _moved_by_the_regroup(reset_set)
    claim = _resume_claim(mover, tick)
    assert scorecard._claim_truth(claim, mover, _routes(reset_set)) == (True, True)


class _NeverYielded:
    """A walk event type the walk never yields: the pre-card route table."""


def test_without_the_applied_meeting_the_same_claim_scores_false(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tick, mover = _moved_by_the_regroup(reset_set)
    monkeypatch.setattr(scorecard, "MeetingApplied", _NeverYielded)
    claim = _resume_claim(mover, tick)
    assert scorecard._claim_truth(claim, mover, _routes(reset_set)) == (False, False)


def test_without_a_regroup_the_applied_meeting_keeps_every_room(
    preserve_set: Path,
) -> None:
    advanced, applied = _frames(preserve_set)
    assert applied
    for tick, rooms in applied.items():
        assert rooms == advanced[tick]
    routes = _routes(preserve_set)
    for tick in applied:
        assert routes[tick] == advanced[tick]


# --------------------------------------------------------------------------- #
# Evidence honesty                                                            #
# --------------------------------------------------------------------------- #


def test_honesty_walks_a_reset_recording_and_checks_its_regrouped_clock(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    checked: list[int] = []
    real = honesty_module._assert_clock_alignment

    def _spy(**kwargs: Any) -> None:
        real(**kwargs)
        checked.append(kwargs["tallies"].clock_checked)

    monkeypatch.setattr(honesty_module, "_assert_clock_alignment", _spy)
    assert compute_evidence_honesty(reset_set) is not None
    assert checked and checked[-1] > 0


def test_with_the_pre_regroup_room_table_the_clock_alignment_raises(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The table honesty kept before this card: every meeting tick's row is the
    # frame the trigger tick's actions resolved in, never the regrouped one.
    real = honesty_module._assert_clock_alignment

    def _pre_card(**kwargs: Any) -> None:
        real(**{**kwargs, "room_at": kwargs["resolved_at"]})

    monkeypatch.setattr(honesty_module, "_assert_clock_alignment", _pre_card)
    with pytest.raises(EvidenceHonestyReconstructionError, match="agent clock moved"):
        compute_evidence_honesty(reset_set)


def test_honesty_reads_every_readable_setting_now() -> None:
    assert HONESTY_READS == READABLE_SETTINGS
    assert "meeting_reset" in HONESTY_READS


def _copy_with(source: Path, target: Path, **settings: object) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    for name in ("roster.json", "MANIFEST.md"):
        shutil.copy(source / name, target / name)
    rows = [json.loads(line) for line in _path(source).read_text().splitlines()]
    for row in rows:
        if row.get("kind") in ("tick", "game_over"):
            config = row.get("experiment_config") or {"format_version": 1}
            config.update(settings)
            row["experiment_config"] = config
    _path(target).write_text("".join(json.dumps(row) + "\n" for row in rows))
    return target


#: Every recorded setting the readers card refused in honesty besides the reset,
#: each beside the reset, which honesty now reads.
_STILL_REFUSED: Final[tuple[tuple[str, object], ...]] = (
    ("crew_idle_policy", "patrol"),
    ("crew_idle_policy", "accompany"),
    ("post_meeting_retarget", True),
    ("self_report", True),
    ("sabotage_threshold", "two_thirds"),
    ("evidence_reasoning_version", 1),
    ("format_version", 2),
)


@pytest.mark.parametrize(("setting", "value"), _STILL_REFUSED)
def test_every_other_setting_the_readers_refused_is_still_refused(
    reset_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    setting: str,
    value: object,
) -> None:
    copy = _copy_with(reset_set, tmp_path / "9p2i", **{setting: value})
    advances: list[int] = []

    def _counting(*args: Any, **kwargs: Any) -> Any:
        advances.append(1)
        return advance_tick(*args, **kwargs)

    monkeypatch.setattr(walk_module, "advance_tick", _counting)
    with pytest.raises(ValueError) as refused:
        compute_evidence_honesty(copy)
    assert setting in str(refused.value)
    assert advances == []


def test_the_offline_lever_counterfactual_keeps_refusing_the_reset(
    reset_set: Path,
) -> None:
    import sys

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import counterfactual_phase20

    with pytest.raises(ValueError, match="meeting_reset='hub_with_grace'"):
        counterfactual_phase20.walk_set(reset_set, set_name="reset/9p2i")


# --------------------------------------------------------------------------- #
# The funnel's memory walk                                                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def vouching_game(tmp_path_factory: pytest.TempPathFactory) -> _Live:
    return _record_live(tmp_path_factory.mktemp("vouching") / "9p2i")


def _vj_walk(live: _Live) -> Any:
    game_map = load_canonical_map()
    initial = seed_initial_state(seed=SEED, game_map=game_map, **_ROSTER)
    return funnel._walk_game_vj(
        live.path,
        seed=SEED,
        roles={pid: p.role for pid, p in initial.players.items()},
        game_map=game_map,
        **_ROSTER,
    )


def test_the_funnel_walk_carries_each_meetings_regroup_ticks(
    vouching_game: _Live,
) -> None:
    walked = _vj_walk(vouching_game)
    assert [m.regroup_ticks for m in walked.meetings] == [
        opening.regroup_ticks for opening in vouching_game.openings
    ]


def test_the_funnel_belief_fold_reads_the_window(
    vouching_game: _Live, monkeypatch: pytest.MonkeyPatch
) -> None:
    windowed = [m.suspicion_graph_by_voter for m in _vj_walk(vouching_game).meetings]
    monkeypatch.setattr(
        walk_module, "derive_regroup_ticks", lambda *a, **k: frozenset()
    )
    plain = [m.suspicion_graph_by_voter for m in _vj_walk(vouching_game).meetings]
    # The vouch in the second meeting sits on the first regroup's tick: it
    # exculpates nobody in the window, so the third meeting's graphs differ.
    assert windowed[:2] == plain[:2]
    assert windowed[2] != plain[2]


def test_the_pooling_folds_read_the_window(vouching_game: _Live) -> None:
    meeting = _vj_walk(vouching_game).meetings[1]
    assert meeting.regroup_ticks
    opener = meeting.triggered_by
    plain = replace(meeting, regroup_ticks=frozenset())
    assert opener not in funnel._grounded_vouch_set(meeting)
    assert opener in funnel._grounded_vouch_set(plain)
    assert opener in funnel._absence_set(meeting)
    assert opener not in funnel._absence_set(plain)


# --------------------------------------------------------------------------- #
# The scorecard's walk profile declares its layers                            #
# --------------------------------------------------------------------------- #

#: Every wave setting at its ON value beside the reset: the round-one config.
_FULL_CONFIG_SETTINGS: Final[dict[str, object]] = {
    "meeting_reset": "hub_with_grace",
    "vent_witness_rule": "physical",
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "bounded_rebuttal_version": 1,
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}


def _counted(monkeypatch: pytest.MonkeyPatch) -> list[int]:
    calls: list[int] = []

    def _counting(*args: Any, **kwargs: Any) -> Any:
        calls.append(1)
        return advance_tick(*args, **kwargs)

    monkeypatch.setattr(walk_module, "advance_tick", _counting)
    return calls


def test_the_profile_declares_the_layers_the_route_reads() -> None:
    config = scorecard._walk_config()
    assert config.profile == "process-scorecard"
    assert (
        config.threaded_layers
        == scorecard.SCORECARD_THREADED_LAYERS
        == frozenset({"orchestrator", "tactical", "meeting"})
    )


def test_the_profile_reads_the_full_config_copy_with_every_hash_verified(
    reset_set: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    full = _copy_with(reset_set, tmp_path / "full" / "9p2i", **_FULL_CONFIG_SETTINGS)
    advances = _counted(monkeypatch)
    assert _routes(full) == _routes(reset_set)
    assert advances


def test_without_its_declaration_the_profile_refuses_the_full_config_copy(
    reset_set: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    full = _copy_with(reset_set, tmp_path / "full" / "9p2i", **_FULL_CONFIG_SETTINGS)
    real = scorecard._walk_config
    monkeypatch.setattr(
        scorecard,
        "_walk_config",
        lambda: replace(real(), threaded_layers=frozenset()),
    )
    advances = _counted(monkeypatch)
    with pytest.raises(
        ValueError, match="replay profile 'process-scorecard' does not read"
    ):
        _routes(full)
    assert advances == []


class _StandIn(RecordedExperimentConfig):
    """The config model with one field no reader has reviewed."""

    stand_in_rule: Literal["old", "new"] = "old"


@pytest.mark.parametrize("layer", ["orchestrator", "tactical", "meeting"])
def test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch, layer: ConfigLayer
) -> None:
    stand_in = _StandIn.model_validate({**RESET.model_dump(), "stand_in_rule": "new"})
    layers = MappingProxyType({**FIELD_LAYER, "stand_in_rule": layer})
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", layers)
    monkeypatch.setattr(walk_module, "FIELD_LAYER", layers)
    monkeypatch.setattr(walk_module, "recorded_experiment_config", lambda _e: stand_in)
    advances = _counted(monkeypatch)
    # Declared: read. The same layer undeclared: refused, by name, before the
    # first advance.
    _routes(reset_set)
    assert advances
    advances.clear()
    real = scorecard._walk_config
    monkeypatch.setattr(
        scorecard,
        "_walk_config",
        lambda: replace(real(), threaded_layers=real().threaded_layers - {layer}),
    )
    with pytest.raises(ValueError, match="stand_in_rule='new'"):
        _routes(reset_set)
    assert advances == []


# --------------------------------------------------------------------------- #
# The clock alignment, on planted tables                                      #
# --------------------------------------------------------------------------- #


def _row(tick: int, subject: str, room: str, action: str | None) -> Any:
    from agents.memory.episodic import EpisodicEvent

    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": subject, "room": room, "action": action},
        provenance="observed",
        observation_id=f"p-1:{tick}:{subject}",
    )


def _regroup_tables() -> tuple[dict[int, dict[str, str]], dict[int, dict[str, str]]]:
    """A meeting at tick 11: ``p-4`` vented ADMIN to MEDBAY on it, then the regroup.

    ``room_at`` holds the regrouped frame at 11, ``resolved_at`` the frame tick
    11's actions resolved in.
    """

    room_at = {
        10: {"p-4": "ADMIN", "p-5": "LABS"},
        11: {"p-4": "CAFETERIA", "p-5": "CAFETERIA"},
        12: {"p-4": "UPPER_HALL", "p-5": "UPPER_HALL"},
    }
    resolved_at = {**room_at, 11: {"p-4": "MEDBAY", "p-5": "LABS"}}
    return room_at, resolved_at


def _observer() -> Any:
    from agents.memory.episodic import MemoryStore

    store = MemoryStore()
    # At the resume tick: the vent seen at its destination, and p-5 in the
    # meeting room where the regroup placed them.
    store.append(_row(12, "p-4", "MEDBAY", "vent"))
    store.append(_row(12, "p-5", "CAFETERIA", None))
    return store


def test_the_clock_reads_state_rows_on_the_regrouped_frame_and_actions_where_resolved() -> (
    None
):
    room_at, resolved_at = _regroup_tables()
    tallies = honesty_module._Tallies()
    honesty_module._assert_clock_alignment(
        game_id="g",
        memories={"p-1": _observer()},
        room_at=room_at,
        resolved_at=resolved_at,
        tallies=tallies,
    )
    assert (tallies.clock_checked, tallies.clock_checked_action_stamped) == (2, 1)


def test_an_action_row_read_on_the_regrouped_frame_raises() -> None:
    room_at, _ = _regroup_tables()
    with pytest.raises(EvidenceHonestyReconstructionError, match="p-4 in MEDBAY"):
        honesty_module._assert_clock_alignment(
            game_id="g",
            memories={"p-1": _observer()},
            room_at=room_at,
            tallies=honesty_module._Tallies(),
        )


def test_a_state_row_read_on_the_resolved_frame_raises() -> None:
    _, resolved_at = _regroup_tables()
    with pytest.raises(EvidenceHonestyReconstructionError, match="p-5 in CAFETERIA"):
        honesty_module._assert_clock_alignment(
            game_id="g",
            memories={"p-1": _observer()},
            room_at=resolved_at,
            resolved_at=resolved_at,
            tallies=honesty_module._Tallies(),
        )


# --------------------------------------------------------------------------- #
# The meeting-quality inform band                                             #
# --------------------------------------------------------------------------- #


def _assembled(directory: Path) -> GameReport:
    """The game as the sample report's own assembly reads it."""

    (game,) = assemble_tournament_report(directory).games
    return game


def test_the_inform_band_reads_the_window_each_live_meeting_ran_with(
    vouching_game: _Live,
) -> None:
    game = _assembled(vouching_game.path.parent)
    assert game.experiment_config is not None
    assert game.experiment_config.meeting_reset == "hub_with_grace"
    read = [
        meeting_quality._regroup_ticks_before(game, index)
        for index in range(len(game.meetings))
    ]
    live = [opening.regroup_ticks for opening in vouching_game.openings]
    assert read == live
    assert sum(1 for ticks in read if ticks) >= 2


def test_without_the_reset_the_inform_band_reads_no_window(preserve_set: Path) -> None:
    game = _assembled(preserve_set)
    assert len(game.meetings) >= 2
    assert all(
        meeting_quality._regroup_ticks_before(game, index) == frozenset()
        for index in range(len(game.meetings))
    )


def _graph_prompt(rows: dict[str, float]) -> str:
    graph = "".join(
        f"- `{pid}`: suspicion {value:.2f}, trust 0.50\n" for pid, value in rows.items()
    )
    return f"## Your suspicion graph\n{graph}\n## Decision rules\n"


def _one_voice(*, turn_id: str, accuser: str, impostor: str, tick: int) -> MeetingTurn:
    """An opening that accuses ``impostor``, backed by a sighting of them at ``tick``."""

    return MeetingTurn(
        turn_id=turn_id,
        turn_index=0,
        speaker=accuser,
        turn_kind="opening",
        reply_to=None,
        observations=(
            SawPlayerObservation(
                type="saw_player",
                tick=tick,
                subject=impostor,
                room=load_canonical_map().meeting.room,
            ),
        ),
        claims=(
            AccusationClaim(
                type="accusation",
                against=impostor,
                confidence=0.7,
                reason="where they stood",
            ),
        ),
        free_text="I saw them.",
    )


def _planted_ejection(
    game: GameReport, *, after_regroup: int
) -> tuple[GameReport, int]:
    """The game's last meeting turned into an impostor ejection with one voice.

    A crewmate accuses the impostor, backed only by a sighting of them in the
    meeting room ``after_regroup`` ticks after the previous meeting's resume
    tick, and one other voter was shown the impostor at 0.55: one inform
    quantum over the prior. The resume tick is read off the meeting rows here,
    never off the derivation under test.
    """

    index = len(game.meetings) - 1
    assert index >= 1
    meeting = game.meetings[index]
    resume = game.meetings[index - 1].tick + 1
    voters = sorted(ballot.voter for ballot in meeting.ballots)
    impostor = next(pid for pid in voters if game.roles[pid] == "IMPOSTOR")
    accuser, shown = [pid for pid in voters if game.roles[pid] == "CREWMATE"][:2]
    turn = _one_voice(
        turn_id=f"{meeting.meeting_id}:turn-0",
        accuser=accuser,
        impostor=impostor,
        tick=resume + after_regroup,
    )
    call = meeting.llm_calls[0].model_copy(
        update={"agent_id": shown, "prompt": _graph_prompt({impostor: 0.55})}
    )
    planted = meeting.model_copy(
        update={
            "outcome": "EJECTED",
            "ejected_player_id": impostor,
            "transcript": MeetingTranscript(turns=(turn,)),
            "contradictions": (),
            "llm_calls": (call,),
        }
    )
    return (
        game.model_copy(update={"meetings": (*game.meetings[:index], planted)}),
        index,
    )


def _inform_conversions(game: GameReport) -> int:
    return compute_multi_signal_conversion(
        (game,)
    ).conversions_with_single_witness_inform


@pytest.mark.parametrize("after_regroup", [0, 1])
def test_a_voice_resting_on_a_regroup_sighting_informs_nobody(
    vouching_game: _Live, after_regroup: int
) -> None:
    planted, index = _planted_ejection(
        _assembled(vouching_game.path.parent), after_regroup=after_regroup
    )
    # The inform band is empty, so the one +0.05 quantum reads as body
    # proximity, the channel left when no voice explains it.
    assert decompose_ejection_channels(planted, index) == frozenset(
        {CHANNEL_BODY_PROXIMITY}
    )
    assert _inform_conversions(planted) == 0


def test_with_the_window_withheld_the_same_fold_credits_the_inform(
    vouching_game: _Live, monkeypatch: pytest.MonkeyPatch
) -> None:
    planted, index = _planted_ejection(
        _assembled(vouching_game.path.parent), after_regroup=0
    )
    monkeypatch.setattr(
        meeting_quality, "derive_regroup_ticks", lambda *a, **k: frozenset()
    )
    assert decompose_ejection_channels(planted, index) == frozenset(
        {CHANNEL_SINGLE_WITNESS_INFORM}
    )
    assert _inform_conversions(planted) == 1


def test_just_past_the_window_the_voice_still_informs(vouching_game: _Live) -> None:
    planted, index = _planted_ejection(
        _assembled(vouching_game.path.parent), after_regroup=2
    )
    assert decompose_ejection_channels(planted, index) == frozenset(
        {CHANNEL_SINGLE_WITNESS_INFORM}
    )


def test_the_preserve_twin_of_the_planted_game_folds_as_before(
    vouching_game: _Live,
) -> None:
    planted, index = _planted_ejection(
        _assembled(vouching_game.path.parent), after_regroup=0
    )
    twin = planted.model_copy(update={"experiment_config": None})
    assert decompose_ejection_channels(twin, index) == frozenset(
        {CHANNEL_SINGLE_WITNESS_INFORM}
    )
    assert _inform_conversions(twin) == 1


# --------------------------------------------------------------------------- #
# The V&J pre-vote graphs                                                     #
# --------------------------------------------------------------------------- #


def test_the_vj_pre_vote_fold_reads_each_meetings_window(
    vouching_game: _Live, monkeypatch: pytest.MonkeyPatch
) -> None:
    import eval.vj_instruments as vj
    from meetings.manager import derive_belief_evidence as real

    seen: list[frozenset[int]] = []

    def _spy(*args: Any, **kwargs: Any) -> Any:
        seen.append(kwargs["regroup_ticks"])
        return real(*args, **kwargs)

    monkeypatch.setattr(vj, "derive_belief_evidence", _spy)
    vj.compute_vj_instruments(vouching_game.path.parent)
    assert seen == [opening.regroup_ticks for opening in vouching_game.openings]
    assert sum(1 for ticks in seen if ticks) >= 2


def test_a_regroup_sighting_lifts_no_row_in_the_vj_pre_vote_graphs(
    vouching_game: _Live,
) -> None:
    from eval.vj_instruments import _pre_vote_graphs

    walked = _vj_walk(vouching_game).meetings[-1]
    assert walked.regroup_ticks
    roles = _assembled(vouching_game.path.parent).roles
    voters = sorted(walked.living)
    impostor = next(pid for pid in voters if roles[pid] == "IMPOSTOR")
    accuser = next(pid for pid in voters if roles[pid] == "CREWMATE")
    turn = _one_voice(
        turn_id=f"{walked.meeting_id}:turn-0",
        accuser=accuser,
        impostor=impostor,
        tick=max(walked.regroup_ticks),
    )
    planted = replace(
        walked, transcript=MeetingTranscript(turns=(turn,)), contradictions=()
    )

    listeners = [
        voter
        for voter in voters
        if voter not in (impostor, accuser) and roles[voter] == "CREWMATE"
    ]

    def _spread(graphs: Any) -> dict[str, float]:
        return {
            voter: sum(
                entry.testimony_spread
                for entry in graphs[voter]
                if entry.player_id == impostor
            )
            for voter in listeners
        }

    carried = _spread(walked.suspicion_graph_by_voter)
    windowed = _spread(_pre_vote_graphs(planted))
    plain = _spread(_pre_vote_graphs(replace(planted, regroup_ticks=frozenset())))
    # In the window the sighting places nobody and backs no voice, so each
    # listener's row takes the absence lift and no inform; without the window
    # it places the impostor and backs the one voice, the inform quantum.
    assert listeners
    for voter in listeners:
        assert windowed[voter] == pytest.approx(
            carried[voter] + ABSENCE_SUSPICION_DELTA
        )
        assert plain[voter] == pytest.approx(
            carried[voter] + ACCUSATION_SUSPICION_DELTA
        )


# --------------------------------------------------------------------------- #
# The frozen deception instruments refuse the reset                           #
# --------------------------------------------------------------------------- #


class _Walked(Exception):
    """The deception walk began: raised in place of the walk."""


def _stop_at_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    import eval.deception_instruments as deception

    def _walk(_directory: Path) -> Any:
        raise _Walked

    monkeypatch.setattr(deception, "_walk_set_vj", _walk)


def test_the_deception_instruments_refuse_the_reset_by_name_before_walking(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from eval.deception_instruments import compute_deception_instruments

    _stop_at_the_walk(monkeypatch)
    with pytest.raises(
        ValueError, match=rf"meeting_reset='hub_with_grace' \(seed {SEED}\)"
    ):
        compute_deception_instruments(reset_set)


def test_a_set_with_one_reset_recording_is_refused_at_that_seed(
    preserve_set: Path,
    reset_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from eval.deception_instruments import compute_deception_instruments

    mixed = tmp_path / "9p2i"
    shutil.copytree(preserve_set, mixed)
    shutil.copy(_path(reset_set), mixed / f"replay-seed-{SEED + 1}.jsonl")
    _stop_at_the_walk(monkeypatch)
    with pytest.raises(ValueError, match=rf"\(seed {SEED + 1}\)"):
        compute_deception_instruments(mixed)


@pytest.mark.parametrize(
    "settings",
    [
        {},
        {"meeting_reset": "preserve"},
        {"vent_witness_rule": "physical", "bounded_rebuttal_version": 1},
    ],
)
def test_the_deception_refusal_names_the_reset_and_nothing_else(
    preserve_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: dict[str, object],
) -> None:
    from eval.deception_instruments import compute_deception_instruments

    source = (
        _copy_with(preserve_set, tmp_path / "copy" / "9p2i", **settings)
        if settings
        else preserve_set
    )
    _stop_at_the_walk(monkeypatch)
    with pytest.raises(_Walked):
        compute_deception_instruments(source)


# --------------------------------------------------------------------------- #
# The phase-21 counterfactual refuses the reset                               #
# --------------------------------------------------------------------------- #


def _phase21(monkeypatch: pytest.MonkeyPatch) -> Any:
    """The script's module, its first re-derivation replaced by :class:`_Walked`."""

    import sys

    scripts = Path(__file__).resolve().parents[2] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    import counterfactual_phase21

    def _walk(*_args: Any, **_kwargs: Any) -> Any:
        raise _Walked

    monkeypatch.setattr(counterfactual_phase21, "roles_by_seed", _walk)
    monkeypatch.setattr(counterfactual_phase21, "walk_replay_meetings", _walk)
    return counterfactual_phase21


def test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking(
    reset_set: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    phase21 = _phase21(monkeypatch)
    with pytest.raises(
        SystemExit, match=rf"meeting_reset='hub_with_grace' \(seed {SEED}\)"
    ):
        phase21.walk_set(reset_set, set_name="reset/9p2i", withhold="testimony_shapes")


def test_the_phase21_command_refuses_a_reset_set_staged_under_replays(
    reset_set: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The command a reader would run: ``--sets`` names a directory under
    # ``replays/``, here a checkout whose only set is the reset recording.
    phase21 = _phase21(monkeypatch)
    shutil.copytree(reset_set, tmp_path / "replays" / "staged" / "9p2i")
    monkeypatch.setattr(phase21, "_REPO_ROOT", tmp_path)
    with pytest.raises(
        SystemExit, match=rf"meeting_reset='hub_with_grace' \(seed {SEED}\)"
    ):
        phase21.main(["--sets", "staged/9p2i"])


def test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed(
    preserve_set: Path,
    reset_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    phase21 = _phase21(monkeypatch)
    mixed = tmp_path / "9p2i"
    shutil.copytree(preserve_set, mixed)
    shutil.copy(_path(reset_set), mixed / f"replay-seed-{SEED + 1}.jsonl")
    with pytest.raises(SystemExit, match=rf"\(seed {SEED + 1}\)"):
        phase21.walk_set(mixed, set_name="mixed/9p2i", withhold="testimony_shapes")


@pytest.mark.parametrize(
    "settings",
    [
        {},
        {"meeting_reset": "preserve"},
        {"vent_witness_rule": "physical", "bounded_rebuttal_version": 1},
    ],
)
def test_the_phase21_refusal_names_the_reset_and_nothing_else(
    preserve_set: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    settings: dict[str, object],
) -> None:
    phase21 = _phase21(monkeypatch)
    source = (
        _copy_with(preserve_set, tmp_path / "copy" / "9p2i", **settings)
        if settings
        else preserve_set
    )
    with pytest.raises(_Walked):
        phase21.walk_set(source, set_name="copy/9p2i", withhold="testimony_shapes")
