"""Optional public facts cannot outlive the recordings they describe."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest

import build_demo_bundle as bdb
import publish_game_profile
from api.replay_loader import ReplayLoader
from api.schemas import AccusationClaimView, GameProfileView, ReplayView
from orchestrator.recording_fingerprint import recording_fingerprint


_SHOWN_SET = Path(__file__).resolve().parents[2] / "replays/samples/9p2i"
_PROFILE = "results-game-profile.json"


@pytest.fixture
def profiled_set(tmp_path: Path) -> Path:
    """A copy of the shown set, its served profile stamped for these bytes."""

    directory = tmp_path / "9p2i"
    shutil.copytree(_SHOWN_SET, directory)
    return directory


def _baked_members(view: GameProfileView, seeds: frozenset[int]) -> list[int]:
    """Every seed the bake ships a member, game or entry for."""

    baked = json.loads(bdb._trimmed_profile(view, seeds))
    pre, reveal = baked["pre_reveal"], baked["reveal"]
    pair = reveal["decided_without_proof"]
    return sorted(
        item["seed"]
        for items in (
            *(shelf["members"] for shelf in pre["shelves"]),
            *(chip["members"] for chip in pre["chips"]),
            pre["games"],
            *(reading["entries"] for reading in pre["tripwires"]["readings"]),
            *(shelf["members"] for shelf in reveal["shelves"]),
            pair["right"]["members"],
            pair["wrong"]["members"],
            reveal["games"],
        )
        for item in items
    )


def test_fresh_source_is_published_and_baked(profiled_set: Path) -> None:
    view = ReplayLoader(profiled_set).game_profile()
    assert not view.stale
    assert len(view.pre_reveal.games) == 50
    assert 19 in _baked_members(view, frozenset({19}))
    assert set(_baked_members(view, frozenset({19}))) == {19}


@pytest.mark.parametrize("source", ["replay", "roster", "manifest", "added_replay"])
def test_changed_inputs_withhold_members_and_the_stamp_follows_the_bytes(
    profiled_set: Path, source: str
) -> None:
    artifact = profiled_set / _PROFILE
    if source == "added_replay":
        (profiled_set / "replay-seed-99.jsonl").write_bytes(
            (profiled_set / "replay-seed-1.jsonl").read_bytes()
        )
    else:
        name = {
            "replay": "replay-seed-1.jsonl",
            "roster": "roster.json",
            "manifest": "MANIFEST.md",
        }[source]
        path = profiled_set / name
        path.write_bytes(path.read_bytes() + b"\n")
    before = artifact.read_bytes()
    view = ReplayLoader(profiled_set).game_profile()
    assert view.stale
    assert view.pre_reveal.games == ()
    assert _baked_members(view, frozenset({19})) == []
    assert artifact.read_bytes() == before
    root = Path(__file__).resolve().parents[2]
    stamp = publish_game_profile.read_stamp(profiled_set, root)
    assert stamp.source_fingerprint != json.loads(before)["source_fingerprint"]


def test_a_missing_stamp_fails_loud(profiled_set: Path) -> None:
    artifact = profiled_set / _PROFILE
    raw = json.loads(artifact.read_text())
    del raw["source_fingerprint"]
    artifact.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="source_fingerprint"):
        ReplayLoader(profiled_set).game_profile()


def test_audits_and_derived_files_do_not_change_source_identity(
    profiled_set: Path,
) -> None:
    stamped = json.loads((profiled_set / _PROFILE).read_text())["source_fingerprint"]
    for name in ("replay-seed-1.audit.jsonl", "tournament-eval-report.json"):
        (profiled_set / name).write_text("derived data\n")
    assert recording_fingerprint(profiled_set) == stamped
    assert not ReplayLoader(profiled_set).game_profile().stale


def test_bundle_bakes_no_member_of_a_stale_profile(profiled_set: Path) -> None:
    view = ReplayLoader(profiled_set).game_profile()
    assert view.pre_reveal.games
    stale = view.model_copy(update={"stale": True})
    assert _baked_members(stale, frozenset({19})) == []


def _asset_mismatches(directory: Path) -> list[str]:
    provenance = json.loads((directory / "provenance.json").read_text())
    return [
        name
        for name, sha in provenance["assets_sha256"].items()
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != sha
    ]


def _recording_mismatch(root: Path, provenance: dict[str, Any]) -> bool:
    """Whether the captured recording is not the bytes this checkout serves."""

    recording = provenance["recording"]
    served = root / recording["path"]
    return (
        not served.is_file()
        or hashlib.sha256(served.read_bytes()).hexdigest() != recording["sha256"]
    )


def test_media_hashes_and_labels_are_current(tmp_path: Path) -> None:
    # The captures show the game the guided tour opens on in the shown 9-player
    # set, 9p2i seed 19, since the promotion of 2026-10-02 (they were a
    # historical seed-2 capture from the baseline-7 record before it), re-shot
    # on round 3's bytes at its promotion of 2026-10-09: the captured recording
    # is the replay this checkout serves, byte for byte, and the README caption
    # names that game, its set and its record.
    root = Path(__file__).resolve().parents[2]
    media = root / "docs/media"
    assert not _asset_mismatches(media)
    provenance = json.loads((media / "provenance.json").read_text())
    assert provenance["status"] == "current"
    assert not _recording_mismatch(root, provenance)
    recording = provenance["recording"]
    assert (recording["game_id"], recording["seed"], recording["recorded_on"]) == (
        "headless-seed-19",
        19,
        "2026-10-09",  # was 2026-10-01, round 2's recording
    )
    readme = (root / "README.md").read_text()
    assert (
        "9p2i seed 19, the game the demo's guided tour opens on, from the "
        "2026-10-09 record" in readme
    )
    assert "earlier recording" not in readme
    # A capture of a recording the checkout no longer serves must fail.
    moved = {**provenance, "recording": {**recording, "sha256": "0" * 64}}
    assert _recording_mismatch(root, moved)
    # A changed image with an unchanged claim must fail the digest check.
    (tmp_path / "provenance.json").write_bytes((media / "provenance.json").read_bytes())
    names = list(provenance["assets_sha256"])
    for name in names:
        (tmp_path / name).write_bytes((media / name).read_bytes())
    changed = tmp_path / names[0]
    changed.write_bytes(changed.read_bytes() + b"changed")
    assert _asset_mismatches(tmp_path) == [names[0]]


#: The two pages that describe the pictured game to a first reader.
_FRONT_DOOR_PAGES = ("README.md", "docs/media/README.md")

#: The picker's internal words for the featured list and its first entry; a
#: first reader has no glossary entry for either.
_PICKER_WORDS = re.compile(r"\b(?:strip|head)\b", re.IGNORECASE)

#: The README caption as `59bbd1be` published it: the jargon and the claim
#: that both impostors stood on the map, when one was inside a vent.
_CAPTION_AT_59BBD1BE = (
    "*9p2i seed 19, the featured strip's head, from the 2026-10-01 record (9p2i): "
    "at tick 9 two players lie dead and both impostors are on the map, while p-5 "
    "can see only p-4, whom p-5 accuses at the meeting that follows."
)


def _front_door_jargon(root: Path) -> list[str]:
    """The front-door pages that name the picked game with the picker's words."""

    return [
        page
        for page in _FRONT_DOOR_PAGES
        if _PICKER_WORDS.search((root / page).read_text())
    ]


def _readme_caption(readme: str) -> str:
    """The italic caption under the README's picture."""

    lines = [line for line in readme.splitlines() if line.startswith("*9p2i seed ")]
    assert len(lines) == 1, lines
    return lines[0]


def test_the_front_door_names_the_pictured_game_in_plain_words(
    tmp_path: Path,
) -> None:
    # The pictured game is the one the guided tour opens on
    # (tests/api/test_sets.py pins it as the featured list's first entry), and
    # the caption keeps one impostor inside a vent, which
    # test_the_captions_scene_is_the_recorded_one holds to the served bytes.
    root = Path(__file__).resolve().parents[2]
    assert _front_door_jargon(root) == []
    readme = (root / "README.md").read_text()
    caption = _readme_caption(readme)
    assert "the game the demo's guided tour opens on" in caption
    assert "the other is inside a vent" in caption
    assert "both impostors are on the map" not in caption
    assert (
        "The picture above is from the 9-player game the guided tour opens on."
        in readme
    )
    assert (
        "the game the demo's guided tour opens on"
        in (root / "docs/media/README.md").read_text()
    )

    # Planted: the `59bbd1be` caption, put back into a scratch README.
    for page in _FRONT_DOOR_PAGES:
        copied = tmp_path / page
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes((root / page).read_bytes())
    assert _front_door_jargon(tmp_path) == []
    planted = tmp_path / "README.md"
    planted.write_text(readme.replace(caption, _CAPTION_AT_59BBD1BE))
    assert _front_door_jargon(tmp_path) == ["README.md"]
    assert "inside a vent" not in _readme_caption(planted.read_text())


#: The pictured game; `test_media_hashes_and_labels_are_current` holds it to the
#: captured recording and to the caption's seed.
_HERO_GAME = "headless-seed-19"

#: The caption's scene clause. Each claim in it is a named group, read back out
#: of the caption and held to the served replay at the tick the caption names.
_CAPTION_SCENE = re.compile(
    r"at tick (?P<tick>\d+) (?P<dead>[a-z]+) players lie dead, one impostor "
    r"stands in (?P<room>[A-Za-z ]+?) and the other is inside a vent, while "
    r"(?P<subject>p-\d+) can see only (?P<seen>p-\d+), whom "
    r"(?P<accuser>p-\d+) accuses at the meeting that follows\."
)

#: The number words a caption counts in, each at its own value.
_COUNT_WORDS = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
)

#: The `tick` of the capture spec's `HERO`: the tick both halves are shot at.
_PICTURE_TICK = re.compile(r"const HERO = \{[^}]*?\n  tick: (\d+),")


def _picture_tick(spec: str) -> int:
    """The tick the capture spec shoots the hero picture at."""

    ticks = _PICTURE_TICK.findall(spec)
    if len(ticks) != 1:
        raise ValueError(f"expected one HERO tick in the spec, found {len(ticks)}")
    return int(ticks[0])


def _caption_scene_problems(
    caption: str, replay: ReplayView, picture_tick: int
) -> list[str]:
    """Why the caption's scene is not what the served replay records.

    Every claim is read from the caption: the tick, which must be the one the
    picture shows; how many players lie dead; the room, by the map's own name,
    the impostor outside the vents stands in; the one player the fog subject can
    see; and the accuser's accusation of that player at the first meeting after
    the tick.
    """

    scene = _CAPTION_SCENE.search(caption)
    if scene is None:
        return ["the caption names no scene"]
    tick = int(scene["tick"])
    problems = []
    if tick != picture_tick:
        problems.append(f"names tick {tick}, the picture shows tick {picture_tick}")
    frames = [frame for frame in replay.ticks if frame.tick == tick]
    if len(frames) != 1:
        return [*problems, f"the replay has no tick {tick}"]
    frame = frames[0]

    dead = scene["dead"]
    if dead not in _COUNT_WORDS or _COUNT_WORDS.index(dead) != len(frame.bodies):
        problems.append(
            f"says {dead} players lie dead, the replay has {len(frame.bodies)}"
        )

    roles = {player.agent_id: player.role for player in replay.players}
    impostors = [
        state
        for state in frame.agent_states
        if roles[state.agent_id] == "IMPOSTOR" and state.is_alive
    ]
    venting = sum(state.is_venting for state in impostors)
    if venting != 1:
        problems.append(f"says one impostor is inside a vent, the replay has {venting}")
    room_ids = {room.name: room.id for room in replay.map.rooms}
    standing = [state.room_id for state in impostors if not state.is_venting]
    if scene["room"] not in room_ids:
        problems.append(f"names no room called {scene['room']}")
    elif standing != [room_ids[scene["room"]]]:
        problems.append(
            f"says one impostor stands in {scene['room']}, the replay has {standing}"
        )

    subject = {state.agent_id: state for state in frame.agent_states}.get(
        scene["subject"]
    )
    seen = (
        None
        if subject is None or subject.visibility is None
        else [player.id for player in subject.visibility.visible_players]
    )
    if seen != [scene["seen"]]:
        problems.append(
            f"says {scene['subject']} can see only {scene['seen']}, "
            f"the replay has {seen}"
        )

    following = [meeting for meeting in replay.meetings if meeting.tick > tick]
    accused = (
        []
        if not following
        else [
            claim.against
            for turn in min(following, key=lambda meeting: meeting.tick).turns
            if turn.speaker == scene["accuser"]
            for claim in turn.claims
            if isinstance(claim, AccusationClaimView)
        ]
    )
    if scene["seen"] not in accused:
        problems.append(
            f"says {scene['accuser']} accuses {scene['seen']} at the meeting that "
            f"follows, the replay has {accused}"
        )
    return problems


def _readme_scene_problems(root: Path, replay: ReplayView) -> list[str]:
    """The scene problems of the caption in ``root``'s README, at the tick
    ``root``'s capture spec shoots the picture at."""

    caption = _readme_caption((root / "README.md").read_text())
    return _caption_scene_problems(
        caption, replay, _picture_tick((root / _MEDIA_SPEC).read_text())
    )


def _scratch_front_door(
    root: Path, scratch: Path, *, caption_edit: tuple[str, str] | None = None
) -> Path:
    """A scratch copy of the README and the capture spec, with one caption
    phrase replaced when ``caption_edit`` names one (old, new)."""

    readme = (root / "README.md").read_text()
    if caption_edit is not None:
        caption = _readme_caption(readme)
        old, new = caption_edit
        assert caption.count(old) == 1, old
        readme = readme.replace(caption, caption.replace(old, new))
    (scratch / "README.md").write_text(readme)
    spec = scratch / _MEDIA_SPEC
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_bytes((root / _MEDIA_SPEC).read_bytes())
    return scratch


@pytest.fixture(scope="module")
def hero_replay() -> ReplayView:
    root = Path(__file__).resolve().parents[2]
    return ReplayLoader(root / "replays/samples/9p2i").load_replay(_HERO_GAME)


def _with_frame(replay: ReplayView, tick: int, **update: Any) -> ReplayView:
    """The replay with the frame at ``tick`` changed by ``update``."""

    ticks = tuple(
        frame.model_copy(update=update) if frame.tick == tick else frame
        for frame in replay.ticks
    )
    return replay.model_copy(update={"ticks": ticks})


def test_the_captions_scene_is_the_recorded_one(
    tmp_path: Path, hero_replay: ReplayView
) -> None:
    # The README caption names a tick, how many players lie dead there, the room
    # one impostor stands in while the other is inside a vent, the one player
    # the fog subject can see and its accusation at the next meeting. The capture
    # harness runs only under its capture switch, so every one of those words is
    # read out of the caption here and held, in every run, to the replay the
    # demo serves and to the tick the capture spec shoots.
    root = Path(__file__).resolve().parents[2]
    assert _readme_scene_problems(root, hero_replay) == []
    caption = _readme_caption((root / "README.md").read_text())
    tick = _picture_tick((root / _MEDIA_SPEC).read_text())

    # Planted: a scratch spec shooting another tick; the read follows the spec.
    scratch = _scratch_front_door(root, tmp_path)
    spec = scratch / _MEDIA_SPEC
    spec.write_text(
        spec.read_text().replace(f"\n  tick: {tick},", f"\n  tick: {tick + 1},")
    )
    assert _readme_scene_problems(scratch, hero_replay) == [
        f"names tick {tick}, the picture shows tick {tick + 1}"
    ]

    # Planted: the replay changed under the caption at the pictured tick.
    frame = next(frame for frame in hero_replay.ticks if frame.tick == tick)
    standing = _with_frame(
        hero_replay,
        tick,
        agent_states=tuple(
            state.model_copy(update={"is_venting": False})
            for state in frame.agent_states
        ),
    )
    assert _caption_scene_problems(caption, standing, tick) == [
        "says one impostor is inside a vent, the replay has 0",
        "says one impostor stands in MedBay, the replay has ['STORAGE', 'MEDBAY']",
    ]
    impostor_ids = {
        player.agent_id for player in hero_replay.players if player.role == "IMPOSTOR"
    }
    both_venting = _with_frame(
        hero_replay,
        tick,
        agent_states=tuple(
            state.model_copy(update={"is_venting": True})
            if state.agent_id in impostor_ids
            else state
            for state in frame.agent_states
        ),
    )
    assert _caption_scene_problems(caption, both_venting, tick) == [
        "says one impostor is inside a vent, the replay has 2",
        "says one impostor stands in MedBay, the replay has []",
    ]
    venter_dead = _with_frame(
        hero_replay,
        tick,
        agent_states=tuple(
            state.model_copy(update={"is_alive": False}) if state.is_venting else state
            for state in frame.agent_states
        ),
    )
    assert _caption_scene_problems(caption, venter_dead, tick) == [
        "says one impostor is inside a vent, the replay has 0"
    ]
    one_body = _with_frame(hero_replay, tick, bodies=frame.bodies[:1])
    assert _caption_scene_problems(caption, one_body, tick) == [
        "says two players lie dead, the replay has 1"
    ]
    # The meeting that follows is the earliest after the tick, in any listing order.
    reversed_meetings = hero_replay.model_copy(
        update={"meetings": hero_replay.meetings[::-1]}
    )
    assert _caption_scene_problems(caption, reversed_meetings, tick) == []

    # Planted: the map's own name for the room changes; the read follows it.
    renamed = hero_replay.model_copy(
        update={
            "map": hero_replay.map.model_copy(
                update={
                    "rooms": tuple(
                        room.model_copy(update={"name": "Sickbay"})
                        if room.id == "MEDBAY"
                        else room
                        for room in hero_replay.map.rooms
                    )
                }
            )
        }
    )
    assert _caption_scene_problems(caption, renamed, tick) == [
        "names no room called MedBay"
    ]
    sickbay = caption.replace("stands in MedBay", "stands in Sickbay")
    assert _caption_scene_problems(sickbay, renamed, tick) == []


@pytest.mark.parametrize(
    ("old", "new", "problems"),
    [
        pytest.param(
            "stands in MedBay",
            "stands in Admin",
            ["says one impostor stands in Admin, the replay has ['MEDBAY']"],
            id="another-room",
        ),
        pytest.param(
            "stands in MedBay",
            "stands in Sickbay",
            ["names no room called Sickbay"],
            id="no-such-room",
        ),
        pytest.param(
            "two players lie dead",
            "three players lie dead",
            ["says three players lie dead, the replay has 2"],
            id="another-count",
        ),
        pytest.param(
            "at tick 9 ",
            "at tick 12 ",
            [
                "names tick 12, the picture shows tick 9",
                "says one impostor stands in MedBay, the replay has ['ENGINEERING']",
                "says p-5 accuses p-4 at the meeting that follows, the replay has []",
            ],
            id="another-tick",
        ),
        pytest.param(
            "can see only p-4",
            "can see only p-3",
            [
                "says p-5 can see only p-3, the replay has ['p-4']",
                "says p-5 accuses p-3 at the meeting that follows, the replay has "
                "['p-4']",
            ],
            id="another-sighting",
        ),
        pytest.param(
            "while p-5 can see",
            "while p-3 can see",
            ["says p-3 can see only p-4, the replay has []"],
            id="another-subject",
        ),
        pytest.param(
            "whom p-5 accuses",
            "whom p-6 accuses",
            [
                "says p-6 accuses p-4 at the meeting that follows, the replay has "
                "['p-1']"
            ],
            id="another-accuser",
        ),
    ],
)
def test_a_caption_naming_another_scene_fails_by_name(
    tmp_path: Path,
    hero_replay: ReplayView,
    old: str,
    new: str,
    problems: list[str],
) -> None:
    # Each planted caption is the README's own with one scene word changed, in a
    # scratch README read back the way the real one is.
    root = Path(__file__).resolve().parents[2]
    scratch = _scratch_front_door(root, tmp_path, caption_edit=(old, new))
    assert _readme_scene_problems(scratch, hero_replay) == problems


@pytest.mark.parametrize(
    ("word", "dead"),
    [
        ("no", 0),
        ("one", 1),
        ("two", 2),
        ("three", 3),
        ("four", 4),
        ("five", 5),
        ("six", 6),
        ("seven", 7),
        ("eight", 8),
        ("nine", 9),
    ],
)
def test_the_caption_counts_its_dead_in_words(
    hero_replay: ReplayView, word: str, dead: int
) -> None:
    # A caption that counts the dead in a word holds exactly when the pictured
    # frame carries that many bodies, and fails by name on one more.
    root = Path(__file__).resolve().parents[2]
    caption = _readme_caption((root / "README.md").read_text())
    tick = _picture_tick((root / _MEDIA_SPEC).read_text())
    frame = next(frame for frame in hero_replay.ticks if frame.tick == tick)
    counted = caption.replace("two players lie dead", f"{word} players lie dead")
    exact = _with_frame(hero_replay, tick, bodies=frame.bodies[:1] * dead)
    assert _caption_scene_problems(counted, exact, tick) == []
    more = _with_frame(hero_replay, tick, bodies=frame.bodies[:1] * (dead + 1))
    assert _caption_scene_problems(counted, more, tick) == [
        f"says {word} players lie dead, the replay has {dead + 1}"
    ]


def test_the_59bbd1be_caption_names_no_scene(hero_replay: ReplayView) -> None:
    # Planted: the caption `59bbd1be` published, both impostors on the map.
    assert _caption_scene_problems(_CAPTION_AT_59BBD1BE, hero_replay, 9) == [
        "the caption names no scene"
    ]


_MEDIA_SPEC = "frontend/e2e/media.spec.ts"

#: The sheet's caption, as the spec builds it: one or more template literals
#: joined by `+`, after `caption:`.
_CAPTION_TEMPLATE = re.compile(r"\bcaption:\s*((?:`[^`]*`\s*\+?\s*)+),")

#: The hero sheet's caption and comment as `59bbd1be` wrote them: the right half
#: is the fog view at tick 9, not everything p-5 knew when it voted at tick 12.
_SPEC_AT_59BBD1BE = (
    "    // ── right: everything the fog subject was allowed to know ────────────────\n"
    "        caption:\n"
    "          `Left: what happened. Right: everything ${HERO.fogSubject} was allowed"
    " to know ` +\n"
    "          `when it voted — and the accusation it wrote at the meeting that"
    " followed.`,\n"
)


def _hero_caption_problems(spec: str) -> list[str]:
    """Why the hero sheet's caption claims more than the picture shows."""

    templates = _CAPTION_TEMPLATE.findall(spec)
    if len(templates) != 1:
        return [f"expected one caption template, found {len(templates)}"]
    caption = "".join(re.findall(r"`([^`]*)`", templates[0]))
    problems = [
        f"says {phrase!r}"
        for phrase in ("when it voted", "allowed to know")
        if phrase in spec
    ]
    problems += [
        f"lacks {placeholder}"
        for placeholder in ("${String(HERO.tick)}", "${String(HERO.meetingTick)}")
        if placeholder not in caption
    ]
    return problems


def test_the_hero_caption_claims_only_what_the_picture_shows() -> None:
    # Both halves are tick 9 (the capture asserts both deep links carry it); the
    # card below is from the meeting at tick 12. So the caption names both ticks
    # and never calls the fog half what p-5 knew when it voted.
    root = Path(__file__).resolve().parents[2]
    spec = (root / _MEDIA_SPEC).read_text()
    assert _hero_caption_problems(spec) == []
    # The whole template, so no clause of it can drift without this case seeing.
    caption = "".join(re.findall(r"`([^`]*)`", _CAPTION_TEMPLATE.findall(spec)[0]))
    assert caption == (
        "Left: what happened at tick ${String(HERO.tick)}. Right: what "
        "${HERO.fogSubject} could see at the same tick. Below: the accusation "
        "${HERO.fogSubject} wrote at the meeting that followed, at tick "
        "${String(HERO.meetingTick)}."
    )
    # Planted: the `59bbd1be` caption and comment fail by name.
    assert _hero_caption_problems(_SPEC_AT_59BBD1BE) == [
        "says 'when it voted'",
        "says 'allowed to know'",
        "lacks ${String(HERO.tick)}",
        "lacks ${String(HERO.meetingTick)}",
    ]


def _media_placement_mismatches(root: Path) -> list[str]:
    """Compare the media inventory's placement claims to actual Markdown targets."""

    media = root / "docs/media"
    rows = re.findall(
        r"^\| `([^`]+)` \| [^|\n]+ \| ([^|\n]+) \|$",
        (media / "README.md").read_text(),
        re.MULTILINE,
    )
    assets = {
        path.name
        for path in media.iterdir()
        if path.suffix in {".png", ".gif", ".webm", ".svg"}
    }
    problems: list[str] = []
    if len(rows) != len(assets) or {name for name, _ in rows} != assets:
        problems.append("media placement table does not match the visual inventory")
    documents = [root / "README.md", root / "docs/architecture.md"]
    targets = {
        document.resolve(): {
            (document.parent / target).resolve()
            for target in re.findall(r"\]\(([^)\s]+)\)", document.read_text())
        }
        for document in documents
    }
    for name, placement in rows:
        declared = {
            (media / target).resolve()
            for target in re.findall(r"\]\(([^)]+)\)", placement)
        }
        actual = {
            document
            for document, links in targets.items()
            if (media / name).resolve() in links
        }
        if declared != actual or (not declared and placement != "Archive only"):
            problems.append(name)
    return problems


def test_media_placement_claims_follow_actual_frontdoor_links(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    assert _media_placement_mismatches(root) == []
    for relative in ("README.md", "docs/architecture.md", "docs/media/README.md"):
        copied = tmp_path / relative
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_bytes((root / relative).read_bytes())
    for source in (root / "docs/media").iterdir():
        if source.suffix in {".png", ".gif", ".webm", ".svg"}:
            (tmp_path / "docs/media" / source.name).touch()
    assert _media_placement_mismatches(tmp_path) == []

    readme = tmp_path / "README.md"
    original = readme.read_text()
    readme.write_text(
        original.replace(
            "docs/media/spectator-two-truths.png", "docs/media/missing.png"
        )
    )
    assert _media_placement_mismatches(tmp_path) == ["spectator-two-truths.png"]
    readme.write_text(original)

    inventory = tmp_path / "docs/media/README.md"
    inventory.write_text(
        inventory.read_text().replace(
            "| Archive only |", "| [README image](../../README.md) |", 1
        )
    )
    assert _media_placement_mismatches(tmp_path) == ["spectator-meeting.png"]
