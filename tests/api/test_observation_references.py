"""Citations resolve to one observer's typed snapshot, never to nearby evidence."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from agents.memory.episodic import EpisodicEvent
from api.observation_references import observation_references
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView

_SAMPLES = Path(__file__).resolve().parents[2] / "replays/samples/9p2i"


@pytest.fixture(scope="module")
def loader() -> ReplayLoader:
    return ReplayLoader(_SAMPLES)


@pytest.mark.parametrize(
    (
        "seed",
        "meeting",
        "observer",
        "observation_id",
        "kind",
        "subject",
        "observed",
        "scene",
    ),
    [
        (23, 0, "p-5", "p-5:8:1", "saw_vent", "p-6", 8, 7),
        (46, 3, "p-9", "p-9:29:3", "saw_player_move", "p-1", 29, 28),
        (46, 3, "p-3", "p-3:29:1", "saw_player", "p-4", 29, 28),
    ],
)
def test_genuine_citations_keep_source_identity_and_separate_scene_time(
    loader: ReplayLoader,
    seed: int,
    meeting: int,
    observer: str,
    observation_id: str,
    kind: str,
    subject: str,
    observed: int,
    scene: int,
) -> None:
    view = loader.get_meeting_memory(
        f"headless-seed-{seed}", f"headless-seed-{seed}:meeting-{meeting}", observer
    )
    assert len(view.observation_references) == 1
    reference = view.observation_references[0]
    assert reference.resolved
    assert reference.observation_id == observation_id
    assert reference.observer_id == observer
    assert reference.kind == kind
    assert reference.subject_id == subject
    assert reference.observation_tick == observed
    assert reference.scene_tick == scene
    assert reference.provenance == "observed"
    if subject == "p-4":
        assert reference.text == "p-3 saw p-4 in CAFETERIA with p-9."
        assert reference.from_room is reference.to_room is None
    elif kind == "saw_player_move":
        assert (reference.from_room, reference.to_room) == ("CAFETERIA", "EAST_HALL")
    else:
        assert reference.room == "ENGINEERING"
    replay = loader.load_replay(f"headless-seed-{seed}")
    assert any(frame.tick == scene for frame in replay.ticks)


@pytest.mark.parametrize("forged", ["p-9:29:3", "p-3:29:99"])
def test_foreign_or_missing_citation_is_explicitly_unresolved(
    tmp_path: Path,
    forged: str,
) -> None:
    path = tmp_path / "replay-seed-46.jsonl"
    shutil.copyfile(_SAMPLES / path.name, path)
    shutil.copyfile(_SAMPLES / "roster.json", tmp_path / "roster.json")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    for row in rows:
        if row.get("kind") == "meeting" and row["meeting_id"].endswith("meeting-3"):
            for ballot in row["ballots"]:
                if ballot["voter"] == "p-3":
                    ballot["primary_reason_observation_id"] = forged
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    view = ReplayLoader(tmp_path).get_meeting_memory(
        "headless-seed-46", "headless-seed-46:meeting-3", "p-3"
    )
    (reference,) = view.observation_references
    assert reference.observation_id == forged
    assert not reference.resolved
    assert reference.text is None
    assert reference.scene_tick is reference.observation_tick is None
    assert reference.subject_id is None


def test_opaque_id_and_unknown_frame_do_not_invent_a_timestamp() -> None:
    event = EpisodicEvent(
        tick=6,
        type="saw_body",
        payload={"victim_id": "p-2", "room": "ADMIN"},
        provenance="observed",
        observation_id="opaque:999:handle",
    )
    refs = observation_references(
        observer_id="p-1",
        cited_ids=("opaque:999:handle", "missing"),
        events=(event,),
        scene_ticks={},
    )
    known = next(ref for ref in refs if ref.resolved)
    assert known.observation_tick == 6
    assert known.scene_tick is None
    assert known.text == "p-1 discovered p-2's body in ADMIN."
    assert (
        observation_references(
            observer_id="p-1", cited_ids=(), events=(event,), scene_ticks={}
        )
        == ()
    )


def test_old_memory_payload_has_no_manufactured_references(
    loader: ReplayLoader,
) -> None:
    original = loader.get_meeting_memory(
        "headless-seed-23", "headless-seed-23:meeting-0", "p-5"
    )
    old = original.model_dump(exclude={"observation_references"})
    assert AgentMemoryView.model_validate(old).observation_references == ()
