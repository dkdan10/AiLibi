"""Loader-side coverage for the tactical-policy provenance guard (Task 15.9).

The honoring half of the stamp (DESIGN.md §11.4; audit
post-phase-14-ML-planning.md §7.2-7.3), mirroring
``ReplaySubstrateMismatchError``. Unlike the substrate, there is no "ambient"
policy — replay re-feeds recorded actions and never re-invokes a policy — so the
guard fires against a caller's explicit ``expected_tactical_policy`` claim: a
recording whose stamp conflicts with the claim is refused via
:class:`ReplayPolicyMismatchError`. An UNSTAMPED replay reads as the scripted FSM
default, so it matches an ``fsm-default`` claim and conflicts with a learned one.
When no claim is set (the default), the guard is inert and every replay serves —
the committed canonical sets are untouched.

The fixtures write real replays through :class:`orchestrator.replay.ReplayLog`
(4p/1i, ``tasks_per_crewmate=1``), so the loader reconstructs them from its
descriptor-less default and each reconstructed ``state_hash`` is verified against
the record — the guard is exercised end-to-end, not against a hand-authored mock.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.replay_loader import ReplayLoader, ReplayPolicyMismatchError
from engine.tick import advance_tick
from engine.world import load_canonical_map
from orchestrator.replay import (
    ReplayLog,
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
)
from orchestrator.seeder import seed_initial_state
from tests.api.fixtures.sample_replay import finish_replay_with_kills

_CHAMPION = TacticalPolicyStamp(
    policy_id="wave2-champion-7",
    method="neuroevolution",
    encoder_version="encoder.v3",
    weights_sha256="a" * 64,
    anchor_policy="fsm-default",
)


def _write_stamped_replay(
    path: Path,
    *,
    seed: int = 0,
    ticks: int = 3,
    stamp: TacticalPolicyStamp | None = None,
    game_over: bool = True,
) -> None:
    """Write a no-op 4p/1i game (like ``write_sample_replay``) with an optional stamp.

    The game is descriptor-less at the loader default (num_impostors=1,
    tasks_per_crewmate=1), so ``ReplayLoader`` reconstructs it without a
    ``roster.json`` and the per-tick ``state_hash`` chain verifies clean.
    ``game_over=False`` omits the game_over footer (a partial / crashed replay),
    so no provenance stamp is ever written — the policy is UNKNOWN, not the FSM
    default.
    """

    game_map = load_canonical_map()
    log = ReplayLog(
        path=path, game_id=f"headless-seed-{seed}", tactical_policy_stamp=stamp
    )
    state = seed_initial_state(
        seed=seed, game_map=game_map, num_players=4, num_impostors=1
    )
    for _ in range(ticks):
        input_tick = state.tick
        state, _events = advance_tick(state, [], game_map=game_map)
        log.record_tick(input_tick, [], state)
    if game_over:
        finish_replay_with_kills(log, state, game_map)
    log.close()


class TestGuardInertByDefault:
    def test_default_loader_serves_a_stamped_replay(self, tmp_path: Path) -> None:
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=_CHAMPION)
        loader = ReplayLoader(replay_dir=tmp_path)
        # No expected policy claim -> the guard is inert; the replay serves.
        assert loader.load_replay("headless-seed-0").metadata.game_id == (
            "headless-seed-0"
        )

    def test_default_loader_serves_an_unstamped_replay(self, tmp_path: Path) -> None:
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=None)
        loader = ReplayLoader(replay_dir=tmp_path)
        assert loader.load_replay("headless-seed-0").metadata.game_id == (
            "headless-seed-0"
        )


class TestPolicyClaimEnforced:
    def test_matching_claim_serves(self, tmp_path: Path) -> None:
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=_CHAMPION)
        loader = ReplayLoader(replay_dir=tmp_path, expected_tactical_policy=_CHAMPION)
        assert loader.load_replay("headless-seed-0").ticks  # reconstructs + serves

    def test_conflicting_claim_raises(self, tmp_path: Path) -> None:
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=_CHAMPION)
        loader = ReplayLoader(
            replay_dir=tmp_path,
            expected_tactical_policy=fsm_default_tactical_policy_stamp(),
        )
        with pytest.raises(ReplayPolicyMismatchError) as excinfo:
            loader.load_replay("headless-seed-0")
        err = excinfo.value
        # Error quality mirrors the substrate guard: names the game id, carries
        # both stamps, and the message calls out the differing fields.
        assert err.game_id == "headless-seed-0"
        assert err.recorded == _CHAMPION
        assert err.expected == fsm_default_tactical_policy_stamp()
        assert "policy_id" in str(err)
        assert "headless-seed-0" in str(err)

    def test_unstamped_matches_fsm_default_claim(self, tmp_path: Path) -> None:
        # Absent stamp = FSM default, so an fsm-default claim SERVES it.
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=None)
        loader = ReplayLoader(
            replay_dir=tmp_path,
            expected_tactical_policy=fsm_default_tactical_policy_stamp(),
        )
        assert loader.load_replay("headless-seed-0").ticks

    def test_unstamped_conflicts_with_learned_claim(self, tmp_path: Path) -> None:
        # Absent stamp = FSM default, so a learned-policy claim REFUSES it.
        _write_stamped_replay(tmp_path / "replay-seed-0.jsonl", stamp=None)
        loader = ReplayLoader(replay_dir=tmp_path, expected_tactical_policy=_CHAMPION)
        with pytest.raises(ReplayPolicyMismatchError) as excinfo:
            loader.load_replay("headless-seed-0")
        # An unstamped recording is reported as the FSM default it stands for.
        assert excinfo.value.recorded == fsm_default_tactical_policy_stamp()

    def test_explicit_fsm_stamp_matches_fsm_default_claim(self, tmp_path: Path) -> None:
        _write_stamped_replay(
            tmp_path / "replay-seed-0.jsonl",
            stamp=fsm_default_tactical_policy_stamp(),
        )
        loader = ReplayLoader(
            replay_dir=tmp_path,
            expected_tactical_policy=fsm_default_tactical_policy_stamp(),
        )
        assert loader.load_replay("headless-seed-0").ticks

    def test_partial_replay_is_not_enforced_under_a_learned_claim(
        self, tmp_path: Path
    ) -> None:
        # A partial replay (no game_over footer) never wrote its provenance stamp
        # — the policy is UNKNOWN, not the FSM default — so a learned-policy claim
        # does NOT reject it. This is the tournament harness's aborted-seed case:
        # a learned-policy run that crashes mid-meeting keeps a partial replay,
        # and the guard must not falsely reject it (mirrors the substrate guard
        # skipping an unstamped replay).
        _write_stamped_replay(
            tmp_path / "replay-seed-0.jsonl", game_over=False, stamp=None
        )
        loader = ReplayLoader(replay_dir=tmp_path, expected_tactical_policy=_CHAMPION)
        # Serves without raising (a partial replay has no winner but an intact
        # timeline).
        assert loader.load_replay("headless-seed-0").metadata.game_id == (
            "headless-seed-0"
        )
