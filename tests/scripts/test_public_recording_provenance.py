"""Optional public facts cannot outlive the recordings they describe."""

from __future__ import annotations

import hashlib
import json
import re
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


def test_historical_media_hashes_and_labels_are_current(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[2]
    media = root / "docs/media"
    assert not _asset_mismatches(media)
    provenance = json.loads((media / "provenance.json").read_text())
    assert provenance["status"] == "historical"
    assert provenance["recording"]["prompt_version"] == "v4"
    assert "earlier recording" in (root / "README.md").read_text()
    assert "historical" in (media / "README.md").read_text()
    # A changed image with an unchanged claim must fail the digest check.
    (tmp_path / "provenance.json").write_bytes((media / "provenance.json").read_bytes())
    names = list(provenance["assets_sha256"])
    for name in names:
        (tmp_path / name).write_bytes((media / name).read_bytes())
    changed = tmp_path / names[0]
    changed.write_bytes(changed.read_bytes() + b"changed")
    assert _asset_mismatches(tmp_path) == [names[0]]


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
        if declared != actual or (
            not declared and placement != "Historical archive only"
        ):
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
            "| Historical archive only |", "| [README image](../../README.md) |", 1
        )
    )
    assert _media_placement_mismatches(tmp_path) == ["spectator-meeting.png"]
