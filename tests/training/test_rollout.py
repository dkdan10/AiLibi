"""Tests for the per-episode rollout records + descriptors (Task 15.8).

Pins: the episode record carries every named behavioral descriptor with values
FIXED on a scripted (frozen-FSM, fake-provider) game; the reconstruction is
state-hash-verified against the recorded replay and fails loud both on hash
drift and on a truncated tick stream (a recorded ``game_over`` the walk never
reaches); the descriptors + hash chain are byte-deterministic; and a completed
full game is not truncated (Task 19.19 retired the first-meeting boundary,
leaving the tick-budget cap as the only truncation source).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from engine.entities import Role
from engine.events import KilledEvent
from engine.world import load_canonical_map
from orchestrator.replay import ReplayEntry, read_all_entries
from training.env import TacticalRolloutEnv
from training.rollout import (
    RolloutReconstructionError,
    crew_witnesses,
    reconstruct_episode,
)

_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2


def _env(**overrides: object) -> TacticalRolloutEnv:
    kwargs: dict[str, object] = {
        "num_players": _NUM_PLAYERS,
        "num_impostors": _NUM_IMPOSTORS,
        "tasks_per_crewmate": _TASKS,
    }
    kwargs.update(overrides)
    return TacticalRolloutEnv(**kwargs)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# A scripted game pins every named behavioral descriptor                       #
# --------------------------------------------------------------------------- #


def test_descriptors_fixture_on_a_scripted_game() -> None:
    """The frozen FSM + fake provider make seed 0 fully deterministic (9p2i).

    Every descriptor named in the task contract is pinned to its scripted value,
    so a regression in the reconstruction folds — or an upstream trajectory
    change — trips this fixture rather than silently shifting a fitness axis.

    The values are the scripted trajectory of the FSM in the tree, and
    ``training/env.py`` wraps that FSM as the surrogate's proposal, so the impostor
    mover repair moved every kill-derived descriptor here (Task 20.32). No training
    code changed.
    """

    rollout = _env().rollout(0)
    descriptors = rollout.descriptors

    assert descriptors.kill_ticks == (5, 12, 43, 51, 56)  # kill-timing distribution
    assert descriptors.kill_count == 5
    assert descriptors.median_kill_tick == 43.0
    assert descriptors.witness_exposure_rate == pytest.approx(0.0)  # 0/5 witnessed
    assert descriptors.vent_usage == 10
    assert descriptors.meeting_count == 5
    assert descriptors.meeting_trigger_rate == pytest.approx(5 / 56)
    assert descriptors.do_task_emissions == 99  # includes impostor pretend do_task
    assert descriptors.do_task_cadence == pytest.approx(99 / 56)
    assert descriptors.win_shape == "IMPOSTORS:IMPOSTOR_PARITY"

    # The QD feature vector projects the numeric descriptors in the fixed order.
    vector = descriptors.vector()
    assert vector.shape == (8,)
    assert vector[0] == 5.0  # kill_count
    assert vector[2] == 10.0  # vent_usage
    assert vector[-1] == 43.0  # median kill tick


def test_rollout_carries_roles_and_terminal_shape() -> None:
    rollout = _env().rollout(0)
    assert rollout.outcome == "IMPOSTORS"
    assert rollout.winner == "IMPOSTORS"
    assert rollout.win_reason == "IMPOSTOR_PARITY"
    assert rollout.complete
    assert not rollout.truncated
    assert len(rollout.impostor_ids()) == _NUM_IMPOSTORS
    assert len(rollout.crew_ids()) == _NUM_PLAYERS - _NUM_IMPOSTORS


def test_descriptors_are_byte_deterministic() -> None:
    env = _env()
    first = env.rollout(0)
    second = env.rollout(0)
    assert first.descriptors == second.descriptors
    assert first.state_hashes == second.state_hashes


# --------------------------------------------------------------------------- #
# Reconstruction is state-hash-verified against the recorded replay            #
# --------------------------------------------------------------------------- #


def test_reconstruction_tick_hashes_match_the_recorded_replay() -> None:
    with tempfile.TemporaryDirectory(prefix="ailibi-recon-") as tmp:
        env = _env(output_dir=Path(tmp))
        rollout = env.rollout(4)
        replay_path = Path(tmp) / "replay-seed-4.jsonl"
        recorded = [
            entry.state_hash
            for entry in read_all_entries(replay_path)
            if isinstance(entry, ReplayEntry)
        ]
    reconstructed_tick_hashes = [
        frame.state_hash for frame in rollout.frames if frame.kind == "tick"
    ]
    assert reconstructed_tick_hashes == recorded


def test_reconstruction_fails_loud_on_state_hash_drift() -> None:
    game_map = load_canonical_map()
    with tempfile.TemporaryDirectory(prefix="ailibi-drift-") as tmp:
        env = _env(output_dir=Path(tmp))
        env.rollout(4)
        replay_path = Path(tmp) / "replay-seed-4.jsonl"

        lines = replay_path.read_text(encoding="utf-8").splitlines()
        tampered: list[str] = []
        did_tamper = False
        for line in lines:
            record = json.loads(line)
            if not did_tamper and record.get("kind") == "tick":
                record["state_hash"] = "0" * 64  # a plausible-shaped but wrong hash
                did_tamper = True
            tampered.append(json.dumps(record))
        assert did_tamper
        replay_path.write_text("\n".join(tampered) + "\n", encoding="utf-8")

        with pytest.raises(RolloutReconstructionError):
            reconstruct_episode(
                replay_path,
                game_map=game_map,
                seed=4,
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
                tasks_per_crewmate=_TASKS,
            )


@pytest.mark.parametrize("keep_recorded_winner", [True, False])
def test_reconstruction_fails_loud_on_a_truncated_tick_stream(
    keep_recorded_winner: bool,
) -> None:
    """A surviving ``game_over`` row the walk never reaches is corruption.

    Dropping trailing tick rows shortens the walk without breaking the
    state-hash chain, so every per-tick hash still verifies and the terminal
    cross-check is the only thing that can catch it. Without it the episode came
    back as a silent ``outcome="TICK_BUDGET" truncated=True``. A capped game
    writes no ``game_over`` row at all, so the row's own winner field is not
    evidence of anything — a winnerless row is rejected on the same terms.
    """

    game_map = load_canonical_map()
    with tempfile.TemporaryDirectory(prefix="ailibi-truncate-") as tmp:
        env = _env(output_dir=Path(tmp))
        env.rollout(4)
        replay_path = Path(tmp) / "replay-seed-4.jsonl"

        lines = replay_path.read_text(encoding="utf-8").splitlines()
        last_tick = max(
            index
            for index, line in enumerate(lines)
            if json.loads(line).get("kind") == "tick"
        )
        del lines[last_tick]
        if not keep_recorded_winner:
            lines = [
                json.dumps({**json.loads(line), "winner": None})
                if json.loads(line).get("kind") == "game_over"
                else line
                for line in lines
            ]
        replay_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(RolloutReconstructionError, match="truncated tick stream"):
            reconstruct_episode(
                replay_path,
                game_map=game_map,
                seed=4,
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
                tasks_per_crewmate=_TASKS,
            )


def test_reconstruction_fails_loud_when_the_recording_names_no_winner() -> None:
    """The same disagreement from the other side: the walk reached GAME_OVER
    but the recording carries no ``game_over`` winner, so the two do not agree
    about the terminal and the episode is not scoreable as a full game."""

    game_map = load_canonical_map()
    with tempfile.TemporaryDirectory(prefix="ailibi-no-winner-") as tmp:
        env = _env(output_dir=Path(tmp))
        env.rollout(4)
        replay_path = Path(tmp) / "replay-seed-4.jsonl"

        lines = [
            line
            for line in replay_path.read_text(encoding="utf-8").splitlines()
            if json.loads(line).get("kind") != "game_over"
        ]
        replay_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(RolloutReconstructionError, match="no game_over winner"):
            reconstruct_episode(
                replay_path,
                game_map=game_map,
                seed=4,
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
                tasks_per_crewmate=_TASKS,
            )


# --------------------------------------------------------------------------- #
# Boundary semantics: the full-game episode                                    #
# --------------------------------------------------------------------------- #


def test_full_game_is_not_truncated() -> None:
    rollout = _env().rollout(0)
    assert not rollout.truncated
    assert rollout.complete
    # The last frame is the terminal GAME_OVER state.
    assert rollout.frames[-1].phase == "GAME_OVER"


def test_meeting_records_capture_trigger_and_outcome() -> None:
    rollout = _env().rollout(0)
    assert rollout.meetings
    for meeting in rollout.meetings:
        assert meeting.trigger in ("report", "emergency")
        assert meeting.triggered_by in rollout.roles


def test_initial_frame_opens_the_potential_chain() -> None:
    """The seeded pre-action state s0 opens the frame chain so the potential
    series starts at Φ(s0) and shaping telescopes over the real episode."""

    rollout = _env().rollout(0)
    first = rollout.frames[0]
    assert first.kind == "initial"
    assert first.tick == 0
    assert first.phase == "PLAY"
    assert first.cumulative_kills == 0
    assert first.tasks_completed == 0
    # Exactly one initial frame, and it is the only non-("tick"/"meeting") frame;
    # the seeded s0 has no recorded replay tick row (kept out of the tick chain).
    assert [frame.kind for frame in rollout.frames].count("initial") == 1
    assert rollout.frames[1].kind == "tick"  # s1 (post-tick-0) is a tick frame


def test_post_meeting_frame_uses_the_resumed_tick() -> None:
    """apply_meeting_result resumes at trigger_tick + 1, so the post-meeting
    frame is stamped with the resumed tick (no off-by-one around meetings)."""

    rollout = _env().rollout(0)
    meeting_frames = [
        (index, frame)
        for index, frame in enumerate(rollout.frames)
        if frame.kind == "meeting"
    ]
    assert meeting_frames  # seed 0 reaches meetings
    for index, frame in meeting_frames:
        previous = rollout.frames[index - 1]
        assert previous.kind == "tick"
        assert previous.phase == "MEETING"  # the meeting occupied the trigger tick
        assert frame.tick == previous.tick + 1  # gameplay resumes at trigger + 1
        assert frame.phase in ("PLAY", "GAME_OVER")


def test_episode_rollout_rejects_inconsistent_terminal_shape() -> None:
    """The rollout record enforces its terminal-shape invariant at construction,
    so an invalid record cannot be built (and thus cannot be scored)."""

    from training.rollout import BehavioralDescriptors, EpisodeRollout

    descriptors = BehavioralDescriptors(
        kill_ticks=(),
        witness_exposure_rate=0.0,
        vent_usage=0,
        meeting_count=0,
        meeting_trigger_rate=0.0,
        do_task_emissions=0,
        do_task_cadence=0.0,
        win_shape="IMPOSTORS",
    )

    def _build(*, truncated: bool, outcome: str, winner: str | None) -> EpisodeRollout:
        return EpisodeRollout(
            seed=0,
            num_players=_NUM_PLAYERS,
            num_impostors=_NUM_IMPOSTORS,
            tasks_per_crewmate=_TASKS,
            episode_boundary="full_game",
            truncated=truncated,
            outcome=outcome,  # type: ignore[arg-type]
            winner=winner,  # type: ignore[arg-type]
            win_reason=None,
            final_tick=1,
            roles={"p0": "IMPOSTOR"},
            frames=(),
            events=(),
            meetings=(),
            descriptors=descriptors,
        )

    # A consistent completed episode builds fine.
    assert _build(truncated=False, outcome="IMPOSTORS", winner="IMPOSTORS").complete
    # Truncated but carrying a winner — rejected.
    with pytest.raises(ValueError):
        _build(truncated=True, outcome="TICK_BUDGET", winner="IMPOSTORS")
    # Terminal outcome disagreeing with the winner — rejected.
    with pytest.raises(ValueError):
        _build(truncated=False, outcome="IMPOSTORS", winner="CREWMATES")
    # Terminal outcome but truncated — rejected.
    with pytest.raises(ValueError):
        _build(truncated=True, outcome="CREWMATES", winner=None)


def test_reconstruct_rejects_unknown_boundary() -> None:
    game_map = load_canonical_map()
    with tempfile.TemporaryDirectory(prefix="ailibi-badbound-") as tmp:
        env = _env(output_dir=Path(tmp))
        env.rollout(0)
        replay_path = Path(tmp) / "replay-seed-0.jsonl"
        with pytest.raises(ValueError, match="unknown episode_boundary"):
            reconstruct_episode(
                replay_path,
                game_map=game_map,
                seed=0,
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
                tasks_per_crewmate=_TASKS,
                episode_boundary="first-meeting",  # type: ignore[arg-type]
            )


# --------------------------------------------------------------------------- #
# crew_witnesses: teammate witnesses are not crew evidence                     #
# --------------------------------------------------------------------------- #


def _kill(actor: str, target: str, witnesses: tuple[str, ...]) -> KilledEvent:
    return KilledEvent(
        type="Killed",
        tick=3,
        actor=actor,
        target=target,
        room="CAFETERIA",
        witnesses=witnesses,
    )


def test_crew_witnesses_excludes_teammate_only_witnesses() -> None:
    roles: dict[str, Role] = {
        "p0": "IMPOSTOR",
        "p1": "IMPOSTOR",
        "p2": "CREWMATE",
        "p3": "CREWMATE",
    }
    # Seen only by the fellow impostor -> no crew evidence.
    teammate_only = _kill("p0", "p2", ("p1",))
    assert crew_witnesses(teammate_only, roles) == ()
    # Mixed: only the crewmate counts.
    mixed = _kill("p0", "p3", ("p1", "p2"))
    assert crew_witnesses(mixed, roles) == ("p2",)
    # Unseen entirely.
    assert crew_witnesses(_kill("p0", "p2", ()), roles) == ()
