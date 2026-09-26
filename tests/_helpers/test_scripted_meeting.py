"""The scripted rebuttal game: a real one-reply rebuttal, recorded offline.

The fake provider never accuses anyone, so a fake game never fires the rebuttal
(``bounded_rebuttal_version``). ``tests/_helpers/scripted_meeting.py`` records a
``HeadlessGame`` whose first meeting's turn 1 accuses the opener, from a declared
config and with no environment export, and this module holds what that one
recording must satisfy: every reader takes it, it carries exactly the rebuttal
the selector picks and no other, the rebuttal's prompt reads the charge back, and
the stamps and substrate stay the defaults. A second recording pins the rule the
owner is asked to confirm: the one reply goes to the target of the earliest
unanswered new charge, whoever that is, so an accused non-opener takes it and the
opener takes none.

No test here prints a prompt; every prompt assertion is a containment check.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

from api.replay_loader import ReplayLoader
from eval.evidence_honesty import LIVE_POLICY_FOLD, compute_evidence_honesty
from eval.funnel import compute_information_funnel, compute_pooling_funnel
from eval.kill_craft import compute_kill_craft_report
from eval.solvability import compute_solvability_report
from eval.win_condition_selfcheck import check_replay_win_condition
from meetings.transcript import walk_chain
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import PROMPT_VERSION_SETS
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
    recorded_experiment_config,
)
from tests._helpers.scripted_meeting import (
    ACCUSE_A_NON_OPENER,
    ACCUSE_THE_OPENER,
    PROMPT_SET,
    Accusation,
    ScriptedMeetingClient,
    record_game,
)
from tests.meetings.test_prompt_byte_golden import walk_directory

_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import publish_gameplay_census  # noqa: E402
import publish_process_scorecard  # noqa: E402

#: A 9p2i game whose first meeting has an opener and at least three more speakers.
_SEED = 0
_REBUTTAL = RecordedExperimentConfig(bounded_rebuttal_version=1)


def _record(directory: Path, script: tuple[Accusation, ...], *, rebuttal: bool) -> Path:
    client = ScriptedMeetingClient(script=script)
    path = record_game(
        directory,
        seed=_SEED,
        config=_REBUTTAL if rebuttal else None,
        client=client,
    )
    assert client.scripted_turns == len(script)
    return path


@pytest.fixture(scope="module")
def opener_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _record(
        tmp_path_factory.mktemp("opener") / "9p2i", ACCUSE_THE_OPENER, rebuttal=True
    )


@pytest.fixture(scope="module")
def non_opener_game(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return _record(
        tmp_path_factory.mktemp("non-opener") / "9p2i",
        ACCUSE_A_NON_OPENER,
        rebuttal=True,
    )


def _meetings(path: Path) -> list[MeetingReplayEntry]:
    return [e for e in read_all_entries(path) if isinstance(e, MeetingReplayEntry)]


def _rebuttals(path: Path) -> list[tuple[int, Any]]:
    """Every trailing reply that answers an opt-in turn: (meeting index, turn)."""

    found = []
    for index, meeting in enumerate(_meetings(path)):
        turns = meeting.transcript.turns
        by_id = {turn.turn_id: turn for turn in turns}
        for turn in turns:
            answered = by_id.get(turn.reply_to or "")
            if (
                turn.turn_kind == "reply"
                and answered is not None
                and answered.turn_kind == "opt_in"
            ):
                found.append((index, turn))
    return found


def _living(meeting: MeetingReplayEntry) -> frozenset[str]:
    return frozenset(ballot.voter for ballot in meeting.ballots)


def test_the_game_is_recorded_from_the_declared_config(opener_game: Path) -> None:
    entries = read_all_entries(opener_game)
    assert recorded_experiment_config(entries) == _REBUTTAL
    rows = [e for e in entries if isinstance(e, (ReplayEntry, GameEndReplayEntry))]
    assert rows and all(row.experiment_config == _REBUTTAL for row in rows)


def test_it_loads_in_a_bare_shell_with_its_memory_and_belief_frames(
    opener_game: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os

    for name in list(os.environ):
        if name.startswith("AILIBI_"):
            monkeypatch.delenv(name)
    loader = ReplayLoader(opener_game.parent)
    replay = loader.load_replay(f"headless-seed-{_SEED}")
    assert replay.metadata.outcome_verified
    first = _meetings(opener_game)[0]
    opener = first.transcript.turns[0].speaker
    memory = loader.get_meeting_memory(
        f"headless-seed-{_SEED}", first.meeting_id, opener
    )
    assert memory is not None
    frames = loader.belief_frames(f"headless-seed-{_SEED}")
    assert len(frames) == len(_meetings(opener_game))


def test_exactly_one_rebuttal_by_the_opener_replying_to_turn_one(
    opener_game: Path,
) -> None:
    rebuttals = _rebuttals(opener_game)
    assert len(rebuttals) == 1
    index, turn = rebuttals[0]
    assert index == 0
    turns = _meetings(opener_game)[0].transcript.turns
    assert turn.speaker == turns[0].speaker
    assert turn.reply_to == turns[1].turn_id
    assert turns[-1] == turn


def test_the_rebuttal_prompt_reads_the_charge_back(opener_game: Path) -> None:
    first = _meetings(opener_game)[0]
    ((_index, rebuttal),) = _rebuttals(opener_game)
    charge = ACCUSE_THE_OPENER[0].reason
    prompts = [
        call.prompt for call in first.llm_calls if call.agent_id == rebuttal.speaker
    ]
    # The opener's calls in this meeting, in order: the opening, the reply that
    # reads the charge back, and the ballot. Only the reply puts it to them.
    carrying = [
        index
        for index, prompt in enumerate(prompts)
        if f"The case against you: {charge}" in prompt
    ]
    assert len(prompts) == 3
    assert carrying == [1]


def test_it_stamps_the_default_prompts_and_no_reporter_voice(opener_game: Path) -> None:
    entries = read_all_entries(opener_game)
    default = dict(PROMPT_VERSION_SETS[PROMPT_SET])
    for meeting in _meetings(opener_game):
        assert dict(meeting.prompt_versions) == default
        for call in meeting.llm_calls:
            assert "<who_reported>" not in call.prompt
    stamps = [
        e.substrate_flags
        for e in entries
        if isinstance(e, (ReplayEntry, GameEndReplayEntry)) and e.substrate_flags
    ]
    assert stamps and all(stamp["reporter_reasoning"] is False for stamp in stamps)


def test_every_meeting_walks_its_chain_under_the_recorded_version(
    opener_game: Path,
) -> None:
    version = recorded_experiment_config(read_all_entries(opener_game))
    assert version is not None and version.bounded_rebuttal_version == 1
    for meeting in _meetings(opener_game):
        walk_chain(
            meeting.transcript,
            living_ids=_living(meeting),
            bounded_rebuttal_version=version.bounded_rebuttal_version,
        )
    first = _meetings(opener_game)[0]
    with pytest.raises(ValueError, match="after the chain must be opt_in"):
        walk_chain(first.transcript, living_ids=_living(first))


def test_the_five_widened_walks_read_it(opener_game: Path) -> None:
    directory = opener_game.parent
    assert compute_kill_craft_report(directory).games_total == 1
    assert compute_information_funnel(directory).games_total == 1
    assert compute_pooling_funnel(directory).meetings_total > 0
    assert compute_solvability_report(directory).games_total == 1
    check = check_replay_win_condition(
        opener_game,
        seed=_SEED,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    assert check.is_consistent
    honesty = compute_evidence_honesty(directory)
    assert honesty.impostor_targeting.policy_mode == LIVE_POLICY_FOLD
    assert honesty.games_total == 1


def test_the_golden_re_renders_every_call_once(opener_game: Path) -> None:
    walk = walk_directory(opener_game.parent)
    assert walk.prompts and all(prompt.reproduced for prompt in walk.prompts)
    recorded = Counter(
        call.prompt for meeting in _meetings(opener_game) for call in meeting.llm_calls
    )
    assert Counter(prompt.recorded_prompt for prompt in walk.prompts) == recorded


def test_the_scorecard_set_dir_and_the_census_set_dir_read_it(
    opener_game: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert (
        publish_process_scorecard.main(
            ["--set-dir", str(opener_game.parent), "--json-stdout"]
        )
        == 0
    )
    card = json.loads(capsys.readouterr().out)
    assert card["games"] == 1 and card["meetings"] == len(_meetings(opener_game))
    census = json.loads(publish_gameplay_census.set_dir_json(opener_game.parent))
    assert census["games"] == 1


def test_the_one_reply_goes_to_the_earliest_charge_not_to_the_opener(
    non_opener_game: Path,
) -> None:
    # The deviation from "one reply for the opener": turn 2 accuses turn 1's
    # speaker and turn 3 accuses the opener; the earlier charge wins the slot.
    rebuttals = _rebuttals(non_opener_game)
    assert len(rebuttals) == 1
    index, turn = rebuttals[0]
    turns = _meetings(non_opener_game)[index].transcript.turns
    opener = turns[0].speaker
    assert turn.speaker == turns[1].speaker != opener
    assert turn.reply_to == turns[2].turn_id
    assert sum(1 for t in turns if t.speaker == opener) == 1
    walk_chain(
        _meetings(non_opener_game)[index].transcript,
        living_ids=_living(_meetings(non_opener_game)[index]),
        bounded_rebuttal_version=1,
    )


def test_the_same_script_without_the_setting_records_no_rebuttal(
    tmp_path: Path,
) -> None:
    path = _record(tmp_path / "9p2i", ACCUSE_THE_OPENER, rebuttal=False)
    assert recorded_experiment_config(read_all_entries(path)) is None
    assert _rebuttals(path) == []
    first = _meetings(path)[0]
    with pytest.raises(ValueError, match="records none"):
        walk_chain(
            first.transcript, living_ids=_living(first), bounded_rebuttal_version=1
        )
    walk_chain(first.transcript, living_ids=_living(first))


def _projected_rebuttals(directory: Path) -> dict[str, int]:
    """Count-only: who the selector would give the one reply to, meeting by meeting.

    The manager runs the selector on the turns recorded after the roll call,
    which is every recorded turn of a meeting made without the setting, so this
    projects what version 1 would have granted on those transcripts. Counts
    only; no transcript text leaves this function.
    """

    from engine.world import load_canonical_map
    from eval.validity import resolve_roster_knobs, roles_by_seed
    from meetings.rebuttal import select_bounded_rebuttal
    from meetings.schemas import AccusationClaim

    num_players, num_impostors, tasks = resolve_roster_knobs(directory)
    roles = roles_by_seed(
        directory,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks,
        game_map=load_canonical_map(),
    )
    counts: Counter[str] = Counter()
    for path in sorted(directory.glob("replay-seed-*.jsonl")):
        seed = int(path.stem.rsplit("-", 1)[1])
        for meeting in _meetings(path):
            turns = meeting.transcript.turns
            opener = turns[0].speaker
            accused = any(
                turn.speaker != opener
                and any(
                    isinstance(claim, AccusationClaim) and claim.against == opener
                    for claim in turn.claims
                )
                for turn in turns
            )
            counts["opener_accused"] += int(accused)
            pick = select_bounded_rebuttal(
                meeting.transcript, living_ids=_living(meeting)
            )
            if pick is None:
                continue
            counts["fires"] += 1
            if pick.speaker == opener:
                counts["to_opener"] += 1
            elif roles[seed][pick.speaker] == "IMPOSTOR":
                counts["to_impostor"] += 1
            else:
                counts["to_other_crewmate"] += 1
            counts["opener_accused_loses_slot"] += int(
                accused and pick.speaker != opener
            )
    return dict(counts)


def test_the_rule_the_owner_is_asked_to_confirm_projected_on_the_committed_sets() -> (
    None
):
    # MEASURED, count-only, on the four committed sets: the one reply goes to the
    # opener in most meetings, and to a non-opener (mostly an accused impostor)
    # wherever an earlier new charge named someone else.
    from tests._helpers.committed import COMMITTED_SETS

    projected = {
        f"{directory.parent.name}/{directory.name}": _projected_rebuttals(directory)
        for directory in COMMITTED_SETS
    }
    assert projected["samples/9p2i"] == {
        "fires": 144,
        "to_opener": 123,
        "to_impostor": 19,
        "to_other_crewmate": 2,
        "opener_accused": 125,
        "opener_accused_loses_slot": 2,
    }
    pooled: Counter[str] = Counter()
    for counts in projected.values():
        pooled.update(counts)
    assert dict(pooled) == {
        "fires": 673,
        "to_opener": 548,
        "to_impostor": 113,
        "to_other_crewmate": 12,
        "opener_accused": 561,
        "opener_accused_loses_slot": 13,
    }


def test_a_script_counts_turns_from_each_meetings_opening(tmp_path: Path) -> None:
    # The same accusation scripted for the second meeting fires there and not in
    # the first: a turn call after the ballots opens the next meeting's count.
    second = (
        Accusation(
            meeting=1,
            turn=1,
            against_turn=0,
            reason="you stood over the body before anyone else arrived",
        ),
    )
    path = _record(tmp_path / "9p2i", second, rebuttal=True)
    meetings = _meetings(path)
    assert len(meetings) >= 2
    rebuttals = _rebuttals(path)
    assert [index for index, _turn in rebuttals] == [1]
    _index, turn = rebuttals[0]
    turns = meetings[1].transcript.turns
    assert (turn.speaker, turn.reply_to) == (turns[0].speaker, turns[1].turn_id)
