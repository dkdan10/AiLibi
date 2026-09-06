"""Strictly replay a recorded set and census its observation-service leak checks."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import BaseModel, ConfigDict  # noqa: E402

from api.replay_loader import _load_roster_config  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from eval.leak_scan import _reconstruct_factory_records, assert_no_factory_packet_leaks  # noqa: E402
from orchestrator.recording_fingerprint import recording_fingerprint  # noqa: E402
from _verify_samples import sample_paths, verify_samples  # noqa: E402


class PacketScanResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    format_version: int = 1
    source_fingerprint: str
    map_sha256: str
    games: int
    packets: int
    kill_views: int
    vent_views: int
    body_views: int
    moved_player_rows: int
    alarm_rows: int


def scan_recording_set(directory: Path) -> PacketScanResult:
    """Count checked snapshot channels; this is not a model or feature-fit audit."""
    directory = directory.resolve()
    identity = recording_fingerprint(directory)
    roster = _load_roster_config(directory)
    if roster is None:
        raise ValueError("packet census requires an explicit roster.json")
    failures = verify_samples(directory)
    if failures:
        raise ValueError(f"recording integrity failed: {failures}")
    map_path = _REPO_ROOT / "engine/maps/canonical_1.yaml"
    map_bytes = map_path.read_bytes()
    game_map = load_canonical_map()
    paths = sample_paths(directory)
    counts = {
        name: 0
        for name in (
            "packets",
            "kill_views",
            "vent_views",
            "body_views",
            "moved_player_rows",
            "alarm_rows",
        )
    }
    with tempfile.TemporaryDirectory(prefix="ailibi-packet-census-") as scratch:
        for path in paths:
            seed = int(path.stem.removeprefix("replay-seed-"))
            records = _reconstruct_factory_records(
                path,
                game_map=game_map,
                seed=seed,
                num_players=roster.num_players,
                num_impostors=roster.num_impostors,
                tasks_per_crewmate=roster.tasks_per_crewmate,
                audit_dir=Path(scratch),
            )
            assert_no_factory_packet_leaks(records)
            counts["packets"] += len(records)
            for packet, _ in records:
                counts["kill_views"] += sum(
                    player.action == "kill" for player in packet.visible_players
                )
                counts["vent_views"] += sum(
                    player.action == "vent" for player in packet.visible_players
                )
                counts["body_views"] += len(packet.visible_bodies)
                counts["moved_player_rows"] += len(packet.moved_players)
                counts["alarm_rows"] += len(packet.audible_events)
    if recording_fingerprint(directory) != identity:
        raise ValueError("recording inputs changed during packet census")
    if map_path.read_bytes() != map_bytes:
        raise ValueError("map inputs changed during packet census")
    return PacketScanResult(
        source_fingerprint=identity,
        map_sha256=hashlib.sha256(map_bytes).hexdigest(),
        games=len(paths),
        **counts,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory",
        type=Path,
        help="Recorded set with roster.json and replay-seed files",
    )
    args = parser.parse_args(argv)
    try:
        result = scan_recording_set(args.directory)
    except (AssertionError, ValueError, OSError, RuntimeError) as exc:
        print(f"Packet census failed: {exc}", file=sys.stderr)
        return 1
    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
