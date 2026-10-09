"""The game-shape profile's served view: mirror, staleness, route and pointers.

``GameProfileView`` mirrors ``eval.game_profile.GameProfile`` field for field,
plus the loader's ``stale``. The loader serves the committed file fresh, and
withholds every member when the file's MANIFEST key, seedset or source bytes
disagree with the set on disk. Every meeting index and kill tick the committed
file points at names a meeting or a kill the served replay shows, in the
``api.public_results._check_case`` idiom.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, get_args, get_origin

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import ReplayLoader, SetLoaderRegistry
from api.schemas import (
    GameProfileView,
    PreRevealHalfView,
    ProfileConstantsView,
    ReplayView,
    VIEW_MODEL_VERSION,
)
from eval import game_profile as gp
from tests._helpers.committed import SAMPLES_9P2I, census_inputs, repo_root

_PARENT = repo_root / "replays" / "samples"
_FILENAME = "results-game-profile.json"

#: The fields the view adds to the file: the contract stamp and the verdict.
_VIEW_ONLY = frozenset({"view_model_version", "stale"})


def _tree(model: type[BaseModel]) -> dict[str, Any]:
    """Each field's name mapped to the tree of the model it holds, if any."""

    def nested(annotation: Any) -> type[BaseModel] | None:
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return annotation
        for arg in get_args(annotation) if get_origin(annotation) is not None else ():
            found = nested(arg)
            if found is not None:
                return found
        return None

    tree: dict[str, Any] = {}
    for name, field in model.model_fields.items():
        inner = nested(field.annotation)
        tree[name] = _tree(inner) if inner is not None else None
    return tree


def mirror_differences(profile: type[BaseModel], view: type[BaseModel]) -> list[str]:
    """Each field path one model has and the other lacks."""

    def walk(
        left: Mapping[str, Any], right: Mapping[str, Any], prefix: str
    ) -> list[str]:
        found = [f"{prefix}{name}" for name in sorted(set(left) ^ set(right))]
        for name in sorted(set(left) & set(right)):
            if isinstance(left[name], dict) and isinstance(right[name], dict):
                found.extend(walk(left[name], right[name], f"{prefix}{name}."))
            elif (left[name] is None) != (right[name] is None):
                found.append(f"{prefix}{name}")
        return found

    view_tree = {
        name: sub for name, sub in _tree(view).items() if name not in _VIEW_ONLY
    }
    return walk(_tree(profile), view_tree, "")


def test_the_view_mirrors_the_profile_field_for_field() -> None:
    assert mirror_differences(gp.GameProfile, GameProfileView) == []
    assert _VIEW_ONLY <= set(GameProfileView.model_fields)


#: The words a key may not carry anywhere in the served view.
_BANNED_KEY_TOKENS = frozenset(
    {"score", "rank", "total", "points", "weight", "best", "top"}
)


def test_no_key_of_the_served_view_names_a_score() -> None:
    def walk(tree: Mapping[str, Any], prefix: str) -> list[str]:
        found: list[str] = []
        for name, sub in tree.items():
            if set(name.split("_")) & _BANNED_KEY_TOKENS:
                found.append(f"{prefix}{name}")
            if isinstance(sub, dict):
                found.extend(walk(sub, f"{prefix}{name}."))
        return found

    assert walk(_tree(GameProfileView), "") == []

    class Planted(GameProfileView):
        best_shelf_total: int

    assert walk(_tree(Planted), "") == ["best_shelf_total"]


def test_a_field_added_to_one_model_only_fails_the_mirror() -> None:
    class WiderConstants(ProfileConstantsView):
        sixth_shelf: int

    class PlantedView(GameProfileView):
        constants: WiderConstants

    assert mirror_differences(gp.GameProfile, PlantedView) == ["constants.sixth_shelf"]

    class NarrowerHalf(PreRevealHalfView):
        moments: tuple[str, ...]

    class PlantedHalf(GameProfileView):
        pre_reveal: NarrowerHalf

    assert mirror_differences(gp.GameProfile, PlantedHalf) == ["pre_reveal.moments"]


# ---------------------------------------------------------------------------
# The loader
# ---------------------------------------------------------------------------


def _committed() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(
        (SAMPLES_9P2I / _FILENAME).read_text(encoding="utf-8")
    )
    return payload


@pytest.fixture
def copied_set(tmp_path: Path) -> Iterator[Path]:
    """A copy of the shown set with its served profile, under a set parent."""

    target = tmp_path / "samples" / "9p2i"
    shutil.copytree(SAMPLES_9P2I, target)
    yield target


def _write(set_dir: Path, payload: Mapping[str, Any]) -> None:
    (set_dir / _FILENAME).write_text(json.dumps(payload), encoding="utf-8")


def _withheld(view: GameProfileView) -> bool:
    """Whether every member, game, entry and table is withheld."""

    pre, reveal = view.pre_reveal, view.reveal
    return (
        all(not shelf.members for shelf in pre.shelves)
        and all(not chip.members for chip in pre.chips)
        and not pre.games
        and all(not reading.entries for reading in pre.tripwires.readings)
        and pre.tripwires.alibi_flags is None
        and pre.tripwires.alibi_flags_evaluable is None
        and all(not shelf.members for shelf in reveal.shelves)
        and not reveal.decided_without_proof.right.members
        and not reveal.decided_without_proof.wrong.members
        and not reveal.games
        and reveal.class_tables is None
    )


def test_the_shown_set_serves_its_profile_fresh() -> None:
    view = SetLoaderRegistry(_PARENT).get("9p2i").game_profile()
    assert view.stale is False
    assert view.view_model_version == VIEW_MODEL_VERSION == "6"
    assert view.model_dump(exclude={"view_model_version", "stale"}, mode="json") == (
        json.loads(json.dumps(_committed()))
    )
    assert not _withheld(view)


def test_the_four_player_set_ships_no_profile() -> None:
    assert not (_PARENT / "4p1i" / _FILENAME).exists()
    with pytest.raises(
        FileNotFoundError, match=rf"^{re.escape(str(_PARENT / '4p1i' / _FILENAME))}$"
    ):
        SetLoaderRegistry(_PARENT).get("4p1i").game_profile()


@pytest.mark.parametrize(
    "source",
    ["manifest_key", "seedset", "source_fingerprint", "recording"],
)
def test_each_stale_source_withholds_every_member(
    copied_set: Path, source: str
) -> None:
    assert ReplayLoader(replay_dir=copied_set).game_profile().stale is False
    payload = _committed()
    if source == "manifest_key":
        payload["manifest_key"] = "deadbee"
        _write(copied_set, payload)
    elif source == "seedset":
        payload["seedset"] = "4p1i"
        _write(copied_set, payload)
    elif source == "source_fingerprint":
        payload["source_fingerprint"] = "sha256:" + "0" * 64
        _write(copied_set, payload)
    else:
        replay = copied_set / "replay-seed-0.jsonl"
        replay.write_bytes(replay.read_bytes() + b"\n")
    view = ReplayLoader(replay_dir=copied_set).game_profile()
    assert view.stale is True
    assert _withheld(view)
    assert view.catalogue and view.constants.slow_burn_ticks == gp.SLOW_BURN_TICKS
    assert [shelf.name for shelf in view.pre_reveal.shelves] == [
        shelf["name"] for shelf in _committed()["pre_reveal"]["shelves"]
    ]


def test_a_set_with_no_recording_reads_stale(tmp_path: Path) -> None:
    _write(tmp_path, _committed())
    view = ReplayLoader(replay_dir=tmp_path).game_profile()
    assert view.stale is True and _withheld(view)


def test_a_file_carrying_a_score_or_a_total_is_refused_at_load(
    copied_set: Path,
) -> None:
    for planted in ({**_committed(), "score": 50.0}, {**_committed(), "rank": 1}):
        _write(copied_set, planted)
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ReplayLoader(replay_dir=copied_set).game_profile()
    per_game = _committed()
    per_game["pre_reveal"]["games"][0]["total"] = 3
    _write(copied_set, per_game)
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ReplayLoader(replay_dir=copied_set).game_profile()


def test_a_malformed_file_fails_loud(copied_set: Path) -> None:
    """Each refusal names the file it refused, so a reader can find it."""

    path = re.escape(str(copied_set / _FILENAME))
    (copied_set / _FILENAME).write_text("[]", encoding="utf-8")
    with pytest.raises(
        ValueError,
        match=rf"^invalid profile file {path}: expected a JSON object, got list$",
    ):
        ReplayLoader(replay_dir=copied_set).game_profile()
    for computed in ("stale", "viewModelVersion", "view_model_version"):
        _write(copied_set, {**_committed(), computed: False})
        with pytest.raises(
            ValueError,
            match=rf"^invalid profile file {path}: '{computed}' is the loader's to set$",
        ):
            ReplayLoader(replay_dir=copied_set).game_profile()
    missing = _committed()
    del missing["catalogue"]
    _write(copied_set, missing)
    with pytest.raises(ValidationError, match="catalogue"):
        ReplayLoader(replay_dir=copied_set).game_profile()


# ---------------------------------------------------------------------------
# The route
# ---------------------------------------------------------------------------


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv(ENV_REPLAY_DIR, str(_PARENT))
    with TestClient(create_app()) as test_client:
        yield test_client


def test_the_route_serves_9p2i_and_404s_on_4p1i(client: TestClient) -> None:
    served = client.get("/eval/game-profile", params={"set": "9p2i"})
    assert served.status_code == 200
    body = served.json()
    assert body["viewModelVersion"] == "6"
    assert body["stale"] is False
    assert body["rubric_version"] == 2
    default = client.get("/eval/game-profile")
    assert default.json() == body
    missing = client.get("/eval/game-profile", params={"set": "4p1i"})
    assert missing.status_code == 404
    assert "results-game-profile.json" in missing.json()["detail"]


def test_the_version_one_route_is_gone(client: TestClient) -> None:
    for name in ("9p2i", "4p1i"):
        assert client.get("/eval/rubric", params={"set": name}).status_code == 404


# ---------------------------------------------------------------------------
# 14. Every pointer is true of the served replay
# ---------------------------------------------------------------------------


def pointer_failures(
    profile: Mapping[str, Any],
    meeting_ids: Mapping[int, tuple[str, ...]],
    replays: Mapping[int, ReplayView],
) -> list[str]:
    """Each meeting index or kill tick the profile names that its replay does not show."""

    failures: list[str] = []

    def check(
        seed: int, where: str, meetings: list[int], kill_ticks: list[int]
    ) -> None:
        replay = replays[seed]
        for index in meetings:
            if not (
                0 <= index < len(replay.meetings)
                and replay.meetings[index].meeting_id == meeting_ids[seed][index]
            ):
                failures.append(f"seed {seed}, {where}: meeting index {index}")
        shown = {
            tick.tick
            for tick in replay.ticks
            if any(event.type == "kill" for event in tick.events)
        }
        for tick in kill_ticks:
            if tick not in shown:
                failures.append(f"seed {seed}, {where}: kill tick {tick}")

    pair = profile["reveal"]["decided_without_proof"]
    shelves = [
        *profile["pre_reveal"]["shelves"],
        *profile["reveal"]["shelves"],
        pair["right"],
        pair["wrong"],
    ]
    for shelf in shelves:
        for member in shelf["members"]:
            check(
                member["seed"],
                f"shelf {shelf['name']}",
                member["meetings"],
                member["kill_ticks"],
            )
    for chip in profile["pre_reveal"]["chips"]:
        for member in chip["members"]:
            check(member["seed"], f"chip {chip['name']}", member["meetings"], [])
    for reading in profile["pre_reveal"]["tripwires"]["readings"]:
        for entry in reading["entries"]:
            check(entry["seed"], f"tripwire {reading['name']}", [entry["meeting"]], [])
    for game in profile["pre_reveal"]["games"]:
        check(
            game["seed"],
            "facets",
            [meeting["index"] for meeting in game["meetings"]]
            + [report["meeting"] for report in game["reports"]]
            + [label["meeting"] for label in game["tripped"]],
            [kill["tick"] for kill in game["kills"]],
        )
    for game in profile["reveal"]["games"]:
        check(
            game["seed"],
            "reveal facets",
            [item["meeting"] for item in game["ejections"]],
            [],
        )
    return failures


@pytest.fixture(scope="module")
def served_replays() -> tuple[Mapping[int, tuple[str, ...]], Mapping[int, ReplayView]]:
    loader = SetLoaderRegistry(_PARENT).get("9p2i")
    inputs = census_inputs(SAMPLES_9P2I)
    meeting_ids = {
        game.seed: tuple(meeting.meeting_id for meeting in game.meetings)
        for game in inputs.games
    }
    replays = {
        seed: loader.load_replay(f"headless-seed-{seed}", include_llm_bodies=False)
        for seed in meeting_ids
    }
    return meeting_ids, replays


def test_every_pointer_names_a_meeting_or_a_kill_the_replay_shows(
    served_replays: tuple[Mapping[int, tuple[str, ...]], Mapping[int, ReplayView]],
) -> None:
    meeting_ids, replays = served_replays
    assert pointer_failures(_committed(), meeting_ids, replays) == []


def test_a_member_pointing_past_the_last_meeting_fails_naming_seed_and_shelf(
    served_replays: tuple[Mapping[int, tuple[str, ...]], Mapping[int, ReplayView]],
) -> None:
    meeting_ids, replays = served_replays
    planted = _committed()
    shelf = planted["pre_reveal"]["shelves"][0]
    member = shelf["members"][0]
    member["meetings"] = [len(meeting_ids[member["seed"]])]
    assert pointer_failures(planted, meeting_ids, replays) == [
        f"seed {member['seed']}, shelf {shelf['name']}: meeting index "
        f"{len(meeting_ids[member['seed']])}"
    ]
    planted = _committed()
    double = next(
        s for s in planted["pre_reveal"]["shelves"] if s["name"] == gp.DOUBLE_KILL
    )
    double["members"][0]["kill_ticks"] = [double["members"][0]["kill_ticks"][0] + 1]
    assert pointer_failures(planted, meeting_ids, replays) == [
        f"seed {double['members'][0]['seed']}, shelf {gp.DOUBLE_KILL}: kill tick "
        f"{double['members'][0]['kill_ticks'][0]}"
    ]


def test_an_eyewitness_chip_past_the_last_meeting_fails_naming_seed_and_chip(
    served_replays: tuple[Mapping[int, tuple[str, ...]], Mapping[int, ReplayView]],
) -> None:
    meeting_ids, replays = served_replays
    planted = _committed()
    chip = planted["pre_reveal"]["chips"][0]
    member = next(item for item in chip["members"] if item["seed"] == 19)
    member["meetings"] = [len(meeting_ids[19])]
    assert pointer_failures(planted, meeting_ids, replays) == [
        f"seed 19, chip {gp.EYEWITNESS_CHIP}: meeting index {len(meeting_ids[19])}"
    ]


def _copy_endings(source: str) -> tuple[str, ...]:
    """The ending keys the viewer's copy gives words to."""

    block = source.split("endings: Object.freeze({", 1)[1].split("})", 1)[0]
    return tuple(
        line.strip().split(":", 1)[0]
        for line in block.splitlines()
        if line.strip() and not line.strip().startswith("//")
    )


def test_the_viewer_has_words_for_every_recorded_ending() -> None:
    from eval.gameplay_census import game_endings

    source = (repo_root / "frontend" / "src" / "lib" / "copy.ts").read_text(
        encoding="utf-8"
    )
    assert sorted(_copy_endings(source)) == sorted(game_endings())
    planted = source.replace('        IMPOSTOR_SABOTAGE: "a sabotage ran out",\n', "")
    assert sorted(_copy_endings(planted)) != sorted(game_endings())
