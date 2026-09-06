from __future__ import annotations

from pathlib import Path
from collections.abc import Sequence

from eval.leak_scan import PacketRecord, assert_no_factory_packet_leaks

import pytest

from scan_recording_packets import scan_recording_set


@pytest.mark.parametrize("set_name", ["4p1i", "9p2i"])
def test_ml_corpus_exercises_real_observation_channels(set_name: str) -> None:
    result = scan_recording_set(Path("replays/ml_corpus") / set_name)
    assert result.games > 0 and result.packets > result.games
    assert (
        result.vent_views > 0 and result.body_views > 0 and result.moved_player_rows > 0
    )
    if set_name == "9p2i":
        assert result.kill_views > 0 and result.alarm_rows > 0
    assert result.source_fingerprint.startswith("sha256:")


def test_corpus_scan_fails_on_a_missing_witness_producer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("engine.rules._witnesses_in_room", lambda *args, **kwargs: ())
    with pytest.raises(AssertionError, match="witness entitlement"):
        scan_recording_set(Path("replays/ml_corpus/9p2i"))


def test_corpus_scan_rejects_inputs_changed_during_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import shutil

    import scan_recording_packets as scanner

    source = Path("replays/ml_corpus/4p1i")
    destination = tmp_path / "corpus"
    shutil.copytree(source, destination)
    original = assert_no_factory_packet_leaks
    changed = False

    def scan_then_change_roster(records: Sequence[PacketRecord]) -> None:
        nonlocal changed
        original(records)
        if not changed:
            roster = destination / "roster.json"
            roster.write_bytes(roster.read_bytes() + b"\n")
            changed = True

    monkeypatch.setattr(
        scanner, "assert_no_factory_packet_leaks", scan_then_change_roster
    )
    with pytest.raises(ValueError, match="inputs changed during packet census"):
        scanner.scan_recording_set(destination)


def test_corpus_scan_requires_explicit_roster(tmp_path: Path) -> None:
    (tmp_path / "replay-seed-0.jsonl").write_text("{}\n")
    with pytest.raises(ValueError, match="explicit roster"):
        scan_recording_set(tmp_path)
