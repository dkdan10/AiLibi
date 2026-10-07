#!/usr/bin/env python3
"""Publish the game-shape profile (rubric version 2) of each profiled set.

Writes ``results-game-profile.json`` beside the recordings of every set in
:data:`PROFILE_SETS` and the generated page ``docs/game-profile.md``, from
:func:`eval.game_profile.build_profile` over bytes already in the tree, with
zero model calls. ``--check`` recomputes both and exits 1 naming the drifted
file; an absent file is reported before anything is computed.
``--set-dir DIR --json-stdout`` prints one 9-player, 2-impostor directory's
profile (a candidate round, an export of an earlier recording) and writes
nothing; a directory of another roster is refused by name.

Each profile is stamped with its era (:mod:`eval.eras`), the set's MANIFEST
key as the API loader reads it (``api.replay_loader._manifest_git_sha``) and
the source fingerprint (:func:`orchestrator.recording_fingerprint.recording_fingerprint`),
both read before and after the walk; a difference raises rather than stamping
bytes the walk may not have read.

A conformance breach (a recording the profile cannot read as ruled, such as an
ejecting ballot whose grounding label the tripwire does not classify) exits 1
and names the set, the seed, the meeting and the voter.

Usage::

    python scripts/publish_game_profile.py
    python scripts/publish_game_profile.py --check
    python scripts/publish_game_profile.py --set-dir DIR --json-stdout
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Final

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _report_output import atomic_write_report, preflight_report_output  # noqa: E402
from api.replay_loader import _expected_seedset, _manifest_git_sha  # noqa: E402
from eval import game_profile as profile_module  # noqa: E402
from eval.eras import COMMITTED_SETS, CommittedSet, committed_set, sets_in  # noqa: E402
from eval.game_profile import (  # noqa: E402
    GameProfile,
    GameProfileConformanceError,
    ProfileStamp,
    build_profile,
    serialize_profile,
)
from eval.gameplay_census import CensusInputs, load_census_inputs  # noqa: E402
from eval.process_scorecard import SetInputs, load_set_inputs  # noqa: E402
from eval.validity import resolve_roster_knobs  # noqa: E402
from orchestrator.recording_fingerprint import recording_fingerprint  # noqa: E402

#: The committed sets that ship a profile. ``replays/samples/4p1i`` ships none:
#: its roster-relative shelves degenerate on a four-player table.
PROFILE_SETS: Final[tuple[str, ...]] = ("replays/samples/9p2i",)

#: The roster a profile reads: (players, impostors).
PROFILE_ROSTER: Final[tuple[int, int]] = (9, 2)

#: The served file's name, beside the recordings of its set.
PROFILE_FILENAME: Final[str] = "results-game-profile.json"

MARKDOWN_PATH: Final[Path] = Path("docs/game-profile.md")

#: The one command a reader, or a red ``--check``, is told to run.
REGENERATE_COMMAND: Final[str] = "uv run python scripts/publish_game_profile.py"

CensusLoader = Callable[[Path], CensusInputs]
ScorecardLoader = Callable[[Path], SetInputs]


class ProfileRefused(ValueError):
    """A directory or set the profile refuses to read, named in the message."""


def _load_scorecard(set_dir: Path) -> SetInputs:
    return load_set_inputs(set_dir)


@dataclass(frozen=True)
class Loaders:
    """The two impure readers a profile walks, injectable for tests."""

    census: CensusLoader = load_census_inputs
    scorecard: ScorecardLoader = _load_scorecard


def require_profile_roster(set_dir: Path) -> None:
    """Refuse, by name, a directory whose roster the profile does not read."""

    players, impostors, _ = resolve_roster_knobs(set_dir)
    if (players, impostors) != PROFILE_ROSTER:
        raise ProfileRefused(
            f"{set_dir} holds a {players}-player, {impostors}-impostor roster; the "
            f"game-shape profile reads {PROFILE_ROSTER[0]}-player, "
            f"{PROFILE_ROSTER[1]}-impostor sets only"
        )


def era_id(
    set_dir: Path, root: Path, *, registry: Sequence[CommittedSet] = COMMITTED_SETS
) -> str | None:
    """The era the registry files ``set_dir`` under, or ``None`` outside it.

    ``set_dir`` is named by its path below ``root``, so a candidate round or a
    scratch copy outside the registry carries no era.
    """

    resolved = set_dir.resolve()
    if not resolved.is_relative_to(root.resolve()):
        return None
    relative = resolved.relative_to(root.resolve()).as_posix()
    if relative not in {entry.path for entry in registry}:
        return None
    return committed_set(relative, registry=registry).era.id


def read_stamp(set_dir: Path, root: Path) -> ProfileStamp:
    """The provenance a profile of ``set_dir`` carries, read from its bytes."""

    seedset = _expected_seedset(set_dir)
    if seedset is None:
        raise ProfileRefused(f"{set_dir} has no roster.json to name its seedset")
    return ProfileStamp(
        era=era_id(set_dir, root),
        manifest_key=_manifest_git_sha(set_dir),
        source_fingerprint=recording_fingerprint(set_dir),
        seedset=seedset,
    )


def compute_profile(
    set_dir: Path, *, root: Path = _REPO_ROOT, loaders: Loaders = Loaders()
) -> GameProfile:
    """One directory's profile, stamped with what the walk read.

    The stamp is read before and after both walks; a difference raises.
    """

    require_profile_roster(set_dir)
    before = read_stamp(set_dir, root)
    inputs = loaders.census(set_dir)
    scorecard = loaders.scorecard(set_dir)
    after = read_stamp(set_dir, root)
    if after != before:
        raise RuntimeError(
            f"{set_dir}: the recordings changed while the profile walked them"
        )
    return build_profile(inputs, scorecard, stamp=before)


def profile_path(root: Path, set_path: str) -> Path:
    return root / set_path / PROFILE_FILENAME


def compute_profiles(
    root: Path, *, loaders: Loaders = Loaders()
) -> tuple[tuple[str, GameProfile], ...]:
    """Every profiled set's profile, each alone in its era."""

    profiles: list[tuple[str, GameProfile]] = []
    for set_path in PROFILE_SETS:
        era = committed_set(set_path).era
        if sets_in(era) != (set_path,):
            raise ProfileRefused(
                f"the {era.id} era holds {', '.join(sets_in(era))}; the leak rule "
                "would span them, and the profile is computed per set"
            )
        profiles.append(
            (set_path, compute_profile(root / set_path, root=root, loaders=loaders))
        )
    return tuple(profiles)


# ---------------------------------------------------------------------------
# The page
# ---------------------------------------------------------------------------

#: Every name the page prints, in plain words.
NAMES: Final[dict[str, str]] = {
    profile_module.REPORTER_SAW_IT: "The reporter saw it happen",
    profile_module.DOUBLE_KILL: "Double kill",
    profile_module.SLOW_BURN: "Slow burn",
    profile_module.TWO_KILLS_AFTER_ONE_REGROUP: "Two kills after one regroup",
    profile_module.CLOSE_CALL: "A close call",
    profile_module.SUSPICION_MOVED: "Suspicion moved",
    profile_module.THIRD_ROUND: "A third round",
    profile_module.CAUGHT_VENTING: "Caught venting",
    profile_module.ONE_LINE_TWO_READINGS: "One line, two readings",
    profile_module.STRUCK_AFTER_THE_REGROUP: "Struck after the regroup",
    profile_module.ONE_VOTE_EJECTION: "One-vote ejection",
    profile_module.NOBODY_VOTED_OUT: "Nobody voted out",
    profile_module.DOWN_TO_THE_WIRE: "Down to the wire",
    profile_module.RUNAWAY: "Runaway",
    profile_module.DECIDED_AT_A_MEETING: "Decided at a meeting",
    profile_module.RIGHT_WITHOUT_PROOF: "Decided without proof: the table was right",
    profile_module.WRONG_ON_WHAT_IT_HELD: (
        "Decided without proof: wrong on what it held"
    ),
    profile_module.EYEWITNESS_CHIP: "An eyewitness voted on it",
    profile_module.HELD_NOTHING: "Decided by a vote that held nothing",
    profile_module.MANUFACTURED: "Decided on a manufactured contradiction",
    profile_module.ANY_EJECTION: "some meeting ejected someone",
    profile_module.CREWMATE_EJECTED: "a crewmate was ejected",
    "length_in_ticks": "length in ticks",
    "meetings_by_trigger": "meetings, by what opened them",
    "kill_timeline": "the kill timeline, with regroups and the wave",
    "reports_with_corpse_age": "reports, with the corpse's age",
    "bodies_never_found": "bodies never found",
    "ending": "the ending",
    "distance_from_the_other_ending": "the losing side's distance from its ending",
    "sabotage_starts": "sabotages in play, with the final task count",
    "ejection_annotations": "each ejection, right or wrong",
}

#: What each tripwire reading removes or keeps, in words.
READING_WORDS: Final[dict[str, str]] = {
    "decisive": (
        "decisive, the governing reading: the ejecting ballots labelled "
        "off-target, uncited or invalid-citation removed"
    ),
    "decisive_read_as_skip": "decisive, those ballots read as SKIP instead",
    "decisive_all_ungrounded_removed": (
        "decisive, every ballot so labelled removed, whatever its target"
    ),
    "every": "every ejecting ballot so labelled",
    "any": "any ejecting ballot so labelled",
    "manufactured": (
        "the ejected player named by an alibi-class flag row 3 classes as manufactured"
    ),
}

CLASS_WORDS: Final[dict[str, str]] = {
    "shelf": "a shelf before the reveal",
    "leaks": "behind the reveal, by the leak rule",
    "saturated": "a facet, by the saturation rule",
    "reads_an_ejection": "behind the reveal: it reads an ejection",
    "reads_the_ending": "behind the reveal: it reads the ending",
    "reads_a_role": "behind the reveal: it reads the ejected player's role",
    "chip": "a meeting chip, not leak-tested",
    "facet": "a facet",
    "tripwire": "a tripwire",
}


def _definitions() -> list[str]:
    c = profile_module
    share = c.SATURATION_SHARE
    return [
        "## Definitions",
        "",
        "Every definition reads committed bytes through the gameplay census's carrier "
        "and scorecard row 3's helpers. The constants are frozen for this profile "
        f"version ({c.RUBRIC_VERSION}); a change to any of them needs a new version.",
        "",
        "**Shelves before the reveal.** Each reads what the table held and did "
        "(ballots, grounding labels, cited ids, accusations, flags, meetings) and the "
        "engine's physical record (kills, the engine's witness lists, bodies, "
        "regroups), and no role and no ending.",
        "",
        f"* **{NAMES[c.REPORTER_SAW_IT]}**: a report meeting opened by a player in "
        "the engine's witness list for the kill of the body reported, the body "
        "joined to its kill by victim.",
        f"* **{NAMES[c.DOUBLE_KILL]}**: two kills on the same tick.",
        f"* **{NAMES[c.SLOW_BURN]}**: a stretch of at least {c.SLOW_BURN_TICKS} ticks "
        "with no kill, counted from tick 0, between kills or to the end.",
        f"* **{NAMES[c.TWO_KILLS_AFTER_ONE_REGROUP]}**: two kills inside one "
        "regroup's wave. A kill is in the wave of the last regroup before it when it "
        "lands more than the recorded kill cooldown, and at most "
        f"{c.WAVE_SLACK_TICKS} ticks past it, after that regroup.",
        f"* **{NAMES[c.CLOSE_CALL]}**: a meeting whose leading choice, a player or "
        f"SKIP, beat the runner-up by at most {c.CLOSE_CALL_MARGIN} ballot.",
        f"* **{NAMES[c.SUSPICION_MOVED]}**: across two consecutive meetings, a "
        "player who drew EJECT ballots earlier is ejected later; or a player who drew "
        "EJECT ballots draws none, and no accusation, while alive; or the leading "
        "EJECT target changes while the old lead lives. Read from ballots and "
        "accusations, never from the engine's suspicion number.",
        f"* **{NAMES[c.THIRD_ROUND]}**: at least {c.THIRD_ROUND_MEETINGS} meetings.",
        f"* **{NAMES[c.CAUGHT_VENTING]}**: a meeting with a vent-sighting flag.",
        f"* **{NAMES[c.ONE_LINE_TWO_READINGS]}**: two ballots labelled supported, "
        "holds-nothing or off-target cite the same turn and name different "
        "targets.",
        f"* **{NAMES[c.STRUCK_AFTER_THE_REGROUP]}**: any kill in a regroup's wave.",
        "",
        "Every one of them is a candidate. The publisher classes each per era:",
        "",
        "* **The saturation rule**, applied first: a candidate holding more than "
        f"{share.numerator} in {share.denominator} of the era's games is a facet, "
        "never a shelf.",
        "* **The leak rule**: each candidate's membership is tested by a two-sided "
        "Fisher exact test against each recorded ending, against some meeting having "
        "ejected someone and against a crewmate having been ejected, over every game "
        "of the era, a game on a tripwire counted as a non-member. Any p below "
        f"{c.profile_constants().leak_p_level} puts the candidate behind the reveal "
        "for that era. The rule can only hide more; it never selects or orders a "
        "game.",
        "",
        "**Shelves behind the reveal** read an ejection, the ending or a role:",
        "",
        f"* **{NAMES[c.ONE_VOTE_EJECTION]}**: an ejection by a margin of one, SKIP "
        "counted as a choice.",
        f"* **{NAMES[c.NOBODY_VOTED_OUT]}**: every meeting skipped.",
        f"* **{NAMES[c.DOWN_TO_THE_WIRE]}**: the losing side was one step from its "
        f"own ending, having started at least {c.DOWN_TO_THE_WIRE_START} steps away.",
        f"* **{NAMES[c.RUNAWAY]}**: the losing side was still at least "
        f"{c.RUNAWAY_SHARE.numerator} in {c.RUNAWAY_SHARE.denominator} of its starting "
        "distance from its ending.",
        "* The distance is measured the same way for each side: an impostor win "
        "counts the crew's tasks left; a task win counts the impostors' kills short "
        "of parity at game over; an ejection win counts their kills short of parity "
        "at the deciding meeting.",
        f"* **{NAMES[c.DECIDED_AT_A_MEETING]}**: the game ended at a meeting.",
        "* **Decided without proof**: an ejection whose ejecting ballots are all "
        "labelled supported or flag-only, where no vent flag and no manufactured flag "
        "names the ejected player. The reveal splits it by the ejected player's role "
        "into two halves, always shown together: the table was right, and wrong on "
        "what it held. A wrong call on lines the voters held and believed is part of "
        "the game, shown beside its right twin; it is reported and gates nothing.",
        "",
        f"**The chip.** *{NAMES[c.EYEWITNESS_CHIP]}* marks a meeting where some "
        "player's ballot cites the own-kill row that player held. It places a game "
        "on no shelf and takes no leak or saturation class.",
        "",
        "**Facets.** Before the reveal: "
        + "; ".join(NAMES[name] for name in c.PRE_REVEAL_FACETS)
        + ". Behind it: "
        + "; ".join(NAMES[name] for name in c.REVEAL_FACETS)
        + ". A sabotage is in play from the first tick it is active on the "
        "engine's frame, so one started on a game's final tick is never in play.",
        "",
        "**Tripwires.** A game that trips one sits on no shelf, keeps a plain label "
        "and stays under All games; it is never hidden and never scored.",
        "",
        f"* **{NAMES[c.HELD_NOTHING]}**: with the ejecting ballots labelled "
        "off-target, uncited or invalid-citation removed, the game's own tally at "
        "the meeting's recorded confidence floor ejects no one or someone else. "
        "Supported and flag-only ballots are held; not-assessed ballots stay as "
        "recorded. An ejecting ballot labelled as holding nothing is a case the "
        "tripwire does not classify, so it stops the publisher, naming the set, the "
        "seed, the meeting and the voter, until the owner says how it reads.",
        f"* **{NAMES[c.MANUFACTURED]}**: the ejected player is named by an "
        "alibi-class flag that row 3 classes as manufactured over the engine's "
        "route. Row 3 can answer few flags, so this tripwire is nearly blind.",
        "",
    ]


#: The smallest p the page prints as a number; a smaller one reads as under it.
_P_FLOOR: Final[float] = 0.0001


def _p_text(p: float) -> str:
    return f"under {_P_FLOOR}" if p < _P_FLOOR else f"{p:.4f}"


def _members(shelf: profile_module.Shelf) -> str:
    return ", ".join(str(member.seed) for member in shelf.members) or "none"


def _set_lines(set_path: str, profile: GameProfile) -> list[str]:
    pre = profile.pre_reveal
    reveal = profile.reveal
    lines = [
        f"## `{set_path}`",
        "",
        f"* rubric version: {profile.rubric_version}",
        f"* era: `{profile.era}`",
        f"* MANIFEST key: `{profile.manifest_key}`",
        f"* source fingerprint: `{profile.source_fingerprint}`",
        f"* seedset: `{profile.seedset}`",
        f"* games: {len(pre.games)}",
        "",
        "### Tripwires",
        "",
        "| reading | ejections | games | entries (seed, meeting index) |",
        "| --- | --- | --- | --- |",
    ]
    for reading in pre.tripwires.readings:
        entries = ", ".join(
            f"({entry.seed}, {entry.meeting})" for entry in reading.entries
        )
        games = len({entry.seed for entry in reading.entries})
        lines.append(
            f"| {READING_WORDS[reading.name]} | {len(reading.entries)} | {games} "
            f"| {entries or 'none'} |"
        )
    tripped = [game.seed for game in pre.games if game.tripped]
    lines.extend(
        [
            "",
            "The governing readings trip "
            + (", ".join(f"seed {seed}" for seed in tripped) or "no game")
            + f". Row 3 can answer {pre.tripwires.alibi_flags_evaluable} of this "
            f"set's {pre.tripwires.alibi_flags} alibi-class flags, so the "
            "manufactured-contradiction tripwire is nearly blind here.",
            "",
            "### Shelves before the reveal",
            "",
            "| shelf | games | seeds |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {NAMES[shelf.name]} | {len(shelf.members)} | {_members(shelf)} |"
        for shelf in pre.shelves
    )
    for chip in pre.chips:
        marked = sum(len(member.meetings) for member in chip.members)
        seeds = ", ".join(str(member.seed) for member in chip.members) or "none"
        lines.extend(
            [
                "",
                f"*{NAMES[chip.name]}* marks {marked} meetings in "
                f"{len(chip.members)} games: {seeds}.",
            ]
        )
    held = Counter(
        sum(
            1
            for shelf in pre.shelves
            if any(m.seed == game.seed for m in shelf.members)
        )
        for game in pre.games
        if not game.tripped
    )
    lines.extend(
        [
            "",
            "Games on no tripwire, by how many shelves before the reveal they sit on: "
            + ", ".join(f"{games} on {count}" for count, games in sorted(held.items()))
            + ".",
            "",
            "### Shelves behind the reveal",
            "",
            "| shelf | games | seeds |",
            "| --- | --- | --- |",
        ]
    )
    lines.extend(
        f"| {NAMES[shelf.name]} | {len(shelf.members)} | {_members(shelf)} |"
        for shelf in reveal.shelves
    )
    for shelf in (
        reveal.decided_without_proof.right,
        reveal.decided_without_proof.wrong,
    ):
        ejections = sum(len(member.meetings) for member in shelf.members)
        lines.append(
            f"| {NAMES[shelf.name]} | {len(shelf.members)} ({ejections} ejections) "
            f"| {_members(shelf)} |"
        )
    lines.extend(
        [
            "",
            "### Classes this era",
            "",
            "Each row is one 2x2 table over every game of the era: members holding the "
            "fact, members without it, non-members holding it, non-members without "
            "it, and the two-sided p.",
            "",
            "| candidate | games on it | fact | table | p | class |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for table in reveal.class_tables:
        for row in table.rows:
            lines.append(
                f"| {NAMES[table.name]} | {table.members} of {table.games} "
                f"| {NAMES.get(row.fact, row.fact)} | {row.a}, {row.b}, {row.c}, {row.d} "
                f"| {_p_text(row.p)} | {CLASS_WORDS[table.classification]} |"
            )
    endings = {game.seed: game.ending for game in reveal.games}
    by_ending: dict[str, list[int]] = {}
    for game in pre.games:
        if game.tripped:
            continue
        count = sum(
            1
            for shelf in pre.shelves
            if any(m.seed == game.seed for m in shelf.members)
        )
        by_ending.setdefault(endings[game.seed], []).append(count)
    lines.extend(
        [
            "",
            "### The lean of the shelf count",
            "",
            "Never served and never used to order a game: the mean number of shelves "
            "before the reveal per game on no tripwire, by ending.",
            "",
            "| ending | games | mean shelves |",
            "| --- | --- | --- |",
        ]
    )
    for ending in sorted(by_ending):
        counts = by_ending[ending]
        mean = Fraction(sum(counts), len(counts))
        lines.append(f"| `{ending}` | {len(counts)} | {float(mean):.2f} |")
    lines.append("")
    return lines


def render_markdown(profiles: Sequence[tuple[str, GameProfile]]) -> str:
    """The published page: what the profile is not, its terms, then each set."""

    lines = [
        "# The game-shape profile",
        "",
        "**This is a description of each game, not a score.** It has no score, no "
        "rank, no total and no zeroing floor. Shelves come in one fixed order and "
        "list their games in seed order, so nothing here orders a game by anything "
        "but its seed.",
        "",
        "**Role-correctness is reported here and gates nothing.** No module under "
        "`agents`, `meetings`, `orchestrator`, `engine` or `training` may import the "
        "profile (`.importlinter`), and no pre-registration, step rule, gate or "
        "objective reads it. It is computed after the fact from committed bytes.",
        "",
        "This page is generated. Do not edit it by hand: run "
        f"`{REGENERATE_COMMAND}` and commit the result. `{REGENERATE_COMMAND} "
        "--check` recomputes this page and each served "
        f"`{PROFILE_FILENAME}` from the recordings and fails on drift, and "
        f"`{REGENERATE_COMMAND} --set-dir DIR --json-stdout` profiles one other "
        "9-player directory and writes nothing. The four-player set ships no "
        "profile: its shelves would degenerate on a table that small.",
        "",
    ]
    lines.extend(_definitions())
    for set_path, profile in profiles:
        lines.extend(_set_lines(set_path, profile))
    lines.extend(
        [
            "## Limitations",
            "",
            "* One recording of 50 games per set, and no interval is claimed.",
            "* The classes swing between eras, which is why they are recomputed per "
            "era and recorded in the served file.",
            "* The constants were chosen with these numbers in view, and the leak "
            "level is not corrected for the many tests it is applied to, so a false "
            "leak verdict is plausible. The rule errs in one direction only: it can "
            "only hide more.",
            "* The facets the viewer already shows before the reveal (the length, the "
            "meetings) carry some information about the ending.",
            "* A ballot labelled as holding nothing is the voter's own statement. An "
            "ejecting one stops the publisher until the owner says how the tripwire "
            "reads it.",
            "* The manufactured-contradiction tripwire is nearly blind.",
            "* *Wrong on what it held* reads the grounding labels, not whether the "
            "cited line is true; the gameplay census measures that, and the profile "
            "does not read it.",
            "* The chip is not leak-tested; the leak rule covers shelves.",
            "",
        ]
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Publish, check, and the command line
# ---------------------------------------------------------------------------


def recording_inputs(set_dir: Path) -> list[Path]:
    """Every recorded byte of a set the served file must never alias."""

    return sorted(path for path in set_dir.iterdir() if path.name != PROFILE_FILENAME)


def publish(
    root: Path, *, loaders: Loaders = Loaders()
) -> tuple[tuple[str, GameProfile], ...]:
    """Compute every profile and replace the served files and the page.

    The page may not land under ``replays/``; each served file lands beside its
    set's recordings and may alias none of them.
    """

    page = root / MARKDOWN_PATH
    preflight_report_output(page, [root / "replays"])
    for set_path in PROFILE_SETS:
        preflight_report_output(
            profile_path(root, set_path), recording_inputs(root / set_path)
        )
    profiles = compute_profiles(root, loaders=loaders)
    for set_path, profile in profiles:
        atomic_write_report(profile_path(root, set_path), serialize_profile(profile))
    atomic_write_report(page, render_markdown(profiles))
    return profiles


def check_report(root: Path, *, loaders: Loaders = Loaders()) -> int:
    """Recompute every file and diff; 0 when consistent, 1 on drift or absence."""

    paths = [
        *(profile_path(root, set_path) for set_path in PROFILE_SETS),
        root / MARKDOWN_PATH,
    ]
    for path in paths:
        if not path.exists():
            print(f"--check: no committed profile file at {path}")
            return 1
    profiles = compute_profiles(root, loaders=loaders)
    expected = [
        *(
            (profile_path(root, set_path), serialize_profile(profile))
            for set_path, profile in profiles
        ),
        (root / MARKDOWN_PATH, render_markdown(profiles)),
    ]
    stale = [
        str(path.relative_to(root))
        for path, text in expected
        if path.read_text(encoding="utf-8") != text
    ]
    if stale:
        print(
            f"--check: {', '.join(stale)} is STALE: it does not match a "
            "recomputation from the committed recordings. Re-run "
            f"`{REGENERATE_COMMAND}` and commit the result."
        )
        return 1
    print(
        "--check: "
        + ", ".join(str(path.relative_to(root)) for path, _ in expected)
        + " are consistent with the committed recordings."
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Recompute every file and diff against the committed ones; exit 1 on drift.",
    )
    parser.add_argument(
        "--set-dir",
        type=Path,
        help="Profile one 9-player replay directory instead of the profiled sets.",
    )
    parser.add_argument(
        "--json-stdout",
        action="store_true",
        help="With --set-dir: print that directory's profile as JSON; write nothing.",
    )
    args = parser.parse_args(argv)
    try:
        if args.set_dir is not None or args.json_stdout:
            if args.set_dir is None or not args.json_stdout or args.check:
                parser.error("--set-dir and --json-stdout go together, without --check")
            sys.stdout.write(serialize_profile(compute_profile(args.set_dir)))
            return 0
        if args.check:
            return check_report(_REPO_ROOT)
        profiles = publish(_REPO_ROOT)
    except GameProfileConformanceError as breach:
        print(f"conformance breach: {breach}", file=sys.stderr)
        return 1
    except ProfileRefused as refused:
        print(f"refused: {refused}", file=sys.stderr)
        return 1
    for set_path, profile in profiles:
        print(
            f"Wrote {set_path}/{PROFILE_FILENAME}: {len(profile.pre_reveal.games)} "
            f"games, era {profile.era}; role-correctness is reported and gates nothing."
        )
    print(f"Wrote {MARKDOWN_PATH}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
