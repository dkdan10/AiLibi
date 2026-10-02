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

``--alternatives`` adds a fourth block, which orders nothing: the shape of the
recorded ``considered_alternatives`` on those games' ballots. The spectator's
ballot card annotates an entry that duplicates its own header — the voter
itself, or the target the vote applied to — and this is where the rate behind
that claim is counted instead of asserted.

``--list`` names the games behind the counts: the ``seed:meeting`` of every
ejection in each band and of the role-correct ones, the eligible openers, and
two candidate lists the strip draws its second and third kinds of card from:

* the NON-VENT OPENERS — games whose first meeting ejects an impostor while no
  flag is raised anywhere in the game and no vent event happens at or before
  that meeting, so the table decided with no vent evidence in front of it;
* the first meetings that eject a crewmate who did not open the meeting.

The role reads behind ``role-correct`` and both lists are curation: they
describe which games the strip can show and gate no record, instrument or
adoption. It prints seeds only, never a transcript line.

Usage::

    uv run python scripts/measure_featured_criterion.py
    uv run python scripts/measure_featured_criterion.py --alternatives --list
    uv run python scripts/measure_featured_criterion.py --alternatives \\
        --games 9p2i:19 9p2i:14 4p1i:2 4p1i:11 4p1i:29
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


def _first_ejected_role(replay: ReplayView) -> tuple[str, str] | None:
    """The first meeting's ejected player and recorded role, or ``None``."""

    if not replay.meetings:
        return None
    ejected = replay.meetings[0].ejected_player_id
    if ejected is None:
        return None
    roles = {player.agent_id: player.role for player in replay.players}
    return ejected, roles[ejected]


def opens_on_non_vent_impostor_ejection(replay: ReplayView) -> bool:
    """Whether the first meeting ejects an impostor with no vent evidence about.

    No flag of any kind is raised in any meeting of the game, and no vent event
    happens at or before the first meeting's tick: whatever the table decided
    on, it was not a vent sighting or a flagged contradiction.
    """

    first = _first_ejected_role(replay)
    if first is None or first[1] != "IMPOSTOR":
        return False
    if any(meeting.contradictions for meeting in replay.meetings):
        return False
    opened = replay.meetings[0].tick
    return not any(
        event.type == "vent" and event.tick <= opened
        for frame in replay.ticks
        for event in frame.events
    )


def first_meeting_ejects_a_crewmate_not_the_opener(replay: ReplayView) -> bool:
    """Whether the first meeting ejects a crewmate other than its opener."""

    first = _first_ejected_role(replay)
    return (
        first is not None
        and first[1] == "CREWMATE"
        and first[0] != replay.meetings[0].triggered_by
    )


def _join(tokens: list[str]) -> str:
    return " ".join(tokens) if tokens else "none"


def alternatives_shape(replay: ReplayView) -> tuple[int, int, int, int]:
    """``(ballots, recorded entries, ballots naming the voter, naming the target)``.

    ``considered_alternatives`` is NOT a list of the other players at the table:
    a ballot can list the voter itself, and it can list the target the vote was
    applied to. Both render a second copy of a pill the ballot card's header
    already shows, so the spectator's render annotates them
    (``frontend/src/components/BallotCard.tsx``) — and the rates that claim
    rests on are counted here rather than asserted.
    """

    ballots = entries = own = applied = 0
    for meeting in replay.meetings:
        for ballot in meeting.ballots:
            ballots += 1
            entries += len(ballot.considered_alternatives)
            if ballot.voter in ballot.considered_alternatives:
                own += 1
            if ballot.target in ballot.considered_alternatives:
                applied += 1
    return ballots, entries, own, applied


def _measure_set(
    parent: Path,
    set_name: str,
    *,
    seeds: frozenset[int] | None = None,
    alternatives: bool = False,
    listing: bool = False,
) -> str:
    loader = SetLoaderRegistry(parent).get(set_name)
    every = sorted(loader.list_replays(), key=lambda meta: meta.seed)
    metas = [meta for meta in every if seeds is None or meta.seed in seeds]
    ejections: dict[Band, list[str]] = {band: [] for band, _ in _BAND_LABELS}
    role_correct: dict[Band, list[str]] = {band: [] for band, _ in _BAND_LABELS}
    eligible: list[int] = []
    silent: list[int] = []
    non_vent: list[int] = []
    crewmate_not_opener: list[int] = []
    shape = [0, 0, 0, 0]

    for meta in metas:
        replay = loader.load_replay(meta.game_id)
        shape = [
            carried + new for carried, new in zip(shape, alternatives_shape(replay))
        ]
        roles = {player.agent_id: player.role for player in replay.players}
        for index, meeting in enumerate(replay.meetings):
            band = ejection_band(meeting)
            if band is None:
                continue
            where = f"{meta.seed}:{index}"
            ejections[band].append(where)
            if roles[str(meeting.ejected_player_id)] == "IMPOSTOR":
                role_correct[band].append(where)
        if opens_on_role_proof(replay):
            eligible.append(meta.seed)
        if establishes_nothing(replay):
            silent.append(meta.seed)
        if opens_on_non_vent_impostor_ejection(replay):
            non_vent.append(meta.seed)
        if first_meeting_ejects_a_crewmate_not_the_opener(replay):
            crewmate_not_opener.append(meta.seed)

    # Repo-relative where it can be, so the output is the same on every machine
    # and can be quoted verbatim in a card's Results.
    try:
        shown = parent.resolve().relative_to(_REPO_ROOT)
    except ValueError:
        shown = parent
    selected = "" if seeds is None else f" of {len(every)} (selected)"
    lines = [f"{shown}/{set_name} — {len(metas)} games{selected}"]
    lines.append("  ejections, by the band of the ejected player in that meeting")
    for band, label in _BAND_LABELS:
        lines.append(
            f"    {label:<16} {len(ejections[band]):>3} ejections "
            f"{len(role_correct[band]):>3} role-correct"
        )
    lines.append(
        f"  first meeting ejects on a role_proof flag: {len(eligible)} of "
        f"{len(metas)} games"
    )
    lines.append(f"  no flag and no ejection anywhere: seeds {silent}")
    if listing:
        lines.append("  the games behind each count (seed:meeting)")
        for band, label in _BAND_LABELS:
            lines.append(f"    {label} ejections: {_join(ejections[band])}")
            lines.append(f"    {label} role-correct: {_join(role_correct[band])}")
        lines.append(f"  first meeting ejects on a role_proof flag: seeds {eligible}")
        lines.append(
            "  first meeting ejects an impostor, no flag anywhere and no vent at or "
            f"before it: seeds {non_vent}"
        )
        lines.append(
            "  first meeting ejects a crewmate who did not open it: seeds "
            f"{crewmate_not_opener}"
        )
    if alternatives:
        ballots, entries, own, applied = shape
        lines.append("  considered_alternatives, over every ballot in those games")
        lines.append(f"    {ballots:>4} ballots  {entries:>4} recorded entries")
        lines.append(f"    ballots listing the voter itself:     {own:>4}")
        lines.append(f"    ballots listing the applied target:   {applied:>4}")
    return "\n".join(lines)


def _parse_games(tokens: list[str]) -> dict[str, frozenset[int]]:
    """``["9p2i:23", "4p1i:2"]`` to ``{"9p2i": {23}, "4p1i": {2}}``.

    A malformed token raises rather than being skipped: a typo that silently
    measured fewer games than asked for would print a number nobody could
    reproduce.
    """

    selected: dict[str, set[int]] = {}
    for token in tokens:
        set_name, _, seed = token.partition(":")
        if not set_name or not seed.isdigit():
            raise ValueError(f"--games takes SET:SEED tokens, got {token!r}")
        selected.setdefault(set_name, set()).add(int(seed))
    return {name: frozenset(seeds) for name, seeds in selected.items()}


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
    parser.add_argument(
        "--games",
        nargs="+",
        metavar="SET:SEED",
        help="measure only these games (e.g. the featured strip's five)",
    )
    parser.add_argument(
        "--alternatives",
        action="store_true",
        help="also count the shape of considered_alternatives on their ballots",
    )
    parser.add_argument(
        "--list",
        dest="listing",
        action="store_true",
        help="also name the games behind each count and the two candidate lists",
    )
    args = parser.parse_args(argv)
    parent: Path = args.parent
    if args.games and args.sets:
        parser.error("--games already names its sets; do not pass --set as well")
    if args.games:
        try:
            chosen = _parse_games(args.games)
        except ValueError as exc:
            parser.error(str(exc))
        for name in sorted(chosen):
            print(
                _measure_set(
                    parent,
                    name,
                    seeds=chosen[name],
                    alternatives=args.alternatives,
                    listing=args.listing,
                )
            )
        return 0
    names: list[str] = args.sets or SetLoaderRegistry(parent).available_sets()
    for name in names:
        print(
            _measure_set(
                parent, name, alternatives=args.alternatives, listing=args.listing
            )
        )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
