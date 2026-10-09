"""Citations resolve to one observer's typed snapshot, never to nearby evidence."""

from __future__ import annotations

import json
import shutil
from dataclasses import replace
from pathlib import Path

import pytest

from agents.memory.episodic import EpisodicEvent
from api.observation_references import observation_references
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView
from eval.validity import seeds_on_disk

_SAMPLES = Path(__file__).resolve().parents[2] / "replays/samples/9p2i"


@pytest.fixture(scope="module")
def loader() -> ReplayLoader:
    return ReplayLoader(_SAMPLES)


def _single_citation_exhibit(loader: ReplayLoader, kind: str) -> tuple[int, int, str]:
    """The shown set's first (seed, meeting, voter) citing one observation of ``kind``.

    The exhibit is found, not named: the walk reads the recorded ballots for a
    voter citing its own observation and keeps the first whose one resolved
    reference has the wanted kind (on round 2's bytes seed 5 M1 held the vent
    and seed 12 M0 the move and the sighting; on the baseline-9 bytes seed 23
    M0 and seed 4 M0).
    """

    for seed in sorted(seeds_on_disk(_SAMPLES)):
        path = _SAMPLES / f"replay-seed-{seed}.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("kind") != "meeting":
                continue
            meeting = int(row["meeting_id"].rsplit("-", 1)[-1])
            voters = sorted(
                {
                    ballot["voter"]
                    for ballot in row["ballots"]
                    if str(
                        ballot.get("primary_reason_observation_id") or ""
                    ).startswith(f"{ballot['voter']}:")
                }
            )
            for voter in voters:
                references = loader.get_meeting_memory(
                    f"headless-seed-{seed}",
                    f"headless-seed-{seed}:meeting-{meeting}",
                    voter,
                ).observation_references
                if (
                    len(references) == 1
                    and references[0].resolved
                    and references[0].kind == kind
                ):
                    return seed, meeting, voter
    raise AssertionError(f"no voter of the shown set cites one {kind} observation")


@pytest.mark.parametrize("kind", ["saw_vent", "saw_player_move", "saw_player"])
def test_genuine_citations_keep_source_identity_and_separate_scene_time(
    loader: ReplayLoader,
    kind: str,
) -> None:
    seed, meeting, observer = _single_citation_exhibit(loader, kind)
    view = loader.get_meeting_memory(
        f"headless-seed-{seed}", f"headless-seed-{seed}:meeting-{meeting}", observer
    )
    assert len(view.observation_references) == 1
    reference = view.observation_references[0]
    assert reference.resolved
    # The id names its observer and the tick it was observed at; the scene the
    # observation describes is the frame before.
    source_observer, observed, _ = reference.observation_id.split(":")
    assert source_observer == observer
    assert reference.observer_id == observer
    assert reference.kind == kind
    assert reference.subject_id is not None
    assert reference.subject_id != observer
    assert reference.observation_tick == int(observed)
    assert reference.scene_tick == reference.observation_tick - 1
    assert reference.provenance == "observed"
    if kind == "saw_player":
        assert reference.room is not None
        assert reference.text is not None
        assert reference.text.startswith(
            f"{observer} saw {reference.subject_id} in {reference.room}"
        )
        assert reference.from_room is reference.to_room is None
    elif kind == "saw_player_move":
        assert reference.from_room is not None
        assert reference.to_room is not None
        assert reference.from_room != reference.to_room
    else:
        assert reference.room is not None
    replay = loader.load_replay(f"headless-seed-{seed}")
    assert any(frame.tick == reference.scene_tick for frame in replay.ticks)


@pytest.mark.parametrize("forgery", ["foreign", "missing"])
def test_foreign_or_missing_citation_is_explicitly_unresolved(
    loader: ReplayLoader,
    tmp_path: Path,
    forgery: str,
) -> None:
    # The first single-citation sighting the shown set holds, its ballot's
    # citation forged (seed 0 M1 on round 2's bytes, seed 46 M3 on the
    # baseline-9 bytes).
    seed, meeting, voter = _single_citation_exhibit(loader, "saw_player")
    meeting_id = f"headless-seed-{seed}:meeting-{meeting}"
    # Another observer's id, or the voter's own id at an order never minted.
    other = "p-1" if voter != "p-1" else "p-2"
    forged = f"{other}:29:3" if forgery == "foreign" else f"{voter}:29:99"
    path = tmp_path / f"replay-seed-{seed}.jsonl"
    shutil.copyfile(_SAMPLES / path.name, path)
    shutil.copyfile(_SAMPLES / "roster.json", tmp_path / "roster.json")
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    forged_ballots = 0
    for row in rows:
        if row.get("kind") == "meeting" and row["meeting_id"] == meeting_id:
            for ballot in row["ballots"]:
                if ballot["voter"] == voter:
                    ballot["primary_reason_observation_id"] = forged
                    forged_ballots += 1
    assert forged_ballots == 1
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    view = ReplayLoader(tmp_path).get_meeting_memory(
        f"headless-seed-{seed}", meeting_id, voter
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


def test_v2_event_order_does_not_invent_co_presence_from_later_events() -> None:
    events = tuple(
        EpisodicEvent(
            tick=6,
            type="saw_player",
            payload={
                "player_id": player,
                "room": "ADMIN",
                "action": "task",
                "source_tick": 6,
                "observation_phase": "event",
                "observation_order": order,
                "observer_room": "ADMIN",
                "observer_in_vent": False,
            },
            provenance="observed",
            observation_id=f"opaque-{999 + order}",
        )
        for order, player in enumerate(("p-2", "p-3"))
    )
    (reference,) = observation_references(
        observer_id="p-1",
        cited_ids=("opaque-999",),
        events=events,
        scene_ticks={"opaque-999": 6},
    )
    assert reference.text == "p-1 saw p-2 in ADMIN."
    assert (
        reference.source_tick,
        reference.observation_phase,
        reference.observation_order,
    ) == (6, "event", 0)
    assert (reference.observer_room, reference.observer_in_vent) == ("ADMIN", False)
    snapshots = tuple(
        replace(
            event,
            payload={
                **event.payload,
                "observation_phase": "snapshot",
                "observation_order": None,
            },
        )
        for event in events
    )
    (together,) = observation_references(
        observer_id="p-1",
        cited_ids=("opaque-999",),
        events=snapshots,
        scene_ticks={"opaque-999": 5},
    )
    assert together.text == "p-1 saw p-2 in ADMIN with p-3."


def test_task_attempt_account_does_not_become_a_completion_certificate() -> None:
    from api.replay_loader import _observation_claim_view
    from meetings.schemas import TaskActivityAccount

    claim = TaskActivityAccount(
        type="task_activity",
        task_id="upload_logs",
        room="ADMIN",
        from_tick=2,
        to_tick=3,
    )
    projected = _observation_claim_view(claim)
    assert projected.model_dump() == claim.model_dump()
    assert projected.type != "completed_task"
