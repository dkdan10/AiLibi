"""The instruments and reconstructors read a recording's own arms, or refuse them.

Every reader that re-reads a recording does one of two things for every recorded
setting: it threads the setting the way the live game did, or it refuses the
recording by name before its first advance. This module holds that contract for
the readers the Stage-B readers card widened and for the ones it keeps refusing:

* the five widened walk profiles (kill-craft, the information funnel's two
  walks, solvability, the win-condition self-check, evidence honesty) read
  arms-ON fake recordings with every hash verified, and refuse any other
  recorded setting by name before the first advance;
* evidence honesty rebuilds each game's impostor decisions with the policy the
  recording names, and refuses the meeting reset until that setting's own card
  makes its room table coherent;
* an event-level planted test threads a stand-in engine setting through the
  spine's engine-arguments helper and a stand-in engine that changes only the
  witness lists of vent exits, so every reader's call site is shown to take the
  helper's arguments, and the readers that fold vent observations change; on a
  recording made under the physical vent witness rule, every reader accepts the
  rule, the stand-in and the recorded rule reach every advance it drives, and
  withholding the rule changes what the vent-folding readers fold;
* the frozen and policy-re-running instruments keep refusing;
* every call site the card owns passes the recorded engine, reset and trigger
  settings explicitly (an ``ast`` scan with planted modules);
* the refusal copy this card adds names no task or audit identifier.

Every recording here is a fake-provider game recorded into a temporary directory
from a declared config (``tests/_helpers/scripted_meeting.py``); no test reads a
committed set. No prompt is printed.
"""

from __future__ import annotations

import ast
import dataclasses
import json
import re
import sys
import tempfile
from collections.abc import Callable, Iterator, Mapping, Sequence, Sized
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, TypedDict, cast

import pytest

import eval.replay_walk as replay_walk_module
import tests.meetings.test_prompt_byte_golden as golden
from agents.memory.episodic import MemoryStore
from agents.tactical.experimental import (
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.events import VentExitedEvent
from engine.tick import advance_tick as real_advance_tick
from engine.world import WorldState, load_canonical_map
from eval import evidence_honesty, funnel, win_condition_selfcheck
from eval.evidence_honesty import (
    HONESTY_READS,
    LIVE_POLICY_FOLD,
    RECORDED_ARM_POLICY_FOLD,
    EvidenceHonestyReconstructionError,
    ReconstructedDecision,
    compute_evidence_honesty,
    live_impostor_policy,
    reconstruct_impostor_decisions,
)
from eval.funnel import FUNNEL_READS, compute_information_funnel, compute_pooling_funnel
from eval.kill_craft import KILL_CRAFT_READS, compute_kill_craft_report
from eval.recorded_settings import (
    READABLE_SETTINGS,
    layers_read,
    read_recorded_settings,
    refuse_unread_settings,
)
from eval.replay_walk import (
    MeetingOpened,
    ReplayWalkConfig,
    ReplayWalkEvent,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    walk_replay,
)
from eval.solvability import SOLVABILITY_READS, compute_solvability_report
from eval.win_condition_selfcheck import (
    WIN_CONDITION_READS,
    WinConditionSelfCheck,
    check_replay_win_condition,
)
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    RecordedExperimentConfig,
    engine_arguments,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from tests._helpers.committed import CommittedMeeting, walk_committed_meetings
from tests._helpers.scripted_meeting import (
    ACCUSE_THE_OPENER,
    ScriptedMeetingClient,
    record_game,
)

_REPO: Final[Path] = Path(__file__).resolve().parents[2]
_SCRIPTS: Final[Path] = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

#: A 9p2i fake game with vent exits whose source rooms held living witnesses who
#: were still alive at a later meeting (asserted below, so no case goes vacuous).
_SEED: Final[int] = 0


class _Roster(TypedDict):
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int


_ROSTER: Final[_Roster] = {
    "num_players": 9,
    "num_impostors": 2,
    "tasks_per_crewmate": 2,
}

# --------------------------------------------------------------------------- #
# Recordings                                                                  #
# --------------------------------------------------------------------------- #


def _record(
    root: Path, name: str, config: RecordedExperimentConfig | None, **kwargs: Any
) -> Path:
    directory = root / name / "9p2i"
    record_game(directory, seed=_SEED, config=config, **kwargs)
    return directory


def _open_the_pending_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))


def _plant_unbuilt(monkeypatch: pytest.MonkeyPatch) -> None:
    """List the two tactical wave values as unbuilt again, as the spine did.

    The factory then refuses them by name, so a walk that reaches the refusal
    proves the recorded value reached the policy builder.
    """

    import agents.tactical.experimental as experimental

    monkeypatch.setattr(
        experimental,
        "UNBUILT_OPTION_VALUES",
        MappingProxyType(
            {
                "vent_exit_policy": frozenset({"look_and_wait"}),
                "vent_entry_policy": frozenset({"own_fresh_kill"}),
            }
        ),
    )


def _with_settings(source: Path, target: Path, **settings: object) -> Path:
    """A copy of a recorded set whose every stamped row also carries ``settings``."""

    target.mkdir(parents=True, exist_ok=True)
    for name in ("roster.json", "MANIFEST.md"):
        (target / name).write_bytes((source / name).read_bytes())
    for replay in source.glob("replay-seed-*.jsonl"):
        rows = [json.loads(line) for line in replay.read_text().splitlines()]
        stamped = 0
        for row in rows:
            if isinstance(row.get("experiment_config"), dict):
                row["experiment_config"].update(settings)
                stamped += 1
            elif row.get("kind") in ("tick", "game_over"):
                row["experiment_config"] = {"format_version": 1, **settings}
                stamped += 1
        assert stamped > 1
        (target / replay.name).write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
    return target


@pytest.fixture(scope="module")
def recordings(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Fake 9p2i recordings on arms that exist today, one directory each."""

    root = tmp_path_factory.mktemp("arms")
    return {
        "plain": _record(root, "plain", None),
        "workload": _record(
            root,
            "workload",
            RecordedExperimentConfig(redistribution_policy="least_remaining_work"),
        ),
        "reset": _record(
            root, "reset", RecordedExperimentConfig(meeting_reset="hub_with_grace")
        ),
        "reset_rebuttal": _record(
            root,
            "reset_rebuttal",
            RecordedExperimentConfig(
                meeting_reset="hub_with_grace", bounded_rebuttal_version=1
            ),
            client=ScriptedMeetingClient(script=ACCUSE_THE_OPENER),
        ),
        "observed_risk_rebuttal": _record(
            root,
            "observed_risk_rebuttal",
            RecordedExperimentConfig(
                vent_exit_policy="observed_risk", bounded_rebuttal_version=1
            ),
            client=ScriptedMeetingClient(script=ACCUSE_THE_OPENER),
        ),
        "physical": _record(
            root, "physical", RecordedExperimentConfig(vent_witness_rule="physical")
        ),
        "patrol": _record(
            root, "patrol", RecordedExperimentConfig(crew_idle_policy="patrol")
        ),
        "evidence_one": _record(
            root, "evidence_one", RecordedExperimentConfig(evidence_reasoning_version=1)
        ),
    }


# The wave fields carried by rewritten copies of recordings that did not run
# them: the readers take the recorded bytes, so the walk reads them exactly as it
# would a recording that ran them. The two tactical values are built; the tests
# that need a builder's refusal plant them back as unbuilt (_plant_unbuilt).
_PENDING_TACTICAL: Final[dict[str, object]] = {
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
}
_PENDING_MEETING_AND_TRIGGER: Final[dict[str, object]] = {
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}


# --------------------------------------------------------------------------- #
# The five profiles                                                           #
# --------------------------------------------------------------------------- #


def _win_condition(directory: Path) -> object:
    return [
        check_replay_win_condition(path, seed=_SEED, **_ROSTER)
        for path in sorted(directory.glob("replay-seed-*.jsonl"))
    ]


#: Each widened reader: its walk profile's name, its field list, and an entry
#: point that walks a whole directory.
_READERS: Final[dict[str, tuple[str, frozenset[str], Callable[[Path], object]]]] = {
    "kill-craft": ("kill-craft", KILL_CRAFT_READS, compute_kill_craft_report),
    "funnel": ("funnel-instrument", FUNNEL_READS, compute_information_funnel),
    "pooling-funnel": ("funnel-instrument", FUNNEL_READS, compute_pooling_funnel),
    "solvability": ("solvability", SOLVABILITY_READS, compute_solvability_report),
    "win-condition": ("win-condition-selfcheck", WIN_CONDITION_READS, _win_condition),
    "evidence-honesty": ("evidence-honesty", HONESTY_READS, compute_evidence_honesty),
}


def test_each_reader_declares_its_fields_and_the_layers_they_cover() -> None:
    profiles: dict[str, ReplayWalkConfig] = {
        "kill-craft": __import__("eval.kill_craft", fromlist=["_"])._WALK_CONFIG,
        "funnel-instrument": funnel._WALK_CONFIG,
        "solvability": __import__("eval.solvability", fromlist=["_"])._WALK_CONFIG,
        "win-condition-selfcheck": __import__(
            "eval.win_condition_selfcheck", fromlist=["_"]
        )._WALK_CONFIG,
        "evidence-honesty": evidence_honesty._WALK_CONFIG,
    }
    for name, reads, _run in _READERS.values():
        profile = profiles[name]
        assert profile.profile == name
        assert profile.supports_experiments
        assert reads <= READABLE_SETTINGS
        assert profile.threaded_layers == layers_read(reads)
        assert not profile.supports_temporal_observations
    for reads in (
        KILL_CRAFT_READS,
        FUNNEL_READS,
        SOLVABILITY_READS,
        WIN_CONDITION_READS,
    ):
        assert reads == READABLE_SETTINGS
    assert HONESTY_READS == READABLE_SETTINGS - {"meeting_reset"}
    assert layers_read(HONESTY_READS) == frozenset(
        {"orchestrator", "tactical", "meeting"}
    )


def test_the_readable_settings_are_the_wave_fields_and_redistribution() -> None:
    wave = {
        "vent_witness_rule",
        "vent_exit_policy",
        "vent_entry_policy",
        "meeting_reset",
        "bounded_rebuttal_version",
        "report_body_handle_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
    }
    assert READABLE_SETTINGS == frozenset(wave | {"redistribution_policy"})
    assert set(READABLE_SETTINGS) <= set(FIELD_LAYER)


#: The arms a fake game records today, the physical vent witness rule included.
_ARMS_TODAY: Final[tuple[str, ...]] = (
    "plain",
    "workload",
    "physical",
    "reset",
    "reset_rebuttal",
    "observed_risk_rebuttal",
)


@pytest.mark.parametrize("reader", sorted(set(_READERS) - {"evidence-honesty"}))
@pytest.mark.parametrize("arm", _ARMS_TODAY)
def test_a_widened_reader_verifies_every_arm_that_exists_today(
    recordings: dict[str, Path], reader: str, arm: str
) -> None:
    _name, _reads, run = _READERS[reader]
    assert run(recordings[arm]) is not None


def _meeting_ids(directory: Path) -> list[str]:
    return [
        row.meeting_id
        for path in sorted(directory.glob("replay-seed-*.jsonl"))
        for row in read_all_entries(path)
        if isinstance(row, MeetingReplayEntry)
    ]


@pytest.mark.parametrize("arm", _ARMS_TODAY)
def test_the_reconstructors_walk_every_meeting_of_every_arm_that_exists_today(
    recordings: dict[str, Path], arm: str
) -> None:
    # The committed-meeting walk and the golden read every readable setting, the
    # meeting reset included, so each walks every recorded meeting of each arm.
    directory = recordings[arm]
    recorded = _meeting_ids(directory)
    assert recorded
    walked = walk_committed_meetings(directory)
    assert [meeting.entry.meeting_id for meeting in walked] == recorded
    walk = golden.walk_directory(directory)
    assert walk.meetings == len(recorded)
    assert walk.prompts and all(prompt.reproduced for prompt in walk.prompts)
    assert walk.miscounted_meetings == ()


_BALLOT_VALUES: Final[dict[str, object]] = {
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}


@pytest.mark.parametrize("arm", ["reset_rebuttal", "observed_risk_rebuttal"])
def test_the_reconstructors_walk_every_meeting_of_a_copy_carrying_the_pending_values(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    arm: str,
) -> None:
    # The pending values each reconstructor reads without reaching a builder that
    # refuses them: the committed-meeting walk builds no agents, so it takes the
    # pending tactical values too; the golden takes the ballot values. (The body
    # handle and the golden's tactical values reach their builders' refusals,
    # pinned below.)
    _open_the_pending_guard(monkeypatch)
    committed_copy = _with_settings(
        recordings[arm],
        tmp_path / "committed" / "9p2i",
        **_PENDING_TACTICAL,
        **_BALLOT_VALUES,
    )
    walked = walk_committed_meetings(committed_copy)
    assert [meeting.entry.meeting_id for meeting in walked] == _meeting_ids(
        committed_copy
    )
    golden_copy = _with_settings(
        recordings[arm], tmp_path / "golden" / "9p2i", **_BALLOT_VALUES
    )
    walk = golden.walk_directory(golden_copy)
    assert walk.meetings == len(_meeting_ids(golden_copy)) > 0
    assert walk.prompts and all(prompt.reproduced for prompt in walk.prompts)
    assert walk.miscounted_meetings == ()


@pytest.mark.parametrize("reader", ["committed-meeting walk", "golden"])
def test_the_reconstructors_hand_the_recorded_witness_rule_to_the_engine_helper(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    reader: str,
) -> None:
    # The recorded witness rule reaches the engine helper; the spy then runs the
    # default rule, which this copy of a default-rule recording holds, so the
    # walk goes on to every meeting. A reader that refused the rule as unread
    # would never call the helper.
    _open_the_pending_guard(monkeypatch)
    copy = _with_settings(
        recordings["plain"], tmp_path / "witness" / "9p2i", vent_witness_rule="physical"
    )
    seen: list[object] = []

    def _spy(config: RecordedExperimentConfig | None) -> object:
        assert config is not None
        seen.append(config.vent_witness_rule)
        return engine_arguments(
            config.model_copy(
                update={
                    "vent_witness_rule": RecordedExperimentConfig.model_fields[
                        "vent_witness_rule"
                    ].default
                }
            )
        )

    monkeypatch.setattr(replay_walk_module, "engine_arguments", _spy)
    monkeypatch.setattr(golden, "engine_arguments", _spy)
    if reader == "golden":
        assert golden.walk_directory(copy).meetings == len(_meeting_ids(copy))
    else:
        walked = walk_committed_meetings(copy)
        assert [meeting.entry.meeting_id for meeting in walked] == _meeting_ids(copy)
    assert seen == ["physical"]


def test_kill_craft_reads_the_regroup_reset_with_every_hash_verified(
    recordings: dict[str, Path],
) -> None:
    report = compute_kill_craft_report(recordings["reset"])
    entries = read_all_entries(next(recordings["reset"].glob("replay-seed-*.jsonl")))
    assert any(row.kind == "meeting" for row in entries)
    assert report.games_total == 1


@pytest.mark.parametrize("reader", sorted(set(_READERS) - {"evidence-honesty"}))
def test_a_widened_reader_verifies_a_copy_carrying_every_wave_value(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    reader: str,
) -> None:
    _open_the_pending_guard(monkeypatch)
    copy = _with_settings(
        recordings["reset_rebuttal"],
        tmp_path / "wave" / "9p2i",
        **_PENDING_TACTICAL,
        **_PENDING_MEETING_AND_TRIGGER,
    )
    _name, _reads, run = _READERS[reader]
    assert run(copy) is not None


def test_honesty_verifies_every_arm_it_reads(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Both honesty walks read the arms, each through its own field-list site:
    # the I-11 cells and the per-decision rebuild.
    for arm in ("plain", "workload", "physical", "observed_risk_rebuttal"):
        assert compute_evidence_honesty(recordings[arm]).games_total == 1
        assert reconstruct_impostor_decisions(recordings[arm], seed=_SEED)
    _open_the_pending_guard(monkeypatch)
    copy = _with_settings(
        recordings["observed_risk_rebuttal"],
        tmp_path / "wave" / "9p2i",
        **_PENDING_MEETING_AND_TRIGGER,
    )
    report = compute_evidence_honesty(copy)
    assert report.impostor_targeting.reconstruction_mismatches == 0
    assert reconstruct_impostor_decisions(copy, seed=_SEED)


@pytest.mark.parametrize("walk", ["cells", "decision rebuild"])
@pytest.mark.parametrize("field", sorted(_PENDING_TACTICAL))
def test_honesty_hands_a_pending_tactical_value_to_the_policy_builder(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    field: str,
    walk: str,
) -> None:
    # With the value planted back as unbuilt, the factory refuses it, so reaching
    # that refusal proves the recorded value passed the walk's field list; a walk
    # that dropped the field would refuse the recording by name first, with a
    # plain ValueError.
    from agents.tactical.experimental import UnbuiltTacticalOptionError

    _plant_unbuilt(monkeypatch)
    value = _PENDING_TACTICAL[field]
    copy = _with_settings(
        recordings["plain"], tmp_path / "tactical" / "9p2i", **{field: value}
    )
    with pytest.raises(
        UnbuiltTacticalOptionError, match=re.escape(f"{field}={value!r}")
    ):
        if walk == "cells":
            compute_evidence_honesty(copy)
        else:
            reconstruct_impostor_decisions(copy, seed=_SEED)


def _advance_refused(*args: object, **kwargs: object) -> object:
    raise AssertionError("a refused recording advanced")


def _refuse_every_advance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(replay_walk_module, "advance_tick", _advance_refused)


@pytest.mark.parametrize("reader", sorted(_READERS))
@pytest.mark.parametrize(
    ("arm", "setting"),
    [
        ("patrol", "crew_idle_policy='patrol'"),
        ("evidence_one", "evidence_reasoning_version=1"),
    ],
)
def test_a_setting_outside_the_reviewed_fields_is_refused_before_the_first_advance(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    reader: str,
    arm: str,
    setting: str,
) -> None:
    name, _reads, run = _READERS[reader]
    _refuse_every_advance(monkeypatch)
    with pytest.raises(ValueError) as refused:
        run(recordings[arm])
    message = str(refused.value)
    assert f"replay profile {name!r}" in message
    assert setting in message


@pytest.mark.parametrize("reader", sorted(_READERS))
def test_a_later_settings_format_is_refused_by_name(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    reader: str,
) -> None:
    copy = _with_settings(
        recordings["reset_rebuttal"], tmp_path / "format" / "9p2i", format_version=2
    )
    name, _reads, run = _READERS[reader]
    _refuse_every_advance(monkeypatch)
    with pytest.raises(ValueError, match=re.escape(f"replay profile {name!r}")) as got:
        run(copy)
    assert "format_version=2" in str(got.value)


def test_honesty_refuses_the_meeting_reset_until_its_room_table_is_coherent(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    _refuse_every_advance(monkeypatch)
    with pytest.raises(ValueError) as refused:
        compute_evidence_honesty(recordings["reset"])
    assert "replay profile 'evidence-honesty'" in str(refused.value)
    assert "meeting_reset='hub_with_grace'" in str(refused.value)
    with pytest.raises(ValueError) as rebuilt:
        reconstruct_impostor_decisions(recordings["reset"], seed=_SEED)
    assert str(rebuilt.value).startswith(
        "replay profile 'evidence-honesty' does not read the recorded "
        "meeting_reset='hub_with_grace'"
    )


def test_the_refusal_checks_the_first_tick_and_passes_every_event_through(
    recordings: dict[str, Path],
) -> None:
    path = next(recordings["workload"].glob("replay-seed-*.jsonl"))
    profile = evidence_honesty._WALK_CONFIG
    walked = list(
        walk_replay(
            path, seed=_SEED, game_map=load_canonical_map(), config=profile, **_ROSTER
        )
    )
    read = list(
        read_recorded_settings(
            walk_replay(
                path,
                seed=_SEED,
                game_map=load_canonical_map(),
                config=profile,
                **_ROSTER,
            ),
            reader="a reader",
            reads=READABLE_SETTINGS,
        )
    )
    assert [type(event) for event in read] == [type(event) for event in walked]
    with pytest.raises(
        ValueError, match="redistribution_policy='least_remaining_work'"
    ):
        next(
            read_recorded_settings(
                iter(walked), reader="a reader", reads=frozenset({"meeting_reset"})
            )
        )


def _exactly(message: str) -> str:
    """A ``match`` pattern that accepts ``message`` and nothing else."""

    return f"^{re.escape(message)}$"


def _workload_walk(recordings: Mapping[str, Path]) -> list[ReplayWalkEvent]:
    path = next(recordings["workload"].glob("replay-seed-*.jsonl"))
    return list(
        walk_replay(
            path,
            seed=_SEED,
            game_map=load_canonical_map(),
            config=evidence_honesty._WALK_CONFIG,
            **_ROSTER,
        )
    )


@pytest.mark.parametrize("lead", [WalkComplete, TickAdvanced, MeetingOpened])
def test_a_leading_event_that_is_not_a_tick_row_passes_and_the_tick_row_refuses(
    recordings: dict[str, Path], lead: type[ReplayWalkEvent]
) -> None:
    # Planted: a stream whose first event is not a TickOpened. The settings are
    # read off a TickOpened only, so the leading event passes through untouched
    # (a WalkComplete carries no row, a TickAdvanced comes after its advance, a
    # MeetingOpened carries a meeting row) and the refusal arrives at the
    # TickOpened after it. An empty replay's walk is led by its WalkComplete.
    walked = _workload_walk(recordings)
    leading = next(event for event in walked if isinstance(event, lead))
    stream = read_recorded_settings(
        iter([leading, *walked]),
        reader="a stream-led reader",
        reads=frozenset({"meeting_reset"}),
    )
    assert next(stream) is leading
    with pytest.raises(
        ValueError,
        match=_exactly(
            "a stream-led reader does not read the recorded "
            "redistribution_policy='least_remaining_work': it reads a recording's "
            "own settings only for meeting_reset"
        ),
    ):
        next(stream)


def test_the_first_tick_row_speaks_for_the_recording(
    recordings: dict[str, Path],
) -> None:
    # Planted: a later tick row carrying a setting the reader does not read. The
    # walk has already checked that every row carries the same settings, so only
    # the first tick row is read and the later one passes through.
    walked = _workload_walk(recordings)
    opened = [
        index for index, event in enumerate(walked) if isinstance(event, TickOpened)
    ]
    assert len(opened) > 1
    later = walked[opened[1]]
    assert isinstance(later, TickOpened)
    planted = dataclasses.replace(
        later,
        entry=later.entry.model_copy(
            update={
                "experiment_config": RecordedExperimentConfig(crew_idle_policy="patrol")
            }
        ),
    )
    stream = [*walked[: opened[1]], planted, *walked[opened[1] + 1 :]]
    read = list(
        read_recorded_settings(iter(stream), reader="a reader", reads=READABLE_SETTINGS)
    )
    assert len(read) == len(stream)
    assert all(got is sent for got, sent in zip(read, stream, strict=True))


def test_an_empty_replay_walks_to_the_vacuous_self_check(tmp_path: Path) -> None:
    # A replay with no rows walks to its WalkComplete alone: there is no tick row
    # to read settings from, so nothing is refused and the check is vacuous.
    path = tmp_path / "replay-seed-2.jsonl"
    path.write_text("", encoding="utf-8")
    walked = list(
        read_recorded_settings(
            walk_replay(
                path,
                seed=2,
                game_map=load_canonical_map(),
                config=win_condition_selfcheck._WALK_CONFIG,
                **_ROSTER,
            ),
            reader="a reader",
            reads=frozenset(),
        )
    )
    assert [type(event) for event in walked] == [WalkComplete]
    assert check_replay_win_condition(path, seed=2, **_ROSTER) == (
        WinConditionSelfCheck(
            game_id="headless-seed-2",
            seed=2,
            winner=None,
            reason=None,
            first_zero_impostor_tick=None,
            game_over_tick=None,
        )
    )


def test_refusing_unread_settings_names_the_reader_and_the_field() -> None:
    config = RecordedExperimentConfig(
        crew_idle_policy="patrol", meeting_reset="hub_with_grace"
    )
    refuse_unread_settings(None, reader="r", reads=frozenset())
    refuse_unread_settings(RecordedExperimentConfig(), reader="r", reads=frozenset())
    refuse_unread_settings(
        RecordedExperimentConfig(format_version=2), reader="r", reads=frozenset()
    )
    with pytest.raises(
        ValueError,
        match=_exactly(
            "r does not read the recorded crew_idle_policy='patrol': it reads a "
            "recording's own settings only for " + ", ".join(sorted(READABLE_SETTINGS))
        ),
    ):
        refuse_unread_settings(config, reader="r", reads=READABLE_SETTINGS)
    with pytest.raises(
        ValueError,
        match=_exactly(
            "replay profile 'solvability' does not read the recorded "
            "self_report=True: it reads a recording's own settings only for "
            "meeting_reset, vent_witness_rule"
        ),
    ):
        refuse_unread_settings(
            RecordedExperimentConfig(self_report=True, meeting_reset="hub_with_grace"),
            reader="replay profile 'solvability'",
            reads=frozenset({"vent_witness_rule", "meeting_reset"}),
        )
    with pytest.raises(
        ValueError,
        match=_exactly(
            "r does not read the recorded meeting_reset='hub_with_grace': it reads "
            "only recordings made without experiment settings"
        ),
    ):
        refuse_unread_settings(
            RecordedExperimentConfig(meeting_reset="hub_with_grace"),
            reader="r",
            reads=frozenset(),
        )
    refuse_unread_settings(
        RecordedExperimentConfig(meeting_reset="hub_with_grace"),
        reader="r",
        reads=frozenset({"meeting_reset"}),
    )


@pytest.mark.parametrize(
    ("reader", "config", "version"),
    [
        (
            "r",
            RecordedExperimentConfig(format_version=2, bounded_rebuttal_version=1),
            2,
        ),
        (
            "replay profile 'kill-craft'",
            RecordedExperimentConfig(format_version=3, evidence_reasoning_version=2),
            3,
        ),
    ],
    ids=["format-2", "format-3"],
)
def test_a_later_settings_format_is_refused_with_the_reader_and_the_format(
    reader: str, config: RecordedExperimentConfig, version: int
) -> None:
    with pytest.raises(
        ValueError,
        match=_exactly(
            f"{reader} does not read the recorded format_version={version}: it "
            "reads recordings made in the first settings format only"
        ),
    ):
        refuse_unread_settings(config, reader=reader, reads=READABLE_SETTINGS)


@pytest.mark.parametrize(
    ("reader", "reads", "outside"),
    [
        ("r", frozenset({"crew_idle_policy"}), "['crew_idle_policy']"),
        (
            "replay profile 'funnel-instrument'",
            frozenset({"self_report", "meeting_reset", "crew_idle_policy"}),
            "['crew_idle_policy', 'self_report']",
        ),
    ],
    ids=["one-outside", "two-outside"],
)
def test_a_field_list_outside_the_reviewed_set_is_refused_with_the_reader(
    reader: str, reads: frozenset[str], outside: str
) -> None:
    with pytest.raises(
        ValueError,
        match=_exactly(f"{reader} names settings no reader is reviewed for: {outside}"),
    ):
        refuse_unread_settings(None, reader=reader, reads=reads)


# --------------------------------------------------------------------------- #
# Evidence honesty: the recorded policy                                        #
# --------------------------------------------------------------------------- #


def test_honesty_rebuilds_decisions_with_the_recorded_policy(
    recordings: dict[str, Path],
) -> None:
    directory = recordings["observed_risk_rebuttal"]
    recorded = compute_evidence_honesty(directory).impostor_targeting
    live = compute_evidence_honesty(
        directory, impostor_policy=live_impostor_policy
    ).impostor_targeting
    assert recorded.policy_mode == RECORDED_ARM_POLICY_FOLD
    assert recorded.reconstruction_mismatches == 0
    assert live.policy_mode == LIVE_POLICY_FOLD
    assert live.reconstruction_mismatches > 0
    assert recorded.decisions_reconstructed == live.decisions_reconstructed > 0
    # The two policies disagree at a vent exit, which is where the arm acts.
    by_recorded = reconstruct_impostor_decisions(directory, seed=_SEED)
    by_live = reconstruct_impostor_decisions(
        directory, seed=_SEED, impostor_policy=live_impostor_policy
    )
    disagreements = [
        (left, right)
        for left, right in zip(by_recorded, by_live, strict=True)
        if left.intent != right.intent
    ]
    assert disagreements
    assert all(left.recorded["type"] == "vent" for left, _right in disagreements)


def test_without_a_config_the_default_is_the_live_policy(
    recordings: dict[str, Path],
) -> None:
    directory = recordings["plain"]
    default = compute_evidence_honesty(directory)
    explicit = compute_evidence_honesty(directory, impostor_policy=live_impostor_policy)
    assert default == explicit
    assert default.impostor_targeting.policy_mode == LIVE_POLICY_FOLD


@pytest.mark.parametrize("seed", [_SEED, _SEED + 2])
def test_a_recording_from_a_custom_factory_is_refused_by_name(
    tmp_path: Path, seed: int
) -> None:
    # Two seeds, so the game the refusal names is the recording's own.
    source = tmp_path / "source" / "9p2i"
    record_game(source, seed=seed, config=None)
    target = tmp_path / "custom" / "9p2i"
    target.mkdir(parents=True)
    for name in ("roster.json", "MANIFEST.md"):
        (target / name).write_bytes((source / name).read_bytes())
    for replay in source.glob("replay-seed-*.jsonl"):
        rows = [json.loads(line) for line in replay.read_text().splitlines()]
        for row in rows:
            if row.get("agent_factory_kind") is not None:
                row["agent_factory_kind"] = "custom"
        (target / replay.name).write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
    with pytest.raises(
        EvidenceHonestyReconstructionError,
        match=_exactly(
            f"headless-seed-{seed}: the recording's agents came from a custom "
            "factory, so the impostor policy it ran cannot be rebuilt from its "
            "settings; pass a policy explicitly to fold a counterfactual"
        ),
    ):
        compute_evidence_honesty(target)
    # An explicit policy is the caller's counterfactual, so it still folds.
    folded = compute_evidence_honesty(target, impostor_policy=live_impostor_policy)
    assert folded.impostor_targeting.policy_mode == LIVE_POLICY_FOLD


def test_a_set_whose_games_name_different_policies_raises(
    recordings: dict[str, Path], tmp_path: Path
) -> None:
    mixed = tmp_path / "mixed" / "9p2i"
    record_game(mixed, seed=_SEED, config=None)
    record_game(
        mixed,
        seed=_SEED + 1,
        config=RecordedExperimentConfig(vent_exit_policy="observed_risk"),
    )
    # The only mixed set the recorded policies can make: one game without
    # tactical settings, one with.
    both = sorted([LIVE_POLICY_FOLD, RECORDED_ARM_POLICY_FOLD])
    assert both == ["live-policy-fold", "recorded-arm-policy-fold"]
    with pytest.raises(
        EvidenceHonestyReconstructionError,
        match=_exactly(
            f"{mixed}: its games name different impostor policies ({both}), and "
            "one set's block carries one policy_mode"
        ),
    ):
        compute_evidence_honesty(mixed)


def test_a_living_experimental_policy_receives_the_announced_dead_roster(
    recordings: dict[str, Path],
) -> None:
    options = TacticalExperimentOptions(vent_exit_policy="observed_risk")
    heard: dict[str, tuple[str, ...]] = {}

    class _Listening(ExperimentalImpostorPolicy):
        def note_meeting_concluded(self, *, dead_ids: tuple[str, ...]) -> None:
            heard[self.agent_id] = dead_ids
            super().note_meeting_concluded(dead_ids=dead_ids)

    policies = evidence_honesty._ImpostorPolicies(
        chosen=lambda pid: _Listening(agent_id=pid, options=options),
        impostor_ids=frozenset({"p-1", "p-2", "p-3"}),
        game_id="g",
    )
    entry = next(
        row
        for row in read_all_entries(next(recordings["plain"].glob("*.jsonl")))
        if row.kind == "tick"
    )
    policies.open(entry)
    built = dict(policies.policies)
    assert policies.mode == evidence_honesty.CUSTOM_POLICY_FOLD
    # Opening again, as every later tick does, keeps the policies built once.
    policies.open(entry)
    assert all(policies.policies[pid] is built[pid] for pid in built)
    state = _state_with(alive={"p-1": True, "p-2": False, "p-3": True, "p-4": False})
    policies.meeting_concluded(state)
    assert heard == {"p-1": ("p-2", "p-4"), "p-3": ("p-2", "p-4")}
    plain = evidence_honesty._ImpostorPolicies(
        chosen=live_impostor_policy, impostor_ids=frozenset({"p-1"}), game_id="g"
    )
    plain.open(entry)
    plain.meeting_concluded(state)
    assert type(plain.policies["p-1"]) is ImpostorPolicy


def _state_with(*, alive: Mapping[str, bool]) -> WorldState:
    from orchestrator.seeder import seed_initial_state

    state = seed_initial_state(
        seed=_SEED,
        game_map=load_canonical_map(),
        num_players=len(alive),
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    return dataclasses.replace(
        state,
        players={
            pid: dataclasses.replace(player, alive=alive[pid])
            for pid, player in state.players.items()
        },
    )


# --------------------------------------------------------------------------- #
# The event-level thread-or-refuse test                                        #
# --------------------------------------------------------------------------- #

#: A setting the spine's helper does not thread, added by the planted helper.
_STAND_IN: Final[str] = "stand_in_witness_rule"


def _physical_exits(events: Sequence[object]) -> list[object]:
    """R7's shape on vent exits: witnessed only in the room surfaced into."""

    return [
        dataclasses.replace(
            event, source_witnesses=(), witnesses=event.destination_witnesses
        )
        if isinstance(event, VentExitedEvent)
        else event
        for event in events
    ]


def _without_the_rule(config: RecordedExperimentConfig) -> RecordedExperimentConfig:
    """``config`` with the vent witness rule at its default, as a helper that withheld it."""

    default = RecordedExperimentConfig.model_fields["vent_witness_rule"].default
    return config.model_copy(update={"vent_witness_rule": default})


class _StandIn:
    """The planted helper and the stand-in engine, installed where readers bind them.

    ``rules`` records the vent witness rule each advance handed the real engine.
    ``withhold`` plants a helper that drops the recorded rule before threading.
    """

    def __init__(self, *, withhold: bool = False) -> None:
        self.seen: list[object] = []
        self.rules: list[object] = []
        self.withhold = withhold

    def arguments(self, config: RecordedExperimentConfig | None) -> dict[str, object]:
        if self.withhold and config is not None:
            config = _without_the_rule(config)
        return {**engine_arguments(config), _STAND_IN: "surfaced-room-only"}

    def advance(
        self,
        state: WorldState,
        actions: Sequence[Any],
        *,
        game_map: Any,
        stand_in_witness_rule: str,
        **kwargs: Any,
    ) -> tuple[WorldState, list[object]]:
        self.seen.append(stand_in_witness_rule)
        self.rules.append(kwargs.get("vent_witness_rule"))
        after, events = real_advance_tick(state, actions, game_map=game_map, **kwargs)
        return after, _physical_exits(events)

    def install(self, monkeypatch: pytest.MonkeyPatch, *modules: object) -> None:
        for module in modules:
            monkeypatch.setattr(module, "engine_arguments", self.arguments)
            monkeypatch.setattr(module, "advance_tick", self.advance)


def _ticks(directory: Path) -> int:
    path = next(directory.glob("replay-seed-*.jsonl"))
    return sum(1 for row in read_all_entries(path) if row.kind == "tick")


def test_the_plain_recording_holds_exits_the_stand_in_changes(
    recordings: dict[str, Path],
) -> None:
    from engine.events import VentExitedEvent as Exited

    path = next(recordings["plain"].glob("replay-seed-*.jsonl"))
    exits = [
        event
        for walk_event in walk_replay(
            path,
            seed=_SEED,
            game_map=load_canonical_map(),
            config=evidence_honesty._WALK_CONFIG,
            **_ROSTER,
        )
        if hasattr(walk_event, "events")
        for event in getattr(walk_event, "events")
        if isinstance(event, Exited) and type(walk_event).__name__ == "TickAdvanced"
    ]
    assert exits
    assert any(event.source_witnesses for event in exits)


@pytest.mark.parametrize("reader", sorted(_READERS))
def test_every_widened_reader_threads_the_helpers_arguments_to_every_advance(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, reader: str
) -> None:
    _name, _reads, run = _READERS[reader]
    baseline = run(recordings["plain"])
    stand_in = _StandIn()
    stand_in.install(monkeypatch, replay_walk_module)
    changed = run(recordings["plain"])
    assert stand_in.seen == ["surfaced-room-only"] * _ticks(recordings["plain"])
    if reader in ("kill-craft", "solvability", "win-condition"):
        # These read state and kills only: the stand-in moves no hash and no cell.
        assert changed == baseline


def test_the_funnel_folds_the_stand_ins_vent_witness_lists(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = next(recordings["plain"].glob("replay-seed-*.jsonl"))
    roles = _roles(recordings["plain"])

    def _vents() -> tuple[object, ...]:
        return funnel._walk_game(
            path, seed=_SEED, roles=roles, game_map=load_canonical_map(), **_ROSTER
        ).vent_sightings

    before = _vents()
    _StandIn().install(monkeypatch, replay_walk_module)
    after = _vents()
    assert len(before) == len(after)
    assert before != after


def _roles(directory: Path) -> Mapping[PlayerId, Role]:
    from eval.validity import roles_by_seed

    return roles_by_seed(directory, **_ROSTER, game_map=load_canonical_map())[_SEED]


def _honesty_memories(path: Path) -> dict[str, tuple[object, ...]]:
    """Every agent's memory as the honesty walk's own perception rebuilds it."""

    from observation.service import ObservationService

    game_map = load_canonical_map()
    memories = {f"p-{index}": MemoryStore() for index in range(1, 10)}
    with tempfile.TemporaryDirectory() as audit:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(audit) / "audit.jsonl"
        )
        try:
            for walk_event in walk_replay(
                path,
                seed=_SEED,
                game_map=game_map,
                config=evidence_honesty._WALK_CONFIG,
                **_ROSTER,
            ):
                if isinstance(walk_event, TickOpened):
                    evidence_honesty._perceive_tick(
                        walk_event, service=service, memories=memories
                    )
        finally:
            service.close()
    return {pid: tuple(store.recent(since_tick=0)) for pid, store in memories.items()}


def test_honestys_perception_folds_the_stand_ins_vent_witness_lists(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = next(recordings["plain"].glob("replay-seed-*.jsonl"))
    before = _honesty_memories(path)
    stand_in = _StandIn()
    stand_in.install(monkeypatch, replay_walk_module)
    after = _honesty_memories(path)
    assert stand_in.seen
    assert before != after


def test_the_committed_meeting_walk_threads_the_helper_and_its_vent_records_change(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = recordings["plain"]
    before = walk_committed_meetings(directory)
    stand_in = _StandIn()
    stand_in.install(monkeypatch, replay_walk_module)
    after = walk_committed_meetings(directory)
    assert stand_in.seen == ["surfaced-room-only"] * _ticks(directory)
    assert [m.entry.meeting_id for m in before] == [m.entry.meeting_id for m in after]
    assert [m.vent_witness_records for m in before] != [
        m.vent_witness_records for m in after
    ]


def test_the_golden_threads_the_helper_and_its_rendered_memory_changes(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    path = next(recordings["plain"].glob("replay-seed-*.jsonl"))
    renderers = golden._canonical_renderers()

    def _memories() -> list[tuple[str, ...]]:
        return [
            tuple(participant.rendered_memory for participant in meeting.participants)
            for meeting in golden.walk_replay_meetings(
                path, game_map=load_canonical_map(), renderers_for_set=renderers
            )
        ]

    before = _memories()
    stand_in = _StandIn()
    stand_in.install(monkeypatch, golden)
    after = _memories()
    assert stand_in.seen
    assert len(stand_in.seen) == _ticks(recordings["plain"])
    assert set(stand_in.seen) == {"surfaced-room-only"}
    assert len(before) == len(after)
    assert before != after


@pytest.mark.parametrize("site", ["walk", "golden"])
def test_a_call_site_that_bypasses_the_helper_fails_its_case(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, site: str
) -> None:
    # Perturbed: the stand-in engine without the planted helper, as a call site
    # that dropped the helper's arguments would drive it.
    stand_in = _StandIn()
    module = replay_walk_module if site == "walk" else golden
    monkeypatch.setattr(module, "advance_tick", stand_in.advance)
    path = next(recordings["plain"].glob("replay-seed-*.jsonl"))
    with pytest.raises(TypeError, match=_STAND_IN):
        if site == "walk":
            compute_kill_craft_report(recordings["plain"])
        else:
            list(
                golden.walk_replay_meetings(
                    path,
                    game_map=load_canonical_map(),
                    renderers_for_set=golden._canonical_renderers(),
                )
            )
    assert stand_in.seen == []


def _rebuilt_decisions(directory: Path) -> tuple[ReconstructedDecision, ...]:
    return reconstruct_impostor_decisions(directory, seed=_SEED)


_EVERY_READER: Final[dict[str, Callable[[Path], object]]] = {
    **{name: run for name, (_p, _r, run) in _READERS.items()},
    "committed-meeting walk": walk_committed_meetings,
    "golden": golden.walk_directory,
    # Evidence honesty's per-decision rebuild walks through its own field list.
    "honesty decision rebuild": _rebuilt_decisions,
}


@pytest.mark.parametrize("reader", sorted(_EVERY_READER))
def test_an_engine_setting_the_helper_does_not_thread_is_refused_by_name(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, reader: str
) -> None:
    # Planted: the helper threads no engine field, so the recorded workload rule
    # is one it does not thread. Every reader refuses before its first advance.
    monkeypatch.setattr(experiment_config, "_THREADED_ENGINE_FIELDS", ())
    _refuse_every_advance(monkeypatch)
    monkeypatch.setattr(golden, "advance_tick", _advance_refused)
    with pytest.raises(
        ValueError, match="redistribution_policy='least_remaining_work'"
    ):
        _EVERY_READER[reader](recordings["workload"])


# --------------------------------------------------------------------------- #
# The event-level test on a physical-rule recording                             #
# --------------------------------------------------------------------------- #


def _exits(directory: Path) -> list[VentExitedEvent]:
    path = next(directory.glob("replay-seed-*.jsonl"))
    return [
        event
        for walk_event in walk_replay(
            path,
            seed=_SEED,
            game_map=load_canonical_map(),
            config=evidence_honesty._WALK_CONFIG,
            **_ROSTER,
        )
        if isinstance(walk_event, TickAdvanced)
        for event in walk_event.events
        if isinstance(event, VentExitedEvent)
    ]


def _withhold_the_rule(monkeypatch: pytest.MonkeyPatch) -> None:
    def _withholding(config: RecordedExperimentConfig | None) -> object:
        return engine_arguments(None if config is None else _without_the_rule(config))

    for module in (replay_walk_module, golden):
        monkeypatch.setattr(module, "engine_arguments", _withholding)


def test_the_physical_recording_holds_exits_the_rule_changes(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Non-vacuity: under the recorded rule no exit into another room lists the
    # room left, and withholding the rule gives at least one such exit a
    # witness in the room left, with every hash still verified.
    directory = recordings["physical"]
    physical = _exits(directory)
    assert physical
    assert not any(
        event.source_witnesses
        for event in physical
        if event.source_room != event.destination_room
    )
    _withhold_the_rule(monkeypatch)
    withheld = _exits(directory)
    assert [(e.tick, e.actor) for e in withheld] == [
        (e.tick, e.actor) for e in physical
    ]
    assert any(
        set(event.source_witnesses) - set(event.destination_witnesses)
        for event in withheld
    )


def _digest(reader: str, result: object) -> object:
    """What a reader's result says, with no rendered prompt or transcript in it.

    A failed comparison prints the digest, so the golden's walk is reduced to
    counts, the committed walk to its witness records and each rebuilt decision
    to its memory's size, ranking and intent.
    """

    if reader == "golden":
        walk = cast(golden._SetWalk, result)
        return (
            walk.meetings,
            len(walk.prompts),
            sum(prompt.reproduced for prompt in walk.prompts),
        )
    if reader == "committed-meeting walk":
        return [
            (m.entry.meeting_id, m.vent_witness_records, m.move_witness_records)
            for m in cast(Sequence[CommittedMeeting], result)
        ]
    if reader == "honesty decision rebuild":
        return [
            (d.tick, d.actor, len(d.memory), d.ranked, d.intent)
            for d in cast(Sequence[ReconstructedDecision], result)
        ]
    return result


@pytest.mark.parametrize("withhold", [False, True], ids=["threaded", "withheld"])
@pytest.mark.parametrize("reader", sorted(_EVERY_READER))
def test_on_a_physical_recording_the_stand_in_and_the_rule_reach_every_advance(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    reader: str,
    withhold: bool,
) -> None:
    # The recorded-arm refusals accept the physical rule, and the planted helper
    # hands every advance each reader drives both the stand-in and the recorded
    # rule. The stand-in is the physical rule's shape, so it moves no output.
    # Perturbed: a helper that withholds the rule still verifies every hash, and
    # only the rule the engine received tells the two apart.
    directory = recordings["physical"]
    run = _EVERY_READER[reader]
    baseline = _digest(reader, run(directory))
    stand_in = _StandIn(withhold=withhold)
    stand_in.install(monkeypatch, replay_walk_module, golden)
    changed = _digest(reader, run(directory))
    ticks = _ticks(directory)
    assert stand_in.seen == ["surfaced-room-only"] * ticks
    assert stand_in.rules == ["both_rooms" if withhold else "physical"] * ticks
    assert changed == baseline
    if reader == "golden":
        meetings, prompts, reproduced = cast(tuple[int, int, int], changed)
        assert meetings == len(_meeting_ids(directory)) and reproduced == prompts > 0
    if reader == "honesty decision rebuild":
        assert changed


def _funnel_vents(directory: Path) -> Sized:
    path = next(directory.glob("replay-seed-*.jsonl"))
    return funnel._walk_game(
        path,
        seed=_SEED,
        roles=_roles(directory),
        game_map=load_canonical_map(),
        **_ROSTER,
    ).vent_sightings


def _committed_vent_records(directory: Path) -> Sized:
    return [m.vent_witness_records for m in walk_committed_meetings(directory)]


def _golden_memories(directory: Path) -> Sized:
    path = next(directory.glob("replay-seed-*.jsonl"))
    return [
        tuple(participant.rendered_memory for participant in meeting.participants)
        for meeting in golden.walk_replay_meetings(
            path,
            game_map=load_canonical_map(),
            renderers_for_set=golden._canonical_renderers(),
        )
    ]


#: The readers that fold vent observations, each reduced to what it folds.
_VENT_FOLDS: Final[dict[str, Callable[[Path], Sized]]] = {
    "funnel": _funnel_vents,
    "evidence-honesty": lambda directory: _honesty_memories(
        next(directory.glob("replay-seed-*.jsonl"))
    ),
    "committed-meeting walk": _committed_vent_records,
    "golden": _golden_memories,
}


@pytest.mark.parametrize("reader", sorted(_VENT_FOLDS))
def test_withholding_the_physical_rule_changes_what_a_vent_folding_reader_folds(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, reader: str
) -> None:
    # Perturbed: the same physical recording read through a helper that
    # withholds the rule folds different vent observations, so each folding
    # reader's output follows the recorded rule, not the engine default. Only
    # sizes and one boolean reach an assertion, so a failure prints no rendered
    # memory.
    fold = _VENT_FOLDS[reader]
    threaded = fold(recordings["physical"])
    _withhold_the_rule(monkeypatch)
    withheld = fold(recordings["physical"])
    sizes = (len(threaded), len(withheld))
    assert sizes[0] == sizes[1] > 0
    changed = threaded != withheld
    assert changed, f"{reader} folded the same vent observations under both rules"


# --------------------------------------------------------------------------- #
# The frozen and policy-re-running instruments keep refusing                    #
# --------------------------------------------------------------------------- #

_HISTORICAL: Final[str] = (
    "historical feature reconstruction does not support experimental recordings"
)
_SURROGATE: Final[str] = (
    "frozen surrogate meeting table does not support experimental recordings"
)


def _kept_refusals() -> dict[str, tuple[str, Callable[[Path], object]]]:
    from eval.off_menu import compute_off_menu_report
    from eval.watchability import _reconstruct_game_kills
    from training.anchor_study import walk_corpus_game
    from training.conviction.dataset import build_conviction_table
    from training.surrogate.dataset import build_meeting_table

    def _anchor(directory: Path) -> object:
        return walk_corpus_game(next(directory.glob("replay-seed-*.jsonl")), **_ROSTER)

    def _referee(directory: Path) -> object:
        return _reconstruct_game_kills(
            next(directory.glob("replay-seed-*.jsonl")),
            seed=_SEED,
            roles=_roles(directory),
            game_map=load_canonical_map(),
            **_ROSTER,
        )

    return {
        "off-menu": (_HISTORICAL, compute_off_menu_report),
        "anchor study": (_HISTORICAL, _anchor),
        "surrogate meeting table": (_SURROGATE, build_meeting_table),
        # The conviction table is built through the surrogate meeting table.
        "conviction table": (_SURROGATE, build_conviction_table),
        "watchability referee": (
            "replay profile 'watchability-referee' does not support experimental "
            "recordings",
            _referee,
        ),
    }


@pytest.mark.parametrize("instrument", sorted(_kept_refusals()))
def test_a_frozen_or_policy_rerunning_instrument_keeps_refusing(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, instrument: str
) -> None:
    import eval.off_menu
    import training.anchor_study
    import training.surrogate.dataset

    def _advance(*args: object, **kwargs: object) -> object:
        raise AssertionError("a refused recording advanced")

    for module in (
        replay_walk_module,
        eval.off_menu,
        training.anchor_study,
        training.surrogate.dataset,
    ):
        monkeypatch.setattr(module, "advance_tick", _advance)
    text, run = _kept_refusals()[instrument]
    with pytest.raises(ValueError, match=re.escape(text)):
        run(recordings["reset_rebuttal"])


def test_the_referee_floors_an_experiment_recording(
    recordings: dict[str, Path],
) -> None:
    from eval.watchability import compute_watchability

    report = compute_watchability(recordings["reset_rebuttal"])
    assert not report.referee_passed


# --------------------------------------------------------------------------- #
# Every call site this card owns passes the recorded settings explicitly        #
# --------------------------------------------------------------------------- #

#: The reader modules whose own re-simulation calls this card owns.
_OWNED_SITES: Final[tuple[str, ...]] = (
    "tests/meetings/test_prompt_byte_golden.py",
    "tests/_helpers/committed.py",
    "tests/_helpers/scripted_meeting.py",
)

#: Each call, and the keywords it must pass: the helper's spread for an advance,
#: the recorded reset and redistribution rule for an applied meeting, the
#: recorded trigger setting for a rebuilt trigger.
_REQUIRED: Final[Mapping[str, frozenset[str]]] = MappingProxyType(
    {
        "advance_tick": frozenset(),
        "apply_meeting_result": frozenset({"meeting_reset", "redistribution_policy"}),
        "_build_meeting_trigger": frozenset({"report_body_handle_version"}),
    }
)


def _name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def recorded_setting_problems(source: str) -> tuple[int, list[str]]:
    """(calls found, problems): every owned call must pass the recorded settings.

    An ``advance_tick`` call must take exactly one ``**`` argument that is a call
    to ``engine_arguments`` or a name bound to one, and no engine field by hand;
    ``apply_meeting_result`` and ``_build_meeting_trigger`` must pass their
    recorded-setting keywords explicitly. An aliased import of any of the three
    is a problem, since the scan matches by name.
    """

    tree = ast.parse(source)
    bound = {
        ast.unparse(target)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Call)
        and _name(node.value.func) == "engine_arguments"
        for target in node.targets
    }
    engine_fields = {field for field, layer in FIELD_LAYER.items() if layer == "engine"}
    problems: list[str] = []
    calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in _REQUIRED and alias.asname is not None:
                    problems.append(f"line {node.lineno}: aliased {alias.name}")
        if not isinstance(node, ast.Call):
            continue
        name = _name(node.func)
        if name is None or name not in _REQUIRED:
            continue
        calls += 1
        passed = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
        missing = sorted(_REQUIRED[name] - passed)
        if missing:
            problems.append(f"line {node.lineno}: {name} without {missing}")
        if name != "advance_tick":
            continue
        spread = [keyword.value for keyword in node.keywords if keyword.arg is None]
        by_hand = sorted(passed & engine_fields)
        helper = len(spread) == 1 and (
            (
                isinstance(spread[0], ast.Call)
                and _name(spread[0].func) == "engine_arguments"
            )
            or ast.unparse(spread[0]) in bound
        )
        if not helper or by_hand:
            problems.append(
                f"line {node.lineno}: advance_tick without the helper's arguments "
                f"(by hand: {by_hand})"
            )
    return calls, problems


@pytest.mark.parametrize("module", _OWNED_SITES)
def test_every_owned_call_site_passes_the_recorded_settings(module: str) -> None:
    calls, problems = recorded_setting_problems((_REPO / module).read_text())
    assert problems == []
    if module != "tests/_helpers/scripted_meeting.py":
        assert calls >= 1, f"{module} no longer re-simulates; update the scan"


@pytest.mark.parametrize(
    ("source", "passes"),
    [
        (
            "engine = engine_arguments(config)\n"
            "advance_tick(state, actions, game_map=m, **engine)\n"
            "apply_meeting_result(s, r, game_map=m, redistribution_policy=p,"
            " meeting_reset=q)\n"
            "_build_meeting_trigger(state=s, events=e, report_body_handle_version=v)\n",
            True,
        ),
        ("advance_tick(state, actions, game_map=m)\n", False),
        (
            "advance_tick(state, actions, game_map=m,"
            " redistribution_policy=config.redistribution_policy)\n",
            False,
        ),
        ("options = {}\nadvance_tick(state, actions, game_map=m, **options)\n", False),
        ("apply_meeting_result(s, r, game_map=m, redistribution_policy=p)\n", False),
        ("apply_meeting_result(s, r, game_map=m, meeting_reset=q)\n", False),
        ("_build_meeting_trigger(state=s, events=e)\n", False),
        (
            "from engine.tick import advance_tick as step\nstep(state, actions)\n",
            False,
        ),
    ],
    ids=[
        "all-explicit",
        "bare-advance",
        "advance-by-hand",
        "other-spread",
        "apply-without-reset",
        "apply-without-redistribution",
        "trigger-without-setting",
        "aliased",
    ],
)
def test_the_scan_bites_a_planted_call_site(source: str, passes: bool) -> None:
    _calls, problems = recorded_setting_problems(source)
    assert (problems == []) is passes


# --------------------------------------------------------------------------- #
# The copy this card adds is plain                                             #
# --------------------------------------------------------------------------- #

#: Task and audit identifiers, memo-style short ids, and bare threshold arithmetic.
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"\bTask \d|audit-|\b[ABDR]\d{1,2}\b|[<>]=?\s*\d|\d+\s*/\s*\d+"
)


def copy_problems(texts: Mapping[str, str]) -> list[str]:
    """Every text that carries an identifier or threshold arithmetic."""

    return [
        f"{label}: {match.group(0)!r}"
        for label, text in texts.items()
        for match in [_IDENTIFIER.search(text)]
        if match is not None
    ]


def _raised(run: Callable[[], object]) -> str:
    try:
        run()
    except (ValueError, RuntimeError, SystemExit) as refused:
        return str(refused)
    raise AssertionError("expected a refusal")


def _new_copy(recordings: Mapping[str, Path]) -> dict[str, str]:
    import importlib

    import publish_process_scorecard

    # Imported dynamically, as the extractor's own tests do: audits/workflows/ is
    # not a package, and a static import makes mypy see the file twice.
    facts: Any = importlib.import_module("audits.workflows.extract_gameplay_facts")
    refuse_experiment_settings = facts.refuse_experiment_settings

    parser_help = publish_process_scorecard.__doc__ or ""
    texts: dict[str, str] = {"scorecard module docstring": parser_help}
    for action in _scorecard_actions():
        texts[f"--{action[0]} help"] = action[1]
    texts["unread setting"] = _raised(
        lambda: refuse_unread_settings(
            RecordedExperimentConfig(crew_idle_policy="patrol"),
            reader="replay profile 'kill-craft'",
            reads=READABLE_SETTINGS,
        )
    )
    texts["unread setting, nothing read"] = _raised(
        lambda: refuse_unread_settings(
            RecordedExperimentConfig(meeting_reset="hub_with_grace"),
            reader="the offline lever counterfactual",
            reads=frozenset(),
        )
    )
    texts["later format"] = _raised(
        lambda: refuse_unread_settings(
            RecordedExperimentConfig(format_version=2, bounded_rebuttal_version=1),
            reader="replay profile 'kill-craft'",
            reads=READABLE_SETTINGS,
        )
    )
    texts["outside the reviewed set"] = _raised(
        lambda: refuse_unread_settings(
            None, reader="r", reads=frozenset({"crew_idle_policy"})
        )
    )
    texts["extractor"] = _raised(
        lambda: refuse_experiment_settings(
            3,
            RecordedExperimentConfig(
                meeting_reset="hub_with_grace", bounded_rebuttal_version=1
            ),
        )
    )
    texts["custom factory"] = _raised(
        lambda: compute_evidence_honesty(_custom_copy(recordings["plain"]))
    )
    with tempfile.TemporaryDirectory() as scratch:
        # A directory the caller named is the caller's text, not this card's copy,
        # so each is replaced by a placeholder before the scan, once the refusal
        # is shown to name that directory.
        empty = Path(scratch) / "empty"
        empty.mkdir()
        texts["--set-dir without --json-stdout"] = _parser_refusal(
            ["--set-dir", str(empty)]
        ).replace(str(empty), "DIR")
        no_replay = _parser_refusal(["--set-dir", str(empty), "--json-stdout"])
        assert no_replay.splitlines()[-1].endswith(
            f": error: --set-dir {empty} holds no replay files"
        )
        texts["--set-dir holding no replay"] = no_replay.replace(str(empty), "DIR")
        mixed = Path(scratch) / "mixed" / "9p2i"
        record_game(mixed, seed=_SEED, config=None)
        record_game(
            mixed,
            seed=_SEED + 1,
            config=RecordedExperimentConfig(vent_exit_policy="observed_risk"),
        )
        different = _raised(lambda: compute_evidence_honesty(mixed))
        assert different.startswith(f"{mixed}: its games name different")
        texts["different impostor policies"] = different.replace(str(mixed), "DIR")
    return texts


def _parser_refusal(argv: list[str]) -> str:
    """What the scorecard script prints when its parser refuses ``argv``."""

    import contextlib
    import io

    import publish_process_scorecard

    stderr = io.StringIO()
    with (
        pytest.MonkeyPatch.context() as patch,
        contextlib.redirect_stderr(stderr),
        pytest.raises(SystemExit) as exited,
    ):
        patch.setattr(sys, "argv", ["publish_process_scorecard.py"])
        publish_process_scorecard.main(argv)
    assert exited.value.code == 2
    return stderr.getvalue()


def _custom_copy(source: Path) -> Path:
    target = Path(tempfile.mkdtemp()) / "9p2i"
    target.mkdir()
    for name in ("roster.json", "MANIFEST.md"):
        (target / name).write_bytes((source / name).read_bytes())
    for replay in source.glob("replay-seed-*.jsonl"):
        rows = [json.loads(line) for line in replay.read_text().splitlines()]
        for row in rows:
            if row.get("agent_factory_kind") is not None:
                row["agent_factory_kind"] = "custom"
        (target / replay.name).write_text(
            "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
        )
    return target


def _scorecard_actions() -> Iterator[tuple[str, str]]:
    import argparse

    import publish_process_scorecard

    captured: list[argparse.ArgumentParser] = []
    original = argparse.ArgumentParser.parse_args

    def _capture(self: argparse.ArgumentParser, *args: Any, **kwargs: Any) -> Any:
        captured.append(self)
        raise SystemExit(0)

    argparse.ArgumentParser.parse_args = _capture  # type: ignore[method-assign]
    try:
        try:
            publish_process_scorecard.main([])
        except SystemExit:
            pass
    finally:
        argparse.ArgumentParser.parse_args = original  # type: ignore[method-assign]
    for action in captured[0]._actions:
        if action.help and action.dest in ("set_dir", "json_stdout"):
            yield action.dest.replace("_", "-"), action.help


def test_the_copy_this_card_adds_carries_no_identifier(
    recordings: dict[str, Path],
) -> None:
    texts = _new_copy(recordings)
    # Each text is the refusal it names, so no entry can scan as clean by being
    # empty or by being some other error.
    expected = {
        "--set-dir help": "Fold one replay directory",
        "--json-stdout help": "With --set-dir",
        "extractor": "reads only recordings made without",
        "custom factory": "came from a custom factory",
        "--set-dir without --json-stdout": (
            "error: --set-dir and --json-stdout go together, without --check"
        ),
        "--set-dir holding no replay": "error: --set-dir DIR holds no replay files",
        "different impostor policies": (
            "DIR: its games name different impostor policies"
        ),
    }
    for label, phrase in expected.items():
        assert phrase in texts[label], label
    assert copy_problems(texts) == []


@pytest.mark.parametrize("planted", ["see Task 20.33 for the reason", "the R7 rule"])
def test_the_copy_scan_bites_an_identifier(planted: str) -> None:
    assert copy_problems({"planted": planted}) != []


# --------------------------------------------------------------------------- #
# A module that reuses a widened profile and keeps refusing                     #
# --------------------------------------------------------------------------- #


def test_the_offline_counterfactual_still_refuses_any_recorded_setting(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    import counterfactual_phase20

    assert (
        counterfactual_phase20.walk_set(recordings["plain"], set_name="plain").games
        == 1
    )
    _refuse_every_advance(monkeypatch)
    for arm, setting in (
        ("workload", "redistribution_policy='least_remaining_work'"),
        ("reset_rebuttal", "meeting_reset='hub_with_grace'"),
    ):
        with pytest.raises(ValueError) as refused:
            counterfactual_phase20.walk_set(recordings[arm], set_name=arm)
        assert str(refused.value).startswith(
            f"the offline lever counterfactual does not read the recorded {setting}"
        )
        assert "only recordings made without experiment settings" in str(refused.value)


def test_every_applied_meeting_reaches_the_meeting_concluded_hook(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = recordings["observed_risk_rebuttal"]
    path = next(directory.glob("replay-seed-*.jsonl"))
    meetings = sum(1 for row in read_all_entries(path) if row.kind == "meeting")
    assert meetings > 0
    calls: list[int] = []
    real = evidence_honesty._ImpostorPolicies.meeting_concluded

    def _counting(self: Any, state: WorldState) -> None:
        calls.append(state.tick)
        real(self, state)

    monkeypatch.setattr(
        evidence_honesty._ImpostorPolicies, "meeting_concluded", _counting
    )
    compute_evidence_honesty(directory)
    assert len(calls) == meetings
    calls.clear()
    reconstruct_impostor_decisions(directory, seed=_SEED)
    assert len(calls) == meetings


@pytest.mark.parametrize(
    ("reader", "label"),
    [
        ("committed-meeting walk", "the committed-meeting channel walk"),
        ("golden", "the prompt-byte golden"),
    ],
)
def test_the_reconstructors_refuse_an_unread_setting_by_name(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    reader: str,
    label: str,
) -> None:
    _refuse_every_advance(monkeypatch)
    monkeypatch.setattr(golden, "advance_tick", _advance_refused)
    with pytest.raises(ValueError) as refused:
        _EVERY_READER[reader](recordings["patrol"])
    assert str(refused.value).startswith(
        f"{label} does not read the recorded crew_idle_policy='patrol'"
    )


@pytest.mark.parametrize("reader", ["committed-meeting walk", "golden"])
def test_the_reconstructors_hand_the_recorded_trigger_setting_to_the_builder(
    recordings: dict[str, Path],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    reader: str,
) -> None:
    # A spy on the builder both readers call records the body-handle value each
    # rebuilt trigger received: None on the recording without the setting and
    # the recorded 1 on a copy that records it, where a reader that dropped the
    # value would hand the builder None both times.
    import orchestrator.game as game_module

    real = game_module._build_meeting_trigger
    seen: list[object] = []

    def _spy(**kwargs: Any) -> Any:
        seen.append(kwargs.get("report_body_handle_version"))
        return real(**kwargs)

    monkeypatch.setattr(game_module, "_build_meeting_trigger", _spy)
    monkeypatch.setattr(golden, "_build_meeting_trigger", _spy)
    copy = _with_settings(
        recordings["plain"], tmp_path / "handle" / "9p2i", report_body_handle_version=1
    )
    meetings = len(_meeting_ids(recordings["plain"]))
    assert meetings > 0
    _EVERY_READER[reader](recordings["plain"])
    assert seen == [None] * meetings
    seen.clear()
    _EVERY_READER[reader](copy)
    assert seen == [1] * meetings


def test_the_golden_builds_the_recorded_arms_agents(
    recordings: dict[str, Path], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The default factory builds the experimental policy a recorded tactical
    # setting names, and refuses a value planted back as unbuilt; an agent built
    # without the recorded settings would not reach that refusal.
    from agents.tactical.experimental import UnbuiltTacticalOptionError

    _plant_unbuilt(monkeypatch)
    copy = _with_settings(
        recordings["plain"], tmp_path / "unbuilt" / "9p2i", **_PENDING_TACTICAL
    )
    with pytest.raises(UnbuiltTacticalOptionError, match="vent_exit_policy"):
        golden.walk_directory(copy)
