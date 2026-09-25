#!/usr/bin/env python3
"""Publish the gameplay census over the committed recordings.

Writes ``docs/gameplay-census.md`` and ``docs/gameplay-census.json`` from
:func:`eval.gameplay_census.compute_gameplay_census`, a fold over bytes already
in the tree with zero model calls. ``--check`` recomputes both and exits 1 on
drift, naming the stale file and the command that regenerates it.
``--set-dir DIR --json-stdout`` folds one directory (a candidate record, or a
scratch rehearsal), prints that one section as JSON and writes nothing; it exits
1 on a conformance breach, which names the set, seed and meeting.

Destinations are pre-flighted through ``scripts/_report_output.py`` before
anything is computed, with every ``replays/**`` file, the recording roots
themselves and every input the census reads declared as protected, so this
writer cannot be aimed at a recording directory whether or not the destination
exists yet.

Usage::

    python scripts/publish_gameplay_census.py
    python scripts/publish_gameplay_census.py --check
    python scripts/publish_gameplay_census.py --set-dir DIR --json-stdout
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _report_output import atomic_write_report, preflight_report_output  # noqa: E402
from eval.gameplay_census import (  # noqa: E402
    HEADINGS,
    CensusCell,
    CensusInputs,
    CensusSection,
    GameplayCensus,
    GameplayCensusConformanceError,
    compute_gameplay_census,
    fold_set,
    load_census_inputs,
    section_from_tally,
    serialize_json,
)
from eval.process_scorecard import RECORDINGS_ROOT  # noqa: E402

MARKDOWN_PATH = Path("docs/gameplay-census.md")
JSON_PATH = Path("docs/gameplay-census.json")

#: The one command a reader, or a red ``--check``, is told to run.
REGENERATE_COMMAND = "uv run python scripts/publish_gameplay_census.py"

Loader = Callable[[Path], CensusInputs]


def protected_inputs(root: Path) -> list[Path]:
    """Every recording location this command must never be able to write into.

    The recording root refuses, by containment, any destination beneath it,
    whether or not it exists yet; every census input lives there. The files
    refuse an alias of an existing recording placed outside it, which only
    file identity can catch: a hard link.
    """

    return [
        root / RECORDINGS_ROOT,
        *(path for path in root.glob(f"{RECORDINGS_ROOT}/**/*") if path.is_file()),
    ]


def _value(cell: CensusCell) -> str:
    """``numerator/denominator (rate)``, ``n/a``, or the by-construction zero."""

    if cell.denominator == 0:
        return "n/a"
    suffix = f", {cell.not_evaluable} not evaluable" if cell.not_evaluable else ""
    if cell.by_construction is not None:
        return f"0/{cell.denominator} by construction{suffix}"
    assert cell.rate is not None
    return f"{cell.numerator}/{cell.denominator} ({cell.rate * 100:.1f}%){suffix}"


def _groups(census: GameplayCensus) -> tuple[tuple[str, CensusSection], ...]:
    return (
        ("all four sets", census.pooled),
        ("the two nine-player sets", census.pooled_9p2i),
        *((section.label, section) for section in census.sets),
    )


def _heading_block(census: GameplayCensus, heading: str) -> list[str]:
    groups = _groups(census)
    header = "| cell | " + " | ".join(name for name, _ in groups) + " |"
    rule = "| --- |" + " --- |" * len(groups)
    lines = [f"### {heading}", "", header, rule]
    for key, cell in census.pooled.cells.items():
        if cell.heading != heading:
            continue
        values = " | ".join(_value(section.cells[key]) for _, section in groups)
        lines.append(f"| {cell.title} | {values} |")
    lines.append("")
    for key, table in census.pooled.tables.items():
        if table.heading != heading:
            continue
        rows = sorted(
            {row for _, section in groups for row in section.tables[key].counts},
            key=lambda row: (0, int(row), "") if row.isdigit() else (1, 0, row),
        )
        lines.extend([f"**{table.title}.**", "", header.replace("cell", "row"), rule])
        for row in rows:
            values = " | ".join(
                str(section.tables[key].counts.get(row, 0)) for _, section in groups
            )
            lines.append(f"| {row} | {values} |")
        if not rows:
            lines.append("| (none) |" + " 0 |" * len(groups))
        if any(section.tables[key].not_evaluable for _, section in groups):
            values = " | ".join(
                str(section.tables[key].not_evaluable) for _, section in groups
            )
            lines.append(f"| not evaluable | {values} |")
        lines.append("")
    return lines


def _era_lines(census: GameplayCensus) -> list[str]:
    era = census.pooled.era
    settings = (
        ", ".join(f"`{name} = {value}`" for name, value in sorted(era.settings.items()))
        or "none beyond the historical defaults"
    )
    flags = era.substrate_flags or {}
    on = ", ".join(sorted(name for name, value in flags.items() if value)) or "none"
    off = (
        ", ".join(sorted(name for name, value in flags.items() if not value)) or "none"
    )
    stamps = ", ".join(f"`{stamp}`" for stamp in era.prompt_stamps or ()) or "none"
    temporal = (
        "not delivered"
        if era.temporal_observation_version is None
        else f"version {era.temporal_observation_version}"
    )
    return [
        "## One era",
        "",
        "Every set below pooled, so every game shares one era, derived from the "
        "recordings themselves rather than stated:",
        "",
        f"* recorded experiment settings: {settings};",
        f"* temporal observations: {temporal};",
        f"* substrate flags on: {on}; off: {off};",
        f"* prompt stamps, read from the MANIFEST rows of games that held a "
        f"meeting: {stamps}.",
        "",
    ]


def _definition_lines(census: GameplayCensus) -> list[str]:
    lines = ["## Definitions", ""]
    for key, cell in census.pooled.cells.items():
        reads = ", ".join(f"`{kind}`" for kind in cell.reads)
        guard = (
            ""
            if cell.guard is None
            else " Zero by construction in every recording."
            if cell.guard == "always"
            else f" Zero by construction while `{cell.guard}`."
        )
        lines.extend(
            [f"**{cell.title}** (`{key}`). {cell.definition} Reads {reads}.{guard}", ""]
        )
    for key, table in census.pooled.tables.items():
        reads = ", ".join(f"`{kind}`" for kind in table.reads)
        lines.extend(
            [f"**{table.title}** (`{key}`). {table.definition} Reads {reads}.", ""]
        )
    return lines


def render_markdown(census: GameplayCensus) -> str:
    """The published page: what it is not, its terms, then the counts."""

    lines = [
        "# The gameplay census",
        "",
        f"**{census.not_the_scorecard_note}** The scorecard is "
        "[its own page](process-scorecard.md).",
        "",
        f"**{census.role_correctness_note}**",
        "",
        census.count_only_note,
        "",
        "This page is generated. Do not edit it by hand: run "
        f"`{REGENERATE_COMMAND}` and commit the result. "
        f"`{REGENERATE_COMMAND} --check` recomputes this page and "
        "[`gameplay-census.json`](gameplay-census.json) from the recordings and "
        f"fails on drift, and `{REGENERATE_COMMAND} --set-dir DIR --json-stdout` "
        "folds one other directory and writes nothing.",
        "",
        "## Terms",
        "",
    ]
    lines.extend(f"* **{term}**: {meaning}" for term, meaning in census.terms.items())
    lines.extend(
        [
            "",
            "Each cell reads `numerator/denominator (rate)`. A cell whose count a "
            "recorded setting forces to zero reads `0/N by construction` while that "
            "setting is on, and every cell with nothing to count reads `n/a`.",
            "",
            "## Recorded settings a zero depends on",
            "",
        ]
    )
    lines.extend(
        f"* `{name}`: {meaning}" for name, meaning in census.setting_meanings.items()
    )
    lines.extend(
        [
            "",
            "Every recorded setting field, and how this census uses it:",
            "",
            "| setting | use |",
            "| --- | --- |",
        ]
    )
    lines.extend(
        f"| `{name}` | {use} |" for name, use in census.field_classification.items()
    )
    lines.extend(["", "Named windows, in ticks:", ""])
    lines.extend(
        f"* `{name}`: {value}" for name, value in sorted(census.constants.items())
    )
    lines.append("")
    lines.extend(_era_lines(census))
    lines.extend(["## The counts", ""])
    for heading in HEADINGS:
        lines.extend(_heading_block(census, heading))
    lines.extend(_definition_lines(census))
    return "\n".join(lines)


def publish(root: Path, *, load: Loader = load_census_inputs) -> GameplayCensus:
    """Compute the fold and replace both published files atomically."""

    protected = protected_inputs(root)
    markdown_path = root / MARKDOWN_PATH
    json_path = root / JSON_PATH
    preflight_report_output(markdown_path, protected)
    preflight_report_output(json_path, protected)
    census = compute_gameplay_census(root, load=load)
    atomic_write_report(markdown_path, render_markdown(census))
    atomic_write_report(json_path, serialize_json(census))
    return census


def check_report(root: Path, *, load: Loader = load_census_inputs) -> int:
    """Recompute both files and diff; 0 when consistent, 1 on drift or absence."""

    markdown_path = root / MARKDOWN_PATH
    json_path = root / JSON_PATH
    for path in (markdown_path, json_path):
        if not path.exists():
            print(f"--check: no committed census at {path}")
            return 1
    census = compute_gameplay_census(root, load=load)
    stale = [
        str(relative)
        for relative, path, expected in (
            (MARKDOWN_PATH, markdown_path, render_markdown(census)),
            (JSON_PATH, json_path, serialize_json(census)),
        )
        if path.read_text(encoding="utf-8") != expected
    ]
    if stale:
        print(
            f"--check: {', '.join(stale)} is STALE: it does not match a "
            "recomputation from the committed recordings. Re-run "
            f"`{REGENERATE_COMMAND}` and commit the result."
        )
        return 1
    print(
        f"--check: {MARKDOWN_PATH} and {JSON_PATH} are consistent with the "
        "committed recordings."
    )
    return 0


def set_dir_json(set_dir: Path, *, load: Loader = load_census_inputs) -> str:
    """One directory's section as JSON. Computes; writes nothing."""

    return serialize_json(section_from_tally(fold_set(load(set_dir))))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Recompute both files and diff against the committed ones; exit 1 on drift.",
    )
    parser.add_argument(
        "--set-dir",
        type=Path,
        help="Fold one replay directory instead of the committed sets.",
    )
    parser.add_argument(
        "--json-stdout",
        action="store_true",
        help="With --set-dir: print that directory's section as JSON; write nothing.",
    )
    args = parser.parse_args(argv)
    if args.set_dir is not None or args.json_stdout:
        if args.set_dir is None or not args.json_stdout or args.check:
            parser.error("--set-dir and --json-stdout go together, without --check")
        try:
            sys.stdout.write(set_dir_json(args.set_dir, load=load_census_inputs))
        except GameplayCensusConformanceError as breach:
            print(f"conformance breach: {breach}", file=sys.stderr)
            return 1
        return 0
    if args.check:
        return check_report(_REPO_ROOT)
    census = publish(_REPO_ROOT)
    pooled = census.pooled
    print(
        f"Wrote {MARKDOWN_PATH} and {JSON_PATH}: {pooled.games} games, "
        f"{pooled.meetings} meetings; role-correctness is reported and gates nothing."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
