"""The route-lines replay: parity with the route-check replay, the ON render, r3, the scan.

``experiments/lab/route_lines_replay.py`` walks the route-check replay's columns
through that replay's own faithful walk and per-meeting reading, renders every
recorded ballot again with ``route_lines_version = 1`` and counts, count only,
what the field would show (``tasks/work/route-lines-field.md``). These tests hold
it to its card: the harness's recomputed records equal the committed route-check
JSON, meeting for meeting and in number, or the run stops, every ON render minus
its block is the recorded render, an r3 column is read from its served blocks,
its served reach equals its rebuilt reach and its block cost and report are read
as served, an r3 set recorded under another config is refused by name, and no
output carries a rendered line or a recorded text.

Columns are read from temporary repositories built here; the committed-output
checks read the checkout's working tree, never history.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Final, cast

import pytest

import experiments.lab.route_check_replay as rcr
import experiments.lab.route_lines_replay as rlr
from eval.gameplay_census import GameFacts
from meetings.route_lines import (
    Placement,
    PlacementKind,
    RouteLine,
    without_route_block,
)
from meetings.schemas import MeetingTranscript, VoteBallot
from tests._helpers.committed import SAMPLES_9P2I, census_inputs, repo_root
from tests._helpers.scripted_routes import record_routes_game, round_two_config

#: r2's game with one meeting, the cheapest whole-game run (the route-check
#: replay's own choice).
_RUN_SEED: Final[int] = 2
_COMMITTED_JSON: Final[Path] = repo_root / rlr.DEFAULT_JSON
_COMMITTED_REPORT: Final[Path] = repo_root / rlr.DEFAULT_REPORT
_ROUTE_CHECK_JSON: Final[Path] = repo_root / rcr.DEFAULT_JSON


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def _commit(repo: Path) -> str:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    _git(repo, "add", "-A")
    _git(
        repo,
        "-c",
        "user.name=route lines",
        "-c",
        "user.email=route-lines@example.invalid",
        "commit",
        "-q",
        "-m",
        "column",
    )
    return _git(repo, "rev-parse", "HEAD")


def _r2_repo(root: Path) -> tuple[Path, str]:
    """A repository holding one r2 game at its real path."""

    repo = root / "repo"
    target = repo / "replays" / "samples" / "9p2i"
    target.mkdir(parents=True)
    for name in ("MANIFEST.md", "roster.json", "experiment-config.json"):
        shutil.copy(SAMPLES_9P2I / name, target / name)
    shutil.copy(SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl", target)
    return repo, _commit(repo)


def _r3_repo(root: Path, *, declared_route_lines: bool = True) -> tuple[Path, str]:
    """A throwaway commit holding scripted ON games as r3, under a declared file."""

    repo = root / "repo"
    set_dir = repo / "replays" / "candidates" / "stage-b-r3" / "9p2i"
    record_routes_game(set_dir, route_lines=True)
    config = round_two_config(route_lines=declared_route_lines).model_dump(mode="json")
    declared = json.loads(
        (SAMPLES_9P2I / "experiment-config.json").read_text(encoding="utf-8")
    )
    payload = {key: config[key] for key in declared}
    if declared_route_lines:
        payload["route_lines_version"] = 1
    (set_dir.parent / "experiment-config.json").write_text(
        json.dumps(payload) + "\n", encoding="utf-8"
    )
    return repo, _commit(repo)


def _run(
    repo: Path, out: Path, *sets: str, route_check: Path = _ROUTE_CHECK_JSON
) -> int:
    return rlr.main(
        [
            *(item for spec in sets for item in ("--set", spec)),
            "--out-json",
            str(out / "results.json"),
            "--out-report",
            str(out / "report.md"),
            "--route-check-json",
            str(route_check),
            "--repo",
            str(repo),
        ]
    )


def _check(repo: Path, out: Path, route_check: Path) -> int:
    return rlr.main(
        [
            "--check",
            "--json",
            str(out / "results.json"),
            "--report",
            str(out / "report.md"),
            "--route-check-json",
            str(route_check),
            "--repo",
            str(repo),
        ]
    )


def _route_check_copy(
    root: Path, *, source: rcr.ColumnSource, records: Sequence[dict[str, Any]]
) -> Path:
    """A route-check JSON pinning ``source`` with ``records`` as its meetings."""

    path = root / "route-check.json"
    path.write_text(
        json.dumps(
            {
                "columns": [
                    {
                        "label": source.label,
                        "sha": source.sha,
                        "path": source.path,
                        "tree": source.tree,
                        "meetings": list(records),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return path


@pytest.fixture(scope="module")
def r2_run(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """One r2 game read through the CLI, with a route-check JSON pinning it."""

    root = tmp_path_factory.mktemp("r2")
    repo, sha = _r2_repo(root)
    source = rcr.resolve_column(
        repo, rcr.ColumnRequest("r2", sha, "replays/samples/9p2i")
    )
    route_check_out = root / "route-check"
    route_check_out.mkdir()
    assert (
        rcr.main(
            [
                "--set",
                f"r2={sha}:replays/samples/9p2i",
                "--out-json",
                str(route_check_out / "results.json"),
                "--out-report",
                str(route_check_out / "report.md"),
                "--repo",
                str(repo),
            ]
        )
        == 0
    )
    route_check = route_check_out / "results.json"
    out = root / "out"
    out.mkdir()
    assert (
        _run(repo, out, f"r2={sha}:replays/samples/9p2i", route_check=route_check) == 0
    )
    return {
        "repo": repo,
        "sha": sha,
        "source": source,
        "route_check": route_check,
        "out": out,
        "root": root,
    }


# ---------------------------------------------------------------------------
# A run and its check
# ---------------------------------------------------------------------------


def test_a_run_holds_parity_and_its_check_reproduces(r2_run: dict[str, Any]) -> None:
    payload = json.loads((r2_run["out"] / "results.json").read_text())
    (column,) = payload["columns"]
    assert column["route_check_parity"] is True
    assert column["mode"] == "rendered"
    assert column["sha"] == r2_run["sha"]
    whole = column["all"]
    assert whole["ballots"] > 0 and whole["tokens"]["recorded_input"] > 0
    assert _check(r2_run["repo"], r2_run["out"], r2_run["route_check"]) == 0


def _census_game(change: str) -> GameFacts:
    """r2's one-meeting game as the census reads it, with ``change`` planted."""

    (game,) = [g for g in census_inputs(SAMPLES_9P2I).games if g.seed == _RUN_SEED]
    (fact,) = game.meetings
    if change == "one meeting short":
        return replace(game, meetings=())
    if change == "one meeting long":
        return replace(game, meetings=(fact, fact))
    if change == "a moved tick":
        return replace(game, meetings=(replace(fact, tick=fact.tick + 1),))
    assert change == "a moved meeting id"
    return replace(game, meetings=(replace(fact, meeting_id="elsewhere"),))


@pytest.mark.parametrize(
    ("change", "message"),
    (
        (
            "one meeting short",
            r"^r2 seed 2 meeting 0: the census holds no such meeting$",
        ),
        (
            "one meeting long",
            r"^r2 seed 2: the census holds 2 meetings and the walk read 1$",
        ),
        (
            "a moved tick",
            r"^r2 seed 2 meeting 0: the census and the walk read different meetings$",
        ),
        (
            "a moved meeting id",
            r"^r2 seed 2 meeting 0: the census and the walk read different meetings$",
        ),
    ),
)
def test_a_census_the_walk_disagrees_with_is_refused_by_name(
    change: str, message: str
) -> None:
    """Planted: each census-against-walk guard of ``read_game``, on its own case."""

    with pytest.raises(rlr.RouteLinesReplayError, match=message):
        rlr.read_game(
            SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl",
            label="r2",
            game=_census_game(change),
        )


def test_a_parity_mismatch_raises(
    r2_run: dict[str, Any], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Planted: one committed route-check record altered."""

    committed = json.loads(r2_run["route_check"].read_text())["columns"][0]
    records = [dict(record) for record in committed["meetings"]]
    records[0]["charges"] = records[0]["charges"] + 1
    altered = _route_check_copy(tmp_path, source=r2_run["source"], records=records)
    out = tmp_path / "out"
    out.mkdir()
    spec = f"r2={r2_run['sha']}:replays/samples/9p2i"
    assert _run(r2_run["repo"], out, spec, route_check=altered) == 1
    assert "differs from the committed one" in capsys.readouterr().err
    assert not (out / "results.json").exists()


@pytest.mark.parametrize(
    ("change", "recorded"),
    (
        pytest.param("one record long", 2, id="one record long"),
        pytest.param("one record short", 0, id="one record short"),
    ),
)
def test_a_route_check_column_of_another_length_is_refused_by_name(
    r2_run: dict[str, Any],
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    change: str,
    recorded: int,
) -> None:
    """Planted: the committed column holds one meeting record more, or one fewer.

    r2's seed 2 holds one meeting, so the committed column holds that record
    twice, or none; the run stops on the named refusal, never a traceback.
    """

    committed = json.loads(r2_run["route_check"].read_text())["columns"][0]
    (record,) = committed["meetings"]
    records = [record, record] if change == "one record long" else []
    assert len(records) == recorded
    altered = _route_check_copy(tmp_path, source=r2_run["source"], records=records)
    out = tmp_path / "out"
    out.mkdir()
    spec = f"r2={r2_run['sha']}:replays/samples/9p2i"
    assert _run(r2_run["repo"], out, spec, route_check=altered) == 1
    assert capsys.readouterr().err == (
        f"route-lines replay: column r2: the route-check replay records {recorded} "
        "meetings and the walk read 1\n"
    )
    assert not (out / "results.json").exists()


def test_a_column_the_route_check_replay_pins_to_other_bytes_raises(
    r2_run: dict[str, Any], tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    committed = json.loads(r2_run["route_check"].read_text())["columns"][0]
    elsewhere = rcr.ColumnSource(
        label="r2",
        commit="x",
        sha="0" * 40,
        path=r2_run["source"].path,
        tree=r2_run["source"].tree,
    )
    moved = _route_check_copy(tmp_path, source=elsewhere, records=committed["meetings"])
    out = tmp_path / "out"
    out.mkdir()
    spec = f"r2={r2_run['sha']}:replays/samples/9p2i"
    assert _run(r2_run["repo"], out, spec, route_check=moved) == 1
    assert "pins other bytes" in capsys.readouterr().err


def test_a_rendered_line_in_an_output_is_refused(
    r2_run: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the report leaks one rendered route line."""

    leaked: list[str] = []
    real = rlr.read_ballot

    def _remembering(*args: Any, **kwargs: Any) -> rlr.BallotReading:
        reading = real(*args, **kwargs)
        leaked.extend(row for row in reading.block_rows if row.startswith("- `"))
        return reading

    real_render = rlr.render_report

    def _leaking(payload: Any) -> str:
        return real_render(payload) + leaked[0] + "\n"

    monkeypatch.setattr(rlr, "read_ballot", _remembering)
    monkeypatch.setattr(rlr, "render_report", _leaking)
    with pytest.raises(rlr.RouteLinesReplayError, match="carries recorded text"):
        rlr.outputs_for(
            r2_run["repo"],
            [r2_run["source"]],
            route_check=json.loads(r2_run["route_check"].read_text()),
        )
    assert leaked


def test_an_on_render_that_moves_more_than_its_block_raises() -> None:
    """Planted: an ON render that also changes a byte outside the block."""

    from meetings.route_lines import build_route_lines
    from tests.meetings.test_route_lines import _ballot_inputs, _sightings, _vote

    transcript = _sightings(("p-3", "WEST_HALL", 5), ("p-3", "ADMIN", 6))
    kwargs = _ballot_inputs(transcript=transcript)
    vote = _vote()
    render = rlr.BallotRender(kwargs=kwargs, prompt=vote(**kwargs))
    reading = rlr.read_ballot(
        render, inner=vote, regroup_ticks=frozenset(), served=False
    )
    assert reading.lines == build_route_lines(
        transcript=transcript,
        candidate_targets=kwargs["candidate_targets"],
        regroup_ticks=frozenset(),
    )
    assert reading.block_chars > 0

    def _drifting(**inputs: Any) -> str:
        return vote(**inputs) + " "

    with pytest.raises(rlr.RouteLinesReplayError, match="minus its block"):
        rlr.read_ballot(
            render, inner=_drifting, regroup_ticks=frozenset(), served=False
        )


def test_an_on_render_whose_block_holds_other_lines_raises() -> None:
    """Planted: an ON render that serves a different line than it was handed."""

    from tests.meetings.test_route_lines import (
        _EXAMPLE,
        _ballot_inputs,
        _sightings,
        _vote,
    )

    transcript = _sightings(("p-3", "WEST_HALL", 5), ("p-3", "ADMIN", 6))
    kwargs = _ballot_inputs(transcript=transcript)
    vote = _vote()
    render = rlr.BallotRender(kwargs=kwargs, prompt=vote(**kwargs))

    def _other_line(**inputs: Any) -> str:
        return vote(**{**inputs, "route_lines": (RouteLine.model_validate(_EXAMPLE),)})

    with pytest.raises(rlr.RouteLinesReplayError, match="does not parse back"):
        rlr.read_ballot(
            render, inner=_other_line, regroup_ticks=frozenset(), served=False
        )


def test_a_ballot_recorded_off_but_rendered_with_lines_raises() -> None:
    from tests.meetings.test_route_lines import _EXAMPLE, _ballot_inputs, _vote

    kwargs = {
        **_ballot_inputs(transcript=MeetingTranscript()),
        "route_lines": (RouteLine.model_validate(_EXAMPLE),),
        "route_lines_version": 1,
    }
    render = rlr.BallotRender(kwargs=kwargs, prompt=_vote()(**kwargs))
    with pytest.raises(rlr.RouteLinesReplayError, match="recorded OFF was rendered"):
        rlr.read_ballot(render, inner=_vote(), regroup_ticks=frozenset(), served=False)


def _meeting_record() -> rcr.MeetingRecord:
    return rcr.MeetingRecord(
        seed=0,
        meeting=0,
        tick=9,
        kind="button",
        witness_meeting=False,
        opener="p-1",
        voters=2,
        charges=0,
        charges_on_reconcilable_pair=0,
        lines=(),
        b_offered=(),
        b_kept=(),
        b_snapshot_offered=(),
        b_snapshot_kept=(),
        case=None,
    )


def _reading(voter: str, lines: tuple[RouteLine, ...]) -> rlr.BallotReading:
    return rlr.BallotReading(
        voter=voter,
        lines=lines,
        block_chars=0,
        block_rows=(),
        recorded_prompt="",
        served_lines=None,
    )


def test_a_meeting_needs_one_ballot_per_participant_and_one_line_per_player() -> None:
    from tests.meetings.test_route_lines import _EXAMPLE

    inputs = rcr.MeetingInputs(
        transcript=MeetingTranscript(),
        contradictions=(),
        ballots=(),
        ejected=None,
        opener="p-1",
        trigger_kind="emergency",
        roster=frozenset({"p-1", "p-2"}),
        sighting_records={},
        move_witness_records={},
        regroup_ticks=frozenset(),
        first_meeting=True,
        memories={},
        ballot_overrides={},
        ballot_prompts={},
    )
    line = RouteLine.model_validate(_EXAMPLE)
    whole = rlr.read_field_meeting(
        inputs,
        record=_meeting_record(),
        readings=[_reading("p-1", (line,)), _reading("p-2", (line,))],
        served=False,
    )
    assert (whole.ballots, whole.ballots_with_block, whole.lines) == (2, 2, 1)
    with pytest.raises(rlr.RouteLinesReplayError, match="one ballot render per"):
        rlr.read_field_meeting(
            inputs,
            record=_meeting_record(),
            readings=[_reading("p-1", ())],
            served=False,
        )
    other = line.model_copy(update={"steps": line.steps[:1]})
    with pytest.raises(rlr.RouteLinesReplayError, match="different lines"):
        rlr.read_field_meeting(
            inputs,
            record=_meeting_record(),
            readings=[_reading("p-1", (line,)), _reading("p-2", (other,))],
            served=False,
        )


def _case_record(*, misjudged: bool) -> rcr.CaseRecord:
    """The harness's record of ``p-3``'s ejection, check (c) reaching it."""

    reached = rcr.CheckCase(
        reaches=True,
        reaches_charge=False,
        insufficient_lines=0,
        reason=None,
        pair_reasons=(),
    )
    return rcr.CaseRecord(
        ejected="p-3",
        eject_voters=1,
        reporter=False,
        placements=0,
        reconcilable_pairs=0,
        charges=0,
        ballot_charges=0,
        flag_charges=0,
        charges_on_reconcilable_pair=0,
        misjudged=misjudged,
        misjudging_pairs=0,
        walkable_pair=tuple((leg, False) for leg in rcr.DISPUTE_LEGS),
        checks=tuple((name, reached) for name in rcr.CHECKS),
        pit_net=False,
    )


def _ballot(voter: str, target: str) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.8,
        primary_reason_id=None,
        rationale_text="a recorded rationale",
    )


def _ejection_case(
    readings: Sequence[rlr.BallotReading],
    *,
    served: bool,
    misjudged: bool = True,
    witness: bool = True,
) -> rlr.FieldCase:
    """``p-3`` ejected by ``p-1`` alone, read through ``read_field_meeting``."""

    inputs = rcr.MeetingInputs(
        transcript=MeetingTranscript(),
        contradictions=(),
        ballots=(_ballot("p-1", "p-3"), _ballot("p-2", "SKIP"), _ballot("p-3", "SKIP")),
        ejected="p-3",
        opener="p-1",
        trigger_kind="emergency",
        roster=frozenset({"p-1", "p-2", "p-3"}),
        sighting_records={},
        move_witness_records={},
        regroup_ticks=frozenset(),
        first_meeting=True,
        memories={},
        ballot_overrides={},
        ballot_prompts={},
    )
    record = replace(
        _meeting_record(),
        witness_meeting=witness,
        case=_case_record(misjudged=misjudged),
    )
    meeting = rlr.read_field_meeting(
        inputs, record=record, readings=readings, served=served
    )
    assert meeting.case is not None
    return meeting.case


def _served(
    voter: str,
    lines: tuple[RouteLine, ...],
    served_lines: tuple[RouteLine, ...] | None = None,
) -> rlr.BallotReading:
    return replace(
        _reading(voter, lines),
        served_lines=lines if served_lines is None else served_lines,
    )


def test_served_reach_counts_only_served_lines_about_the_ejected_from_its_voters() -> (
    None
):
    """Planted: served mode, where a served block's lines miss the ejected player.

    ``p-1`` alone votes ``p-3`` out. Unreached: ``p-1``'s served block holds a
    line about ``p-2`` only, and ``p-2``, who skipped, holds one about ``p-3``.
    Served apart: ``p-1``'s rebuilt lines hold ``p-3`` but its served block holds
    only ``p-2`` (the instrument refuses that state before this reading; here it
    proves the served reach reads the served block). The counts then hold an
    unreached and a reached case at a witness meeting, a reached misjudged case
    at another meeting and a reached case that is not misjudged, so each served
    count counts only its own reached cases.
    """

    from tests.meetings.test_route_lines import _EXAMPLE

    about_ejected = RouteLine.model_validate(_EXAMPLE)
    about_other = RouteLine.model_validate({**_EXAMPLE, "subject": "p-2"})
    unreached_readings = [
        _served("p-1", (about_other,)),
        _served("p-2", (about_ejected,)),
        _served("p-3", ()),
    ]
    reached_readings = [
        _served("p-1", (about_ejected,)),
        _served("p-2", ()),
        _served("p-3", ()),
    ]
    unreached = _ejection_case(unreached_readings, served=True)
    assert (unreached.reaches, unreached.reaches_served) == (False, False)
    apart = _ejection_case(
        [_served("p-1", (about_ejected,), (about_other,)), *reached_readings[1:]],
        served=True,
    )
    assert (apart.reaches, apart.reaches_served) == (True, False)
    reached = _ejection_case(reached_readings, served=True)
    assert (reached.reaches, reached.reaches_served) == (True, True)
    # Rendered mode reads no served block.
    rendered = [replace(reading, served_lines=None) for reading in reached_readings]
    assert _ejection_case(rendered, served=False).reaches_served is None
    elsewhere = _ejection_case(reached_readings, served=True, witness=False)
    not_misjudged = _ejection_case(reached_readings, served=True, misjudged=False)
    counts = rlr._case_counts(
        [unreached, reached, elsewhere, not_misjudged], served=True
    )
    assert (counts["M"], counts["W"]) == (3, 2)
    assert (counts["field_reaches_M"], counts["field_reaches_W"]) == (2, 1)
    assert (counts["field_reaches_M_served"], counts["field_reaches_W_served"]) == (
        2,
        1,
    )
    assert "field_reaches_M_served" not in rlr._case_counts([reached], served=False)


def test_a_served_block_other_than_its_rebuilt_lines_raises() -> None:
    from tests.meetings.test_route_lines import _EXAMPLE, _ballot_inputs, _vote

    kwargs = _ballot_inputs(transcript=MeetingTranscript())
    vote = _vote()
    served = vote(
        **kwargs,
        route_lines=(RouteLine.model_validate(_EXAMPLE),),
        route_lines_version=1,
    )
    render = rlr.BallotRender(kwargs=kwargs, prompt=served)
    with pytest.raises(
        rlr.RouteLinesReplayError, match="not the lines its inputs build"
    ):
        rlr.read_ballot(render, inner=vote, regroup_ticks=frozenset(), served=True)


def test_a_served_ballot_counts_its_whole_block() -> None:
    """Served mode: the block characters are the served block's, not zero.

    The ballot recorded the field ON, so its block characters are its prompt's
    length less the prompt without the block, which is the OFF render's length.
    """

    from meetings.route_lines import build_route_lines
    from tests.meetings.test_route_lines import _ballot_inputs, _sightings, _vote

    transcript = _sightings(("p-3", "WEST_HALL", 5), ("p-3", "ADMIN", 6))
    off_kwargs = _ballot_inputs(transcript=transcript)
    lines = build_route_lines(
        transcript=transcript,
        candidate_targets=off_kwargs["candidate_targets"],
        regroup_ticks=frozenset(),
    )
    assert lines
    vote = _vote()
    on_kwargs = {**off_kwargs, "route_lines": lines, "route_lines_version": 1}
    served = vote(**on_kwargs)
    off = vote(**off_kwargs)
    reading = rlr.read_ballot(
        rlr.BallotRender(kwargs=on_kwargs, prompt=served),
        inner=vote,
        regroup_ticks=frozenset(),
        served=True,
    )
    assert reading.served_lines == lines
    assert reading.recorded_prompt == served
    assert reading.block_chars == len(served) - len(without_route_block(served))
    assert reading.block_chars == len(served) - len(off)
    assert reading.block_chars > 0
    assert reading.block_rows


def _placement(kind: PlacementKind, tick: int, room: str) -> Placement:
    return Placement("p-3", tick, frozenset({room}), kind, f"e-{tick}", "t")


def test_an_unreached_case_names_its_reason() -> None:
    vent = (
        _placement("saw_vent", 4, "REACTOR"),
        _placement("saw_player", 5, "ENGINEERING"),
    )
    sighted = (
        _placement("saw_player", 4, "ADMIN"),
        _placement("saw_player", 6, "CAFETERIA"),
    )
    assert rlr._field_reason([vent], every_pair=False) == "kind"
    assert rlr._field_reason([vent], every_pair=True) == "kind"
    assert rlr._field_reason([vent, sighted], every_pair=True) == "consecutive"
    assert rlr._field_reason([sighted], every_pair=False) == "residual"


# ---------------------------------------------------------------------------
# r3: both instruments read a column recorded with the field ON
# ---------------------------------------------------------------------------


def test_an_r3_column_is_read_from_its_served_blocks_by_both_instruments(
    tmp_path: Path,
) -> None:
    repo, sha = _r3_repo(tmp_path)
    spec = f"r3={sha}:replays/candidates/stage-b-r3/9p2i"
    out = tmp_path / "out"
    out.mkdir()
    assert _run(repo, out, spec) == 0
    (column,) = json.loads((out / "results.json").read_text())["columns"]
    assert column["label"] == "r3"
    assert column["mode"] == "served"
    assert column["route_check_parity"] is False
    assert column["declared_config"] == rcr.R3_CONFIG_PATH
    whole = column["all"]
    assert whole["ballots_with_block"] > 0
    assert whole["field_reaches_M_served"] == whole["field_reaches_M"]
    assert whole["field_reaches_W_served"] == whole["field_reaches_W"]
    cases = [meeting["case"] for meeting in column["meetings"] if "case" in meeting]
    assert cases and all(case["reaches_served"] == case["reaches"] for case in cases)
    assert any(case["reaches"] for case in cases)
    assert whole["steps"]["walking_fits"] > 0 and whole["steps"]["regroup_between"] > 0
    # The route-check replay accepts the label too.
    route_check_out = tmp_path / "route-check"
    route_check_out.mkdir()
    assert (
        rcr.main(
            [
                "--set",
                spec,
                "--out-json",
                str(route_check_out / "results.json"),
                "--out-report",
                str(route_check_out / "report.md"),
                "--repo",
                str(repo),
            ]
        )
        == 0
    )
    (checked,) = json.loads((route_check_out / "results.json").read_text())["columns"]
    assert checked["label"] == "r3"
    assert checked["declared_config"] == rcr.R3_CONFIG_PATH


#: The report's sentence for a column whose ballots recorded the route lines.
_SERVED_SENTENCE: Final[str] = (
    "The ballots recorded the route lines, so the block is read as served and held "
    "equal to the lines its inputs build."
)


def test_an_r3_columns_block_cost_and_report_are_read_as_served(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The served column's block characters, tokens and report rows, pinned.

    Each served ballot's block characters are its recorded prompt's length less
    that prompt without the block, the column's sum of them is above zero and
    its tokens already served are too, and the report states the served
    reading, the as-served reach row and the already-served token row. A copy
    of the payload with the served reach set apart from the rebuilt reach shows
    that row reads the served counts.
    """

    readings: list[rlr.BallotReading] = []
    real = rlr.read_ballot

    def _remembering(*args: Any, **kwargs: Any) -> rlr.BallotReading:
        reading = real(*args, **kwargs)
        readings.append(reading)
        return reading

    monkeypatch.setattr(rlr, "read_ballot", _remembering)
    repo, sha = _r3_repo(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    assert _run(repo, out, f"r3={sha}:replays/candidates/stage-b-r3/9p2i") == 0
    payload = json.loads((out / "results.json").read_text())
    (column,) = payload["columns"]
    whole = column["all"]
    tokens = whole["tokens"]
    assert readings and all(reading.served_lines is not None for reading in readings)
    assert [reading.block_chars for reading in readings] == [
        len(reading.recorded_prompt) - len(without_route_block(reading.recorded_prompt))
        for reading in readings
    ]
    assert whole["block_chars"] == sum(reading.block_chars for reading in readings)
    assert whole["block_chars"] > 0
    assert tokens["added_input"] > 0
    assert tokens["projected_input"] == tokens["recorded_input"]
    report = (out / "report.md").read_text()
    assert report == rlr.render_report(payload)
    rows = report.splitlines()
    assert _SERVED_SENTENCE in report
    assert "rendered again" not in report
    assert (
        f"| route lines, as served | {whole['field_reaches_M_served']} of {whole['M']} "
        f"| {whole['field_reaches_W_served']} of {whole['W']} |"
    ) in rows
    assert (
        f"| already served in the recorded ballots | {tokens['added_input']} |"
    ) in rows
    assert "projected added by the block" not in report
    # The as-served row reads the served counts: a planted payload sets them
    # apart from the rebuilt ones, one fewer over M and one more over W.
    assert whole["field_reaches_M"] > 0
    served_m = whole["field_reaches_M"] - 1
    served_w = whole["field_reaches_W"] + 1
    apart = json.loads(json.dumps(payload))
    apart_whole = apart["columns"][0]["all"]
    apart_whole["field_reaches_M_served"] = served_m
    apart_whole["field_reaches_W_served"] = served_w
    apart_rows = rlr.render_report(apart).splitlines()
    assert (
        f"| route lines, as served | {served_m} of {whole['M']} "
        f"| {served_w} of {whole['W']} |"
    ) in apart_rows
    assert (
        f"| route lines | {whole['field_reaches_M']} of {whole['M']} "
        f"| {whole['field_reaches_W']} of {whole['W']} |"
    ) in apart_rows


def test_an_r3_set_recorded_under_another_config_is_refused_naming_the_column(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo, sha = _r3_repo(tmp_path, declared_route_lines=False)
    out = tmp_path / "out"
    out.mkdir()
    assert _run(repo, out, f"r3={sha}:replays/candidates/stage-b-r3/9p2i") == 1
    assert "column r3: seed 0 recorded settings that differ" in capsys.readouterr().err


def _copy_r2_game(set_dir: Path) -> None:
    set_dir.mkdir(parents=True, exist_ok=True)
    for name in ("MANIFEST.md", "roster.json", "experiment-config.json"):
        if not (set_dir / name).exists():
            shutil.copy(SAMPLES_9P2I / name, set_dir / name)
    shutil.copy(SAMPLES_9P2I / f"replay-seed-{_RUN_SEED}.jsonl", set_dir)


def test_a_census_whose_seeds_differ_from_the_set_is_refused(tmp_path: Path) -> None:
    """Planted: r2's 50-game census beside a set holding one of its games."""

    set_dir = tmp_path / "9p2i"
    _copy_r2_game(set_dir)
    with pytest.raises(
        rlr.RouteLinesReplayError,
        match=r"^r2: the census and the set hold different seeds$",
    ):
        rlr.read_set(set_dir, label="r2", census=census_inputs(SAMPLES_9P2I))


def test_a_set_whose_games_record_the_field_both_ways_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: a scripted game recorded ON beside r2's game recorded OFF.

    Each game's reading is stubbed (it is the mode check under test, and the
    scripted game has no census row here); the modes are read off the bytes.
    """

    set_dir = tmp_path / "9p2i"
    record_routes_game(set_dir, route_lines=True)
    _copy_r2_game(set_dir)
    modes = {
        rlr._column_mode(set_dir / f"replay-seed-{seed}.jsonl")
        for seed in (0, _RUN_SEED)
    }
    assert modes == {"served", "rendered"}
    census = census_inputs(SAMPLES_9P2I)
    (game,) = [g for g in census.games if g.seed == _RUN_SEED]
    read: list[int] = []

    def _read_game(path: Path, *, label: str, game: GameFacts) -> rlr.GameReading:
        read.append(game.seed)
        return rlr.GameReading(
            meetings=(),
            texts=frozenset(),
            recorded_input_tokens=0,
            recorded_ballot_input_tokens=0,
            added_input_tokens=Fraction(0),
        )

    monkeypatch.setattr(rlr, "read_game", _read_game)
    with pytest.raises(
        rlr.RouteLinesReplayError,
        match=r"^r2: its games record the field both ways$",
    ):
        rlr.read_set(
            set_dir,
            label="r2",
            census=replace(census, games=(replace(game, seed=0), game)),
        )
    assert read == [0, _RUN_SEED]


# ---------------------------------------------------------------------------
# The committed outputs
# ---------------------------------------------------------------------------


def test_the_committed_outputs_hold_three_columns_with_r2_governing() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    assert [column["label"] for column in payload["columns"]] == ["s9", "r1", "r2"]
    assert payload["governing_column"] == "r2"
    route_check = json.loads(_ROUTE_CHECK_JSON.read_text())
    for column in payload["columns"]:
        assert column["route_check_parity"] is True
        assert column["mode"] == "rendered"
        pinned = rlr.committed_column(route_check, column["label"])
        assert pinned is not None
        assert (column["sha"], column["path"], column["tree"]) == (
            pinned["sha"],
            pinned["path"],
            pinned["tree"],
        )
        whole = column["all"]
        rule = cast(dict[str, Any], pinned["rule_inputs"])
        assert (whole["M"], whole["W"]) == (rule["M"], rule["W"])
        assert (whole["c_reaches_M"], whole["c_reaches_W"]) == (
            rule["R"]["c"],
            rule["R_W"]["c"],
        )


def test_the_committed_report_is_the_committed_jsons_rendering() -> None:
    payload = json.loads(_COMMITTED_JSON.read_text())
    assert rcr.serialize(payload) == _COMMITTED_JSON.read_text()
    assert rlr.render_report(payload) == _COMMITTED_REPORT.read_text()


def test_the_committed_r2_column_recomputes_from_the_checkouts_bytes() -> None:
    """The committed r2 column is what the instrument reads from these replays today."""

    payload = json.loads(_COMMITTED_JSON.read_text())
    (committed,) = [column for column in payload["columns"] if column["label"] == "r2"]
    census = census_inputs(SAMPLES_9P2I)
    reading = rlr.read_set(SAMPLES_9P2I, label="r2", census=census)
    source = rcr.ColumnSource(
        label="r2",
        commit=committed["commit"],
        sha=committed["sha"],
        path=committed["path"],
        tree=committed["tree"],
    )
    parity = rlr.require_parity(
        source, reading.meetings, route_check=json.loads(_ROUTE_CHECK_JSON.read_text())
    )
    column = rlr.column_payload(
        source,
        reading=reading,
        roles={game.seed: game.roles for game in census.games},
        parity=parity,
    )
    assert json.loads(json.dumps(column)) == committed
