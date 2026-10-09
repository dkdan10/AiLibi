"""The route-lines field end to end: switch, profile, stamp, runner, manager, rehearsals, readers.

``route_lines_version`` is a default-OFF meeting-layer field of
:class:`orchestrator.experiment_config.RecordedExperimentConfig`, set only by a
declared config (``tasks/work/route-lines-field.md``). ON, every ballot of the
served set gains the ``<routes>`` block :mod:`meetings.route_lines` builds, under
the derived stamp ``vote_ballot.qwen3_6_27b.v8.route_lines_v1``; OFF, nothing
moves. The rehearsals record fake and scripted games into ``tmp_path`` from
round 2's declared config with and without the field; nothing here prints a
rendered prompt or reads a recorded text into an assertion message.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType, SimpleNamespace
from typing import Any, Final

import pytest
from pydantic import ValidationError

import eval.evidence_honesty as evidence_honesty_module
import eval.funnel as funnel_module
import eval.kill_craft as kill_craft_module
import eval.solvability as solvability_module
import eval.watchability as watchability_module
import eval.win_condition_selfcheck as win_condition_module
import meetings.manager as manager_module
import orchestrator.game as game_module
import tests.meetings.test_prompt_byte_golden as golden
from agents.strategic.prompts.loader import (
    VOTE_BALLOT_TEMPLATE,
    require_guarded_bodies,
)
from api.replay_loader import ReplayLoader
from eval._suspicion_parse import parse_rendered_max_suspicion
from eval.evidence_honesty import compute_evidence_honesty
from eval.funnel import compute_information_funnel, compute_pooling_funnel
from eval.gameplay_census import FIELD_CLASSIFICATION, served_own_kill_rows
from eval.kill_craft import compute_kill_craft_report
from eval.meeting_quality import _parse_suspicion_graph, _parse_valid_targets
from eval.recorded_settings import READABLE_SETTINGS
from eval.solvability import compute_solvability_report
from eval.validity import _rendered_suspicions
from eval.watchability import compute_watchability
from eval.win_condition_selfcheck import check_replay_win_condition
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import (
    CONFIG_ONLY_PROFILE_FIELDS,
    MeetingEvidenceProfile,
    profile_from_config,
)
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingTrigger,
)
from meetings.route_lines import (
    RouteLine,
    build_route_lines,
    parse_route_lines,
    route_block_span,
    without_route_block,
)
from meetings.schemas import MeetingResult, MeetingTranscript, SawPlayerObservation
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    OMITTED_AT_DEFAULT,
    RecordedExperimentConfig,
    meeting_values,
    wave_settings,
)
from orchestrator.game import (
    PROMPT_VERSION_SETS,
    EXPERIMENT_ARM_TEMPLATES,
    build_default_meeting_runner,
    experiment_arm_suffix,
    prompt_versions_for_set,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    read_all_entries,
    recorded_experiment_config,
)
from tests._helpers.committed import candidate_rounds
from tests._helpers.scripted_meeting import record_game
from tests._helpers.scripted_routes import record_routes_game, round_two_config
from tests.meetings._manager_helpers import (
    _crewmate_report_prompt,
    _impostor_report_prompt,
    _make_responder,
    _participant,
    _ScriptedLLMClient,
    _statement_prompt,
    _vote_prompt,
)
from tests.orchestrator import test_experiment_arms as arms_tests

_REPO: Final[Path] = Path(__file__).resolve().parents[2]
_SET: Final[str] = "qwen3_6_27b"
_FIELD: Final[str] = "route_lines_version"
_STAMP: Final[str] = "vote_ballot.qwen3_6_27b.v8.route_lines_v1"
_ROUND_TWO_BALLOT: Final[str] = (
    "vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1"
    "+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1"
)
#: The fake rehearsal's seed, named in the card's Results.
_FAKE_SEED: Final[int] = 0
_SUSPICION_HEADER: Final[str] = "## Your suspicion of each player"


# ---------------------------------------------------------------------------
# The field
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", [0, 2, True, 1.0, "1"])
def test_a_value_other_than_one_or_none_is_refused(value: object) -> None:
    with pytest.raises(ValidationError):
        RecordedExperimentConfig.model_validate({_FIELD: value})


def test_one_round_trips_and_dumps_the_key() -> None:
    config = RecordedExperimentConfig(route_lines_version=1)
    dumped = config.model_dump(mode="json")
    assert dumped[_FIELD] == 1
    assert RecordedExperimentConfig.model_validate(dumped) == config
    assert not config.is_default
    assert wave_settings(config) == ((_FIELD, 1),)
    assert not config.has_tactical_changes


def test_none_dumps_no_key_and_is_the_default() -> None:
    config = RecordedExperimentConfig()
    assert _FIELD not in config.model_dump(mode="json")
    assert config.is_default
    assert wave_settings(config) == ()


def test_the_field_is_declared_last_in_the_meeting_layer_and_omitted_at_default() -> (
    None
):
    assert list(RecordedExperimentConfig.model_fields)[-2:] == [
        "kill_cooldown_ticks",
        _FIELD,
    ]
    assert FIELD_LAYER[_FIELD] == "meeting"
    assert _FIELD in OMITTED_AT_DEFAULT
    assert _FIELD not in experiment_config._PRE_WAVE_VALUES


def _round_two_file() -> str:
    return (
        _REPO / "replays" / "samples" / "9p2i" / "experiment-config.json"
    ).read_text(encoding="utf-8")


def test_round_twos_file_plus_the_field_validates_at_format_one() -> None:
    raw = _round_two_file()
    declared = json.loads(raw)
    with_field = RecordedExperimentConfig.model_validate({**declared, _FIELD: 1})
    assert with_field.format_version == 1
    dumped_on = with_field.model_dump(mode="json")
    assert dumped_on[_FIELD] == 1
    without = RecordedExperimentConfig.model_validate(declared)
    dumped_off = without.model_dump(mode="json")
    assert _FIELD not in dumped_off
    assert {
        key: value for key, value in dumped_on.items() if key != _FIELD
    } == dumped_off
    # Without the key, the config re-serializes the file's own bytes.
    assert json.dumps({key: dumped_off[key] for key in declared}) + "\n" == raw
    assert round_two_config(route_lines=False) == without
    assert round_two_config(route_lines=True) == with_field


def _config_file_problems() -> list[str]:
    """Each committed ``experiment-config.json`` under ``replays/`` that re-serializes differently."""

    # The keys every first-format payload writes whatever it holds: the fields
    # that existed before the wave, never one omitted at its default.
    always = {
        key
        for key in RecordedExperimentConfig().model_dump(mode="json")
        if key in experiment_config._PRE_WAVE_VALUES
    }
    problems: list[str] = []
    paths = sorted((_REPO / "replays").rglob("experiment-config.json"))
    assert len(paths) >= 2
    for path in paths:
        text = path.read_text(encoding="utf-8")
        raw = json.loads(text)
        dumped = RecordedExperimentConfig.model_validate(raw).model_dump(mode="json")
        if (
            set(dumped) != set(raw) | always
            or json.dumps({key: dumped[key] for key in raw}) + "\n" != text
        ):
            problems.append(path.relative_to(_REPO).as_posix())
    return problems


def test_every_committed_experiment_config_file_reserializes_unchanged() -> None:
    assert _config_file_problems() == []


#: Every committed replay set, read through its first replay's recorded settings.
_COMMITTED_SETS: Final[tuple[str, ...]] = (
    "samples/9p2i",
    "samples/4p1i",
    "ml_corpus/9p2i",
    "ml_corpus/4p1i",
    "candidates/stage-b-r1/9p2i",
)


def _recorded_route_lines(replay: Path) -> int | None:
    """The ``route_lines_version`` ``replay`` recorded; ``None`` when OFF or absent."""

    if not replay.is_file():
        return None
    recorded = recorded_experiment_config(read_all_entries(replay))
    return (recorded or RecordedExperimentConfig()).route_lines_version


def _declared_configs_recording_the_field_on(candidates: Path) -> frozenset[Path]:
    """The declared config of each candidate round whose own recording reads the field ON.

    The rounds come from the candidate declarations, never from a path named
    here: the round's README holds one ``candidate-declaration`` block, parsed by
    the candidate-set test, whose first line names the config file's sha256, and
    every replay of every seed it declares recorded the field at the file's value.
    """

    # The candidate-set test imports the bare ``scripts/`` modules.
    scripts = str(_REPO / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from tests.scripts.test_candidate_sets import (
        declaration_blocks,
        parse_declaration,
    )

    declared: set[Path] = set()
    for round_dir in candidate_rounds(candidates):
        config_path = round_dir / "experiment-config.json"
        # A round still recording holds no config yet, so nothing to leave out.
        if not config_path.is_file():
            continue
        data = config_path.read_bytes()
        value = RecordedExperimentConfig.model_validate_json(data).route_lines_version
        readme = (round_dir / "README.md").read_text(encoding="utf-8")
        blocks = declaration_blocks(readme)
        if value is None or len(blocks) != 1:
            continue
        declaration, problems = parse_declaration(blocks[0])
        if problems or declaration.config_line != (
            f"{hashlib.sha256(data).hexdigest()}  {config_path.name}"
        ):
            continue
        if all(
            _recorded_route_lines(round_dir / name / f"replay-seed-{seed}.jsonl")
            == value
            for name, seeds in declaration.sets.items()
            for seed in seeds
        ):
            declared.add(config_path)
    return frozenset(declared)


def _config_files_reading_the_field_on(replays: Path) -> list[str]:
    """Each ``experiment-config.json`` under ``replays`` that reads the field ON.

    The one exception is a candidate round's declared config whose round
    recorded the field ON; any other file reading it ON is listed, under
    ``samples/`` or ``ml_corpus/`` always.
    """

    declared = _declared_configs_recording_the_field_on(replays / "candidates")
    return [
        path.relative_to(replays.parent).as_posix()
        for path in sorted(replays.rglob("experiment-config.json"))
        if path not in declared
        and RecordedExperimentConfig.model_validate_json(
            path.read_text(encoding="utf-8")
        ).route_lines_version
        is not None
    ]


def _committed_payloads_reading_the_field_on(
    replays: Path, sets: Sequence[str]
) -> list[str]:
    """Each committed payload, config file under ``replays`` or set in ``sets`` reading it ON.

    A candidate round's declared config whose round recorded the field ON is the
    one file left out (:func:`_config_files_reading_the_field_on`).
    """

    if not sets:
        raise ValueError("the walk names no replay set")
    found: list[str] = []
    for suffix in (".jsonl", ".json"):
        for path in arms_tests._committed_files(suffix):
            text = path.read_text(encoding="utf-8")
            documents = (
                [json.loads(line) for line in text.splitlines()]
                if suffix == ".jsonl"
                else [json.loads(text)]
            )
            for document in documents:
                for payload in arms_tests._payloads(document):
                    if RecordedExperimentConfig.model_validate(
                        payload
                    ).route_lines_version:
                        found.append(path.relative_to(_REPO).as_posix())
    found += _config_files_reading_the_field_on(replays)
    for name in sets:
        first = min((replays / name).glob("replay-seed-*.jsonl"))
        recorded = recorded_experiment_config(read_all_entries(first))
        if (recorded or RecordedExperimentConfig()).route_lines_version is not None:
            found.append(name)
    return found


def test_every_committed_payload_reads_the_field_off() -> None:
    """A missing key means OFF: no committed payload, file or set reads the field ON.

    The byte test above cannot see a flipped default, since the omission keys on
    the default and the bytes would still round-trip; this one can. The one file
    that may read it ON is a candidate round's declared config whose round
    recorded it ON, enumerated from the candidate declarations.
    """

    found = _committed_payloads_reading_the_field_on(_REPO / "replays", _COMMITTED_SETS)
    assert found == []


#: The planted round's directory name in a scratch ``replays/`` tree.
_PLANTED_ROUND: Final[str] = "planted"
#: Each plant, and the files it must list.
_PLANTS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "as declared": (),
        "samples on": ("replays/samples/9p2i/experiment-config.json",),
        "corpus on": ("replays/ml_corpus/9p2i/experiment-config.json",),
        "a set recorded on": ("samples/9p2i",),
        "declares other bytes": (
            f"replays/candidates/{_PLANTED_ROUND}/experiment-config.json",
        ),
        "declares no set": (
            f"replays/candidates/{_PLANTED_ROUND}/experiment-config.json",
        ),
        "declares twice": (
            f"replays/candidates/{_PLANTED_ROUND}/experiment-config.json",
        ),
        "a seed recorded off": (
            f"replays/candidates/{_PLANTED_ROUND}/experiment-config.json",
        ),
        "a seed missing": (
            f"replays/candidates/{_PLANTED_ROUND}/experiment-config.json",
        ),
        "a round still recording": (),
    }
)


def _plant_replays(root: Path, games: _Games, plant: str) -> Path:
    """A scratch ``replays/``: round 2's declared set, and a round declaring the field ON.

    ``samples/9p2i`` holds round 2's declared file and the fake rehearsal's OFF
    game. The round's config is round 2's file with the field added (round 3's
    declared bytes), declared by its sha256 for two seeds whose replays are the
    fake rehearsal's ON game; ``plant`` perturbs one part.
    """

    off = _round_two_file()
    on = off.removesuffix("}\n") + ', "route_lines_version": 1}\n'
    replays = root / "replays"
    samples = replays / "samples" / "9p2i"
    samples.mkdir(parents=True)
    (samples / "experiment-config.json").write_text(
        on if plant == "samples on" else off, encoding="utf-8"
    )
    shown = games.fake_on if plant == "a set recorded on" else games.fake_off
    shutil.copyfile(shown, samples / "replay-seed-0.jsonl")
    if plant == "corpus on":
        corpus = replays / "ml_corpus" / "9p2i"
        corpus.mkdir(parents=True)
        (corpus / "experiment-config.json").write_text(on, encoding="utf-8")
    round_dir = replays / "candidates" / _PLANTED_ROUND
    (round_dir / "9p2i").mkdir(parents=True)
    (round_dir / "experiment-config.json").write_text(on, encoding="utf-8")
    named = off if plant == "declares other bytes" else on
    lines = [f"{hashlib.sha256(named.encode()).hexdigest()}  experiment-config.json"]
    if plant != "declares no set":
        lines.append(
            "9p2i seeds 0-2" if plant == "a seed missing" else "9p2i seeds 0-1"
        )
    block = "```candidate-declaration\n" + "\n".join(lines) + "\n```\n"
    (round_dir / "README.md").write_text(
        "# Planted round\n\n" + block * (2 if plant == "declares twice" else 1),
        encoding="utf-8",
    )
    shutil.copyfile(games.fake_on, round_dir / "9p2i" / "replay-seed-0.jsonl")
    second = games.fake_off if plant == "a seed recorded off" else games.fake_on
    shutil.copyfile(second, round_dir / "9p2i" / "replay-seed-1.jsonl")
    if plant == "a round still recording":
        recording = replays / "candidates" / "recording" / "9p2i"
        recording.mkdir(parents=True)
        shutil.copyfile(games.fake_on, recording / "replay-seed-0.jsonl")
    return replays


@pytest.mark.parametrize("plant", list(_PLANTS))
def test_only_a_declared_round_recording_the_field_on_may_read_it_on(
    games: _Games, tmp_path: Path, plant: str
) -> None:
    """Planted: the case's walk over a scratch ``replays/``, one part perturbed.

    An ON file under ``samples/`` or ``ml_corpus/`` is listed, and so is a listed
    set that recorded the field ON, and a round's ON file when its declaration
    names other bytes, names no set or appears twice, or a declared seed is
    missing or recorded the field OFF; the round as declared is not, nor a round
    that holds no config yet.
    """

    replays = _plant_replays(tmp_path, games, plant)
    found = _committed_payloads_reading_the_field_on(replays, ("samples/9p2i",))
    assert found == list(_PLANTS[plant])


def test_the_walk_refuses_to_read_no_set() -> None:
    with pytest.raises(ValueError, match="names no replay set"):
        _committed_payloads_reading_the_field_on(_REPO / "replays", ())


def test_without_its_omission_the_committed_payloads_and_files_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the field dropped from ``OMITTED_AT_DEFAULT``."""

    monkeypatch.setattr(
        experiment_config,
        "OMITTED_AT_DEFAULT",
        tuple(name for name in OMITTED_AT_DEFAULT if name != _FIELD),
    )
    mismatch, rows, _files = arms_tests._first_recorded_mismatch()
    first_file = min(arms_tests._ARCHIVE.glob("*.jsonl"))
    assert mismatch == f"{first_file.relative_to(_REPO)}:1"
    assert rows == 1
    assert _config_file_problems() == [
        "replays/candidates/stage-b-r1/experiment-config.json",
        "replays/samples/9p2i/experiment-config.json",
    ]


# ---------------------------------------------------------------------------
# The profile and its refusals
# ---------------------------------------------------------------------------


def test_the_profile_carries_it_from_the_config_alone() -> None:
    assert _FIELD in CONFIG_ONLY_PROFILE_FIELDS
    assert (
        MeetingEvidenceProfile.from_environment(
            {"AILIBI_ROUTE_LINES": "1", "AILIBI_ROUTE_LINES_VERSION": "1"}
        )
        == MeetingEvidenceProfile()
    )
    config = round_two_config(route_lines=True)
    assert profile_from_config(meeting_values(config)).route_lines_version == 1


@pytest.mark.parametrize("value", [0, 2, True, 1.0, "1"])
def test_the_profile_refuses_a_value_other_than_one_or_none(value: object) -> None:
    with pytest.raises(ValidationError):
        MeetingEvidenceProfile.model_validate({_FIELD: value})
    assert MeetingEvidenceProfile.model_validate({_FIELD: 1}).route_lines_version == 1


@pytest.mark.parametrize(
    "account", ["public_account_version", "attributed_testimony_version"]
)
def test_the_profile_refuses_it_beside_an_account_profile(account: str) -> None:
    with pytest.raises(ValidationError, match=_FIELD):
        MeetingEvidenceProfile.model_validate({_FIELD: 1, account: 1})
    assert MeetingEvidenceProfile.model_validate({account: 1})


def test_the_profile_refuses_it_beside_version_two_evidence() -> None:
    with pytest.raises(ValidationError, match="route_lines_version cannot run"):
        MeetingEvidenceProfile.model_validate(
            {_FIELD: 1, "evidence_reasoning_version": 2}
        )
    for evidence in (None, 1):
        assert MeetingEvidenceProfile.model_validate(
            {_FIELD: 1, "evidence_reasoning_version": evidence}
        )
    assert MeetingEvidenceProfile.model_validate({"evidence_reasoning_version": 2})


@pytest.mark.parametrize(
    "lever",
    [
        "AILIBI_IMPOSTOR_ROLL_CALL",
        "AILIBI_REPORTER_REASONING",
        "AILIBI_CORROBORATION_DISCIPLINE",
        "AILIBI_TESTIMONY_SHAPES",
    ],
)
def test_the_runner_refuses_it_beside_each_legacy_overlay(lever: str) -> None:
    with pytest.raises(ValueError, match=rf"ballot experiment \['{_FIELD}'\]"):
        build_default_meeting_runner(
            llm_client=FakeProvider(),
            env={"AILIBI_PROMPT_SET": _SET, lever: "1"},
            profile=MeetingEvidenceProfile(route_lines_version=1),
        )


def test_the_runner_refuses_it_for_a_set_whose_vote_body_has_no_live_guard() -> None:
    with pytest.raises(ValueError, match=f"carries no live '{_FIELD}' guard"):
        build_default_meeting_runner(
            llm_client=FakeProvider(),
            env={"AILIBI_PROMPT_SET": "qwen3_5_9b"},
            profile=MeetingEvidenceProfile(route_lines_version=1),
        )
    assert build_default_meeting_runner(
        llm_client=FakeProvider(),
        env={"AILIBI_PROMPT_SET": _SET},
        profile=MeetingEvidenceProfile(route_lines_version=1),
    )


def test_a_dead_guard_is_refused(tmp_path: Path) -> None:
    """Planted: the block's guard folded to a constant in a template copy."""

    root = tmp_path / "prompts"
    shutil.copytree(_REPO / "agents" / "strategic" / "prompts" / _SET, root / _SET)
    victim = root / _SET / VOTE_BALLOT_TEMPLATE
    guard = "{% if route_lines_version is defined and route_lines_version and route_lines %}"
    source = victim.read_text(encoding="utf-8")
    assert source.count(guard) == 1
    require_guarded_bodies(
        _SET, guard=_FIELD, templates=(VOTE_BALLOT_TEMPLATE,), root=root, env={}
    )
    victim.write_text(
        source.replace(guard, "{% if false and route_lines_version %}"),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match=f"carries no live '{_FIELD}' guard"):
        require_guarded_bodies(
            _SET, guard=_FIELD, templates=(VOTE_BALLOT_TEMPLATE,), root=root, env={}
        )


# ---------------------------------------------------------------------------
# The stamp
# ---------------------------------------------------------------------------


def test_the_stamp_is_derived_and_served_only_for_a_config_carrying_it() -> None:
    assert EXPERIMENT_ARM_TEMPLATES[_FIELD] == ("vote_ballot",)
    assert experiment_arm_suffix(_FIELD, 1) == "route_lines_v1"
    default = PROMPT_VERSION_SETS[_SET]
    carrying = prompt_versions_for_set(
        _SET, env={}, experiment_config=RecordedExperimentConfig(route_lines_version=1)
    )
    assert dict(carrying) == {**default, "vote_ballot": _STAMP}
    for config in (
        None,
        RecordedExperimentConfig(),
        round_two_config(route_lines=False),
    ):
        served = prompt_versions_for_set(_SET, env={}, experiment_config=config)
        assert _STAMP not in served["vote_ballot"]
    assert prompt_versions_for_set(_SET, env={}, experiment_config=None) is default


def test_round_threes_ballot_folds_the_three_arms_in_declaration_order() -> None:
    served = prompt_versions_for_set(
        _SET, env={}, experiment_config=round_two_config(route_lines=True)
    )
    assert served["vote_ballot"] == f"{_ROUND_TWO_BALLOT}+{_STAMP}"
    assert {k: v for k, v in served.items() if k != "vote_ballot"} == {
        k: v for k, v in PROMPT_VERSION_SETS[_SET].items() if k != "vote_ballot"
    }


def test_a_hand_written_route_lines_stamp_fails_the_derivation_test() -> None:
    assert arms_tests._registry_problems(game_module.EXPERIMENT_ARM_TEMPLATES) == []
    literal = MappingProxyType(
        {_FIELD: {"vote_ballot": "vote_ballot.qwen3_6_27b.v8.rl1"}}
    )
    assert arms_tests._registry_problems(literal) == [
        f"{_FIELD}: must name templates, got "
        "{'vote_ballot': 'vote_ballot.qwen3_6_27b.v8.rl1'}"
    ]


# ---------------------------------------------------------------------------
# The manager threads the lines to every ballot and to nothing else
# ---------------------------------------------------------------------------


@dataclass
class _Recorder:
    """A renderer double that records the keywords of every render."""

    inner: Callable[..., str]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def __call__(self, **kwargs: Any) -> str:
        self.calls.append(dict(kwargs))
        return self.inner(**kwargs)


def _threaded_meeting(
    profile: MeetingEvidenceProfile,
) -> tuple[dict[str, _Recorder], MeetingTranscript]:
    recorders = {
        "crewmate_report": _Recorder(_crewmate_report_prompt),
        "impostor_report": _Recorder(_impostor_report_prompt),
        "statement": _Recorder(_statement_prompt),
        "vote": _Recorder(_vote_prompt),
    }
    responder = _make_responder(
        observations={
            "p-2": (
                SawPlayerObservation(
                    type="saw_player", tick=5, subject="p-3", room="WEST_HALL"
                ),
            ),
            "p-4": (
                SawPlayerObservation(
                    type="saw_player", tick=6, subject="p-3", room="ADMIN"
                ),
                SawPlayerObservation(
                    type="saw_player", tick=3, subject="p-2", room="REACTOR"
                ),
                SawPlayerObservation(
                    type="saw_player", tick=5, subject="p-2", room="MEDBAY"
                ),
            ),
        }
    )
    manager = MeetingManager(
        llm_client=_ScriptedLLMClient(responder=responder),
        crewmate_report_prompt=recorders["crewmate_report"],
        impostor_report_prompt=recorders["impostor_report"],
        statement_prompt=recorders["statement"],
        vote_prompt=recorders["vote"],
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None)
        ),
        evidence_profile=profile,
    )
    result = _run_threaded(manager)
    return recorders, result.transcript


def _run_threaded(manager: MeetingManager) -> MeetingResult:
    return asyncio.new_event_loop().run_until_complete(
        manager.run(
            meeting_id="m-1",
            trigger=MeetingTrigger(
                triggered_by="p-1",
                trigger_tick=12,
                description="p-1 called an emergency meeting",
                kind="emergency",
            ),
            participants=tuple(_participant(f"p-{n}") for n in range(1, 6)),
            regroup_ticks=frozenset({4}),
        )
    )


def test_the_manager_threads_the_lines_to_every_ballot_and_to_nothing_else() -> None:
    recorders, transcript = _threaded_meeting(
        MeetingEvidenceProfile(route_lines_version=1)
    )
    ballots = recorders["vote"].calls
    assert len(ballots) == 5
    served = 0
    for call in ballots:
        assert call["route_lines_version"] == 1
        assert call["route_lines"] == build_route_lines(
            transcript=transcript,
            candidate_targets=call["candidate_targets"],
            regroup_ticks=frozenset({4}),
        )
        served += bool(call["route_lines"])
    # p-3 walks WEST_HALL to ADMIN; p-2 crosses the regroup at tick 4.
    assert served == 5
    readings = {
        step.reading
        for call in ballots
        for line in call["route_lines"]
        for step in line.steps
    }
    assert readings == {"walking_fits", "regroup_between"}
    for name in ("crewmate_report", "impostor_report", "statement"):
        for call in recorders[name].calls:
            assert "route_lines" not in call and _FIELD not in call
    assert recorders["statement"].calls


def test_the_manager_threads_no_line_when_the_field_is_off() -> None:
    recorders, _ = _threaded_meeting(MeetingEvidenceProfile())
    assert recorders["vote"].calls
    for call in recorders["vote"].calls:
        assert call["route_lines"] == ()
        assert call["route_lines_version"] is None


# ---------------------------------------------------------------------------
# The rehearsals
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Games:
    fake_off: Path
    fake_on: Path
    scripted_off: Path
    scripted_on: Path

    def directories(self) -> tuple[Path, ...]:
        return tuple(
            path.parent
            for path in (
                self.fake_off,
                self.fake_on,
                self.scripted_off,
                self.scripted_on,
            )
        )


@pytest.fixture(scope="module")
def games(tmp_path_factory: pytest.TempPathFactory) -> Iterator[_Games]:
    """The four rehearsal games, recorded in a bare shell (no ``AILIBI_*`` export)."""

    root = tmp_path_factory.mktemp("route-lines")
    with pytest.MonkeyPatch.context() as patch:
        for name in list(os.environ):
            if name.startswith("AILIBI_"):
                patch.delenv(name)
        recorded = _Games(
            fake_off=record_game(
                root / "fake-off" / "9p2i",
                seed=_FAKE_SEED,
                config=round_two_config(route_lines=False),
            ),
            fake_on=record_game(
                root / "fake-on" / "9p2i",
                seed=_FAKE_SEED,
                config=round_two_config(route_lines=True),
            ),
            scripted_off=record_routes_game(
                root / "scripted-off" / "9p2i", route_lines=False
            ),
            scripted_on=record_routes_game(
                root / "scripted-on" / "9p2i", route_lines=True
            ),
        )
    yield recorded


def _rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _meetings(path: Path) -> list[MeetingReplayEntry]:
    return [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    ]


def _ballot_calls(entry: MeetingReplayEntry) -> dict[str, str]:
    return {
        str(call.agent_id): call.prompt
        for call in entry.llm_calls
        if _SUSPICION_HEADER in call.prompt
    }


def _row_differences(off: Path, on: Path) -> list[str]:
    """How the ON rows differ from the OFF rows beyond the config key and the stamp."""

    off_rows, on_rows = _rows(off), _rows(on)
    if len(off_rows) != len(on_rows):
        return ["the games hold different row counts"]
    differences: list[str] = []
    for index, (off_row, on_row) in enumerate(zip(off_rows, on_rows, strict=True)):
        on_copy = json.loads(json.dumps(on_row))
        config = on_copy.get("experiment_config")
        if isinstance(config, dict):
            if config.pop(_FIELD, None) != 1:
                differences.append(f"row {index}: the config does not carry the field")
        versions = on_copy.get("prompt_versions")
        if isinstance(versions, dict):
            off_stamp = off_row["prompt_versions"]["vote_ballot"]
            if versions["vote_ballot"] != f"{off_stamp}+{_STAMP}":
                differences.append(f"row {index}: the ballot stamp is not the arm's")
            versions["vote_ballot"] = off_stamp
        if on_copy != off_row:
            differences.append(f"row {index}: differs beyond the key and the stamp")
    return differences


def test_the_fake_rehearsal_is_inert(games: _Games) -> None:
    assert _row_differences(games.fake_off, games.fake_on) == []
    meetings = _meetings(games.fake_on)
    assert meetings
    for entry in meetings:
        assert entry.prompt_versions["vote_ballot"] == f"{_ROUND_TWO_BALLOT}+{_STAMP}"
        for call in entry.llm_calls:
            assert route_block_span(call.prompt) is None
    # Planted: a row whose state hash moved is caught.
    rows = _rows(games.fake_on)
    tick = next(index for index, row in enumerate(rows) if row.get("kind") == "tick")
    rows[tick]["state_hash"] = "0" * 16
    moved = games.fake_on.parent / "moved.jsonl"
    moved.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert _row_differences(games.fake_off, moved) == [
        f"row {tick}: differs beyond the key and the stamp"
    ]
    moved.unlink()


def test_the_scripted_rehearsal_serves_both_readings_and_no_step_for_the_left_out_change(
    games: _Games,
) -> None:
    on, off = _meetings(games.scripted_on), _meetings(games.scripted_off)
    assert len(on) == len(off) >= 2
    readings: set[str] = set()
    carried = 0
    for entry in on:
        for prompt in _ballot_calls(entry).values():
            lines = parse_route_lines(prompt)
            carried += bool(lines)
            readings |= {step.reading for line in lines for step in line.steps}
    assert carried > 0
    assert readings == {"walking_fits", "regroup_between"}
    # Meeting 0 states ADMIN then REACTOR one tick apart for the opener: three
    # doors and no regroup between, so no step ends in REACTOR there.
    opener = on[0].triggered_by
    first = [
        line
        for prompt in _ballot_calls(on[0]).values()
        for line in parse_route_lines(prompt)
        if line.subject == opener
    ]
    assert first and all(
        "REACTOR" not in step.from_rooms + step.to_rooms
        for line in first
        for step in line.steps
    )
    # The one ejection rests on the walk: the opener is ejected at meeting 0.
    assert on[0].ejected_player_id == opener


def test_each_scripted_on_ballot_minus_its_block_is_its_off_twin_and_the_tally_holds(
    games: _Games,
) -> None:
    for on_entry, off_entry in zip(
        _meetings(games.scripted_on), _meetings(games.scripted_off), strict=True
    ):
        on_ballots, off_ballots = _ballot_calls(on_entry), _ballot_calls(off_entry)
        assert set(on_ballots) == set(off_ballots)
        for voter, prompt in on_ballots.items():
            assert without_route_block(prompt) == off_ballots[voter]
        # A fake ballot's free text follows its prompt's bytes; the tally reads
        # only targets and confidences, which match.
        assert [(b.voter, b.target, b.confidence) for b in on_entry.ballots] == [
            (b.voter, b.target, b.confidence) for b in off_entry.ballots
        ]
        assert on_entry.ejected_player_id == off_entry.ejected_player_id
        assert on_entry.outcome == off_entry.outcome
        assert on_entry.state_hash_after == off_entry.state_hash_after


def test_every_rehearsal_game_verifies_and_reproduces_through_the_golden(
    games: _Games,
) -> None:
    for directory in games.directories():
        seed = next(directory.glob("replay-seed-*.jsonl")).stem.removeprefix(
            "replay-seed-"
        )
        replay = ReplayLoader(replay_dir=directory).load_replay(f"headless-seed-{seed}")
        assert replay.metadata.outcome_verified
        walk = golden.walk_directory(directory)
        assert walk.meetings > 0
        assert walk.prompts and all(prompt.reproduced for prompt in walk.prompts)
        assert walk.miscounted_meetings == ()


def _ballots_carrying_the_block(directory: Path) -> set[tuple[str, str]]:
    return {
        (entry.meeting_id, voter)
        for path in directory.glob("replay-seed-*.jsonl")
        for entry in _meetings(path)
        for voter, prompt in _ballot_calls(entry).items()
        if route_block_span(prompt) is not None
    }


def _failing_ballots(directory: Path) -> set[tuple[str, str]]:
    return {
        (prompt.meeting_id, str(prompt.agent_id))
        for prompt in golden.walk_directory(directory).prompts
        if not prompt.reproduced
    }


def test_the_scripted_on_game_walked_without_the_field_fails_at_every_block(
    games: _Games, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: the field dropped from the walk's profile."""

    real = profile_from_config

    def _dropped(values: Mapping[str, object]) -> MeetingEvidenceProfile:
        return real({**values, _FIELD: None})

    monkeypatch.setattr(golden, "profile_from_config", _dropped)
    carrying = _ballots_carrying_the_block(games.scripted_on.parent)
    assert carrying
    assert _failing_ballots(games.scripted_on.parent) == carrying


def test_the_manager_passing_no_lines_fails_the_scripted_on_golden(
    games: _Games, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Perturbed: the manager hands every ballot ``()``."""

    def _none(**kwargs: object) -> tuple[RouteLine, ...]:
        return ()

    monkeypatch.setattr(manager_module, "build_route_lines", _none)
    carrying = _ballots_carrying_the_block(games.scripted_on.parent)
    assert _failing_ballots(games.scripted_on.parent) == carrying


# ---------------------------------------------------------------------------
# Every reader of a ballot reads an ON ballot as before
# ---------------------------------------------------------------------------


def _suspicion_region(prompt: str) -> str:
    return prompt.split(_SUSPICION_HEADER, 1)[1].split("## ", 1)[0]


def _ballot_reader_problems(on: str, off: str, *, voter: str) -> list[str]:
    """Where a ballot reader reads the ON ballot differently from its OFF twin."""

    problems: list[str] = []
    if _suspicion_region(on) != _suspicion_region(off):
        problems.append("the suspicion block moved")
    if _parse_suspicion_graph(on) != _parse_suspicion_graph(off):
        problems.append("the suspicion parse moved")
    if _parse_valid_targets(on) != _parse_valid_targets(off):
        problems.append("the valid-target parse moved")
    if parse_rendered_max_suspicion(on) != parse_rendered_max_suspicion(off):
        problems.append("the rendered maximum moved")
    if served_own_kill_rows(on, holder=voter) != served_own_kill_rows(
        off, holder=voter
    ):
        problems.append("the own-kill rows moved")
    for subject in _parse_suspicion_graph(off):
        meetings = [
            SimpleNamespace(llm_calls=[SimpleNamespace(prompt=prompt)])
            for prompt in (on, off)
        ]
        if _rendered_suspicions(meetings[0], subject) != _rendered_suspicions(  # type: ignore[arg-type]
            meetings[1],  # type: ignore[arg-type]
            subject,
        ):
            problems.append("the railroad tripwire's read moved")
    return problems


def test_every_ballot_reader_reads_an_on_ballot_as_its_off_twin(games: _Games) -> None:
    checked = 0
    for on_entry, off_entry in zip(
        _meetings(games.scripted_on), _meetings(games.scripted_off), strict=True
    ):
        off_ballots = _ballot_calls(off_entry)
        for voter, prompt in _ballot_calls(on_entry).items():
            if route_block_span(prompt) is None:
                continue
            checked += 1
            assert (
                _ballot_reader_problems(prompt, off_ballots[voter], voter=voter) == []
            )
    assert checked > 0


def test_the_block_moved_under_the_suspicion_header_fails_the_suspicion_parse_test(
    games: _Games,
) -> None:
    """Planted: the route block rendered under the suspicion header instead."""

    entry = _meetings(games.scripted_on)[0]
    voter, prompt = next(
        (voter, prompt)
        for voter, prompt in _ballot_calls(entry).items()
        if route_block_span(prompt) is not None
    )
    off = without_route_block(prompt)
    span = route_block_span(prompt)
    assert span is not None
    block = "\n".join(prompt.split("\n")[span[0] : span[1] + 1])
    moved = off.replace(f"{_SUSPICION_HEADER}\n", f"{_SUSPICION_HEADER}\n{block}\n", 1)
    assert "the suspicion block moved" in _ballot_reader_problems(
        moved, off, voter=voter
    )


# ---------------------------------------------------------------------------
# Readers thread or refuse
# ---------------------------------------------------------------------------


def _win_condition(directory: Path) -> object:
    path = next(directory.glob("replay-seed-*.jsonl"))
    seed = int(path.stem.removeprefix("replay-seed-"))
    return check_replay_win_condition(
        path, seed=seed, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )


#: Each instrument that reads :data:`READABLE_SETTINGS`, the module holding its
#: field list, that list's name, and an entry point over a whole directory.
_INSTRUMENTS: Final[dict[str, tuple[Any, str, Callable[[Path], object]]]] = {
    "kill-craft": (kill_craft_module, "KILL_CRAFT_READS", compute_kill_craft_report),
    "funnel": (funnel_module, "FUNNEL_READS", compute_information_funnel),
    "pooling-funnel": (funnel_module, "FUNNEL_READS", compute_pooling_funnel),
    "solvability": (
        solvability_module,
        "SOLVABILITY_READS",
        compute_solvability_report,
    ),
    "win-condition": (win_condition_module, "WIN_CONDITION_READS", _win_condition),
    "evidence-honesty": (
        evidence_honesty_module,
        "HONESTY_READS",
        compute_evidence_honesty,
    ),
    "watchability-referee": (
        watchability_module,
        "REFEREE_READS",
        compute_watchability,
    ),
}


def test_every_instrument_reads_the_readable_settings_whole() -> None:
    for module, name, _run in _INSTRUMENTS.values():
        assert getattr(module, name) == READABLE_SETTINGS
    assert _FIELD in READABLE_SETTINGS
    assert getattr(golden, "READABLE_SETTINGS") is READABLE_SETTINGS


@pytest.mark.parametrize("instrument", sorted(_INSTRUMENTS))
def test_each_instrument_completes_on_the_scripted_on_recording(
    games: _Games, instrument: str
) -> None:
    _module, _name, run = _INSTRUMENTS[instrument]
    report = run(games.scripted_on.parent)
    assert report is not None
    if instrument == "watchability-referee":
        assert report.integrity_ok is True  # type: ignore[attr-defined]


@pytest.mark.parametrize("instrument", sorted(_INSTRUMENTS))
def test_each_instrument_refuses_it_once_the_field_leaves_its_reads(
    games: _Games, monkeypatch: pytest.MonkeyPatch, instrument: str
) -> None:
    module, name, run = _INSTRUMENTS[instrument]
    monkeypatch.setattr(module, name, READABLE_SETTINGS - {_FIELD})
    with pytest.raises(ValueError, match=f"does not read the recorded {_FIELD}=1"):
        run(games.scripted_on.parent)


def test_the_golden_refuses_it_once_the_field_leaves_its_reads(
    games: _Games, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(golden, "READABLE_SETTINGS", READABLE_SETTINGS - {_FIELD})
    with pytest.raises(ValueError, match=f"does not read the recorded {_FIELD}=1"):
        golden.walk_directory(games.scripted_on.parent)


def test_the_census_reads_it_by_its_route_lines_predicate() -> None:
    """The census reads the field by the predicate that scopes its route line cells."""

    use = FIELD_CLASSIFICATION[_FIELD]
    assert use.predicates == ("route_lines",)
    assert not use.reason and not use.value_read_by
