"""The body-handle arm: a report opening names the corpse without its kill tick.

The engine names a corpse ``body-<victim>-<death tick>``, and with the arm OFF a
report meeting's opening prompt carries that id in its trigger line. With the
recorded field ``report_body_handle_version = 1`` the trigger builder
(``orchestrator.game._build_meeting_trigger``) names the corpse by the victim's
public handle ``body-<victim>`` instead, as temporal mode already does, and
changes nothing else. This module holds that contract:

* in fake games recorded with the arm, no recorded prompt carries a kill-tick
  handle and each report opening reads the public handle (a builder without the
  substitution fails both);
* ON versus OFF on the same seed, only the report openings differ, and each by
  exactly its one handle: equal state hashes and call counts, byte-identical
  emergency openings, every other prompt byte-identical once the fake provider's
  prompt-seeded tokens are normalized, or raw under a client whose answers do
  not depend on the handle; no temporal version; the registry's prompt stamps;
* the builder, over generated meetings, changes only a reported corpse's handle,
  never falls back to the engine id and leaves temporal mode's text alone;
* the field round-trips, is omitted at its default and no longer pending;
* the prompt-byte golden re-renders an arm-ON recording through the recorded
  value, and misses the opening without it; a plain shell loads the recording;
* with the meeting reset, a report after a regroup names the public handle and a
  button meeting names no body;
* the gameplay census's opening-handle cell reads 0 on an arm-ON recording, and
  a copy with one kill-tick handle given back raises its conformance guard.

Every recording is a fake game written under ``tmp_path``. No test reads a
committed set, and no prompt is printed: failures name handles, meetings and
counts only.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Final, Literal, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

import orchestrator.game as game_module
import tests.meetings.test_prompt_byte_golden as golden
from agents.strategic.prompts.loader import DEFAULT_PROMPT_SET
from api.replay_loader import ReplayLoader
from engine.entities import BodyState
from engine.events import ActionRejectedEvent, MeetingTriggeredEvent, MovedEvent
from engine.world import Map, WorldState, load_canonical_map
from eval.gameplay_census import CENSUS_WALK_CONFIG, GameplayCensusConformanceError
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkEvent,
    TickAdvanced,
    walk_replay,
)
from experiments.held_out_prefixes import LEGACY_BODY_HANDLE_PATTERN
from llm.client import CallKind, LLMClient, LLMResponse
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import profile_from_config
from meetings.manager import EMERGENCY_TRIGGER_PHRASE, MeetingTrigger
from observation.body_ids import public_body_id
from orchestrator.experiment_config import (
    WAVE_ARMS_PENDING,
    RecordedExperimentConfig,
    meeting_values,
)
from orchestrator.game import (  # noqa: PLC2701
    HeadlessGame,
    _build_meeting_trigger,
    build_default_agent_factory,
    build_default_meeting_runner,
    prompt_versions_for_set,
)
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLogEntry,
    read_all_entries,
    recorded_experiment_config,
    recorded_substrate_flags,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_SCRIPTS: Final[Path] = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import publish_gameplay_census as census_command  # noqa: E402
from _manifest_writer import update_manifest  # noqa: E402

TriggerKind = Literal["report", "emergency"]
Built = tuple[MeetingTrigger, str | None, TriggerKind]
Builder = Callable[..., Built]

#: The prompt set every committed recording and the round-1 candidate use.
ROUND_ONE_SET: Final[str] = "qwen3_6_27b"
ARM_ON: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    report_body_handle_version=1
)
RESET: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    meeting_reset="hub_with_grace"
)
RESET_AND_ARM: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    meeting_reset="hub_with_grace", report_body_handle_version=1
)

#: The fake provider seeds every string field of a reply from a hash of its
#: prompt (``llm/fake_provider.py``), so a reply quoted by a later prompt differs
#: whenever the prompt it answered did.
FAKE_TOKEN: Final[re.Pattern[str]] = re.compile(r"fake-[a-z_]+-[0-9a-f]{8}")

_MAP: Final[Map] = load_canonical_map()
_NINE_PLAYERS: Final[WorldState] = seed_initial_state(
    seed=0, game_map=_MAP, num_players=9, num_impostors=2
)


# --------------------------------------------------------------------------- #
# Recording fake games                                                        #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _Game:
    """One fake game's shape: seed, roster and the scheduler's tick cap."""

    seed: int
    num_players: int
    num_impostors: int
    tasks_per_crewmate: int
    max_ticks: int | None

    @property
    def roster(self) -> str:
        return f"{self.num_players}p{self.num_impostors}i"


#: The OFF control's shape (``tests/orchestrator/test_temporal_delivery.py``):
#: two report meetings, the first on p-3's corpse killed at tick 4, reported at 8.
SEED_1: Final[_Game] = _Game(1, 7, 1, 1, 80)
#: Four report meetings in its first 200 ticks, at the candidate's roster.
SEED_12: Final[_Game] = _Game(12, 9, 2, 2, 200)
#: A full game at the candidate's roster whose first meeting is a button call;
#: under the meeting reset its later reports each follow a regroup.
SEED_0: Final[_Game] = _Game(0, 9, 2, 2, None)


@dataclass
class _HandleBlindClient:
    """The fake provider, answering each prompt as if its handles carried no tick.

    Every ``body-p-N-T`` in the prompt is read as ``body-p-N`` before the fake
    seeds its reply, so an arm-ON and an arm-OFF game receive the same replies
    and the prompts after each opening can be compared byte for byte.
    """

    fake: FakeProvider = field(default_factory=FakeProvider)

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        return await self.fake.complete(
            prompt=_without_kill_ticks(prompt),
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )


def _without_kill_ticks(text: str) -> str:
    return LEGACY_BODY_HANDLE_PATTERN.sub(
        lambda match: match.group(0).rsplit("-", 1)[0], text
    )


@dataclass(frozen=True)
class _Recording:
    """How one named recording is made."""

    game: _Game
    config: RecordedExperimentConfig | None
    prompt_set: str = ROUND_ONE_SET
    blind: bool = False


RECORDINGS: Final[Mapping[str, _Recording]] = {
    "seed1-off": _Recording(SEED_1, None, DEFAULT_PROMPT_SET),
    "seed1-on": _Recording(SEED_1, ARM_ON, DEFAULT_PROMPT_SET),
    "seed1-round-one-on": _Recording(SEED_1, ARM_ON),
    "seed12-off": _Recording(SEED_12, None, DEFAULT_PROMPT_SET),
    "seed12-on": _Recording(SEED_12, ARM_ON, DEFAULT_PROMPT_SET),
    "seed12-round-one-on": _Recording(SEED_12, ARM_ON),
    "seed0-off": _Recording(SEED_0, None),
    "seed0-on": _Recording(SEED_0, ARM_ON),
    "seed1-blind-off": _Recording(SEED_1, None, blind=True),
    "seed1-blind-on": _Recording(SEED_1, ARM_ON, blind=True),
    "seed12-blind-off": _Recording(SEED_12, None, blind=True),
    "seed12-blind-on": _Recording(SEED_12, ARM_ON, blind=True),
    "seed0-reset-off": _Recording(SEED_0, RESET),
    "seed0-reset-on": _Recording(SEED_0, RESET_AND_ARM),
}


@dataclass(frozen=True)
class _Opening:
    """A meeting's opening call and the trigger the live builder gave it."""

    meeting: MeetingReplayEntry
    trigger: MeetingTrigger
    engine_body_id: str | None
    call_index: int

    @property
    def prompt(self) -> str:
        return self.meeting.llm_calls[self.call_index].prompt

    @property
    def public_text(self) -> str:
        """The trigger line naming the corpse by its public handle."""

        victim = self.trigger.body_victim_id
        assert victim is not None, self.meeting.meeting_id
        return (
            f"{self.trigger.triggered_by} reported body {public_body_id(victim)} "
            f"at tick {self.trigger.trigger_tick}"
        )


@dataclass(frozen=True)
class _Played:
    """One recorded fake game and the triggers its live builder returned."""

    directory: Path
    game: _Game
    entries: tuple[ReplayLogEntry, ...]
    built: tuple[Built, ...]

    @property
    def path(self) -> Path:
        return self.directory / f"replay-seed-{self.game.seed}.jsonl"

    @property
    def meetings(self) -> tuple[MeetingReplayEntry, ...]:
        return tuple(e for e in self.entries if isinstance(e, MeetingReplayEntry))

    @property
    def ticks(self) -> tuple[ReplayEntry, ...]:
        return tuple(e for e in self.entries if isinstance(e, ReplayEntry))

    def prompts(self) -> tuple[str, ...]:
        """Every recorded prompt: each call of every meeting, retries included."""

        return tuple(
            call.prompt
            for entry in self.entries
            if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry))
            for call in entry.llm_calls
        )

    def openings(self) -> tuple[_Opening, ...]:
        meetings = self.meetings
        assert len(meetings) == len(self.built), self.directory
        openings = []
        for meeting, (trigger, body_id, _kind) in zip(meetings, self.built):
            assert trigger.triggered_by == meeting.triggered_by, meeting.meeting_id
            index = next(
                i
                for i, call in enumerate(meeting.llm_calls)
                if call.agent_id == meeting.triggered_by
            )
            openings.append(_Opening(meeting, trigger, body_id, index))
        return tuple(openings)

    def report_openings(self) -> tuple[_Opening, ...]:
        return tuple(o for o in self.openings() if o.trigger.kind == "report")


def _play(
    directory: Path,
    recording: _Recording,
    *,
    builder: Builder | None = None,
    env: Mapping[str, str] | None = None,
) -> _Played:
    """Record one fake game into ``directory`` with ``builder`` as the live builder.

    The meeting runner is built from the recording's config and an explicit
    environment naming only the prompt set (plus ``env``), never the shell's.
    """

    game = recording.game
    config = recording.config
    directory.mkdir(parents=True, exist_ok=True)
    client: LLMClient = _HandleBlindClient() if recording.blind else FakeProvider()
    runner = build_default_meeting_runner(
        llm_client=client,
        env={"AILIBI_PROMPT_SET": recording.prompt_set, **(env or {})},
        profile=(
            profile_from_config(meeting_values(config)) if config is not None else None
        ),
    )
    inner: Builder = builder if builder is not None else _build_meeting_trigger
    built: list[Built] = []

    def _capturing(**kwargs: Any) -> Built:
        result = inner(**kwargs)
        built.append(result)
        return result

    path = directory / f"replay-seed-{game.seed}.jsonl"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(game_module, "_build_meeting_trigger", _capturing)
        HeadlessGame(
            seed=game.seed,
            num_players=game.num_players,
            num_impostors=game.num_impostors,
            tasks_per_crewmate=game.tasks_per_crewmate,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(experiment_config=config),
            replay_path=path,
            audit_log_path=Path(os.devnull),
            scheduler=(
                TickScheduler(max_ticks=game.max_ticks)
                if game.max_ticks is not None
                else None
            ),
            meeting_runner=runner,
            experiment_config=config,
        ).run()
    (directory / "roster.json").write_text(
        json.dumps(
            {
                "num_players": game.num_players,
                "num_impostors": game.num_impostors,
                "tasks_per_crewmate": game.tasks_per_crewmate,
            }
        ),
        encoding="utf-8",
    )
    update_manifest(
        directory / "MANIFEST.md",
        directory,
        [game.seed],
        git_sha="scripted",
        refreshed_at="2026-09-26",
    )
    return _Played(directory, game, read_all_entries(path), tuple(built))


class _Recordings:
    """The named recordings, each recorded once per module on first use."""

    def __init__(self, root: Path) -> None:
        self._root = root
        self._played: dict[str, _Played] = {}

    def __getitem__(self, name: str) -> _Played:
        if name not in self._played:
            recording = RECORDINGS[name]
            self._played[name] = _play(
                self._root / name / recording.game.roster, recording
            )
        return self._played[name]


@pytest.fixture(scope="module")
def recorded(tmp_path_factory: pytest.TempPathFactory) -> _Recordings:
    return _Recordings(tmp_path_factory.mktemp("body-handle"))


# --------------------------------------------------------------------------- #
# The checks, as functions a planted case can fail                            #
# --------------------------------------------------------------------------- #


def _kill_tick_handles(played: _Played) -> list[str]:
    """Every kill-tick handle in any recorded prompt (handles only, no text)."""

    return [
        match
        for prompt in played.prompts()
        for match in LEGACY_BODY_HANDLE_PATTERN.findall(prompt)
    ]


def _openings_without_the_public_handle(played: _Played) -> list[str]:
    """Report meetings whose opening does not name the corpse by its public handle."""

    return [
        opening.meeting.meeting_id
        for opening in played.report_openings()
        if opening.public_text not in opening.prompt
    ]


def _hash_and_count_differences(off: _Played, on: _Played) -> list[str]:
    problems = []
    if [row.state_hash for row in off.ticks] != [row.state_hash for row in on.ticks]:
        problems.append("tick state hashes")
    if [(m.state_hash_before, m.state_hash_after) for m in off.meetings] != [
        (m.state_hash_before, m.state_hash_after) for m in on.meetings
    ]:
        problems.append("meeting state hashes")
    if [len(m.llm_calls) for m in off.meetings] != [
        len(m.llm_calls) for m in on.meetings
    ]:
        problems.append("call counts")
    return problems


def _opening_differences(off: _Played, on: _Played) -> list[str]:
    """Openings that differ other than by their one engine id's public handle."""

    problems = []
    for off_opening, on_opening in zip(off.openings(), on.openings(), strict=True):
        where = off_opening.meeting.meeting_id
        if off_opening.trigger.kind == "emergency":
            if on_opening.prompt != off_opening.prompt:
                problems.append(f"{where}: emergency opening")
            continue
        engine_id = off_opening.engine_body_id
        victim = off_opening.trigger.body_victim_id
        assert engine_id is not None and victim is not None, where
        if off_opening.prompt.count(engine_id) != 1:
            problems.append(f"{where}: {engine_id} appears other than once")
        expected = off_opening.prompt.replace(engine_id, public_body_id(victim))
        if on_opening.prompt != expected:
            problems.append(f"{where}: report opening")
    return problems


def _other_prompt_differences(
    off: _Played, on: _Played, *, normalize: bool
) -> list[str]:
    """Non-opening prompts that differ, optionally after normalizing fake tokens."""

    def _form(prompt: str) -> str:
        return FAKE_TOKEN.sub("fake", prompt) if normalize else prompt

    problems = []
    for off_opening, on_opening in zip(off.openings(), on.openings(), strict=True):
        pairs = zip(
            off_opening.meeting.llm_calls, on_opening.meeting.llm_calls, strict=True
        )
        for index, (off_call, on_call) in enumerate(pairs):
            if index == off_opening.call_index:
                continue
            if _form(off_call.prompt) != _form(on_call.prompt):
                problems.append(f"{off_opening.meeting.meeting_id} call {index}")
    return problems


def _temporal_marks(played: _Played) -> list[str]:
    marks = [
        f"tick {row.tick} carries temporal version {row.temporal_observation_version}"
        for row in played.ticks
        if row.temporal_observation_version is not None
    ]
    flags = recorded_substrate_flags(played.entries)
    if flags is None or flags.get("temporal_observations") is not False:
        marks.append("substrate_flags.temporal_observations is not false")
    return marks


def _prompt_version_differences(played: _Played, prompt_set: str) -> list[str]:
    expected = dict(prompt_versions_for_set(prompt_set))
    return [
        meeting.meeting_id
        for meeting in played.meetings
        if dict(meeting.prompt_versions) != expected
    ]


# --------------------------------------------------------------------------- #
# The leak closes in play                                                     #
# --------------------------------------------------------------------------- #


ARM_ON_GAMES: Final[tuple[str, ...]] = (
    "seed1-on",
    "seed1-round-one-on",
    "seed12-on",
    "seed12-round-one-on",
    "seed0-on",
)


@pytest.mark.parametrize("name", ARM_ON_GAMES)
def test_no_recorded_prompt_carries_a_kill_tick_handle_under_the_arm(
    recorded: _Recordings, name: str
) -> None:
    played = recorded[name]
    assert recorded_experiment_config(played.entries) == ARM_ON
    assert played.report_openings()
    assert _kill_tick_handles(played) == []
    assert _openings_without_the_public_handle(played) == []


@pytest.mark.parametrize("name", ["seed1-on", "seed1-round-one-on"])
def test_the_first_report_reads_the_public_handle_at_its_report_tick(
    recorded: _Recordings, name: str
) -> None:
    first = recorded[name].report_openings()[0]
    assert first.engine_body_id == "body-p-3-4"
    reads = "reported body body-p-3 at tick 8" in first.prompt
    assert reads, first.meeting.meeting_id


def _without_the_substitution(**kwargs: Any) -> Built:
    """Planted: the builder with the arm's substitution removed."""

    return _build_meeting_trigger(**{**kwargs, "report_body_handle_version": None})


@pytest.mark.parametrize("name", ["seed1-on", "seed12-round-one-on"])
def test_a_builder_without_the_substitution_fails_both_leak_checks(
    tmp_path: Path, name: str
) -> None:
    planted = _play(
        tmp_path / name, RECORDINGS[name], builder=_without_the_substitution
    )
    assert recorded_experiment_config(planted.entries) == ARM_ON
    assert planted.report_openings()
    assert _kill_tick_handles(planted) != []
    assert _openings_without_the_public_handle(planted) == [
        opening.meeting.meeting_id for opening in planted.report_openings()
    ]
    if name == "seed1-on":
        first = planted.report_openings()[0]
        reads = "reported body body-p-3 at tick 8" in first.prompt
        assert not reads, first.meeting.meeting_id


# --------------------------------------------------------------------------- #
# OFF bytes and the comparison's teeth                                        #
# --------------------------------------------------------------------------- #


NARROWNESS_PAIRS: Final[tuple[tuple[str, str, bool], ...]] = (
    ("seed1-off", "seed1-on", True),
    ("seed12-off", "seed12-on", True),
    ("seed0-off", "seed0-on", True),
    ("seed1-blind-off", "seed1-blind-on", False),
    ("seed12-blind-off", "seed12-blind-on", False),
)


@pytest.mark.parametrize(("off_name", "on_name", "_normalize"), NARROWNESS_PAIRS)
def test_forcing_the_arm_on_changes_every_report_opening(
    recorded: _Recordings, off_name: str, on_name: str, _normalize: bool
) -> None:
    # The OFF game names each corpse by its engine id, so the ON comparison
    # below has a difference to find in every report meeting.
    off, on = recorded[off_name], recorded[on_name]
    assert recorded_experiment_config(off.entries) is None
    reports = list(zip(off.report_openings(), on.report_openings(), strict=True))
    assert reports
    for off_opening, on_opening in reports:
        where = off_opening.meeting.meeting_id
        engine_id = off_opening.engine_body_id
        assert engine_id is not None, where
        names_engine_id = engine_id in off_opening.prompt
        differs = on_opening.prompt != off_opening.prompt
        assert names_engine_id and differs, where
    assert len(_kill_tick_handles(off)) == len(reports)


def test_the_off_control_reads_the_engine_id(recorded: _Recordings) -> None:
    first = recorded["seed1-off"].report_openings()[0]
    reads = "reported body body-p-3-4 at tick 8" in first.prompt
    assert reads, first.meeting.meeting_id


# --------------------------------------------------------------------------- #
# Only the report openings differ                                             #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("off_name", "on_name", "normalize"), NARROWNESS_PAIRS)
def test_only_the_report_openings_differ(
    recorded: _Recordings, off_name: str, on_name: str, normalize: bool
) -> None:
    off, on = recorded[off_name], recorded[on_name]
    assert _hash_and_count_differences(off, on) == []
    assert _opening_differences(off, on) == []
    assert _other_prompt_differences(off, on, normalize=normalize) == []
    assert _temporal_marks(on) == [] and _temporal_marks(off) == []
    prompt_set = RECORDINGS[on_name].prompt_set
    assert _prompt_version_differences(on, prompt_set) == []
    assert _prompt_version_differences(off, prompt_set) == []


def test_the_normalization_is_needed_and_the_blind_client_removes_the_need(
    recorded: _Recordings,
) -> None:
    # The fake's replies follow the handle, so raw non-opening prompts differ;
    # under the blind client they do not.
    raw = _other_prompt_differences(
        recorded["seed1-off"], recorded["seed1-on"], normalize=False
    )
    assert raw
    assert not _other_prompt_differences(
        recorded["seed1-blind-off"], recorded["seed1-blind-on"], normalize=False
    )


def test_the_narrowness_games_hold_both_opening_kinds(recorded: _Recordings) -> None:
    kinds = [
        opening.trigger.kind
        for off_name, _on, _n in NARROWNESS_PAIRS
        for opening in recorded[off_name].openings()
    ]
    assert kinds.count("emergency") >= 1
    assert kinds.count("report") >= 8


def test_the_round_one_stamps_are_the_registry_defaults(recorded: _Recordings) -> None:
    stamps = {
        dict(m.prompt_versions)["vote_ballot"] for m in recorded["seed0-on"].meetings
    }
    assert stamps == {"vote_ballot.qwen3_6_27b.v8"}
    versions = dict(recorded["seed0-on"].meetings[0].prompt_versions)
    for kind in ("crewmate_report", "impostor_report", "accusation_round"):
        assert versions[kind] == f"{kind}.qwen3_6_27b.v6"


def _alters_the_report_tick(**kwargs: Any) -> Built:
    """Planted: the arm's substitution plus a moved ``at tick T``."""

    trigger, body_id, kind = _build_meeting_trigger(**kwargs)
    if kind == "report":
        tick = trigger.trigger_tick
        trigger = replace(
            trigger,
            description=trigger.description.replace(
                f" at tick {tick}", f" at tick {tick + 1}"
            ),
        )
    return trigger, body_id, kind


def _drops_the_report_tick(**kwargs: Any) -> Built:
    """Planted: the arm's substitution with ``at tick T`` dropped."""

    trigger, body_id, kind = _build_meeting_trigger(**kwargs)
    if kind == "report":
        trigger = replace(
            trigger,
            description=trigger.description.replace(
                f" at tick {trigger.trigger_tick}", ""
            ),
        )
    return trigger, body_id, kind


@pytest.mark.parametrize("planted", [_alters_the_report_tick, _drops_the_report_tick])
def test_a_builder_that_moves_the_report_tick_fails_the_opening_equality(
    recorded: _Recordings, tmp_path: Path, planted: Builder
) -> None:
    on = _play(tmp_path / "planted", RECORDINGS["seed1-on"], builder=planted)
    off = recorded["seed1-off"]
    assert _hash_and_count_differences(off, on) == []
    assert _kill_tick_handles(on) == []
    assert _opening_differences(off, on) == [
        f"{opening.meeting.meeting_id}: report opening"
        for opening in off.report_openings()
    ]


def test_temporal_observations_fail_the_no_temporal_check(tmp_path: Path) -> None:
    # Planted: the same arm-ON game with the temporal lever exported to the
    # runner records temporal rows, which the narrowness check refuses.
    temporal = _play(
        tmp_path / "temporal",
        RECORDINGS["seed1-on"],
        env={"AILIBI_TEMPORAL_OBSERVATIONS": "2"},
    )
    marks = _temporal_marks(temporal)
    assert marks and marks[-1] == "substrate_flags.temporal_observations is not false"
    assert len(marks) == len(temporal.ticks) + 1


# --------------------------------------------------------------------------- #
# The builder, unit by unit                                                   #
# --------------------------------------------------------------------------- #


def _meeting_inputs(
    *,
    kind: TriggerKind,
    trigger_tick: int,
    victim: str,
    kill_tick: int,
    corpse_present: bool,
    actor: str = "p-4",
) -> tuple[WorldState, tuple[MeetingTriggeredEvent, ...], str]:
    engine_id = f"body-{victim}-{kill_tick}"
    bodies = (
        {
            engine_id: BodyState(
                id=engine_id,
                player_id=victim,
                room="MEDBAY",
                position=(0.0, 0.0),
                killed_by="p-9",
                discovered_by=None,
            )
        }
        if corpse_present
        else {}
    )
    state = replace(_NINE_PLAYERS, phase="MEETING", bodies=bodies)
    event = MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=trigger_tick,
        actor=actor,
        trigger=kind,
        body_id=engine_id if kind == "report" else None,
    )
    return state, (event,), engine_id


@given(
    kind=st.sampled_from(("report", "emergency")),
    trigger_tick=st.integers(min_value=0, max_value=5_000),
    age=st.integers(min_value=0, max_value=40),
    victim=st.integers(min_value=1, max_value=9).map(lambda n: f"p-{n}"),
    corpse_present=st.booleans(),
    temporal=st.booleans(),
)
@settings(deadline=None, max_examples=200)
def test_the_arm_changes_only_a_reported_corpses_handle(
    kind: TriggerKind,
    trigger_tick: int,
    age: int,
    victim: str,
    corpse_present: bool,
    temporal: bool,
) -> None:
    state, events, engine_id = _meeting_inputs(
        kind=kind,
        trigger_tick=trigger_tick,
        victim=victim,
        kill_tick=max(0, trigger_tick - age),
        corpse_present=corpse_present,
    )
    off = _build_meeting_trigger(
        state=state, events=events, temporal_observations=temporal
    )
    on = _build_meeting_trigger(
        state=state,
        events=events,
        temporal_observations=temporal,
        report_body_handle_version=1,
    )
    assert on[1:] == off[1:]
    assert replace(on[0], description=off[0].description) == off[0]
    assert LEGACY_BODY_HANDLE_PATTERN.search(on[0].description) is None
    if kind == "report" and not temporal:
        # OFF names the event's engine id whether or not the corpse is still in
        # the state; the arm names the public handle, or "a body" without one.
        assert off[0].description.count(engine_id) == 1
        assert on[0].description == (
            off[0].description.replace(engine_id, public_body_id(victim))
            if corpse_present
            else off[0].description.replace(f"body {engine_id} ", "a body ")
        )
    else:
        assert on[0].description == off[0].description


def test_an_emergency_description_is_the_same_under_the_arm() -> None:
    state, events, _engine_id = _meeting_inputs(
        kind="emergency",
        trigger_tick=31,
        victim="p-2",
        kill_tick=20,
        corpse_present=True,
    )
    off, _, _ = _build_meeting_trigger(state=state, events=events)
    on, body_id, kind = _build_meeting_trigger(
        state=state, events=events, report_body_handle_version=1
    )
    assert (
        on.description
        == off.description
        == f"p-4 {EMERGENCY_TRIGGER_PHRASE} at tick 31"
    )
    assert (body_id, kind) == (None, "emergency")


def _absent_corpse_problems(builder: Builder) -> list[str]:
    state, events, engine_id = _meeting_inputs(
        kind="report", trigger_tick=17, victim="p-6", kill_tick=11, corpse_present=False
    )
    trigger, body_id, _kind = builder(
        state=state, events=events, report_body_handle_version=1
    )
    problems = []
    if trigger.description != "p-4 reported a body at tick 17":
        problems.append("description")
    if engine_id in trigger.description:
        problems.append("engine id")
    if body_id != engine_id or trigger.body_victim_id is not None:
        problems.append("returned body")
    return problems


def _falls_back_to_the_engine_id(**kwargs: Any) -> Built:
    """Planted: a builder that names the engine id when the victim is unknown."""

    trigger, body_id, kind = _build_meeting_trigger(**kwargs)
    if kind == "report" and trigger.body_victim_id is None and body_id is not None:
        trigger = replace(
            trigger,
            description=(
                f"{trigger.triggered_by} reported body {body_id} "
                f"at tick {trigger.trigger_tick}"
            ),
        )
    return trigger, body_id, kind


def test_an_absent_corpse_reads_a_body_and_never_the_engine_id() -> None:
    assert _absent_corpse_problems(_build_meeting_trigger) == []
    assert _absent_corpse_problems(_falls_back_to_the_engine_id) == [
        "description",
        "engine id",
    ]


def test_the_arm_beside_temporal_observations_keeps_the_temporal_text() -> None:
    state, events, _engine_id = _meeting_inputs(
        kind="report", trigger_tick=12, victim="p-7", kill_tick=9, corpse_present=True
    )
    temporal = _build_meeting_trigger(
        state=state, events=events, temporal_observations=True
    )
    both = _build_meeting_trigger(
        state=state,
        events=events,
        temporal_observations=True,
        report_body_handle_version=1,
    )
    assert both == temporal
    assert both[0].description == "p-4 reported body body-p-7 at tick 12"


def test_the_builder_reads_the_trigger_among_the_ticks_other_events() -> None:
    # Planted surroundings: the tick's other events come before and after the
    # trigger event, and the builder still reads the trigger.
    state, (trigger_event,), engine_id = _meeting_inputs(
        kind="report", trigger_tick=12, victim="p-7", kill_tick=9, corpse_present=True
    )
    events = (
        MovedEvent(
            type="Moved", tick=12, actor="p-2", from_room="CAFETERIA", to_room="MEDBAY"
        ),
        trigger_event,
        ActionRejectedEvent(
            type="ActionRejected",
            tick=12,
            actor="p-5",
            action="Kill",
            reason="cooldown",
        ),
    )
    trigger, body_id, kind = _build_meeting_trigger(
        state=state, events=events, report_body_handle_version=1
    )
    assert (trigger.description, body_id, kind) == (
        "p-4 reported body body-p-7 at tick 12",
        engine_id,
        "report",
    )


def test_the_handle_follows_its_source(monkeypatch: pytest.MonkeyPatch) -> None:
    # Planted source: the arm names whatever the public-handle function returns.
    monkeypatch.setattr(
        game_module, "public_body_id", lambda victim: f"corpse-{victim}"
    )
    state, events, _engine_id = _meeting_inputs(
        kind="report", trigger_tick=12, victim="p-7", kill_tick=9, corpse_present=True
    )
    on, _, _ = _build_meeting_trigger(
        state=state, events=events, report_body_handle_version=1
    )
    assert on.description == "p-4 reported body corpse-p-7 at tick 12"


def test_an_emergency_description_follows_its_phrase(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Planted source: both values write the phrase the manager module states.
    monkeypatch.setattr(game_module, "EMERGENCY_TRIGGER_PHRASE", "rang the bell")
    state, events, _engine_id = _meeting_inputs(
        kind="emergency",
        trigger_tick=31,
        victim="p-2",
        kill_tick=20,
        corpse_present=True,
    )
    for version in (None, 1):
        trigger, _, _ = _build_meeting_trigger(
            state=state, events=events, report_body_handle_version=version
        )
        assert trigger.description == "p-4 rang the bell at tick 31"


@pytest.mark.parametrize("value", [2, 0, True, False, 1.0, "1"])
def test_the_builder_refuses_a_version_it_does_not_write(value: object) -> None:
    state, events, _engine_id = _meeting_inputs(
        kind="report", trigger_tick=12, victim="p-7", kill_tick=9, corpse_present=True
    )
    message = (
        f"report_body_handle_version={value!r} is not a body-handle version "
        "this builder writes"
    )
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        _build_meeting_trigger(
            state=state, events=events, report_body_handle_version=cast(Any, value)
        )


# --------------------------------------------------------------------------- #
# The field                                                                   #
# --------------------------------------------------------------------------- #


def test_the_field_round_trips_at_format_one() -> None:
    config = RecordedExperimentConfig.model_validate({"report_body_handle_version": 1})
    assert config == ARM_ON and config.format_version == 1
    dumped = config.model_dump(mode="json")
    assert dumped["report_body_handle_version"] == 1
    assert RecordedExperimentConfig.model_validate_json(config.model_dump_json()) == (
        config
    )
    assert not config.is_default


@pytest.mark.parametrize(
    "config",
    [
        RecordedExperimentConfig(),
        RESET,
        RecordedExperimentConfig(format_version=2),
        RecordedExperimentConfig(format_version=3, evidence_reasoning_version=2),
    ],
)
def test_the_default_serializes_without_the_key(
    config: RecordedExperimentConfig,
) -> None:
    assert config.report_body_handle_version is None
    assert "report_body_handle_version" not in config.model_dump(mode="json")
    assert "report_body_handle_version" not in json.loads(config.model_dump_json())


def test_the_arm_is_no_longer_pending() -> None:
    assert "report_body_handle_version" not in WAVE_ARMS_PENDING


@pytest.mark.parametrize("value", [True, 2])
def test_a_coerced_or_unknown_version_is_refused(value: object) -> None:
    with pytest.raises(ValidationError):
        RecordedExperimentConfig.model_validate({"report_body_handle_version": value})


def test_a_recorded_key_the_model_does_not_declare_leaves_the_row_unparseable(
    recorded: _Recordings,
) -> None:
    # Why retirement keeps the key: the config forbids unknown keys, so a tick
    # row carrying a key the model no longer declared would not parse. A
    # misspelled key stands in for a deleted field.
    row = json.loads(
        recorded["seed1-on"].path.read_text(encoding="utf-8").splitlines()[0]
    )
    assert row["kind"] == "tick"
    assert ReplayEntry.model_validate(row).experiment_config == ARM_ON
    config = row["experiment_config"]
    config["report_body_handle_vers"] = config.pop("report_body_handle_version")
    with pytest.raises(ValidationError, match="report_body_handle_vers"):
        ReplayEntry.model_validate(row)


# --------------------------------------------------------------------------- #
# Reconstruction threads the recorded value                                   #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("name", ["seed1-on", "seed0-on"])
def test_the_golden_re_renders_the_arm_on_recording_byte_equal(
    recorded: _Recordings, name: str
) -> None:
    played = recorded[name]
    walk = golden.walk_directory(played.directory)
    assert walk.meetings == len(played.meetings)
    assert len(walk.prompts) == len(played.prompts())
    assert all(prompt.reproduced for prompt in walk.prompts)
    assert walk.miscounted_meetings == ()


def _report_meeting_keys(played: _Played) -> tuple[str, ...]:
    return tuple(
        f"{played.path.name}:{opening.meeting.meeting_id}"
        for opening in played.report_openings()
    )


def test_the_golden_misses_the_opening_when_the_recorded_value_is_dropped(
    recorded: _Recordings, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(golden, "_build_meeting_trigger", _without_the_substitution)
    played = recorded["seed0-on"]
    walk = golden.walk_directory(played.directory)
    assert walk.miscounted_meetings == _report_meeting_keys(played)
    assert not all(prompt.reproduced for prompt in walk.prompts)


def _stamped_copy(source: _Played, target: Path, **settings: object) -> Path:
    """A copy of ``source`` whose tick rows and footer also record ``settings``."""

    target.mkdir(parents=True)
    for name in ("roster.json", "MANIFEST.md"):
        shutil.copyfile(source.directory / name, target / name)
    rows = [
        json.loads(line)
        for line in source.path.read_text(encoding="utf-8").splitlines()
    ]
    stamped = 0
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            row["experiment_config"] = {
                **row.get("experiment_config", {"format_version": 1}),
                **settings,
            }
            stamped += 1
    assert stamped == len(source.ticks) + 1
    (target / source.path.name).write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    return target


def test_the_golden_misses_the_opening_of_an_off_recording_stamped_on(
    recorded: _Recordings, tmp_path: Path
) -> None:
    off = recorded["seed0-off"]
    copy = _stamped_copy(
        off, tmp_path / "stamped" / "9p2i", report_body_handle_version=1
    )
    walk = golden.walk_directory(copy)
    assert walk.miscounted_meetings == _report_meeting_keys(off)
    assert not all(prompt.reproduced for prompt in walk.prompts)
    # The unstamped recording is the control.
    assert golden.walk_directory(off.directory).miscounted_meetings == ()


# --------------------------------------------------------------------------- #
# A plain shell loads it                                                      #
# --------------------------------------------------------------------------- #


def _bare_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("AILIBI_"):
            monkeypatch.delenv(name)
    assert not [name for name in os.environ if name.startswith("AILIBI_")]


def _walk(played: _Played, path: Path | None = None) -> list[ReplayWalkEvent]:
    game = played.game
    return list(
        walk_replay(
            path if path is not None else played.path,
            seed=game.seed,
            num_players=game.num_players,
            num_impostors=game.num_impostors,
            tasks_per_crewmate=game.tasks_per_crewmate,
            game_map=load_canonical_map(),
            config=replace(CENSUS_WALK_CONFIG, verify_meeting_pre_hashes=True),
        )
    )


def test_a_plain_shell_loads_the_arm_on_recording(
    recorded: _Recordings, monkeypatch: pytest.MonkeyPatch
) -> None:
    played = recorded["seed0-on"]
    _bare_shell(monkeypatch)
    replay = ReplayLoader(played.directory).load_replay(
        f"headless-seed-{played.game.seed}"
    )
    assert replay.metadata.outcome_verified
    events = _walk(played)
    assert sum(isinstance(e, TickAdvanced) for e in events) == len(played.ticks)
    assert sum(isinstance(e, MeetingApplied) for e in events) == len(played.meetings)


def test_a_footer_that_disagrees_with_the_tick_rows_is_refused(
    recorded: _Recordings, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    played = recorded["seed0-on"]
    rows = [
        json.loads(line)
        for line in played.path.read_text(encoding="utf-8").splitlines()
    ]
    (footer,) = [row for row in rows if row["kind"] == "game_over"]
    footer["experiment_config"] = {"format_version": 1}
    target = tmp_path / "footer" / "9p2i"
    target.mkdir(parents=True)
    shutil.copyfile(played.directory / "roster.json", target / "roster.json")
    copy = target / played.path.name
    copy.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    message = "terminal experiment configuration disagrees with tick rows"
    with pytest.raises(ValueError, match=message):
        recorded_experiment_config(read_all_entries(copy))
    _bare_shell(monkeypatch)
    with pytest.raises(ValueError, match=message):
        ReplayLoader(target).load_replay(f"headless-seed-{played.game.seed}")


# --------------------------------------------------------------------------- #
# Joint with the meeting reset                                                #
# --------------------------------------------------------------------------- #


def _regrouped_before(played: _Played) -> dict[str, bool]:
    """For each meeting, whether the meeting before it closed with a regroup."""

    meeting_room = _MAP.meeting.room
    regrouped: dict[str, bool] = {}
    previous = False
    for event in _walk(played):
        if isinstance(event, MeetingOpened):
            regrouped[event.entry.meeting_id] = previous
        if isinstance(event, MeetingApplied):
            living = [p for p in event.state.players.values() if p.alive]
            previous = (
                event.state.phase == "PLAY"
                and not event.state.bodies
                and all(p.room == meeting_room and not p.in_vent for p in living)
            )
    return regrouped


def test_after_a_regroup_a_report_names_the_public_handle_and_a_button_no_body(
    recorded: _Recordings,
) -> None:
    played = recorded["seed0-reset-on"]
    assert recorded_experiment_config(played.entries) == RESET_AND_ARM
    regrouped = _regrouped_before(played)
    openings = played.openings()
    after = [
        o
        for o in openings
        if o.trigger.kind == "report" and regrouped[o.meeting.meeting_id]
    ]
    buttons = [o for o in openings if o.trigger.kind == "emergency"]
    assert after and buttons
    for opening in after:
        names_public = opening.public_text in opening.prompt
        assert names_public, opening.meeting.meeting_id
    for opening in buttons:
        assert opening.trigger.description == (
            f"{opening.trigger.triggered_by} {EMERGENCY_TRIGGER_PHRASE} "
            f"at tick {opening.trigger.trigger_tick}"
        )
        carried = opening.trigger.description in opening.prompt
        assert carried, opening.meeting.meeting_id
        assert "body" not in opening.trigger.description
    assert _kill_tick_handles(played) == []


def test_the_reset_alone_leaves_the_kill_tick_handle(recorded: _Recordings) -> None:
    # Planted: the same game with the field None. The regroup clears the
    # corpses at each close, yet the next report still names its engine id.
    played = recorded["seed0-reset-off"]
    regrouped = _regrouped_before(played)
    after = [
        o
        for o in played.openings()
        if o.trigger.kind == "report" and regrouped[o.meeting.meeting_id]
    ]
    assert after
    for opening in after:
        engine_id = opening.engine_body_id
        assert engine_id is not None, opening.meeting.meeting_id
        names_engine_id = engine_id in opening.prompt
        names_public = opening.public_text in opening.prompt
        assert names_engine_id and not names_public, opening.meeting.meeting_id


# --------------------------------------------------------------------------- #
# End to end: the census's opening-handle conformance cell                    #
# --------------------------------------------------------------------------- #

_CELL: Final[str] = "report_openings_with_kill_tick_handle"


def _census_cell(directory: Path, capsys: pytest.CaptureFixture[str]) -> dict[str, Any]:
    assert census_command.main(["--set-dir", str(directory), "--json-stdout"]) == 0
    section = json.loads(capsys.readouterr().out)
    return cast(dict[str, Any], section["cells"][_CELL])


def test_the_census_counts_no_kill_tick_opening_on_the_arm_on_recording(
    recorded: _Recordings, capsys: pytest.CaptureFixture[str]
) -> None:
    on, off = recorded["seed0-on"], recorded["seed0-off"]
    reports = len(on.report_openings())
    assert reports == len(off.report_openings()) > 0
    on_cell = _census_cell(on.directory, capsys)
    assert (on_cell["numerator"], on_cell["denominator"]) == (0, reports)
    assert on_cell["guard"] == "report_body_handle_version = 1"
    off_cell = _census_cell(off.directory, capsys)
    assert (off_cell["numerator"], off_cell["denominator"]) == (reports, reports)


def test_one_opening_given_back_its_kill_tick_handle_breaks_the_census_guard(
    recorded: _Recordings, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    on = recorded["seed0-on"]
    target = tmp_path / "breach" / "9p2i"
    shutil.copytree(on.directory, target)
    first = on.report_openings()[0]
    assert first.engine_body_id is not None
    rows = [
        json.loads(line) for line in on.path.read_text(encoding="utf-8").splitlines()
    ]
    (row,) = [
        r
        for r in rows
        if r["kind"] == "meeting" and r["meeting_id"] == first.meeting.meeting_id
    ]
    call = row["llm_calls"][first.call_index]
    public = public_body_id(cast(str, first.trigger.body_victim_id))
    occurrences = call["prompt"].count(f"body {public} at tick")
    assert occurrences == 1
    call["prompt"] = call["prompt"].replace(
        f"body {public} at tick", f"body {first.engine_body_id} at tick"
    )
    (target / on.path.name).write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8"
    )
    assert census_command.main(["--set-dir", str(target), "--json-stdout"]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "conformance breach" in captured.err
    assert "report_body_handle_version = 1" in captured.err
    assert first.meeting.meeting_id.rsplit(":", 1)[-1] in captured.err
    with pytest.raises(GameplayCensusConformanceError):
        census_command.set_dir_json(target)


def test_the_recorded_rows_are_the_ones_the_census_read(recorded: _Recordings) -> None:
    # The footer and every tick row carry the arm, so the census's era reads it.
    on = recorded["seed0-on"]
    footers = [e for e in on.entries if isinstance(e, GameEndReplayEntry)]
    assert len(footers) == 1 and footers[0].experiment_config == ARM_ON
    assert all(row.experiment_config == ARM_ON for row in on.ticks)
