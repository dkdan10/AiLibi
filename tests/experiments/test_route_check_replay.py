"""The route-check replay: provenance, a faithful walk, each check's reading.

``experiments/lab/route_check_replay.py`` counts, offline, what each candidate
route check would have shown each voter on the committed recordings. These tests
hold it to its card (``tasks/work/route-check-replay.md``): every column is read
from an exact commit, the walk is faithful or the run stops, (a) is built exactly
as the meeting manager builds it, (b) is the recorded field's own rendering, (c)
is a reference reading, the planted route cases tell the checks apart, the
process count reads no role, and the outputs carry counts only.

Columns are read from temporary repositories built here, or from the checkout's
own ``HEAD`` resolved to its sha, so a shallow clone runs every case.
"""

from __future__ import annotations

import json
import pickle
import shutil
import socket
import subprocess
from collections.abc import Callable, Mapping, Sequence
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Final, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import experiments.lab.route_check_replay as rcr
import meetings.corroboration as corroboration
import meetings.manager as manager_module
from agents.memory.episodic import EpisodicEvent
from agents.memory.evidence_context import (
    ingest_public_meeting_roster,
    ingest_public_regroup,
    v2_evidence_context_rows,
)
from agents.memory.store import (
    DEFAULT_TOKEN_BUDGET,
    AgentMemory,
    _latest_self_guard_fields,
    absorb_reported_testimony,
    render_for_prompt,
)
from agents.perception import ingest_packet
from engine.world import load_canonical_map
from engine.entities import Role
from eval.eras import STAGE_B_R2
from eval.gameplay_census import GameFacts, fold_set
from meetings.manager import derive_reported_testimony
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    SawVentObservation,
    VoteBallot,
)
from meetings.transcript import CANONICAL_ROOMS
from observation.packet import GlobalView, ObservationPacket, PlayerView, SelfView
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.replay import (
    derive_regroup_ticks,
    read_all_entries,
    recorded_experiment_config,
)
from tests._helpers.committed import SAMPLES_9P2I, census_inputs, repo_root
from tests.meetings.test_prompt_byte_golden import (
    _canonical_renderers,
    walk_replay_meetings,
)

_PUBLIC_MAP: Final = public_map_from_engine_map(load_canonical_map())
_R1_DIR: Final[Path] = repo_root / "replays" / "candidates" / "stage-b-r1" / "9p2i"
_R1_CONFIG: Final[Path] = repo_root / "replays" / "candidates" / "stage-b-r1"
#: r2 games: seed 0 holds four meetings (regroups from the second on); seed 1
#: holds three; seed 2 holds one, the cheapest whole-game run.
_PARITY_SEED: Final[int] = 0
_WALK_SEED: Final[int] = 1
_RUN_SEED: Final[int] = 2
_SUBJECT: Final[str] = "p-5"
_VOTER: Final[str] = "p-1"


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------


def _saw(subject: str, room: str, tick: int) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room
    )


def _accuses(target: str) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=target, confidence=0.7, reason="movement"
    )


def _turn(
    index: int,
    speaker: str,
    *,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Any, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
        observations=observations,
        claims=claims,
        free_text=f"turn {index} from {speaker}",
    )


def _alibi(subject: str, *legs: tuple[str, int, int]) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        route=tuple(
            AlibiSegment(room=room, from_tick=start, to_tick=end)
            for room, start, end in legs
        ),
    )


def _ballot(voter: str, target: str, reason: str | None) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.8,
        primary_reason_id=reason,
        rationale_text="a recorded rationale long enough to scan for",
    )


def _inputs(
    *turns: MeetingTurn,
    roster: frozenset[str] = frozenset({"p-1", "p-3", "p-7", _SUBJECT}),
    regroup_ticks: frozenset[int] = frozenset(),
    ballots: tuple[VoteBallot, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    ejected: str | None = None,
) -> rcr.MeetingInputs:
    """A meeting with no memories: (a) and (c) read only the transcript."""

    return rcr.MeetingInputs(
        transcript=MeetingTranscript(turns=turns),
        contradictions=contradictions,
        ballots=ballots,
        ejected=ejected,
        opener=turns[0].speaker,
        trigger_kind="emergency",
        roster=roster,
        sighting_records={},
        move_witness_records={},
        regroup_ticks=regroup_ticks,
        first_meeting=False,
        memories={},
        ballot_overrides={},
        ballot_prompts={},
    )


def _pair_transcript(
    first: tuple[str, int], second: tuple[str, int]
) -> tuple[MeetingTurn, ...]:
    """Two speakers place the subject at two room-ticks; the first accuses."""

    return (
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, *first),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw(_SUBJECT, *second),)),
    )


def _global() -> GlobalView:
    return GlobalView(
        tasks_completed=0,
        tasks_total=14,
        task_completion_percent=0.0,
        sabotage_active=False,
        sabotage_kind=None,
    )


def _packet(tick: int, visible: tuple[PlayerView, ...] = ()) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=_VOTER,
        self_state=SelfView(
            room="CAFETERIA",
            role="CREWMATE",
            pending_task_id=None,
            owned_task_ids=(),
            fellow_impostor_ids=(),
        ),
        visible_players=visible,
        visible_bodies=(),
        audible_events=(),
        global_state=_global(),
        cooldown=None,
    )


#: The players every planted memory co-spawns with in the Cafeteria at tick 0.
_SPAWNED: Final[tuple[str, ...]] = ("p-2", "p-3", _SUBJECT, "p-7")


def _memory(version: int | None = None, *, spawn: bool = True) -> AgentMemory:
    """The voter's memory after one perception tick, as production builds it.

    Every player co-spawns in the Cafeteria, so the voter has seen everyone at
    tick 0; ``spawn=False`` leaves the subject unseen for a built-memory case.
    """

    memory = AgentMemory(
        public_map=_PUBLIC_MAP,
        evidence_reasoning_version=2 if version is not None else None,
    )
    visible = tuple(
        PlayerView(id=player, room="CAFETERIA", action=None)
        for player in _SPAWNED
        if spawn or player != _SUBJECT
    )
    ingest_packet(
        packet=_packet(0, visible), memory=memory.episodic, beliefs=memory.beliefs
    )
    return memory


def _see(memory: AgentMemory, tick: int, room: str, action: str | None = None) -> None:
    ingest_packet(
        packet=_packet(tick, (PlayerView(id=_SUBJECT, room=room, action=action),)),
        memory=memory.episodic,
        beliefs=memory.beliefs,
    )


def _sighting_memory(
    first: tuple[str, int], second: tuple[str, int], *, regroup: int | None = None
) -> AgentMemory:
    """The voter's own plain sightings of the subject at two room-ticks."""

    memory = _memory()
    _see(memory, first[1], first[0])
    if regroup is not None:
        ingest_public_regroup(
            memory, tick=regroup, room="CAFETERIA", player_ids=(_VOTER, _SUBJECT)
        )
    if second[1] != regroup:
        _see(memory, second[1], second[0])
    return memory


def _b_lines(memory: AgentMemory, *, snapshot: bool) -> tuple[rcr.TravelLine, ...]:
    reading = rcr.b_voter_reading(
        memory, voter=_VOTER, snapshot=snapshot, suspicion_override=None
    )
    return tuple(line for line in reading.lines if line.subject == _SUBJECT)


def _pair_verdicts(
    memory: AgentMemory, first: int, second: int, *, snapshot: bool
) -> list[str]:
    """The verdicts of the subject's lines whose ends sit at these two ticks."""

    return [
        line.verdict
        for line in _b_lines(memory, snapshot=snapshot)
        if line.ends is not None
        and (line.ends[0].tick, line.ends[1].tick) == (first, second)
    ]


# ---------------------------------------------------------------------------
# Temporary repositories holding one column each
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=route-check test",
            "-c",
            "user.email=route-check@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _column_repo(
    root: Path, *, seeds: Sequence[int] = (_RUN_SEED,), with_r1: bool = False
) -> tuple[Path, str]:
    """A git repository holding r2 games (and optionally r1's) at their real paths."""

    repo = root / "repo"
    target = repo / "replays" / "samples" / "9p2i"
    target.mkdir(parents=True)
    for name in ("MANIFEST.md", "roster.json", "experiment-config.json"):
        shutil.copy(SAMPLES_9P2I / name, target / name)
    for seed in seeds:
        shutil.copy(SAMPLES_9P2I / f"replay-seed-{seed}.jsonl", target)
    if with_r1:
        r1 = repo / "replays" / "candidates" / "stage-b-r1" / "9p2i"
        r1.mkdir(parents=True)
        for name in ("MANIFEST.md", "roster.json"):
            shutil.copy(_R1_DIR / name, r1 / name)
        shutil.copy(
            _R1_CONFIG / "experiment-config.json", r1.parent / "experiment-config.json"
        )
        for seed in seeds:
            shutil.copy(_R1_DIR / f"replay-seed-{seed}.jsonl", r1)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "column")
    return repo, _git(repo, "rev-parse", "HEAD")


def _run(repo: Path, out: Path, *sets: str) -> int:
    return rcr.main(
        [
            *(item for spec in sets for item in ("--set", spec)),
            "--out-json",
            str(out / "results.json"),
            "--out-report",
            str(out / "report.md"),
            "--repo",
            str(repo),
        ]
    )


def _check(repo: Path, out: Path, json_path: Path | None = None) -> int:
    return rcr.main(
        [
            "--check",
            "--json",
            str(json_path or out / "results.json"),
            "--report",
            str(out / "report.md"),
            "--repo",
            str(repo),
        ]
    )


@pytest.fixture(scope="module")
def one_game_run(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path, str]:
    """One r2 game read through the CLI from a temporary repository."""

    root = tmp_path_factory.mktemp("one-game")
    repo, sha = _column_repo(root)
    out = root / "out"
    out.mkdir()
    assert _run(repo, out, f"r2={sha[:10]}:replays/samples/9p2i") == 0
    return repo, out, sha


# ---------------------------------------------------------------------------
# Columns with exact provenance
# ---------------------------------------------------------------------------


def test_the_checkouts_head_resolves_to_its_full_sha_and_tree() -> None:
    head = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source = rcr.resolve_column(
        repo_root, rcr.ColumnRequest("r2", head[:12], "replays/samples/9p2i")
    )
    tree = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", f"{head}:replays/samples/9p2i"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert (source.sha, source.tree, source.commit) == (head, tree, head[:12])


def test_a_run_records_each_columns_sha_tree_and_config(
    one_game_run: tuple[Path, Path, str],
) -> None:
    repo, out, sha = one_game_run
    payload = json.loads((out / "results.json").read_text())
    (column,) = payload["columns"]
    assert column["sha"] == sha and column["commit"] == sha[:10]
    assert column["tree"] == _git(repo, "rev-parse", f"{sha}:replays/samples/9p2i")
    assert column["recorded_experiment_config"] == json.loads(
        (SAMPLES_9P2I / "experiment-config.json").read_text()
    )
    assert column["declared_config"] == "replays/samples/9p2i/experiment-config.json"


def test_check_reproduces_a_run_from_its_recorded_sha(
    one_game_run: tuple[Path, Path, str],
) -> None:
    repo, out, _ = one_game_run
    assert _check(repo, out) == 0


def test_r1s_tree_under_the_r2_label_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path, with_r1=True)
    code = _run(repo, tmp_path, f"r2={sha}:replays/candidates/stage-b-r1/9p2i")
    assert code == 1
    assert "column r2: seed 2 recorded settings that differ" in capsys.readouterr().err


def test_an_unknown_commit_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _ = _column_repo(tmp_path)
    assert _run(repo, tmp_path, "r2=0123456789abcdef:replays/samples/9p2i") == 1
    assert "commit '0123456789abcdef' does not resolve" in capsys.readouterr().err


def test_a_tree_named_as_the_commit_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    tree = _git(repo, "rev-parse", f"{sha}^{{tree}}")
    assert _run(repo, tmp_path, f"r2={tree}:replays/samples/9p2i") == 1
    assert f"commit '{tree}' does not resolve to a commit" in capsys.readouterr().err


def test_the_r2_config_is_read_from_the_era_registry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, sha = _column_repo(tmp_path)
    moved = replace(STAGE_B_R2, declared_config="replays/samples/9p2i/moved.json")
    monkeypatch.setattr(rcr, "STAGE_B_R2", moved)
    assert rcr.declared_config_path("r2") == "replays/samples/9p2i/moved.json"
    assert _run(repo, tmp_path, f"r2={sha}:replays/samples/9p2i") == 1
    assert "moved.json" in capsys.readouterr().err


def test_a_path_that_does_not_resolve_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    assert _run(repo, tmp_path, f"r2={sha}:replays/samples/4p1i") == 1
    assert "path 'replays/samples/4p1i' does not resolve" in capsys.readouterr().err


def test_a_request_to_pool_columns_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    spec = f"r2={sha}:replays/samples/9p2i"
    assert _run(repo, tmp_path, spec, spec) == 1
    assert "never pooled" in capsys.readouterr().err


def test_an_unknown_label_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    assert _run(repo, tmp_path, f"r3={sha}:replays/samples/9p2i") == 1
    assert "column label 'r3'" in capsys.readouterr().err


@pytest.mark.parametrize(
    "text", ("r2", "r2=", "r2=abc", "r2=abc:", "=abc:replays", "r2=:replays")
)
def test_a_malformed_column_request_is_refused(text: str) -> None:
    with pytest.raises(rcr.RouteCheckReplayError, match="expected LABEL=COMMIT:PATH"):
        rcr.parse_column_request(text)


def test_a_column_path_is_recorded_without_a_trailing_slash() -> None:
    request = rcr.parse_column_request("r2=abc:replays/samples/9p2i/")
    assert request == rcr.ColumnRequest("r2", "abc", "replays/samples/9p2i")


def test_a_path_that_names_a_file_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    assert _run(repo, tmp_path, f"r2={sha}:replays/samples/9p2i/roster.json") == 1
    assert "is a blob, not a directory" in capsys.readouterr().err


def test_r2s_tree_under_the_s9_label_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path)
    assert _run(repo, tmp_path, f"s9={sha}:replays/samples/9p2i") == 1
    err = capsys.readouterr().err
    assert "column s9: seed 2 recorded settings" in err
    assert "(no experiment config)" in err


def test_a_declared_config_that_is_no_config_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, _ = _column_repo(tmp_path)
    (repo / "replays" / "samples" / "9p2i" / "experiment-config.json").write_text(
        '{"format_version": 1, "kill_cooldown_ticks": "six"}\n'
    )
    _git(repo, "commit", "-q", "-am", "a broken config")
    sha = _git(repo, "rev-parse", "HEAD")
    assert _run(repo, tmp_path, f"r2={sha}:replays/samples/9p2i") == 1
    assert "is no experiment config" in capsys.readouterr().err


def test_check_takes_no_columns_from_the_command_line(
    one_game_run: tuple[Path, Path, str], capsys: pytest.CaptureFixture[str]
) -> None:
    repo, out, sha = one_game_run
    code = rcr.main(
        [
            "--check",
            "--set",
            f"r2={sha}:replays/samples/9p2i",
            "--json",
            str(out / "results.json"),
            "--report",
            str(out / "report.md"),
            "--repo",
            str(repo),
        ]
    )
    assert code == 1
    assert "never from --set" in capsys.readouterr().err


def test_a_recorded_tree_id_that_is_not_the_shas_tree_fails_check(
    one_game_run: tuple[Path, Path, str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, out, _ = one_game_run
    payload = json.loads((out / "results.json").read_text())
    payload["columns"][0]["tree"] = "0" * 40
    copy = tmp_path / "results.json"
    copy.write_text(rcr.serialize(payload))
    assert _check(repo, out, copy) == 1
    assert "column r2: the recorded tree id" in capsys.readouterr().err


def test_one_count_edited_in_a_copy_of_the_json_fails_check(
    one_game_run: tuple[Path, Path, str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, out, _ = one_game_run
    payload = json.loads((out / "results.json").read_text())
    payload["columns"][0]["all"]["charges"] += 1
    copy = tmp_path / "results.json"
    copy.write_text(rcr.serialize(payload))
    assert _check(repo, out, copy) == 1
    assert "the recomputed JSON differs" in capsys.readouterr().err


def test_a_later_commit_that_rewrites_the_column_leaves_check_green(
    tmp_path: Path,
) -> None:
    repo, sha = _column_repo(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    assert _run(repo, out, f"r2={sha}:replays/samples/9p2i") == 0
    column = repo / "replays" / "samples" / "9p2i"
    (column / f"replay-seed-{_RUN_SEED}.jsonl").unlink()
    shutil.copy(SAMPLES_9P2I / f"replay-seed-{_WALK_SEED}.jsonl", column)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "a different game in the column")
    assert _check(repo, out) == 0


def test_a_file_committed_into_the_column_after_the_run_leaves_check_green(
    tmp_path: Path,
) -> None:
    repo, sha = _column_repo(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    assert _run(repo, out, f"r2={sha}:replays/samples/9p2i") == 0
    later = repo / "replays" / "samples" / "9p2i" / "results-rubric-score.json"
    later.write_text("{}\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "a later file in the column")
    moved = _git(repo, "rev-parse", "HEAD:replays/samples/9p2i")
    assert moved != json.loads((out / "results.json").read_text())["columns"][0]["tree"]
    assert _check(repo, out) == 0


# ---------------------------------------------------------------------------
# A faithful walk, or none
# ---------------------------------------------------------------------------


def _r2_game(seed: int) -> GameFacts:
    (game,) = [g for g in census_inputs(SAMPLES_9P2I).games if g.seed == seed]
    return game


def _game_copy(directory: Path, seed: int) -> Path:
    """A scratch copy of one r2 game beside its roster, which the walk re-seeds from."""

    shutil.copy(SAMPLES_9P2I / "roster.json", directory / "roster.json")
    copy = directory / f"replay-seed-{seed}.jsonl"
    shutil.copy(SAMPLES_9P2I / copy.name, copy)
    return copy


def test_an_unchanged_copy_of_a_game_reads_cleanly(tmp_path: Path) -> None:
    records, _ = rcr.read_game(
        _game_copy(tmp_path, _WALK_SEED),
        label="r2",
        game=_r2_game(_WALK_SEED),
        renderers=_canonical_renderers(),
    )
    assert len(records) == len(_r2_game(_WALK_SEED).meetings)


def _flip_in_line(path: Path, *, kind: str, key: str, after_tick: int = -1) -> None:
    """Swap the case of one letter inside the first ``key`` value of the first
    ``kind`` line later than ``after_tick``."""

    lines = path.read_text().splitlines(keepends=True)
    for number, line in enumerate(lines):
        record = json.loads(line)
        if record.get("kind", "tick") != kind or record["tick"] <= after_tick:
            continue
        start = line.index(f'"{key}":') + len(key) + 3
        position = next(
            index
            for index in range(start + 10, len(line))
            if line[index].isalpha() and line[index - 1] != "\\"
        )
        flipped = line[position].swapcase()
        lines[number] = line[:position] + flipped + line[position + 1 :]
        path.write_text("".join(lines))
        return
    raise AssertionError(f"no {kind} line")


@pytest.mark.parametrize(("seed", "label"), ((_WALK_SEED, "r2"), (_RUN_SEED, "r1")))
def test_a_flipped_byte_in_a_recorded_prompt_raises(
    tmp_path: Path, seed: int, label: str
) -> None:
    copy = _game_copy(tmp_path, seed)
    _flip_in_line(copy, kind="meeting", key="prompt")
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=rf"^{label} seed {seed} meeting 0: \d+ recorded prompt",
    ):
        rcr.read_game(
            copy,
            label=label,
            game=_r2_game(seed),
            renderers=_canonical_renderers(),
        )


def test_a_state_hash_the_walk_cannot_reproduce_raises(tmp_path: Path) -> None:
    copy = _game_copy(tmp_path, _WALK_SEED)
    _flip_in_line(copy, kind="tick", key="state_hash")
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"r2 seed 1 meeting 0: the walk did not reproduce",
    ):
        rcr.read_game(
            copy,
            label="r2",
            game=_r2_game(_WALK_SEED),
            renderers=_canonical_renderers(),
        )


#: Seed 1's meetings sit at ticks 10, 29 and 41: a flip after tick 29 lands in
#: the walk toward its third meeting, index 2.
_SECOND_MEETING_TICK: Final[int] = 29


def test_a_state_hash_flipped_after_the_second_meeting_names_the_third(
    tmp_path: Path,
) -> None:
    copy = _game_copy(tmp_path, _WALK_SEED)
    _flip_in_line(copy, kind="tick", key="state_hash", after_tick=_SECOND_MEETING_TICK)
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r1 seed 1 meeting 2: the walk did not reproduce the recording \(",
    ):
        rcr.read_game(
            copy,
            label="r1",
            game=_r2_game(_WALK_SEED),
            renderers=_canonical_renderers(),
        )


def test_a_prompt_flipped_in_the_third_meeting_names_it(tmp_path: Path) -> None:
    copy = _game_copy(tmp_path, _WALK_SEED)
    _flip_in_line(copy, kind="meeting", key="prompt", after_tick=_SECOND_MEETING_TICK)
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r1 seed 1 meeting 2: \d+ recorded prompt\(s\) were not re-rendered "
        r"by the walk$",
    ):
        rcr.read_game(
            copy,
            label="r1",
            game=_r2_game(_WALK_SEED),
            renderers=_canonical_renderers(),
        )


def test_a_missed_prompt_count_is_the_meetings_own(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def meeting(recorded: Sequence[str], hit: Sequence[str]) -> SimpleNamespace:
        return SimpleNamespace(
            entry=SimpleNamespace(
                llm_calls=[SimpleNamespace(prompt=prompt) for prompt in recorded]
            ),
            hit_prompts=frozenset(hit),
        )

    walked = (meeting(("a", "b"), ("a", "b")), meeting(("a", "b", "c"), ("a",)))
    monkeypatch.setattr(rcr, "walk_replay_meetings", lambda *a, **k: iter(walked))
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r1 seed 7 meeting 1: 2 recorded prompt\(s\) were not re-rendered "
        r"by the walk$",
    ):
        list(rcr.walk_game(Path("unread.jsonl"), label="r1", seed=7, renderers={}))


def test_a_census_with_one_meeting_removed_raises() -> None:
    game = _r2_game(_WALK_SEED)
    short = replace(game, meetings=game.meetings[:-1])
    with pytest.raises(
        rcr.RouteCheckReplayError, match=r"r2 seed 1 meeting 2: the census holds no"
    ):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_WALK_SEED}.jsonl",
            label="r2",
            game=short,
            renderers=_canonical_renderers(),
        )


def test_a_census_with_one_meeting_more_raises() -> None:
    game = _r2_game(_RUN_SEED)
    longer = replace(game, meetings=(*game.meetings, game.meetings[-1]))
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r2 seed 2 meeting 1: the census holds 2 meetings and the walk read 1$",
    ):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
            label="r2",
            game=longer,
            renderers=_canonical_renderers(),
        )


def _fingerprint(memory: AgentMemory) -> tuple[object, ...]:
    """The live memory's content: its events and its other stores, pickled."""

    return (
        memory.episodic.recent(since_tick=0),
        pickle.dumps(memory.working),
        pickle.dumps(memory.beliefs),
        pickle.dumps(memory.meeting_history),
        memory.evidence_reasoning_version,
    )


def _memories_survive(
    monkeypatch: pytest.MonkeyPatch,
    counting: Callable[..., tuple[rcr.MeetingRecord, frozenset[str]]],
) -> list[bool]:
    survived: list[bool] = []

    def watched(
        inputs: rcr.MeetingInputs, **kwargs: Any
    ) -> tuple[rcr.MeetingRecord, frozenset[str]]:
        before = {pid: _fingerprint(m) for pid, m in inputs.memories.items()}
        result = counting(inputs, **kwargs)
        after = {pid: _fingerprint(m) for pid, m in inputs.memories.items()}
        survived.append(before == after)
        return result

    monkeypatch.setattr(rcr, "read_meeting", watched)
    rcr.read_game(
        SAMPLES_9P2I / f"replay-seed-{_WALK_SEED}.jsonl",
        label="r2",
        game=_r2_game(_WALK_SEED),
        renderers=_canonical_renderers(),
    )
    return survived


def test_counting_leaves_every_live_memory_as_it_was(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    survived = _memories_survive(monkeypatch, rcr.read_meeting)
    assert survived == [True] * len(_r2_game(_WALK_SEED).meetings)


def test_a_counting_step_that_appends_to_a_live_store_fails_the_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = rcr.read_meeting

    def appending(
        inputs: rcr.MeetingInputs, **kwargs: Any
    ) -> tuple[rcr.MeetingRecord, frozenset[str]]:
        result = real(inputs, **kwargs)
        voter = sorted(inputs.memories)[0]
        store = inputs.memories[voter].episodic
        store.append(
            EpisodicEvent(
                tick=store.recent(since_tick=0)[-1].tick,
                type="planted",
                payload={},
                provenance="inferred",
            )
        )
        return result

    assert False in _memories_survive(monkeypatch, appending)


def test_the_rerender_check_pins_the_ballot_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rcr, "DEFAULT_TOKEN_BUDGET", DEFAULT_TOKEN_BUDGET // 4)
    with pytest.raises(
        rcr.RouteCheckReplayError, match="not the ballot's memory block"
    ):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
            label="r2",
            game=_r2_game(_RUN_SEED),
            renderers=_canonical_renderers(),
        )


def _first_meeting(seed: int) -> Any:
    return next(
        iter(
            walk_replay_meetings(
                SAMPLES_9P2I / f"replay-seed-{seed}.jsonl",
                game_map=load_canonical_map(),
                renderers_for_set=_canonical_renderers(),
            )
        )
    )


def test_a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises() -> None:
    meeting = _first_meeting(_RUN_SEED)
    rcr.meeting_inputs(meeting, regroup_ticks=frozenset())
    assert meeting.meeting_id == "headless-seed-2:meeting-0"
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^headless-seed-2:meeting-0: the walk threaded no trigger$",
    ):
        rcr.meeting_inputs(
            replace(meeting, trigger_kind=None), regroup_ticks=frozenset()
        )
    with pytest.raises(rcr.RouteCheckReplayError, match="no ballot render for p-"):
        rcr.meeting_inputs(
            replace(
                meeting,
                renders=tuple(r for r in meeting.renders if r.kind != "vote_ballot"),
            ),
            regroup_ticks=frozenset(),
        )
    unrendered = meeting.participants[3].agent_id
    assert unrendered not in {_VOTER, meeting.participants[0].agent_id}
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=rf"^headless-seed-2:meeting-0: no ballot render for {unrendered}$",
    ):
        rcr.meeting_inputs(
            replace(
                meeting,
                renders=tuple(
                    r
                    for r in meeting.renders
                    if r.kind != "vote_ballot" or r.agent_id != unrendered
                ),
            ),
            regroup_ticks=frozenset(),
        )


def test_a_ledger_bound_that_is_no_integer_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert rcr._ledger_bound("MAP_ARBITRATION_MAX_HOPS") == 1
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_HOPS", "1")
    with pytest.raises(rcr.RouteCheckReplayError, match="is not an integer"):
        rcr._ledger_bound("MAP_ARBITRATION_MAX_HOPS")


def test_meeting_kinds_agree_with_the_census_vent_proof_cells() -> None:
    inputs = census_inputs(SAMPLES_9P2I)
    kinds = [rcr.meeting_kind(m) for game in inputs.games for m in game.meetings]
    cells = fold_set(inputs).cells
    button = cells["button_meetings_with_vent_proof"]
    assert kinds.count("button") == button.denominator
    assert (
        kinds.count("report_vent_proof") + button.numerator
        == cells["meetings_with_vent_proof"].numerator
    )


def test_witness_meetings_read_the_kill_facts_since_the_previous_meeting() -> None:
    inputs = census_inputs(SAMPLES_9P2I)
    found = []
    for game in inputs.games:
        for index, fact in enumerate(game.meetings):
            previous = game.meetings[index - 1].tick if index else None
            if rcr.is_witness_meeting(fact, kills=game.kills, previous_tick=previous):
                found.append((game.seed, index))
    assert len(found) == 14
    for seed, index in ((28, 0), (29, 0), (35, 0), (43, 0), (30, 1)):
        assert (seed, index) in found
    # Without the floor, an earlier kill's witness reports again at a later meeting.
    unbounded = [
        (game.seed, index)
        for game in inputs.games
        for index, fact in enumerate(game.meetings)
        if rcr.is_witness_meeting(fact, kills=game.kills, previous_tick=None)
    ]
    assert set(found) < set(unbounded)


# ---------------------------------------------------------------------------
# (a) as the manager builds it
# ---------------------------------------------------------------------------


def test_the_ledger_call_is_the_managers_own(monkeypatch: pytest.MonkeyPatch) -> None:
    spied: list[tuple[MeetingTranscript, Mapping[str, Any]]] = []
    real = vars(manager_module)["build_testimony_ledger"]

    def spy(transcript: MeetingTranscript, **kwargs: Any) -> Any:
        spied.append((transcript, kwargs))
        return real(transcript, **kwargs)

    monkeypatch.setattr(
        manager_module, "corroboration_discipline_enabled", lambda env=None: True
    )
    monkeypatch.setattr(manager_module, "build_testimony_ledger", spy)
    path = SAMPLES_9P2I / f"replay-seed-{_PARITY_SEED}.jsonl"
    recorded = recorded_experiment_config(read_all_entries(path))
    earlier: list[int] = []
    compared = 0
    for meeting in walk_replay_meetings(
        path, game_map=load_canonical_map(), renderers_for_set=_canonical_renderers()
    ):
        transcript, kwargs = spied[-1]
        manager_call = rcr.LedgerCall(
            transcript=transcript,
            contradictions=tuple(kwargs["contradictions"]),
            sighting_records=kwargs["sighting_records"],
            move_witness_records=kwargs["move_witness_records"],
            opener=kwargs["opener"],
            roster=kwargs["roster"],
            trigger_kind=kwargs["trigger_kind"],
            regroup_ticks=kwargs["regroup_ticks"],
        )
        inputs = rcr.meeting_inputs(
            meeting, regroup_ticks=derive_regroup_ticks(recorded, earlier)
        )
        assert rcr.ledger_call(inputs) == manager_call
        if meeting.meeting_index >= 1:
            assert manager_call.regroup_ticks and manager_call.move_witness_records
            for leg in ("a_no_movement", "a_no_regroup", "a_transcript_only"):
                assert rcr.ledger_call(inputs, leg=leg) != manager_call
            compared += 1
        earlier.append(meeting.entry.tick)
    assert compared == 3


def _a_shown(inputs: rcr.MeetingInputs) -> tuple[tuple[str, str], ...]:
    reading = rcr.a_readings(rcr.ledger_call(inputs)).get(_SUBJECT)
    return () if reading is None else reading.shown


def test_the_tick_bound_is_read_from_the_ledgers_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = _inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 16)))
    assert _a_shown(inputs) == ()
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_TICK_GAP", 2)
    assert _a_shown(inputs) == (("WEST_HALL", "ADMIN"),)


def test_the_hop_bound_is_read_from_the_ledgers_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = _inputs(*_pair_transcript(("ADMIN", 14), ("CAFETERIA", 16)))
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_TICK_GAP", 2)
    assert _a_shown(inputs) == ()
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_HOPS", 2)
    assert _a_shown(inputs) == (("ADMIN", "CAFETERIA"),)


def test_the_subject_cap_is_read_from_the_ledgers_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, "MEDBAY", 14),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw(_SUBJECT, "WEST_HALL", 15),)),
        _turn(2, "p-7", observations=(_saw(_SUBJECT, "ADMIN", 16),)),
        _turn(3, "p-1", observations=(_saw(_SUBJECT, "CAFETERIA", 17),)),
    )
    inputs = _inputs(*turns)
    assert len(_a_shown(inputs)) == 2
    monkeypatch.setattr(corroboration, "MAX_WALKABLE_TRANSITS_PER_SUBJECT", 1)
    assert _a_shown(inputs) == (("MEDBAY", "WEST_HALL"),)


def test_the_unreached_bounds_follow_the_ledgers_namespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    spoken = rcr.spoken_placements(
        MeetingTranscript(turns=_pair_transcript(("WEST_HALL", 14), ("ADMIN", 16)))
    )
    pair = (spoken[0], spoken[1]) if spoken[0].tick == 14 else (spoken[1], spoken[0])
    inputs = _inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 16)))
    reading = rcr.a_readings(rcr.ledger_call(inputs))[_SUBJECT]
    assert rcr._a_pair_reason(pair, reading) == "tick_bound"
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_TICK_GAP", 2)
    reading = rcr.a_readings(rcr.ledger_call(inputs))[_SUBJECT]
    assert reading.shown and rcr._a_pair_reason(pair, reading) == "residual"
    far = _inputs(*_pair_transcript(("LABS", 14), ("ADMIN", 20)))
    far_spoken = rcr.spoken_placements(far.transcript)
    far_pair = (
        (far_spoken[0], far_spoken[1])
        if far_spoken[0].tick == 14
        else (far_spoken[1], far_spoken[0])
    )
    far_reading = rcr.a_readings(rcr.ledger_call(far))[_SUBJECT]
    assert rcr._a_pair_reason(far_pair, far_reading) == "hop_bound"
    monkeypatch.setattr(corroboration, "MAP_ARBITRATION_MAX_HOPS", 9)
    assert rcr._a_pair_reason(far_pair, far_reading) == "tick_bound"


# ---------------------------------------------------------------------------
# The dispute: the s9 agreement
# ---------------------------------------------------------------------------


def _s9_counts(walkable: int, ejections: int) -> dict[str, object]:
    return {
        "walkable_pair": {"a": walkable, "a_transcript_only": walkable - 5},
        "ejections": ejections,
    }


def test_the_s9_agreement_holds_at_the_committed_figure() -> None:
    agreement = rcr.s9_agreement(_s9_counts(13, 90))
    assert agreement["a"] == [13, 90] and agreement["a_transcript_only_agrees"] is False


@pytest.mark.parametrize("found", ((12, 90), (14, 90), (13, 89)))
def test_a_different_s9_figure_stops_the_run(found: tuple[int, int]) -> None:
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=rf"^s9: \(a\) as built reads {found[0]} of {found[1]} ejections with "
        r"a walkable pair; the committed cells say 13 of 90$",
    ):
        rcr.s9_agreement(_s9_counts(*found))


def test_the_s9_expectation_moved_by_one_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rcr, "S9_WALKABLE_PAIR_EJECTIONS", (14, 90))
    with pytest.raises(rcr.RouteCheckReplayError):
        rcr.s9_agreement(_s9_counts(13, 90))


# ---------------------------------------------------------------------------
# (b) as the recorded field renders it, and (b-snapshot)
# ---------------------------------------------------------------------------


def test_each_travel_row_shape_is_classified() -> None:
    memory = _memory()
    _see(memory, 4, "WEST_HALL")
    _see(memory, 5, "ADMIN")
    _see(memory, 9, "CAFETERIA")
    _see(memory, 10, "REACTOR")
    ingest_public_regroup(
        memory, tick=13, room="CAFETERIA", player_ids=(_VOTER, _SUBJECT)
    )
    verdicts = {line.verdict for line in _b_lines(memory, snapshot=False)}
    assert verdicts == {
        "insufficient_timing",
        "fits",
        "cannot_reconcile",
        "crosses_regroup",
    }


def test_an_unverifiable_row_is_classified() -> None:
    # A built memory: the subject is never seen, and one reported claim names them.
    memory = _memory(spawn=False)
    memory.episodic.append(
        EpisodicEvent(
            tick=1,
            type="reported_testimony",
            payload={
                "speaker": "p-3",
                "kind": "saw_player",
                "subject": _SUBJECT,
                "from_tick": 6,
                "to_tick": 6,
                "room": "LABS",
            },
            provenance="reported",
        )
    )
    lines = _b_lines(memory, snapshot=False)
    assert [line.verdict for line in lines] == ["unverifiable"]
    assert lines[0].ends is None and not lines[0].two_rooms


def test_a_travel_row_with_an_altered_suffix_raises() -> None:
    memory = _memory()
    _see(memory, 4, "WEST_HALL")
    _see(memory, 9, "ADMIN")
    (row,) = [
        row
        for row in v2_evidence_context_rows(
            rcr.version_2_view(memory, snapshot=False),
            own_agent_id=_VOTER,
            teammate_ids=frozenset(),
        )
        if row.kind == "travel" and "ADMIN" in row.line
    ]
    assert rcr.classify_travel_row(row.line, memory=memory, kept=True).verdict == "fits"
    with pytest.raises(rcr.RouteCheckReplayError, match="no known walking verdict"):
        rcr.classify_travel_row(row.line[:-1] + ";", memory=memory, kept=True)
    with pytest.raises(rcr.RouteCheckReplayError, match="no known travel-check shape"):
        rcr.classify_travel_row(
            row.line.replace(" to ", " onto "), memory=memory, kept=True
        )
    with pytest.raises(rcr.RouteCheckReplayError, match="does not hold"):
        rcr.classify_travel_row(
            row.line.replace("ADMIN", "LABS"), memory=memory, kept=True
        )


def test_rows_the_budget_sheds_are_offered_but_not_kept() -> None:
    memory = _memory()
    for tick, room in enumerate(("WEST_HALL", "ADMIN", "UPPER_HALL", "CAFETERIA"), 4):
        _see(memory, tick, room)
    roomy = rcr.b_voter_reading(
        memory, voter=_VOTER, snapshot=False, suspicion_override=None
    )
    tight = rcr.b_voter_reading(
        memory, voter=_VOTER, snapshot=False, suspicion_override=None, token_budget=60
    )
    assert len(roomy.lines) == len(tight.lines) >= 3
    assert all(line.kept for line in roomy.lines)
    assert sum(line.kept for line in tight.lines) < len(tight.lines)


def _result(*turns: MeetingTurn) -> MeetingResult:
    speakers = sorted({turn.speaker for turn in turns} | {_VOTER, _SUBJECT})
    return MeetingResult(
        meeting_id="m-1",
        triggered_by=turns[0].speaker,
        trigger_tick=8,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(_ballot(voter, "SKIP", None) for voter in speakers),
        transcript=MeetingTranscript(turns=turns),
    )


def _claims_meeting() -> MeetingResult:
    return _result(
        _turn(
            0,
            "p-3",
            observations=(_saw(_SUBJECT, "LABS", 6),),
            claims=(_alibi(_SUBJECT, ("MEDBAY", 2, 5), ("REACTOR", 6, 7)),),
        ),
        _turn(1, "p-7", observations=(_saw(_SUBJECT, "ADMIN", 7),)),
    )


def test_a_version_none_and_a_version_2_ingestion_give_identical_travel_rows() -> None:
    def ingest(version: int | None) -> AgentMemory:
        memory = _memory(version)
        _see(memory, 3, "WEST_HALL")
        _see(memory, 6, "MEDBAY")
        # The meeting opens at tick 6: the roster is public then, the testimony
        # lands at the boundary after it and the regroup on the resume tick.
        ingest_public_meeting_roster(
            memory,
            tick=6,
            living_ids=(_VOTER, "p-3", _SUBJECT, "p-7"),
            dead_ids=("p-2",),
        )
        absorb_reported_testimony(
            memory,
            statements=derive_reported_testimony(
                _claims_meeting(),
                evidence_reasoning_version=None if version is None else 2,
            ),
        )
        ingest_public_regroup(
            memory,
            tick=7,
            room="CAFETERIA",
            player_ids=(_VOTER, "p-3", _SUBJECT, "p-7"),
        )
        _see(memory, 11, "ADMIN")
        _see(memory, 14, "STORAGE")
        return memory

    def travel(memory: AgentMemory) -> tuple[str, ...]:
        own, teammates = _latest_self_guard_fields(memory.episodic)
        return tuple(
            row.line
            for row in v2_evidence_context_rows(
                memory, own_agent_id=own, teammate_ids=teammates
            )
            if row.kind in ("travel", "travel_contradicted")
        )

    viewed = travel(rcr.version_2_view(ingest(None), snapshot=False))
    native = travel(ingest(2))
    assert viewed == native and len(viewed) >= 6


def test_the_context_reads_claims_of_exactly_the_three_kinds() -> None:
    from meetings.schemas import ReportedStatement

    read: set[str] = set()
    for kind in (
        "saw_player",
        "saw_vent",
        "saw_kill",
        "whereabouts",
        "saw_move",
        "alibi",
        "found_body",
    ):
        memory = _memory()
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p-3",
                    kind=kind,
                    subject=_SUBJECT,
                    from_tick=6,
                    to_tick=6,
                    room="MEDBAY",
                ),
            ),
        )
        if any(line.ends is not None for line in _b_lines(memory, snapshot=False)):
            read.add("alibi_stay" if kind == "alibi" else kind)
    assert read == rcr.B_CLAIM_KINDS


def test_a_claim_held_at_a_first_meeting_raises() -> None:
    memory = _memory()
    inputs = replace(
        _inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 15))),
        first_meeting=True,
        roster=frozenset({_VOTER}),
        memories={_VOTER: memory},
    )
    rcr.require_no_claim_at_first_meeting(inputs)
    absorb_reported_testimony(
        memory, statements=derive_reported_testimony(_claims_meeting())
    )
    with pytest.raises(
        rcr.RouteCheckReplayError, match="reported claim at a first meeting"
    ):
        rcr.require_no_claim_at_first_meeting(inputs)
    rcr.require_no_claim_at_first_meeting(replace(inputs, first_meeting=False))
    named = replace(
        inputs,
        roster=frozenset({_VOTER, "p-7"}),
        memories={_VOTER: _memory(), "p-7": memory},
    )
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^voter p-7 holds a reported claim at a first meeting$",
    ):
        rcr.require_no_claim_at_first_meeting(named)


def test_relabelling_marks_plain_sightings_only() -> None:
    memory = _memory()
    _see(memory, 3, "WEST_HALL")
    _see(memory, 4, "ADMIN", action="task")
    memory.episodic.append(
        EpisodicEvent(
            tick=5,
            type="saw_player_move",
            payload={
                "player_id": _SUBJECT,
                "from_room": "ADMIN",
                "to_room": "UPPER_HALL",
            },
            provenance="observed",
        )
    )
    relabelled = rcr.relabel_plain_sightings(memory.episodic)
    phases = {
        (row.tick, row.type, row.payload.get("action")): row.payload.get(
            "observation_phase"
        )
        for row in relabelled.recent(since_tick=0)
        if row.type in ("saw_player", "saw_player_move")
        and row.payload.get("player_id") == _SUBJECT
    }
    assert phases == {
        (0, "saw_player", None): "snapshot",
        (3, "saw_player", None): "snapshot",
        (4, "saw_player", "task"): None,
        (5, "saw_player_move", None): None,
    }
    original = [row.payload for row in memory.episodic.recent(since_tick=0)]
    assert all("observation_phase" not in payload for payload in original)
    assert [row.observation_id for row in relabelled.recent(since_tick=0)] == [
        row.observation_id for row in memory.episodic.recent(since_tick=0)
    ]


# ---------------------------------------------------------------------------
# (c), the reference reading, and the planted route cases
# ---------------------------------------------------------------------------

#: The card's table: what each check shows for each planted case.
_ROUTE_CASES: Final[Mapping[str, Mapping[str, str]]] = {
    "1": {
        "a": "reconciled",
        "b_unknown": "insufficient timing",
        "b_snapshot": "fits",
        "c": "reconciled",
    },
    "2": {
        "a": "silent",
        "b_unknown": "insufficient timing",
        "b_snapshot": "fits",
        "c": "reconciled",
    },
    "2'": {"a": "silent", "b_unknown": "fits", "b_snapshot": "fits", "c": "reconciled"},
    "3": {
        "a": "silent",
        "b_unknown": "crosses the regroup",
        "b_snapshot": "crosses the regroup",
        "c": "by the regroup",
    },
}

_CASE_PAIRS: Final[Mapping[str, tuple[tuple[str, int], tuple[str, int]]]] = {
    "1": (("WEST_HALL", 14), ("ADMIN", 15)),
    "2": (("ADMIN", 14), ("CAFETERIA", 16)),
    "2'": (("ADMIN", 14), ("CAFETERIA", 17)),
    "3": (("LABS", 10), ("CAFETERIA", 11)),
}

#: Case 3: a meeting closed at tick 10, so the public regroup lands at 11.
_CASE_3_REGROUP: Final[frozenset[int]] = derive_regroup_ticks(
    RecordedExperimentConfig(meeting_reset="hub_with_grace"), (10,)
)


def _case_inputs(case: str) -> rcr.MeetingInputs:
    first, second = _CASE_PAIRS[case]
    if case != "3":
        return _inputs(*_pair_transcript(first, second))
    # The reporter's own route crosses the regroup; a sighting inside the
    # regroup window says where the regroup put them and is dropped.
    return _inputs(
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, "LABS", 10),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw(_SUBJECT, "CAFETERIA", 11),)),
        _turn(
            2,
            _SUBJECT,
            claims=(_alibi(_SUBJECT, ("LABS", 8, 10), ("CAFETERIA", 11, 11)),),
        ),
        regroup_ticks=_CASE_3_REGROUP,
    )


def _a_outcome(case: str) -> str:
    return "reconciled" if _a_shown(_case_inputs(case)) else "silent"


def _c_outcome(case: str) -> str:
    inputs = _case_inputs(case)
    (first, second) = _CASE_PAIRS[case]
    spots = rcr.c_spots(inputs)[_SUBJECT]
    for earlier, later, how in rcr.c_pairs(spots, regroup_ticks=inputs.regroup_ticks):
        if (earlier.tick, later.tick) == (first[1], second[1]) and (
            first[0] in earlier.rooms and second[0] in later.rooms
        ):
            return "reconciled" if how == "walk" else "by the regroup"
    return "silent"


_B_NAMES: Final[Mapping[str, str]] = {
    "fits": "fits",
    "insufficient_timing": "insufficient timing",
    "crosses_regroup": "crosses the regroup",
    "cannot_reconcile": "cannot reconcile",
}


def _b_outcome(case: str, *, snapshot: bool) -> str:
    first, second = _CASE_PAIRS[case]
    regroup = 11 if case == "3" else None
    memory = _sighting_memory(first, second, regroup=regroup)
    found = [
        line
        for line in _b_lines(memory, snapshot=snapshot)
        if line.ends is not None
        and (line.ends[0].tick, line.ends[1].tick) == (first[1], second[1])
    ]
    assert len(found) == 1
    return _B_NAMES[found[0].verdict]


def _outcomes(case: str) -> Mapping[str, str]:
    return {
        "a": _a_outcome(case),
        "b_unknown": _b_outcome(case, snapshot=False),
        "b_snapshot": _b_outcome(case, snapshot=True),
        "c": _c_outcome(case),
    }


@pytest.mark.parametrize("case", sorted(_ROUTE_CASES))
def test_a_planted_route_case_reads_as_the_card_tabulates(case: str) -> None:
    assert _outcomes(case) == _ROUTE_CASES[case]


def test_case_3_drops_the_sighting_inside_the_regroup_window() -> None:
    inputs = _case_inputs("3")
    reading = rcr.a_readings(rcr.ledger_call(inputs))[_SUBJECT]
    assert [(spot.tick, sorted(spot.rooms)) for spot in reading.path] == [
        (10, ["LABS"])
    ]
    open_window = rcr.a_readings(
        rcr.ledger_call(replace(inputs, regroup_ticks=frozenset()))
    )
    assert 11 in {spot.tick for spot in open_window[_SUBJECT].path}


def test_a_pair_the_map_reconciles_reads_as_a_walk_across_a_regroup() -> None:
    inputs = _inputs(
        *_pair_transcript(("ADMIN", 10), ("CAFETERIA", 14)),
        regroup_ticks=frozenset({11}),
    )
    pairs = rcr.c_pairs(
        rcr.c_spots(inputs)[_SUBJECT], regroup_ticks=inputs.regroup_ticks
    )
    assert [how for _, _, how in pairs] == ["walk"]


def test_the_hop_search_is_bounded_by_the_room_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, second = rcr.spoken_placements(
        MeetingTranscript(turns=_pair_transcript(("ADMIN", 14), ("CAFETERIA", 17)))
    )
    assert rcr.reconcilable(first, second, regroup_ticks=frozenset()) == "walk"
    monkeypatch.setattr(rcr, "CANONICAL_ROOMS", frozenset({"ADMIN"}))
    assert rcr.reconcilable(first, second, regroup_ticks=frozenset()) is None


def test_the_planted_cases_tell_every_pair_of_checks_apart() -> None:
    rows = [tuple(_ROUTE_CASES[case].values()) for case in sorted(_ROUTE_CASES)]
    columns = list(zip(*rows, strict=True))
    assert len(set(rows)) == len(rows)
    assert len(set(columns)) == len(columns)


# ---------------------------------------------------------------------------
# Properties over the map
# ---------------------------------------------------------------------------

_ROOMS: Final = st.sampled_from(sorted(CANONICAL_ROOMS))


def _c_rule(first: tuple[str, int], second: tuple[str, int], *, shift: int = 0) -> bool:
    """(c) on two stated placements; ``shift`` moves the later tick (a perturbed bound)."""

    inputs = _inputs(*_pair_transcript(first, (second[0], second[1] + shift)))
    spots = rcr.c_spots(inputs)[_SUBJECT]
    return bool(rcr.c_pairs(spots, regroup_ticks=frozenset()))


def _property_failures(
    first: tuple[str, int], second: tuple[str, int], *, shift: int = 0
) -> list[str]:
    a = bool(_a_shown(_inputs(*_pair_transcript(first, second))))
    memory = _sighting_memory(first, second)
    unknown = set(_pair_verdicts(memory, first[1], second[1], snapshot=False))
    snapshot = set(_pair_verdicts(memory, first[1], second[1], snapshot=True))
    c = _c_rule(first, second, shift=shift)
    failures = []
    if a and not c:
        failures.append("a implies c")
    if "fits" in unknown and not c:
        failures.append("b fits implies c")
    if "cannot_reconcile" in unknown and c:
        failures.append("b cannot implies not c")
    if ("fits" in snapshot) != c:
        failures.append("b snapshot fits iff c")
    return failures


@settings(deadline=None, max_examples=80)
@given(
    rooms=st.lists(_ROOMS, min_size=2, max_size=2, unique=True),
    start=st.integers(min_value=2, max_value=30),
    gap=st.integers(min_value=1, max_value=8),
)
def test_the_checks_order_by_the_map(rooms: list[str], start: int, gap: int) -> None:
    assert _property_failures((rooms[0], start), (rooms[1], start + gap)) == []


@pytest.mark.parametrize("shift", (1, -1))
def test_a_reference_bound_off_by_one_fails_a_property(shift: int) -> None:
    rooms = sorted(CANONICAL_ROOMS)
    failing = [
        (first, second, gap)
        for first in rooms
        for second in rooms
        if first != second
        for gap in range(1, 6)
        if _property_failures((first, 14), (second, 14 + gap), shift=shift)
    ]
    assert failing


# ---------------------------------------------------------------------------
# The process count, role-blind
# ---------------------------------------------------------------------------


def test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, "WEST_HALL", 14),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw(_SUBJECT, "ADMIN", 15),)),
        _turn(2, "p-7", claims=(_accuses(_SUBJECT),)),
    )
    universe = rcr.spoken_placements(MeetingTranscript(turns=turns))
    flag = ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-1:turn-0:obs:0",
        event_b_id="turn:m-1:turn-1:obs:0",
        subjects=(_SUBJECT,),
        description="planted",
    )
    stray = flag.model_copy(update={"event_b_id": "turn:m-1:turn-2:claim:0"})
    elsewhere = flag.model_copy(
        update={"contradiction_id": "c-3", "subjects": ("p-3",)}
    )
    ballots = (
        _ballot("p-3", _SUBJECT, "m-1:turn-0"),
        _ballot("p-7", _SUBJECT, "m-1:turn-2"),
        _ballot("p-1", "SKIP", "m-1:turn-1"),
    )
    charges = rcr.charges_against(
        _SUBJECT,
        ballots=ballots,
        contradictions=(flag, stray, elsewhere),
        universe=universe,
    )
    assert [(c.source, sorted(p.tick for p in c.placements)) for c in charges] == [
        ("ballot", [14]),
        ("flag", [14, 15]),
    ]
    charged = frozenset().union(*(c.placements for c in charges))
    own = rcr.placements_of(universe, _SUBJECT)
    assert len(rcr.misjudging_pairs(own, charged, regroup_ticks=frozenset())) == 1
    assert (
        rcr.misjudging_pairs(
            own,
            frozenset(c for c in charged if c.tick == 99),
            regroup_ticks=frozenset(),
        )
        == ()
    )


def test_the_universe_is_ungated_and_typed() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(
                SawPlayerObservation(
                    type="saw_player",
                    tick=1,
                    subject=_SUBJECT,
                    room="CAFETERIA",
                    co_present=("p-7", _SUBJECT),
                ),
                SawVentObservation(
                    type="saw_vent", tick=12, subject=_SUBJECT, room="MEDBAY"
                ),
                _saw(_SUBJECT, "nowhere in particular", 13),
            ),
            claims=(
                _alibi(_SUBJECT, ("LABS", 2, 4), ("LABS", 5, 9), ("nowhere", 10, 11)),
            ),
        ),
    )
    kinds = sorted(
        (spot.player, spot.kind, spot.tick)
        for spot in rcr.spoken_placements(MeetingTranscript(turns=turns))
    )
    assert kinds == [
        ("p-5", "alibi_stay", 2),
        ("p-5", "alibi_stay", 9),
        ("p-5", "saw_player", 1),
        ("p-5", "saw_vent", 12),
        ("p-7", "company", 1),
    ]


def _one_game_records(
    roles: Mapping[str, Role],
) -> tuple[rcr.MeetingRecord, ...]:
    game = replace(_r2_game(_RUN_SEED), roles=roles)
    records, _ = rcr.read_game(
        SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
        label="r2",
        game=game,
        renderers=_canonical_renderers(),
    )
    return records


def _payload_without_classes(roles: Mapping[str, Role]) -> dict[str, object]:
    source = rcr.ColumnSource("r2", "c", "s" * 40, "replays/samples/9p2i", "t" * 40)
    payload = rcr.column_payload(
        source,
        config=None,
        records=_one_game_records(roles),
        roles={_RUN_SEED: roles},
    )
    payload.pop("classes")
    return payload


def _permuted(impostors: Sequence[str]) -> dict[str, Role]:
    players = sorted(_r2_game(_RUN_SEED).roles)
    return {pid: "IMPOSTOR" if pid in impostors else "CREWMATE" for pid in players}


@settings(deadline=None, max_examples=4)
@given(
    impostors=st.lists(
        st.sampled_from([f"p-{n}" for n in range(1, 10)]),
        min_size=2,
        max_size=2,
        unique=True,
    )
)
def test_permuting_the_roles_moves_only_the_class_columns(impostors: list[str]) -> None:
    recorded = dict(_r2_game(_RUN_SEED).roles)
    assert _payload_without_classes(recorded) == _payload_without_classes(
        _permuted(impostors)
    )


def test_a_role_read_inside_a_line_computation_fails_the_property(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A planted line computation that hides (c)'s lines whenever p-1 is an
    # impostor: the role map now reaches a per-meeting count.
    current: dict[str, Mapping[str, Role]] = {}
    real = rcr.c_pairs

    def role_reading(
        spots: Sequence[rcr.CSpot], *, regroup_ticks: frozenset[int]
    ) -> Any:
        if current["roles"].get("p-1") == "IMPOSTOR":
            return ()
        return real(spots, regroup_ticks=regroup_ticks)

    monkeypatch.setattr(rcr, "c_pairs", role_reading)
    recorded = dict(_r2_game(_RUN_SEED).roles)
    current["roles"] = recorded
    original = _payload_without_classes(recorded)
    toggled = ("p-2", "p-3") if recorded["p-1"] == "IMPOSTOR" else ("p-1", "p-2")
    current["roles"] = _permuted(toggled)
    assert original != _payload_without_classes(current["roles"])


# ---------------------------------------------------------------------------
# Count-only, no model call
# ---------------------------------------------------------------------------


def _forbidden(repo: Path, sha: str) -> frozenset[str]:
    """What the run scans its outputs against, held to an independent reading.

    The game's turn texts and rationales are read straight from the replay; the
    run's own set must hold every one of them, and its travel rows besides.
    """

    source = rcr.resolve_column(
        repo, rcr.ColumnRequest("r2", sha, "replays/samples/9p2i")
    )
    _, forbidden = rcr.run_columns(repo, [source])
    recorded = {
        text
        for entry in read_all_entries(SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl")
        for text in (
            *(
                turn.free_text
                for turn in getattr(entry, "transcript", MeetingTranscript()).turns
            ),
            *(ballot.rationale_text for ballot in getattr(entry, "ballots", ())),
        )
        if len(text) >= 16
    }
    assert recorded and recorded <= forbidden
    assert any(text.startswith("Travel check for") for text in forbidden)
    return forbidden


def test_the_outputs_carry_no_recorded_text(
    one_game_run: tuple[Path, Path, str],
) -> None:
    repo, out, sha = one_game_run
    forbidden = _forbidden(repo, sha)
    assert any("Travel check for" in text for text in forbidden)
    texts = ((out / "results.json").read_text(), (out / "report.md").read_text())
    rcr.scan_outputs(texts, forbidden)


def test_a_rationale_written_into_the_json_fails_the_scan(
    one_game_run: tuple[Path, Path, str],
) -> None:
    repo, out, sha = one_game_run
    forbidden = _forbidden(repo, sha)
    rationale = next(
        ballot.rationale_text
        for entry in read_all_entries(SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl")
        for ballot in getattr(entry, "ballots", ())
        if len(ballot.rationale_text) >= 40
    )
    payload = json.loads((out / "results.json").read_text())
    payload["note"] = rationale
    with pytest.raises(rcr.RouteCheckReplayError, match="carries recorded text"):
        rcr.scan_outputs((rcr.serialize(payload),), forbidden)


def test_a_run_needs_no_network(
    one_game_run: tuple[Path, Path, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    def refused(*args: object, **kwargs: object) -> None:
        raise ConnectionRefusedError("no network in the route-check replay")

    monkeypatch.setattr(socket.socket, "connect", refused)
    monkeypatch.setattr(socket, "create_connection", refused)
    repo, out, _ = one_game_run
    assert _check(repo, out) == 0


# ---------------------------------------------------------------------------
# The dated reading's rule, and the committed artifacts
# ---------------------------------------------------------------------------


def _rule(m: int, w: int, r: Mapping[str, int], r_w: Mapping[str, int]) -> int:
    checks: dict[str, int] = {check: 0 for check in rcr.CHECKS}
    return rcr.reading_branch(
        {"M": m, "W": w, "R": {**checks, **r}, "R_W": {**checks, **r_w}}
    )


def test_the_rule_takes_each_branch() -> None:
    assert _rule(0, 0, {}, {}) == 1
    assert _rule(10, 0, {"b_snapshot": 5}, {}) == 2
    assert _rule(10, 2, {"b_snapshot": 5}, {"b_snapshot": 1}) == 2
    assert _rule(10, 2, {"b_snapshot": 5, "c": 5}, {"b_snapshot": 0, "c": 1}) == 3
    assert _rule(10, 0, {"b_snapshot": 4, "c": 5}, {}) == 3
    assert _rule(10, 0, {"b_snapshot": 4, "c": 4, "b": 10, "a": 10}, {}) == 4


_COMMITTED_JSON: Final[Path] = repo_root / rcr.DEFAULT_JSON


def test_the_committed_reading_takes_the_branch_its_rule_inputs_give() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    labels = [column["label"] for column in payload["columns"]]
    assert labels == ["s9", "r1", "r2"]
    for column in payload["columns"]:
        branch = payload["reading"]["branches"][column["label"]]["branch"]
        assert rcr.reading_branch(column["rule_inputs"]) == branch
        zeroed = json.loads(json.dumps(column["rule_inputs"]))
        for key in ("R", "R_W"):
            zeroed[key] = {check: 0 for check in zeroed[key]}
        assert zeroed["M"] == 0 or rcr.reading_branch(zeroed) == 4


def test_the_committed_report_is_the_committed_jsons_rendering() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    assert rcr.serialize(payload) == _COMMITTED_JSON.read_text()
    assert rcr.render_report(payload) == (repo_root / rcr.DEFAULT_REPORT).read_text()


def test_the_committed_columns_name_full_shas_never_a_symbolic_ref() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    for column in payload["columns"]:
        assert len(column["sha"]) == 40 and int(column["sha"], 16) >= 0
        assert len(column["tree"]) == 40 and int(column["tree"], 16) >= 0
        assert column["commit"] != "HEAD"


def test_the_committed_r2_column_recomputes_from_the_checkouts_bytes() -> None:
    """The committed r2 column is what the instrument reads from these replays today.

    The checkout's ``replays/samples/9p2i`` replays are the bytes the column
    records (nothing under ``replays/`` moved since), so every count of the
    column, case by case and in aggregate, is recomputed here and compared. A
    shallow clone runs it: it reads the working tree, never history.
    """

    payload = json.loads(_COMMITTED_JSON.read_text())
    (committed,) = [column for column in payload["columns"] if column["label"] == "r2"]
    census = census_inputs(SAMPLES_9P2I)
    records, _ = rcr.read_set(SAMPLES_9P2I, label="r2", census=census)
    source = rcr.ColumnSource(
        label="r2",
        commit=committed["commit"],
        sha=committed["sha"],
        path=committed["path"],
        tree=committed["tree"],
    )
    column = rcr.column_payload(
        source,
        config=committed["recorded_experiment_config"],
        records=records,
        roles={game.seed: game.roles for game in census.games},
    )
    assert json.loads(json.dumps(column)) == committed


def test_the_committed_s9_column_meets_the_agreement() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    (s9,) = [column for column in payload["columns"] if column["label"] == "s9"]
    assert s9["s9_agreement"]["a"] == list(rcr.S9_WALKABLE_PAIR_EJECTIONS)
    assert s9["sha"] == "d41c90067a0023d08997231f181cc02deb6461bc"


# ---------------------------------------------------------------------------
# Planted cases the neuter pass called for
# ---------------------------------------------------------------------------


def test_an_r1_column_reads_under_its_rounds_config(tmp_path: Path) -> None:
    repo, sha = _column_repo(tmp_path, with_r1=True)
    assert _run(repo, tmp_path, f"r1={sha}:replays/candidates/stage-b-r1/9p2i") == 0
    (column,) = json.loads((tmp_path / "results.json").read_text())["columns"]
    assert column["declared_config"] == rcr.R1_CONFIG_PATH
    assert column["recorded_experiment_config"] == json.loads(
        (_R1_CONFIG / "experiment-config.json").read_text()
    )


def test_a_pair_out_of_tick_order_is_refused() -> None:
    first, second = rcr.spoken_placements(
        MeetingTranscript(turns=_pair_transcript(("ADMIN", 14), ("CAFETERIA", 17)))
    )
    with pytest.raises(ValueError, match="ordered by tick"):
        rcr.reconcilable(second, first, regroup_ticks=frozenset())


def test_the_first_meeting_is_marked_and_a_later_one_is_not() -> None:
    meeting = _first_meeting(_RUN_SEED)
    assert rcr.meeting_inputs(meeting, regroup_ticks=frozenset()).first_meeting
    later = replace(meeting, meeting_index=1)
    assert not rcr.meeting_inputs(later, regroup_ticks=frozenset()).first_meeting


def test_a_subject_outside_the_roster_gets_no_row() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw("p-9", "WEST_HALL", 14),),
            claims=(_accuses("p-9"),),
        ),
        _turn(1, "p-3", observations=(_saw("p-9", "ADMIN", 15),)),
    )
    assert rcr.a_readings(rcr.ledger_call(_inputs(*turns)))["p-9"].shown == ()
    roster = frozenset({"p-1", "p-3", "p-9"})
    assert rcr.a_readings(rcr.ledger_call(_inputs(*turns, roster=roster)))["p-9"].shown


def test_a_button_meetings_opening_body_is_no_kill_scene() -> None:
    from meetings.schemas import FoundBodyObservation

    opening = _turn(
        0,
        "p-1",
        observations=(
            FoundBodyObservation(
                type="found_body", tick=13, body_of="p-2", room="ADMIN"
            ),
            _saw(_SUBJECT, "ADMIN", 14),
        ),
        claims=(_accuses(_SUBJECT),),
    )
    turns = (opening, _turn(1, "p-3", observations=(_saw(_SUBJECT, "WEST_HALL", 15),)))
    button = _inputs(*turns)
    assert _a_shown(button) == (("ADMIN", "WEST_HALL"),)
    report = replace(button, trigger_kind="report")
    assert _a_shown(report) == ()


def test_a_shown_pair_resting_on_no_stated_pair_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inputs = _inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 16)))
    real = vars(rcr)["build_testimony_ledger"]

    def fabricated(*args: Any, **kwargs: Any) -> Any:
        ledger = real(*args, **kwargs)
        rows = tuple(
            replace(row, walkable_transits=(("WEST_HALL", "ADMIN"),))
            for row in ledger.rows
        )
        return replace(ledger, rows=rows)

    monkeypatch.setattr(rcr, "build_testimony_ledger", fabricated)
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^subject p-5: a shown walkable pair rests on no pair of the stated "
        r"path the ledger read$",
    ):
        rcr.a_readings(rcr.ledger_call(inputs))


def test_a_one_room_line_neither_reaches_nor_counts_two_rooms() -> None:
    memory = _memory()
    _see(memory, 4, "WEST_HALL")
    memory.episodic.append(
        EpisodicEvent(
            tick=5,
            type="reported_testimony",
            payload={
                "speaker": "p-3",
                "kind": "saw_player",
                "subject": _SUBJECT,
                "from_tick": 5,
                "to_tick": 5,
                "room": "WEST_HALL",
            },
            provenance="reported",
        )
    )
    (line,) = [
        line
        for line in _b_lines(memory, snapshot=False)
        if line.ends is not None and (line.ends[0].tick, line.ends[1].tick) == (4, 5)
    ]
    assert line.verdict == "fits" and line.kept
    assert not line.two_rooms and not rcr._reaching(line)


def test_a_regroup_lines_ends_take_their_rooms_from_the_memory() -> None:
    memory = _sighting_memory(("LABS", 10), ("CAFETERIA", 11), regroup=11)
    (line,) = [
        line
        for line in _b_lines(memory, snapshot=False)
        if line.verdict == "crosses_regroup"
    ]
    assert line.ends is not None
    assert [sorted(end.rooms) for end in line.ends] == [["LABS"], ["CAFETERIA"]]
    assert line.two_rooms and line.kept and rcr._reaching(line)


def test_the_b_render_takes_the_voters_pre_vote_suspicion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[Any] = []
    real = vars(rcr)["render_for_prompt"]

    def spy(memory: AgentMemory, **kwargs: Any) -> str:
        seen.append(kwargs.get("suspicion_override"))
        rendered: str = real(memory, **kwargs)
        return rendered

    monkeypatch.setattr(rcr, "render_for_prompt", spy)
    override = {_SUBJECT: 0.25}
    rcr.b_voter_reading(
        _memory(), voter=_VOTER, snapshot=False, suspicion_override=override
    )
    assert seen == [override]


def test_a_qualifying_pair_the_cap_cuts_is_given_the_cap() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, "MEDBAY", 14),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw(_SUBJECT, "WEST_HALL", 15),)),
        _turn(2, "p-7", observations=(_saw(_SUBJECT, "ADMIN", 16),)),
        _turn(3, "p-1", observations=(_saw(_SUBJECT, "UPPER_HALL", 17),)),
    )
    inputs = _inputs(*turns)
    reading = rcr.a_readings(rcr.ledger_call(inputs))[_SUBJECT]
    assert len(reading.qualifying_pairs) == 3 and len(reading.shown) == 2
    by_tick = {spot.tick: spot for spot in rcr.spoken_placements(inputs.transcript)}
    assert rcr._a_pair_reason((by_tick[16], by_tick[17]), reading) == "cap"


def test_an_input_of_a_kind_the_check_is_not_read_to_take_raises() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(
                SawPlayerObservation(
                    type="saw_player",
                    tick=14,
                    subject="p-3",
                    room="ADMIN",
                    co_present=(_SUBJECT,),
                ),
            ),
            claims=(_accuses(_SUBJECT),),
        ),
    )
    inputs = _inputs(*turns)
    universe = rcr.spoken_placements(inputs.transcript)
    paths = {
        subject: [spot.event_id for spot in reading.path]
        for subject, reading in rcr.a_readings(rcr.ledger_call(inputs)).items()
    }
    rcr._require_input_kinds(universe, paths, rcr.A_INPUT_KINDS, check="(a)")
    with pytest.raises(rcr.RouteCheckReplayError, match="not read to take"):
        rcr._require_input_kinds(
            universe, paths, rcr.A_INPUT_KINDS - {"company"}, check="(a)"
        )
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^\(c\) placed p-5 by an event of a kind it is not read to take$",
    ):
        rcr._require_input_kinds(
            universe, paths, rcr.A_INPUT_KINDS - {"company"}, check="(c)"
        )


def test_reading_a_meeting_checks_the_first_meetings_claims_first() -> None:
    memory = _memory()
    absorb_reported_testimony(
        memory, statements=derive_reported_testimony(_claims_meeting())
    )
    inputs = replace(
        _inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 15))),
        first_meeting=True,
        roster=frozenset({_VOTER}),
        memories={_VOTER: memory},
        ballot_overrides={_VOTER: {}},
        ballot_prompts={_VOTER: ()},
    )
    with pytest.raises(rcr.RouteCheckReplayError, match="reported claim at a first"):
        rcr.read_meeting(
            inputs, seed=0, index=0, tick=15, kind="button", witness_meeting=False
        )


def _case_of(
    inputs: rcr.MeetingInputs,
    b_readings: Mapping[bool, Mapping[str, rcr.BVoterReading]] | None = None,
) -> rcr.CaseRecord:
    """One ejection read through the production case reader."""

    spots = rcr.c_spots(inputs)
    return rcr._read_case(
        inputs,
        universe=rcr.spoken_placements(inputs.transcript),
        a_by_leg={
            leg: rcr.a_readings(rcr.ledger_call(inputs, leg=leg)) for leg in rcr.A_LEGS
        },
        spots=spots,
        c_lines={
            subject: rcr.c_pairs(found, regroup_ticks=inputs.regroup_ticks)
            for subject, found in spots.items()
        },
        b_readings=b_readings
        or {
            snapshot: {
                ballot.voter: rcr.b_voter_reading(
                    _memory(),
                    voter=ballot.voter,
                    snapshot=snapshot,
                    suspicion_override=None,
                )
                for ballot in inputs.ballots
            }
            for snapshot in (False, True)
        },
    )


def test_a_line_reaches_only_a_voter_who_voted_to_eject() -> None:
    turns = _pair_transcript(("WEST_HALL", 14), ("ADMIN", 15))
    unvoted = _case_of(_inputs(*turns, ejected=_SUBJECT))
    assert not unvoted.check("a").reaches and not unvoted.check("c").reaches
    voted = _case_of(
        _inputs(*turns, ejected=_SUBJECT, ballots=(_ballot("p-3", _SUBJECT, None),))
    )
    assert voted.check("a").reaches and voted.check("c").reaches


def test_a_button_meetings_ejected_opener_is_no_reporter() -> None:
    turns = _pair_transcript(("WEST_HALL", 14), ("ADMIN", 15))
    ballots = (_ballot("p-3", "p-1", None),)
    button = _inputs(*turns, ejected="p-1", ballots=ballots)
    assert not _case_of(button).reporter
    assert _case_of(replace(button, trigger_kind="report")).reporter


def test_an_insufficient_line_counts_only_over_two_rooms() -> None:
    memory = _memory()
    _see(memory, 4, "WEST_HALL")
    _see(memory, 5, "ADMIN")
    memory.episodic.append(
        EpisodicEvent(
            tick=6,
            type="reported_testimony",
            payload={
                "speaker": "p-3",
                "kind": "saw_player",
                "subject": _SUBJECT,
                "from_tick": 7,
                "to_tick": 7,
                "room": "the vents",
            },
            provenance="reported",
        )
    )
    readings = {
        snapshot: {
            _VOTER: rcr.b_voter_reading(
                memory, voter=_VOTER, snapshot=snapshot, suspicion_override=None
            )
        }
        for snapshot in (False, True)
    }
    insufficient = [
        line
        for line in readings[False][_VOTER].lines
        if line.verdict == "insufficient_timing"
    ]
    assert len(insufficient) == 2 and sum(line.two_rooms for line in insufficient) == 1
    inputs = _inputs(
        *_pair_transcript(("WEST_HALL", 4), ("ADMIN", 5)),
        ejected=_SUBJECT,
        ballots=(_ballot(_VOTER, _SUBJECT, "m-1:turn-0"),),
    )
    assert _case_of(inputs, readings).check("b").insufficient_lines == 1


def test_vent_proof_names_a_living_player_and_a_witness_reports() -> None:
    inputs = census_inputs(SAMPLES_9P2I)
    game = next(g for g in inputs.games if g.seed == 28)
    fact = game.meetings[0]
    assert rcr.is_witness_meeting(fact, kills=game.kills, previous_tick=None)
    button = replace(fact, trigger_kind="emergency")
    assert not rcr.is_witness_meeting(button, kills=game.kills, previous_tick=None)
    living = next(iter(fact.living))
    proof = replace(fact, vent_flag_subjects=(frozenset({living}),))
    assert rcr.meeting_kind(proof) == "report_vent_proof"
    dead = replace(fact, vent_flag_subjects=(frozenset({"p-gone"}),))
    assert rcr.meeting_kind(dead) == "report_no_vent_proof"


def test_a_census_that_names_a_different_meeting_raises() -> None:
    game = _r2_game(_RUN_SEED)
    renamed = replace(
        game, meetings=(replace(game.meetings[0], meeting_id="elsewhere"),)
    )
    with pytest.raises(rcr.RouteCheckReplayError, match="read different meetings"):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
            label="r2",
            game=renamed,
            renderers=_canonical_renderers(),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("meeting_id", "elsewhere"),
        ("opener", "p-gone"),
        ("ejected", "p-gone"),
        ("trigger_kind", "elsewhere"),
    ),
)
def test_a_later_meeting_the_census_reads_differently_is_named(
    field: str, value: str
) -> None:
    game = _r2_game(_WALK_SEED)
    changes: dict[str, Any] = {field: value}
    third = replace(game.meetings[2], **changes)
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r1 seed 1 meeting 2: the census and the walk read different "
        r"meetings$",
    ):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_WALK_SEED}.jsonl",
            label="r1",
            game=replace(game, meetings=(*game.meetings[:2], third)),
            renderers=_canonical_renderers(),
        )


def test_a_census_of_other_seeds_raises(tmp_path: Path) -> None:
    _game_copy(tmp_path, _RUN_SEED)
    with pytest.raises(rcr.RouteCheckReplayError, match="hold different seeds"):
        rcr.read_set(tmp_path, label="r2", census=census_inputs(SAMPLES_9P2I))
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^r1: the census and the set hold different seeds$",
    ):
        rcr.read_set(tmp_path, label="r1", census=census_inputs(SAMPLES_9P2I))


def test_a_turn_text_written_into_the_json_fails_the_scan(
    one_game_run: tuple[Path, Path, str],
) -> None:
    repo, out, sha = one_game_run
    forbidden = _forbidden(repo, sha)
    text = next(
        turn.free_text
        for entry in read_all_entries(SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl")
        if (transcript := getattr(entry, "transcript", None)) is not None
        for turn in transcript.turns
        if len(turn.free_text) >= 40
    )
    payload = json.loads((out / "results.json").read_text())
    payload["note"] = text
    with pytest.raises(rcr.RouteCheckReplayError, match="carries recorded text"):
        rcr.scan_outputs((rcr.serialize(payload),), forbidden)


def test_a_run_holds_its_outputs_to_every_travel_row_it_read(
    one_game_run: tuple[Path, Path, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo, _, sha = one_game_run
    source = rcr.resolve_column(
        repo, rcr.ColumnRequest("r2", sha, "replays/samples/9p2i")
    )
    _, forbidden = rcr.run_columns(repo, [source])
    rows = [text for text in forbidden if text.startswith("Travel check for")]
    assert rows
    real = rcr.render_report

    def leaking(payload: Mapping[str, object]) -> str:
        return real(payload) + rows[0] + "\n"

    monkeypatch.setattr(rcr, "render_report", leaking)
    with pytest.raises(rcr.RouteCheckReplayError, match="carries recorded text"):
        rcr.outputs_for(repo, [source])


def test_a_report_that_differs_from_its_recomputation_fails_check(
    one_game_run: tuple[Path, Path, str],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo, out, _ = one_game_run
    report = tmp_path / "report.md"
    report.write_text((out / "report.md").read_text().replace("Column r2", "Column r9"))
    code = rcr.main(
        [
            "--check",
            "--json",
            str(out / "results.json"),
            "--report",
            str(report),
            "--repo",
            str(repo),
        ]
    )
    assert code == 1
    assert "the recomputed report differs" in capsys.readouterr().err


def test_a_census_with_no_meeting_for_a_games_first_raises() -> None:
    game = _r2_game(_RUN_SEED)
    with pytest.raises(
        rcr.RouteCheckReplayError, match=r"r2 seed 2 meeting 0: the census holds no"
    ):
        rcr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
            label="r2",
            game=replace(game, meetings=()),
            renderers=_canonical_renderers(),
        )


def test_an_r1_columns_tree_mismatch_names_r1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _column_repo(tmp_path, with_r1=True)
    assert _run(repo, tmp_path, f"r1={sha}:replays/candidates/stage-b-r1/9p2i") == 0
    payload = json.loads((tmp_path / "results.json").read_text())
    payload["columns"][0]["tree"] = "0" * 40
    copy = tmp_path / "copy.json"
    copy.write_text(rcr.serialize(payload))
    assert _check(repo, tmp_path, copy) == 1
    assert "column r1: the recorded tree id" in capsys.readouterr().err


def _readable(inputs: rcr.MeetingInputs) -> rcr.MeetingInputs:
    """Give a built meeting one voter whose ballot holds its own memory block."""

    memory = _memory()
    block = render_for_prompt(
        deepcopy(memory), token_budget=DEFAULT_TOKEN_BUDGET, suspicion_override={}
    )
    roster = sorted(inputs.roster)
    return replace(
        inputs,
        memories={voter: deepcopy(memory) for voter in roster},
        ballot_overrides={voter: {} for voter in roster},
        ballot_prompts={voter: (f"<memory>\n{block}\n</memory>",) for voter in roster},
    )


def test_charges_are_counted_for_living_targets_only() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw("p-9", "WEST_HALL", 14),),
            claims=(_accuses("p-9"),),
        ),
        _turn(1, "p-3", observations=(_saw("p-9", "ADMIN", 15),)),
    )
    flag = ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-1:turn-0:obs:0",
        event_b_id="turn:m-1:turn-1:obs:0",
        subjects=("p-9",),
        description="planted",
    )
    inputs = _readable(
        _inputs(*turns, roster=frozenset({"p-1", "p-3"}), contradictions=(flag,))
    )
    record, _ = rcr.read_meeting(
        inputs, seed=0, index=1, tick=15, kind="button", witness_meeting=False
    )
    assert record.charges == 0
    living = _readable(replace(inputs, roster=frozenset({"p-1", "p-3", "p-9"})))
    record, _ = rcr.read_meeting(
        living, seed=0, index=1, tick=15, kind="button", witness_meeting=False
    )
    assert (record.charges, record.charges_on_reconcilable_pair) == (1, 1)


# ---------------------------------------------------------------------------
# Planted cases review round 1 called for
# ---------------------------------------------------------------------------


def test_a_flag_whose_second_event_places_only_another_player_is_no_charge() -> None:
    turns = (
        _turn(
            0,
            "p-1",
            observations=(_saw(_SUBJECT, "WEST_HALL", 14),),
            claims=(_accuses(_SUBJECT),),
        ),
        _turn(1, "p-3", observations=(_saw("p-7", "ADMIN", 15),)),
    )
    flag = ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-1:turn-0:obs:0",
        event_b_id="turn:m-1:turn-1:obs:0",
        subjects=(_SUBJECT,),
        description="planted",
    )
    universe = rcr.spoken_placements(MeetingTranscript(turns=turns))
    placed = {(spot.event_id, spot.player) for spot in universe}
    assert (flag.event_a_id, _SUBJECT) in placed
    assert (flag.event_b_id, "p-7") in placed
    assert (flag.event_b_id, _SUBJECT) not in placed
    assert (
        rcr.charges_against(
            _SUBJECT, ballots=(), contradictions=(flag,), universe=universe
        )
        == ()
    )
    inputs = _readable(_inputs(*turns, contradictions=(flag,)))
    record, _ = rcr.read_meeting(
        inputs, seed=0, index=1, tick=15, kind="button", witness_meeting=False
    )
    assert record.charges == 0


def test_a_rerender_that_is_not_the_ballots_block_names_its_voter() -> None:
    inputs = _readable(_inputs(*_pair_transcript(("WEST_HALL", 14), ("ADMIN", 15))))
    rcr.require_faithful_rerender(inputs)
    assert sorted(inputs.roster)[-1] == "p-7"
    prompts = {**inputs.ballot_prompts, "p-7": ("<memory>\nanother block\n</memory>",)}
    with pytest.raises(
        rcr.RouteCheckReplayError,
        match=r"^voter p-7: the memory re-render is not the ballot's memory block$",
    ):
        rcr.require_faithful_rerender(replace(inputs, ballot_prompts=prompts))


def test_the_json_labels_b_snapshot_an_approximation() -> None:
    committed = json.loads(_COMMITTED_JSON.read_text())["checks"]
    assert committed == rcr.checks_payload()
    built = cast(dict[str, Any], rcr.build_payload([])["checks"])
    for checks in (committed, built):
        assert set(checks) == set(rcr.CHECKS)
        approximations = {c for c, label in checks.items() if label["approximation"]}
        assert approximations == {"b_snapshot"}
        snapshot = checks["b_snapshot"]
        assert snapshot["name"] == "(b-snapshot), approximation"
        assert snapshot["approximates"].startswith(
            "the temporal observation delivery that evidence version 2 requires"
        )
        assert all(
            label["approximates"] is None
            for check, label in checks.items()
            if check != "b_snapshot"
        )


def test_the_report_names_each_check_as_the_json_does() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    report = rcr.render_report(payload)
    named = report.count("(b-snapshot), approximation")
    assert named > 0
    payload["checks"]["b_snapshot"]["name"] = "(b-snapshot) renamed"
    renamed = rcr.render_report(payload)
    assert "(b-snapshot), approximation" not in renamed
    assert renamed.count("(b-snapshot) renamed") == named


#: An r2 game whose recorded ballots and turns hold non-ASCII text, which the
#: JSON writes escaped.
_ESCAPED_SEED: Final[int] = 12


def _escaped_recorded_texts(directory: Path) -> tuple[frozenset[str], dict[str, str]]:
    """The scan set of one game, and a recorded rationale and turn text the JSON escapes."""

    copy = _game_copy(directory, _ESCAPED_SEED)
    entries = read_all_entries(copy)
    texts = {
        "rationale": next(
            ballot.rationale_text
            for entry in entries
            for ballot in getattr(entry, "ballots", ())
            if len(ballot.rationale_text) >= 40 and not ballot.rationale_text.isascii()
        ),
        "turn text": next(
            turn.free_text
            for entry in entries
            if (transcript := getattr(entry, "transcript", None)) is not None
            for turn in transcript.turns
            if len(turn.free_text) >= 40 and not turn.free_text.isascii()
        ),
    }
    return rcr.forbidden_strings(directory), texts


@pytest.mark.parametrize("which", ("rationale", "turn text"))
def test_a_recorded_text_the_json_escapes_fails_the_scan(
    tmp_path: Path, which: str
) -> None:
    forbidden, texts = _escaped_recorded_texts(tmp_path)
    text = texts[which]
    payload = json.loads(_COMMITTED_JSON.read_text())
    payload["note"] = text
    written = rcr.serialize(payload)
    escaped_only = text not in written and json.dumps(text)[1:-1] in written
    assert escaped_only, "the planted text reaches the JSON only escaped"
    with pytest.raises(rcr.RouteCheckReplayError, match="carries recorded text"):
        rcr.scan_outputs((written,), forbidden)
    with pytest.raises(rcr.RouteCheckReplayError, match="carries recorded text"):
        rcr.scan_outputs((f"# report\n\n{text}\n",), forbidden)
