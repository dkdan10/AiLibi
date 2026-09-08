"""The version-3 policy oracle runs against bytes this tree did not produce.

Every other version-3 reconstruction in the suite records and re-decides in one
process at one commit. A shared oracle checked that way can only attest
self-consistency: a policy regression moves the recorder and the checker
together, so the check stays green and the "verified policy reconstruction"
label says nothing about whether a later tree still decides the same way.

``tests/fixtures/v3_policy_reconstruction/`` freezes one recording produced by
the tree at `201849fc`, before this card edited any source. Walking it here is
therefore a cross-tree walk, and the planted case below is a policy change in
the checking tree — which is exactly the class of defect the same-process
captures cannot see.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, NoReturn

import pytest

from agents.tactical.crewmate_policy import CrewmatePolicy
from engine.world import load_canonical_map
from eval.replay_walk import (
    ReplayWalkConfig,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
from observation.action_intent import ActionIntent
from orchestrator.replay import (
    ReplayEntry,
    read_all_entries,
    recorded_experiment_config,
    recorded_temporal_observation_version,
)

_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "v3_policy_reconstruction"
    / "replay-seed-1.jsonl"
)
# Pinned here as well as in the fixture README: a re-recording is a decision,
# and it has to be made in both places.
_FIXTURE_SHA256 = "543bf9cde342af39bb762c05e772f57054c1190b8b087c887679355c42fa3205"


def _walk(*, reconstruct: bool, calls: list[str]) -> list[Any]:
    def hook(violation: WalkViolation) -> NoReturn:
        calls.append(violation.kind)
        raise AssertionError(f"{violation.kind} at tick {violation.tick}")

    return list(
        walk_replay(
            _FIXTURE,
            seed=1,
            num_players=7,
            num_impostors=1,
            tasks_per_crewmate=1,
            game_map=load_canonical_map(),
            config=ReplayWalkConfig(
                profile="v3-cross-tree",
                on_violation=hook,
                # The recording is an interrupted prefix that stops when tick 8
                # enters MEETING; truncating there is its recorded timeline.
                missing_meeting_row="truncate",
                supports_temporal_observations=True,
                supports_experiments=True,
                reconstruct_v3_policies=reconstruct,
            ),
        )
    )


def test_the_frozen_recording_still_carries_the_identity_the_check_needs() -> None:
    """A silently re-recorded or relabelled fixture would make the walk vacuous."""

    assert hashlib.sha256(_FIXTURE.read_bytes()).hexdigest() == _FIXTURE_SHA256
    entries = read_all_entries(_FIXTURE)
    experiment = recorded_experiment_config(entries)
    assert experiment is not None and experiment.format_version == 3
    assert experiment.investigation_version == 1
    assert recorded_temporal_observation_version(entries) == 2
    ticks = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    assert len(ticks) == 9
    assert sum(len(entry.actions) for entry in ticks) == 59


def test_this_tree_reproduces_every_recorded_decision() -> None:
    """The cross-tree walk: bytes from another commit, decided again here."""

    calls: list[str] = []
    events = _walk(reconstruct=True, calls=calls)
    assert calls == []
    assert isinstance(events[-1], WalkComplete)


def test_a_planted_policy_change_makes_the_cross_tree_walk_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A later tree that decides differently disagrees with the frozen bytes.

    The planted change is a crewmate policy that stops submitting task attempts
    — the shape a refactor regression takes. The recording's first task attempt
    is at tick 2, so the disagreement is found before any state hash could
    diverge, which is the point: this profile has no hash check, so only the
    re-decision can catch it.
    """

    def no_task_attempt(self: CrewmatePolicy, *, task_id: str) -> ActionIntent:
        return self._wait()

    monkeypatch.setattr(CrewmatePolicy, "_do_task", no_task_attempt)

    calls: list[str] = []
    with pytest.raises(AssertionError, match="v3_policy_mismatch at tick 2"):
        _walk(reconstruct=True, calls=calls)
    assert calls == ["v3_policy_mismatch"]

    # The same defective tree walks the same bytes clean with the option off,
    # so the failure above is the check and not the walk mechanics.
    control: list[str] = []
    assert isinstance(_walk(reconstruct=False, calls=control)[-1], WalkComplete)
    assert control == []
