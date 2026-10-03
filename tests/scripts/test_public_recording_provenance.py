"""Optional public facts cannot outlive the recordings they describe."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest

import build_demo_bundle as bdb
from api.replay_loader import ReplayLoader
from experiments.lab.rubric_score import regen_for_set
from orchestrator.recording_fingerprint import recording_fingerprint
from orchestrator.replay import GameEndReplayEntry, MeetingReplayEntry, read_all_entries
from tests.orchestrator.test_replay_integrity import (
    completed_recording as completed_recording,
)


@pytest.fixture
def scored_set(
    completed_recording: Path, tmp_path: Path
) -> tuple[Path, dict[str, Any]]:
    directory = tmp_path / "7p1i"
    directory.mkdir()
    replay = directory / completed_recording.name
    replay.write_bytes(completed_recording.read_bytes())
    (directory / "roster.json").write_text(
        json.dumps(
            {
                "num_players": 7,
                "num_impostors": 1,
                "tasks_per_crewmate": 1,
            }
        )
    )
    (directory / "MANIFEST.md").write_text(
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "| 1 | fake | fake.v1 | 2026-09-05 | abcdef12 | 0 | CREWMATES |\n"
    )
    rows = read_all_entries(replay)
    end = rows[-1]
    assert isinstance(end, GameEndReplayEntry)
    facts: dict[str, Any] = {
        "seedset": "7p1i",
        "source_fingerprint": recording_fingerprint(directory),
        "games": [
            {
                "seed": 1,
                "reason": end.reason,
                "roles": {},
                "deaths": [],
                "meetings": [
                    {
                        "ejected_player_id": row.ejected_player_id,
                        "n_contradictions": len(row.contradictions),
                        "accusations": [],
                    }
                    for row in rows
                    if isinstance(row, MeetingReplayEntry)
                ],
            }
        ],
    }
    regen_for_set(facts, directory)
    return directory, facts


def test_fresh_source_is_published_and_baked(
    scored_set: tuple[Path, dict[str, Any]],
) -> None:
    directory, _ = scored_set
    view = ReplayLoader(directory).rubric()
    assert not view.stale
    assert len(view.per_game) == 1
    assert view.per_game[0].n_meetings == 2
    assert json.loads(bdb._trimmed_rubric(view, frozenset({1})))["per_game"]


@pytest.mark.parametrize(
    "source", ["replay", "roster", "manifest", "added_replay", "missing_stamp"]
)
def test_changed_inputs_suppress_scores_and_cannot_be_restamped(
    scored_set: tuple[Path, dict[str, Any]],
    source: str,
) -> None:
    directory, facts = scored_set
    artifact = directory / "results-rubric-score.json"
    if source == "missing_stamp":
        raw = json.loads(artifact.read_text())
        del raw["source_fingerprint"]
        artifact.write_text(json.dumps(raw))
        del facts["source_fingerprint"]
    elif source == "added_replay":
        (directory / "replay-seed-99.jsonl").write_bytes(
            (directory / "replay-seed-1.jsonl").read_bytes()
        )
    else:
        name = {
            "replay": "replay-seed-1.jsonl",
            "roster": "roster.json",
            "manifest": "MANIFEST.md",
        }[source]
        path = directory / name
        path.write_bytes(path.read_bytes() + b"\n")
    before = artifact.read_bytes()
    view = ReplayLoader(directory).rubric()
    assert view.stale
    assert view.per_game == ()
    assert json.loads(bdb._trimmed_rubric(view, frozenset({1})))["per_game"] == []
    with pytest.raises(ValueError, match="re-extract"):
        regen_for_set(facts, directory)
    assert artifact.read_bytes() == before


def test_audits_and_derived_files_do_not_change_source_identity(
    scored_set: tuple[Path, dict[str, Any]],
) -> None:
    directory, facts = scored_set
    for name in ("replay-seed-1.audit.jsonl", "tournament-eval-report.json"):
        (directory / name).write_text("derived data\n")
    assert recording_fingerprint(directory) == facts["source_fingerprint"]
    assert not ReplayLoader(directory).rubric().stale


def test_bundle_suppresses_legacy_stale_rows(
    scored_set: tuple[Path, dict[str, Any]],
) -> None:
    directory, _ = scored_set
    view = ReplayLoader(directory).rubric()
    assert view.per_game
    stale = view.model_copy(update={"stale": True})
    assert json.loads(bdb._trimmed_rubric(stale, frozenset({1})))["per_game"] == []


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
    # historical seed-2 capture from the baseline-7 record before it): the
    # captured recording is the replay this checkout serves, byte for byte, and
    # the README caption names that game, its set and its record.
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
        "2026-10-01",
    )
    readme = (root / "README.md").read_text()
    assert (
        "9p2i seed 19, the game the demo's guided tour opens on, from the "
        "2026-10-01 record" in readme
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


#: The caption's scene: the pictured game and tick, and the room the impostor
#: standing outside the vents is in.
_HERO_GAME, _HERO_TICK, _HERO_ROOM = "headless-seed-19", 9, "MEDBAY"


def _hero_scene_problems(
    impostors: Sequence[tuple[str | None, bool]], bodies: int
) -> list[str]:
    """Why the caption's scene is not the one recorded, given each impostor's
    (room, inside-a-vent) and the body count at the pictured tick."""

    problems = []
    if bodies != 2:
        problems.append(f"{bodies} bodies, not two")
    if sorted(venting for _room, venting in impostors) != [False, True]:
        problems.append("not exactly one impostor inside a vent")
    if [room for room, venting in impostors if not venting] != [_HERO_ROOM]:
        problems.append(f"the impostor outside the vents is not in {_HERO_ROOM}")
    return problems


def test_the_captions_scene_is_the_recorded_one() -> None:
    # The README caption says that at tick 9 two players lie dead, one impostor
    # stands in MedBay and the other is inside a vent. The capture harness runs
    # only under its capture switch, so the claim is held here, in every run, to
    # the replay the demo serves.
    root = Path(__file__).resolve().parents[2]
    replay = ReplayLoader(root / "replays/samples/9p2i").load_replay(_HERO_GAME)
    frame = next(frame for frame in replay.ticks if frame.tick == _HERO_TICK)
    roles = {player.agent_id: player.role for player in replay.players}
    impostors = [
        (state.room_id, state.is_venting)
        for state in frame.agent_states
        if roles[state.agent_id] == "IMPOSTOR" and state.is_alive
    ]
    assert _hero_scene_problems(impostors, len(frame.bodies)) == []
    # Planted: the scene the `59bbd1be` caption described, both impostors in rooms.
    standing = [(room, False) for room, _venting in impostors]
    assert _hero_scene_problems(standing, len(frame.bodies)) == [
        "not exactly one impostor inside a vent",
        f"the impostor outside the vents is not in {_HERO_ROOM}",
    ]
    assert _hero_scene_problems(impostors, 1) == ["1 bodies, not two"]


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
