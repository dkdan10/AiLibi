#!/usr/bin/env python
"""Measure the criterion that ORDERS the spectator's featured strip.

Counts only. This reads the committed recordings through the same set loader the
spectator API serves them with, and prints numbers; it makes no provider call,
generates nothing, and writes nothing. It never touches the held-out band.

The criterion, in one sentence: an ejection is GROUNDED when the ejected player
carries a ``role_proof`` flag in the same meeting — the derived category for a
``vent_sighting``, a spoken observation matched against the speaker's own typed
vent-witness record (``api/schemas.py`` :func:`~api.schemas.classify_evidence`).
The other categories are two accounts that cannot both be true, and the alibi
envelope manufactures those against honest movers
(``tasks/direction-2026-09-19-process-over-outcome.md`` §5), so "any flag" would
be the wrong band to order a demo by.

Three things come out of it, and the featured strip's order rests on all three:

* the ejection bands, so the criterion is a measured property of the bytes
  rather than an assertion about them;
* the ELIGIBLE OPENERS — games whose FIRST meeting ejects on such a flag. The
  first meeting is the one the viewer's auto-follow opens, so a game that only
  establishes something in its third meeting is not an opener;
* the games that establish nothing at all: no flag and no ejection anywhere.

``frontend/src/components/ReplayPicker.tsx`` cites this script above
``FEATURED_GAMES``, and ``tests/api/test_sets.py`` pins the head against the
criterion rather than against a seed. The pin re-implements the predicate rather
than importing it from here: the two are deliberately independent readings of
the same bytes, in the idiom the evidence taxonomy already uses for its
API-side and eval-side twins.

Usage::

    uv run python scripts/measure_featured_criterion.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Final, Literal

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:  # `scripts/` runs as a top-level module
    sys.path.insert(0, str(_REPO_ROOT))

from api.replay_loader import SetLoaderRegistry  # noqa: E402
from api.schemas import MeetingView, ReplayView  # noqa: E402

_DEFAULT_PARENT: Final = _REPO_ROOT / "replays" / "samples"

Band = Literal["role_proof", "other_flag", "no_flag"]

_BAND_LABELS: Final[tuple[tuple[Band, str], ...]] = (
    ("role_proof", "role_proof flag"),
    ("other_flag", "other flag"),
    ("no_flag", "no flag"),
)


def ejection_band(meeting: MeetingView) -> Band | None:
    """Which evidence band the meeting's ejection falls in, or ``None``.

    ``None`` means the meeting ejected nobody — not a band, and deliberately not
    folded into ``no_flag``: "the table declined to decide" and "the table
    decided on nothing" are different states and the strip's order turns on
    telling them apart.
    """

    ejected = meeting.ejected_player_id
    if ejected is None:
        return None
    categories = {
        flag.category for flag in meeting.contradictions if ejected in flag.subjects
    }
    if "role_proof" in categories:
        return "role_proof"
    return "other_flag" if categories else "no_flag"


def opens_on_role_proof(replay: ReplayView) -> bool:
    """Whether the game's FIRST meeting ejects on a ``role_proof`` flag."""

    if not replay.meetings:
        return False
    return ejection_band(replay.meetings[0]) == "role_proof"


def establishes_nothing(replay: ReplayView) -> bool:
    """Whether the game records no flag and no ejection anywhere."""

    return not any(
        meeting.contradictions or meeting.ejected_player_id is not None
        for meeting in replay.meetings
    )


def _measure_set(parent: Path, set_name: str) -> str:
    loader = SetLoaderRegistry(parent).get(set_name)
    metas = sorted(loader.list_replays(), key=lambda meta: meta.seed)
    ejections: dict[Band, int] = {band: 0 for band, _ in _BAND_LABELS}
    role_correct: dict[Band, int] = {band: 0 for band, _ in _BAND_LABELS}
    eligible = 0
    silent: list[int] = []

    for meta in metas:
        replay = loader.load_replay(meta.game_id)
        roles = {player.agent_id: player.role for player in replay.players}
        for meeting in replay.meetings:
            band = ejection_band(meeting)
            if band is None:
                continue
            ejections[band] += 1
            if roles[str(meeting.ejected_player_id)] == "IMPOSTOR":
                role_correct[band] += 1
        if opens_on_role_proof(replay):
            eligible += 1
        if establishes_nothing(replay):
            silent.append(meta.seed)

    # Repo-relative where it can be, so the output is the same on every machine
    # and can be quoted verbatim in a card's Results.
    try:
        shown = parent.resolve().relative_to(_REPO_ROOT)
    except ValueError:
        shown = parent
    lines = [f"{shown}/{set_name} — {len(metas)} games"]
    lines.append("  ejections, by the band of the ejected player in that meeting")
    for band, label in _BAND_LABELS:
        lines.append(
            f"    {label:<16} {ejections[band]:>3} ejections "
            f"{role_correct[band]:>3} role-correct"
        )
    lines.append(
        f"  first meeting ejects on a role_proof flag: {eligible} of {len(metas)} games"
    )
    lines.append(f"  no flag and no ejection anywhere: seeds {silent}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__ and __doc__.splitlines()[0])
    parser.add_argument(
        "--parent",
        type=Path,
        default=_DEFAULT_PARENT,
        help="the directory holding the per-set replay subdirectories",
    )
    parser.add_argument(
        "--set",
        dest="sets",
        action="append",
        help="a set to measure (repeatable; default: every set under --parent)",
    )
    args = parser.parse_args(argv)
    parent: Path = args.parent
    names: list[str] = args.sets or SetLoaderRegistry(parent).available_sets()
    for name in names:
        print(_measure_set(parent, name))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
